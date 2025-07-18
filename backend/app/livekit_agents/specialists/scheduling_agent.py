"""
Scheduling management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import logging
import re

from livekit.agents import Agent, RunContext, function_tool
from ..config import LiveKitConfig
from ..business_context_manager import BusinessContextManager

logger = logging.getLogger(__name__)


class SchedulingAgent(Agent):
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
        
        # Initialize business context manager
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        self.scheduling_context = {}
        self.current_appointment = None
        
        # Initialize as LiveKit Agent with instructions only
        super().__init__(instructions=instructions)
        
        logger.info("📅 Scheduling agent initialized successfully")
        
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        logger.info("📅 Business context set for scheduling agent")
    
    @function_tool
    async def check_availability(
        self,
        ctx: RunContext,
        date: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> str:
        """Check availability for a specific date and time range.
        
        Args:
            date: Date to check (format: YYYY-MM-DD)
            start_time: Start time to check (optional, format: HH:MM)
            end_time: End time to check (optional, format: HH:MM)
        """
        try:
            logger.info(f"Checking availability for {date}")
            # This would integrate with the actual availability checking logic
            return f"Here are the available time slots for {date}..."
                
        except Exception as e:
            logger.error(f"❌ Error checking availability: {e}")
            return f"❌ Error checking availability: {str(e)}"
    
    @function_tool
    async def book_appointment(
        self,
        ctx: RunContext,
        contact_id: str,
        date: str,
        time: str,
        duration: Optional[int] = 60,
        service_type: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Book an appointment with the provided information.
        
        Args:
            contact_id: ID of the contact for the appointment (required)
            date: Appointment date (required, format: YYYY-MM-DD)
            time: Appointment time (required, format: HH:MM)
            duration: Duration in minutes (optional, default: 60)
            service_type: Type of service (optional)
            notes: Additional notes (optional)
        """
        try:
            logger.info(f"Booking appointment for contact {contact_id} on {date} at {time}")
            # This would integrate with the actual appointment booking logic
            return f"Appointment booked successfully for {date} at {time}."
                
        except Exception as e:
            logger.error(f"❌ Error booking appointment: {e}")
            return f"❌ Error booking appointment: {str(e)}"
    
    @function_tool
    async def view_schedule(
        self,
        ctx: RunContext,
        date: Optional[str] = None,
        days: int = 1
    ) -> str:
        """View schedule for a specific date or date range.
        
        Args:
            date: Specific date to view (optional, format: YYYY-MM-DD)
            days: Number of days to view (default: 1)
        """
        try:
            logger.info(f"Viewing schedule for {date or f'next {days} days'}")
            # This would integrate with the actual schedule viewing logic
            return f"Here is your schedule for {date or f'the next {days} days'}..."
                
        except Exception as e:
            logger.error(f"❌ Error viewing schedule: {e}")
            return f"❌ Error viewing schedule: {str(e)}"
    
    @function_tool
    async def reschedule_appointment(
        self,
        ctx: RunContext,
        appointment_id: str,
        new_date: str,
        new_time: str
    ) -> str:
        """Reschedule an existing appointment.
        
        Args:
            appointment_id: The ID of the appointment to reschedule
            new_date: New date (format: YYYY-MM-DD)
            new_time: New time (format: HH:MM)
        """
        try:
            logger.info(f"Rescheduling appointment {appointment_id} to {new_date} at {new_time}")
            # This would integrate with the actual rescheduling logic
            return f"Appointment {appointment_id} rescheduled to {new_date} at {new_time}."
                
        except Exception as e:
            logger.error(f"❌ Error rescheduling appointment: {e}")
            return f"❌ Error rescheduling appointment: {str(e)}"
    
    @function_tool
    async def get_scheduling_suggestions(
        self,
        ctx: RunContext,
        contact_id: str,
        service_type: Optional[str] = None
    ) -> str:
        """Get scheduling suggestions for a contact.
        
        Args:
            contact_id: ID of the contact
            service_type: Type of service (optional)
        """
        try:
            logger.info(f"Getting scheduling suggestions for contact {contact_id}")
            # This would integrate with the actual scheduling suggestions logic
            return f"Here are some scheduling suggestions for contact {contact_id}..."
                
        except Exception as e:
            logger.error(f"❌ Error getting scheduling suggestions: {e}")
            return f"❌ Error getting scheduling suggestions: {str(e)}"
    
    @function_tool
    async def get_next_available_slot(
        self,
        ctx: RunContext,
        duration: int = 60,
        after_date: Optional[str] = None
    ) -> str:
        """Get the next available time slot.
        
        Args:
            duration: Duration needed in minutes (default: 60)
            after_date: Only look after this date (optional, format: YYYY-MM-DD)
        """
        try:
            logger.info(f"Finding next available {duration}-minute slot")
            # This would integrate with the actual slot finding logic
            return f"Here is the next available {duration}-minute time slot..."
                
        except Exception as e:
            logger.error(f"❌ Error finding next available slot: {e}")
            return f"❌ Error finding next available slot: {str(e)}"
    
    @function_tool
    async def get_schedule_summary(
        self,
        ctx: RunContext,
        days: int = 7
    ) -> str:
        """Get a summary of the schedule for the specified number of days.
        
        Args:
            days: Number of days to summarize (default: 7)
        """
        try:
            logger.info(f"Getting schedule summary for next {days} days")
            # This would integrate with the actual schedule summary logic
            return f"Here is your schedule summary for the next {days} days..."
                
        except Exception as e:
            logger.error(f"❌ Error getting schedule summary: {e}")
            return f"❌ Error getting schedule summary: {str(e)}" 