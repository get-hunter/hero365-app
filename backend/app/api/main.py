from fastapi import APIRouter

from app.api.routes import auth, businesses, users, utils, business_context, middleware_health, contacts, jobs, projects, activities, scheduling, estimates, invoices, templates, products, suppliers, purchase_orders, mobile_voice
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(utils.router)
api_router.include_router(users.router, tags=["users"], include_in_schema=True)
api_router.include_router(businesses.router, tags=["businesses"], include_in_schema=True)
api_router.include_router(contacts.router, tags=["contacts"], include_in_schema=True)
api_router.include_router(jobs.router, tags=["jobs"], include_in_schema=True)
api_router.include_router(projects.router, tags=["projects"], include_in_schema=True)
api_router.include_router(activities.router, tags=["activities"], include_in_schema=True)
api_router.include_router(scheduling.router, tags=["Intelligent Scheduling"], include_in_schema=True)
api_router.include_router(estimates.router, tags=["estimates"], include_in_schema=True)
api_router.include_router(invoices.router, tags=["invoices"], include_in_schema=True)
api_router.include_router(templates.router, tags=["templates"], include_in_schema=True)
api_router.include_router(products.router, tags=["products"], include_in_schema=True)
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"], include_in_schema=True)
api_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["purchase-orders"], include_in_schema=True)
api_router.include_router(business_context.router, tags=["Business Context"], include_in_schema=True)
api_router.include_router(middleware_health.router, tags=["Middleware Health"], include_in_schema=True)
api_router.include_router(mobile_voice.router, tags=["Mobile Voice Integration"], include_in_schema=True)
