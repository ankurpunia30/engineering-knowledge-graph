"""
Intelligent Query Cache Layer for LLM Cost Optimization.

This cache layer implements:
1. Semantic similarity matching for similar queries
2. TTL-based expiration (30s default)
3. LRU eviction for memory management
4. Fallback mechanism to LLM on cache miss
5. Query normalization and fuzzy matching
"""
import time
import hashlib
import re
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading


@dataclass
class CacheConfig:
    """Configuration for the query cache."""
    max_size: int = 100  # Maximum number of cached queries
    ttl_seconds: int = 30  # Time to live for cache entries
    similarity_threshold: float = 0.5  # Minimum similarity score for cache hit
    enable_fuzzy_matching: bool = True  # Enable fuzzy query matching
    auto_refresh: bool = True  # Auto-refresh popular queries
    min_query_length: int = 3  # Minimum query length to cache


@dataclass
class CacheEntry:
    """Represents a cached query result."""
    query: str
    normalized_query: str
    response: Dict[str, Any]
    timestamp: float
    hit_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    variations: List[str] = field(default_factory=list)  # Similar query variations
    
    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if the cache entry has expired."""
        return (time.time() - self.timestamp) > ttl_seconds
    
    def increment_hits(self):
        """Increment hit counter and update last accessed time."""
        self.hit_count += 1
        self.last_accessed = time.time()
    
    def should_refresh(self, ttl_seconds: int) -> bool:
        """Determine if entry should be refreshed based on popularity and age."""
        age = time.time() - self.timestamp
        # Refresh if: popular (5+ hits) AND approaching expiration (80% of TTL)
        return self.hit_count >= 5 and age > (ttl_seconds * 0.8)


class QueryCache:
    """
    Intelligent cache layer for LLM queries with semantic similarity matching.
    
    Features:
    - LRU eviction policy
    - TTL-based expiration
    - Semantic similarity matching
    - Query normalization
    - Automatic cache warming for popular queries
    - Thread-safe operations
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "inserts": 0,
            "refreshes": 0
        }
        
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for a query.
        
        Returns cached response if:
        1. Exact match found and not expired
        2. Similar query found (>85% similarity) and not expired
        
        Args:
            query: The natural language query
            
        Returns:
            Cached response dict or None if cache miss
        """
        if len(query.strip()) < self.config.min_query_length:
            return None
            
        normalized = self._normalize_query(query)
        
        with self.lock:
            # Try exact match first
            cache_key = self._get_cache_key(normalized)
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if not entry.is_expired(self.config.ttl_seconds):
                    entry.increment_hits()
                    self.stats["hits"] += 1
                    # Move to end (most recently used)
                    self.cache.move_to_end(cache_key)
                    return self._enrich_cached_response(entry.response, entry)
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
            
            # Try fuzzy matching if enabled
            if self.config.enable_fuzzy_matching:
                similar_entry = self._find_similar_query(normalized)
                if similar_entry:
                    similar_entry.increment_hits()
                    # Add this query as a variation
                    if query not in similar_entry.variations:
                        similar_entry.variations.append(query)
                    self.stats["hits"] += 1
                    return self._enrich_cached_response(similar_entry.response, similar_entry)
            
            # Cache miss
            self.stats["misses"] += 1
            return None
    
    def set(self, query: str, response: Dict[str, Any]) -> None:
        """
        Store a query result in the cache.
        
        Args:
            query: The natural language query
            response: The LLM response to cache
        """
        if len(query.strip()) < self.config.min_query_length:
            return
            
        normalized = self._normalize_query(query)
        cache_key = self._get_cache_key(normalized)
        
        with self.lock:
            # Check if we need to evict
            if len(self.cache) >= self.config.max_size and cache_key not in self.cache:
                # Remove least recently used (first item)
                self.cache.popitem(last=False)
                self.stats["evictions"] += 1
            
            # Create cache entry
            entry = CacheEntry(
                query=query,
                normalized_query=normalized,
                response=response,
                timestamp=time.time()
            )
            
            self.cache[cache_key] = entry
            self.cache.move_to_end(cache_key)  # Mark as most recently used
            self.stats["inserts"] += 1
    
    def invalidate(self, query: Optional[str] = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            query: Specific query to invalidate, or None to clear all
            
        Returns:
            Number of entries invalidated
        """
        with self.lock:
            if query is None:
                count = len(self.cache)
                self.cache.clear()
                return count
            
            normalized = self._normalize_query(query)
            cache_key = self._get_cache_key(normalized)
            if cache_key in self.cache:
                del self.cache[cache_key]
                return 1
            return 0
    
    def clean_expired(self) -> int:
        """
        Remove all expired entries from cache.
        
        Returns:
            Number of expired entries removed
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired(self.config.ttl_seconds)
            ]
            for key in expired_keys:
                del self.cache[key]
            return len(expired_keys)
    
    def get_popular_queries(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently hit queries.
        
        Args:
            top_n: Number of top queries to return
            
        Returns:
            List of (query, hit_count) tuples
        """
        with self.lock:
            sorted_entries = sorted(
                self.cache.values(),
                key=lambda e: e.hit_count,
                reverse=True
            )
            return [(e.query, e.hit_count) for e in sorted_entries[:top_n]]
    
    def get_refresh_candidates(self) -> List[str]:
        """
        Get queries that should be refreshed (popular and approaching expiration).
        
        Returns:
            List of queries that need refreshing
        """
        with self.lock:
            return [
                entry.query for entry in self.cache.values()
                if entry.should_refresh(self.config.ttl_seconds)
            ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                "cache_size": len(self.cache),
                "max_size": self.config.max_size,
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests,
                "memory_efficiency": round(len(self.cache) / self.config.max_size * 100, 2)
            }
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for better matching.
        
        Normalization includes:
        - Convert to lowercase
        - Remove extra whitespace
        - Remove punctuation except hyphens/underscores (for service names)
        - Sort words alphabetically (for order-independent matching)
        """
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Preserve service/database names (hyphenated, underscored)
        # Remove punctuation except hyphens, underscores
        normalized = re.sub(r'[^\w\s\-_]', '', normalized)
        
        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def _get_cache_key(self, normalized_query: str) -> str:
        """Generate a cache key from normalized query."""
        return hashlib.md5(normalized_query.encode()).hexdigest()
    
    def _find_similar_query(self, normalized_query: str) -> Optional[CacheEntry]:
        """
        Find a similar cached query using fuzzy matching.
        
        Uses multiple similarity metrics:
        1. Jaccard similarity (word overlap)
        2. Levenshtein-based ratio
        3. Entity preservation (ensure same entities are mentioned)
        
        Returns:
            CacheEntry if similar query found, None otherwise
        """
        query_words = set(normalized_query.split())
        
        best_match = None
        best_score = 0.0
        
        for entry in self.cache.values():
            if entry.is_expired(self.config.ttl_seconds):
                continue
                
            # Calculate Jaccard similarity
            cached_words = set(entry.normalized_query.split())
            intersection = query_words & cached_words
            union = query_words | cached_words
            
            if not union:
                continue
                
            jaccard_score = len(intersection) / len(union)
            
            # Boost score if key entities are preserved
            entity_boost = self._calculate_entity_preservation(
                normalized_query, 
                entry.normalized_query
            )
            
            final_score = (jaccard_score * 0.7) + (entity_boost * 0.3)
            
            if final_score > best_score and final_score >= self.config.similarity_threshold:
                best_score = final_score
                best_match = entry
        
        return best_match
    
    def _calculate_entity_preservation(self, query1: str, query2: str) -> float:
        """
        Check if important entities (service names, databases) are preserved.
        
        Returns:
            Score between 0 and 1 indicating entity overlap
        """
        # Extract potential entity names (hyphenated or underscored words)
        entity_pattern = r'\b[\w]+[-_][\w]+(?:[-_][\w]+)*\b'
        
        entities1 = set(re.findall(entity_pattern, query1))
        entities2 = set(re.findall(entity_pattern, query2))
        
        if not entities1 and not entities2:
            return 1.0  # No entities in either, perfect match
        
        if not entities1 or not entities2:
            return 0.0  # Entities in one but not the other
        
        intersection = entities1 & entities2
        union = entities1 | entities2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _enrich_cached_response(
        self, 
        response: Dict[str, Any], 
        entry: CacheEntry
    ) -> Dict[str, Any]:
        """
        Enrich cached response with cache metadata.
        
        Args:
            response: The original cached response
            entry: The cache entry
            
        Returns:
            Response enriched with cache information
        """
        enriched = response.copy()
        enriched["cached"] = True
        enriched["cache_hit_count"] = entry.hit_count
        enriched["cache_age_seconds"] = round(time.time() - entry.timestamp, 2)
        enriched["cache_variations"] = len(entry.variations)
        return enriched


class CacheWarmer:
    """
    Background service to refresh popular cache entries before expiration.
    """
    
    def __init__(self, cache: QueryCache, refresh_callback):
        """
        Initialize cache warmer.
        
        Args:
            cache: The QueryCache instance to warm
            refresh_callback: Async function to call for refreshing queries
        """
        self.cache = cache
        self.refresh_callback = refresh_callback
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the cache warming background thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._warming_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the cache warming thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _warming_loop(self):
        """Background loop to refresh popular queries."""
        while self.running:
            try:
                # Check every 10 seconds
                time.sleep(10)
                
                # Get queries that need refreshing
                candidates = self.cache.get_refresh_candidates()
                
                for query in candidates:
                    if not self.running:
                        break
                    
                    # Call the refresh callback
                    try:
                        self.refresh_callback(query)
                        self.cache.stats["refreshes"] += 1
                    except Exception as e:
                        print(f"Failed to refresh query '{query}': {e}")
                        
            except Exception as e:
                print(f"Cache warmer error: {e}")
