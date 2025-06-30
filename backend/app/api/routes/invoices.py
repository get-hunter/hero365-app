"""
Invoice API Routes

REST API endpoints for invoice management operations.
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
from ..schemas.invoice_schemas import (
    CreateInvoiceSchema, InvoiceSearchSchema, CreateInvoiceFromEstimateSchema,
    ProcessPaymentSchema, InvoiceResponseSchema, InvoiceListResponseSchema,
    InvoiceStatusUpdateSchema, PaymentResponse
)
from ...application.use_cases.invoice.create_invoice_use_case import CreateInvoiceUseCase
from ...application.use_cases.invoice.process_payment_use_case import ProcessPaymentUseCase
from ...application.dto.invoice_dto import (
    CreateInvoiceDTO, CreateInvoiceFromEstimateDTO, ProcessPaymentDTO,
    InvoiceLineItemDTO, InvoiceDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_invoice_repository,
    get_create_invoice_use_case, get_process_payment_use_case
)
from ...domain.enums import InvoiceStatus, PaymentMethod, CurrencyCode

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/", response_model=InvoiceResponseSchema, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=InvoiceResponseSchema, status_code=status.HTTP_201_CREATED, operation_id="create_invoice_no_slash")
async def create_invoice(
    request: CreateInvoiceSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateInvoiceUseCase = Depends(get_create_invoice_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create a new invoice.
    
    Creates a new invoice for the current business with the provided information.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Starting invoice creation for business {business_id}")
    logger.info(f"🔧 InvoiceAPI: Request data: {request}")
    
    try:
        # Convert line items
        line_items = []
        if request.line_items:
            for item in request.line_items:
                line_items.append(InvoiceLineItemDTO(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    unit=item.unit,
                    category=item.category,
                    notes=item.notes
                ))
        
        # Create DTO
        create_dto = CreateInvoiceDTO(
            business_id=business_id,
            invoice_number=request.invoice_number,
            title=request.title,
            description=request.description,
            contact_id=request.contact_id,
            project_id=request.project_id,
            job_id=request.job_id,
            estimate_id=request.estimate_id,
            line_items=line_items,
            subtotal=request.subtotal,
            tax_rate=request.tax_rate,
            tax_amount=request.tax_amount,
            discount_rate=request.discount_rate,
            discount_amount=request.discount_amount,
            total_amount=request.total_amount,
            currency=CurrencyCode(request.currency.value) if request.currency else CurrencyCode.USD,
            issue_date=request.issue_date,
            due_date=request.due_date,
            payment_terms=request.payment_terms,
            notes=request.notes,
            terms_and_conditions=request.terms_and_conditions,
            created_by=current_user["sub"]
        )
        
        logger.info(f"🔧 InvoiceAPI: DTO created successfully, calling use case")
        
        invoice_dto = await use_case.execute(create_dto, current_user["sub"])
        logger.info(f"🔧 InvoiceAPI: Use case completed successfully")
        return _invoice_dto_to_response(invoice_dto)
    except ValidationError as e:
        logger.error(f"❌ InvoiceAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionDeniedError as e:
        logger.error(f"❌ InvoiceAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ InvoiceAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error creating invoice: {str(e)}")
        logger.error(f"❌ InvoiceAPI: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ InvoiceAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


def _invoice_dto_to_response(invoice_dto) -> InvoiceResponseSchema:
    """Convert InvoiceDTO to InvoiceResponse."""
    return InvoiceResponseSchema(
        invoice_id=invoice_dto.invoice_id,
        business_id=invoice_dto.business_id,
        invoice_number=invoice_dto.invoice_number,
        title=invoice_dto.title,
        description=invoice_dto.description,
        status=invoice_dto.status,
        contact_id=invoice_dto.contact_id,
        project_id=invoice_dto.project_id,
        job_id=invoice_dto.job_id,
        estimate_id=invoice_dto.estimate_id,
        line_items=invoice_dto.line_items,
        subtotal=invoice_dto.subtotal,
        tax_rate=invoice_dto.tax_rate,
        tax_amount=invoice_dto.tax_amount,
        discount_rate=invoice_dto.discount_rate,
        discount_amount=invoice_dto.discount_amount,
        total_amount=invoice_dto.total_amount,
        amount_paid=invoice_dto.amount_paid,
        amount_due=invoice_dto.amount_due,
        currency=invoice_dto.currency,
        issue_date=invoice_dto.issue_date,
        due_date=invoice_dto.due_date,
        payment_terms=invoice_dto.payment_terms,
        notes=invoice_dto.notes,
        terms_and_conditions=invoice_dto.terms_and_conditions,
        created_at=invoice_dto.created_at,
        updated_at=invoice_dto.updated_at,
        created_by=invoice_dto.created_by,
        updated_by=invoice_dto.updated_by
    )


@router.post("/from-estimate", response_model=InvoiceResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_invoice_from_estimate(
    request: CreateInvoiceFromEstimateSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateInvoiceUseCase = Depends(get_create_invoice_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create a new invoice from an estimate.
    
    Creates a new invoice based on an existing estimate.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Creating invoice from estimate {request.estimate_id}")
    
    try:
        # Create DTO for invoice from estimate
        create_dto = CreateInvoiceFromEstimateDTO(
            business_id=business_id,
            estimate_id=request.estimate_id,
            title=request.title,
            description=request.description,
            issue_date=request.issue_date,
            due_date=request.due_date,
            payment_terms=request.payment_terms,
            notes=request.notes,
            terms_and_conditions=request.terms_and_conditions,
            advance_payment_amount=request.advance_payment_amount,
            created_by=current_user["sub"]
        )
        
        invoice_dto = await use_case.execute_from_estimate(create_dto, current_user["sub"])
        return _invoice_dto_to_response(invoice_dto)
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error creating invoice from estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{invoice_id}", response_model=InvoiceResponseSchema)
async def get_invoice(
    invoice_id: uuid.UUID = Path(..., description="Invoice ID"),
    current_user: dict = Depends(get_current_user),
    invoice_repository = Depends(get_invoice_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get an invoice by ID.
    
    Retrieves detailed information about a specific invoice.
    Requires 'view_projects' permission.
    """
    try:
        invoice = await invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice with ID {invoice_id} not found"
            )
        
        return _invoice_dto_to_response(invoice)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error getting invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/", response_model=InvoiceListResponseSchema)
@router.get("", response_model=InvoiceListResponseSchema, operation_id="list_invoices_no_slash")
async def list_invoices(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    contact_id: Optional[uuid.UUID] = Query(None, description="Filter by contact ID"),
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by job ID"),
    overdue_only: bool = Query(False, description="Show only overdue invoices"),
    current_user: dict = Depends(get_current_user),
    invoice_repository = Depends(get_invoice_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    List invoices.
    
    Retrieves a paginated list of invoices for the current business.
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
        if overdue_only:
            filters["overdue_only"] = True
        
        invoices, total = await invoice_repository.list_with_pagination(
            business_id=business_id,
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        return InvoiceListResponse(
            invoices=[_invoice_dto_to_response(invoice) for invoice in invoices],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error listing invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{invoice_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    invoice_id: uuid.UUID = Path(..., description="Invoice ID"),
    request: ProcessPaymentSchema = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProcessPaymentUseCase = Depends(get_process_payment_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Process a payment for an invoice.
    
    Records a payment against an invoice and updates the invoice status.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Processing payment for invoice {invoice_id}")
    
    try:
        # Create payment DTO
        payment_dto = ProcessPaymentDTO(
            business_id=business_id,
            invoice_id=invoice_id,
            amount=request.amount,
            payment_method=PaymentMethod(request.payment_method.value),
            payment_date=request.payment_date,
            reference_number=request.reference_number,
            notes=request.notes,
            processed_by=current_user["sub"]
        )
        
        payment_result = await use_case.execute(payment_dto, current_user["sub"])
        
        return PaymentResponse(
            payment_id=payment_result.payment_id,
            invoice_id=invoice_id,
            amount=payment_result.amount,
            payment_method=payment_result.payment_method,
            payment_date=payment_result.payment_date,
            reference_number=payment_result.reference_number,
            notes=payment_result.notes,
            status=payment_result.status,
            processed_by=payment_result.processed_by,
            processed_at=payment_result.processed_at
        )
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error processing payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
