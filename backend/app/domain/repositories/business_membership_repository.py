"""
Business Membership Repository Interface

Defines the contract for business membership data access operations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.business_membership import BusinessMembership, BusinessRole


class BusinessMembershipRepository(ABC):
    """
    Repository interface for BusinessMembership entity operations.
    
    This interface defines the contract for all business membership data access operations,
    following the Repository pattern to abstract database implementation details.
    """
    
    @abstractmethod
    async def create(self, membership: BusinessMembership) -> BusinessMembership:
        """
        Create a new business membership.
        
        Args:
            membership: BusinessMembership entity to create
            
        Returns:
            Created membership entity with generated ID and timestamps
            
        Raises:
            DuplicateEntityError: If user is already a member of the business
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, membership_id: uuid.UUID) -> Optional[BusinessMembership]:
        """
        Get business membership by ID.
        
        Args:
            membership_id: Unique identifier of the membership
            
        Returns:
            BusinessMembership entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_business_and_user(self, business_id: uuid.UUID, user_id: str) -> Optional[BusinessMembership]:
        """
        Get business membership by business ID and user ID.
        
        Args:
            business_id: ID of the business
            user_id: ID of the user
            
        Returns:
            BusinessMembership entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_user_and_business(self, user_id: str, business_id: uuid.UUID) -> Optional[BusinessMembership]:
        """
        Get business membership by user ID and business ID.
        
        Args:
            user_id: ID of the user
            business_id: ID of the business
            
        Returns:
            BusinessMembership entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_business_members(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """
        Get all members of a specific business.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessMembership entities for the business
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_user_memberships(self, user_id: str, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """
        Get all business memberships for a specific user.
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessMembership entities for the user
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_active_business_members(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """
        Get active members of a specific business.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of active BusinessMembership entities for the business
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_members_by_role(self, business_id: uuid.UUID, role: BusinessRole, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """
        Get business members by role.
        
        Args:
            business_id: ID of the business
            role: Role to filter by
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessMembership entities with the specified role
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_business_owner(self, business_id: uuid.UUID) -> Optional[BusinessMembership]:
        """
        Get the owner membership for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            BusinessMembership entity for the owner, None if not found
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, membership: BusinessMembership) -> BusinessMembership:
        """
        Update an existing business membership.
        
        Args:
            membership: BusinessMembership entity with updated information
            
        Returns:
            Updated membership entity
            
        Raises:
            EntityNotFoundError: If membership doesn't exist
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete(self, membership_id: uuid.UUID) -> bool:
        """
        Delete a business membership (hard delete).
        
        Args:
            membership_id: ID of the membership to delete
            
        Returns:
            True if membership was deleted, False if membership wasn't found
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def deactivate(self, membership_id: uuid.UUID) -> bool:
        """
        Deactivate a business membership (soft delete).
        
        Args:
            membership_id: ID of the membership to deactivate
            
        Returns:
            True if membership was deactivated, False if membership wasn't found
            
        Raises:
            DatabaseError: If deactivation fails
        """
        pass
    
    @abstractmethod
    async def count_business_members(self, business_id: uuid.UUID) -> int:
        """
        Get count of all members in a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Number of members in the business
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_active_business_members(self, business_id: uuid.UUID) -> int:
        """
        Get count of active members in a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Number of active members in the business
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_user_memberships(self, user_id: str) -> int:
        """
        Get count of business memberships for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of business memberships for the user
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def exists(self, membership_id: uuid.UUID) -> bool:
        """
        Check if a business membership exists.
        
        Args:
            membership_id: ID of the membership to check
            
        Returns:
            True if membership exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def user_is_member(self, business_id: uuid.UUID, user_id: str) -> bool:
        """
        Check if a user is a member of a business.
        
        Args:
            business_id: ID of the business
            user_id: ID of the user
            
        Returns:
            True if user is a member, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def user_is_active_member(self, business_id: uuid.UUID, user_id: str) -> bool:
        """
        Check if a user is an active member of a business.
        
        Args:
            business_id: ID of the business
            user_id: ID of the user
            
        Returns:
            True if user is an active member, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def get_members_with_permission(self, business_id: uuid.UUID, permission: str, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """
        Get business members who have a specific permission.
        
        Args:
            business_id: ID of the business
            permission: Permission to check for
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessMembership entities with the specified permission
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass 