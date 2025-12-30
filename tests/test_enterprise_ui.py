#!/usr/bin/env python3
"""
Quick test script to verify backend is working properly with the enterprise UI.
"""

import requests
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000"

def test_health() -> bool:
    """Test health endpoint"""
    print("\n🔍 Testing /api/health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Nodes: {data.get('nodes')}")
            print(f"   - Edges: {data.get('edges')}")
            print(f"   - LLM Provider: {data.get('llm_provider')}")
            print(f"   - Storage Backend: {data.get('storage_backend')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_graph_data() -> bool:
    """Test graph data endpoint"""
    print("\n📊 Testing /api/graph/data endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/graph/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            nodes = data.get('nodes', [])
            edges = data.get('edges', [])
            print(f"✅ Graph data retrieved!")
            print(f"   - Nodes: {len(nodes)}")
            print(f"   - Edges: {len(edges)}")
            if nodes:
                print(f"   - Sample node: {nodes[0].get('id')}")
            return True
        else:
            print(f"❌ Graph data failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat() -> bool:
    """Test chat endpoint"""
    print("\n💬 Testing /api/chat endpoint...")
    try:
        test_query = "Show me all services"
        response = requests.post(
            f"{API_BASE}/api/chat",
            json={"message": test_query},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat query successful!")
            print(f"   - Query: {test_query}")
            print(f"   - Intent: {data.get('intent')}")
            print(f"   - Confidence: {data.get('confidence')}")
            print(f"   - Related nodes: {len(data.get('related_nodes', []))}")
            print(f"   - Response preview: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Chat query failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Enterprise UI Backend Integration Tests")
    print("=" * 60)
    
    results = {
        "health": test_health(),
        "graph_data": test_graph_data(),
        "chat": test_chat()
    }
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ All tests passed! Enterprise UI should work perfectly.")
        print("   Open http://localhost:3000 to view the dashboard.")
    else:
        print("\n⚠️  Some tests failed. Please check:")
        if not results["health"]:
            print("   1. Is the backend running? (python chat/app.py)")
        if not results["graph_data"]:
            print("   2. Is data loaded? (python tests/demo_data_loader.py)")
        if not results["chat"]:
            print("   3. Is GROQ_API_KEY set in .env?")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
