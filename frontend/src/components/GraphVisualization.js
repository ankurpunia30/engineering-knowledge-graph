import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
import { Maximize2, Minimize2, Search, Filter, Zap, RotateCcw } from 'lucide-react';

const createNodeTooltip = (node) => {
  if (!node) return '';
  
  let tooltip = `<div style="font-family: Arial, sans-serif; font-size: 12px; max-width: 300px;">`;
  tooltip += `<div style="font-weight: bold; color: #1e40af; margin-bottom: 8px;">${node.type.toUpperCase()}: ${node.name}</div>`;
  
  if (node.properties) {
    // Add key properties first
    const keyProps = ['team', 'oncall', 'port', 'namespace', 'image', 'lead', 'slack_channel'];
    keyProps.forEach(key => {
      if (node.properties[key]) {
        const displayKey = key.replace(/_/g, ' ').toUpperCase();
        tooltip += `<div style="margin: 2px 0;"><span style="font-weight: bold; color: #374151;">${displayKey}:</span> ${node.properties[key]}</div>`;
      }
    });
    
    // Add environment variables if they exist
    if (node.properties.environment && Object.keys(node.properties.environment).length > 0) {
      tooltip += `<div style="margin-top: 8px; font-weight: bold; color: #374151;">ENVIRONMENT:</div>`;
      const envVars = Object.entries(node.properties.environment).slice(0, 3); // Show first 3
      envVars.forEach(([key, value]) => {
        const shortValue = String(value).length > 30 ? String(value).substring(0, 30) + '...' : value;
        tooltip += `<div style="margin: 1px 0; font-size: 11px; color: #6b7280;">${key}: ${shortValue}</div>`;
      });
      if (Object.keys(node.properties.environment).length > 3) {
        tooltip += `<div style="font-size: 11px; color: #6b7280;">... and ${Object.keys(node.properties.environment).length - 3} more</div>`;
      }
    }
  }
  
  tooltip += `</div>`;
  return tooltip;
};

const GraphVisualization = ({ graphData, onNodeSelect, selectedNodes, className }) => {
  const networkContainer = useRef(null);
  const networkInstance = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedNodeData, setSelectedNodeData] = useState(null);

  // Enhanced ResizeObserver error suppression
  useEffect(() => {
    const handleError = (e) => {
      if (e.message && (
        e.message.includes('ResizeObserver loop completed with undelivered notifications') ||
        e.message.includes('ResizeObserver loop limit exceeded') ||
        e.message.includes('ResizeObserver') ||
        e.error?.message?.includes('ResizeObserver')
      )) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
    };

    const handleUnhandledRejection = (e) => {
      if (e.reason?.message?.includes('ResizeObserver')) {
        e.preventDefault();
        return false;
      }
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    
    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  // Additional global error suppression for ResizeObserver
  useEffect(() => {
    const originalConsoleError = console.error;
    console.error = (...args) => {
      if (args[0] && typeof args[0] === 'string' && args[0].includes('ResizeObserver')) {
        return; // Suppress ResizeObserver console errors
      }
      originalConsoleError.apply(console, args);
    };

    return () => {
      console.error = originalConsoleError;
    };
  }, []);

  useEffect(() => {
    if (!graphData || !networkContainer.current) return;

    // Convert nodes and edges objects to arrays
    const nodesArray = graphData.nodes ? Object.values(graphData.nodes) : [];
    const edgesArray = graphData.edges ? Object.values(graphData.edges) : [];

    // Process nodes and edges for vis-network
    const nodes = new DataSet(
      nodesArray.map(node => {
        // Create detailed tooltip for hover
        const tooltip = createNodeTooltip(node);
        
        return {
          id: node.id,
          label: node.name,
          title: tooltip,
          color: selectedNodes && selectedNodes.includes(node.id) 
            ? { background: '#fbbf24', border: '#f59e0b' } 
            : getNodeColor(node.type),
          shape: getNodeShape(node.type),
          size: selectedNodes && selectedNodes.includes(node.id) 
            ? getNodeSize(node.type) + 5 
            : getNodeSize(node.type),
          font: { size: 12, color: '#333' },
          chosen: true
        };
      })
    );

    const edges = new DataSet(
      edgesArray.map(edge => ({
        id: edge.id,
        from: edge.source,
        to: edge.target,
        label: edge.type,
        color: getEdgeColor(edge.type),
        arrows: 'to',
        width: 2,
        font: { size: 10, align: 'middle' }
      }))
    );

    // Apply filters
    let filteredNodes = nodes.get();
    if (filterType !== 'all') {
      filteredNodes = filteredNodes.filter(node => 
        nodesArray.find(n => n.id === node.id)?.type === filterType
      );
    }
    
    if (searchQuery) {
      filteredNodes = filteredNodes.filter(node => 
        node.label.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = edges.get().filter(edge => 
      filteredNodeIds.has(edge.from) && filteredNodeIds.has(edge.to)
    );

    const data = {
      nodes: new DataSet(filteredNodes),
      edges: new DataSet(filteredEdges)
    };

    const options = {
      layout: {
        improvedLayout: true,
        hierarchical: {
          enabled: false,
          direction: 'UD',
          sortMethod: 'hubsize',
          levelSeparation: 150,
          nodeSpacing: 200
        }
      },
      physics: {
        enabled: true,
        stabilization: { 
          iterations: 50, // Reduced from 100 to stabilize faster
          updateInterval: 5,
          fit: true
        },
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 95,
          springConstant: 0.04,
          damping: 0.09,
          avoidOverlap: 0.1
        },
        adaptiveTimestep: true, // Help prevent ResizeObserver issues
        timestep: 0.5,
        maxVelocity: 50
      },
      nodes: {
        borderWidth: 2,
        shadow: true,
        chosen: {
          node: (values, id, selected, hovering) => {
            values.shadow = true;
            values.shadowSize = 10;
            values.shadowColor = 'rgba(0,0,0,0.3)';
          }
        }
      },
      edges: {
        shadow: true,
        smooth: {
          enabled: true,
          type: 'continuous'
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 300,
        hideEdgesOnDrag: true,
        hideNodesOnDrag: true
      }
    };

    // Destroy existing network
    if (networkInstance.current) {
      try {
        networkInstance.current.destroy();
      } catch (err) {
        console.warn('Error destroying network:', err);
      }
    }

    // Create new network with error handling
    try {
      networkInstance.current = new Network(networkContainer.current, data, options);

      // Add event listeners
      networkInstance.current.on('selectNode', (event) => {
        if (event.nodes.length > 0) {
          const nodeId = event.nodes[0];
          const nodeData = nodesArray.find(n => n.id === nodeId);
          if (nodeData) {
            setSelectedNodeData(nodeData);
            onNodeSelect?.(nodeData);
          }
        }
      });

      networkInstance.current.on('deselectNode', () => {
        setSelectedNodeData(null);
        onNodeSelect?.(null);
      });
    } catch (err) {
      console.error('Error creating network:', err);
    }

    // Cleanup
    return () => {
      if (networkInstance.current) {
        networkInstance.current.destroy();
        networkInstance.current = null;
      }
    };
  }, [graphData, searchQuery, filterType, selectedNodes, onNodeSelect]);

  const getNodeColor = (type) => {
    const colors = {
      service: '#4f46e5',
      database: '#059669',
      cache: '#dc2626',
      team: '#7c3aed',
      deployment: '#ea580c',
      k8s_service: '#0891b2'
    };
    return colors[type] || '#6b7280';
  };

  const getNodeShape = (type) => {
    const shapes = {
      service: 'dot',
      database: 'database',
      cache: 'diamond',
      team: 'star',
      deployment: 'box',
      k8s_service: 'triangle'
    };
    return shapes[type] || 'dot';
  };

  const getNodeSize = (type) => {
    const sizes = {
      service: 20,
      database: 25,
      cache: 18,
      team: 30,
      deployment: 22,
      k8s_service: 20
    };
    return sizes[type] || 20;
  };

  const getEdgeColor = (type) => {
    const colors = {
      calls: '#3b82f6',
      depends_on: '#ef4444',
      reads_from: '#10b981',
      writes_to: '#f59e0b',
      owns: '#8b5cf6',
      uses: '#06b6d4',
      deployed_as: '#ec4899'
    };
    return colors[type] || '#6b7280';
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const fitNetwork = () => {
    if (networkInstance.current) {
      networkInstance.current.fit();
    }
  };

  const nodeTypes = [...new Set(graphData?.nodes ? Object.values(graphData.nodes).map(n => n.type) : [])];

  return (
    <div className={`${className} ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : 'flex flex-col h-full'}`}>
      {/* Controls */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-professional transition-professional"
            />
          </div>
          
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="pl-10 pr-8 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-professional transition-professional"
            >
              <option value="all">All Types</option>
              {nodeTypes.map(type => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fitNetwork}
            className="px-4 py-2 text-sm bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 rounded-lg transition-professional shadow-professional hover:shadow-professional-lg flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset View</span>
          </button>
          <button
            onClick={toggleFullscreen}
            className="p-2 text-slate-600 hover:text-slate-800 bg-white hover:bg-slate-50 border border-slate-300 rounded-lg transition-professional shadow-professional hover:shadow-professional-lg"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Graph Container */}
      <div className="relative flex-1">
        <div 
          ref={networkContainer} 
          className="w-full h-full bg-gradient-to-br from-slate-50 to-blue-50"
          style={{ minHeight: isFullscreen ? '90vh' : '500px' }}
        />
        
        {/* Legend */}
        <div className="absolute top-4 right-4 bg-white p-4 rounded-xl shadow-professional-lg border border-slate-200">
          <div className="flex items-center mb-3">
            <Zap className="w-4 h-4 text-slate-600 mr-2" />
            <h4 className="font-semibold text-sm text-slate-900">Node Types</h4>
          </div>
          <div className="space-y-2">
            {nodeTypes.map(type => (
              <div key={type} className="flex items-center space-x-3 text-xs">
                <div 
                  className="w-3 h-3 rounded-full shadow-professional"
                  style={{ backgroundColor: getNodeColor(type) }}
                />
                <span className="capitalize text-slate-700 font-medium">{type.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Stats overlay */}
        <div className="absolute bottom-4 left-4 bg-white p-3 rounded-xl shadow-professional-lg border border-slate-200">
          <div className="text-xs text-slate-600">
            <div>Nodes: <span className="font-semibold text-slate-900">{graphData?.nodes ? Object.keys(graphData.nodes).length : 0}</span></div>
            <div>Edges: <span className="font-semibold text-slate-900">{graphData?.edges ? Object.keys(graphData.edges).length : 0}</span></div>
          </div>
        </div>
      </div>

      {/* Selected Node Info */}
      {selectedNodeData && (
        <div className="border-t border-slate-200 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
          {/* Header */}
          <div className="p-4 border-b border-blue-200 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{selectedNodeData.name || 'Unknown'}</h3>
                <p className="text-blue-100 capitalize">{(selectedNodeData.type || 'Unknown').replace('_', ' ')}</p>
              </div>
              <div className="bg-white/20 px-3 py-1 rounded-full text-sm font-medium">
                {selectedNodeData.id}
              </div>
            </div>
          </div>

          {selectedNodeData.properties && Object.keys(selectedNodeData.properties).length > 0 && (
            <div className="p-4 space-y-4">
              {/* Key Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {['team', 'oncall', 'lead', 'port', 'namespace', 'image', 'slack_channel', 'pagerduty_schedule'].map(key => {
                  if (!selectedNodeData.properties[key]) return null;
                  return (
                    <div key={key} className="bg-white rounded-lg p-3 border-l-4 border-blue-400 shadow-sm">
                      <div className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-1">
                        {key.replace(/_/g, ' ')}
                      </div>
                      <div className="text-sm font-medium text-gray-900">
                        {String(selectedNodeData.properties[key])}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Environment Variables */}
              {selectedNodeData.properties.environment && Object.keys(selectedNodeData.properties.environment).length > 0 && (
                <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Environment Variables
                  </h4>
                  <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
                    {Object.entries(selectedNodeData.properties.environment).map(([key, value]) => (
                      <div key={key} className="bg-gray-50 rounded-md p-2 border">
                        <div className="text-xs font-mono text-blue-600 font-semibold">{key}</div>
                        <div className="text-xs font-mono text-gray-800 break-all mt-1">
                          {String(value)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Services Owned (for teams) */}
              {selectedNodeData.properties.services_owned && selectedNodeData.properties.services_owned.length > 0 && (
                <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    Services Owned
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedNodeData.properties.services_owned.map(service => (
                      <span key={service} className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
                        {service}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Labels (for k8s) */}
              {selectedNodeData.properties.labels && typeof selectedNodeData.properties.labels === 'object' && (
                <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                    Labels
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedNodeData.properties.labels).map(([key, value]) => (
                      <span key={key} className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-md text-xs font-mono">
                        {key}: {value}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Resources (for k8s) */}
              {selectedNodeData.properties.resources && (
                <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                    <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                    Resource Limits
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedNodeData.properties.resources.requests && (
                      <div>
                        <div className="text-xs font-semibold text-gray-600 mb-1">REQUESTS</div>
                        {Object.entries(selectedNodeData.properties.resources.requests).map(([key, value]) => (
                          <div key={key} className="text-xs font-mono text-gray-800">
                            {key}: {value}
                          </div>
                        ))}
                      </div>
                    )}
                    {selectedNodeData.properties.resources.limits && (
                      <div>
                        <div className="text-xs font-semibold text-gray-600 mb-1">LIMITS</div>
                        {Object.entries(selectedNodeData.properties.resources.limits).map(([key, value]) => (
                          <div key={key} className="text-xs font-mono text-gray-800">
                            {key}: {value}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Other Properties */}
              <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                  <div className="w-2 h-2 bg-gray-500 rounded-full mr-2"></div>
                  Additional Properties
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(selectedNodeData.properties).map(([key, value]) => {
                    // Skip properties we've already displayed above
                    if (['team', 'oncall', 'lead', 'port', 'namespace', 'image', 'slack_channel', 'pagerduty_schedule', 'environment', 'services_owned', 'labels', 'resources'].includes(key)) return null;
                    if (value === null || value === undefined) return null;
                    
                    return (
                      <div key={key} className="bg-gray-50 rounded-md p-2 border">
                        <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                          {key.replace(/_/g, ' ')}
                        </div>
                        <div className="text-sm font-mono text-gray-900 break-all">
                          {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GraphVisualization;
