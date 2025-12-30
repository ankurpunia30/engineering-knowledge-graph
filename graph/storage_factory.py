"""
Storage Factory for the Engineering Knowledge Graph.

Provides a unified interface to create and manage different storage backends
(NetworkX, Neo4j) based on configuration and availability.
"""
import os
import logging
from typing import Union, Optional, Dict, Any
from .storage import GraphStorage
from .neo4j_storage import Neo4jStorage

logger = logging.getLogger(__name__)


class StorageFactory:
    """Factory class for creating and managing graph storage backends."""
    
    @staticmethod
    def create_storage(
        backend: str = None, 
        auto_fallback: bool = True,
        **kwargs
    ) -> Union[GraphStorage, Neo4jStorage]:
        """
        Create a storage instance based on configuration.
        
        Args:
            backend: Storage backend ('neo4j', 'networkx', or None for auto-detect)
            auto_fallback: Whether to fallback to NetworkX if Neo4j fails
            **kwargs: Additional arguments for storage initialization
            
        Returns:
            Storage instance (Neo4jStorage or GraphStorage)
        """
        # Determine backend from environment or parameter
        if backend is None:
            backend = os.getenv("STORAGE_BACKEND", "auto").lower()
        
        if backend in ["auto", "neo4j"]:
            try:
                logger.info("🚀 Attempting to create Neo4j storage...")
                neo4j_storage = Neo4jStorage(**kwargs)
                
                # Test if Neo4j is actually working
                if neo4j_storage.driver is not None:
                    logger.info("✅ Neo4j storage created successfully")
                    return neo4j_storage
                else:
                    logger.warning("⚠️ Neo4j storage created but no active driver")
                    if auto_fallback:
                        logger.info("🔄 Auto-fallback enabled, using NetworkX")
                        return GraphStorage()
                    return neo4j_storage
                    
            except Exception as e:
                logger.error(f"❌ Failed to create Neo4j storage: {e}")
                if auto_fallback:
                    logger.info("🔄 Falling back to NetworkX storage")
                    return GraphStorage()
                raise
        
        elif backend == "networkx":
            logger.info("📊 Creating NetworkX storage")
            return GraphStorage()
        
        else:
            raise ValueError(f"Unknown storage backend: {backend}")
    
    @staticmethod
    def get_backend_info() -> Dict[str, Any]:
        """
        Get information about available storage backends.
        
        Returns:
            Dict with backend availability and features
        """
        info = {
            "available_backends": ["networkx"],
            "neo4j_available": False,
            "recommended_backend": "networkx",
            "environment_setting": os.getenv("STORAGE_BACKEND", "auto")
        }
        
        # Test Neo4j availability
        try:
            from neo4j import GraphDatabase
            
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            test_driver = GraphDatabase.driver(uri, auth=(user, password))
            test_driver.verify_connectivity()
            test_driver.close()
            
            info["available_backends"].append("neo4j")
            info["neo4j_available"] = True
            info["recommended_backend"] = "neo4j"
            
        except Exception as e:
            info["neo4j_error"] = str(e)
        
        return info
    
    @staticmethod
    def compare_backends() -> Dict[str, Dict[str, Any]]:
        """
        Compare different storage backends and their characteristics.
        
        Returns:
            Dict comparing backend features and recommendations
        """
        return {
            "networkx": {
                "type": "In-Memory Graph",
                "persistence": "JSON file backup",
                "performance": "Fast for <10K nodes",
                "scalability": "Limited by memory",
                "setup_complexity": "None",
                "use_cases": ["Development", "Small datasets", "Proof of concept"],
                "pros": ["Zero setup", "Fast development", "No external dependencies"],
                "cons": ["No native persistence", "Memory limitations", "No concurrent access"]
            },
            "neo4j": {
                "type": "Graph Database",
                "persistence": "Native disk storage",
                "performance": "Optimized for large datasets",
                "scalability": "Highly scalable",
                "setup_complexity": "Requires Neo4j installation",
                "use_cases": ["Production", "Large datasets", "Multi-user access"],
                "pros": ["Native persistence", "ACID transactions", "Powerful query language (Cypher)", 
                        "Concurrent access", "Built-in clustering"],
                "cons": ["Requires setup", "More complex", "Resource overhead"]
            },
            "recommendations": {
                "development": "NetworkX - Zero setup, fast iteration",
                "production_small": "Neo4j - Better persistence and reliability",
                "production_large": "Neo4j - Essential for scale and performance",
                "data_exploration": "NetworkX - Quick analysis and visualization",
                "multi_user": "Neo4j - Concurrent access and data integrity"
            }
        }


def create_optimal_storage(**kwargs) -> Union[GraphStorage, Neo4jStorage]:
    """
    Convenience function to create the optimal storage backend.
    
    This function automatically detects the best available backend and creates
    an appropriate storage instance with sensible defaults.
    """
    return StorageFactory.create_storage(auto_fallback=True, **kwargs)


def get_storage_recommendations() -> str:
    """
    Get human-readable recommendations for storage backend selection.
    
    Returns:
        Formatted string with recommendations
    """
    backend_info = StorageFactory.get_backend_info()
    comparison = StorageFactory.compare_backends()
    
    recommendations = []
    
    if backend_info["neo4j_available"]:
        recommendations.append("✅ Neo4j is available and recommended for production use")
        recommendations.append("   - Native persistence and ACID transactions")
        recommendations.append("   - Optimized for large datasets and complex queries")
        recommendations.append("   - Supports concurrent access and clustering")
    else:
        recommendations.append("⚠️ Neo4j is not available, using NetworkX fallback")
        recommendations.append("   - Perfect for development and small datasets")
        recommendations.append("   - Zero setup required")
        recommendations.append("   - Consider Neo4j for production workloads")
    
    recommendations.append(f"\nCurrent environment setting: {backend_info['environment_setting']}")
    recommendations.append(f"Recommended backend: {backend_info['recommended_backend']}")
    
    return "\n".join(recommendations)
