"""
Static Site Builder Service

Service for generating static Next.js websites from template data.
Handles JSON artifact generation, route manifest creation, and Next.js build process.
"""

import json
import uuid
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...domain.entities.website_template import TemplateProps, BuildStatus
from ..exceptions.application_exceptions import BuildError, TemplateNotFoundError


class StaticSiteBuilderService:
    """Service for building static websites from template data."""
    
    def __init__(self, build_root: str = "/tmp/website-builds"):
        self.build_root = Path(build_root)
        self.build_root.mkdir(parents=True, exist_ok=True)
        
        # Template source directory
        self.template_source = Path(__file__).parent.parent.parent.parent.parent / "website-builder"
    
    async def build_static_site(
        self,
        template_props: TemplateProps,
        build_id: str,
        template_name: str = "professional"
    ) -> Dict[str, Any]:
        """
        Build a static Next.js site from template props.
        
        Args:
            template_props: Complete template data
            build_id: Unique build identifier
            template_name: Template to use
            
        Returns:
            Dict with build results including paths and metadata
            
        Raises:
            BuildError: If build process fails
            TemplateNotFoundError: If template doesn't exist
        """
        build_dir = self.build_root / build_id
        
        try:
            # Clean up any existing build directory
            if build_dir.exists():
                shutil.rmtree(build_dir)
            
            # Create build directory
            build_dir.mkdir(parents=True)
            
            # Copy template source
            await self._copy_template_source(build_dir, template_name)
            
            # Generate data artifacts
            await self._generate_data_artifacts(build_dir, template_props)
            
            # Generate route manifest
            await self._generate_route_manifest(build_dir, template_props)
            
            # Update package.json with business-specific info
            await self._update_package_json(build_dir, template_props)
            
            # Generate Next.js config
            await self._generate_next_config(build_dir, template_props)
            
            # Generate PostCSS config
            await self._generate_postcss_config(build_dir)
            
            # Generate Tailwind config
            await self._generate_tailwind_config(build_dir)
            
            # Generate global CSS
            await self._generate_global_css(build_dir)
            
            # Install dependencies
            await self._install_dependencies(build_dir)
            
            # Build the site
            build_result = await self._build_nextjs_site(build_dir)
            
            return {
                "build_id": build_id,
                "build_dir": str(build_dir),
                "out_dir": str(build_dir / "out"),
                "status": BuildStatus.SUCCESS,
                "build_time": build_result["build_time"],
                "build_log": build_result["build_log"],
                "pages_generated": build_result["pages_generated"],
                "assets_generated": build_result["assets_generated"]
            }
            
        except Exception as e:
            return {
                "build_id": build_id,
                "build_dir": str(build_dir) if build_dir.exists() else None,
                "status": BuildStatus.FAILED,
                "error": str(e),
                "build_log": getattr(e, 'build_log', None)
            }
    
    async def _copy_template_source(self, build_dir: Path, template_name: str):
        """Copy template source files to build directory."""
        if not self.template_source.exists():
            raise TemplateNotFoundError(f"Template source directory not found: {self.template_source}")
        
        # Copy entire website-builder directory
        shutil.copytree(self.template_source, build_dir, dirs_exist_ok=True)
        
        # Verify template exists
        template_dir = build_dir / "app" / "templates" / template_name
        if not template_dir.exists():
            raise TemplateNotFoundError(f"Template '{template_name}' not found in {template_dir}")
    
    async def _generate_data_artifacts(self, build_dir: Path, template_props: TemplateProps):
        """Generate JSON data artifacts for the site."""
        data_dir = build_dir / "lib" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Business data
        business_data = {
            "id": str(template_props.business.id),
            "name": template_props.business.name,
            "description": template_props.business.description,
            "phone_number": template_props.business.phone_number,
            "business_email": template_props.business.business_email,
            "website": template_props.business.website,
            "logo_url": template_props.business.logo_url,
            "address": template_props.business.address,
            "city": template_props.business.city,
            "state": template_props.business.state,
            "zip_code": template_props.business.zip_code,
            "trades": template_props.business.trades,
            "service_areas": template_props.business.service_areas,
            "business_hours": template_props.business.business_hours,
            "primary_trade": template_props.business.primary_trade,
            "seo_keywords": template_props.business.seo_keywords
        }
        
        with open(data_dir / "business.json", "w") as f:
            json.dump(business_data, f, indent=2, default=str)
        
        # Service categories
        service_categories_data = []
        for category in template_props.service_categories:
            service_categories_data.append({
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "icon_name": category.icon_name,
                "slug": category.slug,
                "services_count": category.services_count,
                "is_featured": category.is_featured,
                "sort_order": category.sort_order
            })
        
        with open(data_dir / "service-categories.json", "w") as f:
            json.dump(service_categories_data, f, indent=2, default=str)
        
        # Promotional offers
        promos_data = []
        for promo in template_props.promos:
            if promo.is_currently_active():
                promos_data.append({
                    "id": str(promo.id),
                    "title": promo.title,
                    "subtitle": promo.subtitle,
                    "description": promo.description,
                    "offer_type": promo.offer_type.value,
                    "price_label": promo.price_label,
                    "badge_text": promo.badge_text,
                    "cta_text": promo.cta_text,
                    "cta_link": promo.cta_link,
                    "placement": promo.placement.value,
                    "priority": promo.priority,
                    "is_featured": promo.is_featured
                })
        
        with open(data_dir / "promos.json", "w") as f:
            json.dump(promos_data, f, indent=2, default=str)
        
        # Ratings
        ratings_data = []
        for rating in template_props.ratings:
            if rating.is_active:
                ratings_data.append({
                    "platform": rating.platform.value,
                    "rating": float(rating.rating),
                    "review_count": rating.review_count,
                    "display_name": rating.get_display_name(),
                    "logo_url": rating.logo_url,
                    "profile_url": rating.profile_url,
                    "is_featured": rating.is_featured
                })
        
        with open(data_dir / "ratings.json", "w") as f:
            json.dump(ratings_data, f, indent=2, default=str)
        
        # Awards and certifications
        awards_data = []
        for award in template_props.awards:
            if award.is_active and award.display_on_website:
                awards_data.append({
                    "id": str(award.id),
                    "name": award.name,
                    "issuing_organization": award.issuing_organization,
                    "description": award.description,
                    "certificate_type": award.certificate_type.value if award.certificate_type else None,
                    "logo_url": award.logo_url,
                    "certificate_url": award.certificate_url,
                    "verification_url": award.verification_url,
                    "is_featured": award.is_featured,
                    "is_current": award.is_current,
                    "trade_relevance": award.trade_relevance
                })
        
        with open(data_dir / "awards.json", "w") as f:
            json.dump(awards_data, f, indent=2, default=str)
        
        # Partnerships
        partnerships_data = []
        for partnership in template_props.partnerships:
            if partnership.is_partnership_active() and partnership.display_on_website:
                partnerships_data.append({
                    "id": str(partnership.id),
                    "partner_name": partnership.partner_name,
                    "partner_type": partnership.partner_type.value,
                    "partnership_level": partnership.partnership_level,
                    "description": partnership.description,
                    "partnership_benefits": partnership.partnership_benefits,
                    "logo_url": partnership.logo_url,
                    "partner_url": partnership.partner_url,
                    "verification_url": partnership.verification_url,
                    "is_featured": partnership.is_featured,
                    "trade_relevance": partnership.trade_relevance
                })
        
        with open(data_dir / "partnerships.json", "w") as f:
            json.dump(partnerships_data, f, indent=2, default=str)
        
        # Testimonials
        testimonials_data = []
        for testimonial in template_props.testimonials:
            if testimonial.is_ready_for_display():
                testimonials_data.append({
                    "id": str(testimonial.id),
                    "quote": testimonial.quote,
                    "rating": float(testimonial.rating) if testimonial.rating else None,
                    "customer_name": testimonial.get_customer_display_name(),
                    "customer_location": testimonial.customer_location,
                    "service_performed": testimonial.service_performed,
                    "service_date": testimonial.service_date.isoformat() if testimonial.service_date else None,
                    "is_featured": testimonial.is_featured,
                    "is_verified": testimonial.is_verified
                })
        
        with open(data_dir / "testimonials.json", "w") as f:
            json.dump(testimonials_data, f, indent=2, default=str)
        
        # Locations
        locations_data = []
        for location in template_props.locations:
            if location.is_active and location.display_on_website:
                locations_data.append({
                    "id": str(location.id),
                    "name": location.get_display_name(),
                    "address": location.get_full_address(),
                    "city": location.city,
                    "state": location.state,
                    "zip_code": location.zip_code,
                    "latitude": float(location.latitude) if location.latitude else None,
                    "longitude": float(location.longitude) if location.longitude else None,
                    "service_radius_miles": location.service_radius_miles,
                    "location_type": location.location_type.value,
                    "is_primary": location.is_primary,
                    "services_offered": location.services_offered,
                    "trades_covered": location.trades_covered,
                    "page_slug": location.page_slug
                })
        
        with open(data_dir / "locations.json", "w") as f:
            json.dump(locations_data, f, indent=2, default=str)
    
    async def _generate_route_manifest(self, build_dir: Path, template_props: TemplateProps):
        """Generate route manifest for static generation."""
        routes = [
            {"path": "/", "name": "Home", "title": f"{template_props.business.name} - Professional Services"},
            {"path": "/about", "name": "About", "title": f"About {template_props.business.name}"},
            {"path": "/services", "name": "Services", "title": f"Services - {template_props.business.name}"},
            {"path": "/contact", "name": "Contact", "title": f"Contact {template_props.business.name}"},
            {"path": "/reviews", "name": "Reviews", "title": f"Customer Reviews - {template_props.business.name}"}
        ]
        
        # Add service category routes
        for category in template_props.service_categories:
            routes.append({
                "path": f"/services/{category.slug}",
                "name": category.name,
                "title": f"{category.name} Services - {template_props.business.name}"
            })
        
        # Add location routes
        for location in template_props.locations:
            if location.page_slug:
                routes.append({
                    "path": f"/locations/{location.page_slug}",
                    "name": f"Service Area: {location.get_display_name()}",
                    "title": f"Services in {location.get_display_name()} - {template_props.business.name}"
                })
        
        manifest = {
            "routes": routes,
            "generated_at": datetime.utcnow().isoformat(),
            "template_name": template_props.template_name,
            "business_name": template_props.business.name
        }
        
        with open(build_dir / "lib" / "route-manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
    
    async def _update_package_json(self, build_dir: Path, template_props: TemplateProps):
        """Update package.json with business-specific information."""
        package_json_path = build_dir / "package.json"
        
        with open(package_json_path, "r") as f:
            package_data = json.load(f)
        
        # Update with business info
        business_slug = template_props.business.name.lower().replace(" ", "-").replace("&", "and")
        package_data["name"] = f"{business_slug}-website"
        package_data["description"] = f"Professional website for {template_props.business.name}"
        
        # Ensure required dependencies
        if "dependencies" not in package_data:
            package_data["dependencies"] = {}
        
        if "devDependencies" not in package_data:
            package_data["devDependencies"] = {}
        
        # Add PostCSS and Tailwind dependencies
        package_data["devDependencies"].update({
            "postcss": "^8.4.31",
            "autoprefixer": "^10.4.16",
            "tailwindcss": "^3.4.0"
        })
        
        with open(package_json_path, "w") as f:
            json.dump(package_data, f, indent=2)
    
    async def _generate_next_config(self, build_dir: Path, template_props: TemplateProps):
        """Generate Next.js configuration."""
        config_content = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  typescript: {
    ignoreBuildErrors: true
  },
  eslint: {
    ignoreDuringBuilds: true
  }
}

module.exports = nextConfig
'''
        
        with open(build_dir / "next.config.js", "w") as f:
            f.write(config_content)
    
    async def _generate_postcss_config(self, build_dir: Path):
        """Generate PostCSS configuration."""
        config_content = '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
        
        with open(build_dir / "postcss.config.js", "w") as f:
            f.write(config_content)
    
    async def _generate_tailwind_config(self, build_dir: Path):
        """Generate Tailwind CSS configuration."""
        config_content = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
        
        with open(build_dir / "tailwind.config.js", "w") as f:
            f.write(config_content)
    
    async def _generate_global_css(self, build_dir: Path):
        """Generate global CSS with Tailwind directives."""
        css_content = '''@tailwind base;
@tailwind components;
@tailwind utilities;
'''
        
        globals_css_path = build_dir / "app" / "globals.css"
        with open(globals_css_path, "w") as f:
            f.write(css_content)
    
    async def _install_dependencies(self, build_dir: Path):
        """Install npm dependencies."""
        try:
            result = subprocess.run(
                ["npm", "ci"],
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise BuildError(f"npm install failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise BuildError("npm install timed out after 5 minutes")
        except Exception as e:
            raise BuildError(f"Failed to install dependencies: {str(e)}")
    
    async def _build_nextjs_site(self, build_dir: Path) -> Dict[str, Any]:
        """Build the Next.js site."""
        start_time = datetime.utcnow()
        
        try:
            # Run Next.js build
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            build_time = (datetime.utcnow() - start_time).total_seconds()
            
            if result.returncode != 0:
                error = BuildError(f"Next.js build failed: {result.stderr}")
                error.build_log = result.stdout + "\n" + result.stderr
                raise error
            
            # Count generated files
            out_dir = build_dir / "out"
            if not out_dir.exists():
                raise BuildError("Build completed but 'out' directory not found")
            
            pages_generated = len(list(out_dir.glob("**/*.html")))
            assets_generated = len(list(out_dir.glob("**/*"))) - pages_generated
            
            return {
                "build_time": build_time,
                "build_log": result.stdout,
                "pages_generated": pages_generated,
                "assets_generated": assets_generated
            }
            
        except subprocess.TimeoutExpired:
            raise BuildError("Next.js build timed out after 10 minutes")
        except Exception as e:
            if not isinstance(e, BuildError):
                raise BuildError(f"Build failed: {str(e)}")
            raise
    
    def cleanup_build(self, build_id: str):
        """Clean up build directory."""
        build_dir = self.build_root / build_id
        if build_dir.exists():
            shutil.rmtree(build_dir)
