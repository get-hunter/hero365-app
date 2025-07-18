"""
Mobile Voice Integration API
Enhanced implementation with context preloading
"""

import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from livekit import api

from ...api.deps import get_current_user, get_business_context
from ...api.schemas.mobile_voice_schemas import (
    VoiceSessionRequest,
    VoiceSessionResponse,
    VoiceSessionStatusResponse,
    SessionStateUpdate,
    MobileDeviceInfo,
    VoiceSessionStatus
)
from ...livekit_agents.config import LiveKitConfig
from ...livekit_agents.context_preloader import ContextPreloader

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
    Start a new voice session with LiveKit agents and preloaded business context.
    
    This endpoint:
    1. Preloads business context for the user and business
    2. Creates a new LiveKit room with enriched metadata
    3. Generates access tokens for mobile app
    4. Ensures context is available when the agent starts
    """
    try:
        # Extract user_id and business_id from dependencies
        user_id = current_user.get("id") or current_user.get("sub")
        business_id = business_context.get("business_id")
        
        # Generate unique session ID
        session_id = f"hero365_voice_{uuid.uuid4().hex[:12]}"
        room_name = f"voice_session_{session_id}"
        
        logger.info(f"🎙️ Starting voice session {session_id} for user {user_id}")
        
        # Preload business context
        logger.info(f"🔄 Preloading business context for session {session_id}")
        context_preloader = ContextPreloader()
        preloaded_context = await context_preloader.preload_context(user_id, business_id, current_user)
        
        # Create comprehensive room metadata with preloaded context
        room_metadata = {
            'session_id': session_id,
            'user_id': user_id,
            'business_id': business_id,
            'created_at': datetime.utcnow().isoformat(),
            'device_info': {
                'device_name': request.device_info.device_name,
                'device_model': request.device_info.device_model,
                'os_version': request.device_info.os_version,
                'app_version': request.device_info.app_version,
                'network_type': request.device_info.network_type
            },
            'session_config': {
                'session_type': request.session_type.value,
                'language': request.language,
                'background_audio_enabled': request.background_audio_enabled,
                'max_duration_minutes': request.max_duration_minutes
            },
            # Include user info for fallback loading
            'user_info': {
                'email': current_user.get('email'),
                'user_metadata': current_user.get('user_metadata', {})
            },
            # Include preloaded business context
            'preloaded_context': preloaded_context
        }
        
        # Ensure metadata is JSON serializable
        try:
            metadata_json = json.dumps(room_metadata, ensure_ascii=False, separators=(',', ':'))
            logger.info(f"✅ Room metadata serialized successfully ({len(metadata_json)} characters)")
        except Exception as e:
            logger.error(f"❌ Error serializing room metadata: {e}")
            # Fallback to basic metadata without preloaded context
            room_metadata = {
                'session_id': session_id,
                'user_id': user_id,
                'business_id': business_id,
                'created_at': datetime.utcnow().isoformat(),
                'user_info': {
                    'email': current_user.get('email'),
                    'user_metadata': current_user.get('user_metadata', {})
                },
                'error': 'Context serialization failed',
                'fallback_mode': True
            }
            metadata_json = json.dumps(room_metadata, ensure_ascii=False, separators=(',', ':'))
            logger.warning(f"⚠️ Using fallback metadata due to serialization error")
        
        # Create LiveKit room with enriched metadata
        room_config = api.CreateRoomRequest(
            name=room_name,
            empty_timeout=300,  # 5 minutes
            max_participants=2,  # User + Agent
            metadata=metadata_json
        )
        
        room = await get_livekit_api().room.create_room(room_config)
        logger.info(f"✅ Created LiveKit room: {room_name} with preloaded context")
        
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
        
        # Schedule background cleanup if needed
        if request.max_duration_minutes is not None:
            logger.info(f"🔄 Adding background cleanup task for session {session_id}")
            background_tasks.add_task(
                schedule_session_cleanup,
                session_id,
                room_name,
                request.max_duration_minutes
            )
        
        # Prepare voice configuration optimized for mobile
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
                "tts_voice": "professional_male",
                "response_timeout": 10000,
                "silence_timeout": 3000
            },
            "mobile_optimizations": {
                "low_bandwidth_mode": request.device_info.network_type == "cellular",
                "battery_optimization": True,
                "background_audio": request.background_audio_enabled
            }
        }
        
        # Create response with context status
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
                "Business analytics",
                "Universal search"
            ],
            session_expires_at=datetime.utcnow() + timedelta(hours=24),
            status=VoiceSessionStatus.active
        )
        
        # Log successful creation with context status
        context_status = "✅ with preloaded context" if not preloaded_context.get('error') else "⚠️ with fallback context"
        logger.info(f"🚀 Voice session {session_id} started successfully {context_status}")
        
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
        
        # Session status is now handled by LiveKit agents framework
        # For now, return a basic status response
        logger.info(f"Getting status for session {session_id}")
        
        # Get conversation history
        conversation_history = []  # Simplified - no persistent storage
        
        return VoiceSessionStatusResponse(
            session_id=session_id,
            status=VoiceSessionStatus.active,
            conversation_history=conversation_history,
            session_metrics={
                "duration": 0,
                "messages_exchanged": len(conversation_history),
                "agent_switches": 0
            },
            last_activity=datetime.utcnow()
        )
        
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
        
        # Session state updates are now handled by LiveKit agents framework
        logger.info(f"Session state update for {session_id}: {update.current_agent} - {update.last_action}")
        
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
        
        # Close LiveKit room
        room_name = f"voice_session_{session_id}"
        try:
            await get_livekit_api().room.delete_room(api.DeleteRoomRequest(room=room_name))
            logger.info(f"🏠 Deleted LiveKit room: {room_name}")
        except Exception as e:
            logger.warning(f"Failed to delete room {room_name}: {e}")
        
        logger.info(f"🏁 Voice session {session_id} ended successfully")
        
        return {
            "status": "success",
            "message": "Session ended successfully",
            "session_summary": {
                "duration": 0,
                "function_calls": 0,
                "voice_interactions": 0
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
        # Check LiveKit configuration status
        livekit_status = "configured"
        livekit_error = None
        try:
            get_livekit_api()
        except ValueError as e:
            livekit_status = "not_configured"
            livekit_error = str(e)
        
        return {
            "status": "healthy" if livekit_status == "configured" else "degraded",
            "active_sessions": 0,  # Simplified - no tracking
            "total_sessions": 0,   # Simplified - no tracking
            "error_rate": 0.0,     # Simplified - no tracking
            "uptime": 0,           # Simplified - no tracking
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
    """Schedule cleanup for a voice session after max duration"""
    try:
        import asyncio
        
        # Wait for the specified duration
        await asyncio.sleep(max_duration_minutes * 60)
        
        # Close the room
        await get_livekit_api().room.delete_room(api.DeleteRoomRequest(room=room_name))
        logger.info(f"🧹 Cleaned up expired voice session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up session {session_id}: {e}")


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
        "contact_agent": {
            "name": "Contact Manager",
            "description": "Specialized agent for contact management",
            "capabilities": [
                "Create new contacts",
                "Search contacts",
                "Update contact information",
                "Get contact details"
            ]
        },
        "job_agent": {
            "name": "Job Manager",
            "description": "Specialized agent for job management",
            "capabilities": [
                "Create new jobs",
                "Update job status",
                "Search jobs",
                "Get job details"
            ]
        },
        "estimate_agent": {
            "name": "Estimate Manager",
            "description": "Specialized agent for estimate management",
            "capabilities": [
                "Create estimates",
                "Update estimates",
                "Convert to invoices",
                "Get estimate details"
            ]
        },
        "scheduling_agent": {
            "name": "Scheduler",
            "description": "Specialized agent for scheduling",
            "capabilities": [
                "Check availability",
                "Book appointments",
                "View schedule",
                "Reschedule appointments"
            ]
        }
    } 