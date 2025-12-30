import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import GraphVisualization from './GraphVisualization';
import ChatMessage from './ChatMessage';
import FileUpload from './FileUpload';
import { 
  Send, 
  RotateCcw, 
  Eye, 
  Network, 
  Upload,
  Sparkles,
  Zap
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || '';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showGraph, setShowGraph] = useState(true);
  const [graphData, setGraphData] = useState(null);
  const [selectedNodes, setSelectedNodes] = useState([]);
  const [stats, setStats] = useState(null);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load initial graph data
  useEffect(() => {
    loadGraphData();
    // Add welcome message
    setMessages([{
      id: Date.now(),
      type: 'assistant',
      content: {
        message: "👋 Welcome to the Engineering Knowledge Graph! I'm your AI assistant for infrastructure insights.",
        suggestions: [
          "What breaks if order-service goes down?",
          "Who owns the payment-service?",
          "Show me dependencies of auth-service",
          "What teams work on this system?",
          "List all databases and their owners"
        ]
      },
      timestamp: new Date().toISOString()
    }]);
  }, []);

  const loadGraphData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/graph/data`);
      setGraphData(response.data);
      setStats({
        total_nodes: response.data.statistics?.total_nodes || Object.keys(response.data.nodes || {}).length,
        total_edges: response.data.statistics?.total_edges || Object.keys(response.data.edges || {}).length,
        teams: response.data.statistics?.node_types?.team || 0
      });
    } catch (error) {
      console.error('Failed to load graph data:', error);
    }
  };

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, {
        message: message
      });

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update graph visualization if we have relevant nodes
      if (response.data.related_nodes && response.data.related_nodes.length > 0) {
        setSelectedNodes(response.data.related_nodes);
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: {
          error: "Sorry, I encountered an error processing your request. Please try again.",
          type: "error"
        },
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([{
      id: Date.now(),
      type: 'assistant',
      content: {
        message: "👋 Welcome to the Engineering Knowledge Graph! I'm your AI assistant for infrastructure insights.",
        suggestions: [
          "What breaks if order-service goes down?",
          "Who owns the payment-service?",
          "Show me dependencies of auth-service",
          "What teams work on this system?",
          "List all databases and their owners"
        ]
      },
      timestamp: new Date().toISOString()
    }]);
    setSelectedNodes([]);
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const handleGraphNodeSelect = useCallback((nodeData) => {
    if (nodeData) {
      setSelectedNodes([nodeData.id]);
    } else {
      setSelectedNodes([]);
    }
  }, []);

  const handleFileUploadSuccess = async (result) => {
    // Reload graph data after successful upload
    await loadGraphData();
    
    // Add a success message to chat
    const successMessage = {
      id: Date.now(),
      type: 'assistant',
      content: {
        message: `✅ Successfully uploaded ${result.file_type} configuration!`,
        details: `Added ${result.nodes_added} nodes and ${result.edges_added} edges to the knowledge graph.`,
        type: 'success'
      },
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, successMessage]);
    setShowFileUpload(false);
  };

  return (
    <div className="workspace-shell flex h-screen">
      {/* Infrastructure Graph Panel */}
      {showGraph && (
        <div className="w-1/2 system-panel flex flex-col">
          {/* Graph Control Bar */}
          <div className="panel-toolbar">
            <div className="nav-section">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 bg-blue-600 rounded-lg shadow-sm">
                  <Network className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="section-heading">Service Architecture</h2>
                  <p className="section-meta">Live infrastructure mapping</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                {/* System Metrics */}
                <div className="flex items-center space-x-3 px-3 py-1.5 bg-gray-100 rounded-lg">
                  <div className="flex items-center space-x-1.5">
                    <div className="status-dot bg-blue-500"></div>
                    <span className="text-sm font-medium text-gray-700">{stats?.total_nodes || 0}</span>
                  </div>
                  <div className="w-px h-4 bg-gray-300"></div>
                  <div className="flex items-center space-x-1.5">
                    <div className="status-dot bg-emerald-500"></div>
                    <span className="text-sm font-medium text-gray-700">{stats?.total_edges || 0}</span>
                  </div>
                </div>
                
                {/* Control Actions */}
                <button
                  onClick={() => setShowFileUpload(true)}
                  className="action-button-secondary"
                  title="Import Configuration"
                >
                  <Upload className="w-4 h-4" />
                </button>
                
                <button
                  onClick={loadGraphData}
                  className="action-button-secondary"
                  title="Refresh Data"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          
          {/* Graph Visualization Area */}
          <div className="flex-1 relative bg-white">
            <GraphVisualization 
              graphData={graphData}
              onNodeSelect={handleGraphNodeSelect}
              selectedNodes={selectedNodes}
              className="w-full h-full"
            />
          </div>
        </div>
      )}

      {/* Intelligence Interface Panel */}
      <div className={`${showGraph ? 'w-1/2' : 'w-full'} system-panel flex flex-col`}>
        {/* Interface Header */}
        <div className="panel-toolbar">
          <div className="nav-section">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-gradient-to-r from-violet-600 to-purple-600 rounded-lg shadow-sm">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="section-heading">Infrastructure Intelligence</h1>
                <p className="section-meta">AI-powered service analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowFileUpload(true)}
                className="action-button-primary"
              >
                <Upload className="w-4 h-4 mr-2" />
                Import
              </button>
              
              {!showGraph && (
                <button
                  onClick={() => setShowGraph(true)}
                  className="action-button-secondary"
                  title="Show Architecture"
                >
                  <Eye className="w-4 h-4" />
                </button>
              )}
              
              <button
                onClick={clearChat}
                className="action-button-secondary"
                title="Clear Session"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Conversation Area */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5 bg-gradient-to-b from-slate-50/40 to-white">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <Zap className="w-8 h-8 text-white" />
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Infrastructure Intelligence Ready
              </h3>
              <p className="text-gray-600 mb-8 leading-relaxed">
                Ask about service dependencies, team ownership, impact analysis, or system architecture. 
                Get instant insights powered by AI.
              </p>
              
              {/* Intelligence Prompts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                {[
                  "Which team owns the payment service?",
                  "What happens if order-service fails?",
                  "Show me all database connections",
                  "What services does auth-service depend on?"
                ].map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(prompt)}
                    className="elevated-card p-4 text-left group"
                  >
                    <div className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors duration-150">
                      {prompt}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div key={message.id} className="enter-fade" style={{animationDelay: `${index * 0.05}s`}}>
                  <ChatMessage 
                    message={message} 
                    onSuggestionClick={handleSuggestionClick}
                  />
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center justify-center py-6">
                  <div className="flex items-center space-x-3 bg-white rounded-lg px-4 py-3 shadow-sm border border-gray-200">
                    <div className="loading-ring w-4 h-4"></div>
                    <span className="text-sm font-medium text-gray-700">Processing query...</span>
                  </div>
                </div>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Query Input Interface */}
        <div className="px-6 py-4 bg-white border-t border-gray-200">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your infrastructure..."
                className="system-input resize-none min-h-[44px] max-h-32"
                rows={1}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={() => sendMessage()}
              disabled={!inputMessage.trim() || isLoading}
              className="action-button-primary min-w-[44px] h-11"
            >
              {isLoading ? (
                <div className="loading-ring w-4 h-4"></div>
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* File Import Modal */}
      {showFileUpload && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 enter-fade">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 enter-scale">
            <FileUpload 
              onSuccess={handleFileUploadSuccess}
              onClose={() => setShowFileUpload(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
