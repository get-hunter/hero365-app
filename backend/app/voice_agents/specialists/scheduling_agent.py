"""
Scheduling management specialist agent for Hero365 voice system.
"""

from typing import Optional, List
from agents import Agent, function_tool
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
import logging

logger = logging.getLogger(__name__)


class SchedulingAgent(BaseVoiceAgent):
    """Specialist agent for scheduling and calendar management using OpenAI Agents SDK"""
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize scheduling management specialist.
        
        Args:
            context_manager: Shared context manager
        """
        instructions = """
        You are the scheduling specialist for Hero365. You help users manage their 
        calendar and scheduling efficiently and professionally.
        
        You have access to tools for:
        - Checking availability and time slots
        - Booking appointments
        - Managing calendar events
        - Viewing schedules
        - Rescheduling appointments
        - Getting scheduling suggestions
        
        Always be helpful and ask for clarification if needed. When booking appointments,
        collect the required information naturally through conversation.
        """
        
        # Create the OpenAI Agents SDK agent with function tools
        self.sdk_agent = Agent(
            name="Scheduling Management Specialist",
            instructions=instructions,
            tools=[
                self._get_available_time_slots_tool,
                self._book_appointment_tool,
                self._check_availability_tool,
                self._get_today_schedule_tool,
                self._get_upcoming_appointments_tool,
                self._reschedule_appointment_tool
            ]
        )
        
        super().__init__(
            name="Scheduling Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[]
        )
    
    @function_tool
    async def _get_available_time_slots_tool(self,
                                            date: str,
                                            duration: int = 60,
                                            service_type: Optional[str] = None) -> str:
        """Find available time slots for a given date"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the intelligent scheduling use case
            intelligent_scheduling_use_case = self.container.get_intelligent_scheduling_use_case()
            
            # Import the DTO
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
    async def _book_appointment_tool(self,
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
            
            # Import the DTO
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
    async def _check_availability_tool(self, date: str, time: Optional[str] = None) -> str:
        """Check availability for a specific date and optionally time"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the availability checking use case
            availability_use_case = self.container.get_availability_checking_use_case()
            
            # Import the DTO
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
    async def _get_today_schedule_tool(self) -> str:
        """Get today's schedule and appointments"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the schedule viewing use case
            schedule_use_case = self.container.get_schedule_viewing_use_case()
            
            # Import the DTO
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
    async def _get_upcoming_appointments_tool(self, days_ahead: int = 7) -> str:
        """Get upcoming appointments within the specified number of days"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the upcoming appointments use case
            upcoming_appointments_use_case = self.container.get_upcoming_appointments_use_case()
            
            # Import the DTO
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
    async def _reschedule_appointment_tool(self,
                                          appointment_id: str,
                                          new_date: str,
                                          new_time: str,
                                          reason: Optional[str] = None) -> str:
        """Reschedule an existing appointment"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the reschedule appointment use case
            reschedule_use_case = self.container.get_reschedule_appointment_use_case()
            
            # Import the DTO
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
    
    async def get_response(self, text_input: str) -> str:
        """
        Get response from the scheduling agent using OpenAI Agents SDK.
        
        Args:
            text_input: User's input text
            
        Returns:
            Response from the agent
        """
        try:
            from agents import Runner
            
            logger.info(f"📅 Scheduling agent processing: {text_input}")
            
            # Use the OpenAI Agents SDK to process the request
            result = await Runner.run(
                starting_agent=self.sdk_agent,
                input=text_input
            )
            
            response = result.final_output
            logger.info(f"✅ Scheduling agent response: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in SchedulingAgent.get_response: {e}")
            return "I'm having trouble with that request. Could you please be more specific about what you'd like to do with scheduling?"
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Check availability and find open time slots",
            "Book appointments with contact information and scheduling details",
            "View today's schedule and upcoming appointments",
            "Reschedule existing appointments",
            "Get scheduling suggestions and recommendations",
            "Manage calendar events and time blocks",
            "Natural conversation for scheduling management",
            "Automatic parameter collection through conversation"
        ] 