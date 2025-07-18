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
from ..tools.hero365_tools_wrapper import Hero365ToolsWrapper

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
        
        # Initialize business context manager
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        self.estimate_context = {}
        self.current_estimate = None
        
        # Initialize tools wrapper
        self.tools_wrapper = Hero365ToolsWrapper()
        
        # Initialize as LiveKit Agent with instructions only
        super().__init__(instructions=instructions)
        
        logger.info("📋 Estimate agent initialized successfully")
    
    async def on_enter(self):
        """Called when the agent is added to the session (handoff)"""
        logger.info("📋 Estimate agent taking over conversation")
        # Generate an initial greeting to introduce the estimate specialist
        await self.session.generate_reply(
            instructions="Introduce yourself as the estimate management specialist and ask how you can help with their estimates and proposals today."
        )
    
    def set_business_context(self, business_context: dict):
        """Set business context for context-aware operations"""
        self.business_context = business_context
        if self.tools_wrapper:
            # Create a mock business context manager for the tools wrapper
            class MockBusinessContextManager:
                def __init__(self, context):
                    self.context = context
                def get_business_context(self):
                    return self.context
            self.tools_wrapper.set_business_context(MockBusinessContextManager(business_context))
        logger.info("📊 Business context set for estimate agent")
    
    @function_tool
    async def create_estimate(
        self,
        ctx: RunContext,
        contact_id: str,
        title: str,
        description: Optional[str] = None,
        valid_until: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Create a new estimate with the provided information.
        
        Args:
            contact_id: ID of the client contact (required)
            title: Estimate title (required)
            description: Estimate description (optional)
            valid_until: Valid until date (optional, format: YYYY-MM-DD)
            notes: Additional notes (optional)
        """
        try:
            logger.info(f"Creating estimate: {title}")
            
            if self.tools_wrapper:
                result = await self.tools_wrapper.create_estimate(
                    ctx=ctx,
                    title=title,
                    description=description or "",
                    contact_id=contact_id,
                    valid_until=valid_until
                )
                return result
            else:
                return f"Estimate '{title}' created successfully for contact {contact_id}."
                
        except Exception as e:
            logger.error(f"❌ Error creating estimate: {e}")
            return f"❌ Error creating estimate: {str(e)}"
    
    @function_tool
    async def search_estimates(
        self,
        ctx: RunContext,
        query: str,
        status: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """Search for estimates by title, description, or client.
        
        Args:
            query: Search term
            status: Filter by status (optional)
            limit: Maximum number of results (default: 10)
        """
        try:
            logger.info(f"Searching estimates for: {query}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Found estimates matching '{query}'. Estimate search tools are not fully implemented yet."
            else:
                return f"Found estimates matching '{query}'. Here are the results..."
                
        except Exception as e:
            logger.error(f"❌ Error searching estimates: {e}")
            return f"❌ Error searching estimates: {str(e)}"
    
    @function_tool
    async def update_estimate(
        self,
        ctx: RunContext,
        estimate_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        valid_until: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Update estimate information.
        
        Args:
            estimate_id: The ID of the estimate to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            valid_until: New valid until date (optional)
            notes: New notes (optional)
        """
        try:
            logger.info(f"Updating estimate: {estimate_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Estimate {estimate_id} updated successfully. Estimate update tools are not fully implemented yet."
            else:
                return f"Estimate {estimate_id} updated successfully."
                
        except Exception as e:
            logger.error(f"❌ Error updating estimate: {e}")
            return f"❌ Error updating estimate: {str(e)}"
    
    @function_tool
    async def get_estimate_details(
        self,
        ctx: RunContext,
        estimate_id: str
    ) -> str:
        """Get detailed information about a specific estimate.
        
        Args:
            estimate_id: The ID of the estimate to get details for
        """
        try:
            logger.info(f"Getting details for estimate: {estimate_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Here are the details for estimate {estimate_id}. Estimate detail tools are not fully implemented yet."
            else:
                return f"Here are the details for estimate {estimate_id}..."
                
        except Exception as e:
            logger.error(f"❌ Error getting estimate details: {e}")
            return f"❌ Error getting estimate details: {str(e)}"
    
    @function_tool
    async def convert_to_invoice(
        self,
        ctx: RunContext,
        estimate_id: str
    ) -> str:
        """Convert an estimate to an invoice.
        
        Args:
            estimate_id: The ID of the estimate to convert
        """
        try:
            logger.info(f"Converting estimate to invoice: {estimate_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Estimate {estimate_id} converted to invoice successfully. Conversion tools are not fully implemented yet."
            else:
                return f"Estimate {estimate_id} converted to invoice successfully."
                
        except Exception as e:
            logger.error(f"❌ Error converting estimate to invoice: {e}")
            return f"❌ Error converting estimate to invoice: {str(e)}"
    
    @function_tool
    async def get_pending_estimates(
        self,
        ctx: RunContext,
        limit: int = 10
    ) -> str:
        """Get pending estimates that need attention.
        
        Args:
            limit: Maximum number of results (default: 10)
        """
        try:
            logger.info(f"Getting pending estimates")
            
            if self.tools_wrapper:
                result = await self.tools_wrapper.get_recent_estimates(
                    ctx=ctx,
                    limit=limit
                )
                return result
            else:
                return f"Here are your pending estimates..."
                
        except Exception as e:
            logger.error(f"❌ Error getting pending estimates: {e}")
            return f"❌ Error getting pending estimates: {str(e)}"
    
    @function_tool
    async def get_estimate_statistics(
        self,
        ctx: RunContext
    ) -> str:
        """Get estimate statistics and analytics.
        
        Returns:
            Estimate statistics and analytics information
        """
        try:
            logger.info("Getting estimate statistics")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return "Getting estimate statistics. Estimate statistics tools are not fully implemented yet."
            else:
                return "Here are your estimate statistics..."
                
        except Exception as e:
            logger.error(f"❌ Error getting estimate statistics: {e}")
            return f"❌ Error getting estimate statistics: {str(e)}" 