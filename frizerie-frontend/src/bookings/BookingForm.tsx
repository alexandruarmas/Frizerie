import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

interface BookingDetails {
  barberId: string;
  serviceId: string;
  date: string;
  time: string;
}

interface Barber {
  id: string;
  name: string;
}

interface Service {
  id: string;
  name: string;
  price: number;
  duration: number;
}

const BookingForm: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const bookingDetails = location.state as BookingDetails;
  
  const [barber, setBarber] = useState<Barber | null>(null);
  const [service, setService] = useState<Service | null>(null);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // Redirect if no booking details
  useEffect(() => {
    if (!bookingDetails) {
      navigate('/bookings/calendar');
    }
  }, [bookingDetails, navigate]);
  
  // Fetch barber and service details
  useEffect(() => {
    if (!bookingDetails) return;
    
    const fetchDetails = async () => {
      try {
        // In a real app, these would be API calls
        // Simulating API responses with dummy data
        setTimeout(() => {
          // Dummy barber data
          if (bookingDetails.barberId === '1') {
            setBarber({
              id: '1',
              name: 'Alex Barbulescu'
            });
          } else if (bookingDetails.barberId === '2') {
            setBarber({
              id: '2',
              name: 'Maria Stilista'
            });
          } else if (bookingDetails.barberId === '3') {
            setBarber({
              id: '3',
              name: 'Ion Frizeru'
            });
          } else if (bookingDetails.barberId === '4') {
            setBarber({
              id: '4',
              name: 'Ana Coafeza'
            });
          }
          
          // Dummy service data
          if (bookingDetails.serviceId === '1') {
            setService({
              id: '1',
              name: 'Haircut & Styling',
              duration: 45,
              price: 35
            });
          } else if (bookingDetails.serviceId === '2') {
            setService({
              id: '2',
              name: 'Beard Trim',
              duration: 20,
              price: 20
            });
          } else if (bookingDetails.serviceId === '3') {
            setService({
              id: '3',
              name: 'Full Service (Cut, Beard, Styling)',
              duration: 60,
              price: 55
            });
          } else if (bookingDetails.serviceId === '4') {
            setService({
              id: '4',
              name: 'Kids Haircut',
              duration: 30,
              price: 25
            });
          }
        }, 500);
      } catch (error) {
        console.error('Error fetching booking details:', error);
        setError('Failed to load booking details');
      }
    };
    
    fetchDetails();
  }, [bookingDetails]);
  
  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!bookingDetails || !barber || !service) {
      return;
    }
    
    setIsSubmitting(true);
    setError('');
    
    try {
      // In a real app, this would be an API call
      // Simulating API call with timeout
      setTimeout(() => {
        // Booking successful
        setSuccess(true);
        
        // Redirect to bookings list after short delay
        setTimeout(() => {
          navigate('/bookings');
        }, 2000);
      }, 1500);
    } catch (err) {
      console.error('Booking failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to create booking');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (!bookingDetails || !barber || !service) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-4">
            {error || 'Loading booking details...'}
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Confirm Your Booking</h1>
      
      {success ? (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-6">
            <div className="text-green-500 text-5xl mb-4">✓</div>
            <h2 className="text-xl font-semibold mb-2">Booking Confirmed!</h2>
            <p className="text-gray-600 mb-4">
              Your appointment has been successfully booked. You will be redirected to your bookings.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Booking Summary */}
          <div className="bg-white rounded-lg shadow">
            <div className="border-b px-6 py-4">
              <h2 className="font-medium text-lg">Booking Summary</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Barber</h3>
                  <p className="text-lg font-medium">{barber.name}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Service</h3>
                  <p className="text-lg font-medium">{service.name}</p>
                  <p className="text-sm text-gray-600">
                    ${service.price} • {service.duration} minutes
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Date & Time</h3>
                  <p className="text-lg font-medium">
                    {formatDate(bookingDetails.date)} at {bookingDetails.time}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Booking Form */}
          <div className="bg-white rounded-lg shadow">
            <div className="border-b px-6 py-4">
              <h2 className="font-medium text-lg">Complete Your Booking</h2>
            </div>
            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Your Name
                  </label>
                  <input
                    type="text"
                    value={user?.name || ''}
                    disabled
                    className="w-full border border-gray-300 rounded-md px-3 py-2 bg-gray-50"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full border border-gray-300 rounded-md px-3 py-2 bg-gray-50"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Additional Notes (Optional)
                  </label>
                  <textarea
                    className="w-full border border-gray-300 rounded-md px-3 py-2 min-h-[100px]"
                    placeholder="Any special requests or information for the barber..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                  />
                </div>
                
                {error && (
                  <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm">
                    {error}
                  </div>
                )}
                
                <div className="pt-2">
                  <button
                    type="submit"
                    className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Processing...' : 'Confirm Booking'}
                  </button>
                </div>
                
                <div className="text-center text-xs text-gray-500 mt-2">
                  By confirming this booking, you agree to our cancellation policy.
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BookingForm; 