"""
Job Domain Enums

Enums specific to the job domain including job types, statuses,
priorities, and sources.
"""

from enum import Enum


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