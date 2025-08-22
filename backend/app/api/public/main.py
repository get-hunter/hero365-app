"""
Public API Router

This module contains all public endpoints that don't require authentication.
These endpoints are completely separate from the main authenticated API.
"""

from fastapi import APIRouter
from .routes import professional

# Create public API router without any middleware dependencies
public_router = APIRouter(prefix="/public")

# Include public route modules
public_router.include_router(professional.router, prefix="/professional", tags=["Public Professional"])
