"""
Product-Service Association API Routes

Simple endpoints for product-service associations.
"""

from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional, List
import logging
from app.core.config import settings
from supabase import create_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/services/{business_id}/{service_id}/products")
async def get_service_products(
    business_id: str = Path(..., description="Business ID"),
    service_id: str = Path(..., description="Service ID"),
    association_type: Optional[str] = Query(None, description="Filter by association type"),
    featured_only: bool = Query(False, description="Show only featured products"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of products to return")
):
    """
    Get products associated with a specific service.
    
    Returns products that are linked to the service with their association context.
    """
    
    try:
        # Get Supabase client directly
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        
        # First, get the associations
        assoc_response = client.table("product_service_associations").select(
            "product_id, association_type, display_order, is_featured, service_discount_percentage, bundle_price, notes"
        ).eq("business_id", business_id).eq("service_id", service_id).order("display_order").limit(limit).execute()
        
        if not assoc_response.data:
            return []
        
        # Get product IDs
        product_ids = [assoc["product_id"] for assoc in assoc_response.data]
        
        # Fetch products
        products_response = client.table("products").select(
            "id, name, description, unit_price, sku, category, is_featured, is_active"
        ).in_("id", product_ids).execute()
        
        # Create a map of products by ID
        products_map = {p["id"]: p for p in products_response.data}
        
        # Combine association data with product data
        products = []
        for assoc in assoc_response.data:
            product_data = products_map.get(assoc["product_id"])
            if product_data:
                products.append({
                    "id": product_data["id"],
                    "name": product_data["name"],
                    "description": product_data["description"],
                    "price": float(product_data["unit_price"]) if product_data["unit_price"] else 0.0,
                    "sku": product_data["sku"],
                    "category": product_data["category"],
                    "featured": product_data["is_featured"],
                    "available": product_data["is_active"],
                    "service_context": {
                        "association_type": assoc["association_type"],
                        "is_featured": assoc["is_featured"],
                        "display_order": assoc["display_order"],
                        "service_discount_percentage": assoc["service_discount_percentage"],
                        "bundle_price": float(assoc["bundle_price"]) if assoc["bundle_price"] else None,
                        "notes": assoc["notes"]
                    }
                })
        
        return products
        
    except Exception as e:
        logger.error(f"Error getting service products: {str(e)}")
        return []


@router.get("/products/{business_id}/by-service")
async def get_products_by_service(
    business_id: str = Path(..., description="Business ID"),
    service_slug: Optional[str] = Query(None, description="Filter by service slug"),
    association_type: Optional[str] = Query(None, description="Filter by association type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return")
):
    """
    Get products filtered by service associations.
    
    This is the main endpoint for service-driven product filtering.
    """
    
    try:
        # Get Supabase client directly
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        
        # First, get the associations
        assoc_query = client.table("product_service_associations").select(
            "product_id, service_id, association_type, display_order, is_featured, service_discount_percentage, bundle_price, notes"
        ).eq("business_id", business_id)
        
        # Apply filters
        if association_type:
            assoc_query = assoc_query.eq("association_type", association_type)
            
        # Execute association query
        assoc_response = assoc_query.order("display_order").limit(limit).execute()
        
        if not assoc_response.data:
            return []
        
        # Get product IDs and service IDs
        product_ids = [assoc["product_id"] for assoc in assoc_response.data]
        service_ids = [assoc["service_id"] for assoc in assoc_response.data]
        
        # Fetch products
        products_response = client.table("products").select(
            "id, name, description, unit_price, sku, category, is_featured, is_active"
        ).in_("id", product_ids).execute()
        
        # Fetch services
        services_response = client.table("business_services").select(
            "id, canonical_slug, service_name"
        ).in_("id", service_ids).execute()
        
        # Create maps
        products_map = {p["id"]: p for p in products_response.data}
        services_map = {s["id"]: s for s in services_response.data}
        
        # Apply service slug filter if specified
        if service_slug:
            assoc_response.data = [
                assoc for assoc in assoc_response.data 
                if services_map.get(assoc["service_id"], {}).get("canonical_slug") == service_slug
            ]
        
        # Combine association data with product and service data
        products = []
        for assoc in assoc_response.data:
            product_data = products_map.get(assoc["product_id"])
            service_data = services_map.get(assoc["service_id"])
            if product_data and service_data:
                products.append({
                    "id": product_data["id"],
                    "name": product_data["name"],
                    "description": product_data["description"],
                    "price": float(product_data["unit_price"]) if product_data["unit_price"] else 0.0,
                    "sku": product_data["sku"],
                    "category": product_data["category"],
                    "featured": product_data["is_featured"],
                    "available": product_data["is_active"],
                    "service_context": {
                        "association_type": assoc["association_type"],
                        "service_slug": service_data["canonical_slug"],
                        "service_name": service_data["service_name"],
                        "is_featured": assoc["is_featured"],
                        "display_order": assoc["display_order"],
                        "service_discount_percentage": assoc["service_discount_percentage"],
                        "bundle_price": float(assoc["bundle_price"]) if assoc["bundle_price"] else None,
                        "notes": assoc["notes"]
                    }
                })
        
        return products
        
    except Exception as e:
        logger.error(f"Error getting products by service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")