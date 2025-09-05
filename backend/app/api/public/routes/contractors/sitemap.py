"""
Business-specific sitemap generation endpoints
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response

from app.api.deps import get_supabase_client
from supabase import Client as SupabaseClient

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{business_id}/sitemap.xml")
async def generate_business_sitemap(
    business_id: str,
    base_url: str = "https://example.com",  # Should be passed from request headers
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Response:
    """
    Generate XML sitemap for a specific business
    """
    try:
        logger.info(f"🗺️ [SITEMAP] Generating sitemap for business: {business_id}")
        
        # Fetch business context
        business_response = supabase.table('businesses').select('*').eq('id', business_id).execute()
        if not business_response.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        business = business_response.data[0]
        
        # Fetch active services and locations (use existing endpoints)
        # Note: Using the same logic as the active endpoints for consistency
        services_response = supabase.table('business_services').select('service_slug').eq('is_active', True).execute()
        
        # For locations, we'll use a simpler approach since we don't have business-specific locations yet
        # This matches the current /api/v1/public/locations/active endpoint logic
        locations = ['austin-tx', 'cedar-park-tx', 'round-rock-tx']  # Fallback for now
        
        services = [s['service_slug'] for s in services_response.data if s.get('service_slug')]
        # locations already defined above as fallback list
        
        # Generate sitemap XML
        sitemap_xml = _generate_sitemap_xml(base_url, services, locations, business)
        
        logger.info(f"✅ [SITEMAP] Generated sitemap with {len(services)} services × {len(locations)} locations = {len(services) * len(locations)} pages")
        
        return Response(
            content=sitemap_xml,
            media_type="application/xml",
            headers={
                "Cache-Control": "public, max-age=3600",  # 1 hour cache
                "Content-Type": "application/xml; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ [SITEMAP] Failed to generate sitemap for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate sitemap")

@router.get("/{business_id}/robots.txt")
async def generate_business_robots(
    business_id: str,
    base_url: str = "https://example.com",  # Should be passed from request headers
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Response:
    """
    Generate robots.txt for a specific business
    """
    try:
        logger.info(f"🤖 [ROBOTS] Generating robots.txt for business: {business_id}")
        
        # Verify business exists
        business_response = supabase.table('businesses').select('id, name').eq('id', business_id).execute()
        if not business_response.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        business = business_response.data[0]
        
        # Generate robots.txt content
        robots_content = f"""User-Agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /_next/
Disallow: /static/

# Business: {business.get('name', 'Unknown')}
# Generated: {datetime.now().isoformat()}

Sitemap: {base_url}/sitemap.xml
"""
        
        logger.info(f"✅ [ROBOTS] Generated robots.txt for business: {business.get('name', business_id)}")
        
        return Response(
            content=robots_content,
            media_type="text/plain",
            headers={
                "Cache-Control": "public, max-age=86400",  # 24 hour cache
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ [ROBOTS] Failed to generate robots.txt for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate robots.txt")

def _generate_sitemap_xml(base_url: str, services: List[str], locations: List[str], business: Dict[str, Any]) -> str:
    """Generate XML sitemap content"""
    
    now = datetime.now().isoformat()
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Business: {business.get('name', 'Unknown')} -->
  <!-- Generated: {now} -->
  
  <!-- Homepage -->
  <url>
    <loc>{base_url}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- Hub Pages -->
  <url>
    <loc>{base_url}/services</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <url>
    <loc>{base_url}/locations</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <!-- Individual Service Pages -->"""
    
    for service in services:
        xml_content += f"""
  <url>
    <loc>{base_url}/services/{service}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""
    
    xml_content += """
  
  <!-- Service + Location Pages -->"""
    
    for service in services:
        for location in locations:
            xml_content += f"""
  <url>
    <loc>{base_url}/services/{service}/{location}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>"""
    
    xml_content += """
  
  <!-- Static Pages -->
  <url>
    <loc>{base_url}/about</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  
  <url>
    <loc>{base_url}/contact</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  
  <url>
    <loc>{base_url}/privacy</loc>
    <lastmod>{now}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  
  <url>
    <loc>{base_url}/terms</loc>
    <lastmod>{now}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  
</urlset>""".format(base_url=base_url, now=now)
    
    return xml_content
