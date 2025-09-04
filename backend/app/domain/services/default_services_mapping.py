"""
Default Services Mapping for Trades
DEPRECATED: This module is being phased out in favor of the activity-based taxonomy system.
"""

from typing import Dict, List
from app.domain.entities.business import MarketFocus


class DefaultServicesMapping:
    """
    DEPRECATED: Legacy mapping for trades to services.
    
    This class is being phased out in favor of the activity-based taxonomy system.
    Use the trade taxonomy and activity selection instead.
    """
    
    @staticmethod
    def get_default_services_for_business(
        primary_trade: str,
        secondary_trades: List[str] = None,
        market_focus: MarketFocus = MarketFocus.BOTH
    ) -> Dict[str, List[str]]:
        """
        DEPRECATED: Returns empty services list.
        Use the new activity-based onboarding flow instead.
        """
        return {
            "residential": [],
            "commercial": []
        }