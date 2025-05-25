import axios from 'axios';
import api from './api';  // Import the configured API instance

// Use the same API URL as in api.ts
const API_URL = import.meta.env?.VITE_API_URL || 'https://frizerie.onrender.com/api/v1';

// Define types for auth
export interface User {
  id: string;
  name: string;
  email: string;
  vip_level: number;
  loyalty_points: number;
}

export interface AuthResponse {
  user: User;
  token: string;
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
  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const response = await api.post(`/auth/register`, userData);
    const data = response.data as AuthResponse;
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
    }
    return data;
  },

  // Login user
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post(`/auth/login`, credentials);
    const data = response.data as AuthResponse;
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
    }
    return data;
  },

  // Logout user
  logout: (): void => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
  },

  // Get current user token
  getToken: (): string | null => {
    return localStorage.getItem('auth_token');
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('auth_token');
    return !!token;
  }
};

export default authService; 