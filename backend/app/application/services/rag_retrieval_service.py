"""
RAG Retrieval Service for LLM Content Generation

This service retrieves relevant business context from the database to enhance
LLM-generated content with specific business information, testimonials, 
projects, and market data.
"""

from typing import Dict, List, Any, Optional
from supabase import Client
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RAGRetrievalService:
    """Service for retrieving contextual data to enhance LLM content generation."""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_business_context(self, business_id: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive business context for content generation.
        
        Args:
            business_id: The business ID to retrieve context for
            
        Returns:
            Dictionary containing business context data
        """
        try:
            context = {
                "business_info": await self._get_business_info(business_id),
                "testimonials": await self._get_testimonials(business_id),
                "featured_projects": await self._get_featured_projects(business_id),
                "products": await self._get_products(business_id),
                "service_areas": await self._get_service_areas(business_id),
                "business_services": await self._get_business_services(business_id),
                "market_data": await self._get_market_data(business_id),
            }
            
            logger.info(f"Retrieved RAG context for business {business_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving business context for {business_id}: {e}")
            return {}
    
    async def _get_business_info(self, business_id: str) -> Dict[str, Any]:
        """Get core business information."""
        try:
            result = self.supabase.table("businesses").select(
                "name,display_name,phone,email,city,state,postal_code,"
                "primary_trade,secondary_trades,market_focus,years_in_business,"
                "license_number,certifications,service_radius,emergency_available,"
                "business_hours"
            ).eq("id", business_id).execute()
            
            if result.data:
                return result.data[0]
            return {}
            
        except Exception as e:
            logger.error(f"Error retrieving business info: {e}")
            return {}
    
    async def _get_testimonials(self, business_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get customer testimonials for social proof."""
        try:
            result = self.supabase.table("testimonials").select(
                "customer_name,customer_title,customer_location,rating,"
                "testimonial_text,service_provided,project_date,source,"
                "is_featured"
            ).eq("business_id", business_id).eq("display_on_website", True).order(
                "rating", desc=True
            ).order("project_date", desc=True).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error retrieving testimonials: {e}")
            return []
    
    async def _get_featured_projects(self, business_id: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Get featured projects to showcase expertise."""
        try:
            result = self.supabase.table("featured_projects").select(
                "title,description,trade,service_category,location,"
                "completion_date,project_duration_days,project_value,"
                "before_images,after_images,challenges_faced,"
                "equipment_installed,customer_testimonial"
            ).eq("business_id", business_id).eq("is_featured", True).order(
                "completion_date", desc=True
            ).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error retrieving featured projects: {e}")
            return []
    
    async def _get_products(self, business_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Get products/equipment for content enrichment."""
        try:
            result = self.supabase.table("products").select(
                "name,description,short_description,category,brand,"
                "unit_price,weight_lbs,dimensions,requires_installation,"
                "installation_time_hours"
            ).eq("business_id", business_id).eq("is_active", True).order(
                "is_featured", desc=True
            ).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            return []
    
    async def _get_service_areas(self, business_id: str) -> List[Dict[str, Any]]:
        """Get service areas for location-specific content."""
        try:
            result = self.supabase.table("service_areas").select(
                "area_name,city,state,postal_code,service_radius_miles,"
                "travel_fee,minimum_job_amount,priority_level"
            ).eq("business_id", business_id).eq("is_active", True).order(
                "priority_level", desc=True
            ).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error retrieving service areas: {e}")
            return []
    
    async def _get_business_services(self, business_id: str) -> List[Dict[str, Any]]:
        """Get business services for content context."""
        try:
            result = self.supabase.table("business_services").select(
                "service_name,service_slug,category,description,"
                "price_type,price_min,price_max,price_unit,"
                "is_emergency,is_commercial,is_residential"
            ).eq("business_id", business_id).eq("is_active", True).order(
                "category"
            ).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error retrieving business services: {e}")
            return []
    
    async def _get_market_data(self, business_id: str) -> Dict[str, Any]:
        """Get market and competitive data."""
        try:
            # Get business location first
            business_result = self.supabase.table("businesses").select(
                "city,state,primary_trade,secondary_trades"
            ).eq("id", business_id).execute()
            
            if not business_result.data:
                return {}
                
            business = business_result.data[0]
            city = business.get("city")
            state = business.get("state")
            primary_trade = business.get("primary_trade")
            
            market_data = {
                "location": f"{city}, {state}" if city and state else "",
                "primary_trade": primary_trade,
                "secondary_trades": business.get("secondary_trades", []),
            }
            
            # Get market-specific data if available
            if city and state:
                # Enhanced market data with actual business intelligence
                market_data.update({
                    "market_size": self._determine_market_size(city, state, primary_trade),
                    "seasonal_trends": self._get_seasonal_trends(primary_trade),
                    "common_services": self._get_common_services_for_trade(primary_trade),
                    "typical_pricing": self._get_typical_pricing_ranges(primary_trade),
                    "local_competition": self._analyze_local_competition(city, state, primary_trade),
                    "market_opportunities": self._identify_market_opportunities(primary_trade),
                })
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error retrieving market data: {e}")
            return {}
    
    def _get_seasonal_trends(self, trade: str) -> List[str]:
        """Get seasonal trends for a trade."""
        seasonal_map = {
            "HVAC": [
                "Peak demand in summer (cooling) and winter (heating)",
                "Spring maintenance season for tune-ups",
                "Fall preparation for winter heating systems"
            ],
            "Plumbing": [
                "Winter pipe freeze prevention and repairs",
                "Spring outdoor plumbing preparation",
                "Year-round emergency services"
            ],
            "Electrical": [
                "Summer increased demand for electrical upgrades",
                "Holiday lighting installations in winter",
                "Spring safety inspections"
            ],
            "Roofing": [
                "Peak season in late spring and summer",
                "Storm damage repairs year-round",
                "Winter emergency repairs"
            ]
        }
        return seasonal_map.get(trade, ["Year-round service demand"])
    
    def _get_common_services_for_trade(self, trade: str) -> List[str]:
        """Get common services for a trade."""
        services_map = {
            "HVAC": [
                "AC Installation & Repair",
                "Heating System Service",
                "Duct Cleaning & Sealing",
                "Indoor Air Quality",
                "Preventive Maintenance"
            ],
            "Plumbing": [
                "Drain Cleaning",
                "Water Heater Service",
                "Pipe Repair & Replacement",
                "Fixture Installation",
                "Emergency Plumbing"
            ],
            "Electrical": [
                "Panel Upgrades",
                "Outlet & Switch Installation",
                "Lighting Installation",
                "Electrical Repairs",
                "Safety Inspections"
            ],
            "Roofing": [
                "Roof Replacement",
                "Roof Repair",
                "Gutter Installation",
                "Storm Damage Repair",
                "Roof Inspections"
            ]
        }
        return services_map.get(trade, ["General contracting services"])
    
    def _get_typical_pricing_ranges(self, trade: str) -> Dict[str, str]:
        """Get typical pricing ranges for a trade."""
        pricing_map = {
            "HVAC": {
                "service_call": "$75-$150",
                "ac_installation": "$3,000-$8,000",
                "heating_repair": "$150-$800",
                "maintenance": "$100-$300"
            },
            "Plumbing": {
                "service_call": "$75-$125",
                "drain_cleaning": "$100-$300",
                "water_heater": "$800-$2,500",
                "pipe_repair": "$150-$600"
            },
            "Electrical": {
                "service_call": "$75-$150",
                "panel_upgrade": "$1,200-$3,000",
                "outlet_installation": "$100-$300",
                "lighting": "$150-$800"
            },
            "Roofing": {
                "inspection": "$150-$400",
                "repair": "$300-$1,500",
                "replacement": "$8,000-$25,000",
                "gutter_installation": "$800-$2,000"
            }
        }
        return pricing_map.get(trade, {})
    
    def _determine_market_size(self, city: str, state: str, trade: str) -> str:
        """Determine market size based on location and trade."""
        # This could be enhanced with actual market research APIs
        major_cities = ["Austin", "Houston", "Dallas", "San Antonio", "Fort Worth", "El Paso"]
        
        if city in major_cities:
            return "Large - Major metropolitan area with high demand"
        elif state == "TX":
            return "Medium - Growing Texas market with good opportunities"
        else:
            return "Variable - Market size depends on local demographics"
    
    def _analyze_local_competition(self, city: str, state: str, trade: str) -> Dict[str, Any]:
        """Analyze local competition levels."""
        # This could be enhanced with actual competitor analysis
        return {
            "level": "Moderate",
            "key_factors": [
                "Established local contractors",
                "National franchise presence",
                "Seasonal demand fluctuations"
            ],
            "opportunities": [
                "Digital marketing advantage",
                "Specialized service offerings",
                "Customer service differentiation"
            ]
        }
    
    def _identify_market_opportunities(self, trade: str) -> List[str]:
        """Identify market opportunities for the trade."""
        opportunities_map = {
            "HVAC": [
                "Energy efficiency upgrades",
                "Smart home integration",
                "Indoor air quality solutions",
                "Preventive maintenance contracts"
            ],
            "Plumbing": [
                "Water conservation solutions",
                "Smart leak detection systems",
                "Tankless water heater installations",
                "Bathroom remodeling services"
            ],
            "Electrical": [
                "EV charging station installations",
                "Solar panel integration",
                "Home automation systems",
                "Electrical safety inspections"
            ],
            "Roofing": [
                "Solar-ready roof installations",
                "Storm damage restoration",
                "Energy-efficient roofing materials",
                "Gutter protection systems"
            ]
        }
        return opportunities_map.get(trade, [
            "Digital service delivery",
            "Maintenance service contracts",
            "Emergency response services"
        ])
    
    async def get_service_specific_context(
        self, 
        business_id: str, 
        service_slug: str, 
        location_slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get context specific to a service and optionally a location.
        
        Args:
            business_id: The business ID
            service_slug: The service slug (e.g., 'ac-installation')
            location_slug: Optional location slug for location-specific content
            
        Returns:
            Service-specific context data
        """
        try:
            # Get base business context
            context = await self.get_business_context(business_id)
            
            # Get service-specific data
            service_result = self.supabase.table("business_services").select(
                "*"
            ).eq("business_id", business_id).eq("service_slug", service_slug).execute()
            
            if service_result.data:
                context["target_service"] = service_result.data[0]
            
            # Get location-specific data if provided
            if location_slug:
                location_result = self.supabase.table("service_areas").select(
                    "*"
                ).eq("business_id", business_id).ilike("area_name", f"%{location_slug}%").execute()
                
                if location_result.data:
                    context["target_location"] = location_result.data[0]
            
            # Enhanced filtering for testimonials and projects
            if "target_service" in context:
                service_category = context["target_service"].get("category")
                service_name = context["target_service"].get("service_name", "")
                
                if service_category or service_name:
                    # Filter testimonials with fuzzy matching
                    relevant_testimonials = []
                    for testimonial in context.get("testimonials", []):
                        service_provided = testimonial.get("service_provided", "").lower()
                        if (service_category and service_category.lower() in service_provided) or \
                           (service_name and any(word in service_provided for word in service_name.lower().split())):
                            relevant_testimonials.append(testimonial)
                    
                    context["testimonials"] = sorted(
                        relevant_testimonials, 
                        key=lambda x: x.get("rating", 0), 
                        reverse=True
                    )[:5]  # Top 5 by rating
                    
                    # Filter projects with better matching
                    relevant_projects = []
                    for project in context.get("featured_projects", []):
                        project_category = project.get("service_category", "").lower()
                        project_title = project.get("title", "").lower()
                        
                        if (service_category and service_category.lower() in project_category) or \
                           (service_name and any(word in project_title for word in service_name.lower().split())):
                            relevant_projects.append(project)
                    
                    context["featured_projects"] = sorted(
                        relevant_projects,
                        key=lambda x: x.get("completion_date", "1900-01-01"),
                        reverse=True
                    )[:3]  # Most recent 3 projects
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving service-specific context: {e}")
            return {}
