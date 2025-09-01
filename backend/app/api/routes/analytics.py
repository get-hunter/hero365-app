"""
Analytics API Routes - Revenue Tracking & ROI Dashboard
"""
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.application.services.conversion_tracking_service import ConversionTrackingService
from app.api.deps import get_current_user, get_supabase_client
from supabase import Client


router = APIRouter()


class ConversionTrackRequest(BaseModel):
    """Request model for tracking conversions"""
    type: str = Field(..., description="Type of conversion (contact, quote, booking, etc.)")
    value: float = Field(default=0.0, description="Estimated value of the conversion")
    page: str = Field(default="/", description="Source page where conversion happened")
    visitor: Dict = Field(default_factory=dict, description="Visitor data (IP, user agent, etc.)")
    details: Dict = Field(default_factory=dict, description="Additional conversion details")


class ConversionTrackResponse(BaseModel):
    """Response model for conversion tracking"""
    success: bool
    conversion_id: str
    message: str


class AnalyticsResponse(BaseModel):
    """Response model for analytics data"""
    period_days: int
    total_conversions: int
    total_value: float
    average_conversion_value: float
    conversions_by_type: Dict
    conversions_by_page: Dict
    daily_conversions: list


class ROIResponse(BaseModel):
    """Response model for ROI metrics"""
    period_days: int
    total_revenue: float
    estimated_cost: float
    net_profit: float
    roi_percentage: float
    cost_per_conversion: float
    revenue_per_conversion: float


@router.post("/track-conversion", response_model=ConversionTrackResponse)
async def track_conversion(
    request: ConversionTrackRequest,
    business_id: UUID = Query(..., description="Business ID for the website"),
    db: Client = Depends(get_supabase_client)
):
    """
    Track a conversion event from the website
    This endpoint is called by the ConversionTracker component
    """
    try:
        service = ConversionTrackingService(db)
        
        conversion = await service.track_conversion(
            business_id=business_id,
            conversion_data={
                'type': request.type,
                'value': request.value,
                'page': request.page,
                'visitor': request.visitor,
                'details': request.details
            }
        )
        
        return ConversionTrackResponse(
            success=True,
            conversion_id=str(conversion['id']),
            message="Conversion tracked successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track conversion: {str(e)}")


@router.get("/analytics/{business_id}", response_model=AnalyticsResponse)
async def get_analytics(
    business_id: UUID,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """
    Get conversion analytics for the business dashboard
    """
    try:
        # Verify user has access to this business
        # TODO: Add proper authorization check
        
        service = ConversionTrackingService(db)
        analytics = await service.get_conversion_analytics(business_id, days)
        
        return AnalyticsResponse(**analytics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/roi/{business_id}", response_model=ROIResponse)
async def get_roi_metrics(
    business_id: UUID,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """
    Get ROI metrics for the business website
    """
    try:
        # Verify user has access to this business
        # TODO: Add proper authorization check
        
        service = ConversionTrackingService(db)
        roi_metrics = await service.get_roi_metrics(business_id, days)
        
        return ROIResponse(**roi_metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ROI metrics: {str(e)}")


@router.get("/dashboard/{business_id}")
async def get_dashboard_data(
    business_id: UUID,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """
    Get complete dashboard data (analytics + ROI) in one call
    Optimized for mobile app dashboard
    """
    try:
        service = ConversionTrackingService(db)
        
        # Get both analytics and ROI in parallel
        analytics = await service.get_conversion_analytics(business_id, days)
        roi_metrics = await service.get_roi_metrics(business_id, days)
        
        return {
            'analytics': analytics,
            'roi': roi_metrics,
            'summary': {
                'total_conversions': analytics['total_conversions'],
                'total_revenue': analytics['total_value'],
                'roi_percentage': roi_metrics['roi_percentage'],
                'net_profit': roi_metrics['net_profit']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")
