"""
Supabase Contact Repository Implementation

Implements contact data access operations using Supabase as the database backend.
"""

import uuid
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from supabase import Client
from ....domain.repositories.contact_repository import ContactRepository
from ....domain.entities.contact import Contact, ContactType, ContactStatus, ContactPriority, ContactSource, ContactAddress
from ....domain.exceptions.domain_exceptions import EntityNotFoundError, DuplicateEntityError, DatabaseError


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
    
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts by business ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by business ID: {str(e)}")
    
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
            ).or_(f"phone.eq.{phone},mobile_phone.eq.{phone}").execute()
            
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
        """Get contacts assigned to a specific user within a business."""
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
        """Get contacts with a specific tag within a business."""
        try:
            # Use JSONB contains operator for tag search
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).contains("tags", [tag]).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contacts by tag: {str(e)}")
    
    async def search_contacts(self, business_id: uuid.UUID, search_term: str,
                             skip: int = 0, limit: int = 100) -> List[Contact]:
        """Search contacts within a business by name, email, phone, or company."""
        try:
            # Use text search across multiple fields
            search_query = f"%{search_term}%"
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(
                f"first_name.ilike.{search_query},"
                f"last_name.ilike.{search_query},"
                f"company_name.ilike.{search_query},"
                f"email.ilike.{search_query},"
                f"phone.ilike.{search_query},"
                f"mobile_phone.ilike.{search_query}"
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search contacts: {str(e)}")
    
    async def get_recently_contacted(self, business_id: uuid.UUID, days: int = 30,
                                   skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts that were recently contacted within a business."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("last_contacted", cutoff_date.isoformat()).range(
                skip, skip + limit - 1
            ).order("last_contacted", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get recently contacted contacts: {str(e)}")
    
    async def get_never_contacted(self, business_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts that have never been contacted within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).is_("last_contacted", "null").range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_contact(contact_data) for contact_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get never contacted contacts: {str(e)}")
    
    async def get_high_value_contacts(self, business_id: uuid.UUID, min_value: float,
                                    skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get contacts with estimated value above threshold within a business."""
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
            # Remove id from update data
            contact_data.pop('id', None)
            
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
        """Delete a contact by ID."""
        try:
            response = self.client.table(self.table_name).delete().eq(
                "id", str(contact_id)
            ).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete contact: {str(e)}")
    
    async def bulk_update_status(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                               status: ContactStatus) -> int:
        """Update status for multiple contacts."""
        try:
            contact_id_strings = [str(cid) for cid in contact_ids]
            
            response = self.client.table(self.table_name).update({
                "status": status.value,
                "last_modified": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_("id", contact_id_strings).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update status: {str(e)}")
    
    async def bulk_assign_contacts(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                                 user_id: str) -> int:
        """Assign multiple contacts to a user."""
        try:
            contact_id_strings = [str(cid) for cid in contact_ids]
            
            response = self.client.table(self.table_name).update({
                "assigned_to": user_id,
                "last_modified": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_("id", contact_id_strings).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk assign contacts: {str(e)}")
    
    async def bulk_add_tag(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                          tag: str) -> int:
        """Add a tag to multiple contacts."""
        try:
            # This is simplified - in production, you'd want to use a stored procedure
            # or more sophisticated JSONB operations to avoid race conditions
            updated_count = 0
            
            for contact_id in contact_ids:
                contact = await self.get_by_id(contact_id)
                if contact and contact.business_id == business_id:
                    if tag not in contact.tags:
                        contact.add_tag(tag)
                        await self.update(contact)
                        updated_count += 1
            
            return updated_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk add tag: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Get total count of contacts for a business."""
        try:
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count contacts: {str(e)}")
    
    async def count_by_type(self, business_id: uuid.UUID, contact_type: ContactType) -> int:
        """Get count of contacts by type for a business."""
        try:
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).eq(
                "contact_type", contact_type.value
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count contacts by type: {str(e)}")
    
    async def count_by_status(self, business_id: uuid.UUID, status: ContactStatus) -> int:
        """Get count of contacts by status for a business."""
        try:
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).eq(
                "status", status.value
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count contacts by status: {str(e)}")
    
    async def get_contact_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive contact statistics for a business."""
        try:
            # This is simplified - in production, you'd use aggregate queries
            stats = {}
            
            # Total counts
            stats["total_contacts"] = await self.count_by_business(business_id)
            
            # Status counts
            for status in ContactStatus:
                stats[f"{status.value}_contacts"] = await self.count_by_status(business_id, status)
            
            # Type counts
            for contact_type in ContactType:
                stats[contact_type.value + "s"] = await self.count_by_type(business_id, contact_type)
            
            # Priority counts (simplified)
            for priority in ContactPriority:
                response = self.client.table(self.table_name).select(
                    "id", count="exact"
                ).eq("business_id", str(business_id)).eq(
                    "priority", priority.value
                ).execute()
                stats[f"{priority.value}_priority"] = response.count or 0
            
            # Additional statistics
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).not_.is_("email", "null").execute()
            stats["with_email"] = response.count or 0
            
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).or_(
                "phone.not.is.null,mobile_phone.not.is.null"
            ).execute()
            stats["with_phone"] = response.count or 0
            
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).not_.is_("assigned_to", "null").execute()
            stats["assigned_contacts"] = response.count or 0
            
            stats["unassigned_contacts"] = stats["total_contacts"] - stats["assigned_contacts"]
            
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).is_("last_contacted", "null").execute()
            stats["never_contacted"] = response.count or 0
            
            # Recently contacted (last 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).gte(
                "last_contacted", cutoff_date.isoformat()
            ).execute()
            stats["recently_contacted"] = response.count or 0
            
            # High value contacts (> $1000)
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).gte("estimated_value", 1000).execute()
            stats["high_value_contacts"] = response.count or 0
            
            # Financial statistics
            response = self.client.table(self.table_name).select(
                "estimated_value"
            ).eq("business_id", str(business_id)).not_.is_("estimated_value", "null").execute()
            
            values = [float(row["estimated_value"]) for row in response.data if row["estimated_value"]]
            stats["total_estimated_value"] = sum(values)
            stats["average_estimated_value"] = sum(values) / len(values) if values else 0.0
            
            return stats
            
        except Exception as e:
            raise DatabaseError(f"Failed to get contact statistics: {str(e)}")
    
    async def exists(self, contact_id: uuid.UUID) -> bool:
        """Check if a contact exists."""
        try:
            response = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("id", str(contact_id)).execute()
            
            return (response.count or 0) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check contact existence: {str(e)}")
    
    async def has_duplicate_email(self, business_id: uuid.UUID, email: str, 
                                exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if email already exists for another contact in the business."""
        try:
            query = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).eq("email", email)
            
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            
            response = query.execute()
            
            return (response.count or 0) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check duplicate email: {str(e)}")
    
    async def has_duplicate_phone(self, business_id: uuid.UUID, phone: str,
                                exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if phone already exists for another contact in the business."""
        try:
            query = self.client.table(self.table_name).select(
                "id", count="exact"
            ).eq("business_id", str(business_id)).or_(f"phone.eq.{phone},mobile_phone.eq.{phone}")
            
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            
            response = query.execute()
            
            return (response.count or 0) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check duplicate phone: {str(e)}")
    
    # Helper methods
    
    def _contact_to_dict(self, contact: Contact) -> Dict[str, Any]:
        """Convert Contact entity to dictionary for database storage."""
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