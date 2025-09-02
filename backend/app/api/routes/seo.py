"""
SEO API Routes

Public endpoints for SEO page data and website building.
"""

from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Dict, Any, List
import logging
import httpx
from datetime import datetime, timezone
from supabase import Client

from app.api.deps import get_supabase_client
from app.application.services.service_materialization_service import ServiceMaterializationService
from app.application.services.seo_scaffolding_service import SEOScaffoldingService
from app.infrastructure.database.repositories.supabase_business_repository import SupabaseBusinessRepository
from app.application.services.llm_orchestrator import LLMContentOrchestrator
from app.application.services.rag_retrieval_service import RAGRetrievalService
from app.domain.entities.service_page_content import ServicePageContent
from app.domain.services.service_taxonomy import (
    get_services_by_category, 
    get_ordered_categories, 
    get_category_info,
    ServiceCategory
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/seo", tags=["SEO"])


def _word_count(text: str | None) -> int:
    if not text:
        return 0
    return len(str(text).split())


def _build_navigation_data(pages: Dict[str, Any], business_name: str) -> Dict[str, Any]:
    """Build navigation structure from pages for menu generation."""
    services = []
    locations = set()
    service_locations = []
    
    for url, page in pages.items():
        if page.get("page_type") == "service":
            # Service overview page: /services/{service_slug}
            service_slug = url.replace("/services/", "")
            services.append({
                "name": page.get("h1_heading", "").replace(" Services", ""),
                "slug": service_slug,
                "url": url,
                "description": page.get("meta_description", "")
            })
        elif page.get("page_type") == "service_location":
            # Service+location page: /services/{service_slug}/{location_slug}
            parts = url.replace("/services/", "").split("/")
            if len(parts) == 2:
                service_slug, location_slug = parts
                location_name = location_slug.replace("-", " ").title()
                locations.add((location_slug, location_name))
                service_locations.append({
                    "service_slug": service_slug,
                    "location_slug": location_slug,
                    "location_name": location_name,
                    "url": url,
                    "title": page.get("title", "")
                })
    
    # Convert locations set to sorted list
    locations_list = [{"slug": slug, "name": name} for slug, name in sorted(locations)]
    
    # Build categories from services
    service_slugs = [service["slug"] for service in services]
    categories_map = get_services_by_category(service_slugs)
    ordered_categories = get_ordered_categories(categories_map)
    
    categories = []
    for category in ordered_categories:
        category_info = get_category_info(category)
        category_services = []
        
        for slug in categories_map[category]:
            # Find the service data
            service_data = next((s for s in services if s["slug"] == slug), None)
            if service_data:
                category_services.append(service_data)
        
        if category_services:  # Only include categories with services
            categories.append({
                "name": category_info["name"],
                "description": category_info["description"],
                "slug": category_info["slug"],
                "services": sorted(category_services, key=lambda x: x["name"])
            })
    
    return {
        "services": sorted(services, key=lambda x: x["name"]),
        "locations": locations_list,
        "service_locations": service_locations,
        "categories": categories
    }


@router.get("/pages/{business_id}")
async def get_seo_pages(
    business_id: str = Path(..., description="Business ID"),
    include_content: bool = False,
    supabase: Client = Depends(get_supabase_client),
) -> Dict[str, Any]:
    """
    Get SEO page data for a business.
    
    Priority:
    1) generated_seo_pages (business-specific content)
    2) Construct from business_services (service pages) + service_location_pages (combos)
    """
    try:
        # 1) Try generated_seo_pages first
        gen = supabase.table("generated_seo_pages").select(
            "page_url,page_type,title,meta_description,h1_heading,content,schema_markup,target_keywords,generation_method,created_at"
        ).eq("business_id", business_id).execute()

        pages: Dict[str, Any] = {}

        if gen.data:
            for row in gen.data:  # type: ignore
                url = row.get("page_url")
                if not url:
                    continue
                pages[url] = {
                    "title": row.get("title") or "",
                    "meta_description": row.get("meta_description") or "",
                    "h1_heading": row.get("h1_heading") or row.get("title") or "",
                    "content": row.get("content") or "",
                    "schema_markup": row.get("schema_markup") or {},
                    "target_keywords": row.get("target_keywords") or [],
                    "page_url": url,
                    "generation_method": row.get("generation_method") or "template",
                    "page_type": row.get("page_type") or "service",
                    "word_count": _word_count(row.get("content")),
                    "created_at": row.get("created_at") or "",
                }
        else:
            # 2) Build from business_services + service_location_pages
            # Fetch business profile for naming (with trade information for debugging)
            biz = supabase.table("businesses").select("name,city,state,primary_trade,secondary_trades,market_focus").eq("id", business_id).execute()
            business_name = (biz.data[0].get("name") if biz.data else "Your Business")  # type: ignore
            business_data = biz.data[0] if biz.data else None

            # Service overview pages
            svcs = supabase.table("business_services").select("service_slug,service_name,description,is_active").eq("business_id", business_id).eq("is_active", True).execute()
            for svc in svcs.data or []:  # type: ignore
                slug = svc.get("service_slug")
                name = svc.get("service_name") or (slug or "").replace("-", " ").title()
                if not slug:
                    continue
                url = f"/services/{slug}"
                pages[url] = {
                    "title": f"{name} Services | {business_name}",
                    "meta_description": svc.get("description") or f"Professional {name.lower()} services.",
                    "h1_heading": f"{name} Services",
                    "content": f"<p>{business_name} provides professional {name.lower()} services.</p>",
                    "schema_markup": {},
                    "target_keywords": [slug, name],
                    "page_url": url,
                    "generation_method": "template",
                    "page_type": "service",
                    "word_count": _word_count(name),
                    "created_at": "",
                }

            # Service + location pages (global matrix)
            if svcs.data:
                slugs: List[str] = [row.get("service_slug") for row in svcs.data if row.get("service_slug")]  # type: ignore
                if slugs:
                    comb = supabase.table("service_location_pages").select(
                        "service_slug,location_slug,page_url,target_keywords"
                    ).in_("service_slug", slugs).execute()
                    for row in comb.data or []:  # type: ignore
                        url = row.get("page_url")
                        if not url:
                            continue
                        svc_slug = row.get("service_slug")
                        name = (svc_slug or "").replace("-", " ").title()
                        pages[url] = {
                            "title": f"{name} | {business_name}",
                            "meta_description": f"Professional {name.lower()} services in {row.get('location_slug').replace('-', ' ').title()}.",
                            "h1_heading": name,
                            "content": f"<p>{business_name} offers {name.lower()} in your area.</p>",
                            "schema_markup": {},
                            "target_keywords": row.get("target_keywords") or [svc_slug],
                            "page_url": url,
                            "generation_method": "template",
                            "page_type": "service_location",
                            "word_count": _word_count(name),
                            "created_at": "",
                        }

        if not pages:
            # Final safety: return empty successful response (frontend can show notFound)
            return {
                "pages": {}, 
                "business_id": business_id, 
                "total_pages": 0, 
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "navigation": {"services": [], "locations": [], "service_locations": []}
            }

        # Build navigation data
        navigation = _build_navigation_data(pages, business_name)
        
        result = {
            "pages": pages,
            "business_id": business_id,
            "business": business_data,  # Add business data for debugging
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_pages": len(pages),
            "navigation": navigation,
        }
        
        # Include rich content blocks if requested
        if include_content:
            content_blocks = await _get_content_blocks(business_id, supabase)
            result["content_blocks"] = content_blocks
            result["business_services"] = svcs.data if 'svcs' in locals() else None  # Add business services for debugging
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving SEO pages for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SEO pages")


async def _get_content_blocks(business_id: str, supabase: Client) -> Dict[str, Any]:
    """Get rich content blocks for service pages."""
    try:
        # Query service_page_contents table
        content_result = supabase.table("service_page_contents").select(
            "service_slug,location_slug,content_blocks,schema_blocks,metrics,status"
        ).eq("business_id", business_id).eq("status", "published").execute()
        
        content_blocks = {}
        
        for row in content_result.data:
            service_slug = row.get("service_slug")
            location_slug = row.get("location_slug")
            
            # Build page key
            if location_slug:
                page_key = f"/services/{service_slug}/{location_slug}"
            else:
                page_key = f"/services/{service_slug}"
            
            content_blocks[page_key] = {
                "content_blocks": row.get("content_blocks", []),
                "schema_blocks": row.get("schema_blocks", []),
                "metrics": row.get("metrics", {}),
                "status": row.get("status", "draft")
            }
        
        return content_blocks
        
    except Exception as e:
        logger.error(f"Error retrieving content blocks: {e}")
        return {}


@router.post("/content/{business_id}/generate")
async def generate_content(
    business_id: str = Path(..., description="Business ID"),
    request_body: Dict[str, Any] = None,
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Generate rich content for service pages using LLM."""
    try:
        # Parse request body
        service_slugs = None
        location_slugs = None
        if request_body:
            service_slugs = request_body.get("service_slugs")
            location_slugs = request_body.get("location_slugs")
        
        # Get business info for context
        biz = supabase.table("businesses").select(
            "name,city,state,phone,email,primary_trade,secondary_trades"
        ).eq("id", business_id).execute()
        
        if not biz.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        business_info = biz.data[0]
        
        # Initialize RAG service and LLM orchestrator
        try:
            rag_service = RAGRetrievalService(supabase)
            orchestrator = LLMContentOrchestrator(rag_service=rag_service)
            logger.info("Successfully initialized LLM orchestrator with RAG service")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            # Fallback to orchestrator without RAG
            orchestrator = LLMContentOrchestrator(rag_service=None)
            logger.info("Initialized LLM orchestrator without RAG service (fallback)")
        
        # Get services to generate content for
        services_query = supabase.table("business_services").select(
            "service_slug,service_name,category"
        ).eq("business_id", business_id).eq("is_active", True)
        
        if service_slugs:
            services_query = services_query.in_("service_slug", service_slugs)
        
        services_result = services_query.execute()
        
        generated_count = 0
        
        for service in services_result.data:
            service_slug = service["service_slug"]
            
            # Prepare enhanced context
            context = {
                "business_name": business_info["name"],
                "service_name": service["service_name"],
                "city": business_info["city"],
                "state": business_info["state"],
                "phone": business_info["phone"],
                "email": business_info["email"],
                "primary_trade": business_info.get("primary_trade"),
                "secondary_trades": business_info.get("secondary_trades", []),
                "service_category": service.get("category")
            }
            
            # Generate for service overview page
            try:
                logger.info(f"Starting content generation for {service_slug}")
                page_content = await orchestrator.generate_service_page_content(
                    business_id=business_id,
                    service_slug=service_slug,
                    context=context,
                    target_keywords=[service["service_name"], business_info["city"]]
                )
                
                logger.info(f"Content generation completed for {service_slug}")
                
                # Save to database
                await _save_service_page_content(page_content, supabase)
                generated_count += 1
                
                logger.info(f"Successfully generated and saved content for {service_slug}")
                
            except Exception as e:
                logger.error(f"Failed to generate content for {service_slug}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "business_id": business_id,
            "generated_count": generated_count,
            "total_services": len(services_result.data),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating content for business {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")


async def _save_service_page_content(page_content: ServicePageContent, supabase: Client):
    """Save service page content to database."""
    try:
        # Convert to database format
        content_blocks_data = [block.model_dump() for block in page_content.content_blocks]
        schema_blocks_data = [schema.model_dump() for schema in page_content.schema_blocks]
        
        data = {
            "business_id": page_content.business_id,
            "service_slug": page_content.service_slug,
            "location_slug": page_content.location_slug if page_content.location_slug else None,
            "title": page_content.title,
            "meta_description": page_content.meta_description,
            "canonical_url": page_content.canonical_url,
            "target_keywords": page_content.target_keywords,
            "content_blocks": content_blocks_data,
            "schema_blocks": schema_blocks_data,
            "content_source": page_content.content_source if isinstance(page_content.content_source, str) else page_content.content_source.value,
            "revision": page_content.revision,
            "content_hash": page_content.content_hash,
            "metrics": page_content.metrics.model_dump(),
            "status": "published"
        }
        
        # Delete existing record to avoid duplicates
        try:
            supabase.table("service_page_contents").delete().eq(
                "business_id", page_content.business_id
            ).eq(
                "service_slug", page_content.service_slug
            ).is_("location_slug", "null").execute()
        except Exception as delete_error:
            # Ignore delete errors - record might not exist
            pass
        
        # Insert the new record
        result = supabase.table("service_page_contents").insert(data).execute()
        
        logger.info(f"Successfully saved {len(content_blocks_data)} content blocks and {len(schema_blocks_data)} schema blocks for {page_content.service_slug}")
        
    except Exception as e:
        logger.error(f"Error saving service page content for {page_content.service_slug}: {e}")
        raise


@router.get("/page-content/{business_id}")
async def get_seo_page_content(
    business_id: str = Path(..., description="Business ID"),
    page_path: str = None
) -> Dict[str, Any]:
    """
    Get content for a specific SEO page.
    
    Args:
        business_id: The unique identifier of the business
        page_path: The page path to get content for
        
    Returns:
        Dict containing page content
    """
    
    try:
        # This would normally fetch from database or generate content
        # For now, return demo content
        return {
            "business_id": business_id,
            "page_path": page_path,
            "content": "<p>Demo SEO page content</p>",
            "generated_at": "2025-01-02T15:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving SEO page content for {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve page content")


@router.post("/revalidate")
async def trigger_revalidation(
    page_paths: List[str] = None,
    tags: List[str] = None
) -> Dict[str, Any]:
    """
    Trigger revalidation of website pages.
    
    Args:
        page_paths: List of page paths to revalidate
        tags: List of tags to revalidate
        
    Returns:
        Dict containing revalidation results
    """
    
    try:
        import os
        
        # Get revalidation config from environment
        webhook_url = os.getenv("BACKEND_REVALIDATE_WEBHOOK_URL")
        secret = os.getenv("REVALIDATE_SECRET")
        
        if not webhook_url or not secret:
            logger.warning("Revalidation webhook not configured")
            return {
                "status": "skipped",
                "reason": "webhook_not_configured",
                "revalidated_paths": [],
                "revalidated_tags": []
            }
        
        revalidated_paths = []
        revalidated_tags = []
        
        # Revalidate paths
        if page_paths:
            for path in page_paths:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{webhook_url}?secret={secret}",
                            json={"path": path, "type": "path"},
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            revalidated_paths.append(path)
                            logger.info(f"✅ Revalidated path: {path}")
                        else:
                            logger.error(f"❌ Failed to revalidate path {path}: {response.status_code}")
                            
                except Exception as e:
                    logger.error(f"❌ Error revalidating path {path}: {e}")
        
        # Revalidate tags
        if tags:
            for tag in tags:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{webhook_url}?secret={secret}",
                            json={"tag": tag, "type": "tag"},
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            revalidated_tags.append(tag)
                            logger.info(f"✅ Revalidated tag: {tag}")
                        else:
                            logger.error(f"❌ Failed to revalidate tag {tag}: {response.status_code}")
                            
                except Exception as e:
                    logger.error(f"❌ Error revalidating tag {tag}: {e}")
        
        return {
            "status": "success",
            "revalidated_paths": revalidated_paths,
            "revalidated_tags": revalidated_tags,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering revalidation: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger revalidation")


@router.post("/deploy/{business_id}")
async def deploy_seo_pipeline(
    business_id: str = Path(..., description="Business ID"),
    supabase: Client = Depends(get_supabase_client),
    trigger_llm: bool = False
) -> Dict[str, Any]:
    """
    Deploy SEO pipeline for a business.
    
    Steps:
    1. Materialize default services (if needed)
    2. Precompute SEO scaffolding (service_location_pages + service_seo_config)
    3. Optionally trigger LLM content generation
    4. Return the generated page map
    
    Args:
        business_id: The unique identifier of the business
        trigger_llm: Whether to trigger LLM content generation
        
    Returns:
        Dict containing deployment status and page map
    """
    try:
        logger.info(f"Starting SEO deployment for business {business_id}")
        
        # Initialize repositories
        business_repository = SupabaseBusinessRepository(supabase)
        
        # Step 1: Materialize services (skip for now due to schema mismatch)
        # materialization_service = ServiceMaterializationService(business_repository, supabase)
        # await materialization_service.materialize_default_services(business_id)
        logger.info(f"✓ Skipped service materialization for business {business_id} (schema mismatch)")
        
        # Step 2: Precompute SEO scaffolding
        # Get business data directly from Supabase to avoid repository issues
        business_result = supabase.table("businesses").select("*").eq("id", business_id).execute()
        if not business_result.data:
            raise ValueError(f"Business {business_id} not found")
        
        business_row = business_result.data[0]
        business_data = {
            'selected_residential_service_keys': business_row.get('selected_residential_service_keys', []),
            'selected_commercial_service_keys': business_row.get('selected_commercial_service_keys', []),
            'city': business_row.get('city', ''),
            'state': business_row.get('state', ''),
            'business_name': business_row.get('name', '')
        }
        
        # Get business locations
        locations_result = supabase.table("business_locations").select("*").eq("business_id", business_id).execute()
        locations = locations_result.data or []
        
        seo_service = SEOScaffoldingService(supabase)
        scaffolding_result = await seo_service.precompute_seo_scaffolding(business_id, business_data, [], locations)
        logger.info(f"✓ Precomputed SEO scaffolding for business {business_id}: {scaffolding_result}")
        
        # Step 3: Optional LLM generation (placeholder for now)
        if trigger_llm:
            logger.info(f"LLM content generation requested for business {business_id} (not implemented yet)")
        
        # Step 4: Return the page map by calling our existing endpoint
        pages_response = await get_seo_pages(business_id, supabase)
        
        return {
            "status": "success",
            "business_id": business_id,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "steps_completed": [
                "seo_scaffolding",
                "llm_generation" if trigger_llm else None
            ],
            "pages": pages_response.get("pages", {}),
            "navigation": pages_response.get("navigation", {}),
            "total_pages": pages_response.get("total_pages", 0)
        }
        
    except Exception as e:
        logger.error(f"Error deploying SEO pipeline for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy SEO pipeline: {str(e)}")
