import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';

interface Service {
  id: number;
  name: string;
  price: number;
  duration: number;
}

interface BookingFormData {
  date: string;
  time: string;
  stylistId: number;
}

const BookingForm: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get booking data from location state
  const bookingData = location.state as BookingFormData;

  useEffect(() => {
    if (!bookingData) {
      navigate('/bookings/new');
      return;
    }
    fetchServices();
  }, [bookingData, navigate]);

  const fetchServices = async () => {
    try {
      const response = await api.get<Service[]>('/services');
      setServices(response.data);
    } catch (error) {
      console.error('Error fetching services:', error);
      setError('Failed to load services. Please try again.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedService || !bookingData) return;

    setLoading(true);
    setError(null);

    try {
      await api.post('/bookings', {
        service_id: selectedService,
        stylist_id: bookingData.stylistId,
        date: bookingData.date,
        time: bookingData.time
      });

      // Redirect to bookings list on success
      navigate('/bookings');
    } catch (error) {
      console.error('Error creating booking:', error);
      setError('Failed to create booking. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!bookingData) {
    return null;
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Complete Your Booking</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-2">Booking Details</h2>
          <div className="space-y-2 text-gray-600">
            <p>Date: {new Date(bookingData.date).toLocaleDateString()}</p>
            <p>Time: {bookingData.time}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select a Service
            </label>
            <div className="space-y-3">
              {services.map((service) => (
                <button
                  key={service.id}
                  type="button"
                  onClick={() => setSelectedService(service.id)}
                  className={`w-full p-4 text-left rounded-lg border ${
                    selectedService === service.id
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-indigo-300'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">{service.name}</h3>
                      <p className="text-sm text-gray-600">{service.duration} minutes</p>
                    </div>
                    <span className="text-lg font-semibold">${service.price}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border-l-4 border-red-500 text-red-700">
              {error}
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => navigate('/bookings/new')}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={!selectedService || loading}
              className={`flex-1 px-4 py-2 rounded-md text-white ${
                !selectedService || loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
            >
              {loading ? 'Creating Booking...' : 'Confirm Booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BookingForm; 