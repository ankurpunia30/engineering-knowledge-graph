"""
Core data models for the Engineering Knowledge Graph.
"""
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
from enum import Enum


class NodeType(str, Enum):
    """Node types in the knowledge graph."""
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    TEAM = "team"
    DEPLOYMENT = "deployment"
    K8S_SERVICE = "k8s_service"


class EdgeType(str, Enum):
    """Edge types in the knowledge graph."""
    CALLS = "calls"
    DEPENDS_ON = "depends_on"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    OWNS = "owns"
    USES = "uses"
    DEPLOYED_AS = "deployed_as"


class Node(BaseModel):
    """Represents a node in the knowledge graph."""
    id: str = Field(..., description="Unique identifier with type prefix")
    type: NodeType = Field(..., description="Type of the node")
    name: str = Field(..., description="Name of the entity")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id


class Edge(BaseModel):
    """Represents an edge in the knowledge graph."""
    id: str = Field(..., description="Unique identifier for the edge")
    type: EdgeType = Field(..., description="Type of the relationship")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Edge) and self.id == other.id


class KnowledgeGraph(BaseModel):
    """Container for the entire knowledge graph."""
    nodes: Dict[str, Node] = Field(default_factory=dict)
    edges: Dict[str, Edge] = Field(default_factory=dict)
    
    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        self.edges[edge.id] = edge
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_edges_from_node(self, node_id: str) -> List[Edge]:
        """Get all edges originating from a node."""
        return [edge for edge in self.edges.values() if edge.source == node_id]
    
    def get_edges_to_node(self, node_id: str) -> List[Edge]:
        """Get all edges pointing to a node."""
        return [edge for edge in self.edges.values() if edge.target == node_id]
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """Get all nodes of a specific type."""
        return [node for node in self.nodes.values() if node.type == node_type]
    
    def merge(self, other: 'KnowledgeGraph') -> None:
        """Merge another knowledge graph into this one."""
        for node in other.nodes.values():
            if node.id in self.nodes:
                # Merge properties
                existing_node = self.nodes[node.id]
                existing_node.properties.update(node.properties)
            else:
                self.add_node(node)
        
        for edge in other.edges.values():
            if edge.id not in self.edges:
                self.add_edge(edge)
