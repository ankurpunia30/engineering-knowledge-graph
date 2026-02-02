"""
Cache layer for LLM query optimization.
Reduces token usage and costs by caching query results with semantic similarity matching.
"""
from .query_cache import QueryCache, CacheConfig

__all__ = ['QueryCache', 'CacheConfig']
