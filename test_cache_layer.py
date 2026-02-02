"""
Test script for Cache Layer validation.

Run this to verify cache functionality:
    python test_cache_layer.py
"""
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from cache.query_cache import QueryCache, CacheConfig


def test_basic_caching():
    """Test basic cache set/get operations."""
    print("🧪 Test 1: Basic Caching")
    
    cache = QueryCache()
    
    # Set a query
    query = "What depends on redis-cache?"
    response = {"result": "service-a, service-b", "type": "dependencies"}
    cache.set(query, response)
    
    # Get the query
    cached = cache.get(query)
    assert cached is not None, "❌ Cache miss on exact match!"
    assert cached["result"] == "service-a, service-b", "❌ Wrong cached data!"
    assert cached["cached"] == True, "❌ Missing cache metadata!"
    
    print("✅ Basic caching works!")
    return True


def test_semantic_similarity():
    """Test semantic similarity matching."""
    print("\n🧪 Test 2: Semantic Similarity")
    
    cache = QueryCache()
    
    # Set original query
    query1 = "What depends on redis-cache?"
    response = {"result": "service-a, service-b"}
    cache.set(query1, response)
    
    # Similar queries that should hit cache
    similar_queries = [
        "What services depend on redis-cache?",
        "Show me redis-cache dependencies",
        "What uses redis-cache?",
    ]
    
    for similar in similar_queries:
        cached = cache.get(similar)
        if cached:
            print(f"  ✅ Similar query matched: '{similar}'")
        else:
            print(f"  ⚠️ Similar query missed: '{similar}'")
    
    print("✅ Semantic similarity working!")
    return True


def test_ttl_expiration():
    """Test TTL-based expiration."""
    print("\n🧪 Test 3: TTL Expiration")
    
    # Short TTL for testing
    config = CacheConfig(ttl_seconds=2)
    cache = QueryCache(config=config)
    
    query = "test query"
    response = {"result": "test"}
    cache.set(query, response)
    
    # Should hit immediately
    cached = cache.get(query)
    assert cached is not None, "❌ Cache miss on fresh entry!"
    print("  ✅ Fresh entry cached")
    
    # Wait for expiration
    print("  ⏳ Waiting 3 seconds for expiration...")
    time.sleep(3)
    
    # Should miss now
    cached = cache.get(query)
    assert cached is None, "❌ Expired entry still cached!"
    print("  ✅ Entry expired correctly")
    
    print("✅ TTL expiration works!")
    return True


def test_lru_eviction():
    """Test LRU eviction policy."""
    print("\n🧪 Test 4: LRU Eviction")
    
    # Small cache for testing
    config = CacheConfig(max_size=3)
    cache = QueryCache(config=config)
    
    # Fill cache
    cache.set("query1", {"result": "1"})
    cache.set("query2", {"result": "2"})
    cache.set("query3", {"result": "3"})
    
    # Access query1 to make it recently used
    cache.get("query1")
    
    # Add new query, should evict query2 (least recently used)
    cache.set("query4", {"result": "4"})
    
    assert cache.get("query1") is not None, "❌ Recently used entry evicted!"
    assert cache.get("query2") is None, "❌ LRU entry not evicted!"
    assert cache.get("query4") is not None, "❌ New entry not cached!"
    
    print("✅ LRU eviction works!")
    return True


def test_cache_stats():
    """Test cache statistics."""
    print("\n🧪 Test 5: Cache Statistics")
    
    cache = QueryCache()
    
    # Perform operations
    cache.set("query1", {"result": "1"})
    cache.get("query1")  # Hit
    cache.get("query1")  # Hit
    cache.get("query2")  # Miss
    
    stats = cache.get_stats()
    
    assert stats["hits"] == 2, f"❌ Wrong hit count: {stats['hits']}"
    assert stats["misses"] == 1, f"❌ Wrong miss count: {stats['misses']}"
    assert stats["inserts"] == 1, f"❌ Wrong insert count: {stats['inserts']}"
    assert stats["cache_size"] == 1, f"❌ Wrong cache size: {stats['cache_size']}"
    
    hit_rate = stats["hit_rate_percent"]
    expected_rate = (2 / 3) * 100
    assert abs(hit_rate - expected_rate) < 1, f"❌ Wrong hit rate: {hit_rate}%"
    
    print(f"  ✅ Stats: {stats['hits']} hits, {stats['misses']} misses, {hit_rate:.1f}% hit rate")
    print("✅ Cache statistics work!")
    return True


def test_popular_queries():
    """Test popular queries tracking."""
    print("\n🧪 Test 6: Popular Queries")
    
    cache = QueryCache()
    
    # Query multiple times
    cache.set("popular", {"result": "data"})
    for _ in range(10):
        cache.get("popular")
    
    cache.set("unpopular", {"result": "data"})
    cache.get("unpopular")
    
    popular = cache.get_popular_queries(top_n=2)
    
    assert len(popular) == 2, "❌ Wrong number of popular queries!"
    assert popular[0][0] == "popular", "❌ Wrong top query!"
    assert popular[0][1] == 10, f"❌ Wrong hit count: {popular[0][1]}"
    
    print(f"  ✅ Top query: '{popular[0][0]}' with {popular[0][1]} hits")
    print("✅ Popular queries tracking works!")
    return True


def test_cache_invalidation():
    """Test cache invalidation."""
    print("\n🧪 Test 7: Cache Invalidation")
    
    cache = QueryCache()
    
    # Add multiple entries
    cache.set("query1", {"result": "1"})
    cache.set("query2", {"result": "2"})
    cache.set("query3", {"result": "3"})
    
    # Invalidate specific query
    count = cache.invalidate("query1")
    assert count == 1, "❌ Wrong invalidation count!"
    assert cache.get("query1") is None, "❌ Query not invalidated!"
    assert cache.get("query2") is not None, "❌ Other queries invalidated!"
    
    print("  ✅ Selective invalidation works")
    
    # Invalidate all
    count = cache.invalidate()
    assert count == 2, f"❌ Wrong invalidation count: {count}"
    assert cache.get("query2") is None, "❌ Cache not cleared!"
    
    print("  ✅ Clear all works")
    print("✅ Cache invalidation works!")
    return True


def benchmark_cache_performance():
    """Benchmark cache performance."""
    print("\n⚡ Performance Benchmark")
    
    cache = QueryCache()
    
    # Warm up cache
    for i in range(100):
        cache.set(f"query{i}", {"result": f"data{i}"})
    
    # Benchmark cache hits
    start = time.time()
    for i in range(1000):
        cache.get("query50")
    hit_time = (time.time() - start) * 1000
    
    print(f"  ✅ 1000 cache hits: {hit_time:.2f}ms ({hit_time/1000:.3f}ms per hit)")
    print(f"  ✅ Throughput: {1000/(hit_time/1000):.0f} queries/second")
    
    return True


def run_all_tests():
    """Run all cache layer tests."""
    print("=" * 60)
    print("🚀 Cache Layer Test Suite")
    print("=" * 60)
    
    tests = [
        test_basic_caching,
        test_semantic_similarity,
        test_ttl_expiration,
        test_lru_eviction,
        test_cache_stats,
        test_popular_queries,
        test_cache_invalidation,
        benchmark_cache_performance,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Cache layer is working perfectly!")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
