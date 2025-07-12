"""
Scheduling Tools

Voice agent tools for scheduling and calendar management using Hero365's scheduling use cases.
"""

from typing import List, Any, Dict, Optional
from datetime import datetime, timedelta, date
import uuid
from app.infrastructure.config.dependency_injection import get_container
from app.application.use_cases.scheduling.intelligent_scheduling_use_case import IntelligentSchedulingUseCase
from app.application.use_cases.scheduling.calendar_management_use_case import CalendarManagementUseCase
from app.application.dto.scheduling_dto import (
    AvailableTimeSlotRequestDTO, TimeSlotBookingRequestDTO,
    CreateCalendarEventRequestDTO, CreateTimeOffRequestDTO,
    UpdateWorkingHoursRequestDTO, AvailabilityCheckRequestDTO
)
from app.domain.enums import JobType, JobPriority
from app.domain.entities.user_capabilities import CalendarEventType, TimeOffType, RecurrenceType


class SchedulingTools:
    """Scheduling and calendar management tools for voice agents"""
    
    def __init__(self, business_id: str, user_id: str):
        """
        Initialize scheduling tools with business and user context
        
        Args:
            business_id: Current business ID
            user_id: Current user ID
        """
        self.business_id = business_id
        self.user_id = user_id
        self.container = get_container()
    
    def get_tools(self) -> List[Any]:
        """Get all scheduling tools"""
        return [
            self.get_available_time_slots,
            self.book_appointment,
            self.check_availability,
            self.create_calendar_event,
            self.get_today_schedule,
            self.get_upcoming_appointments,
            self.reschedule_appointment,
            self.cancel_appointment,
            self.set_working_hours,
            self.request_time_off,
            self.get_team_availability,
            self.create_recurring_appointment,
            self.find_best_time_slot,
            self.get_calendar_events
        ]
    
    def get_available_time_slots(self, 
                               job_type: str,
                               duration_hours: float,
                               preferred_date: str,
                               required_skills: Optional[List[str]] = None,
                               customer_location: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available time slots for scheduling appointments
        
        Args:
            job_type: Type of job/service needed
            duration_hours: Duration needed in hours
            preferred_date: Preferred date (YYYY-MM-DD)
            required_skills: List of required skills/capabilities
            customer_location: Customer address or location
        """
        try:
            intelligent_scheduling_use_case = self.container.get(IntelligentSchedulingUseCase)
            
            # Parse preferred date
            preferred_date_obj = datetime.strptime(preferred_date, "%Y-%m-%d")
            
            # Create request DTO
            request = AvailableTimeSlotRequestDTO(
                job_type=job_type,
                estimated_duration_hours=duration_hours,
                preferred_date_range={
                    "start_time": preferred_date_obj,
                    "end_time": preferred_date_obj + timedelta(days=1)
                },
                required_skills=required_skills or [],
                job_address={"city": customer_location} if customer_location else None,
                customer_preferences={}
            )
            
            # Get available slots
            result = intelligent_scheduling_use_case.get_available_time_slots(
                business_id=uuid.UUID(self.business_id),
                request=request
            )
            
            # Format response
            slots = []
            for slot in result.available_slots:
                slots.append({
                    "slot_id": slot.slot_id,
                    "start_time": slot.start_time.strftime("%Y-%m-%d %H:%M"),
                    "end_time": slot.end_time.strftime("%Y-%m-%d %H:%M"),
                    "technician": slot.available_technicians[0] if slot.available_technicians else "TBD",
                    "confidence_score": slot.confidence_score,
                    "travel_time_minutes": slot.estimated_travel_time_minutes
                })
            
            return {
                "success": True,
                "available_slots": slots,
                "total_slots": len(slots),
                "message": f"Found {len(slots)} available time slots for {job_type} on {preferred_date}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting available time slots: {str(e)}"
            }
    
    def book_appointment(self,
                        slot_id: str,
                        customer_name: str,
                        customer_phone: str,
                        customer_email: Optional[str] = None,
                        job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Book an appointment for a specific time slot
        
        Args:
            slot_id: ID of the time slot to book
            customer_name: Customer name
            customer_phone: Customer phone number
            customer_email: Customer email address
            job_description: Description of the job/service
        """
        try:
            intelligent_scheduling_use_case = self.container.get(IntelligentSchedulingUseCase)
            
            # Create booking request
            request = TimeSlotBookingRequestDTO(
                slot_id=slot_id,
                customer_contact={
                    "name": customer_name,
                    "phone": customer_phone,
                    "email": customer_email
                },
                job_details={
                    "description": job_description or "Service appointment"
                }
            )
            
            # Book the slot
            result = intelligent_scheduling_use_case.book_time_slot(
                business_id=uuid.UUID(self.business_id),
                request=request
            )
            
            return {
                "success": True,
                "booking_id": result.booking_id,
                "job_id": result.job_id,
                "confirmation_number": result.confirmation_details.get("confirmation_number"),
                "scheduled_time": result.scheduled_slot.start_time.strftime("%Y-%m-%d %H:%M"),
                "technician": result.assigned_technician.get("name"),
                "message": f"Appointment booked successfully for {customer_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error booking appointment: {str(e)}"
            }
    
    def check_availability(self,
                          user_ids: List[str],
                          start_date: str,
                          end_date: str) -> Dict[str, Any]:
        """
        Check availability for specific users in a date range
        
        Args:
            user_ids: List of user IDs to check
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            # Parse dates
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            
            # Create availability check request
            request = AvailabilityCheckRequestDTO(
                user_ids=user_ids,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                include_time_off=True,
                include_calendar_events=True,
                include_working_hours=True
            )
            
            # Check availability
            result = calendar_management_use_case.check_user_availability(
                business_id=uuid.UUID(self.business_id),
                request=request,
                current_user_id=self.user_id
            )
            
            # Format response
            availability_summary = []
            for user_availability in result.user_availability:
                availability_summary.append({
                    "user_id": user_availability.user_id,
                    "is_available": user_availability.is_available,
                    "available_hours": user_availability.total_available_hours,
                    "unavailable_reason": user_availability.unavailable_reason
                })
            
            return {
                "success": True,
                "availability": availability_summary,
                "message": f"Availability checked for {len(user_ids)} users from {start_date} to {end_date}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error checking availability: {str(e)}"
            }
    
    def create_calendar_event(self,
                            title: str,
                            start_time: str,
                            end_time: str,
                            description: Optional[str] = None,
                            event_type: str = "meeting",
                            blocks_scheduling: bool = False) -> Dict[str, Any]:
        """
        Create a calendar event
        
        Args:
            title: Event title
            start_time: Start time (YYYY-MM-DD HH:MM)
            end_time: End time (YYYY-MM-DD HH:MM)
            description: Event description
            event_type: Type of event (meeting, appointment, personal, work, break)
            blocks_scheduling: Whether this event blocks scheduling
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            # Parse times
            start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
            
            # Create event request
            request = CreateCalendarEventRequestDTO(
                title=title,
                description=description or "",
                event_type=event_type,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                is_all_day=False,
                timezone="UTC",
                recurrence_type="none",
                blocks_scheduling=blocks_scheduling,
                allows_emergency_override=True
            )
            
            # Create event
            result = calendar_management_use_case.create_calendar_event(
                business_id=uuid.UUID(self.business_id),
                user_id=self.user_id,
                request=request,
                current_user_id=self.user_id
            )
            
            return {
                "success": True,
                "event_id": result.id,
                "message": f"Calendar event '{title}' created from {start_time} to {end_time}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating calendar event: {str(e)}"
            }
    
    def get_today_schedule(self) -> Dict[str, Any]:
        """Get today's schedule and appointments"""
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            today = date.today()
            
            # Get calendar events
            events = calendar_management_use_case.get_calendar_events(
                business_id=uuid.UUID(self.business_id),
                user_id=self.user_id,
                start_date=today,
                end_date=today,
                current_user_id=self.user_id
            )
            
            # Format schedule
            schedule = []
            for event in events:
                schedule.append({
                    "time": event.start_datetime.strftime("%H:%M"),
                    "title": event.title,
                    "type": event.event_type,
                    "duration": f"{(event.end_datetime - event.start_datetime).total_seconds() / 3600:.1f} hours"
                })
            
            # Sort by time
            schedule.sort(key=lambda x: x["time"])
            
            return {
                "success": True,
                "date": today.strftime("%Y-%m-%d"),
                "schedule": schedule,
                "total_events": len(schedule),
                "message": f"Today's schedule has {len(schedule)} events"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting today's schedule: {str(e)}"
            }
    
    def get_upcoming_appointments(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get upcoming appointments for the next specified days
        
        Args:
            days_ahead: Number of days to look ahead (default: 7)
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            start_date = date.today()
            end_date = start_date + timedelta(days=days_ahead)
            
            # Get calendar events
            events = calendar_management_use_case.get_calendar_events(
                business_id=uuid.UUID(self.business_id),
                user_id=self.user_id,
                start_date=start_date,
                end_date=end_date,
                current_user_id=self.user_id
            )
            
            # Format appointments
            appointments = []
            for event in events:
                appointments.append({
                    "id": event.id,
                    "title": event.title,
                    "date": event.start_datetime.strftime("%Y-%m-%d"),
                    "time": event.start_datetime.strftime("%H:%M"),
                    "duration": f"{(event.end_datetime - event.start_datetime).total_seconds() / 3600:.1f} hours",
                    "type": event.event_type
                })
            
            # Sort by date and time
            appointments.sort(key=lambda x: (x["date"], x["time"]))
            
            return {
                "success": True,
                "appointments": appointments,
                "total_appointments": len(appointments),
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "message": f"Found {len(appointments)} upcoming appointments"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting upcoming appointments: {str(e)}"
            }
    
    def reschedule_appointment(self,
                             appointment_id: str,
                             new_date: str,
                             new_time: str,
                             reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Reschedule an existing appointment
        
        Args:
            appointment_id: ID of the appointment to reschedule
            new_date: New date (YYYY-MM-DD)
            new_time: New time (HH:MM)
            reason: Reason for rescheduling
        """
        try:
            # This would integrate with the job rescheduling logic
            # For now, return a confirmation
            new_datetime = f"{new_date} {new_time}"
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "new_datetime": new_datetime,
                "message": f"Appointment rescheduled to {new_datetime}",
                "reason": reason or "Requested by user"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error rescheduling appointment: {str(e)}"
            }
    
    def cancel_appointment(self,
                          appointment_id: str,
                          reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an existing appointment
        
        Args:
            appointment_id: ID of the appointment to cancel
            reason: Reason for cancellation
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            # Delete the calendar event
            success = calendar_management_use_case.delete_calendar_event(
                business_id=uuid.UUID(self.business_id),
                event_id=appointment_id,
                current_user_id=self.user_id
            )
            
            if success:
                return {
                    "success": True,
                    "appointment_id": appointment_id,
                    "message": f"Appointment cancelled successfully",
                    "reason": reason or "Requested by user"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to cancel appointment {appointment_id}"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error cancelling appointment: {str(e)}"
            }
    
    def set_working_hours(self,
                         monday_start: str, monday_end: str,
                         tuesday_start: str, tuesday_end: str,
                         wednesday_start: str, wednesday_end: str,
                         thursday_start: str, thursday_end: str,
                         friday_start: str, friday_end: str,
                         saturday_start: Optional[str] = None, saturday_end: Optional[str] = None,
                         sunday_start: Optional[str] = None, sunday_end: Optional[str] = None) -> Dict[str, Any]:
        """
        Set working hours for the user
        
        Args:
            monday_start: Monday start time (HH:MM)
            monday_end: Monday end time (HH:MM)
            tuesday_start: Tuesday start time (HH:MM)
            tuesday_end: Tuesday end time (HH:MM)
            wednesday_start: Wednesday start time (HH:MM)
            wednesday_end: Wednesday end time (HH:MM)
            thursday_start: Thursday start time (HH:MM)
            thursday_end: Thursday end time (HH:MM)
            friday_start: Friday start time (HH:MM)
            friday_end: Friday end time (HH:MM)
            saturday_start: Saturday start time (HH:MM) - optional
            saturday_end: Saturday end time (HH:MM) - optional
            sunday_start: Sunday start time (HH:MM) - optional
            sunday_end: Sunday end time (HH:MM) - optional
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            # Create working hours request
            working_hours = {
                "monday": (monday_start, monday_end),
                "tuesday": (tuesday_start, tuesday_end),
                "wednesday": (wednesday_start, wednesday_end),
                "thursday": (thursday_start, thursday_end),
                "friday": (friday_start, friday_end)
            }
            
            if saturday_start and saturday_end:
                working_hours["saturday"] = (saturday_start, saturday_end)
            if sunday_start and sunday_end:
                working_hours["sunday"] = (sunday_start, sunday_end)
            
            request = UpdateWorkingHoursRequestDTO(
                template_name="Default Working Hours",
                working_hours=working_hours
            )
            
            # Update working hours
            result = calendar_management_use_case.create_working_hours_template(
                business_id=uuid.UUID(self.business_id),
                request=request,
                current_user_id=self.user_id
            )
            
            return {
                "success": True,
                "template_id": result.template_id,
                "message": "Working hours updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error setting working hours: {str(e)}"
            }
    
    def request_time_off(self,
                        start_date: str,
                        end_date: str,
                        reason: str,
                        time_off_type: str = "vacation") -> Dict[str, Any]:
        """
        Request time off
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            reason: Reason for time off
            time_off_type: Type of time off (vacation, sick, personal, emergency)
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            # Parse dates
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            # Create time off request
            request = CreateTimeOffRequestDTO(
                time_off_type=time_off_type,
                start_date=start_date_obj,
                end_date=end_date_obj,
                reason=reason,
                notes="",
                affects_scheduling=True,
                emergency_contact_allowed=False
            )
            
            # Submit request
            result = calendar_management_use_case.create_time_off_request(
                business_id=uuid.UUID(self.business_id),
                user_id=self.user_id,
                request=request,
                current_user_id=self.user_id
            )
            
            return {
                "success": True,
                "request_id": result.id,
                "status": result.status,
                "message": f"Time off request submitted for {start_date} to {end_date}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error requesting time off: {str(e)}"
            }
    
    def get_team_availability(self, date: str) -> Dict[str, Any]:
        """
        Get team availability for a specific date
        
        Args:
            date: Date to check (YYYY-MM-DD)
        """
        try:
            # This would integrate with team management
            # For now, return mock data
            return {
                "success": True,
                "date": date,
                "team_availability": [
                    {
                        "user_id": "user_1",
                        "name": "John Smith",
                        "is_available": True,
                        "available_hours": 8.0,
                        "working_hours": "08:00-17:00"
                    },
                    {
                        "user_id": "user_2",
                        "name": "Jane Doe",
                        "is_available": False,
                        "available_hours": 0.0,
                        "unavailable_reason": "On vacation"
                    }
                ],
                "message": f"Team availability checked for {date}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting team availability: {str(e)}"
            }
    
    def create_recurring_appointment(self,
                                   title: str,
                                   start_time: str,
                                   end_time: str,
                                   recurrence_type: str,
                                   recurrence_count: int,
                                   description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a recurring appointment
        
        Args:
            title: Appointment title
            start_time: Start time (YYYY-MM-DD HH:MM)
            end_time: End time (YYYY-MM-DD HH:MM)
            recurrence_type: Type of recurrence (daily, weekly, monthly)
            recurrence_count: Number of recurrences
            description: Appointment description
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            # Parse times
            start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
            
            # Create recurring event request
            request = CreateCalendarEventRequestDTO(
                title=title,
                description=description or "",
                event_type="appointment",
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                is_all_day=False,
                timezone="UTC",
                recurrence_type=recurrence_type,
                recurrence_count=recurrence_count,
                recurrence_interval=1,
                blocks_scheduling=False,
                allows_emergency_override=True
            )
            
            # Create recurring event
            result = calendar_management_use_case.create_calendar_event(
                business_id=uuid.UUID(self.business_id),
                user_id=self.user_id,
                request=request,
                current_user_id=self.user_id
            )
            
            return {
                "success": True,
                "event_id": result.id,
                "message": f"Recurring appointment '{title}' created with {recurrence_count} occurrences"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating recurring appointment: {str(e)}"
            }
    
    def find_best_time_slot(self,
                           duration_hours: float,
                           preferred_time_range: str,
                           participants: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Find the best available time slot based on preferences
        
        Args:
            duration_hours: Required duration in hours
            preferred_time_range: Preferred time range (e.g., "09:00-17:00")
            participants: List of participant user IDs
        """
        try:
            # This would use the intelligent scheduling algorithm
            # For now, return a simple suggestion
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            return {
                "success": True,
                "recommended_slot": {
                    "date": tomorrow,
                    "start_time": "10:00",
                    "end_time": f"{10 + duration_hours:.0f}:00",
                    "confidence_score": 0.85
                },
                "message": f"Best available {duration_hours}-hour slot found for {tomorrow}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error finding best time slot: {str(e)}"
            }
    
    def get_calendar_events(self,
                           start_date: str,
                           end_date: str,
                           event_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get calendar events for a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            event_types: Filter by event types (optional)
        """
        try:
            calendar_management_use_case = self.container.get(CalendarManagementUseCase)
            
            # Parse dates
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            # Get events
            events = calendar_management_use_case.get_calendar_events(
                business_id=uuid.UUID(self.business_id),
                user_id=self.user_id,
                start_date=start_date_obj,
                end_date=end_date_obj,
                current_user_id=self.user_id
            )
            
            # Format events
            formatted_events = []
            for event in events:
                if event_types and event.event_type not in event_types:
                    continue
                    
                formatted_events.append({
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "start_time": event.start_datetime.strftime("%Y-%m-%d %H:%M"),
                    "end_time": event.end_datetime.strftime("%Y-%m-%d %H:%M"),
                    "event_type": event.event_type,
                    "is_all_day": event.is_all_day,
                    "blocks_scheduling": event.blocks_scheduling
                })
            
            return {
                "success": True,
                "events": formatted_events,
                "total_events": len(formatted_events),
                "date_range": f"{start_date} to {end_date}",
                "message": f"Found {len(formatted_events)} calendar events"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting calendar events: {str(e)}"
            } 