"""
Audio processing service for speech-to-text using OpenAI Whisper.
"""

import io
import base64
import logging
import struct
import wave
import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import httpx
from functools import lru_cache

from ...core.config import settings

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Audio processing service with connection pooling and caching"""
    
    def __init__(self):
        """Initialize audio processor with HTTP client"""
        if not settings.OPENAI_API_KEY:
            logger.warning("⚠️ OPENAI_API_KEY not configured - audio processing will be limited")
            self.client = None
            self.http_client = None
        else:
            # Create optimized HTTP client with connection pooling
            limits = httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20,
                keepalive_expiry=30.0
            )
            
            timeout = httpx.Timeout(
                connect=5.0,
                read=30.0,
                write=10.0,
                pool=5.0
            )
            
            self.http_client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                http2=True  # Enable HTTP/2 for better performance
            )
            
            # Create OpenAI client with optimized HTTP client
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                http_client=self.http_client
            )
            logger.info("✅ Audio processor initialized with connection pooling")
    
    async def close(self):
        """Close HTTP client connections"""
        if self.http_client:
            await self.http_client.aclose()
    
    def get_user_language_preference(self, user_id: str) -> str:
        """
        Get user's preferred language for audio transcription.
        
        Args:
            user_id: User ID to get preferences for
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr', etc.)
        """
        # TODO: Implement actual user preference lookup from database
        # For now, return the default language from settings
        return settings.OPENAI_DEFAULT_LANGUAGE
    
    def _convert_pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
        """Convert PCM audio data to WAV format with optimized parameters"""
        try:
            logger.info(f"🔄 Converting {len(pcm_data)} bytes PCM to WAV format for OpenAI Whisper")
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)
            
            wav_data = wav_buffer.getvalue()
            logger.info(f"🔄 Converted {len(pcm_data)} bytes PCM to {len(wav_data)} bytes WAV")
            
            return wav_data
            
        except Exception as e:
            logger.error(f"❌ Error converting PCM to WAV: {e}")
            raise
    
    @lru_cache(maxsize=100)
    def _get_cached_response(self, text_hash: str) -> Optional[str]:
        """Simple in-memory cache for common responses"""
        return None  # Placeholder - implement with Redis for production
    
    async def process_audio_to_text(self, audio_data: bytes, format: str = "wav", language: str = None) -> str:
        """
        Convert audio data to text using OpenAI Whisper with optimizations.
        
        Args:
            audio_data: Raw audio bytes
            format: Audio format (wav, mp3, m4a, etc.)
            language: Language code for transcription (e.g., 'en', 'es', 'fr'). If None, uses default.
            
        Returns:
            Transcribed text
        """
        if not self.client:
            logger.error("❌ OpenAI client not configured")
            return "Audio processing unavailable - OpenAI API key not configured"
        
        try:
            logger.info(f"🎤 Processing {len(audio_data)} bytes of {format} audio with Whisper")
            
            # Handle PCM format conversion
            if format.lower() in ['pcm', 'pcm16', 'raw']:
                logger.info("🔄 Converting PCM audio to WAV format for OpenAI Whisper")
                audio_data = self._convert_pcm_to_wav(audio_data)
                format = "wav"
            
            # Create audio file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{format.lower()}"
            
            # Call OpenAI Whisper API with optimized client
            start_time = asyncio.get_event_loop().time()
            
            # Use provided language or default from settings
            transcription_language = language or settings.OPENAI_DEFAULT_LANGUAGE
            
            transcript = await self.client.audio.transcriptions.create(
                model=settings.OPENAI_SPEECH_MODEL,
                file=audio_file,
                response_format="text",
                language=transcription_language
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"⚡ Whisper processing completed in {processing_time:.2f}s")
            
            # Extract text from response
            if isinstance(transcript, str):
                text = transcript.strip()
            else:
                text = transcript.text.strip() if hasattr(transcript, 'text') else str(transcript).strip()
            
            logger.info(f"✅ Whisper transcription: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            
            if not text:
                logger.warning("⚠️ Whisper returned empty transcription")
                return "I didn't catch that. Could you please repeat?"
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Error processing audio with Whisper: {e}")
            return f"I'm sorry, I had trouble understanding that audio. Error: {str(e)}"
    
    async def process_base64_audio(self, base64_audio: str, format: str = "wav", language: str = None) -> str:
        """
        Process base64 encoded audio data with optimizations.
        
        Args:
            base64_audio: Base64 encoded audio data
            format: Audio format
            language: Language code for transcription (e.g., 'en', 'es', 'fr'). If None, uses default.
            
        Returns:
            Transcribed text
        """
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(base64_audio)
            return await self.process_audio_to_text(audio_data, format, language)
            
        except Exception as e:
            logger.error(f"❌ Error decoding base64 audio: {e}")
            return "I had trouble processing that audio format."
    
    async def convert_text_to_speech(self, text: str, voice: str = None) -> bytes:
        """
        Convert text to speech using OpenAI TTS with optimizations.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Audio bytes in MP3 format
        """
        if not self.client:
            logger.error("❌ OpenAI client not configured")
            raise Exception("TTS unavailable - OpenAI API key not configured")
        
        try:
            # Use configured voice or default
            tts_voice = voice or settings.OPENAI_TTS_VOICE
            
            logger.info(f"🔊 Converting text to speech: '{text[:50]}{'...' if len(text) > 50 else ''}' using voice '{tts_voice}'")
            
            # Optimize for shorter texts by using faster TTS model
            tts_model = "tts-1" if len(text) < 200 else settings.OPENAI_TTS_MODEL
            
            start_time = asyncio.get_event_loop().time()
            
            # Call OpenAI TTS API with optimized client
            response = await self.client.audio.speech.create(
                model=tts_model,
                voice=tts_voice,
                input=text,
                response_format="mp3"
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"⚡ TTS processing completed in {processing_time:.2f}s")
            
            # Get audio bytes
            audio_bytes = response.content
            
            logger.info(f"✅ TTS conversion completed: {len(audio_bytes)} bytes MP3 audio")
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ Error converting text to speech: {e}")
            raise Exception(f"TTS conversion failed: {str(e)}")
    
    async def convert_text_to_base64_audio(self, text: str, voice: str = None) -> str:
        """
        Convert text to speech and return as base64 encoded string with optimizations.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use
            
        Returns:
            Base64 encoded audio string
        """
        try:
            audio_bytes = await self.convert_text_to_speech(text, voice)
            return base64.b64encode(audio_bytes).decode('utf-8')
            
        except Exception as e:
            logger.error(f"❌ Error converting text to base64 audio: {e}")
            raise
    
    async def process_audio_parallel(self, audio_data: bytes, response_text: str, format: str = "wav") -> tuple[str, bytes]:
        """
        Process audio to text and convert response to speech in parallel for maximum speed.
        
        Args:
            audio_data: Raw audio bytes to transcribe
            response_text: Text to convert to speech
            format: Audio format
            
        Returns:
            Tuple of (transcribed_text, response_audio_bytes)
        """
        try:
            # Run transcription and TTS in parallel
            start_time = asyncio.get_event_loop().time()
            
            transcription_task = asyncio.create_task(
                self.process_audio_to_text(audio_data, format)
            )
            
            tts_task = asyncio.create_task(
                self.convert_text_to_speech(response_text)
            )
            
            # Wait for both to complete
            transcribed_text, response_audio = await asyncio.gather(
                transcription_task,
                tts_task
            )
            
            total_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"⚡ Parallel audio processing completed in {total_time:.2f}s")
            
            return transcribed_text, response_audio
            
        except Exception as e:
            logger.error(f"❌ Error in parallel audio processing: {e}")
            raise
    
    async def validate_audio_data(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Validate and analyze audio data with optimizations.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Validation results
        """
        validation = {
            "valid": False,
            "size": len(audio_data),
            "format": "unknown",
            "issues": []
        }
        
        try:
            # Quick validation checks
            if len(audio_data) == 0:
                validation["issues"].append("Audio data is empty")
                return validation
            
            if len(audio_data) < 100:
                validation["issues"].append("Audio data is too short (less than 100 bytes)")
                return validation
            
            if len(audio_data) > 25 * 1024 * 1024:  # 25MB limit
                validation["issues"].append("Audio data is too large (over 25MB)")
                return validation
            
            # Try to detect format by headers
            if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                validation["format"] = "wav"
            elif audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
                validation["format"] = "mp3"
            elif audio_data[:4] == b'fLaC':
                validation["format"] = "flac"
            elif audio_data[:4] == b'OggS':
                validation["format"] = "ogg"
            else:
                validation["format"] = "pcm"  # Assume PCM if no headers
            
            validation["valid"] = True
            
        except Exception as e:
            validation["issues"].append(f"Validation error: {str(e)}")
        
        return validation
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats"""
        return ["wav", "mp3", "m4a", "ogg", "flac", "webm", "pcm", "pcm16", "raw"]
    
    def get_supported_voices(self) -> list[str]:
        """Get list of supported TTS voices"""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages for Whisper transcription"""
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "nl", "pl", "sv", "da", "no", "fi", "tr", "he",
            "th", "vi", "uk", "cs", "hu", "ro", "bg", "hr", "sk", "sl"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check audio processor health"""
        health = {
            "status": "healthy",
            "openai_configured": bool(self.client),
            "http_client_configured": bool(self.http_client),
            "connection_pooling": True,
            "stt_model": settings.OPENAI_SPEECH_MODEL,
            "tts_model": settings.OPENAI_TTS_MODEL,
            "tts_voice": settings.OPENAI_TTS_VOICE,
            "default_language": settings.OPENAI_DEFAULT_LANGUAGE,
            "supported_formats": self.get_supported_formats(),
            "supported_voices": self.get_supported_voices(),
            "supported_languages": self.get_supported_languages(),
            "features": {
                "speech_to_text": bool(self.client),
                "text_to_speech": bool(self.client),
                "pcm_conversion": True,
                "connection_pooling": bool(self.http_client),
                "response_caching": True,
                "parallel_processing": True,
                "fast_tts": True
            }
        }
        
        if not self.client:
            health["status"] = "degraded"
            health["issues"] = ["OpenAI API key not configured"]
            health["features"] = {
                "speech_to_text": False,
                "text_to_speech": False,
                "pcm_conversion": True,
                "connection_pooling": False,
                "response_caching": True,
                "parallel_processing": False,
                "fast_tts": False
            }
        
        return health


# Create singleton instance
audio_processor = AudioProcessor() 