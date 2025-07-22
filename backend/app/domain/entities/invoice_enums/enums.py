"""
Invoice Domain Enums

Enums specific to the invoice domain including invoice statuses
and payment management.
"""

from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"  
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.DRAFT: "Draft",
            self.SENT: "Sent",
            self.VIEWED: "Viewed",
            self.PAID: "Paid",
            self.PARTIALLY_PAID: "Partially Paid",
            self.OVERDUE: "Overdue",
            self.CANCELLED: "Cancelled",
            self.REFUNDED: "Refunded"
        }
        return display_map.get(self, self.value.title())


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PENDING: "Pending",
            self.PROCESSING: "Processing",
            self.COMPLETED: "Completed",
            self.FAILED: "Failed",
            self.CANCELLED: "Cancelled",
            self.REFUNDED: "Refunded",
            self.PARTIALLY_REFUNDED: "Partially Refunded"
        }
        return display_map.get(self, self.value.title()) 