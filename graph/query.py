"""
Query engine for the Engineering Knowledge Graph.

This module provides natural language query capabilities for the graph,
enabling users to ask questions about services, dependencies, teams, and more.

This module now uses the AdvancedQueryEngine for Part 3 functionality while 
maintaining backward compatibility with existing natural language queries.
"""
from typing import List, Dict, Any, Optional, Set, Union
import re
from graph.storage import GraphStorage
from graph.models import Node, Edge, NodeType, EdgeType
from .advanced_query import AdvancedQueryEngine, QueryResult, QueryType


class QueryEngine:
    """
    Natural language query engine for the knowledge graph.
    
    This class provides backward compatibility with existing natural language queries
    while offering access to advanced Part 3 query methods through the underlying
    AdvancedQueryEngine.
    """
    
    def __init__(self, storage: GraphStorage):
        self.storage = storage
        self.advanced_engine = AdvancedQueryEngine(storage)
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process a natural language query and return results (legacy method)."""
        return self.advanced_engine.query(question)
    
    # ========================================================================
    # PART 3 QUERY METHODS - Direct access to advanced functionality
    # ========================================================================
    
    def get_node(self, node_id: str) -> QueryResult:
        """Retrieve single node by ID."""
        return self.advanced_engine.get_node(node_id)
    
    def get_nodes(self, 
                  node_type: Optional[Union[str, NodeType]] = None,
                  filters: Optional[Dict[str, Any]] = None,
                  limit: Optional[int] = None) -> QueryResult:
        """List nodes by type and filters."""
        return self.advanced_engine.get_nodes(node_type, filters, limit)
    
    def downstream(self, 
                   node_id: str, 
                   max_depth: int = 10,
                   edge_types: Optional[List[Union[str, EdgeType]]] = None) -> QueryResult:
        """Find all transitive dependencies (what this node depends on)."""
        return self.advanced_engine.downstream(node_id, max_depth, edge_types)
    
    def upstream(self, 
                 node_id: str, 
                 max_depth: int = 10,
                 edge_types: Optional[List[Union[str, EdgeType]]] = None) -> QueryResult:
        """Find all transitive dependents (what depends on this node)."""
        return self.advanced_engine.upstream(node_id, max_depth, edge_types)
    
    def blast_radius(self, node_id: str, max_depth: int = 5) -> QueryResult:
        """Comprehensive impact analysis - upstream + downstream + team impact."""
        return self.advanced_engine.blast_radius(node_id, max_depth)
    
    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> QueryResult:
        """Find shortest path between two nodes."""
        return self.advanced_engine.path(from_id, to_id, max_depth)
    
    def get_owner(self, node_id: str) -> QueryResult:
        """Find the owning team for a node."""
        return self.advanced_engine.get_owner(node_id)
    
    # ========================================================================
    # LEGACY METHODS - Maintained for backward compatibility
    # ========================================================================
    
    def _handle_blast_radius_query(self, question: str) -> Dict[str, Any]:
        """Legacy blast radius handler - now uses advanced engine."""
        return self.advanced_engine._handle_blast_radius_query(question)
    
    def _handle_ownership_query(self, question: str) -> Dict[str, Any]:
        """Legacy ownership handler."""
        return self.advanced_engine._handle_ownership_query(question)
    
    def _handle_connection_query(self, question: str) -> Dict[str, Any]:
        """Legacy connection handler - now uses path finding."""
        return self.advanced_engine._handle_path_query(question)
    
    def _handle_team_query(self, question: str) -> Dict[str, Any]:
        """Legacy team handler."""
        return self.advanced_engine._handle_team_query(question)
    
    def _handle_database_query(self, question: str) -> Dict[str, Any]:
        """Legacy database handler."""
        return self.advanced_engine._handle_database_query(question)
    
    def _get_blast_radius(self, service_name: str, visited: Optional[Set[str]] = None, 
                         max_depth: int = 5, current_depth: int = 0) -> Set[str]:
        """Legacy blast radius calculation - now uses advanced engine."""
        if visited is None:
            visited = set()
        
        # Use advanced engine for better performance and cycle detection
        result = self.advanced_engine.blast_radius(f"service:{service_name}", max_depth)
        if result.success:
            return set(result.data["all_affected_ids"])
        return set()
    
    def _extract_service_name(self, text: str) -> Optional[str]:
        """Extract service name from text."""
        return self.advanced_engine._extract_service_name(text)
    
    def _extract_team_name(self, text: str) -> Optional[str]:
        """Extract team name from text using patterns."""
        text_lower = text.lower()
        
        # Look for team name patterns
        patterns = [
            r'team\s+([a-z][a-z0-9\-_]*)',
            r'([a-z][a-z0-9\-_]*)\s+team',
            r'owns\s+([a-z][a-z0-9\-_]*)',
            r'([a-z][a-z0-9\-_]*)\s+owns'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                team_name = match.group(1).strip()
                if team_name not in ['the', 'a', 'an', 'this', 'that', 'what', 'how', 'when', 'where']:
                    return team_name
        return None
