"""
Contractor Services API Routes

Public endpoints for retrieving contractor services and pricing.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
import logging

from .schemas import ServiceItem, ServiceCategory, MembershipPlan, ServicePricing, ServicePricingCategory

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/services/{business_id}", response_model=List[ServiceItem])
async def get_contractor_services(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    emergency_only: bool = Query(False, description="Show only emergency services")
):
    """
    Get contractor services offered by a business.
    
    Returns list of services with pricing and availability information.
    Uses the new business_services table from service template system.
    """
    
    try:
        # TODO: Replace with proper service template repository dependency injection
        # For now, use direct database query via supabase
        from .....core.db import get_supabase_client
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
async def get_contractor_service_categories(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get contractor service categories with their services grouped.
    
    Returns service categories with services organized for website navigation and menus.
    """
    
    try:
        from .....core.db import get_supabase_client
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


@router.get("/membership-plans/{business_id}", response_model=List[MembershipPlan])
async def get_membership_plans(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get customer membership plans for a business.
    
    Returns list of available membership plans with benefits and pricing.
    """
    
    try:
        from .....core.db import get_supabase_client
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
            from .schemas import MembershipBenefit
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
        from .....core.db import get_supabase_client
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
