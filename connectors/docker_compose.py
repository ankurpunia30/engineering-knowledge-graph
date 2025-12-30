"""
Docker Compose connector for parsing docker-compose.yml files.
"""
import yaml
import re
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse

from graph.models import Node, Edge, KnowledgeGraph, NodeType, EdgeType
from .base import BaseConnector, registry


class DockerComposeConnector(BaseConnector):
    """Connector for parsing Docker Compose files."""
    
    def parse(self) -> KnowledgeGraph:
        """Parse docker-compose.yml and create knowledge graph."""
        kg = KnowledgeGraph()
        
        with open(self.file_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        services = compose_data.get('services', {})
        
        # First pass: Create all nodes
        for service_name, service_config in services.items():
            node = self._create_service_node(service_name, service_config)
            kg.add_node(node)
        
        # Second pass: Create edges
        for service_name, service_config in services.items():
            edges = self._create_service_edges(service_name, service_config, services)
            for edge in edges:
                kg.add_edge(edge)
        
        return kg
    
    def _create_service_node(self, service_name: str, config: Dict[str, Any]) -> Node:
        """Create a node for a service."""
        # Determine node type based on image or labels
        node_type = self._determine_node_type(config)
        
        properties = {
            'source': 'docker-compose',
            'file_path': str(self.file_path)
        }
        
        # Extract labels
        labels = config.get('labels', {})
        if isinstance(labels, list):
            # Convert list format to dict
            label_dict = {}
            for label in labels:
                if '=' in label:
                    key, value = label.split('=', 1)
                    label_dict[key] = value
            labels = label_dict
        
        properties.update(labels)
        
        # Extract ports
        ports = config.get('ports', [])
        if ports:
            # Extract the first external port
            port_mapping = ports[0]
            if ':' in str(port_mapping):
                external_port = str(port_mapping).split(':')[0].strip('"')
                properties['port'] = int(external_port)
        
        # Extract environment variables
        env_vars = config.get('environment', [])
        env_dict = {}
        if isinstance(env_vars, list):
            for env_var in env_vars:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    env_dict[key] = value
        elif isinstance(env_vars, dict):
            env_dict = env_vars
        
        properties['environment'] = env_dict
        
        # Extract image info
        if 'image' in config:
            properties['image'] = config['image']
        
        return Node(
            id=f"{node_type.value}:{service_name}",
            type=node_type,
            name=service_name,
            properties=properties
        )
    
    def _determine_node_type(self, config: Dict[str, Any]) -> NodeType:
        """Determine the type of node based on configuration."""
        labels = config.get('labels', {})
        
        # Check explicit type in labels
        if isinstance(labels, dict) and 'type' in labels:
            type_mapping = {
                'database': NodeType.DATABASE,
                'cache': NodeType.CACHE
            }
            return type_mapping.get(labels['type'], NodeType.SERVICE)
        
        # Infer from image
        image = config.get('image', '')
        if 'postgres' in image:
            return NodeType.DATABASE
        elif 'redis' in image:
            return NodeType.CACHE
        elif 'mongo' in image:
            return NodeType.DATABASE
        elif 'mysql' in image:
            return NodeType.DATABASE
        
        return NodeType.SERVICE
    
    def _create_service_edges(self, service_name: str, config: Dict[str, Any], 
                            all_services: Dict[str, Any]) -> List[Edge]:
        """Create edges for a service."""
        edges = []
        source_node_type = self._determine_node_type(config)
        source_id = f"{source_node_type.value}:{service_name}"
        
        # Process depends_on relationships
        depends_on = config.get('depends_on', [])
        for dep_name in depends_on:
            if dep_name in all_services:
                target_node_type = self._determine_node_type(all_services[dep_name])
                target_id = f"{target_node_type.value}:{dep_name}"
                
                edge = Edge(
                    id=f"edge:{service_name}-depends-on-{dep_name}",
                    type=EdgeType.DEPENDS_ON,
                    source=source_id,
                    target=target_id
                )
                edges.append(edge)
        
        # Process environment variables for service calls and database connections
        env_vars = config.get('environment', [])
        env_dict = {}
        if isinstance(env_vars, list):
            for env_var in env_vars:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    env_dict[key] = value
        elif isinstance(env_vars, dict):
            env_dict = env_vars
        
        for env_key, env_value in env_dict.items():
            # Look for service URLs
            if 'SERVICE_URL' in env_key:
                service_urls = self._extract_service_urls(env_value)
                for target_service in service_urls:
                    if target_service in all_services:
                        target_node_type = self._determine_node_type(all_services[target_service])
                        target_id = f"{target_node_type.value}:{target_service}"
                        
                        edge = Edge(
                            id=f"edge:{service_name}-calls-{target_service}",
                            type=EdgeType.CALLS,
                            source=source_id,
                            target=target_id,
                            properties={'via': env_key}
                        )
                        edges.append(edge)
            
            # Look for database connections
            elif 'DATABASE_URL' in env_key:
                db_connections = self._extract_database_connections(env_value)
                for db_name in db_connections:
                    if db_name in all_services:
                        target_id = f"database:{db_name}"
                        
                        edge = Edge(
                            id=f"edge:{service_name}-reads-from-{db_name}",
                            type=EdgeType.READS_FROM,
                            source=source_id,
                            target=target_id
                        )
                        edges.append(edge)
                        
                        edge = Edge(
                            id=f"edge:{service_name}-writes-to-{db_name}",
                            type=EdgeType.WRITES_TO,
                            source=source_id,
                            target=target_id
                        )
                        edges.append(edge)
            
            # Look for Redis connections
            elif 'REDIS_URL' in env_key:
                redis_connections = self._extract_redis_connections(env_value)
                for redis_name in redis_connections:
                    if redis_name in all_services:
                        target_id = f"cache:{redis_name}"
                        
                        edge = Edge(
                            id=f"edge:{service_name}-uses-{redis_name}",
                            type=EdgeType.USES,
                            source=source_id,
                            target=target_id
                        )
                        edges.append(edge)
        
        return edges
    
    def _extract_service_urls(self, url: str) -> List[str]:
        """Extract service names from service URLs."""
        services = []
        # Pattern: http://service-name:port
        pattern = r'http://([^:]+):\d+'
        matches = re.findall(pattern, url)
        services.extend(matches)
        return services
    
    def _extract_database_connections(self, db_url: str) -> List[str]:
        """Extract database service names from DATABASE_URL."""
        db_services = []
        # Pattern: postgresql://user:pass@db-service:port/database
        pattern = r'postgresql://[^@]+@([^:]+):\d+'
        matches = re.findall(pattern, db_url)
        db_services.extend(matches)
        return db_services
    
    def _extract_redis_connections(self, redis_url: str) -> List[str]:
        """Extract Redis service names from REDIS_URL."""
        redis_services = []
        # Pattern: redis://redis-service:port
        pattern = r'redis://([^:]+):\d+'
        matches = re.findall(pattern, redis_url)
        redis_services.extend(matches)
        return redis_services
    
    def validate(self) -> List[str]:
        """Validate the docker-compose.yml file."""
        issues = []
        
        try:
            with open(self.file_path, 'r') as f:
                compose_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML syntax: {e}")
            return issues
        
        if 'services' not in compose_data:
            issues.append("No 'services' section found")
            return issues
        
        services = compose_data.get('services', {})
        service_names = set(services.keys())
        
        # Check for missing dependencies
        for service_name, config in services.items():
            depends_on = config.get('depends_on', [])
            for dep in depends_on:
                if dep not in service_names:
                    issues.append(f"Service '{service_name}' depends on '{dep}' which is not defined")
            
            # Check environment variable references
            env_vars = config.get('environment', [])
            if isinstance(env_vars, list):
                for env_var in env_vars:
                    if '=' in env_var:
                        _, value = env_var.split('=', 1)
                        referenced_services = self._extract_service_urls(value)
                        referenced_services.extend(self._extract_database_connections(value))
                        referenced_services.extend(self._extract_redis_connections(value))
                        
                        for ref_service in referenced_services:
                            if ref_service not in service_names:
                                issues.append(
                                    f"Service '{service_name}' references '{ref_service}' "
                                    f"in environment variable but it's not defined"
                                )
        
        return issues


# Register the connector
registry.register('docker-compose', DockerComposeConnector)
