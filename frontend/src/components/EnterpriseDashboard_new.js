import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import './EnterpriseDashboard.css';

// Determine API base URL at runtime
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  return window.location.origin;
};

const API_BASE = getApiBaseUrl();

const EnterpriseDashboard = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ nodes: 0, edges: 0, services: 0, teams: 0 });
  const [selectedNode, setSelectedNode] = useState(null);
  const [filter, setFilter] = useState('all');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const graphRef = useRef();

  // Fetch graph data
  useEffect(() => {
    fetch(`${API_BASE}/api/graph/data`)
      .then(res => res.json())
      .then(data => {
        setGraphData(data);
        setStats({
          nodes: data.nodes.length,
          edges: data.links.length,
          services: data.nodes.filter(n => n.type === 'service').length,
          teams: data.nodes.filter(n => n.type === 'team').length
        });
      })
      .catch(err => console.error('Failed to load graph:', err));
  }, []);

  // Send query
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setInput('');

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      
      if (data.related_nodes) {
        const nodeIds = data.related_nodes.map(n => n.split(':')[1]);
        highlightNodes(nodeIds);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: ' + err.message }]);
    }
    setLoading(false);
  };

  const highlightNodes = (nodeIds) => {
    const nodes = graphData.nodes.filter(n => nodeIds.includes(n.id));
    if (nodes.length > 0 && graphRef.current) {
      graphRef.current.centerAt(nodes[0].x, nodes[0].y, 1000);
      graphRef.current.zoom(3, 1000);
    }
  };

  // Upload file
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData
      });
      // Reload graph data
      window.location.reload();
    } catch (err) {
      alert('Upload failed: ' + err.message);
    }
  };

  const filteredData = {
    nodes: filter === 'all' ? graphData.nodes : graphData.nodes.filter(n => n.type === filter),
    links: graphData.links
  };

  return (
    <div className="ekg-container">
      {/* Top Bar */}
      <div className="ekg-topbar">
        <div className="ekg-topbar-left">
          <h1 className="ekg-title">Engineering Knowledge Graph</h1>
          <div className="ekg-stats-inline">
            <span>{stats.nodes} nodes</span>
            <span>{stats.edges} edges</span>
            <span>{stats.services} services</span>
            <span>{stats.teams} teams</span>
          </div>
        </div>
        <div className="ekg-topbar-right">
          <input
            type="file"
            ref={fileInputRef => fileInputRef}
            onChange={handleFileUpload}
            accept=".yml,.yaml"
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label htmlFor="file-upload" className="ekg-btn-secondary">
            Upload Config
          </label>
          <select 
            className="ekg-select"
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Nodes</option>
            <option value="service">Services</option>
            <option value="database">Databases</option>
            <option value="team">Teams</option>
          </select>
        </div>
      </div>

      {/* Main Content */}
      <div className="ekg-main">
        {/* Sidebar */}
        {sidebarOpen && (
          <div className="ekg-sidebar">
            <div className="ekg-sidebar-header">
              <h3>Query Console</h3>
              <button 
                className="ekg-btn-icon"
                onClick={() => setSidebarOpen(false)}
              >×</button>
            </div>
            
            <div className="ekg-messages">
              {messages.length === 0 ? (
                <div className="ekg-empty-state">
                  <p>Ask questions about your infrastructure:</p>
                  <ul>
                    <li>What depends on redis?</li>
                    <li>Who owns payment-service?</li>
                    <li>Show blast radius of api-gateway</li>
                  </ul>
                </div>
              ) : (
                messages.map((msg, i) => (
                  <div key={i} className={`ekg-message ekg-message-${msg.role}`}>
                    <div className="ekg-message-content">{msg.content}</div>
                  </div>
                ))
              )}
              {loading && <div className="ekg-loading">Processing...</div>}
            </div>

            <form onSubmit={handleSubmit} className="ekg-input-form">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question..."
                className="ekg-input"
              />
              <button type="submit" className="ekg-btn-primary">
                Send
              </button>
            </form>
          </div>
        )}

        {/* Graph View */}
        <div className="ekg-graph-container">
          {!sidebarOpen && (
            <button 
              className="ekg-sidebar-toggle"
              onClick={() => setSidebarOpen(true)}
            >
              ☰ Query
            </button>
          )}
          
          {selectedNode && (
            <div className="ekg-node-info">
              <button 
                className="ekg-close"
                onClick={() => setSelectedNode(null)}
              >×</button>
              <h4>{selectedNode.name}</h4>
              <div className="ekg-node-detail">
                <span className="ekg-label">Type:</span>
                <span>{selectedNode.type}</span>
              </div>
              {selectedNode.team && (
                <div className="ekg-node-detail">
                  <span className="ekg-label">Team:</span>
                  <span>{selectedNode.team}</span>
                </div>
              )}
              <div className="ekg-node-detail">
                <span className="ekg-label">Connections:</span>
                <span>{graphData.links.filter(l => 
                  l.source === selectedNode.id || l.target === selectedNode.id
                ).length}</span>
              </div>
            </div>
          )}

          <ForceGraph2D
            ref={graphRef}
            graphData={filteredData}
            nodeLabel="name"
            nodeColor={node => {
              const colors = {
                service: '#3b82f6',
                database: '#10b981',
                cache: '#f59e0b',
                team: '#8b5cf6'
              };
              return colors[node.type] || '#6b7280';
            }}
            nodeRelSize={6}
            linkDirectionalArrowLength={3}
            linkDirectionalArrowRelPos={1}
            linkColor={() => '#374151'}
            linkWidth={1.5}
            backgroundColor="#0a0e1a"
            onNodeClick={setSelectedNode}
            onNodeHover={node => {
              document.body.style.cursor = node ? 'pointer' : 'default';
            }}
            d3VelocityDecay={0.3}
          />
        </div>
      </div>
    </div>
  );
};

export default EnterpriseDashboard;
