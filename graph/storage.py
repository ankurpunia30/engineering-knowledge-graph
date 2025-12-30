"""
Storage layer for the Engineering Knowledge Graph using NetworkX.
"""
import networkx as nx
import os
from typing import List, Dict, Any, Optional, Set
import json
import pickle
from pathlib import Path

from .models import Node, Edge, KnowledgeGraph, NodeType, EdgeType


class GraphStorage:
    """Storage layer for the knowledge graph using NetworkX."""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.kg = KnowledgeGraph()
    
    def add_node(self, node: Node) -> None:
        """Add a node to the storage."""
        self.kg.add_node(node)
        
        # Avoid 'type' parameter conflict with NetworkX
        node_attrs = {
            'node_type': node.type.value,
            'name': node.name,
            **node.properties
        }
        self.graph.add_node(node.id, **node_attrs)
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the storage."""
        self.kg.add_edge(edge)
        self.graph.add_edge(
            edge.source,
            edge.target,
            key=edge.id,
            edge_type=edge.type.value,  # Changed from 'type' to 'edge_type'
            **edge.properties
        )
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self.kg.get_node(node_id)
    
    def get_all_nodes(self) -> List[Node]:
        """Get all nodes."""
        return list(self.kg.nodes.values())
    
    def get_all_edges(self) -> List[Edge]:
        """Get all edges."""
        return list(self.kg.edges.values())
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """Get all nodes of a specific type."""
        return self.kg.get_nodes_by_type(node_type)
    
    def get_neighbors(self, node_id: str, direction: str = "both") -> List[str]:
        """Get neighboring nodes."""
        if node_id not in self.graph:
            return []
        
        if direction == "out":
            return list(self.graph.successors(node_id))
        elif direction == "in":
            return list(self.graph.predecessors(node_id))
        else:  # both
            return list(set(self.graph.successors(node_id)) | set(self.graph.predecessors(node_id)))
    
    def get_paths(self, source: str, target: str, max_length: int = 5) -> List[List[str]]:
        """Find paths between two nodes."""
        if source not in self.graph or target not in self.graph:
            return []
        
        try:
            paths = list(nx.all_simple_paths(
                self.graph, 
                source, 
                target, 
                cutoff=max_length
            ))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_dependencies(self, node_id: str, depth: int = 1) -> Set[str]:
        """Get all dependencies of a node up to a certain depth."""
        if node_id not in self.graph:
            return set()
        
        dependencies = set()
        current_level = {node_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # Get nodes that this node depends on
                for neighbor in self.graph.predecessors(node):
                    edge_data = self.graph.get_edge_data(neighbor, node)
                    for edge in edge_data.values():
                        if edge.get('edge_type') in ['depends_on', 'uses', 'reads_from', 'writes_to']:
                            next_level.add(neighbor)
                            dependencies.add(neighbor)
            current_level = next_level
        
        return dependencies
    
    def get_dependents(self, node_id: str, depth: int = 1) -> Set[str]:
        """Get all nodes that depend on this node up to a certain depth."""
        if node_id not in self.graph:
            return set()
        
        dependents = set()
        current_level = {node_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # Get nodes that depend on this node
                for neighbor in self.graph.successors(node):
                    edge_data = self.graph.get_edge_data(node, neighbor)
                    for edge in edge_data.values():
                        if edge.get('edge_type') in ['depends_on', 'uses', 'reads_from', 'writes_to']:
                            next_level.add(neighbor)
                            dependents.add(neighbor)
            current_level = next_level
        
        return dependents
    
    def get_team_ownership(self, team_name: str) -> List[Node]:
        """Get all nodes owned by a team."""
        owned_nodes = []
        for node in self.kg.nodes.values():
            if node.properties.get('team') == team_name:
                owned_nodes.append(node)
        return owned_nodes
    
    def find_nodes_by_property(self, property_name: str, property_value: Any) -> List[Node]:
        """Find nodes by property value."""
        matching_nodes = []
        for node in self.kg.nodes.values():
            if node.properties.get(property_name) == property_value:
                matching_nodes.append(node)
        return matching_nodes
    
    def get_blast_radius(self, node_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """Calculate the blast radius if a node goes down."""
        if node_id not in self.graph:
            return {"error": f"Node {node_id} not found"}
        
        # Get all nodes that would be affected
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
    
    def merge_graph(self, other_kg: KnowledgeGraph) -> None:
        """Merge another knowledge graph into this storage."""
        self.kg.merge(other_kg)
        
        # Update NetworkX graph
        for node in other_kg.nodes.values():
            node_attrs = {
                'node_type': node.type.value,
                'name': node.name,
                **node.properties
            }
            self.graph.add_node(node.id, **node_attrs)
        
        for edge in other_kg.edges.values():
            self.graph.add_edge(
                edge.source,
                edge.target,
                key=edge.id,
                edge_type=edge.type.value,
                **edge.properties
            )
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all its connected edges.
        
        Args:
            node_id: The ID of the node to delete
            
        Returns:
            True if node was deleted, False if node didn't exist
        """
        # Check if node exists
        if node_id not in self.kg.nodes:
            return False
        
        # Remove from KnowledgeGraph
        del self.kg.nodes[node_id]
        
        # Remove from NetworkX graph (this automatically removes connected edges)
        if node_id in self.graph:
            self.graph.remove_node(node_id)
        
        # Remove edges from KnowledgeGraph
        edges_to_remove = []
        for edge_id, edge in self.kg.edges.items():
            if edge.source == node_id or edge.target == node_id:
                edges_to_remove.append(edge_id)
        
        for edge_id in edges_to_remove:
            del self.kg.edges[edge_id]
        
        return True
    
    def save_to_file(self, filepath: str) -> bool:
        """Save the knowledge graph to a file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                data = {
                    'nodes': {k: v.dict() for k, v in self.kg.nodes.items()},
                    'edges': {k: v.dict() for k, v in self.kg.edges.items()}
                }
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> None:
        """Load the knowledge graph from a file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.kg = KnowledgeGraph()
        self.graph = nx.MultiDiGraph()
        
        # Load nodes
        for node_data in data['nodes'].values():
            node = Node(**node_data)
            self.add_node(node)
        
        # Load edges
        for edge_data in data['edges'].values():
            edge = Edge(**edge_data)
            self.add_edge(edge)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        node_types = {}
        edge_types = {}
        
        for node in self.kg.nodes.values():
            node_types[node.type.value] = node_types.get(node.type.value, 0) + 1
        
        for edge in self.kg.edges.values():
            edge_types[edge.type.value] = edge_types.get(edge.type.value, 0) + 1
        
        return {
            "total_nodes": len(self.kg.nodes),
            "total_edges": len(self.kg.edges),
            "node_types": node_types,
            "edge_types": edge_types,
            "storage_backend": "networkx",
            "is_connected": nx.is_weakly_connected(self.graph) if self.graph.nodes else False
        }
