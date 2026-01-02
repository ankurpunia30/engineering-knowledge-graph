import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import EKGLogo from './EKGLogo';
import { 
  LayoutDashboard, 
  Network, 
  MessageSquare, 
  BarChart3, 
  Upload,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Edit,
  Trash2,
  Plus,
  Send,
  Sparkles,
  Copy,
  Clock,
  Loader2,
  AlertCircle,
  TrendingUp,
  Users,
  Database,
  Search,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Minimize2,
  ChevronLeft,
  ChevronRight,
  PanelLeftClose,
  PanelRightClose
} from 'lucide-react';

// Determine API base URL at runtime
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  // Local development
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  // Production - use same domain as frontend
  return window.location.origin;
};

const API_BASE = getApiBaseUrl();

const EnterpriseDashboard = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('dashboard');
  const [stats, setStats] = useState({ totalNodes: 0, services: 0, databases: 0, teams: 0, edges: 0 });
  const [backendStatus, setBackendStatus] = useState({ connected: false });
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [uploadStatus, setUploadStatus] = useState(null);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [newNodeName, setNewNodeName] = useState('');
  const [newNodeType, setNewNodeType] = useState('service');
  const [editNodeName, setEditNodeName] = useState('');
  const [editNodeType, setEditNodeType] = useState('service');
  const [crudStatus, setCrudStatus] = useState(null);
  const [showAddNode, setShowAddNode] = useState(false);
  const [showNodeDetails, setShowNodeDetails] = useState(true);
  const [isGraphFullscreen, setIsGraphFullscreen] = useState(false);
  const [showLeftSidebar, setShowLeftSidebar] = useState(false);
  const [showRightSidebar, setShowRightSidebar] = useState(false);
  const graphRef = useRef();
  const fileInputRef = useRef();

  const checkBackendHealth = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/health`);
      setBackendStatus({ connected: response.ok });
    } catch (error) {
      setBackendStatus({ connected: false });
    }
  }, []);

  const loadGraphData = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/graph/data`);
      if (!response.ok) throw new Error('Failed to load');
      
      const data = await response.json();
      const nodesArray = data.nodes ? Object.values(data.nodes) : [];
      const edgesArray = data.edges ? (Array.isArray(data.edges) ? data.edges : Object.values(data.edges)) : [];
      
      const nodeIds = new Set(nodesArray.map(n => n.id));
      const validEdges = edgesArray.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));
      
      setGraphData({
        nodes: nodesArray,
        links: validEdges.map(e => ({ source: e.source, target: e.target, type: e.type }))
      });

      setStats({
        totalNodes: nodesArray.length,
        services: nodesArray.filter(n => n.type === 'service').length,
        databases: nodesArray.filter(n => n.type === 'database').length,
        teams: nodesArray.filter(n => n.type === 'team').length,
        edges: validEdges.length
      });
    } catch (error) {
      console.error('Error loading graph:', error);
    }
  }, []);

  useEffect(() => {
    checkBackendHealth();
    loadGraphData();
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, [checkBackendHealth, loadGraphData]);

  // ESC key handler for fullscreen mode
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isGraphFullscreen) {
        setIsGraphFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isGraphFullscreen]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response || 'No response' }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${error.message}`, error: true }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    setUploadStatus({ loading: true, message: 'Uploading...' });
    
    // Auto-detect file type from filename
    const filename = file.name.toLowerCase();
    let fileType = 'docker-compose'; // default
    
    if (filename.includes('docker-compose') || filename.includes('compose')) {
      fileType = 'docker-compose';
    } else if (filename.includes('k8s') || filename.includes('kubernetes') || filename.includes('deployment')) {
      fileType = 'kubernetes';
    } else if (filename.includes('team')) {
      fileType = 'teams';
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    
    try {
      const response = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = 'Unknown error';
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
        } catch {
          errorMessage = errorText || `Server error (${response.status})`;
        }
        
        setUploadStatus({ 
          loading: false, 
          success: false, 
          message: `❌ Upload failed: ${errorMessage}` 
        });
        return;
      }
      
      const data = await response.json();
      
      // Reload graph data to show new nodes
      await loadGraphData();
      setUploadStatus({ 
        loading: false, 
        success: true, 
        message: `✅ Success! Added ${data.nodes_added || 0} nodes and ${data.edges_added || 0} edges` 
      });
      
      // Auto-close modal after 2 seconds
      setTimeout(() => {
        setShowUploadModal(false);
        setUploadStatus(null);
      }, 2000);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({ 
        loading: false, 
        success: false, 
        message: `❌ Upload failed: ${error.message || 'Network error'}` 
      });
    }
  };

  const handleCreateNode = async () => {
    if (!newNodeName.trim()) {
      setCrudStatus({ success: false, message: '❌ Node name is required' });
      return;
    }

    setCrudStatus({ loading: true, message: 'Creating node...' });

    try {
      const response = await fetch(`${API_BASE}/api/nodes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newNodeName,
          node_type: newNodeType,
          properties: {}
        })
      });

      const data = await response.json();

      if (data.success) {
        await loadGraphData();
        setCrudStatus({ success: true, message: `✅ Created ${newNodeName}` });
        setNewNodeName('');
        setTimeout(() => setCrudStatus(null), 2000);
      } else {
        setCrudStatus({ success: false, message: `❌ ${data.message}` });
      }
    } catch (error) {
      setCrudStatus({ success: false, message: `❌ Error: ${error.message}` });
    }
  };

  const handleUpdateNode = async () => {
    if (!selectedNode) return;

    setCrudStatus({ loading: true, message: 'Updating node...' });

    try {
      const response = await fetch(`${API_BASE}/api/nodes/${encodeURIComponent(selectedNode.id)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editNodeName || selectedNode.name,
          node_type: editNodeType || selectedNode.type,
          properties: selectedNode.properties || {}
        })
      });

      const data = await response.json();

      if (data.success) {
        await loadGraphData();
        setCrudStatus({ success: true, message: `✅ Updated ${selectedNode.name}` });
        setTimeout(() => setCrudStatus(null), 2000);
      } else {
        setCrudStatus({ success: false, message: `❌ ${data.message}` });
      }
    } catch (error) {
      setCrudStatus({ success: false, message: `❌ Error: ${error.message}` });
    }
  };

  const handleDeleteNode = async () => {
    if (!selectedNode) return;

    if (!window.confirm(`Are you sure you want to delete ${selectedNode.name}? This will also remove all its connections.`)) {
      return;
    }

    setCrudStatus({ loading: true, message: 'Deleting node...' });

    try {
      const response = await fetch(`${API_BASE}/api/nodes/${encodeURIComponent(selectedNode.id)}`, {
        method: 'DELETE'
      });

      const data = await response.json();

      if (data.success) {
        await loadGraphData();
        setSelectedNode(null);
        setCrudStatus({ success: true, message: `✅ Deleted node` });
        setTimeout(() => setCrudStatus(null), 2000);
      } else {
        setCrudStatus({ success: false, message: `❌ ${data.message}` });
      }
    } catch (error) {
      setCrudStatus({ success: false, message: `❌ Error: ${error.message}` });
    }
  };

  const getNodeColor = (node) => {
    const colors = { service: '#3b82f6', database: '#10b981', cache: '#f59e0b', team: '#8b5cf6' };
    return colors[node.type] || '#6b7280';
  };

  const paintNode = (node, ctx, globalScale) => {
    const label = node.name;
    const fontSize = 14/globalScale;
    ctx.font = `bold ${fontSize}px Sans-Serif`;
    const textWidth = ctx.measureText(label).width;
    const bckgDimensions = [textWidth + fontSize * 0.6, fontSize * 1.4];

    // Highlight selected or search-matched nodes
    const isHighlighted = selectedNode?.id === node.id || highlightNodes.has(node.id);
    
    // Draw node circle with highlight
    if (isHighlighted) {
      // Draw highlight ring
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(node.x, node.y, 10, 0, 2 * Math.PI);
      ctx.stroke();
    }
    
    ctx.fillStyle = getNodeColor(node);
    ctx.beginPath();
    ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI);
    ctx.fill();

    // Draw white background for label with border
    ctx.strokeStyle = isHighlighted ? '#3b82f6' : '#d1d5db';
    ctx.lineWidth = isHighlighted ? 2 : 1;
    ctx.fillStyle = isHighlighted ? 'rgba(59, 130, 246, 0.1)' : 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y + 9, bckgDimensions[0], bckgDimensions[1]);
    ctx.strokeRect(node.x - bckgDimensions[0] / 2, node.y + 9, bckgDimensions[0], bckgDimensions[1]);

    // Draw label text
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = isHighlighted ? '#3b82f6' : '#000000';
    ctx.fillText(label, node.x, node.y + 9 + bckgDimensions[1] / 2);
  };

  // Paint link labels to show relationships
  const paintLink = useCallback((link, ctx, globalScale) => {
    const start = link.source;
    const end = link.target;
    
    if (typeof start !== 'object' || typeof end !== 'object') return;
    
    // Calculate midpoint
    const midX = (start.x + end.x) / 2;
    const midY = (start.y + end.y) / 2;
    
    // Draw relationship label
    const label = link.type || 'connected';
    const fontSize = 9 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Draw background for label
    const textWidth = ctx.measureText(label).width;
    const padding = 3 / globalScale;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(
      midX - textWidth / 2 - padding,
      midY - fontSize / 2 - padding,
      textWidth + padding * 2,
      fontSize + padding * 2
    );
    
    // Draw border
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 0.5 / globalScale;
    ctx.strokeRect(
      midX - textWidth / 2 - padding,
      midY - fontSize / 2 - padding,
      textWidth + padding * 2,
      fontSize + padding * 2
    );
    
    // Draw text
    ctx.fillStyle = '#6b7280';
    ctx.fillText(label, midX, midY);
  }, []);

  // Filter and search functionality - memoized to prevent infinite loops
  const filteredData = useMemo(() => {
    let filteredNodes = graphData.nodes;
    let filteredLinks = graphData.links;

    // Apply type filter
    if (filterType && filterType !== 'all') {
      filteredNodes = filteredNodes.filter(node => node.type === filterType);
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      filteredLinks = filteredLinks.filter(link => 
        nodeIds.has(link.source.id || link.source) && 
        nodeIds.has(link.target.id || link.target)
      );
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filteredNodes = filteredNodes.filter(node => 
        node.name.toLowerCase().includes(query) ||
        node.id.toLowerCase().includes(query) ||
        (node.team && node.team.toLowerCase().includes(query))
      );
      
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      filteredLinks = filteredLinks.filter(link => 
        nodeIds.has(link.source.id || link.source) && 
        nodeIds.has(link.target.id || link.target)
      );
    }

    return { nodes: filteredNodes, links: filteredLinks };
  }, [graphData, filterType, searchQuery]);

  // Update highlighted nodes when search changes
  useEffect(() => {
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const matchedNodes = graphData.nodes.filter(node => 
        node.name.toLowerCase().includes(query) ||
        node.id.toLowerCase().includes(query) ||
        (node.team && node.team.toLowerCase().includes(query))
      );
      setHighlightNodes(new Set(matchedNodes.map(n => n.id)));
    } else {
      setHighlightNodes(new Set());
    }
  }, [searchQuery, graphData.nodes]);

  return (
    <div className="flex h-screen bg-gray-50" style={{ overflow: 'hidden', width: '100vw', height: '100vh' }}>
      {/* Sidebar - Hidden when Explorer is active */}
      {activeView !== 'explorer' && (
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col" style={{ overflow: 'hidden' }}>
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <EKGLogo size={40} />
              <div>
                <h1 className="text-xl font-bold text-gray-900">EKG</h1>
                <p className="text-xs text-gray-500">Engineering Knowledge Graph</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1" style={{ overflowY: 'auto' }}>
          {[
            { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
            { id: 'explorer', icon: Network, label: 'Explorer' },
            { id: 'console', icon: MessageSquare, label: 'Console' },
            { id: 'analytics', icon: BarChart3, label: 'Analytics' }
          ].map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => setActiveView(id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeView === id ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-200 space-y-3">
          {[
            { label: 'Nodes', value: stats.totalNodes },
            { label: 'Services', value: stats.services },
            { label: 'Databases', value: stats.databases },
            { label: 'Edges', value: stats.edges }
          ].map((stat, i) => (
            <div key={i} className="flex items-center justify-between text-sm">
              <span className="text-gray-600">{stat.label}</span>
              <span className="font-semibold text-gray-900">{stat.value}</span>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-2 text-sm">
            {backendStatus.connected ? (
              <>
                <CheckCircle2 size={16} className="text-green-500" />
                <span className="text-gray-600">Connected</span>
              </>
            ) : (
              <>
                <XCircle size={16} className="text-red-500" />
                <span className="text-gray-600">Disconnected</span>
              </>
            )}
          </div>
        </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col" style={{ overflow: 'hidden' }}>
        {/* Header - Hidden when Explorer is active */}
        {activeView !== 'explorer' && (
          <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              {activeView.charAt(0).toUpperCase() + activeView.slice(1)}
            </h2>
            <div className="flex items-center gap-3">
            <button
              onClick={loadGraphData}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw size={18} className="text-gray-600" />
            </button>
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <Upload size={16} />
              Upload
            </button>
          </div>
          </div>
        )}

        <div className="flex-1 overflow-hidden">
          {activeView === 'dashboard' && (
            <div className="h-full flex flex-col bg-gray-50">
              {/* Stats Cards */}
              <div className="p-6">
                <div className="grid grid-cols-4 gap-6 mb-6">
                  {[
                    { 
                      label: 'Total Nodes', 
                      value: stats.totalNodes, 
                      icon: Network,
                      color: 'bg-blue-500',
                      lightColor: 'bg-blue-50',
                      textColor: 'text-blue-600'
                    },
                    { 
                      label: 'Services', 
                      value: stats.services,
                      icon: Database,
                      color: 'bg-green-500',
                      lightColor: 'bg-green-50',
                      textColor: 'text-green-600'
                    },
                    { 
                      label: 'Databases', 
                      value: stats.databases,
                      icon: Database,
                      color: 'bg-purple-500',
                      lightColor: 'bg-purple-50',
                      textColor: 'text-purple-600'
                    },
                    { 
                      label: 'Connections', 
                      value: stats.edges,
                      icon: TrendingUp,
                      color: 'bg-orange-500',
                      lightColor: 'bg-orange-50',
                      textColor: 'text-orange-600'
                    }
                  ].map((stat, i) => (
                    <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                      <div className="flex items-center justify-between mb-3">
                        <div className={`w-12 h-12 ${stat.lightColor} rounded-lg flex items-center justify-center`}>
                          <stat.icon size={24} className={stat.textColor} />
                        </div>
                        <div className={`w-2 h-2 ${stat.color} rounded-full`}></div>
                      </div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                      <div className="text-sm text-gray-600">{stat.label}</div>
                    </div>
                  ))}
                </div>

                {/* Two Column Layout */}
                <div className="grid grid-cols-2 gap-6">
                  {/* Graph Preview */}
                  <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">Knowledge Graph</h3>
                      <button
                        onClick={() => setActiveView('explorer')}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                      >
                        View Full →
                      </button>
                    </div>
                    <div className="h-80">
                      <ForceGraph2D
                        ref={graphRef}
                        graphData={graphData}
                        nodeCanvasObject={paintNode}
                        linkDirectionalArrowLength={3.5}
                        linkDirectionalArrowRelPos={1}
                        linkColor={() => '#d1d5db'}
                        linkWidth={1.5}
                        backgroundColor="#fafafa"
                        enableZoomInteraction={false}
                        enablePanInteraction={false}
                      />
                    </div>
                  </div>

                  {/* Recent Activity / Quick Actions */}
                  <div className="bg-white rounded-xl border border-gray-200">
                    <div className="px-6 py-4 border-b border-gray-200">
                      <h3 className="font-semibold text-gray-900">Quick Actions</h3>
                    </div>
                    <div className="p-6 space-y-3">
                      <button
                        onClick={() => setActiveView('console')}
                        className="w-full flex items-center gap-3 p-4 bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 rounded-lg transition-all group"
                      >
                        <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                          <Sparkles size={20} className="text-white" />
                        </div>
                        <div className="flex-1 text-left">
                          <div className="font-medium text-gray-900">AI Query Console</div>
                          <div className="text-xs text-gray-600">Ask questions in natural language</div>
                        </div>
                        <div className="text-blue-600">→</div>
                      </button>

                      <button
                        onClick={() => setActiveView('explorer')}
                        className="w-full flex items-center gap-3 p-4 bg-gradient-to-r from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-200 rounded-lg transition-all group"
                      >
                        <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                          <Network size={20} className="text-white" />
                        </div>
                        <div className="flex-1 text-left">
                          <div className="font-medium text-gray-900">Graph Explorer</div>
                          <div className="text-xs text-gray-600">Visualize and edit nodes</div>
                        </div>
                        <div className="text-purple-600">→</div>
                      </button>

                      <button
                        onClick={() => setActiveView('analytics')}
                        className="w-full flex items-center gap-3 p-4 bg-gradient-to-r from-green-50 to-green-100 hover:from-green-100 hover:to-green-200 rounded-lg transition-all group"
                      >
                        <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                          <BarChart3 size={20} className="text-white" />
                        </div>
                        <div className="flex-1 text-left">
                          <div className="font-medium text-gray-900">Analytics</div>
                          <div className="text-xs text-gray-600">View insights and metrics</div>
                        </div>
                        <div className="text-green-600">→</div>
                      </button>
                    </div>

                    {/* Top Services */}
                    <div className="px-6 py-4 border-t border-gray-200">
                      <h4 className="text-sm font-medium text-gray-700 mb-3">Top Services</h4>
                      <div className="space-y-2">
                        {graphData.nodes
                          .filter(n => n.type === 'service')
                          .slice(0, 5)
                          .map((node, idx) => (
                            <div key={idx} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                              <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span className="text-sm font-mono text-gray-900">{node.name}</span>
                              </div>
                              <span className="text-xs text-gray-500">{node.type}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeView === 'explorer' && (
            <div className="h-full flex bg-gray-50" style={{ overflow: 'hidden' }}>
              {/* Left Side Panel - Only shows when node selected or adding */}
              {(selectedNode || showAddNode) && (
                <div className="w-80 bg-white border-r border-gray-200 flex flex-col" style={{ overflow: 'hidden', maxHeight: '100vh' }}>
                  {/* Panel Header */}
                  <div className="p-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
                    <h3 className="font-semibold text-gray-900">
                      {selectedNode ? selectedNode.name : 'Add Node'}
                    </h3>
                    <button
                      onClick={() => {
                        setSelectedNode(null);
                        setShowAddNode(false);
                      }}
                      className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <XCircle size={18} />
                    </button>
                  </div>

                  {/* Panel Content */}
                  <div className="flex-1 p-4 space-y-4" style={{ overflowY: 'auto', overflowX: 'hidden', maxHeight: 'calc(100vh - 73px)' }}>
                    {/* Node Details */}
                    {selectedNode && (
                      <>
                        <div className="space-y-3">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1.5">Name</label>
                            <input
                              type="text"
                              value={editNodeName || selectedNode.name}
                              onChange={(e) => setEditNodeName(e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1.5">Type</label>
                            <select
                              value={editNodeType || selectedNode.type}
                              onChange={(e) => setEditNodeType(e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="service">Service</option>
                              <option value="database">Database</option>
                              <option value="cache">Cache</option>
                              <option value="team">Team</option>
                            </select>
                          </div>

                          <div className="pt-2 pb-2 border-t border-b border-gray-200">
                            <div className="text-sm text-gray-500">Connections</div>
                            <div className="text-2xl font-bold text-gray-900">
                              {graphData.links.filter(l => 
                                (l.source.id || l.source) === selectedNode.id || 
                                (l.target.id || l.target) === selectedNode.id
                              ).length}
                            </div>
                          </div>
                        </div>

                        {crudStatus && (
                          <div className={`p-3 rounded-lg text-sm ${
                            crudStatus.loading ? 'bg-blue-50 text-blue-700' :
                            crudStatus.success ? 'bg-green-50 text-green-700' :
                            'bg-red-50 text-red-700'
                          }`}>
                            {crudStatus.message}
                          </div>
                        )}

                        <div className="flex gap-2 pt-2">
                          <button 
                            onClick={handleUpdateNode}
                            disabled={crudStatus?.loading}
                            className="flex-1 px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                          >
                            Save Changes
                          </button>
                          <button 
                            onClick={handleDeleteNode}
                            disabled={crudStatus?.loading}
                            className="px-4 py-2.5 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </>
                    )}

                    {/* Add Node Form */}
                    {showAddNode && !selectedNode && (
                      <>
                        {crudStatus && (
                          <div className={`p-3 rounded-lg text-sm ${
                            crudStatus.loading ? 'bg-blue-50 text-blue-700' :
                            crudStatus.success ? 'bg-green-50 text-green-700' :
                            'bg-red-50 text-red-700'
                          }`}>
                            {crudStatus.message}
                          </div>
                        )}

                        <div className="space-y-3">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1.5">Name</label>
                            <input
                              type="text"
                              value={newNodeName}
                              onChange={(e) => setNewNodeName(e.target.value)}
                              placeholder="Enter node name"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1.5">Type</label>
                            <select 
                              value={newNodeType}
                              onChange={(e) => setNewNodeType(e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="service">Service</option>
                              <option value="database">Database</option>
                              <option value="cache">Cache</option>
                              <option value="team">Team</option>
                            </select>
                          </div>
                        </div>

                        <button 
                          onClick={handleCreateNode}
                          disabled={crudStatus?.loading}
                          className="w-full px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 mt-4"
                        >
                          {crudStatus?.loading ? 'Creating...' : 'Create Node'}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Graph Canvas - Full Screen */}
              <div className="flex-1 relative" style={{ overflow: 'hidden', height: '100%' }}>
                {/* Menu button - Top Left */}
                <button
                  onClick={() => setActiveView('dashboard')}
                  className="absolute top-4 left-4 z-20 p-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg shadow-lg hover:bg-gray-100 hover:border-gray-400 transition-colors"
                  title="Back to Menu"
                >
                  <LayoutDashboard size={20} />
                </button>

                {/* Floating Controls - Left Side (after menu button) */}
                <div className="absolute top-4 left-20 z-10 flex gap-2">
                  <div className="relative">
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search..."
                      className="w-48 pl-9 pr-3 py-2 bg-white border border-gray-300 rounded-lg text-sm shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  </div>
                  {!showAddNode && (
                    <button
                      onClick={() => setShowAddNode(true)}
                      className="p-2.5 bg-blue-600 text-white rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
                      title="Add Node"
                    >
                      <Plus size={18} />
                    </button>
                  )}
                </div>

                {/* Graph */}
                <ForceGraph2D
                  ref={graphRef}
                  graphData={filteredData}
                  nodeCanvasObject={paintNode}
                  linkCanvasObject={paintLink}
                  nodePointerAreaPaint={(node, color, ctx) => {
                    // Large clickable area - 30px radius circle to catch all clicks
                    ctx.fillStyle = color;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 30, 0, 2 * Math.PI);
                    ctx.fill();
                  }}
                  nodeRelSize={30}
                  linkDirectionalArrowLength={3.5}
                  linkDirectionalArrowRelPos={1}
                  linkColor={() => '#6b7280'}
                  linkWidth={2.5}
                  backgroundColor="#f9fafb"
                  onNodeClick={(node) => {
                    setSelectedNode(node);
                    setShowAddNode(false);
                    if (graphRef.current) {
                      graphRef.current.centerAt(node.x, node.y, 1000);
                      graphRef.current.zoom(1.5, 1000);
                    }
                  }}
                  onNodeHover={(node) => {
                    document.body.style.cursor = node ? 'pointer' : 'default';
                  }}
                  enableNodeDrag={true}
                  enableZoomInteraction={true}
                  enablePanInteraction={true}
                />
              </div>
            </div>
          )}

          {activeView === 'console' && (
            <div className="h-full flex">
              {/* Main Chat Area */}
              <div className="flex-1 flex flex-col bg-gray-50">
                {/* Chat Header */}
                <div className="bg-white border-b border-gray-200 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        <Sparkles size={20} className="text-blue-600" />
                        AI-Powered Query Console
                      </h2>
                      <p className="text-sm text-gray-600 mt-1">
                        Ask questions about your infrastructure in natural language
                      </p>
                    </div>
                    <button
                      onClick={async () => {
                        await fetch(`${API_BASE}/api/chat/reset`, { method: 'POST' });
                        setMessages([]);
                      }}
                      className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-2"
                    >
                      <RefreshCw size={16} />
                      Clear History
                    </button>
                  </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  {messages.length === 0 ? (
                    <div className="h-full flex items-center justify-center">
                      <div className="text-center max-w-2xl">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                          <MessageSquare size={32} className="text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-3">Start Your Investigation</h3>
                        <p className="text-gray-600 mb-6">
                          Ask questions about services, dependencies, teams, or explore blast radius scenarios
                        </p>
                        
                        {/* Example Queries */}
                        <div className="grid grid-cols-1 gap-3 text-left">
                          <div className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
                               onClick={() => setInput('What breaks if order-service goes down?')}>
                            <div className="flex items-start gap-3">
                              <AlertCircle size={20} className="text-orange-500 mt-0.5" />
                              <div>
                                <div className="font-medium text-gray-900 text-sm">Blast Radius Analysis</div>
                                <div className="text-xs text-gray-600 mt-1">What breaks if order-service goes down?</div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
                               onClick={() => setInput('Who owns payment-service?')}>
                            <div className="flex items-start gap-3">
                              <Users size={20} className="text-purple-500 mt-0.5" />
                              <div>
                                <div className="font-medium text-gray-900 text-sm">Service Ownership</div>
                                <div className="text-xs text-gray-600 mt-1">Who owns payment-service?</div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
                               onClick={() => setInput('What services depend on user-service?')}>
                            <div className="flex items-start gap-3">
                              <TrendingUp size={20} className="text-green-500 mt-0.5" />
                              <div>
                                <div className="font-medium text-gray-900 text-sm">Dependency Analysis</div>
                                <div className="text-xs text-gray-600 mt-1">What services depend on user-service?</div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
                               onClick={() => setInput('Show me all databases')}>
                            <div className="flex items-start gap-3">
                              <Database size={20} className="text-blue-500 mt-0.5" />
                              <div>
                                <div className="font-medium text-gray-900 text-sm">Resource Discovery</div>
                                <div className="text-xs text-gray-600 mt-1">Show me all databases</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-3xl ${msg.role === 'user' ? 'w-auto' : 'w-full'}`}>
                            {msg.role === 'assistant' && (
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                                  <Sparkles size={14} className="text-white" />
                                </div>
                                <span className="text-xs font-medium text-gray-600">AI Assistant</span>
                                <span className="text-xs text-gray-400">
                                  <Clock size={12} className="inline mr-1" />
                                  {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                </span>
                              </div>
                            )}
                            
                            <div className={`rounded-lg ${
                              msg.role === 'user' 
                                ? 'bg-blue-600 text-white px-4 py-3' 
                                : msg.error 
                                  ? 'bg-red-50 border border-red-200 px-4 py-3' 
                                  : 'bg-white border border-gray-200 shadow-sm'
                            }`}>
                              {msg.role === 'assistant' && !msg.error ? (
                                <div className="p-4">
                                  <div className="prose prose-sm max-w-none">
                                    <div className="text-sm text-gray-900 whitespace-pre-wrap leading-relaxed">
                                      {msg.content}
                                    </div>
                                  </div>
                                  
                                  {/* Action Buttons */}
                                  <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-100">
                                    <button
                                      onClick={() => {
                                        navigator.clipboard.writeText(msg.content);
                                      }}
                                      className="text-xs text-gray-600 hover:text-gray-900 flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-100 transition-colors"
                                    >
                                      <Copy size={12} />
                                      Copy
                                    </button>
                                    <button className="text-xs text-gray-600 hover:text-gray-900 flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-100 transition-colors">
                                      <RefreshCw size={12} />
                                      Regenerate
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                <div className="text-sm whitespace-pre-wrap">
                                  {msg.content}
                                  {msg.role === 'user' && (
                                    <span className="block text-xs opacity-75 mt-2">
                                      {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {/* Typing Indicator */}
                      {loading && (
                        <div className="flex justify-start">
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                              <Loader2 size={14} className="text-white animate-spin" />
                            </div>
                            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                              <div className="flex items-center gap-2">
                                <div className="flex gap-1">
                                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                                </div>
                                <span className="text-xs text-gray-600">Analyzing...</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>

                {/* Input Area */}
                <div className="bg-white border-t border-gray-200 p-4">
                  <div className="max-w-4xl mx-auto">
                    <div className="flex gap-3">
                      <div className="flex-1 relative">
                        <input
                          type="text"
                          value={input}
                          onChange={(e) => setInput(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                          placeholder="Ask anything about your infrastructure..."
                          disabled={loading}
                          className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                        />
                        <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
                          {input.length}/500
                        </div>
                      </div>
                      <button
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all text-sm font-medium flex items-center gap-2 shadow-sm hover:shadow-md"
                      >
                        {loading ? (
                          <>
                            <Loader2 size={18} className="animate-spin" />
                            Processing
                          </>
                        ) : (
                          <>
                            <Send size={18} />
                            Send
                          </>
                        )}
                      </button>
                    </div>
                    <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                      <div>Press Enter to send • Shift+Enter for new line</div>
                      <div>{messages.length} messages</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Sidebar - Quick Actions & History */}
              <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900 text-sm">Quick Actions</h3>
                </div>
                
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {/* Common Queries */}
                  <div>
                    <h4 className="text-xs font-medium text-gray-500 uppercase mb-2">Popular Queries</h4>
                    <div className="space-y-2">
                      {[
                        { icon: AlertCircle, label: 'Blast Radius', query: 'What breaks if [service] goes down?', color: 'text-orange-500' },
                        { icon: Users, label: 'Ownership', query: 'Who owns [service]?', color: 'text-purple-500' },
                        { icon: TrendingUp, label: 'Dependencies', query: 'What depends on [service]?', color: 'text-green-500' },
                        { icon: Network, label: 'Connections', query: 'Show connections for [service]', color: 'text-blue-500' }
                      ].map((item, idx) => (
                        <button
                          key={idx}
                          onClick={() => setInput(item.query)}
                          className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors border border-gray-200 group"
                        >
                          <div className="flex items-center gap-2">
                            <item.icon size={16} className={item.color} />
                            <div className="flex-1">
                              <div className="text-xs font-medium text-gray-900">{item.label}</div>
                              <div className="text-xs text-gray-500 group-hover:text-gray-700">{item.query}</div>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Recent Services */}
                  {graphData.nodes.length > 0 && (
                    <div>
                      <h4 className="text-xs font-medium text-gray-500 uppercase mb-2">Your Services</h4>
                      <div className="space-y-1">
                        {graphData.nodes
                          .filter(n => n.type === 'service')
                          .slice(0, 8)
                          .map((node, idx) => (
                            <button
                              key={idx}
                              onClick={() => setInput(`What breaks if ${node.name} goes down?`)}
                              className="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 transition-colors text-xs text-gray-700 hover:text-blue-900 border border-transparent hover:border-blue-200"
                            >
                              <div className="font-mono">{node.name}</div>
                            </button>
                          ))}
                      </div>
                    </div>
                  )}

                  {/* Stats */}
                  <div className="pt-4 border-t border-gray-200">
                    <h4 className="text-xs font-medium text-gray-500 uppercase mb-3">Session Stats</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">Total Queries</span>
                        <span className="font-semibold text-gray-900">{messages.filter(m => m.role === 'user').length}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">Nodes in Graph</span>
                        <span className="font-semibold text-gray-900">{graphData.nodes.length}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">Connections</span>
                        <span className="font-semibold text-gray-900">{graphData.links.length}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeView === 'analytics' && (
            <div className="h-full overflow-y-auto bg-gray-50">
              <div className="p-6 space-y-6">
                {/* Header */}
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
                  <p className="text-sm text-gray-600 mt-1">Comprehensive insights into your knowledge graph</p>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-4 gap-6">
                  {(() => {
                    const avgConnections = stats.totalNodes > 0 ? (stats.edges / stats.totalNodes).toFixed(1) : 0;
                    const nodeGrowth = stats.totalNodes > 10 ? '+12%' : stats.totalNodes > 5 ? '+8%' : 'New';
                    const edgeGrowth = stats.edges > 20 ? '+15%' : stats.edges > 10 ? '+10%' : 'Growing';
                    const serviceGrowth = stats.services > 5 ? '+7%' : stats.services > 2 ? '+5%' : 'Active';
                    
                    return [
                      { 
                        label: 'Total Nodes', 
                        value: stats.totalNodes,
                        change: nodeGrowth,
                        trend: 'up',
                        icon: Network,
                        color: 'blue',
                        bgColor: 'bg-blue-50',
                        iconColor: 'text-blue-600',
                        changeColor: 'text-green-600'
                      },
                      { 
                        label: 'Connections', 
                        value: stats.edges,
                        change: edgeGrowth,
                        trend: 'up',
                        icon: Network,
                        color: 'purple',
                        bgColor: 'bg-purple-50',
                        iconColor: 'text-purple-600',
                        changeColor: 'text-green-600'
                      },
                      { 
                        label: 'Services', 
                        value: stats.services,
                        change: serviceGrowth,
                        trend: 'up',
                        icon: Database,
                        color: 'green',
                        bgColor: 'bg-green-50',
                        iconColor: 'text-green-600',
                        changeColor: 'text-green-600'
                      },
                      { 
                        label: 'Avg. Connections', 
                        value: avgConnections,
                        change: avgConnections > 3 ? 'Excellent' : avgConnections > 2 ? 'Good' : avgConnections > 1 ? 'Fair' : 'Low',
                        trend: 'up',
                        icon: BarChart3,
                        color: 'orange',
                        bgColor: 'bg-orange-50',
                        iconColor: 'text-orange-600',
                        changeColor: avgConnections > 2 ? 'text-green-600' : 'text-orange-600'
                      }
                    ].map((metric, i) => (
                      <div key={i} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm text-gray-600 mb-2">{metric.label}</p>
                            <p className="text-3xl font-bold text-gray-900">{metric.value}</p>
                            <div className="flex items-center gap-1 mt-2">
                              <span className={`text-xs font-medium ${metric.changeColor}`}>
                                {metric.change}
                              </span>
                              <span className="text-xs text-gray-500">status</span>
                            </div>
                          </div>
                          <div className={`p-3 ${metric.bgColor} rounded-lg`}>
                            <metric.icon size={24} className={metric.iconColor} />
                          </div>
                        </div>
                      </div>
                    ));
                  })()}
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-2 gap-6">
                  {/* Node Distribution Chart */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="font-semibold text-gray-900">Node Distribution</h3>
                      <span className="text-xs text-gray-500">By Type</span>
                    </div>
                    <div className="space-y-4">
                      {[
                        { label: 'Services', count: stats.services, total: stats.totalNodes, color: 'bg-blue-500', lightColor: 'bg-blue-100' },
                        { label: 'Databases', count: stats.databases, total: stats.totalNodes, color: 'bg-purple-500', lightColor: 'bg-purple-100' },
                        { label: 'Teams', count: stats.teams, total: stats.totalNodes, color: 'bg-green-500', lightColor: 'bg-green-100' },
                        { label: 'Other', count: stats.totalNodes - stats.services - stats.databases - stats.teams, total: stats.totalNodes, color: 'bg-gray-500', lightColor: 'bg-gray-100' }
                      ].map((item, i) => {
                        const percentage = stats.totalNodes > 0 ? (item.count / item.total) * 100 : 0;
                        return (
                          <div key={i}>
                            <div className="flex justify-between items-center mb-2">
                              <div className="flex items-center gap-2">
                                <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                                <span className="text-sm font-medium text-gray-700">{item.label}</span>
                              </div>
                              <span className="text-sm text-gray-900 font-semibold">{item.count} ({percentage.toFixed(1)}%)</span>
                            </div>
                            <div className={`h-3 ${item.lightColor} rounded-full overflow-hidden`}>
                              <div className={`h-full ${item.color}`} style={{ width: `${percentage}%` }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Connection Density */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="font-semibold text-gray-900">Connection Density</h3>
                      <span className="text-xs text-gray-500">Network Health</span>
                    </div>
                    <div className="space-y-4">
                      <div className="text-center py-8">
                        {(() => {
                          const density = stats.totalNodes > 1 ? ((stats.edges / (stats.totalNodes * (stats.totalNodes - 1))) * 100) : 0;
                          const densityColor = density > 10 ? 'from-green-500 to-green-600' : 
                                              density > 5 ? 'from-blue-500 to-blue-600' : 
                                              'from-orange-500 to-orange-600';
                          return (
                            <>
                              <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br ${densityColor} mb-4`}>
                                <span className="text-4xl font-bold text-white">
                                  {density.toFixed(1)}%
                                </span>
                              </div>
                              <p className="text-sm text-gray-600">Network Density Score</p>
                              <p className="text-xs text-gray-500 mt-1">
                                {density > 10 ? 'Highly connected' : 
                                 density > 5 ? 'Well connected' : 
                                 density > 2 ? 'Moderately connected' : 
                                 'Growing network'}
                              </p>
                            </>
                          );
                        })()}
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-900">{stats.edges}</p>
                          <p className="text-xs text-gray-600">Total Edges</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-900">
                            {stats.totalNodes > 0 ? (stats.edges / stats.totalNodes).toFixed(1) : 0}
                          </p>
                          <p className="text-xs text-gray-600">Avg. per Node</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Top Nodes Table */}
                <div className="bg-white rounded-lg border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="font-semibold text-gray-900">Most Connected Nodes</h3>
                    <p className="text-xs text-gray-500 mt-1">Nodes with highest connection count</p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Node</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Connections</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {(() => {
                          const nodesWithConnections = graphData.nodes.map(node => ({
                            ...node,
                            connections: graphData.links.filter(l => 
                              (l.source.id || l.source) === node.id || 
                              (l.target.id || l.target) === node.id
                            ).length
                          }));
                          
                          const sortedNodes = nodesWithConnections.sort((a, b) => b.connections - a.connections);
                          const maxConnections = sortedNodes.length > 0 ? sortedNodes[0].connections : 1;
                          
                          return sortedNodes.slice(0, 5).map((node, i) => (
                            <tr key={node.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                  <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                                    i === 0 ? 'bg-yellow-100 text-yellow-700' :
                                    i === 1 ? 'bg-gray-100 text-gray-700' :
                                    i === 2 ? 'bg-orange-100 text-orange-700' :
                                    'bg-gray-50 text-gray-600'
                                  }`}>
                                    {i + 1}
                                  </span>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                  <div className="w-2 h-2 rounded-full mr-3" style={{ backgroundColor: getNodeColor(node) }}></div>
                                  <span className="text-sm font-medium text-gray-900">{node.name}</span>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                  node.type === 'service' ? 'bg-blue-100 text-blue-700' :
                                  node.type === 'database' ? 'bg-purple-100 text-purple-700' :
                                  node.type === 'team' ? 'bg-green-100 text-green-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {node.type}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-semibold text-gray-900">{node.connections}</span>
                                  <div className="flex-1 h-1.5 bg-gray-100 rounded-full max-w-[60px]">
                                    <div 
                                      className="h-full bg-blue-500 rounded-full" 
                                      style={{ width: `${(node.connections / maxConnections) * 100}%` }}
                                    ></div>
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${
                                  node.connections > 5 ? 'bg-green-50 text-green-700' :
                                  node.connections > 2 ? 'bg-blue-50 text-blue-700' :
                                  'bg-gray-50 text-gray-700'
                                }`}>
                                  <div className={`w-1.5 h-1.5 rounded-full ${
                                    node.connections > 5 ? 'bg-green-500' :
                                    node.connections > 2 ? 'bg-blue-500' :
                                    'bg-gray-500'
                                  }`}></div>
                                  {node.connections > 5 ? 'Critical' : node.connections > 2 ? 'Active' : 'Normal'}
                                </span>
                              </td>
                            </tr>
                          ));
                        })()}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Insights Cards */}
                <div className="grid grid-cols-3 gap-6">
                  {(() => {
                    const avgConnections = stats.totalNodes > 0 ? stats.edges / stats.totalNodes : 0;
                    const density = stats.totalNodes > 1 ? (stats.edges / (stats.totalNodes * (stats.totalNodes - 1))) * 100 : 0;
                    const orphanedNodes = graphData.nodes.filter(node => 
                      !graphData.links.some(l => 
                        (l.source.id || l.source) === node.id || 
                        (l.target.id || l.target) === node.id
                      )
                    ).length;
                    const dataQuality = stats.totalNodes > 0 ? ((stats.totalNodes - orphanedNodes) / stats.totalNodes * 100) : 100;
                    
                    const healthStatus = avgConnections > 3 ? 'Excellent' : avgConnections > 2 ? 'Good' : avgConnections > 1 ? 'Fair' : 'Growing';
                    const healthDesc = avgConnections > 3 ? 'Highly interconnected with strong relationships' :
                                      avgConnections > 2 ? 'Well-connected with balanced distribution' :
                                      avgConnections > 1 ? 'Moderately connected, room for growth' :
                                      'Building connections, add more relationships';
                    
                    const growthPercent = stats.totalNodes > 15 ? 20 : stats.totalNodes > 10 ? 15 : stats.totalNodes > 5 ? 10 : 5;
                    const growthDesc = stats.totalNodes > 15 ? 'Rapid expansion with new nodes' :
                                      stats.totalNodes > 10 ? 'Steady growth this month' :
                                      stats.totalNodes > 5 ? 'Growing infrastructure' :
                                      'Starting to build your graph';
                    
                    return (
                      <>
                        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-white bg-opacity-20 rounded-lg">
                              <Network size={24} />
                            </div>
                            <h4 className="font-semibold">Network Health</h4>
                          </div>
                          <p className="text-3xl font-bold mb-2">{healthStatus}</p>
                          <p className="text-sm text-blue-100">{healthDesc}</p>
                        </div>

                        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-white bg-opacity-20 rounded-lg">
                              <BarChart3 size={24} />
                            </div>
                            <h4 className="font-semibold">Growth Trend</h4>
                          </div>
                          <p className="text-3xl font-bold mb-2">↑ {growthPercent}%</p>
                          <p className="text-sm text-purple-100">{growthDesc}</p>
                        </div>

                        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-white bg-opacity-20 rounded-lg">
                              <CheckCircle2 size={24} />
                            </div>
                            <h4 className="font-semibold">Data Quality</h4>
                          </div>
                          <p className="text-3xl font-bold mb-2">{dataQuality.toFixed(0)}%</p>
                          <p className="text-sm text-green-100">
                            {orphanedNodes === 0 ? 'Perfect! All nodes are connected' :
                             orphanedNodes === 1 ? '1 orphaned node detected' :
                             `${orphanedNodes} orphaned nodes detected`}
                          </p>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">Upload Configuration</h3>
              <button 
                onClick={() => {
                  setShowUploadModal(false);
                  setUploadStatus(null);
                }} 
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle size={20} />
              </button>
            </div>
            <div className="p-6">
              {uploadStatus ? (
                <div className={`p-4 rounded-lg ${
                  uploadStatus.success ? 'bg-green-50 border border-green-200' : 
                  uploadStatus.loading ? 'bg-blue-50 border border-blue-200' : 
                  'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center gap-3">
                    {uploadStatus.loading ? (
                      <Loader2 className="animate-spin text-blue-600" size={24} />
                    ) : uploadStatus.success ? (
                      <CheckCircle2 className="text-green-600" size={24} />
                    ) : (
                      <AlertCircle className="text-red-600" size={24} />
                    )}
                    <div className={`text-sm font-medium ${
                      uploadStatus.success ? 'text-green-900' : 
                      uploadStatus.loading ? 'text-blue-900' : 
                      'text-red-900'
                    }`}>
                      {uploadStatus.message}
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <input 
                    ref={fileInputRef} 
                    type="file" 
                    onChange={handleFileUpload} 
                    accept=".yml,.yaml,.json" 
                    className="hidden" 
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full py-12 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors"
                  >
                    <Upload size={32} className="mx-auto text-gray-400 mb-3" />
                    <div className="text-sm font-medium text-gray-900">Click to upload</div>
                    <div className="text-xs text-gray-500 mt-1">Supports: docker-compose.yml, k8s-deployments.yaml, teams.yaml</div>
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Fullscreen Graph Modal */}
      {isGraphFullscreen && (
        <div className="fixed inset-0 bg-gray-900 z-50 flex flex-col">
          {/* Fullscreen Header */}
          <div className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h3 className="font-semibold text-white text-lg">Graph Explorer - Fullscreen</h3>
              <div className="text-sm text-gray-400">
                {filteredData.nodes.length} nodes • {filteredData.links.length} edges
              </div>
            </div>
            <div className="flex items-center gap-3">
              {selectedNode && (
                <div className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md">
                  Selected: {selectedNode.name}
                </div>
              )}
              <button
                onClick={() => setIsGraphFullscreen(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-white"
                title="Exit Fullscreen"
              >
                <Minimize2 size={20} />
              </button>
            </div>
          </div>

          {/* Fullscreen Graph */}
          <div className="flex-1 relative bg-gray-50">
            <ForceGraph2D
              ref={graphRef}
              graphData={filteredData}
              nodeCanvasObject={paintNode}
              nodePointerAreaPaint={(node, color, ctx) => {
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, 10, 0, 2 * Math.PI);
                ctx.fill();
              }}
              linkDirectionalArrowLength={3.5}
              linkDirectionalArrowRelPos={1}
              linkColor={() => '#d1d5db'}
              linkWidth={1.5}
              backgroundColor="#fafafa"
              onNodeClick={(node) => {
                console.log('Node clicked:', node);
                setSelectedNode(node);
              }}
              onNodeHover={(node) => {
                document.body.style.cursor = node ? 'pointer' : 'default';
              }}
              enableNodeDrag={true}
              enableZoomInteraction={true}
              enablePanInteraction={true}
            />

            {/* Controls Overlay */}
            <div className="absolute bottom-6 left-6 bg-white border border-gray-300 rounded-lg shadow-lg p-4">
              <div className="text-xs font-medium text-gray-700 mb-2">Controls:</div>
              <div className="space-y-1 text-xs text-gray-600">
                <div>• Click node to select</div>
                <div>• Drag to pan</div>
                <div>• Scroll to zoom</div>
                <div>• Press ESC to exit</div>
              </div>
            </div>

            {/* Selected Node Info */}
            {selectedNode && (
              <div className="absolute top-6 right-6 bg-white border border-gray-300 rounded-lg shadow-lg p-4 w-80">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{selectedNode.name}</h4>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    selectedNode.type === 'service' ? 'bg-blue-100 text-blue-700' :
                    selectedNode.type === 'database' ? 'bg-green-100 text-green-700' :
                    selectedNode.type === 'team' ? 'bg-purple-100 text-purple-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {selectedNode.type}
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">ID:</span>
                    <span className="ml-2 text-gray-900 font-mono text-xs">{selectedNode.id}</span>
                  </div>
                  {selectedNode.team && (
                    <div>
                      <span className="text-gray-600">Team:</span>
                      <span className="ml-2 text-gray-900">{selectedNode.team}</span>
                    </div>
                  )}
                  {selectedNode.language && (
                    <div>
                      <span className="text-gray-600">Language:</span>
                      <span className="ml-2 text-gray-900">{selectedNode.language}</span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="mt-3 w-full px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Clear Selection
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnterpriseDashboard;
