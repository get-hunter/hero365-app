"""
Domain Registry Port

Interface for domain registration and management infrastructure services.
Defines contracts for domain registrars and DNS providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass

from ...domain.entities.business import Business


@dataclass
class DomainAvailabilityResult:
    """Domain availability check result."""
    
    domain: str
    available: bool
    premium: bool = False
    price: Optional[Decimal] = None
    renewal_price: Optional[Decimal] = None
    registration_period_years: int = 1
    transfer_lock_days: int = 60
    redemption_period_days: int = 30


@dataclass
class DomainPricingInfo:
    """Domain pricing information."""
    
    domain: str
    tld: str
    registration_price: Decimal
    renewal_price: Decimal
    transfer_price: Decimal
    redemption_price: Optional[Decimal] = None
    currency: str = "USD"
    premium: bool = False
    premium_tier: Optional[str] = None


@dataclass
class ContactInformation:
    """Domain registration contact information."""
    
    first_name: str
    last_name: str
    organization: Optional[str] = None
    email: str
    phone: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "US"


@dataclass
class DomainRegistrationResult:
    """Domain registration operation result."""
    
    success: bool
    domain: str
    registration_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    name_servers: List[str] = None
    auto_renew: bool = True
    privacy_protection: bool = True
    error_message: Optional[str] = None
    transaction_id: Optional[str] = None


@dataclass
class DNSRecord:
    """DNS record data structure."""
    
    name: str
    type: str  # A, AAAA, CNAME, MX, TXT, etc.
    value: str
    ttl: int = 300
    priority: Optional[int] = None  # For MX records


@dataclass
class DNSConfiguration:
    """DNS configuration for a domain."""
    
    domain: str
    records: List[DNSRecord]
    name_servers: List[str]
    dnssec_enabled: bool = False


class DomainRegistryPort(ABC):
    """
    Port (interface) for domain registration services.
    
    This defines the contract for domain registrars and DNS providers
    without containing any business logic.
    """
    
    @abstractmethod
    async def check_domain_availability(
        self,
        domain: str
    ) -> DomainAvailabilityResult:
        """
        Check if a domain is available for registration.
        
        Args:
            domain: Domain name to check
            
        Returns:
            Domain availability result with pricing info
        """
        pass
    
    @abstractmethod
    async def check_multiple_domains(
        self,
        domains: List[str]
    ) -> List[DomainAvailabilityResult]:
        """
        Check availability of multiple domains.
        
        Args:
            domains: List of domain names to check
            
        Returns:
            List of availability results
        """
        pass
    
    @abstractmethod
    async def get_domain_pricing(
        self,
        tld: str
    ) -> DomainPricingInfo:
        """
        Get pricing information for a TLD.
        
        Args:
            tld: Top-level domain (e.g., '.com', '.net')
            
        Returns:
            Pricing information for the TLD
        """
        pass
    
    @abstractmethod
    async def register_domain(
        self,
        domain: str,
        contact_info: ContactInformation,
        registration_years: int = 1,
        auto_renew: bool = True,
        privacy_protection: bool = True,
        name_servers: Optional[List[str]] = None
    ) -> DomainRegistrationResult:
        """
        Register a domain name.
        
        Args:
            domain: Domain name to register
            contact_info: Registration contact information
            registration_years: Number of years to register for
            auto_renew: Enable automatic renewal
            privacy_protection: Enable WHOIS privacy protection
            name_servers: Custom name servers (optional)
            
        Returns:
            Registration result with details
        """
        pass
    
    @abstractmethod
    async def transfer_domain(
        self,
        domain: str,
        auth_code: str,
        contact_info: ContactInformation
    ) -> DomainRegistrationResult:
        """
        Transfer a domain to this registrar.
        
        Args:
            domain: Domain name to transfer
            auth_code: Authorization code from current registrar
            contact_info: New contact information
            
        Returns:
            Transfer result with details
        """
        pass
    
    @abstractmethod
    async def renew_domain(
        self,
        domain: str,
        years: int = 1
    ) -> DomainRegistrationResult:
        """
        Renew a domain registration.
        
        Args:
            domain: Domain name to renew
            years: Number of years to renew for
            
        Returns:
            Renewal result with new expiration date
        """
        pass
    
    @abstractmethod
    async def configure_dns(
        self,
        domain: str,
        dns_config: DNSConfiguration
    ) -> Dict[str, Any]:
        """
        Configure DNS records for a domain.
        
        Args:
            domain: Domain name to configure
            dns_config: DNS configuration with records
            
        Returns:
            DNS configuration result
        """
        pass
    
    @abstractmethod
    async def get_dns_records(
        self,
        domain: str
    ) -> List[DNSRecord]:
        """
        Get current DNS records for a domain.
        
        Args:
            domain: Domain name to query
            
        Returns:
            List of current DNS records
        """
        pass
    
    @abstractmethod
    async def update_name_servers(
        self,
        domain: str,
        name_servers: List[str]
    ) -> Dict[str, Any]:
        """
        Update name servers for a domain.
        
        Args:
            domain: Domain name to update
            name_servers: List of name server hostnames
            
        Returns:
            Update result
        """
        pass
    
    @abstractmethod
    async def get_domain_info(
        self,
        domain: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a domain.
        
        Args:
            domain: Domain name to query
            
        Returns:
            Domain information including registration details
        """
        pass
    
    @abstractmethod
    async def enable_auto_renew(
        self,
        domain: str,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Enable or disable automatic renewal for a domain.
        
        Args:
            domain: Domain name to update
            enabled: Whether to enable auto-renewal
            
        Returns:
            Update result
        """
        pass
    
    @abstractmethod
    async def update_contact_info(
        self,
        domain: str,
        contact_info: ContactInformation
    ) -> Dict[str, Any]:
        """
        Update contact information for a domain.
        
        Args:
            domain: Domain name to update
            contact_info: New contact information
            
        Returns:
            Update result
        """
        pass
    
    @abstractmethod
    async def lock_domain(
        self,
        domain: str,
        locked: bool = True
    ) -> Dict[str, Any]:
        """
        Lock or unlock a domain to prevent transfers.
        
        Args:
            domain: Domain name to update
            locked: Whether to lock the domain
            
        Returns:
            Lock status update result
        """
        pass
    
    @abstractmethod
    async def get_auth_code(
        self,
        domain: str
    ) -> str:
        """
        Get authorization code for domain transfer.
        
        Args:
            domain: Domain name to get auth code for
            
        Returns:
            Authorization code for transfers
        """
        pass
