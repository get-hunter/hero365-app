"""
Voice agent tools for contact management.
Provides voice-activated contact operations for Hero365.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from contextvars import ContextVar

from livekit.agents import function_tool

from app.infrastructure.config.dependency_injection import DependencyContainer
from app.application.use_cases.contact.create_contact_use_case import CreateContactUseCase
from app.application.use_cases.contact.get_contact_use_case import GetContactUseCase
from app.application.use_cases.contact.list_contacts_use_case import ListContactsUseCase
from app.application.use_cases.contact.update_contact_use_case import UpdateContactUseCase
from app.application.use_cases.contact.delete_contact_use_case import DeleteContactUseCase
from app.application.use_cases.contact.search_contacts_use_case import SearchContactsUseCase
from app.application.use_cases.contact.contact_interaction_use_case import ContactInteractionUseCase
from app.application.dto.contact_dto import (
    ContactResponseDTO,
    ContactCreateDTO,
    ContactUpdateDTO,
    ContactSearchDTO,
    ContactAddressDTO,
)
from app.domain.enums import ContactType, ContactStatus

logger = logging.getLogger(__name__)

# Context variable to store the current agent context
_current_context: ContextVar[Dict[str, Any]] = ContextVar('current_context', default={})

def set_current_context(context: Dict[str, Any]) -> None:
    """Set the current agent context."""
    _current_context.set(context)

def get_current_context() -> Dict[str, Any]:
    """Get the current agent context."""
    context = _current_context.get()
    if not context.get("business_id") or not context.get("user_id"):
        logger.warning("Agent context not available for contact tools")
        return {"business_id": None, "user_id": None}
    return context


@function_tool
async def create_contact(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    address: Optional[str] = None,
    contact_type: str = "customer",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new contact for the business.
    
    Args:
        name: Contact name
        email: Contact email address
        phone: Contact phone number
        company: Company name (if applicable)
        address: Contact address
        contact_type: Type of contact (customer, lead, vendor, partner)
        notes: Additional notes about the contact
    
    Returns:
        Dictionary with contact creation result
    """
    try:
        container = DependencyContainer()
        create_contact_use_case = container.get_create_contact_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to create contact. Please try again."
            }
        
        # Convert contact type string to enum
        try:
            contact_type_enum = ContactType(contact_type.upper())
        except ValueError:
            contact_type_enum = ContactType.CUSTOMER
        
        contact_dto = ContactCreateDTO(
            business_id=uuid.UUID(business_id),
            name=name,
            email=email,
            phone=phone,
            company=company,
            address=address,
            contact_type=contact_type_enum,
            notes=notes
        )
        
        result = await create_contact_use_case.execute(contact_dto, business_id, user_id)
        
        logger.info(f"Created contact via voice agent: {result.id}")
        
        return {
            "success": True,
            "contact_id": str(result.id),
            "name": result.name,
            "email": result.email,
            "phone": result.phone,
            "contact_type": result.contact_type.value,
            "message": f"Contact '{name}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating contact via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create contact. Please try again or contact support."
        }


@function_tool
async def search_contacts(search_term: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search contacts by name, email, phone, or company.
    
    Args:
        search_term: Text to search for in contact fields
        limit: Maximum number of contacts to return (default: 10)
    
    Returns:
        Dictionary with search results
    """
    try:
        container = DependencyContainer()
        search_contacts_use_case = container.get_search_contacts_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to search contacts. Please try again."
            }
        
        search_criteria = ContactSearchDTO(
            search_text=search_term
        )
        
        results = await search_contacts_use_case.search_contacts(
            business_id=business_id,
            criteria=search_criteria,
            user_id=user_id,
            skip=0,
            limit=limit
        )
        
        contacts = []
        for contact in results:
            contacts.append({
                "id": str(contact.id),
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "contact_type": contact.contact_type.value,
                "status": contact.status.value if hasattr(contact, 'status') else "active"
            })
        
        logger.info(f"Found {len(contacts)} contacts matching '{search_term}' via voice agent")
        
        return {
            "success": True,
            "contacts": contacts,
            "search_term": search_term,
            "total_count": len(contacts),
            "message": f"Found {len(contacts)} contacts matching '{search_term}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching contacts via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search contacts. Please try again."
        }


@function_tool
async def get_recent_contacts(limit: int = 10) -> Dict[str, Any]:
    """
    Get recently created or updated contacts.
    
    Args:
        limit: Maximum number of contacts to return (default: 10)
    
    Returns:
        Dictionary with recent contacts
    """
    try:
        container = DependencyContainer()
        contact_repository = container.get_contact_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve recent contacts. Please try again."
            }
        
        # Get recent contacts from repository
        contacts = await contact_repository.get_recent_contacts(
            business_id=uuid.UUID(business_id),
            limit=limit
        )
        
        recent_contacts = []
        for contact in contacts:
            recent_contacts.append({
                "id": str(contact.id),
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "contact_type": contact.contact_type.value,
                "created_at": contact.created_at.isoformat() if contact.created_at else None,
                "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
            })
        
        logger.info(f"Retrieved {len(recent_contacts)} recent contacts via voice agent")
        
        return {
            "success": True,
            "contacts": recent_contacts,
            "total_count": len(recent_contacts),
            "message": f"Found {len(recent_contacts)} recent contacts"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving recent contacts via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve recent contacts. Please try again."
        }


@function_tool
async def get_contacts_by_type(contact_type: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get contacts filtered by type.
    
    Args:
        contact_type: Contact type (customer, lead, vendor, partner)
        limit: Maximum number of contacts to return (default: 10)
    
    Returns:
        Dictionary with filtered contacts
    """
    try:
        container = DependencyContainer()
        contact_repository = container.get_contact_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve contacts by type. Please try again."
            }
        
        # Convert contact type string to enum
        try:
            contact_type_enum = ContactType(contact_type.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid contact type: {contact_type}",
                "message": "Valid contact types are: customer, lead, vendor, partner"
            }
        
        # Get contacts by type from repository
        contacts = await contact_repository.get_by_type(
            business_id=uuid.UUID(business_id),
            contact_type=contact_type_enum,
            skip=0,
            limit=limit
        )
        
        contact_list = []
        for contact in contacts:
            contact_list.append({
                "id": str(contact.id),
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "contact_type": contact.contact_type.value
            })
        
        logger.info(f"Retrieved {len(contact_list)} contacts of type {contact_type} via voice agent")
        
        return {
            "success": True,
            "contacts": contact_list,
            "contact_type": contact_type,
            "total_count": len(contact_list),
            "message": f"Found {len(contact_list)} contacts of type: {contact_type}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contacts by type via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve contacts by type. Please try again."
        }


@function_tool
async def get_contact_details(contact_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific contact.
    
    Args:
        contact_id: ID of the contact to retrieve
    
    Returns:
        Dictionary with contact details
    """
    try:
        container = DependencyContainer()
        get_contact_use_case = container.get_get_contact_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve contact details. Please try again."
            }
        
        result = await get_contact_use_case.execute(
            contact_id=uuid.UUID(contact_id),
            business_id=business_id,
            user_id=user_id
        )
        
        logger.info(f"Retrieved contact details for {contact_id} via voice agent")
        
        return {
            "success": True,
            "contact": {
                "id": str(result.id),
                "name": result.name,
                "email": result.email,
                "phone": result.phone,
                "company": result.company,
                "address": result.address,
                "contact_type": result.contact_type.value,
                "status": result.status.value if hasattr(result, 'status') else "active",
                "notes": result.notes,
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None
            },
            "message": f"Retrieved details for contact {result.name}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contact details via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve contact details. Please try again."
        }


@function_tool
async def update_contact(
    contact_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    address: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update contact information.
    
    Args:
        contact_id: ID of the contact to update
        name: Updated contact name
        email: Updated contact email
        phone: Updated contact phone
        company: Updated company name
        address: Updated contact address
        notes: Updated notes
    
    Returns:
        Dictionary with update result
    """
    try:
        container = DependencyContainer()
        update_contact_use_case = container.get_update_contact_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to update contact. Please try again."
            }
        
        # Create update DTO with only provided fields
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if company is not None:
            update_data["company"] = company
        if address is not None:
            update_data["address"] = address
        if notes is not None:
            update_data["notes"] = notes
        
        if not update_data:
            return {
                "success": False,
                "error": "No update data provided",
                "message": "Please provide at least one field to update"
            }
        
        update_dto = ContactUpdateDTO(**update_data)
        
        result = await update_contact_use_case.execute(
            contact_id=uuid.UUID(contact_id),
            contact_data=update_dto,
            business_id=business_id,
            user_id=user_id
        )
        
        logger.info(f"Updated contact {contact_id} via voice agent")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "updated_fields": list(update_data.keys()),
            "message": f"Contact updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating contact via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update contact. Please try again."
        }


@function_tool
async def add_contact_interaction(
    contact_id: str,
    interaction_type: str,
    description: str,
    outcome: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add an interaction record to a contact.
    
    Args:
        contact_id: ID of the contact
        interaction_type: Type of interaction (call, email, meeting, sms, other)
        description: Description of the interaction
        outcome: Outcome of the interaction
    
    Returns:
        Dictionary with interaction record result
    """
    try:
        container = DependencyContainer()
        contact_interaction_use_case = container.get_contact_interaction_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to add contact interaction. Please try again."
            }
        
        interaction_dto = ContactInteractionDTO(
            contact_id=uuid.UUID(contact_id),
            interaction_type=interaction_type,
            description=description,
            outcome=outcome,
            interaction_date=datetime.now()
        )
        
        result = await contact_interaction_use_case.add_interaction(
            interaction_dto,
            business_id,
            user_id
        )
        
        logger.info(f"Added interaction to contact {contact_id} via voice agent")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "interaction_id": str(result.id),
            "interaction_type": interaction_type,
            "description": description,
            "message": f"Interaction added to contact successfully"
        }
        
    except Exception as e:
        logger.error(f"Error adding contact interaction via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add contact interaction. Please try again."
        }


@function_tool
async def get_contact_interactions(contact_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get interaction history for a contact.
    
    Args:
        contact_id: ID of the contact
        limit: Maximum number of interactions to return (default: 10)
    
    Returns:
        Dictionary with interaction history
    """
    try:
        container = DependencyContainer()
        contact_interaction_use_case = container.get_contact_interaction_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve contact interactions. Please try again."
            }
        
        interactions = await contact_interaction_use_case.get_contact_interactions(
            contact_id=uuid.UUID(contact_id),
            business_id=business_id,
            user_id=user_id,
            limit=limit
        )
        
        interaction_list = []
        for interaction in interactions:
            interaction_list.append({
                "id": str(interaction.id),
                "interaction_type": interaction.interaction_type,
                "description": interaction.description,
                "outcome": interaction.outcome,
                "interaction_date": interaction.interaction_date.isoformat() if interaction.interaction_date else None
            })
        
        logger.info(f"Retrieved {len(interaction_list)} interactions for contact {contact_id} via voice agent")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "interactions": interaction_list,
            "total_count": len(interaction_list),
            "message": f"Found {len(interaction_list)} interactions for this contact"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contact interactions via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve contact interactions. Please try again."
        } 