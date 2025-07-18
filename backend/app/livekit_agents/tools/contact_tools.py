"""
Contact Management Tools for Hero365 LiveKit Agents
"""

import logging
from typing import Dict, Any, Optional
from livekit.agents import function_tool

from ..context import BusinessContextManager

logger = logging.getLogger(__name__)


class ContactTools:
    """Contact management tools for the Hero365 agent"""
    
    def __init__(self, business_context: Dict[str, Any], business_context_manager: Optional[BusinessContextManager] = None):
        self.business_context = business_context
        self.business_context_manager = business_context_manager
    
    @function_tool
    async def create_contact(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_type: str = "lead",
        address: Optional[str] = None
    ) -> str:
        """Create a new contact with context-aware assistance.
        
        Args:
            name: Contact's full name (required)
            phone: Contact's phone number
            email: Contact's email address  
            contact_type: Type of contact (lead, customer, vendor)
            address: Contact's physical address
        """
        try:
            logger.info(f"📞 Creating contact: {name}")
            
            # Check if contact already exists using business context
            if self.business_context_manager:
                existing_contact = self.business_context_manager.find_contact_by_name(name)
                if existing_contact:
                    return f"ℹ️ Contact '{name}' already exists. Would you like to update their information instead?"
            
            # Simulate contact creation (replace with actual API call)
            response = f"✅ Successfully created contact '{name}'"
            if phone:
                response += f" with phone {phone}"
            if email:
                response += f" and email {email}"
            response += f" as a {contact_type}."
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.follow_ups:
                    response += f"\n💡 Suggested next step: {suggestions.follow_ups[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating contact: {e}")
            return f"❌ Error creating contact: {str(e)}"

    @function_tool
    async def search_contacts(self, query: str, limit: int = 10) -> str:
        """Search for contacts with context-aware suggestions.
        
        Args:
            query: Search query (name, phone, email, etc.)
            limit: Maximum number of results to return
        """
        try:
            logger.info(f"🔍 Searching contacts for: {query}")
            
            # First check business context for quick matches
            if self.business_context_manager:
                context_match = self.business_context_manager.find_contact_by_name(query)
                if context_match:
                    return f"🎯 Found in recent contacts: {context_match.name} - {context_match.phone or 'No phone'} - {context_match.email or 'No email'}"
            
            # Simulate search results (replace with actual API call)
            contacts = [
                {"name": f"Sample Contact {i}", "phone": f"555-000{i}", "email": f"contact{i}@example.com"}
                for i in range(1, min(limit, 4))
            ]
            
            if contacts:
                response = f"🔍 Found {len(contacts)} contacts matching '{query}':\n"
                for i, contact in enumerate(contacts, 1):
                    response += f"{i}. {contact['name']} - {contact['phone']} - {contact['email']}\n"
                
                # Add contextual suggestions
                if self.business_context_manager:
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.follow_ups:
                        response += f"\n💡 Related suggestion: {suggestions.follow_ups[0]}"
                
                return response
            else:
                return f"🔍 No contacts found matching '{query}'. Would you like to create a new contact with that name?"
                
        except Exception as e:
            logger.error(f"❌ Error searching contacts: {e}")
            return f"❌ Error searching contacts: {str(e)}"

    @function_tool
    async def get_suggested_contacts(self, limit: int = 5) -> str:
        """Get suggested contacts based on business context and recent activity.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            logger.info("💡 Getting suggested contacts")
            
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
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.follow_ups:
                    response += f"\n💡 Consider: {', '.join(suggestions.follow_ups[:2])}"
                
                return response
            else:
                return "📞 No recent contacts found. Would you like to create a new contact?"
                
        except Exception as e:
            logger.error(f"❌ Error getting contact suggestions: {e}")
            return f"❌ Error getting contact suggestions: {str(e)}" 