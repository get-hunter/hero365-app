"""
Mobile Voice Integration API for Hero365 LiveKit Agents
Provides endpoints for iOS Swift app to connect to voice agents
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import uuid
import logging
from datetime import datetime, timedelta

from livekit import api
from ..deps import get_current_user, get_business_context
from ..schemas.mobile_voice_schemas import (
    VoiceSessionRequest,
    VoiceSessionResponse,
    SessionStateUpdate,
    VoiceSessionStatusResponse,
    MobileDeviceInfo,
    VoiceSessionStatus
)
from ...livekit_agents.context_management import get_context_manager
from ...livekit_agents.monitoring.metrics import get_metrics
from ...livekit_agents.config import LiveKitConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mobile/voice", tags=["Mobile Voice Integration"])

# Initialize LiveKit API client - lazy initialization
config = LiveKitConfig()
livekit_api = None

def get_livekit_api():
    """Get LiveKit API client with lazy initialization"""
    global livekit_api
    if livekit_api is None:
        # Check if LiveKit is properly configured
        if not config.LIVEKIT_API_KEY or not config.LIVEKIT_API_SECRET:
            raise ValueError(
                "LiveKit API key and secret must be configured. "
                "Please set LIVEKIT_API_KEY and LIVEKIT_API_SECRET environment variables. "
                "For development, you can get free credentials at https://livekit.io/cloud or run a local LiveKit server."
            )
        livekit_api = api.LiveKitAPI(
            config.LIVEKIT_URL,
            config.LIVEKIT_API_KEY,
            config.LIVEKIT_API_SECRET,
        )
    return livekit_api


@router.post("/session/start", response_model=VoiceSessionResponse)
async def start_voice_session(
    request: VoiceSessionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context)
) -> VoiceSessionResponse:
    """
    Start a new voice session with LiveKit agents.
    
    This endpoint:
    1. Creates a new LiveKit room
    2. Generates access tokens for mobile app
    3. Initializes agent context
    4. Starts monitoring and metrics
    """
    try:
        # Extract user_id and business_id from dependencies
        user_id = current_user.get("id") or current_user.get("sub")
        business_id = business_context.get("business_id")
        
        # Generate unique session ID
        session_id = f"hero365_voice_{uuid.uuid4().hex[:12]}"
        room_name = f"voice_session_{session_id}"
        
        logger.info(f"🎙️ Starting voice session {session_id} for user {user_id}")
        
        # Create LiveKit room
        room_config = api.CreateRoomRequest(
            name=room_name,
            empty_timeout=300,  # 5 minutes
            max_participants=2,  # User + Agent
            metadata=f'{{"session_id": "{session_id}", "user_id": "{user_id}", "business_id": "{business_id}"}}'
        )
        
        room = await get_livekit_api().room.create_room(room_config)
        logger.info(f"✅ Created LiveKit room: {room_name}")
        
        # Note: With LiveKit Agents 1.0, agents automatically join rooms when participants connect
        # No manual dispatch is needed - the worker will automatically receive the job
        
        # Generate access token for mobile app
        token = api.AccessToken(config.LIVEKIT_API_KEY, config.LIVEKIT_API_SECRET)
        token.with_identity(f"mobile_user_{user_id}")
        token.with_name(request.device_info.device_name or "Mobile User")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        ))
        
        # Set token expiration (24 hours)
        token.with_ttl(timedelta(hours=24))
        access_token = token.to_jwt()
        
        # Initialize context manager for this session
        context_manager = await get_context_manager()
        await context_manager.initialize_session(session_id, user_id, business_id)
        
        # Set device information in context
        device_context = {
            "device_type": "mobile",
            "device_info": request.device_info.model_dump(),
            "session_type": request.session_type,
            "preferred_agent": request.preferred_agent
        }
        
        from ...livekit_agents.context_management import ContextType
        await context_manager.set_context(session_id, ContextType.BUSINESS_DATA, device_context)
        
        # Start metrics tracking
        logger.info(f"📊 Starting metrics tracking for session {session_id}")
        metrics = await get_metrics()
        logger.info(f"📊 Got metrics instance for session {session_id}")
        await metrics.start_session(session_id, user_id, business_id)
        logger.info(f"📊 Started metrics tracking for session {session_id}")
        
        # Schedule background cleanup only if there's a time limit
        logger.info(f"🔄 Checking for background cleanup for session {session_id}")
        if request.max_duration_minutes is not None:
            logger.info(f"🔄 Adding background cleanup task for session {session_id}")
            background_tasks.add_task(
                schedule_session_cleanup,
                session_id,
                room_name,
                request.max_duration_minutes
            )
        logger.info(f"🔄 Background cleanup check completed for session {session_id}")
        
        # Prepare voice configuration optimized for mobile
        logger.info(f"⚙️ Preparing voice configuration for session {session_id}")
        voice_config = {
            "audio_settings": {
                "sample_rate": 16000,
                "channels": 1,
                "encoding": "opus",
                "noise_suppression": True,
                "echo_cancellation": True,
                "auto_gain_control": True
            },
            "voice_pipeline": {
                "stt_language": request.language or "en-US",
                "tts_voice": "professional_male",  # Optimized for mobile speakers
                "response_timeout": 10000,  # 10 seconds
                "silence_timeout": 3000     # 3 seconds
            },
            "mobile_optimizations": {
                "low_bandwidth_mode": request.device_info.network_type == "cellular",
                "battery_optimization": True,
                "background_audio": request.background_audio_enabled
            }
        }
        logger.info(f"⚙️ Voice configuration prepared for session {session_id}")
        
        logger.info(f"📝 Creating response for session {session_id}")
        response = VoiceSessionResponse(
            session_id=session_id,
            room_name=room_name,
            access_token=access_token,
            livekit_url=config.LIVEKIT_URL,
            voice_config=voice_config,
            agent_capabilities=[
                "Contact management",
                "Job scheduling", 
                "Estimate creation",
                "Weather information",
                "Business analytics",
                "Universal search"
            ],
            session_expires_at=datetime.utcnow() + timedelta(hours=24),
            status=VoiceSessionStatus.active
        )
        
        logger.info(f"🚀 Voice session {session_id} started successfully")
        logger.info(f"📤 Returning response for session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to start voice session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start voice session: {str(e)}"
        )


@router.get("/session/{session_id}/status", response_model=VoiceSessionStatusResponse)
async def get_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
) -> VoiceSessionStatusResponse:
    """Get the current status of a voice session."""
    try:
        # Extract user_id from dependency
        user_id = current_user.get("id") or current_user.get("sub")
        
        # Get context and metrics
        context_manager = await get_context_manager()
        metrics = await get_metrics()
        
        # Get session context
        user_session = await context_manager.get_user_session(session_id)
        if not user_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user access
        if user_session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get session metrics
        session_metrics = await metrics.get_session_metrics(session_id)
        
        # Get conversation history
        conversation_history = await context_manager.get_conversation_history(session_id, limit=10)
        
        # Get agent state
        from ...livekit_agents.context_management import ContextType
        agent_state = await context_manager.get_context(session_id, ContextType.AGENT_STATE)
        
        # Check room status
        room_name = f"voice_session_{session_id}"
        try:
            room_info = await get_livekit_api().room.list_rooms([room_name])
            room_active = len(room_info) > 0 and room_info[0].num_participants > 0
        except:
            room_active = False
        
        status = VoiceSessionStatusResponse(
            session_id=session_id,
            status="active" if room_active else "inactive",
            started_at=user_session.started_at,
            last_activity=user_session.last_activity,
            current_agent=agent_state.get("current_agent", "triage") if agent_state else "triage",
            function_calls_count=session_metrics.function_calls if session_metrics else 0,
            voice_interactions_count=session_metrics.voice_interactions if session_metrics else 0,
            errors_count=session_metrics.errors if session_metrics else 0,
            recent_conversation=conversation_history[-5:] if conversation_history else [],
            room_active=room_active
        )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get session status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session status: {str(e)}"
        )


@router.post("/session/{session_id}/update-state")
async def update_session_state(
    session_id: str,
    update: SessionStateUpdate,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update session state from mobile app."""
    try:
        # Extract user_id from dependency
        user_id = current_user.get("id") or current_user.get("sub")
        
        context_manager = await get_context_manager()
        
        # Verify session exists and user has access
        user_session = await context_manager.get_user_session(session_id)
        if not user_session or user_session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update voice preferences if provided
        if update.voice_preferences:
            await context_manager.update_voice_preferences(
                session_id, 
                update.voice_preferences
            )
        
        # Update device state if provided
        if update.device_state:
            from ...livekit_agents.context_management import ContextType
            business_context = await context_manager.get_business_context(session_id)
            business_context.update({"device_state": update.device_state})
            await context_manager.set_business_context(session_id, business_context)
        
        # Record metrics if provided
        if update.performance_metrics:
            metrics = await get_metrics()
            await metrics.record_event(
                f"mobile_performance_update_{session_id}",
                update.performance_metrics
            )
        
        logger.info(f"📱 Updated session state for {session_id}")
        return {"status": "success", "message": "Session state updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update session state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session state: {str(e)}"
        )


@router.post("/session/{session_id}/end")
async def end_voice_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """End a voice session and cleanup resources."""
    try:
        # Extract user_id from dependency
        user_id = current_user.get("id") or current_user.get("sub")
        
        context_manager = await get_context_manager()
        metrics = await get_metrics()
        
        # Verify session exists and user has access
        user_session = await context_manager.get_user_session(session_id)
        if not user_session or user_session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # End metrics tracking
        await metrics.end_session(session_id)
        
        # Close LiveKit room
        room_name = f"voice_session_{session_id}"
        try:
            await get_livekit_api().room.delete_room(api.DeleteRoomRequest(room=room_name))
            logger.info(f"🏠 Deleted LiveKit room: {room_name}")
        except Exception as e:
            logger.warning(f"Failed to delete room {room_name}: {e}")
        
        # Export session data for analytics
        session_data = await context_manager.export_session_data(session_id)
        
        # Cleanup session context
        await context_manager.cleanup_session(session_id)
        
        logger.info(f"🏁 Voice session {session_id} ended successfully")
        
        # Calculate duration safely
        try:
            if isinstance(user_session.started_at, str):
                started_at = datetime.fromisoformat(user_session.started_at)
            else:
                started_at = user_session.started_at
            duration = (datetime.utcnow() - started_at).total_seconds()
        except Exception as e:
            logger.warning(f"Could not calculate session duration: {e}")
            duration = 0
        
        # Get session metrics safely
        session_metrics = await metrics.get_session_metrics(session_id)
        function_calls = session_metrics.function_calls if session_metrics else 0
        voice_interactions = session_metrics.voice_interactions if session_metrics else 0
        
        return {
            "status": "success",
            "message": "Session ended successfully",
            "session_summary": {
                "duration": duration,
                "function_calls": function_calls,
                "voice_interactions": voice_interactions
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to end session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end session: {str(e)}"
        )


@router.get("/health")
async def voice_system_health() -> Dict[str, Any]:
    """Get voice system health status for mobile monitoring."""
    try:
        metrics = await get_metrics()
        system_metrics = await metrics.get_system_metrics()
        health_status = await metrics.get_health_status()
        
        # Check LiveKit configuration status
        livekit_status = "configured"
        livekit_error = None
        try:
            get_livekit_api()
        except ValueError as e:
            livekit_status = "not_configured"
            livekit_error = str(e)
        
        return {
            "status": health_status["status"] if livekit_status == "configured" else "degraded",
            "active_sessions": system_metrics.active_sessions,
            "total_sessions": system_metrics.total_sessions,
            "error_rate": health_status["error_rate"],
            "uptime": system_metrics.uptime,
            "livekit_status": livekit_status,
            "livekit_error": livekit_error,
            "configuration": {
                "livekit_url": config.LIVEKIT_URL,
                "livekit_api_key_set": bool(config.LIVEKIT_API_KEY),
                "livekit_api_secret_set": bool(config.LIVEKIT_API_SECRET),
                "voice_enabled": config.HERO365_VOICE_ENABLED,
                "max_concurrent_sessions": config.MAX_CONCURRENT_SESSIONS
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get health status: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def schedule_session_cleanup(session_id: str, room_name: str, max_duration_minutes: int):
    """Background task to cleanup session after maximum duration."""
    import asyncio
    
    # Wait for max duration
    await asyncio.sleep(max_duration_minutes * 60)
    
    try:
        # Check if session is still active
        context_manager = await get_context_manager()
        user_session = await context_manager.get_user_session(session_id)
        
        if user_session:
            logger.info(f"⏰ Auto-cleanup session {session_id} after {max_duration_minutes} minutes")
            
            # End metrics tracking
            metrics = await get_metrics()
            await metrics.end_session(session_id)
            
            # Delete room
            try:
                await get_livekit_api().room.delete_room(api.DeleteRoomRequest(room=room_name))
            except:
                pass
            
            # Cleanup context
            await context_manager.cleanup_session(session_id)
            
    except Exception as e:
        logger.error(f"❌ Failed auto-cleanup for session {session_id}: {e}")


@router.get("/agent-capabilities")
async def get_agent_capabilities() -> Dict[str, Any]:
    """Get available agent capabilities for mobile UI."""
    return {
        "triage_agent": {
            "name": "Main Assistant",
            "description": "Your primary AI assistant for all Hero365 operations",
            "capabilities": [
                "Route requests to specialists",
                "Answer general questions",
                "Provide system help",
                "Handle multiple tasks"
            ]
        },
        "contact_specialist": {
            "name": "Contact Manager",
            "description": "Specialized in contact and customer management",
            "capabilities": [
                "Create and update contacts",
                "Search customer database",
                "Validate contact information",
                "Manage customer relationships"
            ]
        },
        "job_specialist": {
            "name": "Job Manager",
            "description": "Specialized in job scheduling and tracking",
            "capabilities": [
                "Create and schedule jobs",
                "Track job progress",
                "Update job status",
                "Generate job reports"
            ]
        },
        "estimate_specialist": {
            "name": "Estimate Manager", 
            "description": "Specialized in estimates and quotes",
            "capabilities": [
                "Create detailed estimates",
                "Convert estimates to invoices",
                "Track estimate status",
                "Generate pricing reports"
            ]
        },
        "scheduling_specialist": {
            "name": "Calendar Manager",
            "description": "Specialized in appointments and scheduling",
            "capabilities": [
                "Book appointments",
                "Check availability",
                "Reschedule meetings",
                "Manage calendar events"
            ]
        }
    } 