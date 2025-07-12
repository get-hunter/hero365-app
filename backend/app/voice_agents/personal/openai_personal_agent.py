"""
OpenAI Personal Agent

Personal voice agent using OpenAI's voice agents SDK for Hero365 business operations.
"""

from typing import List, Any, Dict, Optional
from agents import Agent
from ..core.base_agent import BaseVoiceAgent
from ..core.voice_config import PersonalAgentConfig, AgentType
from ..tools.hero365_tools import Hero365Tools


class OpenAIPersonalAgent(BaseVoiceAgent):
    """Personal voice agent using OpenAI's voice agents SDK"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any],
                 agent_config: Optional[PersonalAgentConfig] = None):
        """
        Initialize OpenAI personal agent
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
            agent_config: Personal agent configuration
        """
        super().__init__(business_context, user_context, agent_config)
        
        # Use provided config or create default
        self.config = agent_config or PersonalAgentConfig()
        
        # Initialize Hero365 tools
        self.hero365_tools = Hero365Tools(
            business_id=self.get_business_id(),
            user_id=self.get_user_id()
        )
    
    def get_instructions(self) -> str:
        """Get system instructions for the personal agent"""
        business_name = self.business_context.get('name', 'Hero365')
        user_name = self.user_context.get('name', 'User')
        business_type = self.business_context.get('type', 'home services')
        is_driving = self.is_driving_mode()
        safety_mode = self.get_safety_mode()
        
        instructions = f"""You are {business_name}'s personal AI assistant for {user_name}.

CONTEXT:
- Business: {business_name} ({business_type})
- User: {user_name}
- Driving Mode: {"ON" if is_driving else "OFF"}
- Safety Mode: {"ON" if safety_mode else "OFF"}

CORE CAPABILITIES:
You can help with complete business operations including:
- Job Management: Create, update, reschedule, and track jobs
- Project Management: Monitor progress and milestones
- Invoice Management: Create invoices, track payments, send reminders
- Estimate Management: Create estimates, convert to invoices
- Contact Management: Access contact info, record interactions, schedule follow-ups
- Business Operations: Get business summaries, set reminders, check time

COMMUNICATION STYLE:
- Be professional but friendly and conversational
- Use natural speech patterns optimized for voice interaction
- Keep responses concise and actionable
- Ask clarifying questions when needed
- Provide clear confirmations for all actions taken

SAFETY PROTOCOLS:
{"- CRITICAL: Keep all responses brief and hands-free friendly" if is_driving else ""}
{"- Avoid complex multi-step instructions while driving" if is_driving else ""}
{"- Suggest pulling over for complex tasks if driving" if is_driving else ""}
{"- Prioritize urgent safety-related information" if safety_mode else ""}

RESPONSE FORMAT:
- Start with a brief acknowledgment
- Provide the requested information or action result
- End with a clear next step or question if needed
- Always confirm actions taken (e.g., "Job created", "Invoice sent")

BUSINESS CONTEXT:
Your business specializes in {business_type}. You have access to all business data and can perform any business operation through your tools. Always provide specific, actionable responses based on real business data.

Remember: You're an AI assistant focused on helping {user_name} efficiently manage {business_name}'s operations through voice commands."""
        
        return instructions
    
    def get_tools(self) -> List[Any]:
        """Get all available tools for the personal agent"""
        return self.hero365_tools.get_all_tools()
    
    def get_handoffs(self) -> List[Agent]:
        """Get agents this agent can hand off to"""
        # For now, personal agent doesn't hand off to other agents
        # This could be extended to include specialized agents
        return []
    
    def get_agent_name(self) -> str:
        """Get agent name for identification"""
        business_name = self.business_context.get('name', 'Hero365')
        return f"{business_name} Personal Assistant"
    
    def get_personalized_greeting(self) -> str:
        """Generate personalized greeting based on context"""
        user_name = self.user_context.get('name', 'there')
        business_name = self.business_context.get('name', 'Hero365')
        
        # Check time of day for appropriate greeting
        from datetime import datetime
        hour = datetime.now().hour
        
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        # Add driving mode context
        if self.is_driving_mode():
            return f"{time_greeting} {user_name}! I'm your {business_name} assistant. I see you're driving, so I'll keep things brief and hands-free. How can I help you today?"
        else:
            return f"{time_greeting} {user_name}! I'm your {business_name} assistant. I can help you with jobs, projects, invoices, estimates, contacts, and more. What would you like to do?"
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get summary of available capabilities"""
        return {
            "job_management": [
                "Create new jobs",
                "View upcoming jobs", 
                "Update job status",
                "Reschedule jobs",
                "Get job details"
            ],
            "project_management": [
                "Check project status",
                "Update project progress",
                "View active projects"
            ],
            "invoice_management": [
                "Create invoices",
                "Check invoice status",
                "Send payment reminders",
                "View pending invoices"
            ],
            "estimate_management": [
                "Create estimates",
                "Convert estimates to invoices",
                "View pending estimates",
                "Update estimate status"
            ],
            "contact_management": [
                "Get contact information",
                "Record interactions",
                "Schedule follow-ups",
                "Search contacts"
            ],
            "general_business": [
                "Get business summary",
                "Check current time",
                "Set reminders",
                "Get weather information"
            ]
        }
    
    def create_voice_optimized_agent(self) -> Agent:
        """Create agent specifically optimized for voice interactions"""
        return Agent(
            name=self.get_agent_name(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model="gpt-4o-mini"  # Use specific model for voice optimization
        ) 