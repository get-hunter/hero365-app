"""
Voice agent API endpoints for Hero365 mobile integration.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import json
import logging
import base64
from datetime import datetime

from ...api.deps import get_current_user, get_business_context
from ...core.config import settings
from ..core.voice_pipeline import Hero365VoicePipeline
from ..core.context_manager import ContextManager
from ..core.audio_processor import audio_processor
from ..core.cache_manager import cache_manager
from ..core.audio_buffer_manager import audio_buffer_manager
from ..core.realtime_audio_processor import realtime_audio_processor
from ..triage.triage_agent import TriageAgent
from ..specialists.contact_agent import ContactAgent
from ..specialists.job_agent import JobAgent
from ..specialists.estimate_agent import EstimateAgent
from ..specialists.scheduling_agent import SchedulingAgent
from ..monitoring.voice_metrics import voice_metrics, monitor_voice_operation
from ..monitoring.health_check import health_monitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Global voice system components
context_manager = ContextManager()
voice_pipeline = None


def initialize_voice_system():
    """Initialize the voice agent system"""
    global voice_pipeline, context_manager
    
    try:
        # Create specialist agents
        specialist_agents = {
            "contact": ContactAgent(context_manager),
            "job": JobAgent(context_manager),
            "estimate": EstimateAgent(context_manager),
            "scheduling": SchedulingAgent(context_manager)
        }
        
        # Create triage agent
        triage_agent = TriageAgent(context_manager, specialist_agents)
        
        # Create voice pipeline
        voice_pipeline = Hero365VoicePipeline(triage_agent)
        
        # Initialize real-time audio processor cleanup task
        asyncio.create_task(setup_realtime_cleanup_task())
        
        logger.info("Voice agent system initialized successfully")
        logger.info("✅ Real-time audio streaming support enabled")
        
    except Exception as e:
        logger.error(f"Failed to initialize voice system: {e}")
        raise


async def setup_realtime_cleanup_task():
    """Setup periodic cleanup task for real-time audio streams"""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await realtime_audio_processor.cleanup_inactive_streams()
        except Exception as e:
            logger.error(f"Error in real-time cleanup task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


# Initialize on module load
initialize_voice_system()


# Request/Response Models
class VoiceSessionRequest(BaseModel):
    session_metadata: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None


class VoiceSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str
    user_context: Dict[str, Any]


class TextInputRequest(BaseModel):
    message: str
    session_id: str


class TextInputResponse(BaseModel):
    response: str
    session_id: str
    current_agent: Optional[str] = None


class VoiceCommandRequest(BaseModel):
    command: str
    session_id: str
    context: Optional[Dict[str, Any]] = None


# WebSocket connection manager
class VoiceWebSocketManager:
    """Manage WebSocket connections for real-time voice interaction"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
        # Add deduplication tracking
        self.processed_audio_cache: Dict[str, Dict[str, float]] = {}  # session_id -> {audio_hash: timestamp}
        self.cache_timeout = 30  # seconds
        
        # Real-time streaming support
        self.realtime_sessions: Dict[str, bool] = {}  # session_id -> is_realtime
        self.realtime_processor = realtime_audio_processor
        
        # Set this websocket manager in the real-time processor
        self.realtime_processor.set_websocket_manager(self)
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str, business_id: str):
        """Connect a new WebSocket client"""
        logger.info(f"🔗 Accepting WebSocket connection for session {session_id}")
        
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        logger.info(f"✅ WebSocket connection accepted for session {session_id}")
        logger.info(f"📊 Total active connections: {len(self.active_connections)}")
        logger.info(f"📊 WebSocket client state: {websocket.client_state.name}")
        
        # Initialize session metadata
        self.session_metadata[session_id] = {
            "user_id": user_id,
            "business_id": business_id,
            "connected_at": datetime.now().isoformat(),
            "status": "connected",
            "realtime_enabled": False
        }
        
        logger.info(f"📝 Session metadata initialized for {session_id}")
        
        # Register processing callback with audio buffer manager (for existing buffered processing)
        from ..core.audio_buffer_manager import audio_buffer_manager
        audio_buffer_manager.register_processing_callback(
            session_id, 
            lambda: self._process_buffered_audio(session_id)
        )
        
        logger.info(f"✅ Processing callback registered for session {session_id}")
    
    async def disconnect(self, session_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            
            try:
                await websocket.close()
            except:
                pass  # Connection might already be closed
            
            del self.active_connections[session_id]
            
            # Clean up session metadata
            if session_id in self.session_metadata:
                del self.session_metadata[session_id]
            
            # Stop real-time session if active
            if session_id in self.realtime_sessions:
                await self.realtime_processor.stop_real_time_session(session_id)
                del self.realtime_sessions[session_id]
            
            logger.info(f"🔌 WebSocket disconnected for session {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to WebSocket client"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"❌ Error sending message to {session_id}: {e}")
                await self.disconnect(session_id)
    
    async def enable_realtime_streaming(self, session_id: str):
        """Enable real-time streaming for a session"""
        if session_id not in self.session_metadata:
            logger.error(f"❌ Session {session_id} not found")
            return
        
        # Get session metadata
        metadata = self.session_metadata[session_id]
        user_id = metadata["user_id"]
        business_id = metadata["business_id"]
        
        # Start real-time session
        await self.realtime_processor.start_real_time_session(session_id, user_id, business_id)
        
        # Mark as real-time enabled
        self.realtime_sessions[session_id] = True
        self.session_metadata[session_id]["realtime_enabled"] = True
        
        logger.info(f"🎤 Real-time streaming enabled for session {session_id}")
    
    async def disable_realtime_streaming(self, session_id: str):
        """Disable real-time streaming for a session"""
        if session_id in self.realtime_sessions:
            await self.realtime_processor.stop_real_time_session(session_id)
            del self.realtime_sessions[session_id]
            self.session_metadata[session_id]["realtime_enabled"] = False
            
            logger.info(f"🛑 Real-time streaming disabled for session {session_id}")
    
    async def handle_realtime_audio_chunk(self, session_id: str, audio_data: bytes):
        """Handle real-time binary audio chunk"""
        logger.info(f"🎤 handle_realtime_audio_chunk called for session {session_id} with {len(audio_data)} bytes")
        
        if session_id not in self.realtime_sessions:
            logger.warning(f"⚠️ Real-time not enabled for session {session_id}")
            return
        
        logger.info(f"🎤 Forwarding audio chunk to realtime processor for session {session_id}")
        # Process chunk in real-time
        await self.realtime_processor.process_streaming_audio_chunk(session_id, audio_data)
    
    async def handle_control_message(self, session_id: str, message: Dict[str, Any]):
        """Handle control messages for real-time streaming"""
        message_type = message.get("type")
        
        if message_type == "enable_realtime":
            await self.enable_realtime_streaming(session_id)
            await self.send_message(session_id, {
                "type": "realtime_enabled",
                "session_id": session_id,
                "status": "enabled",
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "disable_realtime":
            await self.disable_realtime_streaming(session_id)
            await self.send_message(session_id, {
                "type": "realtime_disabled",
                "session_id": session_id,
                "status": "disabled",
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "finalize_response":
            # Finalize the real-time response
            await self.realtime_processor.finalize_stream_response(session_id)
            

    
    def _is_duplicate_audio(self, session_id: str, audio_data: Any) -> bool:
        """Check if audio data is a duplicate of recently processed audio"""
        import time
        
        if session_id not in self.processed_audio_cache:
            self.processed_audio_cache[session_id] = {}
        
        audio_hash = self._get_audio_hash(audio_data)
        current_time = time.time()
        
        # Clean up old entries
        session_cache = self.processed_audio_cache[session_id]
        expired_hashes = [h for h, timestamp in session_cache.items() 
                         if current_time - timestamp > self.cache_timeout]
        for h in expired_hashes:
            del session_cache[h]
        
        # Check if this audio was recently processed
        if audio_hash in session_cache:
            time_since_processed = current_time - session_cache[audio_hash]
            if time_since_processed < self.cache_timeout:
                logger.info(f"🔄 Duplicate audio detected for session {session_id} (processed {time_since_processed:.1f}s ago)")
                return True
        
        # Mark this audio as processed
        session_cache[audio_hash] = current_time
        return False
    
    def _get_audio_hash(self, audio_data: Any) -> str:
        """Generate hash for audio data"""
        import hashlib
        
        if isinstance(audio_data, str):
            # Base64 encoded audio
            return hashlib.md5(audio_data.encode()).hexdigest()[:16]
        elif isinstance(audio_data, bytes):
            # Raw audio bytes
            return hashlib.md5(audio_data).hexdigest()[:16]
        else:
            return hashlib.md5(str(audio_data).encode()).hexdigest()[:16]
    
    async def _process_buffered_audio(self, session_id: str):
        """Process buffered audio with cancellation support"""
        try:
            # Create cancellation token
            cancellation_token = asyncio.Event()
            
            # Get combined audio from buffer
            combined_audio, audio_format = audio_buffer_manager.get_combined_audio(session_id)
            
            if not combined_audio:
                logger.warning(f"⚠️ No audio data to process for session {session_id}")
                return
            
            # Create processing task
            processing_task = asyncio.create_task(
                self._process_audio_with_cancellation(
                    session_id, combined_audio, audio_format, cancellation_token
                )
            )
            
            # Mark processing as started
            audio_buffer_manager.mark_processing_started(session_id, processing_task, cancellation_token)
            
            # Send processing notification
            await self.send_message(session_id, {
                "type": "audio_processing",
                "session_id": session_id,
                "status": "processing",
                "audio_size": len(combined_audio),
                "timestamp": datetime.now().isoformat()
            })
            
            # Wait for processing to complete
            await processing_task
            
        except asyncio.CancelledError:
            logger.info(f"🚫 Audio processing cancelled for session {session_id}")
            audio_buffer_manager.mark_processing_completed(session_id, success=False)
            
            # Send cancellation notification
            await self.send_message(session_id, {
                "type": "audio_processing",
                "session_id": session_id,
                "status": "cancelled",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Error in buffered audio processing for session {session_id}: {e}")
            audio_buffer_manager.mark_processing_completed(session_id, success=False)
            
            # Send error notification
            await self.send_message(session_id, {
                "type": "audio_processing",
                "session_id": session_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def _process_audio_with_cancellation(self, session_id: str, audio_data: bytes, 
                                             audio_format: str, cancellation_token: asyncio.Event):
        """Process audio data with cancellation support"""
        try:
            logger.info(f"🎤 Converting audio to text using OpenAI Whisper")
            
            # Generate audio hash for caching
            import hashlib
            audio_hash = hashlib.sha256(audio_data).hexdigest()[:16]
            
            # Check cache for transcription first
            cached_transcription = await cache_manager.get_cached_transcription(audio_hash)
            
            if cached_transcription:
                logger.info(f"⚡ Using cached transcription: '{cached_transcription[:50]}...'")
                transcribed_text = cached_transcription
            else:
                # Process audio with cancellation support
                transcribed_text = await audio_processor.process_audio_to_text(
                    audio_data, 
                    audio_format,
                    cancellation_token=cancellation_token
                )
                
                # Cache the transcription
                await cache_manager.cache_transcription(audio_hash, transcribed_text)
            
            # Check for cancellation before proceeding
            if cancellation_token.is_set():
                raise asyncio.CancelledError("Processing cancelled after transcription")
            
            logger.info(f"📝 Whisper transcription: '{transcribed_text[:100]}{'...' if len(transcribed_text) > 100 else ''}'")
            
            # Check cache for common queries
            cached_response = await cache_manager.get_cached_common_query(transcribed_text)
            
            if cached_response:
                logger.info(f"⚡ Using cached common query response")
                response = cached_response
            else:
                # Check for cancellation before agent processing
                if cancellation_token.is_set():
                    raise asyncio.CancelledError("Processing cancelled before agent processing")
                
                # Process transcribed text through triage agent
                response = await voice_pipeline.process_text_input(session_id, transcribed_text)
                
                # Cache response if it's a common query (non-user-specific)
                if any(word in transcribed_text.lower() for word in ["hello", "help", "what", "today", "time", "date"]):
                    await cache_manager.cache_common_query(transcribed_text, response)
            
            # Check for cancellation before TTS
            if cancellation_token.is_set():
                raise asyncio.CancelledError("Processing cancelled before TTS")
            
            logger.info(f"✅ Audio processing completed: {response[:50]}...")
            
            # Convert response text to speech with caching
            try:
                logger.info(f"🔊 Converting response to speech using OpenAI TTS")
                
                # Check cache for TTS response
                cached_tts = await cache_manager.get_cached_tts_response(response, settings.OPENAI_TTS_VOICE)
                
                if cached_tts:
                    logger.info(f"⚡ Using cached TTS response")
                    response_audio_base64 = base64.b64encode(cached_tts).decode('utf-8')
                else:
                    response_audio_base64 = await audio_processor.convert_text_to_base64_audio(response)
                    
                    # Cache the TTS response
                    audio_bytes = base64.b64decode(response_audio_base64)
                    await cache_manager.cache_tts_response(response, settings.OPENAI_TTS_VOICE, audio_bytes)
                
                # Final cancellation check before sending response
                if cancellation_token.is_set():
                    raise asyncio.CancelledError("Processing cancelled before sending response")
                
                # Send audio response
                await self.send_message(session_id, {
                    "type": "agent_response",
                    "session_id": session_id,
                    "response": response,
                    "audio_response": response_audio_base64,
                    "audio_format": "mp3",
                    "audio_processed": True,
                    "transcribed_text": transcribed_text,
                    "input_audio_format": audio_format,
                    "original_size": len(audio_data),
                    "processing_method": "buffered_pause_detection",
                    "tts_voice": settings.OPENAI_TTS_VOICE,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Mark processing as completed successfully
                audio_buffer_manager.mark_processing_completed(session_id, success=True)
                
            except Exception as tts_error:
                if cancellation_token.is_set():
                    raise asyncio.CancelledError("Processing cancelled during TTS error handling")
                
                logger.error(f"❌ TTS conversion error: {tts_error}")
                # Fallback to text-only response
                await self.send_message(session_id, {
                    "type": "agent_response",
                    "session_id": session_id,
                    "response": response,
                    "audio_processed": True,
                    "transcribed_text": transcribed_text,
                    "audio_format": audio_format,
                    "original_size": len(audio_data),
                    "processing_method": "buffered_pause_detection",
                    "tts_error": str(tts_error),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Mark processing as completed with partial success
                audio_buffer_manager.mark_processing_completed(session_id, success=True)
                
        except asyncio.CancelledError:
            logger.info(f"🚫 Audio processing with cancellation cancelled for session {session_id}")
            raise
        except Exception as e:
            logger.error(f"❌ Error in audio processing with cancellation for session {session_id}: {e}")
            raise
    
    async def handle_voice_message(self, session_id: str, message: Dict[str, Any]):
        """Handle incoming voice messages"""
        try:
            message_type = message.get("type")
            logger.info(f"🎤 Processing message type: {message_type} for session {session_id}")
            
            # Handle control messages
            if message_type in ["enable_realtime", "disable_realtime", "finalize_response"]:
                await self.handle_control_message(session_id, message)
                return
            
            elif message_type == "start_session":
                # Handle session start message
                logger.info(f"🎤 Starting voice session for {session_id}")
                
                # Send session started confirmation
                await self.send_message(session_id, {
                    "type": "session_started",
                    "session_id": session_id,
                    "status": "active",
                    "message": "Voice session started successfully",
                    "realtime_available": True,
                    "buffered_available": True,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Get current context and send welcome message
                context = await context_manager.get_current_context()
                welcome_message = "Hello! I'm your Hero365 AI assistant. How can I help you today?"
                
                await self.send_message(session_id, {
                    "type": "agent_response",
                    "session_id": session_id,
                    "response": welcome_message,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                })
                
                return
            
            elif message_type == "end_session":
                # Handle session end message
                logger.info(f"🎤 Ending voice session for {session_id}")
                
                # Clean up session if needed
                if voice_pipeline:
                    try:
                        await voice_pipeline.end_voice_session(session_id)
                    except Exception as e:
                        logger.warning(f"⚠️ Error ending voice session: {e}")
                
                # Send session ended confirmation
                await self.send_message(session_id, {
                    "type": "session_ended",
                    "session_id": session_id,
                    "status": "ended",
                    "message": "Voice session ended successfully",
                    "timestamp": datetime.now().isoformat()
                })
                
                return
            
            elif message_type == "text_input":
                text_input = message.get("text", "")
                logger.info(f"📝 Processing text input: {text_input[:50]}...")
                
                # Check cache for common queries first
                cached_response = await cache_manager.get_cached_common_query(text_input)
                
                if cached_response:
                    logger.info(f"⚡ Using cached common query response")
                    response = cached_response
                else:
                    # Process text input through voice pipeline
                    response = await voice_pipeline.process_text_input(session_id, text_input)
                    
                    # Cache response if it's a common query (non-user-specific)
                    if any(word in text_input.lower() for word in ["hello", "help", "what", "today", "time", "date"]):
                        await cache_manager.cache_common_query(text_input, response)
                
                logger.info(f"✅ Text response generated: {response[:50]}...")
                
                # Check if client wants audio response
                want_audio = message.get("want_audio_response", False)
                
                if want_audio:
                    # Generate TTS response
                    try:
                        # Check cache for TTS response
                        cached_tts = await cache_manager.get_cached_tts_response(response, settings.OPENAI_TTS_VOICE)
                        
                        if cached_tts:
                            logger.info(f"⚡ Using cached TTS response")
                            response_audio_base64 = base64.b64encode(cached_tts).decode('utf-8')
                        else:
                            response_audio_base64 = await audio_processor.convert_text_to_base64_audio(response)
                            
                            # Cache the TTS response
                            audio_bytes = base64.b64decode(response_audio_base64)
                            await cache_manager.cache_tts_response(response, settings.OPENAI_TTS_VOICE, audio_bytes)
                        
                        await self.send_message(session_id, {
                            "type": "agent_response",
                            "session_id": session_id,
                            "response": response,
                            "audio_response": response_audio_base64,
                            "audio_format": "mp3",
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        logger.error(f"❌ Error generating TTS response: {e}")
                        # Send text-only response
                        await self.send_message(session_id, {
                            "type": "agent_response",
                            "session_id": session_id,
                            "response": response,
                            "timestamp": datetime.now().isoformat()
                        })
                else:
                    # Send text-only response
                    await self.send_message(session_id, {
                        "type": "agent_response",
                        "session_id": session_id,
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_type == "audio_data":
                # Handle both real-time and buffered audio processing
                audio_data = message.get("audio")
                audio_size = message.get("size", len(audio_data) if audio_data else 0)
                audio_format = message.get("format", "wav").lower()
                logger.info(f"🎤 Received audio data: {audio_size} bytes ({audio_format})")
                
                # Check for duplicate audio
                if self._is_duplicate_audio(session_id, audio_data):
                    logger.info(f"⏭️ Skipping duplicate audio for session {session_id}")
                    await self.send_message(session_id, {
                        "type": "audio_processing",
                        "session_id": session_id,
                        "status": "skipped_duplicate",
                        "timestamp": datetime.now().isoformat()
                    })
                    return
                
                # Convert audio data to bytes if needed
                if isinstance(audio_data, str):
                    audio_bytes = base64.b64decode(audio_data)
                else:
                    audio_bytes = audio_data
                
                # Check if this session has real-time enabled
                if session_id in self.realtime_sessions:
                    # Process in real-time
                    await self.handle_realtime_audio_chunk(session_id, audio_bytes)
                else:
                    # Use existing buffered processing
                    audio_buffer_manager.add_audio_chunk(session_id, audio_bytes, audio_format)
                    
                    # Check if we should cancel previous processing due to new audio
                    if audio_buffer_manager.should_extend_processing(session_id):
                        logger.info(f"🔄 Cancelling previous processing due to new audio for session {session_id}")
                        await audio_buffer_manager.cancel_previous_processing(session_id)
                    
                    # Just buffering audio, send acknowledgment
                    await self.send_message(session_id, {
                        "type": "audio_buffering",
                        "session_id": session_id,
                        "status": "buffered",
                        "buffer_size": len(audio_bytes),
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_type == "context_update":
                # Update context
                context_data = message.get("data", {})
                await context_manager.update_context(context_data)
                
                await self.send_message(session_id, {
                    "type": "context_updated",
                    "session_id": session_id,
                    "data": context_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "session_status":
                # Get session status
                status = {
                    "session_id": session_id,
                    "status": "active",
                    "realtime_enabled": session_id in self.realtime_sessions,
                    "connected_at": self.session_metadata.get(session_id, {}).get("connected_at"),
                    "active_connections": len(self.active_connections)
                }
                
                await self.send_message(session_id, {
                    "type": "session_status",
                    "session_id": session_id,
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                })
            
            else:
                # Handle unknown message types
                logger.warning(f"⚠️ Unknown message type: {message_type}")
                await self.send_message(session_id, {
                    "type": "error",
                    "session_id": session_id,
                    "error": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"❌ Error handling voice message: {e}")
            await self.send_message(session_id, {
                "type": "error",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })


# Initialize WebSocket manager
websocket_manager = VoiceWebSocketManager()


# API Endpoints
@router.post("/start-session", response_model=VoiceSessionResponse)
async def start_voice_session(
    request: VoiceSessionRequest,
    current_user=Depends(get_current_user),
    business_context=Depends(get_business_context)
):
    """Start a new voice session"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        user_id = current_user["sub"]
        business_id = business_context.get("business_id", current_user.get("business_id"))
        
        # Start voice session
        session_id = await voice_pipeline.start_voice_session(
            user_id=user_id,
            business_id=business_id,
            session_metadata=request.session_metadata
        )
        
        # Record session start in metrics
        voice_metrics.record_session_start(session_id, "triage")
        
        # Update context with location if provided
        if request.location:
            await context_manager.update_context({
                "location": request.location
            })
        
        # Get current context for response
        context = await context_manager.get_current_context()
        
        return VoiceSessionResponse(
            session_id=session_id,
            status="active",
            message="Voice session started successfully",
            user_context=context
        )
        
    except Exception as e:
        logger.error(f"Error starting voice session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-input", response_model=TextInputResponse)
async def process_text_input(
    request: TextInputRequest,
    current_user=Depends(get_current_user)
):
    """Process text input through the voice agent system"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        # Process text input
        response = await voice_pipeline.process_text_input(
            request.session_id,
            request.message
        )
        
        # Get current context
        context = await context_manager.get_current_context()
        
        return TextInputResponse(
            response=response,
            session_id=request.session_id,
            current_agent=context.get("current_agent")
        )
        
    except Exception as e:
        logger.error(f"Error processing text input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-command")
async def process_voice_command(
    request: VoiceCommandRequest,
    current_user=Depends(get_current_user)
):
    """Process a voice command"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        # Update context if provided
        if request.context:
            await context_manager.update_context(request.context)
        
        # Process command
        response = await voice_pipeline.process_text_input(
            request.session_id,
            request.command
        )
        
        return {
            "success": True,
            "response": response,
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-stats")
async def get_performance_stats(
    current_user=Depends(get_current_user)
):
    """Get voice agent performance statistics"""
    try:
        # Get cache statistics
        cache_stats = await cache_manager.get_cache_stats()
        
        # Get audio buffer manager statistics
        buffer_stats = audio_buffer_manager.get_all_sessions_stats()
        
        # Get audio processor health
        audio_stats = {
            "openai_configured": bool(audio_processor.client),
            "http_client_configured": bool(audio_processor.http_client),
            "connection_pooling": True,
            "optimization_features": [
                "HTTP connection pooling",
                "Response caching",
                "Parallel processing",
                "Fast TTS model for short texts",
                "Audio transcription caching",
                "Pause detection processing",
                "Audio buffering and cancellation",
                "Real-time audio streaming"
            ]
        }
        
        # Get active sessions count
        active_sessions = len(voice_pipeline.active_sessions) if voice_pipeline else 0
        
        return {
            "success": True,
            "performance_stats": {
                "cache_stats": cache_stats,
                "audio_processor": audio_stats,
                "audio_buffer_manager": buffer_stats,
                "active_sessions": active_sessions,
                "system_optimizations": {
                    "connection_pooling": True,
                    "response_caching": True,
                    "parallel_audio_processing": True,
                    "fast_tts_for_short_texts": True,
                    "transcription_caching": True,
                    "pause_detection": True,
                    "buffered_processing": True,
                    "cancellation_support": True,
                    "realtime_streaming": True
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_voice_cache(
    current_user=Depends(get_current_user)
):
    """Clear voice agent cache (admin only)"""
    try:
        # Clear all cache
        success = await cache_manager.clear_all_cache()
        
        if success:
            logger.info("✅ Voice agent cache cleared by admin")
            return {"success": True, "message": "Cache cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/enable-realtime")
async def enable_realtime_streaming(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """Enable real-time streaming for a session"""
    try:
        await websocket_manager.enable_realtime_streaming(session_id)
        
        return {
            "success": True,
            "message": "Real-time streaming enabled",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error enabling real-time streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/disable-realtime")
async def disable_realtime_streaming(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """Disable real-time streaming for a session"""
    try:
        await websocket_manager.disable_realtime_streaming(session_id)
        
        return {
            "success": True,
            "message": "Real-time streaming disabled",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error disabling real-time streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))






@router.get("/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """Get status of a voice session"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        status = await voice_pipeline.get_session_status(session_id)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/end")
async def end_voice_session(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """End a voice session"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        await voice_pipeline.end_voice_session(session_id)
        
        # Record session end in metrics
        voice_metrics.record_session_end(session_id, "completed")
        
        return {
            "success": True,
            "message": "Voice session ended successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error ending voice session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/active")
async def get_active_sessions(
    current_user=Depends(get_current_user)
):
    """Get all active voice sessions"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        sessions = await voice_pipeline.get_active_sessions()
        
        return {
            "success": True,
            "data": sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status")
async def get_voice_system_status(
    current_user=Depends(get_current_user)
):
    """Get voice system status"""
    try:
        if not voice_pipeline:
            return {
                "success": False,
                "error": "Voice system not initialized"
            }
        
        stats = voice_pipeline.get_pipeline_stats()
        
        return {
            "success": True,
            "data": {
                "system_initialized": True,
                "pipeline_stats": stats,
                "active_connections": len(websocket_manager.active_connections),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting voice system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-audio/{session_id}")
async def upload_audio(
    session_id: str,
    audio_file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload audio file for processing"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # This would process the audio through the voice pipeline
        # For now, return acknowledgment
        
        return {
            "success": True,
            "message": "Audio uploaded successfully",
            "session_id": session_id,
            "file_size": len(audio_data)
        }
        
    except Exception as e:
        logger.error(f"Error uploading audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: str = None,
    business_id: str = None,
    token: str = None
):
    """WebSocket endpoint for real-time voice interaction"""
    logger.info(f"🎤 WebSocket connection attempt for session {session_id}")
    logger.info(f"📝 Parameters: user_id={user_id}, business_id={business_id}, token={'***' if token else 'None'}")
    
    try:
        # Validate required parameters
        if not user_id or not business_id:
            logger.error("❌ Missing required parameters: user_id and business_id are required")
            await websocket.close(code=4000, reason="Missing required parameters")
            return
        
        # For now, skip token validation (in production, validate the JWT token here)
        # TODO: Add proper JWT token validation for WebSocket connections
        if not token:
            logger.warning("⚠️ No authentication token provided")
        
        await websocket_manager.connect(websocket, session_id, user_id, business_id)
        logger.info(f"✅ WebSocket connected for session {session_id}")
        
        # Start voice session if not already started
        if voice_pipeline:
            await voice_pipeline.start_voice_session(
                user_id=user_id,
                business_id=business_id,
                session_metadata={"websocket": True}
            )
            logger.info(f"🎤 Voice session started for WebSocket {session_id}")
        
        # Send initial connection confirmation with real-time capabilities
        await websocket.send_json({
            "type": "connection_confirmed",
            "session_id": session_id,
            "realtime_available": True,
            "buffered_available": True,
            "message": "WebSocket connection established with real-time support",
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            while True:
                # Receive message from client (can be JSON or binary)
                message = await websocket.receive()
                logger.info(f"📨 WebSocket message received for session {session_id}: {list(message.keys())}")
                
                if message.get("type") == "websocket.receive":
                    if "text" in message:
                        # Handle JSON text message (control messages)
                        try:
                            json_message = json.loads(message["text"])
                            message_type = json_message.get('type', 'unknown')
                            logger.info(f"📝 JSON control message: {message_type}")
                            await websocket_manager.handle_voice_message(session_id, json_message)
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON decode error: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "error": "Invalid JSON format"
                            })
                    
                    elif "bytes" in message:
                        # Handle binary audio data for real-time streaming
                        audio_data = message["bytes"]
                        logger.info(f"🎤 Binary audio chunk received: {len(audio_data)} bytes for session {session_id}")
                        
                        # Check if this session has real-time enabled
                        if session_id in websocket_manager.realtime_sessions:
                            logger.info(f"🎤 Processing real-time audio chunk for session {session_id}")
                            # Process as real-time binary audio
                            await websocket_manager.handle_realtime_audio_chunk(session_id, audio_data)
                        else:
                            logger.info(f"🎤 Processing buffered audio chunk for session {session_id}")
                            # Convert to structured message for buffered processing
                            audio_message = {
                                "type": "audio_data",
                                "audio": audio_data,
                                "format": "pcm16",  # Binary audio is typically PCM16 from mobile apps
                                "size": len(audio_data)
                            }
                            await websocket_manager.handle_voice_message(session_id, audio_message)
                        
                else:
                    logger.warning(f"⚠️ Unexpected message type: {message.get('type')}")
                
        except WebSocketDisconnect:
            logger.info(f"🔌 WebSocket disconnected for session {session_id}")
        except Exception as e:
            logger.error(f"❌ WebSocket error for session {session_id}: {e}")
        finally:
            await websocket_manager.disconnect(session_id)
            logger.info(f"🔌 WebSocket cleanup completed for session {session_id}")
            
    except Exception as e:
        logger.error(f"❌ WebSocket connection error: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close()


# Monitoring endpoints
@router.get("/metrics")
async def get_voice_metrics(
    current_user=Depends(get_current_user)
):
    """Get voice agent system metrics"""
    try:
        metrics = voice_metrics.get_current_metrics()
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/metrics/session/{session_id}")
async def get_session_metrics(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """Get metrics for a specific session"""
    try:
        session_metrics = voice_metrics.get_session_metrics(session_id)
        if not session_metrics:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_metrics": session_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session metrics: {str(e)}")


@router.get("/monitoring/health")
async def get_comprehensive_health(
    current_user=Depends(get_current_user)
):
    """Get comprehensive health status of all voice agent components"""
    try:
        health_status = await health_monitor.run_all_checks()
        return {
            "success": True,
            "health": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")


@router.get("/monitoring/health/{component}")
async def get_component_health(
    component: str,
    current_user=Depends(get_current_user)
):
    """Get health status of a specific component"""
    try:
        health_status = await health_monitor.run_single_check(component)
        return {
            "success": True,
            "component": component,
            "health": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting component health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get component health: {str(e)}")


@router.get("/monitoring/errors")
async def get_recent_errors(
    limit: int = 10,
    current_user=Depends(get_current_user)
):
    """Get recent errors from the voice system"""
    try:
        errors = voice_metrics.get_recent_errors(limit)
        return {
            "success": True,
            "errors": errors,
            "count": len(errors),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent errors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent errors: {str(e)}")


# Health check endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        system_healthy = voice_pipeline is not None
        audio_health = await audio_processor.health_check()
        
        overall_healthy = system_healthy and audio_health.get("status") != "degraded"
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "voice_system_initialized": system_healthy,
            "audio_processor": audio_health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/audio/health")
async def audio_health_check():
    """Detailed audio processor health check"""
    return await audio_processor.health_check()

@router.get("/audio/formats")
async def get_supported_audio_formats():
    """Get supported audio formats"""
    return {
        "supported_formats": audio_processor.get_supported_formats(),
        "recommended_format": "wav",
        "max_file_size": "25MB",
        "processor": "OpenAI Whisper",
        "auto_conversion": ["pcm16", "pcm", "raw"]
    }

@router.get("/audio/voices")
async def get_supported_voices():
    """Get supported TTS voices"""
    return {
        "supported_voices": audio_processor.get_supported_voices(),
        "default_voice": settings.OPENAI_TTS_VOICE,
        "tts_model": settings.OPENAI_TTS_MODEL,
        "output_format": "mp3"
    }

@router.get("/audio/languages")
async def get_supported_languages():
    """Get supported languages for Whisper transcription"""
    return {
        "supported_languages": audio_processor.get_supported_languages(),
        "default_language": settings.OPENAI_DEFAULT_LANGUAGE,
        "stt_model": settings.OPENAI_SPEECH_MODEL,
        "description": "ISO 639-1 language codes supported by OpenAI Whisper"
    }

@router.post("/audio/test-tts")
async def test_text_to_speech(
    text: str,
    voice: str = None,
    current_user=Depends(get_current_user)
):
    """Test text-to-speech conversion"""
    try:
        # Limit text length for testing
        if len(text) > 500:
            raise HTTPException(status_code=400, detail="Text too long for testing (max 500 characters)")
        
        # Convert to audio
        audio_base64 = await audio_processor.convert_text_to_base64_audio(text, voice)
        
        return {
            "success": True,
            "audio_base64": audio_base64,
            "audio_format": "mp3",
            "text": text,
            "voice": voice or settings.OPENAI_TTS_VOICE,
            "audio_size": len(audio_base64)
        }
        
    except Exception as e:
        logger.error(f"TTS test error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS conversion failed: {str(e)}") 