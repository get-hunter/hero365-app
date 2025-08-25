"""
Dynamic Website Builder Service

Generates personalized websites with menus, sections, and pages 
based on the professional's service categories and offerings.
Uses the new service template system for dynamic content generation.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...infrastructure.database.repositories.supabase_service_template_repository import (
    SupabaseServiceCategoryRepository,
    SupabaseBusinessServiceRepository
)
from ...domain.service_templates.models import ServiceCategoryWithServices
from ...core.db import get_supabase_client

logger = logging.getLogger(__name__)


class ServiceCategoryPage(BaseModel):
    """Configuration for a service category page."""
    category_id: str
    category_name: str
    category_slug: str
    page_title: str
    meta_description: str
    hero_headline: str
    hero_subtitle: str
    services: List[Dict[str, Any]]
    page_url: str  # e.g., "/air-conditioning", "/plumbing"


class WebsiteStructure(BaseModel):
    """Complete website structure with dynamic pages."""
    business_info: Dict[str, Any]
    navigation_menu: List[Dict[str, Any]]
    homepage_data: Dict[str, Any]
    category_pages: List[ServiceCategoryPage]
    seo_data: Dict[str, Any]
    promotional_offers: List[Dict[str, Any]]
    trust_signals: Dict[str, Any]
    service_areas: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    

class DynamicWebsiteBuilderService:
    """
    Dynamic website builder that creates personalized websites based on 
    the professional's service categories and business information.
    """
    
    def __init__(self):
        self.supabase_client = get_supabase_client()
        self.category_repo = SupabaseServiceCategoryRepository(self.supabase_client)
        self.business_service_repo = SupabaseBusinessServiceRepository(self.supabase_client)
        
    async def generate_website_structure(
        self, 
        business: Business,
        branding: Optional[BusinessBranding] = None
    ) -> WebsiteStructure:
        """
        Generate complete website structure for a business based on their services.
        
        This creates:
        - Dynamic navigation menu
        - Service category pages
        - Homepage with service overview
        - SEO-optimized content
        """
        
        logger.info(f"Generating dynamic website structure for {business.name}")
        
        try:
            # Step 1: Get business services grouped by categories
            service_categories = await self._get_business_service_categories(business.id)
            
            # Step 2: Generate navigation menu structure
            navigation_menu = await self._generate_navigation_menu(service_categories, business)
            
            # Step 3: Generate homepage data
            homepage_data = await self._generate_homepage_data(business, service_categories, branding)
            
            # Step 4: Generate category pages
            category_pages = await self._generate_category_pages(business, service_categories)
            
            # Step 5: Generate promotional offers
            promotional_offers = await self._generate_promotional_offers(business, service_categories)
            
            # Step 6: Generate trust signals
            trust_signals = await self._generate_trust_signals(business, service_categories)
            
            # Step 7: Generate service areas
            service_areas = await self._generate_service_areas(business)
            
            # Step 8: Generate certifications
            certifications = await self._generate_certifications(business)
            
            # Step 9: Generate SEO data
            seo_data = await self._generate_seo_data(business, service_categories)
            
            # Step 10: Format business information
            business_info = self._format_business_info(business, branding)
            
            return WebsiteStructure(
                business_info=business_info,
                navigation_menu=navigation_menu,
                homepage_data=homepage_data,
                category_pages=category_pages,
                seo_data=seo_data,
                promotional_offers=promotional_offers,
                trust_signals=trust_signals,
                service_areas=service_areas,
                certifications=certifications
            )
            
        except Exception as e:
            logger.error(f"Failed to generate website structure: {str(e)}")
            raise
    
    async def _get_business_service_categories(self, business_id: UUID) -> List[Dict[str, Any]]:
        """Get business services organized by categories."""
        
        try:
            # Get categories with their services for this business
            categories_with_services = await self.category_repo.get_categories_with_services(
                business_id=business_id,
                trade_types=None  # Get all categories for this business
            )
            
            # Format data from ServiceCategoryWithServices models
            formatted_categories = []
            for category in categories_with_services:
                if category.services and len(category.services) > 0:
                    formatted_category = {
                        'id': str(category.id),
                        'name': category.name,
                        'slug': category.slug,
                        'description': category.description,
                        'services': []
                    }
                    
                    # Format services for this category
                    for service in category.services:
                        formatted_service = {
                            'id': str(service.id),
                            'name': service.name,
                            'description': service.description or '',
                            'unit_price': float(service.unit_price) if service.unit_price else None,
                            'pricing_model': service.pricing_model,
                            'unit_of_measure': service.unit_of_measure,
                            'is_emergency': service.is_emergency or False,
                            'is_featured': service.is_featured or False,
                            'estimated_duration_hours': float(service.estimated_duration_hours) if service.estimated_duration_hours else None
                        }
                        formatted_category['services'].append(formatted_service)
                    
                    formatted_categories.append(formatted_category)
            
            logger.info(f"Found {len(formatted_categories)} service categories with services")
            return formatted_categories
            
        except Exception as e:
            logger.error(f"Failed to get business service categories: {str(e)}")
            return []
    
    async def _generate_navigation_menu(
        self, 
        service_categories: List[Dict[str, Any]], 
        business: Business
    ) -> List[Dict[str, Any]]:
        """Generate dynamic navigation menu based on actual service categories the business offers."""
        
        logger.info(f"Generating navigation menu for {len(service_categories)} service categories")
        
        navigation_items = [
            {
                'label': 'Home',
                'url': '/',
                'type': 'page'
            }
        ]
        
        # Only add service categories that the business actually has services for
        active_categories = [cat for cat in service_categories if len(cat['services']) > 0]
        
        if len(active_categories) == 0:
            # No services - just add a generic services page
            navigation_items.append({
                'label': 'Services',
                'url': '/services',
                'type': 'page'
            })
            logger.warning(f"Business {business.name} has no active service categories")
            
        elif len(active_categories) == 1:
            # Single category - can either show as direct link or dropdown
            category = active_categories[0]
            navigation_items.extend([
                {
                    'label': 'Services',
                    'url': '/services', 
                    'type': 'page'
                },
                {
                    'label': f"{category['name']} Services",
                    'url': f"/{category['slug']}",
                    'type': 'page',
                    'service_count': len(category['services'])
                }
            ])
            
        elif len(active_categories) >= 2:
            # Multiple categories - create dropdown menu organized by categories
            services_menu = {
                'label': 'Services',
                'url': '/services',
                'type': 'dropdown',
                'children': []
            }
            
            # Sort categories by service count (most services first) and name
            sorted_categories = sorted(
                active_categories, 
                key=lambda x: (-len(x['services']), x['name'])
            )
            
            for category in sorted_categories:
                # Only include categories with services
                if len(category['services']) > 0:
                    services_menu['children'].append({
                        'label': category['name'],
                        'url': f"/{category['slug']}",
                        'type': 'page',
                        'service_count': len(category['services']),
                        'description': category.get('description', f"{category['name']} services")
                    })
                    
            navigation_items.append(services_menu)
            
            # If there are many categories (5+), also add direct links for top 3 categories
            if len(active_categories) >= 5:
                top_categories = sorted_categories[:3]
                for category in top_categories:
                    navigation_items.append({
                        'label': category['name'],
                        'url': f"/{category['slug']}",
                        'type': 'page',
                        'service_count': len(category['services']),
                        'is_featured': True
                    })
        
        # Add standard pages
        navigation_items.extend([
            {
                'label': 'About Us',
                'url': '/about',
                'type': 'page'
            },
            {
                'label': 'Contact',
                'url': '/contact',
                'type': 'page'
            }
        ])
        
        logger.info(f"Generated navigation with {len(navigation_items)} items for business {business.name}")
        return navigation_items
    
    async def _generate_homepage_data(
        self, 
        business: Business, 
        service_categories: List[Dict[str, Any]], 
        branding: Optional[BusinessBranding]
    ) -> Dict[str, Any]:
        """Generate homepage content data."""
        
        # Generate primary service focus for hero section
        primary_trade = business.trade_category.value if business.trade_category else 'Services'
        
        # Count total services across categories
        total_services = sum(len(cat['services']) for cat in service_categories)
        
        # Identify featured/popular services
        featured_services = []
        emergency_services = []
        
        for category in service_categories:
            for service in category['services']:
                if service.get('is_featured'):
                    featured_services.append(service)
                if service.get('is_emergency'):
                    emergency_services.append(service)
        
        # Generate hero content
        hero_data = {
            'headline': f"{business.name} - Professional {primary_trade} Services",
            'subtitle': f"Serving {', '.join(business.service_areas[:3] if business.service_areas else ['Your Area'])} • Licensed & Insured • {total_services}+ Services Available",
            'cta_buttons': [
                {
                    'text': 'Get Free Quote',
                    'action': 'open_quote',
                    'style': 'primary'
                },
                {
                    'text': 'Call Now',
                    'action': 'call',
                    'phone': business.phone_number,
                    'style': 'secondary'
                }
            ],
            'trust_indicators': [
                'Licensed & Insured',
                'Locally Owned',
                'Satisfaction Guaranteed'
            ],
            'show_emergency_banner': len(emergency_services) > 0,
            'emergency_message': '🚨 Emergency Service Available 24/7 - Call Now!' if emergency_services else None
        }
        
        # Generate services overview for homepage
        services_overview = []
        for category in service_categories[:6]:  # Show up to 6 categories on homepage
            # Get the most popular/featured service from this category
            featured_service = None
            for service in category['services']:
                if service.get('is_featured'):
                    featured_service = service
                    break
            
            # If no featured service, use the first one
            if not featured_service and category['services']:
                featured_service = category['services'][0]
            
            if featured_service:
                services_overview.append({
                    'category': category['name'],
                    'category_slug': category['slug'],
                    'title': featured_service['name'],
                    'description': featured_service['description'][:100] + '...' if len(featured_service['description']) > 100 else featured_service['description'],
                    'price': f"From ${int(featured_service['unit_price'])}" if featured_service['unit_price'] else "Free Quote",
                    'is_emergency': featured_service['is_emergency'],
                    'service_count': len(category['services'])
                })
        
        return {
            'hero': hero_data,
            'services_overview': services_overview,
            'total_categories': len(service_categories),
            'total_services': total_services,
            'emergency_available': len(emergency_services) > 0,
            'featured_services': featured_services[:3]  # Top 3 featured services
        }
    
    async def _generate_category_pages(
        self, 
        business: Business, 
        service_categories: List[Dict[str, Any]]
    ) -> List[ServiceCategoryPage]:
        """Generate individual pages for each service category."""
        
        category_pages = []
        
        for category in service_categories:
            # Generate category-specific hero content
            hero_headline = f"{category['name']} Services in {business.service_areas[0] if business.service_areas else 'Your Area'}"
            hero_subtitle = f"Professional {category['name'].lower()} services from {business.name}. Licensed, insured, and trusted by your community."
            
            # Generate meta description
            meta_description = f"Expert {category['name'].lower()} services from {business.name}. {len(category['services'])} services available. Licensed & insured. Call {business.phone_number or 'today'} for free quotes."
            
            # Format services for the page
            formatted_services = []
            for service in category['services']:
                formatted_service = {
                    'title': service['name'],
                    'description': service['description'],
                    'price': self._format_service_price(service),
                    'features': self._generate_service_features(service),
                    'is_popular': service.get('is_featured', False),
                    'is_emergency': service.get('is_emergency', False),
                    'estimated_duration': self._format_duration(service.get('estimated_duration_hours'))
                }
                formatted_services.append(formatted_service)
            
            # Create category page
            category_page = ServiceCategoryPage(
                category_id=category['id'],
                category_name=category['name'],
                category_slug=category['slug'],
                page_title=f"{category['name']} Services - {business.name}",
                meta_description=meta_description,
                hero_headline=hero_headline,
                hero_subtitle=hero_subtitle,
                services=formatted_services,
                page_url=f"/{category['slug']}"
            )
            
            category_pages.append(category_page)
        
        return category_pages
    
    def _format_service_price(self, service: Dict[str, Any]) -> str:
        """Format service price for display."""
        if not service.get('unit_price'):
            if service.get('pricing_model') == 'quote_required':
                return 'Free Quote'
            return 'Call for Pricing'
        
        price = service['unit_price']
        if service.get('pricing_model') == 'hourly':
            return f"${int(price)}/hour"
        elif service.get('pricing_model') == 'per_unit':
            unit = service.get('unit_of_measure', 'unit')
            return f"${int(price)}/{unit}"
        else:
            return f"From ${int(price)}"
    
    def _generate_service_features(self, service: Dict[str, Any]) -> List[str]:
        """Generate feature list for a service."""
        features = [
            'Licensed & Insured',
            'Professional Service'
        ]
        
        if service.get('is_emergency'):
            features.append('24/7 Emergency Available')
        
        if service.get('estimated_duration_hours'):
            duration = service['estimated_duration_hours']
            if duration <= 1:
                features.append('Quick Service')
            elif duration <= 4:
                features.append(f'{duration} Hour Service')
            else:
                features.append('Multi-Day Project')
        
        return features
    
    def _format_duration(self, duration_hours: Optional[float]) -> Optional[str]:
        """Format service duration for display."""
        if not duration_hours:
            return None
        
        if duration_hours < 1:
            minutes = int(duration_hours * 60)
            return f"{minutes} minutes"
        elif duration_hours == 1:
            return "1 hour"
        elif duration_hours < 24:
            return f"{duration_hours} hours"
        else:
            days = int(duration_hours / 24)
            return f"{days} days"
    
    async def _generate_seo_data(
        self, 
        business: Business, 
        service_categories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate SEO data for the website."""
        
        primary_location = business.service_areas[0] if business.service_areas else "Your Area"
        trade_type = business.trade_category.value if business.trade_category else "services"
        
        # Generate primary keywords
        keywords = [
            f"{trade_type} {primary_location.lower()}",
            f"{business.name.lower()}",
            f"{trade_type} contractor {primary_location.lower()}",
            f"professional {trade_type} services"
        ]
        
        # Add category-specific keywords
        for category in service_categories:
            category_name = category['name'].lower()
            keywords.extend([
                f"{category_name} {primary_location.lower()}",
                f"{category_name} services",
                f"emergency {category_name}"
            ])
        
        return {
            'site_title': f"{business.name} - Professional {trade_type.title()} Services",
            'site_description': f"Professional {trade_type} services in {primary_location}. Licensed & insured. {len(service_categories)} service categories available. Call {business.phone_number or 'today'} for free estimates.",
            'keywords': keywords[:15],  # Limit to top 15 keywords
            'business_schema': {
                '@type': 'HomeAndConstructionBusiness',
                'name': business.name,
                'telephone': business.phone_number,
                'address': {
                    '@type': 'PostalAddress',
                    'addressLocality': primary_location,
                    'addressRegion': business.state or '',
                    'postalCode': business.zip_code or '',
                    'streetAddress': business.address or ''
                },
                'serviceArea': business.service_areas,
                'priceRange': '$$'
            }
        }
    
    def _format_business_info(
        self, 
        business: Business, 
        branding: Optional[BusinessBranding]
    ) -> Dict[str, Any]:
        """Format business information for website use."""
        
        return {
            'name': business.name,
            'phone': business.phone_number,
            'email': business.business_email,
            'address': business.address or f"{business.city}, {business.state}" if business.city else "",
            'service_areas': business.service_areas,
            'description': business.description or f"Professional {business.trade_category.value if business.trade_category else 'services'} for your home and business.",
            'hours': 'Mon-Fri 8AM-6PM, Emergency Service Available',  # Default hours, should be configurable
            'logo_url': branding.logo_url if branding else None,
            'primary_color': branding.primary_color if branding else '#3B82F6',
            'secondary_color': branding.secondary_color if branding else '#10B981'
        }
    
    async def _generate_promotional_offers(
        self, 
        business: Business, 
        service_categories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate promotional offers for the business."""
        
        offers = []
        
        # Rebate offer (universal)
        offers.append({
            'id': 'rebate',
            'title': 'Quality Guaranteed',
            'subtitle': 'Enjoy Up to $1500 Rebate',
            'description': f'Your friends at {business.name} offer incredible rebates for your new efficient equipment. Reach out today to learn more!',
            'cta_text': 'More Details',
            'cta_action': 'rebate_details',
            'background_color': 'bg-gradient-to-r from-green-600 to-green-700',
            'text_color': 'text-white',
            'accent_color': 'text-green-200',
            'icon': 'gift',
            'is_active': True
        })
        
        # Service-specific offers
        hvac_categories = [cat for cat in service_categories if 'hvac' in cat['name'].lower() or 'air' in cat['name'].lower() or 'heat' in cat['name'].lower()]
        if hvac_categories:
            offers.append({
                'id': 'thermostat',
                'title': 'Hot New Offer',
                'subtitle': 'Just $50 for a Thermostat',
                'description': f'Incredible offer from your favorite contractor—smart thermostats for $50 only. Limited time offer!',
                'cta_text': 'Details here',
                'cta_action': 'thermostat_offer',
                'background_color': 'bg-gradient-to-r from-orange-600 to-red-600',
                'text_color': 'text-white',
                'accent_color': 'text-orange-200',
                'icon': 'zap',
                'is_active': True
            })
        
        # Warranty offer (universal)
        offers.append({
            'id': 'warranty',
            'title': 'Top Quality',
            'subtitle': 'Extended Warranty Up to 12 Years',
            'description': f'{business.name} offers up to 12 years of labor warranty and up to 12 years of parts warranty for your installations',
            'cta_text': 'More Details',
            'cta_action': 'warranty_details',
            'background_color': 'bg-gradient-to-r from-blue-600 to-blue-700',
            'text_color': 'text-white',
            'accent_color': 'text-blue-200',
            'icon': 'shield',
            'is_active': True
        })
        
        return offers
    
    async def _generate_trust_signals(
        self, 
        business: Business, 
        service_categories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate trust signals and ratings data."""
        
        # Calculate some basic metrics
        total_services = sum(len(cat['services']) for cat in service_categories)
        
        return {
            'average_rating': 4.9,
            'total_reviews': 1291,  # Sum of platform reviews
            'platforms': [
                {
                    'name': 'Google',
                    'rating': 4.9,
                    'review_count': 497,
                    'color': 'text-blue-600',
                    'background_color': 'bg-blue-50'
                },
                {
                    'name': 'Yelp', 
                    'rating': 4.8,
                    'review_count': 567,
                    'color': 'text-red-600',
                    'background_color': 'bg-red-50'
                },
                {
                    'name': 'Facebook',
                    'rating': 4.9,
                    'review_count': 227,
                    'color': 'text-blue-700',
                    'background_color': 'bg-blue-50'
                }
            ],
            'trust_indicators': [
                {'label': '15+ Years', 'description': 'Experience', 'icon': 'thumbs_up'},
                {'label': '24/7', 'description': 'Friendly Support', 'icon': 'users'},
                {'label': 'Same-Day', 'description': 'Service Available', 'icon': 'star'},
                {'label': '12 Years', 'description': 'Labor Warranty', 'icon': 'star'}
            ],
            'business_metrics': {
                'years_experience': 15,
                'certifications_count': 12,
                'awards_count': 5,
                'satisfaction_guarantee': '100%'
            }
        }
    
    async def _generate_service_areas(self, business: Business) -> List[Dict[str, Any]]:
        """Generate service areas information."""
        
        # Use business service areas if available, otherwise default to common areas
        base_areas = business.service_areas if business.service_areas else ['Austin', 'Round Rock', 'Cedar Park']
        
        # Expand to full service area data
        service_areas = []
        
        # Primary area (first in list)
        if base_areas:
            primary_city = base_areas[0]
            service_areas.append({
                'city': primary_city,
                'state': business.state or 'TX',
                'estimated_time': '20 minutes',
                'is_main_area': True,
                'description': 'Our primary service area with fastest response times',
                'zip_codes': []
            })
            
            # Secondary areas
            for city in base_areas[1:]:
                service_areas.append({
                    'city': city,
                    'state': business.state or 'TX',
                    'estimated_time': '25-35 minutes',
                    'is_main_area': False,
                    'description': f'Professional service in {city}',
                    'zip_codes': []
                })
        
        # Add some common surrounding areas if not enough areas
        if len(service_areas) < 6:
            additional_areas = [
                'Pflugerville', 'Georgetown', 'Leander', 'Kyle', 'Buda', 
                'Lakeway', 'Bee Cave', 'West Lake Hills', 'Manor', 'Elgin'
            ]
            
            for city in additional_areas[:6-len(service_areas)]:
                service_areas.append({
                    'city': city,
                    'state': business.state or 'TX',
                    'estimated_time': '30-45 minutes',
                    'is_main_area': False,
                    'description': f'Extended service area - {city}',
                    'zip_codes': []
                })
        
        return service_areas
    
    async def _generate_certifications(self, business: Business) -> List[Dict[str, Any]]:
        """Generate certifications and awards for the business."""
        
        trade_category = business.trade_category.value.lower() if business.trade_category else 'general'
        
        # Base certifications for all service businesses
        certifications = [
            {
                'name': 'Better Business Bureau A+',
                'issuer': 'BBB',
                'year': '2024',
                'description': 'Highest rating for business ethics and customer service',
                'category': 'rating'
            },
            {
                'name': 'HomeAdvisor Screened & Approved',
                'issuer': 'HomeAdvisor',
                'description': 'Background checked and verified contractor',
                'category': 'certification'
            },
            {
                'name': 'Google Guaranteed',
                'issuer': 'Google',
                'description': 'Licensed, insured, and background checked',
                'category': 'certification'
            },
            {
                'name': 'State Contractor License',
                'issuer': 'State Licensing Board',
                'description': 'Fully licensed contractor in good standing',
                'category': 'license'
            },
            {
                'name': 'Yelp Top Rated Business',
                'issuer': 'Yelp',
                'year': '2024',
                'description': 'Consistently high customer ratings',
                'category': 'award'
            }
        ]
        
        # Trade-specific certifications
        if 'hvac' in trade_category or 'heating' in trade_category or 'cooling' in trade_category:
            certifications.extend([
                {
                    'name': 'EPA Certified',
                    'issuer': 'Environmental Protection Agency',
                    'description': 'Certified for safe handling of refrigerants',
                    'category': 'license'
                },
                {
                    'name': 'NATE Certified',
                    'issuer': 'North American Technician Excellence',
                    'description': 'Industry-leading HVAC technician certification',
                    'category': 'certification'
                }
            ])
        
        if 'electrical' in trade_category:
            certifications.extend([
                {
                    'name': 'Master Electrician License',
                    'issuer': 'State Electrical Board',
                    'description': 'Advanced electrical contractor certification',
                    'category': 'license'
                },
                {
                    'name': 'OSHA Safety Certified',
                    'issuer': 'Occupational Safety and Health Administration',
                    'description': 'Workplace safety compliance certification',
                    'category': 'certification'
                }
            ])
        
        if 'plumbing' in trade_category:
            certifications.extend([
                {
                    'name': 'Master Plumber License',
                    'issuer': 'State Plumbing Board',
                    'description': 'Advanced plumbing contractor certification',
                    'category': 'license'
                },
                {
                    'name': 'Water Quality Association Certified',
                    'issuer': 'WQA',
                    'description': 'Water treatment and quality specialist certification',
                    'category': 'certification'
                }
            ])
        
        # Additional industry awards
        certifications.extend([
            {
                'name': 'Expertise Best Service Companies',
                'issuer': 'Expertise.com',
                'year': '2024',
                'description': 'Ranked among top local service companies',
                'category': 'award'
            },
            {
                'name': 'Three Best Rated',
                'issuer': 'ThreeBestRated.com',
                'year': '2024',
                'description': 'Top 3 service provider in local area',
                'category': 'award'
            }
        ])
        
        return certifications
