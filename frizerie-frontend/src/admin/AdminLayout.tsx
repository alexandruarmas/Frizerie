import React from 'react';
import { Outlet, Link, useLocation, Navigate } from 'react-router-dom';
import useAuth from '../auth/useAuth';

const AdminLayout: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();
  
  // Check if user is admin
  const isAdmin = user?.role === 'admin';
  
  // If not authenticated or not admin, redirect to login
  if (!isAuthenticated || !isAdmin) {
    return <Navigate to="/login" replace />;
  }
  
  const isActive = (path: string) => {
    return location.pathname.startsWith(path) ? 'text-white bg-primary-700' : 'text-gray-300 hover:bg-primary-800';
  };
  
  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <div className="bg-primary-900 w-64 flex-shrink-0">
        <div className="p-4 text-white font-bold text-xl border-b border-primary-800">
          Frizerie Admin
        </div>
        
        <nav className="mt-4">
          <div className="px-4 py-2 text-xs text-gray-400 uppercase">Dashboard</div>
          <Link 
            to="/admin" 
            className={`block px-4 py-2 ${isActive('/admin')} ${location.pathname === '/admin' ? 'text-white bg-primary-700' : 'text-gray-300 hover:bg-primary-800'}`}
          >
            Overview
          </Link>
          
          <div className="px-4 py-2 text-xs text-gray-400 uppercase mt-4">User Management</div>
          <Link 
            to="/admin/users" 
            className={`block px-4 py-2 ${isActive('/admin/users')}`}
          >
            Users
          </Link>
          
          <div className="px-4 py-2 text-xs text-gray-400 uppercase mt-4">Bookings</div>
          <Link 
            to="/admin/bookings" 
            className={`block px-4 py-2 ${isActive('/admin/bookings')}`}
          >
            All Bookings
          </Link>
          
          <div className="px-4 py-2 text-xs text-gray-400 uppercase mt-4">Stylists</div>
          <Link 
            to="/admin/stylists" 
            className={`block px-4 py-2 ${isActive('/admin/stylists')}`}
          >
            Manage Stylists
          </Link>
          <Link 
            to="/admin/schedule" 
            className={`block px-4 py-2 ${isActive('/admin/schedule')}`}
          >
            Stylist Schedule
          </Link>
          
          <div className="px-4 py-2 text-xs text-gray-400 uppercase mt-4">System</div>
          <Link 
            to="/admin/settings" 
            className={`block px-4 py-2 ${isActive('/admin/settings')}`}
          >
            Settings
          </Link>
        </nav>
      </div>
      
      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className="bg-white shadow-sm p-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold">Admin Dashboard</h1>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {user?.name || user?.email}
            </span>
            <Link to="/" className="text-primary-600 hover:text-primary-800 text-sm">
              Exit Admin
            </Link>
          </div>
        </header>
        
        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout; 