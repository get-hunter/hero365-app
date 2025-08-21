"""
Subdomain Hosting Port

Abstract interface for subdomain hosting operations.
Defines the contract for Hero365 subdomain deployment services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...domain.entities.website import BusinessWebsite


class SubdomainInfo(BaseModel):
    """Information about a deployed subdomain."""
    
    subdomain: str
    full_domain: str
    website_url: str
    file_count: int
    total_size_mb: float
    last_modified: Optional[str] = None
    status: str = "active"
    error: Optional[str] = None


class DeploymentResult(BaseModel):
    """Result from subdomain deployment operations."""
    
    success: bool
    subdomain: Optional[str] = None
    full_domain: Optional[str] = None
    website_url: Optional[str] = None
    upload_result: Optional[Dict[str, Any]] = None
    dns_configured: bool = False
    cache_invalidated: bool = False
    deployment_verified: bool = False
    deployed_at: Optional[str] = None
    error: Optional[str] = None


class SubdomainAnalytics(BaseModel):
    """Analytics data for a subdomain."""
    
    subdomain: str
    period: str
    page_views: int = 0
    unique_visitors: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: int = 0
    top_pages: List[Dict[str, Any]] = []
    traffic_sources: Dict[str, int] = {}
    error: Optional[str] = None


class SubdomainHostingPort(ABC):
    """
    Abstract interface for subdomain hosting operations.
    
    This port defines the contract for Hero365 subdomain deployment,
    allowing different hosting implementations to be swapped out.
    """
    
    @abstractmethod
    async def deploy_to_subdomain(
        self,
        website: BusinessWebsite,
        build_path: str,
        subdomain: Optional[str] = None
    ) -> DeploymentResult:
        """
        Deploy website to a hero365.ai subdomain.
        
        Args:
            website: The website to deploy
            build_path: Path to the built website files
            subdomain: Optional specific subdomain name
            
        Returns:
            Deployment operation result
        """
        pass
    
    @abstractmethod
    async def list_subdomains(self) -> Dict[str, Any]:
        """
        List all active subdomains.
        
        Returns:
            Dictionary containing subdomain list and metadata
        """
        pass
    
    @abstractmethod
    async def delete_subdomain(self, subdomain: str) -> Dict[str, Any]:
        """
        Delete a subdomain and all its files.
        
        Args:
            subdomain: The subdomain to delete
            
        Returns:
            Deletion operation result
        """
        pass
    
    @abstractmethod
    async def update_subdomain(
        self,
        subdomain: str,
        build_path: str
    ) -> Dict[str, Any]:
        """
        Update an existing subdomain with new content.
        
        Args:
            subdomain: The subdomain to update
            build_path: Path to the new website files
            
        Returns:
            Update operation result
        """
        pass
    
    @abstractmethod
    async def get_subdomain_info(self, subdomain: str) -> SubdomainInfo:
        """
        Get information about a specific subdomain.
        
        Args:
            subdomain: The subdomain to get info for
            
        Returns:
            Subdomain information
        """
        pass
    
    @abstractmethod
    async def get_subdomain_analytics(self, subdomain: str) -> SubdomainAnalytics:
        """
        Get analytics data for a subdomain.
        
        Args:
            subdomain: The subdomain to get analytics for
            
        Returns:
            Analytics data for the subdomain
        """
        pass
    
    @abstractmethod
    async def verify_subdomain_deployment(self, full_domain: str) -> Dict[str, Any]:
        """
        Verify that a subdomain is accessible and working.
        
        Args:
            full_domain: The full domain to verify (e.g., "test.hero365.ai")
            
        Returns:
            Verification result with status and performance metrics
        """
        pass
    
    @abstractmethod
    async def upload_files_to_subdomain(
        self,
        build_path: str,
        subdomain: str
    ) -> Dict[str, Any]:
        """
        Upload website files to subdomain storage.
        
        Args:
            build_path: Path to the website files
            subdomain: Target subdomain
            
        Returns:
            Upload operation result
        """
        pass
    
    @abstractmethod
    async def configure_subdomain_dns(self, subdomain: str) -> Dict[str, Any]:
        """
        Configure DNS records for a subdomain.
        
        Args:
            subdomain: The subdomain to configure DNS for
            
        Returns:
            DNS configuration result
        """
        pass
    
    @abstractmethod
    async def invalidate_subdomain_cache(self, subdomain: str) -> Dict[str, Any]:
        """
        Invalidate CDN cache for a subdomain.
        
        Args:
            subdomain: The subdomain to invalidate cache for
            
        Returns:
            Cache invalidation result
        """
        pass
