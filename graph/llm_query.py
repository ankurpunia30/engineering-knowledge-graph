"""
LLM-powered query engine using Groq for natural language understanding.
"""
import json
import re
from typing import Dict, Any, List, Optional
from groq import Groq
import os
from dotenv import load_dotenv

from .storage import GraphStorage
from .models import NodeType, EdgeType

load_dotenv()


class LLMQueryEngine:
    """Enhanced query engine powered by Groq LLM."""
    
    def __init__(self, storage: GraphStorage):
        self.storage = storage
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"  # Production model that supports JSON response
        
    def query(self, question: str) -> Dict[str, Any]:
        """Process a natural language query using LLM understanding."""
        try:
            # Get graph context for the LLM
            graph_context = self._get_graph_context()
            
            # Create prompt for query analysis
            prompt = self._create_analysis_prompt(question, graph_context)
            
            # Get LLM analysis
            analysis = self._get_llm_analysis(prompt)
            
            if not analysis:
                return self._fallback_query(question)
            
            # Execute the query based on LLM analysis
            return self._execute_analyzed_query(question, analysis)
            
        except Exception as e:
            print(f"LLM query failed: {e}")
            return self._fallback_query(question)
    
    def _get_graph_context(self) -> Dict[str, Any]:
        """Get relevant context about the graph structure."""
        stats = self.storage.get_stats()
        
        # Get sample services, teams, and databases
        services = [node.name for node in self.storage.get_nodes_by_type(NodeType.SERVICE)][:10]
        databases = [node.name for node in self.storage.get_nodes_by_type(NodeType.DATABASE)]
        teams = [node.name for node in self.storage.get_nodes_by_type(NodeType.TEAM)]
        
        return {
            "total_nodes": stats.get("total_nodes", 0),
            "total_edges": stats.get("total_edges", 0),
            "sample_services": services,
            "databases": databases,
            "teams": teams,
            "node_types": list(stats.get("node_types", {}).keys()),
            "edge_types": list(stats.get("edge_types", {}).keys())
        }
    
    def _create_analysis_prompt(self, question: str, context: Dict[str, Any]) -> str:
        """Create a structured prompt for query analysis."""
        return f"""
You are an expert system for analyzing questions about engineering infrastructure and service dependencies.

INFRASTRUCTURE CONTEXT:
- Services: {', '.join(context['sample_services'])}
- Databases: {', '.join(context['databases'])}
- Teams: {', '.join(context['teams'])}
- Total nodes: {context['total_nodes']}, Total relationships: {context['total_edges']}

QUERY TYPES YOU CAN HANDLE:
1. "blast_radius" - Questions about what breaks when something goes down
2. "ownership" - Questions about who owns or is responsible for services
3. "dependencies" - Questions about service connections and relationships
4. "team_info" - Questions about teams and what they own
5. "service_info" - Questions about specific services
6. "database_info" - Questions about databases and their connections
7. "general" - Overview or statistics questions

USER QUESTION: "{question}"

Analyze this question and respond with a JSON object containing:
{{
    "query_type": "one of the types above",
    "entities": ["list", "of", "entity", "names", "mentioned"],
    "intent": "brief description of what the user wants to know",
    "confidence": 0.95,
    "suggested_entities": ["if", "entities", "seem", "incorrect", "suggest", "alternatives"]
}}

Be precise with entity extraction. Look for service names, database names, team names.
If you can't identify entities clearly, set confidence below 0.7 and suggest alternatives.

RESPOND WITH ONLY THE JSON OBJECT:
"""
    
    def _get_llm_analysis(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get analysis from Groq LLM."""
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return None
    
    def _execute_analyzed_query(self, question: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query based on LLM analysis."""
        query_type = analysis.get("query_type", "general")
        entities = analysis.get("entities", [])
        intent = analysis.get("intent", "")
        confidence = analysis.get("confidence", 0.0)
        
        result = {
            "query": question,
            "type": query_type,
            "intent": intent,
            "confidence": confidence,
            "llm_powered": True
        }
        
        # Route to appropriate handler
        if query_type == "blast_radius":
            result.update(self._handle_blast_radius(entities))
        elif query_type == "ownership":
            result.update(self._handle_ownership(entities))
        elif query_type == "dependencies":
            result.update(self._handle_dependencies(entities))
        elif query_type == "team_info":
            result.update(self._handle_team_info(entities))
        elif query_type == "service_info":
            result.update(self._handle_service_info(entities))
        elif query_type == "database_info":
            result.update(self._handle_database_info(entities))
        else:
            result.update(self._handle_general_info())
        
        return result
    
    def _handle_blast_radius(self, entities: List[str]) -> Dict[str, Any]:
        """Handle blast radius analysis queries."""
        if not entities:
            return {"error": "No service specified for blast radius analysis"}
        
        service_name = entities[0]
        
        # Try to find the service
        possible_ids = [
            f"service:{service_name}",
            f"database:{service_name}",
            f"cache:{service_name}"
        ]
        
        for node_id in possible_ids:
            if self.storage.get_node(node_id):
                blast_radius = self.storage.get_blast_radius(node_id, max_depth=3)
                
                # Enhanced analysis
                affected_teams = {}
                for team_name, services in blast_radius.get("teams_affected", {}).items():
                    team_node = self.storage.get_node(f"team:{team_name}")
                    if team_node:
                        affected_teams[team_name] = {
                            "services": services,
                            "lead": team_node.properties.get("lead", "Unknown"),
                            "slack": team_node.properties.get("slack_channel", "Unknown"),
                            "count": len(services)
                        }
                
                blast_radius.update({
                    "service_analyzed": service_name,
                    "team_details": affected_teams,
                    "severity": "HIGH" if blast_radius.get("affected_services_count", 0) > 5 else 
                               "MEDIUM" if blast_radius.get("affected_services_count", 0) > 2 else "LOW"
                })
                
                return blast_radius
        
        # Suggest similar services
        all_services = [node.name for node in self.storage.get_all_nodes()]
        suggestions = [s for s in all_services if service_name.lower() in s.lower() or s.lower() in service_name.lower()]
        
        return {
            "error": f"Service '{service_name}' not found",
            "suggestions": suggestions[:5]
        }
    
    def _normalize_entity_name(self, entity_name: str) -> str:
        """Normalize entity name by removing spaces and converting to lowercase."""
        return entity_name.lower().replace(' ', '-').replace('_', '-')
    
    def _find_node_fuzzy(self, entity_name: str) -> Optional[Any]:
        """Try to find a node with fuzzy matching."""
        normalized = self._normalize_entity_name(entity_name)
        print(f"🔍 Fuzzy matching: original='{entity_name}', normalized='{normalized}'")
        
        # Try different prefixes
        prefixes = ['service:', 'database:', 'cache:', 'team:']
        
        for prefix in prefixes:
            # Try exact match with prefix
            search_id = f"{prefix}{normalized}"
            print(f"   Trying: {search_id}")
            node = self.storage.get_node(search_id)
            if node:
                print(f"   ✅ Found: {node.name}")
                return node
            
            # Try with original name
            search_id = f"{prefix}{entity_name}"
            print(f"   Trying: {search_id}")
            node = self.storage.get_node(search_id)
            if node:
                print(f"   ✅ Found: {node.name}")
                return node
        
        # Try fuzzy search across all nodes
        print(f"   Trying fuzzy search across all nodes...")
        all_nodes = self.storage.get_all_nodes()
        for node in all_nodes:
            node_name_normalized = self._normalize_entity_name(node.name)
            if node_name_normalized == normalized:
                print(f"   ✅ Found exact match: {node.name}")
                return node
            if normalized in node_name_normalized or node_name_normalized in normalized:
                print(f"   ✅ Found substring match: {node.name}")
                return node
        
        print(f"   ❌ No match found")
        return None
    
    def _handle_ownership(self, entities: List[str]) -> Dict[str, Any]:
        """Handle ownership queries."""
        if not entities:
            return {"error": "No service or team specified"}
        
        entity_name = entities[0]
        
        # Try fuzzy matching first
        node = self._find_node_fuzzy(entity_name)
        if node:
            entity_name = node.name
            
            # If it's a service/database/cache
            if node.type.value in ['service', 'database', 'cache']:
                team_name = node.properties.get("team", "Unknown")
                team_node = self.storage.get_node(f"team:{team_name}")
                
                return {
                    "service": node.name,
                    "service_type": node.type.value,
                    "team": team_name,
                    "team_lead": team_node.properties.get("lead") if team_node else "Unknown",
                    "slack_channel": team_node.properties.get("slack_channel") if team_node else "Unknown",
                    "oncall": node.properties.get("oncall", "Unknown"),
                    "additional_properties": {k: v for k, v in node.properties.items() 
                                            if k not in ["team", "oncall"]}
                }
            
            # If it's a team
            if node.type.value == 'team':
                owned_services = self.storage.get_team_ownership(node.name)
                return {
                    "team": node.name,
                    "team_lead": node.properties.get("lead", "Unknown"),
                    "slack_channel": node.properties.get("slack_channel", "Unknown"),
                    "owned_services": [{"name": s.name, "type": s.type.value} for s in owned_services],
                    "services_count": len(owned_services)
                }
        
        # If not found, suggest similar names
        all_nodes = self.storage.get_all_nodes()
        normalized_query = self._normalize_entity_name(entity_name)
        suggestions = []
        for n in all_nodes:
            n_normalized = self._normalize_entity_name(n.name)
            if normalized_query in n_normalized or n_normalized in normalized_query:
                suggestions.append(n.name)
        
        return {
            "error": f"'{entity_name}' not found in the graph",
            "suggestions": suggestions[:5] if suggestions else ["Try checking the graph for exact service names"],
            "tip": "Service names are case-sensitive and may contain hyphens (e.g., 'notification-service')"
        }
    
    def _handle_dependencies(self, entities: List[str]) -> Dict[str, Any]:
        """Handle dependency and connection queries."""
        if not entities:
            return {"error": "No service specified"}
        
        service_name = entities[0]
        possible_ids = [
            f"service:{service_name}",
            f"database:{service_name}",
            f"cache:{service_name}"
        ]
        
        for node_id in possible_ids:
            node = self.storage.get_node(node_id)
            if node:
                # Get dependencies and dependents
                dependencies = self.storage.get_dependencies(node_id, depth=2)
                dependents = self.storage.get_dependents(node_id, depth=2)
                
                # Get detailed connection info
                outgoing_edges = self.storage.kg.get_edges_from_node(node_id)
                incoming_edges = self.storage.kg.get_edges_to_node(node_id)
                
                outgoing_details = []
                for edge in outgoing_edges:
                    target_node = self.storage.get_node(edge.target)
                    if target_node:
                        outgoing_details.append({
                            "name": target_node.name,
                            "type": target_node.type.value,
                            "relationship": edge.type.value,
                            "team": target_node.properties.get("team", "Unknown")
                        })
                
                incoming_details = []
                for edge in incoming_edges:
                    source_node = self.storage.get_node(edge.source)
                    if source_node:
                        incoming_details.append({
                            "name": source_node.name,
                            "type": source_node.type.value,
                            "relationship": edge.type.value,
                            "team": source_node.properties.get("team", "Unknown")
                        })
                
                return {
                    "service": service_name,
                    "service_type": node.type.value,
                    "dependencies": list(dependencies),
                    "dependents": list(dependents),
                    "outgoing_connections": outgoing_details,
                    "incoming_connections": incoming_details,
                    "dependency_depth": len(dependencies),
                    "dependent_depth": len(dependents)
                }
        
        return {"error": f"Service '{service_name}' not found"}
    
    def _handle_team_info(self, entities: List[str]) -> Dict[str, Any]:
        """Handle team information queries."""
        teams = self.storage.get_nodes_by_type(NodeType.TEAM)
        
        if entities:
            # Specific team query
            team_name = entities[0]
            team_node = self.storage.get_node(f"team:{team_name}")
            if team_node:
                owned_services = self.storage.get_team_ownership(team_name)
                service_types = {}
                for service in owned_services:
                    stype = service.type.value
                    service_types[stype] = service_types.get(stype, 0) + 1
                
                return {
                    "team": team_name,
                    "lead": team_node.properties.get("lead", "Unknown"),
                    "slack_channel": team_node.properties.get("slack_channel", "Unknown"),
                    "pagerduty": team_node.properties.get("pagerduty_schedule", "Unknown"),
                    "owned_services": [{"name": s.name, "type": s.type.value} for s in owned_services],
                    "service_breakdown": service_types,
                    "total_services": len(owned_services)
                }
        
        # All teams overview
        team_info = []
        for team in teams:
            owned_services = self.storage.get_team_ownership(team.name)
            team_info.append({
                "name": team.name,
                "lead": team.properties.get("lead", "Unknown"),
                "services_count": len(owned_services),
                "slack": team.properties.get("slack_channel", "Unknown")
            })
        
        return {
            "teams": team_info,
            "total_teams": len(teams)
        }
    
    def _handle_service_info(self, entities: List[str]) -> Dict[str, Any]:
        """Handle service information queries."""
        services = self.storage.get_nodes_by_type(NodeType.SERVICE)
        
        if entities:
            service_name = entities[0]
            service_node = self.storage.get_node(f"service:{service_name}")
            if service_node:
                deps = self.storage.get_dependencies(service_node.id)
                dependents = self.storage.get_dependents(service_node.id)
                
                return {
                    "service": service_name,
                    "team": service_node.properties.get("team", "Unknown"),
                    "oncall": service_node.properties.get("oncall", "Unknown"),
                    "port": service_node.properties.get("port", "Unknown"),
                    "dependencies_count": len(deps),
                    "dependents_count": len(dependents),
                    "properties": service_node.properties
                }
        
        # All services overview
        service_summary = []
        for service in services:
            service_summary.append({
                "name": service.name,
                "team": service.properties.get("team", "Unknown"),
                "port": service.properties.get("port", "N/A")
            })
        
        return {
            "services": service_summary,
            "total_services": len(services)
        }
    
    def _handle_database_info(self, entities: List[str]) -> Dict[str, Any]:
        """Handle database information queries."""
        databases = self.storage.get_nodes_by_type(NodeType.DATABASE)
        
        db_info = []
        for db in databases:
            incoming_edges = self.storage.kg.get_edges_to_node(db.id)
            connected_services = []
            
            for edge in incoming_edges:
                if edge.type in [EdgeType.READS_FROM, EdgeType.WRITES_TO]:
                    source_node = self.storage.get_node(edge.source)
                    if source_node:
                        connected_services.append({
                            "name": source_node.name,
                            "relationship": edge.type.value
                        })
            
            db_info.append({
                "name": db.name,
                "team": db.properties.get("team", "Unknown"),
                "encrypted": db.properties.get("encrypted", "false") == "true",
                "image": db.properties.get("image", "Unknown"),
                "connected_services": connected_services,
                "connections_count": len(connected_services)
            })
        
        return {
            "databases": db_info,
            "total_databases": len(databases)
        }
    
    def _handle_general_info(self) -> Dict[str, Any]:
        """Handle general information queries."""
        return self.storage.get_stats()
    
    def _fallback_query(self, question: str) -> Dict[str, Any]:
        """Fallback to regex-based query processing."""
        from .query import QueryEngine
        fallback_engine = QueryEngine(self.storage)
        result = fallback_engine.query(question)
        result["llm_powered"] = False
        result["fallback"] = True
        return result
