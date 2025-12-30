"""
Enhanced Query Engine for the Engineering Knowledge Graph - Part 3 Implementation

This module provides a comprehensive query engine that supports both natural language
and programmatic queries with advanced graph traversal capabilities.

Key Features:
- All required Part 3 query methods
- Cycle detection and prevention
- Performance optimizations for large graphs
- Edge type filtering
- Comprehensive path finding
- Impact analysis with team information
"""

from typing import List, Dict, Any, Optional, Set, Union, Tuple
from collections import deque, defaultdict
import re
import time
from dataclasses import dataclass
from enum import Enum

from .models import Node, Edge, NodeType, EdgeType


class QueryType(Enum):
    """Types of queries supported by the engine."""
    GET_NODE = "get_node"
    GET_NODES = "get_nodes"
    DOWNSTREAM = "downstream"
    UPSTREAM = "upstream"
    BLAST_RADIUS = "blast_radius"
    PATH = "path"
    GET_OWNER = "get_owner"
    NATURAL_LANGUAGE = "natural_language"


@dataclass
class QueryResult:
    """Standardized query result structure."""
    query_type: QueryType
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AdvancedQueryEngine:
    """
    Advanced Query Engine implementing all Part 3 requirements.
    
    Supports both programmatic queries and natural language processing
    with performance optimizations and cycle handling.
    """
    
    def __init__(self, storage):
        """
        Initialize the query engine.
        
        Args:
            storage: Storage backend (GraphStorage or Neo4jStorage)
        """
        self.storage = storage
        self._query_cache = {}
        self._max_cache_size = 1000
        self._cycle_detection_enabled = True
    
    # ========================================================================
    # PART 3 REQUIRED QUERY METHODS
    # ========================================================================
    
    def get_node(self, node_id: str) -> QueryResult:
        """
        Retrieve single node by ID.
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            QueryResult with node data or error
            
        Example:
            result = engine.get_node("service:order-service")
        """
        start_time = time.time()
        
        try:
            node = self.storage.get_node(node_id)
            execution_time = (time.time() - start_time) * 1000
            
            if node:
                return QueryResult(
                    query_type=QueryType.GET_NODE,
                    success=True,
                    data={
                        "id": node.id,
                        "type": node.type.value,
                        "name": node.name,
                        "properties": node.properties
                    },
                    execution_time_ms=execution_time,
                    metadata={"node_id": node_id}
                )
            else:
                return QueryResult(
                    query_type=QueryType.GET_NODE,
                    success=False,
                    error=f"Node '{node_id}' not found",
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            return QueryResult(
                query_type=QueryType.GET_NODE,
                success=False,
                error=f"Error retrieving node: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def get_nodes(self, 
                  node_type: Optional[Union[str, NodeType]] = None,
                  filters: Optional[Dict[str, Any]] = None,
                  limit: Optional[int] = None) -> QueryResult:
        """
        List nodes by type and filters.
        
        Args:
            node_type: Filter by node type (e.g., "database", NodeType.SERVICE)
            filters: Property filters (e.g., {"team": "payments", "environment": "prod"})
            limit: Maximum number of results to return
            
        Returns:
            QueryResult with list of matching nodes
            
        Example:
            result = engine.get_nodes(node_type="database")
            result = engine.get_nodes(filters={"team": "payments"})
        """
        start_time = time.time()
        filters = filters or {}
        
        try:
            # Get nodes by type if specified
            if node_type:
                if isinstance(node_type, str):
                    node_type = NodeType(node_type)
                nodes = self.storage.get_nodes_by_type(node_type)
            else:
                nodes = self.storage.get_all_nodes()
            
            # Apply property filters
            filtered_nodes = []
            for node in nodes:
                match = True
                for key, value in filters.items():
                    if key not in node.properties or node.properties[key] != value:
                        match = False
                        break
                if match:
                    filtered_nodes.append(node)
            
            # Apply limit
            if limit and len(filtered_nodes) > limit:
                filtered_nodes = filtered_nodes[:limit]
            
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                query_type=QueryType.GET_NODES,
                success=True,
                data={
                    "nodes": [
                        {
                            "id": node.id,
                            "type": node.type.value,
                            "name": node.name,
                            "properties": node.properties
                        } for node in filtered_nodes
                    ],
                    "total_count": len(filtered_nodes)
                },
                execution_time_ms=execution_time,
                metadata={
                    "node_type": node_type.value if node_type else "all",
                    "filters": filters,
                    "limit": limit
                }
            )
            
        except Exception as e:
            return QueryResult(
                query_type=QueryType.GET_NODES,
                success=False,
                error=f"Error retrieving nodes: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def downstream(self, 
                   node_id: str, 
                   max_depth: int = 10,
                   edge_types: Optional[List[Union[str, EdgeType]]] = None) -> QueryResult:
        """
        Find all transitive dependencies (what this node depends on).
        
        Args:
            node_id: Starting node ID
            max_depth: Maximum traversal depth to prevent infinite loops
            edge_types: Filter by specific edge types (e.g., ["depends_on", "calls"])
            
        Returns:
            QueryResult with downstream dependencies
            
        Example:
            result = engine.downstream("service:order-service")
        """
        start_time = time.time()
        
        try:
            dependencies = self._traverse_graph(
                start_node=node_id,
                direction="downstream",
                max_depth=max_depth,
                edge_types=edge_types
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Get detailed node information
            dependency_nodes = []
            for dep_id in dependencies:
                node = self.storage.get_node(dep_id)
                if node:
                    dependency_nodes.append({
                        "id": node.id,
                        "type": node.type.value,
                        "name": node.name,
                        "properties": node.properties
                    })
            
            return QueryResult(
                query_type=QueryType.DOWNSTREAM,
                success=True,
                data={
                    "node_id": node_id,
                    "dependencies": dependency_nodes,
                    "dependency_count": len(dependencies),
                    "dependency_ids": list(dependencies)
                },
                execution_time_ms=execution_time,
                metadata={
                    "max_depth": max_depth,
                    "edge_types": [et.value if isinstance(et, EdgeType) else et for et in (edge_types or [])]
                }
            )
            
        except Exception as e:
            return QueryResult(
                query_type=QueryType.DOWNSTREAM,
                success=False,
                error=f"Error finding downstream dependencies: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def upstream(self, 
                 node_id: str, 
                 max_depth: int = 10,
                 edge_types: Optional[List[Union[str, EdgeType]]] = None) -> QueryResult:
        """
        Find all transitive dependents (what depends on this node).
        
        Args:
            node_id: Starting node ID
            max_depth: Maximum traversal depth to prevent infinite loops
            edge_types: Filter by specific edge types
            
        Returns:
            QueryResult with upstream dependents
            
        Example:
            result = engine.upstream("database:orders-db")
        """
        start_time = time.time()
        
        try:
            dependents = self._traverse_graph(
                start_node=node_id,
                direction="upstream",
                max_depth=max_depth,
                edge_types=edge_types
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Get detailed node information
            dependent_nodes = []
            for dep_id in dependents:
                node = self.storage.get_node(dep_id)
                if node:
                    dependent_nodes.append({
                        "id": node.id,
                        "type": node.type.value,
                        "name": node.name,
                        "properties": node.properties
                    })
            
            return QueryResult(
                query_type=QueryType.UPSTREAM,
                success=True,
                data={
                    "node_id": node_id,
                    "dependents": dependent_nodes,
                    "dependent_count": len(dependents),
                    "dependent_ids": list(dependents)
                },
                execution_time_ms=execution_time,
                metadata={
                    "max_depth": max_depth,
                    "edge_types": [et.value if isinstance(et, EdgeType) else et for et in (edge_types or [])]
                }
            )
            
        except Exception as e:
            return QueryResult(
                query_type=QueryType.UPSTREAM,
                success=False,
                error=f"Error finding upstream dependents: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def blast_radius(self, node_id: str, max_depth: int = 5) -> QueryResult:
        """
        Comprehensive impact analysis - upstream + downstream + team impact.
        
        Args:
            node_id: Node to analyze
            max_depth: Maximum traversal depth
            
        Returns:
            QueryResult with comprehensive impact analysis
            
        Example:
            result = engine.blast_radius("service:payment-service")
        """
        start_time = time.time()
        
        try:
            # Get upstream and downstream impacts
            upstream_result = self.upstream(node_id, max_depth)
            downstream_result = self.downstream(node_id, max_depth)
            
            if not upstream_result.success or not downstream_result.success:
                return QueryResult(
                    query_type=QueryType.BLAST_RADIUS,
                    success=False,
                    error="Failed to compute upstream or downstream dependencies",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Combine all affected nodes
            all_affected = set(upstream_result.data["dependent_ids"] + downstream_result.data["dependency_ids"])
            all_affected.discard(node_id)  # Remove the source node itself
            
            # Group by teams
            teams_affected = defaultdict(list)
            critical_services = []
            
            for affected_id in all_affected:
                node = self.storage.get_node(affected_id)
                if node:
                    # Team impact
                    team = node.properties.get("team")
                    if team:
                        teams_affected[team].append({
                            "id": node.id,
                            "name": node.name,
                            "type": node.type.value
                        })
                    
                    # Mark critical services (those with many dependencies)
                    if node.type == NodeType.SERVICE:
                        deps = self.downstream(node.id, max_depth=2)
                        if deps.success and deps.data["dependency_count"] > 3:
                            critical_services.append({
                                "id": node.id,
                                "name": node.name,
                                "dependency_count": deps.data["dependency_count"]
                            })
            
            # Get team details
            team_details = {}
            for team_name in teams_affected.keys():
                team_node = self.storage.get_node(f"team:{team_name}")
                if team_node:
                    team_details[team_name] = {
                        "lead": team_node.properties.get("lead", "Unknown"),
                        "slack_channel": team_node.properties.get("slack_channel", "Unknown"),
                        "oncall": team_node.properties.get("oncall", "Unknown"),
                        "affected_services": teams_affected[team_name]
                    }
            
            source_node = self.storage.get_node(node_id)
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                query_type=QueryType.BLAST_RADIUS,
                success=True,
                data={
                    "source_node": {
                        "id": node_id,
                        "name": source_node.name if source_node else "Unknown",
                        "type": source_node.type.value if source_node else "Unknown"
                    },
                    "total_affected": len(all_affected),
                    "upstream_affected": upstream_result.data["dependent_count"],
                    "downstream_affected": downstream_result.data["dependency_count"],
                    "teams_affected": team_details,
                    "teams_count": len(teams_affected),
                    "critical_services": critical_services,
                    "all_affected_ids": list(all_affected),
                    "severity": self._calculate_severity(len(all_affected), len(teams_affected))
                },
                execution_time_ms=execution_time,
                metadata={
                    "max_depth": max_depth,
                    "analysis_timestamp": time.time()
                }
            )
            
        except Exception as e:
            return QueryResult(
                query_type=QueryType.BLAST_RADIUS,
                success=False,
                error=f"Error calculating blast radius: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> QueryResult:
        """
        Find shortest path between two nodes.
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            max_depth: Maximum path length to search
            
        Returns:
            QueryResult with shortest path information
            
        Example:
            result = engine.path("service:api-gateway", "database:payments-db")
        """
        start_time = time.time()
        
        try:
            paths = self._find_paths(from_id, to_id, max_paths=5, max_depth=max_depth)
            execution_time = (time.time() - start_time) * 1000
            
            if not paths:
                return QueryResult(
                    query_type=QueryType.PATH,
                    success=False,
                    error=f"No path found between '{from_id}' and '{to_id}'",
                    execution_time_ms=execution_time
                )
            
            # Get detailed information for the shortest path
            shortest_path = paths[0]
            path_details = []
            
            for i, node_id in enumerate(shortest_path):
                node = self.storage.get_node(node_id)
                if node:
                    path_info = {
                        "step": i,
                        "id": node.id,
                        "name": node.name,
                        "type": node.type.value
                    }
                    
                    # Add edge information if not the last node
                    if i < len(shortest_path) - 1:
                        next_node_id = shortest_path[i + 1]
                        edge = self._find_edge_between(node_id, next_node_id)
                        if edge:
                            path_info["edge_to_next"] = {
                                "type": edge.type.value,
                                "properties": edge.properties
                            }
                    
                    path_details.append(path_info)
            
            return QueryResult(
                query_type=QueryType.PATH,
                success=True,
                data={
                    "from_id": from_id,
                    "to_id": to_id,
                    "shortest_path": shortest_path,
                    "path_length": len(shortest_path),
                    "path_details": path_details,
                    "alternative_paths": paths[1:] if len(paths) > 1 else [],
                    "total_paths_found": len(paths)
                },
                execution_time_ms=execution_time,
                metadata={
                    "max_depth": max_depth,
                    "search_algorithm": "breadth_first_search"
                }
            )
            
        except Exception as e:
            return QueryResult(
                query_type=QueryType.PATH,
                success=False,
                error=f"Error finding path: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def get_owner(self, node_id: str) -> QueryResult:
        """
        Find the owning team for a node.
        
        Args:
            node_id: Node to find owner for
            
        Returns:
            QueryResult with ownership information
            
        Example:
            result = engine.get_owner("service:payment-service")
        """
        start_time = time.time()
        
        try:
            node = self.storage.get_node(node_id)
            if not node:
                return QueryResult(
                    query_type=QueryType.GET_OWNER,
                    success=False,
                    error=f"Node '{node_id}' not found",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            team_name = node.properties.get("team")
            if not team_name:
                return QueryResult(
                    query_type=QueryType.GET_OWNER,
                    success=False,
                    error=f"No team ownership information found for '{node_id}'",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Get detailed team information
            team_node = self.storage.get_node(f"team:{team_name}")
            team_details = {
                "name": team_name,
                "lead": "Unknown",
                "slack_channel": "Unknown",
                "oncall": "Unknown"
            }
            
            if team_node:
                team_details.update({
                    "lead": team_node.properties.get("lead", "Unknown"),
                    "slack_channel": team_node.properties.get("slack_channel", "Unknown"),
                    "oncall": team_node.properties.get("oncall", "Unknown")
                })
            
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                query_type=QueryType.GET_OWNER,
                success=True,
                data={
                    "node": {
                        "id": node.id,
                        "name": node.name,
                        "type": node.type.value
                    },
                    "owner": team_details,
                    "ownership_type": "team"
                },
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return QueryResult(
                query_type=QueryType.GET_OWNER,
                success=False,
                error=f"Error finding owner: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    # ========================================================================
    # ADVANCED GRAPH TRAVERSAL METHODS
    # ========================================================================
    
    def _traverse_graph(self, 
                       start_node: str, 
                       direction: str, 
                       max_depth: int = 10,
                       edge_types: Optional[List[Union[str, EdgeType]]] = None) -> Set[str]:
        """
        Advanced graph traversal with cycle detection and edge filtering.
        
        Args:
            start_node: Starting node ID
            direction: "upstream" or "downstream"
            max_depth: Maximum traversal depth
            edge_types: Filter by specific edge types
            
        Returns:
            Set of node IDs found during traversal
        """
        visited = set()
        result = set()
        queue = deque([(start_node, 0)])  # (node_id, depth)
        
        # Convert edge types to EdgeType enum
        if edge_types:
            edge_type_enums = []
            for et in edge_types:
                if isinstance(et, str):
                    try:
                        edge_type_enums.append(EdgeType(et))
                    except ValueError:
                        continue  # Skip invalid edge types
                else:
                    edge_type_enums.append(et)
            edge_types = edge_type_enums
        
        while queue:
            current_node, depth = queue.popleft()
            
            if current_node in visited or depth > max_depth:
                continue
            
            visited.add(current_node)
            
            if current_node != start_node:  # Don't include the starting node
                result.add(current_node)
            
            # Get connected nodes based on direction
            if direction == "downstream":
                # What this node depends on (outgoing edges in dependency direction)
                connected_nodes = self._get_dependencies(current_node, edge_types)
            else:  # upstream
                # What depends on this node (incoming edges in dependency direction)
                connected_nodes = self._get_dependents(current_node, edge_types)
            
            # Add unvisited connected nodes to queue
            for connected_node in connected_nodes:
                if connected_node not in visited:
                    queue.append((connected_node, depth + 1))
        
        return result
    
    def _get_dependencies(self, node_id: str, edge_types: Optional[List[EdgeType]] = None) -> Set[str]:
        """Get direct dependencies of a node with edge type filtering."""
        dependencies = set()
        all_edges = self.storage.get_all_edges()
        
        for edge in all_edges:
            if edge.source == node_id:
                # Filter by edge type if specified
                if edge_types and edge.type not in edge_types:
                    continue
                dependencies.add(edge.target)
        
        return dependencies
    
    def _get_dependents(self, node_id: str, edge_types: Optional[List[EdgeType]] = None) -> Set[str]:
        """Get direct dependents of a node with edge type filtering."""
        dependents = set()
        all_edges = self.storage.get_all_edges()
        
        for edge in all_edges:
            if edge.target == node_id:
                # Filter by edge type if specified
                if edge_types and edge.type not in edge_types:
                    continue
                dependents.add(edge.source)
        
        return dependents
    
    def _find_paths(self, from_id: str, to_id: str, max_paths: int = 5, max_depth: int = 10) -> List[List[str]]:
        """
        Find multiple paths between two nodes using BFS.
        
        Args:
            from_id: Source node
            to_id: Target node
            max_paths: Maximum number of paths to find
            max_depth: Maximum path length
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        if from_id == to_id:
            return [[from_id]]
        
        paths = []
        queue = deque([(from_id, [from_id])])  # (current_node, path)
        visited_paths = set()
        
        while queue and len(paths) < max_paths:
            current_node, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            # Get all neighbors (both directions)
            neighbors = set()
            all_edges = self.storage.get_all_edges()
            
            for edge in all_edges:
                if edge.source == current_node:
                    neighbors.add(edge.target)
                elif edge.target == current_node:
                    neighbors.add(edge.source)
            
            for neighbor in neighbors:
                new_path = path + [neighbor]
                path_key = tuple(new_path)
                
                if neighbor == to_id:
                    # Found a path to target
                    paths.append(new_path)
                elif neighbor not in path and path_key not in visited_paths:
                    # Continue exploring (avoid cycles)
                    queue.append((neighbor, new_path))
                    visited_paths.add(path_key)
        
        # Sort paths by length (shortest first)
        paths.sort(key=len)
        return paths
    
    def _find_edge_between(self, from_id: str, to_id: str) -> Optional[Edge]:
        """Find an edge between two nodes."""
        all_edges = self.storage.get_all_edges()
        
        for edge in all_edges:
            if (edge.source == from_id and edge.target == to_id) or \
               (edge.source == to_id and edge.target == from_id):
                return edge
        
        return None
    
    def _calculate_severity(self, affected_count: int, teams_count: int) -> str:
        """Calculate impact severity based on affected services and teams."""
        if affected_count >= 10 or teams_count >= 4:
            return "critical"
        elif affected_count >= 5 or teams_count >= 2:
            return "high"
        elif affected_count >= 2 or teams_count >= 1:
            return "medium"
        else:
            return "low"
    
    # ========================================================================
    # NATURAL LANGUAGE PROCESSING (Legacy compatibility)
    # ========================================================================
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language query (maintains backward compatibility).
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with query results
        """
        start_time = time.time()
        
        try:
            result = self._process_natural_language(question)
            result["execution_time_ms"] = (time.time() - start_time) * 1000
            return result
        except Exception as e:
            return {
                "query": question,
                "type": "error",
                "error": f"Query processing failed: {str(e)}",
                "execution_time_ms": (time.time() - start_time) * 1000
            }
    
    def _process_natural_language(self, question: str) -> Dict[str, Any]:
        """Process natural language queries with enhanced pattern matching."""
        question_lower = question.lower()
        
        # Enhanced pattern matching for different query types
        if any(phrase in question_lower for phrase in ['blast radius', 'what breaks', 'goes down', 'fails', 'impact']):
            return self._handle_blast_radius_query(question)
        elif any(phrase in question_lower for phrase in ['who owns', 'owner of', 'owned by', 'ownership']):
            return self._handle_ownership_query(question)
        elif any(phrase in question_lower for phrase in ['path', 'connect', 'route', 'how to get']):
            return self._handle_path_query(question)
        elif any(phrase in question_lower for phrase in ['depends on', 'dependencies', 'downstream']):
            return self._handle_dependency_query(question)
        elif any(phrase in question_lower for phrase in ['dependents', 'upstream', 'what uses']):
            return self._handle_dependent_query(question)
        elif any(phrase in question_lower for phrase in ['team', 'teams']):
            return self._handle_team_query(question)
        elif any(phrase in question_lower for phrase in ['database', 'db', 'data']):
            return self._handle_database_query(question)
        elif any(phrase in question_lower for phrase in ['service', 'services']):
            return self._handle_service_query(question)
        else:
            return self._handle_general_query(question)
    
    def _handle_blast_radius_query(self, question: str) -> Dict[str, Any]:
        """Handle blast radius queries using the advanced blast_radius method."""
        service_name = self._extract_service_name(question)
        
        if not service_name:
            return {
                "query": question,
                "type": "blast_radius",
                "error": "Could not identify a service name in the query",
                "suggestion": "Please specify a service name, e.g., 'What breaks if order-service goes down?'"
            }
        
        # Try different node ID patterns
        possible_ids = [
            f"service:{service_name}",
            f"database:{service_name}",
            f"cache:{service_name}",
            service_name  # Try direct ID
        ]
        
        for node_id in possible_ids:
            if self.storage.get_node(node_id):
                result = self.blast_radius(node_id)
                if result.success:
                    # Convert to legacy format
                    data = result.data
                    return {
                        "query": question,
                        "type": "blast_radius",
                        "service_analyzed": service_name,
                        "node": data["source_node"]["name"],
                        "total_affected": data["total_affected"],
                        "upstream_affected": data["upstream_affected"],
                        "downstream_affected": data["downstream_affected"],
                        "teams_affected": {
                            team: [svc["name"] for svc in services["affected_services"]]
                            for team, services in data["teams_affected"].items()
                        },
                        "teams_count": data["teams_count"],
                        "severity": data["severity"],
                        "team_details": data["teams_affected"],
                        "execution_time_ms": result.execution_time_ms
                    }
        
        return {
            "query": question,
            "type": "blast_radius",
            "error": f"Service '{service_name}' not found in the knowledge graph",
            "available_services": [node.name for node in self.storage.get_nodes_by_type(NodeType.SERVICE)]
        }
    
    def _handle_ownership_query(self, question: str) -> Dict[str, Any]:
        """Handle ownership queries using get_owner method."""
        service_name = self._extract_service_name(question)
        
        if service_name:
            possible_ids = [
                f"service:{service_name}",
                f"database:{service_name}",
                f"cache:{service_name}",
                service_name
            ]
            
            for node_id in possible_ids:
                if self.storage.get_node(node_id):
                    result = self.get_owner(node_id)
                    if result.success:
                        data = result.data
                        return {
                            "query": question,
                            "type": "ownership",
                            "service": data["node"]["name"],
                            "service_type": data["node"]["type"],
                            "team": data["owner"]["name"],
                            "team_lead": data["owner"]["lead"],
                            "slack_channel": data["owner"]["slack_channel"],
                            "oncall": data["owner"]["oncall"]
                        }
        
        return {
            "query": question,
            "type": "ownership",
            "error": "Could not identify a service or find ownership information"
        }
    
    def _handle_path_query(self, question: str) -> Dict[str, Any]:
        """Handle path finding queries."""
        # Extract two service names for path queries
        service_names = self._extract_multiple_service_names(question)
        
        if len(service_names) >= 2:
            from_service, to_service = service_names[0], service_names[1]
            
            # Try different ID combinations
            from_ids = [f"service:{from_service}", f"database:{from_service}", from_service]
            to_ids = [f"service:{to_service}", f"database:{to_service}", to_service]
            
            for from_id in from_ids:
                for to_id in to_ids:
                    if self.storage.get_node(from_id) and self.storage.get_node(to_id):
                        result = self.path(from_id, to_id)
                        if result.success:
                            return {
                                "query": question,
                                "type": "path",
                                "from_service": from_service,
                                "to_service": to_service,
                                "path_length": result.data["path_length"],
                                "shortest_path": result.data["shortest_path"],
                                "path_details": result.data["path_details"]
                            }
        
        return {
            "query": question,
            "type": "path",
            "error": "Could not identify two services for path finding"
        }
    
    def _handle_dependency_query(self, question: str) -> Dict[str, Any]:
        """Handle dependency (downstream) queries."""
        service_name = self._extract_service_name(question)
        
        if service_name:
            possible_ids = [f"service:{service_name}", f"database:{service_name}", service_name]
            
            for node_id in possible_ids:
                if self.storage.get_node(node_id):
                    result = self.downstream(node_id)
                    if result.success:
                        return {
                            "query": question,
                            "type": "dependencies",
                            "service": service_name,
                            "dependencies": result.data["dependencies"],
                            "dependency_count": result.data["dependency_count"]
                        }
        
        return {
            "query": question,
            "type": "dependencies",
            "error": "Could not identify service or find dependencies"
        }
    
    def _handle_dependent_query(self, question: str) -> Dict[str, Any]:
        """Handle dependent (upstream) queries."""
        service_name = self._extract_service_name(question)
        
        if service_name:
            possible_ids = [f"service:{service_name}", f"database:{service_name}", service_name]
            
            for node_id in possible_ids:
                if self.storage.get_node(node_id):
                    result = self.upstream(node_id)
                    if result.success:
                        return {
                            "query": question,
                            "type": "dependents",
                            "service": service_name,
                            "dependents": result.data["dependents"],
                            "dependent_count": result.data["dependent_count"]
                        }
        
        return {
            "query": question,
            "type": "dependents",
            "error": "Could not identify service or find dependents"
        }
    
    def _handle_team_query(self, question: str) -> Dict[str, Any]:
        """Handle team-related queries."""
        teams = self.storage.get_nodes_by_type(NodeType.TEAM)
        
        team_info = []
        for team in teams:
            team_services = self.storage.get_team_ownership(team.name)
            team_info.append({
                "name": team.name,
                "lead": team.properties.get("lead", "Unknown"),
                "services_count": len(team_services),
                "slack": team.properties.get("slack_channel", "Unknown")
            })
        
        return {
            "query": question,
            "type": "team_info",
            "teams": team_info,
            "total_teams": len(teams)
        }
    
    def _handle_database_query(self, question: str) -> Dict[str, Any]:
        """Handle database-related queries."""
        databases = self.storage.get_nodes_by_type(NodeType.DATABASE)
        
        db_info = []
        for db in databases:
            db_info.append({
                "id": db.id,
                "name": db.name,
                "type": db.type.value,
                "properties": db.properties
            })
        
        return {
            "query": question,
            "type": "database_info",
            "databases": db_info,
            "total_databases": len(databases)
        }
    
    def _handle_service_query(self, question: str) -> Dict[str, Any]:
        """Handle service-related queries."""
        services = self.storage.get_nodes_by_type(NodeType.SERVICE)
        
        service_info = []
        for service in services:
            service_info.append({
                "id": service.id,
                "name": service.name,
                "type": service.type.value,
                "properties": service.properties
            })
        
        return {
            "query": question,
            "type": "service_info",
            "services": service_info,
            "total_services": len(services)
        }
    
    def _handle_general_query(self, question: str) -> Dict[str, Any]:
        """Handle general queries with system overview."""
        stats = self.storage.get_stats()
        
        return {
            "query": question,
            "type": "general",
            "message": "Here's an overview of the knowledge graph",
            "statistics": stats,
            "suggestions": [
                "Try asking: 'What breaks if order-service goes down?'",
                "Try asking: 'Who owns the payments database?'",
                "Try asking: 'What path connects api-gateway to payments-db?'",
                "Try asking: 'What depends on auth-service?'",
                "Try asking: 'What uses the users database?'"
            ]
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _extract_service_name(self, text: str) -> Optional[str]:
        """Extract service name from text using enhanced patterns."""
        text_lower = text.lower()
        
        patterns = [
            r'(?:service|database|db|cache)(?:\s+called)?\s+([a-z][a-z0-9\-_]*)',
            r'([a-z][a-z0-9\-_]*)[- ](?:service|database|db|cache)',
            r'if\s+([a-z][a-z0-9\-_]*)\s+(?:goes down|fails)',
            r'owns?\s+(?:the\s+)?([a-z][a-z0-9\-_]*)',
            r'connects?\s+to\s+(?:the\s+)?([a-z][a-z0-9\-_]*)',
            r'depends\s+on\s+([a-z][a-z0-9\-_]*)',
            r'([a-z][a-z0-9\-_]*)\s+depends',
            r'uses\s+([a-z][a-z0-9\-_]*)',
            r'([a-z][a-z0-9\-_]*)\s+uses'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                service_name = match.group(1).strip()
                if service_name not in ['the', 'a', 'an', 'this', 'that', 'what', 'how', 'when', 'where']:
                    return service_name
        
        return None
    
    def _extract_multiple_service_names(self, text: str) -> List[str]:
        """Extract multiple service names for path queries."""
        text_lower = text.lower()
        service_names = []
        
        # Pattern for "from X to Y" or "X connects to Y"
        patterns = [
            r'from\s+([a-z][a-z0-9\-_]*)\s+to\s+([a-z][a-z0-9\-_]*)',
            r'([a-z][a-z0-9\-_]*)\s+connects?\s+to\s+([a-z][a-z0-9\-_]*)',
            r'([a-z][a-z0-9\-_]*)\s+and\s+([a-z][a-z0-9\-_]*)',
            r'between\s+([a-z][a-z0-9\-_]*)\s+and\s+([a-z][a-z0-9\-_]*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return [match.group(1).strip(), match.group(2).strip()]
        
        return service_names


# ========================================================================
# BACKWARD COMPATIBILITY
# ========================================================================

# Create an alias for backward compatibility
QueryEngine = AdvancedQueryEngine
