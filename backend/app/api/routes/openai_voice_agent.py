"""
OpenAI Voice Agent API Routes

API endpoints for OpenAI voice agent integration with Hero365.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer

from app.api.deps import CurrentUser, BusinessContext
from app.api.schemas.voice_agent_schemas import (
    VoiceAgentStartRequest,
    VoiceAgentStartResponse,
    VoiceAgentStatusRequest,
    VoiceAgentStatusResponse,
    VoiceAgentStopRequest,
    VoiceAgentStopResponse,
    WebSocketConnectionSchema
)
from app.voice_agents.personal.openai_personal_agent import OpenAIPersonalAgent
from app.voice_agents.orchestration.agent_orchestrator import AgentOrchestrator
from app.infrastructure.config.dependency_injection import get_business_repository

# OpenAI Agents SDK imports for voice processing
try:
    from agents.voice import VoicePipeline, SingleAgentVoiceWorkflow, AudioInput
    from agents import Agent
    VOICE_PIPELINE_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ OpenAI Agents voice pipeline not available. Install with: pip install openai-agents[voice]")
    VOICE_PIPELINE_AVAILABLE = False

# Router setup
router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Active sessions tracking
active_sessions: Dict[str, Dict[str, Any]] = {}


async def _send_greeting_audio(websocket: WebSocket, session_id: str, session: Dict[str, Any]):
    """
    Send greeting audio to the user after WebSocket connection is established.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
        session: Session data dictionary
    """
    try:
        logger.info(f"🎤 Generating greeting audio for session {session_id}")
        
        # Get the agent and generate personalized greeting
        agent = session.get("agent")
        if not agent:
            logger.error(f"❌ No agent found in session {session_id}")
            return
        
        # Get personalized greeting text
        greeting_text = agent.get_personalized_greeting()
        logger.info(f"📝 Greeting text: {greeting_text}")
        
        # Convert text to speech using OpenAI TTS
        from openai import OpenAI
        from app.core.config import settings
        
        if not settings.OPENAI_API_KEY:
            logger.error("❌ OpenAI API key not configured")
            raise ValueError("OpenAI API key not configured")
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Using alloy voice as specified in the config
            input=greeting_text,
            response_format="wav"
        )
        
        # Convert audio to base64 for transmission
        import base64
        audio_base64 = base64.b64encode(response.content).decode('utf-8')
        
        # Send greeting audio to client
        await websocket.send_json({
            "type": "greeting_audio",
            "data": {
                "audio": audio_base64,
                "text": greeting_text,
                "format": "wav",
                "voice": "alloy"
            },
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Greeting audio sent for session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Error generating greeting audio: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Send text fallback if audio generation fails
        try:
            await websocket.send_json({
                "type": "greeting_text",
                "data": {
                    "text": session["greeting"],
                    "message": "Audio greeting failed, sending text fallback"
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as fallback_error:
            logger.error(f"❌ Fallback greeting also failed: {fallback_error}")


async def _process_with_voice_pipeline(websocket: WebSocket, session_id: str, audio_array, session: Dict[str, Any]):
    """
    Process audio using OpenAI Agents VoicePipeline following the quickstart guide pattern
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
        audio_array: Numpy array of audio data
        session: Session data dictionary
    """
    if not VOICE_PIPELINE_AVAILABLE:
        await websocket.send_json({
            "type": "error",
            "message": "Voice pipeline not available. Please install openai-agents[voice]",
            "timestamp": datetime.now().isoformat()
        })
        return
    
    try:
        logger.info(f"🎤 Processing audio with VoicePipeline for session {session_id}")
        
        # Get the pre-created voice pipeline from session
        voice_pipeline = session.get("voice_pipeline")
        if not voice_pipeline:
            logger.error(f"❌ No voice pipeline found in session {session_id}")
            await websocket.send_json({
                "type": "error",
                "message": "Voice pipeline not initialized in session",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # Create audio input following the quickstart guide
        audio_input = AudioInput(buffer=audio_array)
        
        logger.info(f"🎤 Running voice pipeline with {len(audio_array)} audio samples...")
        
        # Process through voice pipeline following the quickstart guide pattern
        result = await voice_pipeline.run(audio_input)
        
        # Stream results as recommended in the quickstart guide
        response_chunks = []
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                # Convert audio data to base64 for transmission
                import base64
                audio_base64 = base64.b64encode(event.data).decode('utf-8')
                
                # Stream audio back to client
                await websocket.send_json({
                    "type": "audio_response",
                    "data": {
                        "audio": audio_base64,
                        "format": "pcm16",
                        "sample_rate": 16000
                    },
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                response_chunks.append(event.data)
                logger.info(f"🎵 Streamed audio chunk ({len(event.data)} bytes)")
            
            elif event.type == "voice_stream_event_transcript":
                # Send transcript to client
                await websocket.send_json({
                    "type": "transcript",
                    "data": {
                        "text": event.text,
                        "is_final": event.is_final
                    },
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"📝 Transcript: {event.text}")
        
        # Send completion message
        await websocket.send_json({
            "type": "audio_response_complete",
            "message": "Voice processing completed",
            "chunks_sent": len(response_chunks),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Voice pipeline completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Voice pipeline error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        await websocket.send_json({
            "type": "error",
            "message": f"Voice pipeline processing failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


@router.post("/openai/start", response_model=VoiceAgentStartResponse)
async def start_openai_voice_agent(
    request: VoiceAgentStartRequest,
    current_user: CurrentUser,
    business_context: BusinessContext
):
    """
    Start a new OpenAI voice agent session.
    
    Creates a WebSocket endpoint for real-time voice communication
    using OpenAI's voice agents SDK.
    """
    try:
        logger.info(f"🚀 Starting OpenAI voice agent for user {current_user['id']}")
        
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
                "industry": "home_services"
            }
        else:
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
        
        # Build user context
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
        
        # Generate session ID
        session_id = f"openai_voice_{current_user['id']}_{business_id}_{uuid4().hex[:8]}"
        
        # Create agent based on request type
        if request.agent_type == "orchestrated":
            # Use orchestrated workflow with specialized agents
            agent = AgentOrchestrator(business_data, user_context)
            greeting = f"Hi! I'm your {business_data['name']} assistant. I can help you with jobs, projects, invoices, estimates, and contacts. I'll route you to the right specialist for your needs. What would you like to do?"
            available_tools = 25  # Approximate total across all specialized agents
        else:
            # Use personal agent (default)
            agent = OpenAIPersonalAgent(business_data, user_context)
            greeting = agent.get_personalized_greeting()
            available_tools = len(agent.get_tools())
        
        # Create VoicePipeline following the quickstart guide
        voice_pipeline = None
        if VOICE_PIPELINE_AVAILABLE:
            try:
                voice_workflow = SingleAgentVoiceWorkflow(agent.create_voice_optimized_agent())
                voice_pipeline = VoicePipeline(workflow=voice_workflow)
                logger.info(f"✅ VoicePipeline created successfully for session {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to create VoicePipeline: {e}")
                # Continue without VoicePipeline - will fall back to basic functionality
        else:
            logger.warning("⚠️ VoicePipeline not available, session will run without voice processing")
        
        # Store session information
        active_sessions[session_id] = {
            "user_id": current_user["id"],
            "business_id": business_id,
            "agent_type": request.agent_type or "personal",
            "business_context": business_data,
            "user_context": user_context,
            "agent": agent,  # Store the agent instance
            "greeting": greeting,  # Store the greeting text
            "voice_pipeline": voice_pipeline,  # Store the voice pipeline
            "created_at": datetime.now(),
            "status": "active"
        }
        
        # Prepare WebSocket connection details
        from app.core.config import settings
        
        # Generate WebSocket URL based on environment
        if settings.ENVIRONMENT == "local":
            websocket_base_url = "ws://localhost:8000"
        elif settings.ENVIRONMENT == "production":
            websocket_base_url = f"wss://{settings.API_DOMAIN}"
        else:  # staging
            websocket_base_url = "ws://localhost:8000"
        
        # Include the correct API prefix and voice-agent prefix
        websocket_path = f"{settings.API_V1_STR}/voice-agent/ws/{session_id}"
        
        websocket_connection = WebSocketConnectionSchema(
            websocket_url=f"{websocket_base_url}{websocket_path}",
            session_id=session_id,
            audio_format="pcm16",
            sample_rate=16000
        )
        
        response = VoiceAgentStartResponse(
            success=True,
            session_id=session_id,
            agent_type=request.agent_type or "personal",
            greeting=greeting,
            available_tools=available_tools,
            websocket_connection=websocket_connection,
            agent_config={
                "voice_model": request.voice_model or "gpt-4o-realtime-preview",
                "voice_settings": request.voice_settings or {
                    "voice": "alloy",
                    "speed": 1.0,
                    "format": "pcm16"
                },
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 1000
            },
            message="OpenAI voice agent started successfully"
        )
        
        logger.info(f"✅ OpenAI voice agent session created: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ OpenAI voice agent start failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start OpenAI voice agent: {str(e)}"
        )


@router.post("/openai/status", response_model=VoiceAgentStatusResponse)
async def get_openai_voice_agent_status(
    request: VoiceAgentStatusRequest,
    current_user: CurrentUser
):
    """Get status of an active OpenAI voice agent session."""
    try:
        session_id = request.session_id
        
        if session_id not in active_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice agent session not found"
            )
        
        session = active_sessions[session_id]
        
        # Check if session belongs to current user
        if session["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this voice agent session"
            )
        
        # Calculate session duration
        duration = int((datetime.now() - session["created_at"]).total_seconds())
        
        return VoiceAgentStatusResponse(
            success=True,
            session_id=session_id,
            agent_type=session["agent_type"],
            is_active=session["status"] == "active",
            connection_status="connected" if session["status"] == "active" else "disconnected",
            duration=duration,
            message_count=0,  # Would be tracked by the WebSocket transport
            tools_used=[],  # Would be tracked by the agent
            current_context=session["user_context"],
            message="OpenAI voice agent status retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OpenAI voice agent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/openai/stop", response_model=VoiceAgentStopResponse)
async def stop_openai_voice_agent(
    request: VoiceAgentStopRequest,
    current_user: CurrentUser
):
    """Stop an active OpenAI voice agent session."""
    try:
        session_id = request.session_id
        
        if session_id not in active_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice agent session not found"
            )
        
        session = active_sessions[session_id]
        
        # Check if session belongs to current user
        if session["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this voice agent session"
            )
        
        # Calculate session duration
        duration = int((datetime.now() - session["created_at"]).total_seconds())
        
        # Mark session as stopped
        session["status"] = "stopped"
        session["stopped_at"] = datetime.now()
        
        # Clean up session after some time (could be done by a background task)
        # For now, we'll keep it for potential session summary retrieval
        
        return VoiceAgentStopResponse(
            success=True,
            session_id=session_id,
            session_summary={
                "duration": duration,
                "total_messages": 0,  # Would be tracked by WebSocket transport
                "tools_used": [],  # Would be tracked by agent
                "completed_tasks": 0,  # Would be tracked by agent
                "audio_duration": duration  # Approximate
            },
            message="OpenAI voice agent stopped successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping OpenAI voice agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop agent: {str(e)}"
        )


@router.websocket("/ws/{session_id}")
async def websocket_voice_agent(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time voice communication with OpenAI voice agents.
    """
    logger.info(f"🔌 WebSocket connection attempt for session: {session_id}")
    
    try:
        # Validate session BEFORE accepting connection
        if session_id not in active_sessions:
            logger.error(f"❌ Session not found: {session_id}")
            await websocket.close(code=4004, reason="Session not found")
            return
        
        session = active_sessions[session_id]
        
        if session["status"] != "active":
            logger.error(f"❌ Session not active: {session_id}")
            await websocket.close(code=4003, reason="Session not active")
            return
        
        # Accept the WebSocket connection
        await websocket.accept()
        logger.info(f"✅ WebSocket connection accepted for session: {session_id}")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "message": "Voice agent WebSocket connected successfully",
            "timestamp": datetime.now().isoformat()
        })
        
        # Send greeting audio immediately after connection
        await _send_greeting_audio(websocket, session_id, session)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for incoming messages
                message = await websocket.receive_json()
                logger.info(f"📨 Received message: {message.get('type', 'unknown')}")
                
                # Handle different message types
                message_type = message.get("type")
                
                if message_type == "audio_data":
                    # Process audio data using OpenAI Agents VoicePipeline
                    audio_data = message.get("data", {}).get("audio", "")
                    if audio_data:
                        logger.info(f"🎤 Processing audio data with VoicePipeline ({len(audio_data)} chars)")
                        
                        try:
                            # Decode base64 audio data
                            import base64
                            import numpy as np
                            audio_bytes = base64.b64decode(audio_data)
                            
                            # Convert to numpy array (assuming 16-bit PCM)
                            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                            
                            # Send acknowledgment
                            await websocket.send_json({
                                "type": "audio_received",
                                "message": "Audio data received, processing with voice pipeline...",
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Process with VoicePipeline
                            await _process_with_voice_pipeline(websocket, session_id, audio_array, session)
                            
                        except Exception as e:
                            logger.error(f"❌ Error processing audio with VoicePipeline: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Audio processing error: {str(e)}",
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No audio data received",
                            "timestamp": datetime.now().isoformat()
                        })
                    
                elif message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                else:
                    await websocket.send_json({
                        "type": "message_received",
                        "original_type": message_type,
                        "message": f"Received {message_type} message",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close(code=4000, reason="Internal server error")
        except:
            pass
    finally:
        # Update session status
        if session_id in active_sessions:
            active_sessions[session_id]["status"] = "disconnected"
        logger.info(f"🧹 Cleaned up WebSocket session: {session_id}")


@router.get("/openai/sessions")
async def get_active_sessions(current_user: CurrentUser):
    """Get active OpenAI voice agent sessions for the current user."""
    try:
        user_sessions = []
        
        for session_id, session in active_sessions.items():
            if session["user_id"] == current_user["id"]:
                duration = int((datetime.now() - session["created_at"]).total_seconds())
                user_sessions.append({
                    "session_id": session_id,
                    "agent_type": session["agent_type"],
                    "business_name": session["business_context"]["name"],
                    "status": session["status"],
                    "duration": duration,
                    "created_at": session["created_at"].isoformat()
                })
        
        return {
            "success": True,
            "sessions": user_sessions,
            "count": len(user_sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.get("/openai/health")
async def openai_voice_agent_health():
    """Health check endpoint for OpenAI voice agent system."""
    try:
        # Count active sessions
        active_count = sum(1 for s in active_sessions.values() if s["status"] == "active")
        
        return {
            "success": True,
            "status": "healthy",
            "active_sessions": active_count,
            "total_sessions": len(active_sessions),
            "openai_agents_available": True,
            "websocket_transport_available": True,
            "system_info": {
                "agent_types": ["personal", "orchestrated"],
                "specialized_agents": ["job", "project", "invoice", "estimate", "contact"],
                "voice_models": ["gpt-4o-mini-tts"],
                "transport": "websocket"
            },
            "message": "OpenAI voice agent system is operational"
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        } 