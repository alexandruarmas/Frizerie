import React from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import OfflineIndicator from './OfflineIndicator';

const Layout: React.FC = () => {
  const location = useLocation();
  const { logout, user } = useAuth();
  
  const isActive = (path: string) => {
    return location.pathname.startsWith(path) ? 'text-primary-600 font-medium' : 'text-gray-600';
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="container mx-auto flex justify-between items-center p-4">
          <h1 className="text-2xl font-bold text-primary-600">Frizerie</h1>
          <nav className="hidden md:flex space-x-6">
            <Link to="/" className={`${location.pathname === '/' ? 'text-primary-600 font-medium' : 'text-gray-600'}`}>
              Dashboard
            </Link>
            <Link to="/bookings" className={`${isActive('/bookings')}`}>
              Bookings
            </Link>
            <div className="relative group">
              <button className={`${isActive('/hairstyle')} flex items-center`}>
                Hairstyles <span className="ml-1">▼</span>
              </button>
              <div className="absolute hidden group-hover:block bg-white shadow-md rounded-md py-2 min-w-40 z-10">
                <Link 
                  to="/hairstyle-try-on" 
                  className="block px-4 py-2 hover:bg-gray-100 text-gray-800"
                >
                  Try On Hairstyles
                </Link>
                <Link 
                  to="/saved-hairstyles" 
                  className="block px-4 py-2 hover:bg-gray-100 text-gray-800"
                >
                  Saved Looks
                </Link>
              </div>
            </div>
            <Link to="/profile" className={`${isActive('/profile')}`}>
              Profile
            </Link>
            {user?.role === 'admin' && (
              <Link to="/admin" className="text-gray-600 hover:text-primary-600">
                Admin
              </Link>
            )}
            <button 
              onClick={logout}
              className="text-gray-600 hover:text-primary-600"
            >
              Logout
            </button>
          </nav>
          
          {/* Mobile menu button */}
          <button className="md:hidden text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
        
        {/* Mobile menu (hidden by default) */}
        <div className="hidden md:hidden bg-white border-t">
          <div className="container mx-auto px-4 py-2">
            <Link to="/" className="block py-2 text-gray-600">Dashboard</Link>
            <Link to="/bookings" className="block py-2 text-gray-600">Bookings</Link>
            <Link to="/hairstyle-try-on" className="block py-2 text-gray-600">Try On Hairstyles</Link>
            <Link to="/saved-hairstyles" className="block py-2 text-gray-600">Saved Looks</Link>
            <Link to="/profile" className="block py-2 text-gray-600">Profile</Link>
            {user?.role === 'admin' && (
              <Link to="/admin" className="block py-2 text-gray-600">Admin</Link>
            )}
            <button onClick={logout} className="block py-2 text-gray-600 w-full text-left">Logout</button>
          </div>
        </div>
      </header>
      
      <main className="py-6">
        <Outlet />
      </main>
      
      <footer className="bg-white mt-auto py-4 border-t">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          &copy; {new Date().getFullYear()} Frizerie - All rights reserved
        </div>
      </footer>
      
      {/* Offline indicator */}
      <OfflineIndicator />
    </div>
  );
};

export default Layout; 