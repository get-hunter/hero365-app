"""
Purchase Orders API Routes

FastAPI routes for purchase order management with comprehensive workflow operations
including creation, approval, sending, and receiving processes.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

from app.api.deps import get_current_user, get_business_context
from app.infrastructure.config.dependency_injection import (
    get_purchase_order_repository,
    get_supplier_repository,
    get_product_repository
)
from app.domain.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.repositories.supplier_repository import SupplierRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.entities.purchase_order import PurchaseOrder, PurchaseOrderLineItem
from app.domain.enums import PurchaseOrderStatus
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, BusinessRuleViolationError
)
from app.application.exceptions.application_exceptions import ValidationError
from app.application.use_cases.product.process_purchase_order_use_case import ProcessPurchaseOrderUseCase

logger = logging.getLogger(__name__)

# Request/Response Schemas
class PurchaseOrderLineItemSchema(BaseModel):
    """Schema for purchase order line item."""
    product_id: uuid.UUID
    quantity: float = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)

class CreatePurchaseOrderSchema(BaseModel):
    """Schema for creating a new purchase order."""
    supplier_id: uuid.UUID
    line_items: List[PurchaseOrderLineItemSchema] = Field(..., min_items=1)
    notes: Optional[str] = Field(None, max_length=2000)
    reference_number: Optional[str] = Field(None, max_length=100)
    expected_delivery_date: Optional[str] = Field(None, description="Expected delivery date (YYYY-MM-DD)")
    delivery_address: Optional[Dict[str, Any]] = None
    payment_terms_days: Optional[int] = Field(None, ge=0, le=365)

class ApprovePurchaseOrderSchema(BaseModel):
    """Schema for approving a purchase order."""
    approval_notes: Optional[str] = Field(None, max_length=500)

class ReceiveItemSchema(BaseModel):
    """Schema for receiving purchase order items."""
    line_item_id: uuid.UUID
    quantity_received: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=500)

class ReceivePurchaseOrderSchema(BaseModel):
    """Schema for receiving purchase order items."""
    received_items: List[ReceiveItemSchema] = Field(..., min_items=1)
    notes: Optional[str] = Field(None, max_length=2000)
    partial_receipt: bool = Field(default=False)

class PurchaseOrderResponseSchema(BaseModel):
    """Schema for purchase order response."""
    id: uuid.UUID
    business_id: uuid.UUID
    po_number: str
    supplier_id: uuid.UUID
    supplier_name: str
    status: str
    
    # Dates
    order_date: str
    expected_delivery_date: Optional[str]
    actual_delivery_date: Optional[str]
    
    # Financial information
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str
    
    # Line items
    line_items: List[Dict[str, Any]]
    
    # Additional information
    notes: Optional[str]
    internal_notes: Optional[str]
    reference_number: Optional[str]
    
    # Workflow information
    approved_by: Optional[str]
    approved_date: Optional[str]
    sent_date: Optional[str]
    received_date: Optional[str]
    
    # Status flags
    is_approved: bool
    is_sent: bool
    is_fully_received: bool
    is_partially_received: bool
    can_be_edited: bool
    can_be_approved: bool
    can_be_sent: bool
    
    # Metadata
    created_by: str
    created_date: str
    last_modified: str

    class Config:
        from_attributes = True

class PurchaseOrderListResponseSchema(BaseModel):
    """Schema for purchase order list response."""
    purchase_orders: List[PurchaseOrderResponseSchema]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

class PurchaseOrderSearchSchema(BaseModel):
    """Schema for purchase order search parameters."""
    status: Optional[PurchaseOrderStatus] = None
    supplier_id: Optional[uuid.UUID] = None
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    po_number: Optional[str] = Field(None, max_length=50)
    reference_number: Optional[str] = Field(None, max_length=100)

# API Router
router = APIRouter()

# Helper Functions
def _convert_purchase_order_to_response(po: PurchaseOrder) -> PurchaseOrderResponseSchema:
    """Convert purchase order domain entity to response schema."""
    return PurchaseOrderResponseSchema(
        id=po.id,
        business_id=po.business_id,
        po_number=po.po_number,
        supplier_id=po.supplier_id,
        supplier_name=po.supplier_name,
        status=po.status.value,
        order_date=po.order_date.isoformat() if hasattr(po.order_date, 'isoformat') else str(po.order_date),
        expected_delivery_date=po.expected_delivery_date.isoformat() if po.expected_delivery_date and hasattr(po.expected_delivery_date, 'isoformat') else str(po.expected_delivery_date) if po.expected_delivery_date else None,
        actual_delivery_date=po.actual_delivery_date.isoformat() if po.actual_delivery_date and hasattr(po.actual_delivery_date, 'isoformat') else str(po.actual_delivery_date) if po.actual_delivery_date else None,
        subtotal=float(po.subtotal),
        tax_amount=float(po.tax_amount),
        total_amount=float(po.total_amount),
        currency=po.currency.value if hasattr(po.currency, 'value') else str(po.currency),
        line_items=[item.to_dict() for item in po.line_items],
        notes=po.notes,
        internal_notes=po.internal_notes,
        reference_number=po.reference_number,
        approved_by=po.approved_by,
        approved_date=po.approved_date.isoformat() if po.approved_date else None,
        sent_date=po.sent_date.isoformat() if po.sent_date else None,
        received_date=po.actual_delivery_date.isoformat() if po.actual_delivery_date else None,
        is_approved=po.is_approved,
        is_sent=po.is_sent,
        is_fully_received=po.is_fully_received,
        is_partially_received=po.is_partially_received,
        can_be_edited=po.can_be_edited,
        can_be_approved=po.can_be_approved,
        can_be_sent=po.can_be_sent,
        created_by=po.created_by,
        created_date=po.created_date.isoformat(),
        last_modified=po.last_modified.isoformat()
    )

# API Endpoints

@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create Purchase Order",
    description="Create a new purchase order with line items"
)
async def create_purchase_order(
    po_data: CreatePurchaseOrderSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    product_repository: ProductRepository = Depends(get_product_repository),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Create a new purchase order."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Creating purchase order for business {business_id} by user {user_id}")
        
        # Create use case instance
        use_case = ProcessPurchaseOrderUseCase(
            purchase_order_repository=purchase_order_repository,
            product_repository=product_repository,
            supplier_repository=supplier_repository
        )
        
        # Convert line items to dict format expected by use case
        line_items = []
        for item in po_data.line_items:
            line_items.append({
                'product_id': str(item.product_id),
                'quantity': item.quantity,
                'unit_cost': item.unit_cost,
                'description': item.description or '',
                'discount_percentage': item.discount_percentage or 0,
                'tax_rate': item.tax_rate or 0
            })
        
        # Create purchase order
        result = await use_case.create_purchase_order(
            supplier_id=po_data.supplier_id,
            line_items=line_items,
            user_id=user_id,
            business_id=business_id,
            notes=po_data.notes,
            reference_number=po_data.reference_number
        )
        
        logger.info(f"Successfully created purchase order {result['purchase_order_id']}")
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error creating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase order"
        )

@router.get(
    "/",
    response_model=PurchaseOrderListResponseSchema,
    summary="List Purchase Orders",
    description="Get paginated list of purchase orders with optional filtering"
)
async def list_purchase_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    status: Optional[PurchaseOrderStatus] = Query(None, description="Filter by status"),
    supplier_id: Optional[uuid.UUID] = Query(None, description="Filter by supplier"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository)
):
    """Get paginated list of purchase orders."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Listing purchase orders for business {business_id}")
        
        offset = (page - 1) * page_size
        
        # Parse dates if provided
        start_datetime = datetime.fromisoformat(start_date) if start_date else None
        end_datetime = datetime.fromisoformat(end_date) if end_date else None
        
        purchase_orders = await purchase_order_repository.list_by_business(
            business_id=business_id,
            status=status,
            supplier_id=supplier_id,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=page_size,
            offset=offset
        )
        
        # Get total count for pagination
        total_count = await purchase_order_repository.count_by_business(
            business_id=business_id,
            status=status,
            supplier_id=supplier_id,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        po_responses = [_convert_purchase_order_to_response(po) for po in purchase_orders]
        
        return PurchaseOrderListResponseSchema(
            purchase_orders=po_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing purchase orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list purchase orders"
        )

@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponseSchema,
    summary="Get Purchase Order",
    description="Get purchase order details by ID"
)
async def get_purchase_order(
    purchase_order_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository)
):
    """Get purchase order by ID."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Getting purchase order {purchase_order_id} for business {business_id}")
        
        purchase_order = await purchase_order_repository.get_by_id(business_id, purchase_order_id)
        if not purchase_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase order {purchase_order_id} not found"
            )
        
        return _convert_purchase_order_to_response(purchase_order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get purchase order"
        )

@router.post(
    "/{purchase_order_id}/approve",
    response_model=Dict[str, Any],
    summary="Approve Purchase Order",
    description="Approve a purchase order to allow it to be sent"
)
async def approve_purchase_order(
    purchase_order_id: uuid.UUID,
    approval_data: ApprovePurchaseOrderSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    product_repository: ProductRepository = Depends(get_product_repository),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Approve a purchase order."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Approving purchase order {purchase_order_id} by user {user_id}")
        
        # Create use case instance
        use_case = ProcessPurchaseOrderUseCase(
            purchase_order_repository=purchase_order_repository,
            product_repository=product_repository,
            supplier_repository=supplier_repository
        )
        
        # Approve purchase order
        result = await use_case.approve_purchase_order(
            purchase_order_id=purchase_order_id,
            user_id=user_id,
            business_id=business_id,
            approval_notes=approval_data.approval_notes
        )
        
        logger.info(f"Successfully approved purchase order {purchase_order_id}")
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error approving purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BusinessRuleViolationError as e:
        logger.warning(f"Business rule violation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error approving purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve purchase order"
        )

@router.post(
    "/{purchase_order_id}/send",
    response_model=Dict[str, Any],
    summary="Send Purchase Order",
    description="Send approved purchase order to supplier"
)
async def send_purchase_order(
    purchase_order_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    product_repository: ProductRepository = Depends(get_product_repository),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Send purchase order to supplier."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Sending purchase order {purchase_order_id} by user {user_id}")
        
        # Create use case instance
        use_case = ProcessPurchaseOrderUseCase(
            purchase_order_repository=purchase_order_repository,
            product_repository=product_repository,
            supplier_repository=supplier_repository
        )
        
        # Send purchase order
        result = await use_case.send_purchase_order(
            purchase_order_id=purchase_order_id,
            user_id=user_id,
            business_id=business_id
        )
        
        logger.info(f"Successfully sent purchase order {purchase_order_id}")
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error sending purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BusinessRuleViolationError as e:
        logger.warning(f"Business rule violation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send purchase order"
        )

@router.post(
    "/{purchase_order_id}/receive",
    response_model=Dict[str, Any],
    summary="Receive Purchase Order Items",
    description="Record receipt of purchase order items and update inventory"
)
async def receive_purchase_order(
    purchase_order_id: uuid.UUID,
    receive_data: ReceivePurchaseOrderSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    product_repository: ProductRepository = Depends(get_product_repository),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Receive purchase order items."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Receiving items for purchase order {purchase_order_id} by user {user_id}")
        
        # Create use case instance
        use_case = ProcessPurchaseOrderUseCase(
            purchase_order_repository=purchase_order_repository,
            product_repository=product_repository,
            supplier_repository=supplier_repository
        )
        
        # Convert received items to expected format
        received_items = []
        for item in receive_data.received_items:
            received_items.append({
                'line_item_id': str(item.line_item_id),
                'quantity_received': item.quantity_received,
                'notes': item.notes or ''
            })
        
        # Receive purchase order items
        result = await use_case.receive_purchase_order(
            purchase_order_id=purchase_order_id,
            received_items=received_items,
            user_id=user_id,
            business_id=business_id,
            partial_receipt=receive_data.partial_receipt,
            notes=receive_data.notes
        )
        
        logger.info(f"Successfully received items for purchase order {purchase_order_id}")
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error receiving purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BusinessRuleViolationError as e:
        logger.warning(f"Business rule violation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error receiving purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to receive purchase order"
        )

@router.post(
    "/search",
    response_model=PurchaseOrderListResponseSchema,
    summary="Search Purchase Orders",
    description="Advanced search for purchase orders with multiple criteria"
)
async def search_purchase_orders(
    search_params: PurchaseOrderSearchSchema,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository)
):
    """Search purchase orders with advanced criteria."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Searching purchase orders for business {business_id}")
        
        offset = (page - 1) * page_size
        
        # Parse dates if provided
        start_datetime = datetime.fromisoformat(search_params.start_date) if search_params.start_date else None
        end_datetime = datetime.fromisoformat(search_params.end_date) if search_params.end_date else None
        
        # Use advanced search if available
        try:
            filters = {
                "status": search_params.status.value if search_params.status else None,
                "supplier_id": str(search_params.supplier_id) if search_params.supplier_id else None,
                "po_number": search_params.po_number,
                "reference_number": search_params.reference_number,
                "start_date": start_datetime,
                "end_date": end_datetime
            }
            
            # Remove None values
            filters = {k: v for k, v in filters.items() if v is not None}
            
            result = await purchase_order_repository.advanced_search(
                business_id=business_id,
                filters=filters,
                limit=page_size,
                offset=offset
            )
            
            purchase_orders = result.get("purchase_orders", [])
            total_count = result.get("total_count", 0)
            
        except AttributeError:
            # Fallback to basic search if advanced search not implemented
            purchase_orders = await purchase_order_repository.list_by_business(
                business_id=business_id,
                status=search_params.status,
                supplier_id=search_params.supplier_id,
                start_date=start_datetime,
                end_date=end_datetime,
                limit=page_size,
                offset=offset
            )
            
            total_count = await purchase_order_repository.count_by_business(
                business_id=business_id,
                status=search_params.status,
                supplier_id=search_params.supplier_id,
                start_date=start_datetime,
                end_date=end_datetime
            )
        
        po_responses = [_convert_purchase_order_to_response(po) for po in purchase_orders]
        
        return PurchaseOrderListResponseSchema(
            purchase_orders=po_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error searching purchase orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search purchase orders"
        )

@router.get(
    "/pending/approval",
    response_model=PurchaseOrderListResponseSchema,
    summary="Get Purchase Orders Pending Approval",
    description="Get purchase orders that require approval"
)
async def get_pending_approval_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository)
):
    """Get purchase orders pending approval."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Getting pending approval orders for business {business_id}")
        
        offset = (page - 1) * page_size
        
        purchase_orders = await purchase_order_repository.get_orders_pending_approval(
            business_id=business_id,
            limit=page_size,
            offset=offset
        )
        
        total_count = await purchase_order_repository.count_by_business(
            business_id=business_id,
            status=PurchaseOrderStatus.DRAFT
        )
        
        po_responses = [_convert_purchase_order_to_response(po) for po in purchase_orders]
        
        return PurchaseOrderListResponseSchema(
            purchase_orders=po_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error getting pending approval orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending approval orders"
        )

@router.get(
    "/pending/receipt",
    response_model=PurchaseOrderListResponseSchema,
    summary="Get Purchase Orders Pending Receipt",
    description="Get purchase orders that are pending receipt of items"
)
async def get_pending_receipt_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    overdue_only: bool = Query(False, description="Show only overdue orders"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    purchase_order_repository: PurchaseOrderRepository = Depends(get_purchase_order_repository)
):
    """Get purchase orders pending receipt."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Getting pending receipt orders for business {business_id}")
        
        if overdue_only:
            purchase_orders = await purchase_order_repository.get_overdue_orders(
                business_id=business_id
            )
            total_count = len(purchase_orders)
        else:
            purchase_orders = await purchase_order_repository.get_orders_pending_receipt(
                business_id=business_id,
                overdue_only=False
            )
            total_count = len(purchase_orders)
        
        # Apply pagination
        offset = (page - 1) * page_size
        paginated_orders = purchase_orders[offset:offset + page_size]
        
        po_responses = [_convert_purchase_order_to_response(po) for po in paginated_orders]
        
        return PurchaseOrderListResponseSchema(
            purchase_orders=po_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error getting pending receipt orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending receipt orders"
        )

 