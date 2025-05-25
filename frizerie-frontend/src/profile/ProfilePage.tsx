import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';

const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage({ type: '', text: '' });
    
    try {
      // In a real app, this would be an API call
      // Simulating API call with timeout
      setTimeout(() => {
        setMessage({ 
          type: 'success', 
          text: 'Your profile has been updated successfully!' 
        });
        setIsSubmitting(false);
      }, 1000);
    } catch (error) {
      console.error('Profile update failed:', error);
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to update profile'
      });
      setIsSubmitting(false);
    }
  };
  
  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.newPassword !== formData.confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }
    
    setIsSubmitting(true);
    setMessage({ type: '', text: '' });
    
    try {
      // In a real app, this would be an API call
      // Simulating API call with timeout
      setTimeout(() => {
        // Clear password fields
        setFormData(prev => ({
          ...prev,
          currentPassword: '',
          newPassword: '',
          confirmPassword: '',
        }));
        
        setMessage({ 
          type: 'success', 
          text: 'Your password has been updated successfully!' 
        });
        setIsSubmitting(false);
      }, 1000);
    } catch (error) {
      console.error('Password update failed:', error);
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to update password'
      });
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Your Profile</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow h-full">
            <div className="flex flex-col items-center p-6">
              <div className="w-32 h-32 bg-gray-300 rounded-full mb-4 flex items-center justify-center">
                <span className="text-4xl text-gray-600">
                  {user?.name?.charAt(0) || '?'}
                </span>
              </div>
              
              <h2 className="text-xl font-semibold">{user?.name}</h2>
              <p className="text-gray-600">{user?.email}</p>
              
              <div className="mt-6 w-full">
                <button
                  className={`w-full text-left px-4 py-2 mb-2 rounded-md ${
                    activeTab === 'profile' ? 'bg-primary-50 text-primary-700' : ''
                  }`}
                  onClick={() => setActiveTab('profile')}
                >
                  Profile Information
                </button>
                
                <button
                  className={`w-full text-left px-4 py-2 rounded-md ${
                    activeTab === 'password' ? 'bg-primary-50 text-primary-700' : ''
                  }`}
                  onClick={() => setActiveTab('password')}
                >
                  Change Password
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-2">
          {activeTab === 'profile' ? (
            <div className="bg-white rounded-lg shadow">
              <div className="border-b px-6 py-4">
                <h2 className="font-medium text-lg">Profile Information</h2>
              </div>
              <div className="p-6">
                {message.text && (
                  <div className={`mb-4 p-3 rounded-md ${
                    message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    {message.text}
                  </div>
                )}
                
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Full Name
                    </label>
                    <input
                      name="name"
                      type="text"
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    <input
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <input
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleChange}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  
                  <div className="pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow">
              <div className="border-b px-6 py-4">
                <h2 className="font-medium text-lg">Change Password</h2>
              </div>
              <div className="p-6">
                {message.text && (
                  <div className={`mb-4 p-3 rounded-md ${
                    message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    {message.text}
                  </div>
                )}
                
                <form onSubmit={handlePasswordUpdate} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password
                    </label>
                    <input
                      name="currentPassword"
                      type="password"
                      value={formData.currentPassword}
                      onChange={handleChange}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Password
                    </label>
                    <input
                      name="newPassword"
                      type="password"
                      value={formData.newPassword}
                      onChange={handleChange}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirm New Password
                    </label>
                    <input
                      name="confirmPassword"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  
                  <div className="pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Updating...' : 'Update Password'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage; 