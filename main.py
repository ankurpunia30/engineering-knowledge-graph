"""
Main entry point and configuration validator for the Engineering Knowledge Graph.
"""
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Union

from connectors import registry
from graph.storage import GraphStorage
from graph.storage_factory import create_optimal_storage, get_storage_recommendations
from chat.app import EKGChatAPI

# Try to import Neo4j storage
try:
    from graph.neo4j_storage import Neo4jStorage
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


def validate_config_files(data_dir: str = "data") -> Dict[str, Any]:
    """Validate all configuration files and report issues."""
    data_path = Path(data_dir)
    results = {
        "valid": True,
        "files": {},
        "summary": {}
    }
    
    # Configuration files to check
    config_files = [
        ("docker-compose", "docker-compose.yml"),
        ("teams", "teams.yaml"),
        ("kubernetes", "k8s-deployments.yaml")
    ]
    
    total_issues = 0
    
    for connector_name, filename in config_files:
        filepath = data_path / filename
        file_result = {
            "exists": filepath.exists(),
            "issues": []
        }
        
        if filepath.exists():
            try:
                connector = registry.create_connector(connector_name, str(filepath))
                issues = connector.validate()
                file_result["issues"] = issues
                
                if issues:
                    results["valid"] = False
                    total_issues += len(issues)
                    
                print(f"📄 {filename}:")
                if issues:
                    print(f"   ❌ {len(issues)} issues found:")
                    for issue in issues:
                        print(f"      • {issue}")
                else:
                    print("   ✅ No issues found")
                    
            except Exception as e:
                file_result["issues"] = [f"Failed to parse: {e}"]
                results["valid"] = False
                total_issues += 1
                print(f"📄 {filename}:")
                print(f"   ❌ Failed to parse: {e}")
        else:
            print(f"📄 {filename}:")
            print("   ⚠️  File not found (optional for k8s-deployments.yaml)")
            if connector_name != "kubernetes":  # k8s is optional
                results["valid"] = False
                total_issues += 1
        
        results["files"][filename] = file_result
    
    results["summary"] = {
        "total_issues": total_issues,
        "files_checked": len(config_files),
        "files_found": sum(1 for f in results["files"].values() if f["exists"])
    }
    
    print(f"\n📊 Summary: {total_issues} total issues across {results['summary']['files_found']} files")
    
    return results


def load_and_analyze_graph(data_dir: str = "data") -> Union[GraphStorage, Neo4jStorage]:
    """Load configuration files and build the knowledge graph with optimal storage."""
    print("\n🚀 Initializing Engineering Knowledge Graph...")
    
    # Create optimal storage backend
    storage = create_optimal_storage()
    
    # Show storage recommendations
    print("\n📊 Storage Backend Information:")
    print(get_storage_recommendations())
    print()
    
    data_path = Path(data_dir)
    
    print("🔧 Loading configuration files...")
    
    # Load Docker Compose
    docker_file = data_path / "docker-compose.yml"
    if docker_file.exists():
        try:
            connector = registry.create_connector('docker-compose', str(docker_file))
            kg = connector.parse()
            storage.merge_graph(kg)
            print(f"   ✅ Docker Compose: {len(kg.nodes)} nodes, {len(kg.edges)} edges")
        except Exception as e:
            print(f"   ❌ Docker Compose failed: {e}")
    
    # Load Teams
    teams_file = data_path / "teams.yaml"
    if teams_file.exists():
        try:
            connector = registry.create_connector('teams', str(teams_file))
            kg = connector.parse()
            storage.merge_graph(kg)
            print(f"   ✅ Teams: {len(kg.nodes)} nodes, {len(kg.edges)} edges")
        except Exception as e:
            print(f"   ❌ Teams failed: {e}")
    
    # Load Kubernetes (optional)
    k8s_file = data_path / "k8s-deployments.yaml"
    if k8s_file.exists():
        try:
            connector = registry.create_connector('kubernetes', str(k8s_file))
            kg = connector.parse()
            storage.merge_graph(kg)
            print(f"   ✅ Kubernetes: {len(kg.nodes)} nodes, {len(kg.edges)} edges")
        except Exception as e:
            print(f"   ❌ Kubernetes failed: {e}")
    
    # Print final statistics
    stats = storage.get_stats()
    print(f"\n📈 Knowledge Graph Statistics:")
    print(f"   • Total Nodes: {stats['total_nodes']}")
    print(f"   • Total Edges: {stats['total_edges']}")
    print(f"   • Node Types: {dict(stats['node_types'])}")
    print(f"   • Edge Types: {dict(stats['edge_types'])}")
    print(f"   • Connected: {stats['is_connected']}")
    
    return storage


def analyze_architecture(storage: Union[GraphStorage, Neo4jStorage]) -> None:
    """Analyze the architecture and provide insights."""
    print("\n🔍 Architecture Analysis:")
    
    # Service analysis
    services = storage.get_nodes_by_type("service")
    print(f"\n⚙️  Services ({len(services)}):")
    for service in services:
        dependencies = storage.get_dependencies(service.id, depth=1)
        dependents = storage.get_dependents(service.id, depth=1)
        print(f"   • {service.name}: {len(dependencies)} deps, {len(dependents)} dependents")
    
    # Database analysis
    databases = storage.get_nodes_by_type("database")
    print(f"\n🗄️  Databases ({len(databases)}):")
    for db in databases:
        connections = storage.kg.get_edges_to_node(db.id)
        readers = [e for e in connections if e.type.value == "reads_from"]
        writers = [e for e in connections if e.type.value == "writes_to"]
        print(f"   • {db.name}: {len(readers)} readers, {len(writers)} writers")
    
    # Team analysis
    teams = storage.get_nodes_by_type("team")
    print(f"\n👥 Teams ({len(teams)}):")
    for team in teams:
        owned_services = storage.get_team_ownership(team.name)
        print(f"   • {team.name}: owns {len(owned_services)} services")
    
    # Critical services analysis
    print(f"\n⚠️  Critical Services (high blast radius):")
    for service in services:
        blast_radius = storage.get_blast_radius(service.id)
        if blast_radius.get("affected_services_count", 0) > 2:
            print(f"   • {service.name}: affects {blast_radius['affected_services_count']} services")


def interactive_demo(storage: Union[GraphStorage, Neo4jStorage]) -> None:
    """Run an interactive demo of the query engine."""
    from graph.query import QueryEngine
    
    query_engine = QueryEngine(storage)
    
    print("\n🤖 Interactive Demo - Ask me about your infrastructure!")
    print("Examples:")
    print("  • 'What breaks if order-service goes down?'")
    print("  • 'Who owns the payments database?'")
    print("  • 'Show me all teams'")
    print("  • Type 'quit' to exit\n")
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            response = query_engine.query(question)
            
            print(f"\n🤖 Response ({response.get('type', 'unknown')}):")
            
            # Format the response nicely
            if response.get('error'):
                print(f"   ❌ {response['error']}")
                if response.get('suggestion'):
                    print(f"   💡 {response['suggestion']}")
            else:
                # Print key information based on response type
                if response.get('type') == 'blast_radius':
                    print(f"   💥 Service: {response.get('service_analyzed')}")
                    print(f"   📊 Affected Services: {response.get('affected_services_count', 0)}")
                    print(f"   👥 Teams Affected: {response.get('teams_count', 0)}")
                elif response.get('type') == 'ownership':
                    if response.get('service'):
                        print(f"   🏢 Service: {response['service']}")
                        print(f"   👥 Team: {response.get('team', 'Unknown')}")
                        print(f"   👤 Lead: {response.get('team_lead', 'Unknown')}")
                elif response.get('type') == 'connection':
                    print(f"   🔗 Service: {response.get('service')}")
                    print(f"   📤 Outgoing: {response.get('total_outgoing', 0)}")
                    print(f"   📥 Incoming: {response.get('total_incoming', 0)}")
                else:
                    # Print first few fields for other response types
                    for key, value in list(response.items())[:5]:
                        if key not in ['query', 'type'] and not isinstance(value, (list, dict)):
                            print(f"   • {key}: {value}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Engineering Knowledge Graph")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate configuration files")
    parser.add_argument("--analyze", action="store_true",
                       help="Analyze the architecture")
    parser.add_argument("--demo", action="store_true",
                       help="Run interactive demo")
    parser.add_argument("--chat", action="store_true",
                       help="Start the chat server")
    parser.add_argument("--data-dir", default="data",
                       help="Directory containing configuration files")
    parser.add_argument("--host", default="0.0.0.0",
                       help="Host for chat server")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for chat server")
    
    args = parser.parse_args()
    
    print("🔍 Engineering Knowledge Graph")
    print("=" * 40)
    
    # If no specific action, run validation by default
    if not any([args.validate, args.analyze, args.demo, args.chat]):
        args.validate = True
        args.analyze = True
    
    if args.validate:
        print("\n📋 Validating configuration files...")
        validation_results = validate_config_files(args.data_dir)
        
        if not validation_results["valid"]:
            print("\n❌ Configuration validation failed!")
            print("Please fix the issues above before proceeding.")
            return 1
        else:
            print("\n✅ All configuration files are valid!")
    
    if args.analyze or args.demo or args.chat:
        print("\n📥 Loading knowledge graph...")
        storage = load_and_analyze_graph(args.data_dir)
        
        if storage.get_stats()["total_nodes"] == 0:
            print("❌ No data loaded! Please check your configuration files.")
            return 1
    
    if args.analyze:
        analyze_architecture(storage)
    
    if args.demo:
        interactive_demo(storage)
    
    if args.chat:
        print(f"\n🚀 Starting chat server on http://{args.host}:{args.port}")
        print("Open your browser to interact with the knowledge graph!")
        chat_api = EKGChatAPI()
        chat_api.run(host=args.host, port=args.port)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
