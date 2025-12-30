"""
Tests for the graph storage and query engine.
"""
import pytest
from graph.storage import GraphStorage
from graph.query import QueryEngine
from graph.models import Node, Edge, NodeType, EdgeType, KnowledgeGraph


class TestGraphStorage:
    """Test the graph storage functionality."""
    
    def setup_method(self):
        """Setup test data."""
        self.storage = GraphStorage()
        
        # Add test nodes
        self.storage.add_node(Node(
            id="service:web",
            type=NodeType.SERVICE,
            name="web",
            properties={"team": "web-team", "port": 8000}
        ))
        
        self.storage.add_node(Node(
            id="database:db",
            type=NodeType.DATABASE,
            name="db",
            properties={"team": "data-team"}
        ))
        
        self.storage.add_node(Node(
            id="team:web-team",
            type=NodeType.TEAM,
            name="web-team",
            properties={"lead": "@alice"}
        ))
        
        # Add test edges
        self.storage.add_edge(Edge(
            id="edge:web-reads-db",
            type=EdgeType.READS_FROM,
            source="service:web",
            target="database:db"
        ))
    
    def test_add_and_get_nodes(self):
        """Test adding and retrieving nodes."""
        node = self.storage.get_node("service:web")
        assert node is not None
        assert node.name == "web"
        assert node.properties["team"] == "web-team"
    
    def test_get_nodes_by_type(self):
        """Test retrieving nodes by type."""
        services = self.storage.get_nodes_by_type(NodeType.SERVICE)
        assert len(services) == 1
        assert services[0].name == "web"
        
        teams = self.storage.get_nodes_by_type(NodeType.TEAM)
        assert len(teams) == 1
        assert teams[0].name == "web-team"
    
    def test_get_neighbors(self):
        """Test getting neighboring nodes."""
        neighbors = self.storage.get_neighbors("service:web")
        assert "database:db" in neighbors
    
    def test_get_team_ownership(self):
        """Test getting team ownership."""
        owned_nodes = self.storage.get_team_ownership("web-team")
        assert len(owned_nodes) == 1
        assert owned_nodes[0].name == "web"
    
    def test_get_stats(self):
        """Test getting graph statistics."""
        stats = self.storage.get_stats()
        assert stats["total_nodes"] == 3
        assert stats["total_edges"] == 1
        assert stats["node_types"]["service"] == 1
        assert stats["node_types"]["database"] == 1
        assert stats["node_types"]["team"] == 1


class TestQueryEngine:
    """Test the query engine functionality."""
    
    def setup_method(self):
        """Setup test data."""
        self.storage = GraphStorage()
        self.query_engine = QueryEngine(self.storage)
        
        # Create a more complex test graph
        # Services
        self.storage.add_node(Node(
            id="service:order-service",
            type=NodeType.SERVICE,
            name="order-service",
            properties={"team": "orders-team", "oncall": "@dave"}
        ))
        
        self.storage.add_node(Node(
            id="service:payment-service",
            type=NodeType.SERVICE,
            name="payment-service",
            properties={"team": "payments-team", "oncall": "@frank"}
        ))
        
        # Databases
        self.storage.add_node(Node(
            id="database:orders-db",
            type=NodeType.DATABASE,
            name="orders-db",
            properties={"team": "orders-team", "encrypted": "false"}
        ))
        
        self.storage.add_node(Node(
            id="database:payments-db",
            type=NodeType.DATABASE,
            name="payments-db",
            properties={"team": "payments-team", "encrypted": "true"}
        ))
        
        # Teams
        self.storage.add_node(Node(
            id="team:orders-team",
            type=NodeType.TEAM,
            name="orders-team",
            properties={"lead": "@dave", "slack_channel": "#orders"}
        ))
        
        self.storage.add_node(Node(
            id="team:payments-team",
            type=NodeType.TEAM,
            name="payments-team",
            properties={"lead": "@frank", "slack_channel": "#payments"}
        ))
        
        # Edges
        self.storage.add_edge(Edge(
            id="edge:order-calls-payment",
            type=EdgeType.CALLS,
            source="service:order-service",
            target="service:payment-service"
        ))
        
        self.storage.add_edge(Edge(
            id="edge:order-reads-orders-db",
            type=EdgeType.READS_FROM,
            source="service:order-service",
            target="database:orders-db"
        ))
        
        self.storage.add_edge(Edge(
            id="edge:payment-reads-payments-db",
            type=EdgeType.READS_FROM,
            source="service:payment-service",
            target="database:payments-db"
        ))
    
    def test_ownership_query(self):
        """Test ownership queries."""
        response = self.query_engine.query("Who owns order-service?")
        
        assert response["type"] == "ownership"
        assert response["service"] == "order-service"
        assert response["team"] == "orders-team"
        assert response["team_lead"] == "@dave"
    
    def test_connection_query(self):
        """Test connection queries."""
        response = self.query_engine.query("What connects to order-service?")
        
        assert response["type"] == "connection"
        assert response["service"] == "order-service"
        assert len(response["outgoing_connections"]) > 0
    
    def test_team_query(self):
        """Test team queries."""
        response = self.query_engine.query("Show me all teams")
        
        assert response["type"] == "team"
        assert response["total_teams"] == 2
        assert len(response["teams"]) == 2
    
    def test_database_query(self):
        """Test database queries."""
        response = self.query_engine.query("List all databases")
        
        assert response["type"] == "database"
        assert response["total_databases"] == 2
        assert len(response["databases"]) == 2
    
    def test_blast_radius_query(self):
        """Test blast radius queries."""
        response = self.query_engine.query("What breaks if payment-service goes down?")
        
        assert response["type"] == "blast_radius"
        assert response["service_analyzed"] == "payment-service"
        assert "affected_services_count" in response
    
    def test_general_query(self):
        """Test general queries."""
        response = self.query_engine.query("Tell me about the system")
        
        assert response["type"] == "general"
        assert "statistics" in response
        assert "suggestions" in response
