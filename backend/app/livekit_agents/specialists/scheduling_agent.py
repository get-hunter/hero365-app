"""
Scheduling management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List
import uuid
from datetime import datetime
import logging

from livekit.agents import llm, function_tool
from ..base_agent import Hero365BaseAgent
from ..config import LiveKitConfig

logger = logging.getLogger(__name__)


class SchedulingAgent(Hero365BaseAgent):
    """Specialist agent for scheduling and calendar management using LiveKit agents"""
    
    def __init__(self, config: LiveKitConfig):
        """
        Initialize scheduling management specialist.
        
        Args:
            config: LiveKit configuration
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        instructions = f"""
        You are the scheduling specialist for Hero365. You help users manage their 
        calendar and scheduling efficiently and professionally.
        
        CURRENT DATE AND TIME: Today is {current_date} at {current_time}
        
        You have access to tools for:
        - Checking availability and time slots
        - Booking appointments
        - Managing calendar events
        - Viewing schedules
        - Rescheduling appointments
        - Getting scheduling suggestions
        
        Always be helpful and ask for clarification if needed. When booking appointments,
        collect the required information naturally through conversation.
        
        APPOINTMENT INFORMATION PRIORITY:
        1. Contact ID (required)
        2. Date (required)
        3. Time (required)
        4. Duration (optional, default 60 minutes)
        5. Service type and notes (optional)
        """
        
        super().__init__(
            name="Scheduling Management Specialist",
            instructions=instructions
        )
    
    @function_tool
    async def get_available_time_slots(self,
                                      date: str,
                                      duration: int = 60,
                                      service_type: Optional[str] = None) -> str:
        """Find available time slots for a given date"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the intelligent scheduling use case
            intelligent_scheduling_use_case = self.container.get_intelligent_scheduling_use_case()
            
            from ...application.dto.scheduling_dto import AvailabilityCheckDTO
            
            # Execute use case
            result = await intelligent_scheduling_use_case.execute(
                AvailabilityCheckDTO(
                    date=date,
                    duration=duration,
                    service_type=service_type,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.available_slots:
                return f"No available time slots found for {date}"
            
            slots_text = "\n".join([
                f"• {slot.start_time} - {slot.end_time}" + (f" ({slot.notes})" if slot.notes else "")
                for slot in result.available_slots
            ])
            
            return f"📅 Available time slots for {date}:\n{slots_text}"
            
        except Exception as e:
            logger.error(f"Error getting available time slots: {e}")
            return f"❌ I encountered an error while checking availability: {str(e)}"
    
    @function_tool
    async def book_appointment(self,
                              contact_id: str,
                              date: str,
                              time: str,
                              duration: int = 60,
                              service_type: Optional[str] = None,
                              notes: Optional[str] = None) -> str:
        """Book an appointment with the provided information"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            from ...application.dto.scheduling_dto import BookAppointmentDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                BookAppointmentDTO(
                    contact_id=contact_id,
                    date=date,
                    time=time,
                    duration=duration,
                    service_type=service_type,
                    notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Appointment booked successfully for {date} at {time}! Appointment ID: {result.appointment_id}"
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return f"❌ I encountered an error while booking the appointment: {str(e)}"
    
    @function_tool
    async def check_availability(self, date: str, time: Optional[str] = None) -> str:
        """Check availability for a specific date and optionally time"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the availability checking use case
            availability_use_case = self.container.get_availability_checking_use_case()
            
            from ...application.dto.scheduling_dto import CheckAvailabilityDTO
            
            # Execute use case
            result = await availability_use_case.execute(
                CheckAvailabilityDTO(
                    date=date,
                    time=time,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if result.is_available:
                time_str = f" at {time}" if time else ""
                return f"✅ You are available on {date}{time_str}"
            else:
                return f"❌ You are not available on {date}" + (f" at {time}" if time else "")
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return f"❌ I encountered an error while checking availability: {str(e)}"
    
    @function_tool
    async def get_today_schedule(self) -> str:
        """Get today's schedule and appointments"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the schedule viewing use case
            schedule_use_case = self.container.get_schedule_viewing_use_case()
            
            from ...application.dto.scheduling_dto import GetScheduleDTO
            
            # Execute use case
            result = await schedule_use_case.execute(
                GetScheduleDTO(
                    date="today",
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.appointments:
                return "📅 You have no appointments scheduled for today"
            
            appointments_text = "\n".join([
                f"• {appt.time} - {appt.title}" + (f" with {appt.contact_name}" if appt.contact_name else "")
                for appt in result.appointments
            ])
            
            return f"📅 Today's schedule:\n{appointments_text}"
            
        except Exception as e:
            logger.error(f"Error getting today's schedule: {e}")
            return f"❌ I encountered an error while getting today's schedule: {str(e)}"
    
    @function_tool
    async def get_upcoming_appointments(self, days_ahead: int = 7) -> str:
        """Get upcoming appointments within the specified number of days"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the upcoming appointments use case
            upcoming_appointments_use_case = self.container.get_upcoming_appointments_use_case()
            
            from ...application.dto.scheduling_dto import GetUpcomingAppointmentsDTO
            
            # Execute use case
            result = await upcoming_appointments_use_case.execute(
                GetUpcomingAppointmentsDTO(
                    days_ahead=days_ahead,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.appointments:
                return f"📅 No upcoming appointments in the next {days_ahead} days"
            
            appointments_text = "\n".join([
                f"• {appt.date} {appt.time} - {appt.title}" + (f" with {appt.contact_name}" if appt.contact_name else "")
                for appt in result.appointments
            ])
            
            return f"📅 Upcoming appointments in the next {days_ahead} days:\n{appointments_text}"
            
        except Exception as e:
            logger.error(f"Error getting upcoming appointments: {e}")
            return f"❌ I encountered an error while getting upcoming appointments: {str(e)}"
    
    @function_tool
    async def reschedule_appointment(self,
                                    appointment_id: str,
                                    new_date: str,
                                    new_time: str,
                                    reason: Optional[str] = None) -> str:
        """Reschedule an existing appointment"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the reschedule appointment use case
            reschedule_use_case = self.container.get_reschedule_appointment_use_case()
            
            from ...application.dto.scheduling_dto import RescheduleAppointmentDTO
            
            # Execute use case
            result = await reschedule_use_case.execute(
                RescheduleAppointmentDTO(
                    appointment_id=appointment_id,
                    new_date=new_date,
                    new_time=new_time,
                    reason=reason,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Appointment rescheduled successfully to {new_date} at {new_time}!"
            
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {e}")
            return f"❌ I encountered an error while rescheduling the appointment: {str(e)}"
    
    @function_tool
    async def get_schedule_summary(self, date: str) -> str:
        """Get a summary of appointments for a specific date"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the schedule viewing use case
            schedule_use_case = self.container.get_schedule_viewing_use_case()
            
            from ...application.dto.scheduling_dto import GetScheduleDTO
            
            # Execute use case
            result = await schedule_use_case.execute(
                GetScheduleDTO(
                    date=date,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.appointments:
                return f"📅 No appointments scheduled for {date}"
            
            total_appointments = len(result.appointments)
            total_hours = sum(appt.duration for appt in result.appointments if appt.duration) / 60
            
            appointments_text = "\n".join([
                f"• {appt.time} - {appt.title}" + (f" ({appt.duration}min)" if appt.duration else "")
                for appt in result.appointments
            ])
            
            summary = f"""
📅 Schedule Summary for {date}:
• Total Appointments: {total_appointments}
• Total Hours: {total_hours:.1f}

Appointments:
{appointments_text}
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error getting schedule summary: {e}")
            return f"❌ I encountered an error while getting schedule summary: {str(e)}"
    
    @function_tool
    async def find_next_available_slot(self, duration: int = 60, service_type: Optional[str] = None) -> str:
        """Find the next available time slot"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the intelligent scheduling use case
            intelligent_scheduling_use_case = self.container.get_intelligent_scheduling_use_case()
            
            from ...application.dto.scheduling_dto import AvailabilityCheckDTO
            from datetime import datetime, timedelta
            
            # Check availability for the next 7 days
            today = datetime.now()
            for i in range(7):
                check_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
                
                result = await intelligent_scheduling_use_case.execute(
                    AvailabilityCheckDTO(
                        date=check_date,
                        duration=duration,
                        service_type=service_type,
                        business_id=business_id
                    ),
                    user_id=user_id
                )
                
                if result.available_slots:
                    first_slot = result.available_slots[0]
                    return f"✅ Next available slot: {check_date} at {first_slot.start_time} - {first_slot.end_time}"
            
            return "❌ No available slots found in the next 7 days"
            
        except Exception as e:
            logger.error(f"Error finding next available slot: {e}")
            return f"❌ I encountered an error while finding the next available slot: {str(e)}"
    
    def get_specialist_capabilities(self) -> List[str]:
        """Get list of capabilities for this specialist agent"""
        return [
            "Check availability and find open time slots",
            "Book appointments with contact information and scheduling details",
            "View today's schedule and upcoming appointments",
            "Reschedule existing appointments",
            "Get scheduling suggestions and recommendations",
            "Find next available time slots",
            "Get schedule summaries and overviews",
            "Natural conversation for scheduling management",
            "Automatic parameter collection through conversation"
        ]
    
    async def initialize_agent(self, ctx):
        """Initialize scheduling agent"""
        logger.info("📅 Scheduling Agent initialized")
    
    async def cleanup_agent(self, ctx):
        """Clean up scheduling agent"""
        logger.info("👋 Scheduling Agent cleaned up")
    
    async def process_message(self, ctx, message: str) -> str:
        """Process user message"""
        # Process scheduling-related messages
        return f"Scheduling agent processing: {message}" 