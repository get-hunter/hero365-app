"""
Supabase Customer Membership Repository Implementation

Implements the CustomerMembershipRepository interface using Supabase as the data store.
"""

import uuid
import logging
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from supabase import Client

from ....domain.entities.customer_membership import (
    CustomerMembershipPlan, 
    CustomerMembership, 
    MembershipPlanType,
    MembershipStatus
)
from ....domain.repositories.customer_membership_repository import CustomerMembershipRepository
from ....domain.exceptions.domain_exceptions import (
    EntityNotFoundError, 
    DuplicateEntityError, 
    BusinessRuleViolationError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class SupabaseMembershipRepository(CustomerMembershipRepository):
    """
    Supabase implementation of CustomerMembershipRepository.
    
    Handles all database operations for customer membership plans and subscriptions
    using Supabase as the backend data store.
    """
    
    def __init__(self, supabase_client: Optional[Client] = None):
        if supabase_client:
            self.client = supabase_client
        else:
            from ....core.db import get_supabase_client
            self.client = get_supabase_client()
    
    # CustomerMembershipPlan operations
    async def create_plan(self, plan: CustomerMembershipPlan) -> CustomerMembershipPlan:
        """Create a new membership plan."""
        try:
            plan_data = {
                "id": str(plan.id),
                "business_id": str(plan.business_id),
                "name": plan.name,
                "plan_type": plan.plan_type.value,
                "description": plan.description,
                "tagline": plan.tagline,
                "price_monthly": float(plan.price_monthly),
                "price_yearly": float(plan.price_yearly),
                "setup_fee": float(plan.setup_fee),
                "discount_percentage": plan.discount_percentage,
                "priority_service": plan.priority_service,
                "extended_warranty": plan.extended_warranty,
                "maintenance_included": plan.maintenance_included,
                "emergency_response": plan.emergency_response,
                "free_diagnostics": plan.free_diagnostics,
                "annual_tune_ups": plan.annual_tune_ups,
                "is_active": plan.is_active,
                "is_featured": plan.is_featured,
                "popular_badge": plan.popular_badge,
                "color_scheme": plan.color_scheme,
                "sort_order": plan.sort_order,
                "contract_length_months": plan.contract_length_months,
                "cancellation_policy": plan.cancellation_policy,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat()
            }
            
            result = self.client.table("customer_membership_plans").insert(plan_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create membership plan")
            
            created_data = result.data[0]
            return self._map_plan_from_db(created_data)
            
        except Exception as e:
            logger.error(f"Error creating membership plan: {str(e)}")
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError(f"Membership plan with name '{plan.name}' already exists")
            raise DatabaseError(f"Failed to create membership plan: {str(e)}")
    
    async def get_plan_by_id(self, plan_id: uuid.UUID) -> Optional[CustomerMembershipPlan]:
        """Get membership plan by ID."""
        try:
            result = self.client.table("customer_membership_plans").select("*").eq("id", str(plan_id)).execute()
            
            if not result.data:
                return None
            
            return self._map_plan_from_db(result.data[0])
            
        except Exception as e:
            logger.error(f"Error retrieving membership plan {plan_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve membership plan: {str(e)}")
    
    async def get_active_plans_by_business(
        self, 
        business_id: uuid.UUID,
        plan_type: Optional[MembershipPlanType] = None
    ) -> List[CustomerMembershipPlan]:
        """Get all active membership plans for a business."""
        try:
            query = self.client.table("customer_membership_plans").select("*").eq("business_id", str(business_id)).eq("is_active", True)
            
            if plan_type:
                query = query.eq("plan_type", plan_type.value)
            
            result = query.order("sort_order").execute()
            
            plans = []
            for plan_data in result.data:
                plans.append(self._map_plan_from_db(plan_data))
            
            return plans
            
        except Exception as e:
            logger.error(f"Error retrieving membership plans for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve membership plans: {str(e)}")
    
    async def update_plan(self, plan: CustomerMembershipPlan) -> CustomerMembershipPlan:
        """Update an existing membership plan."""
        try:
            plan_data = {
                "name": plan.name,
                "plan_type": plan.plan_type.value,
                "description": plan.description,
                "tagline": plan.tagline,
                "price_monthly": float(plan.price_monthly),
                "price_yearly": float(plan.price_yearly),
                "setup_fee": float(plan.setup_fee),
                "discount_percentage": plan.discount_percentage,
                "priority_service": plan.priority_service,
                "extended_warranty": plan.extended_warranty,
                "maintenance_included": plan.maintenance_included,
                "emergency_response": plan.emergency_response,
                "free_diagnostics": plan.free_diagnostics,
                "annual_tune_ups": plan.annual_tune_ups,
                "is_active": plan.is_active,
                "is_featured": plan.is_featured,
                "popular_badge": plan.popular_badge,
                "color_scheme": plan.color_scheme,
                "sort_order": plan.sort_order,
                "contract_length_months": plan.contract_length_months,
                "cancellation_policy": plan.cancellation_policy,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.client.table("customer_membership_plans").update(plan_data).eq("id", str(plan.id)).execute()
            
            if not result.data:
                raise EntityNotFoundError(f"Membership plan not found: {plan.id}")
            
            return self._map_plan_from_db(result.data[0])
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating membership plan {plan.id}: {str(e)}")
            raise DatabaseError(f"Failed to update membership plan: {str(e)}")
    
    async def delete_plan(self, plan_id: uuid.UUID) -> bool:
        """Delete a membership plan."""
        try:
            # Check for active subscriptions
            subscriptions = self.client.table("customer_memberships").select("id").eq("plan_id", str(plan_id)).eq("status", "active").execute()
            
            if subscriptions.data:
                raise BusinessRuleViolationError("Cannot delete plan with active subscriptions")
            
            result = self.client.table("customer_membership_plans").delete().eq("id", str(plan_id)).execute()
            
            return len(result.data) > 0
            
        except BusinessRuleViolationError:
            raise
        except Exception as e:
            logger.error(f"Error deleting membership plan {plan_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete membership plan: {str(e)}")
    
    # CustomerMembership operations
    async def create_membership(self, membership: CustomerMembership) -> CustomerMembership:
        """Create a new customer membership subscription."""
        try:
            membership_data = {
                "id": str(membership.id),
                "business_id": str(membership.business_id),
                "customer_id": str(membership.customer_id),
                "plan_id": str(membership.plan_id),
                "status": membership.status.value,
                "start_date": membership.start_date.isoformat(),
                "end_date": membership.end_date.isoformat() if membership.end_date else None,
                "next_billing_date": membership.next_billing_date.isoformat(),
                "billing_cycle": membership.billing_cycle,
                "locked_monthly_price": float(membership.locked_monthly_price),
                "locked_yearly_price": float(membership.locked_yearly_price),
                "locked_discount_percentage": membership.locked_discount_percentage,
                "auto_renew": membership.auto_renew,
                "payment_method_id": membership.payment_method_id,
                "last_payment_date": membership.last_payment_date.isoformat() if membership.last_payment_date else None,
                "next_payment_amount": float(membership.next_payment_amount),
                "services_used_this_period": membership.services_used_this_period,
                "total_savings_to_date": float(membership.total_savings_to_date),
                "created_at": membership.created_at.isoformat(),
                "updated_at": membership.updated_at.isoformat()
            }
            
            result = self.client.table("customer_memberships").insert(membership_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create customer membership")
            
            created_data = result.data[0]
            return self._map_membership_from_db(created_data)
            
        except Exception as e:
            logger.error(f"Error creating customer membership: {str(e)}")
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError("Customer already has active membership for this business")
            raise DatabaseError(f"Failed to create customer membership: {str(e)}")
    
    async def get_membership_by_id(self, membership_id: uuid.UUID) -> Optional[CustomerMembership]:
        """Get customer membership by ID."""
        try:
            result = self.client.table("customer_memberships").select("*").eq("id", str(membership_id)).execute()
            
            if not result.data:
                return None
            
            return self._map_membership_from_db(result.data[0])
            
        except Exception as e:
            logger.error(f"Error retrieving customer membership {membership_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve customer membership: {str(e)}")
    
    async def get_active_membership_by_customer(
        self, 
        business_id: uuid.UUID, 
        customer_id: uuid.UUID
    ) -> Optional[CustomerMembership]:
        """Get active membership for a customer in a business."""
        try:
            result = self.client.table("customer_memberships").select("*").eq("business_id", str(business_id)).eq("customer_id", str(customer_id)).eq("status", "active").execute()
            
            if not result.data:
                return None
            
            return self._map_membership_from_db(result.data[0])
            
        except Exception as e:
            logger.error(f"Error retrieving active membership for customer {customer_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve active membership: {str(e)}")
    
    async def get_memberships_by_business(
        self,
        business_id: uuid.UUID,
        status: Optional[MembershipStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CustomerMembership]:
        """Get customer memberships for a business."""
        try:
            query = self.client.table("customer_memberships").select("*").eq("business_id", str(business_id))
            
            if status:
                query = query.eq("status", status.value)
            
            result = query.range(offset, offset + limit - 1).execute()
            
            memberships = []
            for membership_data in result.data:
                memberships.append(self._map_membership_from_db(membership_data))
            
            return memberships
            
        except Exception as e:
            logger.error(f"Error retrieving memberships for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve memberships: {str(e)}")
    
    async def get_memberships_due_for_renewal(
        self,
        business_id: Optional[uuid.UUID] = None,
        days_ahead: int = 7
    ) -> List[CustomerMembership]:
        """Get memberships that are due for renewal."""
        try:
            cutoff_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
            
            query = self.client.table("customer_memberships").select("*").eq("status", "active").eq("auto_renew", True).lte("next_billing_date", cutoff_date.isoformat())
            
            if business_id:
                query = query.eq("business_id", str(business_id))
            
            result = query.execute()
            
            memberships = []
            for membership_data in result.data:
                memberships.append(self._map_membership_from_db(membership_data))
            
            return memberships
            
        except Exception as e:
            logger.error(f"Error retrieving memberships due for renewal: {str(e)}")
            raise DatabaseError(f"Failed to retrieve memberships due for renewal: {str(e)}")
    
    async def update_membership(self, membership: CustomerMembership) -> CustomerMembership:
        """Update an existing customer membership."""
        try:
            membership_data = {
                "status": membership.status.value,
                "end_date": membership.end_date.isoformat() if membership.end_date else None,
                "next_billing_date": membership.next_billing_date.isoformat(),
                "billing_cycle": membership.billing_cycle,
                "auto_renew": membership.auto_renew,
                "payment_method_id": membership.payment_method_id,
                "last_payment_date": membership.last_payment_date.isoformat() if membership.last_payment_date else None,
                "next_payment_amount": float(membership.next_payment_amount),
                "services_used_this_period": membership.services_used_this_period,
                "total_savings_to_date": float(membership.total_savings_to_date),
                "updated_at": membership.updated_at.isoformat(),
                "cancelled_at": membership.cancelled_at.isoformat() if membership.cancelled_at else None,
                "cancellation_reason": membership.cancellation_reason
            }
            
            result = self.client.table("customer_memberships").update(membership_data).eq("id", str(membership.id)).execute()
            
            if not result.data:
                raise EntityNotFoundError(f"Customer membership not found: {membership.id}")
            
            return self._map_membership_from_db(result.data[0])
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating customer membership {membership.id}: {str(e)}")
            raise DatabaseError(f"Failed to update customer membership: {str(e)}")
    
    async def cancel_membership(
        self, 
        membership_id: uuid.UUID, 
        reason: Optional[str] = None
    ) -> CustomerMembership:
        """Cancel a customer membership."""
        try:
            # Get current membership
            membership = await self.get_membership_by_id(membership_id)
            if not membership:
                raise EntityNotFoundError(f"Customer membership not found: {membership_id}")
            
            # Cancel using domain logic
            membership.cancel(reason)
            
            # Update in database
            return await self.update_membership(membership)
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error cancelling customer membership {membership_id}: {str(e)}")
            raise DatabaseError(f"Failed to cancel customer membership: {str(e)}")
    
    def _map_plan_from_db(self, data: dict) -> CustomerMembershipPlan:
        """Map database data to CustomerMembershipPlan entity."""
        return CustomerMembershipPlan(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            name=data["name"],
            plan_type=MembershipPlanType(data["plan_type"]),
            description=data["description"],
            tagline=data["tagline"],
            price_monthly=Decimal(str(data["price_monthly"])),
            price_yearly=Decimal(str(data["price_yearly"])),
            setup_fee=Decimal(str(data["setup_fee"])),
            discount_percentage=data["discount_percentage"],
            priority_service=data["priority_service"],
            extended_warranty=data["extended_warranty"],
            maintenance_included=data["maintenance_included"],
            emergency_response=data["emergency_response"],
            free_diagnostics=data["free_diagnostics"],
            annual_tune_ups=data["annual_tune_ups"],
            is_active=data["is_active"],
            is_featured=data["is_featured"],
            popular_badge=data.get("popular_badge"),
            color_scheme=data["color_scheme"],
            sort_order=data["sort_order"],
            contract_length_months=data["contract_length_months"],
            cancellation_policy=data["cancellation_policy"],
            created_at=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        )
    
    def _map_membership_from_db(self, data: dict) -> CustomerMembership:
        """Map database data to CustomerMembership entity."""
        return CustomerMembership(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            customer_id=uuid.UUID(data["customer_id"]),
            plan_id=uuid.UUID(data["plan_id"]),
            status=MembershipStatus(data["status"]),
            start_date=datetime.fromisoformat(data["start_date"].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data["end_date"].replace('Z', '+00:00')) if data.get("end_date") else None,
            next_billing_date=datetime.fromisoformat(data["next_billing_date"].replace('Z', '+00:00')),
            billing_cycle=data["billing_cycle"],
            locked_monthly_price=Decimal(str(data["locked_monthly_price"])),
            locked_yearly_price=Decimal(str(data["locked_yearly_price"])),
            locked_discount_percentage=data["locked_discount_percentage"],
            auto_renew=data["auto_renew"],
            payment_method_id=data.get("payment_method_id"),
            last_payment_date=datetime.fromisoformat(data["last_payment_date"].replace('Z', '+00:00')) if data.get("last_payment_date") else None,
            next_payment_amount=Decimal(str(data["next_payment_amount"])),
            services_used_this_period=data["services_used_this_period"],
            total_savings_to_date=Decimal(str(data["total_savings_to_date"])),
            created_at=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00')),
            cancelled_at=datetime.fromisoformat(data["cancelled_at"].replace('Z', '+00:00')) if data.get("cancelled_at") else None,
            cancellation_reason=data.get("cancellation_reason")
        )
