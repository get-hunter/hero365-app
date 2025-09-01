"""
SEO Website Generator Service
Handles the generation of all SEO-optimized pages for a contractor's website
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
import logging

from app.core.config import settings
from app.infrastructure.database.models import (
    Business, BusinessService, LocationPage, GeneratedSEOPage,
    SEOContentTemplate, ServiceSEOConfig
)
from app.domain.entities.seo_generation import SEOGenerationResult, PageContent

logger = logging.getLogger(__name__)

class SEOWebsiteGeneratorService:
    """
    Service to generate complete SEO websites with 900+ optimized pages
    """
    
    def __init__(self, business_id: str, config: dict, db: Session):
        self.business_id = business_id
        self.config = config
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.generation_start_time = time.time()
        
        # Cost tracking
        self.template_pages_cost = 0.0
        self.llm_pages_cost = 0.0
        self.total_tokens_used = 0
        
    async def generate_full_seo_website(self) -> SEOGenerationResult:
        """
        Generate complete SEO website with all pages
        
        Returns:
            SEOGenerationResult with metrics and page counts
        """
        logger.info(f"Starting SEO generation for business {self.business_id}")
        
        try:
            # Load business data
            business_data = await self._load_business_data()
            services = await self._load_services()
            locations = await self._load_service_areas()
            
            logger.info(f"Loaded {len(services)} services and {len(locations)} locations")
            
            # Generate pages in parallel for maximum speed
            template_pages, enhanced_pages, meta_pages = await asyncio.gather(
                self._generate_template_pages(business_data, services, locations),
                self._generate_llm_enhanced_pages(business_data, services, locations),
                self._generate_meta_pages(business_data, services, locations)
            )
            
            # Combine all pages
            all_pages = {**template_pages, **enhanced_pages, **meta_pages}
            
            # Generate sitemap and robots.txt
            sitemap_entries = self._generate_sitemap(all_pages)
            robots_txt = self._generate_robots_txt()
            
            # Store all pages in database
            await self._store_generated_pages(all_pages)
            
            # Calculate final metrics
            generation_time = time.time() - self.generation_start_time
            
            result = SEOGenerationResult(
                total_pages=len(all_pages),
                template_pages=len(template_pages),
                enhanced_pages=len(enhanced_pages),
                meta_pages=len(meta_pages),
                sitemap_entries=len(sitemap_entries),
                generation_time=generation_time,
                cost_breakdown={
                    "template_pages": self.template_pages_cost,
                    "llm_enhanced": self.llm_pages_cost,
                    "total": self.template_pages_cost + self.llm_pages_cost,
                    "tokens_used": self.total_tokens_used
                }
            )
            
            logger.info(f"SEO generation completed: {result.total_pages} pages in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"SEO generation failed: {e}")
            raise
    
    async def _load_business_data(self) -> dict:
        """Load business information from database"""
        business = self.db.query(Business).filter(Business.id == self.business_id).first()
        if not business:
            raise ValueError(f"Business {self.business_id} not found")
        
        return {
            "id": str(business.id),
            "name": business.business_name,
            "phone": business.phone_number,
            "email": business.business_email,
            "address": business.address,
            "city": business.city,
            "state": business.state,
            "zip_code": business.zip_code,
            "years_in_business": business.years_in_business or 10,
            "license_number": business.license_number or "Licensed & Insured",
            "description": business.description,
            "trades": business.trades or ["hvac"],
            "service_areas": business.service_areas or [f"{business.city}, {business.state}"],
            "emergency_service": True,
            "average_rating": 4.8,
            "total_reviews": 150
        }
    
    async def _load_services(self) -> List[dict]:
        """Load active services for the business"""
        services = self.db.query(BusinessService).filter(
            BusinessService.business_id == self.business_id,
            BusinessService.is_active == True
        ).all()
        
        return [
            {
                "id": str(service.id),
                "name": service.name,
                "slug": service.slug or service.name.lower().replace(" ", "-"),
                "description": service.description,
                "category": service.category,
                "base_price": float(service.base_price) if service.base_price else None,
                "is_emergency": service.is_emergency or False,
                "keywords": service.keywords or []
            }
            for service in services
        ]
    
    async def _load_service_areas(self) -> List[dict]:
        """Load service areas/locations for the business"""
        locations = self.db.query(LocationPage).filter(
            LocationPage.business_id == self.business_id,
            LocationPage.is_active == True
        ).all()
        
        # If no locations exist, create default from business address
        if not locations:
            business = self.db.query(Business).filter(Business.id == self.business_id).first()
            return [{
                "id": "default",
                "city": business.city,
                "state": business.state,
                "slug": f"{business.city.lower()}-{business.state.lower()}",
                "zip_codes": [business.zip_code] if business.zip_code else [],
                "service_radius_miles": 25,
                "population": 100000,
                "monthly_searches": 1000,
                "competition_level": "medium"
            }]
        
        return [
            {
                "id": str(location.id),
                "city": location.city,
                "state": location.state,
                "slug": location.slug,
                "zip_codes": location.zip_codes or [],
                "service_radius_miles": location.service_radius_miles or 25,
                "population": location.population,
                "monthly_searches": location.monthly_searches or 500,
                "competition_level": location.competition_level or "medium"
            }
            for location in locations
        ]
    
    async def _generate_template_pages(
        self, 
        business: dict, 
        services: List[dict], 
        locations: List[dict]
    ) -> Dict[str, PageContent]:
        """
        Generate template-based pages (90% of all pages)
        Fast generation using variable substitution
        """
        logger.info("Generating template-based pages...")
        pages = {}
        
        # Load templates from database
        templates = await self._load_seo_templates()
        
        # Generate service overview pages
        for service in services:
            page_url = f"/services/{service['slug']}"
            pages[page_url] = self._apply_template(
                templates['service_overview'],
                {**business, **service, "locations": locations}
            )
        
        # Generate location hub pages
        for location in locations:
            page_url = f"/locations/{location['slug']}"
            pages[page_url] = self._apply_template(
                templates['location_hub'],
                {**business, **location, "services": services}
            )
        
        # Generate service + location combination pages
        for service in services:
            for location in locations:
                # Standard service page
                page_url = f"/services/{service['slug']}/{location['slug']}"
                pages[page_url] = self._apply_template(
                    templates['service_location'],
                    {**business, **service, **location}
                )
                
                # Emergency variant
                if service.get('is_emergency'):
                    page_url = f"/emergency/{service['slug']}/{location['slug']}"
                    pages[page_url] = self._apply_template(
                        templates['emergency_service'],
                        {**business, **service, **location}
                    )
                
                # Commercial variant
                page_url = f"/commercial/{service['slug']}/{location['slug']}"
                pages[page_url] = self._apply_template(
                    templates['commercial_service'],
                    {**business, **service, **location}
                )
                
                # Residential variant
                page_url = f"/residential/{service['slug']}/{location['slug']}"
                pages[page_url] = self._apply_template(
                    templates['residential_service'],
                    {**business, **service, **location}
                )
        
        # Track cost (templates are essentially free)
        self.template_pages_cost = len(pages) * 0.001  # $0.001 per page
        
        logger.info(f"Generated {len(pages)} template pages")
        return pages
    
    async def _generate_llm_enhanced_pages(
        self,
        business: dict,
        services: List[dict],
        locations: List[dict]
    ) -> Dict[str, PageContent]:
        """
        Generate LLM-enhanced pages for high-value keywords (10% of pages)
        """
        logger.info("Generating LLM-enhanced pages...")
        pages = {}
        
        # Identify high-value service+location combinations
        high_value_combos = self._identify_high_value_combinations(services, locations)
        
        # Limit based on budget
        max_enhanced_pages = min(
            len(high_value_combos),
            int(self.config.get('seo_settings', {}).get('enhancement_budget', 5.0) / 0.15)
        )
        
        high_value_combos = high_value_combos[:max_enhanced_pages]
        
        # Generate enhanced content in batches to avoid rate limits
        batch_size = 5
        for i in range(0, len(high_value_combos), batch_size):
            batch = high_value_combos[i:i + batch_size]
            
            # Process batch in parallel
            batch_results = await asyncio.gather(*[
                self._generate_enhanced_content(combo, business)
                for combo in batch
            ])
            
            # Store results
            for combo, content in zip(batch, batch_results):
                pages[combo['url']] = content
            
            # Small delay to respect rate limits
            if i + batch_size < len(high_value_combos):
                await asyncio.sleep(1)
        
        logger.info(f"Generated {len(pages)} LLM-enhanced pages")
        return pages
    
    async def _generate_enhanced_content(
        self, 
        combo: dict, 
        business: dict
    ) -> PageContent:
        """
        Use LLM to generate premium content for high-value pages
        """
        service = combo['service']
        location = combo['location']
        
        prompt = f"""
        Create premium SEO content for {service['name']} services in {location['city']}, {location['state']}.
        
        Business Information:
        - Company: {business['name']}
        - Phone: {business['phone']}
        - Years in business: {business['years_in_business']}
        - Service areas: {', '.join(business['service_areas'])}
        
        Market Context:
        - Monthly searches: {combo['monthly_searches']}
        - Competition level: {combo['competition_level']}
        - Population: {location.get('population', 'N/A')}
        
        Generate a comprehensive page with:
        1. SEO title (60 characters max)
        2. Meta description (155 characters max)
        3. H1 heading
        4. 1000-word article with local expertise
        5. FAQ section (5 relevant questions)
        6. Strong call-to-action
        
        Focus on:
        - Local knowledge and expertise
        - Seasonal considerations for {location['state']}
        - Competitive advantages
        - Trust signals and credibility
        - Natural keyword integration
        
        Format as JSON with keys: title, meta_description, h1_heading, content, faqs, cta
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert local SEO copywriter specializing in home services. Create compelling, locally-relevant content that converts visitors into customers."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            # Track usage and cost
            self.total_tokens_used += response.usage.total_tokens
            self.llm_pages_cost += (response.usage.total_tokens / 1000) * 0.15  # GPT-4o-mini pricing
            
            # Parse response
            content_json = json.loads(response.choices[0].message.content)
            
            return PageContent(
                page_url=combo['url'],
                page_type='service_location_enhanced',
                title=content_json['title'],
                meta_description=content_json['meta_description'],
                h1_heading=content_json['h1_heading'],
                content=content_json['content'],
                schema_markup=self._generate_schema_markup(service, location, business),
                target_keywords=combo.get('keywords', []),
                generation_method='llm'
            )
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced content for {combo['url']}: {e}")
            # Fallback to template
            templates = await self._load_seo_templates()
            return self._apply_template(
                templates['service_location'],
                {**business, **service, **location}
            )
    
    async def _generate_meta_pages(
        self,
        business: dict,
        services: List[dict],
        locations: List[dict]
    ) -> Dict[str, PageContent]:
        """
        Generate meta pages (about, contact, privacy, etc.)
        """
        pages = {}
        templates = await self._load_seo_templates()
        
        # About page
        pages["/about"] = self._apply_template(
            templates['about_page'],
            {**business, "services": services, "locations": locations}
        )
        
        # Contact page
        pages["/contact"] = self._apply_template(
            templates['contact_page'],
            {**business, "locations": locations}
        )
        
        # Privacy policy
        pages["/privacy"] = self._apply_template(
            templates['privacy_policy'],
            business
        )
        
        # Terms of service
        pages["/terms"] = self._apply_template(
            templates['terms_of_service'],
            business
        )
        
        return pages
    
    def _identify_high_value_combinations(
        self, 
        services: List[dict], 
        locations: List[dict]
    ) -> List[dict]:
        """
        Identify service+location combinations worth LLM enhancement
        """
        combinations = []
        
        for service in services:
            for location in locations:
                # Calculate value score
                monthly_searches = location.get('monthly_searches', 500)
                competition = location.get('competition_level', 'medium')
                is_emergency = service.get('is_emergency', False)
                
                # Scoring algorithm
                score = monthly_searches
                if competition == 'low':
                    score *= 1.5
                elif competition == 'high':
                    score *= 0.7
                
                if is_emergency:
                    score *= 1.3
                
                combinations.append({
                    'service': service,
                    'location': location,
                    'url': f"/services/{service['slug']}/{location['slug']}",
                    'score': score,
                    'monthly_searches': monthly_searches,
                    'competition_level': competition,
                    'keywords': [
                        f"{service['name']} {location['city']}",
                        f"{service['name']} {location['city']} {location['state']}",
                        f"best {service['name']} {location['city']}",
                        f"{service['name']} near me"
                    ]
                })
        
        # Sort by score and return top combinations
        combinations.sort(key=lambda x: x['score'], reverse=True)
        return combinations
    
    async def _load_seo_templates(self) -> Dict[str, dict]:
        """Load SEO content templates from database"""
        templates = self.db.query(SEOContentTemplate).filter(
            SEOContentTemplate.is_active == True
        ).all()
        
        template_dict = {}
        for template in templates:
            template_dict[template.template_name] = {
                'title_template': template.title_template,
                'intro_template': template.intro_template,
                'body_template': template.body_template,
                'conclusion_template': template.conclusion_template,
                'cta_template': template.cta_template
            }
        
        # If no templates in DB, use defaults
        if not template_dict:
            template_dict = self._get_default_templates()
        
        return template_dict
    
    def _apply_template(self, template: dict, variables: dict) -> PageContent:
        """
        Apply variable substitution to template
        """
        # Replace variables in all template sections
        title = self._replace_variables(template['title_template'], variables)
        content = self._replace_variables(template['body_template'], variables)
        
        return PageContent(
            page_url=variables.get('page_url', '/'),
            page_type=variables.get('page_type', 'service_location'),
            title=title,
            meta_description=self._replace_variables(
                template.get('meta_description_template', title), 
                variables
            ),
            h1_heading=self._replace_variables(
                template.get('h1_template', title), 
                variables
            ),
            content=content,
            schema_markup=self._generate_schema_markup(
                variables.get('service', {}),
                variables.get('location', {}),
                variables
            ),
            target_keywords=variables.get('keywords', []),
            generation_method='template'
        )
    
    def _replace_variables(self, template: str, variables: dict) -> str:
        """
        Replace {variable} placeholders in template
        """
        if not template:
            return ""
        
        # Flatten nested dictionaries for easier access
        flat_vars = {}
        for key, value in variables.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_vars[f"{key}_{sub_key}"] = str(sub_value)
            else:
                flat_vars[key] = str(value)
        
        # Replace variables
        result = template
        for var_name, var_value in flat_vars.items():
            result = result.replace(f"{{{var_name}}}", var_value)
        
        return result
    
    def _generate_schema_markup(
        self, 
        service: dict, 
        location: dict, 
        business: dict
    ) -> dict:
        """
        Generate JSON-LD schema markup for the page
        """
        return {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": f"{service.get('name', 'Professional Service')} in {location.get('city', 'Local Area')}",
            "description": service.get('description', 'Professional service'),
            "provider": {
                "@type": "LocalBusiness",
                "name": business.get('name', 'Professional Services'),
                "telephone": business.get('phone', ''),
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": business.get('city', ''),
                    "addressRegion": business.get('state', ''),
                    "postalCode": business.get('zip_code', '')
                }
            },
            "areaServed": {
                "@type": "City",
                "name": location.get('city', 'Local Area')
            }
        }
    
    def _generate_sitemap(self, pages: Dict[str, PageContent]) -> List[dict]:
        """Generate XML sitemap entries"""
        sitemap_entries = []
        
        for url, page in pages.items():
            priority = 0.8  # Default priority
            
            # Adjust priority based on page type
            if url == "/":
                priority = 1.0
            elif "/services/" in url and url.count("/") == 2:  # Service overview
                priority = 0.9
            elif "/locations/" in url:  # Location hub
                priority = 0.9
            elif "/emergency/" in url:
                priority = 0.7
            
            sitemap_entries.append({
                "url": url,
                "lastmod": datetime.utcnow().isoformat(),
                "changefreq": "weekly",
                "priority": priority
            })
        
        return sitemap_entries
    
    def _generate_robots_txt(self) -> str:
        """Generate robots.txt content"""
        return """User-agent: *
Allow: /

Sitemap: https://{domain}/sitemap.xml

# Block admin and internal pages
Disallow: /admin/
Disallow: /api/
Disallow: /_next/
"""
    
    async def _store_generated_pages(self, pages: Dict[str, PageContent]):
        """Store all generated pages in database"""
        logger.info(f"Storing {len(pages)} pages in database...")
        
        # Clear existing pages for this business
        self.db.query(GeneratedSEOPage).filter(
            GeneratedSEOPage.business_id == self.business_id
        ).delete()
        
        # Insert new pages
        for url, page in pages.items():
            db_page = GeneratedSEOPage(
                business_id=self.business_id,
                page_url=url,
                page_type=page.page_type,
                title=page.title,
                meta_description=page.meta_description,
                h1_heading=page.h1_heading,
                content=page.content,
                schema_markup=page.schema_markup,
                target_keywords=page.target_keywords,
                generation_method=page.generation_method,
                created_at=datetime.utcnow()
            )
            self.db.add(db_page)
        
        self.db.commit()
        logger.info("Pages stored successfully")
    
    def _get_default_templates(self) -> Dict[str, dict]:
        """Default templates if none exist in database"""
        return {
            'service_overview': {
                'title_template': '{name} Services | Professional {name} | {business_name}',
                'body_template': 'Professional {name} services from {business_name}. Serving {service_areas} with {years_in_business} years of experience.',
                'meta_description_template': 'Professional {name} services. Licensed, insured, and experienced. Call {phone} for free estimate.'
            },
            'service_location': {
                'title_template': '{name} in {city}, {state} | 24/7 Service | {business_name}',
                'body_template': 'Need {name} in {city}? {business_name} provides professional {name} services with same-day availability.',
                'meta_description_template': 'Professional {name} in {city}, {state}. Same-day service, licensed & insured. Call {phone} now.'
            },
            'location_hub': {
                'title_template': 'Professional Services in {city}, {state} | {business_name}',
                'body_template': '{business_name} serves {city} with comprehensive professional services.',
                'meta_description_template': 'Professional services in {city}, {state}. Licensed, insured, and locally owned. Call {phone}.'
            }
        }
