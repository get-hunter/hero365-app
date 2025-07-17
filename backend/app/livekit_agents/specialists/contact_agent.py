"""
Contact management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List
import uuid
from datetime import datetime
import logging

from livekit.agents import llm, function_tool
from ..base_agent import Hero365BaseAgent
from ..config import LiveKitConfig

logger = logging.getLogger(__name__)


class ContactAgent(Hero365BaseAgent):
    """Specialist agent for contact management using LiveKit agents"""
    
    def __init__(self, config: LiveKitConfig):
        """
        Initialize contact management specialist.
        
        Args:
            config: LiveKit configuration
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        instructions = f"""
        You are the contact management specialist for Hero365. You help users manage their 
        contacts efficiently and professionally with intelligent assistance.
        
        CURRENT DATE AND TIME: Today is {current_date} at {current_time}
        
        CRITICAL: ALWAYS CALL create_contact FUNCTION TO ACTUALLY CREATE CONTACTS!
        
        SMART CONTACT CREATION PROCESS:
        1. When a user wants to create a contact, start by getting the name
        2. Optionally use check_duplicate_contacts to avoid creating duplicates
        3. Optionally use validate_contact_info to ensure data quality
        4. Collect basic info: name, phone/email, contact type
        5. IMMEDIATELY call create_contact function when you have: name + (phone OR email)
        6. DO NOT just say "contact created" - ACTUALLY CALL the create_contact function!
        
        CONVERSATION STYLE:
        - Be natural and conversational
        - Ask for essential info first: name, then phone/email
        - Once you have name + contact method, CALL create_contact immediately
        - Don't ask for excessive confirmation - just create the contact
        - Contact types: use "customer" for business contacts, "lead" for prospects
        
        CONTACT INFORMATION PRIORITY:
        1. Name (required)
        2. Phone or Email (at least one required)
        3. Contact type (default to "customer" for business contacts)
        4. Address and notes (optional)
        
        IMPORTANT: When user says "create", "go ahead", "proceed", or similar - CALL create_contact function immediately!
        """
        
        super().__init__(
            name="Contact Management Specialist",
            instructions=instructions
        )
    
    @function_tool
    async def create_contact(self,
                           name: str, 
                           phone: Optional[str] = None, 
                           email: Optional[str] = None,
                           address: Optional[str] = None,
                           contact_type: str = "customer",
                           notes: Optional[str] = None) -> str:
        """Create a new contact with the provided information"""
        try:
            logger.info(f"🔥 create_contact function CALLED with name='{name}', phone='{phone}', email='{email}', contact_type='{contact_type}'")
            
            # Get user context
            user_id, business_id = await self.get_user_and_business_ids()
            logger.info(f"🔥 Got user_id='{user_id}', business_id='{business_id}'")
            
            # Get the create contact use case
            create_contact_use_case = self.container.get_create_contact_use_case()
            
            # Import the DTO and enums
            from ...application.dto.contact_dto import ContactCreateDTO, ContactAddressDTO
            from ...domain.entities.contact import ContactType
            
            # Parse the name into first_name and last_name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0] if name_parts else name
            last_name = name_parts[1] if len(name_parts) > 1 else None
            
            # Convert string contact_type to enum
            contact_type_enum = ContactType.CUSTOMER
            if contact_type.lower() in ['lead']:
                contact_type_enum = ContactType.LEAD
            elif contact_type.lower() in ['prospect']:
                contact_type_enum = ContactType.PROSPECT
            elif contact_type.lower() in ['vendor', 'supplier']:
                contact_type_enum = ContactType.VENDOR
            elif contact_type.lower() == 'partner':
                contact_type_enum = ContactType.PARTNER
            elif contact_type.lower() == 'contractor':
                contact_type_enum = ContactType.CONTRACTOR
            elif contact_type.lower() in ['business', 'client', 'customer']:
                contact_type_enum = ContactType.CUSTOMER
            
            logger.info(f"🔥 Mapped contact_type '{contact_type}' to {contact_type_enum}")
            
            # Parse address if provided
            address_dto = None
            if address:
                address_dto = ContactAddressDTO(
                    street_address=address
                )
            
            # Execute use case
            result = await create_contact_use_case.execute(
                ContactCreateDTO(
                    business_id=uuid.UUID(business_id),
                    contact_type=contact_type_enum,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    address=address_dto,
                    notes=notes,
                    created_by=user_id
                ),
                user_id=user_id
            )
            
            logger.info(f"🔥 create_contact_use_case.execute COMPLETED with result: {result}")
            return f"✅ Contact created successfully! Added {name} to your contacts."
            
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            return f"❌ I encountered an error while creating the contact: {str(e)}"
    
    @function_tool
    async def validate_contact_info(self, name: str, phone: Optional[str] = None, email: Optional[str] = None) -> str:
        """Validate contact information before creating the contact"""
        issues = []
        suggestions = []
        
        # Validate name
        if not name or len(name.strip()) < 2:
            issues.append("Name should be at least 2 characters long")
        
        # Validate phone (basic validation)
        if phone:
            clean_phone = ''.join(filter(str.isdigit, phone))
            if len(clean_phone) < 10:
                issues.append("Phone number seems too short")
            elif len(clean_phone) > 15:
                issues.append("Phone number seems too long")
        else:
            suggestions.append("Consider adding a phone number for better contact options")
        
        # Validate email (basic validation)
        if email:
            if '@' not in email or '.' not in email.split('@')[-1]:
                issues.append("Email format doesn't look correct")
        else:
            suggestions.append("Consider adding an email for digital communication")
        
        if issues:
            return f"⚠️ Found some issues: {', '.join(issues)}. Please provide correct information."
        elif suggestions:
            return f"✅ Information looks good! {' '.join(suggestions)}"
        else:
            return "✅ All contact information looks perfect!"
    
    @function_tool
    async def check_duplicate_contacts(self, name: str, phone: Optional[str] = None, email: Optional[str] = None) -> str:
        """Check for potentially duplicate contacts"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Search for similar contacts
            search_contacts_use_case = self.container.get_search_contacts_use_case()
            
            from ...application.dto.contact_dto import ContactSearchDTO
            
            # Check by name first
            result = await search_contacts_use_case.execute(
                ContactSearchDTO(
                    search_term=name,
                    limit=5,
                    business_id=uuid.UUID(business_id)
                ),
                user_id=user_id
            )
            
            similar_contacts = []
            for contact in result.contacts:
                similarity_reasons = []
                
                # Check name similarity
                if name.lower() in contact.name.lower() or contact.name.lower() in name.lower():
                    similarity_reasons.append("similar name")
                
                # Check phone similarity
                if phone and contact.phone and phone in contact.phone:
                    similarity_reasons.append("same phone")
                
                # Check email similarity
                if email and contact.email and email.lower() == contact.email.lower():
                    similarity_reasons.append("same email")
                
                if similarity_reasons:
                    similar_contacts.append(f"• {contact.name} ({', '.join(similarity_reasons)})")
            
            if similar_contacts:
                contacts_text = '\n'.join(similar_contacts[:3])
                return f"⚠️ Found similar contacts:\n{contacts_text}\n\nWould you like to proceed anyway or update an existing contact instead?"
            else:
                return "✅ No duplicate contacts found. Safe to create new contact."
                
        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return "✅ Couldn't check for duplicates, but proceeding with creation."
    
    @function_tool
    async def search_contacts(self, query: str, limit: int = 10) -> str:
        """Search for contacts by name, phone, or email"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the search contacts use case
            search_contacts_use_case = self.container.get_search_contacts_use_case()
            
            from ...application.dto.contact_dto import ContactSearchDTO
            
            # Execute use case
            result = await search_contacts_use_case.execute(
                ContactSearchDTO(
                    business_id=uuid.UUID(business_id),
                    search_term=query,
                    limit=limit
                ),
                user_id=user_id
            )
            
            if not result.contacts:
                return f"No contacts found matching '{query}'"
            
            contacts_text = "\n".join([
                f"• {contact.name} - {contact.phone or 'No phone'} - {contact.email or 'No email'}"
                for contact in result.contacts
            ])
            
            return f"📞 Found {len(result.contacts)} contact(s) matching '{query}':\n{contacts_text}"
            
        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            return f"❌ I encountered an error while searching for contacts: {str(e)}"
    
    @function_tool
    async def get_contact_details(self, contact_id: str) -> str:
        """Get detailed information about a specific contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get contact details use case
            get_contact_details_use_case = self.container.get_get_contact_details_use_case()
            
            from ...application.dto.contact_dto import GetContactDetailsDTO
            
            # Execute use case
            result = await get_contact_details_use_case.execute(
                GetContactDetailsDTO(
                    contact_id=contact_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            contact = result.contact
            details = f"""
📞 Contact Details:
• Name: {contact.name}
• Phone: {contact.phone or 'Not provided'}
• Email: {contact.email or 'Not provided'}
• Address: {contact.address or 'Not provided'}
• Type: {contact.contact_type}
• Notes: {contact.notes or 'None'}
• Created: {contact.created_at}
            """
            
            return details.strip()
            
        except Exception as e:
            logger.error(f"Error getting contact details: {e}")
            return f"❌ I encountered an error while getting contact details: {str(e)}"
    
    @function_tool
    async def update_contact(self,
                           contact_id: str,
                           name: Optional[str] = None,
                           phone: Optional[str] = None,
                           email: Optional[str] = None,
                           address: Optional[str] = None,
                           contact_type: Optional[str] = None,
                           notes: Optional[str] = None) -> str:
        """Update an existing contact with new information"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the update contact use case
            update_contact_use_case = self.container.get_update_contact_use_case()
            
            from ...application.dto.contact_dto import ContactUpdateDTO, ContactAddressDTO
            from ...domain.entities.contact import ContactType
            
            # Parse the name into first_name and last_name if provided
            first_name = None
            last_name = None
            if name:
                name_parts = name.split(' ', 1)
                first_name = name_parts[0] if name_parts else name
                last_name = name_parts[1] if len(name_parts) > 1 else None
            
            # Convert string contact_type to enum if provided
            contact_type_enum = None
            if contact_type:
                if contact_type.lower() in ['lead', 'prospect']:
                    contact_type_enum = ContactType.LEAD
                elif contact_type.lower() == 'vendor':
                    contact_type_enum = ContactType.VENDOR
                elif contact_type.lower() == 'partner':
                    contact_type_enum = ContactType.PARTNER
                elif contact_type.lower() == 'contractor':
                    contact_type_enum = ContactType.CONTRACTOR
                else:
                    contact_type_enum = ContactType.CUSTOMER
            
            # Parse address if provided
            address_dto = None
            if address:
                address_dto = ContactAddressDTO(
                    street_address=address
                )
            
            # Execute use case
            result = await update_contact_use_case.execute(
                ContactUpdateDTO(
                    contact_id=uuid.UUID(contact_id),
                    business_id=uuid.UUID(business_id),
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    address=address_dto,
                    notes=notes
                ),
                user_id=user_id
            )
            
            return f"✅ Contact updated successfully!"
            
        except Exception as e:
            logger.error(f"Error updating contact: {e}")
            return f"❌ I encountered an error while updating the contact: {str(e)}"
    
    @function_tool
    async def delete_contact(self, contact_id: str) -> str:
        """Delete a contact"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the delete contact use case
            delete_contact_use_case = self.container.get_delete_contact_use_case()
            
            from ...application.dto.contact_dto import DeleteContactDTO
            
            # Execute use case
            result = await delete_contact_use_case.execute(
                DeleteContactDTO(
                    contact_id=contact_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Contact deleted successfully!"
            
        except Exception as e:
            logger.error(f"Error deleting contact: {e}")
            return f"❌ I encountered an error while deleting the contact: {str(e)}"
    
    def get_specialist_capabilities(self) -> List[str]:
        """Get list of capabilities for this specialist agent"""
        return [
            "Create new contacts with intelligent validation",
            "Update existing contact information",
            "Search for contacts by name, phone, or email",
            "Get detailed contact information",
            "Delete contacts with confirmation",
            "Validate contact information before creation",
            "Check for duplicate contacts",
            "Natural conversation for contact management",
            "Automatic parameter collection through conversation"
        ]
    
    async def initialize_agent(self, ctx):
        """Initialize contact agent"""
        logger.info("📞 Contact Agent initialized")
    
    async def cleanup_agent(self, ctx):
        """Clean up contact agent"""
        logger.info("👋 Contact Agent cleaned up")
    
    async def process_message(self, ctx, message: str) -> str:
        """Process user message"""
        # Process contact-related messages
        return f"Contact agent processing: {message}" 