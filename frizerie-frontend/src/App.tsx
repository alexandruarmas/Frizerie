import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './auth/AuthContext';
import Layout from './components/Layout';
import React, { ReactNode } from 'react';

// Auth components
import LoginPage from './auth/LoginPage';
import RegisterPage from './auth/RegisterPage';

// Main pages
import Dashboard from './dashboard/Dashboard';
import BookingCalendar from './bookings/BookingCalendar';
import BookingForm from './bookings/BookingForm';
import BookingList from './bookings/BookingList';
import ProfilePage from './profile/ProfilePage';

// AI Hairstyle module
import HairstyleTryOn from './ai_hairstyle/HairstyleTryOn';
import SavedHairstyles from './ai_hairstyle/SavedHairstyles';

// Admin module
import AdminLayout from './admin/AdminLayout';
import AdminDashboard from './admin/Dashboard';
import UserManagement from './admin/UserManagement';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  const { isLoading } = useAuth();
  
  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading application...</div>;
  }
  
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="bookings">
          <Route index element={<BookingList />} />
          <Route path="new" element={<BookingCalendar />} />
          <Route path="form" element={<BookingForm />} />
        </Route>
        <Route path="profile">
          <Route index element={<ProfilePage />} />
        </Route>
        {/* AI Hairstyle module routes */}
        <Route path="hairstyle-try-on" element={<HairstyleTryOn />} />
        <Route path="saved-hairstyles" element={<SavedHairstyles />} />
      </Route>
      
      {/* Admin routes */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="users/:id/edit" element={<div>Edit User (Coming Soon)</div>} />
        <Route path="users/new" element={<div>New User Form (Coming Soon)</div>} />
        <Route path="bookings" element={<div>All Bookings (Coming Soon)</div>} />
        <Route path="bookings/:id" element={<div>Booking Details (Coming Soon)</div>} />
        <Route path="bookings/new" element={<div>New Booking Form (Coming Soon)</div>} />
        <Route path="stylists" element={<div>Stylists Management (Coming Soon)</div>} />
        <Route path="stylists/:id/edit" element={<div>Edit Stylist (Coming Soon)</div>} />
        <Route path="stylists/new" element={<div>New Stylist Form (Coming Soon)</div>} />
        <Route path="schedule" element={<div>Stylist Schedule (Coming Soon)</div>} />
        <Route path="settings" element={<div>Admin Settings (Coming Soon)</div>} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App; 