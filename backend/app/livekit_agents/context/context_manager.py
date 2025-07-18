"""
Business Context Manager for Hero365 LiveKit Agents
Provides comprehensive business context management with better organization
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from ..models import (
    BusinessContext, BusinessSummary, UserContext, RecentContact,
    RecentJob, RecentEstimate, RecentPayment, ContextualSuggestions,
    ContextPriority, JobStatus, EstimateStatus
)
from .context_loader import ContextLoader

logger = logging.getLogger(__name__)


class BusinessContextManager:
    """
    Manages comprehensive business context for voice agents
    Refactored for better organization and maintainability
    """
    
    def __init__(self):
        self.business_context: Optional[BusinessContext] = None
        self.user_context: Optional[UserContext] = None
        self.recent_contacts: List[RecentContact] = []
        self.recent_jobs: List[RecentJob] = []
        self.recent_estimates: List[RecentEstimate] = []
        self.recent_payments: List[RecentPayment] = []
        self.business_summary: Optional[BusinessSummary] = None
        self.contextual_suggestions: Optional[ContextualSuggestions] = None
        
        # Internal state
        self._context_loader: Optional[ContextLoader] = None
        self._container = None
        self._last_refresh: Optional[datetime] = None
        self._refresh_interval_minutes = 15
        
    async def initialize(self, user_id: str, business_id: str, container=None, user_info: dict = None):
        """Initialize business context for the voice agent"""
        try:
            logger.info(f"🏢 Initializing business context for user {user_id}, business {business_id}")
            
            # Store container and initialize loader
            self._container = container or await self._get_container()
            self._context_loader = ContextLoader(self._container)
            
            # Load all context components
            await self._load_all_context(user_id, business_id, user_info)
            
            self._last_refresh = datetime.now()
            logger.info(f"✅ Business context initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing business context: {e}")
            raise
    
    async def _get_container(self):
        """Get dependency injection container"""
        try:
            from ...infrastructure.config.dependency_injection import get_container
            return get_container()
        except ImportError:
            logger.warning("⚠️ Could not import dependency injection container")
            return None
    
    async def _load_all_context(self, user_id: str, business_id: str, user_info: dict = None):
        """Load all context components"""
        if not self._context_loader:
            logger.warning("⚠️ Context loader not initialized")
            return
        
        # Load all components
        self.business_context = await self._context_loader.load_business_context(business_id)
        self.user_context = await self._context_loader.load_user_context(user_id, user_info)
        self.recent_contacts = await self._context_loader.load_recent_contacts(business_id)
        self.recent_jobs = await self._context_loader.load_recent_jobs(business_id)
        self.recent_estimates = await self._context_loader.load_recent_estimates(business_id)
        self.recent_payments = await self._context_loader.load_recent_payments(business_id)
        
        # Generate derived data
        self.business_summary = await self._generate_business_summary()
        self.contextual_suggestions = await self._generate_contextual_suggestions()
        
        # Update business context with calculated metrics
        await self._update_business_context_metrics()
    
    async def _update_business_context_metrics(self):
        """Update business context with calculated metrics"""
        if not self.business_context:
            return
        
        try:
            # Create updated context with new metrics
            updated_context = self.business_context.copy(update={
                'recent_contacts_count': len(self.recent_contacts),
                'recent_jobs_count': len(self.recent_jobs),
                'recent_estimates_count': len(self.recent_estimates),
                'active_jobs': len([job for job in self.recent_jobs if job.status in [JobStatus.IN_PROGRESS, JobStatus.SCHEDULED]]),
                'pending_estimates': len([est for est in self.recent_estimates if est.status == EstimateStatus.DRAFT]),
                'last_refresh': datetime.now()
            })
            
            self.business_context = updated_context
            
            logger.info(f"📊 Updated business context metrics: {self.business_context.active_jobs} active jobs, {self.business_context.pending_estimates} pending estimates")
            
        except Exception as e:
            logger.error(f"❌ Error updating business context metrics: {e}")
    
    async def _generate_business_summary(self) -> BusinessSummary:
        """Generate business summary statistics"""
        try:
            total_contacts = len(self.recent_contacts)
            active_jobs = len([job for job in self.recent_jobs if job.status in [JobStatus.IN_PROGRESS, JobStatus.SCHEDULED]])
            pending_estimates = len([est for est in self.recent_estimates if est.status == EstimateStatus.DRAFT])
            
            # Calculate this week's metrics
            week_start = datetime.now() - timedelta(days=7)
            jobs_this_week = len([job for job in self.recent_jobs if job.scheduled_date and job.scheduled_date >= week_start])
            
            return BusinessSummary(
                total_contacts=total_contacts,
                active_jobs=active_jobs,
                pending_estimates=pending_estimates,
                overdue_invoices=0,  # Would need invoice system
                revenue_this_month=0.0,  # Would need payment system
                jobs_this_week=jobs_this_week,
                upcoming_appointments=active_jobs
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating business summary: {e}")
            return BusinessSummary(
                total_contacts=0,
                active_jobs=0,
                pending_estimates=0,
                overdue_invoices=0,
                revenue_this_month=0.0,
                jobs_this_week=0,
                upcoming_appointments=0
            )
    
    async def _generate_contextual_suggestions(self) -> ContextualSuggestions:
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
                urgent_jobs = [job for job in self.recent_jobs if job.priority.value == "high"]
                if urgent_jobs:
                    urgent_items.extend([f"High priority: {job.title}" for job in urgent_jobs[:3]])
            
            # Analyze estimates for opportunities
            if self.recent_estimates:
                draft_estimates = [est for est in self.recent_estimates if est.status == EstimateStatus.DRAFT]
                if draft_estimates:
                    opportunities.append(f"Send {len(draft_estimates)} pending estimates to customers")
            
            # Analyze contacts for follow-ups
            if self.recent_contacts:
                high_priority_contacts = [c for c in self.recent_contacts if c.priority == ContextPriority.HIGH]
                if high_priority_contacts:
                    follow_ups.extend([f"Follow up with {contact.name}" for contact in high_priority_contacts[:3]])
            
            return ContextualSuggestions(
                quick_actions=quick_actions,
                follow_ups=follow_ups,
                urgent_items=urgent_items,
                opportunities=opportunities
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating contextual suggestions: {e}")
            return ContextualSuggestions()
    
    # Public API methods
    
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
    
    def get_recent_payments(self, limit: int = 10) -> List[RecentPayment]:
        """Get recent payments with optional limit"""
        return self.recent_payments[:limit]
    
    def get_contextual_suggestions(self) -> Optional[ContextualSuggestions]:
        """Get contextual suggestions"""
        return self.contextual_suggestions
    
    def get_business_summary(self) -> Optional[BusinessSummary]:
        """Get business summary"""
        return self.business_summary
    
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
            if not self._last_refresh or datetime.now() - self._last_refresh > timedelta(minutes=self._refresh_interval_minutes):
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
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None
        } 