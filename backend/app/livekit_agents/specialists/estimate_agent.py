"""
Estimate management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import logging
import re
import random

from livekit.agents import Agent, RunContext, function_tool
from ..config import LiveKitConfig
from ..business_context_manager import BusinessContextManager

logger = logging.getLogger(__name__)


class EstimateAgent(Agent):
    """Specialist agent for estimate management using LiveKit agents"""
    
    def __init__(self, config: LiveKitConfig):
        """
        Initialize estimate management specialist.
        
        Args:
            config: LiveKit configuration
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        instructions = f"""
        You are the estimate management specialist for Hero365. You help users manage their 
        estimates efficiently and professionally.
        
        CURRENT DATE AND TIME: Today is {current_date} at {current_time}
        
        You have access to tools for:
        - Creating new estimates
        - Updating estimate details
        - Searching for estimates
        - Getting estimate details
        - Converting estimates to invoices
        - Managing estimate lifecycle
        
        Always be helpful and ask for clarification if needed. When creating estimates,
        collect the required information naturally through conversation.
        
        ESTIMATE INFORMATION PRIORITY:
        1. Client contact ID (required)
        2. Title (required)
        3. Description (optional)
        4. Valid until date (optional)
        5. Notes (optional)
        """
        
        # Initialize as LiveKit Agent with tools
        super().__init__(
            instructions=instructions,
            tools=[
                self.create_estimate,
                self.search_estimates,
                self.update_estimate,
                self.get_estimate_details,
                self.convert_to_invoice,
                self.get_pending_estimates,
                self.get_estimate_statistics,
            ]
        )
        
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        
        # Estimate-specific configuration
        self.estimate_context = {}
        self.current_estimate = None
        
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        logger.info("📊 Business context set for estimate agent")
    
    @function_tool
    async def create_estimate(self,
                             ctx: RunContext,
                             client_contact_id: str,
                             title: str,
                             description: Optional[str] = None,
                             valid_until_date: Optional[str] = None,
                             notes: Optional[str] = None) -> str:
        """Create a new estimate with the provided information"""
        try:
            logger.info(f"Creating estimate: {title}")
            
            # Mock estimate creation (would integrate with real system)
            estimate_id = f"est_{uuid.uuid4().hex[:8]}"
            estimate_number = f"E{random.randint(1000, 9999)}"
            
            response = f"✅ Estimate #{estimate_number} '{title}' created successfully! Estimate ID: {estimate_id}"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self._get_context_suggestions()
                if suggestions:
                    response += f"\n💡 Suggested next steps: {suggestions[0]}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating estimate: {e}")
            return f"❌ I encountered an error while creating the estimate: {str(e)}"
    
    @function_tool
    async def search_estimates(self, ctx: RunContext, query: str, limit: int = 10) -> str:
        """Search for estimates by title, description, or contact"""
        try:
            logger.info(f"Searching estimates for: {query}")
            
            # Mock search results (would integrate with real system)
            mock_results = [
                {"title": f"Sample Estimate {i}", "status": "pending", "total": f"${i*100+200}"}
                for i in range(1, min(limit, 4))
            ]
            
            if not mock_results:
                return f"No estimates found matching '{query}'"
            
            estimates_text = "\n".join([
                f"• {est['title']} - {est['status']} - {est['total']}"
                for est in mock_results
            ])
            
            return f"📊 Found {len(mock_results)} estimate(s) matching '{query}':\n{estimates_text}"
            
        except Exception as e:
            logger.error(f"Error searching estimates: {e}")
            return f"❌ I encountered an error while searching for estimates: {str(e)}"
    
    @function_tool
    async def update_estimate(self, ctx: RunContext, estimate_id: str, updates: Dict[str, Any]) -> str:
        """Update estimate information"""
        try:
            logger.info(f"Updating estimate: {estimate_id}")
            
            # Mock estimate update (would integrate with real system)
            update_fields = ", ".join(updates.keys())
            
            return f"✅ Estimate {estimate_id} updated successfully! Updated fields: {update_fields}"
            
        except Exception as e:
            logger.error(f"Error updating estimate: {e}")
            return f"❌ I encountered an error while updating the estimate: {str(e)}"
    
    @function_tool
    async def get_estimate_details(self, ctx: RunContext, estimate_id: str) -> str:
        """Get detailed information about a specific estimate"""
        try:
            logger.info(f"Getting estimate details for: {estimate_id}")
            
            # Mock estimate details (would integrate with real system)
            return f"📋 Estimate Details for {estimate_id}:\n• Title: Sample Estimate\n• Status: Pending\n• Total: $1,200\n• Valid Until: 2025-08-15\n• Created: 2025-07-15"
            
        except Exception as e:
            logger.error(f"Error getting estimate details: {e}")
            return f"❌ I encountered an error while getting estimate details: {str(e)}"
    
    @function_tool
    async def convert_to_invoice(self, ctx: RunContext, estimate_id: str, notes: Optional[str] = None) -> str:
        """Convert an estimate to an invoice"""
        try:
            logger.info(f"Converting estimate to invoice: {estimate_id}")
            
            # Mock conversion (would integrate with real system)
            invoice_id = f"inv_{uuid.uuid4().hex[:8]}"
            
            response = f"✅ Estimate {estimate_id} converted to invoice successfully! Invoice ID: {invoice_id}"
            
            if notes:
                response += f"\n📝 Notes: {notes}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error converting estimate to invoice: {e}")
            return f"❌ I encountered an error while converting the estimate: {str(e)}"
    
    @function_tool
    async def get_pending_estimates(self, ctx: RunContext, limit: int = 10) -> str:
        """Get pending estimates awaiting customer response"""
        try:
            logger.info("Getting pending estimates")
            
            # Mock pending estimates (would integrate with real system)
            pending_estimates = [
                {"title": "Kitchen Renovation", "total": "$3,500", "valid_until": "2025-08-01"},
                {"title": "Bathroom Repair", "total": "$1,200", "valid_until": "2025-07-25"}
            ]
            
            if not pending_estimates:
                return "📊 No pending estimates found"
            
            estimates_text = "\n".join([
                f"• {est['title']} - {est['total']} - Valid until: {est['valid_until']}"
                for est in pending_estimates
            ])
            
            return f"📊 Pending estimates:\n{estimates_text}"
            
        except Exception as e:
            logger.error(f"Error getting pending estimates: {e}")
            return f"❌ I encountered an error while getting pending estimates: {str(e)}"
    
    @function_tool
    async def get_estimate_statistics(self, ctx: RunContext) -> str:
        """Get estimate statistics and overview"""
        try:
            logger.info("Getting estimate statistics")
            
            # Mock estimate statistics (would integrate with real system)
            stats = {
                "total_estimates": 32,
                "pending_estimates": 8,
                "accepted_estimates": 18,
                "rejected_estimates": 4,
                "draft_estimates": 2
            }
            
            response = f"📊 Estimate Statistics:\n"
            response += f"• Total estimates: {stats['total_estimates']}\n"
            response += f"• Pending estimates: {stats['pending_estimates']}\n"
            response += f"• Accepted estimates: {stats['accepted_estimates']}\n"
            response += f"• Rejected estimates: {stats['rejected_estimates']}\n"
            response += f"• Draft estimates: {stats['draft_estimates']}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting estimate statistics: {e}")
            return f"❌ I encountered an error while getting estimate statistics: {str(e)}"
    
    def _get_context_suggestions(self) -> List[str]:
        """Get contextual suggestions based on business context"""
        suggestions = []
        
        if self.business_context_manager:
            business_context = self.business_context_manager.get_business_context()
            if business_context:
                # Add contextual suggestions based on business state
                suggestions.append("Follow up with customer for approval")
                suggestions.append("Create job when estimate is accepted")
                suggestions.append("Review pricing and materials")
        
        return suggestions 