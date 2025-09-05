"""
Multi-tenant website deployment configuration endpoints
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_supabase_client
from supabase import Client as SupabaseClient

logger = logging.getLogger(__name__)

router = APIRouter()

class BusinessDeploymentConfig(BaseModel):
    """Business deployment configuration"""
    business_id: str
    domain: Optional[str] = None  # Custom domain like "elitehvacaustin.com"
    subdomain: Optional[str] = None  # Subdomain like "elite-hvac-austin"
    site_url: str  # Full URL like "https://elite-hvac-austin.hero365.com"
    backend_url: str = "https://api.hero365.com"
    
    # SEO Configuration
    site_name: str
    site_description: str
    default_og_image: Optional[str] = None
    
    # Business branding
    primary_color: str = "#2563eb"  # Blue-600
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    
    # Features enabled
    enable_booking: bool = True
    enable_products: bool = True
    enable_reviews: bool = True
    enable_blog: bool = False

class DeploymentEnvironment(BaseModel):
    """Environment variables for deployment"""
    NEXT_PUBLIC_BUSINESS_ID: str
    NEXT_PUBLIC_SITE_URL: str
    NEXT_PUBLIC_BACKEND_URL: str
    NEXT_PUBLIC_BUSINESS_NAME: str
    NEXT_PUBLIC_BUSINESS_PHONE: str
    NEXT_PUBLIC_BUSINESS_EMAIL: str
    NEXT_PUBLIC_PRIMARY_COLOR: str
    NEXT_PUBLIC_ENABLE_BOOKING: str
    NEXT_PUBLIC_ENABLE_PRODUCTS: str
    NEXT_PUBLIC_ENABLE_REVIEWS: str

@router.get("/{business_id}/deployment-config")
async def get_deployment_config(
    business_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> BusinessDeploymentConfig:
    """
    Get deployment configuration for a business website
    """
    try:
        logger.info(f"🚀 [DEPLOY] Getting deployment config for business: {business_id}")
        
        # Fetch business data
        business_response = supabase.table('businesses').select('*').eq('id', business_id).execute()
        if not business_response.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        business = business_response.data[0]
        
        # Generate subdomain from business name
        subdomain = _generate_subdomain(business.get('name', 'business'))
        
        # Build deployment config
        config = BusinessDeploymentConfig(
            business_id=business_id,
            subdomain=subdomain,
            site_url=f"https://{subdomain}.hero365.com",
            site_name=business.get('name', 'Professional Services'),
            site_description=f"{business.get('name', 'Professional Services')} - Professional home services in {business.get('city', 'your area')}",
            primary_color=business.get('brand_color', '#2563eb'),
            logo_url=business.get('logo_url'),
            favicon_url=business.get('favicon_url'),
        )
        
        logger.info(f"✅ [DEPLOY] Generated config for: {config.site_name} → {config.site_url}")
        return config
        
    except Exception as e:
        logger.error(f"❌ [DEPLOY] Failed to get deployment config for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get deployment configuration")

@router.get("/{business_id}/env-vars")
async def get_environment_variables(
    business_id: str,
    site_url: Optional[str] = None,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> DeploymentEnvironment:
    """
    Get environment variables for deployment
    """
    try:
        logger.info(f"🔧 [ENV] Getting environment variables for business: {business_id}")
        
        # Get deployment config
        config = await get_deployment_config(business_id, supabase)
        
        # Use provided site_url or default from config
        final_site_url = site_url or config.site_url
        
        # Build environment variables
        env_vars = DeploymentEnvironment(
            NEXT_PUBLIC_BUSINESS_ID=business_id,
            NEXT_PUBLIC_SITE_URL=final_site_url,
            NEXT_PUBLIC_BACKEND_URL=config.backend_url,
            NEXT_PUBLIC_BUSINESS_NAME=config.site_name,
            NEXT_PUBLIC_BUSINESS_PHONE="",  # Will be populated from business context
            NEXT_PUBLIC_BUSINESS_EMAIL="",  # Will be populated from business context
            NEXT_PUBLIC_PRIMARY_COLOR=config.primary_color,
            NEXT_PUBLIC_ENABLE_BOOKING="true" if config.enable_booking else "false",
            NEXT_PUBLIC_ENABLE_PRODUCTS="true" if config.enable_products else "false",
            NEXT_PUBLIC_ENABLE_REVIEWS="true" if config.enable_reviews else "false",
        )
        
        logger.info(f"✅ [ENV] Generated environment variables for: {config.site_name}")
        return env_vars
        
    except Exception as e:
        logger.error(f"❌ [ENV] Failed to get environment variables for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get environment variables")

@router.post("/{business_id}/deploy")
async def trigger_deployment(
    business_id: str,
    site_url: Optional[str] = None,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Trigger deployment for a business website
    This would integrate with your deployment platform (Vercel, Netlify, etc.)
    """
    try:
        logger.info(f"🚀 [DEPLOY] Triggering deployment for business: {business_id}")
        
        # Get deployment configuration
        config = await get_deployment_config(business_id, supabase)
        env_vars = await get_environment_variables(business_id, site_url, supabase)
        
        # TODO: Integrate with deployment platform
        # Examples:
        # - Vercel API: Create new deployment with env vars
        # - Netlify API: Trigger build with environment
        # - Custom CI/CD: Webhook to build system
        
        from datetime import datetime
        
        deployment_info = {
            "business_id": business_id,
            "site_url": env_vars.NEXT_PUBLIC_SITE_URL,
            "subdomain": config.subdomain,
            "status": "triggered",
            "deployment_id": f"deploy_{business_id}_{int(datetime.now().timestamp())}",
            "environment_variables": env_vars.dict(),
            "estimated_completion": "5-10 minutes"
        }
        
        logger.info(f"✅ [DEPLOY] Deployment triggered for: {config.site_name}")
        return deployment_info
        
    except Exception as e:
        logger.error(f"❌ [DEPLOY] Failed to trigger deployment for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger deployment")

def _generate_subdomain(business_name: str) -> str:
    """Generate a clean subdomain from business name"""
    import re
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    subdomain = re.sub(r'[^a-zA-Z0-9\s-]', '', business_name.lower())
    subdomain = re.sub(r'\s+', '-', subdomain)
    subdomain = re.sub(r'-+', '-', subdomain)  # Remove multiple hyphens
    subdomain = subdomain.strip('-')  # Remove leading/trailing hyphens
    
    # Limit length and ensure it's valid
    subdomain = subdomain[:50]  # Max 50 chars
    if not subdomain or subdomain == '-':
        subdomain = 'business'
    
    return subdomain
