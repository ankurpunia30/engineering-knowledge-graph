#!/usr/bin/env python3
"""
Quick test to verify specific queries work with Groq integration.
Tests: "show all teams" and "show all databases"
"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

from dotenv import load_dotenv
load_dotenv()

def test_specific_queries():
    """Test the problematic queries."""
    print("\n🧪 Testing Specific Queries\n")
    print("="*70)
    
    # Check environment
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("❌ GROQ_API_KEY not found in environment!")
        print("Make sure it's set in your .env file")
        return
    
    print(f"✅ Groq API Key: {groq_key[:20]}...")
    
    # Load storage and engine
    print("\n📊 Loading graph data...")
    from graph.storage_factory import create_optimal_storage
    from connectors import registry
    
    storage = create_optimal_storage()
    
    data_dir = Path(__file__).parent / "data"
    for connector_name, filename in [
        ('docker-compose', 'docker-compose.yml'),
        ('teams', 'teams.yaml'),
        ('kubernetes', 'k8s-deployments.yaml')
    ]:
        file_path = data_dir / filename
        if file_path.exists():
            connector = registry.create_connector(connector_name, str(file_path))
            kg = connector.parse()
            storage.merge_graph(kg)
    
    stats = storage.get_stats()
    print(f"✅ Loaded: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
    
    # Initialize Groq engine
    print("\n🤖 Initializing Groq LLM engine...")
    from graph.llm_query import LLMQueryEngine
    llm_engine = LLMQueryEngine(storage)
    print("✅ Groq engine ready")
    
    # Test queries
    test_queries = [
        "show all teams",
        "show all databases",
        "list all services"
    ]
    
    for query in test_queries:
        print("\n" + "="*70)
        print(f"📝 Query: {query}")
        print("="*70)
        
        try:
            result = llm_engine.query(query)
            
            print(f"\n🎯 Type: {result.get('type')}")
            print(f"💯 Confidence: {result.get('confidence', 0.0):.2%}")
            print(f"⚡ LLM Powered: {result.get('llm_powered', False)}")
            
            if result.get('error'):
                print(f"\n❌ Error: {result['error']}")
            else:
                print(f"\n✅ Success! Data structure:")
                
                # Show what data we got
                if result.get('teams'):
                    print(f"  • Found {len(result['teams'])} teams")
                    for team in result['teams'][:3]:
                        print(f"    - {team.get('name')} (Lead: {team.get('lead')})")
                
                if result.get('databases'):
                    print(f"  • Found {len(result['databases'])} databases")
                    for db in result['databases'][:3]:
                        print(f"    - {db.get('name')} (Team: {db.get('team')})")
                
                if result.get('services'):
                    print(f"  • Found {len(result['services'])} services")
                    for svc in result['services'][:3]:
                        print(f"    - {svc.get('name')} (Team: {svc.get('team')})")
                
        except Exception as e:
            print(f"\n❌ Query failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ Test Complete!")
    print("="*70)

if __name__ == "__main__":
    test_specific_queries()
