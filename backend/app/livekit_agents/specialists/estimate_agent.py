"""
Estimate management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List
import uuid
from datetime import datetime
import logging

from livekit.agents import llm, function_tool
from ..base_agent import Hero365BaseAgent
from ..config import LiveKitConfig

logger = logging.getLogger(__name__)


class EstimateAgent(Hero365BaseAgent):
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
        
        super().__init__(
            name="Estimate Management Specialist",
            instructions=instructions
        )
    
    @function_tool
    async def create_estimate(self,
                             client_contact_id: str,
                             title: str,
                             description: Optional[str] = None,
                             valid_until_date: Optional[str] = None,
                             notes: Optional[str] = None) -> str:
        """Create a new estimate with the provided information"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the create estimate use case
            create_estimate_use_case = self.container.get_create_estimate_use_case()
            
            from ...application.dto.estimate_dto import CreateEstimateDTO
            
            # Execute use case
            result = await create_estimate_use_case.execute(
                CreateEstimateDTO(
                    contact_id=client_contact_id,
                    title=title,
                    description=description,
                    valid_until_date=valid_until_date,
                    line_items=[],
                    internal_notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Estimate #{result.estimate_number} '{title}' created successfully! Estimate ID: {result.id}"
            
        except Exception as e:
            logger.error(f"Error creating estimate: {e}")
            return f"❌ I encountered an error while creating the estimate: {str(e)}"
    
    @function_tool
    async def get_estimate_details(self, estimate_id: str) -> str:
        """Get detailed information about a specific estimate"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get estimate details use case
            get_estimate_details_use_case = self.container.get_get_estimate_details_use_case()
            
            from ...application.dto.estimate_dto import GetEstimateDetailsDTO
            
            # Execute use case
            result = await get_estimate_details_use_case.execute(
                GetEstimateDetailsDTO(
                    estimate_id=estimate_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            estimate = result.estimate
            details = f"""
📊 Estimate Details:
• Number: #{estimate.estimate_number}
• Title: {estimate.title}
• Description: {estimate.description or 'None'}
• Status: {estimate.status}
• Contact: {estimate.contact_id}
• Valid Until: {estimate.valid_until_date or 'Not specified'}
• Total: ${estimate.total_amount:.2f}
• Notes: {estimate.internal_notes or 'None'}
• Created: {estimate.created_at}
            """
            
            return details.strip()
            
        except Exception as e:
            logger.error(f"Error getting estimate details: {e}")
            return f"❌ I encountered an error while getting estimate details: {str(e)}"
    
    @function_tool
    async def update_estimate(self,
                             estimate_id: str,
                             title: Optional[str] = None,
                             description: Optional[str] = None,
                             valid_until_date: Optional[str] = None,
                             notes: Optional[str] = None) -> str:
        """Update an existing estimate"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the update estimate use case
            update_estimate_use_case = self.container.get_update_estimate_use_case()
            
            from ...application.dto.estimate_dto import UpdateEstimateDTO
            
            # Execute use case
            result = await update_estimate_use_case.execute(
                UpdateEstimateDTO(
                    estimate_id=estimate_id,
                    title=title,
                    description=description,
                    valid_until_date=valid_until_date,
                    internal_notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Estimate updated successfully!"
            
        except Exception as e:
            logger.error(f"Error updating estimate: {e}")
            return f"❌ I encountered an error while updating the estimate: {str(e)}"
    
    @function_tool
    async def search_estimates(self, query: str, limit: int = 10) -> str:
        """Search for estimates by title, description, or contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the search estimates use case
            search_estimates_use_case = self.container.get_search_estimates_use_case()
            
            from ...application.dto.estimate_dto import SearchEstimatesDTO
            
            # Execute use case
            result = await search_estimates_use_case.execute(
                SearchEstimatesDTO(
                    query=query,
                    limit=limit,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.estimates:
                return f"No estimates found matching '{query}'"
            
            estimates_text = "\n".join([
                f"• #{estimate.estimate_number} - {estimate.title} - {estimate.status} - ${estimate.total_amount:.2f}"
                for estimate in result.estimates
            ])
            
            return f"📊 Found {len(result.estimates)} estimate(s) matching '{query}':\n{estimates_text}"
            
        except Exception as e:
            logger.error(f"Error searching estimates: {e}")
            return f"❌ I encountered an error while searching for estimates: {str(e)}"
    
    @function_tool
    async def convert_estimate_to_invoice(self, estimate_id: str) -> str:
        """Convert an estimate to an invoice"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the convert estimate to invoice use case
            convert_estimate_use_case = self.container.get_convert_estimate_to_invoice_use_case()
            
            from ...application.dto.estimate_dto import ConvertEstimateToInvoiceDTO
            
            # Execute use case
            result = await convert_estimate_use_case.execute(
                ConvertEstimateToInvoiceDTO(
                    estimate_id=estimate_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Estimate converted to invoice successfully! Invoice ID: {result.invoice_id}"
            
        except Exception as e:
            logger.error(f"Error converting estimate to invoice: {e}")
            return f"❌ I encountered an error while converting the estimate to invoice: {str(e)}"
    
    @function_tool
    async def get_pending_estimates(self, limit: int = 10) -> str:
        """Get pending estimates that need attention"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the pending estimates use case
            get_pending_estimates_use_case = self.container.get_get_pending_estimates_use_case()
            
            from ...application.dto.estimate_dto import GetPendingEstimatesDTO
            
            # Execute use case
            result = await get_pending_estimates_use_case.execute(
                GetPendingEstimatesDTO(
                    limit=limit,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.estimates:
                return "No pending estimates found"
            
            estimates_text = "\n".join([
                f"• #{estimate.estimate_number} - {estimate.title} - ${estimate.total_amount:.2f}"
                for estimate in result.estimates
            ])
            
            return f"📋 Pending estimates:\n{estimates_text}"
            
        except Exception as e:
            logger.error(f"Error getting pending estimates: {e}")
            return f"❌ I encountered an error while getting pending estimates: {str(e)}"
    
    @function_tool
    async def get_estimate_statistics(self) -> str:
        """Get estimate statistics and overview"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get estimate statistics through search with different filters
            search_estimates_use_case = self.container.get_search_estimates_use_case()
            
            from ...application.dto.estimate_dto import SearchEstimatesDTO
            
            # Get draft estimates
            draft_result = await search_estimates_use_case.execute(
                SearchEstimatesDTO(
                    query="draft",
                    limit=100,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            # Get sent estimates
            sent_result = await search_estimates_use_case.execute(
                SearchEstimatesDTO(
                    query="sent",
                    limit=100,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            # Get accepted estimates
            accepted_result = await search_estimates_use_case.execute(
                SearchEstimatesDTO(
                    query="accepted",
                    limit=100,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            # Calculate totals
            total_value = sum(est.total_amount for est in sent_result.estimates + accepted_result.estimates)
            
            stats = f"""
📊 Estimate Statistics:
• Draft: {len(draft_result.estimates)}
• Sent: {len(sent_result.estimates)}
• Accepted: {len(accepted_result.estimates)}
• Total Value: ${total_value:.2f}
• Total Estimates: {len(draft_result.estimates) + len(sent_result.estimates) + len(accepted_result.estimates)}
            """
            
            return stats.strip()
            
        except Exception as e:
            logger.error(f"Error getting estimate statistics: {e}")
            return f"❌ I encountered an error while getting estimate statistics: {str(e)}"
    
    def get_specialist_capabilities(self) -> List[str]:
        """Get list of capabilities for this specialist agent"""
        return [
            "Create new estimates with title, description, and details",
            "Update estimate information and status",
            "Search for estimates by title, description, or contact",
            "Get detailed estimate information",
            "Convert estimates to invoices",
            "View pending estimates",
            "Get estimate statistics and overview",
            "Natural conversation for estimate management",
            "Automatic parameter collection through conversation"
        ]
    
    async def initialize_agent(self, ctx):
        """Initialize estimate agent"""
        logger.info("📊 Estimate Agent initialized")
    
    async def cleanup_agent(self, ctx):
        """Clean up estimate agent"""
        logger.info("👋 Estimate Agent cleaned up")
    
    async def process_message(self, ctx, message: str) -> str:
        """Process user message"""
        # Process estimate-related messages
        return f"Estimate agent processing: {message}" 