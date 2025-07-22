"""
Payment Models for Hero365 LiveKit Agents
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    """Payment status options"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Payment method options"""
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    ONLINE = "online"
    OTHER = "other"


class RecentPayment(BaseModel):
    """Recent payment information"""
    id: str = Field(..., description="Unique payment identifier")
    invoice_id: str = Field(..., description="Associated invoice ID")
    amount: float = Field(..., gt=0, description="Payment amount")
    status: PaymentStatus = Field(..., description="Current payment status")
    payment_date: datetime = Field(..., description="Payment date and time")
    payment_method: PaymentMethod = Field(..., description="Payment method used")
    contact_name: str = Field(..., description="Contact's name")
    transaction_id: str = Field(None, description="External transaction identifier")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "pay_123",
                "invoice_id": "inv_456",
                "amount": 1250.00,
                "status": "completed",
                "payment_date": "2024-01-15T16:30:00Z",
                "payment_method": "credit_card",
                "contact_name": "Jane Doe",
                "transaction_id": "txn_789xyz"
            }
        } 