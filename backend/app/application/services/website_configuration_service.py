"""
Website Configuration Service - 10X Engineer Approach
Ultra-simple, revenue-focused website configuration
"""

from typing import Dict, List, Optional, Tuple
from uuid import UUID
import re
from datetime import datetime, timedelta

from app.infrastructure.database import get_database
from app.domain.models.website import WebsiteConfiguration, WebsiteConversion


class WebsiteConfigurationService:
    """
    10X Engineering: Ship fast, iterate based on revenue data
    """
    
    def __init__(self):
        self.db = get_database()
    
    async def create_website_configuration(
        self,
        business_id: UUID,
        custom_domain: Optional[str] = None
    ) -> WebsiteConfiguration:
        """
        Auto-configure website based on existing business data
        """
        # Get all business data from existing tables
        business = await self._get_business_data(business_id)
        branding = await self._get_or_create_branding(business_id, business)
        
        # Smart page detection based on actual data
        enabled_pages = await self._detect_enabled_pages(business_id, business)
        
        # Auto-generate SEO configuration
        seo_config = self._generate_seo_config(business)
        
        # Generate subdomain if no custom domain
        subdomain = custom_domain or self._generate_subdomain(business['name'])
        
        # Create configuration
        config = await self.db.website_configurations.create({
            'business_id': business_id,
            'subdomain': subdomain,
            'enabled_pages': enabled_pages,
            'seo_config': seo_config,
            'deployment_status': 'pending'
        })
        
        # Generate dynamic pages for SEO
        await self._generate_seo_pages(config.id, business, enabled_pages)
        
        return config
    
    async def _get_business_data(self, business_id: UUID) -> Dict:
        """
        Gather all business data from existing tables
        """
        business = await self.db.businesses.get(business_id)
        services = await self.db.business_services.list_by_business(business_id)
        locations = await self.db.business_locations.list_by_business(business_id)
        
        return {
            **business.dict(),
            'services': [s.dict() for s in services],
            'locations': [l.dict() for l in locations]
        }
    
    async def _get_or_create_branding(self, business_id: UUID, business: Dict) -> Dict:
        """
        Get existing branding or create smart defaults
        """
        branding = await self.db.business_branding.get_by_business_id(business_id)
        
        if branding:
            return branding.dict()
        
        # Create smart defaults based on trade
        trade = business.get('primary_trade', 'HVAC')
        colors = self._get_trade_colors(trade)
        
        branding = await self.db.business_branding.create({
            'business_id': business_id,
            'name': business['name'],
            'color_scheme': colors,
            'typography': {
                'heading': 'Inter',
                'body': 'Inter'
            },
            'assets': {
                'logo_url': business.get('logo_url'),
                'favicon_url': None
            }
        })
        
        return branding.dict()
    
    async def _detect_enabled_pages(self, business_id: UUID, business: Dict) -> Dict:
        """
        Smart page detection based on actual business data
        """
        # Count actual data to determine page relevance
        products_count = await self.db.products.count_by_business(business_id)
        projects_count = await self.db.featured_projects.count_by_business(business_id)
        bookable_services_count = await self.db.bookable_services.count_by_business(business_id)
        
        # Base pages (always enabled)
        pages = {
            'home': True,
            'services': True,
            'about': True,
            'contact': True
        }
        
        # Conditional pages based on actual data
        pages['products'] = products_count > 0
        pages['projects'] = projects_count > 0
        pages['booking'] = bookable_services_count > 0
        pages['pricing'] = business.get('show_public_pricing', False)
        
        # Location pages for SEO (only if multiple locations)
        if len(business.get('locations', [])) > 1:
            pages['locations'] = [
                self._slugify(f"{loc['city']}-{loc['state']}")
                for loc in business['locations']
            ]
        
        return pages
    
    def _generate_seo_config(self, business: Dict) -> Dict:
        """
        Auto-generate SEO configuration based on business data
        """
        business_name = business['name']
        trade = business.get('primary_trade', 'Service')
        city = business.get('city', 'Your Area')
        state = business.get('state', '')
        
        return {
            'title_template': f"{trade} Services in {city} | {business_name}",
            'meta_description': f"Professional {trade.lower()} services in {city}, {state}. Licensed, insured, and available 24/7. Call now for free estimate.",
            'keywords': [
                trade.lower(),
                city.lower(),
                'emergency',
                'repair',
                'installation',
                'maintenance',
                'licensed',
                'insured'
            ],
            'business_schema': {
                '@type': 'LocalBusiness',
                'name': business_name,
                'address': {
                    'streetAddress': business.get('address'),
                    'addressLocality': city,
                    'addressRegion': state,
                    'postalCode': business.get('zip_code')
                },
                'telephone': business.get('phone'),
                'url': f"https://{self._generate_subdomain(business_name)}.hero365.app"
            }
        }
    
    async def _generate_seo_pages(
        self,
        config_id: UUID,
        business: Dict,
        enabled_pages: Dict
    ) -> List[Dict]:
        """
        Generate SEO-optimized pages for maximum organic traffic
        """
        pages_created = []
        services = business.get('services', [])
        locations = business.get('locations', [])
        
        # Generate service pages
        for service in services[:10]:  # Top 10 services only
            page = await self._create_service_page(config_id, service, business)
            pages_created.append(page)
        
        # Generate location pages
        if enabled_pages.get('locations'):
            for location in locations:
                page = await self._create_location_page(config_id, location, business, services)
                pages_created.append(page)
                
                # High-value service + location combo pages
                for service in services[:5]:  # Top 5 services per location
                    combo_page = await self._create_service_location_page(
                        config_id, service, location, business
                    )
                    pages_created.append(combo_page)
        
        return pages_created
    
    async def _create_service_location_page(
        self,
        config_id: UUID,
        service: Dict,
        location: Dict,
        business: Dict
    ) -> Dict:
        """
        Create high-converting service + location landing page
        """
        service_name = service['service_name']
        city = location['city']
        state = location['state']
        business_name = business['name']
        
        slug = self._slugify(f"{service['service_slug']}-{city}-{state}")
        
        return await self.db.website_pages.create({
            'website_config_id': config_id,
            'page_type': 'service_location',
            'slug': slug,
            'title': f"{service_name} in {city}, {state} | {business_name}",
            'meta_description': f"Professional {service_name.lower()} services in {city}, {state}. Licensed, insured, and available 24/7. Call now for free estimate.",
            'h1_title': f"{service_name} Services in {city}",
            'content_blocks': {
                'hero': {
                    'title': f"Expert {service_name} in {city}",
                    'subtitle': f"Trusted {service['category']} Services Since {business.get('year_established', '2000')}",
                    'cta': 'Get Free Estimate',
                    'phone': business.get('phone')
                },
                'service_details': {
                    'description': service.get('description', ''),
                    'price_range': f"${service.get('price_min', 100)} - ${service.get('price_max', 500)}",
                    'duration': f"{service.get('duration_hours', 2)} hours average"
                },
                'service_area': {
                    'city': city,
                    'state': state,
                    'zip_codes': location.get('zip_codes', []),
                    'service_radius': location.get('service_radius', 25)
                },
                'trust_signals': {
                    'years_in_business': business.get('years_in_business', 10),
                    'certifications': business.get('certifications', []),
                    'emergency_available': business.get('emergency_available', True)
                }
            },
            'schema_markup': self._generate_service_schema(service, location, business)
        })
    
    def _generate_service_schema(self, service: Dict, location: Dict, business: Dict) -> Dict:
        """
        Generate structured data for service + location pages
        """
        return {
            '@context': 'https://schema.org',
            '@type': 'Service',
            'name': service['service_name'],
            'description': service.get('description', ''),
            'provider': {
                '@type': 'LocalBusiness',
                'name': business['name'],
                'telephone': business.get('phone'),
                'address': {
                    '@type': 'PostalAddress',
                    'addressLocality': location['city'],
                    'addressRegion': location['state']
                }
            },
            'areaServed': {
                '@type': 'City',
                'name': location['city']
            },
            'offers': {
                '@type': 'Offer',
                'priceRange': f"${service.get('price_min', 100)}-${service.get('price_max', 500)}"
            }
        }
    
    def _get_trade_colors(self, trade: str) -> Dict:
        """
        Industry-optimized color schemes that convert
        """
        trade_colors = {
            'HVAC': {
                'primary': '#1E40AF',    # Trust blue
                'secondary': '#DC2626',  # Heating red
                'accent': '#0EA5E9'      # Cooling blue
            },
            'Plumbing': {
                'primary': '#0F766E',    # Water teal
                'secondary': '#1E40AF',  # Trust blue
                'accent': '#F59E0B'      # Warning amber
            },
            'Electrical': {
                'primary': '#F59E0B',    # Electric yellow
                'secondary': '#1F2937',  # Professional gray
                'accent': '#DC2626'      # Danger red
            },
            'Roofing': {
                'primary': '#7C2D12',    # Roof brown
                'secondary': '#1E40AF',  # Trust blue
                'accent': '#F59E0B'      # Warning amber
            }
        }
        return trade_colors.get(trade, trade_colors['HVAC'])
    
    def _generate_subdomain(self, business_name: str) -> str:
        """
        Generate SEO-friendly subdomain
        """
        # Clean and slugify business name
        subdomain = re.sub(r'[^a-zA-Z0-9\s-]', '', business_name.lower())
        subdomain = re.sub(r'\s+', '-', subdomain.strip())
        subdomain = re.sub(r'-+', '-', subdomain)
        
        # Ensure it's not too long
        if len(subdomain) > 30:
            subdomain = subdomain[:30].rstrip('-')
        
        return subdomain
    
    def _slugify(self, text: str) -> str:
        """
        Convert text to URL-friendly slug
        """
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        return re.sub(r'-+', '-', slug)
    
    # Revenue tracking methods
    
    async def track_conversion(
        self,
        website_config_id: UUID,
        conversion_type: str,
        page_url: str,
        contact_info: Optional[Dict] = None,
        traffic_source: str = 'direct'
    ) -> WebsiteConversion:
        """
        Track conversion and calculate estimated value
        """
        # Estimate value based on conversion type
        value_estimates = {
            'phone_call': 150,      # Average service call value
            'form_submit': 100,     # Form leads
            'booking': 200,         # Online bookings
            'chat': 50,            # Chat interactions
            'email': 75            # Email inquiries
        }
        
        estimated_value = value_estimates.get(conversion_type, 100)
        
        conversion = await self.db.website_conversions.create({
            'website_config_id': website_config_id,
            'conversion_type': conversion_type,
            'page_url': page_url,
            'traffic_source': traffic_source,
            'estimated_value': estimated_value,
            'contact_info': contact_info or {}
        })
        
        # Trigger metrics update (handled by database trigger)
        return conversion
    
    async def get_website_roi(self, website_config_id: UUID) -> Dict:
        """
        Calculate ROI for contractor dashboard
        """
        # Get metrics from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        conversions = await self.db.website_conversions.list_by_config_and_date(
            website_config_id, thirty_days_ago
        )
        
        total_conversions = len(conversions)
        total_revenue = sum(c.estimated_value for c in conversions)
        
        # Website hosting cost (our revenue)
        monthly_cost = 49.00
        
        return {
            'monthly_conversions': total_conversions,
            'estimated_revenue': total_revenue,
            'roi_percentage': ((total_revenue - monthly_cost) / monthly_cost * 100) if monthly_cost > 0 else 0,
            'cost_per_lead': monthly_cost / max(total_conversions, 1),
            'avg_conversion_value': total_revenue / max(total_conversions, 1),
            'monthly_profit': total_revenue - monthly_cost
        }
