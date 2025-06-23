from fastapi import APIRouter

from app.api.routes import auth, businesses, users, utils, business_context, middleware_health, contacts, jobs
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)  # Supabase auth routes
api_router.include_router(utils.router)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"], include_in_schema=True)
api_router.include_router(contacts.router, tags=["contacts"], include_in_schema=True)
api_router.include_router(jobs.router, tags=["jobs"], include_in_schema=True)
api_router.include_router(business_context.router, tags=["Business Context"], include_in_schema=True)
api_router.include_router(middleware_health.router, tags=["Middleware Health"], include_in_schema=True)



