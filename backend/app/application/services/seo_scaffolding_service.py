"""
SEO Scaffolding Service
Handles SEO scaffolding generation for businesses - service_location_pages and service_seo_config
"""

import logging
from typing import Dict, List
from uuid import UUID
from decimal import Decimal
from supabase import Client
from app.domain.services.slug_utils import SlugUtils

logger = logging.getLogger(__name__)


class SEOScaffoldingService:
    """
    Service responsible for generating SEO scaffolding.
    Handles service_location_pages matrix and service_seo_config entries.
    """
    
    def __init__(self, db: Client):
        self.db = db
    
    async def precompute_seo_scaffolding(self, business_id: UUID, business_data: Dict, services: List, locations: List) -> Dict[str, int]:
        """
        Precompute SEO scaffolding for a business.
        Generates service_location_pages matrix and service_seo_config entries.
        """
        try:
            # Get service keys from business data
            residential_service_keys = business_data.get('selected_residential_service_keys', [])
            commercial_service_keys = business_data.get('selected_commercial_service_keys', [])
            all_service_keys = residential_service_keys + commercial_service_keys
            
            if not all_service_keys:
                logger.warning(f"No service keys found for business {business_id}")
                return {"service_location_pages": 0, "service_seo_configs": 0}
            
            # Ensure we have locations
            if not locations:
                # Create default location from business address
                city = business_data.get('city', '').strip()
                state = business_data.get('state', '').strip()
                if city and state:
                    locations = [{
                        "city": city,
                        "state": state,
                        "is_primary": True,
                        "service_radius": 25
                    }]
            
            # Generate service_location_pages matrix
            service_location_count = await self.generate_service_location_matrix(
                business_id, all_service_keys, locations, business_data
            )
            
            # Generate service_seo_config entries
            service_seo_count = await self.generate_service_seo_configs(
                all_service_keys, business_data
            )
            
            return {
                "service_location_pages": service_location_count,
                "service_seo_configs": service_seo_count,
                "services": len(all_service_keys),
                "locations": len(locations)
            }
            
        except Exception as e:
            logger.error(f"Error precomputing SEO scaffolding for business {business_id}: {str(e)}")
            return {"service_location_pages": 0, "service_seo_configs": 0, "error": str(e)}
    
    async def generate_service_location_matrix(self, business_id: UUID, service_keys: List[str], locations: List[Dict], business_data: Dict) -> int:
        """Generate service_location_pages entries for service × location combinations."""
        created_count = 0
        market_focus = business_data.get('market_focus', 'both')
        
        for service_key in service_keys:
            service_slug = SlugUtils.normalize_service_slug(service_key)
            
            for location in locations:
                # Generate location slug since business_locations table doesn't have slug field
                city = location.get('city', '')
                state = location.get('state', '')
                location_slug = SlugUtils.normalize_location_slug(f"{city}-{state}")
                
                page_url = f"/services/{service_slug}/{location_slug}"
                
                # Calculate priority score
                priority_score = self.calculate_seo_priority_score(service_key, location, market_focus)
                
                # Generate target keywords
                target_keywords = self.generate_service_location_keywords(
                    service_key, location, business_data.get('name', '')
                )
                
                # Estimate search metrics
                search_metrics = self.estimate_search_metrics(service_key, location, market_focus)
                
                # Prepare entry data
                entry_data = {
                    "service_slug": service_slug,
                    "location_slug": location_slug,
                    "page_url": page_url,
                    "priority_score": priority_score,
                    "enable_llm_enhancement": priority_score >= 70,
                    "target_keywords": target_keywords,
                    "monthly_search_volume": search_metrics["monthly_search_volume"],
                    "competition_difficulty": search_metrics["competition_difficulty"],
                    "estimated_monthly_visitors": search_metrics["estimated_monthly_visitors"],
                    "estimated_monthly_revenue": float(search_metrics["estimated_monthly_revenue"])
                }
                
                # Upsert to database
                try:
                    result = self.db.table("service_location_pages").upsert(
                        entry_data,
                        on_conflict="service_slug,location_slug"
                    ).execute()
                    
                    if result.data:
                        created_count += 1
                        logger.debug(f"Created service_location_page: {page_url}")
                        
                except Exception as e:
                    logger.error(f"Error creating service_location_page {page_url}: {str(e)}")
        
        return created_count
    
    async def generate_service_seo_configs(self, service_keys: List[str], business_data: Dict) -> int:
        """Generate service_seo_config entries for each service."""
        created_count = 0
        market_focus = business_data.get('market_focus', 'both')
        primary_trade = business_data.get('primary_trade', '')
        
        for service_key in service_keys:
            service_slug = SlugUtils.normalize_service_slug(service_key)
            service_name = SlugUtils.service_key_to_display_name(service_key)
            
            # Calculate priority
            priority_score = self.calculate_service_seo_priority(service_key, market_focus)
            
            # Generate keywords
            target_keywords = self.generate_service_base_keywords(service_key, primary_trade)
            
            # Generate meta templates
            meta_templates = self.generate_service_meta_templates(service_key, service_name)
            
            # Prepare config data
            config_data = {
                "service_name": service_name,
                "service_slug": service_slug,
                "target_keywords": target_keywords,
                "priority_score": priority_score,
                "enable_llm_enhancement": priority_score >= 75,
                "meta_title_template": meta_templates["title"],
                "meta_description_template": meta_templates["description"]
            }
            
            # Upsert to database
            try:
                result = self.db.table("service_seo_config").upsert(
                    config_data,
                    on_conflict="service_slug"
                ).execute()
                
                if result.data:
                    created_count += 1
                    logger.debug(f"Created service_seo_config: {service_slug}")
                    
            except Exception as e:
                logger.error(f"Error creating service_seo_config {service_slug}: {str(e)}")
        
        return created_count
    
    def calculate_seo_priority_score(self, service_key: str, location: Dict, market_focus: str) -> int:
        """Calculate priority score for service × location combination."""
        base_score = 50
        
        # High-priority services
        high_priority_services = [
            "emergency_hvac", "emergency_plumbing", "emergency_electrical",
            "hvac_repair", "plumbing_repair", "electrical_repair",
            "hvac_installation", "ac_installation"
        ]
        
        if service_key in high_priority_services:
            base_score += 25
        
        # Emergency services get highest priority
        if "emergency" in service_key:
            base_score += 30
        
        # Primary location gets boost
        if location.get("is_primary", False):
            base_score += 10
        
        # Market focus alignment
        if market_focus == "both":
            base_score += 5
        
        return min(100, max(1, base_score))
    
    def calculate_service_seo_priority(self, service_key: str, market_focus: str) -> int:
        """Calculate priority score for service SEO config."""
        base_score = 50
        
        # Core services get higher priority
        core_services = [
            "hvac_repair", "plumbing_repair", "electrical_repair",
            "hvac_installation", "ac_installation", "furnace_repair"
        ]
        
        if service_key in core_services:
            base_score += 20
        
        # Emergency services get highest priority
        if "emergency" in service_key:
            base_score += 25
        
        # Installation services are high value
        if "installation" in service_key:
            base_score += 15
        
        return min(100, max(1, base_score))
    
    def generate_service_location_keywords(self, service_key: str, location: Dict, business_name: str) -> List[str]:
        """Generate target keywords for service × location."""
        service_name = SlugUtils.service_key_to_display_name(service_key)
        city = location.get("city", "")
        state = location.get("state", "")
        
        keywords = [
            f"{service_name} {city}",
            f"{city} {service_name}",
            f"{service_name} {city} {state}",
            f"{service_name} near me",
            f"{city} {service_name} service",
            f"best {service_name} {city}",
            f"{service_name} repair {city}",
            f"emergency {service_name} {city}"
        ]
        
        return keywords[:8]  # Limit to top 8 keywords
    
    def generate_service_base_keywords(self, service_key: str, primary_trade: str) -> List[str]:
        """Generate base keywords for service SEO config."""
        service_name = SlugUtils.service_key_to_display_name(service_key)
        
        keywords = [
            service_name,
            f"{service_name} service",
            f"{service_name} repair",
            f"professional {service_name}",
            f"{service_name} installation",
            f"emergency {service_name}"
        ]
        
        return keywords[:6]  # Limit to top 6 base keywords
    
    def generate_service_meta_templates(self, service_key: str, service_name: str) -> Dict[str, str]:
        """Generate meta title and description templates."""
        return {
            "title": f"{service_name} Services | Professional {service_name} | {{business_name}}",
            "description": f"Expert {service_name} services by {{business_name}}. Licensed professionals, competitive pricing, and guaranteed satisfaction. Call {{phone}} for free estimate."
        }
    
    def estimate_search_metrics(self, service_key: str, location: Dict, market_focus: str) -> Dict:
        """Estimate search volume and revenue metrics."""
        # Base estimates (would be enhanced with real data)
        base_volume = 100
        
        # High-demand services
        if service_key in ["hvac_repair", "plumbing_repair", "electrical_repair"]:
            base_volume = 300
        elif "emergency" in service_key:
            base_volume = 200
        elif "installation" in service_key:
            base_volume = 150
        
        # Adjust for market focus
        if market_focus == "both":
            base_volume = int(base_volume * 1.3)
        
        # Estimate other metrics
        estimated_visitors = int(base_volume * 0.1)  # 10% CTR
        avg_job_value = 500 if "installation" in service_key else 250
        conversion_rate = 0.05  # 5% conversion rate
        estimated_revenue = estimated_visitors * conversion_rate * avg_job_value
        
        return {
            "monthly_search_volume": base_volume,
            "competition_difficulty": "medium",
            "estimated_monthly_visitors": estimated_visitors,
            "estimated_monthly_revenue": Decimal(str(round(estimated_revenue, 2)))
        }
