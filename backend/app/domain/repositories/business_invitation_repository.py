"""
Business Invitation Repository Interface

Defines the contract for business invitation data access operations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from ..entities.business_invitation import BusinessInvitation, InvitationStatus, BusinessRole


class BusinessInvitationRepository(ABC):
    """
    Repository interface for BusinessInvitation entity operations.
    
    This interface defines the contract for all business invitation data access operations,
    following the Repository pattern to abstract database implementation details.
    """
    
    @abstractmethod
    async def create(self, invitation: BusinessInvitation) -> BusinessInvitation:
        """
        Create a new business invitation.
        
        Args:
            invitation: BusinessInvitation entity to create
            
        Returns:
            Created invitation entity with generated ID and timestamps
            
        Raises:
            DuplicateEntityError: If active invitation already exists for the recipient
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, invitation_id: uuid.UUID) -> Optional[BusinessInvitation]:
        """
        Get business invitation by ID.
        
        Args:
            invitation_id: Unique identifier of the invitation
            
        Returns:
            BusinessInvitation entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_business_invitations(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get all invitations for a specific business.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessInvitation entities for the business
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_pending_business_invitations(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get pending invitations for a specific business.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of pending BusinessInvitation entities for the business
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_user_invitations_by_email(self, email: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get all invitations for a user by email.
        
        Args:
            email: Email address of the user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessInvitation entities for the email
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_user_invitations_by_phone(self, phone: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get all invitations for a user by phone.
        
        Args:
            phone: Phone number of the user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessInvitation entities for the phone
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_pending_user_invitations_by_email(self, email: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get pending invitations for a user by email.
        
        Args:
            email: Email address of the user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of pending BusinessInvitation entities for the email
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_pending_user_invitations_by_phone(self, phone: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get pending invitations for a user by phone.
        
        Args:
            phone: Phone number of the user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of pending BusinessInvitation entities for the phone
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_invitations_by_status(self, status: InvitationStatus, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get invitations by status.
        
        Args:
            status: Invitation status to filter by
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of BusinessInvitation entities with the specified status
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_expired_invitations(self, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """
        Get expired invitations that haven't been marked as expired.
        
        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of expired BusinessInvitation entities
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, invitation: BusinessInvitation) -> BusinessInvitation:
        """
        Update an existing business invitation.
        
        Args:
            invitation: BusinessInvitation entity with updated information
            
        Returns:
            Updated invitation entity
            
        Raises:
            EntityNotFoundError: If invitation doesn't exist
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete(self, invitation_id: uuid.UUID) -> bool:
        """
        Delete a business invitation.
        
        Args:
            invitation_id: ID of the invitation to delete
            
        Returns:
            True if invitation was deleted, False if invitation wasn't found
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def count_business_invitations(self, business_id: uuid.UUID) -> int:
        """
        Get count of all invitations for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Number of invitations for the business
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_pending_business_invitations(self, business_id: uuid.UUID) -> int:
        """
        Get count of pending invitations for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Number of pending invitations for the business
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_user_invitations_by_email(self, email: str) -> int:
        """
        Get count of invitations for a user by email.
        
        Args:
            email: Email address of the user
            
        Returns:
            Number of invitations for the email
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_user_invitations_by_phone(self, phone: str) -> int:
        """
        Get count of invitations for a user by phone.
        
        Args:
            phone: Phone number of the user
            
        Returns:
            Number of invitations for the phone
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def exists(self, invitation_id: uuid.UUID) -> bool:
        """
        Check if a business invitation exists.
        
        Args:
            invitation_id: ID of the invitation to check
            
        Returns:
            True if invitation exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def has_pending_invitation(self, business_id: uuid.UUID, email: Optional[str] = None, phone: Optional[str] = None) -> bool:
        """
        Check if there's a pending invitation for a business and contact method.
        
        Args:
            business_id: ID of the business
            email: Email address to check (optional)
            phone: Phone number to check (optional)
            
        Returns:
            True if pending invitation exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def mark_expired_invitations(self) -> int:
        """
        Mark all expired pending invitations as expired.
        
        Returns:
            Number of invitations marked as expired
            
        Raises:
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def cleanup_expired_invitations(self, days_old: int = 30) -> int:
        """
        Delete expired invitations older than specified days.
        
        Args:
            days_old: Number of days old for cleanup (default 30)
            
        Returns:
            Number of invitations cleaned up
            
        Raises:
            DatabaseError: If cleanup fails
        """
        pass 