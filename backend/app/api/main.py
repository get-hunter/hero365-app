from fastapi import APIRouter

from app.api.routes import auth, businesses, items, login, private, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)  # Supabase auth routes
api_router.include_router(login.router)  # Legacy auth routes
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
