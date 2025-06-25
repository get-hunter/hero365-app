"""
Business Permission Middleware and Decorators

Provides decorators and utilities for enforcing business permissions on API endpoints.
"""

import logging
from functools import wraps
from typing import List, Union, Callable, Any, Dict
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...domain.entities.business_membership import BusinessPermission
from ...core.auth_facade import auth_facade
from ...infrastructure.config.dependency_injection import get_container

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def create_permission_dependency(required_permissions: List[str]):
    """
    Create a FastAPI dependency that checks for required permissions.
    
    Args:
        required_permissions: List of permissions required
        
    Returns:
        Dependency function
    """
    async def check_permissions(request: Request) -> bool:
        logger.info(f"🔐 PermissionCheck: Checking permissions {required_permissions} for {request.method} {request.url.path}")
        
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, 'user', None)
        if not user:
            logger.warning("🔐 PermissionCheck: No user found in request state")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        user_id = user.get('id') or user.get('sub')
        logger.info(f"🔐 PermissionCheck: User {user_id} attempting access")
        
        # Get business context from request state (set by business context middleware)
        business_context_id = getattr(request.state, 'business_id', None)
        if not business_context_id:
            logger.warning("🔐 PermissionCheck: No business context found in request state")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business context required for this operation"
            )
        
        logger.info(f"🔐 PermissionCheck: Business context: {business_context_id}")
        
        # Check if user has required permissions
        has_permission = await check_user_business_permissions(
            user_id, str(business_context_id), required_permissions
        )
        
        if not has_permission:
            logger.warning(
                f"🔐 PermissionCheck: User {user_id} lacks required permissions {required_permissions} "
                f"for business {business_context_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {', '.join(required_permissions)} required"
            )
        
        logger.info(f"🔐 PermissionCheck: User {user_id} has required permissions {required_permissions}")
        return True
    
    return check_permissions


def normalize_permissions(
    permission: Union[BusinessPermission, str, List[Union[BusinessPermission, str]]]
) -> List[str]:
    """
    Normalize permission input to a list of permission strings.
    
    Args:
        permission: Single permission or list of permissions
        
    Returns:
        List of permission strings
    """
    if isinstance(permission, list):
        normalized = []
        for p in permission:
            if isinstance(p, BusinessPermission):
                normalized.append(p.value)
            else:
                normalized.append(str(p))
        return normalized
    elif isinstance(permission, BusinessPermission):
        return [permission.value]
    else:
        return [str(permission)]


async def check_user_business_permissions(
    user_id: str, 
    business_id: str, 
    required_permissions: List[str]
) -> bool:
    """
    Check if user has all required permissions for a business.
    
    Args:
        user_id: User ID
        business_id: Business ID 
        required_permissions: List of required permission strings
        
    Returns:
        True if user has all permissions, False otherwise
    """
    try:
        logger.info(f"🔍 PermissionCheck: Checking {required_permissions} for user {user_id} in business {business_id}")
        
        # Get user's business memberships
        business_memberships = await auth_facade._get_user_business_memberships(user_id)
        
        if not business_memberships:
            logger.warning(f"🔍 PermissionCheck: User {user_id} has no business memberships")
            return False
        
        logger.info(f"🔍 PermissionCheck: User {user_id} has {len(business_memberships)} business memberships")
        
        # Find membership for the specific business
        current_membership = None
        for membership in business_memberships:
            logger.info(f"🔍 PermissionCheck: Checking membership for business {membership['business_id']}")
            if membership["business_id"] == business_id:
                current_membership = membership
                break
        
        if not current_membership:
            logger.warning(f"🔍 PermissionCheck: User {user_id} is not a member of business {business_id}")
            return False
        
        # Check if user has all required permissions
        user_permissions = current_membership.get("permissions", [])
        logger.info(f"🔍 PermissionCheck: User {user_id} has permissions: {user_permissions}")
        logger.info(f"🔍 PermissionCheck: User {user_id} role: {current_membership.get('role')}")
        
        # Special case: if user has "*" permission (owner), they have all permissions
        if "*" in user_permissions:
            logger.info(f"🔍 PermissionCheck: User {user_id} has wildcard permissions (owner) for business {business_id}")
            return True
        
        # Check each required permission
        for required_permission in required_permissions:
            if required_permission not in user_permissions:
                logger.warning(
                    f"🔍 PermissionCheck: User {user_id} missing permission '{required_permission}' "
                    f"for business {business_id}. Has: {user_permissions}"
                )
                return False
        
        logger.info(
            f"🔍 PermissionCheck: User {user_id} has all required permissions {required_permissions} "
            f"for business {business_id}"
        )
        return True
        
    except Exception as e:
        logger.error(f"🔍 PermissionCheck: Error checking user business permissions: {str(e)}")
        return False


async def get_user_business_permissions(
    user_id: str, 
    business_id: str
) -> Dict[str, Any]:
    """
    Get user's permissions and role information for a business.
    
    Args:
        user_id: User ID
        business_id: Business ID
        
    Returns:
        Dictionary with user's role and permissions
    """
    try:
        # Get user's business memberships
        business_memberships = await auth_facade._get_user_business_memberships(user_id)
        
        if not business_memberships:
            return {
                "has_access": False,
                "role": None,
                "permissions": [],
                "role_level": 0
            }
        
        # Find membership for the specific business
        current_membership = None
        for membership in business_memberships:
            if membership["business_id"] == business_id:
                current_membership = membership
                break
        
        if not current_membership:
            return {
                "has_access": False,
                "role": None,
                "permissions": [],
                "role_level": 0
            }
        
        return {
            "has_access": True,
            "role": current_membership.get("role"),
            "permissions": current_membership.get("permissions", []),
            "role_level": current_membership.get("role_level", 0)
        }
        
    except Exception as e:
        logger.error(f"Error getting user business permissions: {str(e)}")
        return {
            "has_access": False,
            "role": None,
            "permissions": [],
            "role_level": 0,
            "error": str(e)
        }


# Create permission dependency functions
require_view_contacts_dep = create_permission_dependency([BusinessPermission.VIEW_CONTACTS.value])
require_edit_contacts_dep = create_permission_dependency([BusinessPermission.EDIT_CONTACTS.value])
require_create_contacts_dep = create_permission_dependency([BusinessPermission.CREATE_CONTACTS.value])
require_delete_contacts_dep = create_permission_dependency([BusinessPermission.DELETE_CONTACTS.value])


# Keep the old decorator functions for backward compatibility but make them no-ops
def require_view_contacts(func: Callable) -> Callable:
    """Decorator to require VIEW_CONTACTS permission. (Deprecated - use dependencies instead)"""
    return func


def require_edit_contacts(func: Callable) -> Callable:
    """Decorator to require EDIT_CONTACTS permission. (Deprecated - use dependencies instead)"""
    return func


def require_create_contacts(func: Callable) -> Callable:
    """Decorator to require CREATE_CONTACTS permission. (Deprecated - use dependencies instead)"""
    return func


def require_delete_contacts(func: Callable) -> Callable:
    """Decorator to require DELETE_CONTACTS permission. (Deprecated - use dependencies instead)"""
    return func


def require_contact_management(func: Callable) -> Callable:
    """Decorator to require any contact management permission. (Deprecated - use dependencies instead)"""
    return func 