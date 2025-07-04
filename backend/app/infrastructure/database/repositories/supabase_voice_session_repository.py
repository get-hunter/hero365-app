"""
Supabase Voice Session Repository Implementation

Repository implementation using Supabase client SDK for voice session management operations.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json

from supabase import Client

from app.domain.repositories.voice_session_repository import VoiceSessionRepository
from app.domain.entities.voice_session import VoiceSession, VoiceSessionAnalytics, VoiceSessionContext
from app.domain.enums import VoiceSessionStatus, AgentType
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseVoiceSessionRepository(VoiceSessionRepository):
    """
    Supabase client implementation of VoiceSessionRepository.
    
    This repository uses Supabase client SDK for all voice session database operations,
    leveraging RLS, real-time features, and tool execution tracking.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "voice_sessions"
        logger.info(f"SupabaseVoiceSessionRepository initialized with client: {self.client}")
    
    async def create(self, session: VoiceSession) -> VoiceSession:
        """Create a new voice session in Supabase."""
        logger.info(f"create() called for session: {session.id}, user: {session.user_id}, agent: {session.agent_type}")
        
        try:
            session_data = self._session_to_dict(session)
            logger.info(f"Session data prepared: {session_data['id']}")
            
            logger.info("Making request to Supabase table.insert")
            response = self.client.table(self.table_name).insert(session_data).execute()
            logger.info(f"Supabase response received: data={response.data is not None}")
            
            if response.data:
                logger.info(f"Voice session created successfully in Supabase: {response.data[0]['id']}")
                return self._dict_to_session(response.data[0])
            else:
                logger.error("Failed to create voice session - no data returned from Supabase")
                raise DatabaseError("Failed to create voice session - no data returned")
                
        except Exception as e:
            logger.error(f"Exception in create(): {type(e).__name__}: {str(e)}")
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Voice session with room name '{session.livekit_room_name}' already exists")
            raise DatabaseError(f"Failed to create voice session: {str(e)}")
    
    async def get_by_id(self, session_id: uuid.UUID, business_id: uuid.UUID) -> Optional[VoiceSession]:
        """Get voice session by ID within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "id", str(session_id)
            ).eq("business_id", str(business_id)).execute()
            
            if response.data:
                return self._dict_to_session(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get voice session by ID: {str(e)}")
    
    async def update(self, session: VoiceSession) -> VoiceSession:
        """Update an existing voice session."""
        try:
            session_data = self._session_to_dict(session)
            session_data.pop('id', None)  # Remove ID from update data
            session_data.pop('created_at', None)  # Remove created_at from update data
            
            response = self.client.table(self.table_name).update(session_data).eq(
                "id", str(session.id)
            ).eq("business_id", str(session.business_id)).execute()
            
            if response.data:
                return self._dict_to_session(response.data[0])
            else:
                raise EntityNotFoundError(f"Voice session with ID {session.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update voice session: {str(e)}")
    
    async def delete(self, session_id: uuid.UUID, business_id: uuid.UUID) -> bool:
        """Delete a voice session (soft delete by setting status to ended)."""
        try:
            response = self.client.table(self.table_name).update({
                "status": VoiceSessionStatus.ENDED.value,
                "ended_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", str(session_id)).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete voice session: {str(e)}")
    
    async def get_by_room_name(self, room_name: str, business_id: uuid.UUID) -> Optional[VoiceSession]:
        """Get voice session by LiveKit room name within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "livekit_room_name", room_name
            ).eq("business_id", str(business_id)).execute()
            
            if response.data:
                return self._dict_to_session(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get voice session by room name: {str(e)}")
    
    async def get_active_sessions(self, business_id: uuid.UUID) -> List[VoiceSession]:
        """Get all active voice sessions for a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).in_("status", [VoiceSessionStatus.ACTIVE.value, VoiceSessionStatus.PAUSED.value]).order(
                "started_at", desc=True
            ).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active voice sessions: {str(e)}")
    
    async def get_by_user(
        self, 
        user_id: str, 
        business_id: uuid.UUID,
        limit: int = 50, 
        offset: int = 0
    ) -> List[VoiceSession]:
        """Get voice sessions for a specific user within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "user_id", user_id
            ).eq("business_id", str(business_id)).order(
                "started_at", desc=True
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get voice sessions by user: {str(e)}")
    
    async def get_by_agent_type(
        self, 
        agent_type: AgentType, 
        business_id: uuid.UUID,
        limit: int = 50, 
        offset: int = 0
    ) -> List[VoiceSession]:
        """Get voice sessions by agent type within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "agent_type", agent_type.value
            ).eq("business_id", str(business_id)).order(
                "started_at", desc=True
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get voice sessions by agent type: {str(e)}")
    
    async def get_by_status(
        self, 
        status: VoiceSessionStatus, 
        business_id: uuid.UUID,
        limit: int = 50, 
        offset: int = 0
    ) -> List[VoiceSession]:
        """Get voice sessions by status within business context."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "status", status.value
            ).eq("business_id", str(business_id)).order(
                "started_at", desc=True
            ).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get voice sessions by status: {str(e)}")
    
    async def get_expired_sessions(self, business_id: uuid.UUID) -> List[VoiceSession]:
        """Get expired voice sessions that should be cleaned up."""
        try:
            # Calculate cutoff times
            timeout_cutoff = datetime.utcnow() - timedelta(minutes=120)  # Max session timeout
            idle_cutoff = datetime.utcnow() - timedelta(minutes=30)  # Idle timeout
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).in_("status", [VoiceSessionStatus.ACTIVE.value, VoiceSessionStatus.PAUSED.value]).or_(
                f"started_at.lt.{timeout_cutoff.isoformat()},last_activity.lt.{idle_cutoff.isoformat()}"
            ).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get expired voice sessions: {str(e)}")
    
    async def update_tool_execution(
        self, 
        session_id: uuid.UUID, 
        business_id: uuid.UUID,
        tool_name: str, 
        success: bool, 
        execution_time_ms: int,
        result_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update tool execution analytics for a session."""
        try:
            # Get current session to update analytics
            session = await self.get_by_id(session_id, business_id)
            if not session:
                return False
            
            # Update analytics
            analytics = session.analytics
            analytics.total_interactions += 1
            if success:
                analytics.successful_actions += 1
            else:
                analytics.failed_actions += 1
            
            # Update average response time
            if analytics.average_response_time_ms is None:
                analytics.average_response_time_ms = execution_time_ms
            else:
                total_time = analytics.average_response_time_ms * (analytics.total_interactions - 1)
                analytics.average_response_time_ms = (total_time + execution_time_ms) / analytics.total_interactions
            
            # Add to tools used if not already there
            if tool_name not in analytics.tools_used:
                analytics.tools_used.append(tool_name)
            
            # Create execution log entry
            execution_log_entry = {
                "tool_name": tool_name,
                "success": success,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.utcnow().isoformat(),
                "result_summary": result_data.get("summary") if result_data else None
            }
            
            # Update the analytics data in database
            analytics_dict = {
                "total_interactions": analytics.total_interactions,
                "successful_actions": analytics.successful_actions,
                "failed_actions": analytics.failed_actions,
                "average_response_time_ms": analytics.average_response_time_ms,
                "tools_used": analytics.tools_used,
                "tool_execution_log": getattr(session, 'analytics_data', {}).get("tool_execution_log", []) + [execution_log_entry]
            }
            
            response = self.client.table(self.table_name).update({
                "analytics_data": analytics_dict,
                "last_activity": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", str(session_id)).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to update tool execution: {str(e)}")
            return False
    
    async def update_conversation_transcript(
        self, 
        session_id: uuid.UUID, 
        business_id: uuid.UUID,
        new_content: str
    ) -> bool:
        """Update conversation transcript for a session."""
        try:
            # Get current transcript
            session = await self.get_by_id(session_id, business_id)
            if not session:
                return False
            
            # Append new content
            current_transcript = session.conversation_transcript or ""
            updated_transcript = f"{current_transcript}\n{new_content}" if current_transcript else new_content
            
            response = self.client.table(self.table_name).update({
                "conversation_transcript": updated_transcript,
                "last_activity": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", str(session_id)).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to update conversation transcript: {str(e)}")
            return False
    
    async def get_session_analytics(
        self, 
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics for voice sessions within a date range."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if start_date:
                query = query.gte("started_at", start_date.isoformat())
            if end_date:
                query = query.lte("started_at", end_date.isoformat())
            
            response = query.execute()
            sessions = [self._dict_to_session(session_data) for session_data in response.data]
            
            # Calculate analytics
            total_sessions = len(sessions)
            active_sessions = len([s for s in sessions if s.status == VoiceSessionStatus.ACTIVE])
            completed_sessions = len([s for s in sessions if s.status == VoiceSessionStatus.ENDED])
            
            total_interactions = sum(s.analytics.total_interactions for s in sessions)
            total_successful = sum(s.analytics.successful_actions for s in sessions)
            total_failed = sum(s.analytics.failed_actions for s in sessions)
            
            # Calculate average session duration
            completed_sessions_with_duration = [
                s for s in sessions 
                if s.status == VoiceSessionStatus.ENDED and s.started_at and s.ended_at
            ]
            avg_duration_minutes = 0
            if completed_sessions_with_duration:
                total_duration = sum(
                    (s.ended_at - s.started_at).total_seconds() / 60 
                    for s in completed_sessions_with_duration
                )
                avg_duration_minutes = total_duration / len(completed_sessions_with_duration)
            
            # Get top tools used
            tool_usage = {}
            for session in sessions:
                for tool in session.analytics.tools_used:
                    tool_usage[tool] = tool_usage.get(tool, 0) + 1
            
            top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions,
                "total_interactions": total_interactions,
                "successful_actions": total_successful,
                "failed_actions": total_failed,
                "success_rate": (total_successful / total_interactions * 100) if total_interactions > 0 else 0,
                "average_duration_minutes": round(avg_duration_minutes, 2),
                "top_tools_used": top_tools,
                "agent_type_breakdown": self._get_agent_type_breakdown(sessions)
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get session analytics: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total voice sessions for a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count voice sessions: {str(e)}")
    
    async def count_by_status(self, business_id: uuid.UUID, status: VoiceSessionStatus) -> int:
        """Count voice sessions by status within a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count voice sessions by status: {str(e)}")
    
    async def exists(self, session_id: uuid.UUID, business_id: uuid.UUID) -> bool:
        """Check if a voice session exists within business context."""
        try:
            response = self.client.table(self.table_name).select("id").eq(
                "id", str(session_id)
            ).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check voice session existence: {str(e)}")
    
    def _session_to_dict(self, session: VoiceSession) -> Dict[str, Any]:
        """Convert VoiceSession entity to dictionary for database storage."""
        return {
            "id": str(session.id),
            "business_id": str(session.business_id),
            "user_id": session.user_id,
            "agent_type": session.agent_type.value,
            "status": session.status.value,
            "livekit_room_name": session.livekit_room_name,
            "livekit_room_token": session.livekit_room_token,
            "session_timeout_minutes": session.session_timeout_minutes,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "last_activity": session.last_activity.isoformat(),
            "context_data": {
                "current_location": session.context.current_location,
                "current_job_id": str(session.context.current_job_id) if session.context.current_job_id else None,
                "current_contact_id": str(session.context.current_contact_id) if session.context.current_contact_id else None,
                "current_project_id": str(session.context.current_project_id) if session.context.current_project_id else None,
                "session_metadata": session.context.session_metadata,
                "conversation_state": session.context.conversation_state
            },
            "analytics_data": {
                "total_interactions": session.analytics.total_interactions,
                "successful_actions": session.analytics.successful_actions,
                "failed_actions": session.analytics.failed_actions,
                "average_response_time_ms": float(session.analytics.average_response_time_ms) if session.analytics.average_response_time_ms else None,
                "total_duration_seconds": session.analytics.total_duration_seconds,
                "interruption_count": session.analytics.interruption_count,
                "sentiment_score": float(session.analytics.sentiment_score) if session.analytics.sentiment_score else None,
                "confidence_score": float(session.analytics.confidence_score) if session.analytics.confidence_score else None,
                "tools_used": session.analytics.tools_used,
                "tool_execution_log": getattr(session, 'analytics_data', {}).get('tool_execution_log', [])
            },
            "conversation_transcript": session.conversation_transcript,
            "audio_recording_url": session.audio_recording_url,
            "voice_enabled": session.voice_enabled,
            "background_mode": session.background_mode,
            "emergency_mode": session.emergency_mode,
            "session_notes": session.session_notes,
            "error_log": session.error_log,
            "custom_settings": session.custom_settings,
            "created_at": session.started_at.isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def _dict_to_session(self, data: Dict[str, Any]) -> VoiceSession:
        """Convert database dictionary to VoiceSession entity."""
        # Parse context data
        context_data = data.get("context_data", {})
        context = VoiceSessionContext(
            business_id=uuid.UUID(data["business_id"]),
            user_id=data["user_id"],
            agent_type=AgentType(data["agent_type"]),
            current_location=context_data.get("current_location"),
            current_job_id=uuid.UUID(context_data["current_job_id"]) if context_data.get("current_job_id") else None,
            current_contact_id=uuid.UUID(context_data["current_contact_id"]) if context_data.get("current_contact_id") else None,
            current_project_id=uuid.UUID(context_data["current_project_id"]) if context_data.get("current_project_id") else None,
            session_metadata=context_data.get("session_metadata", {}),
            conversation_state=context_data.get("conversation_state", {})
        )
        
        # Parse analytics data
        analytics_data = data.get("analytics_data", {})
        analytics = VoiceSessionAnalytics(
            total_interactions=analytics_data.get("total_interactions", 0),
            successful_actions=analytics_data.get("successful_actions", 0),
            failed_actions=analytics_data.get("failed_actions", 0),
            average_response_time_ms=analytics_data.get("average_response_time_ms"),
            total_duration_seconds=analytics_data.get("total_duration_seconds"),
            interruption_count=analytics_data.get("interruption_count", 0),
            sentiment_score=analytics_data.get("sentiment_score"),
            confidence_score=analytics_data.get("confidence_score"),
            tools_used=analytics_data.get("tools_used", [])
        )
        
        # Create session
        session = VoiceSession(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            user_id=data["user_id"],
            agent_type=AgentType(data["agent_type"]),
            status=VoiceSessionStatus(data["status"]),
            livekit_room_name=data["livekit_room_name"],
            livekit_room_token=data.get("livekit_room_token"),
            session_timeout_minutes=data.get("session_timeout_minutes", 60),
            context=context,
            analytics=analytics,
            started_at=datetime.fromisoformat(data["started_at"].replace('Z', '+00:00')),
            ended_at=datetime.fromisoformat(data["ended_at"].replace('Z', '+00:00')) if data.get("ended_at") else None,
            last_activity=datetime.fromisoformat(data["last_activity"].replace('Z', '+00:00')),
            conversation_transcript=data.get("conversation_transcript"),
            audio_recording_url=data.get("audio_recording_url"),
            voice_enabled=data.get("voice_enabled", True),
            background_mode=data.get("background_mode", False),
            emergency_mode=data.get("emergency_mode", False),
            session_notes=data.get("session_notes"),
            error_log=data.get("error_log", []),
            custom_settings=data.get("custom_settings", {})
        )
        
        # Store raw analytics data for tool execution log
        session.analytics_data = analytics_data
        
        return session
    
    def _get_agent_type_breakdown(self, sessions: List[VoiceSession]) -> Dict[str, int]:
        """Get breakdown of sessions by agent type."""
        breakdown = {}
        for session in sessions:
            agent_type = session.agent_type.get_display()
            breakdown[agent_type] = breakdown.get(agent_type, 0) + 1
        return breakdown

    # Additional abstract methods implementation
    async def get_by_livekit_room(self, business_id: uuid.UUID, room_name: str) -> Optional[VoiceSession]:
        """Get voice session by LiveKit room name."""
        return await self.get_by_room_name(room_name, business_id)
    
    async def get_user_active_session(self, business_id: uuid.UUID, user_id: str) -> Optional[VoiceSession]:
        """Get user's current active session."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("user_id", user_id).eq("status", VoiceSessionStatus.ACTIVE.value).execute()
            
            if response.data:
                return self._dict_to_session(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user active session: {str(e)}")
    
    async def get_idle_sessions(self, business_id: uuid.UUID, idle_minutes: int = 10) -> List[VoiceSession]:
        """Get sessions that are idle."""
        try:
            idle_cutoff = datetime.utcnow() - timedelta(minutes=idle_minutes)
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", VoiceSessionStatus.ACTIVE.value).lt(
                "last_activity", idle_cutoff.isoformat()
            ).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get idle sessions: {str(e)}")
    
    async def end_expired_sessions(self, business_id: uuid.UUID) -> int:
        """End all expired sessions and return count."""
        try:
            expired_sessions = await self.get_expired_sessions(business_id)
            count = 0
            
            for session in expired_sessions:
                session.status = VoiceSessionStatus.ENDED
                session.ended_at = datetime.utcnow()
                await self.update(session)
                count += 1
                
            return count
            
        except Exception as e:
            raise DatabaseError(f"Failed to end expired sessions: {str(e)}")
    
    async def list_by_business(
        self,
        business_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[VoiceSessionStatus] = None,
        agent_type: Optional[AgentType] = None,
        user_id: Optional[str] = None
    ) -> List[VoiceSession]:
        """List voice sessions for a business with optional filtering."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if status:
                query = query.eq("status", status.value)
            if agent_type:
                query = query.eq("agent_type", agent_type.value)
            if user_id:
                query = query.eq("user_id", user_id)
                
            response = query.order("started_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list sessions by business: {str(e)}")
    
    async def list_by_user(
        self,
        business_id: uuid.UUID,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        status: Optional[VoiceSessionStatus] = None
    ) -> List[VoiceSession]:
        """List voice sessions for a specific user."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status.value)
                
            response = query.order("started_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list sessions by user: {str(e)}")
    
    async def search_sessions(
        self,
        business_id: uuid.UUID,
        query: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VoiceSession]:
        """Search sessions by transcript or session notes."""
        try:
            search_query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).ilike("conversation_transcript", f"%{query}%")
            
            if filters:
                if "status" in filters:
                    search_query = search_query.eq("status", filters["status"])
                if "agent_type" in filters:
                    search_query = search_query.eq("agent_type", filters["agent_type"])
                if "user_id" in filters:
                    search_query = search_query.eq("user_id", filters["user_id"])
                    
            response = search_query.order("started_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search sessions: {str(e)}")
    
    async def get_user_session_stats(
        self,
        business_id: uuid.UUID,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get session statistics for a specific user."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("user_id", user_id)
            
            if start_date:
                query = query.gte("started_at", start_date.isoformat())
            if end_date:
                query = query.lte("started_at", end_date.isoformat())
                
            response = query.execute()
            sessions = [self._dict_to_session(session_data) for session_data in response.data]
            
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.status == VoiceSessionStatus.ENDED])
            total_interactions = sum(s.analytics.total_interactions for s in sessions)
            
            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "total_interactions": total_interactions,
                "average_interactions_per_session": total_interactions / total_sessions if total_sessions > 0 else 0
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user session stats: {str(e)}")
    
    async def get_agent_performance_metrics(
        self,
        business_id: uuid.UUID,
        agent_type: AgentType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get performance metrics for agent type."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("agent_type", agent_type.value)
            
            if start_date:
                query = query.gte("started_at", start_date.isoformat())
            if end_date:
                query = query.lte("started_at", end_date.isoformat())
                
            response = query.execute()
            sessions = [self._dict_to_session(session_data) for session_data in response.data]
            
            total_sessions = len(sessions)
            successful_sessions = len([s for s in sessions if s.analytics.successful_actions > s.analytics.failed_actions])
            
            return {
                "total_sessions": total_sessions,
                "successful_sessions": successful_sessions,
                "success_rate": successful_sessions / total_sessions * 100 if total_sessions > 0 else 0,
                "agent_type": agent_type.value
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get agent performance metrics: {str(e)}")
    
    async def get_session_duration_analytics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get session duration analytics."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", VoiceSessionStatus.ENDED.value)
            
            if start_date:
                query = query.gte("started_at", start_date.isoformat())
            if end_date:
                query = query.lte("started_at", end_date.isoformat())
                
            response = query.execute()
            sessions = [self._dict_to_session(session_data) for session_data in response.data]
            
            durations = []
            for session in sessions:
                if session.started_at and session.ended_at:
                    duration = (session.ended_at - session.started_at).total_seconds() / 60
                    durations.append(duration)
            
            if durations:
                return {
                    "average_duration_minutes": sum(durations) / len(durations),
                    "min_duration_minutes": min(durations),
                    "max_duration_minutes": max(durations),
                    "total_sessions": len(durations)
                }
            else:
                return {
                    "average_duration_minutes": 0,
                    "min_duration_minutes": 0,
                    "max_duration_minutes": 0,
                    "total_sessions": 0
                }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get session duration analytics: {str(e)}")
    
    async def get_command_success_rate(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        agent_type: Optional[AgentType] = None
    ) -> Decimal:
        """Get overall command success rate."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if start_date:
                query = query.gte("started_at", start_date.isoformat())
            if end_date:
                query = query.lte("started_at", end_date.isoformat())
            if agent_type:
                query = query.eq("agent_type", agent_type.value)
                
            response = query.execute()
            sessions = [self._dict_to_session(session_data) for session_data in response.data]
            
            total_actions = sum(s.analytics.total_interactions for s in sessions)
            successful_actions = sum(s.analytics.successful_actions for s in sessions)
            
            if total_actions > 0:
                return Decimal(successful_actions / total_actions * 100)
            else:
                return Decimal(0)
            
        except Exception as e:
            raise DatabaseError(f"Failed to get command success rate: {str(e)}")
    
    async def update_session_context(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID,
        context_updates: Dict[str, Any]
    ) -> bool:
        """Update session context data."""
        try:
            session = await self.get_by_id(session_id, business_id)
            if not session:
                return False
                
            # Update context data
            updated_context = session.context.session_metadata.copy()
            updated_context.update(context_updates)
            
            response = self.client.table(self.table_name).update({
                "context_data": {
                    "current_location": session.context.current_location,
                    "current_job_id": str(session.context.current_job_id) if session.context.current_job_id else None,
                    "current_contact_id": str(session.context.current_contact_id) if session.context.current_contact_id else None,
                    "current_project_id": str(session.context.current_project_id) if session.context.current_project_id else None,
                    "session_metadata": updated_context,
                    "conversation_state": session.context.conversation_state
                },
                "last_activity": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", str(session_id)).eq("business_id", str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to update session context: {str(e)}")
            return False
    
    async def add_command_to_session(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID,
        command_id: uuid.UUID,
        success: bool,
        response_time_ms: int
    ) -> bool:
        """Add a processed command to the session."""
        try:
            return await self.update_tool_execution(
                session_id, business_id, f"command_{command_id}", success, response_time_ms
            )
            
        except Exception as e:
            logger.error(f"Failed to add command to session: {str(e)}")
            return False
    
    async def update_session_transcript(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID,
        new_content: str
    ) -> bool:
        """Update session transcript."""
        return await self.update_conversation_transcript(session_id, business_id, new_content)
    
    async def get_sessions_for_mobile(
        self,
        business_id: uuid.UUID,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get sessions optimized for mobile display."""
        try:
            sessions = await self.list_by_user(business_id, user_id, limit, offset)
            
            mobile_sessions = []
            for session in sessions:
                mobile_sessions.append({
                    "id": str(session.id),
                    "status": session.status.value,
                    "agent_type": session.agent_type.value,
                    "started_at": session.started_at.isoformat(),
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                    "duration_minutes": session.analytics.total_duration_seconds / 60 if session.analytics.total_duration_seconds else 0
                })
            
            return {
                "sessions": mobile_sessions,
                "total_count": len(mobile_sessions),
                "page": offset // limit + 1 if limit > 0 else 1
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get sessions for mobile: {str(e)}")
    
    async def get_session_status_updates(
        self,
        business_id: uuid.UUID,
        session_ids: List[uuid.UUID]
    ) -> Dict[uuid.UUID, Dict[str, Any]]:
        """Get status updates for multiple sessions."""
        try:
            session_id_strs = [str(sid) for sid in session_ids]
            response = self.client.table(self.table_name).select("id,status,last_activity").eq(
                "business_id", str(business_id)
            ).in_("id", session_id_strs).execute()
            
            updates = {}
            for session_data in response.data:
                session_id = uuid.UUID(session_data["id"])
                updates[session_id] = {
                    "status": session_data["status"],
                    "last_activity": session_data["last_activity"]
                }
            
            return updates
            
        except Exception as e:
            raise DatabaseError(f"Failed to get session status updates: {str(e)}")
    
    async def get_emergency_sessions(
        self,
        business_id: uuid.UUID,
        active_only: bool = True
    ) -> List[VoiceSession]:
        """Get emergency sessions."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("context_data->>conversation_state", "emergency")
            
            if active_only:
                query = query.eq("status", VoiceSessionStatus.ACTIVE.value)
                
            response = query.order("started_at", desc=True).execute()
            
            return [self._dict_to_session(session_data) for session_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get emergency sessions: {str(e)}")
    
    async def escalate_session_to_emergency(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID
    ) -> bool:
        """Escalate session to emergency status."""
        try:
            return await self.update_session_context(
                business_id, session_id, {"conversation_state": "emergency"}
            )
            
        except Exception as e:
            logger.error(f"Failed to escalate session to emergency: {str(e)}")
            return False
    
    async def bulk_end_sessions(
        self,
        business_id: uuid.UUID,
        session_ids: List[uuid.UUID],
        reason: str
    ) -> int:
        """End multiple sessions at once."""
        try:
            count = 0
            for session_id in session_ids:
                session = await self.get_by_id(session_id, business_id)
                if session:
                    session.status = VoiceSessionStatus.ENDED
                    session.ended_at = datetime.utcnow()
                    await self.update(session)
                    count += 1
            
            return count
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk end sessions: {str(e)}")
    
    async def cleanup_old_sessions(
        self,
        business_id: uuid.UUID,
        older_than_days: int = 30
    ) -> int:
        """Clean up old sessions."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            response = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("status", VoiceSessionStatus.ENDED.value).lt(
                "ended_at", cutoff_date.isoformat()
            ).execute()
            
            session_ids = [uuid.UUID(session["id"]) for session in response.data]
            
            # Delete old sessions
            count = 0
            for session_id in session_ids:
                if await self.delete(session_id, business_id):
                    count += 1
            
            return count
            
        except Exception as e:
            raise DatabaseError(f"Failed to cleanup old sessions: {str(e)}")
    
    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced search with complex filters."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            # Apply filters
            if "status" in filters:
                query = query.eq("status", filters["status"])
            if "agent_type" in filters:
                query = query.eq("agent_type", filters["agent_type"])
            if "user_id" in filters:
                query = query.eq("user_id", filters["user_id"])
            if "start_date" in filters:
                query = query.gte("started_at", filters["start_date"])
            if "end_date" in filters:
                query = query.lte("started_at", filters["end_date"])
                
            # Apply sorting
            sort_column = sort_by or "started_at"
            desc = sort_order.lower() == "desc"
            query = query.order(sort_column, desc=desc)
            
            # Apply pagination
            response = query.range(offset, offset + limit - 1).execute()
            
            sessions = [self._dict_to_session(session_data) for session_data in response.data]
            
            return {
                "sessions": sessions,
                "total_count": len(sessions),
                "page": offset // limit + 1 if limit > 0 else 1,
                "has_more": len(sessions) == limit
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to perform advanced search: {str(e)}")
    
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options."""
        try:
            response = self.client.table(self.table_name).select("status,agent_type,user_id").eq(
                "business_id", str(business_id)
            ).execute()
            
            statuses = list(set(session["status"] for session in response.data))
            agent_types = list(set(session["agent_type"] for session in response.data))
            user_ids = list(set(session["user_id"] for session in response.data))
            
            return {
                "statuses": statuses,
                "agent_types": agent_types,
                "user_ids": user_ids
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get filter options: {str(e)}")
    
    async def count_sessions(
        self,
        business_id: uuid.UUID,
        status: Optional[VoiceSessionStatus] = None,
        agent_type: Optional[AgentType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count sessions with optional filters."""
        try:
            query = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            )
            
            if status:
                query = query.eq("status", status.value)
            if agent_type:
                query = query.eq("agent_type", agent_type.value)
            if start_date:
                query = query.gte("started_at", start_date.isoformat())
            if end_date:
                query = query.lte("started_at", end_date.isoformat())
                
            response = query.execute()
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count sessions: {str(e)}")
    
    async def get_concurrent_session_limit(self, business_id: uuid.UUID) -> int:
        """Get concurrent session limit for business."""
        # This would typically be configured per business
        return 10  # Default limit
    
    async def get_current_concurrent_sessions(self, business_id: uuid.UUID) -> int:
        """Get current concurrent session count."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("status", VoiceSessionStatus.ACTIVE.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to get current concurrent sessions: {str(e)}") 