"""
Neo4j storage backend for the Engineering Knowledge Graph.
"""
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Union
from neo4j import GraphDatabase, Driver, exceptions as neo4j_exceptions
from dotenv import load_dotenv
import logging

from .models import Node, Edge, KnowledgeGraph, NodeType, EdgeType

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jStorage:
    """
    Enhanced Neo4j-based storage layer for the knowledge graph.
    
    Features:
    - Upsert operations for nodes and edges
    - Automatic indexing and constraints
    - Transaction handling
    - Backup and restore capabilities
    - Performance optimizations
    - NetworkX fallback for development
    """
    
    def __init__(self, connection_timeout: int = 30, max_connection_pool_size: int = 50):
        """Initialize Neo4j connection with enhanced configuration."""
        self._backup_path = "data/neo4j_backup"
        
        # Connection parameters
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password),
                connection_timeout=connection_timeout,
                max_connection_pool_size=max_connection_pool_size,
                encrypted=False  # Use True for production with SSL
            )
            
            # Verify connection
            self.driver.verify_connectivity()
            logger.info("✅ Connected to Neo4j successfully")
            
            # Set up schema (indexes and constraints)
            self._setup_schema()
            
        except (neo4j_exceptions.ServiceUnavailable, 
                neo4j_exceptions.AuthError,
                Exception) as e:
            logger.warning(f"❌ Neo4j connection failed: {e}")
            logger.info("🔄 Falling back to NetworkX storage")
            
            # Import here to avoid circular imports
            from .storage import GraphStorage
            self._fallback = GraphStorage()
            self.driver = None
    
    def _setup_schema(self):
        """Set up Neo4j constraints and indexes for optimal performance."""
        if not self.driver:
            return
            
        schema_queries = [
            # Constraints (ensure uniqueness and not-null)
            "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE",
            
            # Indexes for faster lookups
            "CREATE INDEX entity_type_idx IF NOT EXISTS FOR (n:Entity) ON (n.type)",
            "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (n:Entity) ON (n.name)",
            "CREATE INDEX entity_team_idx IF NOT EXISTS FOR (n:Entity) ON (n.team)",
            
            # Composite indexes for complex queries
            "CREATE INDEX entity_type_team_idx IF NOT EXISTS FOR (n:Entity) ON (n.type, n.team)",
        ]
        
        with self.driver.session() as session:
            for query in schema_queries:
                try:
                    session.run(query)
                    logger.debug(f"Schema setup: {query.split()[1:4]}")
                except Exception as e:
                    logger.debug(f"Schema already exists or error: {e}")
        
        logger.info("📊 Neo4j schema setup completed")
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("🔌 Neo4j connection closed")
    
    def _execute_transaction(self, transaction_func, *args, **kwargs):
        """Execute a function within a Neo4j transaction with retry logic."""
        if not self.driver:
            return None
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.driver.session() as session:
                    return session.execute_write(transaction_func, *args, **kwargs)
            except (neo4j_exceptions.TransientError, neo4j_exceptions.ServiceUnavailable) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Transaction failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Transaction failed after {max_retries} attempts: {e}")
                    raise
    
    def backup_to_disk(self, backup_path: str = None) -> bool:
        """
        Create a backup of the Neo4j graph to disk as JSON.
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            bool: Success status
        """
        if not self.driver:
            if self._fallback:
                return self._fallback.save_to_file(backup_path or f"{self._backup_path}.json")
            return False
        
        backup_path = backup_path or f"{self._backup_path}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Export all data
            backup_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0",
                    "node_count": 0,
                    "edge_count": 0
                },
                "nodes": [],
                "edges": []
            }
            
            # Export nodes
            nodes = self.get_all_nodes()
            for node in nodes:
                backup_data["nodes"].append({
                    "id": node.id,
                    "type": node.type.value,
                    "name": node.name,
                    "properties": node.properties
                })
            
            # Export edges  
            edges = self.get_all_edges()
            for edge in edges:
                backup_data["edges"].append({
                    "id": edge.id,
                    "type": edge.type.value,
                    "source": edge.source,
                    "target": edge.target,
                    "properties": edge.properties
                })
            
            backup_data["metadata"]["node_count"] = len(nodes)
            backup_data["metadata"]["edge_count"] = len(edges)
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"💾 Backup completed: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def restore_from_disk(self, backup_path: str) -> bool:
        """
        Restore Neo4j graph from disk backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            bool: Success status
        """
        if not os.path.exists(backup_path):
            logger.error(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Clear existing data
            self.clear_all()
            
            # Restore nodes
            for node_data in backup_data.get("nodes", []):
                node = Node(
                    id=node_data["id"],
                    type=NodeType(node_data["type"]),
                    name=node_data["name"],
                    properties=node_data.get("properties", {})
                )
                self.upsert_node(node)
            
            # Restore edges
            for edge_data in backup_data.get("edges", []):
                edge = Edge(
                    id=edge_data["id"],
                    type=EdgeType(edge_data["type"]),
                    source=edge_data["source"],
                    target=edge_data["target"],
                    properties=edge_data.get("properties", {})
                )
                self.upsert_edge(edge)
            
            metadata = backup_data.get("metadata", {})
            logger.info(f"✅ Restored {metadata.get('node_count', 0)} nodes and {metadata.get('edge_count', 0)} edges from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return False
    
    def add_node(self, node: Node) -> None:
        """Add a node to Neo4j (wrapper for upsert_node for backward compatibility)."""
        return self.upsert_node(node)
    
    def upsert_node(self, node: Node) -> None:
        """
        Insert or update a node in Neo4j with optimized upsert operation.
        
        Uses MERGE for atomic upsert to prevent duplicate nodes.
        """
        if not self.driver:
            return self._fallback.add_node(node)
        
        def _upsert_node_tx(tx, node):
            # Create node with labels and properties
            labels = [node.type.value.title(), "Entity"]  # e.g., Service, Database
            
            # Prepare properties (Neo4j doesn't like complex nested objects)
            properties = {
                "id": node.id,
                "name": node.name,
                "type": node.type.value
            }
            
            # Add simple properties only
            for key, value in node.properties.items():
                if isinstance(value, (str, int, float, bool)):
                    properties[key] = value
                elif isinstance(value, dict):
                    # Flatten dict properties with prefix
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (str, int, float, bool)):
                            properties[f"{key}_{sub_key}"] = sub_value
                elif isinstance(value, list):
                    # Convert list to string for simple storage
                    properties[f"{key}_list"] = str(value)
            
            # Build optimized Cypher query with MERGE for upsert
            labels_str = ":".join(labels)
            query = f"""
            MERGE (n:{labels_str} {{id: $id}})
            ON CREATE SET n += $properties
            ON MATCH SET n += $properties
            RETURN n.id as node_id
            """
            
            result = tx.run(query, id=node.id, properties=properties)
            record = result.single()
            return record["node_id"] if record else None
        
        try:
            node_id = self._execute_transaction(_upsert_node_tx, node)
            if node_id:
                logger.debug(f"✅ Upserted node: {node.id}")
            else:
                logger.warning(f"⚠️ Node upsert returned no result: {node.id}")
        except Exception as e:
            logger.error(f"❌ Failed to upsert node {node.id}: {e}")
            raise
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to Neo4j (wrapper for upsert_edge for backward compatibility)."""
        return self.upsert_edge(edge)
    
    def upsert_edge(self, edge: Edge) -> None:
        """
        Insert or update an edge in Neo4j with optimized upsert operation.
        
        Uses MERGE for atomic upsert to prevent duplicate edges.
        """
        if not self.driver:
            return self._fallback.add_edge(edge)
        
        def _upsert_edge_tx(tx, edge):
            # Create relationship
            rel_type = edge.type.value.upper().replace(' ', '_')
            
            properties = {"id": edge.id}
            # Add simple properties only
            for key, value in edge.properties.items():
                if isinstance(value, (str, int, float, bool)):
                    properties[key] = value
            
            query = f"""
            MATCH (source:Entity {{id: $source_id}})
            MATCH (target:Entity {{id: $target_id}})
            MERGE (source)-[r:{rel_type}]->(target)
            ON CREATE SET r += $properties
            ON MATCH SET r += $properties
            RETURN r.id as edge_id
            """
            
            result = tx.run(query, 
                          source_id=edge.source, 
                          target_id=edge.target, 
                          properties=properties)
            record = result.single()
            return record["edge_id"] if record else None
        
        try:
            edge_id = self._execute_transaction(_upsert_edge_tx, edge)
            if edge_id:
                logger.debug(f"✅ Upserted edge: {edge.source} -> {edge.target}")
            else:
                logger.warning(f"⚠️ Edge upsert returned no result: {edge.id}")
        except Exception as e:
            logger.error(f"❌ Failed to upsert edge {edge.id}: {e}")
            raise
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID from Neo4j."""
        if not self.driver:
            return self._fallback.get_node(node_id)
        
        with self.driver.session() as session:
            result = session.run(
                "MATCH (n {id: $node_id}) RETURN n",
                node_id=node_id
            )
            
            record = result.single()
            if not record:
                return None
            
            neo4j_node = record["n"]
            
            # Reconstruct Node object
            properties = dict(neo4j_node)
            node_type = NodeType(properties.pop("type"))
            name = properties.pop("name")
            node_id = properties.pop("id")
            
            return Node(
                id=node_id,
                type=node_type,
                name=name,
                properties=properties
            )
    
    def get_all_nodes(self) -> List[Node]:
        """Get all nodes from Neo4j."""
        if not self.driver:
            return self._fallback.get_all_nodes()
        
        nodes = []
        with self.driver.session() as session:
            result = session.run("MATCH (n:Entity) RETURN n")
            
            for record in result:
                neo4j_node = record["n"]
                properties = dict(neo4j_node)
                
                node_type = NodeType(properties.pop("type"))
                name = properties.pop("name")
                node_id = properties.pop("id")
                
                nodes.append(Node(
                    id=node_id,
                    type=node_type,
                    name=name,
                    properties=properties
                ))
        
        return nodes
    
    def get_all_edges(self) -> List[Edge]:
        """Get all edges from Neo4j."""
        if not self.driver:
            return self._fallback.get_all_edges()
        
        edges = []
        with self.driver.session() as session:
            result = session.run("""
                MATCH (source)-[r]->(target)
                RETURN source.id as source_id, target.id as target_id, 
                       type(r) as rel_type, properties(r) as props
            """)
            
            for record in result:
                # Convert Neo4j relationship type back to EdgeType
                rel_type = record["rel_type"].lower().replace('_', ' ')
                try:
                    edge_type = EdgeType(rel_type)
                except ValueError:
                    edge_type = EdgeType.USES  # Default fallback
                
                properties = dict(record["props"])
                edge_id = properties.pop("id", f"edge_{record['source_id']}_{record['target_id']}")
                
                edges.append(Edge(
                    id=edge_id,
                    type=edge_type,
                    source=record["source_id"],
                    target=record["target_id"],
                    properties=properties
                ))
        
        return edges
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """Get all nodes of a specific type."""
        if not self.driver:
            return self._fallback.get_nodes_by_type(node_type)
        
        nodes = []
        with self.driver.session() as session:
            result = session.run(
                f"MATCH (n:{node_type.value.title()}) RETURN n"
            )
            
            for record in result:
                neo4j_node = record["n"]
                properties = dict(neo4j_node)
                
                name = properties.pop("name")
                node_id = properties.pop("id")
                properties.pop("type", None)  # Remove type as we know it
                
                nodes.append(Node(
                    id=node_id,
                    type=node_type,
                    name=name,
                    properties=properties
                ))
        
        return nodes
    
    def get_neighbors(self, node_id: str, direction: str = "both") -> List[str]:
        """Get neighboring nodes."""
        if not self.driver:
            return self._fallback.get_neighbors(node_id, direction)
        
        with self.driver.session() as session:
            if direction == "out":
                query = "MATCH (n {id: $node_id})-[]->(neighbor) RETURN neighbor.id as neighbor_id"
            elif direction == "in":
                query = "MATCH (n {id: $node_id})<-[]-(neighbor) RETURN neighbor.id as neighbor_id"
            else:  # both
                query = "MATCH (n {id: $node_id})-[]-(neighbor) RETURN neighbor.id as neighbor_id"
            
            result = session.run(query, node_id=node_id)
            return [record["neighbor_id"] for record in result]
    
    def get_dependencies(self, node_id: str, depth: int = 1) -> Set[str]:
        """Get all dependencies of a node up to a certain depth."""
        if not self.driver:
            return self._fallback.get_dependencies(node_id, depth)
        
        with self.driver.session() as session:
            query = """
            MATCH path = (n {id: $node_id})-[:DEPENDS_ON|:USES|:READS_FROM|:WRITES_TO*1..%d]->(dep)
            RETURN DISTINCT dep.id as dep_id
            """ % depth
            
            result = session.run(query, node_id=node_id)
            return {record["dep_id"] for record in result}
    
    def get_dependents(self, node_id: str, depth: int = 1) -> Set[str]:
        """Get all nodes that depend on this node up to a certain depth."""
        if not self.driver:
            return self._fallback.get_dependents(node_id, depth)
        
        with self.driver.session() as session:
            query = """
            MATCH path = (dependent)-[:DEPENDS_ON|:USES|:READS_FROM|:WRITES_TO*1..%d]->(n {id: $node_id})
            RETURN DISTINCT dependent.id as dependent_id
            """ % depth
            
            result = session.run(query, node_id=node_id)
            return {record["dependent_id"] for record in result}
    
    def get_blast_radius(self, node_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """Calculate the blast radius if a node goes down."""
        if not self.driver:
            return self._fallback.get_blast_radius(node_id, max_depth)
        
        affected_services = self.get_dependents(node_id, max_depth)
        
        # Group by team for impact assessment
        teams_affected = {}
        for service_id in affected_services:
            node = self.get_node(service_id)
            if node and node.properties.get('team'):
                team = node.properties['team']
                if team not in teams_affected:
                    teams_affected[team] = []
                teams_affected[team].append(node.name)
        
        return {
            "node": self.get_node(node_id).name if self.get_node(node_id) else node_id,
            "affected_services": list(affected_services),
            "affected_services_count": len(affected_services),
            "teams_affected": teams_affected,
            "teams_count": len(teams_affected)
        }
    
    def get_team_ownership(self, team_name: str) -> List[Node]:
        """Get all nodes owned by a team."""
        if not self.driver:
            return self._fallback.get_team_ownership(team_name)
        
        nodes = []
        with self.driver.session() as session:
            result = session.run(
                "MATCH (n:Entity) WHERE n.team = $team_name RETURN n",
                team_name=team_name
            )
            
            for record in result:
                neo4j_node = record["n"]
                properties = dict(neo4j_node)
                
                node_type = NodeType(properties.pop("type"))
                name = properties.pop("name")
                node_id = properties.pop("id")
                
                nodes.append(Node(
                    id=node_id,
                    type=node_type,
                    name=name,
                    properties=properties
                ))
        
        return nodes
    
    def merge_graph(self, other_kg: KnowledgeGraph) -> None:
        """Merge another knowledge graph into this storage."""
        if not self.driver:
            return self._fallback.merge_graph(other_kg)
        
        # Add all nodes
        for node in other_kg.nodes.values():
            self.add_node(node)
        
        # Add all edges
        for edge in other_kg.edges.values():
            self.add_edge(edge)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        if not self.driver:
            return self._fallback.get_stats()
        
        with self.driver.session() as session:
            # Count nodes by type
            node_result = session.run("""
                MATCH (n:Entity) 
                RETURN n.type as node_type, count(n) as count
            """)
            node_types = {record["node_type"]: record["count"] for record in node_result}
            
            # Count total nodes and relationships
            total_result = session.run("""
                MATCH (n:Entity) 
                OPTIONAL MATCH ()-[r]->()
                RETURN count(DISTINCT n) as total_nodes, count(r) as total_edges
            """)
            
            record = total_result.single()
            total_nodes = record["total_nodes"] if record else 0
            total_edges = record["total_edges"] if record else 0
            
            # Count edge types
            edge_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as edge_type, count(r) as count
            """)
            edge_types = {record["edge_type"].lower().replace('_', ' '): record["count"] 
                         for record in edge_result}
            
            return {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "node_types": node_types,
                "edge_types": edge_types,
                "storage_backend": "neo4j"
            }
    
    def clear_all(self) -> None:
        """Clear all data from Neo4j (useful for testing)."""
        if not self.driver:
            return
        
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Cleared all data from Neo4j")
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all its relationships from Neo4j.
        
        Args:
            node_id: ID of the node to delete
            
        Returns:
            bool: True if node was deleted, False if not found
        """
        if not self.driver:
            if self._fallback:
                # NetworkX storage doesn't have delete_node, so we'll implement it
                if node_id in self._fallback.kg.nodes:
                    # Remove all edges connected to this node
                    edges_to_remove = []
                    for edge_id, edge in self._fallback.kg.edges.items():
                        if edge.source == node_id or edge.target == node_id:
                            edges_to_remove.append(edge_id)
                    
                    for edge_id in edges_to_remove:
                        del self._fallback.kg.edges[edge_id]
                    
                    # Remove the node
                    del self._fallback.kg.nodes[node_id]
                    return True
                return False
        
        def _delete_node_tx(tx, node_id):
            # Delete node and all its relationships
            result = tx.run("""
                MATCH (n:Entity {id: $node_id})
                DETACH DELETE n
                RETURN COUNT(n) as deleted_count
            """, node_id=node_id)
            
            record = result.single()
            return record["deleted_count"] if record else 0
        
        try:
            deleted_count = self._execute_transaction(_delete_node_tx, node_id)
            success = deleted_count > 0
            if success:
                logger.info(f"🗑️ Deleted node: {node_id}")
            else:
                logger.warning(f"⚠️ Node not found for deletion: {node_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to delete node {node_id}: {e}")
            return False
    
    def delete_edge(self, edge_id: str = None, source_id: str = None, target_id: str = None, edge_type: EdgeType = None) -> bool:
        """
        Delete an edge from Neo4j.
        
        Args:
            edge_id: ID of the edge to delete
            source_id: Source node ID (used if edge_id not provided)
            target_id: Target node ID (used if edge_id not provided)
            edge_type: Edge type (used if edge_id not provided)
            
        Returns:
            bool: True if edge was deleted, False if not found
        """
        if not self.driver:
            if self._fallback:
                if edge_id:
                    if edge_id in self._fallback.kg.edges:
                        del self._fallback.kg.edges[edge_id]
                        return True
                else:
                    # Find edge by source, target, type
                    for eid, edge in self._fallback.kg.edges.items():
                        if (edge.source == source_id and edge.target == target_id and
                            (edge_type is None or edge.type == edge_type)):
                            del self._fallback.kg.edges[eid]
                            return True
                return False
        
        def _delete_edge_tx(tx, edge_id, source_id, target_id, edge_type):
            if edge_id:
                # Delete by edge ID
                result = tx.run("""
                    MATCH ()-[r {id: $edge_id}]->()
                    DELETE r
                    RETURN COUNT(r) as deleted_count
                """, edge_id=edge_id)
            else:
                # Delete by source, target, and optionally type
                if edge_type:
                    rel_type = edge_type.value.upper().replace(' ', '_')
                    result = tx.run(f"""
                        MATCH (source:Entity {{id: $source_id}})-[r:{rel_type}]->(target:Entity {{id: $target_id}})
                        DELETE r
                        RETURN COUNT(r) as deleted_count
                    """, source_id=source_id, target_id=target_id)
                else:
                    result = tx.run("""
                        MATCH (source:Entity {id: $source_id})-[r]->(target:Entity {id: $target_id})
                        DELETE r
                        RETURN COUNT(r) as deleted_count
                    """, source_id=source_id, target_id=target_id)
            
            record = result.single()
            return record["deleted_count"] if record else 0
        
        try:
            deleted_count = self._execute_transaction(_delete_edge_tx, edge_id, source_id, target_id, edge_type)
            success = deleted_count > 0
            if success:
                edge_desc = edge_id or f"{source_id} -> {target_id}"
                logger.info(f"🗑️ Deleted edge: {edge_desc}")
            else:
                logger.warning(f"⚠️ Edge not found for deletion")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to delete edge: {e}")
            return False
    
    def bulk_upsert_nodes(self, nodes: List[Node]) -> int:
        """
        Bulk upsert multiple nodes for better performance.
        
        Args:
            nodes: List of nodes to upsert
            
        Returns:
            int: Number of nodes successfully upserted
        """
        if not self.driver:
            if self._fallback:
                for node in nodes:
                    self._fallback.add_node(node)
                return len(nodes)
            return 0
        
        def _bulk_upsert_nodes_tx(tx, nodes):
            success_count = 0
            
            for node in nodes:
                try:
                    # Create node with labels and properties
                    labels = [node.type.value.title(), "Entity"]
                    
                    # Prepare properties
                    properties = {
                        "id": node.id,
                        "name": node.name,
                        "type": node.type.value
                    }
                    
                    # Add simple properties only
                    for key, value in node.properties.items():
                        if isinstance(value, (str, int, float, bool)):
                            properties[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, (str, int, float, bool)):
                                    properties[f"{key}_{sub_key}"] = sub_value
                        elif isinstance(value, list):
                            properties[f"{key}_list"] = str(value)
                    
                    # Build optimized Cypher query
                    labels_str = ":".join(labels)
                    query = f"""
                    MERGE (n:{labels_str} {{id: $id}})
                    ON CREATE SET n += $properties
                    ON MATCH SET n += $properties
                    """
                    
                    tx.run(query, id=node.id, properties=properties)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to upsert node {node.id}: {e}")
                    continue
            
            return success_count
        
        try:
            success_count = self._execute_transaction(_bulk_upsert_nodes_tx, nodes)
            logger.info(f"✅ Bulk upserted {success_count}/{len(nodes)} nodes")
            return success_count
        except Exception as e:
            logger.error(f"❌ Bulk upsert failed: {e}")
            return 0
    
    def bulk_upsert_edges(self, edges: List[Edge]) -> int:
        """
        Bulk upsert multiple edges for better performance.
        
        Args:
            edges: List of edges to upsert
            
        Returns:
            int: Number of edges successfully upserted
        """
        if not self.driver:
            if self._fallback:
                for edge in edges:
                    self._fallback.add_edge(edge)
                return len(edges)
            return 0
        
        def _bulk_upsert_edges_tx(tx, edges):
            success_count = 0
            
            for edge in edges:
                try:
                    rel_type = edge.type.value.upper().replace(' ', '_')
                    
                    properties = {"id": edge.id}
                    for key, value in edge.properties.items():
                        if isinstance(value, (str, int, float, bool)):
                            properties[key] = value
                    
                    query = f"""
                    MATCH (source:Entity {{id: $source_id}})
                    MATCH (target:Entity {{id: $target_id}})
                    MERGE (source)-[r:{rel_type}]->(target)
                    ON CREATE SET r += $properties
                    ON MATCH SET r += $properties
                    """
                    
                    tx.run(query,
                          source_id=edge.source,
                          target_id=edge.target,
                          properties=properties)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to upsert edge {edge.id}: {e}")
                    continue
            
            return success_count
        
        try:
            success_count = self._execute_transaction(_bulk_upsert_edges_tx, edges)
            logger.info(f"✅ Bulk upserted {success_count}/{len(edges)} edges")
            return success_count
        except Exception as e:
            logger.error(f"❌ Bulk edge upsert failed: {e}")
            return 0
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of the Neo4j storage.
        
        Returns:
            Dict with health status and metrics
        """
        health_status = {
            "status": "unknown",
            "storage_backend": "neo4j" if self.driver else "networkx_fallback",
            "connection_active": False,
            "performance_metrics": {},
            "errors": []
        }
        
        if not self.driver:
            health_status.update({
                "status": "fallback",
                "connection_active": False,
                "message": "Using NetworkX fallback storage"
            })
            if self._fallback:
                stats = self._fallback.get_stats()
                health_status["performance_metrics"] = {
                    "total_nodes": stats.get("total_nodes", 0),
                    "total_edges": stats.get("total_edges", 0)
                }
            return health_status
        
        try:
            # Test basic connectivity
            start_time = time.time()
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
            connection_time = time.time() - start_time
            health_status["connection_active"] = test_value == 1
            
            # Get performance metrics
            stats = self.get_stats()
            health_status["performance_metrics"] = {
                "total_nodes": stats.get("total_nodes", 0),
                "total_edges": stats.get("total_edges", 0),
                "connection_time_ms": round(connection_time * 1000, 2),
                "node_types": stats.get("node_types", {}),
                "edge_types": stats.get("edge_types", {})
            }
            
            # Check for performance issues
            if connection_time > 1.0:
                health_status["errors"].append("Slow database connection (>1s)")
            
            if stats.get("total_nodes", 0) > 50000:
                health_status["errors"].append("Large dataset detected, consider optimization")
            
            health_status["status"] = "healthy" if not health_status["errors"] else "degraded"
            
        except Exception as e:
            health_status.update({
                "status": "error",
                "connection_active": False,
                "errors": [str(e)]
            })
            
        return health_status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics for monitoring."""
        if not self.driver:
            return {"backend": "networkx_fallback", "metrics": {}}
        
        metrics = {"backend": "neo4j"}
        
        try:
            with self.driver.session() as session:
                # Query execution time test
                start_time = time.time()
                session.run("MATCH (n:Entity) RETURN count(n) as node_count")
                query_time = time.time() - start_time
                
                # Database size metrics
                result = session.run("""
                    CALL apoc.meta.stats() YIELD labels, relTypesCount
                    RETURN labels, relTypesCount
                """)
                try:
                    meta_stats = result.single()
                    metrics["labels"] = meta_stats["labels"] if meta_stats else {}
                    metrics["relationship_types"] = meta_stats["relTypesCount"] if meta_stats else {}
                except:
                    # Fallback if APOC is not available
                    metrics["labels"] = {}
                    metrics["relationship_types"] = {}
                
                # Index usage metrics
                try:
                    index_result = session.run("CALL db.indexes() YIELD name, state, populationPercent")
                    indexes = []
                    for record in index_result:
                        indexes.append({
                            "name": record["name"],
                            "state": record["state"],
                            "population_percent": record["populationPercent"]
                        })
                    metrics["indexes"] = indexes
                except:
                    metrics["indexes"] = []
                
                metrics.update({
                    "query_time_ms": round(query_time * 1000, 2),
                    "connection_pool_active": True,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            metrics["error"] = str(e)
            
        return metrics
    
    def optimize_database(self) -> Dict[str, Any]:
        """
        Perform database optimization tasks.
        
        Returns:
            Dict with optimization results
        """
        if not self.driver:
            return {"status": "skipped", "reason": "Using NetworkX fallback"}
        
        optimization_results = {
            "status": "started",
            "tasks_completed": [],
            "tasks_failed": [],
            "recommendations": []
        }
        
        try:
            with self.driver.session() as session:
                # Update statistics
                try:
                    session.run("CALL db.schema.visualization()")
                    optimization_results["tasks_completed"].append("Schema visualization updated")
                except Exception as e:
                    optimization_results["tasks_failed"].append(f"Schema update failed: {e}")
                
                # Check for missing indexes
                stats = self.get_stats()
                total_nodes = stats.get("total_nodes", 0)
                
                if total_nodes > 1000:
                    optimization_results["recommendations"].append(
                        "Consider adding more specific indexes for large datasets"
                    )
                
                if total_nodes > 10000:
                    optimization_results["recommendations"].append(
                        "Consider implementing query result caching for better performance"
                    )
                
                optimization_results["status"] = "completed"
                
        except Exception as e:
            optimization_results["status"] = "error"
            optimization_results["error"] = str(e)
        
        return optimization_results
    
    # Compatibility methods to match GraphStorage interface
    @property
    def kg(self):
        """Create a compatible KnowledgeGraph object from Neo4j data."""
        kg = KnowledgeGraph()
        
        # Load all nodes
        for node in self.get_all_nodes():
            kg.add_node(node)
        
        # Load all edges
        for edge in self.get_all_edges():
            kg.add_edge(edge)
        
        return kg
