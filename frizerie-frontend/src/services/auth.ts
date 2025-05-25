import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Define types for auth
export interface User {
  id: string;
  name: string;
  email: string;
  vip_level: number;
  loyalty_points: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
}

// Auth service
const authService = {
  // Register a new user
  register: async (userData: RegisterData): Promise<{ user: User; token: string }> => {
    const response = await axios.post(`${API_URL}/auth/register`, userData);
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
    }
    return response.data;
  },

  // Login user
  login: async (credentials: LoginCredentials): Promise<{ user: User; token: string }> => {
    const response = await axios.post(`${API_URL}/auth/login`, credentials);
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
    }
    return response.data;
  },

  // Logout user
  logout: (): void => {
    localStorage.removeItem('token');
  },

  // Get current user token
  getToken: (): string | null => {
    return localStorage.getItem('token');
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('token');
    return !!token;
  }
};

export default authService; 