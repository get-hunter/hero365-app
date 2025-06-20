"""
Delete User Use Case

Business logic for deleting users.
"""

import uuid
from typing import Optional

from ...exceptions.application_exceptions import (
    UserNotFoundError, PermissionDeniedError
)
from ....domain.exceptions.domain_exceptions import InvalidOperationError
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.repositories.item_repository import ItemRepository


class DeleteUserUseCase:
    """
    Use case for deleting users.
    
    This use case handles the business logic for user deletion,
    including permission checks and cascading operations.
    """
    
    def __init__(self, user_repository: UserRepository, item_repository: ItemRepository):
        self.user_repository = user_repository
        self.item_repository = item_repository
    
    async def execute(self, user_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                     is_superuser: bool = False, hard_delete: bool = False) -> bool:
        """
        Execute the delete user use case.
        
        Args:
            user_id: ID of the user to delete
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            hard_delete: Whether to permanently delete or just deactivate
            
        Returns:
            True if user was deleted successfully
            
        Raises:
            UserNotFoundError: If user doesn't exist
            PermissionDeniedError: If user lacks permission
            InvalidOperationError: If deletion is not allowed
        """
        # Get user to delete
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        # Check permissions
        if not self._can_delete_user(user, requesting_user_id, is_superuser):
            raise PermissionDeniedError("delete_user", str(user_id))
        
        # Validate deletion
        await self._validate_deletion(user, hard_delete)
        
        if hard_delete:
            # Permanently delete user and all associated data
            await self._hard_delete_user(user)
        else:
            # Soft delete - just deactivate the user
            await self._soft_delete_user(user)
        
        return True
    
    async def restore_user(self, user_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                          is_superuser: bool = False) -> bool:
        """
        Restore a deactivated user.
        
        Args:
            user_id: ID of the user to restore
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            True if user was restored successfully
            
        Raises:
            UserNotFoundError: If user doesn't exist
            PermissionDeniedError: If user lacks permission
            InvalidOperationError: If user is not deactivated
        """
        # Only superusers can restore users
        if not is_superuser:
            raise PermissionDeniedError("restore_user")
        
        # Get user to restore
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        # Check if user is actually deactivated
        if user.is_active:
            raise InvalidOperationError("restore_user", "User is already active")
        
        # Restore user
        user.activate()
        await self.user_repository.update(user)
        
        return True
    
    async def _validate_deletion(self, user: User, hard_delete: bool) -> None:
        """
        Validate if the user can be deleted.
        
        Args:
            user: User to delete
            hard_delete: Whether it's a hard delete
            
        Raises:
            InvalidOperationError: If deletion is not allowed
        """
        # Check if user is the last superuser
        if user.is_superuser:
            superuser_count = await self.user_repository.count_superusers()
            if superuser_count <= 1:
                raise InvalidOperationError(
                    "delete_user", 
                    "Cannot delete the last superuser account"
                )
        
        # For hard delete, warn about data loss
        if hard_delete:
            # Check if user has items
            item_count = await self.item_repository.count_by_owner_id(user.id)
            if item_count > 0:
                # In a real application, you might want to require explicit confirmation
                # or transfer ownership of items before deletion
                pass
    
    async def _soft_delete_user(self, user: User) -> None:
        """
        Soft delete user by deactivating the account.
        
        Args:
            user: User to soft delete
        """
        # Deactivate user account
        user.deactivate()
        
        # Update in repository
        await self.user_repository.update(user)
        
        # Optionally, soft delete user's items as well
        await self.item_repository.bulk_delete_by_owner_id(user.id)
    
    async def _hard_delete_user(self, user: User) -> None:
        """
        Permanently delete user and all associated data.
        
        Args:
            user: User to hard delete
        """
        # Delete all user's items first
        await self.item_repository.permanently_delete_by_owner_id(user.id)
        
        # Delete the user
        await self.user_repository.delete(user.id)
    
    def _can_delete_user(self, user: User, requesting_user_id: Optional[uuid.UUID],
                        is_superuser: bool) -> bool:
        """
        Check if the requesting user can delete the target user.
        
        Args:
            user: User to delete
            requesting_user_id: ID of requesting user
            is_superuser: Whether requesting user is superuser
            
        Returns:
            True if user can be deleted, False otherwise
        """
        # Only superusers can delete users (including themselves)
        if not is_superuser:
            return False
        
        # Users can delete themselves
        if requesting_user_id and user.id == requesting_user_id:
            return True
        
        # Superusers can delete other users
        return True 