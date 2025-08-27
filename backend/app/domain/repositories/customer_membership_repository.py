"""
Customer Membership Repository Interface

Defines the contract for customer membership data access operations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from ..entities.customer_membership import CustomerMembershipPlan, CustomerMembership, MembershipPlanType, MembershipStatus


class CustomerMembershipRepository(ABC):
    """
    Repository interface for CustomerMembershipPlan and CustomerMembership operations.
    
    This interface defines the contract for all customer membership data access operations,
    following the Repository pattern to abstract database implementation details.
    """
    
    # CustomerMembershipPlan operations
    @abstractmethod
    async def create_plan(self, plan: CustomerMembershipPlan) -> CustomerMembershipPlan:
        """
        Create a new membership plan.
        
        Args:
            plan: CustomerMembershipPlan entity to create
            
        Returns:
            Created plan entity with generated ID and timestamps
            
        Raises:
            DuplicateEntityError: If plan name already exists for business
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_plan_by_id(self, plan_id: uuid.UUID) -> Optional[CustomerMembershipPlan]:
        """
        Get membership plan by ID.
        
        Args:
            plan_id: Unique identifier of the plan
            
        Returns:
            CustomerMembershipPlan entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_active_plans_by_business(
        self, 
        business_id: uuid.UUID,
        plan_type: Optional[MembershipPlanType] = None
    ) -> List[CustomerMembershipPlan]:
        """
        Get all active membership plans for a business.
        
        Args:
            business_id: Business identifier
            plan_type: Optional filter by plan type
            
        Returns:
            List of active membership plans ordered by sort_order
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update_plan(self, plan: CustomerMembershipPlan) -> CustomerMembershipPlan:
        """
        Update an existing membership plan.
        
        Args:
            plan: CustomerMembershipPlan entity to update
            
        Returns:
            Updated plan entity
            
        Raises:
            EntityNotFoundError: If plan doesn't exist
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete_plan(self, plan_id: uuid.UUID) -> bool:
        """
        Delete a membership plan.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            True if deleted successfully
            
        Raises:
            EntityNotFoundError: If plan doesn't exist
            BusinessRuleViolationError: If plan has active subscriptions
            DatabaseError: If deletion fails
        """
        pass
    
    # CustomerMembership operations
    @abstractmethod
    async def create_membership(self, membership: CustomerMembership) -> CustomerMembership:
        """
        Create a new customer membership subscription.
        
        Args:
            membership: CustomerMembership entity to create
            
        Returns:
            Created membership entity with generated ID and timestamps
            
        Raises:
            DuplicateEntityError: If customer already has active membership for business
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_membership_by_id(self, membership_id: uuid.UUID) -> Optional[CustomerMembership]:
        """
        Get customer membership by ID.
        
        Args:
            membership_id: Unique identifier of the membership
            
        Returns:
            CustomerMembership entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_active_membership_by_customer(
        self, 
        business_id: uuid.UUID, 
        customer_id: uuid.UUID
    ) -> Optional[CustomerMembership]:
        """
        Get active membership for a customer in a business.
        
        Args:
            business_id: Business identifier
            customer_id: Customer identifier
            
        Returns:
            Active CustomerMembership entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_memberships_by_business(
        self,
        business_id: uuid.UUID,
        status: Optional[MembershipStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CustomerMembership]:
        """
        Get customer memberships for a business.
        
        Args:
            business_id: Business identifier
            status: Optional filter by membership status
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of customer memberships
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_memberships_due_for_renewal(
        self,
        business_id: Optional[uuid.UUID] = None,
        days_ahead: int = 7
    ) -> List[CustomerMembership]:
        """
        Get memberships that are due for renewal.
        
        Args:
            business_id: Optional business filter
            days_ahead: Number of days ahead to look for renewals
            
        Returns:
            List of memberships due for renewal
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update_membership(self, membership: CustomerMembership) -> CustomerMembership:
        """
        Update an existing customer membership.
        
        Args:
            membership: CustomerMembership entity to update
            
        Returns:
            Updated membership entity
            
        Raises:
            EntityNotFoundError: If membership doesn't exist
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def cancel_membership(
        self, 
        membership_id: uuid.UUID, 
        reason: Optional[str] = None
    ) -> CustomerMembership:
        """
        Cancel a customer membership.
        
        Args:
            membership_id: Membership identifier
            reason: Optional cancellation reason
            
        Returns:
            Updated membership entity with cancelled status
            
        Raises:
            EntityNotFoundError: If membership doesn't exist
            BusinessRuleViolationError: If membership is already cancelled
            DatabaseError: If update fails
        """
        pass
