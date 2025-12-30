#!/usr/bin/env python3
"""
Test script to verify all Part 2 Graph Storage requirements.
Run this to confirm all storage layer functionality works correctly.
"""

import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.storage import GraphStorage
from graph.models import Node, Edge, NodeType, EdgeType


def test_store_nodes_and_edges():
    """Requirement 1: Store nodes and edges from connector output"""
    print("Testing: Store nodes and edges...")
    storage = GraphStorage()
    
    # Add nodes
    node1 = Node(id="service:api", name="api", type=NodeType.SERVICE, properties={"team": "platform"})
    node2 = Node(id="database:users", name="users-db", type=NodeType.DATABASE)
    storage.add_node(node1)
    storage.add_node(node2)
    
    # Add edge
    edge = Edge(id="edge1", source="service:api", target="database:users", type=EdgeType.USES)
    storage.add_edge(edge)
    
    # Verify
    assert len(storage.get_all_nodes()) == 2, "Should have 2 nodes"
    assert len(storage.get_all_edges()) == 1, "Should have 1 edge"
    print("✅ PASS: Store nodes and edges")


def test_upsert_behavior():
    """Requirement 2a: Add/update nodes and edges (upsert behavior)"""
    print("\nTesting: Upsert behavior...")
    storage = GraphStorage()
    
    # Add node
    node1 = Node(id="service:api", name="api-v1", type=NodeType.SERVICE)
    storage.add_node(node1)
    
    # Update same node (upsert)
    node2 = Node(id="service:api", name="api-v2", type=NodeType.SERVICE)
    storage.add_node(node2)
    
    # Verify only one node exists with updated name
    all_nodes = storage.get_all_nodes()
    api_nodes = [n for n in all_nodes if n.id == "service:api"]
    
    assert len(api_nodes) == 1, "Should have exactly 1 node (upserted, not duplicated)"
    assert api_nodes[0].name == "api-v2", "Node should be updated to api-v2"
    print("✅ PASS: Upsert behavior")


def test_retrieve_by_id():
    """Requirement 2b: Retrieve by ID"""
    print("\nTesting: Retrieve by ID...")
    storage = GraphStorage()
    
    # Add nodes
    storage.add_node(Node(id="service:api", name="api", type=NodeType.SERVICE))
    storage.add_node(Node(id="database:users", name="users-db", type=NodeType.DATABASE))
    
    # Retrieve by ID
    api_node = storage.get_node("service:api")
    users_db = storage.get_node("database:users")
    nonexistent = storage.get_node("service:nonexistent")
    
    # Verify
    assert api_node is not None, "Should find api node"
    assert api_node.name == "api", "Should retrieve correct node"
    assert users_db is not None, "Should find database node"
    assert nonexistent is None, "Should return None for nonexistent node"
    print("✅ PASS: Retrieve by ID")


def test_retrieve_by_type():
    """Requirement 2c: Retrieve by type"""
    print("\nTesting: Retrieve by type...")
    storage = GraphStorage()
    
    # Add various types
    storage.add_node(Node(id="service:api", name="api", type=NodeType.SERVICE))
    storage.add_node(Node(id="service:auth", name="auth", type=NodeType.SERVICE))
    storage.add_node(Node(id="database:users", name="users-db", type=NodeType.DATABASE))
    storage.add_node(Node(id="cache:redis", name="redis", type=NodeType.CACHE))
    storage.add_node(Node(id="team:platform", name="platform", type=NodeType.TEAM))
    
    # Retrieve by type
    services = storage.get_nodes_by_type(NodeType.SERVICE)
    databases = storage.get_nodes_by_type(NodeType.DATABASE)
    caches = storage.get_nodes_by_type(NodeType.CACHE)
    teams = storage.get_nodes_by_type(NodeType.TEAM)
    
    # Verify
    assert len(services) == 2, "Should have 2 services"
    assert len(databases) == 1, "Should have 1 database"
    assert len(caches) == 1, "Should have 1 cache"
    assert len(teams) == 1, "Should have 1 team"
    
    # Verify correct nodes returned
    service_names = {n.name for n in services}
    assert service_names == {"api", "auth"}, "Should return correct service nodes"
    print("✅ PASS: Retrieve by type")


def test_delete_node_with_edges():
    """Requirement 2d: Delete node (and its connected edges)"""
    print("\nTesting: Delete node with connected edges...")
    storage = GraphStorage()
    
    # Create nodes
    storage.add_node(Node(id="service:api", name="api", type=NodeType.SERVICE))
    storage.add_node(Node(id="database:users", name="users", type=NodeType.DATABASE))
    storage.add_node(Node(id="service:auth", name="auth", type=NodeType.SERVICE))
    
    # Create edges
    storage.add_edge(Edge(id="edge1", source="service:api", target="database:users", type=EdgeType.USES))
    storage.add_edge(Edge(id="edge2", source="service:api", target="service:auth", type=EdgeType.DEPENDS_ON))
    storage.add_edge(Edge(id="edge3", source="service:auth", target="database:users", type=EdgeType.USES))
    
    # Verify initial state
    assert len(storage.get_all_nodes()) == 3, "Should have 3 nodes"
    assert len(storage.get_all_edges()) == 3, "Should have 3 edges"
    
    # Delete api node
    result = storage.delete_node("service:api")
    assert result == True, "Delete should return True"
    
    # Verify node is gone
    assert storage.get_node("service:api") is None, "Node should be deleted"
    assert len(storage.get_all_nodes()) == 2, "Should have 2 nodes remaining"
    
    # Verify connected edges are gone
    remaining_edges = storage.get_all_edges()
    assert len(remaining_edges) == 1, "Should have 1 edge remaining (only edge3)"
    assert remaining_edges[0].id == "edge3", "Only edge3 should remain"
    
    # Test deleting nonexistent node
    result = storage.delete_node("service:nonexistent")
    assert result == False, "Deleting nonexistent node should return False"
    
    print("✅ PASS: Delete node with cascade")


def test_persist_to_disk():
    """Requirement 3: Persist to disk (survives restart)"""
    print("\nTesting: Persist to disk...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        filepath = f.name
    
    try:
        # Create and populate storage
        storage1 = GraphStorage()
        storage1.add_node(Node(id="service:api", name="api", type=NodeType.SERVICE, 
                              properties={"team": "platform", "language": "python"}))
        storage1.add_node(Node(id="database:users", name="users-db", type=NodeType.DATABASE))
        storage1.add_edge(Edge(id="edge1", source="service:api", target="database:users", 
                              type=EdgeType.USES))
        
        # Save to file
        save_result = storage1.save_to_file(filepath)
        assert save_result == True, "Save should return True"
        assert os.path.exists(filepath), "File should exist"
        
        # Simulate restart - create new storage and load
        storage2 = GraphStorage()
        storage2.load_from_file(filepath)
        
        # Verify data persisted
        assert len(storage2.get_all_nodes()) == 2, "Should have 2 nodes after load"
        assert len(storage2.get_all_edges()) == 1, "Should have 1 edge after load"
        
        # Verify node details
        api_node = storage2.get_node("service:api")
        assert api_node is not None, "API node should exist"
        assert api_node.name == "api", "Node name should match"
        assert api_node.properties.get("team") == "platform", "Properties should be preserved"
        assert api_node.properties.get("language") == "python", "All properties should persist"
        
        # Verify edge details
        edges = storage2.get_all_edges()
        assert edges[0].source == "service:api", "Edge source should match"
        assert edges[0].target == "database:users", "Edge target should match"
        
        print("✅ PASS: Persist to disk (survives restart)")
        
    finally:
        # Cleanup
        if os.path.exists(filepath):
            os.unlink(filepath)


def run_all_tests():
    """Run all Part 2 requirement tests"""
    print("=" * 60)
    print("Part 2: Graph Storage - Requirements Verification")
    print("=" * 60)
    
    tests = [
        test_store_nodes_and_edges,
        test_upsert_behavior,
        test_retrieve_by_id,
        test_retrieve_by_type,
        test_delete_node_with_edges,
        test_persist_to_disk
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
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ALL PART 2 REQUIREMENTS VERIFIED!")
        print("\n✅ Requirements Met:")
        print("   1. Store nodes and edges from connector output")
        print("   2. Add/update nodes and edges (upsert behavior)")
        print("   3. Retrieve by ID")
        print("   4. Retrieve by type")
        print("   5. Delete node (and its connected edges)")
        print("   6. Persist to disk (survives restart)")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
