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
    WEBSITE = "website"
    GOOGLE_ADS = "google_ads"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    PHONE_CALL = "phone_call"
    PHONE = "phone"
    WALK_IN = "walk_in"
    EMAIL_MARKETING = "email_marketing"
    TRADE_SHOW = "trade_show"
    DIRECT_MAIL = "direct_mail"
    YELLOW_PAGES = "yellow_pages"
    REPEAT_CUSTOMER = "repeat_customer"
    PARTNER = "partner"
    EXISTING_CUSTOMER = "existing_customer"
    COLD_OUTREACH = "cold_outreach"
    EMERGENCY_CALL = "emergency_call"
    EMERGENCY = "emergency"
    EVENT = "event"
    DIRECT = "direct"
    OTHER = "other"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.WEBSITE: "Website",
            self.GOOGLE_ADS: "Google Ads",
            self.SOCIAL_MEDIA: "Social Media",
            self.REFERRAL: "Referral",
            self.PHONE_CALL: "Phone Call",
            self.PHONE: "Phone",
            self.WALK_IN: "Walk-in",
            self.EMAIL_MARKETING: "Email Marketing",
            self.TRADE_SHOW: "Trade Show",
            self.DIRECT_MAIL: "Direct Mail",
            self.YELLOW_PAGES: "Yellow Pages",
            self.REPEAT_CUSTOMER: "Repeat Customer",
            self.PARTNER: "Partner",
            self.EXISTING_CUSTOMER: "Existing Customer",
            self.COLD_OUTREACH: "Cold Outreach",
            self.EMERGENCY_CALL: "Emergency Call",
            self.EMERGENCY: "Emergency",
            self.EVENT: "Event",
            self.DIRECT: "Direct",
            self.OTHER: "Other"
        }
        return display_map.get(self, self.value.title()) 