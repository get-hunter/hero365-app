"""
Centralized Enums Module

Single source of truth for all enums used across the application.
These enums work with both domain entities and API schemas.
"""

from enum import Enum


class ContactType(str, Enum):
    """Contact type enumeration."""
    PROSPECT = "prospect"
    LEAD = "lead"
    CUSTOMER = "customer"
    PARTNER = "partner"
    VENDOR = "vendor"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PROSPECT: "Prospect",
            self.LEAD: "Lead", 
            self.CUSTOMER: "Customer",
            self.PARTNER: "Partner",
            self.VENDOR: "Vendor"
        }
        return display_map.get(self, self.value.title())


class ContactStatus(str, Enum):
    """Contact status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.ACTIVE: "Active",
            self.INACTIVE: "Inactive",
            self.ARCHIVED: "Archived", 
            self.BLOCKED: "Blocked"
        }
        return display_map.get(self, self.value.title())


class ContactPriority(str, Enum):
    """Contact priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.LOW: "Low",
            self.MEDIUM: "Medium",
            self.HIGH: "High",
            self.URGENT: "Urgent"
        }
        return display_map.get(self, self.value.title())


class ContactSource(str, Enum):
    """Contact source enumeration."""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    PHONE_CALL = "phone_call"
    WALK_IN = "walk_in"
    TRADE_SHOW = "trade_show"
    ADVERTISING = "advertising"
    ONLINE = "online"
    OTHER = "other"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.WEBSITE: "Website",
            self.REFERRAL: "Referral",
            self.SOCIAL_MEDIA: "Social Media",
            self.EMAIL_CAMPAIGN: "Email Campaign",
            self.PHONE_CALL: "Phone Call",
            self.WALK_IN: "Walk-in",
            self.TRADE_SHOW: "Trade Show",
            self.ADVERTISING: "Advertising",
            self.ONLINE: "Online",
            self.OTHER: "Other"
        }
        return display_map.get(self, self.value.title())


class RelationshipStatus(str, Enum):
    """Relationship status enumeration."""
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    DORMANT = "dormant"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PROSPECT: "Prospect",
            self.QUALIFIED: "Qualified",
            self.PROPOSAL: "Proposal",
            self.NEGOTIATION: "Negotiation",
            self.CLOSED_WON: "Closed Won",
            self.CLOSED_LOST: "Closed Lost",
            self.DORMANT: "Dormant"
        }
        return display_map.get(self, self.value.title())


class LifecycleStage(str, Enum):
    """Lifecycle stage enumeration."""
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"
    RETENTION = "retention"
    ADVOCACY = "advocacy"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.AWARENESS: "Awareness",
            self.INTEREST: "Interest", 
            self.CONSIDERATION: "Consideration",
            self.INTENT: "Intent",
            self.EVALUATION: "Evaluation",
            self.PURCHASE: "Purchase",
            self.RETENTION: "Retention",
            self.ADVOCACY: "Advocacy"
        }
        return display_map.get(self, self.value.title())


class JobType(str, Enum):
    """Job type enumeration."""
    SERVICE = "service"
    PROJECT = "project"
    MAINTENANCE = "maintenance"
    INSTALLATION = "installation"
    REPAIR = "repair"
    INSPECTION = "inspection"
    CONSULTATION = "consultation"
    QUOTE = "quote"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.SERVICE: "Service",
            self.PROJECT: "Project",
            self.MAINTENANCE: "Maintenance",
            self.INSTALLATION: "Installation",
            self.REPAIR: "Repair",
            self.INSPECTION: "Inspection",
            self.CONSULTATION: "Consultation",
            self.QUOTE: "Quote",
            self.FOLLOW_UP: "Follow Up",
            self.EMERGENCY: "Emergency"
        }
        return display_map.get(self, self.value.title())


class JobStatus(str, Enum):
    """Job status enumeration."""
    DRAFT = "draft"
    QUOTED = "quoted"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INVOICED = "invoiced"
    PAID = "paid"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.DRAFT: "Draft",
            self.QUOTED: "Quoted",
            self.SCHEDULED: "Scheduled",
            self.IN_PROGRESS: "In Progress",
            self.ON_HOLD: "On Hold",
            self.COMPLETED: "Completed",
            self.CANCELLED: "Cancelled",
            self.INVOICED: "Invoiced",
            self.PAID: "Paid"
        }
        return display_map.get(self, self.value.title())


class JobPriority(str, Enum):
    """Job priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.LOW: "Low",
            self.MEDIUM: "Medium",
            self.HIGH: "High",
            self.URGENT: "Urgent",
            self.EMERGENCY: "Emergency"
        }
        return display_map.get(self, self.value.title())


class JobSource(str, Enum):
    """Job source enumeration."""
    PHONE = "phone"
    EMAIL = "email"
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    ADVERTISEMENT = "advertisement"
    WALK_IN = "walk_in"
    REPEAT_CUSTOMER = "repeat_customer"
    PARTNERSHIP = "partnership"
    OTHER = "other"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PHONE: "Phone",
            self.EMAIL: "Email",
            self.WEBSITE: "Website",
            self.REFERRAL: "Referral",
            self.SOCIAL_MEDIA: "Social Media",
            self.ADVERTISEMENT: "Advertisement",
            self.WALK_IN: "Walk-in",
            self.REPEAT_CUSTOMER: "Repeat Customer",
            self.PARTNERSHIP: "Partnership",
            self.OTHER: "Other"
        }
        return display_map.get(self, self.value.title())


# Project-related enums
class ProjectType(str, Enum):
    """Project type enumeration."""
    MAINTENANCE = "maintenance"
    INSTALLATION = "installation"
    RENOVATION = "renovation"
    EMERGENCY = "emergency"
    CONSULTATION = "consultation"
    INSPECTION = "inspection"
    REPAIR = "repair"
    CONSTRUCTION = "construction"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.MAINTENANCE: "Maintenance",
            self.INSTALLATION: "Installation",
            self.RENOVATION: "Renovation",
            self.EMERGENCY: "Emergency",
            self.CONSULTATION: "Consultation",
            self.INSPECTION: "Inspection",
            self.REPAIR: "Repair",
            self.CONSTRUCTION: "Construction"
        }
        return display_map.get(self, self.value.title())


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PLANNING: "Planning",
            self.ACTIVE: "Active",
            self.ON_HOLD: "On Hold",
            self.COMPLETED: "Completed",
            self.CANCELLED: "Cancelled"
        }
        return display_map.get(self, self.value.title())


class ProjectPriority(str, Enum):
    """Project priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.LOW: "Low",
            self.MEDIUM: "Medium",
            self.HIGH: "High",
            self.CRITICAL: "Critical"
        }
        return display_map.get(self, self.value.title()) 