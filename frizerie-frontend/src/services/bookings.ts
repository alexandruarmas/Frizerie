import axios from 'axios';
import authService from './auth';
import api from './api';  // Import the configured API instance

// Use the same API URL from api.ts
const API_URL = import.meta.env?.VITE_API_URL || 'https://frizerie.onrender.com';
const API_PREFIX = '/api/v1';

export interface Booking {
  id: string;
  user_id: string;
  stylist_id: string;
  service: string;
  date: string;
  time: string;
  status: 'scheduled' | 'completed' | 'cancelled';
  notes?: string;
  created_at: string;
  barber_name?: string;
  service_name?: string;
  price?: number;
}

export interface BookingRequest {
  barber_id: string;
  service_id: string;
  date: string;
  time: string;
  notes?: string;
}

export interface TimeSlot {
  time: string;
  available: boolean;
  isVipOnly?: boolean;
}

export interface CheckAvailabilityRequest {
  date: string;
  barber_id?: string;
  service_id?: string;
}

const bookingsService = {
  // Get all bookings
  getBookings: async (): Promise<Booking[]> => {
    const response = await api.get(`${API_PREFIX}/bookings`);
    return response.data as Booking[];
  },

  // Create a new booking
  createBooking: async (bookingData: BookingRequest): Promise<Booking> => {
    const response = await api.post(`${API_PREFIX}/bookings`, bookingData);
    return response.data as Booking;
  },

  // Cancel a booking
  cancelBooking: async (bookingId: string): Promise<Booking> => {
    const response = await api.post(`${API_PREFIX}/bookings/${bookingId}/cancel`, {});
    return response.data as Booking;
  },

  // Check availability for a specific date/barber/service
  checkAvailability: async (params: CheckAvailabilityRequest): Promise<TimeSlot[]> => {
    const response = await api.post(`${API_PREFIX}/bookings/check-availability`, params);
    return response.data as TimeSlot[];
  },
  
  // Mock data for development purposes
  getMockBookings: (): Booking[] => {
    return [
      {
        id: '1',
        user_id: '123',
        stylist_id: '1',
        service: 'haircut',
        date: '2025-06-15',
        time: '10:00 AM',
        status: 'scheduled',
        created_at: '2025-06-01T10:00:00Z',
        barber_name: 'Alex Barbulescu',
        service_name: 'Haircut & Styling',
        price: 35
      },
      {
        id: '2',
        user_id: '123',
        stylist_id: '2',
        service: 'beard_trim',
        date: '2025-06-20',
        time: '2:30 PM',
        status: 'scheduled',
        created_at: '2025-06-02T14:30:00Z',
        barber_name: 'Maria Stilista',
        service_name: 'Beard Trim',
        price: 20
      },
      {
        id: '3',
        user_id: '123',
        stylist_id: '3',
        service: 'full_service',
        date: '2025-05-10',
        time: '11:00 AM',
        status: 'completed',
        created_at: '2025-05-01T11:00:00Z',
        barber_name: 'Ion Frizeru',
        service_name: 'Full Service (Cut, Beard, Styling)',
        price: 55
      },
      {
        id: '4',
        user_id: '123',
        stylist_id: '4',
        service: 'kids_haircut',
        date: '2025-05-05',
        time: '4:00 PM',
        status: 'cancelled',
        created_at: '2025-04-29T16:00:00Z',
        barber_name: 'Ana Coafeza',
        service_name: 'Kids Haircut',
        price: 25
      }
    ];
  },
  
  // Get details of stylists/barbers
  getMockStylists: () => {
    return [
      {
        id: '1',
        name: 'Alex Barbulescu',
        imageUrl: 'https://randomuser.me/api/portraits/men/32.jpg',
        specialties: ['Classic Cut', 'Beard Trim'],
        availability: 'Available Today'
      },
      {
        id: '2',
        name: 'Maria Stilista',
        imageUrl: 'https://randomuser.me/api/portraits/women/44.jpg',
        specialties: ['Modern Styles', 'Color'],
        availability: 'Next Available: Tomorrow'
      },
      {
        id: '3',
        name: 'Ion Frizeru',
        imageUrl: 'https://randomuser.me/api/portraits/men/22.jpg',
        specialties: ['Kids Cut', 'Fades'],
        availability: 'Available Today'
      },
      {
        id: '4',
        name: 'Ana Coafeza',
        imageUrl: 'https://randomuser.me/api/portraits/women/29.jpg',
        specialties: ['Styling', 'Extensions'],
        availability: 'Next Available: Friday'
      }
    ];
  },
  
  // Get services
  getMockServices: () => {
    return [
      {
        id: '1',
        name: 'Haircut & Styling',
        duration: 45,
        price: 35
      },
      {
        id: '2',
        name: 'Beard Trim',
        duration: 20,
        price: 20
      },
      {
        id: '3',
        name: 'Full Service (Cut, Beard, Styling)',
        duration: 60,
        price: 55
      },
      {
        id: '4',
        name: 'Kids Haircut',
        duration: 30,
        price: 25
      }
    ];
  }
};

export default bookingsService; 