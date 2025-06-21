"""
Supabase Business Repository Implementation

Repository implementation using Supabase client SDK for business management operations.
"""

import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
import json

from supabase import Client

from ....domain.repositories.business_repository import BusinessRepository
from ....domain.entities.business import Business, CompanySize, ReferralSource
from ....domain.entities.business_membership import BusinessMembership
from ....domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)


class SupabaseBusinessRepository(BusinessRepository):
    """
    Supabase client implementation of BusinessRepository.
    
    This repository uses Supabase client SDK for all business database operations,
    leveraging RLS, real-time features, and built-in auth integration.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "businesses"
    
    async def create(self, business: Business) -> Business:
        """Create a new business in Supabase."""
        try:
            business_data = self._business_to_dict(business)
            
            response = self.client.table(self.table_name).insert(business_data).execute()
            
            if response.data:
                return self._dict_to_business(response.data[0])
            else:
                raise DatabaseError("Failed to create business - no data returned")
                
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Business with name '{business.name}' already exists for this owner")
            raise DatabaseError(f"Failed to create business: {str(e)}")
    
    async def get_by_id(self, business_id: uuid.UUID) -> Optional[Business]:
        """Get business by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(business_id)).execute()
            
            if response.data:
                return self._dict_to_business(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get business by ID: {str(e)}")
    
    async def get_by_owner(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get businesses owned by a specific user."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "owner_id", owner_id
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_business(business_data) for business_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get businesses by owner: {str(e)}")
    
    async def get_user_businesses(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Tuple[Business, BusinessMembership]]:
        """Get all businesses where user is a member (owner or team member)."""
        try:
            # Query businesses through memberships using a join
            response = self.client.table("business_memberships").select(
                "*, businesses(*)"
            ).eq("user_id", user_id).eq("is_active", True).range(
                skip, skip + limit - 1
            ).order("joined_date", desc=True).execute()
            
            results = []
            for membership_data in response.data:
                business_data = membership_data.pop("businesses")
                business = self._dict_to_business(business_data)
                # Import here to avoid circular import
                from .supabase_business_membership_repository import SupabaseBusinessMembershipRepository
                membership_repo = SupabaseBusinessMembershipRepository(self.client)
                membership = membership_repo._dict_to_membership(membership_data)
                results.append((business, membership))
            
            return results
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user businesses: {str(e)}")
    
    async def update(self, business: Business) -> Business:
        """Update business in Supabase."""
        try:
            business_data = self._business_to_dict(business)
            business_data["last_modified"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(business_data).eq(
                "id", str(business.id)
            ).execute()
            
            if response.data:
                return self._dict_to_business(response.data[0])
            else:
                raise EntityNotFoundError(f"Business with ID {business.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Business name conflicts with existing business")
            raise DatabaseError(f"Failed to update business: {str(e)}")
    
    async def delete(self, business_id: uuid.UUID) -> bool:
        """Delete business from Supabase (soft delete)."""
        try:
            # Soft delete by setting is_active = False
            response = self.client.table(self.table_name).update({
                "is_active": False,
                "last_modified": datetime.utcnow().isoformat()
            }).eq("id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete business: {str(e)}")
    
    async def get_active_businesses(self, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get active businesses with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "is_active", True
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_business(business_data) for business_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active businesses: {str(e)}")
    
    async def search_businesses(self, query: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """Search businesses by name, industry, or description."""
        try:
            # Use Supabase text search with ilike for name, industry, and description
            response = self.client.table(self.table_name).select("*").or_(
                f"name.ilike.%{query}%,industry.ilike.%{query}%,description.ilike.%{query}%"
            ).eq("is_active", True).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_business(business_data) for business_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search businesses: {str(e)}")
    
    async def count(self) -> int:
        """Get total count of businesses."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count businesses: {str(e)}")
    
    async def count_active(self) -> int:
        """Get count of active businesses."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("is_active", True).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count active businesses: {str(e)}")
    
    async def count_by_owner(self, owner_id: str) -> int:
        """Get count of businesses owned by a specific user."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("owner_id", owner_id).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count businesses by owner: {str(e)}")
    
    async def exists(self, business_id: uuid.UUID) -> bool:
        """Check if a business exists."""
        try:
            response = self.client.table(self.table_name).select("id").eq("id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check business existence: {str(e)}")
    
    async def is_name_unique_for_owner(self, name: str, owner_id: str, exclude_business_id: Optional[uuid.UUID] = None) -> bool:
        """Check if business name is unique for a specific owner."""
        try:
            query = self.client.table(self.table_name).select("id").eq("name", name).eq("owner_id", owner_id)
            
            if exclude_business_id:
                query = query.neq("id", str(exclude_business_id))
            
            response = query.execute()
            
            return len(response.data) == 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check name uniqueness: {str(e)}")
    
    async def get_by_industry(self, industry: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get businesses by industry."""
        try:
            response = self.client.table(self.table_name).select("*").eq("industry", industry).eq(
                "is_active", True
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_business(business_data) for business_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get businesses by industry: {str(e)}")
    
    async def get_recent_businesses(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get recently created businesses."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            response = self.client.table(self.table_name).select("*").gte(
                "created_date", cutoff_date.isoformat()
            ).eq("is_active", True).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_business(business_data) for business_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get recent businesses: {str(e)}")
    
    def _business_to_dict(self, business: Business) -> dict:
        """Convert Business entity to dictionary for Supabase."""
        return {
            "id": str(business.id),
            "name": business.name,
            "industry": business.industry,
            "custom_industry": business.custom_industry,
            "company_size": business.company_size.value,
            "owner_id": business.owner_id,
            "description": business.description,
            "phone_number": business.phone_number,
            "business_address": business.business_address,
            "website": business.website,
            "logo_url": business.logo_url,
            "business_email": business.business_email,
            "business_registration_number": business.business_registration_number,
            "tax_id": business.tax_id,
            "business_license": business.business_license,
            "insurance_number": business.insurance_number,
            "selected_features": json.dumps(business.selected_features),
            "primary_goals": json.dumps(business.primary_goals),
            "referral_source": business.referral_source.value if business.referral_source else None,
            "onboarding_completed": business.onboarding_completed,
            "onboarding_completed_date": business.onboarding_completed_date.isoformat() if business.onboarding_completed_date else None,
            "timezone": business.timezone,
            "currency": business.currency,
            "business_hours": json.dumps(business.business_hours) if business.business_hours else None,
            "is_active": business.is_active,
            "max_team_members": business.max_team_members,
            "subscription_tier": business.subscription_tier,
            "enabled_features": json.dumps(business.enabled_features),
            "created_date": business.created_date.isoformat() if business.created_date else None,
            "last_modified": business.last_modified.isoformat() if business.last_modified else None
        }
    
    def _dict_to_business(self, data: dict) -> Business:
        """Convert dictionary from Supabase to Business entity."""
        return Business(
            id=uuid.UUID(data["id"]),
            name=data["name"],
            industry=data["industry"],
            company_size=CompanySize(data["company_size"]),
            owner_id=data["owner_id"],
            custom_industry=data.get("custom_industry"),
            description=data.get("description"),
            phone_number=data.get("phone_number"),
            business_address=data.get("business_address"),
            website=data.get("website"),
            logo_url=data.get("logo_url"),
            business_email=data.get("business_email"),
            business_registration_number=data.get("business_registration_number"),
            tax_id=data.get("tax_id"),
            business_license=data.get("business_license"),
            insurance_number=data.get("insurance_number"),
            selected_features=json.loads(data.get("selected_features", "[]")),
            primary_goals=json.loads(data.get("primary_goals", "[]")),
            referral_source=ReferralSource(data["referral_source"]) if data.get("referral_source") else None,
            onboarding_completed=data.get("onboarding_completed", False),
            onboarding_completed_date=datetime.fromisoformat(data["onboarding_completed_date"]) if data.get("onboarding_completed_date") else None,
            timezone=data.get("timezone"),
            currency=data.get("currency", "USD"),
            business_hours=json.loads(data["business_hours"]) if data.get("business_hours") else None,
            is_active=data.get("is_active", True),
            max_team_members=data.get("max_team_members"),
            subscription_tier=data.get("subscription_tier"),
            enabled_features=json.loads(data.get("enabled_features", "[]")),
            created_date=datetime.fromisoformat(data["created_date"]) if data.get("created_date") else None,
            last_modified=datetime.fromisoformat(data["last_modified"]) if data.get("last_modified") else None
        ) 