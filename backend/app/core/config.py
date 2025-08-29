import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use .env file from environments folder
        env_file="../environments/.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # JWT algorithm for legacy token compatibility
    JWT_ALGORITHM: str = "HS256"
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    
    # Custom domain configuration
    API_DOMAIN: str = "api.hero365.ai"
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def API_V1_STR(self) -> str:
        """Get the API prefix based on environment."""
        if self.ENVIRONMENT == "production":
            return "/v1"  # Production uses custom domain api.hero365.ai/v1
        else:
            return "/api/v1"  # Local/staging uses /api/v1 prefix
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def API_BASE_URL(self) -> str:
        """Get the full API base URL based on environment."""
        if self.ENVIRONMENT == "local":
            return f"http://localhost:8000{self.API_V1_STR}"
        elif self.ENVIRONMENT == "production":
            return f"https://{self.API_DOMAIN}{self.API_V1_STR}"
        else:  # staging
            return f"http://localhost:8000{self.API_V1_STR}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Centralized CORS origins configuration.
        Single source of truth for all allowed origins across environments.
        """
        cors_origins = []
        
        # 1. Environment variable origins (from .env BACKEND_CORS_ORIGINS)
        if self.BACKEND_CORS_ORIGINS:
            cors_origins.extend([str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS])
        
        # 2. Frontend host (from FRONTEND_HOST env var)
        if self.FRONTEND_HOST:
            cors_origins.append(self.FRONTEND_HOST.rstrip("/"))
        
        # 3. Development origins (always included for local environment)
        if self.ENVIRONMENT == "local":
            cors_origins.extend([
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                "https://localhost:3000",
                "https://localhost:5173"
            ])
        
        # 4. Cloudflare Pages domains (for website deployments)
        cors_origins.extend([
            "https://hero365-contractors-webs.pages.dev",  # Main project domain
            # Current active deployments (add new ones as needed):
            "https://bb076026.hero365-contractors-webs.pages.dev",
            "https://4b916b7d.hero365-contractors-webs.pages.dev",
        ])
        
        # 5. Production domains (only in production)
        if self.ENVIRONMENT == "production":
            cors_origins.extend([
                f"https://{self.API_DOMAIN}",
                "https://hero365.ai",
                "https://www.hero365.ai",
                "https://app.hero365.ai"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_origins = []
        for origin in cors_origins:
            if origin and origin not in seen:
                seen.add(origin)
                unique_origins.append(origin)
        
        return unique_origins
    
    def add_cloudflare_deployment_url(self, deployment_url: str) -> None:
        """
        Helper method to add a new Cloudflare Pages deployment URL to CORS origins.
        This is useful for dynamically adding new deployment URLs without code changes.
        
        Args:
            deployment_url: The full deployment URL (e.g., "https://abc123.hero365-contractors-webs.pages.dev")
        """
        # This would require implementing a dynamic CORS update mechanism
        # For now, new deployment URLs should be added to the all_cors_origins method above
        pass

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    
    # Supabase Configuration (required)
    SUPABASE_URL: str
    SUPABASE_KEY: str  # Anon key for client operations
    SUPABASE_SERVICE_KEY: str  # Service key for admin operations
    
    # External Services for Real-time Optimization
    GOOGLE_MAPS_API_KEY: str | None = None
    OPENWEATHER_API_KEY: str | None = None  # OpenWeatherMap API key
    SERPAPI_KEY: str | None = None  # SerpAPI for web search
    WEATHER_API_KEY: str | None = None  # Legacy weather API key (deprecated)
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    
    # Resend Email Configuration
    RESEND_API_KEY: str | None = None
    DEFAULT_FROM_EMAIL: str | None = None
    DEFAULT_FROM_NAME: str | None = None
    
    # LiveKit Configuration
    LIVEKIT_URL: str | None = None
    LIVEKIT_API_KEY: str | None = None
    LIVEKIT_API_SECRET: str | None = None
    
    # AI Provider API Keys for Voice Agents
    OPENAI_API_KEY: str | None = None
    DEEPGRAM_API_KEY: str | None = None
    CARTESIA_API_KEY: str | None = None
    
    # AI Provider Configuration for Content Generation
    CONTENT_GENERATION_PROVIDER: Literal["openai", "claude", "gemini"] = "claude"
    CLAUDE_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    # Content Generation Model Settings
    OPENAI_CONTENT_MODEL: str = "gpt-4o"
    CLAUDE_CONTENT_MODEL: str = "claude-sonnet-4-20250514"
    GEMINI_CONTENT_MODEL: str = "gemini-1.5-pro"
    
    # Content Generation Parameters
    CONTENT_MAX_TOKENS: int = 4000
    CONTENT_TEMPERATURE: float = 0.7
    
    # Voice Agent Context & Memory Configuration
    REDIS_URL: str = "redis://localhost:6379"
    MEM0_API_KEY: str | None = None
    OPENAI_VOICE_MODEL: str = "gpt-4o-realtime-preview"
    OPENAI_SPEECH_MODEL: str = "whisper-1"
    OPENAI_TTS_MODEL: str = "tts-1-hd"
    OPENAI_TTS_VOICE: str = "alloy"
    OPENAI_DEFAULT_LANGUAGE: str = "en"  # Default language for Whisper transcription
    
    # Voice Agent Optimization Settings
    VOICE_PAUSE_THRESHOLD_MS: int = 800  # Milliseconds of silence to trigger processing
    VOICE_MAX_EXTENSION_MS: int = 5000   # Max milliseconds to wait for utterance extension
    VOICE_MIN_AUDIO_LENGTH_MS: int = 200 # Minimum audio length to process
    VOICE_ENABLE_PAUSE_PROCESSING: bool = True  # Enable send-on-pause optimization
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    
    # Website Builder Configuration
    WEBSITE_TEMPLATE_PATH: str = "app/infrastructure/templates"
    WEBSITE_BUILD_PATH: str = "build_output"
    WEBSITE_BUILD_OUTPUT_PATH: str = "build_output"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Hero365 Subdomain Configuration
    HERO365_CLOUDFRONT_DISTRIBUTION_ID: str | None = None
    HERO365_ROUTE53_ZONE_ID: str | None = None
    HERO365_CLOUDFRONT_DOMAIN: str = "d123456789.cloudfront.net"
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SUPABASE_ANON_KEY(self) -> str:
        """Alias for SUPABASE_KEY for clarity."""
        return self.SUPABASE_KEY

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.DEFAULT_FROM_NAME:
            self.DEFAULT_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        # Check if Resend is configured
        return bool(self.RESEND_API_KEY and self.DEFAULT_FROM_EMAIL)
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def livekit_enabled(self) -> bool:
        # Check if LiveKit is configured
        return bool(self.LIVEKIT_URL and self.LIVEKIT_API_KEY and self.LIVEKIT_API_SECRET)
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def voice_agents_enabled(self) -> bool:
        # Check if voice agents are fully configured
        return bool(
            self.OPENAI_API_KEY and 
            self.REDIS_URL
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        return self

    @model_validator(mode="after")
    def _validate_supabase_config(self) -> Self:
        """Validate that all required Supabase configuration is provided."""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY (anon key) is required")
        if not self.SUPABASE_SERVICE_KEY:
            raise ValueError("SUPABASE_SERVICE_KEY is required")
        
        # Validate URL format
        if not (self.SUPABASE_URL.startswith("https://") or self.SUPABASE_URL.startswith("http://")):
            raise ValueError("SUPABASE_URL must start with https:// or http://")
        
        return self


settings = Settings()  # type: ignore
