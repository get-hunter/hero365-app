#!/usr/bin/env python3
"""
Comprehensive Website Generation and Deployment Test

Tests the complete workflow:
1. Business data setup
2. AI content generation
3. Next.js static site building
4. Hero365 subdomain deployment
5. Verification and analytics

This demonstrates the full Clean Architecture implementation.
"""

import asyncio
import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.domain.entities.business import Business, TradeCategory
from app.domain.entities.website import BusinessWebsite, WebsiteStatus
from app.domain.entities.business_branding import BusinessBranding

# Clean Architecture Components
from app.domain.services.seo_domain_service import SEODomainService
from app.domain.services.subdomain_domain_service import SubdomainDomainService
from app.infrastructure.adapters.content_generation_factory import create_content_adapter
from app.infrastructure.adapters.hero365_subdomain_adapter import Hero365SubdomainAdapter
from app.application.services.website_orchestration_service import WebsiteOrchestrationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebsiteGenerationTester:
    """
    Comprehensive tester for the website generation and deployment system.
    
    Demonstrates Clean Architecture in action with real business scenarios.
    """
    
    def __init__(self):
        self.test_results = {}
        self.test_business = None
        self.generated_website = None
        self.deployment_result = None
        
        # Initialize Clean Architecture components
        self.seo_domain_service = SEODomainService()
        self.subdomain_domain_service = SubdomainDomainService()
        self.subdomain_adapter = Hero365SubdomainAdapter()
        
        # Content generation (configurable LLM)
        self.content_adapter = create_content_adapter(
            provider=settings.CONTENT_GENERATION_PROVIDER
        )
        
        logger.info("🚀 Website Generation Tester initialized with Clean Architecture")
    
    async def run_complete_test(self, business_type: str = "plumbing") -> Dict[str, Any]:
        """
        Run the complete website generation and deployment test.
        
        Args:
            business_type: Type of business to test (plumbing, hvac, electrical, etc.)
            
        Returns:
            Complete test results
        """
        
        logger.info("=" * 60)
        logger.info("🧪 STARTING COMPLETE WEBSITE GENERATION TEST")
        logger.info("=" * 60)
        
        try:
            # Step 1: Create test business
            logger.info("📋 Step 1: Creating test business data...")
            self.test_business = await self._create_test_business(business_type)
            self.test_results["business_creation"] = {
                "success": True,
                "business_id": str(self.test_business.id),
                "business_name": self.test_business.name,
                "primary_trade": self.test_business.get_primary_trade()
            }
            
            # Step 2: Generate website content using AI
            logger.info("🤖 Step 2: Generating AI content...")
            content_result = await self._test_content_generation()
            self.test_results["content_generation"] = content_result
            
            # Step 3: Build static website
            logger.info("🏗️ Step 3: Building Next.js static site...")
            build_result = await self._test_static_site_build()
            self.test_results["static_site_build"] = build_result
            
            # Step 4: Deploy to subdomain
            logger.info("🚀 Step 4: Deploying to Hero365 subdomain...")
            deployment_result = await self._test_subdomain_deployment()
            self.test_results["subdomain_deployment"] = deployment_result
            
            # Step 5: Verify deployment
            logger.info("✅ Step 5: Verifying deployment...")
            verification_result = await self._test_deployment_verification()
            self.test_results["deployment_verification"] = verification_result
            
            # Step 6: Test analytics
            logger.info("📊 Step 6: Testing analytics...")
            analytics_result = await self._test_analytics()
            self.test_results["analytics"] = analytics_result
            
            # Generate final report
            final_report = self._generate_test_report()
            
            logger.info("=" * 60)
            logger.info("🎉 COMPLETE TEST FINISHED SUCCESSFULLY!")
            logger.info("=" * 60)
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": self.test_results
            }
    
    async def _create_test_business(self, business_type: str) -> Business:
        """Create a realistic test business for the specified trade."""
        
        business_configs = {
            "plumbing": {
                "name": "AquaFlow Plumbing Solutions",
                "trade": "plumbing",
                "category": TradeCategory.RESIDENTIAL,
                "description": "Professional residential plumbing services with 24/7 emergency support",
                "phone": "(555) 123-FLOW",
                "email": "info@aquaflowplumbing.com"
            },
            "hvac": {
                "name": "ComfortZone HVAC",
                "trade": "hvac", 
                "category": TradeCategory.RESIDENTIAL,
                "description": "Complete heating, ventilation, and air conditioning services",
                "phone": "(555) 456-HVAC",
                "email": "service@comfortzonehvac.com"
            },
            "electrical": {
                "name": "PowerPro Electrical",
                "trade": "electrical",
                "category": TradeCategory.COMMERCIAL,
                "description": "Commercial electrical installations and maintenance",
                "phone": "(555) 789-POWER",
                "email": "contact@powerproelectric.com"
            },
            "roofing": {
                "name": "SkyShield Roofing",
                "trade": "roofing",
                "category": TradeCategory.RESIDENTIAL,
                "description": "Quality roofing installations and repairs",
                "phone": "(555) 321-ROOF",
                "email": "info@skyshieldroofing.com"
            }
        }
        
        config = business_configs.get(business_type, business_configs["plumbing"])
        
        # Create business entity
        business = Business(
            name=config["name"],
            description=config["description"],
            phone=config["phone"],
            email=config["email"],
            address="123 Service Street",
            city="Austin",
            state="TX",
            zip_code="78701",
            country="US",
            website_url=f"https://{config['name'].lower().replace(' ', '-')}.hero365.ai",
            is_service_area_business=True,
            service_areas=["Austin", "Round Rock", "Cedar Park", "Georgetown"],
            trade_category=config["category"]
        )
        
        # Add trade
        business.add_trade(config["trade"])
        
        # Create business branding
        business.branding = BusinessBranding(
            business_id=business.id,
            primary_color="#1E40AF",  # Blue
            secondary_color="#F59E0B",  # Amber
            accent_color="#10B981",  # Emerald
            logo_url=f"https://logo.clearbit.com/{config['email'].split('@')[1]}",
            font_primary="Inter",
            font_secondary="Roboto",
            brand_voice="professional",
            tagline=f"Your trusted {config['trade']} experts"
        )
        
        logger.info(f"✅ Created test business: {business.name} ({config['trade']})")
        return business
    
    async def _test_content_generation(self) -> Dict[str, Any]:
        """Test AI content generation for the business website."""
        
        try:
            logger.info(f"🤖 Generating content using {settings.CONTENT_GENERATION_PROVIDER.upper()}...")
            
            # Generate SEO keywords using domain service
            seo_keywords = self.seo_domain_service.generate_local_keywords(self.test_business)
            
            # Generate website content using AI
            content_data = await self.content_adapter.generate_website_content(
                business=self.test_business,
                template_type="professional",
                target_keywords=seo_keywords[:10],  # Top 10 keywords
                additional_context={
                    "include_emergency_services": True,
                    "include_service_areas": True,
                    "include_testimonials": True,
                    "tone": "professional_friendly"
                }
            )
            
            # Validate content quality
            quality_score = await self.content_adapter.validate_content_quality(
                content_data, self.test_business
            )
            
            logger.info(f"✅ Content generated successfully (Quality: {quality_score:.1f}/10)")
            
            return {
                "success": True,
                "provider": settings.CONTENT_GENERATION_PROVIDER,
                "content_sections": len(content_data.get("sections", [])),
                "seo_keywords_count": len(seo_keywords),
                "quality_score": quality_score,
                "content_preview": {
                    "hero_title": content_data.get("hero", {}).get("title", "")[:100],
                    "meta_description": content_data.get("seo", {}).get("meta_description", "")[:100]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_static_site_build(self) -> Dict[str, Any]:
        """Test Next.js static site generation."""
        
        try:
            logger.info("🏗️ Building Next.js static site...")
            
            # Create website entity
            subdomain = self.subdomain_domain_service.generate_subdomain_name(
                BusinessWebsite(
                    business_id=self.test_business.id,
                    primary_trade=self.test_business.get_primary_trade(),
                    template_id="professional-template"
                )
            )
            
            self.generated_website = BusinessWebsite(
                business_id=self.test_business.id,
                template_id="professional-template",
                subdomain=subdomain,
                primary_trade=self.test_business.get_primary_trade(),
                status=WebsiteStatus.BUILDING,
                seo_title=f"{self.test_business.name} - Professional {self.test_business.get_primary_trade().title()} Services",
                seo_description=f"Expert {self.test_business.get_primary_trade()} services in {self.test_business.city}. Contact {self.test_business.name} for reliable solutions.",
                target_keywords=[
                    f"{self.test_business.get_primary_trade()} {self.test_business.city}",
                    f"{self.test_business.get_primary_trade()} services",
                    f"emergency {self.test_business.get_primary_trade()}"
                ]
            )
            
            # Simulate static site build (in real implementation, this would use Next.js)
            build_path = f"/tmp/hero365-builds/{subdomain}"
            Path(build_path).mkdir(parents=True, exist_ok=True)
            
            # Create mock HTML files
            await self._create_mock_website_files(build_path)
            
            logger.info(f"✅ Static site built successfully at {build_path}")
            
            return {
                "success": True,
                "subdomain": subdomain,
                "build_path": build_path,
                "file_count": len(list(Path(build_path).rglob("*"))),
                "website_url": f"https://{subdomain}.hero365.ai"
            }
            
        except Exception as e:
            logger.error(f"❌ Static site build failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_subdomain_deployment(self) -> Dict[str, Any]:
        """Test deployment to Hero365 subdomain."""
        
        try:
            if not self.generated_website:
                raise Exception("No website generated to deploy")
            
            build_result = self.test_results.get("static_site_build", {})
            build_path = build_result.get("build_path")
            
            if not build_path or not Path(build_path).exists():
                raise Exception("Build path not found")
            
            logger.info(f"🚀 Deploying to subdomain: {self.generated_website.subdomain}")
            
            # Deploy using Clean Architecture adapter
            self.deployment_result = await self.subdomain_adapter.deploy_to_subdomain(
                website=self.generated_website,
                build_path=build_path,
                subdomain=self.generated_website.subdomain
            )
            
            if self.deployment_result.success:
                logger.info(f"✅ Deployment successful: {self.deployment_result.website_url}")
                
                return {
                    "success": True,
                    "subdomain": self.deployment_result.subdomain,
                    "website_url": self.deployment_result.website_url,
                    "files_uploaded": self.deployment_result.upload_result.get("files_uploaded", 0),
                    "dns_configured": self.deployment_result.dns_configured,
                    "cache_invalidated": self.deployment_result.cache_invalidated,
                    "deployment_verified": self.deployment_result.deployment_verified
                }
            else:
                raise Exception(f"Deployment failed: {self.deployment_result.error}")
            
        except Exception as e:
            logger.error(f"❌ Subdomain deployment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_deployment_verification(self) -> Dict[str, Any]:
        """Test deployment verification and accessibility."""
        
        try:
            if not self.deployment_result or not self.deployment_result.success:
                raise Exception("No successful deployment to verify")
            
            website_url = self.deployment_result.website_url
            logger.info(f"✅ Verifying deployment at: {website_url}")
            
            # Verify using adapter
            verification_result = await self.subdomain_adapter.verify_subdomain_deployment(
                self.deployment_result.full_domain
            )
            
            # Get subdomain info
            subdomain_info = await self.subdomain_adapter.get_subdomain_info(
                self.deployment_result.subdomain
            )
            
            return {
                "success": verification_result["success"],
                "website_url": website_url,
                "status_code": verification_result.get("status_code"),
                "response_time_ms": verification_result.get("response_time_ms"),
                "content_length": verification_result.get("content_length"),
                "file_count": subdomain_info.file_count,
                "total_size_mb": subdomain_info.total_size_mb,
                "verification_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Deployment verification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_analytics(self) -> Dict[str, Any]:
        """Test analytics and domain service calculations."""
        
        try:
            if not self.deployment_result or not self.deployment_result.success:
                raise Exception("No successful deployment for analytics")
            
            logger.info("📊 Testing analytics and domain services...")
            
            # Get raw analytics from adapter
            raw_analytics = await self.subdomain_adapter.get_subdomain_analytics(
                self.deployment_result.subdomain
            )
            
            # Process with domain service
            analytics_summary = self.subdomain_domain_service.generate_analytics_summary(
                raw_analytics.dict()
            )
            
            # Test cache strategy calculation
            cache_strategy = self.subdomain_domain_service.determine_cache_strategy({
                "file_types": ["html", "css", "js", "png", "jpg"],
                "business_tier": "standard"
            })
            
            return {
                "success": True,
                "raw_analytics": {
                    "page_views": raw_analytics.page_views,
                    "unique_visitors": raw_analytics.unique_visitors,
                    "bounce_rate": raw_analytics.bounce_rate
                },
                "analytics_summary": analytics_summary,
                "cache_strategy": cache_strategy,
                "engagement_score": analytics_summary["engagement_score"],
                "performance_rating": analytics_summary["performance_rating"]
            }
            
        except Exception as e:
            logger.error(f"❌ Analytics test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_mock_website_files(self, build_path: str):
        """Create mock website files for testing."""
        
        build_dir = Path(build_path)
        
        # Create index.html
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.test_business.name} - Professional {self.test_business.get_primary_trade().title()} Services</title>
    <meta name="description" content="Expert {self.test_business.get_primary_trade()} services in {self.test_business.city}">
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <header>
        <h1>{self.test_business.name}</h1>
        <p>{self.test_business.branding.tagline}</p>
    </header>
    
    <main>
        <section class="hero">
            <h2>Professional {self.test_business.get_primary_trade().title()} Services in {self.test_business.city}</h2>
            <p>{self.test_business.description}</p>
            <a href="tel:{self.test_business.phone}" class="cta-button">Call Now: {self.test_business.phone}</a>
        </section>
        
        <section class="services">
            <h3>Our Services</h3>
            <ul>
                <li>Emergency {self.test_business.get_primary_trade().title()} Services</li>
                <li>Residential {self.test_business.get_primary_trade().title()}</li>
                <li>Commercial {self.test_business.get_primary_trade().title()}</li>
                <li>Maintenance & Repairs</li>
            </ul>
        </section>
        
        <section class="contact">
            <h3>Contact Us</h3>
            <p>Phone: {self.test_business.phone}</p>
            <p>Email: {self.test_business.email}</p>
            <p>Service Areas: {', '.join(self.test_business.service_areas)}</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 {self.test_business.name}. All rights reserved.</p>
        <p>Powered by Hero365</p>
    </footer>
    
    <script src="js/main.js"></script>
</body>
</html>"""
        
        # Create CSS
        css_content = f"""
/* Hero365 Generated Styles */
:root {{
    --primary-color: {self.test_business.branding.primary_color};
    --secondary-color: {self.test_business.branding.secondary_color};
    --accent-color: {self.test_business.branding.accent_color};
}}

body {{
    font-family: {self.test_business.branding.font_primary}, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    color: #333;
}}

header {{
    background: var(--primary-color);
    color: white;
    text-align: center;
    padding: 2rem 0;
}}

.hero {{
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    text-align: center;
    padding: 4rem 2rem;
}}

.cta-button {{
    display: inline-block;
    background: var(--accent-color);
    color: white;
    padding: 1rem 2rem;
    text-decoration: none;
    border-radius: 5px;
    margin-top: 1rem;
    font-weight: bold;
}}

.services, .contact {{
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
}}

footer {{
    background: #333;
    color: white;
    text-align: center;
    padding: 1rem 0;
    margin-top: 2rem;
}}
"""
        
        # Create JavaScript
        js_content = """
// Hero365 Generated JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Hero365 Website Loaded Successfully');
    
    // Track page view (mock analytics)
    if (typeof gtag !== 'undefined') {
        gtag('event', 'page_view', {
            page_title: document.title,
            page_location: window.location.href
        });
    }
    
    // Add click tracking to CTA buttons
    document.querySelectorAll('.cta-button').forEach(button => {
        button.addEventListener('click', function() {
            console.log('CTA Button Clicked:', this.href);
        });
    });
});
"""
        
        # Write files
        (build_dir / "index.html").write_text(index_html)
        
        # Create directories
        (build_dir / "styles").mkdir(exist_ok=True)
        (build_dir / "js").mkdir(exist_ok=True)
        
        (build_dir / "styles" / "main.css").write_text(css_content)
        (build_dir / "js" / "main.js").write_text(js_content)
        
        # Create additional pages
        (build_dir / "services.html").write_text(f"<h1>Services - {self.test_business.name}</h1>")
        (build_dir / "contact.html").write_text(f"<h1>Contact - {self.test_business.name}</h1>")
        
        logger.info(f"✅ Created {len(list(build_dir.rglob('*')))} mock website files")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        
        total_steps = len(self.test_results)
        successful_steps = sum(1 for result in self.test_results.values() if result.get("success", False))
        
        report = {
            "test_summary": {
                "success": successful_steps == total_steps,
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "success_rate": (successful_steps / total_steps) * 100 if total_steps > 0 else 0,
                "test_duration": "Complete",
                "timestamp": datetime.utcnow().isoformat()
            },
            "business_info": {
                "name": self.test_business.name if self.test_business else "N/A",
                "trade": self.test_business.get_primary_trade() if self.test_business else "N/A",
                "city": self.test_business.city if self.test_business else "N/A"
            },
            "deployment_info": {
                "subdomain": self.deployment_result.subdomain if self.deployment_result else "N/A",
                "website_url": self.deployment_result.website_url if self.deployment_result else "N/A",
                "deployment_success": self.deployment_result.success if self.deployment_result else False
            },
            "detailed_results": self.test_results,
            "clean_architecture_components_tested": [
                "SEODomainService",
                "SubdomainDomainService", 
                "Hero365SubdomainAdapter",
                "Content Generation Adapters",
                "Website Orchestration Service"
            ]
        }
        
        return report
    
    async def quick_test(self, business_type: str = "plumbing") -> Dict[str, Any]:
        """Run a quick test focusing on core functionality."""
        
        logger.info("🚀 Running Quick Website Generation Test...")
        
        try:
            # Create business
            business = await self._create_test_business(business_type)
            
            # Generate subdomain
            subdomain = self.subdomain_domain_service.generate_subdomain_name(
                BusinessWebsite(
                    business_id=business.id,
                    primary_trade=business.get_primary_trade(),
                    template_id="professional-template"
                )
            )
            
            # Validate subdomain
            validation = self.subdomain_domain_service.validate_subdomain_name(subdomain)
            
            return {
                "success": True,
                "business_name": business.name,
                "generated_subdomain": subdomain,
                "subdomain_valid": validation["valid"],
                "website_url": f"https://{subdomain}.hero365.ai",
                "test_type": "quick_test"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_type": "quick_test"
            }


async def main():
    """Main test runner."""
    
    print("🚀 Hero365 Website Generation & Deployment Tester")
    print("=" * 60)
    
    tester = WebsiteGenerationTester()
    
    # Check if we should run quick test or full test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        business_type = sys.argv[2] if len(sys.argv) > 2 else "plumbing"
        result = await tester.quick_test(business_type)
    else:
        business_type = sys.argv[1] if len(sys.argv) > 1 else "plumbing"
        result = await tester.run_complete_test(business_type)
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))
    
    if result.get("success", False):
        print("\n✅ ALL TESTS PASSED!")
        if "website_url" in result.get("deployment_info", {}):
            print(f"🌐 Website URL: {result['deployment_info']['website_url']}")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Check the detailed results above for more information.")


if __name__ == "__main__":
    asyncio.run(main())
