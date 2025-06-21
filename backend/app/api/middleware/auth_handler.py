"""
Authentication Middleware

JWT token validation and user authentication middleware.
"""

import logging
from typing import Optional, Dict, Any, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

from ...core.config import settings
from ...core.auth_facade import auth_facade
from ...infrastructure.config.dependency_injection import get_container

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for JWT token validation.
    
    This middleware validates JWT tokens and adds user information to the request.
    """
    
    def __init__(self, app, skip_paths: list = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: FastAPI application
            skip_paths: List of paths to skip authentication
        """
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/login",
            "/register",
            "/reset-password",
            "/forgot-password",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and validate authentication if required."""
        path = request.url.path
        logger.info(f"AuthMiddleware processing request: {request.method} {path}")
        
        # Skip authentication for certain paths
        if self._should_skip_auth(request):
            logger.info(f"Skipping authentication for path: {path}")
            return await call_next(request)
        
        logger.info(f"Authentication required for path: {path}")
        
        # Extract and validate token
        token = self._extract_token(request)
        if token:
            logger.info(f"Token extracted: {token[:50]}...")
            user_info = await self._validate_token(token)
            if user_info:
                logger.info(f"Token validated successfully for user: {user_info.get('sub', 'unknown')}")
                # Add user info to request state
                request.state.user = user_info
                request.state.authenticated = True
            else:
                logger.warning("Token validation failed")
                request.state.authenticated = False
        else:
            logger.warning("No token found in request")
            request.state.authenticated = False
        
        # Continue with request processing
        response = await call_next(request)
        logger.info(f"Request processed, response status: {response.status_code}")
        return response
    
    def _should_skip_auth(self, request: Request) -> bool:
        """Check if authentication should be skipped for this path."""
        path = request.url.path
        
        # Check exact matches
        if path in self.skip_paths:
            return True
        
        # Check path prefixes
        skip_prefixes = ["/docs", "/redoc", "/static", "/assets"]
        if any(path.startswith(prefix) for prefix in skip_prefixes):
            return True
        
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        # Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            logger.info("Token found in Authorization header")
            return auth_header[7:]  # Remove "Bearer " prefix
        
        # Try X-API-Key header as fallback
        api_key = request.headers.get("X-API-Key")
        if api_key:
            logger.info("Token found in X-API-Key header")
            return api_key
        
        # Try cookie (for browser-based requests)
        if "access_token" in request.cookies:
            logger.info("Token found in cookies")
            return request.cookies["access_token"]
        
        logger.info("No token found in request")
        return None
    
    async def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return user information.
        
        Args:
            token: JWT token to validate
            
        Returns:
            User information dict if valid, None otherwise
        """
        try:
            logger.info("Validating token with auth facade")
            # Verify token with Supabase
            user_data = await auth_facade.verify_token(token)
            if not user_data:
                logger.warning("Auth facade returned no user data")
                return None
            
            logger.info(f"Token validation successful for user: {user_data.get('sub', 'unknown')}")
            # Return user information in expected format
            return user_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None


class RequireAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that requires authentication for all requests.
    
    This middleware enforces authentication and returns 401 for unauthenticated requests.
    """
    
    def __init__(self, app, skip_paths: list = None):
        """
        Initialize require auth middleware.
        
        Args:
            app: FastAPI application
            skip_paths: List of paths to skip authentication requirement
        """
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/docs",
            "/redoc",
            "/openapi.json", 
            "/health",
            "/login",
            "/register",
            "/reset-password",
            "/forgot-password",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enforce authentication."""
        # Skip authentication for certain paths
        if self._should_skip_auth(request):
            return await call_next(request)
        
        # Check if user is authenticated
        if not getattr(request.state, 'authenticated', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Continue with request processing
        return await call_next(request)
    
    def _should_skip_auth(self, request: Request) -> bool:
        """Check if authentication should be skipped for this path."""
        path = request.url.path
        
        # Check exact matches
        if path in self.skip_paths:
            return True
        
        # Check path prefixes
        skip_prefixes = ["/docs", "/redoc", "/static", "/assets"]
        if any(path.startswith(prefix) for prefix in skip_prefixes):
            return True
        
        return False


class RoleBasedAccessMiddleware(BaseHTTPMiddleware):
    """
    Middleware for role-based access control.
    
    This middleware checks user roles and permissions for specific endpoints.
    """
    
    def __init__(self, app, role_requirements: Dict[str, list] = None):
        """
        Initialize role-based access middleware.
        
        Args:
            app: FastAPI application
            role_requirements: Dict mapping path patterns to required roles
        """
        super().__init__(app)
        self.role_requirements = role_requirements or {
            "/admin": ["admin", "superuser"],
            "/users": ["admin", "superuser"],
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and check role-based permissions."""
        # Skip if not authenticated
        if not getattr(request.state, 'authenticated', False):
            return await call_next(request)
        
        # Check role requirements
        required_roles = self._get_required_roles(request)
        if required_roles:
            user_roles = self._get_user_roles(request)
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        # Continue with request processing
        return await call_next(request)
    
    def _get_required_roles(self, request: Request) -> Optional[list]:
        """Get required roles for the current request path."""
        path = request.url.path
        
        # Check exact matches and prefixes
        for pattern, roles in self.role_requirements.items():
            if path.startswith(pattern):
                return roles
        
        return None
    
    def _get_user_roles(self, request: Request) -> list:
        """Extract user roles from request state."""
        user = getattr(request.state, 'user', {})
        roles = []
        
        # Check if user is superuser
        if user.get('is_superuser', False):
            roles.extend(['superuser', 'admin'])
        
        # Add roles from app metadata
        app_metadata = user.get('app_metadata', {})
        user_roles = app_metadata.get('roles', [])
        if isinstance(user_roles, list):
            roles.extend(user_roles)
        
        return roles


def get_current_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extract current user from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User information dict or None
    """
    return getattr(request.state, 'user', None)


def require_authenticated_user(request: Request) -> Dict[str, Any]:
    """
    Get authenticated user or raise HTTPException.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User information dict
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not getattr(request.state, 'authenticated', False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    return user


def require_superuser(request: Request) -> Dict[str, Any]:
    """
    Get authenticated superuser or raise HTTPException.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User information dict
        
    Raises:
        HTTPException: If user is not authenticated or not a superuser
    """
    user = require_authenticated_user(request)
    
    if not user.get('is_superuser', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    
    return user 