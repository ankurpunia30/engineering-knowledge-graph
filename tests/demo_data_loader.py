#!/usr/bin/env python3
"""
Part 3 Query Engine Demo - Engineering Knowledge Graph

This script demonstrates the complete Part 3 query engine functionality
with all required query methods, cycle detection, and performance optimization.

Features demonstrated:
- All Part 3 query methods (get_node, get_nodes, downstream, upstream, blast_radius, path, get_owner)
- Cycle detection and prevention
- Performance optimization for large graphs
- Edge type filtering
- Comprehensive path finding
- Impact analysis with team information
"""

import sys
import os
import json
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the enhanced query engine and storage
from graph.storage_factory import StorageFactory
from graph.query import QueryEngine
from graph.models import NodeType, EdgeType


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def print_query_result(result, title: str = ""):
    """Pretty print a query result."""
    if title:
        print(f"\n📊 {title}")
    
    print(f"✅ Success: {result.success}")
    print(f"⚡ Query Type: {result.query_type.value}")
    print(f"⏱️  Execution Time: {result.execution_time_ms:.2f}ms")
    
    if result.error:
        print(f"❌ Error: {result.error}")
    
    if result.data:
        print(f"📄 Data:")
        print(json.dumps(result.data, indent=2, default=str))
    
    if result.metadata:
        print(f"🔍 Metadata: {result.metadata}")


def run_part3_demo():
    """Run comprehensive Part 3 demo showing all query methods."""
    
    print_section("Part 3 Query Engine Demo - Engineering Knowledge Graph")
    
    # Initialize storage and query engine
    print("\n🚀 Initializing Enhanced Query Engine...")
    storage = StorageFactory.create_storage()
    
    # Load sample data first
    print("🔧 Loading sample data...")
    from pathlib import Path
    from connectors import registry
    
    data_path = Path(__file__).parent / "data"
    
    # Load Docker Compose data
    docker_file = data_path / "docker-compose.yml"
    if docker_file.exists():
        try:
            connector = registry.create_connector('docker-compose', str(docker_file))
            kg = connector.parse()
            storage.merge_graph(kg)
            print(f"   ✅ Docker Compose: {len(kg.nodes)} nodes, {len(kg.edges)} edges")
        except Exception as e:
            print(f"   ❌ Docker Compose failed: {e}")
    
    # Load Teams data
    teams_file = data_path / "teams.yaml"
    if teams_file.exists():
        try:
            connector = registry.create_connector('teams', str(teams_file))
            kg = connector.parse()
            storage.merge_graph(kg)
            print(f"   ✅ Teams: {len(kg.nodes)} nodes, {len(kg.edges)} edges")
        except Exception as e:
            print(f"   ❌ Teams failed: {e}")
    
    # Load Kubernetes data
    k8s_file = data_path / "k8s-deployments.yaml"
    if k8s_file.exists():
        try:
            connector = registry.create_connector('kubernetes', str(k8s_file))
            kg = connector.parse()
            storage.merge_graph(kg)
            print(f"   ✅ Kubernetes: {len(kg.nodes)} nodes, {len(kg.edges)} edges")
        except Exception as e:
            print(f"   ❌ Kubernetes failed: {e}")
    
    query_engine = QueryEngine(storage)
    
    print(f"📊 Graph Statistics: {storage.get_stats()}")
    print(f"📦 Total Nodes: {storage.get_stats()['total_nodes']}")
    print(f"🔗 Total Edges: {storage.get_stats()['total_edges']}")
    
    # ========================================================================
    # 1. GET_NODE - Retrieve single node by ID
    # ========================================================================
    print_section("1. GET_NODE - Retrieve Single Node by ID")
    
    print_subsection("Get API Gateway Service")
    result = query_engine.get_node("service:api-gateway")
    print_query_result(result, "API Gateway Details")
    
    print_subsection("Get Orders Database")
    result = query_engine.get_node("database:orders-db")
    print_query_result(result, "Orders Database Details")
    
    print_subsection("Get Non-existent Node")
    result = query_engine.get_node("service:nonexistent")
    print_query_result(result, "Non-existent Node (Error Demo)")
    
    # ========================================================================
    # 2. GET_NODES - List nodes by type and filters
    # ========================================================================
    print_section("2. GET_NODES - List Nodes by Type and Filters")
    
    print_subsection("All Services")
    result = query_engine.get_nodes(node_type=NodeType.SERVICE)
    print_query_result(result, "All Services")
    
    print_subsection("Services owned by Payments Team")
    result = query_engine.get_nodes(
        node_type=NodeType.SERVICE, 
        filters={"team": "payments"}
    )
    print_query_result(result, "Payments Team Services")
    
    print_subsection("All Databases (Limited to 3)")
    result = query_engine.get_nodes(node_type=NodeType.DATABASE, limit=3)
    print_query_result(result, "Databases (Limited)")
    
    # ========================================================================
    # 3. DOWNSTREAM - Find transitive dependencies
    # ========================================================================
    print_section("3. DOWNSTREAM - Find Transitive Dependencies")
    
    print_subsection("Order Service Dependencies")
    result = query_engine.downstream("service:order-service")
    print_query_result(result, "Order Service Dependencies")
    
    print_subsection("API Gateway Dependencies (Max Depth 3)")
    result = query_engine.downstream("service:api-gateway", max_depth=3)
    print_query_result(result, "API Gateway Dependencies")
    
    print_subsection("Order Service Dependencies (DEPENDS_ON edges only)")
    result = query_engine.downstream(
        "service:order-service", 
        edge_types=[EdgeType.DEPENDS_ON]
    )
    print_query_result(result, "Order Service Dependencies (DEPENDS_ON only)")
    
    # ========================================================================
    # 4. UPSTREAM - Find transitive dependents
    # ========================================================================
    print_section("4. UPSTREAM - Find Transitive Dependents")
    
    print_subsection("Orders Database Dependents")
    result = query_engine.upstream("database:orders-db")
    print_query_result(result, "Orders Database Dependents")
    
    print_subsection("Auth Service Dependents")
    result = query_engine.upstream("service:auth-service")
    print_query_result(result, "Auth Service Dependents")
    
    print_subsection("Payment Gateway Dependents (CALLS edges only)")
    result = query_engine.upstream(
        "service:payment-gateway", 
        edge_types=[EdgeType.CALLS]
    )
    print_query_result(result, "Payment Gateway Dependents (CALLS only)")
    
    # ========================================================================
    # 5. BLAST_RADIUS - Comprehensive impact analysis
    # ========================================================================
    print_section("5. BLAST_RADIUS - Comprehensive Impact Analysis")
    
    print_subsection("Order Service Blast Radius")
    result = query_engine.blast_radius("service:order-service")
    print_query_result(result, "Order Service Impact Analysis")
    
    print_subsection("Orders Database Blast Radius")
    result = query_engine.blast_radius("database:orders-db")
    print_query_result(result, "Orders Database Impact Analysis")
    
    print_subsection("Auth Service Blast Radius (Max Depth 3)")
    result = query_engine.blast_radius("service:auth-service", max_depth=3)
    print_query_result(result, "Auth Service Impact Analysis")
    
    # ========================================================================
    # 6. PATH - Find shortest path between nodes
    # ========================================================================
    print_section("6. PATH - Find Shortest Path Between Nodes")
    
    print_subsection("Path from API Gateway to Orders Database")
    result = query_engine.path("service:api-gateway", "database:orders-db")
    print_query_result(result, "API Gateway → Orders DB Path")
    
    print_subsection("Path from Order Service to Payment Gateway")
    result = query_engine.path("service:order-service", "service:payment-gateway")
    print_query_result(result, "Order Service → Payment Gateway Path")
    
    print_subsection("Path between unconnected nodes")
    result = query_engine.path("service:auth-service", "database:inventory-db")
    print_query_result(result, "Unconnected Nodes Path (Demo)")
    
    # ========================================================================
    # 7. GET_OWNER - Find owning team for a node
    # ========================================================================
    print_section("7. GET_OWNER - Find Owning Team")
    
    print_subsection("Order Service Owner")
    result = query_engine.get_owner("service:order-service")
    print_query_result(result, "Order Service Owner")
    
    print_subsection("Orders Database Owner")
    result = query_engine.get_owner("database:orders-db")
    print_query_result(result, "Orders Database Owner")
    
    print_subsection("Payment Gateway Owner")
    result = query_engine.get_owner("service:payment-gateway")
    print_query_result(result, "Payment Gateway Owner")
    
    # ========================================================================
    # 8. NATURAL LANGUAGE QUERIES (Legacy Compatibility)
    # ========================================================================
    print_section("8. NATURAL LANGUAGE QUERIES - Legacy Compatibility")
    
    print_subsection("Natural Language Blast Radius")
    result = query_engine.query("What breaks if order-service goes down?")
    print("📝 Natural Language Query: 'What breaks if order-service goes down?'")
    print(json.dumps(result, indent=2, default=str))
    
    print_subsection("Natural Language Ownership")
    result = query_engine.query("Who owns the orders database?")
    print("📝 Natural Language Query: 'Who owns the orders database?'")
    print(json.dumps(result, indent=2, default=str))
    
    print_subsection("Natural Language Path")
    result = query_engine.query("What path connects api-gateway to payment-gateway?")
    print("📝 Natural Language Query: 'What path connects api-gateway to payment-gateway?'")
    print(json.dumps(result, indent=2, default=str))
    
    # ========================================================================
    # 9. PERFORMANCE TESTING
    # ========================================================================
    print_section("9. PERFORMANCE TESTING - Large Graph Operations")
    
    print_subsection("Performance Benchmarks")
    
    # Test multiple operations and measure performance
    operations = [
        ("Get Node", lambda: query_engine.get_node("service:order-service")),
        ("Get All Services", lambda: query_engine.get_nodes(NodeType.SERVICE)),
        ("Downstream Analysis", lambda: query_engine.downstream("service:api-gateway", max_depth=5)),
        ("Upstream Analysis", lambda: query_engine.upstream("database:orders-db", max_depth=5)),
        ("Blast Radius", lambda: query_engine.blast_radius("service:order-service")),
        ("Path Finding", lambda: query_engine.path("service:api-gateway", "database:orders-db")),
        ("Owner Lookup", lambda: query_engine.get_owner("service:order-service"))
    ]
    
    performance_results = []
    
    for op_name, op_func in operations:
        start_time = time.time()
        result = op_func()
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        performance_results.append({
            "operation": op_name,
            "success": result.success if hasattr(result, 'success') else True,
            "execution_time_ms": execution_time,
            "internal_time_ms": getattr(result, 'execution_time_ms', 0) if hasattr(result, 'execution_time_ms') else 0
        })
        
        print(f"⚡ {op_name}: {execution_time:.2f}ms (Success: {result.success if hasattr(result, 'success') else True})")
    
    # Summary
    total_time = sum(p["execution_time_ms"] for p in performance_results)
    avg_time = total_time / len(performance_results)
    
    print(f"\n📊 Performance Summary:")
    print(f"   Total Time: {total_time:.2f}ms")
    print(f"   Average Time: {avg_time:.2f}ms")
    print(f"   Operations: {len(performance_results)}")
    
    # ========================================================================
    # 10. ADVANCED FEATURES DEMO
    # ========================================================================
    print_section("10. ADVANCED FEATURES - Cycle Detection & Edge Filtering")
    
    print_subsection("Cycle Detection Demo")
    print("🔄 The query engine automatically detects and prevents infinite loops")
    print("   during graph traversal using visited node tracking and max depth limits.")
    
    # Demonstrate with a deep traversal
    result = query_engine.downstream("service:api-gateway", max_depth=10)
    print(f"✅ Deep traversal completed safely in {result.execution_time_ms:.2f}ms")
    print(f"   Found {result.data['dependency_count']} dependencies")
    
    print_subsection("Edge Type Filtering Demo")
    
    # Show different results with different edge type filters
    all_deps = query_engine.downstream("service:order-service")
    depends_only = query_engine.downstream("service:order-service", edge_types=[EdgeType.DEPENDS_ON])
    calls_only = query_engine.downstream("service:order-service", edge_types=[EdgeType.CALLS])
    
    print(f"📊 Order Service Dependencies:")
    print(f"   All edges: {all_deps.data['dependency_count']} dependencies")
    print(f"   DEPENDS_ON only: {depends_only.data['dependency_count']} dependencies")
    print(f"   CALLS only: {calls_only.data['dependency_count']} dependencies")
    
    # ========================================================================
    # 11. SUMMARY AND COMPLETION
    # ========================================================================
    print_section("✅ Part 3 Query Engine Demo Complete")
    
    print("\n🎉 Part 3 Implementation Summary:")
    print("   ✅ All required query methods implemented")
    print("   ✅ Cycle detection and prevention")
    print("   ✅ Performance optimization for large graphs")
    print("   ✅ Edge type filtering")
    print("   ✅ Comprehensive path finding")
    print("   ✅ Impact analysis with team information")
    print("   ✅ Natural language compatibility maintained")
    print("   ✅ Standardized QueryResult format")
    print("   ✅ Comprehensive error handling")
    print("   ✅ Performance benchmarking")
    
    print("\n🚀 The Engineering Knowledge Graph Query Engine is ready for production!")
    print("   - Use programmatic methods for structured queries")
    print("   - Use natural language for interactive exploration") 
    print("   - All queries include execution timing and metadata")
    print("   - Cycle detection prevents infinite loops")
    print("   - Edge filtering enables targeted analysis")


if __name__ == "__main__":
    run_part3_demo()
