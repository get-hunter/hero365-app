"""
Hero365 LiveKit Agents Models Package

Contains all data models and entities used by the voice agents.
Organized by domain for better maintainability using Pydantic for validation.
"""

from .business_context import BusinessContext, BusinessSummary
from .user_context import UserContext
from .contact_models import RecentContact, ContextPriority
from .job_models import RecentJob, JobStatus, JobPriority
from .estimate_models import RecentEstimate, EstimateStatus
from .payment_models import RecentPayment, PaymentStatus, PaymentMethod
from .suggestions import ContextualSuggestions

__all__ = [
    # Business Context
    'BusinessContext',
    'BusinessSummary',
    
    # User Context
    'UserContext',
    
    # Contact Models
    'RecentContact',
    'ContextPriority',
    
    # Job Models
    'RecentJob',
    'JobStatus',
    'JobPriority',
    
    # Estimate Models
    'RecentEstimate',
    'EstimateStatus',
    
    # Payment Models
    'RecentPayment',
    'PaymentStatus',
    'PaymentMethod',
    
    # Suggestions
    'ContextualSuggestions',
] 