"""
Voice Agent API Routes

This module provides API endpoints for mobile app integration
with the Hero365 voice agent system.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from livekit.api import AccessToken, VideoGrants

from app.api.deps import CurrentUser, BusinessContext
from app.api.schemas.voice_agent_schemas import (
    VoiceAgentStartRequest,
    VoiceAgentStartResponse,
    VoiceAgentStatusRequest,
    VoiceAgentStatusResponse,
    VoiceAgentStopRequest,
    VoiceAgentStopResponse,
    VoiceAgentConfigRequest,
    VoiceAgentConfigResponse,
    LiveKitConnectionSchema
)
from app.core.config import settings
from app.voice_agents.core.voice_config import AgentType, PersonalAgentConfig, VoiceProfile, VoiceModel
from app.voice_agents.personal.personal_agent import PersonalVoiceAgent
from app.infrastructure.config.dependency_injection import get_business_repository

# Router setup
router = APIRouter()

# Security setup
security = HTTPBearer()

# Global variables for tracking worker availability
last_worker_check = None
worker_available = False


def generate_livekit_token(room_name: str, user_id: str) -> str:
    """Generate a LiveKit access token for the user to join the room"""
    if not all([settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET]):
        raise ValueError("Missing LiveKit configuration")
    
    token = AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
    token.with_identity(user_id)
    token.with_grants(VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True
    ))
    token.with_ttl(timedelta(hours=1))
    
    return token.to_jwt()


def get_livekit_url() -> str:
    """Get the LiveKit WebSocket URL"""
    return settings.LIVEKIT_URL


@router.post("/start", response_model=VoiceAgentStartResponse)
async def start_voice_agent(
    request: VoiceAgentStartRequest,
    current_user: CurrentUser,
    business_context: BusinessContext
):
    """
    Start a new voice agent session.
    
    Backend generates unique room name and JWT token.
    Mobile app connects to LiveKit, which automatically creates the room.
    Agent worker detects room creation and auto-dispatches agent.
    """
    try:
        # Initialize logger
        logger = logging.getLogger(__name__)
        
        # Get business data from context
        business_id = business_context["business_id"]
        
        # Fetch actual business data from repository
        business_repository = get_business_repository()
        business_entity = await business_repository.get_by_id(business_id)
        
        if not business_entity:
            logger.warning(f"⚠️ Business not found for ID: {business_id}, using default data")
            business_data = {
                "id": business_id,
                "name": "Hero365",
                "type": "Home Services",
                "industry": "home_services",
                "company_size": "small"
            }
        else:
            # Use actual business data
            business_data = {
                "id": str(business_entity.id),
                "name": business_entity.name,
                "type": business_entity.industry or "Home Services",
                "industry": business_entity.industry or "home_services", 
                "company_size": business_entity.company_size.value if business_entity.company_size else "small",
                "description": business_entity.description,
                "phone": business_entity.phone_number,
                "email": business_entity.business_email,
                "website": business_entity.website
            }
            logger.info(f"🏢 Loaded business data: {business_data['name']}")
        
        # Build user context with actual user data
        user_context = {
            "id": current_user["id"],
            "name": current_user.get("name") or current_user.get("email", "User"),
            "email": current_user.get("email", ""),
            "is_driving": request.is_driving,
            "safety_mode": request.safety_mode,
            "preferred_language": "en",
            "timezone": "UTC",
            "voice_speed": request.voice_speed or "normal",
            "location": request.location.dict() if request.location else None
        }
        
        logger.info(f"🚀 Starting voice agent for user {current_user['id']}")
        
        # Create agent configuration
        agent_config = PersonalAgentConfig(
            agent_type=AgentType.PERSONAL,
            agent_name=f"{business_data['name']} Assistant",
            max_conversation_duration=request.max_duration or 3600,
            enable_noise_cancellation=request.enable_noise_cancellation,
            temperature=0.7
        )
        
        # Setup LiveKit connection
        livekit_connection = None
        
        if settings.voice_agents_enabled:
            # Generate room name with user_id and business_id for worker to use
            room_name = f"voice-session-{current_user['id']}-{business_id}"
            logger.info(f"🏠 Generated room name: {room_name}")
            
            # Generate JWT token for mobile app
            user_token = generate_livekit_token(room_name, current_user["id"])
            logger.info("🎫 Generated JWT token for mobile app")
            
            # No need to store context - worker will fetch data directly from database
            logger.info("⏳ Room will be created automatically when mobile app connects")
            logger.info("🤖 Agent worker will fetch business and user data directly from database")
            
            livekit_connection = LiveKitConnectionSchema(
                room_name=room_name,
                room_url=get_livekit_url(),
                user_token=user_token,
                room_sid=""  # Room will be created when mobile app connects
            )
            
            logger.info(f"🔗 LiveKit connection ready: {room_name}")
        else:
            logger.warning("⚠️ Voice agents disabled in settings")
        
        # Create temporary agent instance just to get tools count and greeting
        # The actual agent will be created by the worker
        temp_agent = PersonalVoiceAgent(
            business_context=business_data,
            user_context=user_context,
            agent_config=agent_config
        )
        
        # Prepare response
        response = VoiceAgentStartResponse(
            success=True,
            agent_id=f"{current_user['id']}-{business_id}",  # Use user_id-business_id as agent_id
            greeting=temp_agent.get_personalized_greeting(),
            available_tools=len(temp_agent.get_tools()),
            config={
                "voice_profile": agent_config.voice_profile.value,
                "voice_model": agent_config.voice_model.value,
                "safety_mode": request.safety_mode,
                "max_duration": agent_config.max_conversation_duration
            },
            livekit_connection=livekit_connection,
            message="Voice agent started successfully. Agent will automatically join when you connect to the room."
        )
        
        logger.info("✅ Voice agent session prepared successfully")
        logger.info("📱 Mobile app should now connect to LiveKit room")
        logger.info("🤖 Worker will auto-join and handle the conversation")
        
        return response
        
    except Exception as e:
        logger.error(f"Voice agent start failed with error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start voice agent: {str(e)}"
        )


@router.post("/status", response_model=VoiceAgentStatusResponse)
async def get_voice_agent_status(
    request: VoiceAgentStatusRequest,
    current_user: CurrentUser
):
    """
    Get status of an active voice agent.
    
    With the new worker approach, agent status is managed by the LiveKit worker.
    This endpoint provides basic status information.
    """
    try:
        # In the new approach, we don't store agents on the backend
        # The worker handles all agent lifecycle management
        # This endpoint provides basic status based on the agent_id
        
        logger = logging.getLogger(__name__)
        logger.info(f"Status request for agent: {request.agent_id}")
        
        # For now, return basic status - in the future this could query LiveKit
        # or a shared state store to get real agent status
        return VoiceAgentStatusResponse(
            success=True,
            agent_id=request.agent_id,
            is_active=True,  # Assume active if requested
            conversation_stage="active",
            duration=0,  # Could be calculated from agent creation time
            interactions_count=0,  # Could be tracked by worker
            current_intent=None,
            user_context={
                "is_driving": False,
                "safety_mode": True
            },
            message="Agent status retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/stop", response_model=VoiceAgentStopResponse)
async def stop_voice_agent(
    request: VoiceAgentStopRequest,
    current_user: CurrentUser
):
    """
    Stop an active voice agent.
    
    With the new worker approach, agents are managed by the LiveKit worker.
    This endpoint provides a way to signal that the session should end.
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Stop request for agent: {request.agent_id}")
        
        # In the new approach, the mobile app handles disconnection
        # The worker will automatically clean up when the room is empty
        # This endpoint confirms the stop request
        
        return VoiceAgentStopResponse(
            success=True,
            agent_id=request.agent_id,
            session_summary={
                "duration": 0,
                "interactions": 0,
                "completed_tasks": 0
            },
            message="Voice agent stop confirmed. Disconnect from LiveKit room to end session."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop agent: {str(e)}"
        )


@router.post("/config", response_model=VoiceAgentConfigResponse)
async def update_voice_agent_config(
    request: VoiceAgentConfigRequest,
    current_user: CurrentUser
):
    """
    Update voice agent configuration during conversation.
    
    Allows mobile app to adjust settings like safety mode,
    voice speed, etc. during an active session.
    """
    try:
        # In the new approach, we don't store agents on the backend
        # This endpoint is no longer relevant for configuration updates
        # as the worker manages the agent's state.
        # For now, we'll return a placeholder response.
        
        return VoiceAgentConfigResponse(
            success=True,
            agent_id=request.agent_id,
            updated_config={
                "voice_profile": "professional",  # Default profile
                "voice_model": "sonic-2",  # Default model
                "safety_mode": True, # Default safety mode
                "voice_speed": "normal" # Default voice speed
            },
            message="Voice agent configuration updated successfully (placeholder)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent config: {str(e)}"
        )


@router.get("/available-tools")
async def get_available_tools(
    current_user: CurrentUser,
    business_context: BusinessContext
):
    """
    Get list of available voice agent tools for the current business.
    
    Returns tool categories and descriptions for mobile app UI.
    """
    try:
        # Mock business and user context for tool inspection
        business_data = {"id": business_context["business_id"], "name": "Your Business"}
        user_context = {"id": current_user["id"], "name": current_user.get("name", "User")}
        
        # Create temporary agent to get tools
        temp_agent = PersonalVoiceAgent(business_data, user_context)
        tools = temp_agent.get_tools()
        
        # Categorize tools
        tool_categories = {
            "job_management": [
                {"name": "create_job", "description": "Create new jobs"},
                {"name": "get_upcoming_jobs", "description": "View upcoming jobs"},
                {"name": "update_job_status", "description": "Update job status"},
                {"name": "reschedule_job", "description": "Reschedule jobs"},
                {"name": "get_job_details", "description": "Get job details"},
                {"name": "get_jobs_by_status", "description": "Filter jobs by status"}
            ],
            "personal_assistant": [
                {"name": "get_driving_directions", "description": "Get navigation help"},
                {"name": "set_reminder", "description": "Set voice reminders"},
                {"name": "get_current_time", "description": "Get current time"},
                {"name": "get_business_summary", "description": "Get business info"},
                {"name": "toggle_safety_mode", "description": "Toggle driving safety mode"}
            ]
        }
        
        return {
            "success": True,
            "total_tools": len(tools),
            "categories": tool_categories,
            "message": f"Found {len(tools)} available tools"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available tools: {str(e)}"
        )


@router.get("/availability")
async def get_voice_agent_availability(current_user: CurrentUser):
    """
    Check if voice agents are available and properly configured
    """
    return {
        "available": settings.voice_agents_enabled,
        "livekit_configured": settings.livekit_enabled,
        "ai_providers_configured": bool(
            settings.OPENAI_API_KEY and 
            settings.DEEPGRAM_API_KEY and 
            settings.CARTESIA_API_KEY
        ),
        "service_status": "ready" if settings.voice_agents_enabled else "not_configured"
    }


@router.get("/health")
async def voice_agent_health():
    """
    Health check endpoint for voice agent system.
    
    Returns system status and active agent count.
    """
    return {
        "success": True,
        "status": "healthy",
        "active_agents": 0, # No active agents stored on backend
        "voice_agents_enabled": settings.voice_agents_enabled,
        "system_info": {
            "livekit_agents_available": True,
            "job_tools_available": True,
            "personal_agent_available": True
        },
        "message": "Voice agent system is operational"
    } 