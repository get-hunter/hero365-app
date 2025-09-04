"""
Supabase Trade Taxonomy Repository Implementation

Implements trade taxonomy data access operations using Supabase as the database backend.
"""

import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from supabase import Client
from app.domain.entities.trade_taxonomy import (
    TradeProfile,
    TradeActivity,
    MarketSegment,
    BookingField,
    BookingFieldType,
    TradeProfileListRequest,
    TradeActivityListRequest,
    TradeProfileWithActivities,
    ActivityWithTemplates
)
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class SupabaseTradeProfileRepository:
    """Supabase implementation for trade profile operations."""

    def __init__(self, client: Client):
        self.client = client
        self.logger = logging.getLogger(__name__)

    async def get_all_profiles(self, request: TradeProfileListRequest) -> List[TradeProfile]:
        """Get all trade profiles with optional filtering."""
        try:
            query = self.client.table("trade_profiles").select("*")
            
            # Apply filters
            if request.segments:
                query = query.in_("segments", request.segments)
            
            if request.search:
                # Search in name and synonyms
                search_filter = f"name.ilike.%{request.search}%,synonyms.cs.{{{request.search}}}"
                query = query.or_(search_filter)
            
            # Apply ordering
            if request.order_by:
                direction = "desc" if request.order_desc else "asc"
                query = query.order(request.order_by, desc=request.order_desc)
            else:
                query = query.order("name")
            
            # Apply pagination
            if request.limit:
                query = query.limit(request.limit)
            if request.offset:
                query = query.offset(request.offset)
            
            response = query.execute()
            
            return [
                TradeProfile(
                    slug=row["slug"],
                    name=row["name"],
                    synonyms=row.get("synonyms", []),
                    segments=MarketSegment(row.get("segments", "both")),
                    icon=row.get("icon"),
                    description=row.get("description"),
                    created_at=row.get("created_at"),
                    updated_at=row.get("updated_at")
                )
                for row in response.data
            ]
            
        except Exception as e:
            self.logger.error(f"Error fetching trade profiles: {str(e)}")
            raise DatabaseError(f"Failed to fetch trade profiles: {str(e)}")

    async def get_profile_by_slug(self, slug: str) -> Optional[TradeProfile]:
        """Get a trade profile by slug."""
        try:
            response = self.client.table("trade_profiles").select("*").eq("slug", slug).execute()
            
            if not response.data:
                return None
            
            row = response.data[0]
            return TradeProfile(
                slug=row["slug"],
                name=row["name"],
                synonyms=row.get("synonyms", []),
                segments=MarketSegment(row.get("segments", "both")),
                icon=row.get("icon"),
                description=row.get("description"),
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at")
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching trade profile {slug}: {str(e)}")
            raise DatabaseError(f"Failed to fetch trade profile: {str(e)}")

    async def get_profiles_with_activities(self, request: TradeProfileListRequest) -> List[TradeProfileWithActivities]:
        """Get trade profiles with their activities."""
        try:
            # Get profiles first
            profiles = await self.get_all_profiles(request)
            
            # Get activities for each profile
            result = []
            for profile in profiles:
                activities_response = self.client.table("trade_activities").select("*").eq("trade_slug", profile.slug).execute()
                
                activities = [
                    TradeActivity(
                        id=UUID(row["id"]),
                        trade_slug=row["trade_slug"],
                        slug=row["slug"],
                        name=row["name"],
                        synonyms=row.get("synonyms", []),
                        tags=row.get("tags", []),
                        default_booking_fields=[
                            BookingField(**field) if isinstance(field, dict) else BookingField(key=field, type="text", label=field)
                            for field in row.get("default_booking_fields", [])
                        ],
                        required_booking_fields=[
                            BookingField(**field) if isinstance(field, dict) else BookingField(key=field, type="text", label=field)
                            for field in row.get("required_booking_fields", [])
                        ]
                    )
                    for row in activities_response.data
                ]
                
                result.append(TradeProfileWithActivities(
                    profile=profile,
                    activities=activities
                ))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching profiles with activities: {str(e)}")
            raise DatabaseError(f"Failed to fetch profiles with activities: {str(e)}")


class SupabaseTradeActivityRepository:
    """Supabase implementation for trade activity operations."""

    def __init__(self, client: Client):
        self.client = client
        self.logger = logging.getLogger(__name__)

    async def get_activities_by_trade(self, trade_slug: str, request: TradeActivityListRequest) -> List[TradeActivity]:
        """Get activities for a specific trade."""
        try:
            query = self.client.table("trade_activities").select("*").eq("trade_slug", trade_slug)
            
            # Apply filters
            if request.tags:
                query = query.overlaps("tags", request.tags)
            
            if request.search:
                # Search in name and synonyms
                search_filter = f"name.ilike.%{request.search}%,synonyms.cs.{{{request.search}}}"
                query = query.or_(search_filter)
            
            # Apply ordering
            if request.order_by:
                query = query.order(request.order_by, desc=request.order_desc)
            else:
                query = query.order("name")
            
            # Apply pagination
            if request.limit:
                query = query.limit(request.limit)
            if request.offset:
                query = query.offset(request.offset)
            
            response = query.execute()
            
            return [
                TradeActivity(
                    id=UUID(row["id"]),
                    trade_slug=row["trade_slug"],
                    slug=row["slug"],
                    name=row["name"],
                    synonyms=row.get("synonyms", []),
                    tags=row.get("tags", []),
                    default_booking_fields=[
                        BookingField(**field) if isinstance(field, dict) else BookingField(key=field, type="text", label=field)
                        for field in row.get("default_booking_fields", [])
                    ],
                    required_booking_fields=[
                        BookingField(**field) if isinstance(field, dict) else BookingField(key=field, type="text", label=field)
                        for field in row.get("required_booking_fields", [])
                    ]
                )
                for row in response.data
            ]
            
        except Exception as e:
            self.logger.error(f"Error fetching activities for trade {trade_slug}: {str(e)}")
            raise DatabaseError(f"Failed to fetch activities: {str(e)}")

    async def get_activity_by_slug(self, slug: str) -> Optional[TradeActivity]:
        """Get an activity by slug."""
        try:
            response = self.client.table("trade_activities").select("*").eq("slug", slug).execute()
            
            if not response.data:
                return None
            
            row = response.data[0]
            return TradeActivity(
                id=UUID(row["id"]),
                trade_slug=row["trade_slug"],
                slug=row["slug"],
                name=row["name"],
                synonyms=row.get("synonyms", []),
                tags=row.get("tags", []),
                default_booking_fields=[
                    BookingField(**field) for field in row.get("default_booking_fields", [])
                ],
                required_booking_fields=[
                    BookingField(**field) for field in row.get("required_booking_fields", [])
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching activity {slug}: {str(e)}")
            raise DatabaseError(f"Failed to fetch activity: {str(e)}")

    async def get_activities_with_templates(self, trade_slug: str) -> List[ActivityWithTemplates]:
        """Get activities with their service templates."""
        try:
            # Get activities for the trade
            activities = await self.get_activities_by_trade(trade_slug, TradeActivityListRequest())
            
            result = []
            for activity in activities:
                # Get service templates for this activity
                templates_response = self.client.table("service_templates").select("*").eq("activity_slug", activity.slug).execute()
                
                templates = [
                    # Convert to ServiceTemplate objects (simplified for now)
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "description": row.get("description"),
                        "pricing_model": row.get("pricing_model")
                    }
                    for row in templates_response.data
                ]
                
                result.append(ActivityWithTemplates(
                    activity=activity,
                    templates=templates
                ))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching activities with templates for trade {trade_slug}: {str(e)}")
            raise DatabaseError(f"Failed to fetch activities with templates: {str(e)}")