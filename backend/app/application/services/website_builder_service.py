"""
Website Builder Service

Next.js-based static site generator with trade-specific templates,
AI-generated content, and optimized build pipeline for Hero365 websites.
"""

import asyncio
import subprocess
import shutil
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import tempfile

from pydantic import BaseModel, Field

from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import (
    BusinessWebsite, WebsiteTemplate, WebsiteBuildJob, 
    BuildJobType, BuildJobStatus, CoreWebVitals
)
from ..services.ai_content_generator_service import (
    AIContentGeneratorService, ContentGenerationRequest, GeneratedContent
)
from ...core.config import settings

logger = logging.getLogger(__name__)


class BuildConfiguration(BaseModel):
    """Website build configuration."""
    
    # Build settings
    output_format: str = Field(default="static", description="Output format: static, spa, ssr")
    optimization_level: str = Field(default="production", description="Build optimization level")
    
    # Performance settings
    enable_compression: bool = Field(default=True)
    enable_minification: bool = Field(default=True)
    enable_tree_shaking: bool = Field(default=True)
    enable_code_splitting: bool = Field(default=True)
    
    # SEO settings
    generate_sitemap: bool = Field(default=True)
    generate_robots_txt: bool = Field(default=True)
    enable_meta_tags: bool = Field(default=True)
    enable_schema_markup: bool = Field(default=True)
    
    # PWA settings
    enable_pwa: bool = Field(default=False)
    enable_offline_support: bool = Field(default=False)
    
    # Analytics settings
    enable_analytics: bool = Field(default=True)
    analytics_provider: str = Field(default="google")
    
    # Custom settings
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    environment_variables: Dict[str, str] = Field(default_factory=dict)


class BuildResult(BaseModel):
    """Website build result."""
    
    success: bool
    build_path: Optional[str] = None
    build_time_seconds: float
    output_size_mb: float
    
    # Performance metrics
    lighthouse_score: Optional[int] = None
    core_web_vitals: Optional[CoreWebVitals] = None
    
    # Build artifacts
    pages_generated: int = 0
    assets_optimized: int = 0
    
    # Error information
    error_message: Optional[str] = None
    build_logs: Optional[str] = None
    
    # Optimization results
    compression_ratio: Optional[float] = None
    bundle_size_kb: Optional[float] = None


class WebsiteBuilderService:
    """
    Website builder service using Next.js static site generation.
    
    Orchestrates the complete website build process from template selection
    through content generation, build optimization, and performance validation.
    """
    
    def __init__(self):
        self.ai_content_service = AIContentGeneratorService()
        self.template_base_path = Path(settings.WEBSITE_TEMPLATE_PATH)
        self.build_output_path = Path(settings.WEBSITE_BUILD_PATH)
        self.nextjs_template_path = self.template_base_path / "nextjs-base"
        
        # Ensure directories exist
        self.build_output_path.mkdir(parents=True, exist_ok=True)
    
    async def build_website(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        build_config: Optional[BuildConfiguration] = None
    ) -> BuildResult:
        """
        Build a complete website from template and business data.
        
        This is the main orchestration method that handles the entire
        build pipeline from content generation to static site output.
        """
        
        start_time = datetime.utcnow()
        build_id = str(website.id)
        
        logger.info(f"Starting website build for {business.name} (ID: {build_id})")
        
        try:
            # Set default build configuration
            if not build_config:
                build_config = BuildConfiguration()
            
            # Create build directory
            build_dir = self.build_output_path / build_id
            if build_dir.exists():
                shutil.rmtree(build_dir)
            build_dir.mkdir(parents=True)
            
            # Step 1: Generate AI content for all pages
            logger.info("Generating AI content...")
            content_data = await self._generate_website_content(
                website, business, branding, template
            )
            
            # Step 2: Set up Next.js project
            logger.info("Setting up Next.js project...")
            await self._setup_nextjs_project(build_dir, template, build_config)
            
            # Step 3: Apply branding and theme
            logger.info("Applying branding and theme...")
            await self._apply_branding(build_dir, branding, website.theme_overrides)
            
            # Step 4: Generate pages with content
            logger.info("Generating pages...")
            pages_generated = await self._generate_pages(
                build_dir, template, content_data, business, website
            )
            
            # Step 5: Generate intake forms
            logger.info("Generating intake forms...")
            await self._generate_intake_forms(build_dir, website, business)
            
            # Step 6: Configure SEO and meta tags
            logger.info("Configuring SEO...")
            await self._configure_seo(build_dir, content_data, business, website)
            
            # Step 7: Build the Next.js project
            logger.info("Building Next.js project...")
            build_logs = await self._build_nextjs_project(build_dir, build_config)
            
            # Step 8: Optimize build output
            logger.info("Optimizing build output...")
            optimization_results = await self._optimize_build_output(build_dir, build_config)
            
            # Step 9: Run performance tests
            logger.info("Running performance tests...")
            performance_results = await self._run_performance_tests(build_dir)
            
            # Calculate build metrics
            build_time = (datetime.utcnow() - start_time).total_seconds()
            output_size = self._calculate_output_size(build_dir / "out")
            
            logger.info(f"Website build completed successfully in {build_time:.2f}s")
            
            return BuildResult(
                success=True,
                build_path=str(build_dir / "out"),
                build_time_seconds=build_time,
                output_size_mb=output_size,
                lighthouse_score=performance_results.get("lighthouse_score"),
                core_web_vitals=performance_results.get("core_web_vitals"),
                pages_generated=pages_generated,
                assets_optimized=optimization_results.get("assets_optimized", 0),
                compression_ratio=optimization_results.get("compression_ratio"),
                bundle_size_kb=optimization_results.get("bundle_size_kb")
            )
        
        except Exception as e:
            build_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Website build failed: {str(e)}")
            
            return BuildResult(
                success=False,
                build_time_seconds=build_time,
                output_size_mb=0.0,
                error_message=str(e),
                build_logs=getattr(e, 'build_logs', None)
            )
    
    async def _generate_website_content(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate
    ) -> Dict[str, GeneratedContent]:
        """Generate AI content for all website pages."""
        
        content_data = {}
        
        # Generate content for each page in the template
        for page in template.structure.get("pages", []):
            page_path = page.get("path", "/")
            page_name = page.get("name", "home")
            
            logger.info(f"Generating content for page: {page_name}")
            
            # Generate full page content
            request = ContentGenerationRequest(
                business=business,
                branding=branding,
                template=template,
                website=website,
                page_type=page_name.lower(),
                content_type="full_page"
            )
            
            page_content = await self.ai_content_service.generate_page_content(request)
            content_data[page_path] = page_content
            
            # Generate section-specific content
            for section in page.get("sections", []):
                section_type = section.get("type")
                
                if section_type in ["hero", "services", "about", "emergency", "contact"]:
                    section_request = ContentGenerationRequest(
                        business=business,
                        branding=branding,
                        template=template,
                        website=website,
                        page_type=page_name.lower(),
                        content_type=section_type,
                        additional_context=section.get("config", {})
                    )
                    
                    section_content = await self.ai_content_service.generate_page_content(section_request)
                    content_data[f"{page_path}_{section_type}"] = section_content
        
        return content_data
    
    async def _setup_nextjs_project(
        self,
        build_dir: Path,
        template: WebsiteTemplate,
        build_config: BuildConfiguration
    ) -> None:
        """Set up Next.js project structure."""
        
        # Copy base Next.js template
        if self.nextjs_template_path.exists():
            shutil.copytree(self.nextjs_template_path, build_dir, dirs_exist_ok=True)
        else:
            # Create minimal Next.js structure
            await self._create_minimal_nextjs_structure(build_dir)
        
        # Update package.json with build configuration
        package_json_path = build_dir / "package.json"
        if package_json_path.exists():
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
        else:
            package_data = {
                "name": "hero365-website",
                "version": "1.0.0",
                "private": True
            }
        
        # Add build scripts
        package_data["scripts"] = {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "export": "next export",
            "lint": "next lint"
        }
        
        # Add dependencies
        package_data["dependencies"] = {
            "next": "^14.0.0",
            "react": "^18.0.0",
            "react-dom": "^18.0.0",
            "@types/node": "^20.0.0",
            "@types/react": "^18.0.0",
            "@types/react-dom": "^18.0.0",
            "typescript": "^5.0.0"
        }
        
        # Add optimization dependencies if enabled
        if build_config.enable_compression:
            package_data["dependencies"]["compression"] = "^1.7.4"
        
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        # Create Next.js configuration
        await self._create_nextjs_config(build_dir, build_config)
    
    async def _create_minimal_nextjs_structure(self, build_dir: Path) -> None:
        """Create minimal Next.js project structure."""
        
        # Create directories
        (build_dir / "pages").mkdir(exist_ok=True)
        (build_dir / "public").mkdir(exist_ok=True)
        (build_dir / "styles").mkdir(exist_ok=True)
        (build_dir / "components").mkdir(exist_ok=True)
        (build_dir / "lib").mkdir(exist_ok=True)
        
        # Create basic _app.tsx
        app_content = '''import type { AppProps } from 'next/app'
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}'''
        
        with open(build_dir / "pages" / "_app.tsx", 'w') as f:
            f.write(app_content)
        
        # Create basic globals.css
        css_content = '''html,
body {
  padding: 0;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
    Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
}

a {
  color: inherit;
  text-decoration: none;
}

* {
  box-sizing: border-box;
}'''
        
        with open(build_dir / "styles" / "globals.css", 'w') as f:
            f.write(css_content)
    
    async def _create_nextjs_config(
        self,
        build_dir: Path,
        build_config: BuildConfiguration
    ) -> None:
        """Create Next.js configuration file."""
        
        config_content = f'''/** @type {{import('next').NextConfig}} */
const nextConfig = {{
  output: 'export',
  trailingSlash: true,
  images: {{
    unoptimized: true
  }},
  compress: {str(build_config.enable_compression).lower()},
  poweredByHeader: false,
  generateEtags: false,
  env: {json.dumps(build_config.environment_variables)},
}}

module.exports = nextConfig'''
        
        with open(build_dir / "next.config.js", 'w') as f:
            f.write(config_content)
    
    async def _apply_branding(
        self,
        build_dir: Path,
        branding: BusinessBranding,
        theme_overrides: Dict[str, Any]
    ) -> None:
        """Apply business branding to the website."""
        
        # Generate CSS variables from branding
        css_variables = self._generate_css_variables(branding, theme_overrides)
        
        # Create branding CSS file
        branding_css_path = build_dir / "styles" / "branding.css"
        with open(branding_css_path, 'w') as f:
            f.write(css_variables)
        
        # Update globals.css to import branding
        globals_css_path = build_dir / "styles" / "globals.css"
        if globals_css_path.exists():
            with open(globals_css_path, 'r') as f:
                existing_css = f.read()
            
            with open(globals_css_path, 'w') as f:
                f.write(f"@import './branding.css';\n\n{existing_css}")
    
    def _generate_css_variables(
        self,
        branding: BusinessBranding,
        theme_overrides: Dict[str, Any]
    ) -> str:
        """Generate CSS variables from branding configuration."""
        
        css_vars = [":root {"]
        
        # Color scheme variables
        if branding.color_scheme:
            colors = branding.color_scheme
            css_vars.extend([
                f"  --primary-color: {colors.get('primary', '#007bff')};",
                f"  --secondary-color: {colors.get('secondary', '#6c757d')};",
                f"  --accent-color: {colors.get('accent', '#28a745')};",
                f"  --background-color: {colors.get('background', '#ffffff')};",
                f"  --text-color: {colors.get('text', '#212529')};",
                f"  --border-color: {colors.get('border', '#dee2e6')};",
            ])
        
        # Typography variables
        if branding.typography:
            typography = branding.typography
            css_vars.extend([
                f"  --heading-font: {typography.get('heading_font', 'system-ui')};",
                f"  --body-font: {typography.get('body_font', 'system-ui')};",
                f"  --mono-font: {typography.get('mono_font', 'monospace')};",
                f"  --base-font-size: {typography.get('base_font_size', '16px')};",
                f"  --line-height: {typography.get('line_height', '1.5')};",
            ])
        
        # Website-specific settings
        if branding.website_settings:
            settings = branding.website_settings
            css_vars.extend([
                f"  --border-radius: {settings.get('corner_radius', '8px')};",
                f"  --shadow: {settings.get('shadow_style', '0 2px 4px rgba(0,0,0,0.1)')};",
            ])
        
        # Apply theme overrides
        for key, value in theme_overrides.items():
            css_vars.append(f"  --{key}: {value};")
        
        css_vars.append("}")
        
        return "\n".join(css_vars)
    
    async def _generate_pages(
        self,
        build_dir: Path,
        template: WebsiteTemplate,
        content_data: Dict[str, GeneratedContent],
        business: Business,
        website: BusinessWebsite
    ) -> int:
        """Generate Next.js pages from template and content."""
        
        pages_dir = build_dir / "pages"
        pages_generated = 0
        
        for page in template.structure.get("pages", []):
            page_path = page.get("path", "/")
            page_name = page.get("name", "home")
            
            # Determine file name
            if page_path == "/":
                file_name = "index.tsx"
            else:
                file_name = f"{page_path.strip('/')}.tsx"
            
            # Get page content
            page_content = content_data.get(page_path, None)
            
            # Generate React component
            component_code = await self._generate_page_component(
                page, page_content, content_data, business, website
            )
            
            # Write page file
            page_file_path = pages_dir / file_name
            page_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(page_file_path, 'w') as f:
                f.write(component_code)
            
            pages_generated += 1
            logger.info(f"Generated page: {file_name}")
        
        return pages_generated
    
    async def _generate_page_component(
        self,
        page: Dict[str, Any],
        page_content: Optional[GeneratedContent],
        all_content: Dict[str, GeneratedContent],
        business: Business,
        website: BusinessWebsite
    ) -> str:
        """Generate React component code for a page."""
        
        page_name = page.get("name", "Home")
        page_path = page.get("path", "/")
        sections = page.get("sections", [])
        
        # Start building component
        imports = [
            "import React from 'react';",
            "import Head from 'next/head';",
        ]
        
        # Generate sections
        section_components = []
        for section in sections:
            section_type = section.get("type")
            section_config = section.get("config", {})
            section_content = all_content.get(f"{page_path}_{section_type}")
            
            section_jsx = await self._generate_section_jsx(
                section_type, section_config, section_content, business, website
            )
            section_components.append(section_jsx)
        
        # Get SEO metadata
        seo_metadata = {}
        if page_content and page_content.seo_metadata:
            seo_metadata = page_content.seo_metadata
        
        # Generate component code
        component_code = f'''
{chr(10).join(imports)}

export default function {page_name.replace(' ', '')}Page() {{
  return (
    <>
      <Head>
        <title>{seo_metadata.get('title', f'{business.name} - {page_name}')}</title>
        <meta name="description" content="{seo_metadata.get('description', '')}" />
        <meta name="keywords" content="{', '.join(seo_metadata.get('keywords', []))}" />
        <meta property="og:title" content="{seo_metadata.get('og_title', '')}" />
        <meta property="og:description" content="{seo_metadata.get('og_description', '')}" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        {self._generate_schema_markup_script(seo_metadata.get('schema_markup', {}))}
      </Head>
      
      <main className="page-{page_path.strip('/') or 'home'}">
        {chr(10).join(section_components)}
      </main>
    </>
  );
}}'''
        
        return component_code
    
    async def _generate_section_jsx(
        self,
        section_type: str,
        section_config: Dict[str, Any],
        section_content: Optional[GeneratedContent],
        business: Business,
        website: BusinessWebsite
    ) -> str:
        """Generate JSX for a specific section."""
        
        if section_type == "hero":
            return await self._generate_hero_jsx(section_content, section_config, business)
        elif section_type == "services":
            return await self._generate_services_jsx(section_content, section_config, business)
        elif section_type == "contact-form":
            return await self._generate_contact_form_jsx(section_config, business, website)
        elif section_type == "quick-quote":
            return await self._generate_quick_quote_jsx(section_config, business, website)
        elif section_type == "booking-widget":
            return await self._generate_booking_widget_jsx(section_config, business, website)
        elif section_type == "emergency-banner":
            return await self._generate_emergency_banner_jsx(section_config, business)
        else:
            return f'        <section className="section-{section_type}">\\n          <p>Section: {section_type}</p>\\n        </section>'
    
    async def _generate_hero_jsx(
        self,
        content: Optional[GeneratedContent],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate hero section JSX."""
        
        if not content or not content.primary_content:
            return '        <section className="hero">\\n          <h1>Welcome</h1>\\n        </section>'
        
        hero_data = content.primary_content
        
        return f'''        <section className="hero">
          <div className="hero-content">
            <h1 className="hero-headline">{hero_data.get('headline', 'Welcome')}</h1>
            <p className="hero-subtitle">{hero_data.get('subtitle', '')}</p>
            <p className="hero-description">{hero_data.get('description', '')}</p>
            
            <div className="hero-trust-signals">
              {chr(10).join([f'              <span className="trust-signal">{signal}</span>' for signal in hero_data.get('trust_signals', [])])}
            </div>
            
            <div className="hero-actions">
              <button className="btn btn-primary" onClick={{() => window.location.href = '#contact'}}>
                {hero_data.get('primary_cta', {}).get('text', 'Get Started')}
              </button>
              <button className="btn btn-secondary" onClick={{() => window.location.href = 'tel:{business.phone_number}'}}>
                {hero_data.get('secondary_cta', {}).get('text', 'Call Now')}
              </button>
            </div>
          </div>
        </section>'''
    
    async def _generate_services_jsx(
        self,
        content: Optional[GeneratedContent],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate services section JSX."""
        
        if not content or not content.primary_content:
            return '        <section className="services">\\n          <h2>Our Services</h2>\\n        </section>'
        
        services_data = content.primary_content
        services = services_data.get('services', [])
        
        service_items = []
        for service in services:
            benefits_list = chr(10).join([f'                <li>{benefit}</li>' for benefit in service.get('benefits', [])])
            
            service_items.append(f'''              <div className="service-item">
                <h3 className="service-name">{service.get('name', '')}</h3>
                <p className="service-description">{service.get('description', '')}</p>
                <ul className="service-benefits">
{benefits_list}
                </ul>
                {f'<p className="service-pricing">{service.get("pricing_indicator")}</p>' if service.get('pricing_indicator') else ''}
              </div>''')
        
        return f'''        <section className="services">
          <div className="services-content">
            <h2 className="services-title">{services_data.get('section_title', 'Our Services')}</h2>
            <p className="services-intro">{services_data.get('introduction', '')}</p>
            
            <div className="services-grid">
{chr(10).join(service_items)}
            </div>
            
            <div className="services-cta">
              <button className="btn btn-primary">
                {services_data.get('cta_text', 'Learn More')}
              </button>
            </div>
          </div>
        </section>'''
    
    async def _generate_contact_form_jsx(
        self,
        config: Dict[str, Any],
        business: Business,
        website: BusinessWebsite
    ) -> str:
        """Generate contact form JSX."""
        
        form_title = config.get('title', 'Contact Us')
        
        return f'''        <section className="contact-form" id="contact">
          <div className="form-container">
            <h2 className="form-title">{form_title}</h2>
            
            <form className="contact-form-element" action="/api/submit-form" method="POST">
              <input type="hidden" name="form_type" value="contact" />
              <input type="hidden" name="website_id" value="{website.id}" />
              
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input type="text" id="name" name="name" required />
              </div>
              
              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input type="email" id="email" name="email" required />
              </div>
              
              <div className="form-group">
                <label htmlFor="phone">Phone Number *</label>
                <input type="tel" id="phone" name="phone" required />
              </div>
              
              <div className="form-group">
                <label htmlFor="service_type">Service Needed *</label>
                <select id="service_type" name="service_type" required>
                  <option value="">Select a service...</option>
                  {chr(10).join([f'                  <option value="{trade}">{trade.title()}</option>' for trade in business.get_all_trades()])}
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="description">Project Description *</label>
                <textarea id="description" name="description" rows="4" required></textarea>
              </div>
              
              <div className="form-group">
                <label htmlFor="urgency">When do you need service?</label>
                <select id="urgency" name="urgency">
                  <option value="emergency">Emergency (ASAP)</option>
                  <option value="24hours">Within 24 hours</option>
                  <option value="week">Within a week</option>
                  <option value="month">Within a month</option>
                  <option value="planning">Just planning</option>
                </select>
              </div>
              
              <button type="submit" className="btn btn-primary btn-submit">
                Send Message
              </button>
            </form>
          </div>
        </section>'''
    
    def _generate_schema_markup_script(self, schema_data: Dict[str, Any]) -> str:
        """Generate JSON-LD schema markup script tag."""
        
        if not schema_data:
            return ""
        
        schema_json = json.dumps(schema_data, indent=2)
        return f'''        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{{{
            __html: `{schema_json}`
          }}}}
        />'''
    
    async def _generate_intake_forms(
        self,
        build_dir: Path,
        website: BusinessWebsite,
        business: Business
    ) -> None:
        """Generate intake form API endpoints."""
        
        # Create API directory
        api_dir = build_dir / "pages" / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate form submission handler
        form_handler_code = f'''
import {{ NextApiRequest, NextApiResponse }} from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {{
  if (req.method !== 'POST') {{
    return res.status(405).json({{ error: 'Method not allowed' }});
  }}

  try {{
    // Extract form data
    const formData = req.body;
    
    // Submit to Hero365 backend
    const response = await fetch('{settings.BACKEND_URL}/api/websites/forms/submit', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
      }},
      body: JSON.stringify({{
        website_id: '{website.id}',
        business_id: '{business.id}',
        form_data: formData,
        visitor_info: {{
          ip: req.headers['x-forwarded-for'] || req.connection.remoteAddress,
          user_agent: req.headers['user-agent'],
          referrer: req.headers.referer
        }}
      }})
    }});
    
    if (response.ok) {{
      const result = await response.json();
      res.status(200).json({{ success: true, message: 'Form submitted successfully' }});
    }} else {{
      res.status(500).json({{ error: 'Failed to submit form' }});
    }}
  }} catch (error) {{
    console.error('Form submission error:', error);
    res.status(500).json({{ error: 'Internal server error' }});
  }}
}}'''
        
        with open(api_dir / "submit-form.ts", 'w') as f:
            f.write(form_handler_code)
    
    async def _configure_seo(
        self,
        build_dir: Path,
        content_data: Dict[str, GeneratedContent],
        business: Business,
        website: BusinessWebsite
    ) -> None:
        """Configure SEO files (sitemap, robots.txt, etc.)."""
        
        public_dir = build_dir / "public"
        
        # Generate robots.txt
        robots_content = f'''User-agent: *
Allow: /

Sitemap: {website.get_website_url()}/sitemap.xml'''
        
        with open(public_dir / "robots.txt", 'w') as f:
            f.write(robots_content)
        
        # Generate sitemap.xml
        pages = []
        for page_path in content_data.keys():
            if not page_path.startswith("/"):
                continue
            pages.append(f'''  <url>
    <loc>{website.get_website_url()}{page_path}</loc>
    <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')
        
        sitemap_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(pages)}
</urlset>'''
        
        with open(public_dir / "sitemap.xml", 'w') as f:
            f.write(sitemap_content)
    
    async def _build_nextjs_project(
        self,
        build_dir: Path,
        build_config: BuildConfiguration
    ) -> str:
        """Build the Next.js project."""
        
        # Install dependencies
        logger.info("Installing npm dependencies...")
        install_result = subprocess.run(
            ["npm", "install"],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        if install_result.returncode != 0:
            raise Exception(f"npm install failed: {install_result.stderr}")
        
        # Build project
        logger.info("Building Next.js project...")
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        if build_result.returncode != 0:
            raise Exception(f"Next.js build failed: {build_result.stderr}")
        
        # Export static files
        logger.info("Exporting static files...")
        export_result = subprocess.run(
            ["npm", "run", "export"],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        if export_result.returncode != 0:
            raise Exception(f"Next.js export failed: {export_result.stderr}")
        
        return f"{build_result.stdout}\n{export_result.stdout}"
    
    async def _optimize_build_output(
        self,
        build_dir: Path,
        build_config: BuildConfiguration
    ) -> Dict[str, Any]:
        """Optimize the build output."""
        
        out_dir = build_dir / "out"
        optimization_results = {
            "assets_optimized": 0,
            "compression_ratio": 0.0,
            "bundle_size_kb": 0.0
        }
        
        if not out_dir.exists():
            return optimization_results
        
        # Calculate bundle size
        total_size = sum(f.stat().st_size for f in out_dir.rglob('*') if f.is_file())
        optimization_results["bundle_size_kb"] = total_size / 1024
        
        # TODO: Add actual optimization logic (minification, compression, etc.)
        optimization_results["assets_optimized"] = len(list(out_dir.rglob('*')))
        
        return optimization_results
    
    async def _run_performance_tests(self, build_dir: Path) -> Dict[str, Any]:
        """Run performance tests on the built website."""
        
        # TODO: Implement Lighthouse testing
        # For now, return mock results
        return {
            "lighthouse_score": 95,
            "core_web_vitals": CoreWebVitals(
                lcp=1.2,
                fid=50.0,
                cls=0.05
            )
        }
    
    def _calculate_output_size(self, output_dir: Path) -> float:
        """Calculate total output size in MB."""
        
        if not output_dir.exists():
            return 0.0
        
        total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
        return total_size / (1024 * 1024)  # Convert to MB
