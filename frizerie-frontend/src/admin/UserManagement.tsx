import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// Mock data for demo
const mockUsers = [
  { id: 'u001', name: 'John Smith', email: 'john@example.com', vip_level: 'GOLD', loyalty_points: 875, created_at: '2022-06-15T10:30:00' },
  { id: 'u002', name: 'Alice Johnson', email: 'alice@example.com', vip_level: 'SILVER', loyalty_points: 450, created_at: '2022-07-22T14:15:00' },
  { id: 'u003', name: 'Michael Brown', email: 'michael@example.com', vip_level: 'BRONZE', loyalty_points: 150, created_at: '2022-09-05T09:45:00' },
  { id: 'u004', name: 'Emma Wilson', email: 'emma@example.com', vip_level: 'DIAMOND', loyalty_points: 1200, created_at: '2022-03-12T11:30:00' },
  { id: 'u005', name: 'Robert Davis', email: 'robert@example.com', vip_level: 'BRONZE', loyalty_points: 75, created_at: '2022-11-19T16:20:00' },
  { id: 'u006', name: 'Sarah Lee', email: 'sarah@example.com', vip_level: 'SILVER', loyalty_points: 350, created_at: '2022-08-30T13:10:00' },
  { id: 'u007', name: 'David Kim', email: 'david@example.com', vip_level: 'GOLD', loyalty_points: 780, created_at: '2022-05-27T10:15:00' },
  { id: 'u008', name: 'Jessica Chen', email: 'jessica@example.com', vip_level: 'BRONZE', loyalty_points: 220, created_at: '2022-10-03T15:45:00' },
];

interface User {
  id: string;
  name: string;
  email: string;
  vip_level: string;
  loyalty_points: number;
  created_at: string;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>(mockUsers);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedVipLevel, setSelectedVipLevel] = useState('');
  
  // Fetch real data from API in production
  useEffect(() => {
    // In a real implementation, this would fetch from the backend API
    // For example:
    // async function fetchUsers() {
    //   setIsLoading(true);
    //   try {
    //     const response = await api.get('/admin/users');
    //     setUsers(response.data);
    //   } catch (error) {
    //     console.error('Error fetching users:', error);
    //   } finally {
    //     setIsLoading(false);
    //   }
    // }
    // 
    // fetchUsers();
    
    // Simulate loading for demo
    setIsLoading(true);
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Filter users based on search term and selected VIP level
  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesVipLevel = selectedVipLevel ? user.vip_level === selectedVipLevel : true;
    
    return matchesSearch && matchesVipLevel;
  });
  
  // Format date for display
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  // Get VIP badge class
  const getVipBadgeClass = (vipLevel: string): string => {
    switch (vipLevel) {
      case 'DIAMOND':
        return 'bg-purple-100 text-purple-800';
      case 'GOLD':
        return 'bg-yellow-100 text-yellow-800';
      case 'SILVER':
        return 'bg-gray-100 text-gray-800';
      case 'BRONZE':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Handle user deletion (mock implementation)
  const handleDeleteUser = (userId: string) => {
    if (window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      // In a real implementation, this would call the API to delete the user
      // For demo, we'll just remove from local state
      setUsers(users.filter(user => user.id !== userId));
    }
  };
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">User Management</h1>
        <Link 
          to="/admin/users/new" 
          className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md"
        >
          Add New User
        </Link>
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Search Users
            </label>
            <input
              type="text"
              id="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name or email"
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label htmlFor="vipLevel" className="block text-sm font-medium text-gray-700 mb-1">
              Filter by VIP Level
            </label>
            <select
              id="vipLevel"
              value={selectedVipLevel}
              onChange={(e) => setSelectedVipLevel(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">All Levels</option>
              <option value="DIAMOND">Diamond</option>
              <option value="GOLD">Gold</option>
              <option value="SILVER">Silver</option>
              <option value="BRONZE">Bronze</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Users Table */}
      <div className="bg-white rounded-lg shadow">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    VIP Level
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Loyalty Points
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Joined
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredUsers.length > 0 ? (
                  filteredUsers.map((user) => (
                    <tr key={user.id}>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{user.name}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${getVipBadgeClass(user.vip_level)}`}>
                          {user.vip_level}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{user.loyalty_points}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{formatDate(user.created_at)}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap text-sm font-medium">
                        <Link 
                          to={`/admin/users/${user.id}/edit`} 
                          className="text-primary-600 hover:text-primary-900 mr-4"
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-gray-500">
                      No users found matching your search criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserManagement; 