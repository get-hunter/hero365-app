"""
Contact Management Tools

Voice agent tools for contact management using Hero365's contact use cases.
"""

import uuid
from typing import List, Any, Dict, Optional
from app.infrastructure.config.dependency_injection import get_container
from app.application.dto.contact_dto import ContactCreateDTO, ContactUpdateDTO, ContactSearchDTO
from app.domain.enums import ContactType, ContactStatus, ContactPriority, ContactSource, RelationshipStatus


class ContactTools:
    """Contact management tools for voice agents"""
    
    def __init__(self, business_id: str, user_id: str):
        """Initialize contact tools with business and user context"""
        self.business_id = business_id
        self.user_id = user_id
        self.container = get_container()
    
    def get_tools(self) -> List[Any]:
        """Get all contact management tools"""
        return [
            self.create_contact,
            self.get_contact_info,
            self.update_contact,
            self.search_contacts,
            self.get_recent_contacts,
            self.add_contact_interaction,
            self.schedule_follow_up,
            self.get_contact_interactions
        ]
    
    async def create_contact(self, 
                           first_name: str = None, 
                           last_name: str = None,
                           company_name: str = None,
                           email: str = None,
                           phone: str = None,
                           contact_type: str = "customer",
                           notes: str = None) -> Dict[str, Any]:
        """Create a new contact"""
        try:
            create_use_case = self.container.get_create_contact_use_case()
            
            # Parse contact type
            parsed_type = ContactType.CUSTOMER
            if contact_type.lower() == "lead":
                parsed_type = ContactType.LEAD
            elif contact_type.lower() == "prospect":
                parsed_type = ContactType.PROSPECT
            elif contact_type.lower() == "vendor":
                parsed_type = ContactType.VENDOR
            
            dto = ContactCreateDTO(
                business_id=uuid.UUID(self.business_id),
                contact_type=parsed_type,
                first_name=first_name,
                last_name=last_name,
                company_name=company_name,
                email=email,
                phone=phone,
                notes=notes,
                priority=ContactPriority.MEDIUM,
                source=ContactSource.MANUAL
            )
            
            result = await create_use_case.execute(dto, self.user_id)
            
            return {
                "success": True,
                "contact": {
                    "id": str(result.id),
                    "name": result.display_name,
                    "email": result.email,
                    "phone": result.phone,
                    "company": result.company_name,
                    "type": result.contact_type.value,
                    "relationship_status": result.relationship_status.value
                },
                "message": f"Contact {result.display_name} created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create contact"
            }
    
    async def get_contact_info(self, contact_id: str) -> Dict[str, Any]:
        """Get detailed information about a contact"""
        try:
            get_use_case = self.container.get_get_contact_use_case()
            result = await get_use_case.execute(uuid.UUID(contact_id), self.user_id)
            
            return {
                "success": True,
                "contact": {
                    "id": str(result.id),
                    "name": result.display_name,
                    "email": result.email,
                    "phone": result.phone,
                    "mobile_phone": result.mobile_phone,
                    "company": result.company_name,
                    "job_title": result.job_title,
                    "type": result.contact_type.value,
                    "relationship_status": result.relationship_status.value,
                    "lifecycle_stage": result.lifecycle_stage.value,
                    "priority": result.priority.value,
                    "tags": result.tags,
                    "notes": result.notes,
                    "last_contacted": result.last_contacted.isoformat() if result.last_contacted else None,
                    "created_date": result.created_date.isoformat() if result.created_date else None
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get contact {contact_id}"
            }
    
    async def update_contact(self, 
                           contact_id: str,
                           first_name: str = None,
                           last_name: str = None,
                           company_name: str = None,
                           email: str = None,
                           phone: str = None,
                           notes: str = None,
                           tags: List[str] = None) -> Dict[str, Any]:
        """Update contact information"""
        try:
            update_use_case = self.container.get_update_contact_use_case()
            
            dto = ContactUpdateDTO(
                contact_id=uuid.UUID(contact_id),
                first_name=first_name,
                last_name=last_name,
                company_name=company_name,
                email=email,
                phone=phone,
                notes=notes,
                tags=tags
            )
            
            result = await update_use_case.execute(dto, self.user_id)
            
            return {
                "success": True,
                "contact": {
                    "id": str(result.id),
                    "name": result.display_name,
                    "email": result.email,
                    "phone": result.phone,
                    "company": result.company_name,
                    "type": result.contact_type.value,
                    "relationship_status": result.relationship_status.value
                },
                "message": f"Contact {result.display_name} updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update contact {contact_id}"
            }
    
    async def search_contacts(self, 
                            query: str,
                            relationship_status: Optional[str] = None,
                            contact_type: Optional[str] = None,
                            limit: int = 10) -> Dict[str, Any]:
        """Search contacts by name, company, or other criteria"""
        try:
            search_use_case = self.container.get_search_contacts_use_case()
            
            # Parse relationship status
            parsed_status = None
            if relationship_status:
                status_map = {
                    "prospect": RelationshipStatus.PROSPECT,
                    "lead": RelationshipStatus.QUALIFIED_LEAD,
                    "opportunity": RelationshipStatus.OPPORTUNITY,
                    "client": RelationshipStatus.ACTIVE_CLIENT,
                    "active_client": RelationshipStatus.ACTIVE_CLIENT,
                    "past_client": RelationshipStatus.PAST_CLIENT,
                    "inactive": RelationshipStatus.INACTIVE
                }
                parsed_status = status_map.get(relationship_status.lower())
            
            # Parse contact type
            parsed_type = None
            if contact_type:
                type_map = {
                    "customer": ContactType.CUSTOMER,
                    "lead": ContactType.LEAD,
                    "prospect": ContactType.PROSPECT,
                    "vendor": ContactType.VENDOR
                }
                parsed_type = type_map.get(contact_type.lower())
            
            dto = ContactSearchDTO(
                business_id=uuid.UUID(self.business_id),
                query=query,
                relationship_status=parsed_status,
                contact_type=parsed_type,
                limit=limit
            )
            
            result = await search_use_case.execute(dto, self.user_id)
            
            contacts = []
            for contact in result.contacts:
                contacts.append({
                    "id": str(contact.id),
                    "name": contact.display_name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "company": contact.company_name,
                    "type": contact.contact_type.value,
                    "relationship_status": contact.relationship_status.value,
                    "lifecycle_stage": contact.lifecycle_stage.value,
                    "priority": contact.priority.value,
                    "tags": contact.tags,
                    "last_contacted": contact.last_contacted.isoformat() if contact.last_contacted else None
                })
            
            return {
                "success": True,
                "contacts": contacts,
                "count": result.total_count,
                "message": f"Found {result.total_count} contacts matching '{query}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to search contacts with query '{query}'"
            }
    
    async def get_recent_contacts(self, limit: int = 10) -> Dict[str, Any]:
        """Get recently added or modified contacts"""
        try:
            list_use_case = self.container.get_list_contacts_use_case()
            result = await list_use_case.execute(
                business_id=uuid.UUID(self.business_id),
                user_id=self.user_id,
                limit=limit,
                order_by="created_date",
                order_direction="desc"
            )
            
            contacts = []
            for contact in result.contacts:
                contacts.append({
                    "id": str(contact.id),
                    "name": contact.display_name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "company": contact.company_name,
                    "type": contact.contact_type.value,
                    "relationship_status": contact.relationship_status.value,
                    "created_date": contact.created_date.isoformat() if contact.created_date else None
                })
            
            return {
                "success": True,
                "contacts": contacts,
                "count": len(contacts),
                "message": f"Retrieved {len(contacts)} recent contacts"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get recent contacts"
            }
    
    async def add_contact_interaction(self, 
                                    contact_id: str,
                                    interaction_type: str,
                                    notes: str,
                                    outcome: Optional[str] = None) -> Dict[str, Any]:
        """Add an interaction record for a contact"""
        try:
            interaction_use_case = self.container.get_contact_interaction_use_case()
            
            result = await interaction_use_case.add_interaction(
                contact_id=uuid.UUID(contact_id),
                interaction_type=interaction_type,
                notes=notes,
                outcome=outcome,
                user_id=self.user_id
            )
            
            return {
                "success": True,
                "message": f"Interaction recorded for contact {contact_id}",
                "interaction_id": str(result.id) if hasattr(result, 'id') else f"int_{contact_id}_{interaction_type}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to record interaction for contact {contact_id}"
            }
    
    async def get_contact_interactions(self, 
                                     contact_id: str,
                                     limit: int = 10) -> Dict[str, Any]:
        """Get interaction history for a contact"""
        try:
            interaction_use_case = self.container.get_contact_interaction_use_case()
            
            result = await interaction_use_case.get_interactions(
                contact_id=uuid.UUID(contact_id),
                user_id=self.user_id,
                limit=limit
            )
            
            interactions = []
            for interaction in result.interactions:
                interactions.append({
                    "id": str(interaction.id),
                    "type": interaction.interaction_type,
                    "notes": interaction.notes,
                    "outcome": interaction.outcome,
                    "date": interaction.interaction_date.isoformat() if interaction.interaction_date else None
                })
            
            return {
                "success": True,
                "interactions": interactions,
                "count": len(interactions),
                "message": f"Retrieved {len(interactions)} interactions for contact {contact_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get interactions for contact {contact_id}"
            }
    
    async def schedule_follow_up(self, 
                               contact_id: str,
                               follow_up_date: str,
                               notes: str,
                               priority: str = "medium") -> Dict[str, Any]:
        """Schedule a follow-up with a contact"""
        try:
            # This would integrate with the scheduling system
            # For now, we'll add it as a special interaction
            interaction_use_case = self.container.get_contact_interaction_use_case()
            
            result = await interaction_use_case.add_interaction(
                contact_id=uuid.UUID(contact_id),
                interaction_type="follow_up_scheduled",
                notes=f"Follow-up scheduled for {follow_up_date}: {notes}",
                outcome=f"priority_{priority}",
                user_id=self.user_id
            )
            
            return {
                "success": True,
                "message": f"Follow-up scheduled with contact {contact_id} for {follow_up_date}",
                "follow_up_id": str(result.id) if hasattr(result, 'id') else f"followup_{contact_id}_{follow_up_date}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to schedule follow-up for contact {contact_id}"
            } 