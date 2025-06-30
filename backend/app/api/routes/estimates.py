"""
Estimate API Routes

REST API endpoints for estimate management operations.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import (
    require_view_projects_dep, require_edit_projects_dep, require_delete_projects_dep
)
from ..schemas.estimate_schemas import (
    CreateEstimateSchema, UpdateEstimateSchema, EstimateSearchSchema,
    EstimateStatusUpdateSchema, EstimateResponseSchema, 
    EstimateListResponseSchema, EstimateActionResponse, EstimateAnalyticsResponse
)
from ..schemas.activity_schemas import MessageResponse
from ...application.use_cases.estimate.create_estimate_use_case import CreateEstimateUseCase
from ...application.use_cases.estimate.convert_estimate_to_invoice_use_case import ConvertEstimateToInvoiceUseCase
from ...application.dto.estimate_dto import (
    CreateEstimateDTO, EstimateLineItemDTO, EstimateDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_estimate_repository, get_estimate_template_repository,
    get_create_estimate_use_case, get_convert_estimate_to_invoice_use_case
)
from ...domain.enums import EstimateStatus, CurrencyCode

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/estimates", tags=["estimates"])


@router.post("/", response_model=EstimateResponseSchema, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=EstimateResponseSchema, status_code=status.HTTP_201_CREATED, operation_id="create_estimate_no_slash")
async def create_estimate(
    request: CreateEstimateSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateEstimateUseCase = Depends(get_create_estimate_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create a new estimate.
    
    Creates a new estimate for the current business with the provided information.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 EstimateAPI: Starting estimate creation for business {business_id}")
    logger.info(f"🔧 EstimateAPI: Request data: {request}")
    
    try:
        # Convert line items
        line_items = []
        if request.line_items:
            for item in request.line_items:
                line_items.append(EstimateLineItemDTO(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    unit=item.unit,
                    category=item.category,
                    notes=item.notes
                ))
        
        # Create DTO
        create_dto = CreateEstimateDTO(
            business_id=business_id,
            estimate_number=request.estimate_number,
            title=request.title,
            description=request.description,
            contact_id=request.contact_id,
            project_id=request.project_id,
            job_id=request.job_id,
            line_items=line_items,
            subtotal=request.subtotal,
            tax_rate=request.tax_rate,
            tax_amount=request.tax_amount,
            discount_rate=request.discount_rate,
            discount_amount=request.discount_amount,
            total_amount=request.total_amount,
            currency=CurrencyCode(request.currency.value) if request.currency else CurrencyCode.USD,
            valid_until=request.valid_until,
            notes=request.notes,
            terms_and_conditions=request.terms_and_conditions,
            template_id=request.template_id,
            created_by=current_user["sub"]
        )
        
        logger.info(f"🔧 EstimateAPI: DTO created successfully, calling use case")
        
        estimate_dto = await use_case.execute(create_dto, current_user["sub"])
        logger.info(f"🔧 EstimateAPI: Use case completed successfully")
        return _estimate_dto_to_response(estimate_dto)
    except ValidationError as e:
        logger.error(f"❌ EstimateAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionDeniedError as e:
        logger.error(f"❌ EstimateAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ EstimateAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error creating estimate: {str(e)}")
        logger.error(f"❌ EstimateAPI: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ EstimateAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/from-template", response_model=EstimateResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_estimate_from_template(
    request: CreateEstimateSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateEstimateUseCase = Depends(get_create_estimate_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create a new estimate from a template.
    
    Creates a new estimate using a predefined template with customizable fields.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 EstimateAPI: Creating estimate from template {request.template_id}")
    
    try:
        # Create DTO with template reference
        create_dto = CreateEstimateDTO(
            business_id=business_id,
            title=request.title,
            description=request.description,
            contact_id=request.contact_id,
            project_id=request.project_id,
            job_id=request.job_id,
            template_id=request.template_id,
            template_variables=request.template_variables,
            valid_until=request.valid_until,
            notes=request.notes,
            created_by=current_user["sub"]
        )
        
        estimate_dto = await use_case.execute(create_dto, current_user["sub"])
        return _estimate_dto_to_response(estimate_dto)
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error creating estimate from template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{estimate_id}", response_model=EstimateResponseSchema)
async def get_estimate(
    estimate_id: uuid.UUID = Path(..., description="Estimate ID"),
    current_user: dict = Depends(get_current_user),
    estimate_repository = Depends(get_estimate_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get an estimate by ID.
    
    Retrieves detailed information about a specific estimate.
    Requires 'view_projects' permission.
    """
    try:
        estimate = await estimate_repository.get_by_id(estimate_id)
        if not estimate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estimate with ID {estimate_id} not found"
            )
        
        return _estimate_dto_to_response(estimate)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error getting estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{estimate_id}", response_model=EstimateResponseSchema)
async def update_estimate(
    estimate_id: uuid.UUID = Path(..., description="Estimate ID"),
    request: UpdateEstimateSchema = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    estimate_repository = Depends(get_estimate_repository),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Update an estimate.
    
    Updates an existing estimate with the provided information.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 EstimateAPI: Starting estimate update for estimate {estimate_id}")
    
    try:
        # Convert line items if provided
        line_items = None
        if request.line_items is not None:
            line_items = []
            for item in request.line_items:
                line_items.append(EstimateLineItemDTO(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    unit=item.unit,
                    category=item.category,
                    notes=item.notes
                ))
        
        # Create update DTO
        update_dto = EstimateUpdateDTO(
            estimate_id=estimate_id,
            business_id=business_id,
            title=request.title,
            description=request.description,
            line_items=line_items,
            subtotal=request.subtotal,
            tax_rate=request.tax_rate,
            tax_amount=request.tax_amount,
            discount_rate=request.discount_rate,
            discount_amount=request.discount_amount,
            total_amount=request.total_amount,
            valid_until=request.valid_until,
            notes=request.notes,
            terms_and_conditions=request.terms_and_conditions,
            updated_by=current_user["sub"]
        )
        
        updated_estimate = await estimate_repository.update(update_dto)
        return _estimate_dto_to_response(updated_estimate)
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error updating estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{estimate_id}", response_model=MessageResponse)
async def delete_estimate(
    estimate_id: uuid.UUID = Path(..., description="Estimate ID"),
    current_user: dict = Depends(get_current_user),
    estimate_repository = Depends(get_estimate_repository),
    _: bool = Depends(require_delete_projects_dep)
):
    """
    Delete an estimate.
    
    Deletes an estimate. Only draft estimates can be deleted.
    Requires 'delete_projects' permission.
    """
    try:
        await estimate_repository.delete(estimate_id)
        return MessageResponse(message=f"Estimate {estimate_id} deleted successfully")
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error deleting estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=EstimateListResponseSchema)
@router.get("", response_model=EstimateListResponseSchema, operation_id="list_estimates_no_slash")
async def list_estimates(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[EstimateStatus] = Query(None, description="Filter by estimate status"),
    contact_id: Optional[uuid.UUID] = Query(None, description="Filter by contact ID"),
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by job ID"),
    current_user: dict = Depends(get_current_user),
    estimate_repository = Depends(get_estimate_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    List estimates.
    
    Retrieves a paginated list of estimates for the current business.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Build filters
        filters = {"business_id": business_id}
        if status:
            filters["status"] = status
        if contact_id:
            filters["contact_id"] = contact_id
        if project_id:
            filters["project_id"] = project_id
        if job_id:
            filters["job_id"] = job_id
        
        estimates, total = await estimate_repository.list_with_pagination(
            business_id=business_id,
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        return EstimateListResponse(
            estimates=[_estimate_dto_to_response(estimate) for estimate in estimates],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error listing estimates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search", response_model=EstimateListResponseSchema)
async def search_estimates(
    request: EstimateSearchSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    estimate_repository = Depends(get_estimate_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Search estimates.
    
    Searches estimates with various filters and criteria.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Create search DTO
        search_dto = EstimateSearchDTO(
            business_id=business_id,
            query=request.query,
            status_filters=request.status_filters,
            contact_id=request.contact_id,
            project_id=request.project_id,
            job_id=request.job_id,
            date_from=request.date_from,
            date_to=request.date_to,
            amount_min=request.amount_min,
            amount_max=request.amount_max,
            skip=request.skip,
            limit=request.limit,
            sort_by=request.sort_by,
            sort_order=request.sort_order
        )
        
        estimates, total = await estimate_repository.search(search_dto)
        
        return EstimateListResponse(
            estimates=[_estimate_dto_to_response(estimate) for estimate in estimates],
            total=total,
            skip=request.skip,
            limit=request.limit
        )
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error searching estimates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{estimate_id}/status", response_model=EstimateResponseSchema)
async def update_estimate_status(
    estimate_id: uuid.UUID = Path(..., description="Estimate ID"),
    request: EstimateStatusUpdateSchema = Body(...),
    current_user: dict = Depends(get_current_user),
    estimate_repository = Depends(get_estimate_repository),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Update estimate status.
    
    Updates the status of an estimate with optional notes.
    Requires 'edit_projects' permission.
    """
    try:
        updated_estimate = await estimate_repository.update_status(
            estimate_id=estimate_id,
            status=request.status,
            notes=request.notes,
            updated_by=current_user["sub"]
        )
        
        return _estimate_dto_to_response(updated_estimate)
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error updating estimate status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{estimate_id}/convert-to-invoice", response_model=EstimateActionResponse)
async def convert_estimate_to_invoice(
    estimate_id: uuid.UUID = Path(..., description="Estimate ID"),
    advance_payment_amount: Optional[float] = Query(None, description="Optional advance payment amount"),
    current_user: dict = Depends(get_current_user),
    use_case: ConvertEstimateToInvoiceUseCase = Depends(get_convert_estimate_to_invoice_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Convert estimate to invoice.
    
    Converts an approved estimate to an invoice.
    Requires 'edit_projects' permission.
    """
    try:
        invoice_dto = await use_case.execute(
            estimate_id=estimate_id,
            user_id=current_user["sub"],
            advance_payment_amount=advance_payment_amount
        )
        
        return EstimateActionResponse(
            message="Estimate converted to invoice successfully",
            estimate_id=estimate_id,
            invoice_id=invoice_dto.invoice_id
        )
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error converting estimate to invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/analytics/overview", response_model=EstimateAnalyticsResponse)
async def get_estimate_analytics(
    business_context: dict = Depends(get_business_context),
    date_from: Optional[datetime] = Query(None, description="Start date for analytics"),
    date_to: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: dict = Depends(get_current_user),
    estimate_repository = Depends(get_estimate_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get estimate analytics.
    
    Retrieves comprehensive estimate analytics for the current business.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        analytics = await estimate_repository.get_analytics(
            business_id=business_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return analytics
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error getting estimate analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


def _estimate_dto_to_response(estimate_dto) -> EstimateResponseSchema:
    """Convert EstimateDTO to EstimateResponse."""
    return EstimateResponseSchema(
        estimate_id=estimate_dto.estimate_id,
        business_id=estimate_dto.business_id,
        estimate_number=estimate_dto.estimate_number,
        title=estimate_dto.title,
        description=estimate_dto.description,
        status=estimate_dto.status,
        contact_id=estimate_dto.contact_id,
        project_id=estimate_dto.project_id,
        job_id=estimate_dto.job_id,
        line_items=estimate_dto.line_items,
        subtotal=estimate_dto.subtotal,
        tax_rate=estimate_dto.tax_rate,
        tax_amount=estimate_dto.tax_amount,
        discount_rate=estimate_dto.discount_rate,
        discount_amount=estimate_dto.discount_amount,
        total_amount=estimate_dto.total_amount,
        currency=estimate_dto.currency,
        valid_until=estimate_dto.valid_until,
        notes=estimate_dto.notes,
        terms_and_conditions=estimate_dto.terms_and_conditions,
        template_id=estimate_dto.template_id,
        created_at=estimate_dto.created_at,
        updated_at=estimate_dto.updated_at,
        created_by=estimate_dto.created_by,
        updated_by=estimate_dto.updated_by
    ) 