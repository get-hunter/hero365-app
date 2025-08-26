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


class ServiceCategory(BaseModel):
    """Service category with services."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    services: List[ServiceItem] = Field(default_factory=list, description="Services in this category")


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
    business_id: str = Path(..., description="Business ID")
):
    """
    Get complete professional profile information.
    
    Returns business details, contact information, service areas, and credentials.
    """
    
    try:
        # Use direct database query to avoid repository issues
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Fetch business from database
        result = supabase.table("businesses").select("*").eq("id", business_id).eq("is_active", True).execute()
        
        if result.data and len(result.data) > 0:
            business = result.data[0]
            
            # Convert business data to response model
            profile_data = {
                "business_id": str(business["id"]),
                "business_name": business["name"],
                "trade_type": business["industry"].lower() if business.get("industry") else "general",
                "description": business.get("description") or f"Professional {business.get('industry', 'service')} provider",
                "phone": business.get("phone_number") or "",
                "email": business.get("business_email") or "",
                "address": business.get("business_address") or "",
                "website": business.get("website"),
                "service_areas": business.get("service_areas") or [],
                "emergency_service": True,  # Default for now
                "years_in_business": 10,  # Default for now
                "license_number": business.get("business_license"),
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
    emergency_only: bool = Query(False, description="Show only emergency services")
):
    """
    Get professional services offered by a business.
    
    Returns list of services with pricing and availability information.
    Uses the new business_services table from service template system.
    """
    
    try:
        # TODO: Replace with proper service template repository dependency injection
        # For now, use direct database query via supabase
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Build query with proper join syntax
        query = supabase.table("business_services").select(
            "id, name, description, pricing_model, unit_price, minimum_price, "
            "estimated_duration_hours, is_emergency, is_active, sort_order, "
            "service_categories!inner(id, name, slug)"
        ).eq("business_id", business_id).eq("is_active", True)
        
        # Apply filters
        if category:
            # Filter by category name
            query = query.eq("service_categories.name", category)
        
        if emergency_only:
            query = query.eq("is_emergency", True)
        
        # Order by sort_order and name
        query = query.order("sort_order").order("name")
        
        result = query.execute()
        
        if result.data:
            # Convert business_services to ServiceItem models
            service_items = []
            for service in result.data:
                # Map business_service fields to ServiceItem fields
                category_info = service.get("service_categories", {})
                category_name = category_info.get("name", "General") if category_info else "General"
                
                # Calculate duration in minutes
                duration_hours = service.get("estimated_duration_hours", 1.0)
                duration_minutes = int(duration_hours * 60) if duration_hours else 60
                
                service_data = {
                    "id": str(service["id"]),
                    "name": service["name"],
                    "description": service.get("description", ""),
                    "category": category_name,
                    "base_price": float(service["unit_price"]) if service.get("unit_price") else None,
                    "price_range_min": float(service["minimum_price"]) if service.get("minimum_price") else float(service["unit_price"]) if service.get("unit_price") else None,
                    "price_range_max": float(service["unit_price"]) if service.get("unit_price") else None,
                    "pricing_unit": "service" if service["pricing_model"] == "fixed" else service.get("pricing_model", "service"),
                    "duration_minutes": duration_minutes,
                    "is_emergency": service.get("is_emergency", False),
                    "requires_quote": service["pricing_model"] == "quote_required",
                    "available": service.get("is_active", True),
                    "service_areas": [],  # TODO: get from business or service data
                    "keywords": service["name"].lower().split()  # Simple keyword extraction
                }
                
                service_items.append(ServiceItem(**service_data))
            
            return service_items
        
        # No services found in database
        return []
        
    except Exception as e:
        logger.error(f"Error fetching services for {business_id}: {str(e)}")
        return []


@router.get("/service-categories/{business_id}", response_model=List[ServiceCategory])
async def get_professional_service_categories(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get professional service categories with their services grouped.
    
    Returns service categories with services organized for website navigation and menus.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # First get all services for this business with categories
        services_query = supabase.table("business_services").select(
            "id, name, description, pricing_model, unit_price, minimum_price, "
            "estimated_duration_hours, is_emergency, is_active, sort_order, "
            "service_categories!inner(id, name, slug, description)"
        ).eq("business_id", business_id).eq("is_active", True).order("sort_order").order("name")
        
        services_result = services_query.execute()
        
        if not services_result.data:
            return []
        
        # Group services by category
        categories_dict = {}
        
        for service in services_result.data:
            category_info = service.get("service_categories", {})
            category_id = category_info.get("id")
            category_name = category_info.get("name", "General")
            category_slug = category_info.get("slug", "general")
            category_description = category_info.get("description", "")
            
            if category_id not in categories_dict:
                categories_dict[category_id] = {
                    "id": str(category_id),
                    "name": category_name,
                    "slug": category_slug,
                    "description": category_description,
                    "services": []
                }
            
            # Calculate duration in minutes
            duration_hours = service.get("estimated_duration_hours", 1.0)
            duration_minutes = int(duration_hours * 60) if duration_hours else 60
            
            # Create service item
            service_item = ServiceItem(
                id=str(service["id"]),
                name=service["name"],
                description=service.get("description", ""),
                category=category_name,
                base_price=float(service["unit_price"]) if service.get("unit_price") else None,
                price_range_min=float(service["minimum_price"]) if service.get("minimum_price") else float(service["unit_price"]) if service.get("unit_price") else None,
                price_range_max=float(service["unit_price"]) if service.get("unit_price") else None,
                pricing_unit="service" if service["pricing_model"] == "fixed" else service.get("pricing_model", "service"),
                duration_minutes=duration_minutes,
                is_emergency=service.get("is_emergency", False),
                requires_quote=service["pricing_model"] == "quote_required",
                available=service.get("is_active", True),
                service_areas=[],
                keywords=service["name"].lower().split()
            )
            
            categories_dict[category_id]["services"].append(service_item)
        
        # Convert to list of ServiceCategory objects
        service_categories = []
        for category_data in categories_dict.values():
            service_categories.append(ServiceCategory(**category_data))
        
        # Sort categories by name
        service_categories.sort(key=lambda x: x.name)
        
        return service_categories
        
    except Exception as e:
        logger.error(f"Error fetching service categories for {business_id}: {str(e)}")
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
