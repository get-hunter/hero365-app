"""
Scheduling Agent

Specialized voice agent for calendar management, appointments, and scheduling operations.
Optimized for OpenAI Realtime API with natural voice interactions.
"""

from typing import Dict, Any, List
from agents import Agent, function_tool
from ..core.base_agent import BaseVoiceAgent
from ..tools.scheduling_tools import SchedulingTools


class SchedulingAgent(BaseVoiceAgent):
    """
    Specialized agent for scheduling and calendar management.
    Optimized for OpenAI Realtime API with natural voice interactions.
    
    Handles:
    - Calendar management and appointments
    - Availability checking and booking
    - Working hours and time off management
    - Recurring appointments and events
    - Team scheduling coordination
    """
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        """
        Initialize scheduling agent
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
        """
        super().__init__(business_context, user_context)
        self.scheduling_tools = SchedulingTools(
            business_id=self.get_business_id(),
            user_id=self.get_user_id()
        )
    
    def get_instructions(self) -> str:
        """Get system instructions for the scheduling agent optimized for voice"""
        
        business_name = self.business_context.get('name', 'Hero365')
        user_name = self.user_context.get('name', 'User')
        is_driving = self.is_driving_mode()
        
        instructions = f"""You are the Hero365 Scheduling Assistant for {business_name}.

IDENTITY & ROLE:
You are a specialized scheduling expert focused on calendar management, appointments, and time coordination. Your expertise includes availability checking, appointment booking, calendar event management, and scheduling optimization.

VOICE INTERACTION EXCELLENCE:
- Speak naturally about dates and times: "next Tuesday at 2 PM" instead of "2024-01-15 14:00"
- Use conversational confirmations: "Perfect! I've scheduled that for you" 
- Ask clarifying questions for ambiguous times: "Did you mean this Tuesday or next Tuesday?"
- Provide context with suggestions: "That time slot is available, and it gives you a 30-minute buffer after your previous meeting"
- Always confirm critical details: "Just to confirm, that's Tuesday, January 15th at 2 PM"
- Offer helpful alternatives: "That time isn't available, but I have 2:30 PM or 3 PM open"

CORE CAPABILITIES:
- **Appointment Management**: Schedule, reschedule, and cancel appointments
- **Availability Checking**: Check user and team availability across date ranges
- **Calendar Events**: Create, manage, and track calendar events
- **Working Hours**: Set and manage working hour templates
- **Time Off Management**: Handle time off requests and approvals
- **Recurring Appointments**: Create and manage recurring events
- **Team Coordination**: Coordinate scheduling across team members
- **Intelligent Scheduling**: Find optimal time slots based on preferences

BUSINESS CONTEXT:
- Business: {business_name}
- User: {user_name}
- Driving Mode: {'ACTIVE - Keep responses brief and voice-friendly' if is_driving else 'INACTIVE'}

SCHEDULING EXPERTISE:
You have access to Hero365's intelligent scheduling system that includes:
- Real-time availability checking
- Travel time optimization
- Team coordination capabilities
- Customer booking system
- Calendar integration
- Working hours management
- Time off tracking

VOICE COMMUNICATION STYLE:
- Be professional and efficient with a friendly touch
- Provide clear time and date confirmations in natural language
- Always confirm important scheduling details before finalizing
- Use natural language for dates and times ("tomorrow at 3" not "2024-01-16 15:00")
- Anticipate scheduling conflicts and offer alternatives conversationally
- Be proactive about scheduling optimization and time management
- Use helpful transitions: "Let me check your calendar... Great! I found some options for you"

SAFETY PROTOCOLS:
{self._get_safety_protocols()}

VOICE RESPONSE GUIDELINES:
- Always confirm times and dates clearly in natural language
- Check for conflicts before booking and communicate any issues
- Provide alternative time slots when needed with reasons
- Consider travel time between appointments and mention it
- Suggest optimal scheduling patterns for productivity
- Follow up on important scheduling changes with reminders
- When driving mode is active, keep responses under 40 words and focus on essential scheduling info

Remember: You are the expert in scheduling and time management. Your goal is to help maintain an organized, efficient calendar that maximizes productivity while respecting time boundaries through natural voice interaction."""
        
        return instructions
    
    def get_tools(self) -> List[Any]:
        """Return list of scheduling tools"""
        return [
            self._get_available_time_slots_tool(),
            self._book_appointment_tool(),
            self._check_availability_tool(),
            self._create_calendar_event_tool(),
            self._get_today_schedule_tool(),
            self._get_upcoming_appointments_tool(),
            self._reschedule_appointment_tool(),
            self._cancel_appointment_tool()
        ]
    
    def _get_available_time_slots_tool(self):
        """Get available time slots tool wrapper"""
        @function_tool
        async def get_available_time_slots(job_type: str,
                                         duration_hours: float,
                                         preferred_date: str,
                                         customer_location: str = None) -> str:
            """Find available time slots for scheduling appointments.
            
            Args:
                job_type: Type of job or appointment
                duration_hours: How long the appointment should be
                preferred_date: Preferred date for the appointment
                customer_location: Customer's location for travel time calculation
            
            Returns:
                Available time slots with details
            """
            result = await self.scheduling_tools.get_available_time_slots(
                job_type=job_type,
                duration_hours=duration_hours,
                preferred_date=preferred_date,
                customer_location=customer_location
            )
            
            if result["success"]:
                slots = result["slots"]
                if not slots:
                    return f"I don't have any available slots for {job_type} on {preferred_date}. Would you like me to check a different day or suggest the next available times?"
                
                # Format for voice response
                if len(slots) == 1:
                    slot = slots[0]
                    response = f"I have one available slot on {preferred_date} at {slot.get('start_time', 'unknown time')}"
                    if slot.get('duration'):
                        response += f" for {slot['duration']} hours"
                    response += ". Would you like me to book this time?"
                else:
                    response = f"I found {len(slots)} available slots for {job_type} on {preferred_date}: "
                    slot_times = []
                    for slot in slots[:5]:  # Limit to 5 for voice
                        slot_times.append(slot.get('start_time', 'unknown time'))
                    response += ", ".join(slot_times)
                    
                    if len(slots) > 5:
                        response += f" and {len(slots) - 5} more options"
                    
                    response += ". Which time works best for you?"
                
                return response
            else:
                return f"I had trouble checking availability. {result['message']} Would you like me to try a different approach?"
        
        return get_available_time_slots
    
    def _book_appointment_tool(self):
        """Book appointment tool wrapper"""
        @function_tool
        async def book_appointment(slot_id: str,
                                 customer_name: str,
                                 customer_phone: str,
                                 customer_email: str = None,
                                 job_description: str = None) -> str:
            """Book an appointment in a specific time slot.
            
            Args:
                slot_id: ID of the time slot to book
                customer_name: Customer's name
                customer_phone: Customer's phone number
                customer_email: Customer's email address
                job_description: Description of the job or appointment
            
            Returns:
                Booking confirmation
            """
            result = await self.scheduling_tools.book_appointment(
                slot_id=slot_id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                job_description=job_description
            )
            
            if result["success"]:
                appointment = result["appointment"]
                response = f"Excellent! I've booked the appointment for {customer_name} on {appointment.get('date', 'the scheduled date')} at {appointment.get('time', 'the scheduled time')}"
                
                if job_description:
                    response += f" for {job_description}"
                
                # Add helpful details
                if appointment.get('duration'):
                    response += f". This is scheduled for {appointment['duration']} hours"
                
                if appointment.get('confirmation_code'):
                    response += f". The confirmation code is {appointment['confirmation_code']}"
                
                response += ". I'll send a confirmation to "
                if customer_email:
                    response += f"{customer_email} and "
                response += f"the phone number {customer_phone}."
                
                return response
            else:
                return f"I couldn't book that appointment. {result['message']} Would you like me to try a different time slot?"
        
        return book_appointment
    
    def _check_availability_tool(self):
        """Check availability tool wrapper"""
        @function_tool
        async def check_availability(user_ids: List[str],
                                   start_date: str,
                                   end_date: str) -> str:
            """Check availability for team members across a date range.
            
            Args:
                user_ids: List of user IDs to check
                start_date: Start date for availability check
                end_date: End date for availability check
            
            Returns:
                Availability information
            """
            result = await self.scheduling_tools.check_availability(
                user_ids=user_ids,
                start_date=start_date,
                end_date=end_date
            )
            
            if result["success"]:
                availability = result["availability"]
                
                if len(user_ids) == 1:
                    user_availability = availability.get(user_ids[0], {})
                    if user_availability.get('available'):
                        response = f"Yes, you're available from {start_date} to {end_date}"
                        if user_availability.get('busy_slots'):
                            response += f", but you have {len(user_availability['busy_slots'])} existing appointments during that time"
                    else:
                        response = f"You're not available during that time period"
                        if user_availability.get('conflicts'):
                            response += f" due to existing appointments"
                else:
                    available_users = [uid for uid in user_ids if availability.get(uid, {}).get('available')]
                    if available_users:
                        response = f"I found {len(available_users)} team members available during that time"
                    else:
                        response = f"None of the team members are available from {start_date} to {end_date}"
                
                response += ". Would you like me to find alternative dates or book a specific time?"
                return response
            else:
                return f"I couldn't check availability. {result['message']} Would you like me to try checking specific dates instead?"
        
        return check_availability
    
    def _create_calendar_event_tool(self):
        """Create calendar event tool wrapper"""
        @function_tool
        async def create_calendar_event(title: str,
                                      start_time: str,
                                      end_time: str,
                                      description: str = None,
                                      event_type: str = "meeting") -> str:
            """Create a calendar event or meeting.
            
            Args:
                title: Event title
                start_time: Event start time
                end_time: Event end time
                description: Event description
                event_type: Type of event (meeting, appointment, etc.)
            
            Returns:
                Event creation confirmation
            """
            result = await self.scheduling_tools.create_calendar_event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                event_type=event_type
            )
            
            if result["success"]:
                event = result["event"]
                response = f"Perfect! I've created the {event_type} '{title}' from {start_time} to {end_time}"
                
                if description:
                    response += f". I've added your notes: {description}"
                
                # Add helpful context
                duration = event.get('duration_minutes', 0)
                if duration:
                    hours = duration // 60
                    minutes = duration % 60
                    if hours > 0:
                        response += f". This is scheduled for {hours} hour"
                        if hours > 1:
                            response += "s"
                        if minutes > 0:
                            response += f" and {minutes} minutes"
                    else:
                        response += f". This is scheduled for {minutes} minutes"
                
                response += ". The event has been added to your calendar."
                
                return response
            else:
                return f"I couldn't create that calendar event. {result['message']} Would you like me to try a different time or adjust the details?"
        
        return create_calendar_event
    
    def _get_today_schedule_tool(self):
        """Get today's schedule tool wrapper"""
        @function_tool
        async def get_today_schedule() -> str:
            """Get today's schedule and appointments.
            
            Returns:
                Today's schedule information
            """
            result = await self.scheduling_tools.get_today_schedule()
            
            if result["success"]:
                schedule = result["schedule"]
                
                if not schedule:
                    return "You have a clear schedule today! No appointments or meetings are scheduled. Would you like me to check tomorrow's schedule?"
                
                # Format for voice response
                response = f"Here's your schedule for today with {len(schedule)} appointments: "
                
                for i, appointment in enumerate(schedule):
                    if i > 0:
                        response += ", then "
                    
                    time = appointment.get('time', 'unknown time')
                    title = appointment.get('title', 'appointment')
                    response += f"{time} - {title}"
                    
                    if appointment.get('customer_name'):
                        response += f" with {appointment['customer_name']}"
                
                response += ". Would you like more details about any of these appointments?"
                return response
            else:
                return f"I couldn't retrieve your schedule. {result['message']} Would you like me to try checking your calendar in a different way?"
        
        return get_today_schedule
    
    def _get_upcoming_appointments_tool(self):
        """Get upcoming appointments tool wrapper"""
        @function_tool
        async def get_upcoming_appointments(days_ahead: int = 7) -> str:
            """Get upcoming appointments for the next few days.
            
            Args:
                days_ahead: Number of days ahead to check
            
            Returns:
                Upcoming appointments information
            """
            result = await self.scheduling_tools.get_upcoming_appointments(
                days_ahead=days_ahead
            )
            
            if result["success"]:
                appointments = result["appointments"]
                
                if not appointments:
                    return f"You don't have any appointments scheduled for the next {days_ahead} days. Your calendar is wide open! Would you like me to help you schedule something?"
                
                # Format for voice response
                response = f"You have {len(appointments)} upcoming appointments in the next {days_ahead} days: "
                
                for i, appointment in enumerate(appointments):
                    if i > 0:
                        response += ", "
                    
                    date = appointment.get('date', 'unknown date')
                    time = appointment.get('time', 'unknown time')
                    title = appointment.get('title', 'appointment')
                    
                    response += f"{date} at {time} - {title}"
                    
                    if appointment.get('customer_name'):
                        response += f" with {appointment['customer_name']}"
                
                response += ". Would you like details about any specific appointment?"
                return response
            else:
                return f"I couldn't retrieve your upcoming appointments. {result['message']} Would you like me to try checking your calendar differently?"
        
        return get_upcoming_appointments
    
    def _reschedule_appointment_tool(self):
        """Reschedule appointment tool wrapper"""
        @function_tool
        async def reschedule_appointment(appointment_id: str,
                                       new_date: str,
                                       new_time: str,
                                       reason: str = None) -> str:
            """Reschedule an existing appointment to a new date and time.
            
            Args:
                appointment_id: ID of the appointment to reschedule
                new_date: New date for the appointment
                new_time: New time for the appointment
                reason: Reason for rescheduling
            
            Returns:
                Rescheduling confirmation
            """
            result = await self.scheduling_tools.reschedule_appointment(
                appointment_id=appointment_id,
                new_date=new_date,
                new_time=new_time,
                reason=reason
            )
            
            if result["success"]:
                appointment = result["appointment"]
                customer_name = appointment.get('customer_name', 'customer')
                old_date = appointment.get('old_date', 'the original date')
                old_time = appointment.get('old_time', 'the original time')
                
                response = f"Done! I've rescheduled the appointment with {customer_name} from {old_date} at {old_time} to {new_date} at {new_time}"
                
                if reason:
                    response += f". Reason: {reason}"
                
                # Add helpful context
                if appointment.get('customer_phone'):
                    response += f". I'll send a notification to {appointment['customer_phone']}"
                
                if appointment.get('confirmation_code'):
                    response += f". The updated confirmation code is {appointment['confirmation_code']}"
                
                response += ". Is there anything else you'd like me to adjust for this appointment?"
                
                return response
            else:
                return f"I couldn't reschedule that appointment. {result['message']} Would you like me to try a different time or approach?"
        
        return reschedule_appointment
    
    def _cancel_appointment_tool(self):
        """Cancel appointment tool wrapper"""
        @function_tool
        async def cancel_appointment(appointment_id: str, reason: str = None) -> str:
            """Cancel an existing appointment.
            
            Args:
                appointment_id: ID of the appointment to cancel
                reason: Reason for cancellation
            
            Returns:
                Cancellation confirmation
            """
            result = await self.scheduling_tools.cancel_appointment(
                appointment_id=appointment_id,
                reason=reason
            )
            
            if result["success"]:
                appointment = result["appointment"]
                customer_name = appointment.get('customer_name', 'customer')
                date = appointment.get('date', 'the scheduled date')
                time = appointment.get('time', 'the scheduled time')
                
                response = f"I've cancelled the appointment with {customer_name} on {date} at {time}"
                
                if reason:
                    response += f". Reason: {reason}"
                
                # Add helpful context
                if appointment.get('customer_phone'):
                    response += f". I'll send a cancellation notification to {appointment['customer_phone']}"
                
                if appointment.get('refund_amount'):
                    response += f". A refund of {appointment['refund_amount']} will be processed"
                
                response += ". That time slot is now available for booking. Would you like me to help you reschedule or find a new appointment?"
                
                return response
            else:
                return f"I couldn't cancel that appointment. {result['message']} Would you like me to try a different approach?"
        
        return cancel_appointment
    
    def _get_safety_protocols(self) -> str:
        """Get safety protocols based on user context"""
        if self.is_driving_mode():
            return """
DRIVING MODE SAFETY:
- Keep all responses under 40 words
- Avoid complex scheduling operations
- Focus on simple schedule queries only
- Use clear, concise time confirmations
- Avoid detailed calendar management
- Offer to handle complex scheduling when not driving
"""
        else:
            return """
STANDARD SAFETY:
- Always confirm important scheduling details
- Double-check dates and times before booking
- Verify customer contact information
- Respect business hours and availability
- Handle schedule conflicts appropriately
"""
    
    def get_handoffs(self) -> List[Agent]:
        """Get agents this agent can hand off to"""
        # Scheduling agent can hand off to related agents
        return []
    
    def get_agent_name(self) -> str:
        """Get agent name for identification"""
        business_name = self.business_context.get('name', 'Hero365')
        return f"{business_name} Scheduling Assistant"
    
    def get_personalized_greeting(self) -> str:
        """Generate personalized greeting based on context"""
        user_name = self.user_context.get('name', 'there')
        business_name = self.business_context.get('name', 'Hero365')
        
        if self.is_driving_mode():
            return f"Hi {user_name}! I'm your {business_name} scheduling assistant. I'll keep responses brief since you're driving. What can I help you schedule?"
        else:
            return f"Hi {user_name}! I'm your {business_name} scheduling assistant. I can help you manage appointments, check availability, and organize your calendar. What would you like to schedule?"
    
    def get_scheduling_capabilities(self) -> Dict[str, List[str]]:
        """Get summary of scheduling capabilities"""
        return {
            "appointment_management": [
                "Schedule appointments",
                "Reschedule existing appointments",
                "Cancel appointments",
                "Find available time slots"
            ],
            "availability_checking": [
                "Check personal availability",
                "Check team availability",
                "Find optimal meeting times",
                "Coordinate schedules"
            ],
            "calendar_management": [
                "Create calendar events",
                "View daily schedule",
                "View upcoming appointments",
                "Manage recurring events"
            ],
            "optimization": [
                "Suggest optimal scheduling",
                "Account for travel time",
                "Avoid scheduling conflicts",
                "Maximize productivity"
            ]
        }
    
    def get_safety_mode_instructions(self) -> str:
        """Get safety mode instructions for driving"""
        if self.is_driving_mode():
            return """
DRIVING MODE ACTIVE:
- Keep responses under 40 words
- Provide essential scheduling information only
- Avoid complex appointment management
- Focus on simple schedule queries
- Offer to handle detailed scheduling when not driving
"""
        return ""
    
    def can_handle_request(self, request: str) -> bool:
        """Check if this agent can handle the request"""
        scheduling_keywords = [
            "schedule", "appointment", "meeting", "calendar", "book", "available",
            "availability", "time", "date", "reschedule", "cancel", "event",
            "today", "tomorrow", "next week", "appointment management",
            "calendar management", "schedule appointment", "check availability"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in scheduling_keywords)
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        """Get quick scheduling actions"""
        return [
            {
                "action": "today_schedule",
                "description": "Today's schedule",
                "command": "What's my schedule today?"
            },
            {
                "action": "upcoming_appointments",
                "description": "Upcoming appointments",
                "command": "Show my upcoming appointments"
            },
            {
                "action": "check_availability",
                "description": "Check availability",
                "command": "Am I available tomorrow?"
            },
            {
                "action": "schedule_appointment",
                "description": "Schedule appointment",
                "command": "Schedule a new appointment"
            }
        ]
    
    def get_voice_pipeline(self):
        """Get voice pipeline for realtime audio processing"""
        return self.create_voice_pipeline() 