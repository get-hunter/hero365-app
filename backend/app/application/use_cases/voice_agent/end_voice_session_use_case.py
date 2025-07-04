"""
End Voice Session Use Case

Business logic for ending voice sessions and cleaning up resources.
Handles session termination, analytics updates, and LiveKit cleanup.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ...dto.voice_session_dto import VoiceSessionResponseDTO
from ...ports.voice_agent_service import VoiceAgentServicePort
from app.domain.repositories.voice_session_repository import VoiceSessionRepository
from app.domain.enums import VoiceSessionStatus
from ...exceptions.application_exceptions import (
    ValidationError, BusinessRuleViolationError, ApplicationError, NotFoundError
)
from .voice_agent_helper_service import VoiceAgentHelperService

logger = logging.getLogger(__name__)


class EndVoiceSessionUseCase:
    """
    Use case for ending voice sessions.
    
    Handles the complete voice session termination flow including:
    1. Session validation and permission checks
    2. Analytics calculation and updates
    3. LiveKit session cleanup
    4. Resource cleanup and finalization
    """
    
    def __init__(
        self,
        voice_session_repository: VoiceSessionRepository,
        voice_agent_service: VoiceAgentServicePort,
        voice_agent_helper: VoiceAgentHelperService
    ):
        self.voice_session_repository = voice_session_repository
        self.voice_agent_service = voice_agent_service
        self.voice_agent_helper = voice_agent_helper
        logger.info("EndVoiceSessionUseCase initialized")
    
    async def execute(
        self, 
        session_id: uuid.UUID,
        user_id: str, 
        business_id: uuid.UUID,
        reason: Optional[str] = None,
        summary: Optional[str] = None
    ) -> VoiceSessionResponseDTO:
        """
        Execute the end voice session use case.
        
        Args:
            session_id: Voice session identifier
            user_id: User ending the session
            business_id: Business context
            reason: Optional reason for ending session
            summary: Optional session summary
            
        Returns:
            VoiceSessionResponseDTO with final session details
            
        Raises:
            ValidationError: If input validation fails
            NotFoundError: If session not found
            BusinessRuleViolationError: If session cannot be ended
            ApplicationError: If session termination fails
        """
        logger.info(f"Ending voice session {session_id} for user {user_id}")
        
        try:
            # Validate input data
            self._validate_input(session_id, user_id, business_id, reason, summary)
            
            # Get and validate voice session
            session = await self._get_and_validate_session(session_id, business_id, user_id)
            
            # Check if session can be ended
            self._validate_session_can_be_ended(session)
            
            # Calculate session analytics before ending
            session_analytics = await self._calculate_session_analytics(session)
            
            # End the LiveKit voice session
            voice_result = await self.voice_agent_service.end_voice_session(session.id)
            
            if not voice_result.success:
                logger.warning(f"LiveKit session end failed: {voice_result.error_message}")
                # Continue with local cleanup even if LiveKit fails
            
            # Update session with end details
            session.end_session(
                reason=reason or "user_initiated",
                summary=summary,
                final_analytics=session_analytics
            )
            
            # Save updated session
            updated_session = await self.voice_session_repository.update(session)
            
            # Log session end
            await self.voice_agent_helper.log_voice_interaction(
                session_id=session.id,
                interaction_type="session_end",
                command="Session terminated",
                response=f"Voice session ended: {reason or 'user_initiated'}",
                success=True,
                metadata={
                    "session_duration": session_analytics.get("duration_seconds", 0),
                    "commands_processed": session_analytics.get("commands_processed", 0),
                    "reason": reason or "user_initiated",
                    "livekit_cleanup": voice_result.success if voice_result else False
                }
            )
            
            # Convert to response DTO
            response_dto = self._to_response_dto(updated_session, session_analytics)
            
            logger.info(f"Voice session ended successfully: {session.id}")
            return response_dto
            
        except Exception as e:
            logger.error(f"Failed to end voice session: {str(e)}")
            
            if isinstance(e, (ValidationError, NotFoundError, BusinessRuleViolationError)):
                raise
            
            raise ApplicationError(f"Failed to end voice session: {str(e)}")
    
    async def _get_and_validate_session(
        self, 
        session_id: uuid.UUID, 
        business_id: uuid.UUID, 
        user_id: str
    ):
        """Get and validate voice session."""
        session = await self.voice_session_repository.get_by_id(session_id, business_id)
        
        if not session:
            raise NotFoundError("Voice session not found")
        
        if session.user_id != user_id:
            # Allow managers and owners to end sessions
            await self.voice_agent_helper.check_voice_permission(
                business_id, user_id, "manage_voice_sessions"
            )
        
        return session
    
    def _validate_session_can_be_ended(self, session) -> None:
        """Validate that session can be ended."""
        if session.status == VoiceSessionStatus.ENDED:
            raise BusinessRuleViolationError("Session is already ended")
        
        if session.status == VoiceSessionStatus.ERROR:
            # Allow ending error sessions for cleanup
            logger.info(f"Ending session in error state: {session.id}")
    
    async def _calculate_session_analytics(self, session) -> Dict[str, Any]:
        """Calculate final session analytics."""
        try:
            # Calculate session duration
            session_start = session.created_date
            session_end = datetime.utcnow()
            duration_seconds = (session_end - session_start).total_seconds()
            
            # Get session commands count
            commands_processed = 0
            if hasattr(session, 'analytics') and session.analytics:
                commands_processed = session.analytics.commands_processed
            
            # Calculate basic metrics
            analytics = {
                "duration_seconds": int(duration_seconds),
                "duration_minutes": round(duration_seconds / 60, 2),
                "commands_processed": commands_processed,
                "session_start": session_start.isoformat(),
                "session_end": session_end.isoformat(),
                "agent_type": session.agent_type.value,
                "emergency_mode": session.emergency_mode,
                "language": session.language
            }
            
            # Add command success rate if available
            if hasattr(session, 'analytics') and session.analytics:
                total_commands = session.analytics.commands_processed
                successful_commands = session.analytics.successful_commands
                
                if total_commands > 0:
                    analytics["success_rate"] = round(successful_commands / total_commands * 100, 2)
                else:
                    analytics["success_rate"] = 100
                
                analytics["successful_commands"] = successful_commands
                analytics["failed_commands"] = total_commands - successful_commands
                
                # Add response time analytics
                if hasattr(session.analytics, 'average_response_time_ms'):
                    analytics["average_response_time_ms"] = session.analytics.average_response_time_ms
            
            # Add usage efficiency metrics
            if duration_seconds > 0:
                analytics["commands_per_minute"] = round(commands_processed / (duration_seconds / 60), 2) if duration_seconds > 60 else commands_processed
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error calculating session analytics: {str(e)}")
            return {
                "duration_seconds": 0,
                "commands_processed": 0,
                "error": "Analytics calculation failed"
            }
    
    def _validate_input(
        self, 
        session_id: uuid.UUID, 
        user_id: str, 
        business_id: uuid.UUID,
        reason: Optional[str] = None,
        summary: Optional[str] = None
    ) -> None:
        """Validate input parameters."""
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
        
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not session_id:
            raise ValidationError("Session ID is required")
        
        # Validate reason length if provided
        if reason and len(reason) > 100:
            raise ValidationError("Reason must be 100 characters or less")
        
        # Validate summary length if provided
        if summary and len(summary) > 500:
            raise ValidationError("Summary must be 500 characters or less")
    
    def _to_response_dto(
        self, 
        session, 
        session_analytics: Dict[str, Any]
    ) -> VoiceSessionResponseDTO:
        """Convert voice session entity to response DTO."""
        return VoiceSessionResponseDTO(
            id=session.id,
            business_id=session.business_id,
            user_id=session.user_id,
            agent_type=session.agent_type,
            status=session.status,
            language=session.language,
            emergency_mode=session.emergency_mode,
            session_context=session.session_context,
            join_token=None,  # Not needed for ended sessions
            room_name=session.livekit_room_name,
            available_tools=[],  # Not needed for ended sessions
            created_date=session.created_date,
            ended_date=session.ended_date,
            last_activity=session.last_activity,
            end_reason=session.end_reason,
            session_summary=session.session_summary,
            metadata={
                "session_analytics": session_analytics,
                "final_status": session.status.value,
                "cleanup_completed": True
            }
        )