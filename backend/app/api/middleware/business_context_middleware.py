"""
Business Context Middleware

Middleware for validating business context and permissions in multi-tenant architecture.
"""

import logging
from typing import Optional, Dict, Any, Callable, List
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from ...core.auth_facade import auth_facade
from ...infrastructure.config.dependency_injection import get_container

# Configure logging
logger = logging.getLogger(__name__)


class BusinessContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for business context validation and permission checking.
    
    This middleware validates that users have access to the business context
    they're trying to access and enforces business-scoped permissions.
    """
    
    def __init__(self, app, skip_paths: list = None):
        """
        Initialize business context middleware.
        
        Args:
            app: FastAPI application
            skip_paths: List of paths to skip business context validation
        """
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/api/v1/auth/",
            "/api/v1/users/me",  # User profile doesn't require business context
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and validate business context."""
        path = request.url.path
        logger.info(f"BusinessContextMiddleware processing request: {request.method} {path}")
        
        # Skip business context validation for certain paths
        if self._should_skip_business_context(request):
            logger.info(f"Skipping business context validation for path: {path}")
            return await call_next(request)
        
        # Only validate business context for authenticated requests
        if not getattr(request.state, 'authenticated', False):
            logger.info("Request not authenticated, skipping business context validation")
            return await call_next(request)
        
        # Extract business context from request
        business_id = self._extract_business_id_from_request(request)
        logger.info(f"BusinessContextMiddleware: Extracted business_id: {business_id}")
        
        if business_id:
            # Validate business context
            is_valid = await self._validate_business_access(request, business_id)
            
            if not is_valid:
                logger.warning(f"User does not have access to business {business_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to business context"
                )
            
            # Add validated business context to request state
            request.state.business_id = business_id
            request.state.business_context_validated = True
            logger.info(f"Business context validated and set in request state for business {business_id}")
        else:
            logger.warning(f"No business context could be extracted for path: {path}")
        
        # Continue with request processing
        return await call_next(request)
    
    def _should_skip_business_context(self, request: Request) -> bool:
        """Check if business context validation should be skipped for this path."""
        path = request.url.path
        
        # Check exact matches and prefixes
        for skip_path in self.skip_paths:
            if path.startswith(skip_path):
                return True
        
        return False
    
    def _extract_business_id_from_request(self, request: Request) -> Optional[str]:
        """Extract business ID from request path parameters or headers."""
        # Try to extract from path parameters first
        path_params = request.path_params
        
        # Check common path parameter names
        business_id_keys = ["business_id", "businessId"]
        for key in business_id_keys:
            if key in path_params:
                try:
                    # Validate UUID format
                    uuid.UUID(path_params[key])
                    return path_params[key]
                except (ValueError, TypeError):
                    pass
        
        # Try to extract from query parameters
        query_params = request.query_params
        for key in business_id_keys:
            if key in query_params:
                try:
                    uuid.UUID(query_params[key])
                    return query_params[key]
                except (ValueError, TypeError):
                    pass
        
        # Try to extract from headers
        business_id = request.headers.get("X-Business-ID")
        if business_id:
            try:
                uuid.UUID(business_id)
                return business_id
            except (ValueError, TypeError):
                pass
        
        # Try to get from user's current business context
        user = getattr(request.state, 'user', {})
        current_business_id = user.get('current_business_id')
        if current_business_id:
            return current_business_id
        
        # Fallback: if user has business memberships but no current business context,
        # use the first one (similar to deps.py logic)
        business_memberships = user.get('business_memberships', [])
        if business_memberships:
            first_business_id = business_memberships[0].get("business_id")
            if first_business_id:
                try:
                    # Validate UUID format
                    uuid.UUID(first_business_id)
                    logger.info(f"BusinessContextMiddleware: Using first business membership as fallback context: {first_business_id}")
                    return first_business_id
                except (ValueError, TypeError):
                    pass
        
        return None
    
    async def _validate_business_access(self, request: Request, business_id: str) -> bool:
        """Validate that the user has access to the specified business."""
        try:
            user = getattr(request.state, 'user', {})
            user_id = user.get('id') or user.get('sub')
            
            if not user_id:
                return False
            
            # Check if user is a member of the business
            business_memberships = user.get('business_memberships', [])
            
            valid_business_ids = [membership["business_id"] for membership in business_memberships]
            
            # Normalize UUIDs to lowercase for case-insensitive comparison
            business_id_normalized = business_id.lower()
            valid_business_ids_normalized = [bid.lower() for bid in valid_business_ids]
            
            return business_id_normalized in valid_business_ids_normalized
            
        except Exception as e:
            logger.error(f"Error validating business access: {str(e)}")
            return False


class BusinessPermissionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for checking specific business permissions on endpoints.
    
    This middleware checks if the authenticated user has the required permissions
    for the business context they're accessing.
    """
    
    def __init__(self, app, permission_map: Dict[str, List[str]] = None):
        """
        Initialize business permission middleware.
        
        Args:
            app: FastAPI application
            permission_map: Dict mapping endpoint patterns to required permissions
        """
        super().__init__(app)
        self.permission_map = permission_map or {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and check business permissions."""
        # Skip if business context not validated
        if not getattr(request.state, 'business_context_validated', False):
            return await call_next(request)
        
        # Check if endpoint requires specific permissions
        required_permissions = self._get_required_permissions(request)
        
        if required_permissions:
            has_permission = await self._check_user_permissions(request, required_permissions)
            
            if not has_permission:
                logger.warning(f"User lacks required permissions: {required_permissions}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for this operation"
                )
        
        return await call_next(request)
    
    def _get_required_permissions(self, request: Request) -> List[str]:
        """Get required permissions for the current endpoint."""
        path = request.url.path
        method = request.method.upper()
        
        # Create endpoint key
        endpoint_key = f"{method} {path}"
        
        # Check exact matches first
        if endpoint_key in self.permission_map:
            return self.permission_map[endpoint_key]
        
        # Check pattern matches
        for pattern, permissions in self.permission_map.items():
            if self._matches_pattern(path, pattern):
                return permissions
        
        return []
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches a permission pattern."""
        # Simple pattern matching - can be enhanced with regex
        if "*" in pattern:
            pattern_parts = pattern.split("*")
            if len(pattern_parts) == 2:
                start, end = pattern_parts
                return path.startswith(start) and path.endswith(end)
        
        return path == pattern
    
    async def _check_user_permissions(self, request: Request, required_permissions: List[str]) -> bool:
        """Check if user has all required permissions."""
        try:
            user = getattr(request.state, 'user', {})
            business_id = getattr(request.state, 'business_id')
            
            if not business_id:
                return False
            
            # Find user's membership for this business
            business_memberships = user.get('business_memberships', [])
            
            current_membership = None
            for membership in business_memberships:
                if membership["business_id"] == business_id:
                    current_membership = membership
                    break
            
            if not current_membership:
                return False
            
            # Check if user has all required permissions
            user_permissions = current_membership.get("permissions", [])
            
            return all(permission in user_permissions for permission in required_permissions)
            
        except Exception as e:
            logger.error(f"Error checking user permissions: {str(e)}")
            return False


def require_business_permission(*permissions: str):
    """
    Decorator for requiring specific business permissions on endpoints.
    
    Args:
        *permissions: List of required permissions
    """
    def decorator(func):
        # Store required permissions as function attribute
        func._required_business_permissions = list(permissions)
        return func
    return decorator


def get_business_context_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """Extract business context from request state."""
    if not getattr(request.state, 'business_context_validated', False):
        return None
    
    return {
        "business_id": getattr(request.state, 'business_id'),
        "user": getattr(request.state, 'user', {}),
        "authenticated": getattr(request.state, 'authenticated', False)
    }


def require_business_context(request: Request) -> Dict[str, Any]:
    """
    Get business context or raise HTTPException.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Business context dict
        
    Raises:
        HTTPException: If business context is not validated
    """
    business_context = get_business_context_from_request(request)
    
    if not business_context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business context required for this operation"
        )
    
    return business_context 