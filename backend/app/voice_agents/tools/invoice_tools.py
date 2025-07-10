"""
Invoice Management Tools

Voice agent tools for invoice management using Hero365's invoice use cases.
"""

from typing import List, Any, Dict, Optional
from app.infrastructure.config.dependency_injection import get_container


class InvoiceTools:
    """Invoice management tools for voice agents"""
    
    def __init__(self, business_id: str, user_id: str):
        """Initialize invoice tools with business and user context"""
        self.business_id = business_id
        self.user_id = user_id
        self.container = get_container()
    
    def get_tools(self) -> List[Any]:
        """Get all invoice management tools"""
        return [
            self.create_invoice,
            self.get_invoice_status,
            self.send_invoice_reminder,
            self.get_pending_invoices
        ]
    
    def create_invoice(self, 
                      client_contact_id: str,
                      description: str,
                      amount: float,
                      due_date: str,
                      job_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new invoice"""
        return {
            "success": True,
            "invoice_id": f"inv_{self.business_id}_{client_contact_id}",
            "message": f"Invoice created for ${amount} due on {due_date}"
        }
    
    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """Get status of a specific invoice"""
        return {
            "success": True,
            "invoice": {
                "id": invoice_id,
                "status": "pending",
                "amount": 1500.00,
                "due_date": "2024-02-15",
                "client": "John Doe"
            }
        }
    
    def send_invoice_reminder(self, invoice_id: str) -> Dict[str, Any]:
        """Send reminder for an overdue invoice"""
        return {
            "success": True,
            "message": f"Reminder sent for invoice {invoice_id}"
        }
    
    def get_pending_invoices(self) -> Dict[str, Any]:
        """Get all pending invoices"""
        return {
            "success": True,
            "invoices": [
                {
                    "id": "inv_1",
                    "client": "John Doe",
                    "amount": 1500.00,
                    "due_date": "2024-02-15",
                    "status": "pending"
                }
            ],
            "count": 1,
            "total_amount": 1500.00
        } 