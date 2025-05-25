import axios from 'axios';
import authService from './auth';

const API_URL = 'http://localhost:8000';

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
    const token = authService.getToken();
    const response = await axios.get(`${API_URL}/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  // Update user profile
  updateProfile: async (userData: Partial<UserProfile>): Promise<UserProfile> => {
    const token = authService.getToken();
    const response = await axios.put(`${API_URL}/users/me`, userData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  // Get loyalty status
  getLoyaltyStatus: async (): Promise<LoyaltyStatus> => {
    const token = authService.getToken();
    const response = await axios.get(`${API_URL}/users/loyalty-status`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
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