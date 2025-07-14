"""
OpenAI Voice Agent API Routes

API endpoints for OpenAI voice agent integration with Hero365.
Uses the OpenAI Agents SDK VoicePipeline for proper STT -> LLM -> TTS processing.
"""

import logging
import os
import asyncio
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

import numpy as np
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
from app.infrastructure.config.dependency_injection import get_business_repository
from app.core.config import settings

# OpenAI Agents SDK imports
from agents.voice import VoicePipeline, AudioInput, VoicePipelineConfig, TTSModelSettings
from openai import AsyncOpenAI

# Router setup
router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Set OpenAI API key as environment variable for OpenAI Agents library
if settings.OPENAI_API_KEY:
    os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY
    logger.info("✅ OpenAI API key configured for OpenAI Agents library")
else:
    logger.warning("⚠️ OpenAI API key not found in settings")

# Active sessions tracking
active_sessions: Dict[str, Dict[str, Any]] = {}

logger.info("🎯 Using OpenAI Agents SDK VoicePipeline for proper STT -> LLM -> TTS processing")


async def _send_greeting_audio(websocket: WebSocket, session_id: str, session: Dict[str, Any]):
    """Send greeting audio to the user using the VoicePipeline."""
    try:
        logger.info(f"🎤 Sending greeting audio for session {session_id}")
        
        # Get the voice workflow from session
        voice_workflow = session.get("voice_workflow")
        if not voice_workflow:
            logger.warning(f"⚠️ No voice workflow available for session {session_id}")
            return
        
        # Get personalized greeting
        greeting_text = voice_workflow.get_personalized_greeting()
        logger.info(f"📝 Greeting text: {greeting_text}")
        
        # Get the voice pipeline from session
        voice_pipeline = session.get("voice_pipeline")
        if not voice_pipeline:
            logger.warning(f"⚠️ No voice pipeline available for session {session_id}")
            return
        
        # Create a simple audio input with silence to trigger greeting
        # This is a workaround since we want to generate TTS without STT
        silence_array = np.zeros(1024, dtype=np.int16)  # 1024 samples of silence
        audio_input = AudioInput(buffer=silence_array)
        
        # Manually generate TTS using the pipeline's TTS settings
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Use the pipeline's TTS settings
        tts_settings = voice_pipeline.config.tts_settings if voice_pipeline.config else None
        voice = getattr(tts_settings, 'voice', 'alloy') if tts_settings else 'alloy'
        
        # Generate greeting audio
        speech_response = await openai_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=greeting_text,
            response_format="mp3",
            speed=1.0
        )
        
        # Convert to base64 for transmission
        audio_data = speech_response.content
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Send greeting audio to client
        await websocket.send_json({
            "type": "audio_response",
            "data": {
                "audio": audio_base64,
                "format": "mp3",
                "text": greeting_text
            },
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Greeting audio sent successfully for session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending greeting audio: {str(e)}")
        
        # Fallback to text-only greeting
        try:
            fallback_greeting = voice_workflow.get_personalized_greeting() if voice_workflow else "Hello! How can I help you today?"
            await websocket.send_json({
                "type": "message",
                "data": {
                    "text": fallback_greeting,
                    "is_greeting": True
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as fallback_error:
            logger.error(f"❌ Fallback greeting also failed: {fallback_error}")


async def _process_with_voice_pipeline(websocket: WebSocket, session_id: str, audio_array: np.ndarray, session: Dict[str, Any]):
    """
    Process audio using the OpenAI Agents SDK VoicePipeline.
    
    This replaces the manual STT -> LLM -> TTS chain with the proper
    OpenAI Agents SDK VoicePipeline implementation.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
        audio_array: Numpy array of audio data
        session: Session data dictionary
    """
    try:
        logger.info(f"🎯 Processing audio with OpenAI Agents SDK VoicePipeline for session {session_id}")
        
        # Get the voice pipeline from session
        voice_pipeline = session.get("voice_pipeline")
        if not voice_pipeline:
            logger.error(f"❌ No voice pipeline available for session {session_id}")
            await websocket.send_json({
                "type": "error",
                "message": "Voice pipeline not available",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # Create AudioInput from the audio array
        audio_input = AudioInput(buffer=audio_array)
        
        # Process the audio through the VoicePipeline
        logger.info("🎤 Running VoicePipeline...")
        result = await voice_pipeline.run(audio_input)
        
        # Handle the streaming result
        logger.info("📡 Streaming voice pipeline results...")
        
        response_text = ""
        audio_chunks = []
        
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                # Collect audio chunks
                audio_chunks.append(event.data)
                
            elif event.type == "voice_stream_event_content":
                # Collect text content
                response_text += event.data
                
            elif event.type == "voice_stream_event_transcript":
                # Send transcript to client
                await websocket.send_json({
                    "type": "transcript",
                    "data": {
                        "text": event.data,
                        "is_final": True
                    },
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                })
                
            elif event.type == "voice_stream_event_error":
                logger.error(f"❌ Voice pipeline error: {event.data}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Voice processing error: {event.data}",
                    "timestamp": datetime.now().isoformat()
                })
                return
        
        # Combine all audio chunks and send response
        if audio_chunks:
            # Combine audio chunks into a single response
            combined_audio = np.concatenate(audio_chunks)
            audio_base64 = base64.b64encode(combined_audio.tobytes()).decode('utf-8')
            
            # Send the complete audio response
            await websocket.send_json({
                "type": "audio_response",
                "data": {
                    "audio": audio_base64,
                    "format": "wav",  # VoicePipeline typically returns wav
                    "text": response_text
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ Successfully processed audio via VoicePipeline, response: {len(response_text)} chars, audio: {len(combined_audio)} samples")
        else:
            # No audio returned, send text response
            await websocket.send_json({
                "type": "text_response",
                "data": {
                    "text": response_text or "I processed your request successfully."
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"❌ Error processing audio with VoicePipeline: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Send error response
        await websocket.send_json({
            "type": "error",
            "message": "Failed to process audio. Please try again.",
            "timestamp": datetime.now().isoformat()
        })


async def _process_audio_after_silence(websocket: WebSocket, session_id: str, session: Dict[str, Any]):
    """Process accumulated audio after silence detection."""
    try:
        audio_buffer = session.get("audio_buffer", [])
        if not audio_buffer:
            logger.warning(f"⚠️ No audio buffer to process for session {session_id}")
            return
        
        # Combine audio chunks
        combined_audio = np.concatenate(audio_buffer)
        logger.info(f"🎤 Processing {len(combined_audio)} audio samples after silence detection")
        
        # Process with VoicePipeline
        await _process_with_voice_pipeline(websocket, session_id, combined_audio, session)
        
        # Clear the audio buffer
        session["audio_buffer"] = []
        
    except Exception as e:
        logger.error(f"❌ Error processing audio after silence: {str(e)}")
        
        # Clear the audio buffer even on error
        session["audio_buffer"] = []
        
        # Reset silence timer
        session["silence_timer"] = None


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
        
        # Create triage agent with intelligent routing
        from app.voice_agents.triage import TriageAgent, ContextManager, Hero365VoiceWorkflow
        
        # Create context manager for enhanced context handling
        context_manager = ContextManager(business_data, user_context)
        
        # Create triage agent with intelligent routing capabilities
        triage_agent = TriageAgent(
            business_context=business_data,
            user_context=user_context,
            context_manager=context_manager
        )
        
        # Create the voice workflow for the OpenAI Agents SDK
        voice_workflow = Hero365VoiceWorkflow(
            business_context=business_data,
            user_context=user_context,
            context_manager=context_manager
        )
        
        greeting = voice_workflow.get_personalized_greeting()
        available_capabilities = voice_workflow.get_available_capabilities()
        available_tools = sum(len(caps) for caps in available_capabilities.values())
        
        # Configure TTS settings based on user preferences
        tts_voice = "alloy"  # Default voice
        tts_speed = 1.0
        
        if request.voice_speed:
            speed_mapping = {
                "slow": 0.8,
                "normal": 1.0,
                "fast": 1.2
            }
            tts_speed = speed_mapping.get(request.voice_speed, 1.0)
        
        # Configure TTS settings for driving mode
        if user_context.get("is_driving"):
            tts_speed = 0.9  # Slightly slower for driving safety
        
        # Create VoicePipeline with the Hero365VoiceWorkflow
        voice_pipeline = VoicePipeline(
            workflow=voice_workflow,
            config=VoicePipelineConfig(
                tts_settings=TTSModelSettings(
                    voice=tts_voice,
                    speed=tts_speed,
                    format="mp3"
                )
            )
        )
        logger.info(f"✅ Using OpenAI Agents SDK VoicePipeline with Hero365VoiceWorkflow for session {session_id}")
        
        # Store session information
        active_sessions[session_id] = {
            "user_id": current_user["id"],
            "business_id": business_id,
            "agent_name": voice_workflow.get_current_agent_name(),
            "business_context": business_data,
            "user_context": user_context,
            "context_manager": context_manager,
            "triage_agent": triage_agent,  # Store the triage agent instance
            "voice_workflow": voice_workflow,  # Store the voice workflow
            "greeting": greeting,  # Store the greeting text
            "voice_pipeline": voice_pipeline,  # Store the voice pipeline
            "created_at": datetime.now(),
            "status": "active",
            "audio_buffer": [],
            "silence_timer": None,
            "total_tools": available_tools,
            "available_capabilities": available_capabilities
        }
        
        # Prepare WebSocket connection details
        
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
        
        # Backend-controlled voice model selection
        voice_model = "gpt-4o-mini"  # Backend-controlled model choice
        
        response = VoiceAgentStartResponse(
            success=True,
            session_id=session_id,
            agent_name=voice_workflow.get_current_agent_name(),
            greeting=greeting,
            available_capabilities=available_capabilities,
            available_tools=available_tools,
            websocket_connection=websocket_connection,
            agent_config={
                "voice_model": voice_model,
                "voice_settings": request.voice_settings or {
                    "voice": "alloy",
                    "speed": 1.0,
                    "format": "pcm16"
                },
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 1000,
                "device_type": request.device_type,
                "time_zone": request.time_zone
            },
            context_summary=voice_workflow.get_context_summary(),
            message="Triage-based voice agent started successfully"
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
        
        # Get specialist status from the triage agent
        triage_agent = session.get("triage_agent")
        specialist_status = {}
        if triage_agent and hasattr(triage_agent, 'get_specialist_status'):
            specialist_status = triage_agent.get_specialist_status()
        
        return VoiceAgentStatusResponse(
            success=True,
            session_id=session_id,
            agent_name=session.get("agent_name", "Hero365 AI Assistant"),
            is_active=session["status"] == "active",
            connection_status="connected" if session["status"] == "active" else "disconnected",
            duration=duration,
            message_count=0,  # Would be tracked by the WebSocket transport
            tools_used=[],  # Would be tracked by the agent
            current_context=session["user_context"],
            specialist_status=specialist_status,
            message="Triage-based voice agent status retrieved successfully"
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
                    # Buffer audio chunks until silence is detected
                    audio_data = message.get("data", {}).get("audio", "")
                    if audio_data:
                        logger.info(f"🎤 Buffering audio chunk ({len(audio_data)} chars)")
                        
                        try:
                            # Initialize audio buffer if it doesn't exist
                            if "audio_buffer" not in session:
                                session["audio_buffer"] = []
                                session["last_audio_time"] = datetime.now()
                            
                            # Decode and add to buffer
                            audio_bytes = base64.b64decode(audio_data)
                            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                            
                            # Check if this chunk might be a duplicate of recently processed complete_audio
                            if "last_processed_audio_hash" in session and "last_processed_time" in session:
                                chunk_hash = hashlib.md5(audio_data.encode()).hexdigest()
                                time_diff = (datetime.now() - session["last_processed_time"]).total_seconds()
                                if time_diff < 5 and chunk_hash == session["last_processed_audio_hash"]:
                                    logger.info(f"🚫 Skipping duplicate audio chunk (hash: {chunk_hash[:8]}..., {time_diff:.1f}s ago)")
                                    continue
                            
                            # Add to buffer
                            session["audio_buffer"].extend(audio_array.tolist())
                            session["last_audio_time"] = datetime.now()
                            
                            logger.info(f"🎤 Audio buffer size: {len(session['audio_buffer'])} samples ({len(session['audio_buffer'])/16000:.2f}s)")
                            
                            # Cancel existing silence timer and start new one
                            if "silence_timer" in session and session["silence_timer"]:
                                session["silence_timer"].cancel()
                            
                            # Start new silence timer
                            import asyncio
                            session["silence_timer"] = asyncio.create_task(
                                _process_audio_after_silence(websocket, session_id, session)
                            )
                            
                            # Send acknowledgment (check connection state)
                            try:
                                await websocket.send_json({
                                    "type": "audio_buffered",
                                    "buffer_size": len(session["audio_buffer"]),
                                    "duration": len(session["audio_buffer"]) / 16000,
                                    "timestamp": datetime.now().isoformat()
                                })
                            except Exception as ws_error:
                                logger.warning(f"⚠️ WebSocket send failed during buffering: {ws_error}")
                                break
                            
                        except Exception as e:
                            logger.error(f"❌ Error buffering audio: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Audio buffering error: {str(e)}",
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No audio data received",
                            "timestamp": datetime.now().isoformat()
                        })
                
                elif message_type == "complete_audio":
                    # Process complete audio from mobile VAD
                    audio_data = message.get("data", {}).get("audio", "")
                    if audio_data:
                        logger.info(f"🎤 Processing complete audio from mobile VAD ({len(audio_data)} chars)")
                        
                        try:
                            # Cancel any existing silence timer
                            if "silence_timer" in session and session["silence_timer"]:
                                session["silence_timer"].cancel()
                                session["silence_timer"] = None
                            
                            # Clear buffer since we're processing complete audio
                            session["audio_buffer"] = []
                            
                            # Store the audio hash to prevent duplicate processing
                            import hashlib
                            audio_hash = hashlib.md5(audio_data.encode()).hexdigest()
                            session["last_processed_audio_hash"] = audio_hash
                            session["last_processed_time"] = datetime.now()
                            
                            logger.info(f"🔒 Storing audio hash to prevent duplicates: {audio_hash[:8]}...")
                            
                            # Decode base64 audio data
                            audio_bytes = base64.b64decode(audio_data)
                            logger.info(f"🎤 Decoded complete audio: {len(audio_bytes)} bytes")
                            
                            # Convert to numpy array (assuming 16-bit PCM from mobile app)
                            audio_array_16k = np.frombuffer(audio_bytes, dtype=np.int16)
                            logger.info(f"🎤 Complete audio: {len(audio_array_16k)} samples ({len(audio_array_16k)/16000:.2f}s)")
                            
                            # Process with VoicePipeline
                            await _process_with_voice_pipeline(websocket, session_id, audio_array_16k, session)
                            
                        except Exception as e:
                            logger.error(f"❌ Error processing complete audio: {e}")
                            import traceback
                            logger.error(f"Full traceback: {traceback.format_exc()}")
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Complete audio processing error: {str(e)}",
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No complete audio data received",
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
                    "agent_name": session.get("agent_name", "Hero365 AI Assistant"),
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
                "agent_architecture": "triage-based",
                "specialized_agents": ["scheduling", "job_management", "invoice_management", "estimate_management", "contact_management", "project_management"],
                "voice_models": ["gpt-4o-mini-tts"],
                "transport": "websocket",
                "routing_features": ["context_aware", "parallel_execution", "safety_protocols"]
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