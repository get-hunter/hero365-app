from fastapi import APIRouter

from app.api.routes import auth, businesses, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)  # Supabase auth routes
api_router.include_router(utils.router)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"], include_in_schema=True)



