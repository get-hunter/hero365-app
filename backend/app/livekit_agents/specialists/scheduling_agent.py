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
        
        # Initialize as LiveKit Agent with tools
        super().__init__(
            instructions=instructions,
            tools=[
                self.check_availability,
                self.book_appointment,
                self.view_schedule,
                self.reschedule_appointment,
                self.get_scheduling_suggestions,
                self.get_next_available_slot,
                self.get_schedule_summary,
            ]
        )
        
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        
        # Scheduling-specific configuration
        self.scheduling_context = {}
        self.current_appointment = None
        
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        logger.info("📅 Business context set for scheduling agent")
    
    @function_tool
    async def check_availability(self,
                               ctx: RunContext,
                               date: str,
                               start_time: Optional[str] = None,
                               duration: int = 60) -> str:
        """Check availability for a specific date and time"""
        try:
            logger.info(f"Checking availability for {date} at {start_time}")
            
            # Mock availability check (would integrate with real system)
            if start_time:
                return f"✅ {date} at {start_time} for {duration} minutes is available!"
            else:
                # Return available time slots for the day
                available_slots = [
                    "9:00 AM - 10:00 AM",
                    "11:00 AM - 12:00 PM",
                    "2:00 PM - 3:00 PM",
                    "4:00 PM - 5:00 PM"
                ]
                
                slots_text = "\n".join([f"• {slot}" for slot in available_slots])
                return f"📅 Available time slots for {date}:\n{slots_text}"
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return f"❌ I encountered an error while checking availability: {str(e)}"
    
    @function_tool
    async def book_appointment(self,
                             ctx: RunContext,
                             contact_id: str,
                             date: str,
                             time: str,
                             duration: int = 60,
                             service_type: Optional[str] = None,
                             notes: Optional[str] = None) -> str:
        """Book an appointment with the specified details"""
        try:
            logger.info(f"Booking appointment for {date} at {time}")
            
            # Mock appointment booking (would integrate with real system)
            appointment_id = f"apt_{uuid.uuid4().hex[:8]}"
            
            response = f"✅ Appointment booked successfully for {date} at {time}! Appointment ID: {appointment_id}"
            
            if service_type:
                response += f"\n🔧 Service: {service_type}"
            
            if duration != 60:
                response += f"\n⏱️ Duration: {duration} minutes"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self._get_context_suggestions()
                if suggestions:
                    response += f"\n💡 Suggested next steps: {suggestions[0]}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return f"❌ I encountered an error while booking the appointment: {str(e)}"
    
    @function_tool
    async def view_schedule(self, ctx: RunContext, date: Optional[str] = None, view_type: str = "day") -> str:
        """View schedule for a specific date or period"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"Viewing schedule for {date}")
            
            # Mock schedule view (would integrate with real system)
            appointments = [
                {"time": "10:00 AM", "service": "Plumbing Repair", "customer": "John Smith"},
                {"time": "2:00 PM", "service": "HVAC Maintenance", "customer": "Sarah Johnson"}
            ]
            
            if not appointments:
                return f"📅 No appointments scheduled for {date}"
            
            schedule_text = "\n".join([
                f"• {apt['time']} - {apt['service']} - {apt['customer']}"
                for apt in appointments
            ])
            
            return f"📅 Schedule for {date}:\n{schedule_text}"
            
        except Exception as e:
            logger.error(f"Error viewing schedule: {e}")
            return f"❌ I encountered an error while viewing the schedule: {str(e)}"
    
    @function_tool
    async def reschedule_appointment(self,
                                   ctx: RunContext,
                                   appointment_id: str,
                                   new_date: str,
                                   new_time: str) -> str:
        """Reschedule an existing appointment"""
        try:
            logger.info(f"Rescheduling appointment {appointment_id} to {new_date} at {new_time}")
            
            # Mock rescheduling (would integrate with real system)
            return f"✅ Appointment {appointment_id} rescheduled to {new_date} at {new_time} successfully!"
            
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {e}")
            return f"❌ I encountered an error while rescheduling the appointment: {str(e)}"
    
    @function_tool
    async def get_scheduling_suggestions(self, ctx: RunContext, service_type: Optional[str] = None) -> str:
        """Get scheduling suggestions based on business context"""
        try:
            logger.info("Getting scheduling suggestions")
            
            suggestions = []
            
            # Mock suggestions based on business context
            if self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                if business_context:
                    suggestions.extend([
                        "Book follow-up appointments for recent jobs",
                        "Schedule maintenance calls for existing customers",
                        "Fill gaps in tomorrow's schedule"
                    ])
            
            # Default suggestions
            if not suggestions:
                suggestions = [
                    "Consider scheduling morning appointments for better traffic",
                    "Book buffer time between appointments",
                    "Schedule follow-up calls after completed jobs"
                ]
            
            suggestions_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
            
            return f"💡 Scheduling suggestions:\n{suggestions_text}"
            
        except Exception as e:
            logger.error(f"Error getting scheduling suggestions: {e}")
            return f"❌ I encountered an error while getting scheduling suggestions: {str(e)}"
    
    @function_tool
    async def get_next_available_slot(self,
                                    ctx: RunContext,
                                    duration: int = 60,
                                    service_type: Optional[str] = None) -> str:
        """Get the next available time slot"""
        try:
            logger.info(f"Finding next available slot for {duration} minutes")
            
            # Mock next available slot (would integrate with real system)
            next_slot = {
                "date": "2025-07-19",
                "time": "10:00 AM",
                "duration": duration
            }
            
            response = f"📅 Next available slot: {next_slot['date']} at {next_slot['time']} for {duration} minutes"
            
            if service_type:
                response += f"\n🔧 Service type: {service_type}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting next available slot: {e}")
            return f"❌ I encountered an error while finding the next available slot: {str(e)}"
    
    @function_tool
    async def get_schedule_summary(self, ctx: RunContext, period: str = "week") -> str:
        """Get a summary of the schedule for a specific period"""
        try:
            logger.info(f"Getting schedule summary for {period}")
            
            # Mock schedule summary (would integrate with real system)
            summary = {
                "total_appointments": 12,
                "confirmed_appointments": 10,
                "pending_appointments": 2,
                "free_slots": 8,
                "busiest_day": "Thursday"
            }
            
            response = f"📊 Schedule Summary ({period}):\n"
            response += f"• Total appointments: {summary['total_appointments']}\n"
            response += f"• Confirmed: {summary['confirmed_appointments']}\n"
            response += f"• Pending: {summary['pending_appointments']}\n"
            response += f"• Free slots: {summary['free_slots']}\n"
            response += f"• Busiest day: {summary['busiest_day']}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting schedule summary: {e}")
            return f"❌ I encountered an error while getting the schedule summary: {str(e)}"
    
    def _get_context_suggestions(self) -> List[str]:
        """Get contextual suggestions based on business context"""
        suggestions = []
        
        if self.business_context_manager:
            business_context = self.business_context_manager.get_business_context()
            if business_context:
                # Add contextual suggestions based on business state
                suggestions.append("Send appointment confirmation to customer")
                suggestions.append("Prepare materials for the scheduled service")
                suggestions.append("Set up travel route for the day")
        
        return suggestions 