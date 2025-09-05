"""
Public API Router

This module contains all public endpoints that don't require authentication.
These endpoints are completely separate from the main authenticated API.
"""

from fastapi import APIRouter
from .routes.contractors import contractors_router
from .routes.contractors import services as contractors_services
from .routes.contractors import sitemap as contractors_sitemap
from .routes.contractors import deployment as contractors_deployment

# Create public API router without any middleware dependencies
public_router = APIRouter(prefix="/public")

# Include public route modules
public_router.include_router(contractors_router, prefix="/contractors")
public_router.include_router(contractors_services.router)
public_router.include_router(contractors_sitemap.router, prefix="/contractors")
public_router.include_router(contractors_deployment.router, prefix="/contractors")
