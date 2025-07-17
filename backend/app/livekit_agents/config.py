"""
LiveKit Agents Configuration for Hero365
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the environments folder
env_path = Path(__file__).parent.parent.parent.parent / "environments" / ".env"
load_dotenv(env_path)

class LiveKitConfig:
    """Configuration settings for Hero365 LiveKit agents"""
    
    # LiveKit connection settings
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")
    
    # Audio processing settings
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    CARTESIA_API_KEY: str = os.getenv("CARTESIA_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # External services
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    OPENWEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    
    # Hero365 specific settings
    HERO365_VOICE_ENABLED: bool = os.getenv("HERO365_VOICE_ENABLED", "true").lower() == "true"
    HERO365_AGENT_NAME: str = os.getenv("HERO365_AGENT_NAME", "hero365-voice-assistant")
    
    # Performance settings
    MAX_CONCURRENT_SESSIONS: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "100"))
    AUDIO_BUFFER_SIZE: int = int(os.getenv("AUDIO_BUFFER_SIZE", "1024"))
    
    # LiveKit worker settings
    LIVEKIT_WORKER_PROCESSES: int = int(os.getenv("LIVEKIT_WORKER_PROCESSES", "3"))
    LIVEKIT_LOAD_THRESHOLD: float = float(os.getenv("LIVEKIT_LOAD_THRESHOLD", "0.8"))
    LIVEKIT_MEMORY_LIMIT_MB: int = int(os.getenv("LIVEKIT_MEMORY_LIMIT_MB", "512"))
    LIVEKIT_MEMORY_WARN_MB: int = int(os.getenv("LIVEKIT_MEMORY_WARN_MB", "256"))
    
    # Voice agent audio processing
    VOICE_AGENT_NOISE_CANCELLATION: bool = os.getenv("VOICE_AGENT_NOISE_CANCELLATION", "true").lower() == "true"
    VOICE_AGENT_ECHO_CANCELLATION: bool = os.getenv("VOICE_AGENT_ECHO_CANCELLATION", "true").lower() == "true"
    VOICE_AGENT_AUTO_GAIN_CONTROL: bool = os.getenv("VOICE_AGENT_AUTO_GAIN_CONTROL", "true").lower() == "true"
    
    # Blue-collar industry optimization
    INDUSTRY_KEYWORDS: list[str] = [
        "estimate", "invoice", "job", "contractor", "plumbing", 
        "electrical", "HVAC", "construction", "repair", "install",
        "maintenance", "quote", "appointment", "schedule", "customer",
        "service", "technician", "project", "materials", "labor",
        "permit", "inspection", "warranty", "emergency", "equipment"
    ]
    
    # Voice preferences
    DEFAULT_VOICE_SPEED: float = 1.0
    DEFAULT_VOICE_LANGUAGE: str = "en"
    DEFAULT_TTS_MODEL: str = "sonic-2"
    DEFAULT_STT_MODEL: str = "nova-3"
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    DEFAULT_LLM_TEMPERATURE: float = 0.7
    DEFAULT_LLM_MAX_TOKENS: int = 500
    
    # Turn detection settings
    TURN_DETECTION_THRESHOLD: float = 0.7
    MIN_SPEECH_DURATION: float = 0.3
    MIN_SILENCE_DURATION: float = 0.5
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = [
            cls.LIVEKIT_URL,
            cls.LIVEKIT_API_KEY,
            cls.LIVEKIT_API_SECRET,
        ]
        
        missing_vars = [var for var in required_vars if not var]
        if missing_vars:
            print(f"❌ Missing required configuration variables: {missing_vars}")
            return False
        
        return True
    
    @classmethod
    def validate_ai_services(cls) -> dict[str, bool]:
        """Validate AI service configurations"""
        return {
            "deepgram": bool(cls.DEEPGRAM_API_KEY),
            "cartesia": bool(cls.CARTESIA_API_KEY),
            "openai": bool(cls.OPENAI_API_KEY),
            "serpapi": bool(cls.SERPAPI_KEY),
            "google_maps": bool(cls.GOOGLE_MAPS_API_KEY),
            "openweather": bool(cls.OPENWEATHER_API_KEY),
        }
    
    @classmethod
    def get_voice_pipeline_config(cls) -> dict:
        """Get voice pipeline configuration"""
        return {
            "stt": {
                "model": cls.DEFAULT_STT_MODEL,
                "language": cls.DEFAULT_VOICE_LANGUAGE,
                "keywords": cls.INDUSTRY_KEYWORDS,
                "interim_results": True,
                "punctuation": True,
                "profanity_filter": False,
                "redact_pii": True,
            },
            "llm": {
                "model": cls.DEFAULT_LLM_MODEL,
                "temperature": cls.DEFAULT_LLM_TEMPERATURE,
                "max_tokens": cls.DEFAULT_LLM_MAX_TOKENS,
                "top_p": 0.9,
            },
            "tts": {
                "model": cls.DEFAULT_TTS_MODEL,
                "voice": "a0e99841-438c-4a64-b679-ae501e7d6091",  # Professional male voice
                "speed": cls.DEFAULT_VOICE_SPEED,
                "language": cls.DEFAULT_VOICE_LANGUAGE,
            },
            "turn_detection": {
                "threshold": cls.TURN_DETECTION_THRESHOLD,
                "min_speech_duration": cls.MIN_SPEECH_DURATION,
                "min_silence_duration": cls.MIN_SILENCE_DURATION,
            },
            "audio_processing": {
                "noise_cancellation": cls.VOICE_AGENT_NOISE_CANCELLATION,
                "echo_cancellation": cls.VOICE_AGENT_ECHO_CANCELLATION,
                "auto_gain_control": cls.VOICE_AGENT_AUTO_GAIN_CONTROL,
            }
        }
    
    @classmethod
    def get_worker_config(cls) -> dict:
        """Get worker configuration"""
        return {
            "agent_name": cls.HERO365_AGENT_NAME,
            "num_idle_processes": cls.LIVEKIT_WORKER_PROCESSES,
            "load_threshold": cls.LIVEKIT_LOAD_THRESHOLD,
            "job_memory_limit_mb": cls.LIVEKIT_MEMORY_LIMIT_MB,
            "job_memory_warn_mb": cls.LIVEKIT_MEMORY_WARN_MB,
            "ws_url": cls.LIVEKIT_URL,
            "api_key": cls.LIVEKIT_API_KEY,
            "api_secret": cls.LIVEKIT_API_SECRET,
        }

# Global config instance
config = LiveKitConfig() 