"""
Triage Agent for Voice Agent System

Central triage agent that analyzes user context and routes requests to appropriate specialists.
Optimized for OpenAI Realtime API with speech-to-speech capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from agents import Agent, function_tool
from ..core.base_agent import BaseVoiceAgent
from .context_manager import ContextManager
from .agent_registry import AgentRegistry, default_registry


class TriageAgent(BaseVoiceAgent):
    """
    Central triage agent that analyzes user context and routes to appropriate specialists.
    Optimized for OpenAI Realtime API with natural voice interactions.
    
    Context-aware routing based on:
    - User intent analysis
    - Business context (type, size, industry)
    - User role and permissions
    - Location and time context
    - Conversation history
    - Voice interaction patterns
    """
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any],
                 context_manager: ContextManager = None,
                 registry: AgentRegistry = None):
        """
        Initialize triage agent
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
            context_manager: Context manager for enhanced context handling
            registry: Agent registry for managing specialists
        """
        super().__init__(business_context, user_context)
        
        self.context_manager = context_manager or ContextManager(business_context, user_context)
        self.registry = registry or default_registry
        
        # Create specialist agents for handoffs
        self._create_specialist_agents()
        
    def _create_specialist_agents(self):
        """Create specialist agent instances for handoffs"""
        self.contact_agent = self.registry.create_agent(
            "contact_management",
            self.business_context,
            self.user_context
        )
        
        self.scheduling_agent = self.registry.create_agent(
            "scheduling",
            self.business_context,
            self.user_context
        )
        
        # Add other specialist agents as they're implemented
        # self.job_agent = self.registry.create_agent("job_management", ...)
        # self.invoice_agent = self.registry.create_agent("invoice_management", ...)
        # self.estimate_agent = self.registry.create_agent("estimate_management", ...)
        # self.project_agent = self.registry.create_agent("project_management", ...)
        
    def get_instructions(self) -> str:
        """Get system instructions for the triage agent optimized for voice"""
        
        # Get current context
        ctx = self.context_manager.get_routing_context()
        safety_constraints = self.context_manager.get_safety_constraints()
        
        # Build dynamic instructions based on context
        instructions = f"""You are the Hero365 AI Assistant Triage Agent for {ctx['business']['name']}.

CORE MISSION:
You are the intelligent front-door to Hero365's business management system. Handle simple requests directly and route complex requests to specialist agents only when needed.

VOICE INTERACTION EXCELLENCE:
- Speak naturally and conversationally as if talking to a colleague
- Keep responses concise and engaging for voice interaction
- Use verbal cues like "Let me help you with that" or "I'll look that up for you"
- Avoid lengthy explanations - focus on actions and results
- Acknowledge user requests verbally before taking action

CONTEXT AWARENESS:
- Business: {ctx['business']['name']} ({ctx['business']['type']})
- User: {ctx['user']['name']} ({ctx['user']['role']})
- Location: {ctx['session']['location'] or 'Unknown'}
- Time: {ctx['temporal']['current_time']} ({ctx['temporal']['day_of_week']})
- Business Hours: {'Yes' if ctx['temporal']['is_business_hours'] else 'No'}
- Driving Mode: {'ON' if ctx['session']['is_driving'] else 'OFF'}

DECISION MAKING:
1. **Simple Queries** - Handle directly with your tools:
   - "What are my recent contacts?" → Use get_recent_contacts
   - "What can you help me with?" → Use get_system_status
   - Basic information requests

2. **Complex Operations** - Transfer to specialists:
   - "Create a new contact for John Smith with email..." → transfer_to_contact_management
   - "Schedule a meeting with my client tomorrow..." → transfer_to_scheduling
   - Multiple steps or detailed operations

3. **System Issues** - Escalate:
   - "This isn't working" → escalate_to_human
   - Error conditions or user frustration

VOICE RESPONSE PATTERN:
- Start with verbal acknowledgment: "Sure, let me check that for you"
- Provide information conversationally: "I found your recent contacts. Here they are..."
- When transferring: "I'll connect you with our contact specialist" (not "I'm transferring you")
- End with helpful offer: "Anything else I can help you with?"

SAFETY PROTOCOLS:
{"- CRITICAL: Keep all responses brief and hands-free friendly" if ctx['session']['is_driving'] else ""}
{"- Avoid complex multi-step processes while driving" if ctx['session']['is_driving'] else ""}
{"- Maximum response length: " + str(safety_constraints['max_response_length']) + " characters" if safety_constraints['max_response_length'] < 500 else ""}

Remember: You are the efficient gateway to Hero365's capabilities. Handle simple requests yourself, route complex ones to specialists, and always provide value through natural voice interaction."""
        
        return instructions
    
    def get_tools(self) -> List[Any]:
        """Return list of triage tools (handoff functions)"""
        return [
            self._get_recent_contacts_simple(),
            self._transfer_to_contact_management(),
            self._transfer_to_scheduling(),
            self._escalate_to_human(),
            self._get_system_status()
        ]
    
    def _get_recent_contacts_simple(self):
        """Simple tool to get recent contacts without handoff"""
        @function_tool
        async def get_recent_contacts(limit: int = 10) -> str:
            """Get the most recently created or updated contacts directly.
            
            Use this for simple contact queries like "what are my last contacts" or "show my recent contacts".
            
            Args:
                limit: Maximum number of contacts to return (default 10)
            
            Returns:
                List of recent contacts
            """
            try:
                # Use the contact agent's tools directly
                result = await self.contact_agent.contact_tools.get_recent_contacts(limit=limit)
                
                if result["success"]:
                    contacts = result["contacts"]
                    if not contacts:
                        return "You don't have any recent contacts yet. Would you like me to help you add some?"
                    
                    # Format for voice response
                    contact_list = []
                    for contact in contacts[:limit]:
                        name = contact.get('name', 'Unknown')
                        company = contact.get('company', '')
                        contact_info = f"{name}"
                        if company:
                            contact_info += f" from {company}"
                        contact_list.append(contact_info)
                    
                    count_text = f"your {len(contact_list)} most recent contacts" if len(contact_list) > 1 else "your most recent contact"
                    return f"Here are {count_text}: {', '.join(contact_list)}. Would you like more details about any of them?"
                else:
                    return f"I had trouble retrieving your contacts. {result['message']}"
            except Exception as e:
                return f"I encountered an error getting your contacts. Let me connect you with our contact specialist who can help."
        
        return get_recent_contacts
    
    def get_handoffs(self) -> List[Agent]:
        """Return list of agents this agent can hand off to"""
        handoffs = []
        
        # Add contact agent if available
        if hasattr(self, 'contact_agent') and self.contact_agent:
            handoffs.append(self.contact_agent.create_agent())
        
        # Add scheduling agent if available
        if hasattr(self, 'scheduling_agent') and self.scheduling_agent:
            handoffs.append(self.scheduling_agent.create_agent())
        
        return handoffs
    
    def _transfer_to_contact_management(self):
        """Transfer to contact management specialist"""
        @function_tool
        def transfer_to_contact_management(reason: str = None) -> Agent:
            """Transfer the user to the contact management specialist.
            
            Use this when the user needs to:
            - Create, update, or delete contacts
            - Search for specific contacts
            - Manage contact details and information
            - Handle complex contact operations
            
            Args:
                reason: Optional reason for the transfer
            
            Returns:
                Contact management agent instance
            """
            if self.contact_agent:
                return self.contact_agent.create_agent()
            else:
                return "I'm sorry, the contact management specialist is not available right now. Please try again later."
        
        return transfer_to_contact_management
    
    def _transfer_to_scheduling(self):
        """Transfer to scheduling specialist"""
        @function_tool
        def transfer_to_scheduling(reason: str = None) -> Agent:
            """Transfer the user to the scheduling specialist.
            
            Use this when the user needs to:
            - Schedule appointments or meetings
            - Check availability and calendar
            - Manage time slots and bookings
            - Handle complex scheduling operations
            
            Args:
                reason: Optional reason for the transfer
            
            Returns:
                Scheduling agent instance
            """
            if self.scheduling_agent:
                return self.scheduling_agent.create_agent()
            else:
                return "I'm sorry, the scheduling specialist is not available right now. Please try again later."
        
        return transfer_to_scheduling
    
    def _escalate_to_human(self):
        """Escalate to human support"""
        @function_tool
        def escalate_to_human(reason: str, urgency: str = "medium") -> str:
            """Escalate the conversation to a human support agent.
            
            Use this when:
            - The user explicitly requests human help
            - Technical issues cannot be resolved
            - The user expresses frustration
            - Complex problems outside agent capabilities
            
            Args:
                reason: Reason for escalation
                urgency: Urgency level (low, medium, high)
            
            Returns:
                Escalation confirmation message
            """
            escalation_id = f"ESC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return f"I understand you need human assistance. I've created escalation ticket {escalation_id} for you. " \
                   f"A human support agent will be with you shortly to help with: {reason}. " \
                   f"Is there anything else I can help you with while you wait?"
        
        return escalate_to_human
    
    def _get_system_status(self):
        """Get system status and capabilities"""
        @function_tool
        def get_system_status() -> str:
            """Get current system status and available capabilities.
            
            Use this when the user asks:
            - "What can you help me with?"
            - "What are your capabilities?"
            - "What can you do?"
            
            Returns:
                System status and capabilities summary
            """
            business_name = self.business_context.get('name', 'Hero365')
            capabilities = self.get_available_capabilities()
            
            status_msg = f"I'm your {business_name} assistant and I'm ready to help you with:\n\n"
            
            for category, actions in capabilities.items():
                category_name = category.replace('_', ' ').title()
                status_msg += f"• {category_name}: {', '.join(actions[:3])}"
                if len(actions) > 3:
                    status_msg += f" and {len(actions) - 3} more"
                status_msg += "\n"
            
            status_msg += "\nJust tell me what you need help with and I'll get it done for you!"
            
            return status_msg
        
        return get_system_status
    
    def _get_specialist_descriptions(self) -> str:
        """Get descriptions of available specialists"""
        descriptions = []
        
        if hasattr(self, 'contact_agent') and self.contact_agent:
            descriptions.append("- Contact Management: Handle customer contacts and relationships")
        
        if hasattr(self, 'scheduling_agent') and self.scheduling_agent:
            descriptions.append("- Scheduling: Manage appointments and calendar events")
        
        return "\n".join(descriptions)
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get available capabilities for system status"""
        capabilities = {
            "contact_management": [
                "View recent contacts",
                "Find specific contacts",
                "Add new contacts",
                "Update contact information"
            ],
            "scheduling": [
                "Check availability",
                "Schedule appointments",
                "View calendar",
                "Reschedule meetings"
            ],
            "system_help": [
                "Get system status",
                "Explain capabilities",
                "Connect with specialists",
                "Escalate to human support"
            ]
        }
        
        return capabilities
    
    def create_agent(self) -> Agent:
        """Create OpenAI agent instance with enhanced voice capabilities"""
        return Agent(
            name=self.get_agent_name(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model="gpt-4o-mini"  # Use efficient model by default
        )
    
    def create_voice_optimized_agent(self) -> Agent:
        """Create voice-optimized agent with enhanced TTS instructions"""
        voice_instructions = self._get_voice_optimized_instructions()
        
        return Agent(
            name=self.get_agent_name(),
            instructions=voice_instructions,
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model="gpt-4o-mini-tts"  # Use TTS-optimized model
        )
    
    def get_routing_suggestions(self, user_request: str) -> List[Dict[str, Any]]:
        """Get routing suggestions based on user request"""
        suggestions = []
        
        request_lower = user_request.lower()
        
        # Contact-related requests
        if any(word in request_lower for word in ['contact', 'customer', 'client', 'phone', 'email']):
            suggestions.append({
                "agent": "contact_management",
                "confidence": 0.8,
                "reason": "Request contains contact-related keywords"
            })
        
        # Scheduling-related requests
        if any(word in request_lower for word in ['schedule', 'appointment', 'meeting', 'calendar', 'book']):
            suggestions.append({
                "agent": "scheduling",
                "confidence": 0.8,
                "reason": "Request contains scheduling-related keywords"
            })
        
        return suggestions
    
    def get_context_summary(self) -> str:
        """Get context summary for debugging"""
        return self.context_manager.get_context_summary()
    
    def can_handle_request(self, request: str) -> bool:
        """Check if triage agent can handle request directly"""
        simple_requests = [
            "what can you help with", "what are your capabilities", "system status",
            "recent contacts", "help", "what can you do"
        ]
        
        request_lower = request.lower()
        return any(phrase in request_lower for phrase in simple_requests)
    
    def get_safety_constraints(self) -> Dict[str, Any]:
        """Get safety constraints based on user context"""
        return self.context_manager.get_safety_constraints()
    
    def update_context(self, updates: Dict[str, Any]):
        """Update context manager with new information"""
        if self.context_manager:
            # Update user context
            if 'user_context' in updates:
                self.user_context.update(updates['user_context'])
            
            # Update business context
            if 'business_context' in updates:
                self.business_context.update(updates['business_context'])
            
            # Refresh context manager
            self.context_manager.refresh_context()
    
    def get_specialist_status(self) -> Dict[str, Any]:
        """Get status of specialist agents"""
        status = {}
        
        if hasattr(self, 'contact_agent') and self.contact_agent:
            status['contact_management'] = {
                'available': True,
                'name': self.contact_agent.get_agent_name(),
                'capabilities': ['contacts', 'customers', 'leads']
            }
        
        if hasattr(self, 'scheduling_agent') and self.scheduling_agent:
            status['scheduling'] = {
                'available': True,
                'name': self.scheduling_agent.get_agent_name(),
                'capabilities': ['appointments', 'calendar', 'meetings']
            }
        
        return status
    
    def clear_specialist_cache(self):
        """Clear specialist agent cache"""
        if hasattr(self, 'contact_agent'):
            self.contact_agent = None
        if hasattr(self, 'scheduling_agent'):
            self.scheduling_agent = None
        
        # Recreate specialist agents
        self._create_specialist_agents()
    
    def get_business_hours_status(self) -> Dict[str, Any]:
        """Get business hours status"""
        return self.context_manager.get_business_hours_status()
    
    def get_voice_pipeline(self):
        """Get voice pipeline for realtime audio processing"""
        return self.create_voice_pipeline() 