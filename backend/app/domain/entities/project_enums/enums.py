"""
Project Domain Enums

Enums specific to the project domain including project types,
statuses, and priorities.
"""

from enum import Enum


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