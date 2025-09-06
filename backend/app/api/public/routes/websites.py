"""
Website host resolution endpoints for multi-tenant routing
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_supabase_client
from supabase import Client as SupabaseClient

logger = logging.getLogger(__name__)

router = APIRouter()

class HostResolution(BaseModel):
    """Host resolution response"""
    business_id: str
    hostname: str
    subdomain: str
    is_custom_domain: bool
    business_name: Optional[str] = None

@router.get("/resolve")
async def resolve_business_from_host(
    host: str = Query(..., description="Hostname to resolve (e.g., elite-hvac-austin.hero365.ai)"),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> HostResolution:
    """
    Resolve business ID from hostname for multi-tenant routing
    Supports both hero365.ai subdomains and custom domains
    """
    try:
        logger.info(f"🔍 [HOST-RESOLVE] Resolving business for host: {host}")
        
        # Parse hostname
        is_custom_domain = not host.endswith('.tradesites.app')
        
        if is_custom_domain:
            # Custom domain lookup - check website_configurations table
            subdomain = host
            website_config_response = supabase.table('website_configurations').select('business_id').eq('domain', host).execute()
            
            if website_config_response.data:
                business_id = website_config_response.data[0]['business_id']
                business_response = supabase.table('businesses').select('id, name, subdomain').eq('id', business_id).execute()
            else:
                business_response = {'data': []}
        else:
            # tradesites.app subdomain lookup - prefer businesses.subdomain, then fallbacks
            subdomain = host.replace('.tradesites.app', '')
            business_response = supabase.table('businesses').select('id, name, subdomain').eq('subdomain', subdomain).execute()
            
            # Fallback 1: website_configurations.subdomain mapping
            if not getattr(business_response, 'data', None):
                try:
                    wc_resp = supabase.table('website_configurations').select('business_id, subdomain').eq('subdomain', subdomain).execute()
                    if wc_resp.data:
                        business_id = wc_resp.data[0]['business_id']
                        business_response = supabase.table('businesses').select('id, name, subdomain').eq('id', business_id).execute()
                except Exception as _:
                    pass
            
            # Fallback 2: generate subdomain from business name (compatibility)
            if not getattr(business_response, 'data', None):
                try:
                    all_resp = supabase.table('businesses').select('id, name, subdomain').execute()
                    if all_resp.data:
                        import re
                        def gen_slug(n: str) -> str:
                            s = re.sub(r'[^a-zA-Z0-9\s-]', '', (n or '').lower())
                            s = re.sub(r'\s+', '-', s)
                            s = re.sub(r'-+', '-', s).strip('-')
                            return s[:50]
                        for b in all_resp.data:
                            if gen_slug(b.get('name', '')) == subdomain:
                                business_response = {'data': [b]}
                                break
                except Exception as _:
                    pass
        
        if not business_response.data:
            logger.error(f"❌ [HOST-RESOLVE] No business found for host: {host}")
            raise HTTPException(status_code=404, detail=f"No business configured for hostname: {host}")
        
        business = business_response.data[0]
        logger.info(f"✅ [HOST-RESOLVE] Direct match: {host} → {business['id']}")
        
        return HostResolution(
            business_id=business['id'],
            hostname=host,
            subdomain=business.get('subdomain', subdomain),
            is_custom_domain=is_custom_domain,
            business_name=business.get('name')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [HOST-RESOLVE] Resolution failed for {host}: {str(e)}")
        raise HTTPException(status_code=500, detail="Host resolution failed")

@router.head("/{business_id}/validate")
async def validate_business(
    business_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Quick validation that business exists and is active
    Returns 200 if valid, 404 if not found
    """
    try:
        business_response = supabase.table('businesses').select('id').eq('id', business_id).execute()
        
        if not business_response.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        return {"status": "valid"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [VALIDATE] Business validation failed for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Validation failed")

