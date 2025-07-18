"""
Base Agent for Hero365 LiveKit Voice Agents with Business Context Support
Provides common functionality for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from livekit.agents import function_tool, RunContext
from .tools.hero365_tools_wrapper import Hero365ToolsWrapper
from .monitoring.metrics import get_metrics
from .context_management import get_context_manager
from .business_context_manager import BusinessContextManager

logger = logging.getLogger(__name__)

class Hero365BaseAgent(ABC):
    """Base class for all Hero365 specialized agents with business context support"""
    
    def __init__(self, config, agent_type: str = "base"):
        self.config = config
        self.agent_type = agent_type
        self.context_manager = None
        self.metrics = None
        self.business_context_manager: Optional[BusinessContextManager] = None
        self.tools_wrapper = None
        
        # Agent state
        self.is_initialized = False
        self.conversation_context = []
        self.current_task = None
        
    async def initialize(self):
        """Initialize the agent with context and tools"""
        try:
            # Initialize context manager and metrics
            self.context_manager = await get_context_manager()
            self.metrics = await get_metrics()
            
            # Initialize tools wrapper
            self.tools_wrapper = Hero365ToolsWrapper(self.context_manager)
            
            # Set business context if available
            if self.business_context_manager:
                self.tools_wrapper.set_business_context(self.business_context_manager)
            
            self.is_initialized = True
            logger.info(f"✅ {self.agent_type} agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing {self.agent_type} agent: {e}")
            raise
    
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        
        # Also set it on tools wrapper if available
        if self.tools_wrapper:
            self.tools_wrapper.set_business_context(business_context_manager)
        
        logger.info(f"📊 Business context set for {self.agent_type} agent")
    
    def get_business_context_summary(self) -> Dict[str, Any]:
        """Get business context summary for the agent"""
        if not self.business_context_manager:
            return {}
        
        business_context = self.business_context_manager.get_business_context()
        business_summary = self.business_context_manager.get_business_summary()
        suggestions = self.business_context_manager.get_contextual_suggestions()
        
        return {
            "business_name": business_context.business_name if business_context else None,
            "active_jobs": business_summary.active_jobs if business_summary else 0,
            "pending_estimates": business_summary.pending_estimates if business_summary else 0,
            "recent_contacts_count": len(self.business_context_manager.get_recent_contacts()),
            "suggestions": {
                "urgent_items": suggestions.urgent_items if suggestions else [],
                "quick_actions": suggestions.quick_actions if suggestions else [],
                "opportunities": suggestions.opportunities if suggestions else []
            }
        }
    
    def get_context_aware_suggestions(self, context_type: str) -> List[str]:
        """Get context-aware suggestions based on business state"""
        if not self.business_context_manager:
            return []
        
        suggestions = self.business_context_manager.get_contextual_suggestions()
        if not suggestions:
            return []
        
        context_map = {
            "contacts": suggestions.follow_ups,
            "jobs": suggestions.quick_actions,
            "estimates": suggestions.opportunities,
            "urgent": suggestions.urgent_items
        }
        
        return context_map.get(context_type, [])
    
    def find_relevant_context(self, query: str) -> Dict[str, Any]:
        """Find relevant business context based on query"""
        if not self.business_context_manager:
            return {}
        
        context_matches = {}
        
        # Check for contact matches
        contact_match = self.business_context_manager.find_contact_by_name(query)
        if contact_match:
            context_matches["contact"] = {
                "name": contact_match.name,
                "phone": contact_match.phone,
                "email": contact_match.email,
                "recent_jobs": contact_match.recent_jobs,
                "recent_estimates": contact_match.recent_estimates
            }
        
        # Check for job matches
        job_match = self.business_context_manager.find_job_by_title(query)
        if job_match:
            context_matches["job"] = {
                "title": job_match.title,
                "status": job_match.status,
                "contact_name": job_match.contact_name,
                "scheduled_date": job_match.scheduled_date,
                "priority": job_match.priority
            }
        
        # Check for estimate matches
        estimate_match = self.business_context_manager.find_estimate_by_title(query)
        if estimate_match:
            context_matches["estimate"] = {
                "title": estimate_match.title,
                "status": estimate_match.status,
                "contact_name": estimate_match.contact_name,
                "total_amount": estimate_match.total_amount,
                "created_date": estimate_match.created_date
            }
        
        return context_matches
    
    async def get_contextual_greeting(self) -> str:
        """Generate contextual greeting based on agent type and business state"""
        if not self.business_context_manager:
            return f"Hello! I'm your {self.agent_type} specialist. How can I help you today?"
        
        business_context = self.business_context_manager.get_business_context()
        suggestions = self.get_context_aware_suggestions(self.agent_type)
        
        greeting_parts = []
        greeting_parts.append(f"Hello! I'm your {self.agent_type} specialist for {business_context.business_name if business_context else 'your business'}.")
        
        # Add agent-specific context
        if self.agent_type == "contact" and suggestions:
            greeting_parts.append(f"I noticed you have some contacts that might need follow-up.")
        elif self.agent_type == "job" and suggestions:
            greeting_parts.append(f"I can help you with job scheduling and management.")
        elif self.agent_type == "estimate" and suggestions:
            greeting_parts.append(f"I can help you with pending estimates and proposals.")
        
        greeting_parts.append("What would you like to work on?")
        
        return " ".join(greeting_parts)
    
    async def enhance_response_with_context(self, base_response: str, context_type: str) -> str:
        """Enhance response with relevant business context"""
        if not self.business_context_manager:
            return base_response
        
        suggestions = self.get_context_aware_suggestions(context_type)
        if not suggestions:
            return base_response
        
        # Add contextual suggestions
        enhanced_response = base_response
        
        if suggestions:
            enhanced_response += f"\n💡 Suggested next steps: {suggestions[0]}"
        
        return enhanced_response
    
    def get_specialist_capabilities(self) -> List[str]:
        """Get list of capabilities for this specialist"""
        base_capabilities = [
            "Business context awareness",
            "Smart suggestions",
            "Context-aware search",
            "Proactive recommendations"
        ]
        
        # Add agent-specific capabilities
        if self.agent_type == "contact":
            base_capabilities.extend([
                "Contact creation and management",
                "Contact search and lookup",
                "Contact interaction tracking",
                "Follow-up suggestions"
            ])
        elif self.agent_type == "job":
            base_capabilities.extend([
                "Job creation and scheduling",
                "Job status tracking",
                "Work order management",
                "Priority management"
            ])
        elif self.agent_type == "estimate":
            base_capabilities.extend([
                "Estimate creation and management",
                "Proposal generation",
                "Pricing assistance",
                "Quote tracking"
            ])
        elif self.agent_type == "scheduling":
            base_capabilities.extend([
                "Appointment booking",
                "Calendar management",
                "Availability checking",
                "Schedule optimization"
            ])
        
        return base_capabilities
    
    async def log_interaction(self, message: str, response: str, context: Dict[str, Any] = None):
        """Log interaction with context for metrics"""
        try:
            interaction_data = {
                "agent_type": self.agent_type,
                "message": message[:200],  # Truncate for logging
                "response": response[:200],  # Truncate for logging
                "context": context or {},
                "business_context_available": self.business_context_manager is not None
            }
            
            if self.metrics:
                await self.metrics.log_interaction(interaction_data)
            
            # Add to conversation context
            self.conversation_context.append({
                "user": message,
                "assistant": response,
                "timestamp": logger.info.__module__,  # Using logger timestamp
                "context": context
            })
            
            # Keep only last 10 interactions
            if len(self.conversation_context) > 10:
                self.conversation_context = self.conversation_context[-10:]
                
        except Exception as e:
            logger.error(f"❌ Error logging interaction: {e}")
    
    @abstractmethod
    async def process_message(self, ctx: RunContext, message: str) -> str:
        """Process a message and return appropriate response"""
        pass
    
    async def handle_handoff(self, from_agent: str, context: Dict[str, Any]) -> str:
        """Handle handoff from another agent"""
        try:
            # Log handoff
            logger.info(f"🔄 {self.agent_type} agent receiving handoff from {from_agent}")
            
            # Extract relevant context
            handoff_context = context.get("handoff_context", {})
            user_message = context.get("user_message", "")
            
            # Generate contextual response
            response = await self.get_contextual_greeting()
            
            # Add handoff context if available
            if handoff_context:
                response += f"\nI have the context from {from_agent} and I'm ready to help."
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error handling handoff: {e}")
            return f"I'm your {self.agent_type} specialist. How can I help you?"
    
    async def prepare_for_handoff(self, to_agent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for handoff to another agent"""
        try:
            handoff_context = {
                "from_agent": self.agent_type,
                "to_agent": to_agent,
                "conversation_context": self.conversation_context[-3:],  # Last 3 interactions
                "current_task": self.current_task,
                "business_context_summary": self.get_business_context_summary(),
                "handoff_reason": context.get("handoff_reason", "User request")
            }
            
            logger.info(f"🔄 Preparing handoff from {self.agent_type} to {to_agent}")
            
            return handoff_context
            
        except Exception as e:
            logger.error(f"❌ Error preparing handoff: {e}")
            return {"error": str(e)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_type": self.agent_type,
            "is_initialized": self.is_initialized,
            "has_business_context": self.business_context_manager is not None,
            "conversation_length": len(self.conversation_context),
            "current_task": self.current_task,
            "capabilities": self.get_specialist_capabilities()
        } 