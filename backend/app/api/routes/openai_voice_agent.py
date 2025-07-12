"""
OpenAI Voice Agent API Routes

API endpoints for OpenAI voice agent integration with Hero365.
"""

import logging
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

# Router setup
router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Set up OpenAI API key for the OpenAI Agents library
import os
from app.core.config import settings

# Set OpenAI API key as environment variable for OpenAI Agents library
if settings.OPENAI_API_KEY:
    os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY
    logger.info("✅ OpenAI API key configured for OpenAI Agents library")
else:
    logger.warning("⚠️ OpenAI API key not found in settings")

# Note: We use manual STT → LLM → TTS flow instead of OpenAI Agents VoicePipeline
# This gives us more control and compatibility with our existing agent architecture
logger.info("✅ Using manual voice flow - no OpenAI Agents SDK dependency required")

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


async def _process_with_manual_voice_flow(websocket: WebSocket, session_id: str, audio_array, session: Dict[str, Any]):
    """
    Process audio using manual STT → LLM → TTS flow
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
        audio_array: Numpy array of audio data
        session: Session data dictionary
    """
    try:
        logger.info(f"🎤 Processing audio with manual STT → LLM → TTS flow for session {session_id}")
        
        # Get the agent from session
        agent = session.get("agent")
        if not agent:
            logger.warning(f"⚠️ No agent available for session {session_id}")
            await websocket.send_json({
                "type": "error",
                "message": "Agent not available",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # Step 1: Speech-to-Text
        logger.info(f"🎤 Step 1: Converting audio to text...")
        
        # Create a temporary WAV file for OpenAI Whisper
        import tempfile
        import wave
        import asyncio
        import base64
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            # Write audio as WAV (using 24kHz as that's what we resampled to)
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(24000)  # 24kHz
                wav_file.writeframes(audio_array.tobytes())
            
            # Transcribe with OpenAI Whisper
            with open(temp_file.name, 'rb') as audio_file:
                from app.core.config import settings
                from openai import AsyncOpenAI
                openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                
                transcription = await openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
        
        # Clean up temp file
        import os
        os.unlink(temp_file.name)
        
        transcript_text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        logger.info(f"📝 Transcription: {transcript_text}")
        
        # Send transcript to client
        await websocket.send_json({
            "type": "transcript",
            "data": {
                "text": transcript_text,
                "is_final": True
            },
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 2: Process with LLM Agent
        logger.info(f"🤖 Step 2: Processing with agent...")
        
        # Get business and user context for the agent
        business_context = session.get("business_context", {})
        user_context = session.get("user_context", {})
        
        # Process message with agent - create OpenAI Agent and use its run method
        try:
            # Create OpenAI Agent instance from our custom agent
            openai_agent = agent.create_voice_optimized_agent()
            
            # Use the OpenAI Agent's run method to process the message
            # The OpenAI Agent uses the tools and instructions we configured
            # Note: openai_client is already configured above with API key
            
            # Use chat completion with the agent's instructions
            # Note: Tool calling will be implemented in a future update
            messages = [
                {"role": "system", "content": agent.get_instructions()},
                {"role": "user", "content": transcript_text}
            ]
            
            # Make the API call without tools for now
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Log successful processing
            logger.info(f"🤖 Agent processed message successfully: {len(response_text)} chars")
                
        except Exception as agent_error:
            logger.error(f"❌ Agent processing error: {agent_error}")
            response_text = "I'm sorry, there was an issue processing your request. Please try again."
        
        logger.info(f"🤖 Agent response: {response_text}")
        
        # Step 3: Text-to-Speech
        logger.info(f"🗣️ Step 3: Converting text to speech...")
        
        # Use OpenAI TTS
        speech_response = await openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response_text,
            response_format="mp3",
            speed=1.0
        )
        
        # Convert response to base64
        audio_data = speech_response.content
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        logger.info(f"🎵 Generated audio response ({len(audio_data)} bytes)")
        
        # Send audio response to client (check connection state)
        try:
            await websocket.send_json({
                "type": "audio_response",
                "data": {
                    "audio": audio_base64,
                    "format": "mp3",
                    "text": response_text
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send completion message
            await websocket.send_json({
                "type": "processing_complete",
                "message": "Voice processing completed",
                "transcript": transcript_text,
                "response": response_text,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as ws_error:
            logger.warning(f"⚠️ WebSocket send failed (connection may be closed): {ws_error}")
            return  # Exit gracefully if connection is closed
        
        logger.info(f"✅ Manual voice flow completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Manual voice flow error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Voice processing failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as ws_error:
            logger.warning(f"⚠️ Could not send error message, WebSocket may be closed: {ws_error}")


async def _process_audio_after_silence(websocket: WebSocket, session_id: str, session: Dict[str, Any]):
    """
    Process buffered audio after detecting silence (timeout-based VAD)
    """
    import asyncio
    
    try:
        # Wait for silence timeout (1.5 seconds)
        await asyncio.sleep(1.5)
        
        # Check if we have audio in the buffer
        if "audio_buffer" in session and session["audio_buffer"]:
            logger.info(f"🔇 Silence detected, processing buffered audio ({len(session['audio_buffer'])} samples, {len(session['audio_buffer'])/16000:.2f}s)")
            
            # Convert buffer to numpy array
            audio_array_16k = np.array(session["audio_buffer"], dtype=np.int16)
            
            # Check for duplicate audio (compare with recently processed complete_audio)
            if "last_processed_audio_hash" in session and "last_processed_time" in session:
                # Create hash of buffered audio for comparison
                import base64
                import hashlib
                audio_bytes = audio_array_16k.tobytes()
                buffered_audio_b64 = base64.b64encode(audio_bytes).decode()
                buffered_hash = hashlib.md5(buffered_audio_b64.encode()).hexdigest()
                
                # Check if this matches recently processed audio (within last 10 seconds)
                time_diff = (datetime.now() - session["last_processed_time"]).total_seconds()
                if time_diff < 10 and buffered_hash == session["last_processed_audio_hash"]:
                    logger.info(f"🚫 Skipping duplicate audio processing (hash: {buffered_hash[:8]}..., {time_diff:.1f}s ago)")
                    # Clear buffer and timer
                    session["audio_buffer"] = []
                    session["silence_timer"] = None
                    return
            
            # Clear buffer and timer
            session["audio_buffer"] = []
            session["silence_timer"] = None
            
            # Resample buffered audio from 16kHz to 24kHz
            from scipy import signal
            audio_float = audio_array_16k.astype(np.float32) / 32768.0
            
            # Resample from 16kHz to 24kHz
            original_sample_rate = 16000
            target_sample_rate = 24000
            
            num_samples_24k = int(len(audio_float) * target_sample_rate / original_sample_rate)
            audio_resampled = signal.resample(audio_float, num_samples_24k)
            
            # Convert back to int16 for processing
            audio_int16_24k = (audio_resampled * 32767).astype(np.int16)
            
            logger.info(f"🎤 Resampled buffered audio: {len(audio_int16_24k)} samples at 24kHz")
            
            # Process the complete audio
            await _process_with_manual_voice_flow(websocket, session_id, audio_int16_24k, session)
            
        else:
            # No audio to process
            session["silence_timer"] = None
            
    except Exception as e:
        logger.error(f"❌ Error processing audio after silence: {e}")
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
        from app.voice_agents.triage import TriageAgent, ContextManager
        
        # Create context manager for enhanced context handling
        context_manager = ContextManager(business_data, user_context)
        
        # Create triage agent with intelligent routing capabilities
        agent = TriageAgent(
            business_context=business_data,
            user_context=user_context,
            context_manager=context_manager
        )
        
        greeting = agent.get_personalized_greeting()
        available_capabilities = agent.get_available_capabilities()
        available_tools = sum(len(caps) for caps in available_capabilities.values())
        
        # Note: VoicePipeline is designed for the new OpenAI Agents SDK format
        # Since we have custom agent classes, we'll use manual STT → LLM → TTS flow
        voice_pipeline = None
        logger.info(f"✅ Using manual STT → LLM → TTS flow for session {session_id}")
        
        # Store session information
        active_sessions[session_id] = {
            "user_id": current_user["id"],
            "business_id": business_id,
            "agent_name": agent.get_agent_name(),
            "business_context": business_data,
            "user_context": user_context,
            "context_manager": context_manager,
            "agent": agent,  # Store the triage agent instance
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
        
        # Backend-controlled voice model selection
        voice_model = "gpt-4o-mini"  # Backend-controlled model choice
        
        response = VoiceAgentStartResponse(
            success=True,
            session_id=session_id,
            agent_name=agent.get_agent_name(),
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
            context_summary=agent.get_context_summary(),
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
        agent = session.get("agent")
        specialist_status = {}
        if agent and hasattr(agent, 'get_specialist_status'):
            specialist_status = agent.get_specialist_status()
        
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
                            import base64
                            import hashlib
                            import numpy as np
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
                            import base64
                            import numpy as np
                            from scipy import signal
                            
                            audio_bytes = base64.b64decode(audio_data)
                            logger.info(f"🎤 Decoded complete audio: {len(audio_bytes)} bytes")
                            
                            # Convert to numpy array (assuming 16-bit PCM from mobile app)
                            audio_array_16k = np.frombuffer(audio_bytes, dtype=np.int16)
                            logger.info(f"🎤 Complete audio: {len(audio_array_16k)} samples ({len(audio_array_16k)/16000:.2f}s)")
                            
                            # Convert to float32 for resampling
                            audio_float = audio_array_16k.astype(np.float32) / 32768.0
                            
                            # Resample from 16kHz to 24kHz (OpenAI Agents requirement)
                            original_sample_rate = 16000
                            target_sample_rate = 24000
                            
                            # Resample using scipy
                            num_samples_24k = int(len(audio_float) * target_sample_rate / original_sample_rate)
                            audio_resampled = signal.resample(audio_float, num_samples_24k)
                            
                            # Convert back to int16 for OpenAI Agents
                            audio_int16_24k = (audio_resampled * 32767).astype(np.int16)
                            
                            logger.info(f"🎤 Resampled complete audio: {len(audio_int16_24k)} samples at 24kHz")
                            
                            # Process with manual STT → LLM → TTS flow
                            await _process_with_manual_voice_flow(websocket, session_id, audio_int16_24k, session)
                            
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