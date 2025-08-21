"""
Cloudflare Domain Registration Adapter

Pure infrastructure adapter for Cloudflare domain registration and DNS management.
Contains NO business logic - only external API communication.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime

from ...application.ports.domain_registry_port import (
    DomainRegistryPort, DomainAvailabilityResult, DomainPricingInfo,
    ContactInformation, DomainRegistrationResult, DNSRecord, DNSConfiguration
)
from ...core.config import settings

logger = logging.getLogger(__name__)


class CloudflareDomainAdapter(DomainRegistryPort):
    """
    Infrastructure adapter for Cloudflare domain registration.
    
    This adapter ONLY handles:
    - Cloudflare API communication
    - Data format conversion
    - HTTP requests and responses
    
    It contains NO business logic or domain rules.
    """
    
    def __init__(self):
        self.api_token = getattr(settings, 'CLOUDFLARE_API_TOKEN', None)
        self.account_id = getattr(settings, 'CLOUDFLARE_ACCOUNT_ID', None)
        self.base_url = "https://api.cloudflare.com/client/v4"
        
        if not self.api_token or not self.account_id:
            logger.warning("Cloudflare credentials not configured")
    
    async def check_domain_availability(self, domain: str) -> DomainAvailabilityResult:
        """Check domain availability via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}/availability"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            result_data = data.get('result', {})
                            
                            return DomainAvailabilityResult(
                                domain=domain,
                                available=result_data.get('available', False),
                                premium=result_data.get('premium', False),
                                price=Decimal(str(result_data.get('price', 0))) if result_data.get('price') else None,
                                renewal_price=Decimal(str(result_data.get('renewal_price', 0))) if result_data.get('renewal_price') else None,
                                registration_period_years=1,
                                transfer_lock_days=60,
                                redemption_period_days=30
                            )
                    
                    # Default response for API errors
                    return DomainAvailabilityResult(
                        domain=domain,
                        available=False,
                        premium=False
                    )
                    
        except Exception as e:
            logger.error(f"Cloudflare availability check failed for {domain}: {str(e)}")
            return DomainAvailabilityResult(
                domain=domain,
                available=False,
                premium=False
            )
    
    async def check_multiple_domains(self, domains: List[str]) -> List[DomainAvailabilityResult]:
        """Check availability of multiple domains."""
        
        # Execute checks in parallel
        tasks = [self.check_domain_availability(domain) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Domain check failed for {domains[i]}: {str(result)}")
                # Add failed result
                valid_results.append(DomainAvailabilityResult(
                    domain=domains[i],
                    available=False,
                    premium=False
                ))
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def get_domain_pricing(self, tld: str) -> DomainPricingInfo:
        """Get pricing information for a TLD via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/pricing"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            pricing_data = data.get('result', {})
                            
                            # Find pricing for specific TLD
                            for tld_pricing in pricing_data.get('tlds', []):
                                if tld_pricing.get('tld') == tld:
                                    return DomainPricingInfo(
                                        domain=f"example{tld}",
                                        tld=tld,
                                        registration_price=Decimal(str(tld_pricing.get('registration_price', 0))),
                                        renewal_price=Decimal(str(tld_pricing.get('renewal_price', 0))),
                                        transfer_price=Decimal(str(tld_pricing.get('transfer_price', 0))),
                                        redemption_price=Decimal(str(tld_pricing.get('redemption_price', 0))) if tld_pricing.get('redemption_price') else None,
                                        currency=tld_pricing.get('currency', 'USD'),
                                        premium=False
                                    )
            
            # Default pricing if not found
            return self._get_default_pricing(tld)
            
        except Exception as e:
            logger.error(f"Cloudflare pricing lookup failed for {tld}: {str(e)}")
            return self._get_default_pricing(tld)
    
    async def register_domain(
        self,
        domain: str,
        contact_info: ContactInformation,
        registration_years: int = 1,
        auto_renew: bool = True,
        privacy_protection: bool = True,
        name_servers: Optional[List[str]] = None
    ) -> DomainRegistrationResult:
        """Register domain via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}/register"
                
                # Prepare registration data
                registration_data = {
                    "years": registration_years,
                    "auto_renew": auto_renew,
                    "privacy": privacy_protection,
                    "contacts": {
                        "registrant": self._format_contact_info(contact_info),
                        "admin": self._format_contact_info(contact_info),
                        "tech": self._format_contact_info(contact_info),
                        "billing": self._format_contact_info(contact_info)
                    }
                }
                
                if name_servers:
                    registration_data["name_servers"] = name_servers
                
                async with session.post(url, json=registration_data) as response:
                    data = await response.json()
                    
                    if response.status == 200 and data.get('success'):
                        result_data = data.get('result', {})
                        
                        return DomainRegistrationResult(
                            success=True,
                            domain=domain,
                            registration_id=result_data.get('id'),
                            expires_at=self._parse_datetime(result_data.get('expires_at')),
                            name_servers=result_data.get('name_servers', []),
                            auto_renew=auto_renew,
                            privacy_protection=privacy_protection,
                            transaction_id=result_data.get('transaction_id')
                        )
                    else:
                        error_msg = self._extract_error_message(data)
                        return DomainRegistrationResult(
                            success=False,
                            domain=domain,
                            error_message=error_msg
                        )
                        
        except Exception as e:
            logger.error(f"Cloudflare domain registration failed for {domain}: {str(e)}")
            return DomainRegistrationResult(
                success=False,
                domain=domain,
                error_message=str(e)
            )
    
    async def transfer_domain(
        self,
        domain: str,
        auth_code: str,
        contact_info: ContactInformation
    ) -> DomainRegistrationResult:
        """Transfer domain via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}/transfer"
                
                transfer_data = {
                    "auth_code": auth_code,
                    "contacts": {
                        "registrant": self._format_contact_info(contact_info),
                        "admin": self._format_contact_info(contact_info),
                        "tech": self._format_contact_info(contact_info),
                        "billing": self._format_contact_info(contact_info)
                    }
                }
                
                async with session.post(url, json=transfer_data) as response:
                    data = await response.json()
                    
                    if response.status == 200 and data.get('success'):
                        result_data = data.get('result', {})
                        
                        return DomainRegistrationResult(
                            success=True,
                            domain=domain,
                            registration_id=result_data.get('id'),
                            expires_at=self._parse_datetime(result_data.get('expires_at')),
                            name_servers=result_data.get('name_servers', []),
                            transaction_id=result_data.get('transaction_id')
                        )
                    else:
                        error_msg = self._extract_error_message(data)
                        return DomainRegistrationResult(
                            success=False,
                            domain=domain,
                            error_message=error_msg
                        )
                        
        except Exception as e:
            logger.error(f"Cloudflare domain transfer failed for {domain}: {str(e)}")
            return DomainRegistrationResult(
                success=False,
                domain=domain,
                error_message=str(e)
            )
    
    async def renew_domain(self, domain: str, years: int = 1) -> DomainRegistrationResult:
        """Renew domain via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}/renew"
                
                renew_data = {"years": years}
                
                async with session.post(url, json=renew_data) as response:
                    data = await response.json()
                    
                    if response.status == 200 and data.get('success'):
                        result_data = data.get('result', {})
                        
                        return DomainRegistrationResult(
                            success=True,
                            domain=domain,
                            registration_id=result_data.get('id'),
                            expires_at=self._parse_datetime(result_data.get('expires_at')),
                            transaction_id=result_data.get('transaction_id')
                        )
                    else:
                        error_msg = self._extract_error_message(data)
                        return DomainRegistrationResult(
                            success=False,
                            domain=domain,
                            error_message=error_msg
                        )
                        
        except Exception as e:
            logger.error(f"Cloudflare domain renewal failed for {domain}: {str(e)}")
            return DomainRegistrationResult(
                success=False,
                domain=domain,
                error_message=str(e)
            )
    
    async def configure_dns(self, domain: str, dns_config: DNSConfiguration) -> Dict[str, Any]:
        """Configure DNS records via Cloudflare API."""
        
        try:
            # First, get the zone ID for the domain
            zone_id = await self._get_zone_id(domain)
            if not zone_id:
                return {"success": False, "error": "Zone not found"}
            
            async with self._get_session() as session:
                results = []
                
                # Create/update each DNS record
                for record in dns_config.records:
                    record_data = {
                        "type": record.type,
                        "name": record.name,
                        "content": record.value,
                        "ttl": record.ttl
                    }
                    
                    if record.priority is not None:
                        record_data["priority"] = record.priority
                    
                    # Create DNS record
                    url = f"{self.base_url}/zones/{zone_id}/dns_records"
                    
                    async with session.post(url, json=record_data) as response:
                        data = await response.json()
                        results.append({
                            "record": record.name,
                            "success": response.status == 200 and data.get('success', False),
                            "id": data.get('result', {}).get('id') if data.get('success') else None,
                            "error": self._extract_error_message(data) if not data.get('success') else None
                        })
                
                return {
                    "success": all(r["success"] for r in results),
                    "records": results
                }
                
        except Exception as e:
            logger.error(f"Cloudflare DNS configuration failed for {domain}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_dns_records(self, domain: str) -> List[DNSRecord]:
        """Get DNS records via Cloudflare API."""
        
        try:
            zone_id = await self._get_zone_id(domain)
            if not zone_id:
                return []
            
            async with self._get_session() as session:
                url = f"{self.base_url}/zones/{zone_id}/dns_records"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            records = []
                            for record_data in data.get('result', []):
                                records.append(DNSRecord(
                                    name=record_data.get('name', ''),
                                    type=record_data.get('type', ''),
                                    value=record_data.get('content', ''),
                                    ttl=record_data.get('ttl', 300),
                                    priority=record_data.get('priority')
                                ))
                            return records
            
            return []
            
        except Exception as e:
            logger.error(f"Cloudflare DNS records lookup failed for {domain}: {str(e)}")
            return []
    
    async def update_name_servers(self, domain: str, name_servers: List[str]) -> Dict[str, Any]:
        """Update name servers via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}"
                
                update_data = {"name_servers": name_servers}
                
                async with session.patch(url, json=update_data) as response:
                    data = await response.json()
                    
                    return {
                        "success": response.status == 200 and data.get('success', False),
                        "name_servers": name_servers,
                        "error": self._extract_error_message(data) if not data.get('success') else None
                    }
                    
        except Exception as e:
            logger.error(f"Cloudflare name server update failed for {domain}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get domain information via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            return data.get('result', {})
            
            return {}
            
        except Exception as e:
            logger.error(f"Cloudflare domain info lookup failed for {domain}: {str(e)}")
            return {}
    
    async def enable_auto_renew(self, domain: str, enabled: bool = True) -> Dict[str, Any]:
        """Enable/disable auto-renewal via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}"
                
                update_data = {"auto_renew": enabled}
                
                async with session.patch(url, json=update_data) as response:
                    data = await response.json()
                    
                    return {
                        "success": response.status == 200 and data.get('success', False),
                        "auto_renew": enabled,
                        "error": self._extract_error_message(data) if not data.get('success') else None
                    }
                    
        except Exception as e:
            logger.error(f"Cloudflare auto-renew update failed for {domain}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_contact_info(self, domain: str, contact_info: ContactInformation) -> Dict[str, Any]:
        """Update contact information via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}"
                
                update_data = {
                    "contacts": {
                        "registrant": self._format_contact_info(contact_info),
                        "admin": self._format_contact_info(contact_info),
                        "tech": self._format_contact_info(contact_info),
                        "billing": self._format_contact_info(contact_info)
                    }
                }
                
                async with session.patch(url, json=update_data) as response:
                    data = await response.json()
                    
                    return {
                        "success": response.status == 200 and data.get('success', False),
                        "error": self._extract_error_message(data) if not data.get('success') else None
                    }
                    
        except Exception as e:
            logger.error(f"Cloudflare contact update failed for {domain}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def lock_domain(self, domain: str, locked: bool = True) -> Dict[str, Any]:
        """Lock/unlock domain via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}"
                
                update_data = {"locked": locked}
                
                async with session.patch(url, json=update_data) as response:
                    data = await response.json()
                    
                    return {
                        "success": response.status == 200 and data.get('success', False),
                        "locked": locked,
                        "error": self._extract_error_message(data) if not data.get('success') else None
                    }
                    
        except Exception as e:
            logger.error(f"Cloudflare domain lock update failed for {domain}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_auth_code(self, domain: str) -> str:
        """Get authorization code via Cloudflare API."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/registrar/domains/{domain}/auth_code"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            return data.get('result', {}).get('auth_code', '')
            
            return ''
            
        except Exception as e:
            logger.error(f"Cloudflare auth code lookup failed for {domain}: {str(e)}")
            return ''
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get HTTP session with Cloudflare authentication."""
        
        return aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        )
    
    async def _get_zone_id(self, domain: str) -> Optional[str]:
        """Get Cloudflare zone ID for a domain."""
        
        try:
            async with self._get_session() as session:
                url = f"{self.base_url}/zones"
                params = {"name": domain}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success') and data.get('result'):
                            return data['result'][0].get('id')
            
            return None
            
        except Exception as e:
            logger.error(f"Zone ID lookup failed for {domain}: {str(e)}")
            return None
    
    def _format_contact_info(self, contact_info: ContactInformation) -> Dict[str, str]:
        """Format contact information for Cloudflare API."""
        
        return {
            "first_name": contact_info.first_name,
            "last_name": contact_info.last_name,
            "organization": contact_info.organization or "",
            "email": contact_info.email,
            "phone": contact_info.phone,
            "address": contact_info.address_line_1,
            "address2": contact_info.address_line_2 or "",
            "city": contact_info.city,
            "state": contact_info.state,
            "zip": contact_info.postal_code,
            "country": contact_info.country
        }
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Cloudflare API."""
        
        if not datetime_str:
            return None
        
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _extract_error_message(self, response_data: Dict[str, Any]) -> str:
        """Extract error message from Cloudflare API response."""
        
        if response_data.get('errors'):
            errors = response_data['errors']
            if isinstance(errors, list) and errors:
                return errors[0].get('message', 'Unknown error')
        
        return response_data.get('message', 'Unknown error')
    
    def _get_default_pricing(self, tld: str) -> DomainPricingInfo:
        """Get default pricing for TLD when API fails."""
        
        # Default pricing based on common TLD costs
        default_prices = {
            '.com': {'reg': 12.99, 'renew': 14.99, 'transfer': 12.99},
            '.net': {'reg': 14.99, 'renew': 16.99, 'transfer': 14.99},
            '.org': {'reg': 13.99, 'renew': 15.99, 'transfer': 13.99},
            '.services': {'reg': 29.99, 'renew': 34.99, 'transfer': 29.99},
            '.biz': {'reg': 18.99, 'renew': 20.99, 'transfer': 18.99},
            '.info': {'reg': 16.99, 'renew': 18.99, 'transfer': 16.99},
            '.us': {'reg': 9.99, 'renew': 11.99, 'transfer': 9.99},
            '.co': {'reg': 24.99, 'renew': 29.99, 'transfer': 24.99}
        }
        
        prices = default_prices.get(tld, {'reg': 15.99, 'renew': 17.99, 'transfer': 15.99})
        
        return DomainPricingInfo(
            domain=f"example{tld}",
            tld=tld,
            registration_price=Decimal(str(prices['reg'])),
            renewal_price=Decimal(str(prices['renew'])),
            transfer_price=Decimal(str(prices['transfer'])),
            currency='USD',
            premium=False
        )
