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
    UpdateInvoiceSchema, ProcessPaymentSchema, InvoiceResponseSchema, InvoiceListResponseSchema,
    InvoiceStatusUpdateSchema, PaymentResponse, InvoiceLineItemSchema, PaymentSchema
)
from ...application.use_cases.invoice.create_invoice_use_case import CreateInvoiceUseCase
from ...application.use_cases.invoice.get_invoice_use_case import GetInvoiceUseCase
from ...application.use_cases.invoice.update_invoice_use_case import UpdateInvoiceUseCase
from ...application.use_cases.invoice.delete_invoice_use_case import DeleteInvoiceUseCase
from ...application.use_cases.invoice.list_invoices_use_case import ListInvoicesUseCase
from ...application.use_cases.invoice.search_invoices_use_case import SearchInvoicesUseCase
from ...application.use_cases.invoice.process_payment_use_case import ProcessPaymentUseCase
from ...application.dto.invoice_dto import (
    CreateInvoiceDTO, CreateInvoiceFromEstimateDTO, UpdateInvoiceDTO, ProcessPaymentDTO,
    InvoiceLineItemDTO, InvoiceDTO, InvoiceListFilters, InvoiceSearchCriteria
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_invoice_repository,
    get_create_invoice_use_case, get_get_invoice_use_case, get_update_invoice_use_case, 
    get_delete_invoice_use_case, get_list_invoices_use_case, get_search_invoices_use_case,
    get_process_payment_use_case
)
from ...domain.enums import InvoiceStatus, PaymentMethod, CurrencyCode
from ..schemas.activity_schemas import MessageResponse

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


def _invoice_dto_to_response_from_dto(invoice_dto) -> InvoiceResponseSchema:
    """Convert Invoice DTO to InvoiceResponse."""
    # Convert line items
    line_items_schemas = []
    for item in invoice_dto.line_items:
        line_items_schemas.append(InvoiceLineItemSchema(
            id=item.id,
            description=item.description,
            quantity=float(item.quantity) if item.quantity else 0.0,
            unit_price=float(item.unit_price) if item.unit_price else 0.0,
            unit=item.unit,
            category=item.category,
            discount_type=item.discount_type,
            discount_value=float(item.discount_value) if item.discount_value else 0.0,
            tax_rate=float(item.tax_rate) if item.tax_rate else 0.0,
            notes=item.notes,
            line_total=float(item.line_total) if item.line_total else 0.0,
            discount_amount=float(item.discount_amount) if item.discount_amount else 0.0,
            tax_amount=float(item.tax_amount) if item.tax_amount else 0.0,
            final_total=float(item.final_total) if item.final_total else 0.0
        ))
    
    # Convert payments
    payment_schemas = []
    for payment in invoice_dto.payments:
        payment_schemas.append(PaymentSchema(
            id=payment.id,
            amount=float(payment.amount) if payment.amount else 0.0,
            payment_date=payment.payment_date,
            payment_method=payment.payment_method,
            status=payment.status,
            reference=payment.reference,
            transaction_id=payment.transaction_id,
            notes=payment.notes,
            processed_by=payment.processed_by,
            refunded_amount=float(payment.refunded_amount) if payment.refunded_amount else 0.0,
            refund_date=payment.refund_date,
            refund_reason=payment.refund_reason
        ))
    
    # Calculate financial summary from line items
    subtotal = sum(float(item.line_total) if item.line_total else 0.0 for item in invoice_dto.line_items)
    tax_amount = sum(float(item.tax_amount) if item.tax_amount else 0.0 for item in invoice_dto.line_items)
    discount_amount = sum(float(item.discount_amount) if item.discount_amount else 0.0 for item in invoice_dto.line_items)
    
    # Add overall discount if any
    if invoice_dto.overall_discount_type != "none" and invoice_dto.overall_discount_value:
        if invoice_dto.overall_discount_type == "percentage":
            overall_discount = subtotal * (float(invoice_dto.overall_discount_value) / 100.0)
        else:  # fixed amount
            overall_discount = float(invoice_dto.overall_discount_value)
        discount_amount += overall_discount
    
    total_amount = float(invoice_dto.total_amount) if invoice_dto.total_amount else 0.0
    paid_amount = float(invoice_dto.total_payments) if invoice_dto.total_payments else 0.0
    balance_due = float(invoice_dto.balance_due) if invoice_dto.balance_due else 0.0
    
    # Calculate days overdue
    days_overdue = 0
    if invoice_dto.due_date and invoice_dto.is_overdue:
        from datetime import date
        days_overdue = (date.today() - invoice_dto.due_date).days if invoice_dto.due_date < date.today() else 0
    
    return InvoiceResponseSchema(
        id=invoice_dto.id,
        business_id=invoice_dto.business_id,
        invoice_number=invoice_dto.invoice_number,
        status=invoice_dto.status,
        client_id=invoice_dto.client_id,
        client_name=invoice_dto.client_name,
        client_email=invoice_dto.client_email,
        client_phone=invoice_dto.client_phone,
        client_address=invoice_dto.client_address.to_dict() if invoice_dto.client_address else None,
        title=invoice_dto.title,
        description=invoice_dto.description,
        line_items=line_items_schemas,
        currency=invoice_dto.currency,
        tax_rate=float(invoice_dto.tax_rate) if invoice_dto.tax_rate else 0.0,
        tax_type=invoice_dto.tax_type,
        overall_discount_type=invoice_dto.overall_discount_type,
        overall_discount_value=float(invoice_dto.overall_discount_value) if invoice_dto.overall_discount_value else 0.0,
        payments=payment_schemas,
        template_id=invoice_dto.template_id,
        template_data=invoice_dto.template_data or {},
        estimate_id=invoice_dto.estimate_id,
        project_id=invoice_dto.project_id,
        job_id=invoice_dto.job_id,
        contact_id=invoice_dto.contact_id,
        tags=invoice_dto.tags or [],
        custom_fields=invoice_dto.custom_fields or {},
        internal_notes=invoice_dto.internal_notes,
        created_by=invoice_dto.created_by,
        created_date=invoice_dto.created_date,
        last_modified=invoice_dto.last_modified,
        sent_date=invoice_dto.sent_date,
        viewed_date=invoice_dto.viewed_date,
        due_date=invoice_dto.due_date,
        paid_date=invoice_dto.paid_date,
        financial_summary={
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "balance_due": balance_due,
        },
        status_info={
            "is_paid": invoice_dto.is_paid if invoice_dto.is_paid is not None else False,
            "is_overdue": invoice_dto.is_overdue if invoice_dto.is_overdue is not None else False,
            "days_overdue": days_overdue,
            "can_be_paid": balance_due > 0 and invoice_dto.status not in ['paid', 'cancelled', 'void'],
            "can_be_voided": invoice_dto.status in ['draft', 'sent'],
            "payment_status": "paid" if (invoice_dto.is_paid if invoice_dto.is_paid is not None else False) else ("partially_paid" if paid_amount > 0 else "unpaid")
        }
    )


def _invoice_dto_to_response(invoice) -> InvoiceResponseSchema:
    """Convert Invoice entity to InvoiceResponse."""
    return InvoiceResponseSchema(
        id=invoice.id,
        business_id=invoice.business_id,
        invoice_number=invoice.invoice_number,
        status=invoice.status.value if hasattr(invoice.status, 'value') else str(invoice.status),
        client_id=invoice.client_id,
        client_name=invoice.client_name,
        client_email=invoice.client_email,
        client_phone=invoice.client_phone,
        client_address=invoice.client_address.to_dict() if invoice.client_address else None,
        title=invoice.title,
        description=invoice.description,
        line_items=[],  # TODO: Convert line items properly
        currency=invoice.currency.value if hasattr(invoice.currency, 'value') else str(invoice.currency),
        tax_rate=invoice.tax_rate,
        tax_type=invoice.tax_type.value if hasattr(invoice.tax_type, 'value') else str(invoice.tax_type),
        overall_discount_type=invoice.overall_discount_type.value if hasattr(invoice.overall_discount_type, 'value') else str(invoice.overall_discount_type),
        overall_discount_value=invoice.overall_discount_value,
        payments=[],  # TODO: Convert payments properly
        template_id=invoice.template_id,
        template_data=invoice.template_data or {},
        estimate_id=invoice.estimate_id,
        project_id=invoice.project_id,
        job_id=invoice.job_id,
        contact_id=invoice.contact_id,
        tags=invoice.tags or [],
        custom_fields=invoice.custom_fields or {},
        internal_notes=invoice.internal_notes,
        created_by=invoice.created_by,
        created_date=invoice.created_date,
        last_modified=invoice.last_modified,
        sent_date=invoice.sent_date,
        viewed_date=invoice.viewed_date,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        financial_summary={
            "subtotal": float(invoice.get_line_items_subtotal()) if hasattr(invoice, 'get_line_items_subtotal') else 0.0,
            "tax_amount": float(invoice.get_tax_amount()) if hasattr(invoice, 'get_tax_amount') else 0.0,
            "discount_amount": float(invoice.get_line_items_discount_total() + invoice.get_overall_discount_amount()) if hasattr(invoice, 'get_line_items_discount_total') else 0.0,
            "total_amount": float(invoice.get_total_amount()) if hasattr(invoice, 'get_total_amount') else 0.0,
            "amount_paid": float(invoice.get_total_payments()) if hasattr(invoice, 'get_total_payments') else 0.0,
            "amount_due": float(invoice.get_balance_due()) if hasattr(invoice, 'get_balance_due') else 0.0,
        },
        status_info={
            "is_paid": invoice.is_paid() if hasattr(invoice, 'is_paid') else False,
            "is_overdue": invoice.is_overdue() if hasattr(invoice, 'is_overdue') else False,
            "days_overdue": 0,  # TODO: Calculate days overdue
        }
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
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: GetInvoiceUseCase = Depends(get_get_invoice_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get an invoice by ID.
    
    Retrieves detailed information about a specific invoice.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Getting invoice {invoice_id} for business {business_id}")
    
    try:
        invoice_dto = await use_case.execute(invoice_id, current_user["sub"], business_id)
        return _invoice_dto_to_response_from_dto(invoice_dto)
        
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error getting invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{invoice_id}", response_model=InvoiceResponseSchema)
async def update_invoice(
    invoice_id: uuid.UUID = Path(..., description="Invoice ID"),
    request: UpdateInvoiceSchema = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: UpdateInvoiceUseCase = Depends(get_update_invoice_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Update an invoice.
    
    Updates an existing invoice with the provided information.
    Only draft invoices can be fully updated.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Starting invoice update for invoice {invoice_id}")
    
    try:
        # Convert line items if provided
        line_items = None
        if request.line_items is not None:
            line_items = []
            for item in request.line_items:
                line_items.append(InvoiceLineItemDTO(
                    id=item.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    unit=item.unit,
                    category=item.category,
                    discount_type=item.discount_type,
                    discount_value=item.discount_value,
                    tax_rate=item.tax_rate,
                    notes=item.notes
                ))
        
        # Create update DTO
        update_dto = UpdateInvoiceDTO(
            invoice_id=invoice_id,
            business_id=business_id,
            title=request.title,
            description=request.description,
            line_items=line_items,
            currency=request.currency,
            tax_rate=request.tax_rate,
            tax_type=request.tax_type,
            overall_discount_type=request.overall_discount_type,
            overall_discount_value=request.overall_discount_value,
            template_id=request.template_id,
            template_data=request.template_data,
            tags=request.tags,
            custom_fields=request.custom_fields,
            internal_notes=request.internal_notes,
            due_date=request.due_date,
            payment_net_days=request.payment_net_days,
            early_payment_discount_percentage=request.early_payment_discount_percentage,
            early_payment_discount_days=request.early_payment_discount_days,
            late_fee_percentage=request.late_fee_percentage,
            late_fee_grace_days=request.late_fee_grace_days,
            payment_instructions=request.payment_instructions,
            updated_by=current_user["sub"]
        )
        
        # Execute the use case
        updated_invoice_dto = await use_case.execute(update_dto, current_user["sub"])
        return _invoice_dto_to_response_from_dto(updated_invoice_dto)
        
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error updating invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{invoice_id}", response_model=MessageResponse)
async def delete_invoice(
    invoice_id: uuid.UUID = Path(..., description="Invoice ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: DeleteInvoiceUseCase = Depends(get_delete_invoice_use_case),
    _: bool = Depends(require_delete_projects_dep)
):
    """
    Delete an invoice.
    
    Deletes an invoice. Only draft invoices can be deleted.
    Requires 'delete_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Starting invoice deletion for invoice {invoice_id}")
    
    try:
        # Execute the use case
        result = await use_case.execute(invoice_id, business_id, current_user["sub"])
        return MessageResponse(message=result["message"])
        
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error deleting invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=InvoiceListResponseSchema)
@router.get("", response_model=InvoiceListResponseSchema, operation_id="list_invoices_no_slash")
async def list_invoices(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    invoice_status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    contact_id: Optional[uuid.UUID] = Query(None, description="Filter by contact ID"),
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by job ID"),
    overdue_only: bool = Query(False, description="Show only overdue invoices"),
    current_user: dict = Depends(get_current_user),
    use_case: ListInvoicesUseCase = Depends(get_list_invoices_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    List invoices.
    
    Retrieves a paginated list of invoices for the current business.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Listing invoices for business {business_id}")
    
    try:
        # Create filters DTO
        filters = InvoiceListFilters(
            status=invoice_status.value if invoice_status else None,
            contact_id=contact_id,
            project_id=project_id,
            job_id=job_id,
            overdue_only=overdue_only
        )
        
        result = await use_case.execute(
            business_id=business_id,
            user_id=current_user["sub"],
            filters=filters,
            skip=skip,
            limit=limit
        )
        
        return InvoiceListResponseSchema(
            invoices=[_invoice_dto_to_response_from_dto(invoice_dto) for invoice_dto in result["invoices"]],
            total_count=result["total_count"],
            page=skip // limit + 1,
            per_page=limit,
            has_next=result["has_next"],
            has_prev=result["has_previous"]
        )
        
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error listing invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
            amount=request.amount,
            payment_method=request.payment_method.value,
            payment_date=request.payment_date,
            reference=request.reference_number,
            notes=request.notes
        )
        
        payment_result = await use_case.execute(invoice_id, payment_dto, current_user["sub"], business_id)
        
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


@router.post("/search", response_model=InvoiceListResponseSchema)
async def search_invoices(
    request: InvoiceSearchSchema,
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_user),
    use_case: SearchInvoicesUseCase = Depends(get_search_invoices_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Search invoices with advanced criteria.
    
    Performs advanced search on invoices with multiple filter options.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 InvoiceAPI: Searching invoices for business {business_id}")
    
    try:
        # Create search criteria DTO
        search_criteria = InvoiceSearchCriteria(
            search_text=request.search_text,
            statuses=[status.value for status in request.statuses] if request.statuses else [],
            contact_ids=request.contact_ids,
            project_ids=request.project_ids,
            job_ids=request.job_ids,
            min_amount=request.min_amount,
            max_amount=request.max_amount,
            date_from=request.date_from,
            date_to=request.date_to,
            tags=request.tags,
            created_by=request.created_by,
            overdue_only=request.overdue_only,
            paid_only=request.paid_only
        )
        
        result = await use_case.execute(
            business_id=business_id,
            user_id=current_user["sub"],
            search_criteria=search_criteria,
            skip=skip,
            limit=limit
        )
        
        return InvoiceListResponseSchema(
            invoices=[_invoice_dto_to_response_from_dto(invoice_dto) for invoice_dto in result["invoices"]],
            total_count=result["total_count"],
            page=skip // limit + 1,
            per_page=limit,
            has_next=result["has_next"],
            has_prev=result["has_previous"]
        )
        
    except Exception as e:
        logger.error(f"❌ InvoiceAPI: Error searching invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
