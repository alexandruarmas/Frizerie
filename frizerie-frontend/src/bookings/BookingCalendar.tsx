import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import usersService, { LoyaltyStatus } from '../services/users';

// Define a basic service type
interface Service {
  id: string;
  name: string;
  duration: number;
  price: number;
}

// Define a barber type
interface Barber {
  id: string;
  name: string;
  imageUrl: string;
}

// Define a time slot type
interface TimeSlot {
  time: string;
  available: boolean;
  isVipOnly?: boolean;
}

const BookingCalendar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const preselectedBarberId = queryParams.get('barber');
  
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedBarber, setSelectedBarber] = useState<string>(preselectedBarberId || '');
  const [selectedService, setSelectedService] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  
  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loyaltyStatus, setLoyaltyStatus] = useState<LoyaltyStatus | null>(null);
  const [isVip, setIsVip] = useState(false);

  // Generate dates for the calendar (next 14 days)
  const generateCalendarDays = () => {
    const days = [];
    const today = new Date();
    
    for (let i = 0; i < 14; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      days.push(date);
    }
    
    return days;
  };
  
  const calendarDays = generateCalendarDays();
  
  // Format date for display
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
    }).format(date);
  };
  
  // Check if a date is the selected date
  const isSelectedDate = (date: Date) => {
    return date.toDateString() === selectedDate.toDateString();
  };
  
  // Format date for API requests
  const formatDateForApi = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  // Fetch user's loyalty status
  useEffect(() => {
    const fetchLoyaltyStatus = async () => {
      try {
        // In real app, this would call the API
        // For now, using mock data
        setTimeout(() => {
          const status = usersService.getMockLoyaltyStatus();
          setLoyaltyStatus(status);
          
          // Check if user is VIP (SILVER or above)
          setIsVip(['SILVER', 'GOLD', 'DIAMOND'].includes(status.tier));
        }, 500);
      } catch (error) {
        console.error('Error fetching loyalty status:', error);
      }
    };

    fetchLoyaltyStatus();
  }, []);

  // Fetch barbers
  useEffect(() => {
    const fetchBarbers = async () => {
      try {
        // In a real app, this would be an API call
        // Simulating API response with dummy data
        setTimeout(() => {
          setBarbers([
            {
              id: '1',
              name: 'Alex Barbulescu',
              imageUrl: 'https://randomuser.me/api/portraits/men/32.jpg'
            },
            {
              id: '2',
              name: 'Maria Stilista',
              imageUrl: 'https://randomuser.me/api/portraits/women/44.jpg'
            },
            {
              id: '3',
              name: 'Ion Frizeru',
              imageUrl: 'https://randomuser.me/api/portraits/men/22.jpg'
            },
            {
              id: '4',
              name: 'Ana Coafeza',
              imageUrl: 'https://randomuser.me/api/portraits/women/29.jpg'
            }
          ]);
        }, 500);
      } catch (error) {
        console.error('Error fetching barbers:', error);
      }
    };
    
    fetchBarbers();
  }, []);
  
  // Fetch services
  useEffect(() => {
    const fetchServices = async () => {
      try {
        // In a real app, this would be an API call
        // Simulating API response with dummy data
        setTimeout(() => {
          setServices([
            {
              id: '1',
              name: 'Haircut & Styling',
              duration: 45,
              price: 35
            },
            {
              id: '2',
              name: 'Beard Trim',
              duration: 20,
              price: 20
            },
            {
              id: '3',
              name: 'Full Service (Cut, Beard, Styling)',
              duration: 60,
              price: 55
            },
            {
              id: '4',
              name: 'Kids Haircut',
              duration: 30,
              price: 25
            }
          ]);
          setIsLoading(false);
        }, 800);
      } catch (error) {
        console.error('Error fetching services:', error);
        setIsLoading(false);
      }
    };
    
    fetchServices();
  }, []);
  
  // Fetch available time slots when date, barber, or service changes
  useEffect(() => {
    const fetchTimeSlots = async () => {
      if (!selectedDate || !selectedBarber || !selectedService) {
        return;
      }
      
      setIsLoading(true);
      
      try {
        // In a real app, this would be an API call
        // Simulating API response with dummy data
        setTimeout(() => {
          // Generate some dummy time slots
          const slots: TimeSlot[] = [];
          const startHour = 9; // 9 AM
          const endHour = 18; // 6 PM
          
          for (let hour = startHour; hour < endHour; hour++) {
            // Add slots at :00 and :30
            ['00', '30'].forEach(minutes => {
              // Randomly determine if slot is available (75% chance)
              const available = Math.random() > 0.25;
              
              // Some slots are VIP only (for premium times)
              // Make prime time slots (lunch and after work) VIP only
              const isVipOnly = (hour >= 12 && hour <= 13) || (hour >= 17);
              
              slots.push({
                time: `${hour}:${minutes}`,
                available,
                isVipOnly
              });
            });
          }
          
          // Format times to be more readable
          const formattedSlots = slots.map(slot => {
            const [hours, minutes] = slot.time.split(':');
            const hour = parseInt(hours);
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const hour12 = hour % 12 || 12;
            return {
              time: `${hour12}:${minutes} ${ampm}`,
              available: slot.available,
              isVipOnly: slot.isVipOnly
            };
          });
          
          setTimeSlots(formattedSlots);
          setIsLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error fetching time slots:', error);
        setIsLoading(false);
      }
    };
    
    fetchTimeSlots();
  }, [selectedDate, selectedBarber, selectedService]);
  
  // Handle proceeding to booking form
  const handleProceedToBooking = () => {
    if (!selectedBarber || !selectedService || !selectedTime) {
      return;
    }
    
    navigate('/bookings/new', {
      state: {
        barberId: selectedBarber,
        serviceId: selectedService,
        date: formatDateForApi(selectedDate),
        time: selectedTime
      }
    });
  };

  // Determine if a slot is available based on VIP status
  const isSlotAvailable = (slot: TimeSlot) => {
    if (!slot.available) return false;
    if (slot.isVipOnly && !isVip) return false;
    return true;
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Book Your Appointment</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Step 1: Select a date */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b px-6 py-4">
            <h2 className="font-medium text-lg">1. Select a Date</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-7 gap-2">
              {calendarDays.map((day, index) => (
                <button
                  key={index}
                  className={`p-2 rounded-md text-center transition-colors ${
                    isSelectedDate(day)
                      ? 'bg-primary-600 text-white'
                      : 'hover:bg-primary-100'
                  }`}
                  onClick={() => setSelectedDate(day)}
                >
                  <div className="text-xs">{day.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                  <div className="text-lg font-semibold">{day.getDate()}</div>
                </button>
              ))}
            </div>
            <div className="mt-4 text-center text-sm text-gray-600">
              Selected: {formatDate(selectedDate)}
            </div>
          </div>
        </div>
        
        {/* Step 2: Select barber and service */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b px-6 py-4">
            <h2 className="font-medium text-lg">2. Select Barber & Service</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Barber</label>
                <select
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value={selectedBarber}
                  onChange={(e) => setSelectedBarber(e.target.value)}
                >
                  <option value="">Select a barber</option>
                  {barbers.map((barber) => (
                    <option key={barber.id} value={barber.id}>
                      {barber.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Service</label>
                <select
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value={selectedService}
                  onChange={(e) => setSelectedService(e.target.value)}
                >
                  <option value="">Select a service</option>
                  {services.map((service) => (
                    <option key={service.id} value={service.id}>
                      {service.name} - ${service.price} ({service.duration} min)
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
        
        {/* Step 3: Select time slot */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b px-6 py-4">
            <h2 className="font-medium text-lg">3. Select Time</h2>
          </div>
          <div className="p-6">
            {selectedBarber && selectedService ? (
              <div>
                {isLoading ? (
                  <div className="text-center py-4">Loading available times...</div>
                ) : timeSlots.length === 0 ? (
                  <div className="text-center py-4 text-gray-600">
                    No available time slots for the selected options.
                  </div>
                ) : (
                  <>
                    {!isVip && (
                      <div className="mb-4 p-3 bg-amber-50 border-l-4 border-amber-500 text-amber-700 text-sm">
                        <p>Some premium time slots are reserved for VIP members (Silver tier and above).</p>
                      </div>
                    )}
                    <div className="grid grid-cols-3 gap-2">
                      {timeSlots.map((slot, index) => (
                        <button
                          key={index}
                          className={`p-2 text-center rounded-md transition-colors relative ${
                            !isSlotAvailable(slot)
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                              : slot.time === selectedTime
                              ? 'bg-primary-600 text-white'
                              : slot.isVipOnly
                              ? 'border border-yellow-400 bg-yellow-50 hover:bg-yellow-100'
                              : 'border border-gray-300 hover:bg-primary-100'
                          }`}
                          onClick={() => isSlotAvailable(slot) && setSelectedTime(slot.time)}
                          disabled={!isSlotAvailable(slot)}
                        >
                          {slot.time}
                          {slot.isVipOnly && (
                            <span className="absolute top-0 right-0 transform translate-x-1 -translate-y-1">
                              <span className="inline-block w-3 h-3 bg-yellow-400 rounded-full" 
                                title="VIP only slot"></span>
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  </>
                )}
                
                <div className="mt-6">
                  <button
                    className={`w-full px-4 py-2 rounded-md ${
                      !selectedTime 
                        ? 'bg-gray-300 cursor-not-allowed' 
                        : 'bg-primary-600 text-white hover:bg-primary-700'
                    }`}
                    disabled={!selectedTime}
                    onClick={handleProceedToBooking}
                  >
                    Continue to Booking
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-600">
                Please select a barber and service first.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingCalendar; 