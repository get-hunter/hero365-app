import sentry_sdk
import logging
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.main import api_router
from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.cors_handler import add_cors_middleware
from app.api.middleware.auth_handler import AuthMiddleware
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


def create_application() -> FastAPI:
    """Create and configure the FastAPI application with clean architecture."""
    
    # Initialize Sentry if configured
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

    # Create FastAPI application
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
        description="Hero365 App - the AI-powered business management platform for home service businesses",
        version="2.0.0",
        redirect_slashes=False,  # Prevent automatic redirects that strip auth headers
        servers=[
            {
                "url": settings.API_BASE_URL,
                "description": f"{settings.ENVIRONMENT.title()} environment"
            }
        ] if settings.ENVIRONMENT == "production" else None
    )

    # Add middleware in correct order (last added = first executed)
    
    # 1. Error handling middleware (outermost - catches all exceptions)
    application.add_middleware(ErrorHandlerMiddleware)
    
    # 2. CORS middleware
    add_cors_middleware(application)
    
    # 3. Authentication middleware (innermost - sets user context)
    application.add_middleware(
        AuthMiddleware,
        skip_paths=[
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            f"{settings.API_V1_STR}/auth/signup",
            f"{settings.API_V1_STR}/auth/signup/phone",
            f"{settings.API_V1_STR}/auth/signin",
            f"{settings.API_V1_STR}/auth/signin/phone",
            f"{settings.API_V1_STR}/auth/otp/send",
            f"{settings.API_V1_STR}/auth/otp/verify",
            f"{settings.API_V1_STR}/auth/oauth/google",
            f"{settings.API_V1_STR}/auth/oauth/apple",
            f"{settings.API_V1_STR}/auth/apple/signin",
            f"{settings.API_V1_STR}/auth/google/signin",
            f"{settings.API_V1_STR}/auth/password-recovery",
            f"{settings.API_V1_STR}/auth/refresh",
        ]
    )

    # Include API router
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add health check endpoint (outside of API versioning for infrastructure)
    @application.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy", "environment": settings.ENVIRONMENT}
    
    return application


# Create the application instance
app = create_application()
