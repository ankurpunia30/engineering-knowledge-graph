"""
Test configuration file.
"""
"""
Test configuration for the Engineering Knowledge Graph.
"""
import pytest
from pathlib import Path
import tempfile
import yaml

from graph.storage import GraphStorage
from connectors import registry


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory with test configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test docker-compose.yml
        docker_compose_data = {
            'version': '3.8',
            'services': {
                'test-service': {
                    'build': './test-service',
                    'ports': ['8080:8080'],
                    'environment': [
                        'DATABASE_URL=postgresql://postgres:secret@test-db:5432/test'
                    ],
                    'depends_on': ['test-db'],
                    'labels': {
                        'team': 'test-team',
                        'oncall': '@test-user'
                    }
                },
                'test-db': {
                    'image': 'postgres:15',
                    'environment': [
                        'POSTGRES_DB=test',
                        'POSTGRES_PASSWORD=secret'
                    ],
                    'labels': {
                        'team': 'test-team',
                        'type': 'database'
                    }
                }
            }
        }
        
        with open(temp_path / 'docker-compose.yml', 'w') as f:
            yaml.dump(docker_compose_data, f)
        
        # Create test teams.yaml
        teams_data = {
            'teams': [{
                'name': 'test-team',
                'lead': '@test-user',
                'slack_channel': '#test',
                'pagerduty_schedule': 'test-oncall',
                'owns': ['test-service', 'test-db']
            }]
        }
        
        with open(temp_path / 'teams.yaml', 'w') as f:
            yaml.dump(teams_data, f)
        
        yield temp_path


@pytest.fixture
def graph_storage():
    """Create a fresh graph storage instance."""
    return GraphStorage()
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
