"""
Natural Language Interface for the Engineering Knowledge Graph - Part 4 Implementation

This module provides a comprehensive natural language interface that translates
user queries into structured graph operations using LLM capabilities.

Key Features:
- Intent recognition and parsing
- Context-aware conversation handling
- Follow-up query support
- Graceful error handling for ambiguous queries
- Multiple LLM provider support (OpenAI, Anthropic, local models)
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents we can handle."""
    OWNERSHIP = "ownership"
    DEPENDENCY = "dependency" 
    BLAST_RADIUS = "blast_radius"
    EXPLORATION = "exploration"
    PATH = "path"
    FOLLOW_UP = "follow_up"
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class ConversationContext:
    """Maintains conversation state for follow-up queries."""
    last_query: Optional[str] = None
    last_intent: Optional[IntentType] = None
    last_entities: List[str] = None
    last_results: Optional[Dict] = None
    
    def __post_init__(self):
        if self.last_entities is None:
            self.last_entities = []


@dataclass
class ParsedQuery:
    """Structured representation of a parsed natural language query."""
    intent: IntentType
    entities: List[str]
    filters: Dict[str, Any]
    confidence: float
    original_query: str
    clarifications_needed: List[str] = None
    
    def __post_init__(self):
        if self.clarifications_needed is None:
            self.clarifications_needed = []


class LLMProvider:
    """Abstract base class for LLM providers."""
    
    def __init__(self):
        self.name = "base"
    
    def parse_intent(self, query: str, context: ConversationContext) -> ParsedQuery:
        """Parse user intent from natural language query."""
        raise NotImplementedError
    
    def format_response(self, query_result: Dict, intent: IntentType, original_query: str) -> str:
        """Format query results into human-readable response."""
        raise NotImplementedError


class LocalPatternProvider(LLMProvider):
    """
    Local pattern-based provider that doesn't require external APIs.
    Uses rule-based pattern matching for intent recognition.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "local_patterns"
        
        # Define intent patterns
        self.intent_patterns = {
            IntentType.OWNERSHIP: [
                r"who owns? (?:the )?(.+)",
                r"what (?:does|do) (?:the )?(.+) team own",
                r"who should i (?:page|contact) if (.+) (?:is down|fails)",
                r"(?:owner|ownership) of (.+)",
                r"(.+) (?:owner|team)",
                r"who (?:manages|maintains) (.+)"
            ],
            IntentType.DEPENDENCY: [
                r"what (?:does|do) (.+) depend on",
                r"what (?:services|databases) (?:does|do) (.+) use",
                r"dependencies (?:of|for) (.+)",
                r"what (.+) (?:needs|requires)",
                r"(.+) depends on what",
                r"show (?:me )?(?:the )?dependencies (?:of|for) (.+)"
            ],
            IntentType.BLAST_RADIUS: [
                r"what breaks if (.+) (?:goes down|fails)",
                r"(?:what'?s )?(?:the )?blast radius (?:of|for) (.+)",
                r"if (.+) (?:fails|crashes), what'?s affected",
                r"impact (?:of|if) (.+) (?:going down|failing)",
                r"what (?:gets|is) affected (?:if|when) (.+) (?:fails|is down)",
                r"downstream impact of (.+)"
            ],
            IntentType.EXPLORATION: [
                r"list (?:all )?(.+)",
                r"show (?:me )?(?:all )?(.+)",
                r"what (.+) (?:are there|exist)",
                r"(?:give me|get) (?:all )?(.+)",
                r"find (?:all )?(.+)",
                r"(?:services|databases|teams|nodes)"
            ],
            IntentType.PATH: [
                r"how (?:does|do) (.+) connect to (.+)",
                r"what'?s between (.+) and (.+)",
                r"path (?:from )?(.+) to (.+)",
                r"route (?:from )?(.+) to (.+)",
                r"connection (?:from )?(.+) to (.+)",
                r"how to get from (.+) to (.+)"
            ],
            IntentType.FOLLOW_UP: [
                r"what about (.+)",
                r"who owns that",
                r"what (?:does|do) that depend on",
                r"what breaks if that fails",
                r"and (.+)",
                r"also (.+)",
                r"tell me about (.+)"
            ],
            IntentType.GREETING: [
                r"hi|hello|hey|greetings",
                r"good (?:morning|afternoon|evening)",
                r"how are you",
                r"what'?s up"
            ],
            IntentType.HELP: [
                r"help|assistance",
                r"what can you do",
                r"how (?:does this|do i) work",
                r"commands|options",
                r"examples"
            ]
        }
    
    def parse_intent(self, query: str, context: ConversationContext) -> ParsedQuery:
        """Parse user intent using pattern matching."""
        query_lower = query.lower().strip()
        
        # Check for each intent type
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    entities = [group.strip() for group in match.groups() if group]
                    
                    # Handle follow-up queries
                    if intent_type == IntentType.FOLLOW_UP and context.last_entities:
                        if not entities or entities[0] in ["that", "it", "this"]:
                            entities = context.last_entities
                            # Inherit intent from context if it's a generic follow-up
                            if context.last_intent and any(word in query_lower for word in ["that", "it", "this"]):
                                intent_type = context.last_intent
                    
                    # Extract filters
                    filters = self._extract_filters(query_lower)
                    
                    return ParsedQuery(
                        intent=intent_type,
                        entities=entities,
                        filters=filters,
                        confidence=0.8,  # High confidence for pattern matches
                        original_query=query
                    )
        
        # Default to unknown intent
        return ParsedQuery(
            intent=IntentType.UNKNOWN,
            entities=[],
            filters={},
            confidence=0.1,
            original_query=query,
            clarifications_needed=["I didn't understand your query. Could you rephrase it?"]
        )
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters from the query text."""
        filters = {}
        
        # Extract node type filters
        if any(word in query for word in ["service", "services"]):
            filters["node_type"] = "service"
        elif any(word in query for word in ["database", "databases", "db"]):
            filters["node_type"] = "database"
        elif any(word in query for word in ["team", "teams"]):
            filters["node_type"] = "team"
        elif any(word in query for word in ["cache", "redis"]):
            filters["node_type"] = "cache"
        
        # Extract team filters
        team_match = re.search(r"(.+?)\s+team", query)
        if team_match:
            filters["team"] = team_match.group(1).strip()
        
        return filters
    
    def format_response(self, query_result: Dict, intent: IntentType, original_query: str) -> str:
        """Format query results into human-readable response."""
        if not query_result.get("success", False):
            error_msg = query_result.get("error", "Unknown error occurred")
            return f"❌ {error_msg}"
        
        data = query_result.get("data", {})
        
        if intent == IntentType.OWNERSHIP:
            return self._format_ownership_response(data)
        elif intent == IntentType.DEPENDENCY:
            return self._format_dependency_response(data)
        elif intent == IntentType.BLAST_RADIUS:
            return self._format_blast_radius_response(data)
        elif intent == IntentType.EXPLORATION:
            return self._format_exploration_response(data, query_result.get("metadata", {}))
        elif intent == IntentType.PATH:
            return self._format_path_response(data)
        else:
            return self._format_generic_response(data, intent)
    
    def _format_ownership_response(self, data: Dict) -> str:
        """Format ownership query response."""
        if "owner" in data:
            owner = data["owner"]
            node = data.get("node", {})
            
            response = f"🏢 **{node.get('name', 'Item')}** is owned by the **{owner.get('name', 'Unknown')} team**\n\n"
            
            if owner.get("lead") != "Unknown":
                response += f"👤 **Team Lead:** {owner['lead']}\n"
            if owner.get("slack_channel") != "Unknown":
                response += f"💬 **Slack:** {owner['slack_channel']}\n"
            if owner.get("oncall") != "Unknown":
                response += f"📞 **On-call:** {owner['oncall']}\n"
            
            return response
        
        return "ℹ️ No ownership information found."
    
    def _format_dependency_response(self, data: Dict) -> str:
        """Format dependency query response."""
        if "dependencies" in data:
            deps = data["dependencies"]
            node_id = data.get("node_id", "Unknown")
            
            if not deps:
                return f"✅ **{node_id}** has no dependencies!"
            
            response = f"🔗 **{node_id}** depends on {len(deps)} service(s):\n\n"
            
            for i, dep in enumerate(deps[:10], 1):  # Limit to first 10
                response += f"{i}. **{dep.get('name', 'Unknown')}** ({dep.get('type', 'unknown')})\n"
            
            if len(deps) > 10:
                response += f"\n... and {len(deps) - 10} more dependencies"
            
            return response
        
        return "ℹ️ No dependency information found."
    
    def _format_blast_radius_response(self, data: Dict) -> str:
        """Format blast radius query response."""
        if "total_affected" in data:
            source = data.get("source_node", {})
            total = data.get("total_affected", 0)
            severity = data.get("severity", "unknown")
            teams = data.get("teams_affected", {})
            
            # Severity emoji
            severity_emoji = {
                "low": "🟢",
                "medium": "🟡", 
                "high": "🟠",
                "critical": "🔴"
            }.get(severity, "⚪")
            
            response = f"💥 **Blast Radius Analysis for {source.get('name', 'Unknown')}**\n\n"
            response += f"{severity_emoji} **Severity:** {severity.title()}\n"
            response += f"📊 **Total Affected:** {total} services\n"
            response += f"⬆️ **Upstream Impact:** {data.get('upstream_affected', 0)} services\n"
            response += f"⬇️ **Downstream Impact:** {data.get('downstream_affected', 0)} services\n\n"
            
            if teams:
                response += "👥 **Teams Affected:**\n"
                for team_name, team_info in teams.items():
                    affected_services = team_info.get("affected_services", [])
                    response += f"• **{team_name}**: {len(affected_services)} services affected\n"
                    if team_info.get("lead") != "Unknown":
                        response += f"  👤 Lead: {team_info['lead']}\n"
                    if team_info.get("slack_channel") != "Unknown":
                        response += f"  💬 Slack: {team_info['slack_channel']}\n"
            
            return response
        
        return "ℹ️ No blast radius information found."
    
    def _format_exploration_response(self, data: Dict, metadata: Dict) -> str:
        """Format exploration query response."""
        if "nodes" in data:
            nodes = data["nodes"]
            total = data.get("total_count", len(nodes))
            node_type = metadata.get("node_type", "items")
            
            if not nodes:
                return f"📋 No {node_type}s found."
            
            response = f"📋 **Found {total} {node_type}(s):**\n\n"
            
            # Group by type if mixed types
            if node_type == "all":
                by_type = {}
                for node in nodes:
                    ntype = node.get("type", "unknown")
                    if ntype not in by_type:
                        by_type[ntype] = []
                    by_type[ntype].append(node)
                
                for ntype, type_nodes in by_type.items():
                    response += f"**{ntype.title()}s ({len(type_nodes)}):**\n"
                    for node in type_nodes[:5]:  # Limit per type
                        response += f"• {node.get('name', 'Unknown')}\n"
                    if len(type_nodes) > 5:
                        response += f"  ... and {len(type_nodes) - 5} more\n"
                    response += "\n"
            else:
                for i, node in enumerate(nodes[:15], 1):  # Limit to 15 items
                    name = node.get("name", "Unknown")
                    team = node.get("properties", {}).get("team")
                    if team:
                        response += f"{i}. **{name}** (owned by {team})\n"
                    else:
                        response += f"{i}. **{name}**\n"
                
                if len(nodes) > 15:
                    response += f"\n... and {len(nodes) - 15} more {node_type}s"
            
            return response
        
        return "ℹ️ No items found."
    
    def _format_path_response(self, data: Dict) -> str:
        """Format path query response."""
        if "path_details" in data:
            path_details = data["path_details"]
            from_id = data.get("from_id", "Unknown")
            to_id = data.get("to_id", "Unknown")
            path_length = data.get("path_length", 0)
            
            response = f"🛤️ **Path from {from_id} to {to_id}** (length: {path_length})\n\n"
            
            for step in path_details:
                step_num = step.get("step", 0)
                name = step.get("name", "Unknown")
                node_type = step.get("type", "unknown")
                
                if step_num == 0:
                    response += f"🏁 **Start:** {name} ({node_type})\n"
                elif step_num == len(path_details) - 1:
                    response += f"🎯 **End:** {name} ({node_type})\n"
                else:
                    response += f"{step_num}. {name} ({node_type})\n"
                
                # Add edge information
                edge_info = step.get("edge_to_next")
                if edge_info:
                    edge_type = edge_info.get("type", "connected")
                    response += f"   ↓ {edge_type}\n"
            
            return response
        
        return "ℹ️ No path found."
    
    def _format_generic_response(self, data: Dict, intent: IntentType) -> str:
        """Generic response formatter."""
        return f"✅ Query completed successfully!\n\n{json.dumps(data, indent=2)}"


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider for advanced intent parsing."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.name = "openai"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                self.available = True
            except ImportError:
                logger.warning("OpenAI library not installed. Install with: pip install openai")
                self.available = False
        else:
            logger.warning("OpenAI API key not provided")
            self.available = False
    
    def parse_intent(self, query: str, context: ConversationContext) -> ParsedQuery:
        """Parse intent using OpenAI GPT."""
        if not self.available:
            # Fallback to local patterns
            local_provider = LocalPatternProvider()
            return local_provider.parse_intent(query, context)
        
        try:
            system_prompt = self._build_system_prompt(context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return self._parse_llm_response(result, query)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to local patterns
            local_provider = LocalPatternProvider()
            return local_provider.parse_intent(query, context)
    
    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build system prompt for intent recognition."""
        prompt = """You are an expert at parsing natural language queries for an engineering knowledge graph system.

Parse the user's query and respond with JSON in this exact format:
{
  "intent": "ownership|dependency|blast_radius|exploration|path|follow_up|greeting|help|unknown",
  "entities": ["extracted", "entity", "names"],
  "filters": {"node_type": "service|database|team|cache", "team": "team_name"},
  "confidence": 0.9,
  "clarifications": ["any clarification questions if ambiguous"]
}

Intent definitions:
- ownership: "Who owns X?", "What does team Y own?"
- dependency: "What does X depend on?", "What services use Y?"
- blast_radius: "What breaks if X fails?", "Impact of Y going down?"
- exploration: "List all services", "Show me databases"
- path: "How does X connect to Y?", "Path from A to B?"
- follow_up: "What about that?", "Who owns that?" (referring to previous context)
- greeting: "Hi", "Hello"
- help: "Help", "What can you do?"

Extract specific service/database/team names from the query.
"""
        
        if context.last_query and context.last_entities:
            prompt += f"\n\nConversation context:\nLast query: {context.last_query}\nLast entities: {context.last_entities}"
        
        return prompt
    
    def _parse_llm_response(self, response: str, original_query: str) -> ParsedQuery:
        """Parse LLM JSON response into ParsedQuery."""
        try:
            data = json.loads(response)
            
            intent_str = data.get("intent", "unknown")
            try:
                intent = IntentType(intent_str)
            except ValueError:
                intent = IntentType.UNKNOWN
            
            return ParsedQuery(
                intent=intent,
                entities=data.get("entities", []),
                filters=data.get("filters", {}),
                confidence=data.get("confidence", 0.5),
                original_query=original_query,
                clarifications_needed=data.get("clarifications", [])
            )
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {response}")
            return ParsedQuery(
                intent=IntentType.UNKNOWN,
                entities=[],
                filters={},
                confidence=0.1,
                original_query=original_query,
                clarifications_needed=["I had trouble understanding your query. Could you rephrase it?"]
            )
    
    def format_response(self, query_result: Dict, intent: IntentType, original_query: str) -> str:
        """Format response using OpenAI for natural language generation."""
        if not self.available:
            local_provider = LocalPatternProvider()
            return local_provider.format_response(query_result, intent, original_query)
        
        try:
            system_prompt = f"""You are a helpful assistant that explains engineering knowledge graph query results.

Original user query: "{original_query}"
Query intent: {intent.value}
Query result: {json.dumps(query_result, indent=2)}

Provide a clear, conversational response that:
1. Directly answers the user's question
2. Highlights key information with emojis and formatting
3. Is concise but informative
4. Uses technical terms appropriately

If there's an error, explain it helpfully without technical jargon."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Please format this result in a helpful way."}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI formatting error: {e}")
            # Fallback to local formatting
            local_provider = LocalPatternProvider()
            return local_provider.format_response(query_result, intent, original_query)


class NaturalLanguageInterface:
    """
    Main natural language interface that coordinates intent parsing,
    query execution, and response formatting.
    """
    
    def __init__(self, query_engine, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize the natural language interface.
        
        Args:
            query_engine: The graph query engine (AdvancedQueryEngine)
            llm_provider: LLM provider for intent parsing (defaults to LocalPatternProvider)
        """
        self.query_engine = query_engine
        self.llm_provider = llm_provider or LocalPatternProvider()
        self.context = ConversationContext()
        
        logger.info(f"Natural Language Interface initialized with {self.llm_provider.name} provider")
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process a natural language query and return structured results.
        
        Args:
            user_input: User's natural language query
            
        Returns:
            Dictionary containing response, metadata, and execution info
        """
        try:
            # Parse intent
            parsed = self.llm_provider.parse_intent(user_input, self.context)
            
            # Handle low confidence queries
            if parsed.confidence < 0.3 or parsed.clarifications_needed:
                return {
                    "success": False,
                    "response": self._handle_clarification_needed(parsed),
                    "intent": parsed.intent.value,
                    "confidence": parsed.confidence,
                    "needs_clarification": True
                }
            
            # Handle special intents that don't need graph queries
            if parsed.intent == IntentType.GREETING:
                return {
                    "success": True,
                    "response": self._handle_greeting(),
                    "intent": parsed.intent.value,
                    "confidence": parsed.confidence
                }
            elif parsed.intent == IntentType.HELP:
                return {
                    "success": True,
                    "response": self._handle_help(),
                    "intent": parsed.intent.value,
                    "confidence": parsed.confidence
                }
            
            # Execute graph query
            query_result = self._execute_graph_query(parsed)
            
            # Format response
            formatted_response = self.llm_provider.format_response(
                query_result, parsed.intent, user_input
            )
            
            # Update conversation context
            self._update_context(user_input, parsed, query_result)
            
            return {
                "success": query_result.get("success", False),
                "response": formatted_response,
                "intent": parsed.intent.value,
                "entities": parsed.entities,
                "confidence": parsed.confidence,
                "query_result": query_result,
                "execution_time_ms": query_result.get("execution_time_ms", 0)
            }
            
        except Exception as e:
            logger.error(f"Error processing query '{user_input}': {e}")
            return {
                "success": False,
                "response": f"❌ Sorry, I encountered an error processing your query: {str(e)}",
                "intent": "error",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _execute_graph_query(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """Execute the appropriate graph query based on parsed intent."""
        try:
            entities = parsed.entities
            filters = parsed.filters
            
            if parsed.intent == IntentType.OWNERSHIP:
                return self._handle_ownership_query(entities)
                
            elif parsed.intent == IntentType.DEPENDENCY:
                return self._handle_dependency_query(entities, filters)
                
            elif parsed.intent == IntentType.BLAST_RADIUS:
                return self._handle_blast_radius_query(entities)
                
            elif parsed.intent == IntentType.EXPLORATION:
                return self._handle_exploration_query(filters)
                
            elif parsed.intent == IntentType.PATH:
                return self._handle_path_query(entities)
                
            else:
                return {
                    "success": False,
                    "error": f"Query type {parsed.intent.value} not yet implemented",
                    "execution_time_ms": 0
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Graph query execution failed: {str(e)}",
                "execution_time_ms": 0
            }
    
    def _handle_ownership_query(self, entities: List[str]) -> Dict[str, Any]:
        """Handle ownership queries."""
        if not entities:
            return {"success": False, "error": "No entity specified for ownership query"}
        
        entity_name = entities[0]
        
        # Try different node ID patterns
        possible_ids = [
            f"service:{entity_name}",
            f"database:{entity_name}",
            f"cache:{entity_name}",
            entity_name
        ]
        
        for node_id in possible_ids:
            result = self.query_engine.get_owner(node_id)
            if result.success:
                return {
                    "success": True,
                    "data": result.data,
                    "execution_time_ms": result.execution_time_ms
                }
        
        return {
            "success": False,
            "error": f"Entity '{entity_name}' not found or has no ownership information",
            "execution_time_ms": 0
        }
    
    def _handle_dependency_query(self, entities: List[str], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dependency queries."""
        if not entities:
            return {"success": False, "error": "No entity specified for dependency query"}
        
        entity_name = entities[0]
        
        # Try different node ID patterns
        possible_ids = [
            f"service:{entity_name}",
            f"database:{entity_name}",
            f"cache:{entity_name}",
            entity_name
        ]
        
        for node_id in possible_ids:
            result = self.query_engine.downstream(node_id)
            if result.success:
                return {
                    "success": True,
                    "data": result.data,
                    "execution_time_ms": result.execution_time_ms
                }
        
        return {
            "success": False,
            "error": f"Entity '{entity_name}' not found",
            "execution_time_ms": 0
        }
    
    def _handle_blast_radius_query(self, entities: List[str]) -> Dict[str, Any]:
        """Handle blast radius queries."""
        if not entities:
            return {"success": False, "error": "No entity specified for blast radius query"}
        
        entity_name = entities[0]
        
        # Try different node ID patterns
        possible_ids = [
            f"service:{entity_name}",
            f"database:{entity_name}",
            f"cache:{entity_name}",
            entity_name
        ]
        
        for node_id in possible_ids:
            result = self.query_engine.blast_radius(node_id)
            if result.success:
                return {
                    "success": True,
                    "data": result.data,
                    "execution_time_ms": result.execution_time_ms
                }
        
        return {
            "success": False,
            "error": f"Entity '{entity_name}' not found",
            "execution_time_ms": 0
        }
    
    def _handle_exploration_query(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exploration queries."""
        node_type = filters.get("node_type")
        team_filter = filters.get("team")
        
        query_filters = {}
        if team_filter:
            query_filters["team"] = team_filter
        
        result = self.query_engine.get_nodes(
            node_type=node_type,
            filters=query_filters if query_filters else None
        )
        
        return {
            "success": result.success,
            "data": result.data,
            "metadata": result.metadata,
            "execution_time_ms": result.execution_time_ms,
            "error": result.error
        }
    
    def _handle_path_query(self, entities: List[str]) -> Dict[str, Any]:
        """Handle path queries."""
        if len(entities) < 2:
            return {"success": False, "error": "Path queries need two entities (from and to)"}
        
        from_entity, to_entity = entities[0], entities[1]
        
        # Try different combinations of node IDs
        from_ids = [f"service:{from_entity}", f"database:{from_entity}", f"cache:{from_entity}", from_entity]
        to_ids = [f"service:{to_entity}", f"database:{to_entity}", f"cache:{to_entity}", to_entity]
        
        for from_id in from_ids:
            for to_id in to_ids:
                if self.query_engine.storage.get_node(from_id) and self.query_engine.storage.get_node(to_id):
                    result = self.query_engine.path(from_id, to_id)
                    if result.success:
                        return {
                            "success": True,
                            "data": result.data,
                            "execution_time_ms": result.execution_time_ms
                        }
        
        return {
            "success": False,
            "error": f"Could not find path between '{from_entity}' and '{to_entity}'",
            "execution_time_ms": 0
        }
    
    def _handle_clarification_needed(self, parsed: ParsedQuery) -> str:
        """Handle queries that need clarification."""
        if parsed.clarifications_needed:
            return "🤔 " + parsed.clarifications_needed[0]
        
        return """🤔 I'm not sure I understood your query. Here are some examples of what I can help with:

**Ownership queries:**
• "Who owns the payment service?"
• "What does the orders team own?"

**Dependency queries:**  
• "What does order-service depend on?"
• "What services use redis?"

**Blast radius queries:**
• "What breaks if redis-main goes down?"
• "What's the blast radius of users-db?"

**Exploration queries:**
• "List all services"
• "Show me all databases"

**Path queries:**
• "How does api-gateway connect to orders-db?"

Try rephrasing your question using one of these patterns!"""
    
    def _handle_greeting(self) -> str:
        """Handle greeting messages."""
        return """👋 Hello! I'm your Engineering Knowledge Graph assistant.

I can help you understand your infrastructure by answering questions like:
• Who owns what services?
• What depends on what?
• What breaks if something goes down?
• How are services connected?

What would you like to know?"""
    
    def _handle_help(self) -> str:
        """Handle help requests."""
        return """🔍 **Engineering Knowledge Graph Assistant**

I can answer these types of questions:

**🏢 Ownership Questions:**
• "Who owns the payment service?"
• "What does the orders team own?"
• "Who should I page if orders-db is down?"

**🔗 Dependency Questions:**
• "What does order-service depend on?"
• "What services use redis?"
• "What databases does the orders team manage?"

**💥 Blast Radius Questions:**
• "What breaks if redis-main goes down?"
• "What's the blast radius of users-db?"
• "If auth-service fails, what's affected?"

**📋 Exploration Questions:**
• "List all services"
• "Show me all databases"
• "What teams are there?"

**🛤️ Path Questions:**
• "How does api-gateway connect to orders-db?"
• "What's between order-service and notification-service?"

**🔄 Follow-up Questions:**
• "What about payments?" (after discussing services)
• "Who owns that?" (referring to previous result)

Just ask me anything about your infrastructure!"""
    
    def _update_context(self, query: str, parsed: ParsedQuery, result: Dict[str, Any]):
        """Update conversation context for follow-up queries."""
        self.context.last_query = query
        self.context.last_intent = parsed.intent
        self.context.last_entities = parsed.entities
        self.context.last_results = result
    
    def reset_context(self):
        """Reset conversation context."""
        self.context = ConversationContext()
