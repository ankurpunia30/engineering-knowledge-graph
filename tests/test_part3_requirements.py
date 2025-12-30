"""
Part 3: Query Engine - Requirements Verification

This script tests all Part 3 requirements to ensure the query engine
implementation is complete and correct.

Part 3 Requirements:
1. get_node(id) - Retrieve single node by ID
2. get_nodes(type, filters) - List nodes by type and property filters
3. downstream(node_id) - Find transitive dependencies
4. upstream(node_id) - Find transitive dependents
5. blast_radius(node_id) - Impact analysis (upstream + downstream + teams)
6. path(from_id, to_id) - Find shortest path between two nodes
7. get_owner(node_id) - Get owning team/person

Additional Requirements:
- Handle cycles in the graph
- Support edge type filtering
- Performance considerations for large graphs
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.storage import GraphStorage
from graph.advanced_query import AdvancedQueryEngine, QueryType
from graph.models import Node, Edge, NodeType, EdgeType


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_get_node():
    """Requirement 1: get_node(id) - Retrieve single node by ID"""
    print("\nTesting: get_node(id)...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Add test node
    node = Node(
        id="service:payment-api",
        name="Payment API",
        type=NodeType.SERVICE,
        properties={"team": "payments", "language": "python"}
    )
    storage.add_node(node)
    
    # Test successful retrieval
    result = engine.get_node("service:payment-api")
    assert result.success, "Should successfully retrieve node"
    assert result.query_type == QueryType.GET_NODE
    assert result.data["id"] == "service:payment-api"
    assert result.data["name"] == "Payment API"
    assert result.data["type"] == "service"
    assert result.data["properties"]["team"] == "payments"
    assert result.execution_time_ms > 0
    
    # Test non-existent node
    result = engine.get_node("service:nonexistent")
    assert not result.success, "Should fail for non-existent node"
    assert "not found" in result.error.lower()
    
    print("✅ PASS: get_node(id)")


def test_get_nodes():
    """Requirement 2: get_nodes(type, filters) - List nodes by type and filters"""
    print("\nTesting: get_nodes(type, filters)...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Add test nodes
    storage.add_node(Node(id="service:api1", name="API 1", type=NodeType.SERVICE,
                         properties={"team": "payments", "env": "prod"}))
    storage.add_node(Node(id="service:api2", name="API 2", type=NodeType.SERVICE,
                         properties={"team": "payments", "env": "staging"}))
    storage.add_node(Node(id="database:db1", name="DB 1", type=NodeType.DATABASE,
                         properties={"team": "payments", "env": "prod"}))
    storage.add_node(Node(id="service:api3", name="API 3", type=NodeType.SERVICE,
                         properties={"team": "orders", "env": "prod"}))
    
    # Test 1: Get all nodes of a specific type
    result = engine.get_nodes(node_type="service")
    assert result.success
    assert result.data["total_count"] == 3
    assert all(node["type"] == "service" for node in result.data["nodes"])
    
    # Test 2: Get nodes with property filters
    result = engine.get_nodes(filters={"team": "payments"})
    assert result.success
    assert result.data["total_count"] == 3
    
    # Test 3: Combine type and filters
    result = engine.get_nodes(node_type="service", filters={"team": "payments", "env": "prod"})
    assert result.success
    assert result.data["total_count"] == 1
    assert result.data["nodes"][0]["id"] == "service:api1"
    
    # Test 4: Apply limit
    result = engine.get_nodes(node_type="service", limit=2)
    assert result.success
    assert result.data["total_count"] == 2
    
    print("✅ PASS: get_nodes(type, filters)")


def test_downstream():
    """Requirement 3: downstream(node_id) - Find transitive dependencies"""
    print("\nTesting: downstream(node_id)...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create dependency chain: service -> cache -> database
    storage.add_node(Node(id="service:api", name="API", type=NodeType.SERVICE))
    storage.add_node(Node(id="cache:redis", name="Redis", type=NodeType.CACHE))
    storage.add_node(Node(id="database:postgres", name="Postgres", type=NodeType.DATABASE))
    
    storage.add_edge(Edge(id="e1", source="service:api", target="cache:redis", type=EdgeType.USES))
    storage.add_edge(Edge(id="e2", source="cache:redis", target="database:postgres", type=EdgeType.USES))
    
    # Test transitive dependencies
    result = engine.downstream("service:api")
    assert result.success
    assert result.query_type == QueryType.DOWNSTREAM
    assert result.data["dependency_count"] == 2
    assert "cache:redis" in result.data["dependency_ids"]
    assert "database:postgres" in result.data["dependency_ids"]
    assert len(result.data["dependencies"]) == 2
    
    # Test edge type filtering
    storage.add_edge(Edge(id="e3", source="service:api", target="database:postgres", type=EdgeType.CALLS))
    result = engine.downstream("service:api", edge_types=["calls"])
    assert result.success
    assert result.data["dependency_count"] == 1
    assert "database:postgres" in result.data["dependency_ids"]
    
    print("✅ PASS: downstream(node_id)")


def test_upstream():
    """Requirement 4: upstream(node_id) - Find transitive dependents"""
    print("\nTesting: upstream(node_id)...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create dependency chain: api-gateway -> service -> database
    storage.add_node(Node(id="service:gateway", name="Gateway", type=NodeType.SERVICE))
    storage.add_node(Node(id="service:api", name="API", type=NodeType.SERVICE))
    storage.add_node(Node(id="database:postgres", name="Postgres", type=NodeType.DATABASE))
    
    storage.add_edge(Edge(id="e1", source="service:gateway", target="service:api", type=EdgeType.CALLS))
    storage.add_edge(Edge(id="e2", source="service:api", target="database:postgres", type=EdgeType.USES))
    
    # Test transitive dependents
    result = engine.upstream("database:postgres")
    assert result.success
    assert result.query_type == QueryType.UPSTREAM
    assert result.data["dependent_count"] == 2
    assert "service:api" in result.data["dependent_ids"]
    assert "service:gateway" in result.data["dependent_ids"]
    
    print("✅ PASS: upstream(node_id)")


def test_blast_radius():
    """Requirement 5: blast_radius(node_id) - Impact analysis"""
    print("\nTesting: blast_radius(node_id)...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create a complex dependency graph
    storage.add_node(Node(id="service:payment", name="Payment Service", type=NodeType.SERVICE,
                         properties={"team": "payments"}))
    storage.add_node(Node(id="service:order", name="Order Service", type=NodeType.SERVICE,
                         properties={"team": "orders"}))
    storage.add_node(Node(id="database:payments", name="Payments DB", type=NodeType.DATABASE,
                         properties={"team": "payments"}))
    storage.add_node(Node(id="service:billing", name="Billing Service", type=NodeType.SERVICE,
                         properties={"team": "billing"}))
    
    # Add team nodes
    storage.add_node(Node(id="team:payments", name="Payments Team", type=NodeType.TEAM,
                         properties={"lead": "Alice", "slack_channel": "#payments"}))
    storage.add_node(Node(id="team:orders", name="Orders Team", type=NodeType.TEAM,
                         properties={"lead": "Bob", "slack_channel": "#orders"}))
    
    # Create dependencies
    storage.add_edge(Edge(id="e1", source="service:order", target="service:payment", type=EdgeType.CALLS))
    storage.add_edge(Edge(id="e2", source="service:payment", target="database:payments", type=EdgeType.USES))
    storage.add_edge(Edge(id="e3", source="service:billing", target="database:payments", type=EdgeType.USES))
    
    # Test blast radius
    result = engine.blast_radius("service:payment")
    assert result.success
    assert result.query_type == QueryType.BLAST_RADIUS
    assert result.data["total_affected"] > 0
    assert result.data["upstream_affected"] >= 1  # order service
    assert result.data["downstream_affected"] >= 1  # database
    assert "severity" in result.data
    
    print("✅ PASS: blast_radius(node_id)")


def test_path():
    """Requirement 6: path(from_id, to_id) - Find shortest path"""
    print("\nTesting: path(from_id, to_id)...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create a path: gateway -> api -> cache -> database
    storage.add_node(Node(id="service:gateway", name="Gateway", type=NodeType.SERVICE))
    storage.add_node(Node(id="service:api", name="API", type=NodeType.SERVICE))
    storage.add_node(Node(id="cache:redis", name="Redis", type=NodeType.CACHE))
    storage.add_node(Node(id="database:postgres", name="Postgres", type=NodeType.DATABASE))
    
    storage.add_edge(Edge(id="e1", source="service:gateway", target="service:api", type=EdgeType.CALLS))
    storage.add_edge(Edge(id="e2", source="service:api", target="cache:redis", type=EdgeType.USES))
    storage.add_edge(Edge(id="e3", source="cache:redis", target="database:postgres", type=EdgeType.USES))
    
    # Test path finding
    result = engine.path("service:gateway", "database:postgres")
    assert result.success
    assert result.query_type == QueryType.PATH
    assert result.data["path_length"] == 4
    assert result.data["path_details"][0]["id"] == "service:gateway"
    assert result.data["path_details"][-1]["id"] == "database:postgres"
    
    # Test no path exists
    storage.add_node(Node(id="service:isolated", name="Isolated", type=NodeType.SERVICE))
    result = engine.path("service:gateway", "service:isolated")
    assert not result.success
    assert "no path" in result.error.lower()
    
    print("✅ PASS: path(from_id, to_id)")


def test_get_owner():
    """Requirement 7: get_owner(node_id) - Get owning team/person"""
    print("\nTesting: get_owner(node_id)...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create service with team ownership
    storage.add_node(Node(id="service:payment", name="Payment API", type=NodeType.SERVICE,
                         properties={"team": "payments", "owner": "alice@company.com"}))
    storage.add_node(Node(id="team:payments", name="Payments Team", type=NodeType.TEAM,
                         properties={"lead": "Alice Smith", "slack_channel": "#payments",
                                   "oncall": "payments-oncall@company.com"}))
    
    # Link service to team
    storage.add_edge(Edge(id="e1", source="team:payments", target="service:payment", type=EdgeType.OWNS))
    
    # Test owner retrieval
    result = engine.get_owner("service:payment")
    assert result.success
    assert result.query_type == QueryType.GET_OWNER
    assert result.data["ownership_type"] == "team"
    assert result.data["node"]["id"] == "service:payment"
    assert result.data["owner"]["name"] == "payments"
    assert result.data["owner"]["lead"] == "Alice Smith"
    assert result.data["owner"]["slack_channel"] == "#payments"
    
    print("✅ PASS: get_owner(node_id)")


def test_cycle_handling():
    """Additional Requirement: Handle cycles in the graph"""
    print("\nTesting: Cycle handling...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create a cycle: A -> B -> C -> A
    storage.add_node(Node(id="service:a", name="Service A", type=NodeType.SERVICE))
    storage.add_node(Node(id="service:b", name="Service B", type=NodeType.SERVICE))
    storage.add_node(Node(id="service:c", name="Service C", type=NodeType.SERVICE))
    
    storage.add_edge(Edge(id="e1", source="service:a", target="service:b", type=EdgeType.CALLS))
    storage.add_edge(Edge(id="e2", source="service:b", target="service:c", type=EdgeType.CALLS))
    storage.add_edge(Edge(id="e3", source="service:c", target="service:a", type=EdgeType.CALLS))  # Creates cycle
    
    # Test that downstream handles cycles without infinite loop
    result = engine.downstream("service:a", max_depth=10)
    assert result.success, "Should handle cycles without infinite loop"
    assert result.data["dependency_count"] == 2  # B and C
    assert "service:b" in result.data["dependency_ids"]
    assert "service:c" in result.data["dependency_ids"]
    
    # Test upstream with cycles
    result = engine.upstream("service:a", max_depth=10)
    assert result.success
    assert result.data["dependent_count"] == 2  # B and C depend on A (through the cycle)
    
    print("✅ PASS: Cycle handling")


def test_edge_type_filtering():
    """Additional Requirement: Support edge type filtering"""
    print("\nTesting: Edge type filtering...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create nodes with different edge types
    storage.add_node(Node(id="service:api", name="API", type=NodeType.SERVICE))
    storage.add_node(Node(id="database:postgres", name="Postgres", type=NodeType.DATABASE))
    storage.add_node(Node(id="cache:redis", name="Redis", type=NodeType.CACHE))
    storage.add_node(Node(id="service:worker", name="Worker", type=NodeType.SERVICE))
    
    storage.add_edge(Edge(id="e1", source="service:api", target="database:postgres", type=EdgeType.USES))
    storage.add_edge(Edge(id="e2", source="service:api", target="cache:redis", type=EdgeType.USES))
    storage.add_edge(Edge(id="e3", source="service:api", target="service:worker", type=EdgeType.CALLS))
    
    # Test filtering by edge type
    result = engine.downstream("service:api", edge_types=["uses"])
    assert result.success
    assert result.data["dependency_count"] == 2
    assert "database:postgres" in result.data["dependency_ids"]
    assert "cache:redis" in result.data["dependency_ids"]
    assert "service:worker" not in result.data["dependency_ids"]
    
    # Test with different edge type
    result = engine.downstream("service:api", edge_types=["calls"])
    assert result.success
    assert result.data["dependency_count"] == 1
    assert "service:worker" in result.data["dependency_ids"]
    
    # Test with multiple edge types
    result = engine.downstream("service:api", edge_types=["uses", "calls"])
    assert result.success
    assert result.data["dependency_count"] == 3
    
    print("✅ PASS: Edge type filtering")


def test_performance():
    """Additional Requirement: Performance considerations"""
    print("\nTesting: Performance with larger graph...")
    
    storage = GraphStorage()
    engine = AdvancedQueryEngine(storage)
    
    # Create a larger graph (100 nodes, 200 edges)
    num_services = 50
    num_databases = 25
    num_caches = 25
    
    for i in range(num_services):
        storage.add_node(Node(
            id=f"service:svc{i}",
            name=f"Service {i}",
            type=NodeType.SERVICE,
            properties={"team": f"team{i % 5}"}
        ))
    
    for i in range(num_databases):
        storage.add_node(Node(
            id=f"database:db{i}",
            name=f"Database {i}",
            type=NodeType.DATABASE
        ))
    
    for i in range(num_caches):
        storage.add_node(Node(
            id=f"cache:cache{i}",
            name=f"Cache {i}",
            type=NodeType.CACHE
        ))
    
    # Create edges
    edge_count = 0
    for i in range(num_services):
        # Each service depends on 2-3 databases/caches
        for j in range(2):
            storage.add_edge(Edge(
                id=f"e{edge_count}",
                source=f"service:svc{i}",
                target=f"database:db{j}",
                type=EdgeType.USES
            ))
            edge_count += 1
        
        if i % 2 == 0:
            storage.add_edge(Edge(
                id=f"e{edge_count}",
                source=f"service:svc{i}",
                target=f"cache:cache{i % num_caches}",
                type=EdgeType.USES
            ))
            edge_count += 1
    
    # Test performance of queries
    result = engine.get_nodes(node_type="service")
    assert result.success
    assert result.execution_time_ms < 1000, f"get_nodes took {result.execution_time_ms}ms (should be < 1000ms)"
    
    result = engine.downstream("service:svc0", max_depth=5)
    assert result.success
    assert result.execution_time_ms < 2000, f"downstream took {result.execution_time_ms}ms (should be < 2000ms)"
    
    result = engine.blast_radius("service:svc0", max_depth=3)
    assert result.success
    assert result.execution_time_ms < 3000, f"blast_radius took {result.execution_time_ms}ms (should be < 3000ms)"
    
    print(f"✅ PASS: Performance (graph with {num_services + num_databases + num_caches} nodes, {edge_count} edges)")


def run_all_tests():
    """Run all Part 3 requirement tests."""
    print_section("Part 3: Query Engine - Requirements Verification")
    
    tests = [
        test_get_node,
        test_get_nodes,
        test_downstream,
        test_upstream,
        test_blast_radius,
        test_path,
        test_get_owner,
        test_cycle_handling,
        test_edge_type_filtering,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
    
    print_section(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL PART 3 REQUIREMENTS VERIFIED!")
        print("\n✅ Core Query Methods (7/7):")
        print("   1. get_node(id)")
        print("   2. get_nodes(type, filters)")
        print("   3. downstream(node_id)")
        print("   4. upstream(node_id)")
        print("   5. blast_radius(node_id)")
        print("   6. path(from_id, to_id)")
        print("   7. get_owner(node_id)")
        print("\n✅ Additional Requirements:")
        print("   - Cycle handling with max_depth")
        print("   - Edge type filtering")
        print("   - Performance optimizations")
        print("\n" + "=" * 60)
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
