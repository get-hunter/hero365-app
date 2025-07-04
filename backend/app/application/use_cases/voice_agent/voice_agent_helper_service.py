"""
Voice Agent Helper Service

Common helper functionality for voice agent use cases.
Provides shared validation, permission checking, and business logic.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ...dto.voice_session_dto import VoiceSessionResponseDTO
from ...dto.outbound_call_dto import OutboundCallResponseDTO
from app.domain.repositories.voice_session_repository import VoiceSessionRepository
from app.domain.repositories.outbound_call_repository import OutboundCallRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.repositories.job_repository import JobRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.entities.business_membership import BusinessRole
from app.domain.enums import VoiceSessionStatus, CallStatus, AgentType
from ...exceptions.application_exceptions import (
    PermissionDeniedError, NotFoundError, BusinessRuleViolationError, ValidationError
)

logger = logging.getLogger(__name__)


class VoiceAgentHelperService:
    """
    Helper service for voice agent operations.
    
    Provides common functionality for voice session management,
    permission checking, and business rule validation.
    """
    
    def __init__(
        self,
        voice_session_repository: VoiceSessionRepository,
        outbound_call_repository: OutboundCallRepository,
        membership_repository: BusinessMembershipRepository,
        job_repository: Optional[JobRepository] = None,
        project_repository: Optional[ProjectRepository] = None,
        contact_repository: Optional[ContactRepository] = None
    ):
        self.voice_session_repository = voice_session_repository
        self.outbound_call_repository = outbound_call_repository
        self.membership_repository = membership_repository
        self.job_repository = job_repository
        self.project_repository = project_repository
        self.contact_repository = contact_repository
    
    async def check_voice_permission(
        self, 
        business_id: uuid.UUID, 
        user_id: str, 
        permission: str
    ) -> None:
        """
        Check if user has permission for voice operations in business.
        
        Args:
            business_id: Business identifier
            user_id: User identifier
            permission: Required permission name
            
        Raises:
            PermissionDeniedError: If user lacks permission
        """
        try:
            # Get user's membership in the business
            membership = await self.membership_repository.get_by_user_and_business(
                user_id, business_id
            )
            
            if not membership:
                raise PermissionDeniedError("User is not a member of this business")
            
            # Voice permissions mapping
            voice_permissions = {
                "use_voice_assistant": [BusinessRole.OWNER, BusinessRole.ADMIN, BusinessRole.MANAGER, BusinessRole.EMPLOYEE],
                "manage_voice_sessions": [BusinessRole.OWNER, BusinessRole.ADMIN, BusinessRole.MANAGER],
                "schedule_outbound_calls": [BusinessRole.OWNER, BusinessRole.ADMIN, BusinessRole.MANAGER],
                "emergency_scheduling": [BusinessRole.OWNER, BusinessRole.ADMIN, BusinessRole.MANAGER, BusinessRole.EMPLOYEE],
                "voice_analytics": [BusinessRole.OWNER, BusinessRole.ADMIN, BusinessRole.MANAGER],
                "configure_voice_agents": [BusinessRole.OWNER, BusinessRole.ADMIN]
            }
            
            allowed_roles = voice_permissions.get(permission, [])
            
            if membership.role not in allowed_roles:
                raise PermissionDeniedError(f"User role {membership.role.value} cannot perform {permission}")
            
            logger.info(f"Voice permission '{permission}' granted for user {user_id} in business {business_id}")
            
        except Exception as e:
            if isinstance(e, PermissionDeniedError):
                raise
            logger.error(f"Error checking voice permission: {str(e)}")
            raise PermissionDeniedError("Permission check failed")
    
    async def validate_voice_session_limits(
        self, 
        business_id: uuid.UUID, 
        user_id: str,
        agent_type: AgentType
    ) -> None:
        """
        Validate voice session limits for user and business.
        
        Args:
            business_id: Business identifier
            user_id: User identifier
            agent_type: Type of voice agent
            
        Raises:
            BusinessRuleViolationError: If limits exceeded
        """
        try:
            # Check active sessions for user
            active_user_sessions = await self.voice_session_repository.get_active_sessions_by_user(
                business_id, user_id
            )
            
            # Limit active sessions per user (configurable)
            max_sessions_per_user = 3
            if len(active_user_sessions) >= max_sessions_per_user:
                raise BusinessRuleViolationError(
                    f"Maximum active voice sessions per user ({max_sessions_per_user}) exceeded"
                )
            
            # Check business-wide active sessions
            active_business_sessions = await self.voice_session_repository.get_active_sessions_by_business(
                business_id
            )
            
            # Limit active sessions per business (configurable)
            max_sessions_per_business = 20
            if len(active_business_sessions) >= max_sessions_per_business:
                raise BusinessRuleViolationError(
                    f"Maximum active voice sessions per business ({max_sessions_per_business}) exceeded"
                )
            
            # Agent-specific limits
            if agent_type == AgentType.PERSONAL_ASSISTANT:
                # Personal assistants are limited to 1 per user
                assistant_sessions = [s for s in active_user_sessions if s.agent_type == AgentType.PERSONAL_ASSISTANT]
                if len(assistant_sessions) >= 1:
                    raise BusinessRuleViolationError("Only one personal assistant session allowed per user")
            
            logger.info(f"Voice session limits validated for user {user_id} in business {business_id}")
            
        except Exception as e:
            if isinstance(e, BusinessRuleViolationError):
                raise
            logger.error(f"Error validating voice session limits: {str(e)}")
            raise BusinessRuleViolationError("Session limit validation failed")
    
    async def get_business_context_for_voice(
        self, 
        business_id: uuid.UUID, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get business context information for voice agents.
        
        Args:
            business_id: Business identifier
            user_id: User identifier
            
        Returns:
            Dictionary containing business context
        """
        try:
            context = {
                "business_id": str(business_id),
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "capabilities": [],
                "recent_activity": {}
            }
            
            # Get user membership and role
            membership = await self.membership_repository.get_by_user_and_business(
                user_id, business_id
            )
            
            if membership:
                context["user_role"] = membership.role.value
                context["user_permissions"] = self._get_role_permissions(membership.role)
            
            # Get recent jobs if job repository available
            if self.job_repository:
                try:
                    recent_jobs = await self.job_repository.get_recent_jobs(
                        business_id, limit=5
                    )
                    context["recent_activity"]["recent_jobs"] = [
                        {
                            "id": str(job.id),
                            "title": job.title,
                            "status": job.status.value,
                            "scheduled_start": job.scheduled_start.isoformat() if job.scheduled_start else None
                        }
                        for job in recent_jobs
                    ]
                except Exception as e:
                    logger.warning(f"Could not get recent jobs: {str(e)}")
            
            # Get active projects if project repository available
            if self.project_repository:
                try:
                    active_projects = await self.project_repository.search_projects(
                        business_id, filters={"status": "active"}, limit=5
                    )
                    context["recent_activity"]["active_projects"] = [
                        {
                            "id": str(project.id),
                            "name": project.name,
                            "status": project.status.value
                        }
                        for project in active_projects.items
                    ]
                except Exception as e:
                    logger.warning(f"Could not get active projects: {str(e)}")
            
            # Add voice capabilities based on permissions
            context["capabilities"] = self._get_voice_capabilities(membership.role if membership else None)
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting business context for voice: {str(e)}")
            return {
                "business_id": str(business_id),
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Could not load business context"
            }
    
    async def validate_emergency_session(
        self, 
        business_id: uuid.UUID, 
        user_id: str,
        emergency_type: str
    ) -> bool:
        """
        Validate emergency voice session request.
        
        Args:
            business_id: Business identifier
            user_id: User identifier
            emergency_type: Type of emergency
            
        Returns:
            True if emergency session is validated
        """
        try:
            # Check if user has emergency permissions
            await self.check_voice_permission(business_id, user_id, "emergency_scheduling")
            
            # Validate emergency type
            valid_emergency_types = [
                "urgent_job", "equipment_failure", "safety_incident", 
                "client_emergency", "weather_emergency", "supply_shortage"
            ]
            
            if emergency_type not in valid_emergency_types:
                raise ValidationError(f"Invalid emergency type: {emergency_type}")
            
            # Check for recent emergency sessions (prevent abuse)
            recent_emergency_sessions = await self.voice_session_repository.get_recent_emergency_sessions(
                business_id, user_id, hours=1
            )
            
            if len(recent_emergency_sessions) >= 5:
                logger.warning(f"Excessive emergency sessions for user {user_id}")
                # Still allow but log for review
            
            logger.info(f"Emergency voice session validated for {emergency_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating emergency session: {str(e)}")
            return False
    
    def _get_role_permissions(self, role: BusinessRole) -> List[str]:
        """Get list of permissions for a business role."""
        permissions_map = {
            BusinessRole.OWNER: [
                "use_voice_assistant", "manage_voice_sessions", "schedule_outbound_calls",
                "emergency_scheduling", "voice_analytics", "configure_voice_agents"
            ],
            BusinessRole.ADMIN: [
                "use_voice_assistant", "manage_voice_sessions", "schedule_outbound_calls",
                "emergency_scheduling", "voice_analytics", "configure_voice_agents"
            ],
            BusinessRole.MANAGER: [
                "use_voice_assistant", "manage_voice_sessions", "schedule_outbound_calls",
                "emergency_scheduling", "voice_analytics"
            ],
            BusinessRole.EMPLOYEE: [
                "use_voice_assistant", "emergency_scheduling"
            ],
            BusinessRole.CLIENT: []  # Clients typically don't have voice access
        }
        
        return permissions_map.get(role, [])
    
    def _get_voice_capabilities(self, role: Optional[BusinessRole]) -> List[str]:
        """Get list of voice capabilities for a role."""
        if not role:
            return []
        
        capabilities_map = {
            BusinessRole.OWNER: [
                "schedule_jobs", "update_job_status", "get_schedule", "navigate_to_job",
                "add_voice_notes", "check_inventory", "emergency_scheduling", 
                "client_communication", "business_analytics", "team_management",
                "outbound_calling", "campaign_management"
            ],
            BusinessRole.ADMIN: [
                "schedule_jobs", "update_job_status", "get_schedule", "navigate_to_job",
                "add_voice_notes", "check_inventory", "emergency_scheduling",
                "client_communication", "business_analytics", "team_management",
                "outbound_calling", "campaign_management"
            ],
            BusinessRole.MANAGER: [
                "schedule_jobs", "update_job_status", "get_schedule", "navigate_to_job",
                "add_voice_notes", "check_inventory", "emergency_scheduling",
                "client_communication", "business_analytics", "outbound_calling"
            ],
            BusinessRole.EMPLOYEE: [
                "update_job_status", "get_schedule", "navigate_to_job",
                "add_voice_notes", "check_inventory", "emergency_scheduling"
            ],
            BusinessRole.CLIENT: []
        }
        
        return capabilities_map.get(role, [])
    
    async def log_voice_interaction(
        self,
        session_id: uuid.UUID,
        interaction_type: str,
        command: str,
        response: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log voice interaction for analytics and debugging.
        
        Args:
            session_id: Voice session identifier
            interaction_type: Type of interaction (command, response, etc.)
            command: Voice command text
            response: Agent response text
            success: Whether interaction was successful
            metadata: Additional metadata
        """
        try:
            # This would typically be stored in a dedicated analytics/logging system
            # For now, we'll log it for debugging
            logger.info(
                f"Voice Interaction - Session: {session_id}, Type: {interaction_type}, "
                f"Command: {command[:100]}..., Success: {success}"
            )
            
            # In a production system, this would:
            # 1. Store interaction in analytics database
            # 2. Update session analytics
            # 3. Track performance metrics
            # 4. Enable conversation review
            
        except Exception as e:
            logger.error(f"Error logging voice interaction: {str(e)}")
            # Don't fail the main operation if logging fails 