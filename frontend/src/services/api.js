/**
 * API Service for AI Blog Generator.
 * Wraps axios with base configuration and error handling.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    if (!config.headers['X-Request-ID']) {
      config.headers['X-Request-ID'] = crypto.randomUUID();
    }
    const token = import.meta.env.VITE_API_TOKEN;
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.error?.message ||
                         error.response?.data?.detail ||
                         error.message ||
                         'An unexpected error occurred';

    return Promise.reject({
      message: errorMessage,
      code: error.response?.data?.error?.code || 'API_ERROR',
      status: error.response?.status,
      details: error.response?.data?.error?.details || {},
    });
  }
);

// API endpoints
export const blogApi = {
  // Generate a new blog post
  generate: (data, params) => api.post('/generate/', data, { params }),

  // Poll generation job status
  generationStatus: (jobId) => api.get(`/generation-status/${jobId}/`),

  // List all blog posts
  list: (params) => api.get('/posts/', { params }),

  // Get a single blog post
  get: (id) => api.get(`/posts/${id}/`),

  // Delete a blog post
  delete: (id) => api.delete(`/posts/${id}/`),
};

export const engagementApi = {
  // Record an engagement action
  record: (data) => api.post('/engage/', data),

  // Get engagement metrics for a post
  getMetrics: (blogId, sessionId) =>
    api.get(`/posts/${blogId}/engagement/`, {
      params: sessionId ? { session_id: sessionId } : {},
    }),
};

export const personaApi = {
  // List all personas
  list: () => api.get('/personas/'),

  // Get a single persona
  get: (slug) => api.get(`/personas/${slug}/`),
};

export const analyticsApi = {
  // Get overall analytics
  get: (params) => api.get('/analytics/', { params }),
};

export default api;
