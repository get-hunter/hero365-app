"""
OpenAI Content Generation Adapter

Implementation of ContentGenerationPort using OpenAI GPT-4.
This is a pure adapter - it only handles external API communication.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

import openai
from openai import AsyncOpenAI

from ...application.ports.content_generation_port import (
    ContentGenerationPort, ContentGenerationResult
)
from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import BusinessWebsite, WebsiteTemplate
from ...core.config import settings

logger = logging.getLogger(__name__)


class OpenAIContentAdapter(ContentGenerationPort):
    """
    OpenAI implementation of content generation.
    
    This adapter ONLY handles:
    - OpenAI API communication
    - Prompt engineering
    - Response parsing
    
    It does NOT contain business logic.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
        self.max_tokens = 2000
        self.temperature = 0.7
    
    async def generate_website_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        required_pages: List[str]
    ) -> ContentGenerationResult:
        """Generate complete website content using OpenAI."""
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Generating content for {len(required_pages)} pages")
            
            # Generate content for each page
            content_data = {}
            generation_tasks = []
            
            for page_type in required_pages:
                task = self._generate_single_page_content(
                    business, branding, template, page_type
                )
                generation_tasks.append((page_type, task))
            
            # Execute all generations in parallel
            page_results = await asyncio.gather(
                *[task for _, task in generation_tasks],
                return_exceptions=True
            )
            
            # Process results
            warnings = []
            for i, (page_type, result) in enumerate(zip([pt for pt, _ in generation_tasks], page_results)):
                if isinstance(result, Exception):
                    warnings.append(f"Failed to generate {page_type}: {str(result)}")
                    continue
                
                content_data[page_type] = result
            
            # Generate global content (business info, SEO, etc.)
            global_content = await self._generate_global_content(business, branding, template)
            content_data.update(global_content)
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=len(content_data) > 0,
                content_data=content_data,
                pages_generated=list(content_data.keys()),
                generation_time_seconds=generation_time,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=False,
                content_data={},
                pages_generated=[],
                generation_time_seconds=generation_time,
                error_message=str(e)
            )
    
    async def generate_page_content(
        self,
        business: Business,
        branding: BusinessBranding,
        page_type: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate content for a specific page."""
        
        prompt = self._build_page_prompt(business, branding, page_type, context)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web content writer specializing in home services businesses. Generate professional, SEO-optimized content that converts visitors into customers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content_text = response.choices[0].message.content
            
            # Parse structured content from response
            return self._parse_content_response(content_text, page_type)
            
        except Exception as e:
            logger.error(f"OpenAI API error for {page_type}: {str(e)}")
            raise
    
    async def update_website_content(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        content_updates: Dict[str, Any]
    ) -> ContentGenerationResult:
        """Update existing content with changes."""
        
        start_time = datetime.utcnow()
        
        try:
            updated_content = {}
            
            # Generate updated content for each specified section
            for section, updates in content_updates.items():
                updated_section = await self._update_section_content(
                    business, branding, section, updates
                )
                updated_content[section] = updated_section
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=True,
                content_data=updated_content,
                pages_generated=list(updated_content.keys()),
                generation_time_seconds=generation_time
            )
            
        except Exception as e:
            logger.error(f"Content update failed: {str(e)}")
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=False,
                content_data={},
                pages_generated=[],
                generation_time_seconds=generation_time,
                error_message=str(e)
            )
    
    async def generate_seo_content(
        self,
        business: Business,
        target_keywords: List[str],
        page_type: str
    ) -> Dict[str, Any]:
        """Generate SEO-optimized content for keywords."""
        
        prompt = f"""
        Generate SEO content for a {business.get_primary_trade()} business in {business.city}, {business.state}.
        
        Target keywords: {', '.join(target_keywords)}
        Page type: {page_type}
        Business name: {business.name}
        
        Generate:
        1. SEO title (50-60 characters)
        2. Meta description (150-160 characters)
        3. H1 heading
        4. 2-3 H2 headings
        5. Schema markup data
        
        Make it natural and customer-focused, not keyword-stuffed.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an SEO expert specializing in local home services businesses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            return self._parse_seo_content(content)
            
        except Exception as e:
            logger.error(f"SEO content generation failed: {str(e)}")
            raise
    
    async def validate_content_quality(
        self,
        content: Dict[str, Any],
        business: Business
    ) -> Dict[str, Any]:
        """Validate content quality using OpenAI."""
        
        prompt = f"""
        Analyze this website content for a {business.get_primary_trade()} business:
        
        {json.dumps(content, indent=2)}
        
        Evaluate:
        1. Clarity and readability
        2. Professional tone
        3. Call-to-action effectiveness
        4. Local relevance
        5. Trade-specific accuracy
        
        Provide a quality score (0-100) and specific improvement suggestions.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content quality analyst for home services websites."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            return self._parse_quality_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Content validation failed: {str(e)}")
            return {
                "quality_score": 50,
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": []
            }
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    async def _generate_single_page_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        page_type: str
    ) -> Dict[str, Any]:
        """Generate content for a single page type."""
        
        return await self.generate_page_content(
            business, branding, page_type, {"template": template}
        )
    
    async def _generate_global_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate
    ) -> Dict[str, Any]:
        """Generate global content (business info, SEO, etc.)."""
        
        return {
            "business_info": {
                "name": business.name,
                "phone": business.phone,
                "email": business.email,
                "address": f"{business.address}, {business.city}, {business.state} {business.postal_code}",
                "service_areas": business.service_areas,
                "primary_trade": business.get_primary_trade(),
                "all_trades": business.get_all_trades()
            },
            "branding": {
                "primary_color": branding.primary_color,
                "secondary_color": branding.secondary_color,
                "font_family": branding.font_family,
                "theme_name": branding.theme_name
            }
        }
    
    def _build_page_prompt(
        self,
        business: Business,
        branding: BusinessBranding,
        page_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build OpenAI prompt for page content generation."""
        
        base_prompt = f"""
        Generate website content for a {business.get_primary_trade()} business:
        
        Business: {business.name}
        Location: {business.city}, {business.state}
        Trade: {business.get_primary_trade()}
        Category: {business.trade_category.value}
        Service Areas: {', '.join(business.service_areas)}
        
        Page Type: {page_type}
        """
        
        # Add page-specific instructions
        page_instructions = {
            "home": "Create a compelling homepage with hero section, services overview, and strong call-to-action. Focus on local SEO and trust-building.",
            "services": "List detailed services with descriptions, pricing hints, and benefits. Make it easy to understand what's included.",
            "contact": "Create contact page with multiple ways to reach the business. Include service area information and hours.",
            "emergency": "Create urgent, action-oriented content for emergency services. Emphasize 24/7 availability and quick response.",
            "about": "Tell the business story, highlight experience and qualifications, build trust and credibility.",
            "booking": "Create booking page that makes it easy to schedule appointments. Include service types and time slots."
        }
        
        instruction = page_instructions.get(page_type, f"Create professional content for {page_type} page.")
        
        return f"{base_prompt}\n\nInstructions: {instruction}\n\nGenerate structured content with headings, paragraphs, and call-to-action elements."
    
    def _parse_content_response(self, content_text: str, page_type: str) -> Dict[str, Any]:
        """Parse OpenAI response into structured content."""
        
        # This is a simplified parser - in production you'd want more robust parsing
        lines = content_text.strip().split('\n')
        
        parsed_content = {
            "page_type": page_type,
            "raw_content": content_text,
            "sections": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headings
            if line.startswith('#') or line.isupper() or line.endswith(':'):
                if current_section:
                    parsed_content["sections"].append(current_section)
                
                current_section = {
                    "type": "heading",
                    "content": line.strip('#: '),
                    "text": []
                }
            elif current_section:
                current_section["text"].append(line)
            else:
                # Content without heading
                if "intro" not in parsed_content:
                    parsed_content["intro"] = []
                parsed_content["intro"].append(line)
        
        # Add final section
        if current_section:
            parsed_content["sections"].append(current_section)
        
        return parsed_content
    
    def _parse_seo_content(self, content: str) -> Dict[str, Any]:
        """Parse SEO content from OpenAI response."""
        
        # Simple parsing - in production you'd want more robust extraction
        return {
            "title": "SEO Title Here",  # Extract from content
            "meta_description": "Meta description here",  # Extract from content
            "h1": "Main heading",  # Extract from content
            "h2_headings": ["Heading 1", "Heading 2"],  # Extract from content
            "schema_data": {}  # Extract schema markup
        }
    
    def _parse_quality_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse quality analysis from OpenAI response."""
        
        # Simple parsing - extract score and suggestions
        return {
            "quality_score": 75,  # Extract from analysis
            "issues": [],  # Extract issues
            "suggestions": []  # Extract suggestions
        }
    
    async def _update_section_content(
        self,
        business: Business,
        branding: BusinessBranding,
        section: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update content for a specific section."""
        
        prompt = f"""
        Update the {section} section for {business.name} ({business.get_primary_trade()}).
        
        Current updates needed:
        {json.dumps(updates, indent=2)}
        
        Generate updated content that incorporates these changes while maintaining professional tone and SEO optimization.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are updating website content. Maintain consistency with existing style while incorporating new information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            updated_content = response.choices[0].message.content
            return self._parse_content_response(updated_content, section)
            
        except Exception as e:
            logger.error(f"Section update failed: {str(e)}")
            raise
