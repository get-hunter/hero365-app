"""
Domain Registration Port

Interface/contract for domain registration services.
Defines what the application layer expects from domain providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ...domain.entities.business import Business


@dataclass
class DomainSuggestion:
    """Domain name suggestion with SEO scoring."""
    
    domain: str
    available: bool
    price_usd: float
    seo_score: int  # 0-100
    trade_relevance: float  # 0-1
    tld: str
    recommended_for: str
    registration_years: int = 1


@dataclass
class DomainRegistrationResult:
    """Result of domain registration operation."""
    
    success: bool
    domain: str
    registration_info: Dict[str, Any]
    expires_at: datetime
    auto_renew_enabled: bool
    dns_configured: bool
    error_message: str = None


class DomainRegistrationPort(ABC):
    """
    Port (interface) for domain registration services.
    
    This defines the contract that any domain registration implementation
    must follow (Cloudflare, Namecheap, GoDaddy, etc.).
    """
    
    @abstractmethod
    async def search_domains(
        self,
        business: Business,
        base_name: str,
        max_suggestions: int = 20
    ) -> List[DomainSuggestion]:
        """
        Search for available domains with trade-based SEO scoring.
        
        Args:
            business: Business entity for context
            base_name: Base name for domain suggestions
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of domain suggestions with SEO scores
        """
        pass
    
    @abstractmethod
    async def check_domain_availability(
        self,
        domain: str
    ) -> Dict[str, Any]:
        """
        Check if a specific domain is available.
        
        Args:
            domain: Domain name to check
            
        Returns:
            Dictionary with availability and pricing info
        """
        pass
    
    @abstractmethod
    async def register_domain(
        self,
        domain_name: str,
        business: Business,
        duration_years: int = 1,
        auto_renew: bool = True
    ) -> DomainRegistrationResult:
        """
        Register a domain name.
        
        Args:
            domain_name: Domain to register
            business: Business entity for contact info
            duration_years: Registration period
            auto_renew: Enable auto-renewal
            
        Returns:
            DomainRegistrationResult with registration details
        """
        pass
    
    @abstractmethod
    async def configure_dns(
        self,
        domain: str,
        target_url: str,
        dns_records: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Configure DNS records for a domain.
        
        Args:
            domain: Domain name
            target_url: Target URL for main record
            dns_records: Additional DNS records
            
        Returns:
            True if DNS configuration successful
        """
        pass
    
    @abstractmethod
    async def get_domain_info(
        self,
        domain: str
    ) -> Dict[str, Any]:
        """
        Get information about a registered domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary with domain information
        """
        pass
    
    @abstractmethod
    async def renew_domain(
        self,
        domain: str,
        years: int = 1
    ) -> bool:
        """
        Renew a domain registration.
        
        Args:
            domain: Domain name to renew
            years: Number of years to renew
            
        Returns:
            True if renewal successful
        """
        pass
    
    @abstractmethod
    async def transfer_domain(
        self,
        domain: str,
        auth_code: str
    ) -> bool:
        """
        Transfer a domain to this registrar.
        
        Args:
            domain: Domain name to transfer
            auth_code: Authorization code from current registrar
            
        Returns:
            True if transfer initiated successfully
        """
        pass
    
    @abstractmethod
    async def calculate_seo_score(
        self,
        domain: str,
        business: Business
    ) -> int:
        """
        Calculate SEO score for a domain based on business context.
        
        Args:
            domain: Domain name to score
            business: Business entity for context
            
        Returns:
            SEO score (0-100)
        """
        pass
