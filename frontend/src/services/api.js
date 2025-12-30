import axios from 'axios';

// Use relative URL for production (same domain as frontend)
// Fall back to localhost for local development
const getApiBaseUrl = () => {
  // If running on the same domain (production), use relative path
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return ''; // Empty string means relative to current domain
  }
  // Local development
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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
