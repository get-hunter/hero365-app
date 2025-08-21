"""
Website Orchestration Service

Application service that orchestrates website building by coordinating
between domain services and external service adapters.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import BusinessWebsite, WebsiteTemplate, WebsiteStatus
from ...domain.services.website_builder_domain_service import WebsiteBuilderDomainService
from ...domain.services.seo_domain_service import SEODomainService
from ...domain.services.deployment_domain_service import DeploymentDomainService
from ...domain.services.domain_registration_domain_service import DomainRegistrationDomainService

# Ports (interfaces) for external services
from ...application.ports.content_generation_port import ContentGenerationPort
from ...application.ports.deployment_port import DeploymentPort
from ...application.ports.domain_registration_port import DomainRegistrationPort
from ...application.ports.seo_research_port import SEOResearchPort
from ...application.ports.hosting_port import HostingPort

# Factory for creating content generation adapters
from ...infrastructure.adapters.content_generation_factory import create_content_adapter

# Website builder service for static site generation
from ..services.website_builder_service import WebsiteBuilderService

logger = logging.getLogger(__name__)


class WebsiteOrchestrationService:
    """
    Application service that orchestrates website building.
    
    This service coordinates between:
    - Domain services (business logic)
    - External service adapters (infrastructure)
    - Use cases (application logic)
    """
    
    def __init__(
        self,
        hosting_service: HostingPort,
        domain_registry: Optional[DomainRegistrationPort] = None,
        seo_research: Optional[SEOResearchPort] = None,
        content_provider: Optional[str] = None
    ):
        # Domain services (business logic)
        self.website_domain_service = WebsiteBuilderDomainService()
        self.seo_domain_service = SEODomainService()
        self.deployment_domain_service = DeploymentDomainService()
        self.domain_registration_domain_service = DomainRegistrationDomainService()
        
        # Infrastructure services (via ports)
        self.content_generator = create_content_adapter(provider=content_provider)
        self.current_content_provider = content_provider
        self.hosting_service = hosting_service
        self.domain_registry = domain_registry
        self.seo_research = seo_research
        
        # Website builder service for static site generation
        self.website_builder = WebsiteBuilderService()
    
    async def build_website(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate the complete website building process.
        
        This method coordinates all the steps without containing business logic.
        """
        
        build_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting website build {build_id} for business {business.id}")
        
        try:
            # Step 1: Domain validation (business logic)
            validation = self.website_domain_service.validate_website_creation(
                business, template, options.get("subdomain") if options else None
            )
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "build_id": build_id,
                    "errors": validation["errors"]
                }
            
            # Step 2: Create website entity
            website = BusinessWebsite(
                id=uuid.uuid4(),
                business_id=business.id,
                template_id=template.id,
                subdomain=options.get("subdomain") if options else None,
                status=WebsiteStatus.BUILDING,
                primary_trade=business.get_primary_trade(),
                seo_keywords=self.seo_domain_service.generate_local_keywords(business)
            )
            
            # Step 3: Determine required pages (business logic)
            required_pages = self.website_domain_service.determine_required_pages(business, template)
            
            # Step 4: Generate content (external service)
            logger.info("Generating website content...")
            content_result = await self.content_generator.generate_website_content(
                business=business,
                branding=branding,
                template=template,
                required_pages=required_pages
            )
            
            if not content_result.success:
                return {
                    "success": False,
                    "build_id": build_id,
                    "error": f"Content generation failed: {content_result.error_message}"
                }
            
            # Step 5: Validate generated content (business logic)
            content_validation = self.website_domain_service.validate_content_requirements(
                business, content_result.content_data
            )
            
            if not content_validation["valid"]:
                logger.warning(f"Content validation issues: {content_validation['missing_content']}")
            
            # Step 6: Determine deployment strategy (business logic)
            deployment_strategy = self.deployment_domain_service.determine_deployment_strategy(
                website, business, options.get("environment", "production") if options else "production"
            )
            
            # Step 7: Build static website files (external service)
            logger.info("Building static website files...")
            build_result = await self.website_builder.build_website(
                website=website,
                business=business,
                branding=branding,
                template=template
            )
            
            if not build_result.success:
                return {
                    "success": False,
                    "build_id": build_id,
                    "error": f"Website build failed: {build_result.error_message}"
                }
            
            # Update website status to BUILT
            website.status = WebsiteStatus.BUILT
            
            # Step 8: Validate deployment readiness (business logic)
            readiness_validation = self.deployment_domain_service.validate_deployment_readiness(
                website, business, options or {}
            )
            
            if not readiness_validation.is_valid:
                return {
                    "success": False,
                    "build_id": build_id,
                    "error": f"Deployment validation failed: {'; '.join(readiness_validation.issues)}"
                }
            
            # Step 9: Deploy website (external service)
            logger.info("Deploying website...")
            
            # Use the Hero365 subdomain adapter for deployment
            from ...infrastructure.adapters.hero365_subdomain_adapter import Hero365SubdomainAdapter
            subdomain_adapter = Hero365SubdomainAdapter()
            
            deployment_result = await subdomain_adapter.deploy_to_subdomain(
                website=website,
                build_path=build_result.build_path
            )
            
            if not deployment_result.success:
                return {
                    "success": False,
                    "build_id": build_id,
                    "error": f"Deployment failed: {getattr(deployment_result, 'error', 'Unknown deployment error')}"
                }
            
            # Step 10: Calculate final metrics
            build_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Step 11: Update website status
            website.status = WebsiteStatus.DEPLOYED
            website.website_url = deployment_result.website_url
            website.last_build_at = datetime.utcnow()
            website.last_deploy_at = datetime.utcnow()
            
            logger.info(f"Website build {build_id} completed successfully in {build_time:.1f}s")
            
            return {
                "success": True,
                "build_id": build_id,
                "website": website,
                "website_url": deployment_result.website_url,
                "build_path": build_result.build_path,
                "build_time_seconds": build_time,
                "pages_generated": len(required_pages),
                "lighthouse_score": build_result.lighthouse_score,
                "readiness_score": readiness_validation.readiness_score,
                "deployment_strategy": deployment_strategy,
                "content_warnings": content_validation.get("quality_issues", [])
            }
            
        except Exception as e:
            logger.error(f"Website build {build_id} failed: {str(e)}")
            return {
                "success": False,
                "build_id": build_id,
                "error": str(e),
                "build_time_seconds": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def register_domain_and_deploy(
        self,
        business: Business,
        domain_name: str,
        website: BusinessWebsite
    ) -> Dict[str, Any]:
        """
        Register a custom domain and deploy website to it.
        
        Orchestrates domain registration and deployment.
        """
        
        if not self.domain_registration:
            return {
                "success": False,
                "error": "Domain registration service not configured"
            }
        
        try:
            # Step 1: Register domain (external service)
            logger.info(f"Registering domain: {domain_name}")
            registration_result = await self.domain_registration.register_domain(
                domain_name=domain_name,
                business=business,
                duration_years=1
            )
            
            if not registration_result.success:
                return {
                    "success": False,
                    "error": f"Domain registration failed: {registration_result.error_message}"
                }
            
            # Step 2: Deploy to custom domain (external service)
            logger.info(f"Deploying to custom domain: {domain_name}")
            deployment_result = await self.deployment_service.deploy_to_custom_domain(
                website=website,
                domain=domain_name,
                ssl_enabled=True
            )
            
            if not deployment_result.success:
                return {
                    "success": False,
                    "error": f"Custom domain deployment failed: {deployment_result.error_message}"
                }
            
            # Step 3: Update website record
            website.domain = domain_name
            website.website_url = f"https://{domain_name}"
            
            return {
                "success": True,
                "domain": domain_name,
                "website_url": f"https://{domain_name}",
                "registration_details": registration_result.registration_info,
                "deployment_details": deployment_result.deployment_info
            }
            
        except Exception as e:
            logger.error(f"Domain registration and deployment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_website_content(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        content_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update website content and redeploy.
        
        Orchestrates content updates and redeployment.
        """
        
        try:
            # Step 1: Validate content updates (business logic)
            validation = self.domain_service.validate_content_requirements(
                business, content_updates
            )
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "errors": validation["missing_content"]
                }
            
            # Step 2: Regenerate affected content (external service)
            logger.info("Regenerating website content...")
            content_result = await self.content_generator.update_website_content(
                website=website,
                business=business,
                branding=branding,
                content_updates=content_updates
            )
            
            if not content_result.success:
                return {
                    "success": False,
                    "error": f"Content update failed: {content_result.error_message}"
                }
            
            # Step 3: Rebuild and redeploy (external service)
            logger.info("Rebuilding and redeploying website...")
            deployment_result = await self.deployment_service.update_deployment(
                website=website,
                updated_content=content_result.content_data
            )
            
            if not deployment_result.success:
                return {
                    "success": False,
                    "error": f"Redeployment failed: {deployment_result.error_message}"
                }
            
            # Step 4: Update website record
            website.last_build_at = datetime.utcnow()
            website.last_deploy_at = datetime.utcnow()
            
            return {
                "success": True,
                "website_url": website.website_url,
                "updated_at": datetime.utcnow(),
                "content_warnings": validation.get("quality_issues", [])
            }
            
        except Exception as e:
            logger.error(f"Website content update failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def switch_content_provider(self, provider: str):
        """
        Switch to a different content generation provider.
        
        Args:
            provider: New provider name ("openai", "claude", "gemini")
        """
        
        logger.info(f"Switching content provider from {self.current_content_provider} to {provider}")
        
        try:
            self.content_generator = create_content_adapter(provider=provider)
            self.current_content_provider = provider
            logger.info(f"Successfully switched to {provider} content provider")
        except Exception as e:
            logger.error(f"Failed to switch to {provider}: {str(e)}")
            raise ValueError(f"Cannot switch to {provider}: {str(e)}")
    
    def get_current_provider(self) -> str:
        """Get the currently active content generation provider."""
        return self.current_content_provider or "default"
    
    def get_available_providers(self) -> Dict[str, Dict[str, any]]:
        """Get information about available content generation providers."""
        from ...infrastructure.adapters.content_generation_factory import get_provider_info
        return get_provider_info()
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _convert_content_to_files(
        self,
        content_data: Dict[str, Any],
        template: WebsiteTemplate
    ) -> List[Any]:
        """Convert generated content to file objects for deployment."""
        
        from ...application.ports.hosting_port import FileUploadInfo
        
        files = []
        
        # Generate HTML files for each page
        for page_type, page_content in content_data.items():
            if page_type in ["business_info", "branding", "generated_by"]:
                continue  # Skip metadata
            
            # Generate HTML content (simplified - would use actual template rendering)
            html_content = self._render_page_html(page_content, page_type, template)
            
            files.append(FileUploadInfo(
                path=f"{page_type}.html" if page_type != "home" else "index.html",
                content=html_content,
                content_type="text/html",
                cache_control="max-age=3600"
            ))
        
        # Add static assets (CSS, JS, images)
        files.extend(self._get_static_assets(template))
        
        return files
    
    def _create_deployment_config(
        self,
        website: BusinessWebsite,
        strategy: Any,  # DeploymentStrategy
        options: Optional[Dict[str, Any]]
    ) -> Any:  # DeploymentConfiguration
        """Create deployment configuration from strategy and options."""
        
        from ...application.ports.hosting_port import DeploymentConfiguration
        
        return DeploymentConfiguration(
            site_name=f"hero365-{website.id}",
            environment=options.get("environment", "production") if options else "production",
            enable_compression=strategy.compression_enabled,
            enable_caching=True,
            cache_ttl_seconds=86400,  # 24 hours default
            enable_https=strategy.ssl_required,
            enable_security_headers=strategy.security_level != "BASIC",
            enable_cdn=strategy.cdn_required,
            enable_http2=True,
            enable_ipv6=True,
            custom_headers=options.get("custom_headers", {}) if options else {},
            error_pages={"404": "/404.html", "500": "/500.html"}
        )
    
    def _render_page_html(
        self,
        page_content: Dict[str, Any],
        page_type: str,
        template: WebsiteTemplate
    ) -> str:
        """Render page content to HTML (simplified implementation)."""
        
        # This is a simplified version - in reality, you'd use a proper template engine
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_content.get('title', f'{page_type.title()} Page')}</title>
    <meta name="description" content="{page_content.get('description', '')}">
    <link rel="stylesheet" href="/css/main.css">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/services.html">Services</a>
            <a href="/contact.html">Contact</a>
        </nav>
    </header>
    
    <main>
        <h1>{page_content.get('h1', page_type.title())}</h1>
        
        {self._render_content_sections(page_content.get('sections', []))}
    </main>
    
    <footer>
        <p>&copy; 2024 Hero365. All rights reserved.</p>
    </footer>
    
    <script src="/js/main.js"></script>
</body>
</html>"""
        
        return html_template
    
    def _render_content_sections(self, sections: List[Dict[str, Any]]) -> str:
        """Render content sections to HTML."""
        
        html_parts = []
        
        for section in sections:
            if section.get("type") == "heading":
                html_parts.append(f"<h2>{section.get('content', '')}</h2>")
                
                # Add section text
                if section.get("text"):
                    for text_line in section["text"]:
                        html_parts.append(f"<p>{text_line}</p>")
            else:
                # Handle other section types
                html_parts.append(f"<div>{section}</div>")
        
        return "\n".join(html_parts)
    
    def _get_static_assets(self, template: WebsiteTemplate) -> List[Any]:
        """Get static assets (CSS, JS, images) for the template."""
        
        from ...application.ports.hosting_port import FileUploadInfo
        
        assets = []
        
        # Basic CSS
        css_content = """
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        header { background: #333; color: white; padding: 1rem; }
        nav a { color: white; text-decoration: none; margin-right: 1rem; }
        main { padding: 2rem; }
        footer { background: #f5f5f5; padding: 1rem; text-align: center; }
        """
        
        assets.append(FileUploadInfo(
            path="css/main.css",
            content=css_content,
            content_type="text/css",
            cache_control="max-age=604800"  # 7 days
        ))
        
        # Basic JavaScript
        js_content = """
        console.log('Hero365 website loaded');
        
        // Basic analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('config', 'GA_MEASUREMENT_ID');
        }
        """
        
        assets.append(FileUploadInfo(
            path="js/main.js",
            content=js_content,
            content_type="application/javascript",
            cache_control="max-age=604800"  # 7 days
        ))
        
        return assets
