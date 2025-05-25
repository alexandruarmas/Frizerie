import axios from 'axios';

// Get API URL from environment variable or use deployed URL as fallback
// Use the correct backend domain
const API_URL = import.meta.env?.VITE_API_URL || 'https://frizerie-backend.onrender.com';

// Create base API instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token in requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle token expiration (401 Unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, { 
            refresh_token: refreshToken 
          });
          
          // Type assertion for response.data
          const data = response.data as { access_token: string };
          const { access_token } = data;
          localStorage.setItem('auth_token', access_token);
          
          // Retry the original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Function to configure the API URL
export const configureApiUrl = (baseUrl: string) => {
  api.defaults.baseURL = baseUrl;
};

export default api; 