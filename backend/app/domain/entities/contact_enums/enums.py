"""
Contact Domain Enums

Enums specific to the contact domain including contact types, statuses,
priorities, sources, and relationship management.
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