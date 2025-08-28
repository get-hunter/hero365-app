from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.infrastructure.database.repositories.supabase_website_deployment_repository import SupabaseBusinessWebsiteRepository

router = APIRouter(prefix="/api/v1/public/websites", tags=["Public Websites"], include_in_schema=True)

@router.get("/resolve")
def resolve_website(host: str = Query(..., description="Full host, e.g., sub.hero365.app or customdomain.com"), subdomain: Optional[str] = None):
    repo = SupabaseBusinessWebsiteRepository()

    # Prefer explicit subdomain if provided
    if subdomain:
        website = repo.get_by_subdomain(subdomain)
        if website:
            return {
                "business_id": str(website.business_id),
                "subdomain": website.subdomain,
                "custom_domain": getattr(website, "domain", None) or None,
                "status": website.status,
                "website_url": website.website_url,
            }

    # Derive subdomain if under hero365 base; otherwise treat host as custom domain
    base = ".hero365.app"
    resolved = None
    try:
        if host.endswith(base):
            sd = host[: -len(base)]
            if sd and sd != "*":
                resolved = repo.get_by_subdomain(sd)
        else:
            # TODO: when repo supports domain lookup, implement get_by_domain
            # For now, return not found; frontend can fall back to default business
            resolved = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resolver error: {str(e)}")

    if not resolved:
        raise HTTPException(status_code=404, detail="Website not found for host")

    return {
        "business_id": str(resolved.business_id),
        "subdomain": resolved.subdomain,
        "custom_domain": getattr(resolved, "domain", None) or None,
        "status": resolved.status,
        "website_url": resolved.website_url,
    }
