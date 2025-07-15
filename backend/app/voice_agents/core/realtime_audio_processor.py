"""
Real-time audio processor for streaming voice interactions without pause detection.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Deque, Union
from collections import deque
from datetime import datetime
import json
import hashlib

from .audio_processor import audio_processor
from .cache_manager import cache_manager
from .context_manager import ContextManager
from ...core.config import settings

logger = logging.getLogger(__name__)


class AudioStreamChunk:
    """Represents a chunk of streaming audio data"""
    def __init__(self, data: bytes, timestamp: float, voice_activity: float = 0.0):
        self.data = data
        self.timestamp = timestamp
        self.voice_activity = voice_activity
        self.size = len(data)


class RealTimeAudioStream:
    """Manages a continuous audio stream for real-time processing"""
    
    def __init__(self, session_id: str, user_id: str, business_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.business_id = business_id
        self.audio_buffer: Deque[AudioStreamChunk] = deque(maxlen=2000)  # ~10 seconds at 16kHz
        self.last_transcription_time = 0.0
        self.last_response_time = 0.0
        self.current_transcription = ""
        self.current_response = ""
        self.is_processing = False
        self.voice_activity_level = 0.0
        self.created_at = time.time()
        
        # Real-time processing intervals
        self.transcription_interval = 0.3  # Transcribe every 300ms
        self.response_interval = 0.8      # Generate response every 800ms
        self.max_transcription_window = 3.0  # Use last 3 seconds for transcription
        
        # Interruption handling
        self.last_significant_audio_time = 0.0  # Track when user last spoke significantly
        self.silence_threshold = 0.5  # 500ms silence before considering processing
        self.processing_task: Optional[asyncio.Task] = None
        self.cancellation_token: Optional[asyncio.Event] = None
        self.is_user_speaking = False  # Track if user is actively speaking
        
    def add_chunk(self, chunk: AudioStreamChunk):
        """Add audio chunk to the stream"""
        self.audio_buffer.append(chunk)
        self.voice_activity_level = chunk.voice_activity
        
        # Update speaking state based on voice activity (restored thresholds with adaptive gain)
        if chunk.voice_activity > 0.01:  # User is speaking (restored from 0.001)
            self.is_user_speaking = True
            self.last_significant_audio_time = chunk.timestamp
        elif chunk.voice_activity < 0.005:  # Silence (restored from 0.0001)
            # Check if we've been silent long enough to stop considering user as speaking
            if time.time() - self.last_significant_audio_time > self.silence_threshold:
                self.is_user_speaking = False
        
    def should_transcribe(self) -> bool:
        """Check if it's time to generate a partial transcription"""
        # Allow transcription during speech, but with a longer interval for active speech
        if self.is_user_speaking:
            # During active speech, transcribe less frequently to avoid interruptions
            return time.time() - self.last_transcription_time > (self.transcription_interval * 2)
        else:
            # After silence, transcribe more frequently for responsiveness
            return time.time() - self.last_transcription_time > self.transcription_interval
    
    def should_respond(self) -> bool:
        """Check if it's time to generate a partial response"""
        # Only respond during silence to avoid interrupting the user
        return (time.time() - self.last_response_time > self.response_interval and 
                not self.is_user_speaking and
                len(self.current_transcription.strip()) > 0)
    
    def should_interrupt_processing(self) -> bool:
        """Check if current processing should be interrupted due to new speech"""
        return self.is_user_speaking and self.is_processing
    
    async def cancel_current_processing(self):
        """Cancel current processing task"""
        if self.processing_task and not self.processing_task.done():
            logger.info(f"🔄 Cancelling processing for session {self.session_id} due to user interruption")
            
            # Signal cancellation
            if self.cancellation_token:
                self.cancellation_token.set()
            
            # Cancel the task
            self.processing_task.cancel()
            
            try:
                await self.processing_task
            except asyncio.CancelledError:
                logger.info(f"✅ Processing cancelled for session {self.session_id}")
            
            # Reset processing state
            self.is_processing = False
            self.processing_task = None
            self.cancellation_token = None
    
    def get_recent_audio(self, duration_seconds: float = None) -> bytes:
        """Get recent audio data for transcription"""
        if duration_seconds is None:
            duration_seconds = self.max_transcription_window
            
        cutoff_time = time.time() - duration_seconds
        total_chunks = len(self.audio_buffer)
        
        # Get all recent chunks (remove voice activity filtering for debugging)
        all_recent_chunks = [
            chunk for chunk in self.audio_buffer 
            if chunk.timestamp > cutoff_time
        ]
        
        # Get chunks with voice activity (restored threshold with adaptive gain)
        voice_chunks = [
            chunk for chunk in all_recent_chunks 
            if chunk.voice_activity > 0.01  # Restored from 0.001
        ]
        
        # Get chunks with any voice activity (even very low)
        any_voice_chunks = [
            chunk for chunk in all_recent_chunks 
            if chunk.voice_activity > 0.0
        ]
        
        logger.info(f"🎤 Audio buffer analysis for session {self.session_id}:")
        logger.info(f"   - Total chunks in buffer: {total_chunks}")
        logger.info(f"   - Recent chunks (last {duration_seconds}s): {len(all_recent_chunks)}")
        logger.info(f"   - Recent chunks with voice activity > 0.01: {len(voice_chunks)}")
        logger.info(f"   - Recent chunks with any voice activity > 0.0: {len(any_voice_chunks)}")
        
        if any_voice_chunks:
            # Log voice activity levels
            voice_levels = [f"{chunk.voice_activity:.4f}" for chunk in any_voice_chunks]
            logger.info(f"   - Voice activity levels: {voice_levels}")
        
        # For debugging low-level audio, use all recent chunks instead of filtering
        # This will help us understand if the audio data is present but just quiet
        recent_audio_data = b''.join(chunk.data for chunk in all_recent_chunks)
        voice_filtered_data = b''.join(chunk.data for chunk in voice_chunks)
        
        logger.info(f"   - Combined audio data (all recent): {len(recent_audio_data)} bytes")
        logger.info(f"   - Combined audio data (voice filtered): {len(voice_filtered_data)} bytes")
        
        # Return all recent audio if voice filtering results in no data
        if len(voice_filtered_data) == 0 and len(recent_audio_data) > 0:
            logger.info(f"   - Using all recent audio data due to low voice activity")
            return recent_audio_data
        
        return voice_filtered_data
    

    
    def cleanup_old_audio(self):
        """Remove old audio data to prevent memory buildup"""
        cutoff_time = time.time() - 30.0  # Keep last 30 seconds max
        while self.audio_buffer and self.audio_buffer[0].timestamp < cutoff_time:
            self.audio_buffer.popleft()


class SimpleVoiceActivityDetector:
    """Simple voice activity detection based on audio energy"""
    
    def __init__(self):
        # Restored thresholds - mobile team implemented adaptive gain
        self.energy_threshold = 0.01  # Restored from 0.001
        self.silence_threshold = 0.005  # Restored from 0.0001
        
    def detect_voice_activity(self, audio_data: bytes) -> float:
        """Detect voice activity level (0.0 to 1.0)"""
        if len(audio_data) < 2:
            logger.debug(f"🔍 Audio data too short: {len(audio_data)} bytes")
            return 0.0
        
        # Convert bytes to 16-bit integers
        samples = []
        for i in range(0, len(audio_data) - 1, 2):
            sample = int.from_bytes(audio_data[i:i+2], byteorder='little', signed=True)
            samples.append(sample)
        
        if not samples:
            logger.debug(f"🔍 No samples extracted from {len(audio_data)} bytes")
            return 0.0
        
        # Calculate RMS energy
        energy = sum(sample ** 2 for sample in samples) / len(samples)
        normalized_energy = min(energy / 32768**2, 1.0)  # Normalize to 0-1
        
        # More detailed debugging
        max_sample = max(abs(s) for s in samples) if samples else 0
        avg_sample = sum(abs(s) for s in samples) / len(samples) if samples else 0
        non_zero_samples = sum(1 for s in samples if s != 0)
        
        logger.info(f"🔍 Audio analysis for {len(audio_data)} bytes:")
        logger.info(f"   - Samples: {len(samples)}, Non-zero: {non_zero_samples}")
        logger.info(f"   - Max sample: {max_sample}, Avg sample: {avg_sample:.2f}")
        logger.info(f"   - Energy: {energy:.6f}, Normalized: {normalized_energy:.6f}")
        logger.info(f"   - Thresholds: energy={self.energy_threshold}, silence={self.silence_threshold}")
        
        # Check if audio is completely silent
        if max_sample == 0:
            logger.info(f"   - Result: 0.0 (completely silent)")
            return 0.0
        
        # Lower thresholds for debugging low-level audio
        if normalized_energy > self.energy_threshold:
            result = min(normalized_energy * 10, 1.0)  # Amplify for better detection
            logger.info(f"   - Result: {result:.4f} (high energy)")
            if max_sample > 100:
                logger.info(f"   ✅ EXCELLENT: Adaptive gain working perfectly!")
            return result
        elif normalized_energy > self.silence_threshold:
            result = normalized_energy * 2
            logger.info(f"   - Result: {result:.4f} (medium energy)")
            if max_sample > 50:
                logger.info(f"   ✅ GOOD: Audio levels look healthy")
            return result
        elif normalized_energy > 0.0:
            # Very low energy but not completely silent
            result = normalized_energy * 0.5
            logger.info(f"   - Result: {result:.4f} (very low energy)")
            if max_sample > 20:
                logger.info(f"   ⚠️ FAIR: Some audio detected but could be stronger")
            return result
        else:
            logger.info(f"   - Result: 0.0 (below silence threshold)")
            return 0.0


class RealTimeAudioProcessor:
    """Real-time audio processor for streaming voice interactions"""
    
    def __init__(self):
        self.active_streams: Dict[str, RealTimeAudioStream] = {}
        self.voice_activity_detector = SimpleVoiceActivityDetector()
        self.context_manager = ContextManager()
        self.websocket_manager = None  # Will be set by voice endpoints
        
        # Processing configuration
        self.min_transcription_length = 10  # Minimum bytes for transcription
        self.min_response_length = 5      # Minimum words for response
        self.max_concurrent_processing = 5
        
        logger.info("✅ Real-time audio processor initialized")
    
    def set_websocket_manager(self, websocket_manager):
        """Set the WebSocket manager for sending messages"""
        self.websocket_manager = websocket_manager
    
    async def start_real_time_session(self, session_id: str, user_id: str, business_id: str):
        """Start a real-time audio streaming session"""
        if session_id in self.active_streams:
            logger.warning(f"⚠️ Real-time session {session_id} already exists")
            return
        
        # Create new stream
        stream = RealTimeAudioStream(session_id, user_id, business_id)
        self.active_streams[session_id] = stream
        
        # Initialize context
        await self.context_manager.initialize_context(user_id, business_id, session_id)
        
        logger.info(f"🎤 Started real-time session {session_id} for user {user_id}")
        
        # Send session started message
        if self.websocket_manager:
            await self.websocket_manager.send_message(session_id, {
                "type": "realtime_session_started",
                "session_id": session_id,
                "status": "streaming",
                "timestamp": datetime.now().isoformat()
            })
    
    async def stop_real_time_session(self, session_id: str):
        """Stop a real-time streaming session"""
        if session_id in self.active_streams:
            stream = self.active_streams[session_id]
            del self.active_streams[session_id]
            
            logger.info(f"🛑 Stopped real-time session {session_id}")
            
            # Send session stopped message
            if self.websocket_manager:
                await self.websocket_manager.send_message(session_id, {
                    "type": "realtime_session_stopped",
                    "session_id": session_id,
                    "stream_duration": time.time() - stream.created_at,
                    "timestamp": datetime.now().isoformat()
                })
    
    async def process_streaming_audio_chunk(self, session_id: str, audio_data: bytes):
        """Process a single audio chunk in real-time with interruption handling"""
        logger.info(f"🎤 process_streaming_audio_chunk called for session {session_id} with {len(audio_data)} bytes")
        
        if session_id not in self.active_streams:
            logger.warning(f"⚠️ No active stream for session {session_id}")
            return
        
        stream = self.active_streams[session_id]
        logger.info(f"🎤 Processing audio chunk for active stream {session_id}")
        
        # Debug audio data format
        self._debug_audio_data(audio_data, session_id)
        
        # Detect voice activity
        voice_activity = self.voice_activity_detector.detect_voice_activity(audio_data)
        logger.info(f"🎤 Voice activity detected: {voice_activity:.2f} for session {session_id}")
        
        # Create audio chunk
        chunk = AudioStreamChunk(
            data=audio_data,
            timestamp=time.time(),
            voice_activity=voice_activity
        )
        
        # Add to stream (this updates speaking state)
        stream.add_chunk(chunk)
        logger.info(f"🎤 Audio chunk added to stream for session {session_id}, is_user_speaking: {stream.is_user_speaking}")
        
        # Check if we should interrupt current processing
        if stream.should_interrupt_processing():
            logger.info(f"🔄 User started speaking again, cancelling current processing for session {session_id}")
            await stream.cancel_current_processing()
            
            # Send interruption notification
            if self.websocket_manager:
                await self.websocket_manager.send_message(session_id, {
                    "type": "processing_interrupted",
                    "session_id": session_id,
                    "reason": "user_speaking",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Send voice activity update
        if self.websocket_manager:
            await self.websocket_manager.send_message(session_id, {
                "type": "voice_activity",
                "session_id": session_id,
                "level": voice_activity,
                "is_speaking": stream.is_user_speaking,
                "timestamp": datetime.now().isoformat()
            })
        
        # Process transcription if needed (during speech or after silence)
        if stream.should_transcribe():
            logger.info(f"🎤 Triggering transcription for session {session_id}")
            await self._process_partial_transcription(stream)
        else:
            logger.debug(f"🎤 Skipping transcription for session {session_id} (not ready yet)")
        
        # Process response if needed (only when user is not speaking)
        if stream.should_respond() and len(stream.current_transcription.strip()) > self.min_response_length:
            await self._process_partial_response(stream)
        
        # Cleanup old audio
        stream.cleanup_old_audio()
    
    def _debug_audio_data(self, audio_data: bytes, session_id: str):
        """Debug audio data format and content"""
        if len(audio_data) < 10:
            return
        
        # Sample the first few bytes for format analysis
        first_samples = []
        for i in range(0, min(20, len(audio_data) - 1), 2):
            sample = int.from_bytes(audio_data[i:i+2], byteorder='little', signed=True)
            first_samples.append(sample)
        
        # Check if all samples are zero (completely silent)
        all_zero = all(s == 0 for s in first_samples)
        
        logger.info(f"🔍 Audio data format analysis for session {session_id}:")
        logger.info(f"   - Total bytes: {len(audio_data)}")
        logger.info(f"   - Expected samples: {len(audio_data) // 2}")
        logger.info(f"   - First 10 samples: {first_samples}")
        logger.info(f"   - All zeros: {all_zero}")
        
        if not all_zero:
            max_sample = max(abs(s) for s in first_samples)
            logger.info(f"   - Max sample in first 10: {max_sample}")
            
            # Check if mobile team's adaptive gain is working
            if max_sample > 100:
                logger.info(f"🎯 ADAPTIVE GAIN WORKING: High amplitude detected ({max_sample})")
            elif max_sample > 10:
                logger.info(f"🔧 MODERATE GAIN: Medium amplitude detected ({max_sample})")
            else:
                logger.info(f"⚠️ LOW GAIN: Still low amplitude ({max_sample}) - gain may need adjustment")
    
    async def _process_partial_transcription(self, stream: RealTimeAudioStream):
        """Generate partial transcription from recent audio with context switching detection"""
        try:
            logger.info(f"🎤 Starting partial transcription for session {stream.session_id}")
            
            # Get recent audio
            recent_audio = stream.get_recent_audio(duration_seconds=2.0)
            logger.info(f"🎤 Recent audio length: {len(recent_audio)} bytes (min required: {self.min_transcription_length})")
            
            if len(recent_audio) < self.min_transcription_length:
                logger.info(f"🎤 Skipping transcription - audio too short: {len(recent_audio)} < {self.min_transcription_length}")
                return
            
            # Generate audio hash for caching
            audio_hash = hashlib.sha256(recent_audio).hexdigest()[:16]
            
            # Check cache first
            cached_transcription = await cache_manager.get_cached_transcription(audio_hash)
            
            if cached_transcription:
                transcription = cached_transcription
                logger.info(f"⚡ Using cached partial transcription: '{transcription[:50]}...'")
            else:
                logger.info(f"🎤 Sending {len(recent_audio)} bytes to OpenAI Whisper for transcription")
                
                # Transcribe with OpenAI Whisper
                transcription = await audio_processor.process_audio_to_text(
                    recent_audio, 
                    format="pcm16",
                    language=settings.OPENAI_DEFAULT_LANGUAGE
                )
                
                # Cache the transcription
                await cache_manager.cache_transcription(audio_hash, transcription)
                
                logger.info(f"🎤 Real-time transcription result: '{transcription[:100]}...'")
                
                # Success indicator for mobile team's adaptive gain
                if len(recent_audio) > 50000:  # Good amount of audio data
                    logger.info(f"✅ TRANSCRIPTION SUCCESS: Adaptive gain system working well!")
                else:
                    logger.info(f"✅ TRANSCRIPTION SUCCESS: Audio processed successfully")
            
            # Detect context switches
            context_switched = self._detect_context_switch(stream.current_transcription, transcription)
            
            if context_switched:
                # Cancel any ongoing processing since context changed
                await stream.cancel_current_processing()
                
                # Send context switch notification
                if self.websocket_manager:
                    await self.websocket_manager.send_message(stream.session_id, {
                        "type": "context_switch_detected",
                        "session_id": stream.session_id,
                        "old_transcription": stream.current_transcription,
                        "new_transcription": transcription,
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Update stream
            stream.current_transcription = transcription
            stream.last_transcription_time = time.time()
            
            # Send to client
            if self.websocket_manager:
                await self.websocket_manager.send_message(stream.session_id, {
                    "type": "partial_transcription",
                    "session_id": stream.session_id,
                    "transcription": transcription,
                    "confidence": 0.8,
                    "is_final": False,
                    "context_switched": context_switched,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"❌ Error in partial transcription for session {stream.session_id}: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    async def _process_partial_response(self, stream: RealTimeAudioStream):
        """Generate partial response from current transcription with cancellation support"""
        try:
            if stream.is_processing:
                return  # Avoid multiple concurrent processing
            
            # Create cancellation token
            cancellation_token = asyncio.Event()
            stream.cancellation_token = cancellation_token
            
            # Create processing task
            processing_task = asyncio.create_task(
                self._generate_response_with_cancellation(stream, cancellation_token)
            )
            
            stream.processing_task = processing_task
            stream.is_processing = True
            
            # Wait for processing to complete
            await processing_task
            
        except asyncio.CancelledError:
            logger.info(f"🚫 Response processing cancelled for session {stream.session_id}")
        except Exception as e:
            logger.error(f"❌ Error in partial response: {e}")
        finally:
            stream.is_processing = False
            stream.processing_task = None
            stream.cancellation_token = None
    
    async def _generate_response_with_cancellation(self, stream: RealTimeAudioStream, cancellation_token: asyncio.Event):
        """Generate response with cancellation support"""
        # Get current transcription
        transcription = stream.current_transcription.strip()
        
        if len(transcription) < self.min_response_length:
            return
        
        # Check for cancellation
        if cancellation_token.is_set():
            raise asyncio.CancelledError("Response generation cancelled")
        
        # Check cache for common queries
        cached_response = await cache_manager.get_cached_common_query(transcription)
        
        if cached_response:
            response = cached_response
            logger.info(f"⚡ Using cached response for partial query")
        else:
            # Check for cancellation before expensive operation
            if cancellation_token.is_set():
                raise asyncio.CancelledError("Response generation cancelled")
            
            # Import voice pipeline here to avoid circular imports
            from ..api.voice_endpoints import voice_pipeline
            
            if voice_pipeline:
                # Generate response using existing voice pipeline
                response = await voice_pipeline.process_text_input(
                    stream.session_id, 
                    transcription
                )
                
                # Cache if it's a common query
                if any(word in transcription.lower() for word in ["hello", "help", "what", "today", "time"]):
                    await cache_manager.cache_common_query(transcription, response)
            else:
                response = "I'm processing your request..."
            
            logger.info(f"🤖 Real-time response: '{response[:50]}...'")
        
        # Final cancellation check before sending response
        if cancellation_token.is_set():
            raise asyncio.CancelledError("Response generation cancelled")
        
        # Update stream
        stream.current_response = response
        stream.last_response_time = time.time()
        
        # Send to client
        if self.websocket_manager:
            await self.websocket_manager.send_message(stream.session_id, {
                "type": "partial_response",
                "session_id": stream.session_id,
                "response": response,
                "transcription": transcription,
                "is_final": False,
                "timestamp": datetime.now().isoformat()
            })
    
    async def finalize_stream_response(self, session_id: str):
        """Finalize the response for a stream (called when user stops speaking)"""
        if session_id not in self.active_streams:
            return
        
        stream = self.active_streams[session_id]
        
        try:
            # Cancel any ongoing processing first
            await stream.cancel_current_processing()
            
            # Get the complete transcription from the entire conversation
            complete_transcription = await self._get_complete_transcription(stream)
            
            # Generate final response if we have transcription
            if complete_transcription.strip():
                logger.info(f"📝 Finalizing response for session {session_id}")
                logger.info(f"📝 Complete transcription: '{complete_transcription[:100]}...'")
                
                # Import voice pipeline here to avoid circular imports
                from ..api.voice_endpoints import voice_pipeline
                
                if voice_pipeline:
                    final_response = await voice_pipeline.process_text_input(
                        session_id, 
                        complete_transcription
                    )
                    
                    # Send final response
                    if self.websocket_manager:
                        await self.websocket_manager.send_message(session_id, {
                            "type": "final_response",
                            "session_id": session_id,
                            "response": final_response,
                            "transcription": complete_transcription,
                            "is_final": True,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Generate TTS for final response
                        try:
                            audio_response = await audio_processor.convert_text_to_base64_audio(final_response)
                            
                            await self.websocket_manager.send_message(session_id, {
                                "type": "final_audio_response",
                                "session_id": session_id,
                                "audio_response": audio_response,
                                "audio_format": "mp3",
                                "response_text": final_response,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                        except Exception as e:
                            logger.error(f"❌ Error generating final TTS: {e}")
                
                # Reset stream for next interaction
                stream.current_transcription = ""
                stream.current_response = ""
                
        except Exception as e:
            logger.error(f"❌ Error finalizing stream response: {e}")
    
    async def _get_complete_transcription(self, stream: RealTimeAudioStream) -> str:
        """Get complete transcription from entire conversation, handling context switches"""
        try:
            # Get all recent audio (last 10 seconds) for complete transcription
            recent_audio = stream.get_recent_audio(duration_seconds=10.0)
            
            if len(recent_audio) < self.min_transcription_length:
                return stream.current_transcription
            
            # Generate complete transcription
            complete_transcription = await audio_processor.process_audio_to_text(
                recent_audio, 
                format="pcm16",
                language=settings.OPENAI_DEFAULT_LANGUAGE
            )
            
            logger.info(f"🎤 Complete transcription: '{complete_transcription[:100]}...'")
            return complete_transcription
            
        except Exception as e:
            logger.error(f"❌ Error getting complete transcription: {e}")
            return stream.current_transcription
    

    
    async def cleanup_inactive_streams(self):
        """Clean up streams that have been inactive for too long"""
        current_time = time.time()
        inactive_sessions = []
        
        for session_id, stream in self.active_streams.items():
            # Consider stream inactive if no audio for 5 minutes
            if current_time - stream.created_at > 300:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            await self.stop_real_time_session(session_id)
            logger.info(f"🧹 Cleaned up inactive stream {session_id}")
    
    def _detect_context_switch(self, old_transcription: str, new_transcription: str) -> bool:
        """Detect if user has switched topics or context"""
        if not old_transcription or not new_transcription:
            return False
        
        # Simple heuristic: look for topic switching keywords
        switch_keywords = [
            "actually", "instead", "wait", "no", "rather", "let me", 
            "change that", "forget that", "never mind", "on second thought",
            "hold on", "first", "before that", "check", "show me"
        ]
        
        new_words = new_transcription.lower().split()
        
        # Check for explicit topic switches
        for keyword in switch_keywords:
            if keyword in new_transcription.lower():
                logger.info(f"🔄 Context switch detected: '{keyword}' in '{new_transcription[:50]}...'")
                return True
        
        # Check for completely different context (basic word overlap)
        old_words = set(old_transcription.lower().split())
        new_words_set = set(new_words)
        
        if len(old_words) > 3 and len(new_words_set) > 3:
            overlap = len(old_words.intersection(new_words_set))
            overlap_ratio = overlap / min(len(old_words), len(new_words_set))
            
            if overlap_ratio < 0.3:  # Less than 30% word overlap
                logger.info(f"🔄 Context switch detected: Low word overlap ({overlap_ratio:.2f})")
                return True
        
        return False


# Global instance
realtime_audio_processor = RealTimeAudioProcessor() 