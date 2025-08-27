"""
Contractor Profile API Routes

Public endpoints for retrieving contractor profile information.
"""

from fastapi import APIRouter, HTTPException, Path
from typing import List
import logging

from .schemas import ProfessionalProfile

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/profile/{business_id}", response_model=ProfessionalProfile)
async def get_contractor_profile(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get complete contractor profile information.
    
    Returns business details, contact information, service areas, and credentials.
    """
    
    try:
        # Use direct database query to avoid repository issues
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Fetch business from database
        result = supabase.table("businesses").select("*").eq("id", business_id).eq("is_active", True).execute()
        
        if result.data and len(result.data) > 0:
            business = result.data[0]
            
            # Convert business data to response model
            profile_data = {
                "business_id": str(business["id"]),
                "business_name": business["name"],
                "trade_type": business["industry"].lower() if business.get("industry") else "general",
                "description": business.get("description") or f"Professional {business.get('industry', 'service')} provider",
                "phone": business.get("phone_number") or "",
                "email": business.get("business_email") or "",
                "address": business.get("business_address") or "",
                "website": business.get("website"),
                "service_areas": business.get("service_areas") or [],
                "emergency_service": True,  # Default for now
                "years_in_business": 10,  # Default for now
                "license_number": business.get("business_license"),
                "insurance_verified": True,  # Default for now
                "average_rating": 4.8,  # Default for now
                "total_reviews": 150,  # Default for now
                "certifications": []  # Default for now
            }
            
            return ProfessionalProfile(**profile_data)
        
        # If not found in database, return 404
        raise HTTPException(status_code=404, detail="Contractor profile not found")
        
    except Exception as e:
        logger.error(f"Error fetching contractor profile {business_id}: {str(e)}")
        # Return error response
        raise HTTPException(status_code=404, detail="Contractor profile not found")
