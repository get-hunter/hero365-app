"""
Business Trades Public API

Provides public endpoints for business trade relationships and capabilities.
Used by website builder for trade-based filtering and navigation.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Optional
import logging
from pydantic import BaseModel

from app.api.deps import get_supabase_client
from supabase import Client as SupabaseClient

logger = logging.getLogger(__name__)

router = APIRouter()


class TradeItem(BaseModel):
    """Public trade item for website consumption."""
    trade_slug: str
    trade_display_name: str
    trade_icon: Optional[str] = None
    trade_color: Optional[str] = None
    market_type: str
    is_primary: bool = False
    proficiency_level: str = "standard"
    years_experience: int = 0


class BusinessTradesResponse(BaseModel):
    """Response containing business trade relationships."""
    business_id: str
    primary_trade: Optional[TradeItem] = None
    secondary_trades: List[TradeItem] = []
    all_trades: List[TradeItem] = []


@router.get("/trades", response_model=BusinessTradesResponse)
async def get_business_trades(
    business_id: str = Path(..., description="Business ID"),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> BusinessTradesResponse:
    """
    Get all trade relationships for a business.
    
    This endpoint provides the canonical trade relationships for filtering
    services, products, and content by trade specialization.
    """
    try:
        logger.info(f"🔍 [API] Fetching trades for business: {business_id}")
        
        # Query business_trades with trade details
        result = supabase.table("business_trades")\
            .select("""
                is_primary,
                proficiency_level,
                years_experience,
                trades!inner(slug, display_name, icon, color, market_type)
            """)\
            .eq("business_id", business_id)\
            .order("is_primary", desc=True)\
            .execute()
        
        if not result.data:
            logger.warning(f"⚠️ [API] No trades found for business: {business_id}")
            return BusinessTradesResponse(
                business_id=business_id,
                primary_trade=None,
                secondary_trades=[],
                all_trades=[]
            )
        
        # Process trade relationships
        primary_trade = None
        secondary_trades = []
        all_trades = []
        
        for row in result.data:
            trade_data = row["trades"]
            trade_item = TradeItem(
                trade_slug=trade_data["slug"],
                trade_display_name=trade_data["display_name"],
                trade_icon=trade_data.get("icon"),
                trade_color=trade_data.get("color"),
                market_type=trade_data["market_type"],
                is_primary=row["is_primary"],
                proficiency_level=row.get("proficiency_level", "standard"),
                years_experience=row.get("years_experience", 0)
            )
            
            all_trades.append(trade_item)
            
            if row["is_primary"]:
                primary_trade = trade_item
            else:
                secondary_trades.append(trade_item)
        
        response = BusinessTradesResponse(
            business_id=business_id,
            primary_trade=primary_trade,
            secondary_trades=secondary_trades,
            all_trades=all_trades
        )
        
        logger.info(f"✅ [API] Returning {len(all_trades)} trades for business: {business_id}")
        return response
        
    except Exception as e:
        logger.error(f"Application error retrieving trades for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve business trades")


@router.get("/available-trades", response_model=List[TradeItem])
async def get_available_trades(
    market_type: Optional[str] = Query(None, description="Filter by market type (residential/commercial/both)"),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[TradeItem]:
    """
    Get all available trades in the system.
    
    This endpoint provides the complete trade taxonomy for filtering
    and selection purposes.
    """
    try:
        logger.info(f"🔍 [API] Fetching available trades, market_type: {market_type}")
        
        # Query all active trades
        query = supabase.table("trades")\
            .select("slug, display_name, icon, color, market_type")\
            .eq("is_active", True)\
            .order("display_order")\
            .order("display_name")
        
        if market_type and market_type in ["residential", "commercial"]:
            # Filter by market type (both 'both' and specific type)
            query = query.in_("market_type", [market_type, "both"])
        
        result = query.execute()
        
        if not result.data:
            logger.warning("⚠️ [API] No active trades found")
            return []
        
        # Convert to TradeItem objects
        trades = []
        for row in result.data:
            trade_item = TradeItem(
                trade_slug=row["slug"],
                trade_display_name=row["display_name"],
                trade_icon=row.get("icon"),
                trade_color=row.get("color"),
                market_type=row["market_type"],
                is_primary=False,  # Not applicable for available trades
                proficiency_level="standard",  # Not applicable for available trades
                years_experience=0  # Not applicable for available trades
            )
            trades.append(trade_item)
        
        logger.info(f"✅ [API] Returning {len(trades)} available trades")
        return trades
        
    except Exception as e:
        logger.error(f"Application error retrieving available trades: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available trades")
