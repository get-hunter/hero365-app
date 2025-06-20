import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.cors_handler import add_cors_middleware
from app.api.middleware.auth_handler import AuthMiddleware
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


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
        description="Hero365 App - Clean Architecture Implementation",
        version="2.0.0",
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
            f"{settings.API_V1_STR}/login",
            f"{settings.API_V1_STR}/register",
            f"{settings.API_V1_STR}/reset-password",
            f"{settings.API_V1_STR}/forgot-password",
        ]
    )

    # Include API router
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    return application


# Create the application instance
app = create_application()
