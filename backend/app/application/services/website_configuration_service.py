"""
Website Configuration Service - 10X Engineer Approach
Handles website configuration logic for the simplified website builder
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
import logging
from supabase import Client
# Legacy SEO scaffolding removed; website configuration no longer depends on it

logger = logging.getLogger(__name__)

class WebsiteConfigurationService:
    """10X approach: Simple, fast, revenue-focused"""
    
    def __init__(self, db: Client):
        self.db = db
        self.seo_scaffolding_service = None
    
    async def get_or_create_website_config(
        self,
        business_id: UUID,
        deployment_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Get existing website config or create a new one
        """
        try:
            # Try to get existing configuration
            result = self.db.table('website_configurations').select('*').eq('business_id', str(business_id)).execute()
            
            if result.data:
                config = result.data[0]
                logger.info(f"✅ Found existing website config for business {business_id}")
                return self._format_config(config)
            
            # Create new configuration
            return await self.create_website_config(business_id, deployment_type)
            
        except Exception as e:
            logger.error(f"❌ Failed to get/create website config: {e}")
            raise
    
    async def create_website_config(
        self,
        business_id: UUID,
        deployment_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Create new website configuration based on business data
        """
        try:
            # Get business data
            business_result = self.db.table('businesses').select('*').eq('id', str(business_id)).execute()
            if not business_result.data:
                raise Exception(f"Business {business_id} not found")
            
            business_data = business_result.data[0]
            
            # Get business services
            services_result = self.db.table('business_services').select('*').eq('business_id', str(business_id)).execute()
            services = services_result.data or []
            
            # Get business locations
            locations_result = self.db.table('business_locations').select('*').eq('business_id', str(business_id)).execute()
            locations = locations_result.data or []
            
            # Get business branding
            branding_result = self.db.table('business_branding').select('*').eq('business_id', str(business_id)).execute()
            branding = branding_result.data[0] if branding_result.data else None
            
            # Determine enabled pages based on available data
            enabled_pages = self._determine_enabled_pages(services, locations, deployment_type)
            
            # Generate SEO configuration
            seo_config = self._generate_seo_config(business_data, services, locations)
            
            # Legacy SEO scaffolding removed (artifacts pipeline supersedes this)
            
            # Create subdomain
            subdomain = self._generate_subdomain(business_data)
            
            # Create website configuration
            config_data = {
                'business_id': str(business_id),
                'subdomain': subdomain,
                'deployment_status': 'pending',
                'enabled_pages': enabled_pages,
                'seo_config': seo_config,
                'content_overrides': {},
                'monthly_conversions': 0,
                'estimated_monthly_revenue': 0.0
            }
            
            result = self.db.table('website_configurations').insert(config_data).execute()
            
            if result.data:
                logger.info(f"✅ Created website config for business {business_id}")
                return self._format_config(result.data[0], business_data, services, locations, branding)
            else:
                raise Exception("Failed to create website configuration")
                
        except Exception as e:
            logger.error(f"❌ Failed to create website config: {e}")
            raise
    
    def _determine_enabled_pages(self, services: list, locations: list, deployment_type: str) -> Dict[str, Any]:
        """Determine which pages should be enabled based on business data"""
        enabled_pages = {
            "home": True,
            "contact": True,
            "about": True
        }
        
        # Enable services page if services exist
        if services:
            enabled_pages["services"] = True
        
        # Enable projects page (we know from seed data it exists)
        enabled_pages["projects"] = True
        
        # Enable booking if it's a full deployment
        if deployment_type == "full_seo":
            enabled_pages["booking"] = True
            enabled_pages["products"] = False  # Disabled for HVAC business
            enabled_pages["pricing"] = False   # Disabled for now
        
        # Add location pages
        if locations:
            location_slugs = []
            for location in locations:
                city = location.get('city', '').lower().replace(' ', '-')
                state = location.get('state', '').lower()
                location_slugs.append(f"{city}-{state}")
            enabled_pages["locations"] = location_slugs
        
        return enabled_pages
    
    def _generate_seo_config(self, business_data: Dict, services: list, locations: list) -> Dict[str, Any]:
        """Generate SEO configuration"""
        business_name = business_data.get('name', 'Business')
        city = business_data.get('city', 'Local Area')
        
        return {
            "title_template": f"{{service}} in {{city}} | {business_name}",
            "meta_description": f"Professional services in {city}. Licensed, insured, and trusted by customers.",
            "keywords": [service.get('service_name', '').lower() for service in services[:5]],
            "business_schema": {
                "@type": "LocalBusiness",
                "name": business_name,
                "telephone": business_data.get('phone', ''),
                "address": {
                    "streetAddress": business_data.get('address', ''),
                    "addressLocality": business_data.get('city', ''),
                    "addressRegion": business_data.get('state', ''),
                    "postalCode": business_data.get('postal_code', '')
                }
            }
        }
    
    def _generate_subdomain(self, business_data: Dict) -> str:
        """Generate subdomain from business name"""
        name = business_data.get('name', 'business')
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        subdomain = name.lower().replace(' ', '-').replace('&', 'and')
        # Remove any non-alphanumeric characters except hyphens
        subdomain = ''.join(c for c in subdomain if c.isalnum() or c == '-')
        # Ensure it starts with a letter
        if not subdomain[0].isalpha():
            subdomain = 'business-' + subdomain
        return subdomain[:50]  # Limit length
    
    def _format_config(self, config: Dict, business_data: Dict = None, services: list = None, locations: list = None, branding: Dict = None) -> Dict[str, Any]:
        """Format configuration for API response"""
        return {
            "id": config.get('id'),
            "business_id": config.get('business_id'),
            "subdomain": config.get('subdomain'),
            "deployment_status": config.get('deployment_status'),
            "enabled_pages": config.get('enabled_pages', {}),
            "seo_config": config.get('seo_config', {}),
            "content_overrides": config.get('content_overrides', {}),
            "business_data": business_data,
            "services": services,
            "locations": locations,
            "branding": branding
        }