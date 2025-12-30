"""
Base connector interface for parsing configuration files.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

from graph.models import KnowledgeGraph


class BaseConnector(ABC):
    """Base class for all connectors."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    @abstractmethod
    def parse(self) -> KnowledgeGraph:
        """Parse the configuration file and return a knowledge graph."""
        pass
    
    @abstractmethod
    def validate(self) -> List[str]:
        """Validate the configuration file and return any issues found."""
        pass
    
    def get_connector_type(self) -> str:
        """Get the type of this connector."""
        return self.__class__.__name__


class ConnectorRegistry:
    """Registry for managing connectors."""
    
    def __init__(self):
        self._connectors = {}
    
    def register(self, name: str, connector_class):
        """Register a connector class."""
        self._connectors[name] = connector_class
    
    def get_connector(self, name: str):
        """Get a connector class by name."""
        return self._connectors.get(name)
    
    def list_connectors(self) -> List[str]:
        """List all registered connectors."""
        return list(self._connectors.keys())
    
    def create_connector(self, name: str, file_path: str) -> BaseConnector:
        """Create a connector instance."""
        connector_class = self.get_connector(name)
        if not connector_class:
            raise ValueError(f"Unknown connector: {name}")
        return connector_class(file_path)


# Global registry instance
registry = ConnectorRegistry()
