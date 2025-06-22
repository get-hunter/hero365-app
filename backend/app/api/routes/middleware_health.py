"""
Middleware Health Check Routes

API endpoints for monitoring and debugging middleware status.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from ..middleware.middleware_manager import middleware_manager
from ..middleware.auth_handler import get_current_user_from_request, get_current_business_context

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/middleware", tags=["Middleware Health"])


class MiddlewareHealthResponse(BaseModel):
    """Schema for middleware health response."""
    
    status: str
    total_middlewares: int
    cors_enabled: bool
    cors_origins: list
    middlewares: list
    request_info: Dict[str, Any]


class MiddlewareTestResponse(BaseModel):
    """Schema for middleware test response."""
    
    authentication_status: str
    business_context_status: str
    user_info: Dict[str, Any]
    business_info: Dict[str, Any]
    headers: Dict[str, str]


@router.get("/health", response_model=MiddlewareHealthResponse)
async def get_middleware_health(request: Request) -> MiddlewareHealthResponse:
    """
    Get middleware health and configuration information.
    
    This endpoint provides information about the current middleware stack,
    configuration, and request processing status.
    """
    try:
        # Get middleware information
        middleware_info = middleware_manager.get_middleware_info()
        
        # Get request information
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "authenticated": getattr(request.state, 'authenticated', False),
            "business_context_validated": getattr(request.state, 'business_context_validated', False),
            "business_id": getattr(request.state, 'business_id', None),
        }
        
        return MiddlewareHealthResponse(
            status="healthy",
            total_middlewares=middleware_info["total_middlewares"],
            cors_enabled=middleware_info["cors_enabled"],
            cors_origins=middleware_info["cors_origins"],
            middlewares=middleware_info["middlewares"],
            request_info=request_info
        )
        
    except Exception as e:
        logger.error(f"Error getting middleware health: {str(e)}")
        return MiddlewareHealthResponse(
            status="error",
            total_middlewares=0,
            cors_enabled=False,
            cors_origins=[],
            middlewares=[],
            request_info={"error": str(e)}
        )


@router.get("/test", response_model=MiddlewareTestResponse)
async def test_middleware_stack(request: Request) -> MiddlewareTestResponse:
    """
    Test the middleware stack functionality.
    
    This endpoint tests authentication and business context middleware
    to ensure they are working correctly.
    """
    try:
        # Test authentication middleware
        user = get_current_user_from_request(request)
        auth_status = "authenticated" if user else "not_authenticated"
        
        # Test business context middleware
        business_context = get_current_business_context(request)
        business_status = "has_business_context" if business_context else "no_business_context"
        
        # Sanitize user info (remove sensitive data)
        user_info = {}
        if user:
            user_info = {
                "user_id": user.get("sub") or user.get("id"),
                "email": user.get("email"),
                "current_business_id": user.get("current_business_id"),
                "business_memberships_count": len(user.get("business_memberships", []))
            }
        
        # Get business info
        business_info = business_context or {}
        
        # Get relevant headers
        relevant_headers = {
            "authorization": request.headers.get("authorization", "not_present"),
            "x-business-id": request.headers.get("x-business-id", "not_present"),
            "user-agent": request.headers.get("user-agent", "not_present"),
            "origin": request.headers.get("origin", "not_present"),
        }
        
        return MiddlewareTestResponse(
            authentication_status=auth_status,
            business_context_status=business_status,
            user_info=user_info,
            business_info=business_info,
            headers=relevant_headers
        )
        
    except Exception as e:
        logger.error(f"Error testing middleware stack: {str(e)}")
        return MiddlewareTestResponse(
            authentication_status="error",
            business_context_status="error",
            user_info={"error": str(e)},
            business_info={"error": str(e)},
            headers={}
        )


@router.get("/config")
async def get_middleware_config() -> Dict[str, Any]:
    """
    Get detailed middleware configuration.
    
    This endpoint provides detailed configuration information
    for debugging and monitoring purposes.
    """
    try:
        config = middleware_manager.config
        
        return {
            "api_v1_str": config.api_v1_str,
            "public_paths": config.public_paths,
            "auth_skip_paths": config.auth_skip_paths,
            "business_context_skip_paths": config.business_context_skip_paths,
            "cors_origins": config.cors_origins,
            "middleware_stack": [
                {
                    "name": m["name"],
                    "description": m["description"],
                    "configuration": m["kwargs"]
                }
                for m in middleware_manager.middlewares
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting middleware config: {str(e)}")
        return {"error": str(e)}


@router.post("/test-auth")
async def test_authentication_required(request: Request) -> Dict[str, Any]:
    """
    Test endpoint that requires authentication.
    
    This endpoint will return 401 if authentication middleware is not working.
    """
    user = get_current_user_from_request(request)
    
    if not user:
        return {"error": "Authentication required", "status": "unauthenticated"}
    
    return {
        "status": "authenticated",
        "user_id": user.get("sub") or user.get("id"),
        "message": "Authentication middleware is working correctly"
    }


@router.post("/test-business-context")
async def test_business_context_required(request: Request) -> Dict[str, Any]:
    """
    Test endpoint that requires business context.
    
    This endpoint will return 400 if business context middleware is not working.
    """
    user = get_current_user_from_request(request)
    business_context = get_current_business_context(request)
    
    if not user:
        return {"error": "Authentication required", "status": "unauthenticated"}
    
    if not business_context:
        return {"error": "Business context required", "status": "no_business_context"}
    
    return {
        "status": "business_context_validated",
        "business_id": business_context.get("business_id"),
        "role": business_context.get("role"),
        "message": "Business context middleware is working correctly"
    } 