"""
Triage Agent for Voice Agent System

Central triage agent that analyzes user context and routes requests to appropriate specialists.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from agents import Agent
from ..core.base_agent import BaseVoiceAgent
from .context_manager import ContextManager
from .specialist_tools import SpecialistAgentTools
from .agent_registry import AgentRegistry, default_registry


class TriageAgent(BaseVoiceAgent):
    """
    Central triage agent that analyzes user context and routes to appropriate specialists.
    
    Context-aware routing based on:
    - User intent analysis
    - Business context (type, size, industry)
    - User role and permissions
    - Location and time context
    - Conversation history
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
        self.specialist_tools = SpecialistAgentTools(self.context_manager, self.registry)
        
    def get_instructions(self) -> str:
        """Get system instructions for the triage agent"""
        
        # Get current context
        ctx = self.context_manager.get_routing_context()
        safety_constraints = self.context_manager.get_safety_constraints()
        
        # Build dynamic instructions based on context
        instructions = f"""You are the Hero365 AI Assistant Triage Agent for {ctx['business']['name']}.

CORE MISSION:
Analyze user requests and intelligently route them to the most appropriate specialist agents based on intent, context, and business needs. You are the central intelligence that ensures users get connected to the right expert for their specific needs.

CONTEXT AWARENESS:
- Business: {ctx['business']['name']} ({ctx['business']['type']})
- User: {ctx['user']['name']} ({ctx['user']['role']})
- Location: {ctx['session']['location'] or 'Unknown'}
- Time: {ctx['temporal']['current_time']} ({ctx['temporal']['day_of_week']})
- Business Hours: {'Yes' if ctx['temporal']['is_business_hours'] else 'No'}
- Driving Mode: {'ON' if ctx['session']['is_driving'] else 'OFF'}

AVAILABLE SPECIALISTS:
{self._get_specialist_descriptions()}

ROUTING INTELLIGENCE:
1. **Intent Analysis**: Carefully analyze what the user wants to accomplish
2. **Context Consideration**: Factor in business type, user role, time, location
3. **Permission Checking**: Ensure user has access to requested functions
4. **Complexity Assessment**: Determine if single or multiple specialists needed
5. **Safety Evaluation**: Consider driving mode and safety constraints

ROUTING PATTERNS:
- **Simple Requests**: Route to single most appropriate specialist
- **Complex Requests**: Use parallel execution for multi-domain tasks
- **Ambiguous Requests**: Ask clarifying questions before routing
- **Unauthorized Requests**: Politely explain permission requirements
- **Emergency Requests**: Escalate to human support when appropriate

RESPONSE PATTERN:
1. **Acknowledge**: Briefly acknowledge the user's request
2. **Analyze**: Understand the intent and context
3. **Route**: Connect to appropriate specialist(s)
4. **Synthesize**: Provide coherent response from specialist results
5. **Follow-up**: Offer related assistance or next steps

SAFETY PROTOCOLS:
{"- CRITICAL: Keep all responses brief and hands-free friendly" if ctx['session']['is_driving'] else ""}
{"- Avoid complex multi-step processes while driving" if ctx['session']['is_driving'] else ""}
{"- Limit financial transactions and confirmations while driving" if ctx['session']['is_driving'] else ""}
{"- Maximum response length: " + str(safety_constraints['max_response_length']) + " characters" if safety_constraints['max_response_length'] < 500 else ""}

COMMUNICATION STYLE:
- Be professional, friendly, and efficient
- Use natural conversational language
- Provide clear routing explanations when helpful
- Acknowledge when you're connecting to specialists
- Synthesize specialist responses into coherent answers
- Ask clarifying questions when intent is unclear

ESCALATION TRIGGERS:
- Legal or compliance issues
- Major system failures or errors
- High-value client concerns requiring human judgment
- Requests outside all specialist capabilities
- User explicitly requests human support

BUSINESS CONTEXT OPTIMIZATION:
- Home Services: Focus on job scheduling, customer management
- Contracting: Emphasize project management, estimates, invoicing
- Field Service: Prioritize scheduling, job tracking, inventory
- General: Provide balanced access to all specialists

Remember: Your goal is to be an intelligent router that ensures {ctx['user']['name']} gets connected to the right specialist for their specific business needs. You are the front door to Hero365's comprehensive business management capabilities."""

        return instructions
    
    def _get_specialist_descriptions(self) -> str:
        """Get formatted descriptions of available specialists"""
        descriptions = []
        
        # Get compatible agents for current context
        compatible_agents = self.registry.get_compatible_agents(
            self.context_manager.business_context,
            self.context_manager.user_context
        )
        
        # Format descriptions for compatible agents
        for agent_name in compatible_agents:
            config = self.registry.get_agent_by_name(agent_name)
            if config:
                key_capabilities = ", ".join(config.capabilities[:3])
                descriptions.append(f"**{config.name.title()}**: {config.description} ({key_capabilities})")
        
        return "\n".join(descriptions)
    
    def get_tools(self) -> List[Any]:
        """Get all available tools for the triage agent"""
        return self.specialist_tools.get_all_tools()
    
    def get_handoffs(self) -> List[Agent]:
        """Get agents this agent can hand off to (none for triage pattern)"""
        return []
    
    def get_agent_name(self) -> str:
        """Get agent name for identification"""
        business_name = self.business_context.get('name', 'Hero365')
        return f"{business_name} AI Assistant"
    
    def get_personalized_greeting(self) -> str:
        """Generate personalized greeting based on context"""
        ctx = self.context_manager.get_routing_context()
        
        user_name = ctx['user']['name'] or 'there'
        business_name = ctx['business']['name'] or 'Hero365'
        
        # Time-based greeting
        current_hour = ctx['temporal']['current_hour']
        if current_hour < 12:
            time_greeting = "Good morning"
        elif current_hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        # Context-aware greeting
        if ctx['session']['is_driving']:
            return f"{time_greeting} {user_name}! I'm your {business_name} assistant. I'll keep this brief since you're driving. What can I help you with?"
        elif not ctx['temporal']['is_business_hours']:
            return f"{time_greeting} {user_name}! I'm your {business_name} assistant. I'm here to help even outside business hours. What do you need assistance with?"
        else:
            return f"{time_greeting} {user_name}! I'm your {business_name} assistant. I can help you with scheduling, jobs, invoicing, contacts, and more. What would you like to do?"
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get summary of available capabilities through specialists"""
        capabilities = {}
        
        # Get compatible agents
        compatible_agents = self.registry.get_compatible_agents(
            self.context_manager.business_context,
            self.context_manager.user_context
        )
        
        # Get capabilities for each compatible agent
        for agent_name in compatible_agents:
            config = self.registry.get_agent_by_name(agent_name)
            if config:
                capabilities[agent_name] = config.capabilities
        
        return capabilities
    
    def create_agent(self) -> Agent:
        """Create OpenAI agent instance with triage capabilities"""
        return Agent(
            name=self.get_agent_name(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model="gpt-4o-mini"  # Use efficient model for triage
        )
    
    def create_voice_optimized_agent(self) -> Agent:
        """Create agent specifically optimized for voice interactions"""
        return Agent(
            name=self.get_agent_name(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model="gpt-4o-mini"
        )
    
    def get_routing_suggestions(self, user_request: str) -> List[Dict[str, Any]]:
        """Get routing suggestions for a user request"""
        return self.specialist_tools.get_routing_suggestions(user_request)
    
    def get_context_summary(self) -> str:
        """Get formatted summary of current context"""
        return self.context_manager.get_context_summary()
    
    def can_handle_request(self, request: str) -> bool:
        """Check if the triage agent can handle a request"""
        # Triage agent can handle any request by routing to specialists
        return True
    
    def get_safety_constraints(self) -> Dict[str, Any]:
        """Get current safety constraints"""
        return self.context_manager.get_safety_constraints()
    
    def update_context(self, updates: Dict[str, Any]):
        """Update user or business context"""
        if "user" in updates:
            self.context_manager.user_context.update(updates["user"])
        if "business" in updates:
            self.context_manager.business_context.update(updates["business"])
    
    def get_specialist_status(self) -> Dict[str, Any]:
        """Get status of specialist agents"""
        return {
            "available_specialists": len(self.registry.get_all_agents()),
            "compatible_specialists": len(self.registry.get_compatible_agents(
                self.context_manager.business_context,
                self.context_manager.user_context
            )),
            "cached_agents": self.specialist_tools.get_cached_agents(),
            "registry_health": "healthy"
        }
    
    def clear_specialist_cache(self):
        """Clear cached specialist agents"""
        self.specialist_tools.clear_agent_cache()
    
    def get_business_hours_status(self) -> Dict[str, Any]:
        """Get business hours status"""
        ctx = self.context_manager.get_routing_context()
        return {
            "is_business_hours": ctx['temporal']['is_business_hours'],
            "current_time": ctx['temporal']['current_time'],
            "day_of_week": ctx['temporal']['day_of_week'],
            "business_hours": ctx['business']['business_hours']
        } 