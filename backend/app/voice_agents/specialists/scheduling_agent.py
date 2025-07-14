"""
Scheduling management specialist agent for Hero365 voice system.
"""

from typing import Dict, Any, List, Optional
# from openai_agents import tool, handoff
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
import logging

logger = logging.getLogger(__name__)


class SchedulingAgent(BaseVoiceAgent):
    """Specialist agent for scheduling and calendar management"""
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize scheduling management specialist.
        
        Args:
            context_manager: Shared context manager
        """
        instructions = """
        You are the scheduling specialist for Hero365. You help users manage their calendar, 
        schedule appointments, check availability, and handle all time-related operations.
        
        You can help with booking appointments, checking availability, rescheduling, 
        and managing calendar events efficiently.
        
        Be helpful and guide users through scheduling tasks with precision and efficiency.
        """
        
        super().__init__(
            name="Scheduling Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.get_available_time_slots,
                self.book_appointment,
                self.check_availability,
                self.create_calendar_event,
                self.get_today_schedule,
                self.get_upcoming_appointments,
                self.reschedule_appointment,
                self.cancel_appointment,
                self.get_calendar_view,
                self.intelligent_scheduling_suggestion
            ]
        )
    
    def get_handoffs(self) -> List:
        """Return list of agents this agent can hand off to"""
        return []  # These would be populated when initializing the system
    
    # @tool
    async def get_available_time_slots(self, 
                                      date: str, 
                                      duration: int = 60, 
                                      service_type: str = None) -> str:
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
                return f"I don't see any available time slots for {date}. Would you like me to check another date or suggest alternative times?"
            
            slot_list = []
            for slot in result.available_slots:
                slot_info = f"• {slot.start_time} - {slot.end_time}"
                if slot.notes:
                    slot_info += f" ({slot.notes})"
                slot_list.append(slot_info)
            
            slots_text = "\n".join(slot_list)
            
            return await self.format_success_response(
                "get_available_time_slots",
                result,
                f"Here are the available time slots for {date}:\n\n{slots_text}\n\nWould you like me to book any of these slots?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_available_time_slots",
                e,
                f"I'm having trouble finding available time slots for {date}. Let me try a different approach."
            )
    
    # @tool
    async def book_appointment(self, 
                              contact_id: str,
                              date: str,
                              time: str,
                              duration: int = 60,
                              service_type: str = None,
                              notes: str = None) -> str:
        """Book an appointment"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import CreateAppointmentDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                CreateAppointmentDTO(
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
            
            return await self.format_success_response(
                "book_appointment",
                result,
                f"Perfect! I've booked the appointment for {date} at {time}. The appointment ID is {result.id}. Would you like me to send a confirmation to the client?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "book_appointment",
                e,
                f"I couldn't book the appointment for {date} at {time}. Please check the details and try again."
            )
    
    # @tool
    async def check_availability(self, date: str, time: str = None) -> str:
        """Check availability for a specific date and time"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import AvailabilityCheckDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                AvailabilityCheckDTO(
                    date=date,
                    time=time,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if result.is_available:
                return await self.format_success_response(
                    "check_availability",
                    result,
                    f"Great news! You're available on {date}" + (f" at {time}" if time else "") + ". Would you like me to help you book an appointment?"
                )
            else:
                return await self.format_success_response(
                    "check_availability",
                    result,
                    f"You're not available on {date}" + (f" at {time}" if time else "") + ". Would you like me to suggest alternative times?"
                )
            
        except Exception as e:
            return await self.format_error_response(
                "check_availability",
                e,
                f"I'm having trouble checking availability for {date}. Let me try a different approach."
            )
    
    # @tool
    async def create_calendar_event(self, 
                                   title: str,
                                   date: str,
                                   time: str,
                                   duration: int = 60,
                                   description: str = None) -> str:
        """Create a calendar event"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import CreateCalendarEventDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                CreateCalendarEventDTO(
                    title=title,
                    date=date,
                    time=time,
                    duration=duration,
                    description=description,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "create_calendar_event",
                result,
                f"Excellent! I've created the calendar event '{title}' for {date} at {time}. The event has been added to your calendar."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "create_calendar_event",
                e,
                f"I couldn't create the calendar event '{title}'. Please check the details and try again."
            )
    
    # @tool
    async def get_today_schedule(self) -> str:
        """Get today's schedule"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import GetScheduleDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                GetScheduleDTO(
                    date="today",
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.appointments:
                return "You don't have any appointments scheduled for today. Your schedule is wide open! Would you like me to help you schedule something?"
            
            appointment_list = []
            for appointment in result.appointments:
                appt_info = f"• {appointment.time} - {appointment.title}"
                if appointment.contact_name:
                    appt_info += f" with {appointment.contact_name}"
                if appointment.duration:
                    appt_info += f" ({appointment.duration} min)"
                appointment_list.append(appt_info)
            
            schedule_text = "\n".join(appointment_list)
            
            return await self.format_success_response(
                "get_today_schedule",
                result,
                f"Here's your schedule for today:\n\n{schedule_text}\n\nAnything you'd like me to help you with regarding these appointments?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_today_schedule",
                e,
                "I'm having trouble getting your today's schedule. Let me help you with something else."
            )
    
    # @tool
    async def get_upcoming_appointments(self, days_ahead: int = 7) -> str:
        """Get upcoming appointments"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import GetScheduleDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                GetScheduleDTO(
                    date_range=f"next_{days_ahead}_days",
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.appointments:
                return f"You don't have any appointments scheduled for the next {days_ahead} days. Would you like me to help you schedule some?"
            
            appointment_list = []
            for appointment in result.appointments:
                appt_info = f"• {appointment.date} at {appointment.time} - {appointment.title}"
                if appointment.contact_name:
                    appt_info += f" with {appointment.contact_name}"
                appointment_list.append(appt_info)
            
            schedule_text = "\n".join(appointment_list)
            
            return await self.format_success_response(
                "get_upcoming_appointments",
                result,
                f"Here are your upcoming appointments for the next {days_ahead} days:\n\n{schedule_text}\n\nWould you like me to help you with any of these appointments?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_upcoming_appointments",
                e,
                f"I'm having trouble getting your upcoming appointments. Let me help you with something else."
            )
    
    # @tool
    async def reschedule_appointment(self, 
                                   appointment_id: str,
                                   new_date: str,
                                   new_time: str,
                                   reason: str = None) -> str:
        """Reschedule an appointment"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import RescheduleAppointmentDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                RescheduleAppointmentDTO(
                    appointment_id=appointment_id,
                    new_date=new_date,
                    new_time=new_time,
                    reason=reason,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "reschedule_appointment",
                result,
                f"Perfect! I've rescheduled the appointment to {new_date} at {new_time}. Would you like me to notify the client about this change?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "reschedule_appointment",
                e,
                f"I couldn't reschedule the appointment. Please check the appointment ID and try again."
            )
    
    # @tool
    async def cancel_appointment(self, appointment_id: str, reason: str = None) -> str:
        """Cancel an appointment"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import CancelAppointmentDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                CancelAppointmentDTO(
                    appointment_id=appointment_id,
                    reason=reason,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "cancel_appointment",
                result,
                f"The appointment has been cancelled successfully. Would you like me to notify the client about this cancellation?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "cancel_appointment",
                e,
                f"I couldn't cancel the appointment. Please check the appointment ID and try again."
            )
    
    # @tool
    async def get_calendar_view(self, view_type: str = "week", date: str = None) -> str:
        """Get calendar view (day, week, month)"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the calendar management use case
            calendar_management_use_case = self.container.get_calendar_management_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import GetCalendarViewDTO
            
            # Execute use case
            result = await calendar_management_use_case.execute(
                GetCalendarViewDTO(
                    view_type=view_type,
                    date=date,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "get_calendar_view",
                result,
                f"Here's your {view_type} calendar view. You have {len(result.appointments)} appointments scheduled. Would you like me to help you with any specific time slot?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_calendar_view",
                e,
                f"I'm having trouble getting your {view_type} calendar view. Let me help you with something else."
            )
    
    # @tool
    async def intelligent_scheduling_suggestion(self, 
                                              service_type: str,
                                              duration: int = 60,
                                              preferred_time: str = None) -> str:
        """Get intelligent scheduling suggestions"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the intelligent scheduling use case
            intelligent_scheduling_use_case = self.container.get_intelligent_scheduling_use_case()
            
            # Import the DTO
            from ...application.dto.scheduling_dto import IntelligentSchedulingDTO
            
            # Execute use case
            result = await intelligent_scheduling_use_case.execute(
                IntelligentSchedulingDTO(
                    service_type=service_type,
                    duration=duration,
                    preferred_time=preferred_time,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.suggestions:
                return f"I don't have any scheduling suggestions for {service_type} right now. Would you like me to check specific dates and times?"
            
            suggestion_list = []
            for suggestion in result.suggestions:
                sugg_info = f"• {suggestion.date} at {suggestion.time}"
                if suggestion.reason:
                    sugg_info += f" - {suggestion.reason}"
                suggestion_list.append(sugg_info)
            
            suggestions_text = "\n".join(suggestion_list)
            
            return await self.format_success_response(
                "intelligent_scheduling_suggestion",
                result,
                f"Here are my scheduling suggestions for {service_type}:\n\n{suggestions_text}\n\nWould you like me to book any of these suggested times?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "intelligent_scheduling_suggestion",
                e,
                f"I'm having trouble generating scheduling suggestions. Let me help you find available times manually."
            )
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Find available time slots",
            "Book appointments",
            "Check availability",
            "Create calendar events",
            "View today's schedule",
            "Get upcoming appointments",
            "Reschedule appointments",
            "Cancel appointments",
            "Calendar view management",
            "Intelligent scheduling suggestions"
        ] 