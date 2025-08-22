import React, { useState } from 'react';
import { Calendar, Clock, MapPin, Wrench, CheckCircle } from 'lucide-react';

interface BookingWidgetProps {
  title?: string;
  subtitle?: string;
  services?: string[];
  timeSlots?: string[];
  showPricing?: boolean;
  apiEndpoint?: string;
}

export default function BookingWidget({
  title = 'Schedule Your Service',
  subtitle = 'Choose a convenient time that works for you',
  services = [],
  timeSlots = ['8:00 AM', '10:00 AM', '12:00 PM', '2:00 PM', '4:00 PM'],
  showPricing = false,
  apiEndpoint = '/api/booking',
}: BookingWidgetProps) {
  const [selectedService, setSelectedService] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [duration, setDuration] = useState('');
  const [location, setLocation] = useState('');
  const [specialRequirements, setSpecialRequirements] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bookingComplete, setBookingComplete] = useState(false);

  // Generate next 14 days for date selection
  const generateDates = () => {
    const dates = [];
    const today = new Date();
    for (let i = 0; i < 14; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
  };

  const availableDates = generateDates();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // In production, this would send to the actual API
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service: selectedService,
          date: selectedDate,
          time: selectedTime,
          duration,
          location,
          specialRequirements,
        }),
      });

      if (response.ok) {
        setBookingComplete(true);
      }
    } catch (error) {
      console.error('Booking error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (bookingComplete) {
    return (
      <section className="py-16 bg-gradient-to-br from-green-50 to-blue-50">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <div className="bg-white rounded-2xl shadow-xl p-12">
            <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4">Booking Confirmed!</h2>
            <p className="text-gray-600 mb-2">
              Your service appointment has been scheduled for
            </p>
            <p className="text-xl font-semibold text-blue-600 mb-6">
              {new Date(selectedDate).toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })} at {selectedTime}
            </p>
            <p className="text-gray-600">
              You'll receive a confirmation email with all the details shortly.
            </p>
            <button
              onClick={() => setBookingComplete(false)}
              className="mt-8 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Schedule Another Service
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-2">{title}</h2>
          {subtitle && <p className="text-gray-600">{subtitle}</p>}
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Service Selection */}
            {services.length > 0 && (
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                  <Wrench className="w-4 h-4" />
                  Select Service *
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {services.map((service) => (
                    <button
                      key={service}
                      type="button"
                      onClick={() => setSelectedService(service)}
                      className={`
                        p-4 rounded-lg border-2 text-left transition-all
                        ${selectedService === service
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                    >
                      <div className="font-medium">{service}</div>
                      {showPricing && (
                        <div className="text-sm text-gray-500 mt-1">
                          Starting at $99
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Date Selection */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Calendar className="w-4 h-4" />
                Select Date *
              </label>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                {availableDates.slice(0, 10).map((date) => {
                  const dateObj = new Date(date);
                  const isWeekend = dateObj.getDay() === 0 || dateObj.getDay() === 6;
                  return (
                    <button
                      key={date}
                      type="button"
                      onClick={() => setSelectedDate(date)}
                      disabled={isWeekend}
                      className={`
                        p-3 rounded-lg text-center transition-all
                        ${selectedDate === date
                          ? 'bg-blue-500 text-white'
                          : isWeekend
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-gray-50 hover:bg-gray-100'
                        }
                      `}
                    >
                      <div className="text-xs">
                        {dateObj.toLocaleDateString('en-US', { weekday: 'short' })}
                      </div>
                      <div className="font-semibold">
                        {dateObj.getDate()}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Time Selection */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Clock className="w-4 h-4" />
                Select Time *
              </label>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                {timeSlots.map((time) => (
                  <button
                    key={time}
                    type="button"
                    onClick={() => setSelectedTime(time)}
                    className={`
                      py-2 px-4 rounded-lg transition-all
                      ${selectedTime === time
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-50 hover:bg-gray-100'
                      }
                    `}
                  >
                    {time}
                  </button>
                ))}
              </div>
            </div>

            {/* Duration Estimate */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Estimated Duration *
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select duration</option>
                <option value="30min">30 minutes</option>
                <option value="1hour">1 hour</option>
                <option value="2hours">2 hours</option>
                <option value="3hours">3+ hours</option>
                <option value="fullday">Full day</option>
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4" />
                Service Address *
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="123 Main St, City, State ZIP"
              />
            </div>

            {/* Special Requirements */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Special Requirements or Access Instructions
              </label>
              <textarea
                value={specialRequirements}
                onChange={(e) => setSpecialRequirements(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Gate codes, parking instructions, equipment needed, etc."
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!selectedService || !selectedDate || !selectedTime || !duration || !location || isSubmitting}
              className={`
                w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all duration-200
                ${(!selectedService || !selectedDate || !selectedTime || !duration || !location || isSubmitting)
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
                }
              `}
            >
              {isSubmitting ? 'Booking...' : 'Book Appointment'}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
