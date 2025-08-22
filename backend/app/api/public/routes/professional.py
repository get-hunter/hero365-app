"""
Public Professional API Routes

Public endpoints for retrieving professional information, services, products,
and availability. These endpoints are completely public and don't require authentication.
"""

from fastapi import APIRouter, HTTPException, Query, Path, status, Depends
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from uuid import UUID
import uuid
import logging
from decimal import Decimal

from ....infrastructure.config.dependency_injection import get_container, get_product_repository as get_product_repo_func
from ....domain.repositories.business_repository import BusinessRepository
from ....domain.repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency injection for database access
def get_business_repository() -> BusinessRepository:
    """Get business repository instance."""
    container = get_container()
    return container.get_business_repository()

def get_product_repository() -> ProductRepository:
    """Get product repository instance."""
    return get_product_repo_func()


# Response Models
class ProfessionalProfile(BaseModel):
    """Professional profile information."""
    
    business_id: str = Field(..., description="Business ID")
    business_name: str = Field(..., description="Business name")
    trade_type: str = Field(..., description="Primary trade type")
    description: str = Field(..., description="Business description")
    
    # Contact information
    phone: str = Field(..., description="Business phone")
    email: str = Field(..., description="Business email")
    address: str = Field(..., description="Business address")
    website: Optional[HttpUrl] = Field(None, description="Business website")
    
    # Service information
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    emergency_service: bool = Field(False, description="24/7 emergency service available")
    
    # Business details
    years_in_business: Optional[int] = Field(None, description="Years in business")
    license_number: Optional[str] = Field(None, description="License number")
    insurance_verified: bool = Field(False, description="Insurance verified")
    
    # Ratings and reviews
    average_rating: Optional[float] = Field(None, description="Average customer rating")
    total_reviews: Optional[int] = Field(None, description="Total number of reviews")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")


class ServiceItem(BaseModel):
    """Professional service information."""
    
    id: str = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    description: str = Field(..., description="Service description")
    category: str = Field(..., description="Service category")
    
    # Pricing information
    base_price: Optional[float] = Field(None, description="Base price")
    price_range_min: Optional[float] = Field(None, description="Minimum price")
    price_range_max: Optional[float] = Field(None, description="Maximum price")
    pricing_unit: str = Field("service", description="Pricing unit")
    
    # Service details
    duration_minutes: Optional[int] = Field(None, description="Estimated duration")
    is_emergency: bool = Field(False, description="Emergency service available")
    requires_quote: bool = Field(False, description="Requires custom quote")
    available: bool = Field(True, description="Currently available")
    
    # Service areas and keywords
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    keywords: List[str] = Field(default_factory=list, description="SEO keywords")


class ProductItem(BaseModel):
    """Professional product information."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    
    # Product details
    brand: Optional[str] = Field(None, description="Product brand")
    model: Optional[str] = Field(None, description="Product model")
    sku: Optional[str] = Field(None, description="Product SKU")
    
    # Pricing and availability
    price: float = Field(..., description="Product price")
    msrp: Optional[float] = Field(None, description="Manufacturer suggested retail price")
    in_stock: bool = Field(True, description="Product in stock")
    stock_quantity: int = Field(0, description="Current stock quantity")
    
    # Additional information
    specifications: Dict[str, str] = Field(default_factory=dict, description="Product specifications")
    warranty_years: Optional[int] = Field(None, description="Warranty period in years")
    energy_rating: Optional[str] = Field(None, description="Energy efficiency rating")


class AvailabilitySlot(BaseModel):
    """Available time slot."""
    
    slot_date: date = Field(..., description="Available date")
    start_time: str = Field(..., description="Start time (HH:MM format)")
    end_time: str = Field(..., description="End time (HH:MM format)")
    slot_type: str = Field(..., description="Slot type (regular, emergency, consultation)")
    duration_minutes: int = Field(..., description="Slot duration in minutes")
    available: bool = Field(True, description="Slot is available")


# API Endpoints
@router.get("/profile/{business_id}", response_model=ProfessionalProfile)
async def get_professional_profile(
    business_id: str = Path(..., description="Business ID"),
    business_repo: BusinessRepository = Depends(get_business_repository)
):
    """
    Get complete professional profile information.
    
    Returns business details, contact information, service areas, and credentials.
    """
    
    try:
        # Try to fetch business from database
        business = await business_repo.get_by_id(uuid.UUID(business_id))
        
        if business:
            # Convert business entity to response model
            profile_data = {
                "business_id": str(business.id),
                "business_name": business.name,
                "trade_type": business.industry.lower() if business.industry else "general",
                "description": business.description or f"Professional {business.industry} services",
                "phone": business.phone_number or "",
                "email": business.business_email or "",
                "address": business.business_address or "",
                "website": business.website,
                "service_areas": business.service_areas or [],
                "emergency_service": True,  # Default for now
                "years_in_business": 10,  # Default for now
                "license_number": business.business_license,
                "insurance_verified": True,  # Default for now
                "average_rating": 4.8,  # Default for now
                "total_reviews": 150,  # Default for now
                "certifications": []  # Default for now
            }
            
            return ProfessionalProfile(**profile_data)
        
        # If not found in database, return 404
        raise HTTPException(status_code=404, detail="Professional profile not found")
        
    except Exception as e:
        logger.error(f"Error fetching professional profile {business_id}: {str(e)}")
        # Return error response
        raise HTTPException(status_code=404, detail="Professional profile not found")


@router.get("/services/{business_id}", response_model=List[ServiceItem])
async def get_professional_services(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    emergency_only: bool = Query(False, description="Show only emergency services"),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """
    Get professional services offered by a business.
    
    Returns list of services with pricing and availability information.
    """
    
    try:
        # Fetch services from database (services are stored as products with product_type='service')
        all_products = await product_repo.list_by_business(uuid.UUID(business_id))
        
        if all_products:
            # Filter for services only and convert to ServiceItem models
            service_items = []
            for product in all_products:
                # Only include products that are services
                if hasattr(product, 'product_type') and str(product.product_type) == 'service':
                    # Map product fields to service fields
                    service_data = {
                        "id": str(product.id),
                        "name": product.name,
                        "description": product.description or "",
                        "category": _get_service_category_from_name(product.name),
                        "base_price": float(product.unit_price) if product.unit_price else None,
                        "price_range_min": float(product.unit_price) if product.unit_price else None,
                        "price_range_max": float(product.unit_price * Decimal('1.5')) if product.unit_price else None,  # Estimate range
                        "pricing_unit": "service call" if "repair" in product.name.lower() else "service",
                        "duration_minutes": _estimate_service_duration(product.name),
                        "is_emergency": "emergency" in product.name.lower(),
                        "requires_quote": "installation" in product.name.lower() or "system" in product.name.lower(),
                        "available": product.is_active(),
                        "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville"],  # Default areas
                        "keywords": _generate_service_keywords(product.name)
                    }
                    
                    service_items.append(ServiceItem(**service_data))
            
            # Apply filters
            if category:
                service_items = [s for s in service_items if s.category.lower() == category.lower()]
            
            if emergency_only:
                service_items = [s for s in service_items if s.is_emergency]
            
            return service_items
        
        # No services found in database
        return []
        
    except Exception as e:
        logger.error(f"Error fetching services for {business_id}: {str(e)}")
        return []


@router.get("/products/{business_id}", response_model=List[ProductItem])
async def get_professional_products(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    in_stock_only: bool = Query(True, description="Show only in-stock products"),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """
    Get professional products sold by a business.
    
    Returns list of products with pricing and availability information.
    """
    
    try:
        # Try to fetch products from database
        products = await product_repo.list_by_business(uuid.UUID(business_id))
        
        if products:
            # Convert product entities to response models
            product_items = []
            for product in products:
                # Only include actual products, not services
                if hasattr(product, 'product_type') and str(product.product_type) == 'service':
                    continue
                    
                if in_stock_only and not product.is_active():
                    continue
                
                if category and product.category_id != category:
                    continue
                
                product_data = {
                    "id": str(product.id),
                    "name": product.name,
                    "description": product.description or "",
                    "category": "General",  # TODO: Get category name from category_id
                    "brand": "Professional Brand",  # TODO: Add brand field to product entity
                    "model": "",  # TODO: Add model field to product entity
                    "sku": product.sku or "",
                    "price": float(product.unit_price),
                    "msrp": None,  # TODO: Add MSRP field to product entity
                    "in_stock": product.is_active(),
                    "stock_quantity": int(product.quantity_on_hand) if product.quantity_on_hand else 0,
                    "specifications": {},  # TODO: Add specifications field
                    "warranty_years": None,  # TODO: Add warranty field
                    "energy_rating": None  # TODO: Add energy rating field
                }
                
                product_items.append(ProductItem(**product_data))
            
            return product_items
        
        # No products found in database
        return []
        
    except Exception as e:
        logger.error(f"Error fetching products for {business_id}: {str(e)}")
        return []


@router.get("/availability/{business_id}", response_model=List[AvailabilitySlot])
async def get_professional_availability(
    business_id: str = Path(..., description="Business ID"),
    start_date: date = Query(..., description="Start date for availability"),
    end_date: date = Query(..., description="End date for availability")
):
    """
    Get professional availability for a date range.
    
    Returns available time slots for booking appointments.
    """
    
    try:
        # TODO: Implement real database integration with calendar_events table
        # For now, return empty availability until calendar integration is implemented
        return []
        
    except Exception as e:
        logger.error(f"Error fetching availability for {business_id}: {str(e)}")
        return []


# Helper functions for service data mapping
def _get_service_category_from_name(service_name: str) -> str:
    """Determine service category based on service name."""
    name_lower = service_name.lower()
    if "repair" in name_lower or "emergency" in name_lower:
        return "Repair"
    elif "installation" in name_lower or "install" in name_lower:
        return "Installation"
    elif "maintenance" in name_lower or "tune" in name_lower:
        return "Maintenance"
    elif "cleaning" in name_lower or "duct" in name_lower:
        return "Air Quality"
    elif "thermostat" in name_lower:
        return "Controls"
    else:
        return "General"

def _estimate_service_duration(service_name: str) -> int:
    """Estimate service duration in minutes based on service type."""
    name_lower = service_name.lower()
    if "emergency" in name_lower or "repair" in name_lower:
        return 90
    elif "installation" in name_lower and "system" in name_lower:
        return 240
    elif "installation" in name_lower:
        return 120
    elif "maintenance" in name_lower:
        return 60
    elif "cleaning" in name_lower:
        return 180
    else:
        return 120

def _generate_service_keywords(service_name: str) -> List[str]:
    """Generate SEO keywords based on service name."""
    name_lower = service_name.lower()
    keywords = []
    
    if "hvac" in name_lower:
        keywords.extend(["hvac", "heating", "cooling", "air conditioning"])
    if "ac" in name_lower or "air conditioning" in name_lower:
        keywords.extend(["ac repair", "air conditioning", "cooling"])
    if "repair" in name_lower:
        keywords.extend(["repair", "fix", "service"])
    if "emergency" in name_lower:
        keywords.extend(["emergency", "24/7", "urgent"])
    if "installation" in name_lower:
        keywords.extend(["installation", "new system", "replacement"])
    if "maintenance" in name_lower:
        keywords.extend(["maintenance", "tune up", "service"])
    if "duct" in name_lower:
        keywords.extend(["duct cleaning", "air quality", "ventilation"])
    if "thermostat" in name_lower:
        keywords.extend(["thermostat", "smart thermostat", "temperature control"])
    
    return keywords
