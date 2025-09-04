"""
Service Management DTOs
Data Transfer Objects for service management operations
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.domain.entities.business import MarketFocus


class ServiceInfo(BaseModel):
    """Information about a service"""
    key: str = Field(..., description="Service key/identifier")
    display_name: str = Field(..., description="Human-readable service name")
    trade_category: str = Field(..., description="Trade category this service belongs to")


class DefaultServicesResponse(BaseModel):
    """Response containing default services for trades"""
    residential_services: Dict[str, List[ServiceInfo]] = Field(
        ..., description="Residential services organized by trade"
    )
    commercial_services: Dict[str, List[ServiceInfo]] = Field(
        ..., description="Commercial services organized by trade"
    )


class BusinessServicesResponse(BaseModel):
    """Response containing current business services"""
    business_id: str = Field(..., description="Business identifier")
    market_focus: MarketFocus = Field(..., description="Business market focus")
    residential_services: List[str] = Field(..., description="Current residential services")
    commercial_services: List[str] = Field(..., description="Current commercial services")
    available_residential_services: Dict[str, List[ServiceInfo]] = Field(
        ..., description="All available residential services by trade"
    )
    available_commercial_services: Dict[str, List[ServiceInfo]] = Field(
        ..., description="All available commercial services by trade"
    )


class UpdateBusinessServicesRequest(BaseModel):
    """Request to update business services"""
    residential_services: Optional[List[str]] = Field(
        None, description="Residential services to set (trade keys)"
    )
    commercial_services: Optional[List[str]] = Field(
        None, description="Commercial services to set (trade keys)"
    )


class AutoAssignServicesRequest(BaseModel):
    """Request to auto-assign default services"""
    primary_trade: str = Field(..., description="Primary trade of the business")
    secondary_trades: Optional[List[str]] = Field(
        default_factory=list, description="Secondary trades"
    )
    market_focus: MarketFocus = Field(..., description="Market focus")


class TradeServicesPreviewResponse(BaseModel):
    """Preview of services that would be assigned for given trades"""
    primary_trade: str = Field(..., description="Primary trade")
    secondary_trades: List[str] = Field(..., description="Secondary trades")
    market_focus: MarketFocus = Field(..., description="Market focus")
    residential_services: List[str] = Field(..., description="Residential services that would be assigned")
    commercial_services: List[str] = Field(..., description="Commercial services that would be assigned")
    service_details: Dict[str, ServiceInfo] = Field(..., description="Details for all services")
