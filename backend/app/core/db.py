from supabase import create_client, Client

from app.core.config import settings
# Removed monolithic supabase_service import - now using clean architecture components


def get_supabase_client() -> Client:
    """Get Supabase client."""
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_ANON_KEY
    )


def init_db() -> None:
    """Initialize database with first superuser if needed."""
    try:
        # Check if first superuser exists via Supabase service
        # This now uses Supabase Auth instead of database tables
        if settings.FIRST_SUPERUSER and settings.FIRST_SUPERUSER_PASSWORD:
            # The superuser initialization is now handled by Supabase Auth
            # You can create the first superuser through Supabase Dashboard
            # or use the Supabase Admin API
            pass
    except Exception as e:
        print(f"Database initialization warning: {e}")
        # Non-critical error during initialization
