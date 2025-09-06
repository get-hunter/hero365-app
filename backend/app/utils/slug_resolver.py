"""
Slug Resolution Utilities

Provides canonical slug normalization and resolution for services and locations.
All frontend URLs use canonical slugs; aliases are resolved internally.
"""

import re
from typing import Optional, List
from app.api.deps import get_supabase_client


def normalize_service_slug(input_slug: str) -> str:
    """
    Normalize a service slug to canonical format.
    
    Args:
        input_slug: Raw slug input (may contain aliases, mixed case, etc.)
        
    Returns:
        Canonical slug in lowercase-hyphen format
    """
    if not input_slug:
        return ""
    
    # Basic normalization: lowercase, replace non-alphanumeric with hyphens
    normalized = re.sub(r'[^a-zA-Z0-9-]', '-', input_slug.lower().strip())
    
    # Remove multiple consecutive hyphens and trim
    normalized = re.sub(r'-+', '-', normalized).strip('-')
    
    return normalized


def normalize_location_slug(city: str, state: str) -> str:
    """
    Generate canonical location slug from city and state.
    
    Args:
        city: City name
        state: State abbreviation or name
        
    Returns:
        Canonical location slug in format "city-state"
    """
    if not city or not state:
        return ""
    
    # Normalize city and state separately
    city_clean = normalize_service_slug(city)
    state_clean = normalize_service_slug(state)
    
    return f"{city_clean}-{state_clean}"


def resolve_service_slug(input_slug: str, business_id: Optional[str] = None) -> Optional[str]:
    """
    Resolve input slug to canonical slug, checking aliases if needed.
    
    Args:
        input_slug: Input slug to resolve
        business_id: Optional business context for business-specific services
        
    Returns:
        Canonical slug if found, None if not found
    """
    if not input_slug:
        return None
        
    normalized = normalize_service_slug(input_slug)
    
    # If we have a business context, check business_services first
    if business_id:
        canonical = _resolve_business_service_slug(normalized, business_id)
        if canonical:
            return canonical
    
    # Check service_templates for global canonical slugs and aliases
    canonical = _resolve_template_slug(normalized)
    if canonical:
        return canonical
        
    # Return normalized version as fallback
    return normalized


def _resolve_business_service_slug(input_slug: str, business_id: str) -> Optional[str]:
    """Resolve slug within business_services table."""
    try:
        supabase = get_supabase_client()
        
        # Direct canonical match
        result = supabase.table("business_services")\
            .select("canonical_slug")\
            .eq("business_id", business_id)\
            .eq("canonical_slug", input_slug)\
            .eq("is_active", True)\
            .execute()
            
        if result.data:
            return result.data[0]["canonical_slug"]
            
        return None
        
    except Exception:
        return None


def _resolve_template_slug(input_slug: str) -> Optional[str]:
    """Resolve slug within service_templates, checking aliases."""
    try:
        supabase = get_supabase_client()
        
        # Direct canonical match (activity_slug or template_slug)
        result = supabase.table("service_templates")\
            .select("template_slug, activity_slug")\
            .or_(f"template_slug.eq.{input_slug},activity_slug.eq.{input_slug}")\
            .eq("status", "active")\
            .execute()
            
        if result.data:
            template = result.data[0]
            return template.get("activity_slug") or template["template_slug"]
        
        # Check aliases (if we add aliases column later)
        # This would search within aliases arrays for matches
        
        return None
        
    except Exception:
        return None


def get_business_service_slugs(business_id: str, active_only: bool = True) -> List[str]:
    """
    Get all canonical service slugs for a business.
    
    Args:
        business_id: Business identifier
        active_only: Only return active services
        
    Returns:
        List of canonical slugs
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("business_services")\
            .select("canonical_slug")\
            .eq("business_id", business_id)\
            .order("sort_order", desc=False)\
            .order("service_name", desc=False)
            
        if active_only:
            query = query.eq("is_active", True)
            
        result = query.execute()
        
        return [row["canonical_slug"] for row in result.data]
        
    except Exception:
        return []


def get_business_location_slugs(business_id: str, active_only: bool = True) -> List[str]:
    """
    Get all location slugs for a business.
    
    Args:
        business_id: Business identifier
        active_only: Only return active locations
        
    Returns:
        List of location slugs
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("service_areas")\
            .select("location_slug")\
            .eq("business_id", business_id)\
            .order("priority_level", desc=True)\
            .order("city", desc=False)
            
        if active_only:
            query = query.eq("is_active", True)
            
        result = query.execute()
        
        return [row["location_slug"] for row in result.data]
        
    except Exception:
        return []


def validate_service_location_combination(
    business_id: str, 
    service_slug: str, 
    location_slug: str
) -> bool:
    """
    Validate that a service-location combination is valid for a business.
    
    Args:
        business_id: Business identifier
        service_slug: Canonical service slug
        location_slug: Location slug
        
    Returns:
        True if combination is valid
    """
    service_slugs = get_business_service_slugs(business_id, active_only=True)
    location_slugs = get_business_location_slugs(business_id, active_only=True)
    
    return service_slug in service_slugs and location_slug in location_slugs
