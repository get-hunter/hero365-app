"""
Public Contractors API Routes

Aggregated router for all contractor-related public endpoints.
These endpoints are completely public and don't require authentication.
"""

from fastapi import APIRouter
from . import profile, services, products, cart, checkout, availability, projects, membership

# Create contractors API router
contractors_router = APIRouter()

# Include all contractor route modules
contractors_router.include_router(profile.router, tags=["Contractors Profile"])
contractors_router.include_router(services.router, tags=["Contractors Services"])
contractors_router.include_router(products.router, tags=["Contractors Products"])
contractors_router.include_router(projects.router, tags=["Contractors Projects"])
contractors_router.include_router(cart.router, tags=["Contractors Cart"])
contractors_router.include_router(checkout.router, tags=["Contractors Checkout"])
contractors_router.include_router(availability.router, tags=["Contractors Availability"])
contractors_router.include_router(membership.router, tags=["Contractors Membership"])
