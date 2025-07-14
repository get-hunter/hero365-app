"""
Audio buffer manager for intelligent voice processing with pause detection and cancellation.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from ...core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AudioChunk:
    """Represents a chunk of audio data"""
    data: bytes
    format: str
    timestamp: float
    size: int


@dataclass
class ProcessingState:
    """Tracks the processing state for a session"""
    session_id: str
    is_processing: bool = False
    cancellation_token: Optional[asyncio.Event] = None
    last_audio_timestamp: Optional[float] = None
    audio_buffer: List[AudioChunk] = None
    processing_task: Optional[asyncio.Task] = None
    processing_requested: bool = False
    
    def __post_init__(self):
        if self.audio_buffer is None:
            self.audio_buffer = []


class AudioBufferManager:
    """Manages audio buffering, pause detection, and processing cancellation"""
    
    def __init__(self):
        """Initialize audio buffer manager"""
        self.session_states: Dict[str, ProcessingState] = {}
        self.pause_threshold_ms = settings.VOICE_PAUSE_THRESHOLD_MS
        self.max_extension_ms = settings.VOICE_MAX_EXTENSION_MS
        self.min_audio_length_ms = settings.VOICE_MIN_AUDIO_LENGTH_MS
        self.enable_pause_processing = settings.VOICE_ENABLE_PAUSE_PROCESSING
        
        # Background pause detection
        self.pause_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Processing callbacks for each session
        self.processing_callbacks: Dict[str, callable] = {}
        
        logger.info(f"✅ Audio buffer manager initialized:")
        logger.info(f"   - Pause threshold: {self.pause_threshold_ms}ms")
        logger.info(f"   - Max extension: {self.max_extension_ms}ms")
        logger.info(f"   - Min audio length: {self.min_audio_length_ms}ms")
        logger.info(f"   - Pause processing: {self.enable_pause_processing}")
    
    def get_session_state(self, session_id: str) -> ProcessingState:
        """Get or create processing state for session"""
        if session_id not in self.session_states:
            self.session_states[session_id] = ProcessingState(session_id=session_id)
        return self.session_states[session_id]
    
    def cleanup_session(self, session_id: str):
        """Clean up session state"""
        if session_id in self.session_states:
            state = self.session_states[session_id]
            # Cancel any ongoing processing
            if state.processing_task and not state.processing_task.done():
                state.processing_task.cancel()
            if state.cancellation_token:
                state.cancellation_token.set()
            del self.session_states[session_id]
            logger.info(f"🧹 Cleaned up session state for {session_id}")
        
        # Cancel pause detection task
        if session_id in self.pause_check_tasks:
            self.pause_check_tasks[session_id].cancel()
            del self.pause_check_tasks[session_id]
            logger.info(f"🧹 Cancelled pause detection task for {session_id}")
        
        # Remove processing callback
        if session_id in self.processing_callbacks:
            del self.processing_callbacks[session_id]
            logger.info(f"🧹 Removed processing callback for {session_id}")
    
    async def cancel_previous_processing(self, session_id: str) -> bool:
        """
        Cancel any ongoing processing for the session.
        
        Args:
            session_id: Session ID to cancel processing for
            
        Returns:
            True if there was processing to cancel, False otherwise
        """
        state = self.get_session_state(session_id)
        
        if state.is_processing:
            logger.info(f"🚫 Cancelling previous processing for session {session_id}")
            
            # Set cancellation token
            if state.cancellation_token:
                state.cancellation_token.set()
            
            # Cancel processing task
            if state.processing_task and not state.processing_task.done():
                state.processing_task.cancel()
                try:
                    await state.processing_task
                except asyncio.CancelledError:
                    logger.info(f"✅ Previous processing cancelled for session {session_id}")
                except Exception as e:
                    logger.error(f"❌ Error during cancellation for session {session_id}: {e}")
            
            # Reset state
            state.is_processing = False
            state.processing_task = None
            state.cancellation_token = None
            
            return True
        
        return False
    
    def add_audio_chunk(self, session_id: str, audio_data: bytes, format: str) -> None:
        """
        Add audio chunk to session buffer and start pause detection.
        
        Args:
            session_id: Session ID
            audio_data: Raw audio bytes
            format: Audio format
        """
        state = self.get_session_state(session_id)
        
        chunk = AudioChunk(
            data=audio_data,
            format=format,
            timestamp=time.time(),
            size=len(audio_data)
        )
        
        state.audio_buffer.append(chunk)
        state.last_audio_timestamp = chunk.timestamp
        
        logger.debug(f"📦 Added audio chunk to session {session_id}: {len(audio_data)} bytes")
        
        # Start or restart pause detection task
        self._start_pause_detection_task(session_id)
    

    
    def should_extend_processing(self, session_id: str) -> bool:
        """
        Check if we should extend/cancel current processing due to new audio.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            True if current processing should be cancelled due to new audio
        """
        state = self.get_session_state(session_id)
        
        if not state.is_processing:
            return False
        
        # If we have new audio chunks after processing started, we should cancel and restart
        if state.audio_buffer:
            # Check if any audio chunk is newer than when processing started
            if state.last_audio_timestamp:
                processing_start_time = time.time() - (self.max_extension_ms / 1000)
                
                for chunk in state.audio_buffer:
                    if chunk.timestamp > processing_start_time:
                        logger.info(f"🔄 New audio detected during processing for session {session_id}, will cancel and restart")
                        return True
        
        return False
    
    def get_combined_audio(self, session_id: str) -> tuple[bytes, str]:
        """
        Get combined audio from buffer and clear it.
        
        Args:
            session_id: Session ID
            
        Returns:
            Tuple of (combined_audio_data, format)
        """
        state = self.get_session_state(session_id)
        
        if not state.audio_buffer:
            return b'', 'wav'
        
        # For now, just concatenate the audio data
        # TODO: Implement proper audio mixing/concatenation based on format
        combined_data = b''.join(chunk.data for chunk in state.audio_buffer)
        format = state.audio_buffer[0].format
        
        # Clear buffer
        state.audio_buffer.clear()
        
        logger.info(f"🔗 Combined {len(state.audio_buffer)} audio chunks for session {session_id}: {len(combined_data)} bytes")
        
        return combined_data, format
    
    def mark_processing_started(self, session_id: str, task: asyncio.Task, cancellation_token: asyncio.Event) -> None:
        """
        Mark that processing has started for session.
        
        Args:
            session_id: Session ID
            task: The processing task
            cancellation_token: Cancellation token for the task
        """
        state = self.get_session_state(session_id)
        state.is_processing = True
        state.processing_task = task
        state.cancellation_token = cancellation_token
        
        logger.info(f"🚀 Processing started for session {session_id}")
    
    def mark_processing_completed(self, session_id: str, success: bool = True) -> None:
        """
        Mark that processing has completed for session.
        
        Args:
            session_id: Session ID
            success: Whether processing completed successfully
        """
        state = self.get_session_state(session_id)
        state.is_processing = False
        state.processing_task = None
        state.cancellation_token = None
        
        status = "✅ completed" if success else "❌ failed"
        logger.info(f"🏁 Processing {status} for session {session_id}")
    
    def _estimate_audio_duration_ms(self, audio_size: int, format: str) -> float:
        """
        Estimate audio duration in milliseconds based on size and format.
        
        Args:
            audio_size: Size of audio data in bytes
            format: Audio format
            
        Returns:
            Estimated duration in milliseconds
        """
        # Rough estimates based on common audio formats
        if format.lower() in ['pcm', 'pcm16', 'raw']:
            # PCM 16-bit, 16kHz, mono: 2 bytes per sample, 16000 samples per second
            samples = audio_size / 2
            duration_seconds = samples / 16000
            return duration_seconds * 1000
        elif format.lower() == 'wav':
            # Assume similar to PCM for rough estimate (header overhead is minimal)
            samples = (audio_size - 44) / 2  # Subtract WAV header
            duration_seconds = max(0, samples / 16000)
            return duration_seconds * 1000
        else:
            # For compressed formats, very rough estimate
            # Assume ~8:1 compression ratio
            uncompressed_size = audio_size * 8
            samples = uncompressed_size / 2
            duration_seconds = samples / 16000
            return duration_seconds * 1000
    
    def register_processing_callback(self, session_id: str, callback: callable) -> None:
        """Register a callback to be called when processing should start"""
        self.processing_callbacks[session_id] = callback
        logger.info(f"✅ Registered processing callback for session {session_id}")
    
    def unregister_processing_callback(self, session_id: str) -> None:
        """Unregister processing callback for session"""
        if session_id in self.processing_callbacks:
            del self.processing_callbacks[session_id]
            logger.info(f"🗑️ Unregistered processing callback for session {session_id}")
    
    def _start_pause_detection_task(self, session_id: str) -> None:
        """Start or restart pause detection task for session"""
        # Cancel existing task if running
        if session_id in self.pause_check_tasks:
            self.pause_check_tasks[session_id].cancel()
        
        # Start new pause detection task
        self.pause_check_tasks[session_id] = asyncio.create_task(
            self._pause_detection_loop(session_id)
        )
        logger.debug(f"🎯 Started pause detection task for session {session_id}")
    
    async def _pause_detection_loop(self, session_id: str) -> None:
        """Background loop to detect pauses in audio stream"""
        try:
            while True:
                # Wait for the pause threshold duration
                await asyncio.sleep(self.pause_threshold_ms / 1000.0)
                
                state = self.get_session_state(session_id)
                
                # Check if session still exists and has audio
                if not state.audio_buffer:
                    continue
                
                # Check if we're already processing
                if state.is_processing:
                    continue
                
                # Check if enough time has passed since last audio
                if state.last_audio_timestamp:
                    time_since_last_audio = (time.time() - state.last_audio_timestamp) * 1000
                    
                    if time_since_last_audio >= self.pause_threshold_ms:
                        # Check if we have minimum audio length
                        total_audio_size = sum(chunk.size for chunk in state.audio_buffer)
                        estimated_duration_ms = self._estimate_audio_duration_ms(total_audio_size, state.audio_buffer[0].format)
                        
                        if estimated_duration_ms >= self.min_audio_length_ms:
                            logger.info(f"⏸️ Pause detected for session {session_id}: {time_since_last_audio:.0f}ms silence, {estimated_duration_ms:.0f}ms audio")
                            
                            # Call the processing callback if registered
                            if session_id in self.processing_callbacks:
                                try:
                                    callback = self.processing_callbacks[session_id]
                                    logger.info(f"🚀 Triggering processing callback for session {session_id}")
                                    
                                    # Create a task to call the callback asynchronously
                                    asyncio.create_task(callback())
                                except Exception as e:
                                    logger.error(f"❌ Error calling processing callback for session {session_id}: {e}")
                            else:
                                logger.warning(f"⚠️ No processing callback registered for session {session_id}")
                            
                            # Exit the loop since processing should start
                            break
                        else:
                            logger.debug(f"⏭️ Audio too short for session {session_id}: {estimated_duration_ms:.0f}ms < {self.min_audio_length_ms}ms")
                
        except asyncio.CancelledError:
            logger.debug(f"🛑 Pause detection task cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"❌ Error in pause detection loop for session {session_id}: {e}")
    
    def check_processing_requested(self, session_id: str) -> bool:
        """Check if processing has been requested for this session"""
        state = self.get_session_state(session_id)
        
        # Check if processing_requested flag exists and is True
        processing_requested = getattr(state, 'processing_requested', False)
        
        if processing_requested:
            # Reset the flag
            state.processing_requested = False
            return True
        
        return False
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        state = self.get_session_state(session_id)
        
        total_buffer_size = sum(chunk.size for chunk in state.audio_buffer)
        estimated_duration = self._estimate_audio_duration_ms(total_buffer_size, 'pcm16') if state.audio_buffer else 0
        
        return {
            "session_id": session_id,
            "is_processing": state.is_processing,
            "buffer_chunks": len(state.audio_buffer),
            "buffer_size_bytes": total_buffer_size,
            "estimated_duration_ms": estimated_duration,
            "last_audio_timestamp": state.last_audio_timestamp,
            "has_cancellation_token": state.cancellation_token is not None,
            "has_processing_task": state.processing_task is not None
        }
    
    def get_all_sessions_stats(self) -> Dict[str, Any]:
        """Get statistics for all sessions"""
        return {
            "total_sessions": len(self.session_states),
            "active_processing_sessions": sum(1 for state in self.session_states.values() if state.is_processing),
            "sessions": {
                session_id: self.get_session_stats(session_id)
                for session_id in self.session_states.keys()
            },
            "configuration": {
                "pause_threshold_ms": self.pause_threshold_ms,
                "max_extension_ms": self.max_extension_ms,
                "min_audio_length_ms": self.min_audio_length_ms,
                "pause_processing_enabled": self.enable_pause_processing
            }
        }


# Global audio buffer manager instance
audio_buffer_manager = AudioBufferManager() 