import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../auth/useAuth';
import Card from '../components/Card';
import Input from '../components/Input';
import Button from '../components/Button';

const EditProfile: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || ''
      });
      setIsLoading(false);
    }
  }, [user]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage({ type: '', text: '' });
    
    try {
      const response = await fetch('/api/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
        }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update profile');
      }
      
      setMessage({ 
        type: 'success', 
        text: 'Your profile has been updated successfully!' 
      });
      
      // Redirect to profile page after successful update
      setTimeout(() => {
        navigate('/profile');
      }, 1500);
    } catch (error) {
      console.error('Profile update failed:', error);
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to update profile'
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="p-4">
        <Card>
          <div className="text-center py-4">Loading profile information...</div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Edit Profile</h1>
      
      <Card title="Profile Information">
        {message.text && (
          <div className={`mb-4 p-3 rounded-md ${
            message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              fullWidth
            />
          </div>
          
          <div>
            <Input
              label="Email Address"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              fullWidth
            />
          </div>
          
          <div>
            <Input
              label="Phone Number"
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              fullWidth
            />
          </div>
          
          <div className="flex space-x-4 pt-2">
            <Button
              type="submit"
              isLoading={isSubmitting}
            >
              Save Changes
            </Button>
            
            <Button
              variant="outline"
              onClick={() => navigate('/profile')}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default EditProfile; 