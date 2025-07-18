"""
Context Loader for Hero365 LiveKit Agents
Handles loading of business context data from various sources
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from ..models import (
    BusinessContext, UserContext, RecentContact, RecentJob, 
    RecentEstimate, RecentPayment, ContextPriority, JobStatus, EstimateStatus
)

logger = logging.getLogger(__name__)


class ContextLoader:
    """
    Handles loading of business context data from repositories
    Separated from the manager for better single responsibility
    """
    
    def __init__(self, container=None):
        self.container = container
        
    async def load_business_context(self, business_id: str) -> Optional[BusinessContext]:
        """Load business information"""
        try:
            if not self.container:
                logger.warning("⚠️ No container available for business context loading")
                return None
            
            # Get business repository
            business_repo = self.container.get_business_repository()
            business = await business_repo.get_by_id(business_id)
            
            if business:
                return BusinessContext(
                    business_id=business.id,
                    business_name=business.name,
                    business_type=business.business_type.value if business.business_type else "Service",
                    owner_name="Owner",  # We only have owner_id, not owner_name
                    phone=business.phone_number,
                    email=business.business_email,
                    address=business.business_address,
                    timezone=business.timezone or "UTC",
                    # Initialize metrics - will be updated after loading all data
                    recent_contacts_count=0,
                    recent_jobs_count=0,
                    recent_estimates_count=0,
                    active_jobs=0,
                    pending_estimates=0,
                )
            else:
                logger.warning(f"⚠️ Business {business_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading business context: {e}")
            return None
    
    async def load_user_context(self, user_id: str, user_info: dict = None) -> Optional[UserContext]:
        """Load user information and preferences"""
        try:
            if not self.container:
                # Create user context from auth info if available
                if user_info:
                    user_email = user_info.get("email", "user@example.com")
                    user_metadata = user_info.get("user_metadata", {})
                    full_name = user_metadata.get("full_name") or user_metadata.get("name") or user_email.split("@")[0]
                    
                    return UserContext(
                        user_id=user_id,
                        name=full_name,
                        email=user_email,
                        role="user",
                        permissions=[],
                        preferences={},
                        recent_actions=[]
                    )
                else:
                    # Create a minimal user context
                    return UserContext(
                        user_id=user_id,
                        name="User",
                        email="user@example.com",
                        role="user",
                        permissions=[],
                        preferences={},
                        recent_actions=[]
                    )
                    
            # Get user repository (returns None for this project - users managed via Supabase Auth)
            user_repo = self.container.get_user_repository()
            if user_repo is None:
                # Use actual user info if provided, otherwise create minimal context
                if user_info:
                    user_email = user_info.get("email", "user@example.com")
                    user_metadata = user_info.get("user_metadata", {})
                    full_name = user_metadata.get("full_name") or user_metadata.get("name") or user_email.split("@")[0]
                    
                    return UserContext(
                        user_id=user_id,
                        name=full_name,
                        email=user_email,
                        role="user",
                        permissions=[],
                        preferences={},
                        recent_actions=[]
                    )
                else:
                    return UserContext(
                        user_id=user_id,
                        name="User",
                        email="user@example.com",
                        role="user",
                        permissions=[],
                        preferences={},
                        recent_actions=[]
                    )
            
            user = await user_repo.get_by_id(user_id)
            
            if user:
                return UserContext(
                    user_id=user.id,
                    name=user.full_name or user.email,
                    email=user.email,
                    role=user.role or "user",
                    permissions=user.permissions or [],
                    preferences=user.preferences or {},
                    recent_actions=[]
                )
            else:
                logger.warning(f"⚠️ User {user_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading user context: {e}")
            return None
    
    async def load_recent_contacts(self, business_id: str, limit: int = 20) -> List[RecentContact]:
        """Load recent contacts with interaction history"""
        try:
            if not self.container:
                return []
                
            # Get contact repository
            contact_repo = self.container.get_contact_repository()
            contacts = await contact_repo.get_recent_by_business(business_id, limit)
            
            recent_contacts = []
            for contact in contacts:
                # Get recent interactions
                recent_jobs = await self._get_recent_jobs_for_contact(contact.id)
                recent_estimates = await self._get_recent_estimates_for_contact(contact.id)
                
                # Determine priority based on recent activity
                priority = self._calculate_contact_priority(contact, recent_jobs, recent_estimates)
                
                recent_contacts.append(RecentContact(
                    id=contact.id,
                    name=contact.get_display_name(),
                    phone=contact.phone,
                    email=contact.email,
                    contact_type=contact.contact_type.value if contact.contact_type else "customer",
                    last_interaction=contact.last_modified or contact.created_date,
                    recent_jobs=[job.id for job in recent_jobs],
                    recent_estimates=[est.id for est in recent_estimates],
                    priority=priority
                ))
            
            logger.info(f"📞 Loaded {len(recent_contacts)} recent contacts")
            return recent_contacts
            
        except Exception as e:
            logger.error(f"❌ Error loading recent contacts: {e}")
            return []
    
    async def load_recent_jobs(self, business_id: str, limit: int = 15) -> List[RecentJob]:
        """Load recent jobs"""
        try:
            if not self.container:
                return []
                
            # Get job repository
            job_repo = self.container.get_job_repository()
            jobs = await job_repo.get_recent_by_business(business_id, limit)
            
            recent_jobs = []
            for job in jobs:
                # Get contact name
                contact_name = await self._get_contact_name(job.contact_id)
                
                # Convert domain status to model status
                status = self._convert_job_status(job.status)
                priority = self._convert_job_priority(job.priority)
                
                recent_jobs.append(RecentJob(
                    id=job.id,
                    title=job.title,
                    contact_id=job.contact_id,
                    contact_name=contact_name,
                    status=status,
                    scheduled_date=job.scheduled_date,
                    estimated_duration=job.estimated_duration,
                    priority=priority,
                    description=job.description,
                    location=job.location
                ))
            
            logger.info(f"🔧 Loaded {len(recent_jobs)} recent jobs")
            return recent_jobs
            
        except Exception as e:
            logger.error(f"❌ Error loading recent jobs: {e}")
            return []
    
    async def load_recent_estimates(self, business_id: str, limit: int = 15) -> List[RecentEstimate]:
        """Load recent estimates"""
        try:
            if not self.container:
                return []
                
            # Get estimate repository
            estimate_repo = self.container.get_estimate_repository()
            estimates = await estimate_repo.get_recent_by_business(business_id, limit)
            
            recent_estimates = []
            for estimate in estimates:
                # Get contact name
                contact_name = await self._get_contact_name(estimate.contact_id)
                
                # Convert domain status to model status
                status = self._convert_estimate_status(estimate.status)
                
                recent_estimates.append(RecentEstimate(
                    id=estimate.id,
                    title=estimate.title,
                    contact_id=estimate.contact_id,
                    contact_name=contact_name,
                    status=status,
                    total_amount=estimate.total_amount,
                    created_date=estimate.created_at,
                    valid_until=estimate.valid_until_date,
                    line_items_count=len(estimate.line_items) if estimate.line_items else 0
                ))
            
            logger.info(f"📊 Loaded {len(recent_estimates)} recent estimates")
            return recent_estimates
            
        except Exception as e:
            logger.error(f"❌ Error loading recent estimates: {e}")
            return []
    
    async def load_recent_payments(self, business_id: str, limit: int = 10) -> List[RecentPayment]:
        """Load recent payments"""
        try:
            if not self.container:
                return []
                
            # Get payment repository (if exists)
            # This would need to be implemented in your payment system
            logger.info(f"💳 Payment history loading not implemented yet")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error loading recent payments: {e}")
            return []
    
    # Helper methods
    
    async def _get_recent_jobs_for_contact(self, contact_id: str) -> List[Any]:
        """Get recent jobs for a specific contact"""
        try:
            if not self.container:
                return []
            job_repo = self.container.get_job_repository()
            return await job_repo.get_by_contact_id(contact_id, limit=5)
        except Exception as e:
            logger.error(f"❌ Error getting recent jobs for contact: {e}")
            return []
    
    async def _get_recent_estimates_for_contact(self, contact_id: str) -> List[Any]:
        """Get recent estimates for a specific contact"""
        try:
            if not self.container:
                return []
            estimate_repo = self.container.get_estimate_repository()
            return await estimate_repo.get_by_contact_id(contact_id, limit=5)
        except Exception as e:
            logger.error(f"❌ Error getting recent estimates for contact: {e}")
            return []
    
    async def _get_contact_name(self, contact_id: str) -> str:
        """Get contact name by ID"""
        try:
            if not self.container:
                return "Unknown Contact"
            contact_repo = self.container.get_contact_repository()
            contact = await contact_repo.get_by_id(contact_id)
            return contact.get_display_name() if contact else "Unknown Contact"
        except Exception as e:
            logger.error(f"❌ Error getting contact name: {e}")
            return "Unknown Contact"
    
    def _calculate_contact_priority(self, contact, recent_jobs, recent_estimates) -> ContextPriority:
        """Calculate contact priority based on recent activity"""
        try:
            # High priority if recent activity
            if recent_jobs or recent_estimates:
                return ContextPriority.HIGH
            
            # Medium priority if contacted recently
            if contact.last_modified and contact.last_modified > datetime.now() - timedelta(days=30):
                return ContextPriority.MEDIUM
            
            return ContextPriority.LOW
            
        except Exception as e:
            logger.error(f"❌ Error calculating contact priority: {e}")
            return ContextPriority.LOW
    
    def _convert_job_status(self, domain_status) -> JobStatus:
        """Convert domain job status to model status"""
        if not domain_status:
            return JobStatus.PENDING
        
        status_map = {
            "pending": JobStatus.PENDING,
            "scheduled": JobStatus.SCHEDULED,
            "in_progress": JobStatus.IN_PROGRESS,
            "completed": JobStatus.COMPLETED,
            "cancelled": JobStatus.CANCELLED,
        }
        
        return status_map.get(domain_status.value if hasattr(domain_status, 'value') else str(domain_status), JobStatus.PENDING)
    
    def _convert_job_priority(self, domain_priority):
        """Convert domain job priority to model priority"""
        if not domain_priority:
            return JobStatus.PENDING
        
        from ..models.job_models import JobPriority
        
        priority_map = {
            "low": JobPriority.LOW,
            "medium": JobPriority.MEDIUM,
            "high": JobPriority.HIGH,
            "urgent": JobPriority.URGENT,
        }
        
        return priority_map.get(domain_priority.value if hasattr(domain_priority, 'value') else str(domain_priority), JobPriority.MEDIUM)
    
    def _convert_estimate_status(self, domain_status) -> EstimateStatus:
        """Convert domain estimate status to model status"""
        if not domain_status:
            return EstimateStatus.DRAFT
        
        status_map = {
            "draft": EstimateStatus.DRAFT,
            "sent": EstimateStatus.SENT,
            "viewed": EstimateStatus.VIEWED,
            "approved": EstimateStatus.APPROVED,
            "rejected": EstimateStatus.REJECTED,
            "expired": EstimateStatus.EXPIRED,
        }
        
        return status_map.get(domain_status.value if hasattr(domain_status, 'value') else str(domain_status), EstimateStatus.DRAFT) 