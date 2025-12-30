"""
Teams connector for parsing teams.yaml files.
"""
import yaml
from typing import List, Dict, Any

from graph.models import Node, Edge, KnowledgeGraph, NodeType, EdgeType
from .base import BaseConnector, registry


class TeamsConnector(BaseConnector):
    """Connector for parsing teams configuration files."""
    
    def parse(self) -> KnowledgeGraph:
        """Parse teams.yaml and create knowledge graph."""
        kg = KnowledgeGraph()
        
        with open(self.file_path, 'r') as f:
            teams_data = yaml.safe_load(f)
        
        teams = teams_data.get('teams', [])
        
        # Create team nodes and ownership edges
        for team_data in teams:
            # Create team node
            team_node = self._create_team_node(team_data)
            kg.add_node(team_node)
            
            # Create ownership edges
            edges = self._create_ownership_edges(team_data)
            for edge in edges:
                kg.add_edge(edge)
        
        return kg
    
    def _create_team_node(self, team_data: Dict[str, Any]) -> Node:
        """Create a node for a team."""
        team_name = team_data.get('name')
        
        properties = {
            'source': 'teams',
            'file_path': str(self.file_path),
            'lead': team_data.get('lead', ''),
            'slack_channel': team_data.get('slack_channel', ''),
            'pagerduty_schedule': team_data.get('pagerduty_schedule', ''),
            'services_owned': team_data.get('owns', [])
        }
        
        return Node(
            id=f"team:{team_name}",
            type=NodeType.TEAM,
            name=team_name,
            properties=properties
        )
    
    def _create_ownership_edges(self, team_data: Dict[str, Any]) -> List[Edge]:
        """Create ownership edges for a team."""
        edges = []
        team_name = team_data.get('name')
        team_id = f"team:{team_name}"
        
        owned_services = team_data.get('owns', [])
        for service_name in owned_services:
            # We need to guess the service type since we don't have that context here
            # This will be resolved when graphs are merged
            possible_types = [NodeType.SERVICE, NodeType.DATABASE, NodeType.CACHE]
            
            for node_type in possible_types:
                target_id = f"{node_type.value}:{service_name}"
                
                edge = Edge(
                    id=f"edge:{team_name}-owns-{service_name}-{node_type.value}",
                    type=EdgeType.OWNS,
                    source=team_id,
                    target=target_id,
                    properties={'service_name': service_name}
                )
                edges.append(edge)
        
        return edges
    
    def validate(self) -> List[str]:
        """Validate the teams.yaml file."""
        issues = []
        
        try:
            with open(self.file_path, 'r') as f:
                teams_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML syntax: {e}")
            return issues
        
        if 'teams' not in teams_data:
            issues.append("No 'teams' section found")
            return issues
        
        teams = teams_data.get('teams', [])
        team_names = set()
        
        for i, team in enumerate(teams):
            if not isinstance(team, dict):
                issues.append(f"Team at index {i} is not a dictionary")
                continue
            
            # Check required fields
            if 'name' not in team:
                issues.append(f"Team at index {i} is missing 'name' field")
                continue
            
            team_name = team['name']
            if team_name in team_names:
                issues.append(f"Duplicate team name: {team_name}")
            team_names.add(team_name)
            
            # Check for required fields
            required_fields = ['lead', 'slack_channel', 'pagerduty_schedule', 'owns']
            for field in required_fields:
                if field not in team:
                    issues.append(f"Team '{team_name}' is missing required field: {field}")
            
            # Validate owns field
            owns = team.get('owns', [])
            if not isinstance(owns, list):
                issues.append(f"Team '{team_name}': 'owns' field must be a list")
            elif len(owns) == 0:
                issues.append(f"Team '{team_name}': 'owns' list is empty")
        
        return issues


# Register the connector
registry.register('teams', TeamsConnector)
