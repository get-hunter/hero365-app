"""
CORS Middleware

Cross-Origin Resource Sharing middleware for the application.
"""

from typing import Sequence
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ...core.config import settings


def add_cors_middleware(app: FastAPI) -> None:
    """
    Add CORS middleware to the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Get allowed origins from settings
    allowed_origins = []
    
    # Add development origins
    if settings.ENVIRONMENT == "local":
        allowed_origins.extend([
            "http://localhost:3000",  # React dev server
            "http://localhost:5173",  # Vite dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ])
    
    # Add production origins from settings
    if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
        allowed_origins.append(settings.FRONTEND_URL)
    
    # Add any additional allowed origins from environment
    if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
        if isinstance(settings.CORS_ORIGINS, str):
            # Parse comma-separated string
            origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
            allowed_origins.extend(origins)
        elif isinstance(settings.CORS_ORIGINS, (list, tuple)):
            allowed_origins.extend(settings.CORS_ORIGINS)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_origins = []
    for origin in allowed_origins:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=unique_origins or ["*"],  # Fallback to allow all if no origins specified
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-API-Key",
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count",
            "X-Has-Next",
            "X-Has-Previous",
        ],
        max_age=600,  # Cache preflight requests for 10 minutes
    )


class CORSConfig:
    """CORS configuration class."""
    
    def __init__(
        self,
        allow_origins: Sequence[str] = None,
        allow_credentials: bool = True,
        allow_methods: Sequence[str] = None,
        allow_headers: Sequence[str] = None,
        expose_headers: Sequence[str] = None,
        max_age: int = 600
    ):
        """
        Initialize CORS configuration.
        
        Args:
            allow_origins: List of allowed origins
            allow_credentials: Whether to allow credentials
            allow_methods: List of allowed HTTP methods
            allow_headers: List of allowed headers
            expose_headers: List of headers to expose to the client
            max_age: Max age for preflight cache
        """
        self.allow_origins = allow_origins or ["*"]
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        self.allow_headers = allow_headers or [
            "Accept",
            "Accept-Language",
            "Content-Language", 
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-API-Key",
        ]
        self.expose_headers = expose_headers or [
            "X-Total-Count",
            "X-Page-Count", 
            "X-Has-Next",
            "X-Has-Previous",
        ]
        self.max_age = max_age
    
    def apply_to_app(self, app: FastAPI) -> None:
        """
        Apply CORS configuration to FastAPI app.
        
        Args:
            app: FastAPI application instance
        """
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allow_origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
            expose_headers=self.expose_headers,
            max_age=self.max_age,
        )


def get_development_cors_config() -> CORSConfig:
    """Get CORS configuration for development environment."""
    return CORSConfig(
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        max_age=300  # Shorter cache for development
    )


def get_production_cors_config(allowed_origins: Sequence[str]) -> CORSConfig:
    """
    Get CORS configuration for production environment.
    
    Args:
        allowed_origins: List of allowed production origins
        
    Returns:
        Production CORS configuration
    """
    return CORSConfig(
        allow_origins=list(allowed_origins),
        allow_credentials=True,
        max_age=3600  # Longer cache for production
    ) 