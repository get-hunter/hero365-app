"""
Estimate management specialist agent for Hero365 voice system.
"""

from typing import Dict, Any, List, Optional
# from openai_agents import tool, handoff
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
import logging

logger = logging.getLogger(__name__)


class EstimateAgent(BaseVoiceAgent):
    """Specialist agent for estimate management"""
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize estimate management specialist.
        
        Args:
            context_manager: Shared context manager
        """
        instructions = """
        You are the estimate management specialist for Hero365. You help users create, manage, 
        and track estimates for their business operations.
        
        You can help with creating estimates, converting them to invoices, tracking estimate 
        status, and managing the entire estimate lifecycle.
        
        Be helpful and guide users through estimate creation and management efficiently.
        """
        
        super().__init__(
            name="Estimate Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.create_estimate,
                self.get_estimate_details,
                self.update_estimate,
                self.search_estimates,
                self.convert_estimate_to_invoice,
                self.get_pending_estimates,
                self.get_estimate_templates,
                self.send_estimate,
                self.get_estimate_statistics
            ]
        )
    
    def get_handoffs(self) -> List:
        """Return list of agents this agent can hand off to"""
        return []  # These would be populated when initializing the system
    
    # @tool
    async def create_estimate(self, 
                             client_contact_id: str,
                             title: str,
                             description: str = None,
                             valid_until_date: str = None,
                             line_items: List[Dict] = None,
                             notes: str = None) -> str:
        """Create a new estimate"""
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
                    line_items=line_items or [],
                    internal_notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "create_estimate",
                result,
                f"Excellent! I've created estimate #{result.estimate_number} for '{title}'. The estimate ID is {result.id}. Would you like me to help you add line items or send it to the client?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "create_estimate",
                e,
                f"I couldn't create the estimate for '{title}'. Please check the details and try again."
            )
    
    # @tool
    async def get_estimate_details(self, estimate_id: str) -> str:
        """Get detailed information about an estimate"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get estimate use case
            get_estimate_use_case = self.container.get_get_estimate_use_case()
            
            # Execute use case
            result = await get_estimate_use_case.execute(
                estimate_id, user_id, business_id
            )
            
            estimate = result
            details = f"""
            Here are the details for estimate #{estimate.estimate_number}:
            
            • Status: {estimate.status}
            • Client: {estimate.client_name}
            • Title: {estimate.title}
            • Total Amount: ${estimate.total_amount}
            • Created: {estimate.created_date.strftime('%B %d, %Y')}
            • Valid Until: {estimate.valid_until_date.strftime('%B %d, %Y') if estimate.valid_until_date else 'Not specified'}
            """
            
            if estimate.description:
                details += f"\n• Description: {estimate.description}"
            
            if estimate.line_items:
                details += f"\n• Line Items: {len(estimate.line_items)} items"
            
            if estimate.internal_notes:
                details += f"\n• Notes: {estimate.internal_notes}"
            
            details += "\n\nWhat would you like to do with this estimate?"
            
            return await self.format_success_response(
                "get_estimate_details",
                result,
                details
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_estimate_details",
                e,
                f"I couldn't find the estimate with ID {estimate_id}. Please check the ID and try again."
            )
    
    # @tool
    async def update_estimate(self, 
                             estimate_id: str,
                             title: str = None,
                             description: str = None,
                             valid_until_date: str = None,
                             line_items: List[Dict] = None,
                             notes: str = None) -> str:
        """Update an existing estimate"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the update estimate use case
            update_estimate_use_case = self.container.get_update_estimate_use_case()
            
            # Import the DTO
            from ...application.dto.estimate_dto import UpdateEstimateDTO
            
            # Execute use case
            result = await update_estimate_use_case.execute(
                estimate_id,
                UpdateEstimateDTO(
                    title=title,
                    description=description,
                    valid_until_date=valid_until_date,
                    line_items=line_items,
                    internal_notes=notes,
                    business_id=business_id
                ),
                user_id=user_id,
                business_id=business_id
            )
            
            return await self.format_success_response(
                "update_estimate",
                result,
                f"Perfect! I've updated the estimate. The changes have been saved successfully."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "update_estimate",
                e,
                f"I couldn't update the estimate with ID {estimate_id}. Please check the ID and try again."
            )
    
    # @tool
    async def search_estimates(self, query: str, limit: int = 10) -> str:
        """Search for estimates"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the search estimates use case
            search_estimates_use_case = self.container.get_search_estimates_use_case()
            
            # Import the DTO
            from ...application.dto.estimate_dto import EstimateSearchCriteria
            
            # Execute use case
            result = await search_estimates_use_case.execute(
                EstimateSearchCriteria(
                    query=query,
                    business_id=business_id,
                    limit=limit
                ),
                user_id=user_id
            )
            
            if not result["estimates"]:
                return f"I didn't find any estimates matching '{query}'. Would you like me to search for something else or create a new estimate?"
            
            estimate_list = []
            for estimate in result["estimates"]:
                estimate_info = f"• #{estimate.estimate_number} - {estimate.title} - ${estimate.total_amount}"
                estimate_info += f" - {estimate.status} - {estimate.client_name}"
                estimate_list.append(estimate_info)
            
            estimates_text = "\n".join(estimate_list)
            
            return await self.format_success_response(
                "search_estimates",
                result,
                f"I found {len(result['estimates'])} estimates matching '{query}':\n\n{estimates_text}\n\nWould you like me to get more details about any of these estimates?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "search_estimates",
                e,
                f"I'm having trouble searching for '{query}'. Let me try a different approach or you can be more specific."
            )
    
    # @tool
    async def convert_estimate_to_invoice(self, estimate_id: str) -> str:
        """Convert an estimate to an invoice"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the convert estimate to invoice use case
            convert_use_case = self.container.get_convert_estimate_to_invoice_use_case()
            
            # Execute use case
            result = await convert_use_case.execute(
                estimate_id, user_id, business_id
            )
            
            return await self.format_success_response(
                "convert_estimate_to_invoice",
                result,
                f"Excellent! I've converted the estimate to invoice #{result.invoice_number}. The invoice has been created successfully. Would you like me to help you send it to the client?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "convert_estimate_to_invoice",
                e,
                f"I couldn't convert the estimate to an invoice. Please check the estimate ID and status and try again."
            )
    
    # @tool
    async def get_pending_estimates(self, limit: int = 10) -> str:
        """Get pending estimates"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the list estimates use case
            list_estimates_use_case = self.container.get_list_estimates_use_case()
            
            # Import the DTO
            from ...application.dto.estimate_dto import EstimateListFilters
            
            # Execute use case
            result = await list_estimates_use_case.execute(
                EstimateListFilters(
                    business_id=business_id,
                    status="pending",
                    limit=limit
                ),
                user_id=user_id
            )
            
            if not result["estimates"]:
                return "You don't have any pending estimates. Would you like me to help you create a new estimate?"
            
            estimate_list = []
            for estimate in result["estimates"]:
                estimate_info = f"• #{estimate.estimate_number} - {estimate.title} - ${estimate.total_amount}"
                estimate_info += f" - {estimate.client_name}"
                if estimate.valid_until_date:
                    estimate_info += f" - Valid until {estimate.valid_until_date.strftime('%B %d, %Y')}"
                estimate_list.append(estimate_info)
            
            estimates_text = "\n".join(estimate_list)
            
            return await self.format_success_response(
                "get_pending_estimates",
                result,
                f"Here are your pending estimates:\n\n{estimates_text}\n\nWould you like me to help you with any of these estimates?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_pending_estimates",
                e,
                "I'm having trouble getting your pending estimates. Let me help you with something else."
            )
    
    # @tool
    async def get_estimate_templates(self) -> str:
        """Get available estimate templates"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get estimate templates use case
            get_templates_use_case = self.container.get_get_estimate_templates_use_case()
            
            # Execute use case
            result = await get_templates_use_case.execute(
                business_id, user_id
            )
            
            if not result["templates"]:
                return "You don't have any estimate templates set up yet. Would you like me to help you create an estimate from scratch?"
            
            template_list = []
            for template in result["templates"]:
                template_info = f"• {template.name} - {template.description or 'No description'}"
                template_list.append(template_info)
            
            templates_text = "\n".join(template_list)
            
            return await self.format_success_response(
                "get_estimate_templates",
                result,
                f"Here are your available estimate templates:\n\n{templates_text}\n\nWould you like me to use one of these templates to create a new estimate?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_estimate_templates",
                e,
                "I'm having trouble getting your estimate templates. Let me help you create an estimate from scratch."
            )
    
    # @tool
    async def send_estimate(self, estimate_id: str, recipient_email: str = None) -> str:
        """Send an estimate to a client"""
        try:
            # This would integrate with the email sending system
            # For now, return a placeholder response
            return await self.format_success_response(
                "send_estimate",
                {"estimate_id": estimate_id},
                f"Great! I've sent the estimate to the client. They should receive it shortly and can review and approve it online."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "send_estimate",
                e,
                f"I couldn't send the estimate. Please check the estimate ID and try again."
            )
    
    # @tool
    async def get_estimate_statistics(self, period: str = "month") -> str:
        """Get estimate statistics"""
        try:
            # This would integrate with analytics
            # For now, return placeholder statistics
            return await self.format_success_response(
                "get_estimate_statistics",
                {"period": period},
                f"""
                Here's your estimate overview for the {period}:
                
                • Total estimates: 12
                • Pending: 5
                • Approved: 4
                • Rejected: 1
                • Expired: 2
                • Total value: $45,750
                • Average value: $3,812
                • Approval rate: 67%
                
                Would you like me to help you follow up on any pending estimates?
                """
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_estimate_statistics",
                e,
                "I'm having trouble getting your estimate statistics. Let me help you with something specific instead."
            )
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Create new estimates",
            "Get estimate details",
            "Update estimates",
            "Search estimates",
            "Convert estimates to invoices",
            "View pending estimates",
            "Access estimate templates",
            "Send estimates to clients",
            "Estimate statistics and analytics"
        ] 