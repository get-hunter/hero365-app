"""
Contact Management Tools for Hero365 LiveKit Agents
"""

import logging
import uuid
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ContactTools:
    """Contact management tools for the Hero365 agent"""
    
    def __init__(self, session_context: Dict[str, Any], context_intelligence: Optional[Any] = None):
        self.session_context = session_context
        self.context_intelligence = context_intelligence
        self._container = None
        self._contact_repo = None
        
    def _get_container(self):
        """Get dependency injection container"""
        if not self._container:
            try:
                from app.infrastructure.config.dependency_injection import get_container
                self._container = get_container()
                logger.info("✅ Retrieved container for ContactTools")
            except Exception as e:
                logger.error(f"❌ Error getting container: {e}")
                return None
        return self._container
    
    def _get_contact_repository(self):
        """Get contact repository with caching"""
        if not self._contact_repo:
            container = self._get_container()
            if container:
                try:
                    self._contact_repo = container.get_contact_repository()
                    logger.info("✅ Contact repository retrieved successfully")
                except Exception as e:
                    logger.error(f"❌ Error getting contact repository: {e}")
                    return None
        return self._contact_repo
    
    def _get_business_id(self) -> Optional[uuid.UUID]:
        """Get business ID from context"""
        business_id = self.session_context.get('business_id')
        if business_id:
            if isinstance(business_id, str):
                return uuid.UUID(business_id)
            return business_id
        return None

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
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get contact repository
            contact_repo = self._get_contact_repository()
            if not contact_repo:
                return "Contact repository not available"
            
            # Check if contact already exists
            if phone:
                existing_contact = await contact_repo.get_by_phone(business_id, phone)
                if existing_contact:
                    return f"A contact with phone {phone} already exists: {existing_contact.get_display_name()}"
            
            if email:
                existing_contact = await contact_repo.get_by_email(business_id, email)
                if existing_contact:
                    return f"A contact with email {email} already exists: {existing_contact.get_display_name()}"
            
            # Parse name into first and last name
            name_parts = name.strip().split(' ', 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Import contact entity and enums
            from app.domain.entities.contact import Contact, ContactType
            from app.domain.value_objects.address import Address
            
            # Convert string contact_type to enum
            try:
                contact_type_enum = ContactType(contact_type.lower())
            except ValueError:
                contact_type_enum = ContactType.LEAD
            
            # Create address object if provided
            address_obj = None
            if address:
                address_obj = Address(street_address=address, city="", state="", postal_code="", country="US")
            
            # Create new contact
            new_contact = Contact(
                business_id=business_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                contact_type=contact_type_enum,
                address=address_obj,
                notes=f"Created via voice agent on {logger.name}"
            )
            
            # Save to repository
            created_contact = await contact_repo.create(new_contact)
            
            response = f"Successfully created contact {created_contact.get_display_name()}"
            if phone:
                response += f" with phone number {phone}"
            if email:
                response += f" and email {email}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating contact: {e}")
            return f"Error creating contact: {str(e)}"

    async def search_contacts(self, query: str, limit: int = 10) -> str:
        """Search for contacts with direct repository access.
        
        Args:
            query: Search query (name, phone, email, etc.)
            limit: Maximum number of results to return
        """
        try:
            logger.info(f"🔍 Searching contacts for: {query}")
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get contact repository
            contact_repo = self._get_contact_repository()
            if not contact_repo:
                return "Contact repository not available"
            
            # Search in database
            contacts = await contact_repo.search_contacts(business_id, query, limit=limit)
            
            if contacts:
                response = f"Found {len(contacts)} contacts matching '{query}': "
                contact_list = []
                for i, contact in enumerate(contacts, 1):
                    contact_info = f"{i}. {contact.get_display_name()}"
                    if contact.phone:
                        contact_info += f", phone {contact.phone}"
                    if contact.email:
                        contact_info += f", email {contact.email}"
                    contact_list.append(contact_info)
                response += ". ".join(contact_list)
                return response
            else:
                return f"No contacts found matching '{query}'. Would you like to create a new contact?"
                
        except Exception as e:
            logger.error(f"❌ Error searching contacts: {e}")
            return f"Error searching contacts: {str(e)}"

    async def get_suggested_contacts(self, limit: int = 5) -> str:
        """Get recent contacts directly from repository.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            logger.info("💡 Getting recent contacts")
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get contact repository
            contact_repo = self._get_contact_repository()
            if not contact_repo:
                return "Contact repository not available"
            
            # Get recent contacts from repository
            recent_contacts = await contact_repo.get_recent_by_business(business_id, limit=limit)
            
            if recent_contacts:
                response = f"Here are {len(recent_contacts)} recent contacts you might want to reach out to: "
                contact_list = []
                for i, contact in enumerate(recent_contacts, 1):
                    contact_info = f"{i}. {contact.get_display_name()}"
                    if contact.phone:
                        contact_info += f", phone {contact.phone}"
                    contact_list.append(contact_info)
                response += ". ".join(contact_list)
                return response
            else:
                return "No recent contacts found. Would you like to create a new contact?"
                
        except Exception as e:
            logger.error(f"❌ Error getting contact suggestions: {e}")
            return f"Error getting contact suggestions: {str(e)}"

    async def get_contact_info(self, contact_name: str, info_type: str = "all") -> str:
        """Get specific information about a contact by name.
        
        Args:
            contact_name: Name of the contact to get information for
            info_type: Type of information to retrieve. Examples:
                - "phone" or "number" - Get phone numbers
                - "email" or "mail" - Get email address
                - "address" or "location" - Get physical address
                - "company" or "work" - Get company information
                - "notes" or "comments" - Get contact notes
                - "all" (default) - Get complete contact information
        """
        try:
            logger.info(f"📋 Getting {info_type} info for: {contact_name}")
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get contact repository
            contact_repo = self._get_contact_repository()
            if not contact_repo:
                return "Contact repository not available"
            
            # Search for contact by name
            contacts = await contact_repo.search_contacts(business_id, contact_name, limit=5)
            
            if not contacts:
                return f"Contact '{contact_name}' not found"
            
            if len(contacts) > 1:
                response = f"Found multiple contacts matching '{contact_name}': "
                contact_list = []
                for i, contact in enumerate(contacts, 1):
                    contact_info = f"{i}. {contact.get_display_name()}"
                    if contact.phone:
                        contact_info += f", phone {contact.phone}"
                    contact_list.append(contact_info)
                response += ". ".join(contact_list)
                response += ". Please be more specific with the contact name."
                return response
            
            # Get the single contact
            contact = contacts[0]
            contact_name_display = contact.get_display_name()
            
            # Handle specific info types
            info_type = info_type.lower().strip()
            
            if info_type in ["phone", "phone number", "number", "call"]:
                if contact.phone and contact.mobile_phone:
                    return f"{contact_name_display} has primary phone {contact.phone} and mobile phone {contact.mobile_phone}"
                elif contact.phone:
                    return f"{contact_name_display}'s phone number is {contact.phone}"
                elif contact.mobile_phone:
                    return f"{contact_name_display}'s mobile number is {contact.mobile_phone}"
                else:
                    return f"{contact_name_display} doesn't have a phone number on file."
            
            elif info_type in ["email", "e-mail", "mail"]:
                if contact.email:
                    return f"{contact_name_display}'s email is {contact.email}"
                else:
                    return f"{contact_name_display} doesn't have an email on file."
            
            elif info_type in ["address", "location", "where"]:
                if contact.address:
                    return f"{contact_name_display}'s address is {contact.address.street_address}, {contact.address.city}, {contact.address.state} {contact.address.postal_code}"
                else:
                    return f"{contact_name_display} doesn't have an address on file."
            
            elif info_type in ["company", "business", "work"]:
                if contact.company_name:
                    company_info = f"{contact_name_display} works at {contact.company_name}"
                    if contact.job_title:
                        company_info += f" as {contact.job_title}"
                    return company_info
                else:
                    return f"{contact_name_display} doesn't have company information on file."
            
            elif info_type in ["notes", "note", "comments"]:
                if contact.notes:
                    return f"Notes for {contact_name_display}: {contact.notes}"
                else:
                    return f"No notes on file for {contact_name_display}."
            
            # Default: return comprehensive information
            else:
                response = f"Complete information for {contact_name_display}: "
                info_parts = []
                
                if contact.phone:
                    info_parts.append(f"phone {contact.phone}")
                if contact.mobile_phone and contact.mobile_phone != contact.phone:
                    info_parts.append(f"mobile {contact.mobile_phone}")
                if contact.email:
                    info_parts.append(f"email {contact.email}")
                if contact.company_name:
                    company_part = f"works at {contact.company_name}"
                    if contact.job_title:
                        company_part += f" as {contact.job_title}"
                    info_parts.append(company_part)
                if contact.address:
                    info_parts.append(f"address is {contact.address.street_address}, {contact.address.city}, {contact.address.state} {contact.address.postal_code}")
                
                contact_type = contact.get_type_display() if hasattr(contact, 'get_type_display') else "customer"
                info_parts.append(f"contact type is {contact_type}")
                
                if contact.notes:
                    info_parts.append(f"notes: {contact.notes}")
                
                if hasattr(contact, 'last_contacted') and contact.last_contacted:
                    info_parts.append(f"last contacted on {contact.last_contacted.strftime('%B %d, %Y')}")
                
                response += ", ".join(info_parts)
                return response
                
        except Exception as e:
            logger.error(f"❌ Error getting contact info: {e}")
            return f"Error getting contact info: {str(e)}" 