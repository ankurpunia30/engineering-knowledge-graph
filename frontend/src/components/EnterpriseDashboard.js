import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
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
  Search
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

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
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Knowledge Graph</h1>
          <p className="text-xs text-gray-500 mt-1">Engineering Platform</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
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

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
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
            <div className="h-full flex bg-gray-50">
              {/* Left Sidebar - Search & Filter */}
              <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-3">Explorer</h3>
                  
                  {/* Search Input */}
                  <div className="relative mb-3">
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search nodes..."
                      className="w-full px-3 py-2 pl-10 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
                    {searchQuery && (
                      <button
                        onClick={() => {
                          setSearchQuery('');
                          setHighlightNodes(new Set());
                        }}
                        className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                      >
                        <XCircle size={16} />
                      </button>
                    )}
                  </div>

                  {/* Filter Tabs */}
                  <div className="flex gap-2 flex-wrap">
                    {[
                      { id: 'all', label: 'All', icon: Network },
                      { id: 'service', label: 'Services', icon: Database },
                      { id: 'database', label: 'Databases', icon: Database },
                      { id: 'team', label: 'Teams', icon: Users }
                    ].map((filter) => (
                      <button
                        key={filter.id}
                        onClick={() => setFilterType(filter.id)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                          filterType === filter.id
                            ? 'bg-blue-500 text-white shadow-sm'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        <filter.icon size={14} />
                        {filter.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Node List */}
                <div className="flex-1 overflow-y-auto p-4">
                  <div className="text-xs text-gray-500 mb-2">
                    Showing {filteredData.nodes.length} of {graphData.nodes.length} nodes
                  </div>
                  <div className="space-y-2">
                    {filteredData.nodes.map((node) => (
                      <div
                        key={node.id}
                        onClick={() => {
                          setSelectedNode(node);
                          // Center graph on selected node
                          if (graphRef.current) {
                            graphRef.current.centerAt(node.x, node.y, 1000);
                            graphRef.current.zoom(2, 1000);
                          }
                        }}
                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                          selectedNode?.id === node.id
                            ? 'border-blue-500 bg-blue-50 shadow-md'
                            : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-sm'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <div
                                className="w-2 h-2 rounded-full"
                                style={{ backgroundColor: getNodeColor(node) }}
                              ></div>
                              <div className="font-medium text-sm text-gray-900 font-mono">
                                {node.name}
                              </div>
                            </div>
                            <div className="text-xs text-gray-500">{node.type}</div>
                            {node.team && (
                              <div className="text-xs text-gray-400 mt-1">Team: {node.team}</div>
                            )}
                          </div>
                          {selectedNode?.id === node.id && (
                            <CheckCircle2 size={16} className="text-blue-500 flex-shrink-0" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Stats Footer */}
                <div className="border-t border-gray-200 p-4 bg-gray-50">
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <div className="text-gray-500">Nodes</div>
                      <div className="font-semibold text-gray-900">{filteredData.nodes.length}</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Edges</div>
                      <div className="font-semibold text-gray-900">{filteredData.links.length}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Center - Graph Visualization */}
              <div className="flex-1 relative">
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

                {/* Search Results Badge */}
                {searchQuery && (
                  <div className="absolute top-4 left-4 bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-lg">
                    <div className="text-sm font-medium text-gray-900">
                      Found {filteredData.nodes.length} results for "{searchQuery}"
                    </div>
                  </div>
                )}
              </div>

              {/* Right Sidebar - CRUD Operations */}
              <div className="w-96 bg-white border-l border-gray-200 flex flex-col shadow-lg">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
                  <h2 className="text-lg font-semibold text-gray-900 mb-1">
                    {selectedNode ? 'Edit Node' : 'Node Operations'}
                  </h2>
                  <p className="text-xs text-gray-600">
                    {selectedNode ? `Editing: ${selectedNode.name}` : 'Select a node from the list or graph'}
                  </p>
                </div>

                {selectedNode ? (
                  <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* Node Details */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-900">{selectedNode.name}</h3>
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
                        {selectedNode.language && (
                          <div>
                            <span className="text-gray-600">Language:</span>
                            <span className="ml-2 text-gray-900">{selectedNode.language}</span>
                          </div>
                        )}
                        {selectedNode.owner && (
                          <div>
                            <span className="text-gray-600">Owner:</span>
                            <span className="ml-2 text-gray-900">{selectedNode.owner}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* CRUD Status Messages */}
                    {crudStatus && (
                      <div className={`p-3 rounded-lg ${
                        crudStatus.loading ? 'bg-blue-50 border border-blue-200' :
                        crudStatus.success ? 'bg-green-50 border border-green-200' :
                        'bg-red-50 border border-red-200'
                      }`}>
                        <div className="flex items-center gap-2 text-sm">
                          {crudStatus.loading ? <Loader2 className="animate-spin" size={16} /> :
                           crudStatus.success ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                          <span>{crudStatus.message}</span>
                        </div>
                      </div>
                    )}

                    {/* Edit Node */}
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Edit size={16} />
                        Edit Node
                      </h4>
                      <div className="space-y-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Name</label>
                          <input
                            type="text"
                            value={editNodeName || selectedNode.name}
                            onChange={(e) => setEditNodeName(e.target.value)}
                            placeholder={selectedNode.name}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
                          <select
                            value={editNodeType || selectedNode.type}
                            onChange={(e) => setEditNodeType(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="service">Service</option>
                            <option value="database">Database</option>
                            <option value="cache">Cache</option>
                            <option value="team">Team</option>
                          </select>
                        </div>
                        <button 
                          onClick={handleUpdateNode}
                          disabled={crudStatus?.loading}
                          className="w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {crudStatus?.loading ? 'Updating...' : 'Update Node'}
                        </button>
                      </div>
                    </div>

                    {/* Delete Node */}
                    <div className="border border-red-200 rounded-lg p-4 bg-red-50">
                      <h4 className="font-semibold text-red-900 mb-2 flex items-center gap-2">
                        <Trash2 size={16} />
                        Delete Node
                      </h4>
                      <p className="text-xs text-red-700 mb-3">
                        This will permanently delete the node and all its connections.
                      </p>
                      <button 
                        onClick={handleDeleteNode}
                        disabled={crudStatus?.loading}
                        className="w-full px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {crudStatus?.loading ? 'Deleting...' : 'Delete Node'}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex-1 flex items-center justify-center p-4">
                    <div className="text-center">
                      <Network size={48} className="mx-auto text-gray-300 mb-3" />
                      <p className="text-sm text-gray-600">Select a node to view details</p>
                      <p className="text-xs text-gray-500 mt-1">Click any node in the graph</p>
                    </div>
                  </div>
                )}

                {/* Add New Node Section */}
                <div className="border-t border-gray-200 p-4">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Plus size={16} />
                    Add New Node
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Name</label>
                      <input
                        type="text"
                        value={newNodeName}
                        onChange={(e) => setNewNodeName(e.target.value)}
                        placeholder="new-service"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
                      <select 
                        value={newNodeType}
                        onChange={(e) => setNewNodeType(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="service">Service</option>
                        <option value="database">Database</option>
                        <option value="cache">Cache</option>
                        <option value="team">Team</option>
                      </select>
                    </div>
                    <button 
                      onClick={handleCreateNode}
                      disabled={crudStatus?.loading}
                      className="w-full px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Plus size={16} />
                      {crudStatus?.loading ? 'Creating...' : 'Create Node'}
                    </button>
                  </div>
                </div>
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
            <div className="h-full overflow-y-auto p-6">
              <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Node Distribution</h3>
                  <div className="space-y-4">
                    {[
                      { label: 'Services', count: stats.services, total: stats.totalNodes, color: 'bg-blue-500' },
                      { label: 'Databases', count: stats.databases, total: stats.totalNodes, color: 'bg-green-500' },
                      { label: 'Teams', count: stats.teams, total: stats.totalNodes, color: 'bg-purple-500' }
                    ].map((item, i) => {
                      const percentage = stats.totalNodes > 0 ? (item.count / item.total) * 100 : 0;
                      return (
                        <div key={i}>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-700">{item.label}</span>
                            <span className="text-sm text-gray-600">{item.count} ({percentage.toFixed(0)}%)</span>
                          </div>
                          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div className={`h-full ${item.color}`} style={{ width: `${percentage}%` }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
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
    </div>
  );
};

export default EnterpriseDashboard;
