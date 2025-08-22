import sentry_sdk
import logging
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.api.main import api_router
from app.api.public.main import public_router
from app.api.middleware.middleware_manager import middleware_manager
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique IDs for API routes."""
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to provide detailed logging."""
    logger.error(f"🚨 Validation error on {request.method} {request.url.path}")
    logger.error(f"🚨 Validation error details: {exc.errors()}")
    logger.error(f"🚨 Request body: {await request.body()}")
    
    # Extract validation error details
    details = []
    for error in exc.errors():
        details.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", ""),
            "input": error.get("input", "")
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "validation_error",
                "message": "Request validation failed",
                "details": details
            }
        }
    )


def create_application() -> FastAPI:
    """Create and configure the FastAPI application with clean architecture."""
    
    logger.info(f"🚀 Creating Hero365 application in {settings.ENVIRONMENT} environment")
    
    # Initialize Sentry if configured
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        logger.info("📊 Initializing Sentry monitoring")
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

    # Create FastAPI application
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
        description="Hero365 App - the AI-native business management platform for home service businesses",
        version="2.0.0",
        redirect_slashes=False,  # Prevent automatic redirects that strip auth headers
        servers=[
            {
                "url": settings.API_BASE_URL,
                "description": f"{settings.ENVIRONMENT.title()} environment"
            }
        ] if settings.ENVIRONMENT == "production" else None
    )

    # Add custom exception handlers
    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Include public API router BEFORE applying middleware (no authentication required)
    logger.info("🌐 Including public API routes...")
    application.include_router(public_router, prefix=settings.API_V1_STR)

    # Apply all middlewares using the middleware manager
    logger.info("🔧 Applying middleware stack...")
    middleware_manager.apply_all_middlewares(application)

    # Include API router (with authentication required)
    logger.info("🛣️  Including API routes...")
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add health check endpoint (outside of API versioning for infrastructure)
    @application.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint for infrastructure monitoring."""
        return {
            "status": "healthy", 
            "environment": settings.ENVIRONMENT,
            "version": "2.0.0",
            "middleware_info": middleware_manager.get_middleware_info()
        }
    
    logger.info("✅ Hero365 application created successfully!")
    return application


# Create the application instance
app = create_application()
