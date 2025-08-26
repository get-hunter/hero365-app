"""
Public Professional API Routes

Public endpoints for retrieving professional information, services, products,
and availability. These endpoints are completely public and don't require authentication.
"""

from fastapi import APIRouter, HTTPException, Query, Path, status, Depends, Body
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


class MembershipBenefit(BaseModel):
    """Membership plan benefit."""
    
    id: str = Field(..., description="Benefit ID")
    title: str = Field(..., description="Benefit title")
    description: str = Field(..., description="Benefit description")
    icon: Optional[str] = Field(None, description="Icon name for UI")
    value: Optional[str] = Field(None, description="Benefit value (e.g., '15%', '$69 value')")
    is_highlighted: bool = Field(False, description="Whether this benefit should be highlighted")
    sort_order: int = Field(0, description="Display order")


class MembershipPlan(BaseModel):
    """Customer membership plan."""
    
    id: str = Field(..., description="Plan ID")
    name: str = Field(..., description="Plan name")
    plan_type: str = Field(..., description="Plan type (residential, commercial, premium)")
    description: str = Field(..., description="Plan description")
    tagline: Optional[str] = Field(None, description="Marketing tagline")
    
    # Pricing
    price_monthly: Optional[float] = Field(None, description="Monthly price")
    price_yearly: Optional[float] = Field(None, description="Yearly price")
    yearly_savings: Optional[float] = Field(None, description="Annual savings amount")
    setup_fee: Optional[float] = Field(None, description="One-time setup fee")
    
    # Service benefits
    discount_percentage: int = Field(0, description="Service discount percentage")
    priority_service: bool = Field(False, description="Priority scheduling")
    extended_warranty: bool = Field(False, description="Extended warranty coverage")
    maintenance_included: bool = Field(False, description="Maintenance visits included")
    emergency_response: bool = Field(False, description="24/7 emergency response")
    free_diagnostics: bool = Field(False, description="Free diagnostic calls")
    annual_tune_ups: int = Field(0, description="Number of annual tune-ups")
    
    # Display
    is_active: bool = Field(True, description="Plan is active")
    is_featured: bool = Field(False, description="Plan is featured/popular")
    popular_badge: Optional[str] = Field(None, description="Popular badge text")
    color_scheme: Optional[str] = Field(None, description="UI color scheme")
    sort_order: int = Field(0, description="Display order")
    
    # Terms
    contract_length_months: Optional[int] = Field(None, description="Contract length in months")
    cancellation_policy: Optional[str] = Field(None, description="Cancellation policy")
    
    # Benefits list
    benefits: List[MembershipBenefit] = Field(default_factory=list, description="Plan benefits")


class ServicePricing(BaseModel):
    """Service pricing with membership discounts."""
    
    id: str = Field(..., description="Pricing ID")
    service_name: str = Field(..., description="Service name")
    service_category: str = Field(..., description="Service category")
    
    # Base pricing
    base_price: float = Field(..., description="Base service price")
    price_display: str = Field("fixed", description="Price display type (from, fixed, quote_required, free)")
    
    # Member pricing
    residential_member_price: Optional[float] = Field(None, description="Residential member price")
    commercial_member_price: Optional[float] = Field(None, description="Commercial member price")
    premium_member_price: Optional[float] = Field(None, description="Premium member price")
    
    # Service details
    description: Optional[str] = Field(None, description="Service description")
    includes: List[str] = Field(default_factory=list, description="What's included in service")
    duration_estimate: Optional[str] = Field(None, description="Estimated duration")
    minimum_labor_fee: Optional[float] = Field(None, description="Minimum labor charge")
    
    # Service conditions
    height_surcharge: bool = Field(False, description="Height surcharge may apply")
    additional_tech_fee: bool = Field(False, description="Additional technician fee may apply")
    parts_separate: bool = Field(False, description="Parts are charged separately")
    
    # Display
    is_active: bool = Field(True, description="Service pricing is active")
    sort_order: int = Field(0, description="Display order")


class ServicePricingCategory(BaseModel):
    """Service pricing grouped by category."""
    
    category: str = Field(..., description="Category name")
    services: List[ServicePricing] = Field(default_factory=list, description="Services in this category")


class ProductInstallationOption(BaseModel):
    """Product installation option with pricing."""
    
    id: str = Field(..., description="Installation option ID")
    option_name: str = Field(..., description="Installation option name")
    description: Optional[str] = Field(None, description="Installation description")
    base_install_price: float = Field(..., description="Base installation price")
    
    # Membership pricing
    residential_install_price: Optional[float] = Field(None, description="Residential member price")
    commercial_install_price: Optional[float] = Field(None, description="Commercial member price")
    premium_install_price: Optional[float] = Field(None, description="Premium member price")
    
    # Installation details
    estimated_duration_hours: Optional[float] = Field(None, description="Estimated installation time")
    complexity_multiplier: float = Field(1.0, description="Complexity multiplier")
    is_default: bool = Field(False, description="Default installation option")
    
    # Requirements and inclusions
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Installation requirements")
    included_in_install: List[str] = Field(default_factory=list, description="What's included")


class ProductCatalogItem(BaseModel):
    """Product catalog item with installation options."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Product SKU")
    description: Optional[str] = Field(None, description="Product description")
    long_description: Optional[str] = Field(None, description="Detailed product description")
    
    # Pricing
    unit_price: float = Field(..., description="Product unit price")
    price_display: str = Field("fixed", description="Price display type")
    
    # Product details
    category_name: Optional[str] = Field(None, description="Product category")
    brand: Optional[str] = Field(None, description="Product brand")
    warranty_years: Optional[int] = Field(None, description="Warranty period")
    energy_efficiency_rating: Optional[str] = Field(None, description="Energy efficiency rating")
    
    # Installation
    requires_professional_install: bool = Field(False, description="Requires professional installation")
    install_complexity: str = Field("standard", description="Installation complexity level")
    installation_time_estimate: Optional[str] = Field(None, description="Installation time estimate")
    
    # E-commerce
    featured_image_url: Optional[str] = Field(None, description="Main product image")
    gallery_images: List[str] = Field(default_factory=list, description="Product gallery images")
    product_highlights: List[str] = Field(default_factory=list, description="Key product features")
    technical_specs: Dict[str, Any] = Field(default_factory=dict, description="Technical specifications")
    
    # SEO
    meta_title: Optional[str] = Field(None, description="SEO title")
    meta_description: Optional[str] = Field(None, description="SEO description")
    slug: Optional[str] = Field(None, description="URL slug")
    
    # Availability
    is_active: bool = Field(True, description="Product is active")
    is_featured: bool = Field(False, description="Product is featured")
    current_stock: Optional[float] = Field(None, description="Current stock level")
    
    # Installation options
    installation_options: List[ProductInstallationOption] = Field(default_factory=list, description="Available installation options")


class PricingBreakdown(BaseModel):
    """Detailed pricing breakdown for product + installation."""
    
    # Base pricing
    product_unit_price: float = Field(..., description="Product unit price")
    installation_base_price: float = Field(..., description="Installation base price") 
    quantity: int = Field(1, description="Quantity")
    
    # Subtotals
    product_subtotal: float = Field(..., description="Product subtotal")
    installation_subtotal: float = Field(..., description="Installation subtotal")
    subtotal_before_discounts: float = Field(..., description="Subtotal before discounts")
    
    # Discounts
    membership_type: Optional[str] = Field(None, description="Applied membership type")
    product_discount_amount: float = Field(0, description="Product discount amount")
    installation_discount_amount: float = Field(0, description="Installation discount amount")
    total_discount_amount: float = Field(0, description="Total discount amount")
    bundle_savings: float = Field(0, description="Bundle discount savings")
    
    # Final pricing
    subtotal_after_discounts: float = Field(..., description="Subtotal after discounts")
    tax_rate: float = Field(0, description="Tax rate applied")
    tax_amount: float = Field(0, description="Tax amount")
    total_amount: float = Field(..., description="Final total amount")
    
    # Savings summary
    total_savings: float = Field(0, description="Total amount saved")
    savings_percentage: float = Field(0, description="Percentage saved")
    
    # Display
    formatted_display_price: str = Field(..., description="Formatted display price")
    price_display_type: str = Field("fixed", description="Price display type")


class ProductCategory(BaseModel):
    """Product category with products."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    product_count: int = Field(0, description="Number of products in category")
    sort_order: int = Field(0, description="Display order")


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


@router.get("/membership-plans/{business_id}", response_model=List[MembershipPlan])
async def get_membership_plans(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get customer membership plans for a business.
    
    Returns list of available membership plans with benefits and pricing.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Fetch membership plans with benefits
        plans_query = supabase.table("customer_membership_plans").select(
            "*, customer_membership_benefits(*)"
        ).eq("business_id", business_id).eq("is_active", True).order("sort_order")
        
        plans_result = plans_query.execute()
        
        if not plans_result.data:
            return []
        
        membership_plans = []
        for plan in plans_result.data:
            # Convert benefits
            benefits = []
            for benefit in plan.get("customer_membership_benefits", []):
                benefits.append(MembershipBenefit(
                    id=str(benefit["id"]),
                    title=benefit["title"],
                    description=benefit.get("description", ""),
                    icon=benefit.get("icon"),
                    value=benefit.get("value"),
                    is_highlighted=benefit.get("is_highlighted", False),
                    sort_order=benefit.get("sort_order", 0)
                ))
            
            # Sort benefits by sort_order
            benefits.sort(key=lambda x: x.sort_order)
            
            # Convert plan
            membership_plan = MembershipPlan(
                id=str(plan["id"]),
                name=plan["name"],
                plan_type=plan["plan_type"],
                description=plan.get("description", ""),
                tagline=plan.get("tagline"),
                price_monthly=float(plan["price_monthly"]) if plan.get("price_monthly") else None,
                price_yearly=float(plan["price_yearly"]) if plan.get("price_yearly") else None,
                yearly_savings=float(plan["yearly_savings"]) if plan.get("yearly_savings") else None,
                setup_fee=float(plan["setup_fee"]) if plan.get("setup_fee") else None,
                discount_percentage=plan.get("discount_percentage", 0),
                priority_service=plan.get("priority_service", False),
                extended_warranty=plan.get("extended_warranty", False),
                maintenance_included=plan.get("maintenance_included", False),
                emergency_response=plan.get("emergency_response", False),
                free_diagnostics=plan.get("free_diagnostics", False),
                annual_tune_ups=plan.get("annual_tune_ups", 0),
                is_active=plan.get("is_active", True),
                is_featured=plan.get("is_featured", False),
                popular_badge=plan.get("popular_badge"),
                color_scheme=plan.get("color_scheme"),
                sort_order=plan.get("sort_order", 0),
                contract_length_months=plan.get("contract_length_months"),
                cancellation_policy=plan.get("cancellation_policy"),
                benefits=benefits
            )
            
            membership_plans.append(membership_plan)
        
        return membership_plans
        
    except Exception as e:
        logger.error(f"Error fetching membership plans for {business_id}: {str(e)}")
        return []


@router.get("/service-pricing/{business_id}", response_model=List[ServicePricingCategory])
async def get_service_pricing(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by service category")
):
    """
    Get service pricing with membership discounts for a business.
    
    Returns service pricing organized by category with member pricing.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("service_membership_pricing").select("*").eq("business_id", business_id).eq("is_active", True)
        
        # Apply category filter
        if category:
            query = query.eq("service_category", category)
        
        query = query.order("service_category").order("sort_order").order("service_name")
        
        result = query.execute()
        
        if not result.data:
            return []
        
        # Group by category
        categories_dict = {}
        
        for service_pricing in result.data:
            service_category = service_pricing["service_category"]
            
            if service_category not in categories_dict:
                categories_dict[service_category] = []
            
            # Convert includes array
            includes = service_pricing.get("includes", []) or []
            
            pricing = ServicePricing(
                id=str(service_pricing["id"]),
                service_name=service_pricing["service_name"],
                service_category=service_category,
                base_price=float(service_pricing["base_price"]),
                price_display=service_pricing["price_display"],
                residential_member_price=float(service_pricing["residential_member_price"]) if service_pricing.get("residential_member_price") else None,
                commercial_member_price=float(service_pricing["commercial_member_price"]) if service_pricing.get("commercial_member_price") else None,
                premium_member_price=float(service_pricing["premium_member_price"]) if service_pricing.get("premium_member_price") else None,
                description=service_pricing.get("description"),
                includes=includes,
                duration_estimate=service_pricing.get("duration_estimate"),
                minimum_labor_fee=float(service_pricing["minimum_labor_fee"]) if service_pricing.get("minimum_labor_fee") else None,
                height_surcharge=service_pricing.get("height_surcharge", False),
                additional_tech_fee=service_pricing.get("additional_tech_fee", False),
                parts_separate=service_pricing.get("parts_separate", False),
                is_active=service_pricing.get("is_active", True),
                sort_order=service_pricing.get("sort_order", 0)
            )
            
            categories_dict[service_category].append(pricing)
        
        # Convert to ServicePricingCategory objects
        pricing_categories = []
        for category_name, services in categories_dict.items():
            pricing_categories.append(ServicePricingCategory(
                category=category_name,
                services=services
            ))
        
        # Sort categories by name
        pricing_categories.sort(key=lambda x: x.category)
        
        return pricing_categories
        
    except Exception as e:
        logger.error(f"Error fetching service pricing for {business_id}: {str(e)}")
        return []


@router.get("/product-catalog/{business_id}", response_model=List[ProductCatalogItem])
async def get_product_catalog(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search products by name or description"),
    featured_only: bool = Query(False, description="Show only featured products"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get product catalog with installation options for e-commerce display.
    
    Returns products that are available for website display with their installation options
    and pricing information for different membership tiers.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Build query for products
        query = supabase.table("products").select(
            """
            id, name, sku, description, long_description, unit_price,
            category_id, warranty_years, energy_efficiency_rating,
            requires_professional_install, install_complexity, installation_time_estimate,
            featured_image_url, gallery_images, product_highlights, technical_specs,
            meta_title, meta_description, slug, is_active, is_featured, current_stock
            """
        ).eq("business_id", business_id).eq("show_on_website", True).eq("is_active", True)
        
        # Apply filters
        if featured_only:
            query = query.eq("is_featured", True)
        if search:
            query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
        
        # Apply pagination  
        query = query.range(offset, offset + limit - 1).order("name")
        
        products_result = query.execute()
        
        if not products_result.data:
            return []
        
        # Get categories for these products
        category_ids = [p["category_id"] for p in products_result.data if p.get("category_id")]
        categories_by_id = {}
        
        if category_ids:
            categories_query = supabase.table("product_categories").select("id, name").in_("id", category_ids)
            categories_result = categories_query.execute()
            categories_by_id = {cat["id"]: cat["name"] for cat in categories_result.data or []}
        
        # Apply category filter if specified
        if category:
            filtered_products = []
            for product in products_result.data:
                category_name = categories_by_id.get(product.get("category_id"))
                if category_name == category:
                    filtered_products.append(product)
            products_result.data = filtered_products
        
        if not products_result.data:
            return []
        
        # Get installation options for these products
        product_ids = [p["id"] for p in products_result.data]
        
        install_options_query = supabase.table("product_installation_options").select(
            """
            id, product_id, option_name, description, base_install_price,
            residential_install_price, commercial_install_price, premium_install_price,
            estimated_duration_hours, complexity_multiplier, is_default,
            requirements, included_in_install
            """
        ).in_("product_id", product_ids).eq("is_active", True).order("product_id")
        
        install_options_result = install_options_query.execute()
        
        # Group installation options by product_id
        install_options_by_product = {}
        for option in install_options_result.data or []:
            product_id = option["product_id"]
            if product_id not in install_options_by_product:
                install_options_by_product[product_id] = []
            install_options_by_product[product_id].append(option)
        
        # Convert to response models
        catalog_items = []
        for product in products_result.data:
            # Get category name
            category_name = categories_by_id.get(product.get("category_id"))
            
            # Get installation options for this product
            product_install_options = install_options_by_product.get(product["id"], [])
            
            # Convert installation options
            installation_options = []
            for option in product_install_options:
                installation_option = ProductInstallationOption(
                    id=str(option["id"]),
                    option_name=option["option_name"],
                    description=option.get("description"),
                    base_install_price=float(option["base_install_price"]),
                    residential_install_price=float(option["residential_install_price"]) if option.get("residential_install_price") else None,
                    commercial_install_price=float(option["commercial_install_price"]) if option.get("commercial_install_price") else None,
                    premium_install_price=float(option["premium_install_price"]) if option.get("premium_install_price") else None,
                    estimated_duration_hours=float(option["estimated_duration_hours"]) if option.get("estimated_duration_hours") else None,
                    complexity_multiplier=float(option.get("complexity_multiplier", 1.0)),
                    is_default=option.get("is_default", False),
                    requirements=option.get("requirements", {}),
                    included_in_install=option.get("included_in_install", [])
                )
                installation_options.append(installation_option)
            
            # Create catalog item
            catalog_item = ProductCatalogItem(
                id=str(product["id"]),
                name=product["name"],
                sku=product["sku"],
                description=product.get("description"),
                long_description=product.get("long_description"),
                unit_price=float(product["unit_price"]),
                category_name=category_name,
                warranty_years=product.get("warranty_years"),
                energy_efficiency_rating=product.get("energy_efficiency_rating"),
                requires_professional_install=product.get("requires_professional_install", False),
                install_complexity=product.get("install_complexity", "standard"),
                installation_time_estimate=product.get("installation_time_estimate"),
                featured_image_url=product.get("featured_image_url"),
                gallery_images=product.get("gallery_images", []),
                product_highlights=product.get("product_highlights", []),
                technical_specs=product.get("technical_specs", {}),
                meta_title=product.get("meta_title"),
                meta_description=product.get("meta_description"),
                slug=product.get("slug"),
                is_active=product.get("is_active", True),
                is_featured=product.get("is_featured", False),
                current_stock=float(product["current_stock"]) if product.get("current_stock") else None,
                installation_options=installation_options
            )
            
            catalog_items.append(catalog_item)
        
        return catalog_items
        
    except Exception as e:
        logger.error(f"Error fetching product catalog for {business_id}: {str(e)}")
        return []


@router.get("/debug-products/{business_id}")
async def debug_products(business_id: str = Path(..., description="Business ID")):
    """Debug endpoint to check raw product data"""
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Simple query to get all products for this business
        query = supabase.table("products").select("*").eq("business_id", business_id)
        result = query.execute()
        
        # Also check total products in database (all businesses)
        all_products_query = supabase.table("products").select("business_id, name, sku").limit(10)
        all_products_result = all_products_query.execute()
        
        debug_info = {
            "total_products_for_business": len(result.data) if result.data else 0,
            "products_with_website_flag": len([p for p in result.data if p.get("show_on_website")]) if result.data else 0,
            "products_active": len([p for p in result.data if p.get("is_active")]) if result.data else 0,
            "sample_product": result.data[0] if result.data else None,
            "total_products_in_database": len(all_products_result.data) if all_products_result.data else 0,
            "all_products_sample": all_products_result.data[:3] if all_products_result.data else []
        }
        
        return debug_info
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/product-categories/{business_id}", response_model=List[ProductCategory])
async def get_product_categories(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get product categories for a business.
    
    Returns list of product categories with product counts for navigation.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Get categories with product counts
        query = supabase.table("product_categories").select(
            "id, name, description, sort_order, active_product_count"
        ).eq("business_id", business_id).eq("is_active", True).order("sort_order").order("name")
        
        result = query.execute()
        
        if not result.data:
            return []
        
        categories = []
        for category in result.data:
            categories.append(ProductCategory(
                id=str(category["id"]),
                name=category["name"],
                description=category.get("description"),
                product_count=category.get("active_product_count", 0),
                sort_order=category.get("sort_order", 0)
            ))
        
        return categories
        
    except Exception as e:
        logger.error(f"Error fetching product categories for {business_id}: {str(e)}")
        return []


@router.get("/product/{business_id}/{product_id}", response_model=ProductCatalogItem)
async def get_product_details(
    business_id: str = Path(..., description="Business ID"),
    product_id: str = Path(..., description="Product ID")
):
    """
    Get detailed product information with installation options.
    
    Returns complete product details for product detail page display.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Get product details
        product_query = supabase.table("products").select(
            """
            id, name, sku, description, long_description, unit_price,
            category_id, warranty_years, energy_efficiency_rating,
            requires_professional_install, install_complexity, installation_time_estimate,
            featured_image_url, gallery_images, product_highlights, technical_specs,
            installation_requirements, meta_title, meta_description, slug,
            is_active, is_featured, current_stock,
            product_categories(id, name)
            """
        ).eq("business_id", business_id).eq("id", product_id).eq("show_on_website", True).eq("is_active", True)
        
        product_result = product_query.execute()
        
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = product_result.data[0]
        
        # Get installation options
        install_options_query = supabase.table("product_installation_options").select(
            """
            id, option_name, description, base_install_price,
            residential_install_price, commercial_install_price, premium_install_price,
            estimated_duration_hours, complexity_multiplier, is_default,
            requirements, included_in_install
            """
        ).eq("product_id", product_id).eq("is_active", True).order("sort_order").order("option_name")
        
        install_options_result = install_options_query.execute()
        
        # Convert installation options
        installation_options = []
        for option in install_options_result.data or []:
            installation_option = ProductInstallationOption(
                id=str(option["id"]),
                option_name=option["option_name"],
                description=option.get("description"),
                base_install_price=float(option["base_install_price"]),
                residential_install_price=float(option["residential_install_price"]) if option.get("residential_install_price") else None,
                commercial_install_price=float(option["commercial_install_price"]) if option.get("commercial_install_price") else None,
                premium_install_price=float(option["premium_install_price"]) if option.get("premium_install_price") else None,
                estimated_duration_hours=float(option["estimated_duration_hours"]) if option.get("estimated_duration_hours") else None,
                complexity_multiplier=float(option.get("complexity_multiplier", 1.0)),
                is_default=option.get("is_default", False),
                requirements=option.get("requirements", {}),
                included_in_install=option.get("included_in_install", [])
            )
            installation_options.append(installation_option)
        
        # Get category info
        category_info = product.get("product_categories", {})
        category_name = category_info.get("name") if category_info else None
        
        # Create detailed product response
        product_detail = ProductCatalogItem(
            id=str(product["id"]),
            name=product["name"],
            sku=product["sku"],
            description=product.get("description"),
            long_description=product.get("long_description"),
            unit_price=float(product["unit_price"]),
            category_name=category_name,
            warranty_years=product.get("warranty_years"),
            energy_efficiency_rating=product.get("energy_efficiency_rating"),
            requires_professional_install=product.get("requires_professional_install", False),
            install_complexity=product.get("install_complexity", "standard"),
            installation_time_estimate=product.get("installation_time_estimate"),
            featured_image_url=product.get("featured_image_url"),
            gallery_images=product.get("gallery_images", []),
            product_highlights=product.get("product_highlights", []),
            technical_specs=product.get("technical_specs", {}),
            meta_title=product.get("meta_title"),
            meta_description=product.get("meta_description"),
            slug=product.get("slug"),
            is_active=product.get("is_active", True),
            is_featured=product.get("is_featured", False),
            current_stock=float(product["current_stock"]) if product.get("current_stock") else None,
            installation_options=installation_options
        )
        
        return product_detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product details for {business_id}/{product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch product details")


@router.post("/product-pricing/{business_id}/{product_id}", response_model=PricingBreakdown)
async def calculate_product_pricing(
    business_id: str = Path(..., description="Business ID"),
    product_id: str = Path(..., description="Product ID"),
    installation_option_id: Optional[str] = Query(None, description="Installation option ID"),
    quantity: int = Query(1, ge=1, le=100, description="Quantity"),
    membership_type: Optional[str] = Query(None, description="Membership type (residential, commercial, premium)")
):
    """
    Calculate detailed pricing for product + installation combination.
    
    Returns comprehensive pricing breakdown including membership discounts,
    bundle savings, tax calculations, and formatted display pricing.
    """
    
    try:
        from ....core.db import get_supabase_client
        from ....application.services.product_install_pricing_service import (
            ProductInstallPricingEngine, ProductInfo, InstallationOption, MembershipType
        )
        from decimal import Decimal
        
        supabase = get_supabase_client()
        
        # Get product information
        product_query = supabase.table("products").select(
            """
            id, name, sku, unit_price, cost_price, requires_professional_install,
            install_complexity, warranty_years, is_taxable, tax_rate
            """
        ).eq("business_id", business_id).eq("id", product_id).eq("show_on_website", True).eq("is_active", True)
        
        product_result = product_query.execute()
        
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = product_result.data[0]
        
        # Create ProductInfo object
        product_info = ProductInfo(
            id=str(product_data["id"]),
            name=product_data["name"],
            sku=product_data["sku"],
            unit_price=Decimal(str(product_data["unit_price"])),
            cost_price=Decimal(str(product_data["cost_price"])) if product_data.get("cost_price") else None,
            requires_professional_install=product_data.get("requires_professional_install", False),
            install_complexity=product_data.get("install_complexity", "standard"),
            warranty_years=product_data.get("warranty_years", 1),
            is_taxable=product_data.get("is_taxable", True),
            tax_rate=Decimal(str(product_data["tax_rate"])) if product_data.get("tax_rate") else None
        )
        
        # Default installation option if none specified
        install_option = None
        
        if installation_option_id:
            # Get specific installation option
            install_query = supabase.table("product_installation_options").select(
                """
                id, option_name, description, base_install_price, complexity_multiplier,
                residential_install_price, commercial_install_price, premium_install_price,
                estimated_duration_hours, requirements, included_in_install
                """
            ).eq("id", installation_option_id).eq("product_id", product_id).eq("is_active", True)
            
            install_result = install_query.execute()
            
            if install_result.data:
                install_data = install_result.data[0]
                install_option = InstallationOption(
                    id=str(install_data["id"]),
                    option_name=install_data["option_name"],
                    description=install_data.get("description", ""),
                    base_install_price=Decimal(str(install_data["base_install_price"])),
                    complexity_multiplier=Decimal(str(install_data.get("complexity_multiplier", 1.0))),
                    estimated_duration_hours=Decimal(str(install_data.get("estimated_duration_hours", 2.0))),
                    residential_install_price=Decimal(str(install_data["residential_install_price"])) if install_data.get("residential_install_price") else None,
                    commercial_install_price=Decimal(str(install_data["commercial_install_price"])) if install_data.get("commercial_install_price") else None,
                    premium_install_price=Decimal(str(install_data["premium_install_price"])) if install_data.get("premium_install_price") else None,
                    requirements=install_data.get("requirements", {}),
                    included_in_install=install_data.get("included_in_install", [])
                )
        
        # If no installation option but product requires installation, get default
        if not install_option and product_info.requires_professional_install:
            default_install_query = supabase.table("product_installation_options").select(
                """
                id, option_name, description, base_install_price, complexity_multiplier,
                residential_install_price, commercial_install_price, premium_install_price,
                estimated_duration_hours, requirements, included_in_install
                """
            ).eq("product_id", product_id).eq("is_default", True).eq("is_active", True)
            
            default_result = default_install_query.execute()
            
            if default_result.data:
                install_data = default_result.data[0]
                install_option = InstallationOption(
                    id=str(install_data["id"]),
                    option_name=install_data["option_name"],
                    description=install_data.get("description", ""),
                    base_install_price=Decimal(str(install_data["base_install_price"])),
                    complexity_multiplier=Decimal(str(install_data.get("complexity_multiplier", 1.0))),
                    estimated_duration_hours=Decimal(str(install_data.get("estimated_duration_hours", 2.0))),
                    residential_install_price=Decimal(str(install_data["residential_install_price"])) if install_data.get("residential_install_price") else None,
                    commercial_install_price=Decimal(str(install_data["commercial_install_price"])) if install_data.get("commercial_install_price") else None,
                    premium_install_price=Decimal(str(install_data["premium_install_price"])) if install_data.get("premium_install_price") else None,
                    requirements=install_data.get("requirements", {}),
                    included_in_install=install_data.get("included_in_install", [])
                )
        
        # Create default installation option if none found
        if not install_option:
            install_option = InstallationOption(
                id="default",
                option_name="No Installation",
                description="Product only, no installation included",
                base_install_price=Decimal('0')
            )
        
        # Parse membership type
        membership = None
        if membership_type:
            try:
                membership = MembershipType(membership_type)
            except ValueError:
                pass  # Invalid membership type, proceed without membership
        
        # Calculate pricing
        pricing_engine = ProductInstallPricingEngine()
        calculation = pricing_engine.calculate_combined_pricing(
            product_info, install_option, quantity, membership
        )
        
        # Convert to response model
        pricing_breakdown = PricingBreakdown(
            product_unit_price=float(calculation.product_unit_price),
            installation_base_price=float(calculation.installation_base_price),
            quantity=calculation.quantity,
            product_subtotal=float(calculation.product_subtotal),
            installation_subtotal=float(calculation.installation_subtotal),
            subtotal_before_discounts=float(calculation.subtotal_before_discounts),
            membership_type=calculation.membership_type.value if calculation.membership_type else None,
            product_discount_amount=float(calculation.product_discount_amount),
            installation_discount_amount=float(calculation.installation_discount_amount),
            total_discount_amount=float(calculation.total_discount_amount),
            bundle_savings=float(calculation.bundle_savings),
            subtotal_after_discounts=float(calculation.subtotal_after_discounts),
            tax_rate=float(calculation.tax_rate),
            tax_amount=float(calculation.tax_amount),
            total_amount=float(calculation.total_amount),
            total_savings=float(calculation.total_savings),
            savings_percentage=float(calculation.savings_percentage),
            formatted_display_price=calculation.formatted_display_price,
            price_display_type=calculation.price_display_type.value
        )
        
        return pricing_breakdown
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating pricing for {business_id}/{product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate pricing")


# ========================================
# SHOPPING CART API ENDPOINTS
# ========================================

# Shopping Cart Data Models
class CartItemRequest(BaseModel):
    product_id: str
    installation_option_id: Optional[str] = None
    quantity: int = Field(ge=1, le=100)
    membership_type: Optional[str] = None

class CartItem(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_sku: str
    unit_price: float
    installation_option_id: Optional[str] = None
    installation_option_name: Optional[str] = None
    installation_price: float = 0.0
    quantity: int
    item_total: float
    discount_amount: float = 0.0
    membership_discount: float = 0.0
    bundle_savings: float = 0.0

class ShoppingCart(BaseModel):
    id: str
    session_id: Optional[str] = None
    customer_id: Optional[str] = None
    status: str = "active"
    items: List[CartItem]
    membership_type: Optional[str] = None
    subtotal: float = 0.0
    total_discount: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    item_count: int = 0
    created_at: str
    updated_at: str

class CartSummary(BaseModel):
    item_count: int
    subtotal: float
    total_discount: float
    tax_amount: float
    total_amount: float
    savings_percentage: float = 0.0


@router.post("/shopping-cart/create", response_model=ShoppingCart)
async def create_shopping_cart(
    session_id: Optional[str] = Query(None, description="Session ID for guest users"),
    customer_id: Optional[str] = Query(None, description="Customer ID for logged-in users")
):
    """
    Create a new shopping cart.
    
    Creates a new cart for either guest users (session-based) or logged-in users.
    At least one of session_id or customer_id must be provided.
    """
    
    if not session_id and not customer_id:
        raise HTTPException(status_code=400, detail="Either session_id or customer_id must be provided")
    
    try:
        from ....core.db import get_supabase_client
        import uuid
        from datetime import datetime
        
        supabase = get_supabase_client()
        
        # Create new cart
        cart_data = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "customer_id": customer_id,
            "status": "active",
            "subtotal": 0.0,
            "total_discount": 0.0,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "item_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("shopping_carts").insert(cart_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create cart")
        
        cart = result.data[0]
        
        return ShoppingCart(
            id=cart["id"],
            session_id=cart.get("session_id"),
            customer_id=cart.get("customer_id"),
            status=cart["status"],
            items=[],
            subtotal=float(cart["subtotal"]),
            total_discount=float(cart["total_discount"]),
            tax_amount=float(cart["tax_amount"]),
            total_amount=float(cart["total_amount"]),
            item_count=cart["item_count"],
            created_at=cart["created_at"],
            updated_at=cart["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error creating shopping cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create shopping cart")


@router.get("/shopping-cart/{cart_identifier}", response_model=ShoppingCart)
async def get_shopping_cart(
    cart_identifier: str = Path(..., description="Cart ID or Session ID"),
    business_id: str = Query(..., description="Business ID for pricing context")
):
    """
    Get shopping cart with all items and pricing calculations.
    
    Retrieves cart by cart ID or session ID with real-time pricing updates.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Try to find cart by ID first, then by session_id
        cart_query = supabase.table("shopping_carts").select("*")
        
        if len(cart_identifier) > 20:  # Likely a UUID cart ID
            cart_query = cart_query.eq("id", cart_identifier)
        else:  # Likely a session ID
            cart_query = cart_query.eq("session_id", cart_identifier)
        
        cart_result = cart_query.execute()
        
        if not cart_result.data:
            raise HTTPException(status_code=404, detail="Shopping cart not found")
        
        cart_data = cart_result.data[0]
        cart_id = cart_data["id"]
        
        # Get cart items with product details
        items_query = supabase.table("cart_items").select(
            """
            id, product_id, installation_option_id, quantity,
            unit_price, installation_price, item_total, discount_amount,
            products(name, sku, unit_price),
            product_installation_options(option_name, base_install_price)
            """
        ).eq("cart_id", cart_id).order("created_at")
        
        items_result = items_query.execute()
        
        # Process cart items with real-time pricing
        cart_items = []
        total_subtotal = 0.0
        total_discount = 0.0
        
        for item_data in items_result.data or []:
            product = item_data.get("products", {})
            install_option = item_data.get("product_installation_options", {})
            
            # Recalculate pricing for this item (ensures up-to-date pricing)
            try:
                # Get fresh pricing calculation
                from ....application.services.product_install_pricing_service import (
                    ProductInstallPricingEngine, ProductInfo, InstallationOption, MembershipType
                )
                from decimal import Decimal
                
                pricing_engine = ProductInstallPricingEngine()
                
                # Create product info (simplified for cart calculation)
                product_info = ProductInfo(
                    id=item_data["product_id"],
                    name=product.get("name", "Unknown Product"),
                    sku=product.get("sku", ""),
                    unit_price=Decimal(str(product.get("unit_price", item_data["unit_price"]))),
                    requires_professional_install=bool(item_data.get("installation_option_id"))
                )
                
                # Create installation option if exists
                install_opt = None
                if item_data.get("installation_option_id") and install_option:
                    install_opt = InstallationOption(
                        id=item_data["installation_option_id"],
                        option_name=install_option.get("option_name", "Installation"),
                        base_install_price=Decimal(str(install_option.get("base_install_price", item_data["installation_price"])))
                    )
                
                # Parse membership type from cart
                membership = None
                if cart_data.get("membership_type"):
                    try:
                        membership = MembershipType(cart_data["membership_type"])
                    except ValueError:
                        pass
                
                # Calculate current pricing
                calculation = pricing_engine.calculate_combined_pricing(
                    product_info, install_opt, item_data["quantity"], membership
                )
                
                item_total = float(calculation.subtotal_after_discounts)
                discount_amount = float(calculation.total_discount_amount)
                
            except Exception as e:
                logger.warning(f"Failed to recalculate pricing for cart item {item_data['id']}: {str(e)}")
                # Fallback to stored values
                item_total = float(item_data["item_total"])
                discount_amount = float(item_data["discount_amount"])
            
            cart_item = CartItem(
                id=str(item_data["id"]),
                product_id=item_data["product_id"],
                product_name=product.get("name", "Unknown Product"),
                product_sku=product.get("sku", ""),
                unit_price=float(product.get("unit_price", item_data["unit_price"])),
                installation_option_id=item_data.get("installation_option_id"),
                installation_option_name=install_option.get("option_name") if install_option else None,
                installation_price=float(item_data["installation_price"]),
                quantity=item_data["quantity"],
                item_total=item_total,
                discount_amount=discount_amount
            )
            
            cart_items.append(cart_item)
            total_subtotal += item_total + discount_amount  # Subtotal before discounts
            total_discount += discount_amount
        
        # Calculate tax (8.25% default)
        tax_rate = 0.0825
        tax_amount = (total_subtotal - total_discount) * tax_rate
        total_amount = (total_subtotal - total_discount) + tax_amount
        
        # Update cart totals in database
        try:
            supabase.table("shopping_carts").update({
                "subtotal": total_subtotal,
                "total_discount": total_discount,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "item_count": len(cart_items),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", cart_id).execute()
        except Exception as e:
            logger.warning(f"Failed to update cart totals: {str(e)}")
        
        return ShoppingCart(
            id=cart_data["id"],
            session_id=cart_data.get("session_id"),
            customer_id=cart_data.get("customer_id"),
            status=cart_data["status"],
            items=cart_items,
            membership_type=cart_data.get("membership_type"),
            subtotal=total_subtotal,
            total_discount=total_discount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            item_count=len(cart_items),
            created_at=cart_data["created_at"],
            updated_at=cart_data["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching shopping cart {cart_identifier}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch shopping cart")


@router.post("/shopping-cart/{cart_id}/items", response_model=CartItem)
async def add_cart_item(
    cart_id: str = Path(..., description="Shopping cart ID"),
    item: CartItemRequest = Body(...),
    business_id: str = Query(..., description="Business ID for pricing context")
):
    """
    Add item to shopping cart with real-time pricing calculation.
    
    Adds a product with optional installation to the cart and calculates
    pricing with membership discounts and bundle savings.
    """
    
    try:
        from ....core.db import get_supabase_client
        from ....application.services.product_install_pricing_service import (
            ProductInstallPricingEngine, ProductInfo, InstallationOption, MembershipType
        )
        from decimal import Decimal
        import uuid
        from datetime import datetime
        
        supabase = get_supabase_client()
        
        # Verify cart exists
        cart_result = supabase.table("shopping_carts").select("id, membership_type").eq("id", cart_id).execute()
        if not cart_result.data:
            raise HTTPException(status_code=404, detail="Shopping cart not found")
        
        cart_data = cart_result.data[0]
        
        # Get product information
        product_query = supabase.table("products").select(
            """
            id, name, sku, unit_price, cost_price, requires_professional_install,
            install_complexity, warranty_years, is_taxable
            """
        ).eq("business_id", business_id).eq("id", item.product_id).eq("show_on_website", True).eq("is_active", True)
        
        product_result = product_query.execute()
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = product_result.data[0]
        
        # Create ProductInfo object
        product_info = ProductInfo(
            id=str(product_data["id"]),
            name=product_data["name"],
            sku=product_data["sku"],
            unit_price=Decimal(str(product_data["unit_price"])),
            cost_price=Decimal(str(product_data["cost_price"])) if product_data.get("cost_price") else None,
            requires_professional_install=product_data.get("requires_professional_install", False),
            install_complexity=product_data.get("install_complexity", "standard"),
            warranty_years=product_data.get("warranty_years", 1),
            is_taxable=product_data.get("is_taxable", True)
        )
        
        # Get installation option if specified
        install_option = None
        if item.installation_option_id:
            install_query = supabase.table("product_installation_options").select(
                """
                id, option_name, description, base_install_price, complexity_multiplier,
                residential_install_price, commercial_install_price, premium_install_price,
                estimated_duration_hours, requirements, included_in_install
                """
            ).eq("id", item.installation_option_id).eq("product_id", item.product_id).eq("is_active", True)
            
            install_result = install_query.execute()
            if install_result.data:
                install_data = install_result.data[0]
                install_option = InstallationOption(
                    id=str(install_data["id"]),
                    option_name=install_data["option_name"],
                    description=install_data.get("description", ""),
                    base_install_price=Decimal(str(install_data["base_install_price"])),
                    complexity_multiplier=Decimal(str(install_data.get("complexity_multiplier", 1.0))),
                    estimated_duration_hours=Decimal(str(install_data.get("estimated_duration_hours", 2.0))),
                    residential_install_price=Decimal(str(install_data["residential_install_price"])) if install_data.get("residential_install_price") else None,
                    commercial_install_price=Decimal(str(install_data["commercial_install_price"])) if install_data.get("commercial_install_price") else None,
                    premium_install_price=Decimal(str(install_data["premium_install_price"])) if install_data.get("premium_install_price") else None,
                    requirements=install_data.get("requirements", {}),
                    included_in_install=install_data.get("included_in_install", [])
                )
        
        # Parse membership type (prioritize item level, then cart level)
        membership = None
        membership_type = item.membership_type or cart_data.get("membership_type")
        if membership_type:
            try:
                membership = MembershipType(membership_type)
            except ValueError:
                pass  # Invalid membership type, proceed without membership
        
        # Calculate pricing
        pricing_engine = ProductInstallPricingEngine()
        calculation = pricing_engine.calculate_combined_pricing(
            product_info, install_option, item.quantity, membership
        )
        
        # Check for existing item with same product and installation option
        existing_item_query = supabase.table("cart_items").select("id, quantity").eq("cart_id", cart_id).eq("product_id", item.product_id)
        
        if item.installation_option_id:
            existing_item_query = existing_item_query.eq("installation_option_id", item.installation_option_id)
        else:
            existing_item_query = existing_item_query.is_("installation_option_id", "null")
        
        existing_item_result = existing_item_query.execute()
        
        if existing_item_result.data:
            # Update existing item quantity
            existing_item = existing_item_result.data[0]
            new_quantity = existing_item["quantity"] + item.quantity
            
            # Recalculate pricing for new quantity
            new_calculation = pricing_engine.calculate_combined_pricing(
                product_info, install_option, new_quantity, membership
            )
            
            updated_item = supabase.table("cart_items").update({
                "quantity": new_quantity,
                "unit_price": float(calculation.product_unit_price),
                "installation_price": float(calculation.installation_base_price),
                "item_total": float(new_calculation.subtotal_after_discounts),
                "discount_amount": float(new_calculation.total_discount_amount),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", existing_item["id"]).execute()
            
            if not updated_item.data:
                raise HTTPException(status_code=500, detail="Failed to update cart item")
            
            cart_item_data = updated_item.data[0]
            final_quantity = new_quantity
        else:
            # Create new cart item
            cart_item_data = {
                "id": str(uuid.uuid4()),
                "cart_id": cart_id,
                "product_id": item.product_id,
                "installation_option_id": item.installation_option_id,
                "quantity": item.quantity,
                "unit_price": float(calculation.product_unit_price),
                "installation_price": float(calculation.installation_base_price),
                "item_total": float(calculation.subtotal_after_discounts),
                "discount_amount": float(calculation.total_discount_amount),
                "membership_discount": float(calculation.product_discount_amount + calculation.installation_discount_amount),
                "bundle_savings": float(calculation.bundle_savings),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("cart_items").insert(cart_item_data).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to add item to cart")
            
            cart_item_data = result.data[0]
            final_quantity = item.quantity
        
        # Update cart membership type if provided
        if item.membership_type and item.membership_type != cart_data.get("membership_type"):
            supabase.table("shopping_carts").update({
                "membership_type": item.membership_type,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", cart_id).execute()
        
        # Return cart item response
        return CartItem(
            id=str(cart_item_data["id"]),
            product_id=cart_item_data["product_id"],
            product_name=product_info.name,
            product_sku=product_info.sku,
            unit_price=float(cart_item_data["unit_price"]),
            installation_option_id=cart_item_data.get("installation_option_id"),
            installation_option_name=install_option.option_name if install_option else None,
            installation_price=float(cart_item_data["installation_price"]),
            quantity=final_quantity,
            item_total=float(cart_item_data["item_total"]),
            discount_amount=float(cart_item_data["discount_amount"]),
            membership_discount=float(cart_item_data.get("membership_discount", 0)),
            bundle_savings=float(cart_item_data.get("bundle_savings", 0))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add item to cart")


@router.put("/shopping-cart/{cart_id}/items/{item_id}", response_model=CartItem)
async def update_cart_item(
    cart_id: str = Path(..., description="Shopping cart ID"),
    item_id: str = Path(..., description="Cart item ID"),
    quantity: int = Query(..., ge=0, le=100, description="New quantity (0 to remove)"),
    business_id: str = Query(..., description="Business ID for pricing context")
):
    """
    Update cart item quantity with real-time pricing recalculation.
    
    Updates quantity and recalculates pricing. Set quantity to 0 to remove item.
    """
    
    try:
        from ....core.db import get_supabase_client
        from datetime import datetime
        
        supabase = get_supabase_client()
        
        # Verify cart and item exist
        cart_item_query = supabase.table("cart_items").select(
            "id, cart_id, product_id, installation_option_id"
        ).eq("id", item_id).eq("cart_id", cart_id)
        
        cart_item_result = cart_item_query.execute()
        if not cart_item_result.data:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        cart_item_data = cart_item_result.data[0]
        
        if quantity == 0:
            # Remove item from cart
            supabase.table("cart_items").delete().eq("id", item_id).execute()
            raise HTTPException(status_code=204, detail="Item removed from cart")
        
        # Get product and installation info for pricing recalculation
        product_query = supabase.table("products").select(
            "id, name, sku, unit_price, cost_price, requires_professional_install, install_complexity"
        ).eq("business_id", business_id).eq("id", cart_item_data["product_id"]).eq("is_active", True)
        
        product_result = product_query.execute()
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = product_result.data[0]
        
        # Recalculate pricing with new quantity
        from ....application.services.product_install_pricing_service import (
            ProductInstallPricingEngine, ProductInfo, InstallationOption
        )
        from decimal import Decimal
        
        product_info = ProductInfo(
            id=str(product_data["id"]),
            name=product_data["name"],
            sku=product_data["sku"],
            unit_price=Decimal(str(product_data["unit_price"])),
            requires_professional_install=bool(cart_item_data.get("installation_option_id"))
        )
        
        install_option = None
        if cart_item_data.get("installation_option_id"):
            install_query = supabase.table("product_installation_options").select(
                "id, option_name, base_install_price"
            ).eq("id", cart_item_data["installation_option_id"]).eq("is_active", True)
            
            install_result = install_query.execute()
            if install_result.data:
                install_data = install_result.data[0]
                install_option = InstallationOption(
                    id=str(install_data["id"]),
                    option_name=install_data["option_name"],
                    base_install_price=Decimal(str(install_data["base_install_price"]))
                )
        
        # Calculate new pricing
        pricing_engine = ProductInstallPricingEngine()
        calculation = pricing_engine.calculate_combined_pricing(
            product_info, install_option, quantity, None  # TODO: Get membership from cart
        )
        
        # Update cart item
        updated_item = supabase.table("cart_items").update({
            "quantity": quantity,
            "item_total": float(calculation.subtotal_after_discounts),
            "discount_amount": float(calculation.total_discount_amount),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", item_id).execute()
        
        if not updated_item.data:
            raise HTTPException(status_code=500, detail="Failed to update cart item")
        
        updated_data = updated_item.data[0]
        
        return CartItem(
            id=str(updated_data["id"]),
            product_id=updated_data["product_id"],
            product_name=product_info.name,
            product_sku=product_info.sku,
            unit_price=float(calculation.product_unit_price),
            installation_option_id=updated_data.get("installation_option_id"),
            installation_option_name=install_option.option_name if install_option else None,
            installation_price=float(calculation.installation_base_price),
            quantity=quantity,
            item_total=float(updated_data["item_total"]),
            discount_amount=float(updated_data["discount_amount"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update cart item")


@router.delete("/shopping-cart/{cart_id}/items/{item_id}")
async def remove_cart_item(
    cart_id: str = Path(..., description="Shopping cart ID"),
    item_id: str = Path(..., description="Cart item ID")
):
    """
    Remove specific item from shopping cart.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Verify item exists and belongs to cart
        item_query = supabase.table("cart_items").select("id").eq("id", item_id).eq("cart_id", cart_id)
        item_result = item_query.execute()
        
        if not item_result.data:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Delete item
        supabase.table("cart_items").delete().eq("id", item_id).execute()
        
        return {"message": "Item removed from cart successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove cart item")


@router.delete("/shopping-cart/{cart_id}")
async def clear_shopping_cart(
    cart_id: str = Path(..., description="Shopping cart ID")
):
    """
    Clear all items from shopping cart or delete the cart entirely.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Verify cart exists
        cart_query = supabase.table("shopping_carts").select("id").eq("id", cart_id)
        cart_result = cart_query.execute()
        
        if not cart_result.data:
            raise HTTPException(status_code=404, detail="Shopping cart not found")
        
        # Delete all cart items
        supabase.table("cart_items").delete().eq("cart_id", cart_id).execute()
        
        # Update cart totals to zero
        from datetime import datetime
        supabase.table("shopping_carts").update({
            "subtotal": 0.0,
            "total_discount": 0.0,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "item_count": 0,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", cart_id).execute()
        
        return {"message": "Shopping cart cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear shopping cart")


@router.get("/shopping-cart/{cart_identifier}/summary", response_model=CartSummary)
async def get_cart_summary(
    cart_identifier: str = Path(..., description="Cart ID or Session ID")
):
    """
    Get cart summary with totals for header/navigation display.
    
    Returns lightweight cart summary for UI elements that need
    quick access to cart totals and item counts.
    """
    
    try:
        from ....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Find cart
        cart_query = supabase.table("shopping_carts").select(
            "id, subtotal, total_discount, tax_amount, total_amount, item_count"
        )
        
        if len(cart_identifier) > 20:  # UUID cart ID
            cart_query = cart_query.eq("id", cart_identifier)
        else:  # Session ID
            cart_query = cart_query.eq("session_id", cart_identifier)
        
        cart_result = cart_query.execute()
        
        if not cart_result.data:
            # Return empty cart summary
            return CartSummary(
                item_count=0,
                subtotal=0.0,
                total_discount=0.0,
                tax_amount=0.0,
                total_amount=0.0,
                savings_percentage=0.0
            )
        
        cart = cart_result.data[0]
        subtotal = float(cart["subtotal"])
        total_discount = float(cart["total_discount"])
        
        savings_percentage = (total_discount / subtotal * 100) if subtotal > 0 else 0.0
        
        return CartSummary(
            item_count=cart["item_count"],
            subtotal=subtotal,
            total_discount=total_discount,
            tax_amount=float(cart["tax_amount"]),
            total_amount=float(cart["total_amount"]),
            savings_percentage=savings_percentage
        )
        
    except Exception as e:
        logger.error(f"Error fetching cart summary for {cart_identifier}: {str(e)}")
        # Return empty cart on error
        return CartSummary(
            item_count=0,
            subtotal=0.0,
            total_discount=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            savings_percentage=0.0
        )


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
