"""
Business Context Manager for Hero365 LiveKit Agents
Provides comprehensive business context loading and management for voice agents
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class ContextPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class BusinessContext:
    """Complete business context for the voice agent"""
    business_id: str
    business_name: str
    business_type: str
    owner_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    current_time: datetime = None
    timezone: str = "UTC"
    
    def __post_init__(self):
        if self.current_time is None:
            self.current_time = datetime.now()

@dataclass
class UserContext:
    """User-specific context for the voice agent"""
    user_id: str
    name: str
    email: str
    role: str
    permissions: List[str]
    last_active: datetime
    preferences: Dict[str, Any]
    recent_actions: List[Dict[str, Any]]

@dataclass
class RecentContact:
    """Recent contact information"""
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    contact_type: str
    last_interaction: datetime
    recent_jobs: List[str]
    recent_estimates: List[str]
    priority: ContextPriority = ContextPriority.MEDIUM

@dataclass
class RecentJob:
    """Recent job information"""
    id: str
    title: str
    contact_id: str
    contact_name: str
    status: str
    scheduled_date: Optional[datetime]
    estimated_duration: Optional[int]
    priority: str
    description: Optional[str]
    location: Optional[str]

@dataclass
class RecentEstimate:
    """Recent estimate information"""
    id: str
    title: str
    contact_id: str
    contact_name: str
    status: str
    total_amount: Optional[float]
    created_date: datetime
    valid_until: Optional[datetime]
    line_items_count: int

@dataclass
class RecentPayment:
    """Recent payment information"""
    id: str
    invoice_id: str
    amount: float
    status: str
    payment_date: datetime
    payment_method: str
    contact_name: str

@dataclass
class BusinessSummary:
    """Business summary for quick context"""
    total_contacts: int
    active_jobs: int
    pending_estimates: int
    overdue_invoices: int
    revenue_this_month: float
    jobs_this_week: int
    upcoming_appointments: int

@dataclass
class ContextualSuggestions:
    """Contextual suggestions based on current business state"""
    quick_actions: List[str]
    follow_ups: List[str]
    urgent_items: List[str]
    opportunities: List[str]

class BusinessContextManager:
    """Manages comprehensive business context for voice agents"""
    
    def __init__(self):
        self.business_context: Optional[BusinessContext] = None
        self.user_context: Optional[UserContext] = None
        self.recent_contacts: List[RecentContact] = []
        self.recent_jobs: List[RecentJob] = []
        self.recent_estimates: List[RecentEstimate] = []
        self.recent_payments: List[RecentPayment] = []
        self.business_summary: Optional[BusinessSummary] = None
        self.contextual_suggestions: Optional[ContextualSuggestions] = None
        self.container = None
        self.last_refresh: Optional[datetime] = None
        self.refresh_interval_minutes = 15
        
    async def initialize(self, user_id: str, business_id: str, container=None):
        """Initialize business context for the voice agent"""
        try:
            logger.info(f"🏢 Initializing business context for user {user_id}, business {business_id}")
            
            # Store container for data access
            self.container = container or await self._get_container()
            
            # Load all context components
            await self._load_business_context(business_id)
            await self._load_user_context(user_id)
            await self._load_recent_contacts(business_id)
            await self._load_recent_jobs(business_id)
            await self._load_recent_estimates(business_id)
            await self._load_recent_payments(business_id)
            await self._load_business_summary(business_id)
            await self._generate_contextual_suggestions()
            
            self.last_refresh = datetime.now()
            logger.info(f"✅ Business context initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing business context: {e}")
            raise
    
    async def _get_container(self):
        """Get dependency injection container"""
        try:
            from ..infrastructure.config.dependency_injection import get_container
            return get_container()
        except ImportError:
            logger.warning("⚠️ Could not import dependency injection container")
            return None
    
    async def _load_business_context(self, business_id: str):
        """Load business information"""
        try:
            if not self.container:
                logger.warning("⚠️ No container available for business context loading")
                return
            
            # Get business repository
            business_repo = self.container.get_business_repository()
            business = await business_repo.get_by_id(business_id)
            
            if business:
                self.business_context = BusinessContext(
                    business_id=business.id,
                    business_name=business.name,
                    business_type=business.business_type or "Service",
                    owner_name=business.owner_name or "Owner",
                    phone=business.phone,
                    email=business.email,
                    address=business.address.full_address if business.address else None,
                    current_time=datetime.now(),
                    timezone=business.timezone or "UTC"
                )
                logger.info(f"📋 Loaded business context: {business.name}")
            else:
                logger.warning(f"⚠️ Business {business_id} not found")
                
        except Exception as e:
            logger.error(f"❌ Error loading business context: {e}")
    
    async def _load_user_context(self, user_id: str):
        """Load user information and preferences"""
        try:
            if not self.container:
                return
                
            # Get user repository
            user_repo = self.container.get_user_repository()
            user = await user_repo.get_by_id(user_id)
            
            if user:
                self.user_context = UserContext(
                    user_id=user.id,
                    name=user.full_name or user.email,
                    email=user.email,
                    role=user.role or "user",
                    permissions=user.permissions or [],
                    last_active=datetime.now(),
                    preferences=user.preferences or {},
                    recent_actions=[]
                )
                logger.info(f"👤 Loaded user context: {user.email}")
            else:
                logger.warning(f"⚠️ User {user_id} not found")
                
        except Exception as e:
            logger.error(f"❌ Error loading user context: {e}")
    
    async def _load_recent_contacts(self, business_id: str, limit: int = 20):
        """Load recent contacts with interaction history"""
        try:
            if not self.container:
                return
                
            # Get contact repository
            contact_repo = self.container.get_contact_repository()
            contacts = await contact_repo.get_recent_by_business(business_id, limit)
            
            self.recent_contacts = []
            for contact in contacts:
                # Get recent interactions
                recent_jobs = await self._get_recent_jobs_for_contact(contact.id)
                recent_estimates = await self._get_recent_estimates_for_contact(contact.id)
                
                # Determine priority based on recent activity
                priority = self._calculate_contact_priority(contact, recent_jobs, recent_estimates)
                
                self.recent_contacts.append(RecentContact(
                    id=contact.id,
                    name=contact.full_name,
                    phone=contact.phone,
                    email=contact.email,
                    contact_type=contact.contact_type.value if contact.contact_type else "customer",
                    last_interaction=contact.updated_at or contact.created_at,
                    recent_jobs=[job.id for job in recent_jobs],
                    recent_estimates=[est.id for est in recent_estimates],
                    priority=priority
                ))
            
            logger.info(f"📞 Loaded {len(self.recent_contacts)} recent contacts")
            
        except Exception as e:
            logger.error(f"❌ Error loading recent contacts: {e}")
    
    async def _load_recent_jobs(self, business_id: str, limit: int = 15):
        """Load recent jobs"""
        try:
            if not self.container:
                return
                
            # Get job repository
            job_repo = self.container.get_job_repository()
            jobs = await job_repo.get_recent_by_business(business_id, limit)
            
            self.recent_jobs = []
            for job in jobs:
                # Get contact name
                contact_name = await self._get_contact_name(job.contact_id)
                
                self.recent_jobs.append(RecentJob(
                    id=job.id,
                    title=job.title,
                    contact_id=job.contact_id,
                    contact_name=contact_name,
                    status=job.status.value if job.status else "pending",
                    scheduled_date=job.scheduled_date,
                    estimated_duration=job.estimated_duration,
                    priority=job.priority.value if job.priority else "medium",
                    description=job.description,
                    location=job.location
                ))
            
            logger.info(f"🔧 Loaded {len(self.recent_jobs)} recent jobs")
            
        except Exception as e:
            logger.error(f"❌ Error loading recent jobs: {e}")
    
    async def _load_recent_estimates(self, business_id: str, limit: int = 15):
        """Load recent estimates"""
        try:
            if not self.container:
                return
                
            # Get estimate repository
            estimate_repo = self.container.get_estimate_repository()
            estimates = await estimate_repo.get_recent_by_business(business_id, limit)
            
            self.recent_estimates = []
            for estimate in estimates:
                # Get contact name
                contact_name = await self._get_contact_name(estimate.contact_id)
                
                self.recent_estimates.append(RecentEstimate(
                    id=estimate.id,
                    title=estimate.title,
                    contact_id=estimate.contact_id,
                    contact_name=contact_name,
                    status=estimate.status.value if estimate.status else "draft",
                    total_amount=estimate.total_amount,
                    created_date=estimate.created_at,
                    valid_until=estimate.valid_until_date,
                    line_items_count=len(estimate.line_items) if estimate.line_items else 0
                ))
            
            logger.info(f"📊 Loaded {len(self.recent_estimates)} recent estimates")
            
        except Exception as e:
            logger.error(f"❌ Error loading recent estimates: {e}")
    
    async def _load_recent_payments(self, business_id: str, limit: int = 10):
        """Load recent payments"""
        try:
            if not self.container:
                return
                
            # Get payment repository (if exists)
            # This would need to be implemented in your payment system
            self.recent_payments = []
            logger.info(f"💳 Payment history loading not implemented yet")
            
        except Exception as e:
            logger.error(f"❌ Error loading recent payments: {e}")
    
    async def _load_business_summary(self, business_id: str):
        """Load business summary statistics"""
        try:
            if not self.container:
                return
                
            # Calculate business metrics
            total_contacts = len(self.recent_contacts)
            active_jobs = len([job for job in self.recent_jobs if job.status in ["in_progress", "scheduled"]])
            pending_estimates = len([est for est in self.recent_estimates if est.status == "draft"])
            
            # Calculate this week's metrics
            week_start = datetime.now() - timedelta(days=7)
            jobs_this_week = len([job for job in self.recent_jobs if job.scheduled_date and job.scheduled_date >= week_start])
            
            self.business_summary = BusinessSummary(
                total_contacts=total_contacts,
                active_jobs=active_jobs,
                pending_estimates=pending_estimates,
                overdue_invoices=0,  # Would need invoice system
                revenue_this_month=0.0,  # Would need payment system
                jobs_this_week=jobs_this_week,
                upcoming_appointments=active_jobs
            )
            
            logger.info(f"📈 Generated business summary: {active_jobs} active jobs, {pending_estimates} pending estimates")
            
        except Exception as e:
            logger.error(f"❌ Error loading business summary: {e}")
    
    async def _generate_contextual_suggestions(self):
        """Generate contextual suggestions based on current business state"""
        try:
            quick_actions = []
            follow_ups = []
            urgent_items = []
            opportunities = []
            
            # Analyze recent activity for suggestions
            if self.recent_jobs:
                # Jobs without scheduled dates
                unscheduled_jobs = [job for job in self.recent_jobs if not job.scheduled_date]
                if unscheduled_jobs:
                    quick_actions.append(f"Schedule {len(unscheduled_jobs)} unscheduled jobs")
                
                # High priority jobs
                urgent_jobs = [job for job in self.recent_jobs if job.priority == "high"]
                if urgent_jobs:
                    urgent_items.extend([f"High priority: {job.title}" for job in urgent_jobs[:3]])
            
            # Analyze estimates for opportunities
            if self.recent_estimates:
                draft_estimates = [est for est in self.recent_estimates if est.status == "draft"]
                if draft_estimates:
                    opportunities.append(f"Send {len(draft_estimates)} pending estimates to customers")
            
            # Analyze contacts for follow-ups
            if self.recent_contacts:
                high_priority_contacts = [c for c in self.recent_contacts if c.priority == ContextPriority.HIGH]
                if high_priority_contacts:
                    follow_ups.extend([f"Follow up with {contact.name}" for contact in high_priority_contacts[:3]])
            
            self.contextual_suggestions = ContextualSuggestions(
                quick_actions=quick_actions,
                follow_ups=follow_ups,
                urgent_items=urgent_items,
                opportunities=opportunities
            )
            
            logger.info(f"💡 Generated {len(quick_actions)} quick actions, {len(urgent_items)} urgent items")
            
        except Exception as e:
            logger.error(f"❌ Error generating contextual suggestions: {e}")
    
    # Helper methods
    
    async def _get_recent_jobs_for_contact(self, contact_id: str) -> List[Any]:
        """Get recent jobs for a specific contact"""
        try:
            if not self.container:
                return []
            job_repo = self.container.get_job_repository()
            return await job_repo.get_by_contact(contact_id, limit=5)
        except Exception as e:
            logger.error(f"❌ Error getting recent jobs for contact: {e}")
            return []
    
    async def _get_recent_estimates_for_contact(self, contact_id: str) -> List[Any]:
        """Get recent estimates for a specific contact"""
        try:
            if not self.container:
                return []
            estimate_repo = self.container.get_estimate_repository()
            return await estimate_repo.get_by_contact(contact_id, limit=5)
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
            return contact.full_name if contact else "Unknown Contact"
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
            if contact.updated_at and contact.updated_at > datetime.now() - timedelta(days=30):
                return ContextPriority.MEDIUM
            
            return ContextPriority.LOW
            
        except Exception as e:
            logger.error(f"❌ Error calculating contact priority: {e}")
            return ContextPriority.LOW
    
    # Context access methods
    
    def get_business_context(self) -> Optional[BusinessContext]:
        """Get current business context"""
        return self.business_context
    
    def get_user_context(self) -> Optional[UserContext]:
        """Get current user context"""
        return self.user_context
    
    def get_recent_contacts(self, limit: int = 10) -> List[RecentContact]:
        """Get recent contacts with optional limit"""
        return self.recent_contacts[:limit]
    
    def get_recent_jobs(self, limit: int = 10) -> List[RecentJob]:
        """Get recent jobs with optional limit"""
        return self.recent_jobs[:limit]
    
    def get_recent_estimates(self, limit: int = 10) -> List[RecentEstimate]:
        """Get recent estimates with optional limit"""
        return self.recent_estimates[:limit]
    
    def get_business_summary(self) -> Optional[BusinessSummary]:
        """Get business summary"""
        return self.business_summary
    
    def get_contextual_suggestions(self) -> Optional[ContextualSuggestions]:
        """Get contextual suggestions"""
        return self.contextual_suggestions
    
    def find_contact_by_name(self, name: str) -> Optional[RecentContact]:
        """Find contact by name (fuzzy search)"""
        name_lower = name.lower()
        for contact in self.recent_contacts:
            if name_lower in contact.name.lower():
                return contact
        return None
    
    def find_job_by_title(self, title: str) -> Optional[RecentJob]:
        """Find job by title (fuzzy search)"""
        title_lower = title.lower()
        for job in self.recent_jobs:
            if title_lower in job.title.lower():
                return job
        return None
    
    def find_estimate_by_title(self, title: str) -> Optional[RecentEstimate]:
        """Find estimate by title (fuzzy search)"""
        title_lower = title.lower()
        for estimate in self.recent_estimates:
            if title_lower in estimate.title.lower():
                return estimate
        return None
    
    async def refresh_context(self):
        """Refresh business context if needed"""
        try:
            if not self.last_refresh or datetime.now() - self.last_refresh > timedelta(minutes=self.refresh_interval_minutes):
                logger.info("🔄 Refreshing business context")
                if self.business_context and self.user_context:
                    await self.initialize(self.user_context.user_id, self.business_context.business_id)
        except Exception as e:
            logger.error(f"❌ Error refreshing context: {e}")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context for logging/debugging"""
        return {
            "business_name": self.business_context.business_name if self.business_context else None,
            "user_name": self.user_context.name if self.user_context else None,
            "recent_contacts_count": len(self.recent_contacts),
            "recent_jobs_count": len(self.recent_jobs),
            "recent_estimates_count": len(self.recent_estimates),
            "active_jobs": self.business_summary.active_jobs if self.business_summary else 0,
            "pending_estimates": self.business_summary.pending_estimates if self.business_summary else 0,
            "last_refresh": self.last_refresh.isoformat() if self.last_refresh else None
        }

# Global instance
_business_context_manager = None

async def get_business_context_manager() -> BusinessContextManager:
    """Get or create business context manager singleton"""
    global _business_context_manager
    if _business_context_manager is None:
        _business_context_manager = BusinessContextManager()
    return _business_context_manager 