import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// Mock data for demo
const mockStats = {
  totalUsers: 157,
  totalBookings: 428,
  totalStylists: 8,
  activeBookingsToday: 24,
  revenue: 8475.50,
  newUsersThisWeek: 15,
  upcomingAppointments: 85,
  avgRating: 4.7,
};

// Mock data for recent bookings
const mockRecentBookings = [
  { id: 'bk001', userName: 'John Smith', service: 'Classic Cut', date: '2023-08-15T10:30:00', stylist: 'Maria Garcia', status: 'completed' },
  { id: 'bk002', userName: 'Alice Johnson', service: 'Hair Color', date: '2023-08-15T13:00:00', stylist: 'David Kim', status: 'completed' },
  { id: 'bk003', userName: 'Michael Brown', service: 'Beard Trim', date: '2023-08-15T15:30:00', stylist: 'Sarah Lee', status: 'in-progress' },
  { id: 'bk004', userName: 'Emma Wilson', service: 'Full Service', date: '2023-08-15T16:45:00', stylist: 'James Taylor', status: 'upcoming' },
  { id: 'bk005', userName: 'Robert Davis', service: 'Classic Cut', date: '2023-08-15T17:30:00', stylist: 'Maria Garcia', status: 'upcoming' },
];

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState(mockStats);
  const [recentBookings, setRecentBookings] = useState(mockRecentBookings);
  const [isLoading, setIsLoading] = useState(false);
  
  // Fetch real data from API in production
  useEffect(() => {
    // In a real implementation, this would fetch from the backend API
    // For example:
    // async function fetchData() {
    //   setIsLoading(true);
    //   try {
    //     const statsResponse = await api.get('/admin/stats');
    //     setStats(statsResponse.data);
    //     
    //     const bookingsResponse = await api.get('/admin/recent-bookings');
    //     setRecentBookings(bookingsResponse.data);
    //   } catch (error) {
    //     console.error('Error fetching admin data:', error);
    //   } finally {
    //     setIsLoading(false);
    //   }
    // }
    // 
    // fetchData();
    
    // Simulate loading for demo
    setIsLoading(true);
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Format date for display
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Get status badge class
  const getStatusBadge = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800';
      case 'upcoming':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-gray-500 text-sm">Total Users</div>
              <div className="text-2xl font-bold mt-1">{stats.totalUsers}</div>
              <div className="text-xs text-green-600 mt-2">
                +{stats.newUsersThisWeek} this week
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-gray-500 text-sm">Total Bookings</div>
              <div className="text-2xl font-bold mt-1">{stats.totalBookings}</div>
              <div className="text-xs text-gray-500 mt-2">
                {stats.upcomingAppointments} upcoming
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-gray-500 text-sm">Revenue</div>
              <div className="text-2xl font-bold mt-1">${stats.revenue.toLocaleString()}</div>
              <div className="text-xs text-gray-500 mt-2">
                All time
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-gray-500 text-sm">Active Stylists</div>
              <div className="text-2xl font-bold mt-1">{stats.totalStylists}</div>
              <div className="text-xs text-gray-500 mt-2">
                {stats.activeBookingsToday} bookings today
              </div>
            </div>
          </div>
          
          {/* Recent Bookings */}
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-semibold">Recent Bookings</h2>
              <Link to="/admin/bookings" className="text-primary-600 hover:text-primary-800 text-sm">
                View All
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Service
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date & Time
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stylist
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {recentBookings.map((booking) => (
                    <tr key={booking.id}>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{booking.userName}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{booking.service}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{formatDate(booking.date)}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{booking.stylist}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadge(booking.status)}`}>
                          {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap text-sm font-medium">
                        <Link to={`/admin/bookings/${booking.id}`} className="text-primary-600 hover:text-primary-900 mr-4">
                          Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold">Quick Actions</h2>
            </div>
            <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link 
                to="/admin/bookings/new" 
                className="block p-3 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100"
              >
                <div className="font-medium">Create Booking</div>
                <div className="text-sm mt-1">Schedule a new appointment</div>
              </Link>
              
              <Link 
                to="/admin/users/new" 
                className="block p-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100"
              >
                <div className="font-medium">Add New User</div>
                <div className="text-sm mt-1">Register a new customer</div>
              </Link>
              
              <Link 
                to="/admin/stylists/new" 
                className="block p-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100"
              >
                <div className="font-medium">Add New Stylist</div>
                <div className="text-sm mt-1">Register a new stylist</div>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AdminDashboard; 