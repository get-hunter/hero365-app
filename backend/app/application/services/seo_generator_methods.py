"""
SEO Generator Methods - Page Generation and Processing
Additional methods for the SEO Website Generator Service
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

from .seo_generator_core import PageGenerationConfig, BusinessData, ServiceData, LocationData

logger = logging.getLogger(__name__)

class SEOGeneratorMethods:
    """Additional methods for SEO generation"""
    
    def __init__(self, generator_service):
        self.service = generator_service
    
    async def generate_page_configurations(
        self, 
        business: BusinessData, 
        services: List[ServiceData], 
        locations: List[LocationData]
    ) -> List[PageGenerationConfig]:
        """Generate all page configurations for maximum SEO coverage"""
        configs = []
        
        # 1. Service overview pages
        for service in services:
            configs.append(PageGenerationConfig(
                service=service,
                location=locations[0],
                business=business,
                page_type="service",
                url_path=f"/services/{service.slug}",
                generation_method="template",
                priority_score=service.priority_score
            ))
        
        # 2. Location hub pages
        for location in locations:
            configs.append(PageGenerationConfig(
                service=services[0],
                location=location,
                business=business,
                page_type="location",
                url_path=f"/locations/{location.slug}",
                generation_method="template",
                priority_score=70 + (location.monthly_searches // 100)
            ))
        
        # 3. Service + Location combinations (the money makers!)
        for service in services:
            for location in locations:
                base_config = PageGenerationConfig(
                    service=service,
                    location=location,
                    business=business,
                    page_type="service_location",
                    url_path=f"/services/{service.slug}/{location.slug}",
                    generation_method=self.determine_generation_method(service, location),
                    priority_score=service.priority_score + (location.monthly_searches // 100)
                )
                configs.append(base_config)
                
                # 4. Service variants (emergency, commercial, residential)
                variants = ["emergency", "commercial", "residential"]
                for variant in variants:
                    variant_config = PageGenerationConfig(
                        service=service,
                        location=location,
                        business=business,
                        page_type=f"{variant}_service",
                        url_path=f"/{variant}/{service.slug}/{location.slug}",
                        generation_method="template",
                        priority_score=base_config.priority_score - 10
                    )
                    configs.append(variant_config)
        
        # Sort by priority (highest first for LLM enhancement)
        configs.sort(key=lambda x: x.priority_score, reverse=True)
        
        logger.info(f"📊 Generated {len(configs)} page configurations")
        return configs
    
    def determine_generation_method(self, service: ServiceData, location: LocationData) -> str:
        """Smart method selection for maximum ROI"""
        score = 0
        
        # High search volume = more traffic opportunity
        if location.monthly_searches > 1000:
            score += 30
        
        # High competition = need better content
        if location.competition_level == "high":
            score += 25
        
        # High-priority service = business focus
        if service.priority_score > 80:
            score += 20
        
        # High conversion potential = more revenue
        if location.conversion_potential > 0.06:
            score += 15
        
        # High-income area = premium service opportunity
        if location.median_income > 70000:
            score += 10
        
        # Use LLM for top 10% of pages (score >= 70)
        return "llm" if score >= 70 else "template"
    
    async def generate_pages_parallel(self, page_configs: List[PageGenerationConfig]) -> Dict[str, Dict]:
        """Generate pages in parallel batches for maximum speed"""
        all_pages = {}
        batch_size = 20
        
        logger.info(f"🔄 Generating {len(page_configs)} pages in parallel batches")
        
        for i in range(0, len(page_configs), batch_size):
            batch = page_configs[i:i + batch_size]
            
            # Process batch in parallel
            batch_results = await asyncio.gather(*[
                self.generate_single_page(config) for config in batch
            ], return_exceptions=True)
            
            # Handle results and exceptions
            for config, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate {config.url_path}: {result}")
                    result = await self.generate_fallback_page(config)
                
                all_pages[config.url_path] = result
            
            # Progress update
            progress = min(100, ((i + batch_size) / len(page_configs)) * 100)
            logger.info(f"📈 Progress: {progress:.1f}% ({len(all_pages)}/{len(page_configs)} pages)")
        
        return all_pages
    
    async def generate_single_page(self, config: PageGenerationConfig) -> Dict[str, Any]:
        """Generate individual page based on method"""
        start_time = time.time()
        
        try:
            if config.generation_method == "template":
                page_data = await self.generate_template_page(config)
            else:  # LLM enhancement
                page_data = await self.generate_llm_enhanced_page(config)
                self.service.cost_tracker['llm_enhancement'] += 0.005
            
            # Add metadata
            page_data.update({
                'generation_method': config.generation_method,
                'generation_time_ms': int((time.time() - start_time) * 1000),
                'page_type': config.page_type,
                'priority_score': config.priority_score,
                'created_at': datetime.utcnow().isoformat()
            })
            
            return page_data
            
        except Exception as e:
            logger.error(f"Failed to generate {config.url_path}: {e}")
            return await self.generate_fallback_page(config)
    
    async def generate_template_page(self, config: PageGenerationConfig) -> Dict[str, Any]:
        """Generate page using smart templates (90% of pages, $0 cost, <100ms)"""
        
        # Get template and variables
        template = self.service.template_engine.get_template(config.page_type)
        variables = self.service.template_engine.generate_variables(config)
        
        # Apply template substitution
        title = self.service.template_engine.apply_variables(template['title_template'], variables)
        meta_description = self.service.template_engine.apply_variables(template['meta_description_template'], variables)
        h1_heading = self.service.template_engine.apply_variables(template['h1_template'], variables)
        content = self.service.template_engine.apply_variables(template['content_template'], variables)
        
        # Generate schema markup
        schema_markup = self.generate_schema_markup(config)
        
        return {
            'title': title,
            'meta_description': meta_description,
            'h1_heading': h1_heading,
            'content': content,
            'schema_markup': schema_markup,
            'target_keywords': config.service.keywords + [f"{config.service.name} {config.location.city}"],
            'word_count': len(content.split()),
            'page_url': config.url_path
        }
    
    async def generate_llm_enhanced_page(self, config: PageGenerationConfig) -> Dict[str, Any]:
        """Generate premium page using LLM (10% of pages, $0.005 cost, 2-5s)"""
        
        # Start with template base
        base_page = await self.generate_template_page(config)
        
        # Create enhancement prompt
        prompt = f"""Enhance this {config.service.name} page for {config.location.city}, {config.location.state} to outrank competitors.

Business: {config.business.name}
Service: {config.service.name}  
Location: {config.location.city}, {config.location.state}
Monthly Searches: {config.location.monthly_searches:,}
Competition: {config.location.competition_level}

Create enhanced content with:
1. Local expertise specific to {config.location.city}
2. Seasonal considerations for {config.location.state}
3. Neighborhood references and local knowledge
4. Competitive advantages and unique value props
5. Emergency service emphasis
6. Trust signals and credibility markers
7. Strong conversion-focused CTAs
8. FAQ section (5 relevant questions)

Requirements:
- 800-1200 words total
- Natural keyword integration
- Professional, trustworthy tone  
- Local SEO optimization
- High conversion focus

Make this page dominate search results and convert visitors to customers."""
        
        try:
            response = await self.service.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert local SEO copywriter specializing in home services. Create compelling content that ranks #1 and converts visitors to customers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            enhanced_content = response.choices[0].message.content
            
            return {
                **base_page,
                'content': enhanced_content,
                'word_count': len(enhanced_content.split()),
                'llm_enhanced': True,
                'llm_model': 'gpt-4o-mini'
            }
            
        except Exception as e:
            logger.error(f"LLM enhancement failed for {config.url_path}: {e}")
            return base_page
    
    async def generate_fallback_page(self, config: PageGenerationConfig) -> Dict[str, Any]:
        """Generate basic fallback page if generation fails"""
        return {
            'title': f"{config.service.name} in {config.location.city}, {config.location.state}",
            'meta_description': f"Professional {config.service.name} services in {config.location.city}",
            'h1_heading': f"{config.service.name} Services",
            'content': f"Professional {config.service.name} services available in {config.location.city}, {config.location.state}. Contact {config.business.name} at {config.business.phone}.",
            'schema_markup': {},
            'target_keywords': [config.service.name],
            'word_count': 25,
            'page_url': config.url_path,
            'generation_method': 'fallback'
        }
    
    def generate_schema_markup(self, config: PageGenerationConfig) -> Dict[str, Any]:
        """Generate JSON-LD schema for SEO"""
        return {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": f"{config.service.name} in {config.location.city}",
            "description": f"Professional {config.service.name} services in {config.location.city}, {config.location.state}",
            "provider": {
                "@type": "LocalBusiness",
                "name": config.business.name,
                "telephone": config.business.phone,
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": config.business.city,
                    "addressRegion": config.business.state,
                    "postalCode": config.business.zip_code
                }
            },
            "areaServed": {
                "@type": "City",
                "name": config.location.city
            }
        }
    
    async def generate_meta_pages(self, business: BusinessData, pages: Dict[str, Dict]) -> Dict[str, Dict]:
        """Generate sitemap, robots.txt, and other meta pages"""
        meta_pages = {}
        
        # Generate sitemap.xml
        sitemap_content = self.generate_sitemap_xml(pages, business)
        meta_pages['/sitemap.xml'] = {
            'content': sitemap_content,
            'content_type': 'application/xml',
            'generation_method': 'template',
            'page_type': 'sitemap'
        }
        
        # Generate robots.txt
        robots_content = f"""User-agent: *
Allow: /

Sitemap: https://{business.id}-website.hero365.workers.dev/sitemap.xml
"""
        meta_pages['/robots.txt'] = {
            'content': robots_content,
            'content_type': 'text/plain',
            'generation_method': 'template',
            'page_type': 'robots'
        }
        
        return meta_pages
    
    def generate_sitemap_xml(self, pages: Dict[str, Dict], business: BusinessData) -> str:
        """Generate XML sitemap for SEO"""
        base_url = f"https://{business.id}-website.hero365.workers.dev"
        
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url_path, page_data in pages.items():
            if url_path.startswith('/') and not url_path.endswith('.xml') and not url_path.endswith('.txt'):
                priority = "0.9" if page_data.get('generation_method') == 'llm' else "0.8"
                sitemap += f'  <url>\n'
                sitemap += f'    <loc>{base_url}{url_path}</loc>\n'
                sitemap += f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>\n'
                sitemap += f'    <priority>{priority}</priority>\n'
                sitemap += f'  </url>\n'
        
        sitemap += '</urlset>'
        return sitemap
    
    async def store_generated_pages(self, pages: Dict[str, Dict]) -> str:
        """Store generated pages (simulated for now)"""
        deployment_id = f"seo_deployment_{int(time.time())}"
        
        logger.info(f"📊 Storing {len(pages)} pages for deployment {deployment_id}")
        
        # In production, this would:
        # 1. Insert into website_deployments table
        # 2. Insert all pages into generated_seo_pages table  
        # 3. Update performance tracking
        # 4. Trigger Cloudflare Workers deployment
        
        return deployment_id
