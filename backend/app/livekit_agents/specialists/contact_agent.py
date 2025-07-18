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
        
        # Initialize as LiveKit Agent with tools
        super().__init__(
            instructions=instructions,
            tools=[
                self.create_contact,
                self.search_contacts,
                self.get_contact_suggestions,
                self.update_contact,
                self.get_contact_details,
                self.call_contact,
                self.delete_contact,
                self.get_business_context_overview,
            ]
        )
        
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        
        # Contact-specific configuration
        self.contact_context = {}
        self.current_contact = None
        
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        logger.info("📊 Business context set for contact agent")
    
    @function_tool
    async def create_contact(
        self,
        ctx: RunContext,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_type: str = "customer",
        address: Optional[str] = None
    ) -> str:
        """Create a new contact with business context awareness.
        
        Args:
            name: Contact's full name (required)
            phone: Contact's phone number
            email: Contact's email address
            contact_type: Type of contact (customer, lead, vendor, etc.)
            address: Contact's physical address
        """
        try:
            # Check if contact already exists in business context
            if self.business_context_manager:
                existing_contact = self.business_context_manager.find_contact_by_name(name)
                if existing_contact:
                    return f"ℹ️ Contact '{name}' already exists. Phone: {existing_contact.phone or 'Not provided'}, Email: {existing_contact.email or 'Not provided'}. Would you like to update their information instead?"
            
            # Simulate contact creation (would integrate with real system)
            logger.info(f"Creating contact: {name}")
            
            # Get contextual suggestions
            suggestions = self._get_context_suggestions()
            
            response = f"✅ Successfully created contact '{name}'"
            if phone:
                response += f" with phone {phone}"
            if email:
                response += f" and email {email}"
            
            # Add contextual suggestions
            if suggestions:
                response += f"\n💡 Suggested next steps: {suggestions[0]}"
            
            return response
                
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
        """Search for contacts with business context awareness.
        
        Args:
            query: Search query (name, phone, email, etc.)
            limit: Maximum number of results to return
        """
        try:
            # First check business context for quick matches
            if self.business_context_manager:
                context_match = self.business_context_manager.find_contact_by_name(query)
                if context_match:
                    response = f"🎯 Found {context_match.name} in your recent contacts:\n"
                    response += f"📞 Phone: {context_match.phone or 'Not provided'}\n"
                    response += f"📧 Email: {context_match.email or 'Not provided'}\n"
                    response += f"🔥 Priority: {context_match.priority.value}\n"
                    
                    # Add recent activity context
                    if context_match.recent_jobs:
                        response += f"🔧 Recent jobs: {len(context_match.recent_jobs)} jobs\n"
                    if context_match.recent_estimates:
                        response += f"📊 Recent estimates: {len(context_match.recent_estimates)} estimates\n"
                    
                    return response
            
            # Simulate search (would integrate with real system)
            logger.info(f"Searching contacts for: {query}")
            
            # Mock search results
            mock_results = [
                {"name": f"Sample Contact {i}", "phone": f"555-000{i}", "email": f"contact{i}@example.com"}
                for i in range(1, min(limit, 4))
            ]
            
            if mock_results:
                response = f"🔍 Found {len(mock_results)} contacts matching '{query}':\n"
                for i, contact in enumerate(mock_results, 1):
                    response += f"{i}. {contact['name']} - {contact['phone']} - {contact['email']}\n"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions()
                if suggestions:
                    response += f"\n💡 Related suggestions: {', '.join(suggestions[:2])}"
                
                return response
            else:
                return f"🔍 No contacts found matching '{query}'. Would you like to create a new contact with that name?"
                
        except Exception as e:
            logger.error(f"❌ Error searching contacts: {e}")
            return f"❌ Error searching contacts: {str(e)}"
    
    @function_tool
    async def get_contact_suggestions(
        self,
        ctx: RunContext,
        limit: int = 5
    ) -> str:
        """Get suggested contacts based on business context and recent activity.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            if not self.business_context_manager:
                return "📞 Business context not available for contact suggestions"
            
            # Get recent contacts from business context
            recent_contacts = self.business_context_manager.get_recent_contacts(limit)
            
            if recent_contacts:
                response = f"📞 Recent contacts you might want to reach out to:\n"
                for i, contact in enumerate(recent_contacts, 1):
                    priority_icon = "🔥" if contact.priority.value == "high" else "📞"
                    response += f"{i}. {priority_icon} {contact.name} - {contact.phone or 'No phone'}\n"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions()
                if suggestions:
                    response += f"\n💡 Consider: {', '.join(suggestions[:2])}"
                
                return response
            else:
                return "📞 No recent contacts found. Would you like to create a new contact?"
                
        except Exception as e:
            logger.error(f"❌ Error getting contact suggestions: {e}")
            return f"❌ Error getting contact suggestions: {str(e)}"
    
    @function_tool
    async def update_contact(
        self,
        ctx: RunContext,
        contact_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        contact_type: Optional[str] = None
    ) -> str:
        """Update an existing contact's information.
        
        Args:
            contact_name: Name of the contact to update
            phone: New phone number (optional)
            email: New email address (optional)
            address: New address (optional)
            contact_type: New contact type (optional)
        """
        try:
            # Find contact in business context first
            if self.business_context_manager:
                existing_contact = self.business_context_manager.find_contact_by_name(contact_name)
                if existing_contact:
                    updates = []
                    if phone:
                        updates.append(f"phone to {phone}")
                    if email:
                        updates.append(f"email to {email}")
                    if address:
                        updates.append(f"address to {address}")
                    if contact_type:
                        updates.append(f"type to {contact_type}")
                    
                    if updates:
                        return f"✅ I'll update {existing_contact.name}'s {', '.join(updates)}. Changes would be saved to the system."
                    else:
                        return f"I found {existing_contact.name}. What would you like to update? (phone, email, address, contact type)"
                else:
                    return f"I couldn't find a contact named '{contact_name}'. Would you like to create a new contact with this name?"
            
            return f"I'd update {contact_name}'s information, but I need to connect to the system first."
            
        except Exception as e:
            logger.error(f"❌ Error updating contact: {e}")
            return f"❌ Error updating contact: {str(e)}"
    
    @function_tool
    async def get_contact_details(
        self,
        ctx: RunContext,
        contact_name: str
    ) -> str:
        """Get detailed information about a specific contact.
        
        Args:
            contact_name: Name of the contact to get details for
        """
        try:
            # Find contact in business context
            if self.business_context_manager:
                contact = self.business_context_manager.find_contact_by_name(contact_name)
                if contact:
                    response = f"📞 Contact Details for {contact.name}:\n"
                    response += f"• Phone: {contact.phone or 'Not provided'}\n"
                    response += f"• Email: {contact.email or 'Not provided'}\n"
                    response += f"• Type: {contact.contact_type}\n"
                    response += f"• Priority: {contact.priority.value}\n"
                    response += f"• Last interaction: {contact.last_interaction.strftime('%Y-%m-%d') if contact.last_interaction else 'N/A'}\n"
                    
                    if contact.recent_jobs:
                        response += f"• Recent jobs: {len(contact.recent_jobs)} jobs\n"
                    if contact.recent_estimates:
                        response += f"• Recent estimates: {len(contact.recent_estimates)} estimates\n"
                    
                    return response
                else:
                    return f"I couldn't find a contact named '{contact_name}'. Would you like to search for similar names?"
            
            return f"I'd get details for {contact_name}, but I need to connect to the system first."
            
        except Exception as e:
            logger.error(f"❌ Error getting contact details: {e}")
            return f"❌ Error getting contact details: {str(e)}"
    
    @function_tool
    async def call_contact(
        self,
        ctx: RunContext,
        contact_name: str
    ) -> str:
        """Help with calling a contact - provides phone number and call logging options.
        
        Args:
            contact_name: Name of the contact to call
        """
        try:
            # Find contact in business context
            if self.business_context_manager:
                contact = self.business_context_manager.find_contact_by_name(contact_name)
                if contact:
                    phone = contact.phone
                    if phone:
                        return f"📞 {contact.name}'s phone number is {phone}. Would you like me to help you log this call or create a follow-up reminder after your call?"
                    else:
                        return f"I found {contact.name} but there's no phone number on file. Would you like to add their phone number?"
                else:
                    return f"I couldn't find a contact named '{contact_name}'. Would you like to search for contacts or create a new one?"
            
            return f"I'd help you call {contact_name}, but I need to connect to the system first."
            
        except Exception as e:
            logger.error(f"❌ Error getting contact phone: {e}")
            return f"❌ Error getting contact phone: {str(e)}"
    
    @function_tool
    async def delete_contact(
        self,
        ctx: RunContext,
        contact_name: str,
        confirm: bool = False
    ) -> str:
        """Delete a contact with confirmation.
        
        Args:
            contact_name: Name of the contact to delete
            confirm: Set to True to confirm deletion
        """
        try:
            # Find contact in business context
            if self.business_context_manager:
                contact = self.business_context_manager.find_contact_by_name(contact_name)
                if contact:
                    if not confirm:
                        return f"⚠️ Are you sure you want to delete {contact.name}? This action cannot be undone. To confirm, call this function again with confirm=True."
                    else:
                        return f"✅ Contact {contact.name} would be deleted from the system. (This is a simulation - actual deletion would require system connection.)"
                else:
                    return f"I couldn't find a contact named '{contact_name}' to delete."
            
            return f"I'd delete {contact_name}, but I need to connect to the system first."
            
        except Exception as e:
            logger.error(f"❌ Error deleting contact: {e}")
            return f"❌ Error deleting contact: {str(e)}"
    
    @function_tool
    async def get_business_context_overview(
        self,
        ctx: RunContext
    ) -> str:
        """Get an overview of the current business context and contact statistics.
        """
        try:
            # Get business context summary
            if self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                business_summary = self.business_context_manager.get_business_summary()
                
                if business_context and business_summary:
                    response = f"📞 Contact Management Overview:\n"
                    response += f"• Business: {business_context.business_name}\n"
                    response += f"• Recent contacts: {len(self.business_context_manager.get_recent_contacts())}\n"
                    response += f"• Active jobs: {business_summary.active_jobs}\n"
                    response += f"• Pending estimates: {business_summary.pending_estimates}\n"
                    
                    # Add suggestions
                    suggestions = self._get_context_suggestions()
                    if suggestions:
                        response += f"\n💡 Quick actions: {', '.join(suggestions[:2])}\n"
                    
                    response += "\nI can help you create new contacts, search for existing ones, update contact information, or provide suggestions for follow-ups."
                    
                    return response
            
            return "I'm your contact management specialist. I can help you create new contacts, search for existing ones, update contact information, or provide suggestions for follow-ups."
                
        except Exception as e:
            logger.error(f"❌ Error getting business context overview: {e}")
            return "I'm your contact management specialist. How can I help you with your contacts today?"
    
    def _get_context_suggestions(self) -> list:
        """Get contextual suggestions based on business context"""
        if not self.business_context_manager:
            return []
        
        suggestions = self.business_context_manager.get_contextual_suggestions()
        if not suggestions:
            return []
        
        return suggestions.follow_ups or [] 