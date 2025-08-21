"""
Google Business Profile Port

Abstract interface for Google Business Profile operations.
Defines the contract for external Google Business Profile integrations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...domain.entities.business import Business
from ...domain.entities.website import GoogleBusinessProfile, ReviewData, InsightData


class ProfileSearchResult(BaseModel):
    """Result from profile search operations."""
    
    location_id: str
    name: str
    place_id: Optional[str] = None
    address: Dict[str, Any]
    phone: Optional[str] = None
    website: Optional[str] = None
    categories: List[Dict[str, Any]] = []
    verification_status: Optional[str] = None
    profile_url: Optional[str] = None
    match_score: float = 0.0
    can_claim: bool = False


class ProfileSyncResult(BaseModel):
    """Result from profile synchronization operations."""
    
    success: bool
    updates_applied: int = 0
    fields_updated: List[str] = []
    profile_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PostContent(BaseModel):
    """Content for Google Business Profile posts."""
    
    summary: str
    post_type: str = "STANDARD"  # STANDARD, OFFER, EVENT
    cta_type: Optional[str] = "LEARN_MORE"
    cta_url: Optional[str] = None
    image_url: Optional[str] = None
    
    # Offer-specific fields
    coupon_code: Optional[str] = None
    redeem_url: Optional[str] = None
    terms: Optional[str] = None
    
    # Event-specific fields
    event_title: Optional[str] = None
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    end_date: Optional[str] = None
    end_time: Optional[str] = None


class GoogleBusinessProfilePort(ABC):
    """
    Abstract interface for Google Business Profile operations.
    
    This port defines the contract for external Google Business Profile
    integrations, allowing different implementations to be swapped out.
    """
    
    @abstractmethod
    async def search_business_profiles(
        self,
        business: Business,
        query: Optional[str] = None
    ) -> List[ProfileSearchResult]:
        """
        Search for existing Google Business Profiles for a business.
        
        Args:
            business: The business to search profiles for
            query: Optional custom search query
            
        Returns:
            List of matching profiles with match scores
        """
        pass
    
    @abstractmethod
    async def create_business_profile(
        self,
        business: Business,
        additional_info: Dict[str, Any]
    ) -> Optional[GoogleBusinessProfile]:
        """
        Create a new Google Business Profile for a business.
        
        Args:
            business: The business to create a profile for
            additional_info: Additional profile configuration
            
        Returns:
            Created GoogleBusinessProfile entity or None if failed
        """
        pass
    
    @abstractmethod
    async def sync_profile_data(
        self,
        gbp_profile: GoogleBusinessProfile,
        business: Business
    ) -> ProfileSyncResult:
        """
        Sync business data with Google Business Profile.
        
        Args:
            gbp_profile: The Google Business Profile to sync
            business: Current business data
            
        Returns:
            Sync operation result
        """
        pass
    
    @abstractmethod
    async def get_reviews(
        self,
        gbp_profile: GoogleBusinessProfile,
        limit: int = 50
    ) -> List[ReviewData]:
        """
        Fetch reviews from Google Business Profile.
        
        Args:
            gbp_profile: The profile to fetch reviews for
            limit: Maximum number of reviews to fetch
            
        Returns:
            List of review data
        """
        pass
    
    @abstractmethod
    async def respond_to_review(
        self,
        gbp_profile: GoogleBusinessProfile,
        review_id: str,
        response_text: str
    ) -> bool:
        """
        Respond to a Google Business Profile review.
        
        Args:
            gbp_profile: The profile containing the review
            review_id: ID of the review to respond to
            response_text: Response content
            
        Returns:
            True if response was posted successfully
        """
        pass
    
    @abstractmethod
    async def get_insights(
        self,
        gbp_profile: GoogleBusinessProfile,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[InsightData]:
        """
        Fetch Google Business Profile insights and analytics.
        
        Args:
            gbp_profile: The profile to fetch insights for
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Insights data or None if failed
        """
        pass
    
    @abstractmethod
    async def create_post(
        self,
        gbp_profile: GoogleBusinessProfile,
        post_content: PostContent
    ) -> bool:
        """
        Create a post on Google Business Profile.
        
        Args:
            gbp_profile: The profile to post to
            post_content: Content and configuration for the post
            
        Returns:
            True if post was created successfully
        """
        pass
    
    @abstractmethod
    async def get_profile_data(
        self,
        gbp_profile: GoogleBusinessProfile
    ) -> Optional[Dict[str, Any]]:
        """
        Get current profile data from Google Business Profile.
        
        Args:
            gbp_profile: The profile to fetch data for
            
        Returns:
            Current profile data or None if failed
        """
        pass
    
    @abstractmethod
    async def update_profile_field(
        self,
        gbp_profile: GoogleBusinessProfile,
        field_name: str,
        field_value: Any
    ) -> bool:
        """
        Update a specific field in the Google Business Profile.
        
        Args:
            gbp_profile: The profile to update
            field_name: Name of the field to update
            field_value: New value for the field
            
        Returns:
            True if update was successful
        """
        pass
    
    @abstractmethod
    async def verify_profile(
        self,
        gbp_profile: GoogleBusinessProfile,
        verification_method: str = "SMS"
    ) -> Dict[str, Any]:
        """
        Initiate profile verification process.
        
        Args:
            gbp_profile: The profile to verify
            verification_method: Method for verification (SMS, POSTCARD, etc.)
            
        Returns:
            Verification process result
        """
        pass
