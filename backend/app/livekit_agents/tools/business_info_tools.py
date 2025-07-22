"""
Business Information Tools for Hero365 LiveKit Agents
"""

import logging
import uuid
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BusinessInfoTools:
    """Business information tools for the Hero365 agent"""
    
    def __init__(self, business_context: Dict[str, Any], business_context_manager: Optional[Any] = None):
        self.business_context = business_context
        self.business_context_manager = business_context_manager
        self._container = None
        
    def _get_container(self):
        """Get dependency injection container"""
        if not self._container:
            try:
                from app.infrastructure.config.dependency_injection import get_container
                self._container = get_container()
                logger.info("✅ Retrieved container for BusinessInfoTools")
            except Exception as e:
                logger.error(f"❌ Error getting container: {e}")
                return None
        return self._container
    
    def _get_business_id(self) -> Optional[uuid.UUID]:
        """Get business ID from context"""
        business_id = self.business_context.get('business_id')
        if business_id:
            if isinstance(business_id, str):
                return uuid.UUID(business_id)
            return business_id
        return None

    async def get_business_info(self) -> str:
        """Get current business information including name, type, and contact details"""
        logger.info("🏢 get_business_info tool called")
        
        if not self.business_context:
            return "Business information is not available at the moment."
            
        info = []
        if self.business_context.get('business_name'):
            info.append(f"Business Name: {self.business_context['business_name']}")
        if self.business_context.get('business_type'):
            info.append(f"Business Type: {self.business_context['business_type']}")
        if self.business_context.get('phone'):
            info.append(f"Phone: {self.business_context['phone']}")
        if self.business_context.get('email'):
            info.append(f"Email: {self.business_context['email']}")
        if self.business_context.get('address'):
            info.append(f"Address: {self.business_context['address']}")
            
        return ". ".join(info) if info else "Business information is not available."

    async def get_user_info(self) -> str:
        """Get current user information"""
        logger.info("👤 get_user_info tool called")
        
        if not self.business_context:
            return "User information is not available at the moment."
            
        info = []
        if self.business_context.get('user_name'):
            info.append(f"Name: {self.business_context['user_name']}")
        if self.business_context.get('user_email'):
            info.append(f"Email: {self.business_context['user_email']}")
        if self.business_context.get('user_role'):
            info.append(f"Role: {self.business_context['user_role']}")
            
        return ". ".join(info) if info else "User information is not available."

    async def get_business_status(self) -> str:
        """Get complete business status and activity overview"""
        logger.info("📊 get_business_status tool called")
        
        if not self.business_context:
            return "Business status is not available at the moment."
            
        status = []
        if self.business_context.get('business_name'):
            status.append(f"Business: {self.business_context['business_name']}")
        if self.business_context.get('business_type'):
            status.append(f"Type: {self.business_context['business_type']}")
        if self.business_context.get('active_jobs'):
            status.append(f"Active Jobs: {self.business_context['active_jobs']}")
        if self.business_context.get('pending_estimates'):
            status.append(f"Pending Estimates: {self.business_context['pending_estimates']}")
        if self.business_context.get('total_contacts'):
            status.append(f"Total Contacts: {self.business_context['total_contacts']}")
        if self.business_context.get('recent_contacts_count'):
            status.append(f"Recent Contacts: {self.business_context['recent_contacts_count']}")
        if self.business_context.get('revenue_this_month'):
            status.append(f"Revenue This Month: ${self.business_context['revenue_this_month']}")
        if self.business_context.get('jobs_this_week'):
            status.append(f"Jobs This Week: {self.business_context['jobs_this_week']}")
            
        return ". ".join(status) if status else "Business status is not available." 