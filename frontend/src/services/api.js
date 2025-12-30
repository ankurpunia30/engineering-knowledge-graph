import axios from 'axios';

// Determine API base URL at runtime (not build time!)
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  // Local development
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  // Production - use same domain as frontend (empty string for relative URLs)
  return window.location.origin;
};

// Create axios instance
export const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to set baseURL at runtime
api.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl();
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const chatService = {
  async sendMessage(message) {
    try {
      const response = await api.post('/api/chat', { message });
      return response.data;
    } catch (error) {
      console.error('Chat service error:', error);
      throw new Error('Failed to send message');
    }
  },

  async getGraphData() {
    try {
      const response = await api.get('/api/graph/data');
      return response.data;
    } catch (error) {
      console.error('Graph data error:', error);
      throw new Error('Failed to fetch graph data');
    }
  },

  async getGraphStats() {
    try {
      const response = await api.get('/api/graph/stats');
      return response.data;
    } catch (error) {
      console.error('Graph stats error:', error);
      throw new Error('Failed to fetch graph statistics');
    }
  },

  async searchNodes(query) {
    try {
      const response = await api.get(`/api/graph/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Search error:', error);
      throw new Error('Failed to search nodes');
    }
  }
};
