"""
Dynamic Website Deployment API Routes

Enhanced website deployment that creates personalized websites based on 
professional service categories and business information. Uses the new 
service template system for dynamic content generation.
"""

import asyncio
import json
import logging
import os
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field, HttpUrl

from app.api.deps import get_current_user, get_business_context
from app.application.services.dynamic_website_builder_service import (
    DynamicWebsiteBuilderService, WebsiteStructure
)
from app.application.services.service_validation_service import ServiceValidationService
from app.infrastructure.config.dependency_injection import get_business_repository
from app.domain.entities.business_branding import BusinessBranding

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dynamic-websites", tags=["Dynamic Website Deployment"])


class DynamicWebsiteRequest(BaseModel):
    """Request model for dynamic website deployment."""
    
    template_variant: str = Field(default="professional", description="Template variant to use")
    custom_domain: Optional[str] = Field(None, description="Custom domain (optional)")
    
    # Branding options
    primary_color: Optional[str] = Field("#3B82F6", description="Primary brand color")
    secondary_color: Optional[str] = Field("#10B981", description="Secondary brand color") 
    logo_url: Optional[HttpUrl] = Field(None, description="Logo URL")
    
    # Content preferences
    include_reviews: bool = Field(True, description="Include reviews section")
    include_service_areas: bool = Field(True, description="Include service areas")
    include_about: bool = Field(True, description="Include about section")
    enable_emergency_banner: bool = Field(True, description="Show emergency service banner")
    
    # Advanced options
    enable_seo_optimization: bool = Field(True, description="Enable advanced SEO features")
    enable_schema_markup: bool = Field(True, description="Include JSON-LD schema markup")
    enable_performance_optimization: bool = Field(True, description="Enable performance optimizations")


class DynamicWebsiteResponse(BaseModel):
    """Response model for dynamic website deployment."""
    
    deployment_id: str
    status: str
    website_url: Optional[str] = None
    preview_url: Optional[str] = None
    
    # Website structure info
    total_pages: int
    service_categories: int
    navigation_items: int
    
    # Build info
    build_started_at: datetime
    estimated_completion: Optional[datetime] = None
    
    # Generated content summary
    content_summary: Dict[str, Any]


class WebsiteStructureResponse(BaseModel):
    """Response model for website structure preview."""
    
    business_info: Dict[str, Any]
    navigation_menu: List[Dict[str, Any]]
    service_categories: List[Dict[str, Any]]
    seo_data: Dict[str, Any]
    estimated_pages: int
    promotional_offers: List[Dict[str, Any]]
    trust_signals: Dict[str, Any]
    service_areas: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]


# =============================================
# Dynamic Website Generation Endpoints
# =============================================

@router.get("/readiness-check")
async def check_website_generation_readiness(
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_repository = Depends(get_business_repository)
):
    """
    Check if a business is ready for website generation.
    
    This endpoint validates that the business has sufficient services
    and provides recommendations for improving website generation readiness.
    """
    
    try:
        business_id = UUID(business_context["business_id"])
        
        # Get business information
        business = await business_repository.get_by_id(business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Validate services
        validation_service = ServiceValidationService()
        readiness_info = await validation_service.get_website_generation_readiness(business)
        
        return {
            "business_id": str(business_id),
            "business_name": business.name,
            **readiness_info,
            "next_steps": {
                "can_generate_preview": readiness_info["is_ready_for_generation"],
                "can_deploy_website": readiness_info["is_ready_for_generation"] and readiness_info["total_services"] >= 3,
                "recommended_action": (
                    "generate_preview" if readiness_info["is_ready_for_generation"] 
                    else "configure_services"
                )
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check website generation readiness: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check readiness: {str(e)}"
        )


@router.post("/generate-structure", response_model=WebsiteStructureResponse)
async def generate_website_structure(
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_repository = Depends(get_business_repository)
):
    """
    Generate website structure preview based on business services.
    
    This endpoint analyzes the business's service categories and generates
    a complete website structure without actually building the site.
    Useful for previewing what the website will look like.
    
    IMPORTANT: Only generates websites for businesses with actual service offerings.
    """
    
    try:
        business_id = UUID(business_context["business_id"])
        
        # Get business information
        business = await business_repository.get_by_id(business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Validate that business has services before generating website
        validation_service = ServiceValidationService()
        validation_result = await validation_service.validate_business_services(business)
        
        if not validation_result.is_valid:
            logger.warning(f"Business {business.name} is not ready for website generation: {validation_result.issues}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Business not ready for website generation",
                    "issues": validation_result.issues,
                    "recommendations": [
                        "Add services to your business catalog",
                        "Ensure services have proper descriptions and pricing",
                        "Organize services into appropriate categories"
                    ],
                    "total_services": validation_result.total_services,
                    "total_categories": validation_result.total_categories
                }
            )
        
        logger.info(f"Generating website structure for {business.name} with {validation_result.total_services} services in {validation_result.total_categories} categories")
        
        # Generate website structure
        website_builder = DynamicWebsiteBuilderService()
        structure = await website_builder.generate_website_structure(business)
        
        # Format response
        return WebsiteStructureResponse(
            business_info=structure.business_info,
            navigation_menu=structure.navigation_menu,
            service_categories=[{
                'category_name': page.category_name,
                'category_slug': page.category_slug,
                'service_count': len(page.services),
                'page_url': page.page_url
            } for page in structure.category_pages],
            seo_data=structure.seo_data,
            estimated_pages=len(structure.category_pages) + 4,  # Categories + Home/About/Contact/Services
            promotional_offers=structure.promotional_offers,
            trust_signals=structure.trust_signals,
            service_areas=structure.service_areas,
            certifications=structure.certifications
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate website structure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate website structure: {str(e)}"
        )


@router.post("/deploy", response_model=DynamicWebsiteResponse)
async def deploy_dynamic_website(
    request: DynamicWebsiteRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_repository = Depends(get_business_repository)
):
    """
    Deploy a dynamic website with personalized content based on service categories.
    
    This creates a complete professional website with:
    - Dynamic navigation based on service categories
    - Individual pages for each service category
    - SEO-optimized content
    - Service-specific call-to-actions
    - Professional design and layout
    """
    
    try:
        business_id = UUID(business_context["business_id"])
        deployment_id = str(uuid4())
        
        # Get business information
        business = await business_repository.get_by_id(business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Validate that business has services before deploying website
        validation_service = ServiceValidationService()
        validation_result = await validation_service.validate_business_services(business, min_services_required=1)
        
        if not validation_result.is_valid:
            logger.warning(f"Cannot deploy website for {business.name}: {validation_result.issues}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Business not ready for website deployment",
                    "issues": validation_result.issues,
                    "recommendations": [
                        "Configure at least one service before website deployment",
                        "Add proper service descriptions and pricing",
                        "Consider adding services in multiple categories for better website structure"
                    ],
                    "total_services": validation_result.total_services,
                    "total_categories": validation_result.total_categories,
                    "readiness_check_url": "/api/dynamic-websites/readiness-check"
                }
            )
        
        logger.info(f"Deploying website for {business.name} with {validation_result.total_services} services in {validation_result.total_categories} categories")
        
        # Create branding object if custom colors provided
        branding = None
        if request.primary_color != "#3B82F6" or request.secondary_color != "#10B981" or request.logo_url:
            branding = BusinessBranding(
                business_id=business_id,
                primary_color=request.primary_color,
                secondary_color=request.secondary_color,
                logo_url=str(request.logo_url) if request.logo_url else None
            )
        
        # Generate website structure 
        website_builder = DynamicWebsiteBuilderService()
        structure = await website_builder.generate_website_structure(business, branding)
        
        # Start background deployment
        background_tasks.add_task(
            deploy_dynamic_website_background,
            deployment_id,
            structure,
            request,
            business
        )
        
        # Generate content summary
        content_summary = {
            'service_categories': len(structure.category_pages),
            'total_services': sum(len(page.services) for page in structure.category_pages),
            'navigation_items': len(structure.navigation_menu),
            'seo_keywords': len(structure.seo_data.get('keywords', [])),
            'emergency_services': sum(1 for page in structure.category_pages 
                                    for service in page.services 
                                    if service.get('is_emergency')),
            'featured_services': sum(1 for page in structure.category_pages 
                                   for service in page.services 
                                   if service.get('is_popular')),
            'promotional_offers': len(structure.promotional_offers),
            'service_areas': len(structure.service_areas),
            'certifications': len(structure.certifications),
            'trust_rating': structure.trust_signals.get('average_rating', 4.9),
            'total_reviews': structure.trust_signals.get('total_reviews', 0),
            'fuse_inspired_features': [
                'Promotional banners with rebates and offers',
                'Trust rating display with multiple platforms',
                'Customer review showcase',
                'Service area mapping',
                'Professional certifications display',
                'Emergency service highlighting',
                'Warranty promotion system'
            ]
        }
        
        return DynamicWebsiteResponse(
            deployment_id=deployment_id,
            status="building",
            total_pages=len(structure.category_pages) + 4,  # Categories + standard pages
            service_categories=len(structure.category_pages),
            navigation_items=len(structure.navigation_menu),
            build_started_at=datetime.utcnow(),
            estimated_completion=datetime.utcnow().replace(minute=datetime.utcnow().minute + 3),  # Estimated 3 minutes
            content_summary=content_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start dynamic website deployment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start website deployment: {str(e)}"
        )


async def deploy_dynamic_website_background(
    deployment_id: str,
    structure: WebsiteStructure,
    request: DynamicWebsiteRequest,
    business: Any
):
    """Background task for dynamic website deployment."""
    
    try:
        logger.info(f"Starting dynamic website deployment for {business.name} (ID: {deployment_id})")
        
        # Step 1: Setup build directory
        await asyncio.sleep(1)  # Simulate setup time
        build_dir = Path(f"/tmp/dynamic-websites/{deployment_id}")
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 2: Generate Next.js project structure
        logger.info("Setting up Next.js project with dynamic pages...")
        await setup_dynamic_nextjs_project(build_dir, structure, request)
        
        # Step 3: Generate all page files
        logger.info("Generating dynamic pages...")
        await generate_dynamic_pages(build_dir, structure, request)
        
        # Step 4: Generate navigation component
        logger.info("Generating dynamic navigation...")
        await generate_dynamic_navigation(build_dir, structure)
        
        # Step 5: Build the Next.js project
        logger.info("Building Next.js project...")
        success = await build_nextjs_project(build_dir)
        
        if success:
            # Step 6: Deploy to hosting (placeholder)
            website_url = await deploy_to_hosting(deployment_id, build_dir)
            logger.info(f"Website deployed successfully: {website_url}")
        else:
            logger.error(f"Failed to build website for deployment {deployment_id}")
            
    except Exception as e:
        logger.error(f"Dynamic website deployment failed: {str(e)}")


async def setup_dynamic_nextjs_project(
    build_dir: Path, 
    structure: WebsiteStructure, 
    request: DynamicWebsiteRequest
):
    """Setup Next.js project with dynamic configuration."""
    
    # Copy base website-builder template to build directory
    website_builder_path = Path(__file__).parent.parent.parent.parent.parent / "website-builder"
    
    if website_builder_path.exists():
        # Copy essential files
        import shutil
        
        # Copy package.json
        if (website_builder_path / "package.json").exists():
            shutil.copy2(website_builder_path / "package.json", build_dir)
        
        # Copy components directory
        if (website_builder_path / "components").exists():
            shutil.copytree(
                website_builder_path / "components",
                build_dir / "components",
                dirs_exist_ok=True
            )
        
        # Copy configuration files
        for config_file in ["next.config.ts", "tsconfig.json", "postcss.config.mjs"]:
            if (website_builder_path / config_file).exists():
                shutil.copy2(website_builder_path / config_file, build_dir)
        
        # Create app directory
        (build_dir / "app").mkdir(exist_ok=True)
        
        logger.info("Base Next.js project setup completed")


async def generate_dynamic_pages(
    build_dir: Path, 
    structure: WebsiteStructure, 
    request: DynamicWebsiteRequest
):
    """Generate all dynamic pages based on actual business services and categories."""
    
    app_dir = build_dir / "app"
    
    logger.info(f"Generating dynamic pages for {len(structure.category_pages)} service categories")
    
    # Generate layout.tsx
    await generate_layout_file(app_dir, structure)
    
    # Generate homepage (page.tsx) with actual business services
    await generate_homepage_file(app_dir, structure, request)
    
    # Only generate services overview page if there are services
    if structure.category_pages and len(structure.category_pages) > 0:
        await generate_services_overview_page(app_dir, structure)
        
        # Generate individual service category pages - only for categories with services
        for category_page in structure.category_pages:
            if category_page.services and len(category_page.services) > 0:
                logger.info(f"Generating page for category: {category_page.category_name} with {len(category_page.services)} services")
                await generate_category_page_file(app_dir, category_page, structure)
            else:
                logger.warning(f"Skipping empty category: {category_page.category_name}")
    else:
        logger.warning("No service categories found - generating basic services page")
        await generate_basic_services_page(app_dir, structure)
    
    # Generate standard pages
    await generate_about_page(app_dir, structure)
    await generate_contact_page(app_dir, structure)


async def generate_layout_file(app_dir: Path, structure: WebsiteStructure):
    """Generate the main layout.tsx file."""
    
    layout_content = f'''import {{ Inter, Poppins }} from 'next/font/google'
import './globals.css'

const inter = Inter({{
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap'
}})

const poppins = Poppins({{
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-poppins',
  display: 'swap'
}})

export const metadata = {{
  title: '{structure.seo_data.get("site_title", "Professional Services")}',
  description: '{structure.seo_data.get("site_description", "Professional services for your home and business")}',
  keywords: '{", ".join(structure.seo_data.get("keywords", []))}',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body className={{`${{inter.variable}} ${{poppins.variable}} antialiased`}}>
        {{children}}
      </body>
    </html>
  )
}}
'''
    
    with open(app_dir / "layout.tsx", "w") as f:
        f.write(layout_content)


async def generate_homepage_file(
    app_dir: Path, 
    structure: WebsiteStructure, 
    request: DynamicWebsiteRequest
):
    """Generate the main homepage file."""
    
    # This would be a comprehensive homepage template using the structure data
    homepage_content = f'''\'use client\';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import Hero from '@/components/base/Hero';
import ServiceCard from '@/components/base/ServiceCard';
import ContactForm from '@/components/base/ContactForm';

export default function HomePage() {{
  const business = {json.dumps(structure.business_info, indent=2)};
  const navigation = {json.dumps(structure.navigation_menu, indent=2)};
  const homepageData = {json.dumps(structure.homepage_data, indent=2)};
  const seo = {json.dumps(structure.seo_data, indent=2)};

  return (
    <Layout seo={{seo}} business={{business}}>
      <Navigation business={{business}} navigationItems={{navigation}} />
      
      <div id="home">
        <Hero
          {{...homepageData.hero}}
          business={{business}}
        />
      </div>

      <section id="services" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Our Services</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {{homepageData.services_overview?.map((service, index) => (
              <ServiceCard
                key={{index}}
                title={{service.title}}
                description={{service.description}}
                price={{service.price}}
                features={{service.features || []}}
                isPopular={{service.is_popular || false}}
                categorySlug={{service.category_slug}}
              />
            ))}}
          </div>
        </div>
      </section>

      <ContactForm business={{business}} />
    </Layout>
  );
}}
'''
    
    with open(app_dir / "page.tsx", "w") as f:
        f.write(homepage_content)


async def generate_category_page_file(
    app_dir: Path, 
    category_page, 
    structure: WebsiteStructure
):
    """Generate individual service category page."""
    
    category_dir = app_dir / category_page.category_slug
    category_dir.mkdir(exist_ok=True)
    
    category_content = f'''\'use client\';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import ServiceCard from '@/components/base/ServiceCard';
import ContactForm from '@/components/base/ContactForm';

export default function {category_page.category_name.replace(' ', '')}Page() {{
  const business = {json.dumps(structure.business_info, indent=2)};
  const navigation = {json.dumps(structure.navigation_menu, indent=2)};
  const services = {json.dumps(category_page.services, indent=2)};

  const seo = {{
    title: '{category_page.page_title}',
    description: '{category_page.meta_description}',
    keywords: ['{category_page.category_name.lower()}', 'services', '{structure.business_info["name"]}']
  }};

  return (
    <Layout seo={{seo}} business={{business}}>
      <Navigation business={{business}} navigationItems={{navigation}} />
      
      {{/* Hero Section */}}
      <section className="bg-blue-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">{category_page.hero_headline}</h1>
          <p className="text-xl opacity-90">{category_page.hero_subtitle}</p>
        </div>
      </section>

      {{/* Services Section */}}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">{category_page.category_name} Services</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {{services.map((service, index) => (
              <ServiceCard
                key={{index}}
                title={{service.title}}
                description={{service.description}}
                price={{service.price}}
                features={{service.features || []}}
                isPopular={{service.is_popular || false}}
                isEmergency={{service.is_emergency || false}}
              />
            ))}}
          </div>
        </div>
      </section>

      <ContactForm business={{business}} />
    </Layout>
  );
}}
'''
    
    with open(category_dir / "page.tsx", "w") as f:
        f.write(category_content)


async def generate_services_overview_page(app_dir: Path, structure: WebsiteStructure):
    """Generate the main services overview page."""
    
    services_dir = app_dir / "services"
    services_dir.mkdir(exist_ok=True)
    
    # Combine all services from all categories
    all_services = []
    for category_page in structure.category_pages:
        for service in category_page.services:
            service_with_category = service.copy()
            service_with_category['category'] = category_page.category_name
            service_with_category['category_slug'] = category_page.category_slug
            all_services.append(service_with_category)
    
    services_content = f'''\'use client\';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import ServiceCard from '@/components/base/ServiceCard';
import ContactForm from '@/components/base/ContactForm';

export default function ServicesPage() {{
  const business = {json.dumps(structure.business_info, indent=2)};
  const navigation = {json.dumps(structure.navigation_menu, indent=2)};
  const allServices = {json.dumps(all_services, indent=2)};
  const categories = {json.dumps([{"name": page.category_name, "slug": page.category_slug} for page in structure.category_pages], indent=2)};

  const seo = {{
    title: 'All Services - {structure.business_info["name"]}',
    description: 'Complete list of professional services offered by {structure.business_info["name"]}. Licensed & insured.',
    keywords: ['services', '{structure.business_info["name"]}', 'professional']
  }};

  return (
    <Layout seo={{seo}} business={{business}}>
      <Navigation business={{business}} navigationItems={{navigation}} />
      
      {{/* Hero Section */}}
      <section className="bg-blue-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">All Our Services</h1>
          <p className="text-xl opacity-90">Comprehensive professional services for your needs</p>
        </div>
      </section>

      {{/* Services by Category */}}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          {{categories.map((category, categoryIndex) => {{
            const categoryServices = allServices.filter(service => service.category_slug === category.slug);
            return (
              <div key={{categoryIndex}} className="mb-16">
                <h2 className="text-3xl font-bold mb-8">{{category.name}}</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {{categoryServices.map((service, serviceIndex) => (
                    <ServiceCard
                      key={{serviceIndex}}
                      title={{service.title}}
                      description={{service.description}}
                      price={{service.price}}
                      features={{service.features || []}}
                      isPopular={{service.is_popular || false}}
                      isEmergency={{service.is_emergency || false}}
                    />
                  ))}}
                </div>
              </div>
            );
          }})}}
        </div>
      </section>

      <ContactForm business={{business}} />
    </Layout>
  );
}}
'''
    
    with open(services_dir / "page.tsx", "w") as f:
        f.write(services_content)


async def generate_about_page(app_dir: Path, structure: WebsiteStructure):
    """Generate about page."""
    
    about_dir = app_dir / "about"
    about_dir.mkdir(exist_ok=True)
    
    about_content = f'''\'use client\';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import ContactForm from '@/components/base/ContactForm';

export default function AboutPage() {{
  const business = {json.dumps(structure.business_info, indent=2)};
  const navigation = {json.dumps(structure.navigation_menu, indent=2)};

  const seo = {{
    title: 'About Us - {structure.business_info["name"]}',
    description: 'Learn about {structure.business_info["name"]} - your trusted professional service provider.',
    keywords: ['about', '{structure.business_info["name"]}', 'professional', 'team']
  }};

  return (
    <Layout seo={{seo}} business={{business}}>
      <Navigation business={{business}} navigationItems={{navigation}} />
      
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-4xl font-bold mb-8">About {{business.name}}</h1>
          
          <div className="prose prose-lg max-w-none">
            <p className="text-xl text-gray-600 mb-6">
              {{business.description}}
            </p>
            
            <h2>Our Service Areas</h2>
            <p>We proudly serve:</p>
            <ul>
              {{business.service_areas?.map((area, index) => (
                <li key={{index}}>{{area}}</li>
              ))}}
            </ul>
            
            <h2>Why Choose Us?</h2>
            <ul>
              <li>Licensed & Insured</li>
              <li>Professional Service</li>
              <li>Satisfaction Guaranteed</li>
              <li>Emergency Service Available</li>
            </ul>
          </div>
        </div>
      </section>

      <ContactForm business={{business}} />
    </Layout>
  );
}}
'''
    
    with open(about_dir / "page.tsx", "w") as f:
        f.write(about_content)


async def generate_contact_page(app_dir: Path, structure: WebsiteStructure):
    """Generate contact page."""
    
    contact_dir = app_dir / "contact"
    contact_dir.mkdir(exist_ok=True)
    
    contact_content = f'''\'use client\';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import ContactForm from '@/components/base/ContactForm';

export default function ContactPage() {{
  const business = {json.dumps(structure.business_info, indent=2)};
  const navigation = {json.dumps(structure.navigation_menu, indent=2)};

  const seo = {{
    title: 'Contact Us - {structure.business_info["name"]}',
    description: 'Get in touch with {structure.business_info["name"]} for professional services. Call {structure.business_info.get("phone", "")} today.',
    keywords: ['contact', '{structure.business_info["name"]}', 'phone', 'address']
  }};

  return (
    <Layout seo={{seo}} business={{business}}>
      <Navigation business={{business}} navigationItems={{navigation}} />
      
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-12">
            <div>
              <h1 className="text-4xl font-bold mb-8">Contact {{business.name}}</h1>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-2">Phone</h3>
                  <p className="text-lg">
                    <a href="tel:{{business.phone}}" className="text-blue-600 hover:text-blue-800">
                      {{business.phone}}
                    </a>
                  </p>
                </div>
                
                <div>
                  <h3 className="text-xl font-semibold mb-2">Email</h3>
                  <p className="text-lg">
                    <a href="mailto:{{business.email}}" className="text-blue-600 hover:text-blue-800">
                      {{business.email}}
                    </a>
                  </p>
                </div>
                
                <div>
                  <h3 className="text-xl font-semibold mb-2">Address</h3>
                  <p className="text-lg">{{business.address}}</p>
                </div>
                
                <div>
                  <h3 className="text-xl font-semibold mb-2">Service Areas</h3>
                  <p className="text-lg">
                    {{business.service_areas?.join(', ')}}
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <ContactForm business={{business}} />
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}}
'''
    
    with open(contact_dir / "page.tsx", "w") as f:
        f.write(contact_content)


async def generate_basic_services_page(app_dir: Path, structure: WebsiteStructure):
    """Generate a basic services page for businesses with no service categories."""
    
    services_dir = app_dir / "services"
    services_dir.mkdir(exist_ok=True)
    
    basic_services_content = f'''\'use client\';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import ContactForm from '@/components/base/ContactForm';
import {{ Wrench, Phone }} from 'lucide-react';

export default function ServicesPage() {{
  const business = {json.dumps(structure.business_info, indent=2)};
  const navigation = {json.dumps(structure.navigation_menu, indent=2)};

  const seo = {{
    title: 'Services - {structure.business_info["name"]}',
    description: 'Professional services from {structure.business_info["name"]}. Licensed & insured.',
    keywords: ['services', '{structure.business_info["name"]}', 'professional']
  }};

  return (
    <Layout seo={{seo}} business={{business}}>
      <Navigation business={{business}} navigationItems={{navigation}} />
      
      {{/* Hero Section */}}
      <section className="bg-blue-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">Professional Services</h1>
          <p className="text-xl opacity-90">Quality service from {{business.name}}</p>
        </div>
      </section>

      {{/* Services Coming Soon */}}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="bg-gray-50 rounded-lg p-12">
            <Wrench size={{48}} className="mx-auto text-blue-600 mb-6" />
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Services Information Coming Soon
            </h2>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              We're currently updating our service catalog. In the meantime, please contact us 
              directly to discuss your specific needs and how we can help.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={{() => window.location.href = `tel:${{business.phone}}`}}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200 flex items-center gap-2 justify-center"
              >
                <Phone size={{20}} />
                Call {{business.phone}}
              </button>
              <button 
                onClick={{() => document.getElementById('contact')?.scrollIntoView({{ behavior: 'smooth' }})}}
                className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200"
              >
                Contact Us
              </button>
            </div>
          </div>
        </div>
      </section>

      <div id="contact">
        <ContactForm business={{business}} />
      </div>
    </Layout>
  );
}}
'''
    
    with open(services_dir / "page.tsx", "w") as f:
        f.write(basic_services_content)


async def generate_dynamic_navigation(build_dir: Path, structure: WebsiteStructure):
    """Generate dynamic navigation component that handles the menu structure."""
    
    # This would create an enhanced navigation component that uses the dynamic menu structure
    # For now, we'll use the existing navigation component
    pass


async def build_nextjs_project(build_dir: Path) -> bool:
    """Build the Next.js project."""
    
    try:
        # Install dependencies
        logger.info("Installing dependencies...")
        install_result = subprocess.run(
            ["npm", "install"],
            cwd=build_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if install_result.returncode != 0:
            logger.error(f"npm install failed: {install_result.stderr}")
            return False
        
        # Build the project
        logger.info("Building Next.js project...")
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=build_dir,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if build_result.returncode == 0:
            logger.info("Next.js build completed successfully")
            return True
        else:
            logger.error(f"Next.js build failed: {build_result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Build process failed: {str(e)}")
        return False


async def deploy_to_hosting(deployment_id: str, build_dir: Path) -> Optional[str]:
    """Deploy the built website to Cloudflare Pages."""
    
    try:
        logger.info(f"🚀 Deploying website to Cloudflare Pages...")
        
        # Cloudflare deployment configuration
        env = os.environ.copy()
        env['CLOUDFLARE_API_TOKEN'] = os.getenv('CLOUDFLARE_API_TOKEN', 'muGRINW0SuRdhq5otaMRwMf0piAn24wFdRgrGiXl')
        env['CLOUDFLARE_ACCOUNT_ID'] = os.getenv('CLOUDFLARE_ACCOUNT_ID', '4e131688804526ec202c7d530e635307')
        
        # Use existing project name
        project_name = "hero365-websites"
        out_dir = build_dir / "out"
        
        if not out_dir.exists():
            logger.error(f"Build output directory not found: {out_dir}")
            return None
        
        # Deploy using wrangler CLI
        cmd = [
            'npx', 'wrangler', 'pages', 'deploy', str(out_dir),
            '--project-name', project_name,
            '--commit-dirty=true'
        ]
        
        logger.info(f"Running deployment command: {' '.join(cmd)}")
        
        # Run deployment in build directory for context
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(build_dir)
        )
        
        if result.returncode == 0:
            # Parse URL from output
            website_url = None
            for line in result.stdout.split('\n'):
                if 'https://' in line and '.pages.dev' in line:
                    # Extract the URL using regex
                    url_match = re.search(r'https://[^\s]+\.pages\.dev[^\s]*', line)
                    if url_match:
                        website_url = url_match.group(0).rstrip('.,!')
                        break
            
            if not website_url:
                # Generate expected URL if we can't parse it
                website_url = f"https://{deployment_id[:8]}.hero365-websites.pages.dev"
            
            logger.info(f"✅ Website deployed successfully to: {website_url}")
            return website_url
            
        else:
            logger.error(f"❌ Cloudflare deployment failed:")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return None
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Cloudflare deployment timed out")
        return None
    except Exception as e:
        logger.error(f"❌ Deployment failed: {str(e)}")
        return None


@router.get("/status/{deployment_id}")
async def get_deployment_status(
    deployment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a dynamic website deployment."""
    
    # This would track deployment status in a database/cache
    # For now, return a mock status
    return {
        "deployment_id": deployment_id,
        "status": "completed",
        "progress": 100,
        "current_step": "Deployment completed",
        "website_url": f"https://{deployment_id}.hero365-websites.pages.dev",
        "build_logs": ["Setup completed", "Pages generated", "Build successful", "Deployed"]
    }
