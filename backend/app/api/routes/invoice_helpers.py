"""
Invoice Helper API Routes

Helper endpoints for creating invoice line items from products and services.
These endpoints help users quickly add items from their catalog to invoices.
"""

from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.api.deps import get_current_user, get_business_context
from app.infrastructure.database.repositories.supabase_service_template_repository import (
    SupabaseBusinessServiceRepository
)
from app.infrastructure.config.dependency_injection import get_product_repository
from app.core.db import get_supabase_client

router = APIRouter(prefix="/invoice-helpers", tags=["Invoice Helpers"])

# Dependencies
def get_business_service_repo(client=Depends(get_supabase_client)):
    return SupabaseBusinessServiceRepository(client)


class CatalogItemLineItem(BaseModel):
    """Line item data from catalog item (product or service)."""
    id: UUID  # Original product/service ID (for reference only)
    name: str
    description: str
    unit_price: float
    unit: str = "each"
    category: str = "General"
    item_type: str  # "product" or "service"


@router.get("/catalog-items/{item_id}/line-item", response_model=CatalogItemLineItem)
async def get_line_item_from_catalog(
    item_id: UUID,
    item_type: str = Query(..., regex="^(product|service)$", description="Type: 'product' or 'service'"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo),
    product_repository = Depends(get_product_repository)
):
    """
    Get line item data for a specific catalog item (product or service).
    
    This endpoint fetches current pricing and details from the catalog
    and formats them ready for invoice line items.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        if item_type == "product":
            # Get product details
            product = await product_repository.get_by_id(business_id, item_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            
            return CatalogItemLineItem(
                id=product.id,
                name=product.name,
                description=product.description or "",
                unit_price=float(product.unit_price),
                unit=str(product.unit_of_measure) if hasattr(product, 'unit_of_measure') else "each",
                category=getattr(product, 'category_name', 'Products'),
                item_type="product"
            )
            
        elif item_type == "service":
            # Get service details
            service = await business_service_repo.get_business_service_by_id(business_id, item_id)
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found"
                )
            
            return CatalogItemLineItem(
                id=service.id,
                name=service.name,
                description=service.description or "",
                unit_price=float(service.unit_price) if service.unit_price else 0.0,
                unit=service.unit_of_measure or "service",
                category=getattr(service, 'category_name', 'Services'),
                item_type="service"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get catalog item: {str(e)}"
        )


class BulkCatalogRequest(BaseModel):
    """Request for bulk catalog item line items."""
    items: List[dict]  # [{"id": "uuid", "type": "product|service"}]


@router.post("/catalog-items/bulk-line-items", response_model=List[CatalogItemLineItem])
async def get_bulk_line_items_from_catalog(
    request: BulkCatalogRequest,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo),
    product_repository = Depends(get_product_repository)
):
    """
    Get line item data for multiple catalog items at once.
    
    Useful for quickly adding multiple products/services to an invoice.
    """
    try:
        business_id = UUID(business_context["business_id"])
        line_items = []
        
        for item_request in request.items:
            item_id = UUID(item_request["id"])
            item_type = item_request["type"]
            
            if item_type == "product":
                product = await product_repository.get_by_id(business_id, item_id)
                if product:
                    line_items.append(CatalogItemLineItem(
                        id=product.id,
                        name=product.name,
                        description=product.description or "",
                        unit_price=float(product.unit_price),
                        unit=str(product.unit_of_measure) if hasattr(product, 'unit_of_measure') else "each",
                        category=getattr(product, 'category_name', 'Products'),
                        item_type="product"
                    ))
                    
            elif item_type == "service":
                service = await business_service_repo.get_business_service_by_id(business_id, item_id)
                if service:
                    line_items.append(CatalogItemLineItem(
                        id=service.id,
                        name=service.name,
                        description=service.description or "",
                        unit_price=float(service.unit_price) if service.unit_price else 0.0,
                        unit=service.unit_of_measure or "service",
                        category=getattr(service, 'category_name', 'Services'),
                        item_type="service"
                    ))
        
        return line_items
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bulk catalog items: {str(e)}"
        )


@router.get("/catalog/search", response_model=List[CatalogItemLineItem])
async def search_catalog_for_invoice(
    query: str = Query(..., min_length=2, description="Search term"),
    item_type: str = Query(None, regex="^(product|service|all)$", description="Filter by type"),
    limit: int = Query(20, le=50, description="Limit results"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo),
    product_repository = Depends(get_product_repository)
):
    """
    Search products and services for adding to invoices.
    
    Returns combined results from both product and service catalogs
    formatted ready for invoice line items.
    """
    try:
        business_id = UUID(business_context["business_id"])
        results = []
        
        # Search products if requested
        if item_type in [None, "all", "product"]:
            # TODO: Implement product search by query
            # For now, get first few products
            from ...application.dto.product_dto import ProductSearchCriteria
            criteria = ProductSearchCriteria(
                business_id=business_id,
                search_term=query,
                limit=limit//2 if item_type == "all" else limit
            )
            products, _ = await product_repository.search(criteria)
            
            for product in products:
                results.append(CatalogItemLineItem(
                    id=product.id,
                    name=product.name,
                    description=product.description or "",
                    unit_price=float(product.unit_price),
                    unit=str(product.unit_of_measure) if hasattr(product, 'unit_of_measure') else "each",
                    category=getattr(product, 'category_name', 'Products'),
                    item_type="product"
                ))
        
        # Search services if requested  
        if item_type in [None, "all", "service"]:
            # Get services that match query
            services = await business_service_repo.list_business_services(
                business_id=business_id,
                is_active=True,
                limit=limit//2 if item_type == "all" else limit
            )
            
            # Filter services by search term (basic text matching)
            for service in services:
                if query.lower() in service.name.lower() or (service.description and query.lower() in service.description.lower()):
                    results.append(CatalogItemLineItem(
                        id=service.id,
                        name=service.name,
                        description=service.description or "",
                        unit_price=float(service.unit_price) if service.unit_price else 0.0,
                        unit=service.unit_of_measure or "service",
                        category=getattr(service, 'category_name', 'Services'),
                        item_type="service"
                    ))
        
        # Sort by relevance (name matches first) and limit
        results = sorted(results, key=lambda x: (
            0 if query.lower() in x.name.lower() else 1,
            x.name.lower()
        ))[:limit]
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search catalog: {str(e)}"
        )
