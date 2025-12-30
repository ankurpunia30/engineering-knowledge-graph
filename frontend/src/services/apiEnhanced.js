import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service methods
const apiService = {
  // Enhanced chat with Natural Language Interface
  async sendMessage(message) {
    try {
      const response = await api.post('/api/chat', { message });
      return response.data;
    } catch (error) {
      console.error('Chat API error:', error);
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  // Legacy chat endpoint for backward compatibility
  async sendLegacyMessage(message) {
    try {
      const response = await api.post('/api/chat/legacy', { message });
      return response.data;
    } catch (error) {
      console.error('Legacy chat API error:', error);
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  // Reset conversation context
  async resetConversation() {
    try {
      const response = await api.post('/api/chat/reset');
      return response.data;
    } catch (error) {
      console.error('Reset conversation error:', error);
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  // Part 3 Query Engine API methods
  async getNode(nodeId) {
    try {
      const response = await api.get(`/api/query/node/${encodeURIComponent(nodeId)}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  async getNodes(filters = {}) {
    try {
      const params = new URLSearchParams();
      
      if (filters.node_type) params.append('node_type', filters.node_type);
      if (filters.team) params.append('team', filters.team);
      if (filters.environment) params.append('environment', filters.environment);
      if (filters.limit) params.append('limit', filters.limit.toString());
      
      const response = await api.get(`/api/query/nodes?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  async getDownstream(nodeId, maxDepth = 10, edgeTypes = null) {
    try {
      const params = new URLSearchParams();
      params.append('max_depth', maxDepth.toString());
      if (edgeTypes) params.append('edge_types', edgeTypes.join(','));
      
      const response = await api.get(`/api/query/downstream/${encodeURIComponent(nodeId)}?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  async getUpstream(nodeId, maxDepth = 10, edgeTypes = null) {
    try {
      const params = new URLSearchParams();
      params.append('max_depth', maxDepth.toString());
      if (edgeTypes) params.append('edge_types', edgeTypes.join(','));
      
      const response = await api.get(`/api/query/upstream/${encodeURIComponent(nodeId)}?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  async getBlastRadius(nodeId, maxDepth = 5) {
    try {
      const params = new URLSearchParams();
      params.append('max_depth', maxDepth.toString());
      
      const response = await api.get(`/api/query/blast-radius/${encodeURIComponent(nodeId)}?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  async getPath(fromId, toId, maxDepth = 10) {
    try {
      const params = new URLSearchParams();
      params.append('max_depth', maxDepth.toString());
      
      const response = await api.get(`/api/query/path/${encodeURIComponent(fromId)}/${encodeURIComponent(toId)}?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  async getOwner(nodeId) {
    try {
      const response = await api.get(`/api/query/owner/${encodeURIComponent(nodeId)}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  // Graph data methods
  async getGraphData() {
    try {
      const response = await api.get('/api/graph/data');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  async getGraphStats() {
    try {
      const response = await api.get('/api/graph/stats');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  // File upload
  async uploadFile(file, fileType) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('file_type', fileType);

      const response = await api.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  },
};

export default apiService;
