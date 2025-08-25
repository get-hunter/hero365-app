/**
 * Date Time Selector Component
 * 
 * Allows customers to select their preferred appointment date and time
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Calendar } from '../ui/calendar';
import { Calendar as CalendarIcon, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { format, addDays, isSameDay, isAfter, isBefore, startOfDay } from 'date-fns';
import { cn } from '../../lib/utils';

import { DateTimeSelectorProps, TimeSlot, AvailabilityRequest } from '../../lib/types/booking';
import { bookingApi } from '../../lib/api/booking-client';

export default function DateTimeSelector({
  businessId,
  serviceId,
  selectedDate,
  selectedTimeSlot,
  onDateSelect,
  onTimeSlotSelect,
  className
}: DateTimeSelectorProps) {
  const [availableSlots, setAvailableSlots] = useState<Record<string, TimeSlot[]>>({});
  const [isLoadingAvailability, setIsLoadingAvailability] = useState(false);
  const [availabilityError, setAvailabilityError] = useState<string | null>(null);
  const [calendarMonth, setCalendarMonth] = useState<Date>(new Date());

  // Load availability when service or month changes
  useEffect(() => {
    if (serviceId) {
      loadAvailability();
    }
  }, [serviceId, calendarMonth]);

  const loadAvailability = async () => {
    setIsLoadingAvailability(true);
    setAvailabilityError(null);

    try {
      const startDate = startOfDay(calendarMonth);
      const endDate = addDays(startDate, 30); // Load 30 days of availability

      const request: AvailabilityRequest = {
        business_id: businessId,
        service_id: serviceId,
        start_date: bookingApi.formatDate(startDate),
        end_date: bookingApi.formatDate(endDate),
      };

      const response = await bookingApi.getAvailability(request);
      setAvailableSlots(response.available_dates);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load availability';
      setAvailabilityError(errorMessage);
      setAvailableSlots({});
    } finally {
      setIsLoadingAvailability(false);
    }
  };

  const getAvailableDates = (): Date[] => {
    return Object.keys(availableSlots)
      .map(dateStr => new Date(dateStr))
      .filter(date => availableSlots[bookingApi.formatDate(date)]?.length > 0);
  };

  const getTimeSlotsForDate = (date: Date): TimeSlot[] => {
    const dateStr = bookingApi.formatDate(date);
    return availableSlots[dateStr] || [];
  };

  const formatTimeSlot = (slot: TimeSlot): string => {
    const startTime = new Date(slot.start_time);
    const endTime = new Date(slot.end_time);
    return `${format(startTime, 'h:mm a')} - ${format(endTime, 'h:mm a')}`;
  };

  const isDateAvailable = (date: Date): boolean => {
    const dateStr = bookingApi.formatDate(date);
    const slots = availableSlots[dateStr];
    return slots && slots.length > 0 && slots.some(slot => slot.capacity > slot.booked_count);
  };

  const isDateDisabled = (date: Date): boolean => {
    const today = startOfDay(new Date());
    return isBefore(date, today) || !isDateAvailable(date);
  };

  const handleDateSelect = (date: Date | undefined) => {
    if (date && !isDateDisabled(date)) {
      onDateSelect(date);
      // Clear selected time slot when date changes
      if (selectedTimeSlot && selectedDate && !isSameDay(date, selectedDate)) {
        onTimeSlotSelect(undefined as any);
      }
    }
  };

  const selectedDateSlots = selectedDate ? getTimeSlotsForDate(selectedDate) : [];

  return (
    <div className={cn("space-y-6", className)}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Select Date & Time</h3>
        <p className="text-gray-600">Choose your preferred appointment date and time slot.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Calendar */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="w-5 h-5" />
              Select Date
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingAvailability ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin mr-2" />
                <span>Loading availability...</span>
              </div>
            ) : availabilityError ? (
              <div className="text-center py-8">
                <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
                <p className="text-red-600 mb-4">{availabilityError}</p>
                <Button onClick={loadAvailability} variant="outline" size="sm">
                  Try Again
                </Button>
              </div>
            ) : (
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={handleDateSelect}
                disabled={isDateDisabled}
                month={calendarMonth}
                onMonthChange={setCalendarMonth}
                className="rounded-md border"
                modifiers={{
                  available: getAvailableDates(),
                }}
                modifiersStyles={{
                  available: {
                    backgroundColor: '#dbeafe',
                    color: '#1e40af',
                    fontWeight: 'bold',
                  },
                }}
              />
            )}

            {/* Legend */}
            <div className="mt-4 space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-100 border border-blue-300 rounded" />
                <span>Available dates</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-100 border border-gray-300 rounded" />
                <span>No availability</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Time Slots */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Select Time
              {selectedDate && (
                <Badge variant="outline" className="ml-2">
                  {format(selectedDate, 'MMM d, yyyy')}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedDate ? (
              <div className="text-center py-8 text-gray-500">
                <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Select a date to see available times</p>
              </div>
            ) : selectedDateSlots.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No available times for this date</p>
                <p className="text-sm mt-1">Please select a different date</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {selectedDateSlots.map((slot, index) => {
                  const isSelected = selectedTimeSlot?.start_time === slot.start_time;
                  const isAvailable = slot.capacity > slot.booked_count;
                  
                  return (
                    <Button
                      key={`${slot.start_time}-${index}`}
                      variant={isSelected ? "default" : "outline"}
                      className={cn(
                        "w-full justify-between h-auto p-3",
                        !isAvailable && "opacity-50 cursor-not-allowed"
                      )}
                      onClick={() => isAvailable && onTimeSlotSelect(slot)}
                      disabled={!isAvailable}
                    >
                      <div className="flex flex-col items-start">
                        <span className="font-medium">
                          {formatTimeSlot(slot)}
                        </span>
                        {slot.price && (
                          <span className="text-sm text-gray-500">
                            {new Intl.NumberFormat('en-US', {
                              style: 'currency',
                              currency: 'USD',
                            }).format(slot.price)}
                          </span>
                        )}
                      </div>
                      
                      <div className="flex flex-col items-end text-xs">
                        {isAvailable ? (
                          <>
                            <Badge variant="secondary" className="mb-1">
                              Available
                            </Badge>
                            {slot.capacity > 1 && (
                              <span className="text-gray-500">
                                {slot.capacity - slot.booked_count} spots left
                              </span>
                            )}
                          </>
                        ) : (
                          <Badge variant="destructive">
                            Fully Booked
                          </Badge>
                        )}
                      </div>
                    </Button>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Selected Summary */}
      {selectedDate && selectedTimeSlot && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <CalendarIcon className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h4 className="font-medium text-green-800">
                  Appointment Selected
                </h4>
                <p className="text-green-600">
                  {format(selectedDate, 'EEEE, MMMM d, yyyy')} at {formatTimeSlot(selectedTimeSlot)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Booking Information */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-medium text-blue-800 mb-2">Booking Information</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Appointments are confirmed within 2 hours</li>
          <li>• You'll receive a reminder 24 hours before your appointment</li>
          <li>• Rescheduling is available up to 24 hours in advance</li>
          <li>• Emergency services are available 24/7</li>
        </ul>
      </div>
    </div>
  );
}
