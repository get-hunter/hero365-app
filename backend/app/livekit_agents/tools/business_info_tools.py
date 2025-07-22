"""
Business Information Tools for Hero365 LiveKit Agents
"""

import logging
import uuid
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BusinessInfoTools:
    """Business information tools for the Hero365 agent"""
    
    def __init__(self, session_context: Dict[str, Any], context_intelligence: Optional[Any] = None):
        self.session_context = session_context
        self.context_intelligence = context_intelligence
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
        business_id = self.session_context.get('business_id')
        if business_id:
            if isinstance(business_id, str):
                return uuid.UUID(business_id)
            return business_id
        return None

    async def get_business_info(self) -> str:
        """Get current business information including name, type, and contact details"""
        logger.info("🏢 get_business_info tool called")
        
        if not self.session_context:
            return "Business information is not available at the moment."
            
        info = []
        if self.session_context.get('business_name'):
            info.append(f"Business Name: {self.session_context['business_name']}")
        if self.session_context.get('business_type'):
            info.append(f"Business Type: {self.session_context['business_type']}")
        if self.session_context.get('phone'):
            info.append(f"Phone: {self.session_context['phone']}")
        if self.session_context.get('email'):
            info.append(f"Email: {self.session_context['email']}")
        if self.session_context.get('address'):
            info.append(f"Address: {self.session_context['address']}")
            
        return ". ".join(info) if info else "Business information is not available."

    async def get_user_info(self) -> str:
        """Get current user information"""
        logger.info("👤 get_user_info tool called")
        
        if not self.session_context:
            return "User information is not available at the moment."
            
        info = []
        if self.session_context.get('user_name'):
            info.append(f"Name: {self.session_context['user_name']}")
        if self.session_context.get('user_email'):
            info.append(f"Email: {self.session_context['user_email']}")
        if self.session_context.get('user_role'):
            info.append(f"Role: {self.session_context['user_role']}")
            
        return ". ".join(info) if info else "User information is not available."

    async def get_business_status(self) -> str:
        """Get complete business status and activity overview"""
        logger.info("📊 get_business_status tool called")
        
        if not self.session_context:
            return "Business status is not available at the moment."
            
        status = []
        if self.session_context.get('business_name'):
            status.append(f"Business: {self.session_context['business_name']}")
        if self.session_context.get('business_type'):
            status.append(f"Type: {self.session_context['business_type']}")
        if self.session_context.get('active_jobs'):
            status.append(f"Active Jobs: {self.session_context['active_jobs']}")
        if self.session_context.get('pending_estimates'):
            status.append(f"Pending Estimates: {self.session_context['pending_estimates']}")
        if self.session_context.get('total_contacts'):
            status.append(f"Total Contacts: {self.session_context['total_contacts']}")
        if self.session_context.get('recent_contacts_count'):
            status.append(f"Recent Contacts: {self.session_context['recent_contacts_count']}")
        if self.session_context.get('revenue_this_month'):
            status.append(f"Revenue This Month: ${self.session_context['revenue_this_month']}")
        if self.session_context.get('jobs_this_week'):
            status.append(f"Jobs This Week: {self.session_context['jobs_this_week']}")
            
        return ". ".join(status) if status else "Business status is not available." 