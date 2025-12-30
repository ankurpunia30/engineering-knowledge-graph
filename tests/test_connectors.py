"""
Tests for the connectors.
"""
import pytest
import tempfile
import os
from pathlib import Path

from connectors import registry, DockerComposeConnector, TeamsConnector, KubernetesConnector
from graph.models import NodeType, EdgeType


class TestDockerComposeConnector:
    """Test the Docker Compose connector."""
    
    def setup_method(self):
        """Setup test data."""
        self.docker_compose_content = """
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - CACHE_URL=redis://redis:6379
    labels:
      team: web-team
      oncall: "@alice"

  db:
    image: postgres:15
    labels:
      team: db-team
      type: database

  redis:
    image: redis:7
    labels:
      team: cache-team
      type: cache
"""
    
    def test_parse_docker_compose(self):
        """Test parsing docker-compose.yml."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(self.docker_compose_content)
            f.flush()
            
            try:
                connector = DockerComposeConnector(f.name)
                kg = connector.parse()
                
                # Check nodes
                assert len(kg.nodes) == 3
                
                # Check service node
                web_node = kg.get_node('service:web')
                assert web_node is not None
                assert web_node.type == NodeType.SERVICE
                assert web_node.properties.get('team') == 'web-team'
                
                # Check database node
                db_node = kg.get_node('database:db')
                assert db_node is not None
                assert db_node.type == NodeType.DATABASE
                
                # Check cache node
                redis_node = kg.get_node('cache:redis')
                assert redis_node is not None
                assert redis_node.type == NodeType.CACHE
                
                # Check edges
                assert len(kg.edges) > 0
                
                # Check for dependency edge
                dep_edges = [e for e in kg.edges.values() if e.type == EdgeType.DEPENDS_ON]
                assert len(dep_edges) >= 2  # web depends on db and redis
                
            finally:
                os.unlink(f.name)
    
    def test_validate_docker_compose(self):
        """Test validation of docker-compose.yml."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(self.docker_compose_content)
            f.flush()
            
            try:
                connector = DockerComposeConnector(f.name)
                issues = connector.validate()
                
                # Should have no issues with valid config
                assert len(issues) == 0
                
            finally:
                os.unlink(f.name)


class TestTeamsConnector:
    """Test the Teams connector."""
    
    def setup_method(self):
        """Setup test data."""
        self.teams_content = """
teams:
  - name: web-team
    lead: "@alice"
    slack_channel: "#web-eng"
    pagerduty_schedule: "web-oncall"
    owns:
      - web-service
      - web-db

  - name: data-team
    lead: "@bob"
    slack_channel: "#data-eng"
    pagerduty_schedule: "data-oncall"
    owns:
      - analytics-service
      - data-warehouse
"""
    
    def test_parse_teams(self):
        """Test parsing teams.yaml."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(self.teams_content)
            f.flush()
            
            try:
                connector = TeamsConnector(f.name)
                kg = connector.parse()
                
                # Check team nodes
                team_nodes = [n for n in kg.nodes.values() if n.type == NodeType.TEAM]
                assert len(team_nodes) == 2
                
                web_team = kg.get_node('team:web-team')
                assert web_team is not None
                assert web_team.properties.get('lead') == '@alice'
                assert web_team.properties.get('slack_channel') == '#web-eng'
                
                # Check ownership edges
                ownership_edges = [e for e in kg.edges.values() if e.type == EdgeType.OWNS]
                assert len(ownership_edges) > 0
                
            finally:
                os.unlink(f.name)
    
    def test_validate_teams(self):
        """Test validation of teams.yaml."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(self.teams_content)
            f.flush()
            
            try:
                connector = TeamsConnector(f.name)
                issues = connector.validate()
                
                # Should have no issues with valid config
                assert len(issues) == 0
                
            finally:
                os.unlink(f.name)


class TestKubernetesConnector:
    """Test the Kubernetes connector."""
    
    def setup_method(self):
        """Setup test data."""
        self.k8s_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  labels:
    app: web-app
    team: web-team
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
        - name: web-app
          image: myapp:v1.0.0
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: web-app
  namespace: production
spec:
  selector:
    app: web-app
  ports:
    - port: 80
      targetPort: 8080
"""
    
    def test_parse_kubernetes(self):
        """Test parsing k8s YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(self.k8s_content)
            f.flush()
            
            try:
                connector = KubernetesConnector(f.name)
                kg = connector.parse()
                
                # Check nodes
                deployment_nodes = [n for n in kg.nodes.values() if n.type == NodeType.DEPLOYMENT]
                service_nodes = [n for n in kg.nodes.values() if n.type == NodeType.K8S_SERVICE]
                
                assert len(deployment_nodes) == 1
                assert len(service_nodes) == 1
                
                # Check deployment node
                deployment = kg.get_node('deployment:web-app')
                assert deployment is not None
                assert deployment.properties.get('team') == 'web-team'
                assert deployment.properties.get('replicas') == 3
                
                # Check service node
                service = kg.get_node('k8s_service:web-app')
                assert service is not None
                assert service.properties.get('port') == 80
                
            finally:
                os.unlink(f.name)
    
    def test_validate_kubernetes(self):
        """Test validation of k8s YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(self.k8s_content)
            f.flush()
            
            try:
                connector = KubernetesConnector(f.name)
                issues = connector.validate()
                
                # Should have no issues with valid config
                assert len(issues) == 0
                
            finally:
                os.unlink(f.name)


class TestConnectorRegistry:
    """Test the connector registry."""
    
    def test_registry_operations(self):
        """Test registry registration and retrieval."""
        # Test listing connectors
        connectors = registry.list_connectors()
        assert 'docker-compose' in connectors
        assert 'teams' in connectors
        assert 'kubernetes' in connectors
        
        # Test getting connector class
        docker_connector_class = registry.get_connector('docker-compose')
        assert docker_connector_class == DockerComposeConnector
        
        # Test unknown connector
        unknown = registry.get_connector('unknown')
        assert unknown is None
