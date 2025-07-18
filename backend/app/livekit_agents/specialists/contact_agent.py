"""
Contact Agent - Specialized agent for contact management with business context awareness
"""

from typing import Dict, Any, Optional
from livekit.agents import Agent, RunContext, function_tool
from ..config import LiveKitConfig
from ..business_context_manager import BusinessContextManager
from ..tools.hero365_tools_wrapper import Hero365ToolsWrapper
import logging

logger = logging.getLogger(__name__)

class ContactAgent(Agent):
    """Specialized agent for contact management with business context awareness"""
    
    def __init__(self, config: LiveKitConfig):
        # Initialize business context manager
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        self.contact_context = {}
        self.current_contact = None
        
        # Initialize tools wrapper
        self.tools_wrapper = Hero365ToolsWrapper()
        
        # Create context-aware instructions
        instructions = """
        You are the contact management specialist for Hero365. You help users manage their 
        contacts efficiently and professionally with intelligent business context awareness.
        
        You have comprehensive knowledge of:
        - Recent contact interactions and history
        - Contact priorities based on business activity
        - Related jobs and estimates for each contact
        - Business context for smarter suggestions
        
        You have access to tools for:
        - Creating new contacts with smart defaults
        - Searching contacts with context-aware results
        - Getting contact suggestions based on business activity
        - Updating contact information
        - Getting detailed contact information
        - Helping with contact interactions and calls
        - Managing contact lifecycle
        
        Always be helpful and provide context-aware suggestions. Use business context 
        to make smarter recommendations and provide proactive assistance.
        
        IMPORTANT: Use the available tools to provide accurate, up-to-date information.
        """
        
        # Initialize as LiveKit Agent with instructions only
        super().__init__(instructions=instructions)
        
        logger.info("👥 Contact agent initialized successfully")
    
    async def on_enter(self):
        """Called when the agent is added to the session (handoff)"""
        logger.info("👥 Contact agent taking over conversation")
        # Generate an initial greeting to introduce the contact specialist
        await self.session.generate_reply(
            instructions="Introduce yourself as the contact management specialist and ask how you can help with their contacts today."
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
        logger.info("📊 Business context set for contact agent")
    
    @function_tool
    async def create_contact(
        self,
        ctx: RunContext,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_type: str = "lead",
        address: Optional[str] = None
    ) -> str:
        """Create a new contact with the provided information.
        
        Args:
            name: Full name of the contact
            phone: Phone number (optional)
            email: Email address (optional)
            contact_type: Type of contact (lead, customer, prospect, vendor)
            address: Address information (optional)
        """
        try:
            logger.info(f"Creating contact: {name}")
            
            if self.tools_wrapper:
                result = await self.tools_wrapper.create_contact(
                    ctx=ctx,
                    name=name,
                    phone=phone,
                    email=email,
                    contact_type=contact_type,
                    address=address
                )
                return result
            else:
                return f"Contact '{name}' created successfully. Contact management tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error creating contact: {e}")
            return f"❌ Error creating contact: {str(e)}"
    
    @function_tool
    async def search_contacts(
        self,
        ctx: RunContext,
        query: str,
        limit: int = 10
    ) -> str:
        """Search for contacts by name, email, or phone.
        
        Args:
            query: Search term (name, email, or phone)
            limit: Maximum number of results to return (default: 10)
        """
        try:
            logger.info(f"Searching contacts for: {query}")
            
            if self.tools_wrapper:
                result = await self.tools_wrapper.search_contacts(
                    ctx=ctx,
                    query=query,
                    limit=limit
                )
                return result
            else:
                return f"Searching for contacts matching '{query}'. Contact search tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error searching contacts: {e}")
            return f"❌ Error searching contacts: {str(e)}"
    
    @function_tool
    async def get_suggested_contacts(
        self,
        ctx: RunContext,
        limit: int = 5
    ) -> str:
        """Get suggested contacts based on business activity and context.
        
        Args:
            limit: Maximum number of suggestions to return (default: 5)
        """
        try:
            logger.info(f"Getting suggested contacts")
            
            if self.tools_wrapper:
                result = await self.tools_wrapper.get_suggested_contacts(
                    ctx=ctx,
                    limit=limit
                )
                return result
            else:
                return "Getting contact suggestions based on your business activity. Contact suggestion tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error getting suggested contacts: {e}")
            return f"❌ Error getting suggested contacts: {str(e)}"
    
    @function_tool
    async def get_contact_details(
        self,
        ctx: RunContext,
        contact_id: str
    ) -> str:
        """Get detailed information about a specific contact.
        
        Args:
            contact_id: The ID of the contact to get details for
        """
        try:
            logger.info(f"Getting details for contact: {contact_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Getting detailed information for contact {contact_id}. Contact detail tools are not fully implemented yet."
            else:
                return f"Getting details for contact {contact_id}. Contact detail tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error getting contact details: {e}")
            return f"❌ Error getting contact details: {str(e)}"
    
    @function_tool
    async def update_contact(
        self,
        ctx: RunContext,
        contact_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_type: Optional[str] = None,
        address: Optional[str] = None
    ) -> str:
        """Update an existing contact's information.
        
        Args:
            contact_id: The ID of the contact to update
            name: New name (optional)
            phone: New phone number (optional)
            email: New email address (optional)
            contact_type: New contact type (optional)
            address: New address (optional)
        """
        try:
            logger.info(f"Updating contact: {contact_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Updating contact {contact_id}. Contact update tools are not fully implemented yet."
            else:
                return f"Updating contact {contact_id}. Contact update tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error updating contact: {e}")
            return f"❌ Error updating contact: {str(e)}"
    
    @function_tool
    async def get_contact_interactions(
        self,
        ctx: RunContext,
        contact_id: str,
        limit: int = 10
    ) -> str:
        """Get recent interactions and history for a contact.
        
        Args:
            contact_id: The ID of the contact
            limit: Maximum number of interactions to return (default: 10)
        """
        try:
            logger.info(f"Getting interactions for contact: {contact_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Getting interaction history for contact {contact_id}. Interaction tools are not fully implemented yet."
            else:
                return f"Getting interaction history for contact {contact_id}. Interaction tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error getting contact interactions: {e}")
            return f"❌ Error getting contact interactions: {str(e)}"
    
    @function_tool
    async def add_contact_note(
        self,
        ctx: RunContext,
        contact_id: str,
        note: str
    ) -> str:
        """Add a note to a contact's record.
        
        Args:
            contact_id: The ID of the contact
            note: The note to add
        """
        try:
            logger.info(f"Adding note to contact: {contact_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Adding note to contact {contact_id}. Note tools are not fully implemented yet."
            else:
                return f"Adding note to contact {contact_id}. Note tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error adding contact note: {e}")
            return f"❌ Error adding contact note: {str(e)}"
    
    @function_tool
    async def schedule_contact_follow_up(
        self,
        ctx: RunContext,
        contact_id: str,
        follow_up_date: str,
        notes: Optional[str] = None
    ) -> str:
        """Schedule a follow-up for a contact.
        
        Args:
            contact_id: The ID of the contact
            follow_up_date: Date for the follow-up (YYYY-MM-DD)
            notes: Optional notes about the follow-up
        """
        try:
            logger.info(f"Scheduling follow-up for contact: {contact_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Scheduling follow-up for contact {contact_id} on {follow_up_date}. Follow-up tools are not fully implemented yet."
            else:
                return f"Scheduling follow-up for contact {contact_id} on {follow_up_date}. Follow-up tools are not available at the moment."
                
        except Exception as e:
            logger.error(f"❌ Error scheduling contact follow-up: {e}")
            return f"❌ Error scheduling contact follow-up: {str(e)}" 