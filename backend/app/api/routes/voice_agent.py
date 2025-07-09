"""
Voice Agent API Routes

This module provides API endpoints for mobile app integration
with the Hero365 voice agent system.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer

from app.api.deps import CurrentUser, BusinessContext
from app.api.schemas.voice_agent_schemas import (
    VoiceAgentStartRequest,
    VoiceAgentStartResponse,
    VoiceAgentStopRequest,
    VoiceAgentStopResponse,
    VoiceAgentStatusRequest,
    VoiceAgentStatusResponse,
    VoiceAgentConfigRequest,
    VoiceAgentConfigResponse,
    LiveKitConnectionSchema
)
from app.core.config import settings
from app.voice_agents.core.voice_config import AgentType, PersonalAgentConfig, VoiceProfile, VoiceModel
from app.infrastructure.external_services.livekit_service import LiveKitService
from app.voice_agents.personal.personal_agent import PersonalVoiceAgent

router = APIRouter()
security = HTTPBearer()

# Global storage for active agents (for API compatibility)
active_agents: Dict[str, PersonalVoiceAgent] = {}

# Initialize LiveKit service
livekit_service = None
livekit_api_available = False

try:
    if settings.LIVEKIT_URL and settings.LIVEKIT_API_KEY and settings.LIVEKIT_API_SECRET:
        livekit_service = LiveKitService()
        livekit_api_available = True
        logger = logging.getLogger(__name__)
        logger.info("✅ LiveKit service initialized successfully")
    else:
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ LiveKit credentials not configured, voice agents will be disabled")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Failed to initialize LiveKit service: {e}")

@router.post("/start", response_model=VoiceAgentStartResponse)
async def start_voice_agent(
    request: VoiceAgentStartRequest,
    current_user: CurrentUser,
    business_context: BusinessContext
):
    """
    Start a new voice agent session.
    
    Creates a new voice agent instance configured for the user's business
    and returns connection details for the mobile app.
    """
    try:
        # Get business data from context
        business_id = business_context["business_id"]
        business_data = {
            "id": business_id,
            "name": "Your Business",  # TODO: Get actual business name from repository
            "type": "Home Services",
            "services": [],
            "company_size": "small"
        }
        
        # Build user context
        user_context = {
            "id": current_user["id"],
            "name": current_user.get("name", "User"),
            "email": current_user.get("email", ""),
            "is_driving": request.is_driving,
            "safety_mode": request.safety_mode,
            "preferred_language": "en",  # Default language
            "timezone": "UTC",  # Default timezone
            "voice_speed": request.voice_speed or "normal",
            "location": request.location.dict() if request.location else None
        }
        
        # Debug logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting voice agent for user {current_user['id']}")
        logger.info(f"Business context: {business_data}")
        logger.info(f"User context: {user_context}")
        
        # Always create a new session for each start request
        # This ensures proper session isolation and worker dispatch
        
        # Clean up any old agents for this user to prevent memory leaks
        agents_to_remove = []
        for existing_agent_id, existing_agent in active_agents.items():
            if (existing_agent.user_context.get("id") == current_user["id"] and 
                existing_agent.business_context.get("id") == business_data["id"]):
                agents_to_remove.append(existing_agent_id)
        
        for agent_id_to_remove in agents_to_remove:
            logger.info(f"Cleaning up old agent: {agent_id_to_remove}")
            del active_agents[agent_id_to_remove]
        
        import uuid
        agent_id = str(uuid.uuid4())
        logger.info(f"Creating new agent with ID: {agent_id}")
        
        # Create agent configuration
        try:
            agent_config = PersonalAgentConfig(
                agent_type=AgentType.PERSONAL,
                agent_name=f"{business_data['name']} Assistant",
                max_conversation_duration=request.max_duration or 3600,
                enable_noise_cancellation=request.enable_noise_cancellation,
                temperature=0.7
            )
            logger.info("Agent configuration created successfully")
        except Exception as e:
            logger.error(f"Failed to create agent configuration: {e}")
            raise e
        
        # Setup LiveKit connection if configured
        livekit_connection = None
        
        if livekit_service and settings.voice_agents_enabled:
            try:
                # Create unique room name for this session
                room_name = f"voice-session-{agent_id}"
                logger.info(f"Creating LiveKit room: {room_name}")
                
                # Store agent context for the worker to use
                # The worker's entrypoint function will extract this from job metadata
                agent_context = {
                    "business_context": business_data,
                    "user_context": user_context,
                    "agent_config": {
                        "agent_id": agent_id,
                        "voice_profile": agent_config.voice_profile.value,
                        "voice_model": agent_config.voice_model.value,
                        "temperature": 0.7,
                        "max_duration": agent_config.max_conversation_duration
                    },
                    "created_at": datetime.now().isoformat(),
                    "interactions": []
                }
                
                # Create LiveKit room with the agent context in metadata
                room_info = await livekit_service.create_voice_session_room(
                    session_id=agent_id,
                    user_id=current_user["id"],
                    room_name=room_name,
                    agent_context=agent_context
                )
                logger.info(f"LiveKit room created: {room_info}")
                
                # Generate user token for mobile app
                user_token = livekit_service.generate_user_token(
                    room_name=room_name,
                    user_id=current_user["id"]
                )
                logger.info("User token generated")
                
                # With automatic dispatch, the worker will automatically handle jobs
                # when users connect to the room - no explicit dispatch needed
                logger.info(f"Room ready for automatic agent dispatch: {room_name}")
                logger.info("Worker will automatically join when user connects")
                
                livekit_connection = LiveKitConnectionSchema(
                    room_name=room_name,
                    room_url=livekit_service.get_connection_url(),
                    user_token=user_token,
                    room_sid=room_info.get("room_sid", "") if room_info else ""
                )
                
            except Exception as e:
                # LiveKit setup failed, log error but continue without it
                logger.error(f"Failed to setup LiveKit connection: {e}")
                import traceback
                logger.error(f"LiveKit error traceback: {traceback.format_exc()}")
                # Continue without LiveKit connection
        
        # Create and store agent for API compatibility
        try:
            logger.info("Creating PersonalVoiceAgent instance...")
            agent = PersonalVoiceAgent(
                business_context=business_data,
                user_context=user_context,
                agent_config=agent_config
            )
            agent.agent_id = agent_id  # Set the same ID
            logger.info("PersonalVoiceAgent created successfully")
        except Exception as e:
            logger.error(f"Failed to create PersonalVoiceAgent: {e}")
            import traceback
            logger.error(f"Agent creation traceback: {traceback.format_exc()}")
            raise e
        
        # Store the room name for reconnection purposes
        if livekit_connection:
            agent.livekit_room_name = livekit_connection.room_name
            logger.info(f"Stored room name in agent: {livekit_connection.room_name}")
        
        # Store active agent for status/stop endpoints
        active_agents[agent_id] = agent
        logger.info(f"Stored agent in active_agents: {agent_id}")
        
        # Initialize agent
        try:
            logger.info("Initializing agent...")
            await agent.on_agent_start()
            logger.info("Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            import traceback
            logger.error(f"Agent initialization traceback: {traceback.format_exc()}")
            raise e
        
        # Prepare response
        try:
            logger.info("Preparing response...")
            response = VoiceAgentStartResponse(
                success=True,
                agent_id=agent_id,
                greeting=agent.get_personalized_greeting(),
                available_tools=len(agent.get_tools()),
                config={
                    "voice_profile": agent_config.voice_profile.value,
                    "voice_model": agent_config.voice_model.value,
                    "safety_mode": request.safety_mode,
                    "max_duration": agent_config.max_conversation_duration
                },
                livekit_connection=livekit_connection,
                message="Voice agent started successfully. Agent will automatically join when you connect to the room."
            )
            logger.info("Response prepared successfully")
            return response
        except Exception as e:
            logger.error(f"Failed to prepare response: {e}")
            import traceback
            logger.error(f"Response preparation traceback: {traceback.format_exc()}")
            raise e
        
    except Exception as e:
        logger = logging.getLogger(__name__)
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
    
    Returns current agent status, conversation metrics,
    and any pending actions.
    """
    try:
        agent = active_agents.get(request.agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice agent not found or has been stopped"
            )
        
        # Calculate session duration
        session_duration = (datetime.now() - agent.created_at).total_seconds()
        
        return VoiceAgentStatusResponse(
            success=True,
            agent_id=agent.agent_id,
            is_active=True,  # Agent is active if found in active_agents
            conversation_stage="active",
            duration=session_duration,
            interactions_count=0,  # Could be tracked by worker in future
            current_intent=None,
            user_context={
                "is_driving": agent.user_context.get("is_driving", False),
                "safety_mode": agent.user_context.get("safety_mode", True)
            },
            message="Agent status retrieved successfully"
        )
        
    except HTTPException:
        raise
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
    
    Gracefully shuts down the agent and returns
    session summary.
    """
    try:
        agent = active_agents.get(request.agent_id)
        
        if not agent:
            # Agent might have already been cleaned up by LiveKit session end
            # This is normal behavior, so return success
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Agent {request.agent_id} not found in active_agents - likely already stopped")
            
            # Agent context is now handled by LiveKit room metadata
            # No need to clean up agent_contexts as it doesn't exist in the new worker pattern
            logger.info(f"Agent context cleanup not needed for {request.agent_id} - handled by LiveKit")
            
            return VoiceAgentStopResponse(
                success=True,
                agent_id=request.agent_id,
                session_summary={
                    "duration": 0,
                    "interactions": 0,
                    "completed_tasks": 0
                },
                message="Voice agent was already stopped"
            )
        
        # Calculate session duration
        session_duration = (datetime.now() - agent.created_at).total_seconds()
        
        # Stop agent
        await agent.on_agent_stop()
        
        # Don't close the LiveKit room on explicit stop - the user might want to reconnect
        # The room will be cleaned up by LiveKit's automatic timeout mechanisms
        if livekit_service and hasattr(agent, 'livekit_room_name') and agent.livekit_room_name:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Keeping room {agent.livekit_room_name} alive for potential reconnection")
        
        # Don't clean up agent context from worker - keep it for reconnection
        # The agent context will be reused when the user reconnects
        
        # Remove agent from active_agents since we're creating fresh sessions
        del active_agents[request.agent_id]
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Agent {request.agent_id} stopped and cleaned up successfully")
        
        return VoiceAgentStopResponse(
            success=True,
            agent_id=request.agent_id,
            session_summary={
                "duration": session_duration,
                "interactions": 0,  # Could be tracked by worker in future
                "completed_tasks": 0  # Could be tracked by worker in future
            },
            message="Voice agent stopped successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop voice agent: {str(e)}"
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
        agent = active_agents.get(request.agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice agent not found"
            )
        
        # Update user context directly
        if request.safety_mode is not None:
            agent.user_context["safety_mode"] = request.safety_mode
            agent.user_context["is_driving"] = request.safety_mode
        
        if request.voice_speed:
            agent.user_context["voice_speed"] = request.voice_speed
        
        # Update location if provided
        if request.location:
            agent.user_context["current_location"] = request.location.dict()
        
        return VoiceAgentConfigResponse(
            success=True,
            agent_id=request.agent_id,
            updated_config={
                "voice_profile": "professional",  # Default profile
                "voice_model": "sonic-2",  # Default model
                "safety_mode": agent.user_context.get("safety_mode", True),
                "voice_speed": agent.user_context.get("voice_speed", "normal")
            },
            message="Voice agent configuration updated successfully"
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
        "active_agents": len(active_agents),
        "voice_agents_enabled": settings.voice_agents_enabled,
        "system_info": {
            "livekit_agents_available": True,
            "job_tools_available": True,
            "personal_agent_available": True
        },
        "message": "Voice agent system is operational"
    } 