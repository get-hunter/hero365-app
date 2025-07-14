"""
Audio processing service for speech-to-text using OpenAI Whisper.
"""

import io
import base64
import logging
import struct
import wave
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import asyncio

from ...core.config import settings

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Audio processing service using OpenAI Whisper for STT"""
    
    def __init__(self):
        """Initialize audio processor with OpenAI client"""
        if not settings.OPENAI_API_KEY:
            logger.warning("⚠️ OPENAI_API_KEY not configured - audio processing will be limited")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("✅ Audio processor initialized with OpenAI Whisper")
    
    def _convert_pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
        """
        Convert raw PCM audio data to WAV format.
        
        Args:
            pcm_data: Raw PCM audio bytes
            sample_rate: Sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            sample_width: Bytes per sample (default: 2 for 16-bit)
            
        Returns:
            WAV format audio bytes
        """
        try:
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)
            
            wav_buffer.seek(0)
            wav_data = wav_buffer.getvalue()
            
            logger.info(f"🔄 Converted {len(pcm_data)} bytes PCM to {len(wav_data)} bytes WAV")
            return wav_data
            
        except Exception as e:
            logger.error(f"❌ Error converting PCM to WAV: {e}")
            raise
    
    async def process_audio_to_text(self, audio_data: bytes, format: str = "wav") -> str:
        """
        Convert audio data to text using OpenAI Whisper.
        
        Args:
            audio_data: Raw audio bytes
            format: Audio format (wav, mp3, m4a, etc.)
            
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
            
            # Call OpenAI Whisper API
            transcript = await self.client.audio.transcriptions.create(
                model=settings.OPENAI_SPEECH_MODEL,
                file=audio_file,
                response_format="text"
            )
            
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
    
    async def process_base64_audio(self, base64_audio: str, format: str = "wav") -> str:
        """
        Process base64 encoded audio data.
        
        Args:
            base64_audio: Base64 encoded audio data
            format: Audio format
            
        Returns:
            Transcribed text
        """
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(base64_audio)
            return await self.process_audio_to_text(audio_data, format)
            
        except Exception as e:
            logger.error(f"❌ Error decoding base64 audio: {e}")
            return "I had trouble processing that audio format."
    
    async def convert_text_to_speech(self, text: str, voice: str = None) -> bytes:
        """
        Convert text to speech using OpenAI TTS.
        
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
            
            # Call OpenAI TTS API
            response = await self.client.audio.speech.create(
                model=settings.OPENAI_TTS_MODEL,
                voice=tts_voice,
                input=text,
                response_format="mp3"
            )
            
            # Get audio bytes
            audio_bytes = response.content
            
            logger.info(f"✅ TTS conversion completed: {len(audio_bytes)} bytes MP3 audio")
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ Error converting text to speech: {e}")
            raise Exception(f"TTS conversion failed: {str(e)}")
    
    async def convert_text_to_base64_audio(self, text: str, voice: str = None) -> str:
        """
        Convert text to speech and return as base64 encoded string.
        
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
    
    async def validate_audio_data(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Validate and analyze audio data.
        
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
            # Check minimum size
            if len(audio_data) < 100:
                validation["issues"].append("Audio data too small")
                return validation
            
            # Check maximum size (OpenAI has 25MB limit)
            max_size = 25 * 1024 * 1024  # 25MB
            if len(audio_data) > max_size:
                validation["issues"].append(f"Audio data too large ({len(audio_data)} bytes > {max_size} bytes)")
                return validation
            
            # Try to detect format from headers
            if audio_data.startswith(b'RIFF'):
                validation["format"] = "wav"
            elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
                validation["format"] = "mp3"
            elif audio_data.startswith(b'\x00\x00\x00\x20ftypM4A'):
                validation["format"] = "m4a"
            elif audio_data.startswith(b'OggS'):
                validation["format"] = "ogg"
            else:
                validation["format"] = "unknown"
                validation["issues"].append("Unknown audio format")
            
            validation["valid"] = len(validation["issues"]) == 0
            
        except Exception as e:
            validation["issues"].append(f"Validation error: {str(e)}")
        
        return validation
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats"""
        return ["wav", "mp3", "m4a", "ogg", "flac", "webm", "pcm", "pcm16", "raw"]
    
    def get_supported_voices(self) -> list[str]:
        """Get list of supported TTS voices"""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check audio processor health"""
        health = {
            "status": "healthy",
            "openai_configured": bool(self.client),
            "stt_model": settings.OPENAI_SPEECH_MODEL,
            "tts_model": settings.OPENAI_TTS_MODEL,
            "tts_voice": settings.OPENAI_TTS_VOICE,
            "supported_formats": self.get_supported_formats(),
            "supported_voices": self.get_supported_voices(),
            "features": {
                "speech_to_text": bool(self.client),
                "text_to_speech": bool(self.client),
                "pcm_conversion": True
            }
        }
        
        if not self.client:
            health["status"] = "degraded"
            health["issues"] = ["OpenAI API key not configured"]
            health["features"] = {
                "speech_to_text": False,
                "text_to_speech": False,
                "pcm_conversion": True
            }
        
        return health


# Global audio processor instance
audio_processor = AudioProcessor() 