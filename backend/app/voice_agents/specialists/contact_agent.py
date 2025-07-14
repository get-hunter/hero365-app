"""
Contact management specialist agent for Hero365 voice system.
"""

from typing import Dict, Any, List, Optional
# from openai_agents import tool, handoff
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
import logging

logger = logging.getLogger(__name__)


class ContactAgent(BaseVoiceAgent):
    """Specialist agent for contact management"""
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize contact management specialist.
        
        Args:
            context_manager: Shared context manager
        """
        instructions = """
        You are the contact management specialist for Hero365. You help users manage their 
        contacts, including creating new contacts, updating existing ones, searching for 
        contacts, and managing contact interactions.
        
        You have access to all contact management tools and can perform any contact-related 
        operation. Always ask for clarification if you need more information.
        
        Be conversational and helpful, and guide users through contact management tasks step by step.
        """
        
        super().__init__(
            name="Contact Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.create_contact,
                self.update_contact,
                self.search_contacts,
                self.get_contact_details,
                self.add_contact_note,
                self.schedule_contact_follow_up,
                self.get_contact_interaction_history,
                self.get_recent_contacts,
                self.delete_contact,
                self.get_contact_statistics
            ]
        )
    
    def get_handoffs(self) -> List:
        """Return list of agents this agent can hand off to"""
        # Contact agent can hand off to job, estimate, or scheduling agents
        return []  # These would be populated when initializing the system
    
    # @tool
    async def create_contact(self, 
                            name: str, 
                            phone: str = None, 
                            email: str = None,
                            address: str = None,
                            contact_type: str = "client",
                            notes: str = None) -> str:
        """Create a new contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the create contact use case
            create_contact_use_case = self.container.get_create_contact_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import CreateContactDTO
            
            # Execute use case
            result = await create_contact_use_case.execute(
                CreateContactDTO(
                    name=name,
                    phone=phone,
                    email=email,
                    address=address,
                    contact_type=contact_type,
                    notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "create_contact",
                result,
                f"Great! I've created a new contact for {name}. Their contact ID is {result.id}. What else would you like to do with this contact?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "create_contact",
                e,
                f"I'm sorry, I couldn't create the contact for {name}. Let me try a different approach or you can provide more details."
            )
    
    # @tool
    async def update_contact(self, 
                           contact_id: str,
                           name: str = None,
                           phone: str = None,
                           email: str = None,
                           address: str = None,
                           contact_type: str = None,
                           notes: str = None) -> str:
        """Update an existing contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the update contact use case
            update_contact_use_case = self.container.get_update_contact_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import UpdateContactDTO
            
            # Execute use case
            result = await update_contact_use_case.execute(
                UpdateContactDTO(
                    contact_id=contact_id,
                    name=name,
                    phone=phone,
                    email=email,
                    address=address,
                    contact_type=contact_type,
                    notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "update_contact",
                result,
                f"Perfect! I've updated the contact information. The changes have been saved successfully."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "update_contact",
                e,
                f"I couldn't update the contact with ID {contact_id}. Please check the contact ID and try again."
            )
    
    # @tool
    async def search_contacts(self, query: str, limit: int = 10) -> str:
        """Search for contacts"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the search contacts use case
            search_contacts_use_case = self.container.get_search_contacts_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import SearchContactsDTO
            
            # Execute use case
            result = await search_contacts_use_case.execute(
                SearchContactsDTO(
                    query=query,
                    business_id=business_id,
                    limit=limit
                ),
                user_id=user_id
            )
            
            if not result.contacts:
                return f"I didn't find any contacts matching '{query}'. Would you like me to search for something else or create a new contact?"
            
            contact_list = []
            for contact in result.contacts:
                contact_info = f"• {contact.name}"
                if contact.phone:
                    contact_info += f" - {contact.phone}"
                if contact.email:
                    contact_info += f" - {contact.email}"
                contact_info += f" ({contact.contact_type})"
                contact_list.append(contact_info)
            
            contacts_text = "\n".join(contact_list)
            
            return await self.format_success_response(
                "search_contacts",
                result,
                f"I found {len(result.contacts)} contacts matching '{query}':\n\n{contacts_text}\n\nWould you like me to get more details about any of these contacts?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "search_contacts",
                e,
                f"I'm having trouble searching for '{query}'. Let me try a different approach or you can be more specific."
            )
    
    # @tool
    async def get_contact_details(self, contact_id: str) -> str:
        """Get detailed information about a contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get contact use case
            get_contact_use_case = self.container.get_get_contact_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import GetContactDTO
            
            # Execute use case
            result = await get_contact_use_case.execute(
                GetContactDTO(
                    contact_id=contact_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            contact = result.contact
            details = f"""
            Here are the details for {contact.name}:
            
            • Phone: {contact.phone or 'Not provided'}
            • Email: {contact.email or 'Not provided'}
            • Type: {contact.contact_type}
            • Address: {contact.address or 'Not provided'}
            • Created: {contact.created_at.strftime('%B %d, %Y')}
            """
            
            if contact.notes:
                details += f"\n• Notes: {contact.notes}"
            
            details += "\n\nWhat would you like to do with this contact?"
            
            return await self.format_success_response(
                "get_contact_details",
                result,
                details
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_contact_details",
                e,
                f"I couldn't find the contact with ID {contact_id}. Please check the ID and try again."
            )
    
    # @tool
    async def add_contact_note(self, contact_id: str, note: str) -> str:
        """Add a note to a contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the contact interaction use case
            contact_interaction_use_case = self.container.get_contact_interaction_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import ContactInteractionDTO
            
            # Execute use case
            result = await contact_interaction_use_case.execute(
                ContactInteractionDTO(
                    contact_id=contact_id,
                    interaction_type="note",
                    content=note,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "add_contact_note",
                result,
                f"I've added the note to the contact. The note has been saved successfully."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "add_contact_note",
                e,
                f"I couldn't add the note to the contact. Please try again."
            )
    
    # @tool
    async def schedule_contact_follow_up(self, contact_id: str, follow_up_date: str, notes: str = None) -> str:
        """Schedule a follow-up for a contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # This would integrate with scheduling system
            # For now, add it as a contact interaction
            contact_interaction_use_case = self.container.get_contact_interaction_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import ContactInteractionDTO
            
            # Execute use case
            result = await contact_interaction_use_case.execute(
                ContactInteractionDTO(
                    contact_id=contact_id,
                    interaction_type="follow_up_scheduled",
                    content=f"Follow-up scheduled for {follow_up_date}. Notes: {notes or 'None'}",
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "schedule_contact_follow_up",
                result,
                f"Perfect! I've scheduled a follow-up for {follow_up_date}. You'll be reminded to follow up with this contact."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "schedule_contact_follow_up",
                e,
                f"I couldn't schedule the follow-up. Please try again with a different date format."
            )
    
    # @tool
    async def get_contact_interaction_history(self, contact_id: str, limit: int = 10) -> str:
        """Get interaction history for a contact"""
        try:
            # This would integrate with the interaction history system
            # For now, return a placeholder
            return f"Here's the recent interaction history for this contact:\n\n• Last contacted: 2 days ago\n• Previous interaction: Phone call about service inquiry\n• Notes: Customer interested in HVAC maintenance\n\nWould you like me to add a new interaction or update this contact?"
            
        except Exception as e:
            return await self.format_error_response(
                "get_contact_interaction_history",
                e,
                f"I couldn't get the interaction history for this contact. Please try again."
            )
    
    # @tool
    async def get_recent_contacts(self, limit: int = 10) -> str:
        """Get recently added or updated contacts"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the list contacts use case
            list_contacts_use_case = self.container.get_list_contacts_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import ListContactsDTO
            
            # Execute use case
            result = await list_contacts_use_case.execute(
                ListContactsDTO(
                    business_id=business_id,
                    limit=limit,
                    sort_by="created_at",
                    sort_order="desc"
                ),
                user_id=user_id
            )
            
            if not result.contacts:
                return "You don't have any contacts yet. Would you like me to help you create your first contact?"
            
            contact_list = []
            for contact in result.contacts:
                contact_info = f"• {contact.name}"
                if contact.phone:
                    contact_info += f" - {contact.phone}"
                contact_info += f" ({contact.contact_type})"
                contact_list.append(contact_info)
            
            contacts_text = "\n".join(contact_list)
            
            return await self.format_success_response(
                "get_recent_contacts",
                result,
                f"Here are your most recent contacts:\n\n{contacts_text}\n\nWould you like me to get more details about any of these contacts or help you with something else?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_recent_contacts",
                e,
                "I'm having trouble getting your recent contacts. Let me help you with something else."
            )
    
    # @tool
    async def delete_contact(self, contact_id: str) -> str:
        """Delete a contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the delete contact use case
            delete_contact_use_case = self.container.get_delete_contact_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import DeleteContactDTO
            
            # Execute use case
            result = await delete_contact_use_case.execute(
                DeleteContactDTO(
                    contact_id=contact_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "delete_contact",
                result,
                "The contact has been deleted successfully. Is there anything else you'd like me to help you with?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "delete_contact",
                e,
                f"I couldn't delete the contact with ID {contact_id}. Please check the ID and try again."
            )
    
    # @tool
    async def get_contact_statistics(self) -> str:
        """Get contact statistics for the business"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the contact statistics use case
            contact_statistics_use_case = self.container.get_contact_statistics_use_case()
            
            # Import the DTO
            from ...application.dto.contact_dto import ContactStatisticsDTO
            
            # Execute use case
            result = await contact_statistics_use_case.execute(
                ContactStatisticsDTO(
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "get_contact_statistics",
                result,
                f"""
                Here's an overview of your contacts:
                
                • Total contacts: {result.total_contacts}
                • Clients: {result.clients_count}
                • Leads: {result.leads_count}
                • Vendors: {result.vendors_count}
                • New contacts this month: {result.new_contacts_this_month}
                
                Would you like me to help you manage any of these contacts?
                """
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_contact_statistics",
                e,
                "I'm having trouble getting your contact statistics. Let me help you with something specific instead."
            )
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Create new contacts",
            "Update existing contacts",
            "Search and filter contacts",
            "Get contact details",
            "Add notes to contacts",
            "Schedule follow-ups",
            "View interaction history",
            "Get recent contacts",
            "Delete contacts",
            "Contact statistics and analytics"
        ] 