"""
Suppliers API Routes

FastAPI routes for supplier management with comprehensive CRUD operations,
search functionality, and supplier relationship management.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, get_business_context
from app.infrastructure.config.dependency_injection import (
    get_supplier_repository
)
from app.domain.repositories.supplier_repository import SupplierRepository
from app.domain.entities.supplier import Supplier, SupplierContact, PaymentTerms
from app.domain.entities.product_enums.enums import SupplierStatus
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, BusinessRuleViolationError
)
from app.application.exceptions.application_exceptions import ValidationError
from app.domain.value_objects.address import Address

logger = logging.getLogger(__name__)

# Request/Response Schemas
class SupplierContactSchema(BaseModel):
    """Schema for supplier contact information."""
    name: str = Field(..., min_length=1, max_length=200)
    title: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    is_primary: bool = Field(default=False)

class PaymentTermsSchema(BaseModel):
    """Schema for payment terms."""
    payment_days: int = Field(default=30, ge=0, le=365)
    early_discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    early_discount_days: Optional[int] = Field(None, ge=0, le=365)
    late_fee_percentage: Optional[float] = Field(None, ge=0, le=100)

class AddressSchema(BaseModel):
    """Schema for address information."""
    street_address: str = Field(..., min_length=1, max_length=200)
    street_address_2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)

class CreateSupplierSchema(BaseModel):
    """Schema for creating a new supplier."""
    name: str = Field(..., min_length=1, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    supplier_code: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    is_preferred: bool = Field(default=False)
    
    # Contact information
    contacts: List[SupplierContactSchema] = Field(default_factory=list)
    primary_email: Optional[str] = Field(None, max_length=255)
    primary_phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=200)
    
    # Address information
    billing_address: Optional[AddressSchema] = None
    shipping_address: Optional[AddressSchema] = None
    
    # Business details
    tax_id: Optional[str] = Field(None, max_length=50)
    business_registration: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    
    # Payment terms
    payment_terms: Optional[PaymentTermsSchema] = None
    
    # Operational details
    lead_time_days: Optional[int] = Field(None, ge=0)
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    shipping_terms: Optional[str] = Field(None, max_length=100)
    
    # Notes
    notes: Optional[str] = Field(None, max_length=2000)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    tags: List[str] = Field(default_factory=list)

class UpdateSupplierSchema(BaseModel):
    """Schema for updating an existing supplier."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    supplier_code: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    is_preferred: Optional[bool] = None
    status: Optional[SupplierStatus] = None
    
    # Contact information
    contacts: Optional[List[SupplierContactSchema]] = None
    primary_email: Optional[str] = Field(None, max_length=255)
    primary_phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=200)
    
    # Address information
    billing_address: Optional[AddressSchema] = None
    shipping_address: Optional[AddressSchema] = None
    
    # Business details
    tax_id: Optional[str] = Field(None, max_length=50)
    business_registration: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    
    # Payment terms
    payment_terms: Optional[PaymentTermsSchema] = None
    
    # Operational details
    lead_time_days: Optional[int] = Field(None, ge=0)
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    shipping_terms: Optional[str] = Field(None, max_length=100)
    
    # Notes
    notes: Optional[str] = Field(None, max_length=2000)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = None

class SupplierResponseSchema(BaseModel):
    """Schema for supplier response."""
    id: uuid.UUID
    business_id: uuid.UUID
    name: str
    display_name: Optional[str]
    supplier_code: Optional[str]
    status: str
    category: Optional[str]
    is_preferred: bool
    
    # Contact information
    contacts: List[Dict[str, Any]]
    primary_email: Optional[str]
    primary_phone: Optional[str]
    website: Optional[str]
    
    # Address information
    billing_address: Optional[Dict[str, Any]]
    shipping_address: Optional[Dict[str, Any]]
    
    # Business details
    tax_id: Optional[str]
    business_registration: Optional[str]
    industry: Optional[str]
    
    # Payment terms
    payment_terms: Dict[str, Any]
    
    # Performance metrics
    performance: Dict[str, Any]
    
    # Operational details
    lead_time_days: Optional[int]
    minimum_order_amount: Optional[float]
    shipping_terms: Optional[str]
    
    # Notes
    notes: Optional[str]
    internal_notes: Optional[str]
    tags: List[str]
    
    # Metadata
    created_by: str
    created_date: str
    last_modified: str
    last_contact_date: Optional[str]

    class Config:
        from_attributes = True

class SupplierListResponseSchema(BaseModel):
    """Schema for supplier list response."""
    suppliers: List[SupplierResponseSchema]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

class SupplierSearchSchema(BaseModel):
    """Schema for supplier search parameters."""
    query: Optional[str] = Field(None, max_length=200)
    status: Optional[SupplierStatus] = None
    category: Optional[str] = Field(None, max_length=100)
    is_preferred: Optional[bool] = None
    country: Optional[str] = Field(None, max_length=100)
    has_active_orders: Optional[bool] = None

# API Router
router = APIRouter()

# Helper Functions
def _convert_address_schema_to_address(address_schema: Optional[AddressSchema]) -> Optional[Address]:
    """Convert address schema to domain Address value object."""
    if not address_schema:
        return None
    
    return Address(
        street_address=address_schema.street_address,
        street_address_2=address_schema.street_address_2,
        city=address_schema.city,
        state=address_schema.state,
        postal_code=address_schema.postal_code,
        country=address_schema.country
    )

def _convert_contacts_schema_to_contacts(contacts_schema: List[SupplierContactSchema]) -> List[SupplierContact]:
    """Convert contact schemas to domain SupplierContact entities."""
    contacts = []
    for contact_schema in contacts_schema:
        contact = SupplierContact(
            name=contact_schema.name,
            title=contact_schema.title,
            email=contact_schema.email,
            phone=contact_schema.phone,
            mobile=contact_schema.mobile,
            is_primary=contact_schema.is_primary
        )
        contacts.append(contact)
    return contacts

def _convert_payment_terms_schema_to_payment_terms(payment_terms_schema: Optional[PaymentTermsSchema]) -> PaymentTerms:
    """Convert payment terms schema to domain PaymentTerms entity."""
    if not payment_terms_schema:
        return PaymentTerms()
    
    return PaymentTerms(
        payment_days=payment_terms_schema.payment_days,
        early_discount_percentage=payment_terms_schema.early_discount_percentage or 0,
        early_discount_days=payment_terms_schema.early_discount_days or 0,
        late_fee_percentage=payment_terms_schema.late_fee_percentage or 0
    )

def _convert_supplier_to_response(supplier: Supplier) -> SupplierResponseSchema:
    """Convert supplier domain entity to response schema."""
    return SupplierResponseSchema(
        id=supplier.id,
        business_id=supplier.business_id,
        name=supplier.name,
        display_name=supplier.display_name,
        supplier_code=supplier.supplier_code,
        status=supplier.status.value,
        category=supplier.category,
        is_preferred=supplier.is_preferred,
        contacts=[contact.to_dict() for contact in supplier.contacts],
        primary_email=supplier.primary_email,
        primary_phone=supplier.primary_phone,
        website=supplier.website,
        billing_address=supplier.billing_address.to_dict() if supplier.billing_address else None,
        shipping_address=supplier.shipping_address.to_dict() if supplier.shipping_address else None,
        tax_id=supplier.tax_id,
        business_registration=supplier.business_registration,
        industry=supplier.industry,
        payment_terms=supplier.payment_terms.to_dict(),
        performance=supplier.performance.to_dict(),
        lead_time_days=supplier.lead_time_days,
        minimum_order_amount=float(supplier.minimum_order_amount) if supplier.minimum_order_amount else None,
        shipping_terms=supplier.shipping_terms,
        notes=supplier.notes,
        internal_notes=supplier.internal_notes,
        tags=supplier.tags,
        created_by=supplier.created_by,
        created_date=supplier.created_date.isoformat(),
        last_modified=supplier.last_modified.isoformat(),
        last_contact_date=supplier.last_contact_date.isoformat() if supplier.last_contact_date else None
    )

# API Endpoints

@router.post(
    "/",
    response_model=SupplierResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Supplier",
    description="Create a new supplier with comprehensive information"
)
async def create_supplier(
    supplier_data: CreateSupplierSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Create a new supplier."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Creating supplier for business {business_id} by user {user_id}")
        
        # Convert schemas to domain entities
        contacts = _convert_contacts_schema_to_contacts(supplier_data.contacts)
        billing_address = _convert_address_schema_to_address(supplier_data.billing_address)
        shipping_address = _convert_address_schema_to_address(supplier_data.shipping_address)
        payment_terms = _convert_payment_terms_schema_to_payment_terms(supplier_data.payment_terms)
        
        # Create supplier domain entity
        supplier = Supplier(
            id=uuid.uuid4(),
            business_id=business_id,
            name=supplier_data.name,
            display_name=supplier_data.display_name,
            supplier_code=supplier_data.supplier_code,
            category=supplier_data.category,
            is_preferred=supplier_data.is_preferred,
            contacts=contacts,
            primary_email=supplier_data.primary_email,
            primary_phone=supplier_data.primary_phone,
            website=supplier_data.website,
            billing_address=billing_address,
            shipping_address=shipping_address,
            tax_id=supplier_data.tax_id,
            business_registration=supplier_data.business_registration,
            industry=supplier_data.industry,
            payment_terms=payment_terms,
            lead_time_days=supplier_data.lead_time_days,
            minimum_order_amount=supplier_data.minimum_order_amount,
            shipping_terms=supplier_data.shipping_terms,
            notes=supplier_data.notes,
            internal_notes=supplier_data.internal_notes,
            tags=supplier_data.tags,
            created_by=user_id
        )
        
        # Save supplier
        created_supplier = await supplier_repository.create(supplier)
        
        logger.info(f"Successfully created supplier {created_supplier.id}")
        return _convert_supplier_to_response(created_supplier)
        
    except DuplicateEntityError as e:
        logger.warning(f"Duplicate supplier error: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        logger.warning(f"Validation error creating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create supplier"
        )

@router.get(
    "/",
    response_model=SupplierListResponseSchema,
    summary="List Suppliers",
    description="Get paginated list of suppliers with optional filtering"
)
async def list_suppliers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    status: Optional[SupplierStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_preferred: Optional[bool] = Query(None, description="Filter by preferred status"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Get paginated list of suppliers."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Listing suppliers for business {business_id}")
        
        offset = (page - 1) * page_size
        
        if search:
            suppliers = await supplier_repository.search_suppliers(
                business_id=business_id,
                query=search,
                status=status,
                limit=page_size,
                offset=offset
            )
        else:
            suppliers = await supplier_repository.list_by_business(
                business_id=business_id,
                status=status,
                limit=page_size,
                offset=offset
            )
        
        # Get total count for pagination
        total_count = await supplier_repository.count_suppliers(business_id, status)
        
        supplier_responses = [_convert_supplier_to_response(supplier) for supplier in suppliers]
        
        return SupplierListResponseSchema(
            suppliers=supplier_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list suppliers"
        )

@router.get(
    "/{supplier_id}",
    response_model=SupplierResponseSchema,
    summary="Get Supplier",
    description="Get supplier details by ID"
)
async def get_supplier(
    supplier_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Get supplier by ID."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Getting supplier {supplier_id} for business {business_id}")
        
        supplier = await supplier_repository.get_by_id(business_id, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier {supplier_id} not found"
            )
        
        return _convert_supplier_to_response(supplier)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get supplier"
        )

@router.put(
    "/{supplier_id}",
    response_model=SupplierResponseSchema,
    summary="Update Supplier",
    description="Update supplier information"
)
async def update_supplier(
    supplier_id: uuid.UUID,
    supplier_data: UpdateSupplierSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Update supplier."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Updating supplier {supplier_id} for business {business_id}")
        
        # Get existing supplier
        supplier = await supplier_repository.get_by_id(business_id, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier {supplier_id} not found"
            )
        
        # Update fields if provided
        if supplier_data.name is not None:
            supplier.name = supplier_data.name
        if supplier_data.display_name is not None:
            supplier.display_name = supplier_data.display_name
        if supplier_data.supplier_code is not None:
            supplier.supplier_code = supplier_data.supplier_code
        if supplier_data.category is not None:
            supplier.category = supplier_data.category
        if supplier_data.is_preferred is not None:
            supplier.is_preferred = supplier_data.is_preferred
        if supplier_data.status is not None:
            supplier.status = supplier_data.status
        
        # Update contact information
        if supplier_data.contacts is not None:
            supplier.contacts = _convert_contacts_schema_to_contacts(supplier_data.contacts)
        if supplier_data.primary_email is not None:
            supplier.primary_email = supplier_data.primary_email
        if supplier_data.primary_phone is not None:
            supplier.primary_phone = supplier_data.primary_phone
        if supplier_data.website is not None:
            supplier.website = supplier_data.website
        
        # Update addresses
        if supplier_data.billing_address is not None:
            supplier.billing_address = _convert_address_schema_to_address(supplier_data.billing_address)
        if supplier_data.shipping_address is not None:
            supplier.shipping_address = _convert_address_schema_to_address(supplier_data.shipping_address)
        
        # Update business details
        if supplier_data.tax_id is not None:
            supplier.tax_id = supplier_data.tax_id
        if supplier_data.business_registration is not None:
            supplier.business_registration = supplier_data.business_registration
        if supplier_data.industry is not None:
            supplier.industry = supplier_data.industry
        
        # Update payment terms
        if supplier_data.payment_terms is not None:
            supplier.payment_terms = _convert_payment_terms_schema_to_payment_terms(supplier_data.payment_terms)
        
        # Update operational details
        if supplier_data.lead_time_days is not None:
            supplier.lead_time_days = supplier_data.lead_time_days
        if supplier_data.minimum_order_amount is not None:
            supplier.minimum_order_amount = supplier_data.minimum_order_amount
        if supplier_data.shipping_terms is not None:
            supplier.shipping_terms = supplier_data.shipping_terms
        
        # Update notes
        if supplier_data.notes is not None:
            supplier.notes = supplier_data.notes
        if supplier_data.internal_notes is not None:
            supplier.internal_notes = supplier_data.internal_notes
        if supplier_data.tags is not None:
            supplier.tags = supplier_data.tags
        
        # Save updated supplier
        updated_supplier = await supplier_repository.update(supplier)
        
        logger.info(f"Successfully updated supplier {supplier_id}")
        return _convert_supplier_to_response(updated_supplier)
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error updating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update supplier"
        )

@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Supplier",
    description="Delete supplier (soft delete)"
)
async def delete_supplier(
    supplier_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Delete supplier (soft delete)."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Deleting supplier {supplier_id} for business {business_id}")
        
        success = await supplier_repository.delete(business_id, supplier_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier {supplier_id} not found"
            )
        
        logger.info(f"Successfully deleted supplier {supplier_id}")
        
    except HTTPException:
        raise
    except BusinessRuleViolationError as e:
        logger.warning(f"Business rule violation deleting supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete supplier"
        )

@router.post(
    "/search",
    response_model=SupplierListResponseSchema,
    summary="Advanced Supplier Search",
    description="Advanced search for suppliers with multiple criteria"
)
async def search_suppliers(
    search_params: SupplierSearchSchema,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Advanced supplier search."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Searching suppliers for business {business_id}")
        
        offset = (page - 1) * page_size
        
        # Use advanced search if available
        try:
            filters = {
                "query": search_params.query,
                "status": search_params.status.value if search_params.status else None,
                "category": search_params.category,
                "is_preferred": search_params.is_preferred,
                "country": search_params.country,
                "has_active_orders": search_params.has_active_orders
            }
            
            # Remove None values
            filters = {k: v for k, v in filters.items() if v is not None}
            
            result = await supplier_repository.advanced_search(
                business_id=business_id,
                filters=filters,
                limit=page_size,
                offset=offset
            )
            
            suppliers = result.get("suppliers", [])
            total_count = result.get("total_count", 0)
            
        except AttributeError:
            # Fallback to basic search if advanced search not implemented
            if search_params.query:
                suppliers = await supplier_repository.search_suppliers(
                    business_id=business_id,
                    query=search_params.query,
                    status=search_params.status,
                    limit=page_size,
                    offset=offset
                )
            else:
                suppliers = await supplier_repository.list_by_business(
                    business_id=business_id,
                    status=search_params.status,
                    limit=page_size,
                    offset=offset
                )
            
            total_count = await supplier_repository.count_suppliers(business_id, search_params.status)
        
        supplier_responses = [_convert_supplier_to_response(supplier) for supplier in suppliers]
        
        return SupplierListResponseSchema(
            suppliers=supplier_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error searching suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search suppliers"
        )

@router.get(
    "/{supplier_id}/performance",
    summary="Get Supplier Performance",
    description="Get comprehensive performance metrics for a supplier"
)
async def get_supplier_performance(
    supplier_id: uuid.UUID,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Get supplier performance metrics."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Getting performance for supplier {supplier_id}")
        
        # Get supplier analytics
        analytics = await supplier_repository.get_supplier_analytics(
            business_id=business_id,
            supplier_id=supplier_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "supplier_id": supplier_id,
            "analytics": analytics,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier {supplier_id} not found"
        )
    except Exception as e:
        logger.error(f"Error getting supplier performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get supplier performance"
        )

@router.get(
    "/{supplier_id}/orders",
    summary="Get Supplier Order History",
    description="Get purchase order history for a supplier"
)
async def get_supplier_orders(
    supplier_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    supplier_repository: SupplierRepository = Depends(get_supplier_repository)
):
    """Get supplier order history."""
    try:
        business_id = uuid.UUID(business_context["business_id"])
        user_id = current_user["sub"]
        logger.info(f"Getting order history for supplier {supplier_id}")
        
        offset = (page - 1) * page_size
        
        order_history = await supplier_repository.get_supplier_order_history(
            business_id=business_id,
            supplier_id=supplier_id,
            start_date=start_date,
            end_date=end_date,
            limit=page_size,
            offset=offset
        )
        
        return {
            "supplier_id": supplier_id,
            "orders": order_history,
            "page": page,
            "page_size": page_size,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier {supplier_id} not found"
        )
    except Exception as e:
        logger.error(f"Error getting supplier orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get supplier orders"
        )

 