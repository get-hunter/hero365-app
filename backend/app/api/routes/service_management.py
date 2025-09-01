"""
Service Management API Routes
Endpoints for managing business services and default service assignments
"""

import uuid
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.api.dtos.service_management_dtos import (
    DefaultServicesResponse,
    BusinessServicesResponse,
    UpdateBusinessServicesRequest,
    AutoAssignServicesRequest,
    TradeServicesPreviewResponse,
    ServiceInfo
)
from app.domain.repositories.business_repository import BusinessRepository
from app.domain.services.default_services_mapping import DefaultServicesMapping
from app.domain.entities.business import MarketFocus, ResidentialTrade, CommercialTrade
from app.application.services.service_materialization_service import ServiceMaterializationService
from app.api.deps import get_current_user, get_supabase_client
from app.infrastructure.config.dependency_injection import get_business_repository

router = APIRouter(prefix="/services", tags=["Service Management"])
security = HTTPBearer()


@router.get("/default", response_model=DefaultServicesResponse)
async def get_default_services():
    """
    Get all available default services organized by trade categories.
    This endpoint helps mobile apps show available service options.
    """
    try:
        # Get services organized by category
        residential_by_trade = DefaultServicesMapping.get_services_by_category('residential')
        commercial_by_trade = DefaultServicesMapping.get_services_by_category('commercial')
        
        # Convert to ServiceInfo objects
        residential_services = {}
        for trade, services in residential_by_trade.items():
            residential_services[trade] = [
                ServiceInfo(
                    key=service,
                    display_name=DefaultServicesMapping.get_service_display_name(service),
                    trade_category=trade
                )
                for service in services
            ]
        
        commercial_services = {}
        for trade, services in commercial_by_trade.items():
            commercial_services[trade] = [
                ServiceInfo(
                    key=service,
                    display_name=DefaultServicesMapping.get_service_display_name(service),
                    trade_category=trade
                )
                for service in services
            ]
        
        return DefaultServicesResponse(
            residential_services=residential_services,
            commercial_services=commercial_services
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get default services: {str(e)}"
        )


@router.post("/preview", response_model=TradeServicesPreviewResponse)
async def preview_services_for_trades(request: AutoAssignServicesRequest):
    """
    Preview what services would be auto-assigned for given trades.
    This helps users see what services they'll get before creating their business.
    """
    try:
        # Get default services for the trades
        default_services = DefaultServicesMapping.get_default_services_for_business(
            primary_trade=request.primary_trade,
            secondary_trades=request.secondary_trades,
            market_focus=request.market_focus
        )
        
        # Create service details map
        service_details = {}
        all_services = set(default_services['residential'] + default_services['commercial'])
        
        for service in all_services:
            service_details[service] = ServiceInfo(
                key=service,
                display_name=DefaultServicesMapping.get_service_display_name(service),
                trade_category="auto-assigned"
            )
        
        return TradeServicesPreviewResponse(
            primary_trade=request.primary_trade,
            secondary_trades=request.secondary_trades,
            market_focus=request.market_focus,
            residential_services=default_services['residential'],
            commercial_services=default_services['commercial'],
            service_details=service_details
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to preview services: {str(e)}"
        )


@router.get("/business/{business_id}", response_model=BusinessServicesResponse)
async def get_business_services(
    business_id: str,
    business_repository: BusinessRepository = Depends(get_business_repository),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current services for a business along with all available options.
    """
    try:
        current_user_id = current_user.get('id')
        business_uuid = uuid.UUID(business_id)
        
        # Get business
        business = await business_repository.get_by_id(business_uuid)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Check if user has access to this business
        if str(business.owner_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get all available services
        residential_by_trade = DefaultServicesMapping.get_services_by_category('residential')
        commercial_by_trade = DefaultServicesMapping.get_services_by_category('commercial')
        
        # Convert to ServiceInfo objects
        available_residential = {}
        for trade, services in residential_by_trade.items():
            available_residential[trade] = [
                ServiceInfo(
                    key=service,
                    display_name=DefaultServicesMapping.get_service_display_name(service),
                    trade_category=trade
                )
                for service in services
            ]
        
        available_commercial = {}
        for trade, services in commercial_by_trade.items():
            available_commercial[trade] = [
                ServiceInfo(
                    key=service,
                    display_name=DefaultServicesMapping.get_service_display_name(service),
                    trade_category=trade
                )
                for service in services
            ]
        
        return BusinessServicesResponse(
            business_id=business_id,
            market_focus=business.market_focus,
            residential_services=[service.value for service in business.residential_services],
            commercial_services=[service.value for service in business.commercial_services],
            available_residential_services=available_residential,
            available_commercial_services=available_commercial
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid business ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business services: {str(e)}"
        )


@router.put("/business/{business_id}", response_model=BusinessServicesResponse)
async def update_business_services(
    business_id: str,
    request: UpdateBusinessServicesRequest,
    business_repository: BusinessRepository = Depends(get_business_repository),
    current_user: dict = Depends(get_current_user)
):
    """
    Update services for a business. Users can select/unselect services.
    """
    try:
        current_user_id = current_user.get('id')
        business_uuid = uuid.UUID(business_id)
        
        # Get business
        business = await business_repository.get_by_id(business_uuid)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Check if user has access to this business
        if str(business.owner_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update services
        updates = {}
        
        if request.residential_services is not None:
            # Convert strings to ResidentialTrade enums
            residential_services = []
            for service_key in request.residential_services:
                try:
                    residential_services.append(ResidentialTrade(service_key))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid residential service: {service_key}"
                    )
            updates['residential_services'] = residential_services
        
        if request.commercial_services is not None:
            # Convert strings to CommercialTrade enums
            commercial_services = []
            for service_key in request.commercial_services:
                try:
                    commercial_services.append(CommercialTrade(service_key))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid commercial service: {service_key}"
                    )
            updates['commercial_services'] = commercial_services
        
        # Update business
        updated_business = business.model_copy(update=updates)
        await business_repository.update(updated_business)
        
        # Return updated services (reuse the get endpoint logic)
        return await get_business_services(business_id, business_repository, current_user)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid business ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update business services: {str(e)}"
        )


@router.post("/business/{business_id}/auto-assign", response_model=BusinessServicesResponse)
async def auto_assign_services(
    business_id: str,
    request: AutoAssignServicesRequest,
    business_repository: BusinessRepository = Depends(get_business_repository),
    current_user: dict = Depends(get_current_user)
):
    """
    Auto-assign default services based on primary and secondary trades.
    This is useful for onboarding or when users change their trade focus.
    """
    try:
        current_user_id = current_user.get('id')
        business_uuid = uuid.UUID(business_id)
        
        # Get business
        business = await business_repository.get_by_id(business_uuid)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Check if user has access to this business
        if str(business.owner_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update business with new trades and market focus
        updated_business = business.model_copy(update={
            'industry': request.primary_trade,
            'secondary_trades': request.secondary_trades,
            'market_focus': request.market_focus
        })
        
        # Auto-assign services
        updated_business = updated_business.auto_assign_default_services()
        
        # Save updated business
        await business_repository.update(updated_business)
        
        # Return updated services
        return await get_business_services(business_id, business_repository, current_user)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid business ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-assign services: {str(e)}"
        )


@router.post("/business/{business_id}/materialize-defaults")
async def materialize_default_services(
    business_id: str,
    business_repository: BusinessRepository = Depends(get_business_repository),
    supabase_client = Depends(get_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Materialize default services into business_services table.
    Creates actual service catalog entries based on business trades and market focus.
    """
    try:
        current_user_id = current_user.get('id')
        business_uuid = uuid.UUID(business_id)
        
        # Get business and check access
        business = await business_repository.get_by_id(business_uuid)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Check if user has access to this business
        if str(business.owner_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Initialize materialization service
        materialization_service = ServiceMaterializationService(
            business_repository=business_repository,
            supabase_client=supabase_client
        )
        
        # Materialize services
        result = await materialization_service.materialize_default_services(business_uuid)
        
        return {
            "success": True,
            "business_id": business_id,
            "message": "Default services materialized successfully",
            **result
        }
        
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to materialize services: {str(e)}"
        )
