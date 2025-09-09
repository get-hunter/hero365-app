"""
Service Materialization Service
Handles materializing default services into business_services table
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID
from decimal import Decimal

from app.domain.entities.business import Business, MarketFocus
from app.domain.services.default_services_mapping import DefaultServicesMapping
from app.domain.services.slug_utils import SlugUtils
from app.domain.repositories.business_repository import BusinessRepository
from app.infrastructure.database.repositories.supabase_service_template_repository import SupabaseBusinessServiceRepository
from supabase import Client

logger = logging.getLogger(__name__)


class ServiceMaterializationService:
    """
    Service to materialize default services into business_services table
    based on business trades and market focus.
    """
    
    def __init__(self, business_repository: BusinessRepository, supabase_client: Client):
        self.business_repository = business_repository
        self.business_service_repository = SupabaseBusinessServiceRepository(supabase_client)
    
    async def materialize_default_services(self, business_id: UUID) -> Dict[str, int]:
        """
        Materialize default services for a business.
        
        Returns:
            Dict with counts of created residential and commercial services
        """
        logger.info(f"Materializing default services for business {business_id}")
        
        # Get business
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        
        # Get default services based on trades and market focus
        default_services = DefaultServicesMapping.get_default_services_for_business(
            primary_trade=business.industry or "",
            secondary_trades=self._get_secondary_trades(business),
            market_focus=business.market_focus
        )
        
        # Note: No longer updating legacy service keys - services are materialized directly into business_services
        
        # Create business_services entries
        residential_count = await self._create_business_services(
            business_id, default_services['residential'], 'residential', business.market_focus
        )
        commercial_count = await self._create_business_services(
            business_id, default_services['commercial'], 'commercial', business.market_focus
        )
        
        logger.info(f"Materialized {residential_count} residential and {commercial_count} commercial services")
        
        return {
            'residential_services_created': residential_count,
            'commercial_services_created': commercial_count,
            'total_services_created': residential_count + commercial_count
        }
    
    def _get_secondary_trades(self, business: Business) -> List[str]:
        """Extract secondary trades from business."""
        trades = []
        
        # Add from commercial_trades
        for trade in business.commercial_trades:
            trade_value = trade.value if hasattr(trade, 'value') else trade
            if trade_value != business.industry and trade_value not in trades:
                trades.append(trade_value)
        
        # Add from residential_trades  
        for trade in business.residential_trades:
            trade_value = trade.value if hasattr(trade, 'value') else trade
            if trade_value != business.industry and trade_value not in trades:
                trades.append(trade_value)
        
        return trades
    
    async def _create_business_services(
        self, 
        business_id: UUID, 
        service_keys: List[str], 
        market_type: str,
        market_focus: MarketFocus
    ) -> int:
        """Create business_services entries for the given service keys."""
        if not service_keys:
            return 0
        
        created_count = 0
        
        for service_key in service_keys:
            try:
                # Convert service key to display name
                display_name = DefaultServicesMapping.get_service_display_name(service_key)
                
                # Generate slug (kebab-case)
                slug = SlugUtils.normalize_service_slug(service_key)
                
                # Set market flags
                is_residential = market_type == 'residential' or market_focus == MarketFocus.BOTH
                is_commercial = market_type == 'commercial' or market_focus == MarketFocus.BOTH
                
                # Get default pricing based on service type
                price_min, price_max = self._get_default_pricing(service_key, market_type)
                
                service_data = {
                    'business_id': str(business_id),
                    'service_name': display_name,
                    'service_slug': slug,
                    'description': f"Professional {display_name.lower()} services",
                    'category': market_type.title(),
                    'price_type': 'range',
                    'price_min': price_min,
                    'price_max': price_max,
                    'price_unit': 'job',
                    'is_emergency': 'emergency' in service_key.lower(),
                    'is_residential': is_residential,
                    'is_commercial': is_commercial,
                    'is_active': True,
                    'display_order': 0
                }
                
                # Create the service (will handle conflicts)
                await self.business_service_repository.create_business_service(service_data)
                created_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to create service {service_key} for business {business_id}: {e}")
                continue
        
        return created_count
    
    def _get_default_pricing(self, service_key: str, market_type: str) -> tuple[Decimal, Decimal]:
        """Get default pricing for a service based on type and market."""
        # Basic pricing logic - can be enhanced with more sophisticated rules
        base_prices = {
            'residential': {
                'emergency': (150, 800),
                'installation': (200, 2000),
                'repair': (100, 600),
                'maintenance': (80, 300),
                'cleaning': (100, 400),
                'inspection': (75, 200),
                'default': (120, 500)
            },
            'commercial': {
                'emergency': (200, 1200),
                'installation': (500, 5000),
                'repair': (150, 1500),
                'maintenance': (200, 2000),
                'cleaning': (200, 800),
                'inspection': (150, 500),
                'default': (200, 1000)
            }
        }
        
        market_prices = base_prices.get(market_type, base_prices['residential'])
        
        # Determine price category based on service key
        if 'emergency' in service_key:
            min_price, max_price = market_prices['emergency']
        elif 'installation' in service_key:
            min_price, max_price = market_prices['installation']
        elif 'repair' in service_key:
            min_price, max_price = market_prices['repair']
        elif 'maintenance' in service_key:
            min_price, max_price = market_prices['maintenance']
        elif 'cleaning' in service_key:
            min_price, max_price = market_prices['cleaning']
        elif 'inspection' in service_key:
            min_price, max_price = market_prices['inspection']
        else:
            min_price, max_price = market_prices['default']
        
        return Decimal(str(min_price)), Decimal(str(max_price))
