"""
Scheduling Agent

Specialized voice agent for calendar management, appointments, and scheduling operations.
"""

from typing import Dict, Any, List
from agents import Agent
from ..core.base_agent import BaseVoiceAgent
from ..tools.scheduling_tools import SchedulingTools


class SchedulingAgent(BaseVoiceAgent):
    """
    Specialized agent for scheduling and calendar management.
    
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
        """Get system instructions for the scheduling agent"""
        
        business_name = self.business_context.get('name', 'Hero365')
        user_name = self.user_context.get('name', 'User')
        is_driving = self.is_driving_mode()
        
        instructions = f"""You are the Hero365 Scheduling Assistant for {business_name}.

IDENTITY & ROLE:
You are a specialized scheduling expert focused on calendar management, appointments, and time coordination. Your expertise includes availability checking, appointment booking, calendar event management, and scheduling optimization.

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

COMMUNICATION STYLE:
- Be professional and efficient
- Provide clear time and date confirmations
- Always confirm important scheduling details
- Use natural language for dates and times
- Anticipate scheduling conflicts and offer alternatives
- Be proactive about scheduling optimization

SAFETY PROTOCOLS:
{f'- Keep all responses brief and hands-free friendly' if is_driving else ''}
{f'- Avoid complex scheduling operations while driving' if is_driving else ''}
{f'- Prioritize simple queries like "What is my next appointment?"' if is_driving else ''}

COMMON SCHEDULING SCENARIOS:
1. **New Appointments**: "Schedule a service call for tomorrow at 2 PM"
2. **Availability**: "When am I available this week?"
3. **Rescheduling**: "Move my 3 PM meeting to 4 PM"
4. **Team Coordination**: "Who's available Friday afternoon?"
5. **Time Off**: "I need to request vacation next week"
6. **Recurring Events**: "Set up weekly team meetings"

RESPONSE PATTERNS:
- **Confirmation**: Always confirm scheduled times with date, time, and duration
- **Alternatives**: Offer alternative times if preferred slots are unavailable
- **Context**: Provide relevant context like travel time, preparation needs
- **Follow-up**: Suggest related actions like sending confirmations or setting reminders

SCHEDULING BEST PRACTICES:
- Always double-check appointment details before confirming
- Consider travel time between appointments
- Respect working hours and time off
- Provide clear confirmation numbers and references
- Offer multiple options when possible
- Be mindful of scheduling conflicts

EMERGENCY PROTOCOLS:
- For urgent scheduling needs, prioritize immediate availability
- Handle emergency rescheduling with appropriate urgency
- Escalate complex scheduling conflicts to human support when needed

Remember: You are the scheduling expert for {business_name}. Your goal is to make scheduling seamless, efficient, and conflict-free while maintaining professional service standards."""

        return instructions
    
    def get_tools(self) -> List[Any]:
        """Get all scheduling tools"""
        return self.scheduling_tools.get_tools()
    
    def get_handoffs(self) -> List[Agent]:
        """Get agents this agent can hand off to"""
        # Scheduling agent typically doesn't hand off - it's a specialist
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
            return f"Hi {user_name}! I'm your {business_name} scheduling assistant. I'll keep this brief since you're driving. How can I help with your schedule?"
        else:
            return f"Hi {user_name}! I'm your {business_name} scheduling assistant. I can help you with appointments, calendar management, availability checking, and more. What would you like to do?"
    
    def get_scheduling_capabilities(self) -> Dict[str, List[str]]:
        """Get summary of scheduling capabilities"""
        return {
            "appointment_management": [
                "Schedule new appointments",
                "Reschedule existing appointments", 
                "Cancel appointments",
                "Find available time slots"
            ],
            "calendar_management": [
                "Create calendar events",
                "Manage recurring events",
                "Check daily/weekly schedules",
                "Set reminders"
            ],
            "availability_management": [
                "Check personal availability",
                "Check team availability",
                "Set working hours",
                "Manage time off requests"
            ],
            "scheduling_optimization": [
                "Find optimal time slots",
                "Consider travel time",
                "Avoid scheduling conflicts",
                "Coordinate team schedules"
            ]
        }
    
    def get_safety_mode_instructions(self) -> str:
        """Get safety mode instructions for driving"""
        if self.is_driving_mode():
            return """
DRIVING MODE ACTIVE:
- Keep responses brief and clear
- Provide essential information only
- Avoid complex scheduling operations
- Focus on simple queries like "What's my next appointment?"
- Offer to handle complex scheduling when user is not driving
"""
        return ""
    
    def can_handle_request(self, request: str) -> bool:
        """Check if this agent can handle the request"""
        scheduling_keywords = [
            "schedule", "appointment", "calendar", "meeting", "book", "available",
            "reschedule", "cancel", "time", "date", "when", "busy", "free",
            "working hours", "time off", "vacation", "availability", "recurring"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in scheduling_keywords)
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        """Get quick scheduling actions"""
        return [
            {
                "action": "check_today_schedule",
                "description": "Check today's schedule",
                "command": "What's on my schedule today?"
            },
            {
                "action": "check_availability",
                "description": "Check availability",
                "command": "When am I available this week?"
            },
            {
                "action": "next_appointment",
                "description": "Next appointment",
                "command": "When is my next appointment?"
            },
            {
                "action": "schedule_appointment",
                "description": "Schedule new appointment",
                "command": "Schedule a new appointment"
            }
        ] 