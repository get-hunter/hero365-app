"""
Triage agent that routes user requests to appropriate specialist agents.
"""

from typing import List, Dict, Any, Optional
# from openai_agents import Agent, tool, handoff
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
import logging

logger = logging.getLogger(__name__)


class TriageAgent(BaseVoiceAgent):
    """Main triage agent that routes to specialist agents"""
    
    def __init__(self, context_manager: ContextManager, specialist_agents: Dict[str, Any]):
        """
        Initialize triage agent with specialist agents.
        
        Args:
            context_manager: Shared context manager
            specialist_agents: Dictionary of specialist agents
        """
        self.specialist_agents = specialist_agents
        
        instructions = """
        You are the main assistant for Hero365, an AI-native ERP system for home services 
        businesses and independent contractors. Your role is to understand what the user needs 
        and seamlessly connect them with the right specialist to help them.
        
        You can help users with:
        - Contact management (creating, updating, searching contacts)
        - Job management (scheduling, tracking, updating jobs)
        - Estimates (creating, sending, converting to invoices)
        - Invoicing (creating, sending, tracking payments)
        - Project management (tracking progress, milestones)
        - Scheduling (appointments, availability, calendar management)
        - Payments (processing, tracking, collections)
        
        When you understand what they need, transfer them to the appropriate specialist.
        Never tell the user about the transfer - just seamlessly continue the conversation.
        Be warm, helpful, and professional in your responses.
        """
        
        super().__init__(
            name="Hero365 Assistant",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.get_system_status,
                self.get_quick_stats,
                self.search_everything,
                self.search_web,
                self.get_business_overview,
                self.get_user_capabilities
            ]
        )
    
    def get_handoffs(self) -> List[Any]:
        """Return list of agents this agent can hand off to"""
        return list(self.specialist_agents.values())
    
    # @tool
    async def get_system_status(self) -> str:
        """Get current system status and recent activity"""
        try:
            context = await self.get_context()
            business_name = context.get("business_name", "your business")
            
            # This would integrate with actual system monitoring
            # For now, return a basic status
            return f"""
            Everything looks good with {business_name}! 
            
            The system is running smoothly and all services are operational.
            
            What can I help you with today?
            """
        except Exception as e:
            return await self.format_error_response(
                "get_system_status",
                e,
                "I'm having trouble checking the system status right now, but I'm here to help you with your business needs."
            )
    
    # @tool
    async def get_quick_stats(self) -> str:
        """Get quick business statistics"""
        try:
            context = await self.get_context()
            business_name = context.get("business_name", "your business")
            
            # This would integrate with actual analytics
            # For now, return placeholder stats
            return f"""
            Here's a quick overview of {business_name}:
            
            • Active jobs: 3
            • Pending estimates: 2
            • Upcoming appointments: 5
            • Recent activity: 12 interactions today
            
            Would you like me to dive deeper into any of these areas?
            """
        except Exception as e:
            return await self.format_error_response(
                "get_quick_stats",
                e,
                "I'm having trouble getting your business stats right now, but I can still help you with specific tasks."
            )
    
    # @tool
    async def search_everything(self, query: str) -> str:
        """Search across all Hero365 data"""
        try:
            # This would integrate with the actual search functionality
            # For now, return a placeholder response
            return f"""
            I searched for '{query}' across your business data.
            
            I found some relevant results, but let me connect you with the right specialist 
            who can help you with the specific details you need.
            """
        except Exception as e:
            return await self.format_error_response(
                "search_everything",
                e,
                f"I'm having trouble searching for '{query}' right now, but I can connect you with a specialist who can help."
            )
    
    # @tool
    async def search_web(self, query: str) -> str:
        """Search the web for real-time information relevant to business operations"""
        try:
            # This would integrate with OpenAI's web search tool
            # For now, return a placeholder response
            return f"""
            I searched the web for information about '{query}' relevant to your business.
            
            Based on current information, here's what I found: [web search results would go here]
            
            Would you like me to help you apply this information to your business operations?
            """
        except Exception as e:
            return await self.format_error_response(
                "search_web",
                e,
                f"I'm having trouble searching the web for '{query}' right now, but I can still help you with your business needs."
            )
    
    # @tool
    async def get_business_overview(self) -> str:
        """Get overview of current business status"""
        try:
            context = await self.get_context()
            business_name = context.get("business_name", "your business")
            user_name = context.get("user_name", "")
            
            return f"""
            Welcome to {business_name}! 
            
            I'm here to help you manage your business operations efficiently. 
            I can assist you with contacts, jobs, estimates, invoices, scheduling, and more.
            
            What would you like to work on today?
            """
        except Exception as e:
            return await self.format_error_response(
                "get_business_overview",
                e,
                "I'm here to help you with your business operations. What would you like to work on?"
            )
    
    # @tool
    async def get_user_capabilities(self) -> str:
        """Get user's capabilities and permissions"""
        try:
            context = await self.get_context()
            user_role = context.get("user_role", "user")
            
            capabilities = [
                "View and manage contacts",
                "Create and track jobs",
                "Generate estimates and invoices",
                "Schedule appointments",
                "Access business analytics"
            ]
            
            return f"""
            As a {user_role}, you have access to:
            
            """ + "\n".join(f"• {cap}" for cap in capabilities) + """
            
            What would you like to do?
            """
        except Exception as e:
            return await self.format_error_response(
                "get_user_capabilities",
                e,
                "I can help you with various business operations. What would you like to work on?"
            )
    
    # Handoff functions to specialist agents
    # @handoff
    def transfer_to_contact_specialist(self) -> Any:
        """Transfer to contact management specialist"""
        return self.specialist_agents.get("contact")
    
    # @handoff
    def transfer_to_job_specialist(self) -> Any:
        """Transfer to job management specialist"""
        return self.specialist_agents.get("job")
    
    # @handoff
    def transfer_to_estimate_specialist(self) -> Any:
        """Transfer to estimate specialist"""
        return self.specialist_agents.get("estimate")
    
    # @handoff
    def transfer_to_invoice_specialist(self) -> Any:
        """Transfer to invoice specialist"""
        return self.specialist_agents.get("invoice")
    
    # @handoff
    def transfer_to_payment_specialist(self) -> Any:
        """Transfer to payment specialist"""
        return self.specialist_agents.get("payment")
    
    # @handoff
    def transfer_to_project_specialist(self) -> Any:
        """Transfer to project specialist"""
        return self.specialist_agents.get("project")
    
    # @handoff
    def transfer_to_scheduling_specialist(self) -> Any:
        """Transfer to scheduling specialist"""
        return self.specialist_agents.get("scheduling")
    
    # @handoff
    def escalate_to_human(self) -> Any:
        """Escalate to human support"""
        # This would typically connect to a human agent system
        # For now, return None to indicate this handoff is not yet implemented
        return None
    
    async def determine_intent(self, user_input: str) -> str:
        """
        Determine user intent to help with routing decisions.
        
        Args:
            user_input: User's message
            
        Returns:
            Detected intent category
        """
        try:
            # This would use NLP to determine intent
            # For now, use simple keyword matching
            user_input_lower = user_input.lower()
            
            # Contact-related intents
            if any(word in user_input_lower for word in ["contact", "customer", "client", "phone", "email"]):
                return "contact_management"
            
            # Job-related intents
            elif any(word in user_input_lower for word in ["job", "work", "task", "project", "service"]):
                return "job_management"
            
            # Estimate-related intents
            elif any(word in user_input_lower for word in ["estimate", "quote", "proposal", "bid"]):
                return "estimate_management"
            
            # Invoice-related intents
            elif any(word in user_input_lower for word in ["invoice", "bill", "payment", "charge"]):
                return "invoice_management"
            
            # Scheduling-related intents
            elif any(word in user_input_lower for word in ["schedule", "appointment", "calendar", "booking"]):
                return "scheduling"
            
            # General or unclear intent
            else:
                return "general"
                
        except Exception as e:
            logger.error(f"Error determining intent: {e}")
            return "general"
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Intent detection and routing",
            "System status monitoring",
            "Business overview and statistics",
            "Universal search capabilities",
            "Web search integration",
            "Handoff to specialist agents",
            "User capability assessment"
        ] 