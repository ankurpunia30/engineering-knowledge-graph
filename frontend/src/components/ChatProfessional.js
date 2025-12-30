import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import api from '../services/apiEnhanced';

/**
 * Network Graph Visualization Component
 * Renders force-directed graph using react-force-graph
 */
const NetworkGraphView = ({ graphData, highlightedNodes, onNodeClick }) => {
  const fgRef = useRef();
  const [hoveredNode, setHoveredNode] = useState(null);

  useEffect(() => {
    // Auto-fit graph after initial render
    if (fgRef.current && graphData.nodes.length > 0) {
      setTimeout(() => {
        fgRef.current.zoomToFit(400, 50);
      }, 100);
    }
  }, [graphData]);

  const getNodeColor = (node) => {
    // Highlight selected nodes
    if (highlightedNodes.includes(node.id)) {
      return '#3B82F6'; // Bright blue for highlighted
    }
    
    // Color by node type
    const type = node.type?.toLowerCase() || '';
    if (type.includes('service')) return '#60A5FA';
    if (type.includes('database')) return '#34D399';
    if (type.includes('cache')) return '#FBBF24';
    if (type.includes('team')) return '#A78BFA';
    return '#9CA3AF';
  };

  const handleNodeClick = (node) => {
    if (onNodeClick) {
      onNodeClick(node.id);
    }
  };

  return (
    <div className="relative w-full h-full bg-gray-900">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel="name"
        nodeColor={getNodeColor}
        nodeVal={node => highlightedNodes.includes(node.id) ? 15 : 8}
        nodeRelSize={8}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12/globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.4);

          // Draw node circle
          const nodeSize = highlightedNodes.includes(node.id) ? 6 : 4;
          ctx.beginPath();
          ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI, false);
          ctx.fillStyle = getNodeColor(node);
          ctx.fill();

          // Draw label background
          ctx.fillStyle = 'rgba(17, 24, 39, 0.8)';
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - nodeSize - bckgDimensions[1], bckgDimensions[0], bckgDimensions[1]);

          // Draw label text
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = highlightedNodes.includes(node.id) ? '#60A5FA' : '#E5E7EB';
          ctx.fillText(label, node.x, node.y - nodeSize - fontSize/2);
        }}
        linkColor={link => {
          // Highlight links connected to highlighted nodes
          const sourceHighlighted = highlightedNodes.includes(link.source.id || link.source);
          const targetHighlighted = highlightedNodes.includes(link.target.id || link.target);
          if (sourceHighlighted || targetHighlighted) {
            return '#60A5FA';
          }
          return '#9CA3AF'; // Brighter gray for better visibility
        }}
        linkWidth={link => {
          const sourceHighlighted = highlightedNodes.includes(link.source.id || link.source);
          const targetHighlighted = highlightedNodes.includes(link.target.id || link.target);
          return (sourceHighlighted || targetHighlighted) ? 3 : 1.5;
        }}
        linkDirectionalArrowLength={8}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={2}
        linkDirectionalArrowColor={link => {
          const sourceHighlighted = highlightedNodes.includes(link.source.id || link.source);
          const targetHighlighted = highlightedNodes.includes(link.target.id || link.target);
          if (sourceHighlighted || targetHighlighted) {
            return '#60A5FA';
          }
          return '#9CA3AF';
        }}
        onNodeClick={handleNodeClick}
        onNodeHover={setHoveredNode}
        backgroundColor="#111827"
        cooldownTicks={100}
        onEngineStop={() => fgRef.current?.zoomToFit(400, 50)}
        d3VelocityDecay={0.3}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
      />
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-gray-800 border border-gray-700 rounded-lg p-3 text-xs">
        <div className="font-semibold text-gray-200 mb-2">Node Types</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#60A5FA]"></div>
            <span className="text-gray-300">Service</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#34D399]"></div>
            <span className="text-gray-300">Database</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#FBBF24]"></div>
            <span className="text-gray-300">Cache</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#A78BFA]"></div>
            <span className="text-gray-300">Team</span>
          </div>
        </div>
      </div>

      {/* Enhanced Hover Tooltip with Details */}
      {hoveredNode && (
        <div className="absolute top-4 right-4 bg-gray-800 border-2 border-gray-600 rounded-lg p-4 text-sm max-w-sm shadow-2xl">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: getNodeColor(hoveredNode) }}
                ></div>
                <span className="font-bold text-gray-100 text-base">{hoveredNode.name}</span>
              </div>
              <div className="text-xs text-gray-400 mt-1">ID: {hoveredNode.id}</div>
            </div>
          </div>
          
          <div className="space-y-2 border-t border-gray-700 pt-2">
            <div>
              <span className="text-gray-500 text-xs font-semibold">Type:</span>
              <span className="text-gray-200 text-xs ml-2">{hoveredNode.type || 'N/A'}</span>
            </div>
            
            {hoveredNode.team && (
              <div>
                <span className="text-gray-500 text-xs font-semibold">Team:</span>
                <span className="text-gray-200 text-xs ml-2">{hoveredNode.team}</span>
              </div>
            )}
            
            {/* Show connections count */}
            <div>
              <span className="text-gray-500 text-xs font-semibold">Connections:</span>
              <span className="text-gray-200 text-xs ml-2">
                {graphData.links.filter(l => 
                  (l.source.id || l.source) === hoveredNode.id || 
                  (l.target.id || l.target) === hoveredNode.id
                ).length} edges
              </span>
            </div>
            
            {highlightedNodes.includes(hoveredNode.id) && (
              <div className="mt-2 px-2 py-1 bg-blue-900 bg-opacity-50 rounded text-xs text-blue-300">
                ✨ Currently Highlighted
              </div>
            )}
          </div>
          
          <div className="mt-3 text-xs text-gray-500 border-t border-gray-700 pt-2">
            💡 Click to query this node
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * ChatProfessional - Professional knowledge graph interface
 * Features: Force-directed network graph, natural language queries, split view
 */
const ChatProfessional = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [highlightedNodes, setHighlightedNodes] = useState([]);
  const [viewMode, setViewMode] = useState('split'); // 'graph', 'split', 'chat'
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadGraphData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadGraphData = async () => {
    try {
      const data = await api.getGraphData();
      
      // Transform nodes
      const nodes = Object.values(data.nodes).map(node => ({
        id: node.id,
        name: node.name,
        type: node.type,
        team: node.metadata?.team
      }));

      // Create a set of valid node IDs for validation
      const validNodeIds = new Set(nodes.map(n => n.id));

      // Transform edges to links, filtering out invalid references
      const links = Object.values(data.edges)
        .filter(edge => {
          // Filter out edges with missing or invalid node references
          if (!edge.from_node || !edge.to_node) {
            console.warn('Edge missing source or target:', edge);
            return false;
          }
          if (!validNodeIds.has(edge.from_node)) {
            console.warn('Edge source node not found:', edge.from_node);
            return false;
          }
          if (!validNodeIds.has(edge.to_node)) {
            console.warn('Edge target node not found:', edge.to_node);
            return false;
          }
          return true;
        })
        .map(edge => ({
          source: edge.from_node,
          target: edge.to_node,
          type: edge.type
        }));

      console.log(`Loaded ${nodes.length} nodes and ${links.length} links`);
      console.log('Sample nodes:', nodes.slice(0, 3));
      console.log('Sample links:', links.slice(0, 5));
      setGraphData({ nodes, links });
    } catch (error) {
      console.error('Failed to load graph data:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await api.sendMessage(inputValue);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        intent: response.intent,
        confidence: response.confidence,
        entities: response.entities || [],
        execution_time_ms: response.execution_time_ms,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Highlight related nodes in graph
      if (response.related_nodes && response.related_nodes.length > 0) {
        setHighlightedNodes(response.related_nodes);
      } else {
        setHighlightedNodes([]);
      }

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeClick = (nodeId) => {
    setInputValue(`Tell me about ${nodeId}`);
  };

  const handleReset = async () => {
    try {
      await api.resetConversation();
      setMessages([]);
      setHighlightedNodes([]);
    } catch (error) {
      console.error('Failed to reset conversation:', error);
    }
  };

  const getIntentColor = (intent) => {
    const colors = {
      exploration: 'bg-blue-500',
      dependency: 'bg-green-500',
      ownership: 'bg-purple-500',
      impact: 'bg-red-500',
      path: 'bg-yellow-500',
      team: 'bg-indigo-500',
      unknown: 'bg-gray-500'
    };
    return colors[intent] || colors.unknown;
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100">
      {/* Graph View */}
      {(viewMode === 'graph' || viewMode === 'split') && (
        <div className={`${viewMode === 'split' ? 'w-2/3' : 'w-full'} border-r border-gray-800`}>
          <NetworkGraphView
            graphData={graphData}
            highlightedNodes={highlightedNodes}
            onNodeClick={handleNodeClick}
          />
        </div>
      )}

      {/* Query Panel */}
      {(viewMode === 'chat' || viewMode === 'split') && (
        <div className={`${viewMode === 'split' ? 'w-1/3' : 'w-full'} flex flex-col`}>
          {/* Header */}
          <div className="bg-gray-800 border-b border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-lg font-semibold text-gray-100">Knowledge Graph Query</h1>
                <p className="text-xs text-gray-400 mt-1">Natural language interface</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode(viewMode === 'split' ? 'chat' : 'split')}
                  className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                >
                  {viewMode === 'split' ? 'Full Query' : 'Split View'}
                </button>
                <button
                  onClick={handleReset}
                  className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-sm">Ask me about your infrastructure:</p>
                <div className="mt-4 space-y-2 text-xs">
                  <p className="text-gray-400">"Show me all services"</p>
                  <p className="text-gray-400">"What depends on payment-service?"</p>
                  <p className="text-gray-400">"Who owns user-service?"</p>
                  <p className="text-gray-400">"Find path from api to database"</p>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.isError
                      ? 'bg-red-900 border border-red-700 text-red-100'
                      : 'bg-gray-800 border border-gray-700 text-gray-100'
                  }`}
                >
                  {message.role === 'assistant' && !message.isError && (
                    <div className="flex gap-2 mb-2 text-xs">
                      <span className={`px-2 py-0.5 rounded ${getIntentColor(message.intent)} text-white`}>
                        {message.intent}
                      </span>
                      {message.confidence > 0 && (
                        <span className="text-gray-400">
                          {Math.round(message.confidence * 100)}% confident
                        </span>
                      )}
                      {message.execution_time_ms > 0 && (
                        <span className="text-gray-400">
                          {message.execution_time_ms.toFixed(1)}ms
                        </span>
                      )}
                    </div>
                  )}
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  {message.entities && message.entities.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {message.entities.map((entity, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs"
                        >
                          {entity}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                    <span className="text-sm text-gray-400">Processing...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-700 p-4 bg-gray-800">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about your infrastructure..."
                className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-sm text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatProfessional;
