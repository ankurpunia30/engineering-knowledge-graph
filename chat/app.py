"""
Enhanced chat interface for the Engineering Knowledge Graph with React frontend support.
Includes Part 4 Natural Language Interface functionality.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
import uvicorn
import os
import tempfile
import shutil
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys
from pathlib import Path
import os

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from graph.storage import GraphStorage
from graph.storage_factory import create_optimal_storage
from graph.query import QueryEngine
from connectors import registry
from chat.llm_interface import NaturalLanguageInterface, LocalPatternProvider, OpenAIProvider

# Try to import Neo4j storage
try:
    from graph.neo4j_storage import Neo4jStorage
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: str = "unknown"
    confidence: float = 0.0
    success: bool = True
    execution_time_ms: float = 0.0
    entities: List[str] = []
    related_nodes: List[str] = []


class GraphDataResponse(BaseModel):
    nodes: Dict[str, Any]
    edges: Dict[str, Any]
    statistics: Dict[str, Any]


class FileUploadResponse(BaseModel):
    success: bool
    message: str
    nodes_added: int = 0
    edges_added: int = 0
    file_type: Optional[str] = None
    errors: List[str] = []


class CreateNodeRequest(BaseModel):
    name: str
    node_type: str
    properties: Dict[str, Any] = {}


class UpdateNodeRequest(BaseModel):
    name: Optional[str] = None
    node_type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class NodeResponse(BaseModel):
    success: bool
    message: str
    node: Optional[Dict[str, Any]] = None


class EKGChatAPI:
    """Enhanced FastAPI-based chat interface for the EKG with React support and Part 4 NLI."""
    
    def __init__(self):
        self.app = FastAPI(
            title="Engineering Knowledge Graph Chat with NLI", 
            version="3.0.0",
            description="Natural language interface for infrastructure knowledge with advanced query capabilities"
        )
        
        # Add CORS middleware for React frontend
        # Allow localhost for development and Render URL for production
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://engineering-knowledge-graph-oki5.onrender.com",
            "https://engineering-knowledge-graph.onrender.com",
        ]
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize storage backend
        # Use the storage factory for optimal backend selection
        self.storage = create_optimal_storage()
        
        # Check what storage backend we got
        if hasattr(self.storage, 'driver'):
            backend_type = "Neo4j" if self.storage.driver else "NetworkX (Neo4j fallback)"
        else:
            backend_type = "NetworkX"
            
        print(f"✅ Using {backend_type} storage backend")
        
        self.query_engine = QueryEngine(self.storage)
        
        # Initialize Natural Language Interface
        # This will set self.use_groq flag if Groq is available
        self._init_nlp_provider()
        
        # IMPORTANT: Setup API routes BEFORE frontend catch-all route
        self.setup_routes()
        self.load_data()
        self.serve_frontend()  # This must be last to avoid catching API routes
    
    def _init_nlp_provider(self):
        """Initialize the Natural Language Processing provider."""
        # Priority 1: Try Groq-based LLM query engine (best accuracy)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from graph.llm_query import LLMQueryEngine
                self.llm_query_engine = LLMQueryEngine(self.storage)
                self.use_groq = True
                print("✅ Using Groq LLM for natural language processing (most accurate)")
                # Still initialize NLI for context tracking
                local_provider = LocalPatternProvider()
                self.nli = NaturalLanguageInterface(self.query_engine, local_provider)
                return
            except Exception as e:
                print(f"⚠️ Failed to initialize Groq provider: {e}")
        
        # Priority 2: Try OpenAI if API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                openai_provider = OpenAIProvider(openai_key)
                if openai_provider.available:
                    self.nli = NaturalLanguageInterface(self.query_engine, openai_provider)
                    self.use_groq = False
                    print("✅ Using OpenAI GPT for natural language processing")
                    return
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI provider: {e}")
        
        # Priority 3: Fallback to local pattern-based provider
        local_provider = LocalPatternProvider()
        self.nli = NaturalLanguageInterface(self.query_engine, local_provider)
        self.use_groq = False
        print("✅ Using local pattern matching for natural language processing")
        
        if not groq_key and not openai_key:
            print("💡 Tip: Set GROQ_API_KEY or OPENAI_API_KEY environment variable for better accuracy")
    
    def serve_frontend(self):
        """Setup static file serving for React frontend."""
        frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
        
        if frontend_build_path.exists():
            # Serve React build files
            self.app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
            
            @self.app.get("/", response_class=HTMLResponse)
            async def serve_react_app():
                """Serve the React app at the root URL."""
                return FileResponse(str(frontend_build_path / "index.html"))
                
            # Catch-all route for React Router (must be last!)
            @self.app.get("/{full_path:path}", response_class=HTMLResponse)
            async def catch_all(full_path: str):
                """Catch-all for React Router - serves index.html for client-side routing."""
                # Don't catch API routes
                if full_path.startswith("api/") or full_path == "api":
                    raise HTTPException(status_code=404, detail="API endpoint not found")
                # Serve index.html for all other routes (React Router handles them)
                return FileResponse(str(frontend_build_path / "index.html"))
        else:
            @self.app.get("/", response_class=HTMLResponse)
            async def dev_message():
                return """
                <html>
                <head><title>EKG - Development Mode</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1>Engineering Knowledge Graph</h1>
                    <p>Development mode - React frontend not built yet.</p>
                    <p>Run <code>cd frontend && npm run build</code> to build the frontend.</p>
                    <h2>API Endpoints:</h2>
                    <ul style="text-align: left; max-width: 600px; margin: 0 auto;">
                        <li><strong>POST /api/chat</strong> - Send chat messages</li>
                        <li><strong>GET /api/graph/data</strong> - Get graph data</li>
                        <li><strong>GET /api/graph/stats</strong> - Get graph statistics</li>
                        <li><strong>GET /api/health</strong> - Health check</li>
                    </ul>
                </body>
                </html>
                """
    
    def setup_routes(self):
        """Setup API routes."""
        
        @self.app.post("/api/chat", response_model=ChatResponse)
        async def chat_endpoint(request: ChatRequest):
            """Process chat messages using the best available NLI system."""
            try:
                # Priority: Use Groq-based LLM if available (most accurate)
                if hasattr(self, 'use_groq') and self.use_groq and hasattr(self, 'llm_query_engine'):
                    # Use Groq LLM query engine
                    print(f"\n🔍 Processing query: '{request.message}'")
                    result = self.llm_query_engine.query(request.message)
                    print(f"📊 Result: {result}")
                    
                    # Extract related nodes from Groq response
                    related_nodes = self._extract_related_nodes(result)
                    
                    # Convert Groq response to standard format
                    return ChatResponse(
                        response=self._format_groq_response(result),
                        intent=result.get("type", "unknown"),
                        confidence=result.get("confidence", 0.9),
                        success=not result.get("error"),
                        execution_time_ms=result.get("execution_time_ms", 0.0),
                        entities=result.get("entities", []),
                        related_nodes=related_nodes
                    )
                else:
                    # Fallback to pattern-based NLI
                    result = self.nli.process_query(request.message)
                    related_nodes = self._extract_related_nodes_from_nli(result)
                    
                    return ChatResponse(
                        response=result.get("response", "I couldn't process your request."),
                        intent=result.get("intent", "unknown"),
                        confidence=result.get("confidence", 0.0),
                        success=result.get("success", False),
                        execution_time_ms=result.get("execution_time_ms", 0.0),
                        entities=result.get("entities", []),
                        related_nodes=related_nodes
                    )
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
        
        @self.app.post("/api/chat/legacy", response_model=Dict[str, Any])
        async def chat_legacy_endpoint(request: ChatRequest):
            """Legacy chat endpoint for backward compatibility."""
            try:
                # Use Groq LLM if available
                if hasattr(self, 'use_groq') and self.use_groq and hasattr(self, 'llm_query_engine'):
                    response = self.llm_query_engine.query(request.message)
                else:
                    response = self.query_engine.query(request.message)
                
                # Extract related nodes for graph highlighting
                related_nodes = self._extract_related_nodes(response)
                
                return {
                    "response": response,
                    "related_nodes": related_nodes
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Legacy query processing failed: {str(e)}")
        
        @self.app.post("/api/chat/reset")
        async def reset_conversation():
            """Reset conversation context."""
            try:
                self.nli.reset_context()
                return {"success": True, "message": "Conversation context reset"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Context reset failed: {str(e)}")
        
        @self.app.get("/api/graph/data", response_model=GraphDataResponse)
        async def get_graph_data():
            """Get the complete graph data for visualization."""
            try:
                stats = self.storage.get_stats()
                return GraphDataResponse(
                    nodes={k: v.model_dump() for k, v in self.storage.kg.nodes.items()},
                    edges={k: v.model_dump() for k, v in self.storage.kg.edges.items()},
                    statistics=stats
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get graph data: {str(e)}")
        
        @self.app.get("/api/graph/stats")
        async def get_graph_stats():
            """Get graph statistics."""
            try:
                return self.storage.get_stats()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
        
        # ========================================================================
        # PART 3 QUERY ENGINE API ENDPOINTS
        # ========================================================================
        
        @self.app.get("/api/query/node/{node_id}")
        async def get_node(node_id: str):
            """Get a single node by ID."""
            try:
                result = self.query_engine.get_node(node_id)
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "metadata": result.metadata
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get node: {str(e)}")
        
        @self.app.get("/api/query/nodes")
        async def get_nodes(
            node_type: Optional[str] = None,
            team: Optional[str] = None,
            environment: Optional[str] = None,
            limit: Optional[int] = None
        ):
            """Get nodes by type and filters."""
            try:
                filters = {}
                if team:
                    filters["team"] = team
                if environment:
                    filters["environment"] = environment
                
                result = self.query_engine.get_nodes(
                    node_type=node_type,
                    filters=filters if filters else None,
                    limit=limit
                )
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "metadata": result.metadata
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get nodes: {str(e)}")
        
        @self.app.get("/api/query/downstream/{node_id}")
        async def get_downstream(
            node_id: str,
            max_depth: int = 10,
            edge_types: Optional[str] = None
        ):
            """Get transitive dependencies (what this node depends on)."""
            try:
                edge_type_list = edge_types.split(",") if edge_types else None
                result = self.query_engine.downstream(node_id, max_depth, edge_type_list)
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "metadata": result.metadata
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get downstream: {str(e)}")
        
        @self.app.get("/api/query/upstream/{node_id}")
        async def get_upstream(
            node_id: str,
            max_depth: int = 10,
            edge_types: Optional[str] = None
        ):
            """Get transitive dependents (what depends on this node)."""
            try:
                edge_type_list = edge_types.split(",") if edge_types else None
                result = self.query_engine.upstream(node_id, max_depth, edge_type_list)
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "metadata": result.metadata
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get upstream: {str(e)}")
        
        @self.app.get("/api/query/blast-radius/{node_id}")
        async def get_blast_radius(node_id: str, max_depth: int = 5):
            """Get comprehensive impact analysis."""
            try:
                result = self.query_engine.blast_radius(node_id, max_depth)
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "metadata": result.metadata
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get blast radius: {str(e)}")
        
        @self.app.get("/api/query/path/{from_id}/{to_id}")
        async def get_path(from_id: str, to_id: str, max_depth: int = 10):
            """Find shortest path between two nodes."""
            try:
                result = self.query_engine.path(from_id, to_id, max_depth)
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "metadata": result.metadata
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to find path: {str(e)}")
        
        @self.app.get("/api/query/owner/{node_id}")
        async def get_owner(node_id: str):
            """Get the owning team for a node."""
            try:
                result = self.query_engine.get_owner(node_id)
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "metadata": result.metadata
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get owner: {str(e)}")
        
        @self.app.post("/api/upload", response_model=FileUploadResponse)
        async def upload_configuration_file(
            file: UploadFile = File(...),
            file_type: str = Form(...)
        ):
            """Upload and process a configuration file."""
            try:
                # Validate file type
                supported_types = ['docker-compose', 'kubernetes', 'teams']
                if file_type not in supported_types:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Unsupported file type. Supported types: {supported_types}"
                    )
                
                # Validate file extension
                file_extension = Path(file.filename).suffix.lower()
                expected_extensions = {
                    'docker-compose': ['.yml', '.yaml'],
                    'kubernetes': ['.yml', '.yaml'],
                    'teams': ['.yml', '.yaml', '.json']
                }
                
                if file_extension not in expected_extensions[file_type]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid file extension for {file_type}. Expected: {expected_extensions[file_type]}"
                    )
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                    shutil.copyfileobj(file.file, tmp_file)
                    temp_file_path = tmp_file.name
                
                try:
                    # Process the file based on type
                    nodes_before = len(self.storage.kg.nodes)
                    edges_before = len(self.storage.kg.edges)
                    
                    if file_type == 'docker-compose':
                        from connectors.docker_compose import DockerComposeConnector
                        connector = DockerComposeConnector(temp_file_path)
                        
                    elif file_type == 'kubernetes':
                        from connectors.kubernetes import KubernetesConnector
                        connector = KubernetesConnector(temp_file_path)
                        
                    elif file_type == 'teams':
                        from connectors.teams import TeamsConnector
                        connector = TeamsConnector(temp_file_path)
                    
                    # Parse and get the knowledge graph
                    knowledge_graph = connector.parse()
                    
                    # Update storage with new data using merge_graph
                    self.storage.merge_graph(knowledge_graph)
                    
                    nodes_after = len(self.storage.kg.nodes)
                    edges_after = len(self.storage.kg.edges)
                    
                    return FileUploadResponse(
                        success=True,
                        message=f"Successfully processed {file.filename}",
                        nodes_added=nodes_after - nodes_before,
                        edges_added=edges_after - edges_before,
                        file_type=file_type
                    )
                    
                finally:
                    # Clean up temporary file
                    os.unlink(temp_file_path)
                    
            except HTTPException:
                raise
            except Exception as e:
                return FileUploadResponse(
                    success=False,
                    message=f"Failed to process file: {str(e)}",
                    file_type=file_type,
                    errors=[str(e)]
                )
        
        @self.app.get("/api/supported-formats")
        async def get_supported_formats():
            """Get list of supported file formats and their descriptions."""
            return {
                "formats": {
                    "docker-compose": {
                        "name": "Docker Compose",
                        "description": "Docker Compose YAML files defining services, dependencies, and configurations",
                        "extensions": [".yml", ".yaml"],
                        "example_filename": "docker-compose.yml"
                    },
                    "kubernetes": {
                        "name": "Kubernetes",
                        "description": "Kubernetes YAML files with deployments, services, and configurations",
                        "extensions": [".yml", ".yaml"],
                        "example_filename": "k8s-deployments.yaml"
                    },
                    "teams": {
                        "name": "Teams Configuration",
                        "description": "Team structure and ownership information in YAML or JSON format",
                        "extensions": [".yml", ".yaml", ".json"],
                        "example_filename": "teams.yaml"
                    }
                }
            }
        
        # ========================================================================
        # CRUD OPERATIONS FOR NODES
        # ========================================================================
        
        @self.app.post("/api/nodes", response_model=NodeResponse)
        async def create_node(request: CreateNodeRequest):
            """Create a new node in the graph."""
            try:
                from graph.models import Node, NodeType
                
                # Create the node with proper ID prefix
                node_id = f"{request.node_type}:{request.name}"
                
                # Check if node already exists
                existing_node = self.storage.get_node(node_id)
                if existing_node:
                    return NodeResponse(
                        success=False,
                        message=f"Node with ID '{node_id}' already exists"
                    )
                
                # Create new node
                node = Node(
                    id=node_id,
                    name=request.name,
                    type=NodeType(request.node_type),
                    properties=request.properties
                )
                
                # Add to storage
                self.storage.add_node(node)
                
                return NodeResponse(
                    success=True,
                    message=f"Successfully created node '{node_id}'",
                    node=node.model_dump()
                )
                
            except ValueError as e:
                return NodeResponse(
                    success=False,
                    message=f"Invalid node type. Must be one of: service, database, cache, team. Error: {str(e)}"
                )
            except Exception as e:
                return NodeResponse(
                    success=False,
                    message=f"Failed to create node: {str(e)}"
                )
        
        @self.app.put("/api/nodes/{node_id}", response_model=NodeResponse)
        async def update_node(node_id: str, request: UpdateNodeRequest):
            """Update an existing node."""
            try:
                from graph.models import Node, NodeType
                
                # Get existing node
                existing_node = self.storage.get_node(node_id)
                if not existing_node:
                    return NodeResponse(
                        success=False,
                        message=f"Node '{node_id}' not found"
                    )
                
                # Update fields if provided
                if request.name:
                    existing_node.name = request.name
                if request.node_type:
                    existing_node.type = NodeType(request.node_type)
                if request.properties is not None:
                    # Merge properties instead of replacing
                    existing_node.properties.update(request.properties)
                
                # Update in storage (upsert)
                self.storage.add_node(existing_node)
                
                return NodeResponse(
                    success=True,
                    message=f"Successfully updated node '{node_id}'",
                    node=existing_node.model_dump()
                )
                
            except ValueError as e:
                return NodeResponse(
                    success=False,
                    message=f"Invalid update data: {str(e)}"
                )
            except Exception as e:
                return NodeResponse(
                    success=False,
                    message=f"Failed to update node: {str(e)}"
                )
        
        @self.app.delete("/api/nodes/{node_id}", response_model=NodeResponse)
        async def delete_node(node_id: str):
            """Delete a node and all its edges."""
            try:
                # Get existing node
                existing_node = self.storage.get_node(node_id)
                if not existing_node:
                    return NodeResponse(
                        success=False,
                        message=f"Node '{node_id}' not found"
                    )
                
                # Delete node (this should also delete connected edges)
                if hasattr(self.storage, 'delete_node'):
                    self.storage.delete_node(node_id)
                else:
                    # Fallback for basic storage
                    if node_id in self.storage.kg.nodes:
                        del self.storage.kg.nodes[node_id]
                    
                    # Remove edges connected to this node
                    edges_to_remove = []
                    for edge_id, edge in self.storage.kg.edges.items():
                        if edge.source == node_id or edge.target == node_id:
                            edges_to_remove.append(edge_id)
                    
                    for edge_id in edges_to_remove:
                        del self.storage.kg.edges[edge_id]
                
                return NodeResponse(
                    success=True,
                    message=f"Successfully deleted node '{node_id}' and its connections"
                )
                
            except Exception as e:
                return NodeResponse(
                    success=False,
                    message=f"Failed to delete node: {str(e)}"
                )
        
        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            llm_provider = "none"
            if hasattr(self, 'use_groq') and self.use_groq:
                llm_provider = "groq"
            elif hasattr(self, 'nli') and hasattr(self.nli, 'llm_provider'):
                llm_provider = self.nli.llm_provider.name if hasattr(self.nli.llm_provider, 'name') else "pattern-based"
            
            return {
                "status": "healthy",
                "nodes": len(self.storage.kg.nodes),
                "edges": len(self.storage.kg.edges),
                "llm_provider": llm_provider,
                "storage_backend": self.storage.get_stats().get("storage_backend", "unknown")
            }
        
        # Add root health endpoint for Railway
        @self.app.get("/health")
        async def root_health_check():
            """Root health check endpoint (redirects to /api/health)."""
            return await health_check()
    
    def _extract_related_nodes_from_nli(self, nli_result: Dict[str, Any]) -> List[str]:
        """Extract related node IDs from NLI result for graph highlighting."""
        related_nodes = []
        
        try:
            # Extract entities mentioned in the query
            entities = nli_result.get("entities", [])
            for entity in entities:
                # Try different node ID patterns
                possible_ids = [
                    f"service:{entity}",
                    f"database:{entity}",
                    f"cache:{entity}",
                    f"team:{entity}",
                    entity
                ]
                
                for node_id in possible_ids:
                    if self.storage.get_node(node_id):
                        related_nodes.append(node_id)
                        break
            
            # Extract nodes from query result data
            query_result = nli_result.get("query_result", {})
            if query_result.get("success") and "data" in query_result:
                data = query_result["data"]
                
                # Extract from different result types
                if "dependencies" in data:
                    for dep in data["dependencies"]:
                        if "id" in dep:
                            related_nodes.append(dep["id"])
                
                if "dependents" in data:
                    for dep in data["dependents"]:
                        if "id" in dep:
                            related_nodes.append(dep["id"])
                
                if "all_affected_ids" in data:
                    related_nodes.extend(data["all_affected_ids"])
                
                if "shortest_path" in data:
                    related_nodes.extend(data["shortest_path"])
                
                if "nodes" in data:
                    for node in data["nodes"]:
                        if "id" in node:
                            related_nodes.append(node["id"])
                
                if "node" in data and "id" in data["node"]:
                    related_nodes.append(data["node"]["id"])
        
        except Exception as e:
            print(f"Error extracting related nodes: {e}")
        
        return list(set(related_nodes))  # Remove duplicates
    
    def _extract_related_nodes(self, response: Dict[str, Any]) -> List[str]:
        """Extract node IDs that are relevant to the response for graph highlighting."""
        related_nodes = []
        
        # Extract from different response types
        if response.get("type") == "blast_radius":
            if response.get("affected_services"):
                related_nodes.extend(response["affected_services"])
            # Add the source node
            service_name = response.get("service_analyzed")
            if service_name:
                possible_ids = [f"service:{service_name}", f"database:{service_name}", f"cache:{service_name}"]
                for node_id in possible_ids:
                    if self.storage.get_node(node_id):
                        related_nodes.append(node_id)
                        break
        
        elif response.get("type") == "ownership":
            service_name = response.get("service")
            team_name = response.get("team")
            if service_name:
                possible_ids = [f"service:{service_name}", f"database:{service_name}", f"cache:{service_name}"]
                for node_id in possible_ids:
                    if self.storage.get_node(node_id):
                        related_nodes.append(node_id)
                        break
            if team_name:
                related_nodes.append(f"team:{team_name}")
        
        elif response.get("type") == "connection":
            service_name = response.get("service")
            if service_name:
                possible_ids = [f"service:{service_name}", f"database:{service_name}", f"cache:{service_name}"]
                for node_id in possible_ids:
                    if self.storage.get_node(node_id):
                        related_nodes.append(node_id)
                        break
        
        return list(set(related_nodes))  # Remove duplicates
    
    def load_data(self):
        """Load data from configuration files."""
        data_dir = Path(__file__).parent.parent / "data"
        
        connectors_config = [
            ('docker-compose', 'docker-compose.yml'),
            ('teams', 'teams.yaml'),
            ('kubernetes', 'k8s-deployments.yaml')
        ]
        
        total_nodes = 0
        total_edges = 0
        
        for connector_name, filename in connectors_config:
            file_path = data_dir / filename
            if file_path.exists():
                try:
                    connector = registry.create_connector(connector_name, str(file_path))
                    kg = connector.parse()
                    
                    print(f"Loaded {len(kg.nodes)} nodes and {len(kg.edges)} edges from {filename}")
                    total_nodes += len(kg.nodes)
                    total_edges += len(kg.edges)
                    
                    self.storage.merge_graph(kg)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"Configuration file not found: {file_path}")
        
        print(f"Total loaded: {total_nodes} nodes, {total_edges} edges")
        print(f"Final graph: {len(self.storage.kg.nodes)} nodes, {len(self.storage.kg.edges)} edges")
    
    def _format_groq_response(self, result: Dict[str, Any]) -> str:
        """Format Groq query result into natural language response."""
        if result.get("error"):
            return f"❌ {result['error']}"
        
        query_type = result.get("type", "unknown")
        
        # Format based on query type
        if query_type == "blast_radius":
            return self._format_blast_radius_response(result)
        elif query_type == "ownership":
            return self._format_ownership_response(result)
        elif query_type == "connection":
            return self._format_connection_response(result)
        elif query_type == "team_info":
            return self._format_team_info_response(result)
        elif query_type == "service_info":
            return self._format_service_info_response(result)
        elif query_type == "database_info":
            return self._format_database_info_response(result)
        else:
            # Generic response formatting
            if isinstance(result.get("answer"), str):
                return result["answer"]
            return json.dumps(result, indent=2)
    
    def _format_blast_radius_response(self, result: Dict[str, Any]) -> str:
        """Format blast radius response."""
        service = result.get("service_analyzed", "Unknown")
        affected = result.get("affected_services", [])
        total = result.get("affected_services_count", len(affected))
        teams = result.get("team_details", {})
        
        response = f"🔍 Blast Radius Analysis for {service}\n\n"
        response += f"Total Impact: {total} services affected\n"
        response += f"Upstream: {result.get('upstream_affected', 0)} services depend on this\n"
        response += f"Downstream: {result.get('downstream_affected', 0)} dependencies\n\n"
        
        if teams:
            response += "👥 Teams Affected:\n"
            for team_name, team_info in teams.items():
                services = team_info.get("services", [])
                count = team_info.get("count", len(services))
                response += f"• {team_name}: {count} services\n"
                
                # List the actual services
                if services:
                    for svc in services[:5]:  # Show first 5 services
                        response += f"  - {svc}\n"
                    if len(services) > 5:
                        response += f"  - ... and {len(services) - 5} more\n"
                
                if team_info.get("lead"):
                    response += f"  👤 Lead: {team_info['lead']}\n"
                if team_info.get("slack"):
                    response += f"  💬 Slack: {team_info['slack']}\n"
                response += "\n"
        
        # Add severity if available
        severity = result.get("severity")
        if severity:
            emoji = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
            response += f"\n{emoji} Severity: {severity}\n"
        
        return response
    
    def _format_ownership_response(self, result: Dict[str, Any]) -> str:
        """Format ownership response."""
        service = result.get("service", "Unknown")
        team = result.get("team", "Unknown")
        
        response = f"👥 **Ownership Information for {service}**\n\n"
        response += f"**Team:** {team}\n"
        
        if result.get("lead"):
            response += f"**Lead:** {result['lead']}\n"
        if result.get("slack_channel"):
            response += f"**Slack:** {result['slack_channel']}\n"
        if result.get("pagerduty_schedule"):
            response += f"**PagerDuty:** {result['pagerduty_schedule']}\n"
        
        return response
    
    def _format_connection_response(self, result: Dict[str, Any]) -> str:
        """Format connection/dependency response."""
        service = result.get("service", "Unknown")
        dependencies = result.get("dependencies", [])
        dependents = result.get("dependents", [])
        
        response = f"🔗 **Dependencies for {service}**\n\n"
        
        if dependencies:
            response += "**Dependencies (what this uses):**\n"
            for dep in dependencies[:10]:  # Limit to 10
                response += f"• {dep}\n"
        
        if dependents:
            response += f"\n**Dependents (what uses this):**\n"
            for dep in dependents[:10]:  # Limit to 10
                response += f"• {dep}\n"
        
        return response
    
    def _format_team_info_response(self, result: Dict[str, Any]) -> str:
        """Format team information response."""
        # Handle "show all teams" query
        if "teams" in result:
            teams = result.get("teams", [])
            response = f"👥 **All Teams ({result.get('total_teams', len(teams))}):**\n\n"
            
            for team in teams:
                response += f"**{team.get('name')}**\n"
                if team.get('lead'):
                    response += f"  👤 Lead: {team['lead']}\n"
                if team.get('slack'):
                    response += f"  💬 Slack: {team['slack']}\n"
                response += f"  🔧 Services: {team.get('services_count', 0)}\n\n"
            
            return response
        
        # Handle specific team query
        team = result.get("team", "Unknown")
        owned_services = result.get("owned_services", [])
        
        response = f"👥 **Team: {team}**\n\n"
        
        if result.get("lead"):
            response += f"**Lead:** {result['lead']}\n"
        if result.get("slack_channel"):
            response += f"**Slack:** {result['slack_channel']}\n"
        if result.get("pagerduty"):
            response += f"**PagerDuty:** {result['pagerduty']}\n"
        
        if owned_services:
            response += f"\n**Services Owned ({len(owned_services)}):**\n"
            service_breakdown = result.get("service_breakdown", {})
            if service_breakdown:
                for stype, count in service_breakdown.items():
                    response += f"  • {stype}: {count}\n"
                response += "\n**Service List:**\n"
            
            for svc in owned_services:
                svc_name = svc.get('name') if isinstance(svc, dict) else svc
                svc_type = svc.get('type', '') if isinstance(svc, dict) else ''
                response += f"• {svc_name}"
                if svc_type:
                    response += f" ({svc_type})"
                response += "\n"
        
        return response
    
    def _format_service_info_response(self, result: Dict[str, Any]) -> str:
        """Format service information response."""
        # Handle "show all services" query
        if "services" in result:
            services = result.get("services", [])
            response = f"🔧 **All Services ({result.get('total_services', len(services))}):**\n\n"
            
            # Group by team
            teams = {}
            for svc in services:
                team = svc.get('team', 'Unknown')
                if team not in teams:
                    teams[team] = []
                teams[team].append(svc)
            
            for team, team_services in sorted(teams.items()):
                response += f"**{team}:**\n"
                for svc in team_services:
                    response += f"  • {svc.get('name')}"
                    if svc.get('port'):
                        response += f" (port {svc['port']})"
                    response += "\n"
                response += "\n"
            
            return response
        
        # Handle specific service query
        service = result.get("service", "Unknown")
        
        response = f"🔧 **Service: {service}**\n\n"
        
        if result.get("type"):
            response += f"**Type:** {result['type']}\n"
        if result.get("team"):
            response += f"**Team:** {result['team']}\n"
        if result.get("oncall"):
            response += f"**On-Call:** {result['oncall']}\n"
        if result.get("port"):
            response += f"**Port:** {result['port']}\n"
        if result.get("dependencies_count") is not None:
            response += f"**Dependencies:** {result['dependencies_count']}\n"
        if result.get("dependents_count") is not None:
            response += f"**Dependents:** {result['dependents_count']}\n"
        
        return response
    
    def _format_database_info_response(self, result: Dict[str, Any]) -> str:
        """Format database information response."""
        # Handle "show all databases" query
        if "databases" in result:
            databases = result.get("databases", [])
            response = f"💾 **All Databases ({result.get('total_databases', len(databases))}):**\n\n"
            
            for db in databases:
                response += f"**{db.get('name')}**\n"
                if db.get('team'):
                    response += f"  👥 Team: {db['team']}\n"
                if db.get('image'):
                    response += f"  🐳 Image: {db['image']}\n"
                if db.get('encrypted'):
                    response += f"  🔒 Encrypted: Yes\n"
                
                connected = db.get('connected_services', [])
                if connected:
                    response += f"  🔗 Connected Services ({len(connected)}):\n"
                    for svc in connected[:5]:  # Limit to 5
                        svc_name = svc.get('name') if isinstance(svc, dict) else svc
                        rel = svc.get('relationship', '') if isinstance(svc, dict) else ''
                        response += f"    • {svc_name}"
                        if rel:
                            response += f" ({rel})"
                        response += "\n"
                    if len(connected) > 5:
                        response += f"    ... and {len(connected) - 5} more\n"
                response += "\n"
            
            return response
        
        # Handle specific database query
        database = result.get("database", "Unknown")
        
        response = f"💾 **Database: {database}**\n\n"
        
        if result.get("team"):
            response += f"**Team:** {result['team']}\n"
        if result.get("connected_services"):
            services = result["connected_services"]
            response += f"\n**Connected Services ({len(services)}):**\n"
            for svc in services:
                svc_name = svc.get('name') if isinstance(svc, dict) else svc
                response += f"• {svc_name}\n"
        
        return response
    
def create_app():
    """Factory function to create the FastAPI app."""
    api = EKGChatAPI()
    return api.app


# Create app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import os
    api = EKGChatAPI()
    port = int(os.getenv('PORT', 8001))  # Use port 8001 by default
    print("🚀 Engineering Knowledge Graph starting...")
    print(f"📊 Graph loaded: {len(api.storage.kg.nodes)} nodes, {len(api.storage.kg.edges)} edges")
    print(f"🌐 Server starting at http://localhost:{port}")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    uvicorn.run(
        api.app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
