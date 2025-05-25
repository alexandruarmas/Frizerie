import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import LoyaltyCard from './LoyaltyCard';
import usersService, { LoyaltyStatus } from '../services/users';

interface AppointmentSummary {
  today: number;
  upcoming: number;
  completed: number;
}

interface Barber {
  id: string;
  name: string;
  imageUrl: string;
  specialties: string[];
  availability: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [appointmentStats, setAppointmentStats] = useState<AppointmentSummary>({
    today: 0,
    upcoming: 0,
    completed: 0
  });
  const [popularBarbers, setPopularBarbers] = useState<Barber[]>([]);
  const [loyaltyStatus, setLoyaltyStatus] = useState<LoyaltyStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoyaltyLoading, setIsLoyaltyLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // In a real app, these would be API calls
        // Simulating API response with dummy data
        setTimeout(() => {
          setAppointmentStats({
            today: 1,
            upcoming: 3,
            completed: 8
          });
          
          setPopularBarbers([
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
          ]);
          
          setIsLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  // Fetch loyalty status
  useEffect(() => {
    const fetchLoyaltyStatus = async () => {
      setIsLoyaltyLoading(true);
      try {
        // In real app, this would call the API
        // For now, using mock data
        setTimeout(() => {
          const status = usersService.getMockLoyaltyStatus();
          setLoyaltyStatus(status);
          setIsLoyaltyLoading(false);
        }, 1200);
      } catch (error) {
        console.error('Error fetching loyalty status:', error);
        setIsLoyaltyLoading(false);
      }
    };

    fetchLoyaltyStatus();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-800">Welcome, {user?.name || 'Guest'}</h1>
        <p className="text-gray-600">Here's an overview of your appointments and services</p>
      </header>
      
      {isLoading ? (
        <div className="text-center py-8">Loading dashboard data...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6 bg-primary-50">
              <div className="flex flex-col items-center">
                <div className="text-4xl font-bold text-primary-600">{appointmentStats.today}</div>
                <div className="text-sm text-gray-600">Today's Appointments</div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 bg-primary-50">
              <div className="flex flex-col items-center">
                <div className="text-4xl font-bold text-primary-600">{appointmentStats.upcoming}</div>
                <div className="text-sm text-gray-600">Upcoming Appointments</div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 bg-primary-50">
              <div className="flex flex-col items-center">
                <div className="text-4xl font-bold text-primary-600">{appointmentStats.completed}</div>
                <div className="text-sm text-gray-600">Completed Appointments</div>
              </div>
            </div>
          </div>
          
          {/* Loyalty Status Card */}
          <div className="mb-8">
            {isLoyaltyLoading ? (
              <LoyaltyCard loyaltyStatus={{
                tier: 'BRONZE',
                points: 0,
                bookings_count: 0,
                perks: []
              }} isLoading={true} />
            ) : loyaltyStatus && (
              <LoyaltyCard loyaltyStatus={loyaltyStatus} />
            )}
          </div>
          
          <div className="mt-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800">Popular Barbers</h2>
              <button 
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                onClick={() => navigate('/bookings/calendar')}
              >
                Book Now
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {popularBarbers.map((barber) => (
                <div key={barber.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
                  <div className="flex flex-col items-center">
                    <img 
                      src={barber.imageUrl} 
                      alt={barber.name} 
                      className="w-24 h-24 rounded-full mb-3 object-cover"
                    />
                    <h3 className="text-lg font-medium">{barber.name}</h3>
                    <div className="text-sm text-gray-600 mt-1">
                      {barber.specialties.join(', ')}
                    </div>
                    <div className="text-xs text-green-600 mt-2">
                      {barber.availability}
                    </div>
                    <button 
                      className="mt-3 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm"
                      onClick={() => navigate(`/bookings/calendar?barber=${barber.id}`)}
                    >
                      Book
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard; 