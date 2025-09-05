"""
Unified Content API Routes

High-performance API endpoints that replace the fragmented content systems:
- Single endpoint for all content types
- Parallel processing for speed
- Quality gates and caching
- Real-time personalization support
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.application.services.unified_content_orchestrator import (
    UnifiedContentOrchestrator,
    ContentRequest,
    ContentTier,
    ContentStatus
)
from app.infrastructure.database.repositories.supabase_business_repository import SupabaseBusinessRepository
from app.infrastructure.database.repositories.supabase_contact_repository import SupabaseContactRepository
from app.application.services.llm_content_generation_service import LLMContentGenerationService
from app.application.services.rag_retrieval_service import RAGRetrievalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/content", tags=["Unified Content"])

# Pydantic models for API
class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    business_id: str = Field(..., description="Business identifier")
    activity_slug: str = Field(..., description="Service activity slug (e.g., 'ac-repair')")
    location_slug: Optional[str] = Field(None, description="Location slug (e.g., 'austin-tx')")
    page_variant: str = Field("standard", description="Page variant: standard, emergency, commercial")
    target_tier: str = Field("enhanced", description="Content tier: template, enhanced, premium, personalized")
    personalization_context: Optional[Dict[str, Any]] = Field(None, description="Real-time personalization context")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")

class ContentGenerationResponse(BaseModel):
    """Response model for content generation"""
    request_id: str
    business_id: str
    activity_slug: str
    location_slug: Optional[str]
    page_variant: str
    
    # Content data
    artifact: Dict[str, Any]
    business_context: Dict[str, Any]
    location_context: Optional[Dict[str, Any]]
    
    # Metadata
    tier: str
    status: str
    quality_score: float
    generation_time_ms: int
    cached: bool
    expires_at: datetime
    
    # Performance metrics
    seo_score: float
    readability_score: float
    conversion_potential: float

class BulkContentRequest(BaseModel):
    """Request model for bulk content generation"""
    business_id: str
    requests: List[Dict[str, Any]] = Field(..., description="List of content requests")
    target_tier: str = Field("template", description="Default content tier for all requests")
    parallel_limit: int = Field(10, description="Maximum parallel generations")

class CacheInvalidationRequest(BaseModel):
    """Request model for cache invalidation"""
    business_id: str
    activity_slug: Optional[str] = None
    location_slug: Optional[str] = None

# Dependency injection
async def get_content_orchestrator() -> UnifiedContentOrchestrator:
    """Get the unified content orchestrator instance"""
    # In production, these would be properly injected
    from app.infrastructure.database.supabase_client import get_supabase_client
    supabase_client = get_supabase_client()
    
    business_repo = SupabaseBusinessRepository(supabase_client)
    contact_repo = SupabaseContactRepository(supabase_client)
    llm_service = LLMContentGenerationService()
    rag_service = RAGRetrievalService()
    
    return UnifiedContentOrchestrator(
        business_repository=business_repo,
        contact_repository=contact_repo,
        llm_service=llm_service,
        rag_service=rag_service,
    )

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    orchestrator: UnifiedContentOrchestrator = Depends(get_content_orchestrator)
) -> ContentGenerationResponse:
    """
    Generate content for a specific service and location
    
    This is the main endpoint that replaces all fragmented content APIs.
    It provides:
    - Instant template content for immediate deployment
    - LLM-enhanced content for better quality
    - RAG-enhanced premium content
    - Real-time personalization
    """
    try:
        logger.info(f"🎯 [API] Content generation request: {request.activity_slug} in {request.location_slug}")
        
        # Convert request to internal format
        content_request = ContentRequest(
            business_id=request.business_id,
            activity_slug=request.activity_slug,
            location_slug=request.location_slug,
            page_variant=request.page_variant,
            target_tier=ContentTier(request.target_tier),
            personalization_context=request.personalization_context,
            cache_ttl=request.cache_ttl,
        )
        
        # Generate content
        response = await orchestrator.generate_content(content_request)
        
        # Convert to API response format
        return ContentGenerationResponse(
            request_id=response.request_id,
            business_id=response.business_id,
            activity_slug=response.activity_slug,
            location_slug=response.location_slug,
            page_variant=response.page_variant,
            artifact=response.artifact,
            business_context=response.business_context,
            location_context=response.location_context,
            tier=response.tier.value,
            status=response.status.value,
            quality_score=response.quality_score,
            generation_time_ms=response.generation_time_ms,
            cached=response.cached,
            expires_at=response.expires_at,
            seo_score=response.seo_score,
            readability_score=response.readability_score,
            conversion_potential=response.conversion_potential,
        )
        
    except Exception as e:
        logger.error(f"❌ [API] Content generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/bulk")
async def generate_bulk_content(
    request: BulkContentRequest,
    background_tasks: BackgroundTasks,
    orchestrator: UnifiedContentOrchestrator = Depends(get_content_orchestrator)
) -> JSONResponse:
    """
    Generate content for multiple services/locations in parallel
    
    This is perfect for:
    - Initial site deployment (generate all pages at once)
    - Bulk updates after business changes
    - Preemptive cache warming
    """
    try:
        logger.info(f"🚀 [API] Bulk content generation: {len(request.requests)} requests")
        
        # Convert requests to internal format
        content_requests = []
        for req_data in request.requests:
            content_requests.append(ContentRequest(
                business_id=request.business_id,
                activity_slug=req_data['activity_slug'],
                location_slug=req_data.get('location_slug'),
                page_variant=req_data.get('page_variant', 'standard'),
                target_tier=ContentTier(req_data.get('target_tier', request.target_tier)),
                cache_ttl=req_data.get('cache_ttl', 3600),
            ))
        
        # Process in parallel batches
        results = []
        semaphore = asyncio.Semaphore(request.parallel_limit)
        
        async def generate_single(content_request: ContentRequest):
            async with semaphore:
                try:
                    return await orchestrator.generate_content(content_request)
                except Exception as e:
                    logger.error(f"❌ Failed to generate {content_request.activity_slug}: {str(e)}")
                    return None
        
        # Execute all requests in parallel
        start_time = datetime.now()
        responses = await asyncio.gather(*[
            generate_single(req) for req in content_requests
        ])
        total_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Filter successful responses
        successful_responses = [r for r in responses if r is not None]
        
        logger.info(f"✅ [API] Bulk generation completed: {len(successful_responses)}/{len(content_requests)} successful in {total_time}ms")
        
        return JSONResponse({
            "success": True,
            "total_requests": len(content_requests),
            "successful_generations": len(successful_responses),
            "failed_generations": len(content_requests) - len(successful_responses),
            "total_time_ms": total_time,
            "average_time_per_request_ms": total_time // len(content_requests) if content_requests else 0,
            "results": [
                {
                    "request_id": r.request_id,
                    "activity_slug": r.activity_slug,
                    "location_slug": r.location_slug,
                    "tier": r.tier.value,
                    "quality_score": r.quality_score,
                    "generation_time_ms": r.generation_time_ms,
                } for r in successful_responses
            ]
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Bulk content generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Bulk content generation failed: {str(e)}"
        )

@router.get("/artifact/{business_id}/{activity_slug}")
async def get_artifact(
    business_id: str,
    activity_slug: str,
    location_slug: Optional[str] = Query(None),
    page_variant: str = Query("standard"),
    tier: str = Query("enhanced"),
    orchestrator: UnifiedContentOrchestrator = Depends(get_content_orchestrator)
) -> ContentGenerationResponse:
    """
    Get artifact content (compatible with existing frontend)
    
    This endpoint maintains compatibility with the existing frontend
    while using the new unified orchestrator backend.
    """
    request = ContentGenerationRequest(
        business_id=business_id,
        activity_slug=activity_slug,
        location_slug=location_slug,
        page_variant=page_variant,
        target_tier=tier,
    )
    
    return await generate_content(request, orchestrator)

@router.post("/cache/invalidate")
async def invalidate_cache(
    request: CacheInvalidationRequest,
    orchestrator: UnifiedContentOrchestrator = Depends(get_content_orchestrator)
) -> JSONResponse:
    """
    Invalidate cached content
    
    Use this when:
    - Business information changes
    - Service offerings are updated
    - Location data is modified
    """
    try:
        invalidated_count = await orchestrator.invalidate_cache(
            business_id=request.business_id,
            activity_slug=request.activity_slug
        )
        
        logger.info(f"🗑️ [API] Cache invalidated: {invalidated_count} entries for {request.business_id}")
        
        return JSONResponse({
            "success": True,
            "invalidated_entries": invalidated_count,
            "business_id": request.business_id,
            "activity_slug": request.activity_slug,
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Cache invalidation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Cache invalidation failed: {str(e)}"
        )

@router.get("/stats")
async def get_generation_stats(
    orchestrator: UnifiedContentOrchestrator = Depends(get_content_orchestrator)
) -> JSONResponse:
    """
    Get content generation statistics
    
    Useful for monitoring and optimization
    """
    try:
        stats = await orchestrator.get_generation_stats()
        
        return JSONResponse({
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Stats retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Stats retrieval failed: {str(e)}"
        )

@router.post("/pregenerate/{business_id}")
async def pregenerate_content(
    business_id: str,
    background_tasks: BackgroundTasks,
    tier: str = Query("template", description="Content tier to pregenerate"),
    orchestrator: UnifiedContentOrchestrator = Depends(get_content_orchestrator)
) -> JSONResponse:
    """
    Pregenerate content for all service-location combinations
    
    This creates the full SEO matrix (900+ pages) for a business:
    - 20 services × 15 locations × 3 variants = 900 pages
    - Template tier for instant deployment
    - Enhanced tier generated in background
    """
    try:
        logger.info(f"🚀 [API] Pregenerating content matrix for {business_id}")
        
        # Define the service-location matrix
        services = [
            'ac-repair', 'ac-installation', 'hvac-maintenance', 'heating-repair',
            'drain-cleaning', 'water-heater-repair', 'leak-detection', 'pipe-repair',
            'panel-upgrade', 'lighting-installation', 'wiring-repair', 'generator-installation',
            'roof-repair', 'roof-replacement', 'gutter-installation', 'storm-damage-repair',
            'home-renovation', 'kitchen-remodel', 'bathroom-remodel', 'room-addition'
        ]
        
        locations = [
            'austin-tx', 'round-rock-tx', 'cedar-park-tx', 'pflugerville-tx', 'leander-tx',
            'georgetown-tx', 'lakeway-tx', 'bee-cave-tx', 'west-lake-hills-tx', 'rollingwood-tx',
            'sunset-valley-tx', 'manchaca-tx', 'del-valle-tx', 'elgin-tx', 'manor-tx'
        ]
        
        variants = ['standard', 'emergency', 'commercial']
        
        # Generate all combinations
        requests = []
        for service in services:
            for location in locations:
                for variant in variants:
                    requests.append({
                        'activity_slug': service,
                        'location_slug': location,
                        'page_variant': variant,
                        'target_tier': tier,
                    })
        
        total_pages = len(requests)
        logger.info(f"📊 [API] Generating {total_pages} pages for {business_id}")
        
        # Use bulk generation
        bulk_request = BulkContentRequest(
            business_id=business_id,
            requests=requests,
            target_tier=tier,
            parallel_limit=20,  # High parallelism for pregeneration
        )
        
        # Start generation in background
        background_tasks.add_task(
            _execute_bulk_generation,
            bulk_request,
            orchestrator
        )
        
        return JSONResponse({
            "success": True,
            "message": f"Pregeneration started for {business_id}",
            "total_pages": total_pages,
            "services": len(services),
            "locations": len(locations),
            "variants": len(variants),
            "tier": tier,
            "estimated_completion_minutes": total_pages // 60,  # Rough estimate
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Pregeneration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Pregeneration failed: {str(e)}"
        )

async def _execute_bulk_generation(
    request: BulkContentRequest,
    orchestrator: UnifiedContentOrchestrator
) -> None:
    """Execute bulk generation in background"""
    try:
        logger.info(f"🔄 [BACKGROUND] Starting bulk generation of {len(request.requests)} pages")
        
        # Convert requests
        content_requests = []
        for req_data in request.requests:
            content_requests.append(ContentRequest(
                business_id=request.business_id,
                activity_slug=req_data['activity_slug'],
                location_slug=req_data.get('location_slug'),
                page_variant=req_data.get('page_variant', 'standard'),
                target_tier=ContentTier(req_data.get('target_tier', request.target_tier)),
                cache_ttl=7200,  # 2 hours for pregenerated content
            ))
        
        # Process in batches to avoid overwhelming the system
        batch_size = request.parallel_limit
        successful = 0
        failed = 0
        
        for i in range(0, len(content_requests), batch_size):
            batch = content_requests[i:i + batch_size]
            logger.info(f"🔄 [BACKGROUND] Processing batch {i // batch_size + 1}/{(len(content_requests) + batch_size - 1) // batch_size}")
            
            # Process batch
            semaphore = asyncio.Semaphore(batch_size)
            
            async def generate_single(content_request: ContentRequest):
                async with semaphore:
                    try:
                        await orchestrator.generate_content(content_request)
                        return True
                    except Exception as e:
                        logger.error(f"❌ Failed to generate {content_request.activity_slug}/{content_request.location_slug}: {str(e)}")
                        return False
            
            results = await asyncio.gather(*[generate_single(req) for req in batch])
            successful += sum(results)
            failed += len(results) - sum(results)
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        logger.info(f"✅ [BACKGROUND] Bulk generation completed: {successful} successful, {failed} failed")
        
    except Exception as e:
        logger.error(f"❌ [BACKGROUND] Bulk generation failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check() -> JSONResponse:
    """Health check for the unified content system"""
    return JSONResponse({
        "status": "healthy",
        "service": "unified_content_orchestrator",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    })
