import axios from 'axios';
import authService from './auth';
import api from './api';  // Import the configured API instance

// Use the correct backend URL
const API_URL = import.meta.env?.VITE_API_URL || 'https://frizerie.onrender.com';

export interface LoyaltyStatus {
  tier: 'BRONZE' | 'SILVER' | 'GOLD' | 'DIAMOND';
  points: number;
  bookings_count: number;
  next_tier?: {
    name: 'SILVER' | 'GOLD' | 'DIAMOND';
    points_needed: number;
    bookings_needed: number;
  };
  perks: string[];
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone?: string;
  vip_level: string;
  loyalty_points: number;
  created_at: string;
}

const usersService = {
  // Get user profile
  getProfile: async (): Promise<UserProfile> => {
    const response = await api.get(`/users/me`);
    return response.data as UserProfile;
  },

  // Update user profile
  updateProfile: async (userData: Partial<UserProfile>): Promise<UserProfile> => {
    const response = await api.put(`/users/me`, userData);
    return response.data as UserProfile;
  },

  // Get loyalty status
  getLoyaltyStatus: async (): Promise<LoyaltyStatus> => {
    const response = await api.get(`/users/loyalty-status`);
    return response.data as LoyaltyStatus;
  },

  // For demo/development purposes: simulate loyalty status
  getMockLoyaltyStatus: (): LoyaltyStatus => {
    // This is mock data for development before connecting to real backend
    return {
      tier: 'SILVER',
      points: 350,
      bookings_count: 7,
      next_tier: {
        name: 'GOLD',
        points_needed: 150,
        bookings_needed: 3
      },
      perks: [
        'Access to standard appointment slots',
        'Priority booking (24h in advance)',
        '5% discount on products'
      ]
    };
  }
};

export default usersService; 