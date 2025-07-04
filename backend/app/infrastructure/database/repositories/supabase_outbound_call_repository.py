"""
Supabase Outbound Call Repository Implementation

Repository implementation using Supabase client SDK for outbound call management operations.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from supabase import Client

from app.domain.repositories.outbound_call_repository import OutboundCallRepository
from app.domain.entities.outbound_call import OutboundCall
from app.domain.enums import CallStatus, CallPurpose, CallOutcome
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseOutboundCallRepository(OutboundCallRepository):
    """
    Supabase client implementation of OutboundCallRepository.
    
    This repository uses Supabase client SDK for all outbound call database operations,
    leveraging RLS, real-time features, and campaign tracking.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "outbound_calls"
        logger.info(f"SupabaseOutboundCallRepository initialized with client: {self.client}")
    
    async def create(self, call: OutboundCall) -> OutboundCall:
        """Create a new outbound call in Supabase."""
        logger.info(f"create() called for call: {call.id}, recipient: {call.recipient_phone}, campaign: {call.campaign_id}")
        
        try:
            call_data = self._call_to_dict(call)
            logger.info(f"Call data prepared: {call_data['id']}")
            
            logger.info("Making request to Supabase table.insert")
            response = self.client.table(self.table_name).insert(call_data).execute()
            logger.info(f"Supabase response received: data={response.data is not None}")
            
            if response.data:
                logger.info(f"Outbound call created successfully in Supabase: {response.data[0]['id']}")
                return self._dict_to_call(response.data[0])
            else:
                logger.error("Failed to create outbound call - no data returned from Supabase")
                raise DatabaseError("Failed to create outbound call - no data returned")
                
        except Exception as e:
            logger.error(f"Exception in create(): {type(e).__name__}: {str(e)}")
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Outbound call for recipient '{call.recipient_phone}' already exists in campaign")
            raise DatabaseError(f"Failed to create outbound call: {str(e)}")
    
    async def get_by_id(self, call_id: uuid.UUID, business_id: uuid.UUID) -> Optional[OutboundCall]:
        """Get outbound call by ID within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "id", str(call_id)
            ).eq("business_id", str(business_id)).execute()
            
            if response.data:
                return self._dict_to_call(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get outbound call by ID: {str(e)}")
    
    async def update(self, call: OutboundCall) -> OutboundCall:
        """Update an existing outbound call."""
        try:
            call_data = self._call_to_dict(call)
            call_data.pop('id', None)  # Remove ID from update data
            call_data.pop('created_at', None)  # Remove created_at from update data
            
            response = self.client.table(self.table_name).update(call_data).eq(
                "id", str(call.id)
            ).eq("business_id", str(call.business_id)).execute()
            
            if response.data:
                return self._dict_to_call(response.data[0])
            else:
                raise EntityNotFoundError(f"Outbound call with ID {call.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update outbound call: {str(e)}")
    
    async def delete(self, call_id: uuid.UUID, business_id: uuid.UUID) -> bool:
        """Delete an outbound call (soft delete by setting status to cancelled)."""
        try:
            response = self.client.table(self.table_name).update({
                "status": CallStatus.CANCELLED.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", str(call_id)).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete outbound call: {str(e)}")
    
    async def get_by_campaign(
        self, 
        campaign_id: uuid.UUID, 
        business_id: uuid.UUID,
        limit: int = 100, 
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get outbound calls for a specific campaign within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "campaign_id", str(campaign_id)
            ).eq("business_id", str(business_id)).order(
                "scheduled_at", desc=False
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get outbound calls by campaign: {str(e)}")
    
    async def get_by_status(
        self, 
        status: CallStatus, 
        business_id: uuid.UUID,
        limit: int = 100, 
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get outbound calls by status within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "status", status.value
            ).eq("business_id", str(business_id)).order(
                "scheduled_at", desc=False
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get outbound calls by status: {str(e)}")
    
    async def get_scheduled_calls(
        self, 
        business_id: uuid.UUID,
        before_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OutboundCall]:
        """Get scheduled calls that are ready to be made."""
        try:
            current_time = before_time or datetime.utcnow()
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", CallStatus.SCHEDULED.value).lte(
                "scheduled_at", current_time.isoformat()
            ).order("priority", desc=True).order("scheduled_at", desc=False).limit(limit).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get scheduled calls: {str(e)}")
    
    async def get_retry_calls(
        self, 
        business_id: uuid.UUID,
        max_attempts: int = 3,
        limit: int = 100
    ) -> List[OutboundCall]:
        """Get calls that need to be retried."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", CallStatus.FAILED.value).lt(
                "attempt_count", max_attempts
            ).order("priority", desc=True).order("last_attempted_at", desc=False).limit(limit).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get retry calls: {str(e)}")
    
    async def get_by_contact(
        self, 
        contact_id: uuid.UUID, 
        business_id: uuid.UUID,
        limit: int = 50, 
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get outbound calls for a specific contact within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "contact_id", str(contact_id)
            ).eq("business_id", str(business_id)).order(
                "scheduled_at", desc=True
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get outbound calls by contact: {str(e)}")
    
    async def get_by_date_range(
        self, 
        business_id: uuid.UUID,
        start_date: date, 
        end_date: date,
        limit: int = 1000, 
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get outbound calls within a date range."""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("scheduled_at", start_datetime.isoformat()).lte(
                "scheduled_at", end_datetime.isoformat()
            ).order("scheduled_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get outbound calls by date range: {str(e)}")
    
    async def get_follow_up_calls(
        self, 
        business_id: uuid.UUID,
        due_before: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OutboundCall]:
        """Get calls that need follow-up."""
        try:
            cutoff_time = due_before or datetime.utcnow()
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("requires_follow_up", True).lte(
                "follow_up_date", cutoff_time.isoformat()
            ).order("follow_up_date", desc=False).limit(limit).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get follow-up calls: {str(e)}")
    
    async def update_call_outcome(
        self, 
        call_id: uuid.UUID, 
        business_id: uuid.UUID,
        outcome: CallOutcome, 
        notes: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        follow_up_date: Optional[datetime] = None
    ) -> bool:
        """Update call outcome and related data."""
        try:
            update_data = {
                "outcome": outcome.value,
                "status": CallStatus.COMPLETED.value,
                "completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if notes:
                update_data["outcome_notes"] = notes
            if duration_seconds:
                update_data["duration_seconds"] = duration_seconds
            if follow_up_date:
                update_data["follow_up_date"] = follow_up_date.isoformat()
                update_data["requires_follow_up"] = True
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "id", str(call_id)
            ).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update call outcome: {str(e)}")
    
    async def update_call_status(
        self, 
        call_id: uuid.UUID, 
        business_id: uuid.UUID,
        status: CallStatus,
        attempt_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update call status."""
        try:
            update_data = {
                "status": status.value,
                "last_attempted_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if attempt_count is not None:
                update_data["attempt_count"] = attempt_count
            if error_message:
                update_data["error_message"] = error_message
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "id", str(call_id)
            ).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update call status: {str(e)}")
    
    async def get_campaign_analytics(
        self, 
        campaign_id: uuid.UUID, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get analytics for a specific campaign."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "campaign_id", str(campaign_id)
            ).eq("business_id", str(business_id)).execute()
            
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            # Calculate analytics
            total_calls = len(calls)
            completed_calls = len([c for c in calls if c.status == CallStatus.COMPLETED])
            failed_calls = len([c for c in calls if c.status == CallStatus.FAILED])
            scheduled_calls = len([c for c in calls if c.status == CallStatus.SCHEDULED])
            in_progress_calls = len([c for c in calls if c.status == CallStatus.IN_PROGRESS])
            
            # Calculate outcome breakdown
            outcome_breakdown = {}
            for call in calls:
                if call.outcome:
                    outcome_breakdown[call.outcome.value] = outcome_breakdown.get(call.outcome.value, 0) + 1
            
            # Calculate average duration
            completed_with_duration = [c for c in calls if c.duration_seconds and c.duration_seconds > 0]
            avg_duration = sum(c.duration_seconds for c in completed_with_duration) / len(completed_with_duration) if completed_with_duration else 0
            
            # Calculate success rate (appointments scheduled + sales)
            success_outcomes = [CallOutcome.APPOINTMENT_SCHEDULED.value, CallOutcome.SALE_COMPLETED.value]
            successful_calls = len([c for c in calls if c.outcome and c.outcome.value in success_outcomes])
            success_rate = (successful_calls / completed_calls * 100) if completed_calls > 0 else 0
            
            return {
                "campaign_id": str(campaign_id),
                "total_calls": total_calls,
                "completed_calls": completed_calls,
                "failed_calls": failed_calls,
                "scheduled_calls": scheduled_calls,
                "in_progress_calls": in_progress_calls,
                "completion_rate": (completed_calls / total_calls * 100) if total_calls > 0 else 0,
                "success_rate": round(success_rate, 2),
                "average_duration_seconds": round(avg_duration, 2),
                "outcome_breakdown": outcome_breakdown,
                "calls_requiring_follow_up": len([c for c in calls if c.requires_follow_up])
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get campaign analytics: {str(e)}")
    
    async def get_daily_call_summary(
        self, 
        business_id: uuid.UUID,
        summary_date: date
    ) -> Dict[str, Any]:
        """Get daily call summary for a specific date."""
        try:
            start_datetime = datetime.combine(summary_date, datetime.min.time())
            end_datetime = datetime.combine(summary_date, datetime.max.time())
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("scheduled_at", start_datetime.isoformat()).lte(
                "scheduled_at", end_datetime.isoformat()
            ).execute()
            
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            # Calculate daily metrics
            total_scheduled = len(calls)
            completed_today = len([c for c in calls if c.completed_at and c.completed_at.date() == summary_date])
            failed_today = len([c for c in calls if c.status == CallStatus.FAILED])
            
            return {
                "date": summary_date.isoformat(),
                "total_scheduled": total_scheduled,
                "completed": completed_today,
                "failed": failed_today,
                "pending": total_scheduled - completed_today - failed_today,
                "success_rate": (completed_today / total_scheduled * 100) if total_scheduled > 0 else 0
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get daily call summary: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total outbound calls for a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count outbound calls: {str(e)}")
    
    async def count_by_status(self, business_id: uuid.UUID, status: CallStatus) -> int:
        """Count outbound calls by status within a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count outbound calls by status: {str(e)}")
    
    async def count_by_campaign(self, campaign_id: uuid.UUID, business_id: uuid.UUID) -> int:
        """Count outbound calls for a specific campaign."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "campaign_id", str(campaign_id)
            ).eq("business_id", str(business_id)).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count outbound calls by campaign: {str(e)}")
    
    async def exists(self, call_id: uuid.UUID, business_id: uuid.UUID) -> bool:
        """Check if an outbound call exists within business context."""
        try:
            response = self.client.table(self.table_name).select("id").eq(
                "id", str(call_id)
            ).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check outbound call existence: {str(e)}")
    
    def _call_to_dict(self, call: OutboundCall) -> Dict[str, Any]:
        """Convert OutboundCall entity to dictionary for database storage."""
        return {
            "id": str(call.id),
            "business_id": str(call.business_id),
            "campaign_id": str(call.campaign_id) if call.campaign_id else None,
            "contact_id": str(call.recipient.contact_id) if call.recipient.contact_id else None,
            "recipient_name": call.recipient.name,
            "recipient_phone": call.recipient.phone_number,
            "priority": call.priority,
            "status": call.status.value,
            "purpose": call.purpose.value,
            "outcome": call.outcome.value if call.outcome else None,
            "scheduled_at": call.scheduled_time.isoformat() if call.scheduled_time else None,
            "started_at": call.actual_start_time.isoformat() if call.actual_start_time else None,
            "completed_at": call.actual_end_time.isoformat() if call.actual_end_time else None,
            "duration_seconds": call.analytics.connection_duration_seconds,
            "attempt_count": call.current_attempt,
            "max_attempts": call.max_attempts,
            "last_attempted_at": call.last_modified.isoformat(),
            "script_data": {
                "opening_script": call.script.opening_script,
                "main_script": call.script.main_script,
                "closing_script": call.script.closing_script,
                "call_to_action": call.script.call_to_action,
                "max_duration_minutes": call.script.max_duration_minutes
            },
            "recipient_data": {
                "email": call.recipient.email,
                "preferred_contact_time": call.recipient.preferred_contact_time,
                "time_zone": call.recipient.time_zone,
                "language": call.recipient.language,
                "do_not_call": call.recipient.do_not_call
            },
            "call_recording_url": call.audio_recording_url,
            "conversation_transcript": call.conversation_transcript,
            "outcome_notes": call.outcome_notes,
            "follow_up_date": call.follow_up_date.isoformat() if call.follow_up_date else None,
            "requires_follow_up": call.follow_up_required,
            "analytics_data": {
                "dial_attempts": call.analytics.dial_attempts,
                "connection_duration_seconds": call.analytics.connection_duration_seconds,
                "talk_time_seconds": call.analytics.talk_time_seconds,
                "sentiment_score": float(call.analytics.sentiment_score) if call.analytics.sentiment_score else None,
                "engagement_score": float(call.analytics.engagement_score) if call.analytics.engagement_score else None,
                "interruption_count": call.analytics.interruption_count,
                "objections_raised": call.analytics.objections_raised,
                "questions_asked": call.analytics.questions_asked,
                "questions_answered": call.analytics.questions_answered
            },
            "error_message": None,  # Not in entity
            "created_at": call.created_date.isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def _dict_to_call(self, data: Dict[str, Any]) -> OutboundCall:
        """Convert database dictionary to OutboundCall entity."""
        from app.domain.entities.outbound_call import CallRecipient, CallScript, CallAnalytics
        from decimal import Decimal
        
        # Create recipient object
        recipient_data = data.get("recipient_data", {})
        recipient = CallRecipient(
            contact_id=uuid.UUID(data["contact_id"]) if data.get("contact_id") else None,
            name=data["recipient_name"],
            phone_number=data["recipient_phone"],
            email=recipient_data.get("email"),
            preferred_contact_time=recipient_data.get("preferred_contact_time"),
            time_zone=recipient_data.get("time_zone", "UTC"),
            language=recipient_data.get("language", "en"),
            do_not_call=recipient_data.get("do_not_call", False)
        )
        
        # Create script object
        script_data = data.get("script_data", {})
        script = CallScript(
            opening_script=script_data.get("opening_script", ""),
            main_script=script_data.get("main_script", ""),
            closing_script=script_data.get("closing_script", ""),
            call_to_action=script_data.get("call_to_action", ""),
            max_duration_minutes=script_data.get("max_duration_minutes", 10)
        )
        
        # Create analytics object
        analytics_data = data.get("analytics_data", {})
        analytics = CallAnalytics(
            dial_attempts=analytics_data.get("dial_attempts", 0),
            connection_duration_seconds=analytics_data.get("connection_duration_seconds"),
            talk_time_seconds=analytics_data.get("talk_time_seconds"),
            sentiment_score=Decimal(str(analytics_data["sentiment_score"])) if analytics_data.get("sentiment_score") else None,
            engagement_score=Decimal(str(analytics_data["engagement_score"])) if analytics_data.get("engagement_score") else None,
            interruption_count=analytics_data.get("interruption_count", 0),
            objections_raised=analytics_data.get("objections_raised", 0),
            questions_asked=analytics_data.get("questions_asked", 0),
            questions_answered=analytics_data.get("questions_answered", 0)
        )
        
        return OutboundCall(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            purpose=CallPurpose(data["purpose"]),
            status=CallStatus(data["status"]),
            recipient=recipient,
            script=script,
            campaign_id=uuid.UUID(data["campaign_id"]) if data.get("campaign_id") else None,
            priority=data.get("priority", 1),
            max_attempts=data.get("max_attempts", 3),
            retry_interval_minutes=60,  # Default
            scheduled_time=datetime.fromisoformat(data["scheduled_at"].replace('Z', '+00:00')) if data.get("scheduled_at") else None,
            actual_start_time=datetime.fromisoformat(data["started_at"].replace('Z', '+00:00')) if data.get("started_at") else None,
            actual_end_time=datetime.fromisoformat(data["completed_at"].replace('Z', '+00:00')) if data.get("completed_at") else None,
            current_attempt=data.get("attempt_count", 0),
            session_id=None,  # Not stored in basic table
            livekit_room_name=None,  # Not stored in basic table
            outcome=CallOutcome(data["outcome"]) if data.get("outcome") else None,
            outcome_notes=data.get("outcome_notes"),
            follow_up_required=data.get("requires_follow_up", False),
            follow_up_date=datetime.fromisoformat(data["follow_up_date"].replace('Z', '+00:00')) if data.get("follow_up_date") else None,
            analytics=analytics,
            conversation_transcript=data.get("conversation_transcript"),
            audio_recording_url=data.get("call_recording_url"),
            created_date=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
            last_modified=datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00')) if data.get("updated_at") else datetime.utcnow(),
            created_by="system",  # Default
            tags=[],  # Not stored in basic table
            custom_fields={}  # Not stored in basic table
        )

    # Implementation of missing abstract methods
    
    async def get_by_session_id(self, business_id: uuid.UUID, session_id: uuid.UUID) -> Optional[OutboundCall]:
        """Get outbound call by voice session ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("session_id", str(session_id)).execute()
            
            if response.data:
                return self._dict_to_call(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get outbound call by session ID: {str(e)}")

    async def get_due_calls(
        self,
        business_id: uuid.UUID,
        priority_threshold: int = 1
    ) -> List[OutboundCall]:
        """Get calls that are due to be made."""
        try:
            current_time = datetime.utcnow()
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", CallStatus.SCHEDULED.value).lte(
                "scheduled_at", current_time.isoformat()
            ).gte("priority", priority_threshold).order(
                "priority", desc=True
            ).order("scheduled_at", desc=False).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get due calls: {str(e)}")

    async def get_active_calls(
        self,
        business_id: uuid.UUID,
        include_queued: bool = True
    ) -> List[OutboundCall]:
        """Get currently active calls."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            if include_queued:
                query = query.in_("status", [CallStatus.IN_PROGRESS.value, CallStatus.SCHEDULED.value])
            else:
                query = query.eq("status", CallStatus.IN_PROGRESS.value)
            
            response = query.execute()
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active calls: {str(e)}")

    async def get_next_call_in_queue(
        self,
        business_id: uuid.UUID,
        campaign_id: Optional[uuid.UUID] = None
    ) -> Optional[OutboundCall]:
        """Get next call to be made from queue."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", CallStatus.SCHEDULED.value)
            
            if campaign_id:
                query = query.eq("campaign_id", str(campaign_id))
            
            response = query.order("priority", desc=True).order(
                "scheduled_at", desc=False
            ).limit(1).execute()
            
            if response.data:
                return self._dict_to_call(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get next call in queue: {str(e)}")

    async def list_by_business(
        self,
        business_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[CallStatus] = None,
        purpose: Optional[CallPurpose] = None,
        campaign_id: Optional[uuid.UUID] = None
    ) -> List[OutboundCall]:
        """List outbound calls for a business with optional filtering."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            if status:
                query = query.eq("status", status.value)
            if purpose:
                query = query.eq("purpose", purpose.value)
            if campaign_id:
                query = query.eq("campaign_id", str(campaign_id))
            
            response = query.order("created_at", desc=True).range(
                offset, offset + limit - 1
            ).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list calls by business: {str(e)}")

    async def list_by_campaign(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[CallStatus] = None
    ) -> List[OutboundCall]:
        """List calls for a specific campaign."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("campaign_id", str(campaign_id))
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.order("created_at", desc=True).range(
                offset, offset + limit - 1
            ).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list calls by campaign: {str(e)}")

    async def search_calls(
        self,
        business_id: uuid.UUID,
        query: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[OutboundCall]:
        """Search calls by recipient name, phone, or notes."""
        try:
            search_query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            # Basic text search
            if query:
                search_query = search_query.or_(
                    f"recipient_name.ilike.%{query}%,recipient_phone.ilike.%{query}%,outcome_notes.ilike.%{query}%"
                )
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if key == "status" and value:
                        search_query = search_query.eq("status", value)
                    elif key == "purpose" and value:
                        search_query = search_query.eq("purpose", value)
                    elif key == "campaign_id" and value:
                        search_query = search_query.eq("campaign_id", str(value))
            
            response = search_query.order("created_at", desc=True).range(
                offset, offset + limit - 1
            ).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search calls: {str(e)}")

    async def get_campaign_calls(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID,
        status: Optional[CallStatus] = None,
        outcome: Optional[CallOutcome] = None
    ) -> List[OutboundCall]:
        """Get all calls for a campaign."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("campaign_id", str(campaign_id))
            
            if status:
                query = query.eq("status", status.value)
            if outcome:
                query = query.eq("outcome", outcome.value)
            
            response = query.order("created_at", desc=True).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get campaign calls: {str(e)}")

    async def pause_campaign_calls(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID
    ) -> int:
        """Pause all scheduled calls for a campaign."""
        try:
            response = self.client.table(self.table_name).update({
                "status": CallStatus.PAUSED.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq(
                "campaign_id", str(campaign_id)
            ).eq("status", CallStatus.SCHEDULED.value).execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to pause campaign calls: {str(e)}")

    async def resume_campaign_calls(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID
    ) -> int:
        """Resume all paused calls for a campaign."""
        try:
            response = self.client.table(self.table_name).update({
                "status": CallStatus.SCHEDULED.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq(
                "campaign_id", str(campaign_id)
            ).eq("status", CallStatus.PAUSED.value).execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to resume campaign calls: {str(e)}")

    async def get_calls_by_contact(
        self,
        business_id: uuid.UUID,
        contact_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get all calls for a specific contact."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("contact_id", str(contact_id)).order(
                "created_at", desc=True
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get calls by contact: {str(e)}")

    async def get_calls_by_phone_number(
        self,
        business_id: uuid.UUID,
        phone_number: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get all calls for a specific phone number."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("recipient_phone", phone_number).order(
                "created_at", desc=True
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get calls by phone number: {str(e)}")

    async def check_do_not_call_list(
        self,
        business_id: uuid.UUID,
        phone_number: str
    ) -> bool:
        """Check if phone number is on do-not-call list."""
        try:
            # Check if any call record has do_not_call flag set
            response = self.client.table(self.table_name).select("recipient_data").eq(
                "business_id", str(business_id)
            ).eq("recipient_phone", phone_number).execute()
            
            if response.data:
                for call_data in response.data:
                    recipient_data = call_data.get("recipient_data", {})
                    if recipient_data.get("do_not_call", False):
                        return True
            
            return False
            
        except Exception as e:
            raise DatabaseError(f"Failed to check do-not-call list: {str(e)}")

    async def add_to_do_not_call_list(
        self,
        business_id: uuid.UUID,
        phone_number: str,
        reason: str
    ) -> bool:
        """Add phone number to do-not-call list."""
        try:
            # Update all calls for this phone number to set do_not_call flag
            response = self.client.table(self.table_name).update({
                "recipient_data": {
                    "do_not_call": True,
                    "do_not_call_reason": reason
                },
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq(
                "recipient_phone", phone_number
            ).execute()
            
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to add to do-not-call list: {str(e)}")

    async def get_call_analytics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        purpose: Optional[CallPurpose] = None,
        campaign_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get comprehensive call analytics."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            if purpose:
                query = query.eq("purpose", purpose.value)
            if campaign_id:
                query = query.eq("campaign_id", str(campaign_id))
            
            response = query.execute()
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            # Calculate analytics
            total_calls = len(calls)
            completed_calls = len([c for c in calls if c.status == CallStatus.COMPLETED])
            failed_calls = len([c for c in calls if c.status == CallStatus.FAILED])
            
            return {
                "total_calls": total_calls,
                "completed_calls": completed_calls,
                "failed_calls": failed_calls,
                "success_rate": (completed_calls / total_calls * 100) if total_calls > 0 else 0,
                "average_duration": sum(c.analytics.connection_duration_seconds or 0 for c in calls) / total_calls if total_calls > 0 else 0,
                "total_talk_time": sum(c.analytics.talk_time_seconds or 0 for c in calls),
                "average_engagement_score": sum(float(c.analytics.engagement_score or 0) for c in calls) / total_calls if total_calls > 0 else 0
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get call analytics: {str(e)}")

    async def get_success_rate_by_purpose(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Decimal]:
        """Get success rate by call purpose."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.execute()
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            # Group by purpose and calculate success rates
            purpose_stats = {}
            for call in calls:
                purpose = call.purpose.value
                if purpose not in purpose_stats:
                    purpose_stats[purpose] = {"total": 0, "completed": 0}
                
                purpose_stats[purpose]["total"] += 1
                if call.status == CallStatus.COMPLETED:
                    purpose_stats[purpose]["completed"] += 1
            
            result = {}
            for purpose, stats in purpose_stats.items():
                result[purpose] = Decimal(stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else Decimal(0)
            
            return result
            
        except Exception as e:
            raise DatabaseError(f"Failed to get success rate by purpose: {str(e)}")

    async def get_daily_call_volumes(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get daily call volumes."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.execute()
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            # Group by date
            daily_volumes = {}
            for call in calls:
                date_str = call.created_date.strftime("%Y-%m-%d")
                daily_volumes[date_str] = daily_volumes.get(date_str, 0) + 1
            
            return daily_volumes
            
        except Exception as e:
            raise DatabaseError(f"Failed to get daily call volumes: {str(e)}")

    async def get_agent_performance_metrics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get agent performance metrics."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.execute()
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            total_calls = len(calls)
            completed_calls = len([c for c in calls if c.status == CallStatus.COMPLETED])
            
            if total_calls == 0:
                return {
                    "total_calls": 0,
                    "success_rate": 0,
                    "average_duration": 0,
                    "average_engagement": 0
                }
            
            return {
                "total_calls": total_calls,
                "success_rate": (completed_calls / total_calls * 100),
                "average_duration": sum(c.analytics.connection_duration_seconds or 0 for c in calls) / total_calls,
                "average_engagement": sum(float(c.analytics.engagement_score or 0) for c in calls) / total_calls,
                "total_talk_time": sum(c.analytics.talk_time_seconds or 0 for c in calls)
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get agent performance metrics: {str(e)}")

    async def get_conversion_funnel_data(
        self,
        business_id: uuid.UUID,
        campaign_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get conversion funnel data."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            if campaign_id:
                query = query.eq("campaign_id", str(campaign_id))
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.execute()
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            # Calculate funnel metrics
            total_scheduled = len(calls)
            connected = len([c for c in calls if c.status in [CallStatus.COMPLETED, CallStatus.IN_PROGRESS]])
            completed = len([c for c in calls if c.status == CallStatus.COMPLETED])
            
            return {
                "total_scheduled": total_scheduled,
                "connected": connected,
                "completed": completed,
                "connection_rate": (connected / total_scheduled * 100) if total_scheduled > 0 else 0,
                "completion_rate": (completed / connected * 100) if connected > 0 else 0,
                "overall_success_rate": (completed / total_scheduled * 100) if total_scheduled > 0 else 0
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get conversion funnel data: {str(e)}")

    async def schedule_follow_up(
        self,
        business_id: uuid.UUID,
        original_call_id: uuid.UUID,
        follow_up_date: datetime,
        purpose: CallPurpose,
        notes: Optional[str] = None
    ) -> OutboundCall:
        """Schedule a follow-up call."""
        try:
            # Get original call
            original_call = await self.get_by_id(original_call_id, business_id)
            if not original_call:
                raise EntityNotFoundError(f"Original call {original_call_id} not found")
            
            # Create new follow-up call
            from app.domain.entities.outbound_call import OutboundCall
            
            follow_up_call = OutboundCall(
                business_id=business_id,
                purpose=purpose,
                recipient=original_call.recipient,
                script=original_call.script,
                campaign_id=original_call.campaign_id,
                priority=original_call.priority,
                scheduled_time=follow_up_date,
                tags=original_call.tags + ["follow-up"],
                custom_fields={"original_call_id": str(original_call_id)},
                outcome_notes=notes or f"Follow-up to call {original_call_id}",
                created_by=original_call.created_by
            )
            
            return await self.create(follow_up_call)
            
        except Exception as e:
            raise DatabaseError(f"Failed to schedule follow-up: {str(e)}")

    async def mark_follow_up_completed(
        self,
        business_id: uuid.UUID,
        call_id: uuid.UUID,
        follow_up_call_id: uuid.UUID
    ) -> bool:
        """Mark follow-up as completed."""
        try:
            response = self.client.table(self.table_name).update({
                "requires_follow_up": False,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq(
                "id", str(call_id)
            ).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to mark follow-up completed: {str(e)}")

    async def get_calls_by_outcome(
        self,
        business_id: uuid.UUID,
        outcome: CallOutcome,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OutboundCall]:
        """Get calls by outcome."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("outcome", outcome.value)
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.order("created_at", desc=True).execute()
            
            return [self._dict_to_call(call_data) for call_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get calls by outcome: {str(e)}")

    async def bulk_schedule_calls(
        self,
        business_id: uuid.UUID,
        calls: List[Dict[str, Any]]
    ) -> List[OutboundCall]:
        """Bulk schedule calls."""
        try:
            from app.domain.entities.outbound_call import OutboundCall
            
            created_calls = []
            for call_data in calls:
                call = OutboundCall(
                    business_id=business_id,
                    purpose=CallPurpose(call_data["purpose"]),
                    recipient=call_data["recipient"],
                    script=call_data["script"],
                    campaign_id=call_data.get("campaign_id"),
                    priority=call_data.get("priority", 1),
                    scheduled_time=call_data.get("scheduled_time"),
                    created_by=call_data.get("created_by", "system")
                )
                created_call = await self.create(call)
                created_calls.append(created_call)
            
            return created_calls
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk schedule calls: {str(e)}")

    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        call_ids: List[uuid.UUID],
        status: CallStatus
    ) -> int:
        """Bulk update call status."""
        try:
            call_ids_str = [str(call_id) for call_id in call_ids]
            
            response = self.client.table(self.table_name).update({
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_(
                "id", call_ids_str
            ).execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update status: {str(e)}")

    async def bulk_cancel_calls(
        self,
        business_id: uuid.UUID,
        call_ids: List[uuid.UUID],
        reason: str
    ) -> int:
        """Bulk cancel calls."""
        try:
            call_ids_str = [str(call_id) for call_id in call_ids]
            
            response = self.client.table(self.table_name).update({
                "status": CallStatus.CANCELLED.value,
                "outcome_notes": reason,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_(
                "id", call_ids_str
            ).execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk cancel calls: {str(e)}")

    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced search with filters and sorting."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            )
            
            # Apply filters
            for key, value in filters.items():
                if value is not None:
                    if key == "status":
                        query = query.eq("status", value)
                    elif key == "purpose":
                        query = query.eq("purpose", value)
                    elif key == "campaign_id":
                        query = query.eq("campaign_id", str(value))
                    elif key == "outcome":
                        query = query.eq("outcome", value)
                    elif key == "phone_number":
                        query = query.eq("recipient_phone", value)
                    elif key == "start_date":
                        query = query.gte("created_at", value)
                    elif key == "end_date":
                        query = query.lte("created_at", value)
            
            # Apply sorting
            if sort_by:
                desc = sort_order.lower() == "desc"
                query = query.order(sort_by, desc=desc)
            else:
                query = query.order("created_at", desc=True)
            
            # Get count
            count_response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            total_count = count_response.count or 0
            
            # Get results
            response = query.range(offset, offset + limit - 1).execute()
            calls = [self._dict_to_call(call_data) for call_data in response.data]
            
            return {
                "calls": calls,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to perform advanced search: {str(e)}")

    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options."""
        try:
            response = self.client.table(self.table_name).select(
                "status, purpose, campaign_id, outcome"
            ).eq("business_id", str(business_id)).execute()
            
            statuses = set()
            purposes = set()
            campaigns = set()
            outcomes = set()
            
            for call_data in response.data:
                if call_data.get("status"):
                    statuses.add(call_data["status"])
                if call_data.get("purpose"):
                    purposes.add(call_data["purpose"])
                if call_data.get("campaign_id"):
                    campaigns.add(call_data["campaign_id"])
                if call_data.get("outcome"):
                    outcomes.add(call_data["outcome"])
            
            return {
                "statuses": list(statuses),
                "purposes": list(purposes),
                "campaigns": list(campaigns),
                "outcomes": list(outcomes)
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get filter options: {str(e)}")

    async def count_calls(
        self,
        business_id: uuid.UUID,
        status: Optional[CallStatus] = None,
        purpose: Optional[CallPurpose] = None,
        campaign_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count calls with optional filters."""
        try:
            query = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            )
            
            if status:
                query = query.eq("status", status.value)
            if purpose:
                query = query.eq("purpose", purpose.value)
            if campaign_id:
                query = query.eq("campaign_id", str(campaign_id))
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.execute()
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count calls: {str(e)}")

    async def get_call_queue_size(self, business_id: uuid.UUID) -> int:
        """Get the size of the call queue."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("status", CallStatus.SCHEDULED.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to get call queue size: {str(e)}")

    async def get_average_call_duration(
        self,
        business_id: uuid.UUID,
        purpose: Optional[CallPurpose] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Decimal]:
        """Get average call duration."""
        try:
            query = self.client.table(self.table_name).select("duration_seconds").eq(
                "business_id", str(business_id)
            ).eq("status", CallStatus.COMPLETED.value)
            
            if purpose:
                query = query.eq("purpose", purpose.value)
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.execute()
            
            if not response.data:
                return None
            
            durations = [call["duration_seconds"] for call in response.data if call.get("duration_seconds")]
            if not durations:
                return None
            
            average = sum(durations) / len(durations)
            return Decimal(str(average))
            
        except Exception as e:
            raise DatabaseError(f"Failed to get average call duration: {str(e)}") 