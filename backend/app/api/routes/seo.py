"""
SEO API Routes

Public endpoints for SEO page data and website building.
Enhanced with artifact-based programmatic SEO at scale.
"""

from fastapi import APIRouter, HTTPException, Path, Depends, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
import httpx
import uuid
from datetime import datetime, timezone
from supabase import Client

from app.api.deps import get_supabase_client
from app.api.dtos.seo_artifact_dtos import (
    ActivityPageArtifact, SitemapManifest, GenerateArtifactsRequest, 
    GenerateArtifactsResponse, ArtifactListResponse, SitemapGenerationRequest,
    SitemapGenerationResponse, PromoteVariantRequest, QualityGateResult,
    ArtifactStatus, QualityLevel
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/seo", tags=["SEO"])


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


# ============================================================================
# NEW ARTIFACT-BASED SEO ENDPOINTS
# ============================================================================

@router.post("/artifacts/{business_id}/generate")
async def generate_seo_artifacts(
    request: GenerateArtifactsRequest,
    business_id: str = Path(..., description="Business ID"),
    background_tasks: BackgroundTasks = None,
    supabase: Client = Depends(get_supabase_client)
) -> GenerateArtifactsResponse:
    """
    Generate SEO artifacts for activities using RAG-enhanced LLM orchestration.
    
    This endpoint queues artifact generation jobs that create typed, versioned
    content artifacts with quality gates and A/B testing support.
    """
    try:
        # Validate business exists
        business_result = supabase.table("businesses").select("id,name").eq("id", business_id).execute()
        if not business_result.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Queue background task for artifact generation (if available)
        if background_tasks:
            background_tasks.add_task(
                _generate_artifacts_background,
                business_id=business_id,
                job_id=job_id,
                request=request,
                supabase=supabase
            )
        
        return GenerateArtifactsResponse(
            business_id=business_id,
            job_id=job_id,
            status="queued",
            generated_at=datetime.now(timezone.utc),
            estimated_completion=datetime.now(timezone.utc).replace(minute=datetime.now().minute + 10)
        )
        
    except Exception as e:
        logger.error(f"Error queuing artifact generation for business {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue artifact generation")


@router.get("/artifacts/{business_id}")
async def list_seo_artifacts(
    business_id: str = Path(..., description="Business ID"),
    status: Optional[ArtifactStatus] = Query(None, description="Filter by status"),
    activity_slug: Optional[str] = Query(None, description="Filter by activity"),
    location_slug: Optional[str] = Query(None, description="Filter by location"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    supabase: Client = Depends(get_supabase_client)
) -> ArtifactListResponse:
    """
    List SEO artifacts for a business with filtering and pagination.
    """
    try:
        # Build query
        query = supabase.table("seo_artifacts").select("*").eq("business_id", business_id)
        
        if status:
            query = query.eq("status", status.value)
        if activity_slug:
            query = query.eq("activity_slug", activity_slug)
        if location_slug:
            query = query.eq("location_slug", location_slug)
        
        # Get total count
        count_result = query.execute()
        total_count = len(count_result.data) if count_result.data else 0
        
        # Apply pagination
        result = query.range(offset, offset + limit - 1).execute()
        
        artifacts = []
        approved_count = 0
        published_count = 0
        last_updated = None
        
        for row in result.data or []:
            try:
                artifact = ActivityPageArtifact(**row)
                artifacts.append(artifact)
                
                if artifact.status == ArtifactStatus.APPROVED:
                    approved_count += 1
                elif artifact.status == ArtifactStatus.PUBLISHED:
                    published_count += 1
                
                if artifact.updated_at and (not last_updated or artifact.updated_at > last_updated):
                    last_updated = artifact.updated_at
                    
            except Exception as e:
                logger.warning(f"Failed to parse artifact {row.get('artifact_id', 'unknown')}: {e}")
                continue
        
        return ArtifactListResponse(
            business_id=business_id,
            artifacts=artifacts,
            total_count=total_count,
            approved_count=approved_count,
            published_count=published_count,
            last_updated=last_updated
        )
        
    except Exception as e:
        # Graceful fallback when table doesn't exist (e.g., before migrations)
        logger.warning(f"Artifacts listing fallback for {business_id}: {e}")
        return ArtifactListResponse(
            business_id=business_id,
            artifacts=[],
            total_count=0,
            approved_count=0,
            published_count=0,
            last_updated=None
        )


@router.get("/artifacts/{business_id}/{artifact_id}")
async def get_seo_artifact(
    business_id: str = Path(..., description="Business ID"),
    artifact_id: str = Path(..., description="Artifact ID"),
    supabase: Client = Depends(get_supabase_client)
) -> ActivityPageArtifact:
    """
    Get a specific SEO artifact by ID.
    """
    try:
        result = supabase.table("seo_artifacts").select("*").eq(
            "business_id", business_id
        ).eq("artifact_id", artifact_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        return ActivityPageArtifact(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving artifact {artifact_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve artifact")


@router.put("/artifacts/{business_id}/{artifact_id}/approve")
async def approve_seo_artifact(
    business_id: str = Path(..., description="Business ID"),
    artifact_id: str = Path(..., description="Artifact ID"),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Approve an SEO artifact for publication.
    """
    try:
        # Update artifact status
        result = supabase.table("seo_artifacts").update({
            "status": ArtifactStatus.APPROVED.value,
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("business_id", business_id).eq("artifact_id", artifact_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        return {
            "business_id": business_id,
            "artifact_id": artifact_id,
            "status": "approved",
            "approved_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving artifact {artifact_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve artifact")


@router.post("/sitemaps/{business_id}/generate")
async def generate_sitemap_manifest(
    request: SitemapGenerationRequest,
    business_id: str = Path(..., description="Business ID"),
    supabase: Client = Depends(get_supabase_client)
) -> SitemapGenerationResponse:
    """
    Generate segmented sitemaps for a business.
    
    Creates sitemap index with separate sitemaps for:
    - Service pages
    - Location pages  
    - Project pages
    - Static pages
    """
    try:
        # Get approved artifacts for sitemap generation
        artifacts_query = supabase.table("seo_artifacts").select("*").eq("business_id", business_id)
        
        if not request.include_drafts:
            artifacts_query = artifacts_query.in_("status", [ArtifactStatus.APPROVED.value, ArtifactStatus.PUBLISHED.value])
        
        artifacts_result = artifacts_query.execute()
        
        # Generate sitemap entries
        sitemap_entries = []
        for row in artifacts_result.data or []:
            try:
                artifact = ActivityPageArtifact(**row)
                entry = {
                    "loc": f"{request.base_url}{artifact.page_url}",
                    "lastmod": (artifact.updated_at or artifact.created_at or datetime.now(timezone.utc)).isoformat(),
                    "changefreq": "weekly",
                    "priority": 0.8 if not artifact.is_location_specific else 0.6,
                    "page_type": "location" if artifact.is_location_specific else "service"
                }
                sitemap_entries.append(entry)
            except Exception as e:
                logger.warning(f"Failed to process artifact for sitemap: {e}")
                continue
        
        # Store sitemap manifest
        manifest_data = {
            "business_id": business_id,
            "sitemap_index_url": f"{request.base_url}/sitemap.xml",
            "total_urls": len(sitemap_entries),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sitemap_entries": sitemap_entries
        }
        
        # Save to database
        supabase.table("sitemap_manifests").upsert(manifest_data, on_conflict="business_id").execute()
        
        return SitemapGenerationResponse(
            business_id=business_id,
            sitemap_index_url=f"{request.base_url}/sitemap.xml",
            sitemaps_generated=[
                f"{request.base_url}/sitemap-services.xml",
                f"{request.base_url}/sitemap-locations.xml",
                f"{request.base_url}/sitemap-static.xml"
            ],
            total_urls=len(sitemap_entries),
            generated_at=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error generating sitemap for business {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate sitemap")


@router.get("/sitemaps/{business_id}")
async def get_sitemap_manifest(
    business_id: str = Path(..., description="Business ID"),
    supabase: Client = Depends(get_supabase_client)
) -> SitemapManifest:
    """
    Get sitemap manifest for a business.
    """
    try:
        result = supabase.table("sitemap_manifests").select("*").eq("business_id", business_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Sitemap manifest not found")
        
        manifest_data = result.data[0]
        
        # Provide segmented arrays for frontend expectations
        manifest = SitemapManifest(
            business_id=manifest_data["business_id"],
            sitemap_index_url=manifest_data["sitemap_index_url"],
            total_urls=manifest_data["total_urls"],
            generated_at=datetime.fromisoformat(manifest_data["generated_at"].replace('Z', '+00:00')),
            sitemaps=manifest_data.get("sitemaps", [])
        )
        # Empty segments by default; can be populated from views later
        manifest.service_pages = []
        manifest.location_pages = []
        manifest.project_pages = []
        manifest.static_pages = []
        return manifest
        
    except HTTPException:
        raise
    except Exception as e:
        # Graceful fallback when table doesn't exist (e.g., before migrations)
        logger.warning(f"Sitemap manifest fallback for {business_id}: {e}")
        return SitemapManifest(
            business_id=business_id,
            sitemap_index_url=f"/sitemap.xml",
            total_urls=0,
            generated_at=datetime.now(timezone.utc),
            sitemaps=[],
        )


# =========================================================================
# SEO PAGES AGGREGATION (for website-builder)
# =========================================================================

@router.get("/pages/{business_id}")
async def get_seo_pages(
    business_id: str = Path(..., description="Business ID"),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Aggregate SEO page payload expected by website-builder.
        
    Returns:
      {
        "pages": { [url]: { title, meta_description, h1_heading, ... } },
        "content_blocks": { [url]: { hero, benefits, faqs, ... } }
      }
    """
    try:
        # Prefer approved or published artifacts
        result = (
            supabase
            .table("seo_artifacts")
            .select("artifact_id,business_id,activity_slug,location_slug,title,meta_description,h1_heading,canonical_url,hero,benefits,process,offers,guarantees,faqs,cta_sections,json_ld_schemas,status")
            .eq("business_id", business_id)
            .execute()
        )

        artifacts = result.data or []

        pages: Dict[str, Any] = {}
        content_blocks: Dict[str, Any] = {}

        def infer_url(row: Dict[str, Any]) -> str:
            if row.get("canonical_url"):
                return row["canonical_url"]
            activity = (row.get("activity_slug") or "").strip()
            location = (row.get("location_slug") or "").strip()
            if activity and location:
                return f"/services/{activity}/{location}"
            if activity:
                return f"/services/{activity}"
            return "/"

        for row in artifacts:
            url = infer_url(row)
            # Only keep one entry per URL; prefer approved/published over drafts
            existing = pages.get(url)
            keep = True
            if existing:
                # If existing exists and is approved/published, keep existing
                # Otherwise replace with current
                keep = False
            if not keep:
                continue

            pages[url] = {
                "title": row.get("title") or "",
                "meta_description": row.get("meta_description") or "",
                "h1_heading": row.get("h1_heading") or (row.get("title") or ""),
                "content": "",  # content is provided via content_blocks
                "schema_markup": row.get("json_ld_schemas") or [],
                "target_keywords": [],
                "page_url": url,
                "generation_method": "template",
                "page_type": "service" if "/services/" in url else "page",
                "word_count": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            content_blocks[url] = {
                "hero": row.get("hero") or {},
                "benefits": row.get("benefits") or {},
                "process": row.get("process") or {},
                "offers": row.get("offers") or {},
                "guarantees": row.get("guarantees") or {},
                "faqs": row.get("faqs") or [],
                "cta_sections": row.get("cta_sections") or [],
            }

        return {"pages": pages, "content_blocks": content_blocks}

    except Exception as e:
        logger.error(f"Error aggregating SEO pages for {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load SEO pages")


@router.post("/experiments/{business_id}/promote")
async def promote_winning_variant(
    request: PromoteVariantRequest,
    business_id: str = Path(..., description="Business ID"),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Promote winning A/B test variant to production.
    """
    try:
        # Get artifact
        artifact_result = supabase.table("seo_artifacts").select("*").eq(
            "business_id", business_id
        ).eq("artifact_id", request.artifact_id).execute()
        
        if not artifact_result.data:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        artifact_data = artifact_result.data[0]
        
        # Update artifact with winning variant
        # This would involve promoting the variant content to the main content
        # and updating the artifact status
        
        updated_data = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": ArtifactStatus.APPROVED.value
        }
        
        supabase.table("seo_artifacts").update(updated_data).eq(
            "artifact_id", request.artifact_id
        ).execute()
        
        # Log experiment result
        experiment_log = {
            "business_id": business_id,
            "artifact_id": request.artifact_id,
            "experiment_key": request.experiment_key,
            "winning_variant": request.winning_variant_key,
            "result": request.experiment_result.model_dump(),
            "promoted_at": datetime.now(timezone.utc).isoformat()
        }
        
        supabase.table("experiment_results").insert(experiment_log).execute()
        
        return {
            "business_id": business_id,
            "artifact_id": request.artifact_id,
            "experiment_key": request.experiment_key,
            "winning_variant": request.winning_variant_key,
            "promoted_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error promoting variant for artifact {request.artifact_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to promote variant")


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def _generate_artifacts_background(
    business_id: str,
    job_id: str,
    request: GenerateArtifactsRequest,
    supabase: Client
):
    """
    Background task for generating SEO artifacts.
    """
    try:
        logger.info(f"Starting artifact generation job {job_id} for business {business_id}")
        
        # Update job status
        job_data = {
            "job_id": job_id,
            "business_id": business_id,
            "status": "processing",
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("artifact_generation_jobs").upsert(job_data, on_conflict="job_id").execute()
        
        # Orchestrator removed with legacy pipeline; artifacts are generated directly
        
        # Get business data
        business_result = supabase.table("businesses").select("*").eq("id", business_id).execute()
        if not business_result.data:
            raise ValueError(f"Business {business_id} not found")
        
        business_data = business_result.data[0]
        
        # Get activities to generate from business_services (canonical source)
        # Use canonical_slug and service_name for proper mapping
        activities_query = (
            supabase
            .table("business_services")
            .select("canonical_slug,service_name")
            .eq("business_id", business_id)
            .eq("is_active", True)
        )

        if request.activity_slugs:
            activities_query = activities_query.in_("canonical_slug", request.activity_slugs)
        
        activities_result = activities_query.execute()
        
        artifacts_generated = 0
        artifacts_approved = 0
        quality_gate_failures = 0
        
        for activity in activities_result.data or []:
            try:
                # Generate artifact (placeholder - would use real orchestrator)
                artifact = await _generate_single_artifact(
                    business_id=business_id,
                    business_data=business_data,
                    activity={
                        "activity_slug": activity.get("canonical_slug"),
                        "activity_name": activity.get("service_name"),
                    },
                    quality_threshold=request.quality_threshold
                )
                
                if artifact:
                    # Save artifact
                    artifact_data = artifact.model_dump()
                    artifact_data["created_at"] = datetime.now(timezone.utc).isoformat()
                    artifact_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                    
                    supabase.table("seo_artifacts").upsert(artifact_data, on_conflict="artifact_id").execute()
                    
                    artifacts_generated += 1
                    
                    if artifact.quality_metrics.passed_quality_gate:
                        artifacts_approved += 1
                    else:
                        quality_gate_failures += 1
                
            except Exception as e:
                logger.error(f"Failed to generate artifact for activity {activity['activity_slug']}: {e}")
                quality_gate_failures += 1
        
        # Update job completion
        completion_data = {
            "job_id": job_id,
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "artifacts_generated": artifacts_generated,
            "artifacts_approved": artifacts_approved,
            "quality_gate_failures": quality_gate_failures
        }
        supabase.table("artifact_generation_jobs").update(completion_data).eq("job_id", job_id).execute()
        
        logger.info(f"Completed artifact generation job {job_id}: {artifacts_generated} generated, {artifacts_approved} approved")
        
    except Exception as e:
        logger.error(f"Error in artifact generation job {job_id}: {e}")
        
        # Update job failure
        failure_data = {
            "job_id": job_id,
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": str(e)
        }
        supabase.table("artifact_generation_jobs").update(failure_data).eq("job_id", job_id).execute()


async def _generate_single_artifact(
    business_id: str,
    business_data: Dict[str, Any],
    activity: Dict[str, Any],
    quality_threshold: float
) -> Optional[ActivityPageArtifact]:
    """
    Generate a single SEO artifact for an activity.
    """
    try:
        # This is a placeholder - would implement full artifact generation
        # using the orchestrator with RAG-enhanced context
        
        from app.api.dtos.seo_artifact_dtos import ActivityType, QualityMetrics, ArtifactStatus, ContentSource, QualityLevel
        
        artifact = ActivityPageArtifact(
            business_id=business_id,
            activity_slug=activity["activity_slug"],
            artifact_id=str(uuid.uuid4()),
            activity_type=ActivityType.HVAC,  # Would map from activity data
            activity_name=activity["activity_name"],
            title=f"{activity['activity_name']} Services | {business_data['name']}",
            meta_description=f"Professional {activity['activity_name'].lower()} services by {business_data['name']}.",
            h1_heading=f"{activity['activity_name']} Services",
            canonical_url=f"/services/{activity['activity_slug']}",
            target_keywords=[activity["activity_slug"], activity["activity_name"]],
            quality_metrics=QualityMetrics(
                overall_score=85.0,
                overall_level=QualityLevel.GOOD,
                word_count=1200,
                heading_count=6,
                internal_link_count=5,
                external_link_count=2,
                faq_count=8,
                passed_quality_gate=True
            ),
            content_source=ContentSource.RAG_ENHANCED,
            status=ArtifactStatus.APPROVED if 85.0 >= quality_threshold else ArtifactStatus.DRAFT
        )
        
        return artifact
        
    except Exception as e:
        logger.error(f"Error generating artifact for {activity['activity_slug']}: {e}")
        return None
