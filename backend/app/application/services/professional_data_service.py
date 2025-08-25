"""
Professional Data Service

Service for fetching real professional data from the Hero365 backend
to populate website templates with dynamic content.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from urllib.parse import urljoin

from ...core.config import settings

logger = logging.getLogger(__name__)


class ProfessionalDataService:
    """Service for fetching professional data from Hero365 APIs."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or "http://localhost:8000"  # Default to local API
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def get_professional_profile(self, business_id: str) -> Dict[str, Any]:
        """Fetch professional profile information."""
        
        url = f"{self.base_url}/api/v1/public/professional/profile/{business_id}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched profile for {business_id}")
                        return data
                    else:
                        logger.warning(f"Failed to fetch profile for {business_id}: {response.status}")
                        return self._get_fallback_profile(business_id)
                        
        except Exception as e:
            logger.error(f"Error fetching profile for {business_id}: {str(e)}")
            return self._get_fallback_profile(business_id)
    
    async def get_professional_services(
        self, 
        business_id: str, 
        category: Optional[str] = None,
        emergency_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch professional services using the new service template system."""
        
        # Use the new service template API endpoint
        url = f"{self.base_url}/service-templates/business/{business_id}/services"
        params = {
            "is_active": True,
            "include_template": True
        }
        
        if category:
            # TODO: Map category name to category_id if needed
            params["category_name"] = category
        if emergency_only:
            params["is_emergency"] = emergency_only
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched {len(data)} services for {business_id}")
                        return data
                    else:
                        logger.warning(f"Failed to fetch services for {business_id}: {response.status}")
                        return self._get_fallback_services(business_id)
                        
        except Exception as e:
            logger.error(f"Error fetching services for {business_id}: {str(e)}")
            return self._get_fallback_services(business_id)
    
    async def get_professional_products(
        self, 
        business_id: str,
        category: Optional[str] = None,
        in_stock_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Fetch professional products."""
        
        url = f"{self.base_url}/api/v1/public/professional/products/{business_id}"
        params = {}
        
        if category:
            params["category"] = category
        if in_stock_only:
            params["in_stock_only"] = in_stock_only
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched {len(data)} products for {business_id}")
                        return data
                    else:
                        logger.warning(f"Failed to fetch products for {business_id}: {response.status}")
                        return self._get_fallback_products(business_id)
                        
        except Exception as e:
            logger.error(f"Error fetching products for {business_id}: {str(e)}")
            return self._get_fallback_products(business_id)
    
    async def get_professional_availability(
        self, 
        business_id: str,
        days_ahead: int = 14
    ) -> Dict[str, Any]:
        """Fetch professional availability."""
        
        url = f"{self.base_url}/api/v1/public/professional/availability/{business_id}"
        
        # Calculate date range
        start_date = date.today()
        end_date = date.today().replace(day=start_date.day + days_ahead)
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched availability for {business_id}")
                        return data
                    else:
                        logger.warning(f"Failed to fetch availability for {business_id}: {response.status}")
                        return self._get_fallback_availability(business_id)
                        
        except Exception as e:
            logger.error(f"Error fetching availability for {business_id}: {str(e)}")
            return self._get_fallback_availability(business_id)
    
    async def get_complete_professional_data(self, business_id: str) -> Dict[str, Any]:
        """Fetch all professional data in parallel for website generation."""
        
        logger.info(f"Fetching complete professional data for {business_id}")
        
        # Fetch all data in parallel
        tasks = [
            self.get_professional_profile(business_id),
            self.get_professional_services(business_id),
            self.get_professional_products(business_id),
            self.get_professional_availability(business_id)
        ]
        
        try:
            profile, services, products, availability = await asyncio.gather(*tasks)
            
            return {
                "profile": profile,
                "services": services,
                "products": products,
                "availability": availability,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching complete data for {business_id}: {str(e)}")
            # Return fallback data
            return {
                "profile": self._get_fallback_profile(business_id),
                "services": self._get_fallback_services(business_id),
                "products": self._get_fallback_products(business_id),
                "availability": self._get_fallback_availability(business_id),
                "fetched_at": datetime.utcnow().isoformat(),
                "fallback_used": True
            }
    
    def _get_fallback_profile(self, business_id: str) -> Dict[str, Any]:
        """Fallback profile data when API is unavailable."""
        
        return {
            "business_id": business_id,
            "business_name": "Professional Services",
            "trade_type": "hvac",
            "description": "Professional HVAC services with years of experience",
            "phone": "(555) 123-4567",
            "email": "info@professional.com",
            "address": "123 Main St, Austin, TX 78701",
            "service_areas": ["Austin", "Round Rock", "Cedar Park"],
            "emergency_service": True,
            "years_in_business": 10,
            "license_number": "LICENSE123",
            "insurance_verified": True,
            "average_rating": 4.8,
            "total_reviews": 150,
            "certifications": ["Licensed & Insured", "Professional Certified"]
        }
    
    def _get_fallback_services(self, business_id: str) -> List[Dict[str, Any]]:
        """Fallback services data when API is unavailable."""
        
        return [
            {
                "id": "service-1",
                "name": "Emergency Repair",
                "description": "24/7 emergency repair service",
                "category": "Repair",
                "base_price": 99.0,
                "price_range_min": 99.0,
                "price_range_max": 299.0,
                "pricing_unit": "service call",
                "duration_minutes": 120,
                "is_emergency": True,
                "requires_quote": False,
                "available": True,
                "service_areas": ["Austin", "Round Rock"],
                "keywords": ["emergency", "repair", "24/7"]
            },
            {
                "id": "service-2",
                "name": "Installation Service",
                "description": "Professional installation service",
                "category": "Installation",
                "base_price": None,
                "price_range_min": 500.0,
                "price_range_max": 5000.0,
                "pricing_unit": "project",
                "duration_minutes": 240,
                "is_emergency": False,
                "requires_quote": True,
                "available": True,
                "service_areas": ["Austin", "Round Rock"],
                "keywords": ["installation", "new", "professional"]
            }
        ]
    
    def _get_fallback_products(self, business_id: str) -> List[Dict[str, Any]]:
        """Fallback products data when API is unavailable."""
        
        return [
            {
                "id": "product-1",
                "name": "Professional Equipment",
                "description": "High-quality professional equipment",
                "category": "Equipment",
                "brand": "Professional Brand",
                "model": "Model 2024",
                "price": 1299.99,
                "msrp": 1499.99,
                "in_stock": True,
                "stock_quantity": 10,
                "specifications": {
                    "type": "Professional Grade",
                    "warranty": "5 years"
                },
                "warranty_years": 5,
                "energy_rating": "Energy Star"
            }
        ]
    
    def _get_fallback_availability(self, business_id: str) -> Dict[str, Any]:
        """Fallback availability data when API is unavailable."""
        
        from datetime import timedelta
        
        today = date.today()
        available_dates = [
            (today + timedelta(days=i)).isoformat() 
            for i in range(1, 8)  # Next 7 days
        ]
        
        return {
            "business_id": business_id,
            "available_dates": available_dates,
            "slots": [],
            "emergency_available": True,
            "next_available": (datetime.now() + timedelta(hours=2)).isoformat(),
            "service_areas": [
                {"area": "Austin", "available": True, "response_time": "30 min"},
                {"area": "Round Rock", "available": True, "response_time": "45 min"}
            ]
        }
    
    def format_services_for_website(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format services data for website template consumption."""
        
        formatted_services = []
        
        for service in services:
            # Format pricing display
            if service.get("requires_quote"):
                price_display = "Free Quote"
            elif service.get("base_price"):
                price_display = f"From ${service['base_price']:.0f}"
            elif service.get("price_range_min") and service.get("price_range_max"):
                price_display = f"${service['price_range_min']:.0f} - ${service['price_range_max']:.0f}"
            else:
                price_display = "Contact for Pricing"
            
            # Format features
            features = []
            if service.get("is_emergency"):
                features.append("24/7 Emergency Service")
            if service.get("duration_minutes"):
                hours = service["duration_minutes"] / 60
                if hours >= 1:
                    features.append(f"~{hours:.0f} hour service")
                else:
                    features.append(f"~{service['duration_minutes']} min service")
            if service.get("service_areas"):
                features.append(f"Serves {len(service['service_areas'])} areas")
            
            formatted_services.append({
                "title": service["name"],
                "description": service["description"],
                "price": price_display,
                "features": features,
                "isPopular": service.get("is_emergency", False),
                "isEmergency": service.get("is_emergency", False),
                "category": service.get("category", "Service")
            })
        
        return formatted_services
    
    def format_products_for_website(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format products data for website template consumption."""
        
        formatted_products = []
        
        for product in products:
            # Format pricing
            price_display = f"${product['price']:.2f}" if product.get("price") else "Contact for Price"
            
            # Format specifications as features
            features = []
            specs = product.get("specifications", {})
            for key, value in specs.items():
                features.append(f"{key.replace('_', ' ').title()}: {value}")
            
            if product.get("warranty_years"):
                features.append(f"{product['warranty_years']}-year warranty")
            
            if product.get("energy_rating"):
                features.append(f"Energy Rating: {product['energy_rating']}")
            
            formatted_products.append({
                "title": product["name"],
                "description": product["description"],
                "price": price_display,
                "features": features,
                "brand": product.get("brand", ""),
                "model": product.get("model", ""),
                "category": product.get("category", "Product"),
                "in_stock": product.get("in_stock", True),
                "image_url": product.get("image_url")
            })
        
        return formatted_products


# Factory function
def create_professional_data_service(base_url: str = None) -> ProfessionalDataService:
    """Create and configure professional data service."""
    return ProfessionalDataService(base_url=base_url)
