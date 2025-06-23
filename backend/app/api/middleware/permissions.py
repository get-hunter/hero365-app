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


def require_permission(
    permission: Union[BusinessPermission, str, List[Union[BusinessPermission, str]]]
) -> Callable:
    """
    Decorator to enforce permission requirements on API endpoints.
    
    Args:
        permission: Single permission or list of permissions required.
                   Can be BusinessPermission enum or string values.
    
    Returns:
        Decorator function
        
    Usage:
        @require_permission(BusinessPermission.VIEW_CONTACTS)
        async def get_contacts(...):
            pass
            
        @require_permission([BusinessPermission.EDIT_CONTACTS, BusinessPermission.CREATE_CONTACTS])
        async def update_contact(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract request from function arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Extract request from kwargs if not found in args
            if not request:
                request = kwargs.get('request')
            
            if not request:
                logger.error("No request object found in function arguments")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error: Request object not found"
                )
            
            # Get authenticated user
            user = getattr(request.state, 'user', None)
            if not user:
                logger.warning("No authenticated user found in request state")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get business context
            business_id = getattr(request.state, 'business_id', None)
            if not business_id:
                # Try to extract from path parameters or kwargs
                business_id = request.path_params.get('business_id')
                if not business_id:
                    business_id = kwargs.get('business_id')
            
            if not business_id:
                logger.warning("No business context found for permission check")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Business context required for this operation"
                )
            
            # Normalize permissions to list of strings
            required_permissions = normalize_permissions(permission)
            
            # Check if user has required permissions
            user_id = user.get('id') or user.get('sub')
            has_permission = await check_user_business_permissions(
                user_id, business_id, required_permissions
            )
            
            if not has_permission:
                logger.warning(
                    f"User {user_id} lacks required permissions {required_permissions} "
                    f"for business {business_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {', '.join(required_permissions)} required"
                )
            
            # Permission check passed, execute the function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


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
        # Get user's business memberships
        business_memberships = await auth_facade._get_user_business_memberships(user_id)
        
        if not business_memberships:
            logger.debug(f"User {user_id} has no business memberships")
            return False
        
        # Find membership for the specific business
        current_membership = None
        for membership in business_memberships:
            if membership["business_id"] == business_id:
                current_membership = membership
                break
        
        if not current_membership:
            logger.debug(f"User {user_id} is not a member of business {business_id}")
            return False
        
        # Check if user has all required permissions
        user_permissions = current_membership.get("permissions", [])
        
        # Check each required permission
        for required_permission in required_permissions:
            if required_permission not in user_permissions:
                logger.debug(
                    f"User {user_id} missing permission '{required_permission}' "
                    f"for business {business_id}"
                )
                return False
        
        logger.debug(
            f"User {user_id} has all required permissions {required_permissions} "
            f"for business {business_id}"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error checking user business permissions: {str(e)}")
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


def require_any_permission(*permissions: Union[BusinessPermission, str]) -> Callable:
    """
    Decorator to enforce that user has ANY of the specified permissions.
    
    Args:
        *permissions: Variable number of permissions (user needs any one of them)
        
    Returns:
        Decorator function
    """
    async def permission_checker(user_id: str, business_id: str) -> bool:
        required_permissions = normalize_permissions(list(permissions))
        
        try:
            # Get user's business memberships
            business_memberships = await auth_facade._get_user_business_memberships(user_id)
            
            if not business_memberships:
                return False
            
            # Find membership for the specific business
            current_membership = None
            for membership in business_memberships:
                if membership["business_id"] == business_id:
                    current_membership = membership
                    break
            
            if not current_membership:
                return False
            
            # Check if user has any of the required permissions
            user_permissions = current_membership.get("permissions", [])
            
            for required_permission in required_permissions:
                if required_permission in user_permissions:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking any permission: {str(e)}")
            return False
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract request and business context
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error: Request object not found"
                )
            
            user = getattr(request.state, 'user', None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            business_id = getattr(request.state, 'business_id', None)
            if not business_id:
                business_id = request.path_params.get('business_id') or kwargs.get('business_id')
            
            if not business_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Business context required for this operation"
                )
            
            user_id = user.get('id') or user.get('sub')
            has_permission = await permission_checker(user_id, business_id)
            
            if not has_permission:
                required_permissions = normalize_permissions(list(permissions))
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: any of {', '.join(required_permissions)} required"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Convenience decorators for common permissions
def require_view_contacts(func: Callable) -> Callable:
    """Decorator to require VIEW_CONTACTS permission."""
    return require_permission(BusinessPermission.VIEW_CONTACTS)(func)


def require_edit_contacts(func: Callable) -> Callable:
    """Decorator to require EDIT_CONTACTS permission."""
    return require_permission(BusinessPermission.EDIT_CONTACTS)(func)


def require_create_contacts(func: Callable) -> Callable:
    """Decorator to require CREATE_CONTACTS permission."""
    return require_permission(BusinessPermission.CREATE_CONTACTS)(func)


def require_delete_contacts(func: Callable) -> Callable:
    """Decorator to require DELETE_CONTACTS permission."""
    return require_permission(BusinessPermission.DELETE_CONTACTS)(func)


def require_contact_management(func: Callable) -> Callable:
    """Decorator to require any contact management permission."""
    return require_any_permission(
        BusinessPermission.VIEW_CONTACTS,
        BusinessPermission.CREATE_CONTACTS,
        BusinessPermission.EDIT_CONTACTS,
        BusinessPermission.DELETE_CONTACTS
    )(func) 