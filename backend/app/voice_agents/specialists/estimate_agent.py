"""
Estimate management specialist agent for Hero365 voice system.
"""

from typing import Optional, List, Dict
from agents import Agent, function_tool
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
import logging

logger = logging.getLogger(__name__)


class EstimateAgent(BaseVoiceAgent):
    """Specialist agent for estimate management using OpenAI Agents SDK"""
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize estimate management specialist.
        
        Args:
            context_manager: Shared context manager
        """
        instructions = """
        You are the estimate management specialist for Hero365. You help users manage their 
        estimates efficiently and professionally.
        
        You have access to tools for:
        - Creating new estimates
        - Updating estimate details
        - Searching for estimates
        - Getting estimate details
        - Converting estimates to invoices
        - Managing estimate lifecycle
        
        Always be helpful and ask for clarification if needed. When creating estimates,
        collect the required information naturally through conversation.
        """
        
        # Create the OpenAI Agents SDK agent with function tools
        self.sdk_agent = Agent(
            name="Estimate Management Specialist",
            instructions=instructions,
            tools=[
                self._create_estimate_tool,
                self._get_estimate_details_tool,
                self._update_estimate_tool,
                self._search_estimates_tool,
                self._convert_estimate_to_invoice_tool,
                self._get_pending_estimates_tool
            ]
        )
        
        super().__init__(
            name="Estimate Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[]
        )
    
    @function_tool
    async def _create_estimate_tool(self,
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
            
            # Import the DTO
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
    async def _get_estimate_details_tool(self, estimate_id: str) -> str:
        """Get detailed information about a specific estimate"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get estimate details use case
            get_estimate_details_use_case = self.container.get_get_estimate_details_use_case()
            
            # Import the DTO
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
    async def _update_estimate_tool(self,
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
            
            # Import the DTO
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
    async def _search_estimates_tool(self, query: str, limit: int = 10) -> str:
        """Search for estimates by title, description, or contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the search estimates use case
            search_estimates_use_case = self.container.get_search_estimates_use_case()
            
            # Import the DTO
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
    async def _convert_estimate_to_invoice_tool(self, estimate_id: str) -> str:
        """Convert an estimate to an invoice"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the convert estimate to invoice use case
            convert_estimate_use_case = self.container.get_convert_estimate_to_invoice_use_case()
            
            # Import the DTO
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
    async def _get_pending_estimates_tool(self, limit: int = 10) -> str:
        """Get pending estimates that need attention"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the pending estimates use case
            get_pending_estimates_use_case = self.container.get_get_pending_estimates_use_case()
            
            # Import the DTO
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
    
    async def get_response(self, text_input: str) -> str:
        """
        Get response from the estimate agent using OpenAI Agents SDK.
        
        Args:
            text_input: User's input text
            
        Returns:
            Response from the agent
        """
        try:
            from agents import Runner
            
            logger.info(f"📊 Estimate agent processing: {text_input}")
            
            # Use the OpenAI Agents SDK to process the request
            result = await Runner.run(
                starting_agent=self.sdk_agent,
                input=text_input
            )
            
            response = result.final_output
            logger.info(f"✅ Estimate agent response: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in EstimateAgent.get_response: {e}")
            return "I'm having trouble with that request. Could you please be more specific about what you'd like to do with estimates?"
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Create new estimates with title, description, and details",
            "Update estimate information and status",
            "Search for estimates by title, description, or contact",
            "Get detailed estimate information",
            "Convert estimates to invoices",
            "View pending estimates",
            "Natural conversation for estimate management",
            "Automatic parameter collection through conversation"
        ] 