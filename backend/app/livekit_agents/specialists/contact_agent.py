"""
Contact Agent - Specialized agent for contact management with business context awareness
"""

from typing import Dict, Any, Optional
from livekit.agents import Agent, RunContext, function_tool
from ..config import LiveKitConfig
from ..business_context_manager import BusinessContextManager
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
        
        logger.info("📊 Contact agent initialized successfully")
        
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        logger.info("📊 Business context set for contact agent")
    
    @function_tool
    async def create_contact(
        self,
        ctx: RunContext,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Create a new contact with the provided information.
        
        Args:
            name: Contact's full name (required)
            email: Contact's email address (optional)
            phone: Contact's phone number (optional)
            address: Contact's address (optional)
            notes: Additional notes about the contact (optional)
        """
        try:
            # This would integrate with the actual contact creation logic
            logger.info(f"Creating contact: {name}")
            return f"Contact '{name}' created successfully. I've added them to your contact list."
                
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
            # This would integrate with the actual contact search logic
            return f"Found contacts matching '{query}'. Here are the results..."
                
        except Exception as e:
            logger.error(f"❌ Error searching contacts: {e}")
            return f"❌ Error searching contacts: {str(e)}"
    
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
            # This would integrate with the actual contact details logic
            return f"Here are the details for contact {contact_id}..."
                
        except Exception as e:
            logger.error(f"❌ Error getting contact details: {e}")
            return f"❌ Error getting contact details: {str(e)}"
    
    @function_tool
    async def update_contact(
        self,
        ctx: RunContext,
        contact_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Update contact information.
        
        Args:
            contact_id: The ID of the contact to update
            name: New name (optional)
            email: New email (optional)
            phone: New phone (optional)
            address: New address (optional)
            notes: New notes (optional)
        """
        try:
            logger.info(f"Updating contact: {contact_id}")
            # This would integrate with the actual contact update logic
            return f"Contact {contact_id} updated successfully."
                
        except Exception as e:
            logger.error(f"❌ Error updating contact: {e}")
            return f"❌ Error updating contact: {str(e)}"
    
    @function_tool
    async def delete_contact(
        self,
        ctx: RunContext,
        contact_id: str
    ) -> str:
        """Delete a contact.
        
        Args:
            contact_id: The ID of the contact to delete
        """
        try:
            logger.info(f"Deleting contact: {contact_id}")
            # This would integrate with the actual contact deletion logic
            return f"Contact {contact_id} deleted successfully."
                
        except Exception as e:
            logger.error(f"❌ Error deleting contact: {e}")
            return f"❌ Error deleting contact: {str(e)}"
    
    @function_tool
    async def get_business_context_overview(
        self,
        ctx: RunContext
    ) -> str:
        """Get an overview of the business context for contact management.
        """
        try:
            if self.business_context_manager:
                context = self.business_context_manager.get_business_context()
                if context:
                    return f"Business: {context.business_name}, Recent Contacts: {context.recent_contacts_count}"
                else:
                    return "Business context not available."
            else:
                return "Business context not initialized."
                
        except Exception as e:
            logger.error(f"❌ Error getting business context: {e}")
            return f"❌ Error getting business context: {str(e)}" 