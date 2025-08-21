"""
Deployment Port

Interface/contract for website deployment services.
Defines what the application layer expects from deployment providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import BusinessWebsite, WebsiteTemplate


class BuildResult(BaseModel):
    """Result of static site build operation."""
    
    success: bool
    build_path: str
    build_time_seconds: float
    pages_built: int
    total_size_mb: float
    error_message: Optional[str] = None
    build_logs: Optional[str] = None


class DeploymentResult(BaseModel):
    """Result of website deployment operation."""
    
    success: bool
    website_url: str
    deployment_time_seconds: float
    files_uploaded: int
    performance_score: Optional[int] = None
    deployment_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class DeploymentPort(ABC):
    """
    Port (interface) for website deployment services.
    
    This defines the contract that any deployment implementation
    must follow (AWS, Vercel, Netlify, etc.).
    """
    
    @abstractmethod
    async def build_static_site(
        self,
        website: BusinessWebsite,
        content_data: Dict[str, Any],
        template: WebsiteTemplate,
        branding: BusinessBranding
    ) -> BuildResult:
        """
        Build static website from content and template.
        
        Args:
            website: Website entity
            content_data: Generated content for all pages
            template: Website template structure
            branding: Business branding settings
            
        Returns:
            BuildResult with build information
        """
        pass
    
    @abstractmethod
    async def deploy_website(
        self,
        website: BusinessWebsite,
        build_path: str,
        deployment_options: Dict[str, Any] = None
    ) -> DeploymentResult:
        """
        Deploy built website to hosting platform.
        
        Args:
            website: Website entity
            build_path: Path to built static files
            deployment_options: Platform-specific options
            
        Returns:
            DeploymentResult with deployment information
        """
        pass
    
    @abstractmethod
    async def deploy_to_custom_domain(
        self,
        website: BusinessWebsite,
        domain: str,
        ssl_enabled: bool = True
    ) -> DeploymentResult:
        """
        Deploy website to a custom domain.
        
        Args:
            website: Website entity
            domain: Custom domain name
            ssl_enabled: Whether to enable SSL
            
        Returns:
            DeploymentResult with custom domain deployment info
        """
        pass
    
    @abstractmethod
    async def update_deployment(
        self,
        website: BusinessWebsite,
        updated_content: Dict[str, Any]
    ) -> DeploymentResult:
        """
        Update existing deployment with new content.
        
        Args:
            website: Website entity
            updated_content: New content to deploy
            
        Returns:
            DeploymentResult with update information
        """
        pass
    
    @abstractmethod
    async def delete_deployment(
        self,
        website: BusinessWebsite
    ) -> bool:
        """
        Delete website deployment and clean up resources.
        
        Args:
            website: Website entity to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_deployment_status(
        self,
        website: BusinessWebsite
    ) -> Dict[str, Any]:
        """
        Get current deployment status and metrics.
        
        Args:
            website: Website entity
            
        Returns:
            Dictionary with deployment status information
        """
        pass
    
    @abstractmethod
    async def invalidate_cache(
        self,
        website: BusinessWebsite,
        paths: Optional[List[str]] = None
    ) -> bool:
        """
        Invalidate CDN cache for website.
        
        Args:
            website: Website entity
            paths: Specific paths to invalidate (None = all)
            
        Returns:
            True if invalidation successful, False otherwise
        """
        pass
