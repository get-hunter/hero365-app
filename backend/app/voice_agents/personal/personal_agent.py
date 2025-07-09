"""
Personal Voice Agent for Hero365

This module provides the personal voice agent for mobile users,
enabling voice-based job management during driving or working.
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

from livekit.agents import function_tool

from app.voice_agents.core.base_agent import BaseVoiceAgent
from app.voice_agents.core.voice_config import PersonalAgentConfig, DEFAULT_PERSONAL_CONFIG
from app.voice_agents.tools import job_tools

logger = logging.getLogger(__name__)


class PersonalVoiceAgent(BaseVoiceAgent):
    """Personal voice agent for mobile users during driving/working"""
    
    def __init__(self, 
                 business_context: Dict[str, Any], 
                 user_context: Dict[str, Any],
                 agent_config: Optional[PersonalAgentConfig] = None):
        
        # Use default config if none provided
        if agent_config is None:
            agent_config = DEFAULT_PERSONAL_CONFIG
        
        super().__init__(
            business_context=business_context,
            user_context=user_context,
            agent_config=agent_config.to_dict()
        )
        
        # Store agent configuration
        self.agent_config_obj = agent_config
        
        logger.info(f"Initialized PersonalVoiceAgent for user {self.get_current_user_id()}")
    
    def get_tools(self) -> List[Callable]:
        """Return list of tools available to personal agent"""
        
        return [
            # Job management tools
            job_tools.create_job,
            job_tools.get_upcoming_jobs,
            job_tools.update_job_status,
            job_tools.reschedule_job,
            job_tools.get_job_details,
            job_tools.get_jobs_by_status,
            
            # Personal assistant tools
            self.get_driving_directions,
            self.set_reminder,
            self.get_current_time,
            self.get_business_summary,
            self.toggle_safety_mode
        ]
    
    def get_system_prompt(self) -> str:
        """Generate system prompt based on context"""
        
        business_name = self.get_business_name()
        user_name = self.get_user_name()
        
        # Check if user is driving for safety-focused prompts
        is_driving = self.user_context.get("is_driving", False)
        safety_mode = self.user_context.get("safety_mode", True)
        
        base_prompt = f"""You are Hero365's personal AI assistant for {business_name}.

USER CONTEXT:
- Name: {user_name}
- Business: {business_name}
- Current Status: {"Driving (Safety Mode)" if is_driving and safety_mode else "Available"}

CAPABILITIES:
You can help with:
- Job management (create, update, reschedule, check status)
- Upcoming job schedules and details
- Quick business information
- Time and reminder services
- Navigation assistance

COMMUNICATION STYLE:
- Be concise and professional
- Use hands-free friendly responses
- Provide clear confirmations for actions
- Ask clarifying questions when needed"""

        if is_driving and safety_mode:
            base_prompt += """

SAFETY PROTOCOLS (USER IS DRIVING):
- Keep ALL responses under 20 words when possible
- Prioritize voice-only interactions
- Suggest pulling over for complex tasks
- Use simple yes/no confirmations
- Avoid detailed information unless essential
- Focus on immediate, actionable items"""
        
        base_prompt += """

RESPONSE FORMAT:
- Speak naturally as if talking to a colleague
- Use "I can help you with..." for capabilities
- Confirm actions before executing
- Provide brief status updates after actions
- Ask "Is there anything else?" to continue helping

Remember: You represent {business_name} professionally while being helpful and efficient."""
        
        return base_prompt
    
    async def on_agent_start(self) -> None:
        """Called when agent starts"""
        
        # Record agent start
        await self.record_interaction("agent_start", {
            "agent_type": "personal",
            "business_id": self.get_current_business_id(),
            "user_id": self.get_current_user_id(),
            "is_driving": self.user_context.get("is_driving", False),
            "safety_mode": self.user_context.get("safety_mode", True)
        })
        
        logger.info(f"Personal agent {self.agent_id} started")
    
    async def on_agent_stop(self) -> None:
        """Called when agent stops"""
        
        # Record agent stop
        await self.record_interaction("agent_stop", {
            "agent_type": "personal",
            "session_duration": (datetime.now() - self.created_at).total_seconds()
        })
        
        logger.info(f"Personal agent {self.agent_id} stopped")
    
    # Personal Assistant Function Tools
    
    @function_tool
    async def get_driving_directions(self, destination: str) -> str:
        """Get driving directions to a destination"""
        
        # TODO: Integrate with Google Maps API or similar
        return f"Getting directions to {destination}. For safety, I recommend using your phone's navigation app while driving."
    
    @function_tool
    async def set_reminder(self, message: str, time: str) -> str:
        """Set a voice reminder"""
        
        # TODO: Integrate with business reminder system
        return f"Reminder set: '{message}' for {time}. I'll notify you when the time comes."
    
    @function_tool
    async def get_current_time(self) -> str:
        """Get current time"""
        
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%A, %B %d")
        
        return f"It's currently {current_time} on {current_date}."
    
    @function_tool
    async def get_business_summary(self) -> str:
        """Get quick business summary"""
        
        business_name = self.get_business_name()
        business_type = self.business_context.get("type", "Home Services")
        
        return f"{business_name} is a {business_type} business. You can ask me about jobs, scheduling, or other business operations."
    
    @function_tool
    async def toggle_safety_mode(self, enabled: bool) -> str:
        """Toggle safety mode for driving"""
        
        # Update user context
        self.user_context["safety_mode"] = enabled
        self.user_context["is_driving"] = enabled
        
        status = "enabled" if enabled else "disabled"
        return f"Safety mode {status}. {'Responses will be brief and hands-free friendly.' if enabled else 'Normal conversation mode restored.'}"
    
    def get_personalized_greeting(self) -> str:
        """Generate personalized greeting based on context"""
        
        user_name = self.get_user_name()
        business_name = self.get_business_name()
        
        # Check time of day for appropriate greeting
        hour = datetime.now().hour
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        # Check if user is driving
        is_driving = self.user_context.get("is_driving", False)
        
        if is_driving:
            return f"{time_greeting}, {user_name}! I'm your {business_name} assistant. Drive safely - I'll keep responses brief."
        else:
            return f"{time_greeting}, {user_name}! I'm your {business_name} assistant. How can I help you today?" 