"""
Business Services Public API

Provides public endpoints for contractor service listings and navigation.
Used by website builder for menus, sitemaps, and service pages.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Optional, Dict, Any
import logging
from pydantic import BaseModel

from app.api.deps import get_supabase_client
from app.utils.slug_resolver import get_business_service_slugs, get_business_location_slugs
from supabase import Client as SupabaseClient

logger = logging.getLogger(__name__)

router = APIRouter()


class ServiceItem(BaseModel):
    """Public service item for website consumption."""
    canonical_slug: str
    name: str
    trade_slug: Optional[str] = None
    category: Optional[str] = None
    is_emergency: bool = False
    is_featured: bool = False
    is_commercial: bool = False
    is_residential: bool = True
    sort_order: int = 0
    pricing_summary: Optional[str] = None


class LocationItem(BaseModel):
    """Public location item for website consumption."""
    location_slug: str
    name: str
    city: str
    state: str
    kind: str  # 'physical' or 'coverage'
    is_primary: bool = False
    service_radius_miles: Optional[int] = None


class NavigationResponse(BaseModel):
    """Navigation data for website menus."""
    services: List[ServiceItem]
    featured_services: List[ServiceItem]
    emergency_services: List[ServiceItem]
    service_categories: Dict[str, List[ServiceItem]]
    locations: List[LocationItem]
    primary_location: Optional[LocationItem] = None


@router.get("/services", response_model=List[ServiceItem])
async def get_business_services(
    business_id: str = Path(..., description="Business ID"),
    only_active: bool = Query(True, description="Only return active services"),
    include_pricing: bool = Query(False, description="Include pricing summary"),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[ServiceItem]:
    """
    Get all services offered by a business.
    
    This is the primary endpoint for website service listings.
    """
    try:
        logger.info(f"🔍 [API] Fetching services for business: {business_id}")
        
        # Build query
        query = supabase.table("business_services")\
            .select("""
                canonical_slug,
                service_name,
                trade_slug,
                category,
                is_emergency,
                is_featured,
                is_commercial,
                is_residential,
                sort_order,
                price_type,
                price_min,
                price_max,
                price_unit
            """)\
            .eq("business_id", business_id)\
            .order("sort_order", desc=False)\
            .order("service_name", desc=False)
            
        if only_active:
            query = query.eq("is_active", True)
            
        result = query.execute()
        
        if not result.data:
            logger.warning(f"⚠️ [API] No services found for business: {business_id}")
            return []
        
        # Convert to response format
        services = []
        for row in result.data:
            pricing_summary = None
            if include_pricing and row.get("price_type") and row.get("price_min"):
                if row["price_type"] == "range" and row.get("price_max"):
                    pricing_summary = f"${row['price_min']}-${row['price_max']}"
                    if row.get("price_unit"):
                        pricing_summary += f" per {row['price_unit']}"
                elif row["price_type"] == "fixed":
                    pricing_summary = f"${row['price_min']}"
                    if row.get("price_unit"):
                        pricing_summary += f" per {row['price_unit']}"
                elif row["price_type"] == "hourly":
                    pricing_summary = f"${row['price_min']}/hour"
                else:
                    pricing_summary = "Quote required"
            
            service = ServiceItem(
                canonical_slug=row["canonical_slug"],
                name=row["service_name"],
                trade_slug=row.get("trade_slug"),
                category=row.get("category"),
                is_emergency=row.get("is_emergency", False),
                is_featured=row.get("is_featured", False),
                is_commercial=row.get("is_commercial", False),
                is_residential=row.get("is_residential", True),
                sort_order=row.get("sort_order", 0),
                pricing_summary=pricing_summary
            )
            services.append(service)
        
        logger.info(f"✅ [API] Returning {len(services)} services for business: {business_id}")
        return services
        
    except Exception as e:
        logger.error(f"❌ [API] Error fetching services for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch business services")


@router.get("/locations", response_model=List[LocationItem])
async def get_business_locations(
    business_id: str = Path(..., description="Business ID"),
    only_active: bool = Query(True, description="Only return active locations"),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[LocationItem]:
    """
    Get all service areas/locations for a business.
    """
    try:
        logger.info(f"🔍 [API] Fetching locations for business: {business_id}")
        
        # Build query
        query = supabase.table("service_areas")\
            .select("""
                location_slug,
                area_name,
                city,
                state,
                kind,
                is_primary,
                service_radius_miles
            """)\
            .eq("business_id", business_id)\
            .order("is_primary", desc=True)\
            .order("priority_level", desc=True)\
            .order("city", desc=False)
            
        if only_active:
            query = query.eq("is_active", True)
            
        result = query.execute()
        
        if not result.data:
            logger.warning(f"⚠️ [API] No locations found for business: {business_id}")
            return []
        
        # Convert to response format
        locations = []
        for row in result.data:
            location = LocationItem(
                location_slug=row["location_slug"],
                name=row.get("area_name") or f"{row['city']}, {row['state']}",
                city=row["city"],
                state=row["state"],
                kind=row.get("kind", "coverage"),
                is_primary=row.get("is_primary", False),
                service_radius_miles=row.get("service_radius_miles")
            )
            locations.append(location)
        
        logger.info(f"✅ [API] Returning {len(locations)} locations for business: {business_id}")
        return locations
        
    except Exception as e:
        logger.error(f"❌ [API] Error fetching locations for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch business locations")


@router.get("/navigation", response_model=NavigationResponse)
async def get_business_navigation(
    business_id: str = Path(..., description="Business ID"),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> NavigationResponse:
    """
    Get structured navigation data for website menus and sitemaps.
    
    This endpoint combines services and locations into a navigation-friendly format.
    """
    try:
        logger.info(f"🔍 [API] Building navigation for business: {business_id}")
        
        # Get services and locations in parallel
        services = await get_business_services(business_id, only_active=True, supabase=supabase)
        locations = await get_business_locations(business_id, only_active=True, supabase=supabase)
        
        # Group services by category
        service_categories = {}
        featured_services = []
        emergency_services = []
        
        for service in services:
            # Add to featured if marked
            if service.is_featured:
                featured_services.append(service)
                
            # Add to emergency if marked
            if service.is_emergency:
                emergency_services.append(service)
            
            # Group by trade_slug or category
            category_key = service.trade_slug or service.category or "General"
            if category_key not in service_categories:
                service_categories[category_key] = []
            service_categories[category_key].append(service)
        
        # Find primary location
        primary_location = None
        for location in locations:
            if location.is_primary:
                primary_location = location
                break
        
        # If no primary found, use first physical location
        if not primary_location:
            for location in locations:
                if location.kind == "physical":
                    primary_location = location
                    break
        
        navigation = NavigationResponse(
            services=services,
            featured_services=featured_services,
            emergency_services=emergency_services,
            service_categories=service_categories,
            locations=locations,
            primary_location=primary_location
        )
        
        logger.info(f"✅ [API] Built navigation with {len(services)} services, {len(locations)} locations")
        return navigation
        
    except Exception as e:
        logger.error(f"❌ [API] Error building navigation for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to build navigation data")


@router.get("/service-slugs", response_model=List[str])
async def get_service_slugs_only(
    business_id: str = Path(..., description="Business ID"),
    only_active: bool = Query(True, description="Only return active services")
) -> List[str]:
    """
    Get just the canonical service slugs for a business.
    
    Lightweight endpoint for sitemap generation and URL validation.
    """
    try:
        return get_business_service_slugs(business_id, active_only=only_active)
    except Exception as e:
        logger.error(f"❌ [API] Error fetching service slugs for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch service slugs")


@router.get("/location-slugs", response_model=List[str])
async def get_location_slugs_only(
    business_id: str = Path(..., description="Business ID"),
    only_active: bool = Query(True, description="Only return active locations")
) -> List[str]:
    """
    Get just the location slugs for a business.
    
    Lightweight endpoint for sitemap generation and URL validation.
    """
    try:
        return get_business_location_slugs(business_id, active_only=only_active)
    except Exception as e:
        logger.error(f"❌ [API] Error fetching location slugs for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch location slugs")
