"""
Context Loader for Hero365 LiveKit Agents
Handles loading of business context data from various sources
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from datetime import timezone

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
                    business_id=str(business.id),  # Convert UUID to string
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
                recent_jobs = await self._get_recent_jobs_for_contact(str(contact.id))
                recent_estimates = await self._get_recent_estimates_for_contact(str(contact.id))
                
                # Determine priority based on recent activity
                priority = self._calculate_contact_priority(contact, recent_jobs, recent_estimates)
                
                recent_contacts.append(RecentContact(
                    id=str(contact.id),  # Convert UUID to string
                    name=contact.get_display_name(),
                    phone=contact.phone,
                    email=contact.email,
                    contact_type=contact.contact_type.value if contact.contact_type else "customer",
                    last_interaction=contact.last_modified or contact.created_date,
                    recent_jobs=[str(job.id) for job in recent_jobs],  # Convert UUIDs to strings
                    recent_estimates=[str(est.id) for est in recent_estimates],  # Convert UUIDs to strings
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
                contact_name = await self._get_contact_name(str(job.contact_id))
                
                # Convert domain status to model status
                status = self._convert_job_status(job.status)
                priority = self._convert_job_priority(job.priority)
                
                recent_jobs.append(RecentJob(
                    id=str(job.id),  # Convert UUID to string
                    title=job.title,
                    contact_id=str(job.contact_id),  # Convert UUID to string
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
    
    async def load_recent_estimates(self, business_id: str, limit: int = 10) -> List[RecentEstimate]:
        """Load recent estimates"""
        try:
            logger.info(f"📊 Loading recent estimates for business_id: {business_id} (limit: {limit})")
            
            if not self.container:
                logger.warning("⚠️ No container available for recent estimates loading")
                return []
            
            # Get estimate repository
            estimate_repo = self.container.get_estimate_repository()
            logger.info(f"🔍 Debug - Got estimate repository: {type(estimate_repo).__name__ if estimate_repo else None}")
            
            # Convert string business_id to UUID
            import uuid
            try:
                business_uuid = uuid.UUID(business_id)
                logger.info(f"🔍 Debug - Converted business_id to UUID: {business_uuid}")
            except ValueError as e:
                logger.error(f"❌ Invalid business_id format: {business_id} - {e}")
                return []
            
            # Get recent estimates from repository with debugging
            logger.info(f"🔍 Debug - Calling estimate_repo.get_recent_by_business with UUID: {business_uuid}")
            
            recent_estimates_entities = await estimate_repo.get_recent_by_business(business_uuid, limit=limit)
            logger.info(f"🔍 Debug - Repository returned {len(recent_estimates_entities) if recent_estimates_entities else 0} estimate entities")
            
            if recent_estimates_entities:
                logger.info(f"✅ Found {len(recent_estimates_entities)} estimates from repository")
                for i, est in enumerate(recent_estimates_entities):
                    logger.info(f"  Estimate {i+1}: {est.title} - Status: {est.status.value if hasattr(est, 'status') else 'No status'} - Created: {est.created_date if hasattr(est, 'created_date') else 'No date'}")
            else:
                logger.warning(f"⚠️ No estimates returned from repository for business_id: {business_uuid}")
                
                # Additional debugging - try to get ALL estimates to see if there are any at all
                try:
                    logger.info("🔍 Debug - Checking for ANY estimates in the database...")
                    all_estimates = await estimate_repo.get_by_business_id(business_uuid, limit=100)
                    logger.info(f"🔍 Debug - get_by_business_id returned {len(all_estimates) if all_estimates else 0} estimates")
                    
                    if all_estimates:
                        logger.info("🔍 Debug - Some estimates found with get_by_business_id, showing first few:")
                        for i, est in enumerate(all_estimates[:3]):
                            logger.info(f"    Estimate {i+1}: {est.title} - Status: {est.status.value if hasattr(est, 'status') else 'No status'}")
                            logger.info(f"                    Created: {est.created_date if hasattr(est, 'created_date') else 'No date'}")
                            logger.info(f"                    Business ID: {est.business_id if hasattr(est, 'business_id') else 'No business_id'}")
                    else:
                        logger.warning("🔍 Debug - NO estimates found with get_by_business_id either!")
                        logger.warning(f"🔍 Debug - This suggests the business_id {business_uuid} doesn't match any estimates in the database")
                
                except Exception as debug_e:
                    logger.error(f"🔍 Debug query failed: {debug_e}")
                
                return []
            
            # Convert entities to RecentEstimate models
            recent_estimates = []
            for estimate_entity in recent_estimates_entities:
                try:
                    # Resolve contact name
                    contact_name = "Unknown Contact"
                    if hasattr(estimate_entity, 'client_name') and estimate_entity.client_name:
                        contact_name = estimate_entity.client_name
                    elif hasattr(estimate_entity, 'contact_id') and estimate_entity.contact_id:
                        # Try to get contact name from repository
                        try:
                            contact_repo = self.container.get_contact_repository()
                            if contact_repo:
                                contact = await contact_repo.get_by_id(estimate_entity.contact_id)
                                if contact:
                                    contact_name = contact.get_display_name()
                        except Exception:
                            pass  # Fallback to Unknown Contact
                    
                    # Create RecentEstimate model from entity with correct field mapping
                    recent_estimate = RecentEstimate(
                        id=str(estimate_entity.id),  # Correct field name
                        title=estimate_entity.title,
                        contact_id=str(estimate_entity.contact_id) if estimate_entity.contact_id else "",
                        contact_name=contact_name,
                        status=self._convert_estimate_status(estimate_entity.status),  # Use conversion method
                        total_amount=float(estimate_entity.get_total_amount()) if hasattr(estimate_entity, 'get_total_amount') else None,  # Correct field name
                        created_date=estimate_entity.created_date if hasattr(estimate_entity, 'created_date') else datetime.now(timezone.utc),
                        valid_until=estimate_entity.valid_until_date if hasattr(estimate_entity, 'valid_until_date') else None,
                        line_items_count=len(estimate_entity.line_items) if hasattr(estimate_entity, 'line_items') and estimate_entity.line_items else 0
                    )
                    recent_estimates.append(recent_estimate)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error converting estimate entity to RecentEstimate: {e}")
                    logger.warning(f"    Estimate entity: {estimate_entity}")
            
            logger.info(f"📊 Loaded {len(recent_estimates)} recent estimates")
            return recent_estimates
            
        except Exception as e:
            logger.error(f"❌ Error loading recent estimates: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
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
            # Convert string to UUID if needed
            if isinstance(contact_id, str):
                import uuid
                contact_uuid = uuid.UUID(contact_id)
            else:
                contact_uuid = contact_id
            return await job_repo.get_by_contact_id(contact_uuid, limit=5)
        except Exception as e:
            logger.error(f"❌ Error getting recent jobs for contact: {e}")
            return []
    
    async def _get_recent_estimates_for_contact(self, contact_id: str) -> List[Any]:
        """Get recent estimates for a specific contact"""
        try:
            if not self.container:
                return []
            estimate_repo = self.container.get_estimate_repository()
            # Convert string to UUID if needed
            if isinstance(contact_id, str):
                import uuid
                contact_uuid = uuid.UUID(contact_id)
            else:
                contact_uuid = contact_id
            return await estimate_repo.get_by_contact_id(contact_uuid, limit=5)
        except Exception as e:
            logger.error(f"❌ Error getting recent estimates for contact: {e}")
            return []
    
    async def _get_contact_name(self, contact_id: str) -> str:
        """Get contact name by ID"""
        try:
            if not self.container:
                return "Unknown Contact"
            contact_repo = self.container.get_contact_repository()
            # Convert string to UUID if needed
            if isinstance(contact_id, str):
                import uuid
                contact_uuid = uuid.UUID(contact_id)
            else:
                contact_uuid = contact_id
            contact = await contact_repo.get_by_id(contact_uuid)
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
            "converted": EstimateStatus.CONVERTED,
            "cancelled": EstimateStatus.CANCELLED,
        }
        
        return status_map.get(domain_status.value if hasattr(domain_status, 'value') else str(domain_status), EstimateStatus.DRAFT) 