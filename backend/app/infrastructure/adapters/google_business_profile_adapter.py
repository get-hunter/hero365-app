"""
Google Business Profile Infrastructure Adapter

Pure infrastructure implementation for Google Business Profile API integration.
Contains only external API communication - no business logic.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import base64

import httpx
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...core.config import settings
from ...domain.entities.business import Business
from ...domain.entities.website import GoogleBusinessProfile, ReviewData, InsightData
from ...application.ports.google_business_profile_port import (
    GoogleBusinessProfilePort, ProfileSearchResult, ProfileSyncResult, PostContent
)

logger = logging.getLogger(__name__)


class GoogleBusinessProfileAdapter(GoogleBusinessProfilePort):
    """
    Infrastructure adapter for Google Business Profile API.
    
    Pure infrastructure implementation - only handles external API communication.
    All business logic is delegated to domain services.
    """
    
    def __init__(self):
        self.api_version = "v1"
        self.base_url = f"https://mybusinessbusinessinformation.googleapis.com/{self.api_version}"
        self.reviews_url = f"https://mybusiness.googleapis.com/v4"
        self.posts_url = f"https://mybusinessbusinessinformation.googleapis.com/{self.api_version}"
        
        # Initialize credentials
        self._credentials = None
        self._service = None
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize Google API credentials."""
        
        try:
            if settings.GOOGLE_SERVICE_ACCOUNT_KEY:
                # Use service account for server-to-server authentication
                credentials_info = json.loads(
                    base64.b64decode(settings.GOOGLE_SERVICE_ACCOUNT_KEY).decode('utf-8')
                )
                
                self._credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=[
                        'https://www.googleapis.com/auth/business.manage',
                        'https://www.googleapis.com/auth/plus.business.manage'
                    ]
                )
                
                self._service = build(
                    'mybusinessbusinessinformation',
                    self.api_version,
                    credentials=self._credentials
                )
                
                logger.info("Google Business Profile adapter initialized with service account")
                
            else:
                logger.warning("Google Business Profile credentials not configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Business Profile credentials: {str(e)}")
    
    async def search_business_profiles(
        self,
        business: Business,
        query: Optional[str] = None
    ) -> List[ProfileSearchResult]:
        """Search for existing Google Business Profiles via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            search_query = query or f"{business.name} {business.city} {business.state}"
            
            # API call to search for locations
            request = self._service.accounts().locations().search(
                parent="accounts/-",  # Search across all accounts
                body={
                    "query": search_query,
                    "pageSize": 20
                }
            )
            
            response = request.execute()
            locations = response.get('locations', [])
            
            # Convert API response to ProfileSearchResult objects
            results = []
            for location in locations:
                profile_data = self._extract_profile_data(location)
                
                result = ProfileSearchResult(
                    location_id=profile_data["location_id"],
                    name=profile_data["name"],
                    place_id=profile_data.get("place_id"),
                    address=profile_data["address"],
                    phone=profile_data.get("phone"),
                    website=profile_data.get("website"),
                    categories=profile_data.get("categories", []),
                    verification_status=profile_data.get("verification_status"),
                    profile_url=profile_data.get("profile_url"),
                    can_claim=location.get('locationState', {}).get('canUpdate', False)
                )
                
                results.append(result)
            
            logger.info(f"API returned {len(results)} profiles for search: {search_query}")
            return results
            
        except HttpError as e:
            logger.error(f"Google API error searching profiles: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching Google Business Profiles: {str(e)}")
            return []
    
    async def create_business_profile(
        self,
        business: Business,
        additional_info: Dict[str, Any]
    ) -> Optional[GoogleBusinessProfile]:
        """Create a new Google Business Profile via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            # Prepare location data for API
            location_data = {
                "languageCode": "en-US",
                "storeCode": f"hero365-{business.id}",
                "locationName": business.name,
                "primaryPhone": business.phone,
                "address": {
                    "addressLines": [business.address],
                    "locality": business.city,
                    "administrativeArea": business.state,
                    "postalCode": business.postal_code,
                    "regionCode": "US"
                },
                "websiteUri": additional_info.get("website_url"),
                "regularHours": additional_info.get("business_hours", {}),
                "specialHours": [],
                "serviceArea": {
                    "businessType": "CUSTOMER_LOCATION_ONLY" if business.is_service_area_business else "CUSTOMER_AND_BUSINESS_LOCATION",
                    "places": {
                        "placeInfos": [
                            {"name": area, "placeId": ""} for area in business.service_areas
                        ]
                    }
                },
                "labels": [f"hero365-{business.get_primary_trade()}"],
                "adWordsLocationExtensions": {
                    "adPhone": business.phone
                }
            }
            
            # API call to create location
            request = self._service.accounts().locations().create(
                parent=f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}",
                body=location_data,
                validateOnly=False,
                requestId=f"hero365-create-{business.id}-{int(datetime.utcnow().timestamp())}"
            )
            
            response = request.execute()
            
            # Extract profile information from API response
            profile_data = self._extract_profile_data(response)
            
            # Create GoogleBusinessProfile entity
            gbp_profile = GoogleBusinessProfile(
                business_id=business.id,
                google_location_id=profile_data["location_id"],
                place_id=profile_data.get("place_id"),
                profile_name=profile_data["name"],
                profile_url=profile_data.get("profile_url"),
                verification_status=profile_data.get("verification_status", "UNVERIFIED"),
                is_verified=False,
                is_suspended=False,
                last_sync_at=datetime.utcnow(),
                sync_enabled=True,
                auto_respond_reviews=additional_info.get("auto_respond_reviews", False),
                auto_post_updates=additional_info.get("auto_post_updates", False)
            )
            
            logger.info(f"Created Google Business Profile via API: {gbp_profile.google_location_id}")
            return gbp_profile
            
        except HttpError as e:
            logger.error(f"Google API error creating profile: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating Google Business Profile: {str(e)}")
            return None
    
    async def sync_profile_data(
        self,
        gbp_profile: GoogleBusinessProfile,
        business: Business
    ) -> ProfileSyncResult:
        """Sync business data with Google Business Profile via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            location_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}"
            
            # API call to get current profile data
            current_profile = self._service.accounts().locations().get(
                name=location_name,
                readMask="name,locationName,primaryPhone,websiteUri,regularHours,serviceArea"
            ).execute()
            
            # Prepare updates
            updates = {}
            update_mask = []
            
            # Check and prepare field updates
            if current_profile.get("locationName") != business.name:
                updates["locationName"] = business.name
                update_mask.append("locationName")
            
            if current_profile.get("primaryPhone") != business.phone:
                updates["primaryPhone"] = business.phone
                update_mask.append("primaryPhone")
            
            # Update website URL if available
            website_url = gbp_profile.website_url or f"https://{business.name.lower().replace(' ', '-')}.hero365.ai"
            if current_profile.get("websiteUri") != website_url:
                updates["websiteUri"] = website_url
                update_mask.append("websiteUri")
            
            # Apply updates via API if any
            if updates:
                update_request = self._service.accounts().locations().patch(
                    name=location_name,
                    body=updates,
                    updateMask=",".join(update_mask)
                )
                
                updated_profile = update_request.execute()
                
                logger.info(f"Updated Google Business Profile via API: {gbp_profile.google_location_id}")
                
                return ProfileSyncResult(
                    success=True,
                    updates_applied=len(update_mask),
                    fields_updated=update_mask,
                    profile_data=updated_profile
                )
            
            else:
                logger.info(f"Google Business Profile already up to date: {gbp_profile.google_location_id}")
                
                return ProfileSyncResult(
                    success=True,
                    updates_applied=0,
                    fields_updated=[],
                    profile_data=current_profile
                )
            
        except HttpError as e:
            logger.error(f"Google API error syncing profile: {str(e)}")
            return ProfileSyncResult(success=False, error=str(e))
        except Exception as e:
            logger.error(f"Error syncing Google Business Profile: {str(e)}")
            return ProfileSyncResult(success=False, error=str(e))
    
    async def get_reviews(
        self,
        gbp_profile: GoogleBusinessProfile,
        limit: int = 50
    ) -> List[ReviewData]:
        """Fetch reviews from Google Business Profile via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            location_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}"
            
            # API call to fetch reviews
            request = self._service.accounts().locations().reviews().list(
                parent=location_name,
                pageSize=min(limit, 50),  # API limit is 50
                orderBy="updateTime desc"
            )
            
            response = request.execute()
            reviews_data = response.get('reviews', [])
            
            # Convert API response to ReviewData entities
            reviews = []
            
            for review_data in reviews_data:
                review = ReviewData(
                    google_review_id=review_data.get('name', '').split('/')[-1],
                    reviewer_name=review_data.get('reviewer', {}).get('displayName', 'Anonymous'),
                    reviewer_profile_photo=review_data.get('reviewer', {}).get('profilePhotoUrl'),
                    rating=review_data.get('starRating', 0),
                    review_text=review_data.get('comment', ''),
                    review_date=datetime.fromisoformat(
                        review_data.get('updateTime', '').replace('Z', '+00:00')
                    ),
                    business_response=review_data.get('reviewReply', {}).get('comment'),
                    response_date=datetime.fromisoformat(
                        review_data.get('reviewReply', {}).get('updateTime', '').replace('Z', '+00:00')
                    ) if review_data.get('reviewReply', {}).get('updateTime') else None,
                    is_responded=bool(review_data.get('reviewReply')),
                    review_url=f"https://www.google.com/maps/reviews/{review_data.get('name', '').split('/')[-1]}"
                )
                
                reviews.append(review)
            
            logger.info(f"Fetched {len(reviews)} reviews via API for profile: {gbp_profile.google_location_id}")
            return reviews
            
        except HttpError as e:
            logger.error(f"Google API error fetching reviews: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Google Business Profile reviews: {str(e)}")
            return []
    
    async def respond_to_review(
        self,
        gbp_profile: GoogleBusinessProfile,
        review_id: str,
        response_text: str
    ) -> bool:
        """Respond to a Google Business Profile review via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            review_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}/reviews/{review_id}"
            
            # API call to post response
            request = self._service.accounts().locations().reviews().reply(
                name=review_name,
                body={
                    "comment": response_text
                }
            )
            
            response = request.execute()
            
            logger.info(f"Posted review response via API for review {review_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google API error responding to review: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error responding to Google Business Profile review: {str(e)}")
            return False
    
    async def get_insights(
        self,
        gbp_profile: GoogleBusinessProfile,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[InsightData]:
        """Fetch Google Business Profile insights via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            location_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}"
            
            # Prepare date range for API
            date_range = {
                "startDate": {
                    "year": start_date.year,
                    "month": start_date.month,
                    "day": start_date.day
                },
                "endDate": {
                    "year": end_date.year,
                    "month": end_date.month,
                    "day": end_date.day
                }
            }
            
            # API call to fetch insights
            search_request = self._service.accounts().locations().reportInsights(
                name=location_name,
                body={
                    "locationNames": [location_name],
                    "basicRequest": {
                        "metricRequests": [
                            {"metric": "QUERIES_DIRECT"},
                            {"metric": "QUERIES_INDIRECT"},
                            {"metric": "QUERIES_CHAIN"},
                            {"metric": "VIEWS_MAPS"},
                            {"metric": "VIEWS_SEARCH"},
                            {"metric": "ACTIONS_WEBSITE"},
                            {"metric": "ACTIONS_PHONE"},
                            {"metric": "ACTIONS_DRIVING_DIRECTIONS"}
                        ],
                        "timeRange": date_range
                    }
                }
            )
            
            search_response = search_request.execute()
            
            # Process API response
            metrics = {}
            
            for location_metric in search_response.get('locationMetrics', []):
                for metric_value in location_metric.get('metricValues', []):
                    metric_name = metric_value.get('metric')
                    total_value = sum(
                        int(dv.get('value', 0)) 
                        for dv in metric_value.get('dimensionalValues', [])
                    )
                    metrics[metric_name] = total_value
            
            # Create InsightData entity from API response
            insight_data = InsightData(
                profile_id=gbp_profile.id,
                date_range_start=start_date.date(),
                date_range_end=end_date.date(),
                
                # Search metrics
                search_queries_direct=metrics.get('QUERIES_DIRECT', 0),
                search_queries_indirect=metrics.get('QUERIES_INDIRECT', 0),
                search_queries_chain=metrics.get('QUERIES_CHAIN', 0),
                
                # View metrics
                views_search=metrics.get('VIEWS_SEARCH', 0),
                views_maps=metrics.get('VIEWS_MAPS', 0),
                
                # Action metrics
                actions_website=metrics.get('ACTIONS_WEBSITE', 0),
                actions_phone=metrics.get('ACTIONS_PHONE', 0),
                actions_directions=metrics.get('ACTIONS_DRIVING_DIRECTIONS', 0),
                
                # Calculated metrics
                total_searches=metrics.get('QUERIES_DIRECT', 0) + metrics.get('QUERIES_INDIRECT', 0),
                total_views=metrics.get('VIEWS_SEARCH', 0) + metrics.get('VIEWS_MAPS', 0),
                total_actions=metrics.get('ACTIONS_WEBSITE', 0) + metrics.get('ACTIONS_PHONE', 0) + metrics.get('ACTIONS_DRIVING_DIRECTIONS', 0),
                
                collected_at=datetime.utcnow()
            )
            
            logger.info(f"Collected insights via API for profile: {gbp_profile.google_location_id}")
            return insight_data
            
        except HttpError as e:
            logger.error(f"Google API error fetching insights: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Google Business Profile insights: {str(e)}")
            return None
    
    async def create_post(
        self,
        gbp_profile: GoogleBusinessProfile,
        post_content: PostContent
    ) -> bool:
        """Create a post on Google Business Profile via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            location_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}"
            
            # Prepare post data for API
            post_data = {
                "languageCode": "en-US",
                "summary": post_content.summary,
                "callToAction": {
                    "actionType": post_content.cta_type or "LEARN_MORE",
                    "url": post_content.cta_url
                },
                "media": []
            }
            
            # Add media if provided
            if post_content.image_url:
                post_data["media"].append({
                    "mediaFormat": "PHOTO",
                    "sourceUrl": post_content.image_url
                })
            
            # Set post type specific fields
            if post_content.post_type == "OFFER":
                post_data["offer"] = {
                    "couponCode": post_content.coupon_code,
                    "redeemOnlineUrl": post_content.redeem_url,
                    "termsConditions": post_content.terms
                }
            elif post_content.post_type == "EVENT":
                post_data["event"] = {
                    "title": post_content.event_title,
                    "schedule": {
                        "startDate": post_content.start_date,
                        "startTime": post_content.start_time,
                        "endDate": post_content.end_date,
                        "endTime": post_content.end_time
                    }
                }
            
            # API call to create post
            request = self._service.accounts().locations().localPosts().create(
                parent=location_name,
                body=post_data
            )
            
            response = request.execute()
            
            logger.info(f"Created post via API for profile: {gbp_profile.google_location_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google API error creating post: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error creating Google Business Profile post: {str(e)}")
            return False
    
    async def get_profile_data(
        self,
        gbp_profile: GoogleBusinessProfile
    ) -> Optional[Dict[str, Any]]:
        """Get current profile data from Google Business Profile via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            location_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}"
            
            # API call to get profile data
            profile = self._service.accounts().locations().get(
                name=location_name
            ).execute()
            
            return self._extract_profile_data(profile)
            
        except HttpError as e:
            logger.error(f"Google API error fetching profile data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Google Business Profile data: {str(e)}")
            return None
    
    async def update_profile_field(
        self,
        gbp_profile: GoogleBusinessProfile,
        field_name: str,
        field_value: Any
    ) -> bool:
        """Update a specific field in the Google Business Profile via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            location_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}"
            
            # API call to update field
            update_request = self._service.accounts().locations().patch(
                name=location_name,
                body={field_name: field_value},
                updateMask=field_name
            )
            
            response = update_request.execute()
            
            logger.info(f"Updated field {field_name} via API for profile: {gbp_profile.google_location_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google API error updating field: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating Google Business Profile field: {str(e)}")
            return False
    
    async def verify_profile(
        self,
        gbp_profile: GoogleBusinessProfile,
        verification_method: str = "SMS"
    ) -> Dict[str, Any]:
        """Initiate profile verification process via API."""
        
        try:
            if not self._service:
                raise Exception("Google Business Profile service not initialized")
            
            location_name = f"accounts/{settings.GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{gbp_profile.google_location_id}"
            
            # API call to request verification
            verification_request = self._service.accounts().locations().requestVerification(
                name=location_name,
                body={
                    "method": verification_method
                }
            )
            
            response = verification_request.execute()
            
            logger.info(f"Initiated verification via API for profile: {gbp_profile.google_location_id}")
            return {
                "success": True,
                "verification_id": response.get("name"),
                "method": verification_method,
                "status": response.get("state", "PENDING")
            }
            
        except HttpError as e:
            logger.error(f"Google API error initiating verification: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error initiating Google Business Profile verification: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # HELPER METHODS (Infrastructure Only)
    # =====================================
    
    def _extract_profile_data(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize profile data from Google API response."""
        
        return {
            "location_id": location_data.get("name", "").split("/")[-1],
            "name": location_data.get("locationName", ""),
            "place_id": location_data.get("metadata", {}).get("placeId"),
            "address": location_data.get("address", {}),
            "phone": location_data.get("primaryPhone"),
            "website": location_data.get("websiteUri"),
            "categories": location_data.get("categories", []),
            "verification_status": location_data.get("metadata", {}).get("verificationState"),
            "profile_url": f"https://www.google.com/maps/place/?q=place_id:{location_data.get('metadata', {}).get('placeId')}"
        }
