"""
Claude Content Generation Adapter

Implementation of ContentGenerationPort using Anthropic's Claude.
This adapter specializes in generating high-quality React/Next.js components and content.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

import anthropic
from anthropic import AsyncAnthropic

from ...application.ports.content_generation_port import (
    ContentGenerationPort, ContentGenerationResult
)
from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import BusinessWebsite, WebsiteTemplate
from ...core.config import settings

logger = logging.getLogger(__name__)


class ClaudeContentAdapter(ContentGenerationPort):
    """
    Claude implementation of content generation.
    
    This adapter ONLY handles:
    - Anthropic Claude API communication
    - Prompt engineering optimized for Claude
    - Response parsing
    
    It does NOT contain business logic.
    """
    
    def __init__(self):
        if not settings.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required for Claude content generation")
        
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
        self.model = settings.CLAUDE_CONTENT_MODEL
        self.max_tokens = settings.CONTENT_MAX_TOKENS
        self.temperature = settings.CONTENT_TEMPERATURE
    
    async def generate_website_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        required_pages: List[str]
    ) -> ContentGenerationResult:
        """Generate complete website content using Claude in a SINGLE optimized request."""
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Generating ALL website content in single Claude request (pages: {required_pages})")
            
            # Generate ALL content in one batch request
            content_data = await self._generate_complete_website_batch(
                business, branding, template, required_pages
            )
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=len(content_data) > 0,
                content_data=content_data,
                pages_generated=list(content_data.keys()),
                generation_time_seconds=generation_time,
                warnings=None
            )
            
        except Exception as e:
            logger.error(f"Claude batch content generation failed: {str(e)}")
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
        """Generate content for a specific page using Claude."""
        
        prompt = self._build_claude_page_prompt(business, branding, page_type, context)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self._get_claude_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content_text = response.content[0].text
            
            # Parse structured content from response
            return self._parse_claude_content_response(content_text, page_type)
            
        except Exception as e:
            logger.error(f"Claude API error for {page_type}: {str(e)}")
            raise
    
    async def update_website_content(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        content_updates: Dict[str, Any]
    ) -> ContentGenerationResult:
        """Update existing content with changes using Claude."""
        
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
            logger.error(f"Claude content update failed: {str(e)}")
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
        """Generate SEO-optimized content for keywords using Claude."""
        
        prompt = f"""
        Generate comprehensive SEO content for a {business.get_primary_trade()} business in {business.city}, {business.state}.
        
        Business Details:
        - Name: {business.name}
        - Trade: {business.get_primary_trade()}
        - Category: {business.trade_category.value}
        - Service Areas: {', '.join(business.service_areas)}
        
        Target Keywords: {', '.join(target_keywords)}
        Page Type: {page_type}
        
        Please generate:
        1. SEO title (50-60 characters, compelling and keyword-rich)
        2. Meta description (150-160 characters, action-oriented)
        3. H1 heading (primary keyword focus)
        4. 3-4 H2 headings (semantic keyword variations)
        5. Schema markup JSON-LD for LocalBusiness
        6. Open Graph tags
        7. Suggested internal linking keywords
        
        Focus on:
        - Natural keyword integration (avoid stuffing)
        - Local SEO optimization
        - User intent matching
        - Conversion-focused messaging
        
        Return as structured JSON.
        """
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for SEO precision
                system="You are an expert SEO specialist for home services businesses. Generate precise, effective SEO content that ranks well and converts visitors.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            return self._parse_claude_seo_content(content)
            
        except Exception as e:
            logger.error(f"Claude SEO content generation failed: {str(e)}")
            raise
    
    async def validate_content_quality(
        self,
        content: Dict[str, Any],
        business: Business
    ) -> Dict[str, Any]:
        """Validate content quality using Claude's analytical capabilities."""
        
        prompt = f"""
        Analyze this website content for a {business.get_primary_trade()} business and provide detailed quality assessment:
        
        Business Context:
        - Name: {business.name}
        - Trade: {business.get_primary_trade()}
        - Location: {business.city}, {business.state}
        
        Content to Analyze:
        {json.dumps(content, indent=2)}
        
        Please evaluate and score (0-100) each aspect:
        
        1. **Clarity & Readability** (0-100)
           - Clear, jargon-free language
           - Logical flow and structure
           - Appropriate reading level
        
        2. **Professional Tone** (0-100)
           - Industry expertise demonstration
           - Trustworthy and authoritative voice
           - Consistent brand personality
        
        3. **Call-to-Action Effectiveness** (0-100)
           - Clear, compelling CTAs
           - Strategic placement
           - Action-oriented language
        
        4. **Local Relevance** (0-100)
           - Location-specific content
           - Local market understanding
           - Community connection
        
        5. **Trade-Specific Accuracy** (0-100)
           - Technical accuracy
           - Industry best practices
           - Service descriptions precision
        
        6. **SEO Optimization** (0-100)
           - Keyword integration
           - Meta elements quality
           - Content structure for search
        
        Provide:
        - Overall quality score (weighted average)
        - Top 3 strengths
        - Top 3 improvement areas
        - Specific actionable recommendations
        
        Return as structured JSON.
        """
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.2,  # Very low temperature for analytical precision
                system="You are a content quality analyst specializing in home services websites. Provide thorough, actionable analysis.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis = response.content[0].text
            return self._parse_claude_quality_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Claude content validation failed: {str(e)}")
            return {
                "overall_score": 50,
                "category_scores": {
                    "clarity": 50,
                    "professionalism": 50,
                    "cta_effectiveness": 50,
                    "local_relevance": 50,
                    "trade_accuracy": 50,
                    "seo_optimization": 50
                },
                "strengths": [],
                "improvement_areas": [f"Validation error: {str(e)}"],
                "recommendations": ["Please retry content validation"]
            }
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _get_claude_system_prompt(self) -> str:
        """Get Claude-optimized system prompt for content generation."""
        
        return """You are an expert web content creator specializing in home services businesses. You excel at:

1. **Technical Accuracy**: Deep understanding of trades like HVAC, plumbing, electrical, etc.
2. **Local SEO**: Creating location-specific content that ranks well in local search
3. **Conversion Optimization**: Writing content that turns visitors into customers
4. **Professional Tone**: Balancing expertise with accessibility
5. **React/Next.js Components**: Generating clean, modern component structures

When generating content:
- Use clear, professional language that builds trust
- Include specific service benefits and outcomes
- Incorporate local references naturally
- Structure content for both humans and search engines
- Focus on solving customer problems
- Include compelling calls-to-action

Always return structured, well-formatted content that can be easily parsed and used in web applications."""
    
    async def _generate_single_page_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        page_type: str
    ) -> Dict[str, Any]:
        """Generate content for a single page type using Claude."""
        
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
                "phone": business.phone_number,
                "email": business.business_email,
                "address": f"{business.address}, {business.city}, {business.state} {business.postal_code}",
                "service_areas": business.service_areas,
                "primary_trade": business.get_primary_trade(),
                "all_trades": business.get_all_trades()
            },
            "branding": {
                "primary_color": branding.color_scheme.primary_color,
                "secondary_color": branding.color_scheme.secondary_color,
                "font_family": branding.typography.heading_font,
                "theme_name": branding.theme_name
            },
            "generated_by": "claude",
            "generation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_claude_page_prompt(
        self,
        business: Business,
        branding: BusinessBranding,
        page_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build Claude-optimized prompt for page content generation."""
        
        base_context = f"""
        Generate professional website content for this home services business:
        
        **Business Profile:**
        - Company: {business.name}
        - Trade: {business.get_primary_trade()} ({business.trade_category.value})
        - Location: {business.city}, {business.state}
        - Service Areas: {', '.join(business.service_areas)}
        - Phone: {business.phone_number}
        - Email: {business.business_email}
        
        **Branding Guidelines:**
        - Primary Color: {branding.color_scheme.primary_color}
        - Secondary Color: {branding.color_scheme.secondary_color}
        - Font Family: {branding.typography.heading_font}
        - Theme: {branding.theme_name}
        
        **Page Type:** {page_type}
        """
        
        # Claude-specific page instructions optimized for better output
        page_instructions = {
            "home": """
            Create a compelling homepage that immediately communicates value and builds trust:
            
            **Required Sections:**
            1. Hero section with powerful headline and clear value proposition
            2. Services overview highlighting key offerings
            3. Why choose us (unique selling points)
            4. Service areas coverage
            5. Customer testimonials/social proof
            6. Emergency services callout (if applicable)
            7. Contact information and strong CTA
            
            **Focus Areas:**
            - Local SEO optimization with location keywords
            - Trust signals (licenses, insurance, experience)
            - Clear next steps for customers
            - Mobile-first design considerations
            """,
            
            "services": """
            Create detailed service pages that educate and convert:
            
            **Required Content:**
            1. Service category overview
            2. Individual service descriptions with benefits
            3. Process/methodology explanation
            4. Pricing transparency (ranges or starting points)
            5. Service area coverage
            6. Emergency vs. scheduled service options
            7. Warranty/guarantee information
            
            **Optimization:**
            - Service-specific keywords
            - Problem-solution messaging
            - Clear service differentiation
            """,
            
            "contact": """
            Create a conversion-optimized contact page:
            
            **Essential Elements:**
            1. Multiple contact methods (phone, email, form)
            2. Business hours and availability
            3. Service area map or list
            4. Response time expectations
            5. Emergency contact information
            6. Physical address and directions
            7. Social media links
            
            **Conversion Focus:**
            - Reduce friction to contact
            - Build confidence in response
            - Clear next steps after contact
            """,
            
            "emergency": """
            Create urgent, action-oriented emergency service content:
            
            **Critical Elements:**
            1. 24/7 availability messaging
            2. Emergency phone number prominence
            3. Response time guarantees
            4. Common emergency scenarios
            5. What to do while waiting
            6. Service area coverage for emergencies
            7. Pricing transparency for emergency calls
            
            **Urgency Optimization:**
            - Action-oriented headlines
            - Immediate contact options
            - Trust and reliability messaging
            """,
            
            "about": """
            Create trust-building about page that establishes credibility:
            
            **Key Content:**
            1. Company story and founding
            2. Owner/team qualifications and experience
            3. Licenses, certifications, insurance
            4. Community involvement
            5. Awards and recognition
            6. Company values and mission
            7. Why customers choose us
            
            **Trust Building:**
            - Personal connection elements
            - Professional credentials
            - Local community ties
            """,
            
            "booking": """
            Create streamlined booking experience:
            
            **Booking Elements:**
            1. Service type selection
            2. Preferred date/time options
            3. Contact information collection
            4. Service address input
            5. Problem description field
            6. Urgency level selection
            7. Confirmation and next steps
            
            **User Experience:**
            - Simple, step-by-step process
            - Clear expectations setting
            - Mobile-optimized interface
            """
        }
        
        instruction = page_instructions.get(page_type, f"Create professional, conversion-focused content for the {page_type} page that serves the business goals and user needs.")
        
        return f"""{base_context}
        
        {instruction}
        
        **Output Requirements:**
        - Return structured JSON with clear content sections
        - Include SEO elements (title, description, headings)
        - Provide component-ready content blocks
        - Ensure mobile-responsive considerations
        - Include conversion-focused CTAs
        - Maintain professional, trustworthy tone
        
        Generate comprehensive, high-quality content that will help this business succeed online."""
    
    def _parse_claude_content_response(self, content_text: str, page_type: str) -> Dict[str, Any]:
        """Parse Claude response into structured content."""
        
        try:
            # Try to parse as JSON first (Claude often returns structured JSON)
            if content_text.strip().startswith('{'):
                parsed_json = json.loads(content_text)
                parsed_json["page_type"] = page_type
                parsed_json["generated_by"] = "claude"
                return parsed_json
        except json.JSONDecodeError:
            pass
        
        # Fallback to text parsing
        lines = content_text.strip().split('\n')
        
        parsed_content = {
            "page_type": page_type,
            "generated_by": "claude",
            "raw_content": content_text,
            "sections": [],
            "seo": {},
            "components": []
        }
        
        current_section = None
        in_json_block = False
        json_content = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle JSON blocks
            if line.startswith('```json') or line.startswith('{'):
                in_json_block = True
                if line.startswith('{'):
                    json_content = line
                continue
            elif line.startswith('```') and in_json_block:
                in_json_block = False
                try:
                    json_data = json.loads(json_content)
                    parsed_content.update(json_data)
                except json.JSONDecodeError:
                    pass
                json_content = ""
                continue
            elif in_json_block:
                json_content += line + "\n"
                continue
            
            # Detect headings (more sophisticated than OpenAI version)
            if (line.startswith('#') or 
                line.startswith('**') and line.endswith('**') or
                line.isupper() and len(line) < 50 or
                line.endswith(':')):
                
                if current_section:
                    parsed_content["sections"].append(current_section)
                
                heading_text = line.strip('#*: ')
                current_section = {
                    "type": "heading",
                    "level": line.count('#') if line.startswith('#') else 2,
                    "content": heading_text,
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
    
    def _parse_claude_seo_content(self, content: str) -> Dict[str, Any]:
        """Parse SEO content from Claude response."""
        
        try:
            # Try JSON parsing first
            if content.strip().startswith('{'):
                return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Fallback parsing for non-JSON responses
        seo_data = {
            "title": "",
            "meta_description": "",
            "h1": "",
            "h2_headings": [],
            "schema_markup": {},
            "open_graph": {},
            "internal_links": []
        }
        
        lines = content.split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip()
            if 'title:' in line.lower():
                seo_data["title"] = line.split(':', 1)[1].strip().strip('"')
            elif 'meta description:' in line.lower():
                seo_data["meta_description"] = line.split(':', 1)[1].strip().strip('"')
            elif 'h1:' in line.lower():
                seo_data["h1"] = line.split(':', 1)[1].strip().strip('"')
        
        return seo_data
    
    def _parse_claude_quality_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse quality analysis from Claude response."""
        
        try:
            # Try JSON parsing first
            if analysis.strip().startswith('{'):
                return json.loads(analysis)
        except json.JSONDecodeError:
            pass
        
        # Fallback parsing
        return {
            "overall_score": 75,
            "category_scores": {
                "clarity": 75,
                "professionalism": 75,
                "cta_effectiveness": 75,
                "local_relevance": 75,
                "trade_accuracy": 75,
                "seo_optimization": 75
            },
            "strengths": ["Professional content", "Clear structure", "Good readability"],
            "improvement_areas": ["Could enhance local SEO", "Add more specific CTAs"],
            "recommendations": ["Include more location-specific keywords", "Strengthen call-to-action language"]
        }
    
    async def _update_section_content(
        self,
        business: Business,
        branding: BusinessBranding,
        section: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update content for a specific section using Claude."""
        
        prompt = f"""
        Update the {section} section for {business.name}, a {business.get_primary_trade()} business in {business.city}, {business.state}.
        
        **Current Updates Needed:**
        {json.dumps(updates, indent=2)}
        
        **Requirements:**
        - Maintain professional, trustworthy tone
        - Incorporate updates seamlessly
        - Preserve SEO optimization
        - Keep brand consistency
        - Ensure mobile-friendly content
        
        Generate updated content that incorporates these changes while improving overall quality and effectiveness.
        
        Return as structured JSON with clear content sections.
        """
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.4,
                system="You are updating website content. Maintain consistency with existing style while incorporating new information and improving quality.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            updated_content = response.content[0].text
            return self._parse_claude_content_response(updated_content, section)
            
        except Exception as e:
            logger.error(f"Claude section update failed: {str(e)}")
            raise
    
    async def _generate_complete_website_batch(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        required_pages: List[str]
    ) -> Dict[str, Any]:
        """Generate ALL website content in a single optimized Claude request."""
        
        # Build comprehensive prompt for entire website
        prompt = self._build_batch_website_prompt(business, branding, template, required_pages)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=8000,  # Increased for batch generation
                temperature=self.temperature,
                system=self._get_batch_generation_system_prompt(),
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            content_text = response.content[0].text
            
            # Parse the batch response into structured content
            return self._parse_batch_content_response(content_text, template)
            
        except Exception as e:
            logger.error(f"Claude batch generation failed: {str(e)}")
            raise
    
    def _build_batch_website_prompt(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        required_pages: List[str]
    ) -> str:
        """Build optimized prompt for generating entire website content in one request."""
        
        # Get trade-specific context
        trade_context = self._get_trade_context(business.industry, business.trade_category)
        
        # Build business context
        business_context = f"""
**Business Information:**
- Name: {business.name}
- Industry: {business.industry.title()}
- Trade Category: {business.trade_category.value}
- Service Areas: {', '.join(business.service_areas)}
- Phone: {business.phone_number}
- Email: {business.business_email}
- Address: {business.address}, {business.city}, {business.state} {business.postal_code}
"""
        
        # Build branding context
        branding_context = f"""
**Branding Guidelines:**
- Primary Color: {branding.color_scheme.primary_color}
- Secondary Color: {branding.color_scheme.secondary_color}
- Typography: {branding.typography.heading_font}
- Brand Voice: Professional, trustworthy, expert
"""
        
        # Build template structure
        pages_structure = []
        for page in template.structure.get("pages", []):
            page_name = page.get("name", "Home")
            sections = [s.get("type") for s in page.get("sections", [])]
            pages_structure.append(f"- {page_name}: {', '.join(sections)}")
        
        structure_context = f"""
**Website Structure:**
{chr(10).join(pages_structure)}
"""
        
        return f"""Generate complete website content for a {business.industry} business in {business.trade_category.value.lower()} sector.

{business_context}

{branding_context}

{structure_context}

{trade_context}

**Content Requirements:**
Generate ALL content for the entire website in a single response. Include:

1. **Hero Section**: Compelling headline, subheadline, primary/secondary CTAs
2. **Services Grid**: 6 core services with titles, descriptions, and benefits
3. **About Section**: Company story, expertise, credentials, team info
4. **Emergency Banner**: 24/7 availability, urgent service messaging
5. **Contact/Quote Form**: Lead capture with service selection
6. **SEO Content**: Meta titles, descriptions, keywords for each page

**Output Format:**
Return as structured JSON with this exact format:

```json
{{
  "hero": {{
    "headline": "Main headline",
    "subheadline": "Supporting text",
    "primaryCTA": {{"text": "Call Now", "action": "phone"}},
    "secondaryCTA": {{"text": "Get Quote", "action": "scroll"}}
  }},
  "servicesGrid": {{
    "heading": "Our Services",
    "subheading": "Professional services description",
    "services": [
      {{"title": "Service 1", "description": "Service description"}},
      {{"title": "Service 2", "description": "Service description"}},
      {{"title": "Service 3", "description": "Service description"}},
      {{"title": "Service 4", "description": "Service description"}},
      {{"title": "Service 5", "description": "Service description"}},
      {{"title": "Service 6", "description": "Service description"}}
    ]
  }},
  "about": {{
    "heading": "About Us",
    "story": "Company background and expertise",
    "credentials": ["License info", "Insurance", "Certifications"],
    "experience": "Years of experience and specialties"
  }},
  "emergencyBanner": {{
    "heading": "24/7 Emergency Service",
    "message": "Urgent service availability",
    "phone": "{business.phone_number}",
    "availability": "Available 24/7"
  }},
  "quoteForm": {{
    "heading": "Get Free Estimate",
    "subheading": "Contact form description",
    "services": ["Service 1", "Service 2", "Service 3", "Emergency"],
    "button": {{"text": "Get Quote"}}
  }},
  "seo": {{
    "title": "SEO page title",
    "description": "Meta description",
    "keywords": ["keyword1", "keyword2", "keyword3"]
  }}
}}
```

Generate professional, conversion-focused content that builds trust and drives leads. Focus on local SEO and trade-specific expertise."""
    
    def _get_batch_generation_system_prompt(self) -> str:
        """System prompt optimized for batch website content generation."""
        
        return """You are an expert website content creator specializing in home services and trade businesses. 

Your expertise includes:
- Trade-specific marketing and customer psychology
- Local SEO optimization for service businesses
- Conversion-focused copywriting
- Professional branding and messaging
- Mobile-first content strategy

Generate complete, professional website content that:
- Builds trust and credibility
- Drives phone calls and form submissions
- Ranks well in local search results
- Appeals to homeowners and property managers
- Showcases expertise and professionalism

Always return valid JSON with all required sections. Focus on benefits over features, use action-oriented language, and include local/regional references when appropriate."""
    
    def _parse_batch_content_response(self, content_text: str, template: WebsiteTemplate) -> Dict[str, Any]:
        """Parse batch content response into structured format."""
        
        try:
            # Extract JSON from response
            json_start = content_text.find('{')
            json_end = content_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_content = content_text[json_start:json_end]
            parsed_content = json.loads(json_content)
            
            # Structure content for website builder
            structured_content = {}
            
            # Map content to page paths and sections
            for page in template.structure.get("pages", []):
                page_path = page.get("path", "/")
                
                # Add full page content
                structured_content[page_path] = parsed_content
                
                # Add section-specific content
                for section in page.get("sections", []):
                    section_type = section.get("type")
                    section_key = f"{page_path}_{section_type}"
                    
                    if section_type in parsed_content:
                        structured_content[section_key] = {section_type: parsed_content[section_type]}
            
            return structured_content
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse batch content JSON: {str(e)}")
            logger.error(f"Content: {content_text[:500]}...")
            
            # Fallback: create basic content structure
            return self._create_fallback_content(template)
        
        except Exception as e:
            logger.error(f"Batch content parsing failed: {str(e)}")
            return self._create_fallback_content(template)
    
    def _create_fallback_content(self, template: WebsiteTemplate) -> Dict[str, Any]:
        """Create fallback content structure when parsing fails."""
        
        fallback_content = {
            "hero": {
                "headline": "Professional Service You Can Trust",
                "subheadline": "Expert solutions for your home and business needs",
                "primaryCTA": {"text": "Call Now", "action": "phone"},
                "secondaryCTA": {"text": "Get Quote", "action": "scroll"}
            },
            "servicesGrid": {
                "heading": "Our Services",
                "subheading": "Professional services tailored to your needs",
                "services": [
                    {"title": "Emergency Repairs", "description": "24/7 emergency service availability"},
                    {"title": "Installation", "description": "Professional installation services"},
                    {"title": "Maintenance", "description": "Regular maintenance and inspections"},
                    {"title": "Consultation", "description": "Expert advice and recommendations"}
                ]
            },
            "emergencyBanner": {
                "heading": "24/7 Emergency Service",
                "message": "Call now for immediate assistance",
                "availability": "Available 24/7"
            },
            "quoteForm": {
                "heading": "Get Free Estimate",
                "subheading": "Contact us for a personalized quote",
                "button": {"text": "Get Quote"}
            }
        }
        
        # Structure for website builder
        structured_content = {}
        
        for page in template.structure.get("pages", []):
            page_path = page.get("path", "/")
            structured_content[page_path] = fallback_content
            
            for section in page.get("sections", []):
                section_type = section.get("type")
                section_key = f"{page_path}_{section_type}"
                
                if section_type in fallback_content:
                    structured_content[section_key] = {section_type: fallback_content[section_type]}
        
        return structured_content
    
    def _get_trade_context(self, industry: str, trade_category) -> str:
        """Get trade-specific context for content generation."""
        
        trade_contexts = {
            "plumbing": """
**Plumbing Industry Context:**
- Emergency services are critical (burst pipes, water damage, no hot water)
- Common services: drain cleaning, pipe repair, water heater installation, leak detection
- Customer pain points: water damage, expensive repairs, unreliable contractors
- Trust factors: licensing, insurance, 24/7 availability, upfront pricing
- Seasonal considerations: frozen pipes in winter, outdoor plumbing in summer
""",
            "electrical": """
**Electrical Industry Context:**
- Safety is paramount (electrical hazards, code compliance)
- Common services: panel upgrades, outlet installation, lighting, troubleshooting
- Customer pain points: power outages, safety concerns, code violations
- Trust factors: licensed electrician, insured, code compliance, safety certifications
- Emergency situations: power outages, electrical fires, dangerous wiring
""",
            "hvac": """
**HVAC Industry Context:**
- Comfort and energy efficiency are key selling points
- Common services: AC repair, heating installation, duct cleaning, maintenance
- Customer pain points: high energy bills, uncomfortable temperatures, poor air quality
- Trust factors: certified technicians, energy efficiency expertise, maintenance plans
- Seasonal peaks: AC in summer, heating in winter, maintenance in spring/fall
""",
            "roofing": """
**Roofing Industry Context:**
- Weather protection and property value are primary concerns
- Common services: roof repair, replacement, inspection, gutter work
- Customer pain points: leaks, storm damage, expensive replacements
- Trust factors: insurance work, warranty, storm response, quality materials
- Weather dependency: storm season, winter limitations, urgent repairs
"""
        }
        
        return trade_contexts.get(industry.lower(), trade_contexts["plumbing"])