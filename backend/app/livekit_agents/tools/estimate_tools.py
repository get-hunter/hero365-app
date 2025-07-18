"""
Estimate Management Tools for Hero365 LiveKit Agents
"""

import logging
from typing import Dict, Any, Optional
from livekit.agents import function_tool

from ..context import BusinessContextManager

logger = logging.getLogger(__name__)


class EstimateTools:
    """Estimate management tools for the Hero365 agent"""
    
    def __init__(self, business_context: Dict[str, Any], business_context_manager: Optional[BusinessContextManager] = None):
        self.business_context = business_context
        self.business_context_manager = business_context_manager
    
    @function_tool
    async def create_estimate(
        self,
        title: str,
        description: str,
        contact_id: Optional[str] = None,
        total_amount: Optional[float] = None,
        valid_until: Optional[str] = None
    ) -> str:
        """Create a new estimate with context-aware assistance.
        
        Args:
            title: Estimate title/summary
            description: Detailed estimate description
            contact_id: ID of the contact for this estimate
            total_amount: Total estimated amount
            valid_until: Estimate validity date (YYYY-MM-DD format)
        """
        try:
            logger.info(f"📊 Creating estimate: {title}")
            
            # If no contact_id provided, try to find from title/description
            if not contact_id and self.business_context_manager:
                recent_contacts = self.business_context_manager.get_recent_contacts(10)
                for contact in recent_contacts:
                    if contact.name.lower() in title.lower() or contact.name.lower() in description.lower():
                        contact_id = contact.id
                        break
            
            # Simulate estimate creation (replace with actual API call)
            response = f"✅ Successfully created estimate '{title}'"
            if total_amount:
                response += f" for ${total_amount:,.2f}"
            if valid_until:
                response += f" valid until {valid_until}"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.opportunities:
                    response += f"\n💡 Next step: {suggestions.opportunities[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating estimate: {e}")
            return f"❌ Error creating estimate: {str(e)}"

    @function_tool
    async def get_recent_estimates(self, limit: int = 10) -> str:
        """Get recent estimates with context-aware insights.
        
        Args:
            limit: Maximum number of estimates to return
        """
        try:
            logger.info(f"📋 Getting recent estimates (limit: {limit})")
            
            if not self.business_context_manager:
                return "📊 Business context not available for estimate insights"
            
            # Get recent estimates from business context
            recent_estimates = self.business_context_manager.get_recent_estimates(limit)
            
            if recent_estimates:
                response = f"📋 Recent estimates:\n"
                for i, estimate in enumerate(recent_estimates, 1):
                    status_icon = "💰" if estimate.status.value == "approved" else "📊"
                    amount_str = f"${estimate.total_amount:,.2f}" if estimate.total_amount else "No amount"
                    response += f"{i}. {status_icon} {estimate.title} - {estimate.status.value} - {amount_str} - {estimate.contact_name}\n"
                
                # Add contextual suggestions
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.opportunities:
                    response += f"\n💡 Opportunities: {', '.join(suggestions.opportunities[:2])}"
                
                return response
            else:
                return "📋 No recent estimates found. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"❌ Error getting recent estimates: {e}")
            return f"❌ Error getting recent estimates: {str(e)}"

    @function_tool
    async def get_suggested_estimates(self, limit: int = 5) -> str:
        """Get suggested estimates based on business context and opportunities.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            logger.info("💡 Getting suggested estimates")
            
            if not self.business_context_manager:
                return "📊 Business context not available for estimate suggestions"
            
            # Get recent estimates from business context
            recent_estimates = self.business_context_manager.get_recent_estimates(limit)
            
            if recent_estimates:
                # Focus on draft estimates that need action
                from ..models.estimate_models import EstimateStatus
                draft_estimates = [e for e in recent_estimates if e.status == EstimateStatus.DRAFT]
                
                if draft_estimates:
                    response = f"📊 Draft estimates that need attention:\n"
                    for i, estimate in enumerate(draft_estimates, 1):
                        response += f"{i}. 📝 {estimate.title} - {estimate.contact_name}"
                        if estimate.total_amount:
                            response += f" - ${estimate.total_amount:,.2f}"
                        response += "\n"
                    
                    # Add contextual suggestions
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.opportunities:
                        response += f"\n💡 Next steps: {', '.join(suggestions.opportunities[:2])}"
                    
                    return response
                else:
                    return "📊 No draft estimates found. All estimates are up to date!"
            else:
                return "📊 No recent estimates found. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"❌ Error getting estimate suggestions: {e}")
            return f"❌ Error getting estimate suggestions: {str(e)}"

    @function_tool
    async def search_estimates(self, query: str, limit: int = 10) -> str:
        """Search for estimates with context-aware suggestions.
        
        Args:
            query: Search query (title, description, contact name, etc.)
            limit: Maximum number of results to return
        """
        try:
            logger.info(f"🔍 Searching estimates for: {query}")
            
            # First check business context for quick matches
            if self.business_context_manager:
                context_match = self.business_context_manager.find_estimate_by_title(query)
                if context_match:
                    amount_str = f"${context_match.total_amount:,.2f}" if context_match.total_amount else "No amount"
                    return f"🎯 Found in recent estimates: {context_match.title} - {context_match.status.value} - {amount_str} - {context_match.contact_name}"
            
            # Simulate search results (replace with actual API call)
            estimates = [
                {"title": f"Sample Estimate {i}", "status": "draft", "contact_name": f"Contact {i}", "total_amount": 1000.00 * i}
                for i in range(1, min(limit, 4))
            ]
            
            if estimates:
                response = f"🔍 Found {len(estimates)} estimates matching '{query}':\n"
                for i, estimate in enumerate(estimates, 1):
                    amount_str = f"${estimate['total_amount']:,.2f}" if estimate['total_amount'] else "No amount"
                    response += f"{i}. {estimate['title']} - {estimate['status']} - {amount_str} - {estimate['contact_name']}\n"
                
                # Add contextual suggestions
                if self.business_context_manager:
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.opportunities:
                        response += f"\n💡 Related suggestion: {suggestions.opportunities[0]}"
                
                return response
            else:
                return f"🔍 No estimates found matching '{query}'. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"❌ Error searching estimates: {e}")
            return f"❌ Error searching estimates: {str(e)}"

    @function_tool
    async def update_estimate_status(self, estimate_id: str, status: str) -> str:
        """Update estimate status.
        
        Args:
            estimate_id: The ID of the estimate to update
            status: New status (draft, sent, viewed, approved, rejected, expired)
        """
        try:
            logger.info(f"🔄 Updating estimate {estimate_id} status to {status}")
            
            # Simulate estimate update (replace with actual API call)
            response = f"✅ Estimate {estimate_id} status updated to '{status}'"
            
            if status == "approved":
                response += ". Congratulations! 🎉"
            elif status == "sent":
                response += ". Estimate has been sent to the client. 📧"
            elif status == "rejected":
                response += ". Consider following up or revising the estimate. 📝"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error updating estimate status: {e}")
            return f"❌ Error updating estimate status: {str(e)}"

    @function_tool
    async def convert_estimate_to_invoice(self, estimate_id: str) -> str:
        """Convert an approved estimate to an invoice.
        
        Args:
            estimate_id: The ID of the estimate to convert
        """
        try:
            logger.info(f"💰 Converting estimate {estimate_id} to invoice")
            
            # Simulate estimate conversion (replace with actual API call)
            response = f"✅ Estimate {estimate_id} successfully converted to invoice"
            response += "\n📋 Invoice has been created and is ready to be sent to the client."
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.quick_actions:
                    response += f"\n💡 Next step: {suggestions.quick_actions[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error converting estimate to invoice: {e}")
            return f"❌ Error converting estimate to invoice: {str(e)}" 