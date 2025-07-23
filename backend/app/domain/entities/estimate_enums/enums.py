"""
Estimate Domain Enums

Enums specific to the estimate domain including status management,
document types, and communication tracking.
"""

from enum import Enum
from typing import Optional, List


class EstimateStatus(str, Enum):
    """Estimate status enumeration with voice-friendly parsing."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"
    CANCELLED = "cancelled"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.DRAFT: "Draft",
            self.SENT: "Sent",
            self.VIEWED: "Viewed",
            self.APPROVED: "Approved",
            self.REJECTED: "Rejected",
            self.EXPIRED: "Expired",
            self.CONVERTED: "Converted",
            self.CANCELLED: "Cancelled"
        }
        return display_map.get(self, self.value.title())
    
    @classmethod
    def parse_from_string(cls, status_string: str) -> Optional['EstimateStatus']:
        """
        Parse estimate status from string with support for aliases and common typos.
        
        Args:
            status_string: String representation of status
            
        Returns:
            EstimateStatus enum value or None if invalid
            
        Examples:
            >>> EstimateStatus.parse_from_string("approved")
            EstimateStatus.APPROVED
            >>> EstimateStatus.parse_from_string("canceled")  # typo
            EstimateStatus.CANCELLED
            >>> EstimateStatus.parse_from_string("pending")  # alias
            EstimateStatus.SENT
            >>> EstimateStatus.parse_from_string("EstimateStatus.CONVERTED")  # malformed
            EstimateStatus.CONVERTED
        """
        if not status_string:
            return None
            
        try:
            # Normalize the input
            normalized = status_string.lower().strip()
            
            # Handle malformed enum string representations (e.g., "EstimateStatus.CONVERTED")
            if normalized.startswith('estimatestatus.'):
                # Extract just the enum value part
                normalized = normalized.replace('estimatestatus.', '')
            
            # Direct mapping with aliases and common typos
            status_mapping = {
                "draft": cls.DRAFT,
                "sent": cls.SENT,
                "viewed": cls.VIEWED,
                "approved": cls.APPROVED,
                "rejected": cls.REJECTED,
                "expired": cls.EXPIRED,
                "converted": cls.CONVERTED,
                "cancelled": cls.CANCELLED,
                # Common typos and aliases
                "canceled": cls.CANCELLED,  # American spelling
                "pending": cls.SENT,  # Alias - sent estimates are "pending" approval
                "approve": cls.APPROVED,  # Voice input variation
                "reject": cls.REJECTED,  # Voice input variation
                "cancel": cls.CANCELLED,  # Voice input variation
                "expire": cls.EXPIRED,  # Voice input variation
                "convert": cls.CONVERTED,  # Voice input variation
            }
            
            return status_mapping.get(normalized)
            
        except Exception:
            return None

    @classmethod
    def get_available_transitions(cls, current_status: 'EstimateStatus') -> List['EstimateStatus']:
        """
        Get available status transitions from the current status.
        
        This defines the core business rules for estimate status transitions.
        
        Args:
            current_status: The current status to get transitions from
            
        Returns:
            List of valid EstimateStatus values that can be transitioned to
        """
        transitions = {
            cls.DRAFT: [cls.SENT, cls.CANCELLED],
            cls.SENT: [cls.VIEWED, cls.APPROVED, cls.REJECTED, cls.CANCELLED, cls.EXPIRED],
            cls.VIEWED: [cls.APPROVED, cls.REJECTED, cls.CANCELLED, cls.EXPIRED],
            cls.APPROVED: [cls.CONVERTED, cls.CANCELLED],
            cls.REJECTED: [],  # Terminal state
            cls.CANCELLED: [],  # Terminal state
            cls.CONVERTED: [],  # Terminal state
            cls.EXPIRED: [cls.SENT, cls.CANCELLED]
        }
        
        return transitions.get(current_status, [])
    
    def get_available_transitions_from_this(self) -> List['EstimateStatus']:
        """Get available transitions from this status instance."""
        return self.get_available_transitions(self)


class DocumentType(str, Enum):
    """Document type enumeration for estimates and quotes."""
    ESTIMATE = "estimate"
    QUOTE = "quote"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.ESTIMATE: "Estimate",
            self.QUOTE: "Quote"
        }
        return display_map.get(self, self.value.title())


class EmailStatus(str, Enum):
    """Email delivery status enumeration for estimate communications."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    UNSUBSCRIBED = "unsubscribed"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PENDING: "Pending",
            self.SENT: "Sent",
            self.DELIVERED: "Delivered",
            self.OPENED: "Opened", 
            self.CLICKED: "Clicked",
            self.BOUNCED: "Bounced",
            self.FAILED: "Failed",
            self.UNSUBSCRIBED: "Unsubscribed"
        }
        return display_map.get(self, self.value.title()) 