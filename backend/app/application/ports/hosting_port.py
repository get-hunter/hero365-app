"""
Hosting Port

Interface for website hosting and deployment infrastructure services.
Defines contracts for cloud hosting providers and CDN services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from ...domain.entities.website import BusinessWebsite


@dataclass
class DeploymentConfiguration:
    """Configuration for website deployment."""
    
    # Basic settings
    site_name: str
    environment: str = "production"  # production, staging, development
    
    # Performance settings
    enable_compression: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 86400  # 24 hours
    
    # Security settings
    enable_https: bool = True
    enable_security_headers: bool = True
    ssl_redirect: bool = True
    
    # CDN settings
    enable_cdn: bool = True
    cdn_regions: List[str] = None  # Specific regions or None for global
    
    # Custom settings
    custom_headers: Dict[str, str] = None
    error_pages: Dict[str, str] = None  # HTTP code -> page path
    redirects: List[Dict[str, str]] = None  # List of redirect rules


@dataclass
class FileUploadInfo:
    """Information about a file to upload."""
    
    path: str  # Relative path in the site
    content: Union[bytes, str]
    content_type: str
    cache_control: Optional[str] = None
    encoding: Optional[str] = None


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""
    
    success: bool
    deployment_id: str
    website_url: str
    
    # Infrastructure details
    hosting_provider: str
    region: str
    cdn_enabled: bool
    ssl_enabled: bool
    
    # Performance metrics
    deployment_time_seconds: float
    files_uploaded: int
    total_size_bytes: int
    
    # URLs and endpoints
    primary_url: str
    cdn_url: Optional[str] = None
    admin_url: Optional[str] = None
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = None


@dataclass
class SSLCertificateInfo:
    """SSL certificate information."""
    
    domain: str
    status: str  # PENDING, ACTIVE, EXPIRED, ERROR
    issuer: str
    expires_at: datetime
    auto_renew: bool = True
    san_domains: List[str] = None  # Subject Alternative Names


@dataclass
class CDNConfiguration:
    """CDN configuration settings."""
    
    enabled: bool = True
    regions: List[str] = None  # Specific regions or None for global
    cache_behaviors: List[Dict[str, Any]] = None
    origin_settings: Dict[str, Any] = None
    security_settings: Dict[str, Any] = None


@dataclass
class PerformanceMetrics:
    """Website performance metrics."""
    
    domain: str
    measured_at: datetime
    
    # Core Web Vitals
    largest_contentful_paint: Optional[float] = None  # LCP in seconds
    first_input_delay: Optional[float] = None  # FID in milliseconds
    cumulative_layout_shift: Optional[float] = None  # CLS score
    
    # Other metrics
    time_to_first_byte: Optional[float] = None  # TTFB in milliseconds
    first_contentful_paint: Optional[float] = None  # FCP in seconds
    speed_index: Optional[float] = None
    
    # Lighthouse scores (0-100)
    performance_score: Optional[int] = None
    accessibility_score: Optional[int] = None
    best_practices_score: Optional[int] = None
    seo_score: Optional[int] = None


class HostingPort(ABC):
    """
    Port (interface) for hosting and deployment services.
    
    This defines the contract for cloud hosting providers
    without containing any business logic.
    """
    
    @abstractmethod
    async def deploy_static_site(
        self,
        files: List[FileUploadInfo],
        config: DeploymentConfiguration
    ) -> DeploymentResult:
        """
        Deploy a static website.
        
        Args:
            files: List of files to upload
            config: Deployment configuration
            
        Returns:
            Deployment result with URLs and metrics
        """
        pass
    
    @abstractmethod
    async def update_deployment(
        self,
        deployment_id: str,
        files: List[FileUploadInfo],
        config: Optional[DeploymentConfiguration] = None
    ) -> DeploymentResult:
        """
        Update an existing deployment.
        
        Args:
            deployment_id: ID of existing deployment
            files: Updated files to upload
            config: Optional updated configuration
            
        Returns:
            Updated deployment result
        """
        pass
    
    @abstractmethod
    async def delete_deployment(
        self,
        deployment_id: str
    ) -> Dict[str, Any]:
        """
        Delete a deployment and all associated resources.
        
        Args:
            deployment_id: ID of deployment to delete
            
        Returns:
            Deletion result
        """
        pass
    
    @abstractmethod
    async def configure_custom_domain(
        self,
        deployment_id: str,
        domain: str,
        ssl_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Configure a custom domain for a deployment.
        
        Args:
            deployment_id: ID of deployment
            domain: Custom domain name
            ssl_enabled: Whether to enable SSL
            
        Returns:
            Domain configuration result with DNS instructions
        """
        pass
    
    @abstractmethod
    async def setup_ssl_certificate(
        self,
        domain: str,
        auto_renew: bool = True
    ) -> SSLCertificateInfo:
        """
        Set up SSL certificate for a domain.
        
        Args:
            domain: Domain name for certificate
            auto_renew: Enable automatic renewal
            
        Returns:
            SSL certificate information
        """
        pass
    
    @abstractmethod
    async def configure_cdn(
        self,
        deployment_id: str,
        cdn_config: CDNConfiguration
    ) -> Dict[str, Any]:
        """
        Configure CDN for a deployment.
        
        Args:
            deployment_id: ID of deployment
            cdn_config: CDN configuration settings
            
        Returns:
            CDN configuration result
        """
        pass
    
    @abstractmethod
    async def invalidate_cache(
        self,
        deployment_id: str,
        paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Invalidate CDN cache for specific paths or entire site.
        
        Args:
            deployment_id: ID of deployment
            paths: Specific paths to invalidate, or None for all
            
        Returns:
            Cache invalidation result
        """
        pass
    
    @abstractmethod
    async def get_deployment_status(
        self,
        deployment_id: str
    ) -> Dict[str, Any]:
        """
        Get current status of a deployment.
        
        Args:
            deployment_id: ID of deployment
            
        Returns:
            Deployment status information
        """
        pass
    
    @abstractmethod
    async def get_deployment_logs(
        self,
        deployment_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get deployment logs.
        
        Args:
            deployment_id: ID of deployment
            limit: Maximum number of log entries
            
        Returns:
            List of log entries
        """
        pass
    
    @abstractmethod
    async def measure_performance(
        self,
        url: str,
        device: str = "desktop"
    ) -> PerformanceMetrics:
        """
        Measure website performance metrics.
        
        Args:
            url: URL to measure
            device: Device type (desktop, mobile)
            
        Returns:
            Performance metrics including Core Web Vitals
        """
        pass
    
    @abstractmethod
    async def configure_redirects(
        self,
        deployment_id: str,
        redirects: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Configure URL redirects.
        
        Args:
            deployment_id: ID of deployment
            redirects: List of redirect rules (from -> to, status)
            
        Returns:
            Redirect configuration result
        """
        pass
    
    @abstractmethod
    async def configure_security_headers(
        self,
        deployment_id: str,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Configure security headers for a deployment.
        
        Args:
            deployment_id: ID of deployment
            headers: Security headers to set
            
        Returns:
            Security configuration result
        """
        pass
    
    @abstractmethod
    async def get_bandwidth_usage(
        self,
        deployment_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get bandwidth usage statistics.
        
        Args:
            deployment_id: ID of deployment
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Bandwidth usage data
        """
        pass
    
    @abstractmethod
    async def get_visitor_analytics(
        self,
        deployment_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get visitor analytics data.
        
        Args:
            deployment_id: ID of deployment
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Visitor analytics data
        """
        pass
    
    @abstractmethod
    async def backup_deployment(
        self,
        deployment_id: str
    ) -> Dict[str, Any]:
        """
        Create a backup of a deployment.
        
        Args:
            deployment_id: ID of deployment to backup
            
        Returns:
            Backup creation result with backup ID
        """
        pass
    
    @abstractmethod
    async def restore_from_backup(
        self,
        deployment_id: str,
        backup_id: str
    ) -> DeploymentResult:
        """
        Restore a deployment from a backup.
        
        Args:
            deployment_id: ID of deployment to restore
            backup_id: ID of backup to restore from
            
        Returns:
            Restoration result
        """
        pass
    
    @abstractmethod
    async def scale_deployment(
        self,
        deployment_id: str,
        scaling_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Scale deployment resources (if applicable).
        
        Args:
            deployment_id: ID of deployment
            scaling_config: Scaling configuration
            
        Returns:
            Scaling operation result
        """
        pass
