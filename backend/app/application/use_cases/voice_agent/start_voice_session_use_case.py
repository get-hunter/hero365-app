"""
Start Voice Session Use Case

Business logic for starting voice sessions with personal assistant or outbound caller agents.
Handles session creation, validation, and LiveKit integration.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ...dto.voice_session_dto import CreateVoiceSessionDTO, VoiceSessionResponseDTO
from ...ports.voice_agent_service import (
    VoiceAgentServicePort, VoiceSessionConfig, VoiceAgentResult
)
from app.domain.repositories.voice_session_repository import VoiceSessionRepository
from app.domain.entities.voice_session import VoiceSession
from app.domain.enums import AgentType, VoiceSessionStatus
from ...exceptions.application_exceptions import (
    ValidationError, BusinessRuleViolationError, ApplicationError
)
from .voice_agent_helper_service import VoiceAgentHelperService

logger = logging.getLogger(__name__)


class StartVoiceSessionUseCase:
    """
    Use case for starting voice sessions.
    
    Handles the complete voice session startup flow including:
    1. Permission validation
    2. Session limit checking
    3. Business context gathering
    4. LiveKit session creation
    5. Agent initialization
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
        logger.info("StartVoiceSessionUseCase initialized")
    
    async def execute(
        self, 
        request: CreateVoiceSessionDTO, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> VoiceSessionResponseDTO:
        """
        Execute the start voice session use case.
        
        Args:
            request: Voice session creation request
            user_id: User starting the session
            business_id: Business context
            
        Returns:
            VoiceSessionResponseDTO with session details and join token
            
        Raises:
            ValidationError: If input validation fails
            BusinessRuleViolationError: If business rules are violated
            ApplicationError: If session creation fails
        """
        logger.info(f"Starting voice session for user {user_id} in business {business_id}")
        
        try:
            # Validate input data
            self._validate_input(request, user_id, business_id)
            
            # Check permissions
            await self.voice_agent_helper.check_voice_permission(
                business_id, user_id, "use_voice_assistant"
            )
            
            # Validate session limits
            await self.voice_agent_helper.validate_voice_session_limits(
                business_id, user_id, request.agent_type
            )
            
            # Handle emergency session validation if needed
            if request.emergency_mode:
                is_valid_emergency = await self.voice_agent_helper.validate_emergency_session(
                    business_id, user_id, request.emergency_type or "urgent_job"
                )
                if not is_valid_emergency:
                    raise BusinessRuleViolationError("Emergency session validation failed")
            
            # Get business context for the voice agent
            business_context = await self.voice_agent_helper.get_business_context_for_voice(
                business_id, user_id
            )
            
            # Create voice session configuration
            voice_config = VoiceSessionConfig(
                agent_type=request.agent_type,
                business_id=business_id,
                user_id=user_id,
                language=request.language or "en-US",
                max_duration_minutes=request.max_duration_minutes or 30,
                emergency_mode=request.emergency_mode or False,
                tools=request.tools,
                custom_instructions=request.custom_instructions
            )
            
            # Create voice session with LiveKit service
            voice_result = await self.voice_agent_service.create_voice_session(voice_config)
            
            if not voice_result.success:
                raise ApplicationError(f"Failed to create voice session: {voice_result.error_message}")
            
            # Create voice session entity
            voice_session = VoiceSession.create_session(
                business_id=business_id,
                user_id=user_id,
                agent_type=request.agent_type,
                language=request.language or "en-US",
                max_duration_minutes=request.max_duration_minutes or 30,
                emergency_mode=request.emergency_mode or False,
                business_context=business_context,
                livekit_room_name=voice_result.room_name
            )
            
            # Update session with LiveKit details
            if voice_result.session_id:
                voice_session.id = voice_result.session_id
            
            # Save session to repository
            created_session = await self.voice_session_repository.create(voice_session)
            
            # Log session start
            await self.voice_agent_helper.log_voice_interaction(
                session_id=created_session.id,
                interaction_type="session_start",
                command="Session initiated",
                response=f"Voice session started with {request.agent_type.value} agent",
                success=True,
                metadata={
                    "agent_type": request.agent_type.value,
                    "emergency_mode": request.emergency_mode,
                    "room_name": voice_result.room_name
                }
            )
            
            # Convert to response DTO
            response_dto = self._to_response_dto(
                created_session, 
                voice_result.join_token,
                voice_result.room_name,
                business_context
            )
            
            logger.info(f"Voice session started successfully: {created_session.id}")
            return response_dto
            
        except Exception as e:
            logger.error(f"Failed to start voice session: {str(e)}")
            
            if isinstance(e, (ValidationError, BusinessRuleViolationError)):
                raise
            
            raise ApplicationError(f"Failed to start voice session: {str(e)}")
    
    def _validate_input(
        self, 
        request: CreateVoiceSessionDTO, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> None:
        """Validate input parameters."""
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
        
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not request.agent_type:
            raise ValidationError("Agent type is required")
        
        # Validate agent type
        if request.agent_type not in [AgentType.PERSONAL_ASSISTANT, AgentType.OUTBOUND_CALLER]:
            raise ValidationError(f"Invalid agent type: {request.agent_type}")
        
        # Validate duration
        if request.max_duration_minutes and (request.max_duration_minutes < 1 or request.max_duration_minutes > 120):
            raise ValidationError("Session duration must be between 1 and 120 minutes")
        
        # Validate language code
        if request.language and not self._is_valid_language_code(request.language):
            raise ValidationError(f"Invalid language code: {request.language}")
        
        # Validate emergency type if emergency mode
        if request.emergency_mode and not request.emergency_type:
            raise ValidationError("Emergency type is required when emergency mode is enabled")
    
    def _is_valid_language_code(self, language: str) -> bool:
        """Validate language code format."""
        valid_languages = [
            "en-US", "en-GB", "es-ES", "es-MX", "fr-FR", "de-DE", 
            "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN", "zh-TW"
        ]
        return language in valid_languages
    
    def _to_response_dto(
        self, 
        session: VoiceSession, 
        join_token: str,
        room_name: str,
        business_context: Dict[str, Any]
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
            join_token=join_token,
            room_name=room_name,
            available_tools=business_context.get("capabilities", []),
            created_date=session.created_date,
            last_activity=session.last_activity,
            metadata={
                "business_context": business_context,
                "session_limits": {
                    "max_duration_minutes": session.max_duration_minutes,
                    "expires_at": (session.created_date.timestamp() + (session.max_duration_minutes * 60)) if session.max_duration_minutes else None
                }
            }
        ) 