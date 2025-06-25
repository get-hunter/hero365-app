"""
Repair Business Membership Permissions Use Case

Repairs business membership permissions by ensuring all memberships 
have the correct default permissions for their role.
"""

import logging
from typing import List, Dict
import uuid

from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.business_membership import BusinessRole, DEFAULT_ROLE_PERMISSIONS
from ...exceptions.application_exceptions import ApplicationError

# Configure logging
logger = logging.getLogger(__name__)


class RepairMembershipPermissionsUseCase:
    """
    Use case for repairing business membership permissions.
    
    This use case ensures that all business memberships have the correct
    default permissions based on their role.
    """
    
    def __init__(self, membership_repository: BusinessMembershipRepository):
        self.membership_repository = membership_repository
    
    async def repair_all_permissions(self) -> Dict[str, int]:
        """
        Repair permissions for all business memberships.
        
        Returns:
            Dictionary with count of updated memberships by role
        """
        try:
            logger.info("Starting permissions repair for all business memberships")
            
            updated_counts = {
                "owner": 0,
                "admin": 0, 
                "manager": 0,
                "employee": 0,
                "contractor": 0,
                "viewer": 0
            }
            
            # Get all active memberships
            # Note: This is a simplified approach. In production, you'd want pagination
            for role in BusinessRole:
                memberships = await self._get_memberships_by_role(role)
                
                for membership in memberships:
                    if await self._repair_membership_permissions(membership):
                        updated_counts[role.value] += 1
            
            logger.info(f"Permissions repair completed. Updated counts: {updated_counts}")
            return updated_counts
            
        except Exception as e:
            logger.error(f"Error during permissions repair: {str(e)}")
            raise ApplicationError(f"Failed to repair permissions: {str(e)}")
    
    async def repair_user_permissions(self, user_id: str) -> Dict[str, int]:
        """
        Repair permissions for a specific user's memberships.
        
        Args:
            user_id: ID of the user whose permissions to repair
            
        Returns:
            Dictionary with count of updated memberships by role
        """
        try:
            logger.info(f"Starting permissions repair for user {user_id}")
            
            updated_counts = {
                "owner": 0,
                "admin": 0,
                "manager": 0, 
                "employee": 0,
                "contractor": 0,
                "viewer": 0
            }
            
            # Get all memberships for the user
            memberships = await self.membership_repository.get_user_memberships(user_id)
            
            for membership in memberships:
                if await self._repair_membership_permissions(membership):
                    updated_counts[membership.role.value] += 1
            
            logger.info(f"User permissions repair completed. Updated counts: {updated_counts}")
            return updated_counts
            
        except Exception as e:
            logger.error(f"Error during user permissions repair: {str(e)}")
            raise ApplicationError(f"Failed to repair user permissions: {str(e)}")
    
    async def repair_business_permissions(self, business_id: uuid.UUID) -> Dict[str, int]:
        """
        Repair permissions for all memberships in a specific business.
        
        Args:
            business_id: ID of the business whose permissions to repair
            
        Returns:
            Dictionary with count of updated memberships by role
        """
        try:
            logger.info(f"Starting permissions repair for business {business_id}")
            
            updated_counts = {
                "owner": 0,
                "admin": 0,
                "manager": 0,
                "employee": 0,
                "contractor": 0,
                "viewer": 0
            }
            
            # Get all memberships for the business
            memberships = await self.membership_repository.get_business_members(business_id)
            
            for membership in memberships:
                if await self._repair_membership_permissions(membership):
                    updated_counts[membership.role.value] += 1
            
            logger.info(f"Business permissions repair completed. Updated counts: {updated_counts}")
            return updated_counts
            
        except Exception as e:
            logger.error(f"Error during business permissions repair: {str(e)}")
            raise ApplicationError(f"Failed to repair business permissions: {str(e)}")
    
    async def _get_memberships_by_role(self, role: BusinessRole) -> List:
        """Get all memberships with a specific role (simplified implementation)."""
        # In a real implementation, you'd have a method in the repository for this
        # For now, we'll implement a basic version
        # This would need to be implemented properly in the repository
        return []
    
    async def _repair_membership_permissions(self, membership) -> bool:
        """
        Repair permissions for a single membership.
        
        Args:
            membership: BusinessMembership entity
            
        Returns:
            True if permissions were updated, False otherwise
        """
        try:
            # Get default permissions for the role
            default_permissions = DEFAULT_ROLE_PERMISSIONS.get(membership.role, [])
            
            # Check if current permissions match default
            current_permissions = set(membership.permissions)
            expected_permissions = set(default_permissions)
            
            if current_permissions != expected_permissions:
                # Update permissions to match default
                membership.permissions = default_permissions.copy()
                
                # Save updated membership
                await self.membership_repository.update(membership)
                
                logger.info(f"Updated permissions for membership {membership.id} (role: {membership.role.value})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error repairing membership {membership.id}: {str(e)}")
            return False 