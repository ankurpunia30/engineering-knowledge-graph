"""
Kubernetes connector for parsing k8s deployment files.
"""
import yaml
import re
from typing import List, Dict, Any, Optional

from graph.models import Node, Edge, KnowledgeGraph, NodeType, EdgeType
from .base import BaseConnector, registry


class KubernetesConnector(BaseConnector):
    """Connector for parsing Kubernetes YAML files."""
    
    def parse(self) -> KnowledgeGraph:
        """Parse k8s YAML and create knowledge graph."""
        kg = KnowledgeGraph()
        
        with open(self.file_path, 'r') as f:
            # Handle multiple documents in one file
            documents = list(yaml.safe_load_all(f))
        
        # Group documents by type and name for easier processing
        deployments = {}
        services = {}
        
        for doc in documents:
            if not doc:
                continue
                
            kind = doc.get('kind')
            name = doc.get('metadata', {}).get('name')
            
            if kind == 'Deployment':
                deployments[name] = doc
            elif kind == 'Service':
                services[name] = doc
        
        # Create nodes and edges
        for deployment_name, deployment in deployments.items():
            # Create deployment node
            deployment_node = self._create_deployment_node(deployment)
            kg.add_node(deployment_node)
            
            # Create edges for this deployment
            edges = self._create_deployment_edges(deployment, deployments)
            for edge in edges:
                kg.add_edge(edge)
        
        for service_name, service in services.items():
            # Create service node
            service_node = self._create_service_node(service)
            kg.add_node(service_node)
        
        # Create edges between deployments and services
        for deployment_name, deployment in deployments.items():
            for service_name, service in services.items():
                if self._deployment_matches_service(deployment, service):
                    edge = Edge(
                        id=f"edge:{deployment_name}-deployed-as-{service_name}",
                        type=EdgeType.DEPLOYED_AS,
                        source=f"deployment:{deployment_name}",
                        target=f"k8s_service:{service_name}"
                    )
                    kg.add_edge(edge)
        
        return kg
    
    def _create_deployment_node(self, deployment: Dict[str, Any]) -> Node:
        """Create a node for a Kubernetes deployment."""
        metadata = deployment.get('metadata', {})
        spec = deployment.get('spec', {})
        template = spec.get('template', {})
        template_spec = template.get('spec', {})
        containers = template_spec.get('containers', [])
        
        deployment_name = metadata.get('name')
        
        properties = {
            'source': 'kubernetes',
            'file_path': str(self.file_path),
            'namespace': metadata.get('namespace', 'default'),
            'replicas': spec.get('replicas', 1),
            'labels': metadata.get('labels', {})
        }
        
        # Extract team from labels
        labels = metadata.get('labels', {})
        if 'team' in labels:
            properties['team'] = labels['team']
        
        # Extract container information
        if containers:
            container = containers[0]  # Use first container
            properties['image'] = container.get('image', '')
            properties['container_name'] = container.get('name', '')
            
            # Extract ports
            ports = container.get('ports', [])
            if ports:
                properties['port'] = ports[0].get('containerPort')
            
            # Extract environment variables
            env_vars = container.get('env', [])
            env_dict = {}
            for env_var in env_vars:
                name = env_var.get('name')
                value = env_var.get('value')
                if name and value:
                    env_dict[name] = value
            properties['environment'] = env_dict
            
            # Extract resources
            resources = container.get('resources', {})
            if resources:
                properties['resources'] = resources
        
        return Node(
            id=f"deployment:{deployment_name}",
            type=NodeType.DEPLOYMENT,
            name=deployment_name,
            properties=properties
        )
    
    def _create_service_node(self, service: Dict[str, Any]) -> Node:
        """Create a node for a Kubernetes service."""
        metadata = service.get('metadata', {})
        spec = service.get('spec', {})
        
        service_name = metadata.get('name')
        
        properties = {
            'source': 'kubernetes',
            'file_path': str(self.file_path),
            'namespace': metadata.get('namespace', 'default'),
            'selector': spec.get('selector', {}),
            'ports': spec.get('ports', [])
        }
        
        # Extract port information
        ports = spec.get('ports', [])
        if ports:
            port_info = ports[0]
            properties['port'] = port_info.get('port')
            properties['target_port'] = port_info.get('targetPort')
        
        return Node(
            id=f"k8s_service:{service_name}",
            type=NodeType.K8S_SERVICE,
            name=service_name,
            properties=properties
        )
    
    def _create_deployment_edges(self, deployment: Dict[str, Any], 
                               all_deployments: Dict[str, Any]) -> List[Edge]:
        """Create edges for a deployment."""
        edges = []
        
        metadata = deployment.get('metadata', {})
        spec = deployment.get('spec', {})
        template = spec.get('template', {})
        template_spec = template.get('spec', {})
        containers = template_spec.get('containers', [])
        
        deployment_name = metadata.get('name')
        source_id = f"deployment:{deployment_name}"
        
        # Process environment variables for service dependencies
        if containers:
            container = containers[0]
            env_vars = container.get('env', [])
            
            for env_var in env_vars:
                name = env_var.get('name')
                value = env_var.get('value', '')
                
                if 'SERVICE_URL' in name and value:
                    # Extract service names from k8s service URLs
                    # Pattern: http://service-name.namespace.svc.cluster.local:port
                    service_names = self._extract_k8s_service_urls(value)
                    for target_service in service_names:
                        # Check if this service exists as a deployment
                        if target_service in all_deployments:
                            edge = Edge(
                                id=f"edge:{deployment_name}-calls-{target_service}",
                                type=EdgeType.CALLS,
                                source=source_id,
                                target=f"deployment:{target_service}",
                                properties={'via': name}
                            )
                            edges.append(edge)
        
        return edges
    
    def _extract_k8s_service_urls(self, url: str) -> List[str]:
        """Extract service names from Kubernetes service URLs."""
        services = []
        # Pattern: http://service-name.namespace.svc.cluster.local:port
        pattern = r'http://([^.]+)\.[\w-]+\.svc\.cluster\.local:\d+'
        matches = re.findall(pattern, url)
        services.extend(matches)
        return services
    
    def _deployment_matches_service(self, deployment: Dict[str, Any], 
                                  service: Dict[str, Any]) -> bool:
        """Check if a deployment matches a service based on selectors."""
        service_selector = service.get('spec', {}).get('selector', {})
        deployment_labels = (deployment.get('spec', {})
                           .get('template', {})
                           .get('metadata', {})
                           .get('labels', {}))
        
        if not service_selector:
            return False
        
        # Check if all selector labels match deployment labels
        for key, value in service_selector.items():
            if deployment_labels.get(key) != value:
                return False
        
        return True
    
    def validate(self) -> List[str]:
        """Validate the Kubernetes YAML file."""
        issues = []
        
        try:
            with open(self.file_path, 'r') as f:
                documents = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML syntax: {e}")
            return issues
        
        deployments = {}
        services = {}
        
        for i, doc in enumerate(documents):
            if not doc:
                continue
            
            if 'kind' not in doc:
                issues.append(f"Document {i}: Missing 'kind' field")
                continue
            
            if 'metadata' not in doc:
                issues.append(f"Document {i}: Missing 'metadata' field")
                continue
            
            metadata = doc['metadata']
            if 'name' not in metadata:
                issues.append(f"Document {i}: Missing 'name' in metadata")
                continue
            
            kind = doc['kind']
            name = metadata['name']
            
            if kind == 'Deployment':
                deployments[name] = doc
                # Validate deployment structure
                if 'spec' not in doc:
                    issues.append(f"Deployment '{name}': Missing 'spec' field")
                else:
                    spec = doc['spec']
                    if 'template' not in spec:
                        issues.append(f"Deployment '{name}': Missing 'template' in spec")
                    elif 'spec' not in spec['template']:
                        issues.append(f"Deployment '{name}': Missing 'spec' in template")
                    elif 'containers' not in spec['template']['spec']:
                        issues.append(f"Deployment '{name}': Missing 'containers' in template spec")
            
            elif kind == 'Service':
                services[name] = doc
                # Validate service structure
                if 'spec' not in doc:
                    issues.append(f"Service '{name}': Missing 'spec' field")
                else:
                    spec = doc['spec']
                    if 'selector' not in spec:
                        issues.append(f"Service '{name}': Missing 'selector' in spec")
                    if 'ports' not in spec:
                        issues.append(f"Service '{name}': Missing 'ports' in spec")
        
        # Check if services have matching deployments
        for service_name, service in services.items():
            has_matching_deployment = any(
                self._deployment_matches_service(deployment, service)
                for deployment in deployments.values()
            )
            if not has_matching_deployment:
                issues.append(f"Service '{service_name}': No matching deployment found")
        
        return issues


# Register the connector
registry.register('kubernetes', KubernetesConnector)
