import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface TimeSlot {
  id: string;
  time: string;
  available: boolean;
}

interface Stylist {
  id: number;
  name: string;
  specialization: string;
}

const BookingCalendar: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [stylists, setStylists] = useState<Stylist[]>([]);
  const [selectedStylist, setSelectedStylist] = useState<number | null>(null);
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStylists();
  }, []);

  const fetchStylists = async () => {
    try {
      const response = await api.get<Stylist[]>('/bookings/stylists');
      setStylists(response.data);
    } catch (error) {
      console.error('Error fetching stylists:', error);
    }
  };

  const handleDateChange = async (date: string) => {
    setSelectedDate(date);
    if (selectedStylist) {
      await fetchTimeSlots(date, selectedStylist);
    }
  };

  const handleStylistChange = async (stylistId: number) => {
    setSelectedStylist(stylistId);
    if (selectedDate) {
      await fetchTimeSlots(selectedDate, stylistId);
    }
  };

  const fetchTimeSlots = async (date: string, stylistId: number) => {
    setLoading(true);
    try {
      const response = await api.get<TimeSlot[]>(`/bookings/available-slots/${stylistId}/${date}`);
      setTimeSlots(response.data);
    } catch (error) {
      console.error('Error fetching time slots:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeSlotSelect = (slot: TimeSlot) => {
    if (slot.available) {
      navigate('/bookings/form', {
        state: {
          date: selectedDate,
          time: slot.time,
          stylistId: selectedStylist
        }
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Book an Appointment</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Stylist Selection */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Select a Stylist</h2>
          <div className="space-y-4">
            {stylists.map((stylist) => (
              <button
                key={stylist.id}
                onClick={() => handleStylistChange(stylist.id)}
                className={`w-full p-4 text-left rounded-lg border ${
                  selectedStylist === stylist.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-indigo-300'
                }`}
              >
                <h3 className="font-medium">{stylist.name}</h3>
                <p className="text-sm text-gray-600">{stylist.specialization}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Date and Time Selection */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Select Date & Time</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date
            </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => handleDateChange(e.target.value)}
              className="w-full p-2 border rounded-lg"
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
          ) : timeSlots.length > 0 ? (
            <div className="grid grid-cols-3 gap-2">
              {timeSlots.map((slot) => (
                <button
                  key={slot.id}
                  onClick={() => handleTimeSlotSelect(slot)}
                  disabled={!slot.available}
                  className={`p-2 text-center rounded-lg ${
                    slot.available
                      ? 'bg-indigo-100 hover:bg-indigo-200'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {slot.time}
                </button>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500">
              {selectedDate && selectedStylist
                ? 'No available time slots for this date'
                : 'Please select a date and stylist'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookingCalendar; 