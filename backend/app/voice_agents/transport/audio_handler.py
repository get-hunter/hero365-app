"""
Audio Handler

Audio processing utilities for voice agents.
"""

import base64
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AudioHandler:
    """Audio processing handler for voice agents"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        Initialize audio handler
        
        Args:
            sample_rate: Audio sample rate (default: 16000 Hz)
            channels: Number of audio channels (default: 1 - mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
    
    def decode_audio_data(self, audio_data: str) -> Optional[np.ndarray]:
        """
        Decode base64 audio data to numpy array
        
        Args:
            audio_data: Base64 encoded audio data
            
        Returns:
            Decoded audio as numpy array or None if error
        """
        try:
            # Decode base64 data
            audio_bytes = base64.b64decode(audio_data)
            
            # Convert to numpy array (assuming 16-bit PCM)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Reshape for multi-channel audio if needed
            if self.channels > 1:
                audio_array = audio_array.reshape(-1, self.channels)
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Error decoding audio data: {e}")
            return None
    
    def encode_audio_data(self, audio_array: np.ndarray) -> Optional[str]:
        """
        Encode numpy array to base64 audio data
        
        Args:
            audio_array: Audio data as numpy array
            
        Returns:
            Base64 encoded audio data or None if error
        """
        try:
            # Ensure correct data type
            if audio_array.dtype != np.int16:
                audio_array = audio_array.astype(np.int16)
            
            # Convert to bytes
            audio_bytes = audio_array.tobytes()
            
            # Encode to base64
            audio_data = base64.b64encode(audio_bytes).decode('utf-8')
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error encoding audio data: {e}")
            return None
    
    def concatenate_audio_chunks(self, audio_chunks: list) -> Optional[np.ndarray]:
        """
        Concatenate multiple audio chunks into single array
        
        Args:
            audio_chunks: List of numpy arrays containing audio data
            
        Returns:
            Concatenated audio array or None if error
        """
        try:
            if not audio_chunks:
                return None
            
            # Concatenate all chunks
            concatenated = np.concatenate(audio_chunks, axis=0)
            
            return concatenated
            
        except Exception as e:
            logger.error(f"Error concatenating audio chunks: {e}")
            return None
    
    def normalize_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """
        Normalize audio array to prevent clipping
        
        Args:
            audio_array: Audio data as numpy array
            
        Returns:
            Normalized audio array
        """
        try:
            # Convert to float for processing
            audio_float = audio_array.astype(np.float32)
            
            # Normalize to [-1, 1] range
            max_val = np.max(np.abs(audio_float))
            if max_val > 0:
                audio_float = audio_float / max_val
            
            # Convert back to int16
            audio_normalized = (audio_float * 32767).astype(np.int16)
            
            return audio_normalized
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio_array
    
    def apply_noise_reduction(self, audio_array: np.ndarray) -> np.ndarray:
        """
        Apply basic noise reduction to audio
        
        Args:
            audio_array: Audio data as numpy array
            
        Returns:
            Noise-reduced audio array
        """
        try:
            # Simple noise gate - remove samples below threshold
            threshold = 0.01 * np.max(np.abs(audio_array))
            audio_array = np.where(np.abs(audio_array) < threshold, 0, audio_array)
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Error applying noise reduction: {e}")
            return audio_array
    
    def get_audio_duration(self, audio_array: np.ndarray) -> float:
        """
        Get duration of audio in seconds
        
        Args:
            audio_array: Audio data as numpy array
            
        Returns:
            Duration in seconds
        """
        try:
            num_samples = len(audio_array)
            duration = num_samples / self.sample_rate
            return duration
            
        except Exception as e:
            logger.error(f"Error calculating audio duration: {e}")
            return 0.0
    
    def validate_audio_format(self, audio_array: np.ndarray) -> Tuple[bool, str]:
        """
        Validate audio format and quality
        
        Args:
            audio_array: Audio data as numpy array
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if array is empty
            if len(audio_array) == 0:
                return False, "Empty audio array"
            
            # Check data type
            if audio_array.dtype not in [np.int16, np.float32]:
                return False, f"Unsupported audio data type: {audio_array.dtype}"
            
            # Check duration (minimum 0.1 seconds)
            duration = self.get_audio_duration(audio_array)
            if duration < 0.1:
                return False, f"Audio too short: {duration:.3f} seconds"
            
            # Check for clipping
            if audio_array.dtype == np.int16:
                max_val = np.max(np.abs(audio_array))
                if max_val >= 32767:
                    logger.warning("Audio may be clipped")
            
            return True, "Audio format is valid"
            
        except Exception as e:
            logger.error(f"Error validating audio format: {e}")
            return False, str(e) 