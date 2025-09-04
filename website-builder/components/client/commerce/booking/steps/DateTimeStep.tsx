/**
 * Date & Time Step (Step 3)
 * 
 * Allows user to select appointment date and time from available slots
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Zap, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
import { serviceAreasApi } from '@/lib/api/service-areas-client';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useBookingWizard, TimeSlot } from '../Hero365BookingContext';

interface DateTimeStepProps {
  businessId: string;
}

interface AvailableSlot {
  start: string;
  end: string;
  available: boolean;
  price?: number;
  isEmergency?: boolean;
}

export default function DateTimeStep({ businessId }: DateTimeStepProps) {
  const { state, updateSlot, nextStep, setLoading, setError } = useBookingWizard();
  
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedSlot, setSelectedSlot] = useState<AvailableSlot | null>(null);
  const [viewMode, setViewMode] = useState<'first_available' | 'calendar'>('first_available');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [availableSlots, setAvailableSlots] = useState<Record<string, AvailableSlot[]>>({});
  const [isLoadingSlots, setIsLoadingSlots] = useState(false);

  // Load available slots when component mounts or date changes
  useEffect(() => {
    loadAvailableSlots();
  }, [businessId, state.serviceId, state.zipInfo]);

  const loadAvailableSlots = async () => {
    if (!state.serviceId || !state.zipInfo?.postalCode) return;

    setIsLoadingSlots(true);
    setError();

    try {
      const today = new Date();
      const endDate = new Date(today);
      endDate.setDate(today.getDate() + 14); // Load 14 days ahead

      // Try to get real availability data from the API
      try {
        const result = await serviceAreasApi.getAvailableSlots({
          business_id: businessId,
          service_id: state.serviceId,
          postal_code: state.zipInfo.postalCode,
          country_code: state.zipInfo.countryCode,
          timezone: state.zipInfo.timezone,
          date_range: {
            from: today.toISOString().split('T')[0],
            to: endDate.toISOString().split('T')[0]
          }
        });

        // Convert API response to our internal format
        const slots: Record<string, AvailableSlot[]> = {};
        
        // Group slots by date
        result.slots.forEach(slot => {
          const date = new Date(slot.start);
          const dateStr = date.toISOString().split('T')[0];
          
          if (!slots[dateStr]) {
            slots[dateStr] = [];
          }
          
          slots[dateStr].push({
            start: slot.start,
            end: slot.end,
            available: true,
            price: 15000 + Math.floor(Math.random() * 5000), // Mock pricing
            isEmergency: false
          });
        });

        setAvailableSlots(slots);
        
        // Auto-select first available slot if in "first available" mode
        if (viewMode === 'first_available' && result.first_available) {
          const firstAvailableDate = new Date(result.first_available.start).toISOString().split('T')[0];
          setSelectedDate(firstAvailableDate);
          setSelectedSlot({
            start: result.first_available.start,
            end: result.first_available.end,
            available: true,
            price: 15000
          });
        }

      } catch (apiError) {
        console.warn('Availability API not available:', apiError);
        
        // Show error message instead of mock data
        setError('Unable to load available time slots. Please contact us directly to schedule your appointment.');
        setAvailableSlots({});
      }

    } catch (error) {
      console.error('Error loading availability:', error);
      setError('Unable to load available time slots. Please try again.');
    } finally {
      setIsLoadingSlots(false);
    }
  };

  const findFirstAvailableSlot = (slots: Record<string, AvailableSlot[]>) => {
    for (const [date, daySlots] of Object.entries(slots)) {
      const availableSlot = daySlots.find(slot => slot.available);
      if (availableSlot) {
        return { date, slot: availableSlot };
      }
    }
    return null;
  };

  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
    setSelectedSlot(null);
  };

  const handleSlotSelect = (slot: AvailableSlot) => {
    setSelectedSlot(slot);
  };

  const handleContinue = () => {
    if (selectedSlot && selectedDate) {
      const timeSlot: TimeSlot = {
        start: selectedSlot.start,
        end: selectedSlot.end,
        timezone: state.zipInfo?.timezone || 'America/New_York'
      };

      updateSlot(timeSlot);
      nextStep();
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const hasAvailableSlots = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    const daySlots = availableSlots[dateStr] || [];
    return daySlots.some(slot => slot.available);
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isPast = (date: Date) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  const selectedDateSlots = selectedDate ? availableSlots[selectedDate] || [] : [];
  const availableSlotsForDate = selectedDateSlots.filter(slot => slot.available);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Calendar className="w-8 h-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          When do you need us?
        </h1>
        <p className="text-gray-600">
          Choose your preferred appointment time
        </p>
      </div>

      {/* View Mode Tabs */}
      <div className="flex justify-center">
        <div className="bg-gray-100 rounded-lg p-1 flex">
          <Button
            variant={viewMode === 'first_available' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('first_available')}
            className="rounded-md"
          >
            <Zap className="w-4 h-4 mr-2" />
            First Available
          </Button>
          <Button
            variant={viewMode === 'calendar' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('calendar')}
            className="rounded-md"
          >
            <Calendar className="w-4 h-4 mr-2" />
            All Appointments
          </Button>
        </div>
      </div>

      {/* Loading State */}
      {isLoadingSlots && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading available time slots...</p>
          </CardContent>
        </Card>
      )}

      {/* First Available Mode */}
      {viewMode === 'first_available' && !isLoadingSlots && (
        <div className="space-y-4">
          {selectedSlot && selectedDate ? (
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="text-green-900 flex items-center">
                  <Zap className="w-5 h-5 mr-2" />
                  Next Available Appointment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-green-900">
                        {formatDate(selectedDate)}
                      </p>
                      <p className="text-green-700">
                        {formatTime(selectedSlot.start)} - {formatTime(selectedSlot.end)}
                      </p>
                    </div>
                    {selectedSlot.price && (
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        ${(selectedSlot.price / 100).toFixed(0)} starting
                      </Badge>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-green-700">
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      2 hours estimated
                    </div>
                    {state.zipInfo?.emergencyAvailable && (
                      <div className="flex items-center">
                        <Zap className="w-4 h-4 mr-1" />
                        Emergency available
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="p-6 text-center">
                <AlertCircle className="w-8 h-8 text-orange-600 mx-auto mb-3" />
                <h3 className="font-semibold text-orange-900 mb-2">
                  No immediate availability
                </h3>
                <p className="text-orange-700 mb-4">
                  Switch to "All Appointments" to see available times
                </p>
                <Button
                  variant="outline"
                  onClick={() => setViewMode('calendar')}
                  className="border-orange-300 text-orange-700 hover:bg-orange-100"
                >
                  View Calendar
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Calendar Mode */}
      {viewMode === 'calendar' && !isLoadingSlots && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Calendar */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </CardTitle>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-1 mb-4">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                    {day}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {getDaysInMonth(currentMonth).map((date, index) => {
                  if (!date) {
                    return <div key={index} className="p-2"></div>;
                  }

                  const dateStr = date.toISOString().split('T')[0];
                  const hasSlots = hasAvailableSlots(date);
                  const isSelected = selectedDate === dateStr;
                  const disabled = isPast(date) || !hasSlots;

                  return (
                    <button
                      key={index}
                      onClick={() => !disabled && handleDateSelect(dateStr)}
                      disabled={disabled}
                      className={`
                        p-2 text-sm rounded-md transition-colors relative
                        ${disabled 
                          ? 'text-gray-300 cursor-not-allowed' 
                          : 'text-gray-900 hover:bg-blue-50 cursor-pointer'
                        }
                        ${isSelected ? 'bg-blue-500 text-white hover:bg-blue-600' : ''}
                        ${isToday(date) && !isSelected ? 'bg-blue-100 font-semibold' : ''}
                      `}
                    >
                      {date.getDate()}
                      {hasSlots && !isSelected && (
                        <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-green-500 rounded-full"></div>
                      )}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Time Slots */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                Available Times
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedDate ? (
                availableSlotsForDate.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600 mb-3">
                      {formatDate(selectedDate)}
                    </p>
                    {availableSlotsForDate.map((slot, index) => (
                      <button
                        key={index}
                        onClick={() => handleSlotSelect(slot)}
                        className={`
                          w-full p-3 rounded-md border text-left transition-colors
                          ${selectedSlot === slot
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-blue-300 hover:bg-blue-25'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">
                              {formatTime(slot.start)} - {formatTime(slot.end)}
                            </p>
                            {slot.isEmergency && (
                              <Badge variant="destructive" className="text-xs mt-1">
                                After Hours
                              </Badge>
                            )}
                          </div>
                          {slot.price && (
                            <Badge variant="outline" className="text-xs">
                              ${(slot.price / 100).toFixed(0)}
                            </Badge>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Clock className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-500">No available times on this date</p>
                  </div>
                )
              ) : (
                <div className="text-center py-8">
                  <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">Select a date to see available times</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Continue Button */}
      {selectedSlot && selectedDate && (
        <div className="flex justify-center pt-4">
          <Button
            onClick={handleContinue}
            size="lg"
            className="px-8"
          >
            Continue to Contact Info
          </Button>
        </div>
      )}

      {/* Emergency Contact */}
      {state.zipInfo?.emergencyAvailable && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <Zap className="w-5 h-5 text-red-600" />
              <div>
                <p className="text-sm font-medium text-red-900">
                  Need emergency service?
                </p>
                <p className="text-xs text-red-700">
                  Call us directly for immediate assistance: {state.zipInfo.emergencyAvailable ? 'Available 24/7' : 'Available during business hours'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
