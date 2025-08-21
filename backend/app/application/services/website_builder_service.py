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
        # Use the same content generation factory as orchestration service
        from ...infrastructure.adapters.content_generation_factory import create_content_adapter
        self.ai_content_service = create_content_adapter(provider="claude")
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
    ) -> Dict[str, Any]:
        """Generate AI content for all website pages using optimized batch generation."""
        
        logger.info("Generating ALL website content in single optimized request")
        
        # Extract required pages from template
        required_pages = []
        for page in template.structure.get("pages", []):
            page_name = page.get("name", "home")
            required_pages.append(page_name.lower())
        
        # Generate ALL content in a single Claude request
        result = await self.ai_content_service.generate_website_content(
            business=business,
            branding=branding,
            template=template,
            required_pages=required_pages
        )
        
        if not result.success:
            logger.error(f"Batch content generation failed: {result.error_message}")
            raise Exception(f"Content generation failed: {result.error_message}")
        
        logger.info(f"Successfully generated content for {len(result.pages_generated)} pages in {result.generation_time_seconds:.2f}s")
        
        return result.content_data
    
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
            "lint": "next lint"
        }
        
        # Add dependencies with latest versions (2025) - Fixed PostCSS compatibility
        package_data["dependencies"] = {
            "next": "^15.4.4",
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
            "@types/node": "^22.0.0",
            "@types/react": "^19.0.0",
            "@types/react-dom": "^19.0.0",
            "typescript": "^5.7.0",
            "tailwindcss": "^3.4.0",  # Use v3 for PostCSS compatibility
            "@tailwindcss/postcss": "^4.1.4",  # Separate PostCSS plugin
            "autoprefixer": "^10.4.20",
            "postcss": "^8.5.0",
            "@tailwindcss/forms": "^0.5.9",
            "@tailwindcss/typography": "^0.5.15",
            "@headlessui/react": "^2.2.0",
            "@heroicons/react": "^2.2.0",
            "framer-motion": "^11.15.0"
        }
        
        # Add optimization dependencies if enabled
        if build_config.enable_compression:
            package_data["dependencies"]["compression"] = "^1.7.4"
        
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        # Create Next.js configuration
        await self._create_nextjs_config(build_dir, build_config)
        
        # Create Tailwind CSS configuration
        await self._create_tailwind_config(build_dir, template)
        
        # Create PostCSS configuration
        await self._create_postcss_config(build_dir)
    
    async def _create_nextjs_config(self, build_dir: Path, build_config: BuildConfiguration) -> None:
        """Create next.config.js with static export configuration."""
        
        next_config_path = build_dir / "next.config.js"
        next_config_content = """/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  }
}

module.exports = nextConfig
"""
        
        with open(next_config_path, 'w') as f:
            f.write(next_config_content)
        
        logger.info("Created next.config.js with static export configuration")
    
    async def _create_tailwind_config(self, build_dir: Path, template: WebsiteTemplate) -> None:
        """Create Tailwind CSS configuration with trade-specific design system."""
        
        tailwind_config_path = build_dir / "tailwind.config.js"
        
        # Get trade-specific color palette
        trade_colors = self._get_trade_color_palette(template.trade_category, template.trade_type)
        
        tailwind_config_content = f"""/** @type {{import('tailwindcss').Config}} */
module.exports = {{
  content: [
    './pages/**/*.{{js,ts,jsx,tsx,mdx}}',
    './components/**/*.{{js,ts,jsx,tsx,mdx}}',
    './app/**/*.{{js,ts,jsx,tsx,mdx}}',
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          50: '{trade_colors["primary_50"]}',
          100: '{trade_colors["primary_100"]}',
          200: '{trade_colors["primary_200"]}',
          300: '{trade_colors["primary_300"]}',
          400: '{trade_colors["primary_400"]}',
          500: '{trade_colors["primary_500"]}',
          600: '{trade_colors["primary_600"]}',
          700: '{trade_colors["primary_700"]}',
          800: '{trade_colors["primary_800"]}',
          900: '{trade_colors["primary_900"]}',
          950: '{trade_colors["primary_950"]}',
        }},
        secondary: {{
          50: '{trade_colors["secondary_50"]}',
          100: '{trade_colors["secondary_100"]}',
          200: '{trade_colors["secondary_200"]}',
          300: '{trade_colors["secondary_300"]}',
          400: '{trade_colors["secondary_400"]}',
          500: '{trade_colors["secondary_500"]}',
          600: '{trade_colors["secondary_600"]}',
          700: '{trade_colors["secondary_700"]}',
          800: '{trade_colors["secondary_800"]}',
          900: '{trade_colors["secondary_900"]}',
          950: '{trade_colors["secondary_950"]}',
        }},
        accent: {{
          50: '{trade_colors["accent_50"]}',
          500: '{trade_colors["accent_500"]}',
          600: '{trade_colors["accent_600"]}',
        }},
      }},
      fontFamily: {{
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Inter', 'system-ui', 'sans-serif'],
      }},
      animation: {{
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
      }},
      keyframes: {{
        fadeIn: {{
          '0%': {{ opacity: '0' }},
          '100%': {{ opacity: '1' }},
        }},
        slideUp: {{
          '0%': {{ transform: 'translateY(20px)', opacity: '0' }},
          '100%': {{ transform: 'translateY(0)', opacity: '1' }},
        }},
        bounceGentle: {{
          '0%, 100%': {{ transform: 'translateY(0)' }},
          '50%': {{ transform: 'translateY(-5px)' }},
        }},
      }},
    }},
  }},
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}}"""
        
        with open(tailwind_config_path, 'w') as f:
            f.write(tailwind_config_content)
        
        logger.info("Created tailwind.config.js with trade-specific design system")
    
    async def _create_postcss_config(self, build_dir: Path) -> None:
        """Create PostCSS configuration for Tailwind CSS."""
        
        postcss_config_path = build_dir / "postcss.config.js"
        postcss_config_content = """module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}"""
        
        with open(postcss_config_path, 'w') as f:
            f.write(postcss_config_content)
        
        logger.info("Created postcss.config.js")
    
    def _get_trade_color_palette(self, trade_category: str, trade_type: str) -> Dict[str, str]:
        """Get trade-specific color palette for professional branding."""
        
        # Professional color palettes for different trades
        trade_palettes = {
            # Plumbing - Blue tones (trust, reliability, water)
            "plumbing": {
                "primary_50": "#eff6ff", "primary_100": "#dbeafe", "primary_200": "#bfdbfe",
                "primary_300": "#93c5fd", "primary_400": "#60a5fa", "primary_500": "#3b82f6",
                "primary_600": "#2563eb", "primary_700": "#1d4ed8", "primary_800": "#1e40af",
                "primary_900": "#1e3a8a", "primary_950": "#172554",
                "secondary_50": "#f0f9ff", "secondary_100": "#e0f2fe", "secondary_200": "#bae6fd",
                "secondary_300": "#7dd3fc", "secondary_400": "#38bdf8", "secondary_500": "#0ea5e9",
                "secondary_600": "#0284c7", "secondary_700": "#0369a1", "secondary_800": "#075985",
                "secondary_900": "#0c4a6e", "secondary_950": "#082f49",
                "accent_50": "#ecfeff", "accent_500": "#06b6d4", "accent_600": "#0891b2"
            },
            
            # Electrical - Orange/Yellow tones (energy, power, safety)
            "electrical": {
                "primary_50": "#fff7ed", "primary_100": "#ffedd5", "primary_200": "#fed7aa",
                "primary_300": "#fdba74", "primary_400": "#fb923c", "primary_500": "#f97316",
                "primary_600": "#ea580c", "primary_700": "#c2410c", "primary_800": "#9a3412",
                "primary_900": "#7c2d12", "primary_950": "#431407",
                "secondary_50": "#fefce8", "secondary_100": "#fef9c3", "secondary_200": "#fef08a",
                "secondary_300": "#fde047", "secondary_400": "#facc15", "secondary_500": "#eab308",
                "secondary_600": "#ca8a04", "secondary_700": "#a16207", "secondary_800": "#854d0e",
                "secondary_900": "#713f12", "secondary_950": "#422006",
                "accent_50": "#fef2f2", "accent_500": "#ef4444", "accent_600": "#dc2626"
            },
            
            # HVAC - Green tones (environment, efficiency, comfort)
            "hvac": {
                "primary_50": "#f0fdf4", "primary_100": "#dcfce7", "primary_200": "#bbf7d0",
                "primary_300": "#86efac", "primary_400": "#4ade80", "primary_500": "#22c55e",
                "primary_600": "#16a34a", "primary_700": "#15803d", "primary_800": "#166534",
                "primary_900": "#14532d", "primary_950": "#052e16",
                "secondary_50": "#ecfdf5", "secondary_100": "#d1fae5", "secondary_200": "#a7f3d0",
                "secondary_300": "#6ee7b7", "secondary_400": "#34d399", "secondary_500": "#10b981",
                "secondary_600": "#059669", "secondary_700": "#047857", "secondary_800": "#065f46",
                "secondary_900": "#064e3b", "secondary_950": "#022c22",
                "accent_50": "#f0fdfa", "accent_500": "#14b8a6", "accent_600": "#0d9488"
            },
            
            # Roofing - Gray/Blue tones (strength, protection, sky)
            "roofing": {
                "primary_50": "#f8fafc", "primary_100": "#f1f5f9", "primary_200": "#e2e8f0",
                "primary_300": "#cbd5e1", "primary_400": "#94a3b8", "primary_500": "#64748b",
                "primary_600": "#475569", "primary_700": "#334155", "primary_800": "#1e293b",
                "primary_900": "#0f172a", "primary_950": "#020617",
                "secondary_50": "#f0f9ff", "secondary_100": "#e0f2fe", "secondary_200": "#bae6fd",
                "secondary_300": "#7dd3fc", "secondary_400": "#38bdf8", "secondary_500": "#0ea5e9",
                "secondary_600": "#0284c7", "secondary_700": "#0369a1", "secondary_800": "#075985",
                "secondary_900": "#0c4a6e", "secondary_950": "#082f49",
                "accent_50": "#fef2f2", "accent_500": "#ef4444", "accent_600": "#dc2626"
            },
        }
        
        # Default to plumbing colors if trade not found
        return trade_palettes.get(trade_type.lower(), trade_palettes["plumbing"])
    
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
        
        # Create Tailwind CSS globals.css
        css_content = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    scroll-behavior: smooth;
  }
  
  body {
    @apply font-sans antialiased;
  }
}

@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-6 py-3 text-base font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
  
  .btn-primary {
    @apply bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5;
  }
  
  .btn-secondary {
    @apply bg-white text-primary-600 border-2 border-primary-600 hover:bg-primary-50 focus:ring-primary-500;
  }
  
  .btn-accent {
    @apply bg-accent-500 text-white hover:bg-accent-600 focus:ring-accent-500;
  }
  
  .section-padding {
    @apply py-16 px-4 sm:px-6 lg:px-8;
  }
  
  .container-custom {
    @apply max-w-7xl mx-auto;
  }
  
  .hero-gradient {
    @apply bg-gradient-to-br from-primary-50 via-white to-secondary-50;
  }
  
  .card {
    @apply bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100;
  }
  
  .text-gradient {
    @apply bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent;
  }
}

@layer utilities {
  .animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out forwards;
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
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
                f"  --primary-color: {colors.primary_color};",
                f"  --secondary-color: {colors.secondary_color};",
                f"  --accent-color: {colors.accent_color};",
                f"  --background-color: {colors.background_color};",
                f"  --text-color: {colors.text_color};",
                f"  --border-color: {colors.border_color};",
            ])
        
        # Typography variables
        if branding.typography:
            typography = branding.typography
            css_vars.extend([
                f"  --heading-font: {typography.heading_font};",
                f"  --body-font: {typography.body_font};",
                f"  --mono-font: {typography.mono_font};",
                f"  --base-font-size: {typography.body_size};",
                f"  --line-height: {typography.body_line_height};",
            ])
        
        # Website-specific settings (using default values)
        css_vars.extend([
            f"  --border-radius: 8px;",
            f"  --shadow: 0 2px 4px rgba(0,0,0,0.1);",
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
        if page_content and page_content.get('seo_metadata'):
            seo_metadata = page_content.get('seo_metadata', {})
        
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
        
        if not content or not content.get('primary_content'):
            return '        <section className="hero">\\n          <h1>Welcome</h1>\\n        </section>'
        
        hero_data = content.get('primary_content', {})
        
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
        
        if not content or not content.get('primary_content'):
            return '        <section className="services">\\n          <h2>Our Services</h2>\\n        </section>'
        
        services_data = content.get('primary_content', {})
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
        
        # Static files are automatically exported during build (output: 'export' in next.config.js)
        logger.info("Static files automatically exported during build")
        
        # Verify the 'out' directory was created
        out_dir = build_dir / "out"
        if not out_dir.exists():
            raise Exception("Next.js build did not create 'out' directory with static export")
        
        return build_result.stdout
    
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
    
    async def _generate_section_jsx(
        self,
        section_type: str,
        section_config: Dict[str, Any],
        section_content: Optional[Dict[str, Any]],
        business: Business,
        website: BusinessWebsite
    ) -> str:
        """Generate JSX for a specific section type."""
        
        if section_type == "hero":
            return await self._generate_hero_jsx(section_content, section_config, business)
        elif section_type in ["services", "services-grid"]:
            return await self._generate_services_jsx(section_content, section_config, business)
        elif section_type == "about":
            return await self._generate_about_jsx(section_content, section_config, business)
        elif section_type in ["emergency", "emergency-banner"]:
            return await self._generate_emergency_jsx(section_content, section_config, business)
        elif section_type == "contact":
            return await self._generate_contact_jsx(section_content, section_config, business)
        elif section_type == "quick-quote":
            return await self._generate_quick_quote_jsx(section_content, section_config, business)
        else:
            # Default section
            return f'        <section className="{section_type}">\\n          <h2>{section_type.title()}</h2>\\n        </section>'
    
    async def _generate_hero_jsx(
        self,
        content: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate modern hero section JSX with Tailwind CSS."""
        
        if not content or not content.get('hero'):
            return '''        <section className="hero-gradient section-padding">
          <div className="container-custom">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 animate-fade-in">Welcome</h1>
            </div>
          </div>
        </section>'''
        
        hero_data = content.get('hero', {})
        headline = hero_data.get('headline', 'Welcome')
        subheadline = hero_data.get('subheadline', '')
        primary_cta = hero_data.get('primaryCTA', {}).get('text', 'Call Now')
        secondary_cta = hero_data.get('secondaryCTA', {}).get('text', 'Get Quote')
        
        return f'''        <section className="hero-gradient section-padding min-h-screen flex items-center">
          <div className="container-custom">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div className="text-center lg:text-left">
                <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 animate-fade-in">
                  {headline}
                </h1>
                <p className="text-xl text-gray-600 mb-8 max-w-2xl animate-fade-in-up">
                  {subheadline}
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start animate-fade-in-up">
                  <button 
                    className="btn btn-primary"
                    onClick={{() => window.location.href = 'tel:{business.phone_number}'}}
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                    </svg>
                    {primary_cta}
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={{() => document.getElementById('contact')?.scrollIntoView({{ behavior: 'smooth' }})}}
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    {secondary_cta}
                  </button>
                </div>
              </div>
              <div className="hidden lg:block">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-2xl transform rotate-6"></div>
                  <div className="relative bg-white p-8 rounded-2xl shadow-2xl">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Professional Service</h3>
                      <p className="text-gray-600">Licensed & Insured</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>'''
    
    async def _generate_services_jsx(
        self,
        content: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate modern services section JSX with Tailwind CSS."""
        
        if not content or not content.get('servicesGrid'):
            return '''        <section className="section-padding bg-gray-50">
          <div className="container-custom">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Our Services</h2>
            </div>
          </div>
        </section>'''
        
        services_data = content.get('servicesGrid', {})
        services = services_data.get('services', [])
        heading = services_data.get('heading', 'Our Services')
        subheading = services_data.get('subheading', '')
        
        service_items = []
        service_icons = [
            'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z',
            'M13 10V3L4 14h7v7l9-11h-7z',
            'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
            'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16',
            'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4',
            'M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10v11M20 10v11M8 14h8'
        ]
        
        for i, service in enumerate(services[:6]):  # Limit to 6 services
            icon_path = service_icons[i % len(service_icons)]
            service_items.append(f'''
              <div className="card p-8 text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-primary-200 transition-colors">
                  <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="{icon_path}"></path>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{service.get('title', 'Service')}</h3>
                <p className="text-gray-600 mb-6">{service.get('description', '')}</p>
                <button className="text-primary-600 font-medium hover:text-primary-700 transition-colors">
                  Learn More →
                </button>
              </div>''')
        
        return f'''        <section className="section-padding bg-gray-50">
          <div className="container-custom">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 animate-fade-in">
                {heading}
              </h2>
              {f'<p className="text-xl text-gray-600 max-w-3xl mx-auto animate-fade-in-up">{subheading}</p>' if subheading else ''}
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {''.join(service_items)}
            </div>
            <div className="text-center mt-12">
              <button 
                className="btn btn-primary"
                onClick={{() => document.getElementById('contact')?.scrollIntoView({{ behavior: 'smooth' }})}}
              >
                Get Free Estimate
              </button>
            </div>
          </div>
        </section>'''
    
    async def _generate_about_jsx(
        self,
        content: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate about section JSX."""
        
        if not content or not content.get('primary_content'):
            return '        <section className="about">\\n          <h2>About Us</h2>\\n        </section>'
        
        about_data = content.get('primary_content', {})
        
        return f'''        <section className="about">
          <div className="container">
            <h2>{about_data.get('title', 'About Us')}</h2>
            <p>{about_data.get('description', '')}</p>
          </div>
        </section>'''
    
    async def _generate_emergency_jsx(
        self,
        content: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate emergency section JSX."""
        
        if not content or not content.get('emergencyBanner'):
            return '        <section className="emergency">\\n          <h2>Emergency Service</h2>\\n        </section>'
        
        emergency_data = content.get('emergencyBanner', {})
        
        return f'''        <section className="emergency">
          <div className="container">
            <h2>{emergency_data.get('text', '24/7 Emergency Service')}</h2>
            <p>{emergency_data.get('available', 'Available for emergency repairs')}</p>
            <button className="btn btn-emergency" onClick={{() => window.location.href = 'tel:{emergency_data.get('phone', business.phone_number)}'}}>
              Call Now: {emergency_data.get('phone', business.phone_number)}
            </button>
          </div>
        </section>'''
    
    async def _generate_contact_jsx(
        self,
        content: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate contact section JSX."""
        
        if not content or not content.get('primary_content'):
            return '        <section className="contact">\\n          <h2>Contact Us</h2>\\n        </section>'
        
        contact_data = content.get('primary_content', {})
        
        return f'''        <section className="contact">
          <div className="container">
            <h2>{contact_data.get('title', 'Contact Us')}</h2>
            <div className="contact-info">
              <p><strong>Phone:</strong> {business.phone_number}</p>
              <p><strong>Email:</strong> {business.business_email}</p>
              <p><strong>Service Areas:</strong> {', '.join(business.service_areas)}</p>
            </div>
          </div>
        </section>'''
    
    async def _generate_quick_quote_jsx(
        self,
        content: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        business: Business
    ) -> str:
        """Generate modern quick quote section JSX with Tailwind CSS."""
        
        if not content or not content.get('quoteForm'):
            return '''        <section id="contact" className="section-padding bg-primary-600">
          <div className="container-custom">
            <div className="text-center text-white">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Get a Quote</h2>
              <p className="text-xl mb-8">Contact us for a free estimate</p>
            </div>
          </div>
        </section>'''
        
        quote_data = content.get('quoteForm', {})
        heading = quote_data.get('heading', 'Get a Quote')
        subheading = quote_data.get('subheading', 'Contact us for a free estimate')
        button_text = quote_data.get('button', {}).get('text', 'Call Now')
        
        return f'''        <section id="contact" className="section-padding bg-primary-600">
          <div className="container-custom">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div className="text-white">
                <h2 className="text-3xl md:text-4xl font-bold mb-6 animate-fade-in">
                  {heading}
                </h2>
                <p className="text-xl mb-8 text-primary-100 animate-fade-in-up">
                  {subheading}
                </p>
                <div className="flex flex-col sm:flex-row gap-4 animate-fade-in-up">
                  <button 
                    className="btn bg-white text-primary-600 hover:bg-gray-100"
                    onClick={{() => window.location.href = 'tel:{business.phone_number}'}}
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                    </svg>
                    {button_text}
                  </button>
                  <button 
                    className="btn btn-secondary border-white text-white hover:bg-white hover:text-primary-600"
                    onClick={{() => window.location.href = 'mailto:{business.business_email}'}}
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                    Send Email
                  </button>
                </div>
              </div>
              <div className="bg-white rounded-2xl p-8 shadow-2xl">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Quick Contact Form</h3>
                <form className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                    <input 
                      type="text" 
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Your full name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                    <input 
                      type="tel" 
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Your phone number"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Service Needed</label>
                    <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                      <option>Select a service</option>
                      <option>Emergency Repair</option>
                      <option>Installation</option>
                      <option>Maintenance</option>
                      <option>Inspection</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                    <textarea 
                      rows="4"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Describe your project or issue..."
                    ></textarea>
                  </div>
                  <button 
                    type="submit" 
                    className="w-full btn btn-primary"
                  >
                    Get Free Estimate
                  </button>
                </form>
              </div>
            </div>
          </div>
        </section>'''
