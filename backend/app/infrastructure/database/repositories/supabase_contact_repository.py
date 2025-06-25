"""
Supabase Contact Repository Implementation

Implements contact data access operations using Supabase as the database backend.
"""

import uuid
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from supabase import Client
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.entities.contact import Contact, ContactType, ContactStatus, ContactPriority, ContactSource, ContactAddress, RelationshipStatus, LifecycleStage
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, DuplicateEntityError, DatabaseError
from app.api.schemas.contact_schemas import UserDetailLevel


class SupabaseContactRepository(ContactRepository):
    """
    Supabase implementation of the Contact repository.
    
    Handles all contact data access operations using Supabase as the backend database.
    """
    
    def __init__(self, client: Client):
        self.client = client
        self.table_name = "contacts"
    
    async def create(self, contact: Contact) -> Contact:
        """Create a new contact."""
        try:
            contact_data = self._contact_to_dict(contact)
            
            response = self.client.table(self.table_name).insert(contact_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create contact")
            
            return self._dict_to_contact(response.data[0])
            
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError("Contact with this email or phone already exists")
            raise DatabaseError(f"Failed to create contact: {str(e)}")
    
    async def get_by_id(self, contact_id: uuid.UUID) -> Optional[Contact]:
        """Get contact by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "id", str(contact_id)
            ).execute()
            
            if not response.data:
                return None
            
            return self._dict_to_contact(response.data[0])
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contact by ID: {str(e)}")
    
    async def get_by_id_with_users(self, contact_id: uuid.UUID, user_detail_level: UserDetailLevel = UserDetailLevel.BASIC) -> Optional[Dict[str, Any]]:
        """Get contact by ID with user data included."""
        try:
            if user_detail_level == UserDetailLevel.NONE:
                # Just return the contact without user joins
                response = self.client.table(self.table_name).select("*").eq(
                    "id", str(contact_id)
                ).execute()
                
                if not response.data:
                    return None
                
                return self._prepare_contact_with_user_data(response.data[0], user_detail_level)
            
            # Build query with user joins
            user_fields = self._get_user_fields(user_detail_level)
            query = f"*,assigned_user:users!assigned_to({user_fields}),created_user:users!created_by({user_fields})"
            
            response = self.client.table(self.table_name).select(query).eq(
                "id", str(contact_id)
            ).execute()
            
            if not response.data:
                return None
            
            return self._prepare_contact_with_user_data(response.data[0], user_detail_level)
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contact with user data: {str(e)}")
    
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts by business ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by business ID: {str(e)}")
    
    async def get_by_business_id_with_users(self, business_id: uuid.UUID, user_detail_level: UserDetailLevel = UserDetailLevel.BASIC, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get contacts by business ID with user data included."""
        try:
            if user_detail_level == UserDetailLevel.NONE:
                # Just return the contacts without user joins
                response = self.client.table(self.table_name).select("*").eq(
                    "business_id", str(business_id)
                ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
                
                return [self._prepare_contact_with_user_data(contact_data, user_detail_level) for contact_data in response.data]
            
            # Build query with user joins using the public.users table
            user_fields = self._get_user_fields(user_detail_level)
            query = f"*,assigned_user:users!assigned_to({user_fields}),created_user:users!created_by({user_fields})"
            
            response = self.client.table(self.table_name).select(query).eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._prepare_contact_with_user_data(contact_data, user_detail_level) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts with user data: {str(e)}")

    def _get_user_fields(self, user_detail_level: UserDetailLevel) -> str:
        """Get the appropriate user fields for the detail level."""
        if user_detail_level == UserDetailLevel.BASIC:
            return "id,display_name,email"
        elif user_detail_level == UserDetailLevel.FULL:
            return "id,display_name,email,full_name,phone,is_active,last_sign_in"
        else:
            return "id"

    async def get_by_email(self, business_id: uuid.UUID, email: str) -> Optional[Contact]:
        """Get contact by email within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("email", email).execute()
            
            if not response.data:
                return None
            
            return self._dict_to_contact(response.data[0])
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contact by email: {str(e)}")
    
    async def get_by_phone(self, business_id: uuid.UUID, phone: str) -> Optional[Contact]:
        """Get contact by phone within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("phone", phone).execute()
            
            if not response.data:
                return None
            
            return self._dict_to_contact(response.data[0])
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contact by phone: {str(e)}")
    
    async def get_by_type(self, business_id: uuid.UUID, contact_type: ContactType, 
                         skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts by type within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("contact_type", contact_type.value).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by type: {str(e)}")
    
    async def get_by_status(self, business_id: uuid.UUID, status: ContactStatus,
                           skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts by status within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by status: {str(e)}")
    
    async def get_by_priority(self, business_id: uuid.UUID, priority: ContactPriority,
                             skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts by priority within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("priority", priority.value).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by priority: {str(e)}")
    
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts assigned to a user within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("assigned_to", user_id).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by assigned user: {str(e)}")
    
    async def get_by_tag(self, business_id: uuid.UUID, tag: str,
                        skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts by tag within a business."""
        try:
            # Using PostgREST array contains operator
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).contains("tags", f'["{tag}"]').range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by tag: {str(e)}")
    
    async def search_contacts(self, business_id: uuid.UUID, search_term: str,
                             skip: int = 0, limit: int = 100) -> List[Contact]:
        """Search contacts by name, email, phone, or company within a business."""
        try:
            # Using full-text search on multiple fields
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(
                f"first_name.ilike.%{search_term}%,"
                f"last_name.ilike.%{search_term}%,"
                f"email.ilike.%{search_term}%,"
                f"phone.ilike.%{search_term}%,"
                f"company_name.ilike.%{search_term}%"
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search contacts: {str(e)}")
    
    async def get_recently_contacted(self, business_id: uuid.UUID, days: int = 30,
                                   skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts contacted within the specified number of days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("last_contacted", cutoff_date.isoformat()).range(
                skip, skip + limit - 1
            ).order("last_contacted", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get recently contacted: {str(e)}")
    
    async def get_never_contacted(self, business_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts that have never been contacted."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).is_("last_contacted", "null").range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get never contacted: {str(e)}")
    
    async def get_high_value_contacts(self, business_id: uuid.UUID, min_value: float,
                                    skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts with estimated value above the minimum."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("estimated_value", min_value).range(
                skip, skip + limit - 1
            ).order("estimated_value", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get high value contacts: {str(e)}")
    
    async def update(self, contact: Contact) -> Contact:
        """Update an existing contact."""
        try:
            contact_data = self._contact_to_dict(contact)
            contact_data["last_modified"] = datetime.now().isoformat()
            
            response = self.client.table(self.table_name).update(contact_data).eq(
                "id", str(contact.id)
            ).execute()
            
            if not response.data:
                raise EntityNotFoundError("Contact not found")
            
            return self._dict_to_contact(response.data[0])
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update contact: {str(e)}")
    
    async def delete(self, contact_id: uuid.UUID) -> bool:
        """Delete a contact."""
        try:
            response = self.client.table(self.table_name).delete().eq(
                "id", str(contact_id)
            ).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete contact: {str(e)}")
    
    async def bulk_update_status(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                               status: ContactStatus) -> int:
        """Bulk update contact status."""
        try:
            contact_ids_str = [str(cid) for cid in contact_ids]
            
            response = self.client.table(self.table_name).update({
                "status": status.value,
                "last_modified": datetime.now().isoformat()
            }).eq("business_id", str(business_id)).in_("id", contact_ids_str).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update status: {str(e)}")
    
    async def bulk_assign_contacts(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                                 user_id: str) -> int:
        """Bulk assign contacts to a user."""
        try:
            contact_ids_str = [str(cid) for cid in contact_ids]
            
            response = self.client.table(self.table_name).update({
                "assigned_to": user_id,
                "last_modified": datetime.now().isoformat()
            }).eq("business_id", str(business_id)).in_("id", contact_ids_str).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk assign contacts: {str(e)}")
    
    async def bulk_add_tag(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                          tag: str) -> int:
        """Bulk add tag to contacts."""
        try:
            # This is a simplified implementation - in practice, you'd want to 
            # merge with existing tags rather than replace
            contact_ids_str = [str(cid) for cid in contact_ids]
            
            # Get current contacts to merge tags
            current_contacts = self.client.table(self.table_name).select(
                "id,tags"
            ).eq("business_id", str(business_id)).in_("id", contact_ids_str).execute()
            
            updates = []
            for contact_data in current_contacts.data:
                current_tags = contact_data.get("tags", [])
                if isinstance(current_tags, str):
                    current_tags = json.loads(current_tags)
                
                if tag not in current_tags:
                    current_tags.append(tag)
                
                updates.append({
                    "id": contact_data["id"],
                    "tags": json.dumps(current_tags),
                    "last_modified": datetime.now().isoformat()
                })
            
            # Perform batch update
            updated_count = 0
            for update_data in updates:
                response = self.client.table(self.table_name).update({
                    "tags": update_data["tags"],
                    "last_modified": update_data["last_modified"]
                }).eq("id", update_data["id"]).execute()
                
                if response.data:
                    updated_count += 1
            
            return updated_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk add tag: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count contacts in a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count contacts: {str(e)}")
    
    async def count_by_type(self, business_id: uuid.UUID, contact_type: ContactType) -> int:
        """Count contacts by type in a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("contact_type", contact_type.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count contacts by type: {str(e)}")
    
    async def count_by_status(self, business_id: uuid.UUID, status: ContactStatus) -> int:
        """Count contacts by status in a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count contacts by status: {str(e)}")
    
    async def get_contact_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive contact statistics for a business."""
        try:
            # Get total count
            total_response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            total_contacts = total_response.count or 0
            
            # Get counts by status
            status_counts = {}
            for status in ContactStatus:
                count_response = self.client.table(self.table_name).select("id", count="exact").eq(
                    "business_id", str(business_id)
                ).eq("status", status.value).execute()
                
                status_counts[status.value] = count_response.count or 0
            
            # Get counts by type
            type_counts = {}
            for contact_type in ContactType:
                count_response = self.client.table(self.table_name).select("id", count="exact").eq(
                    "business_id", str(business_id)
                ).eq("contact_type", contact_type.value).execute()
                
                type_counts[contact_type.value] = count_response.count or 0
            
            # Get recently contacted count (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).gte("last_contacted", cutoff_date.isoformat()).execute()
            
            recently_contacted = recent_response.count or 0
            
            # Get never contacted count
            never_response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).is_("last_contacted", "null").execute()
            
            never_contacted = never_response.count or 0
            
            # Get high value contacts count (>$1000)
            high_value_response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).gte("estimated_value", 1000).execute()
            
            high_value_contacts = high_value_response.count or 0
            
            return {
                "total_contacts": total_contacts,
                "status_breakdown": status_counts,
                "type_breakdown": type_counts,
                "recently_contacted": recently_contacted,
                "never_contacted": never_contacted,
                "high_value_contacts": high_value_contacts,
                "contact_quality_score": min(100, (recently_contacted / max(total_contacts, 1)) * 100)
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contact statistics: {str(e)}")
    
    async def exists(self, contact_id: uuid.UUID) -> bool:
        """Check if contact exists."""
        try:
            response = self.client.table(self.table_name).select("id").eq(
                "id", str(contact_id)
            ).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check contact existence: {str(e)}")
    
    async def has_duplicate_email(self, business_id: uuid.UUID, email: str, 
                                exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if email exists for another contact in the business."""
        try:
            query = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("email", email)
            
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            
            response = query.execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check duplicate email: {str(e)}")
    
    async def has_duplicate_phone(self, business_id: uuid.UUID, phone: str,
                                exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if phone exists for another contact in the business."""
        try:
            query = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("phone", phone)
            
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            
            response = query.execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check duplicate phone: {str(e)}")
    
    def _contact_to_dict(self, contact: Contact) -> Dict[str, Any]:
        """Convert Contact entity to database dictionary."""
        # Convert address to dictionary if it exists
        address_dict = None
        if contact.address:
            address_dict = {
                "street_address": contact.address.street_address,
                "city": contact.address.city,
                "state": contact.address.state,
                "postal_code": contact.address.postal_code,
                "country": contact.address.country
            }
        
        return {
            "id": str(contact.id),
            "business_id": str(contact.business_id),
            "contact_type": contact.contact_type.value,
            "status": contact.status.value,
            "relationship_status": contact.relationship_status.value,
            "lifecycle_stage": contact.lifecycle_stage.value,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "company_name": contact.company_name,
            "job_title": contact.job_title,
            "email": contact.email,
            "phone": contact.phone,
            "mobile_phone": contact.mobile_phone,
            "website": contact.website,
            "address": json.dumps(address_dict) if address_dict else None,
            "priority": contact.priority.value,
            "source": contact.source.value if contact.source else None,
            "tags": json.dumps(contact.tags),
            "notes": contact.notes,
            "estimated_value": contact.estimated_value,
            "currency": contact.currency,
            "assigned_to": contact.assigned_to,
            "created_by": contact.created_by,
            "custom_fields": json.dumps(contact.custom_fields),
            "created_date": contact.created_date.isoformat() if contact.created_date else None,
            "last_modified": contact.last_modified.isoformat() if contact.last_modified else None,
            "last_contacted": contact.last_contacted.isoformat() if contact.last_contacted else None
        }
    
    def _dict_to_contact(self, data: Dict[str, Any]) -> Contact:
        """Convert database dictionary to Contact entity."""
        # Parse address
        address = None
        if data.get("address"):
            if isinstance(data["address"], str):
                address_data = json.loads(data["address"])
            else:
                address_data = data["address"]
            
            address = ContactAddress(
                street_address=address_data.get("street_address"),
                city=address_data.get("city"),
                state=address_data.get("state"),
                postal_code=address_data.get("postal_code"),
                country=address_data.get("country")
            )
        
        # Parse tags
        tags = []
        if data.get("tags"):
            if isinstance(data["tags"], str):
                tags = json.loads(data["tags"])
            else:
                tags = data["tags"]
        
        # Parse custom fields
        custom_fields = {}
        if data.get("custom_fields"):
            if isinstance(data["custom_fields"], str):
                custom_fields = json.loads(data["custom_fields"])
            else:
                custom_fields = data["custom_fields"]
        
        # Parse dates
        created_date = None
        if data.get("created_date"):
            created_date = datetime.fromisoformat(data["created_date"].replace('Z', '+00:00'))
        
        last_modified = None
        if data.get("last_modified"):
            last_modified = datetime.fromisoformat(data["last_modified"].replace('Z', '+00:00'))
        
        last_contacted = None
        if data.get("last_contacted"):
            last_contacted = datetime.fromisoformat(data["last_contacted"].replace('Z', '+00:00'))
        
        return Contact(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            contact_type=ContactType(data["contact_type"]),
            status=ContactStatus(data["status"]),
            relationship_status=RelationshipStatus(data.get("relationship_status", "prospect")),
            lifecycle_stage=LifecycleStage(data.get("lifecycle_stage", "awareness")),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            company_name=data.get("company_name"),
            job_title=data.get("job_title"),
            email=data.get("email"),
            phone=data.get("phone"),
            mobile_phone=data.get("mobile_phone"),
            website=data.get("website"),
            address=address,
            priority=ContactPriority(data.get("priority", "medium")),
            source=ContactSource(data["source"]) if data.get("source") else None,
            tags=tags,
            notes=data.get("notes"),
            estimated_value=float(data["estimated_value"]) if data.get("estimated_value") else None,
            currency=data.get("currency", "USD"),
            assigned_to=data.get("assigned_to"),
            created_by=data.get("created_by"),
            custom_fields=custom_fields,
            created_date=created_date,
            last_modified=last_modified,
            last_contacted=last_contacted
        )
    
    def _prepare_contact_with_user_data(self, contact_data: Dict[str, Any], user_detail_level: UserDetailLevel) -> Dict[str, Any]:
        """Prepare contact data with user information based on detail level."""
        try:
            # Start with the base contact data
            result = dict(contact_data)
            
            if user_detail_level == UserDetailLevel.NONE:
                # Return just IDs for assigned_to and created_by
                result["assigned_to"] = contact_data.get("assigned_to")
                result["created_by"] = contact_data.get("created_by")
            
            elif user_detail_level == UserDetailLevel.BASIC:
                # Replace assigned_to and created_by with user objects
                if contact_data.get("assigned_user"):
                    assigned_user_data = contact_data["assigned_user"]
                    if isinstance(assigned_user_data, list) and assigned_user_data:
                        assigned_user_data = assigned_user_data[0]
                    
                    if assigned_user_data:
                        result["assigned_to"] = {
                            "id": str(assigned_user_data.get("id", "")),
                            "display_name": assigned_user_data.get("display_name", ""),
                            "email": assigned_user_data.get("email")
                        }
                    else:
                        result["assigned_to"] = None
                else:
                    result["assigned_to"] = None
                
                if contact_data.get("created_user"):
                    created_user_data = contact_data["created_user"]
                    if isinstance(created_user_data, list) and created_user_data:
                        created_user_data = created_user_data[0]
                    
                    if created_user_data:
                        result["created_by"] = {
                            "id": str(created_user_data.get("id", "")),
                            "display_name": created_user_data.get("display_name", ""),
                            "email": created_user_data.get("email")
                        }
                    else:
                        result["created_by"] = None
                else:
                    result["created_by"] = None
            
            elif user_detail_level == UserDetailLevel.FULL:
                # Replace assigned_to and created_by with full user objects
                if contact_data.get("assigned_user"):
                    assigned_user_data = contact_data["assigned_user"]
                    if isinstance(assigned_user_data, list) and assigned_user_data:
                        assigned_user_data = assigned_user_data[0]
                    
                    if assigned_user_data:
                        result["assigned_to"] = {
                            "id": str(assigned_user_data.get("id", "")),
                            "display_name": assigned_user_data.get("display_name", ""),
                            "email": assigned_user_data.get("email"),
                            "full_name": assigned_user_data.get("full_name"),
                            "phone": assigned_user_data.get("phone"),
                            "is_active": assigned_user_data.get("is_active", True),
                            "last_sign_in": assigned_user_data.get("last_sign_in")
                        }
                    else:
                        result["assigned_to"] = None
                else:
                    result["assigned_to"] = None
                
                if contact_data.get("created_user"):
                    created_user_data = contact_data["created_user"]
                    if isinstance(created_user_data, list) and created_user_data:
                        created_user_data = created_user_data[0]
                    
                    if created_user_data:
                        result["created_by"] = {
                            "id": str(created_user_data.get("id", "")),
                            "display_name": created_user_data.get("display_name", ""),
                            "email": created_user_data.get("email"),
                            "full_name": created_user_data.get("full_name"),
                            "phone": created_user_data.get("phone"),
                            "is_active": created_user_data.get("is_active", True),
                            "last_sign_in": created_user_data.get("last_sign_in")
                        }
                    else:
                        result["created_by"] = None
                else:
                    result["created_by"] = None
            
            # Remove the user join data from the result to keep it clean
            result.pop("assigned_user", None)
            result.pop("created_user", None)
            
            return result
            
        except Exception as e:
            raise DatabaseError(f"Failed to prepare contact with user data: {str(e)}")