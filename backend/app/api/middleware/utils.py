"""
Middleware Utilities

Common utilities and helper functions for middleware operations.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import Request
import json
import uuid

# Configure logging
logger = logging.getLogger(__name__)


def log_request_info(request: Request, middleware_name: str = "Unknown"):
    """
    Log detailed request information for debugging.
    
    Args:
        request: FastAPI request object
        middleware_name: Name of the middleware logging the request
    """
    request_info = {
        "middleware": middleware_name,
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": getattr(request.client, 'host', 'unknown') if request.client else 'unknown',
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_type": request.headers.get("content-type", "unknown"),
        "authenticated": getattr(request.state, 'authenticated', False),
        "business_context": getattr(request.state, 'business_context_validated', False),
        "business_id": getattr(request.state, 'business_id', None),
    }
    
    # Add authorization header info (without exposing the actual token)
    auth_header = request.headers.get("authorization")
    if auth_header:
        if auth_header.startswith("Bearer "):
            request_info["auth_type"] = "Bearer"
            token_preview = auth_header[7:17] + "..." if len(auth_header) > 17 else "short_token"
            request_info["token_preview"] = token_preview
        else:
            request_info["auth_type"] = "Other"
    else:
        request_info["auth_type"] = "None"
    
    logger.info(f"Request processed by {middleware_name}: {json.dumps(request_info, indent=2)}")


def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Sanitize headers by removing or masking sensitive information.
    
    Args:
        headers: Dictionary of headers
        
    Returns:
        Sanitized headers dictionary
    """
    sensitive_headers = {
        "authorization": lambda x: f"Bearer {x[7:17]}..." if x.startswith("Bearer ") and len(x) > 17 else "***",
        "cookie": lambda x: "***",
        "x-api-key": lambda x: f"{x[:8]}..." if len(x) > 8 else "***",
    }
    
    sanitized = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in sensitive_headers:
            sanitized[key] = sensitive_headers[key_lower](value)
        else:
            sanitized[key] = value
    
    return sanitized


def extract_user_info_from_request(request: Request) -> Dict[str, Any]:
    """
    Extract user information from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary containing user information
    """
    user = getattr(request.state, 'user', {})
    
    if not user:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user_id": user.get("sub") or user.get("id"),
        "email": user.get("email"),
        "current_business_id": user.get("current_business_id"),
        "business_memberships": len(user.get("business_memberships", [])),
        "is_superuser": user.get("is_superuser", False),
    }


def extract_business_context_from_request(request: Request) -> Dict[str, Any]:
    """
    Extract business context information from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary containing business context information
    """
    business_context = {
        "business_context_validated": getattr(request.state, 'business_context_validated', False),
        "business_id": getattr(request.state, 'business_id', None),
    }
    
    # Add user's business memberships if available
    user = getattr(request.state, 'user', {})
    if user:
        business_memberships = user.get('business_memberships', [])
        business_context["available_businesses"] = len(business_memberships)
        
        # Find current business membership details
        current_business_id = business_context["business_id"]
        if current_business_id:
            for membership in business_memberships:
                if membership.get("business_id") == current_business_id:
                    business_context.update({
                        "role": membership.get("role"),
                        "permissions": len(membership.get("permissions", [])),
                        "role_level": membership.get("role_level", 0)
                    })
                    break
    
    return business_context


def is_public_path(path: str, public_paths: List[str]) -> bool:
    """
    Check if a path is in the public paths list.
    
    Args:
        path: Request path to check
        public_paths: List of public paths
        
    Returns:
        True if path is public, False otherwise
    """
    # Check exact matches
    if path in public_paths:
        return True
    
    # Check prefix matches
    for public_path in public_paths:
        if path.startswith(public_path):
            return True
    
    return False


def generate_request_id() -> str:
    """
    Generate a unique request ID for tracing.
    
    Returns:
        Unique request ID string
    """
    return str(uuid.uuid4())


def add_request_id_to_state(request: Request) -> str:
    """
    Add a unique request ID to the request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Generated request ID
    """
    request_id = generate_request_id()
    request.state.request_id = request_id
    return request_id


def get_request_id_from_state(request: Request) -> Optional[str]:
    """
    Get request ID from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Request ID if available, None otherwise
    """
    return getattr(request.state, 'request_id', None)


def log_middleware_error(middleware_name: str, error: Exception, request: Request):
    """
    Log middleware errors with context information.
    
    Args:
        middleware_name: Name of the middleware where error occurred
        error: Exception that occurred
        request: FastAPI request object
    """
    error_info = {
        "middleware": middleware_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "request_id": get_request_id_from_state(request),
        "path": request.url.path,
        "method": request.method,
        "user_info": extract_user_info_from_request(request),
        "business_context": extract_business_context_from_request(request),
    }
    
    logger.error(f"Middleware error in {middleware_name}: {json.dumps(error_info, indent=2)}")


def create_middleware_response_headers(request: Request) -> Dict[str, str]:
    """
    Create response headers with middleware processing information.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary of response headers
    """
    headers = {}
    
    # Add request ID if available
    request_id = get_request_id_from_state(request)
    if request_id:
        headers["X-Request-ID"] = request_id
    
    # Add processing information
    if getattr(request.state, 'authenticated', False):
        headers["X-Auth-Status"] = "authenticated"
    else:
        headers["X-Auth-Status"] = "unauthenticated"
    
    if getattr(request.state, 'business_context_validated', False):
        headers["X-Business-Context"] = "validated"
        business_id = getattr(request.state, 'business_id', None)
        if business_id:
            headers["X-Business-ID"] = business_id
    else:
        headers["X-Business-Context"] = "not_validated"
    
    return headers


def validate_uuid_format(value: str) -> bool:
    """
    Validate if a string is a valid UUID format.
    
    Args:
        value: String to validate
        
    Returns:
        True if valid UUID format, False otherwise
    """
    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive data in a dictionary for logging.
    
    Args:
        data: Dictionary potentially containing sensitive data
        
    Returns:
        Dictionary with sensitive data masked
    """
    sensitive_keys = {
        "password", "token", "secret", "key", "authorization", 
        "cookie", "session", "credentials", "private"
    }
    
    masked_data = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive_key in key_lower for sensitive_key in sensitive_keys):
            if isinstance(value, str) and len(value) > 8:
                masked_data[key] = f"{value[:4]}***{value[-4:]}"
            else:
                masked_data[key] = "***"
        else:
            masked_data[key] = value
    
    return masked_data 