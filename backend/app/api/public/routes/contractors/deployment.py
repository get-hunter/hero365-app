"""
Multi-tenant website deployment configuration endpoints
"""

import logging
import httpx
import os
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
    site_url: str  # Full URL like "https://elite-hvac-austin.hero365.ai"
    backend_url: str = "https://api.hero365.ai"
    
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
            site_url=f"https://{subdomain}.tradesites.app",
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
    Trigger automated deployment for a business website
    - Maps custom domain to Cloudflare Worker
    - No rebuilds required (multi-tenant routing)
    """
    try:
        logger.info(f"🚀 [DEPLOY] Triggering deployment for business: {business_id}")
        
        # Get deployment configuration
        config = await get_deployment_config(business_id, supabase)
        env_vars = await get_environment_variables(business_id, site_url, supabase)
        
        # Extract subdomain from site_url
        final_site_url = env_vars.NEXT_PUBLIC_SITE_URL
        subdomain = _extract_subdomain(final_site_url)
        
        # Cloudflare automation
        cf_result = await _provision_cloudflare_domain(subdomain, config.site_name)
        
        # Update business record with subdomain for host resolution
        try:
            supabase.table('businesses').update({'subdomain': subdomain}).eq('id', business_id).execute()
            logger.info(f"✅ [DEPLOY] Updated business subdomain: {business_id} → {subdomain}")
        except Exception as e:
            logger.warning(f"⚠️ [DEPLOY] Could not update subdomain (table may not have column): {str(e)}")
        
        # Store deployment record
        deployment_record = await _store_deployment_record(business_id, config, env_vars, cf_result, supabase)
        
        logger.info(f"✅ [DEPLOY] Deployment completed for: {config.site_name} → {final_site_url}")
        return deployment_record
        
    except Exception as e:
        logger.error(f"❌ [DEPLOY] Failed to trigger deployment for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

async def _provision_cloudflare_domain(subdomain: str, business_name: str) -> Dict[str, Any]:
    """Provision custom domain mapping in Cloudflare Workers"""
    
    # Required environment variables
    cf_api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    cf_account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    cf_worker_service = os.getenv('CLOUDFLARE_WORKER_SERVICE', 'hero365-website-staging')
    cf_worker_env = os.getenv('CLOUDFLARE_WORKER_ENV', 'staging')
    
    if not all([cf_api_token, cf_account_id]):
        raise HTTPException(
            status_code=500, 
            detail="Cloudflare credentials not configured. Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID"
        )
    
    hostname = f"{subdomain}.tradesites.app"
    
    logger.info(f"🌐 [CF] Mapping {hostname} to Worker {cf_worker_service}/{cf_worker_env}")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Get Zone ID for tradesites.app
        zones_url = f"https://api.cloudflare.com/client/v4/zones?name=tradesites.app"
        headers = {
            "Authorization": f"Bearer {cf_api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            zones_response = await client.get(zones_url, headers=headers)
            zones_response.raise_for_status()
            zones_data = zones_response.json()
            
            if not zones_data.get('result'):
                raise HTTPException(status_code=500, detail="tradesites.app zone not found in Cloudflare")
            
            zone_id = zones_data['result'][0]['id']
            logger.info(f"📍 [CF] Found zone ID for tradesites.app: {zone_id}")
            
            # Step 2: Create DNS record for subdomain
            dns_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
            
            # Check if DNS record already exists
            existing_dns_url = f"{dns_url}?name={hostname}&type=CNAME"
            existing_response = await client.get(existing_dns_url, headers=headers)
            existing_data = existing_response.json()
            
            if existing_data.get('result'):
                logger.info(f"ℹ️ [CF] DNS record for {hostname} already exists")
                dns_record_id = existing_data['result'][0]['id']
            else:
                # Create new DNS record pointing to Worker
                worker_hostname = f"{cf_worker_service}.{cf_account_id}.workers.dev"
                dns_payload = {
                    "type": "CNAME",
                    "name": hostname,
                    "content": worker_hostname,
                    "proxied": True,  # Enable Cloudflare proxy
                    "comment": f"Auto-created for business deployment - Worker: {cf_worker_service}"
                }
                
                dns_response = await client.post(dns_url, json=dns_payload, headers=headers)
                dns_response.raise_for_status()
                dns_result = dns_response.json()
                
                if not dns_result.get('success'):
                    raise HTTPException(
                        status_code=500,
                        detail=f"DNS record creation failed: {dns_result.get('errors', 'Unknown error')}"
                    )
                
                dns_record_id = dns_result['result']['id']
                logger.info(f"✅ [CF] Created DNS record for {hostname} → {worker_hostname}")
            
            # Step 3: Add custom hostname to Worker (if supported)
            # Note: This might require a different approach depending on your Worker setup
            worker_domain_url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account_id}/workers/scripts/{cf_worker_service}/custom-hostnames"
            
            worker_payload = {
                "hostname": hostname
            }
            
            try:
                worker_response = await client.post(worker_domain_url, json=worker_payload, headers=headers)
                if worker_response.status_code == 200:
                    logger.info(f"✅ [CF] Added custom hostname to Worker: {hostname}")
                else:
                    logger.warning(f"⚠️ [CF] Worker custom hostname API not available, DNS routing will handle it")
            except Exception as e:
                logger.warning(f"⚠️ [CF] Worker custom hostname setup skipped: {str(e)}")
            
            return {
                "hostname": hostname,
                "worker_service": cf_worker_service,
                "worker_environment": cf_worker_env,
                "zone_id": zone_id,
                "dns_record_id": dns_record_id,
                "status": "success"
            }
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"❌ [CF] Deployment failed: {e.response.status_code} - {error_detail}")
            
            raise HTTPException(
                status_code=500,
                detail=f"Cloudflare deployment failed: {error_detail}"
            )

async def _store_deployment_record(
    business_id: str, 
    config: BusinessDeploymentConfig, 
    env_vars: DeploymentEnvironment,
    cf_result: Dict[str, Any],
    supabase: SupabaseClient
) -> Dict[str, Any]:
    """Store deployment record and return response"""
    from datetime import datetime
    
    deployment_id = f"deploy_{business_id}_{int(datetime.now().timestamp())}"
    
    # TODO: Store in deployments table for tracking
    # deployment_record = {
    #     "id": deployment_id,
    #     "business_id": business_id,
    #     "hostname": cf_result["hostname"],
    #     "status": "active",
    #     "deployed_at": datetime.now().isoformat(),
    #     "cloudflare_config": cf_result
    # }
    # supabase.table('deployments').insert(deployment_record).execute()
    
    return {
        "deployment_id": deployment_id,
        "business_id": business_id,
        "site_url": env_vars.NEXT_PUBLIC_SITE_URL,
        "subdomain": config.subdomain,
        "business_name": config.site_name,
        "status": "deployed",
        "cloudflare": cf_result,
        "deployed_at": datetime.now().isoformat(),
        "estimated_propagation": "1-2 minutes"
    }

def _extract_subdomain(site_url: str) -> str:
    """Extract subdomain from site URL"""
    import re
    
    # Extract subdomain from https://subdomain.tradesites.app
    match = re.match(r'https?://([^.]+)\.tradesites\.app', site_url)
    if match:
        return match.group(1)
    
    # Fallback: extract from any URL format
    from urllib.parse import urlparse
    parsed = urlparse(site_url)
    hostname = parsed.hostname or ""
    
    if '.tradesites.app' in hostname:
        return hostname.split('.')[0]
    
    raise ValueError(f"Invalid site_url format: {site_url}")

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
