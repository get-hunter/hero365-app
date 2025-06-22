"""
Middleware Manager

Centralized middleware configuration and management for Hero365 application.
Provides clean separation of concerns and easy middleware management.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .error_handler import ErrorHandlerMiddleware
from .cors_handler import CORSMiddleware as CustomCORSMiddleware
from .auth_handler import AuthMiddleware
from .business_context_middleware import BusinessContextMiddleware
from ...core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class MiddlewareConfig:
    """Configuration class for middleware settings."""
    
    def __init__(self):
        self.api_v1_str = settings.API_V1_STR
        
    @property
    def public_paths(self) -> List[str]:
        """Paths that don't require authentication."""
        return [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
        ]
    
    @property
    def auth_skip_paths(self) -> List[str]:
        """Paths that skip authentication middleware."""
        return self.public_paths + [
            f"{self.api_v1_str}/auth/signup",
            f"{self.api_v1_str}/auth/signup/phone",
            f"{self.api_v1_str}/auth/signin",
            f"{self.api_v1_str}/auth/signin/phone",
            f"{self.api_v1_str}/auth/otp/send",
            f"{self.api_v1_str}/auth/otp/verify",
            f"{self.api_v1_str}/auth/oauth/google",
            f"{self.api_v1_str}/auth/oauth/apple",
            f"{self.api_v1_str}/auth/apple/signin",
            f"{self.api_v1_str}/auth/google/signin",
            f"{self.api_v1_str}/auth/password-recovery",
            f"{self.api_v1_str}/auth/refresh",
        ]
    
    @property
    def business_context_skip_paths(self) -> List[str]:
        """Paths that skip business context middleware."""
        return self.public_paths + [
            f"{self.api_v1_str}/auth/",
            f"{self.api_v1_str}/users/me",
            f"{self.api_v1_str}/business-context/",
        ]
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS allowed origins."""
        if settings.BACKEND_CORS_ORIGINS:
            return [str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS]
        return []


class MiddlewareManager:
    """
    Centralized middleware manager for Hero365 application.
    
    Manages middleware configuration, ordering, and application to FastAPI app.
    Middleware are applied in reverse order (last added = first executed).
    """
    
    def __init__(self, config: Optional[MiddlewareConfig] = None):
        """
        Initialize middleware manager.
        
        Args:
            config: Middleware configuration. If None, uses default config.
        """
        self.config = config or MiddlewareConfig()
        self.middlewares = []
        self._setup_middlewares()
    
    def _setup_middlewares(self):
        """Setup middleware configuration in execution order (reverse of addition order)."""
        
        # Middleware execution order (outermost to innermost):
        # 1. Error Handler - Catches all exceptions
        # 2. CORS - Handles cross-origin requests  
        # 3. Business Context - Validates business access
        # 4. Authentication - Sets user context
        
        self.middlewares = [
            {
                "name": "ErrorHandler",
                "middleware": ErrorHandlerMiddleware,
                "kwargs": {},
                "description": "Catches and formats all application exceptions"
            },
            {
                "name": "CustomCORS", 
                "middleware": CustomCORSMiddleware,
                "kwargs": {},
                "description": "Custom CORS handling with additional features"
            },
            {
                "name": "BusinessContext",
                "middleware": BusinessContextMiddleware,
                "kwargs": {
                    "skip_paths": self.config.business_context_skip_paths
                },
                "description": "Validates business access and permissions"
            },
            {
                "name": "Authentication",
                "middleware": AuthMiddleware,
                "kwargs": {
                    "skip_paths": self.config.auth_skip_paths
                },
                "description": "JWT token validation and user authentication"
            }
        ]
    
    def apply_cors_middleware(self, app: FastAPI):
        """Apply CORS middleware if origins are configured."""
        if self.config.cors_origins:
            logger.info(f"Applying CORS middleware with origins: {self.config.cors_origins}")
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        else:
            logger.info("No CORS origins configured, skipping CORS middleware")
    
    def apply_custom_middlewares(self, app: FastAPI):
        """Apply all custom middlewares to the FastAPI application."""
        logger.info("Applying custom middlewares...")
        
        for middleware_config in self.middlewares:
            name = middleware_config["name"]
            middleware_class = middleware_config["middleware"]
            kwargs = middleware_config["kwargs"]
            description = middleware_config["description"]
            
            logger.info(f"Adding {name} middleware: {description}")
            
            try:
                app.add_middleware(middleware_class, **kwargs)
                logger.info(f"✅ {name} middleware added successfully")
            except Exception as e:
                logger.error(f"❌ Failed to add {name} middleware: {str(e)}")
                raise
    
    def apply_all_middlewares(self, app: FastAPI):
        """Apply all middlewares to the FastAPI application."""
        logger.info("🚀 Starting middleware application process...")
        
        # Apply CORS middleware first (if configured)
        self.apply_cors_middleware(app)
        
        # Apply custom middlewares
        self.apply_custom_middlewares(app)
        
        logger.info("✅ All middlewares applied successfully!")
        self._log_middleware_stack()
    
    def _log_middleware_stack(self):
        """Log the middleware stack for debugging."""
        logger.info("📋 Middleware execution order (outermost to innermost):")
        
        execution_order = ["CORS (if configured)"] + [m["name"] for m in self.middlewares]
        
        for i, middleware_name in enumerate(execution_order, 1):
            logger.info(f"  {i}. {middleware_name}")
    
    def get_middleware_info(self) -> Dict[str, Any]:
        """Get information about configured middlewares."""
        return {
            "total_middlewares": len(self.middlewares),
            "cors_enabled": bool(self.config.cors_origins),
            "cors_origins": self.config.cors_origins,
            "middlewares": [
                {
                    "name": m["name"],
                    "description": m["description"],
                    "skip_paths": m["kwargs"].get("skip_paths", [])
                }
                for m in self.middlewares
            ]
        }
    
    def add_custom_middleware(self, name: str, middleware_class, description: str = "", **kwargs):
        """
        Add a custom middleware to the stack.
        
        Args:
            name: Middleware name for logging
            middleware_class: Middleware class to add
            description: Description of what the middleware does
            **kwargs: Additional arguments for the middleware
        """
        middleware_config = {
            "name": name,
            "middleware": middleware_class,
            "kwargs": kwargs,
            "description": description or f"Custom {name} middleware"
        }
        
        self.middlewares.append(middleware_config)
        logger.info(f"Added custom middleware: {name}")
    
    def remove_middleware(self, name: str) -> bool:
        """
        Remove a middleware from the stack by name.
        
        Args:
            name: Name of the middleware to remove
            
        Returns:
            True if middleware was removed, False if not found
        """
        original_count = len(self.middlewares)
        self.middlewares = [m for m in self.middlewares if m["name"] != name]
        
        removed = len(self.middlewares) < original_count
        if removed:
            logger.info(f"Removed middleware: {name}")
        else:
            logger.warning(f"Middleware not found: {name}")
        
        return removed


def create_middleware_manager(environment: str = None) -> MiddlewareManager:
    """
    Factory function to create middleware manager based on environment.
    
    Args:
        environment: Environment name (production, development, testing)
        
    Returns:
        Configured MiddlewareManager instance
    """
    config = MiddlewareConfig()
    manager = MiddlewareManager(config)
    
    # Environment-specific middleware adjustments
    if environment == "testing":
        # For testing, we might want to remove certain middlewares
        logger.info("Configuring middleware for testing environment")
        # Could add test-specific middleware here
    elif environment == "development":
        # Development might have additional debugging middleware
        logger.info("Configuring middleware for development environment")
    elif environment == "production":
        # Production might have additional security middleware
        logger.info("Configuring middleware for production environment")
    
    return manager


# Global middleware manager instance
middleware_manager = create_middleware_manager(settings.ENVIRONMENT) 