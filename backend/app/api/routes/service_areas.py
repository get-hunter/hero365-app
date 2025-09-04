"""
Service Areas API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from io import StringIO
import csv
import logging

from app.domain.entities.service_areas import (
    ServiceAreaCheckRequest,
    ServiceAreaCheckResponse,
    ServiceAreaBulkUpsert,
    ServiceArea,
    ServiceAreaUpdate,
    AvailabilityRequestCreate,
    AvailabilityRequestResponse,
    AvailabilityRequest
)
from app.application.services.service_areas_service import ServiceAreasService
from app.api.deps import get_current_user, get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)

router = APIRouter()


# =====================================
# PUBLIC ENDPOINTS (for booking widget)
# =====================================

@router.get("/public/service-areas/check", response_model=ServiceAreaCheckResponse)
async def check_service_area_support(
    business_id: str = Query(..., description="Business UUID"),
    postal_code: str = Query(..., description="Postal/ZIP code to check"),
    country_code: str = Query(default="US", description="Country code (ISO 3166-1 alpha-2)")
):
    """
    Check if a postal code is supported by a business.
    
    This endpoint is public and used by the booking widget to validate
    service areas before allowing users to proceed with booking.
    """
    try:
        service = ServiceAreasService()
        request = ServiceAreaCheckRequest(
            business_id=business_id,
            postal_code=postal_code,
            country_code=country_code
        )
        
        result = await service.check_service_area_support(request)
        return result
        
    except Exception as e:
        logger.error(f"Error checking service area support: {e}")
        raise HTTPException(status_code=500, detail="Failed to check service area")


@router.post("/public/availability/request", response_model=AvailabilityRequestResponse)
async def create_availability_request(request: AvailabilityRequestCreate):
    """
    Create an availability request for unsupported postal codes.
    
    This endpoint allows users to request service in areas where
    the business doesn't currently operate.
    """
    try:
        service = ServiceAreasService()
        result = await service.create_availability_request(request)
        return result
        
    except Exception as e:
        logger.error(f"Error creating availability request: {e}")
        raise HTTPException(status_code=500, detail="Failed to create availability request")


@router.get("/public/service-areas/{business_id}", response_model=List[ServiceArea])
async def get_public_service_areas(
    business_id: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip")
):
    """
    Get active service areas for a business (public endpoint).
    
    This endpoint is public and used by website builders, SEO tools, and other
    applications that need to know where a business provides services.
    Only returns active service areas.
    """
    try:
        service = ServiceAreasService()
        service_areas = await service.get_service_areas(
            business_id=business_id,
            q=None,  # No search filter for public endpoint
            limit=limit,
            offset=offset
        )
        # Filter to only return active service areas
        active_areas = [area for area in service_areas if area.is_active]
        return active_areas
        
    except Exception as e:
        logger.error(f"Error fetching public service areas for business {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch service areas")


# =====================================
# PROFESSIONAL ENDPOINTS (auth required)
# =====================================

@router.get("/pro/service-areas", response_model=List[ServiceArea])
async def get_service_areas(
    business_id: str = Query(..., description="Business UUID"),
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(default=50, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get service areas for a business.
    
    Supports search by postal code, city, or region.
    """
    try:
        # Basic business access validation (user must have access to the business)
        user_businesses = current_user.get("business_memberships", [])
        if not any(bm.get("business_id") == business_id for bm in user_businesses):
            raise HTTPException(status_code=403, detail="Access denied to business")
            
        service = ServiceAreasService()
        result = await service.get_service_areas(business_id, q, limit, offset)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service areas: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service areas")


@router.post("/pro/service-areas/bulk-upsert")
async def bulk_upsert_service_areas(
    request: ServiceAreaBulkUpsert,
    current_user: dict = Depends(get_current_user)
):
    """
    Bulk create or update service areas.
    
    This endpoint allows businesses to efficiently manage large numbers
    of service areas. Existing areas are updated, new ones are created.
    """
    try:
        # Ensure user has access to the business
        user_businesses = current_user.get("business_memberships", [])
        if not any(bm.get("business_id") == request.business_id for bm in user_businesses):
            raise HTTPException(status_code=403, detail="Access denied to business")
            
        service = ServiceAreasService()
        result = await service.bulk_upsert_service_areas(request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk upserting service areas: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk upsert service areas")


@router.put("/pro/service-areas/{area_id}", response_model=ServiceArea)
async def update_service_area(
    area_id: str,
    update_data: ServiceAreaUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a specific service area."""
    try:
        service = ServiceAreasService()
        result = await service.update_service_area(area_id, update_data)
        return result
        
    except Exception as e:
        logger.error(f"Error updating service area: {e}")
        raise HTTPException(status_code=500, detail="Failed to update service area")


@router.delete("/pro/service-areas/{area_id}")
async def delete_service_area(
    area_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a service area."""
    try:
        service = ServiceAreasService()
        success = await service.delete_service_area(area_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Service area not found")
            
        return {"success": True, "message": "Service area deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting service area: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete service area")


@router.post("/pro/service-areas/import")
async def import_service_areas_csv(
    business_id: str = Query(..., description="Business UUID"),
    file: UploadFile = File(..., description="CSV file with service areas"),
    current_user: dict = Depends(get_current_user)
):
    """
    Import service areas from CSV file.
    
    Expected CSV format:
    postal_code,country_code,city,region,timezone,is_active
    78701,US,Austin,TX,America/Chicago,true
    78702,US,Austin,TX,America/Chicago,true
    """
    try:
        # Ensure user has access to the business
        user_businesses = current_user.get("business_memberships", [])
        if not any(bm.get("business_id") == business_id for bm in user_businesses):
            raise HTTPException(status_code=403, detail="Access denied to business")
            
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        service = ServiceAreasService()
        result = await service.import_service_areas_csv(business_id, csv_content)
        
        return result
        
    except Exception as e:
        logger.error(f"Error importing service areas CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to import service areas")


@router.get("/pro/service-areas/export.csv")
async def export_service_areas_csv(
    business_id: str = Query(..., description="Business UUID"),
    current_user: dict = Depends(get_current_user)
):
    """Export service areas as CSV file."""
    try:
        # Ensure user has access to the business
        user_businesses = current_user.get("business_memberships", [])
        if not any(bm.get("business_id") == business_id for bm in user_businesses):
            raise HTTPException(status_code=403, detail="Access denied to business")
            
        service = ServiceAreasService()
        csv_content = await service.export_service_areas_csv(business_id)
        
        # Create streaming response
        def generate():
            yield csv_content
            
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=service_areas_{business_id}.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting service areas CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to export service areas")


@router.get("/pro/availability-requests", response_model=List[AvailabilityRequest])
async def get_availability_requests(
    business_id: str = Query(..., description="Business UUID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(default=50, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get availability requests for a business.
    
    These are requests from potential customers in areas where
    the business doesn't currently provide service.
    """
    try:
        # Ensure user has access to the business
        user_businesses = current_user.get("business_memberships", [])
        if not any(bm.get("business_id") == business_id for bm in user_businesses):
            raise HTTPException(status_code=403, detail="Access denied to business")
            
        service = ServiceAreasService()
        result = await service.get_availability_requests(business_id, status, limit, offset)
        return result
        
    except Exception as e:
        logger.error(f"Error getting availability requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to get availability requests")


@router.put("/pro/availability-requests/{request_id}/status", response_model=AvailabilityRequest)
async def update_availability_request_status(
    request_id: str,
    status: str = Query(..., description="New status"),
    notes: Optional[str] = Query(None, description="Optional notes"),
    current_user: dict = Depends(get_current_user)
):
    """
    Update the status of an availability request.
    
    Valid statuses: new, contacted, scheduled, converted, declined
    """
    try:
        valid_statuses = ['new', 'contacted', 'scheduled', 'converted', 'declined']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
            
        service = ServiceAreasService()
        result = await service.update_availability_request_status(request_id, status, notes)
        return result
        
    except Exception as e:
        logger.error(f"Error updating availability request status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update availability request status")
