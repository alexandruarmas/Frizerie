import axios from 'axios';
import authService from './auth';
const API_URL = 'https://frizerie.onrender.com/api/v1';
import api from './api';  // Import the configured API instance

export interface LoyaltyReward {
  id: number;
  name: string;
  description?: string;
  points_cost: number;
  reward_type: string;
  reward_value: number;
  is_active: boolean;
  valid_from?: string;
  valid_until?: string;
  min_tier_required?: string;
  created_at: string;
  updated_at: string;
}

export interface LoyaltyRedemption {
  id: number;
  user_id: number;
  reward_id: number;
  points_spent: number;
  redeemed_at: string;
  status: string;
  booking_id?: number;
  notes?: string;
  reward?: LoyaltyReward;
}

export interface LoyaltyPointsHistory {
  id: number;
  user_id: number;
  points_change: number;
  reason: string;
  reference_id?: number;
  reference_type?: string;
  created_at: string;
}

export interface ReferralProgram {
  id: number;
  referrer_id: number;
  referred_id: number;
  points_awarded: number;
  status: string;
  created_at: string;
  completed_at?: string;
}

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
  points_history: LoyaltyPointsHistory[];
  available_rewards: LoyaltyReward[];
  recent_redemptions: LoyaltyRedemption[];
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
    const response = await api.get(`/users/me/loyalty-status`);
    return response.data as LoyaltyStatus;
  },

  // Get available rewards
  getAvailableRewards: async (): Promise<LoyaltyReward[]> => {
    const response = await api.get(`/users/me/loyalty/rewards`);
    return response.data as LoyaltyReward[];
  },

  // Redeem a reward
  redeemReward: async (rewardId: number, bookingId?: number): Promise<LoyaltyRedemption> => {
    const response = await api.post(`/users/me/loyalty/rewards/${rewardId}/redeem`, {
      booking_id: bookingId
    });
    return response.data as LoyaltyRedemption;
  },

  // Get points history
  getPointsHistory: async (skip: number = 0, limit: number = 10): Promise<LoyaltyPointsHistory[]> => {
    const response = await api.get(`/users/me/loyalty/points-history`, {
      params: { skip, limit }
    });
    return response.data as LoyaltyPointsHistory[];
  },

  // Create a referral
  createReferral: async (referredEmail: string): Promise<ReferralProgram> => {
    const response = await api.post(`/users/me/loyalty/refer`, {
      referred_email: referredEmail
    });
    return response.data as ReferralProgram;
  },

  // Complete a referral
  completeReferral: async (referralId: number): Promise<ReferralProgram> => {
    const response = await api.post(`/users/me/loyalty/referrals/${referralId}/complete`);
    return response.data as ReferralProgram;
  },

  // Admin methods
  createReward: async (rewardData: Partial<LoyaltyReward>): Promise<LoyaltyReward> => {
    const response = await api.post(`/users/admin/loyalty/rewards`, rewardData);
    return response.data as LoyaltyReward;
  },

  updateReward: async (rewardId: number, rewardData: Partial<LoyaltyReward>): Promise<LoyaltyReward> => {
    const response = await api.put(`/users/admin/loyalty/rewards/${rewardId}`, rewardData);
    return response.data as LoyaltyReward;
  },

  getAllRedemptions: async (skip: number = 0, limit: number = 100, status?: string): Promise<LoyaltyRedemption[]> => {
    const response = await api.get(`/users/admin/loyalty/redemptions`, {
      params: { skip, limit, status }
    });
    return response.data as LoyaltyRedemption[];
  },

  updateRedemptionStatus: async (redemptionId: number, status: string): Promise<LoyaltyRedemption> => {
    const response = await api.put(`/users/admin/loyalty/redemptions/${redemptionId}`, { status });
    return response.data as LoyaltyRedemption;
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
      ],
      points_history: [],
      available_rewards: [],
      recent_redemptions: []
    };
  }
};

export default usersService; 