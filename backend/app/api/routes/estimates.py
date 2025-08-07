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
    EstimateListResponseSchema, EstimateActionResponse, NextEstimateNumberSchema
)
from ..schemas.activity_schemas import MessageResponse
from ...application.use_cases.estimate.create_estimate_use_case import CreateEstimateUseCase
from ...application.use_cases.estimate.get_estimate_use_case import GetEstimateUseCase
from ...application.use_cases.estimate.update_estimate_use_case import UpdateEstimateUseCase
from ...application.use_cases.estimate.delete_estimate_use_case import DeleteEstimateUseCase
from ...application.use_cases.estimate.list_estimates_use_case import ListEstimatesUseCase
from ...application.use_cases.estimate.search_estimates_use_case import SearchEstimatesUseCase
from ...application.use_cases.estimate.convert_estimate_to_invoice_use_case import ConvertEstimateToInvoiceUseCase
from ...application.use_cases.estimate.get_next_estimate_number_use_case import GetNextEstimateNumberUseCase
from ...application.dto.estimate_dto import (
    EstimateCreateDTO, EstimateUpdateDTO, EstimateDTO, EstimateFilters
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_estimate_repository,
    get_create_estimate_use_case, get_get_estimate_use_case, get_update_estimate_use_case,
    get_delete_estimate_use_case, get_list_estimates_use_case, get_search_estimates_use_case,
    get_convert_estimate_to_invoice_use_case, get_get_next_estimate_number_use_case
)
from ...domain.entities.estimate_enums.enums import EstimateStatus
from ...domain.shared.enums import CurrencyCode

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
        # Create DTO 
        create_dto = EstimateCreateDTO(
            contact_id=request.contact_id,
            title=request.title,
            description=request.description,
            currency=request.currency,
            tax_rate=float(request.tax_rate),
            tax_type=request.tax_type,
            overall_discount_type=request.overall_discount_type,
            overall_discount_value=float(request.overall_discount_value),
            terms=request.terms.__dict__ if request.terms else None,
            advance_payment=request.advance_payment.__dict__ if request.advance_payment else None,
            template_id=request.template_id,
            template_data=request.template_data,
            project_id=request.project_id,
            job_id=request.job_id,
            tags=request.tags,
            custom_fields=request.custom_fields,
            internal_notes=request.internal_notes,
            valid_until_date=request.valid_until_date,
            estimate_number=request.estimate_number,
            number_prefix=request.number_prefix,
            po_number=request.po_number,
            issue_date=request.issue_date
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
        create_dto = EstimateCreateDTO(
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


@router.get("/next-number", response_model=NextEstimateNumberSchema)
async def get_next_estimate_number(
    prefix: str = Query("EST", description="Prefix for the document number"),
    document_type: str = Query("estimate", description="Type of document: estimate or quote"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: GetNextEstimateNumberUseCase = Depends(get_get_next_estimate_number_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get the next available estimate or quote number.
    
    Returns the next available document number without creating an estimate.
    This is useful for showing users what number their next document will have.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        next_number = await use_case.execute(
            business_id=business_id,
            user_id=current_user["sub"],
            prefix=prefix,
            document_type=document_type
        )
        
        return NextEstimateNumberSchema(
            next_number=next_number,
            prefix=prefix,
            document_type=document_type
        )
    except ValidationError as e:
        logger.error(f"❌ EstimateAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error getting next estimate number: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{estimate_id}", response_model=EstimateResponseSchema)
async def get_estimate(
    estimate_id: uuid.UUID = Path(..., description="Estimate ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: GetEstimateUseCase = Depends(get_get_estimate_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get an estimate by ID.
    
    Retrieves detailed information about a specific estimate.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        estimate_dto = await use_case.execute(estimate_id, current_user["sub"], business_id)
        return _estimate_dto_to_response_from_dto(estimate_dto)
    except ValidationError as e:
        logger.error(f"❌ EstimateAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        logger.error(f"❌ EstimateAPI: Not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
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
    use_case: UpdateEstimateUseCase = Depends(get_update_estimate_use_case),
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
        line_items_dict = None
        if request.line_items is not None:
            line_items_dict = []
            for item in request.line_items:
                line_items_dict.append({
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "unit": item.unit,
                    "category": item.category,
                    "notes": item.notes
                })
        
        # Create update DTO
        update_dto = EstimateUpdateDTO(
            title=request.title,
            description=request.description,
            contact_id=request.contact_id,
            project_id=request.project_id,
            job_id=request.job_id,
            line_items=line_items_dict,
            currency=request.currency.value if request.currency else None,
            tax_rate=request.tax_rate,
            tax_type=request.tax_type.value if request.tax_type else None,
            overall_discount_type=request.overall_discount_type.value if request.overall_discount_type else None,
            overall_discount_value=request.overall_discount_value,
            tags=request.tags,
            custom_fields=request.custom_fields,
            internal_notes=request.internal_notes,
            valid_until_date=request.valid_until_date
        )
        
        estimate_dto = await use_case.execute(estimate_id, update_dto, current_user["sub"], business_id)
        return _estimate_dto_to_response_from_dto(estimate_dto)
    except ValidationError as e:
        logger.error(f"❌ EstimateAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        logger.error(f"❌ EstimateAPI: Not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ EstimateAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error updating estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{estimate_id}", response_model=MessageResponse)
async def delete_estimate(
    estimate_id: uuid.UUID = Path(..., description="Estimate ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: DeleteEstimateUseCase = Depends(get_delete_estimate_use_case),
    _: bool = Depends(require_delete_projects_dep)
):
    """
    Delete an estimate.
    
    Deletes an estimate. Only draft estimates can be deleted.
    Requires 'delete_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        await use_case.execute(estimate_id, current_user["sub"], business_id)
        return MessageResponse(message=f"Estimate {estimate_id} deleted successfully")
    except ValidationError as e:
        logger.error(f"❌ EstimateAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        logger.error(f"❌ EstimateAPI: Not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ EstimateAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ EstimateAPI: Error deleting estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/", response_model=EstimateListResponseSchema)
@router.get("", response_model=EstimateListResponseSchema, operation_id="list_estimates_no_slash")
async def list_estimates(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    estimate_status: Optional[EstimateStatus] = Query(None, description="Filter by estimate status"),
    contact_id: Optional[uuid.UUID] = Query(None, description="Filter by contact ID"),
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by job ID"),
    current_user: dict = Depends(get_current_user),
    use_case: ListEstimatesUseCase = Depends(get_list_estimates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    List estimates.
    
    Retrieves a paginated list of estimates for the current business.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Create filters DTO
        filters = EstimateFilters(
            status=estimate_status if estimate_status else None,
            contact_id=contact_id,
            project_id=project_id,
            job_id=job_id
        )
        
        result = await use_case.execute(
            business_id=business_id,
            user_id=current_user["sub"],
            filters=filters,
            skip=skip,
            limit=limit
        )
        
        return EstimateListResponseSchema(
            estimates=[_estimate_dto_to_response_from_dto(estimate_dto) for estimate_dto in result["estimates"]],
            total_count=result["total_count"],
            page=skip // limit + 1,
            per_page=limit,
            has_next=result["has_next"],
            has_prev=result["has_previous"]
        )
    except ValidationError as e:
        logger.error(f"❌ EstimateAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
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
    use_case: SearchEstimatesUseCase = Depends(get_search_estimates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Search estimates.
    
    Searches estimates with various filters and criteria.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Create search criteria DTO
        search_filters = EstimateFilters(
            search_term=request.query,
            status_list=request.status_filters,
            contact_id=request.contact_id,
            project_id=request.project_id,
            job_id=request.job_id,
            min_value=request.amount_min,
            max_value=request.amount_max,
            date_from=request.date_from,
            date_to=request.date_to
        )
        
        result = await use_case.execute(
            business_id=business_id,
            user_id=current_user["sub"],
            search_criteria=search_filters,
            skip=request.skip,
            limit=request.limit
        )
        
        return EstimateListResponseSchema(
            estimates=[_estimate_dto_to_response_from_dto(estimate_dto) for estimate_dto in result["estimates"]],
            total_count=result["total_count"],
            page=request.skip // request.limit + 1,
            per_page=request.limit,
            has_next=result["has_next"],
            has_prev=result["has_previous"]
        )
    except ValidationError as e:
        logger.error(f"❌ EstimateAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
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


def _estimate_dto_to_response(estimate) -> EstimateResponseSchema:
    """Convert estimate entity to response schema."""
    # Implementation
    pass  # Will be replaced with proper implementation

def _convert_terms_to_schema(terms) -> dict:
    """Convert EstimateTerms domain object to EstimateTermsSchema format."""
    if not terms:
        return None
    
    return {
        "payment_terms": terms.payment_terms or "",
        "validity_period": getattr(terms, 'validity_days', 30),
        "work_schedule": getattr(terms, 'work_schedule', ""),
        "materials_policy": getattr(terms, 'materials_policy', ""),
        "change_order_policy": getattr(terms, 'change_order_policy', ""),
        "warranty_terms": terms.warranty_period or "",
        "cancellation_policy": getattr(terms, 'cancellation_policy', ""),
        "acceptance_criteria": getattr(terms, 'acceptance_criteria', ""),
        "additional_terms": getattr(terms, 'additional_terms', [])
    }

def _estimate_dto_to_response_from_dto(estimate_dto: EstimateDTO) -> EstimateResponseSchema:
    """Convert estimate DTO to response schema."""
    return EstimateResponseSchema(
        id=estimate_dto.id,
        business_id=estimate_dto.business_id,
        estimate_number=estimate_dto.estimate_number,
        document_type=estimate_dto.document_type,
        document_type_display=estimate_dto.document_type_display,
        status=estimate_dto.status,
        contact_id=estimate_dto.contact_id,
        client_name=estimate_dto.client_name,
        client_email=estimate_dto.client_email,
        client_phone=estimate_dto.client_phone,
        client_address=estimate_dto.client_address.model_dump() if estimate_dto.client_address else None,
        title=estimate_dto.title,
        description=estimate_dto.description,
        po_number=estimate_dto.po_number,
        line_items=estimate_dto.line_items or [],
        currency=estimate_dto.currency,
        tax_rate=estimate_dto.tax_rate,
        tax_type=estimate_dto.tax_type,
        overall_discount_type=estimate_dto.overall_discount_type,
        overall_discount_value=estimate_dto.overall_discount_value,
        terms=_convert_terms_to_schema(estimate_dto.terms) if estimate_dto.terms else None,
        advance_payment=estimate_dto.advance_payment,
        template_id=estimate_dto.template_id,
        template_data=estimate_dto.template_data or {},
        project_id=estimate_dto.project_id,
        job_id=estimate_dto.job_id,
        tags=estimate_dto.tags or [],
        custom_fields=estimate_dto.custom_fields or {},
        internal_notes=estimate_dto.internal_notes,
        valid_until_date=estimate_dto.valid_until_date,
        issue_date=estimate_dto.issue_date,
        created_by=estimate_dto.created_by,
        created_date=estimate_dto.created_date,
        last_modified=estimate_dto.last_modified,
        sent_date=estimate_dto.sent_date,
        viewed_date=estimate_dto.viewed_date,
        accepted_date=estimate_dto.responded_date,
        financial_summary={
            "subtotal": float(estimate_dto.total_amount) if estimate_dto.total_amount else 0.0,
            "tax_amount": 0.0,  # Will be calculated properly later
            "discount_amount": 0.0,  # Will be calculated properly later
            "total_amount": float(estimate_dto.total_amount) if estimate_dto.total_amount else 0.0,
        },
        status_info={
            "is_expired": False,  # Will be calculated properly when needed
            "days_until_expiry": 0,  # Will be calculated properly when needed
            "can_be_converted": estimate_dto.status == "approved",
        }
    ) 