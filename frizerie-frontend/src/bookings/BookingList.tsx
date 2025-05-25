import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import bookingsService, { Booking } from '../services/bookings';

const BookingList: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [selectedBookingId, setSelectedBookingId] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);
  
  // Filter state
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'past'>('upcoming');
  
  // Fetch bookings
  useEffect(() => {
    const fetchBookings = async () => {
      setIsLoading(true);
      
      try {
        // In a real app, this would call the API endpoint
        // For now, using mock data
        setTimeout(() => {
          const data = bookingsService.getMockBookings();
          setBookings(data);
          setIsLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error fetching bookings:', error);
        setError('Failed to load your bookings');
        setIsLoading(false);
      }
    };
    
    fetchBookings();
  }, []);
  
  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };
  
  // Filter bookings based on the selected filter
  const filteredBookings = bookings.filter((booking) => {
    const bookingDate = new Date(`${booking.date}T${booking.time}`);
    const today = new Date();
    
    if (filter === 'upcoming') {
      return bookingDate >= today && booking.status !== 'cancelled';
    } else if (filter === 'past') {
      return bookingDate < today || booking.status === 'completed' || booking.status === 'cancelled';
    }
    
    return true;
  });
  
  // Handle booking cancellation
  const handleCancelBooking = async () => {
    if (!selectedBookingId) return;
    
    setIsCancelling(true);
    
    try {
      // In a real app, this would call the API endpoint
      // For now, simulating API call with timeout
      setTimeout(() => {
        // Update the booking status in the local state
        setBookings(bookings.map(booking => 
          booking.id === selectedBookingId 
            ? { ...booking, status: 'cancelled' as const } 
            : booking
        ));
        
        setShowCancelModal(false);
        setIsCancelling(false);
        setSelectedBookingId(null);
      }, 1000);
    } catch (error) {
      console.error('Error cancelling booking:', error);
      setError('Failed to cancel booking');
      setIsCancelling(false);
      setSelectedBookingId(null);
    }
  };
  
  // Handle initiating cancellation
  const initiateCancel = (bookingId: string) => {
    setSelectedBookingId(bookingId);
    setShowCancelModal(true);
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h1 className="text-2xl font-semibold text-gray-800">Your Bookings</h1>
        
        <div className="mt-4 md:mt-0 flex">
          <div className="inline-flex bg-gray-100 rounded-lg p-1">
            <button
              className={`px-4 py-2 text-sm rounded-md ${filter === 'upcoming' ? 'bg-white shadow' : ''}`}
              onClick={() => setFilter('upcoming')}
            >
              Upcoming
            </button>
            <button
              className={`px-4 py-2 text-sm rounded-md ${filter === 'past' ? 'bg-white shadow' : ''}`}
              onClick={() => setFilter('past')}
            >
              Past
            </button>
            <button
              className={`px-4 py-2 text-sm rounded-md ${filter === 'all' ? 'bg-white shadow' : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
          </div>
          
          <Link to="/bookings/calendar">
            <button className="ml-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm">
              New Booking
            </button>
          </Link>
        </div>
      </div>
      
      {isLoading ? (
        <div className="text-center py-8">Loading your bookings...</div>
      ) : error ? (
        <div className="text-center py-8 text-red-600">{error}</div>
      ) : filteredBookings.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">You don't have any {filter === 'upcoming' ? 'upcoming' : filter === 'past' ? 'past' : ''} bookings.</p>
            <Link to="/bookings/calendar">
              <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors">
                Book an Appointment
              </button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredBookings.map((booking) => (
            <div key={booking.id} className="bg-white rounded-lg shadow overflow-hidden">
              <div className="flex flex-col md:flex-row">
                <div className="flex-grow p-4">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">{booking.service_name}</h3>
                      <p className="text-gray-600">with {booking.barber_name}</p>
                    </div>
                    
                    <div className="mt-2 md:mt-0 md:text-right">
                      <div className="text-gray-700">{formatDate(booking.date)}</div>
                      <div className="text-gray-600">{booking.time}</div>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex flex-col md:flex-row md:items-center md:justify-between">
                    <div className="flex items-center">
                      <span className="text-gray-700 font-medium">${booking.price?.toFixed(2)}</span>
                      <span className={`ml-3 px-2 py-1 text-xs rounded-full ${
                        booking.status === 'scheduled' ? 'bg-green-100 text-green-800' :
                        booking.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                      </span>
                    </div>
                    
                    {booking.status === 'scheduled' && (
                      <div className="mt-3 md:mt-0">
                        <button 
                          className="px-3 py-1 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 text-sm"
                          onClick={() => initiateCancel(booking.id)}
                        >
                          Cancel Booking
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Cancel Confirmation Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Cancel Booking</h3>
              <div className="py-2">
                <p className="text-gray-700">
                  Are you sure you want to cancel this booking? This action cannot be undone.
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Note: Cancellations made less than 24 hours before the appointment may incur a fee.
                </p>
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  onClick={() => setShowCancelModal(false)}
                  disabled={isCancelling}
                >
                  Keep Booking
                </button>
                <button
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  onClick={handleCancelBooking}
                  disabled={isCancelling}
                >
                  {isCancelling ? 'Cancelling...' : 'Yes, Cancel'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BookingList; 