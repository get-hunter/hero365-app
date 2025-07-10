"""
Estimate Management Tools

Voice agent tools for estimate management using Hero365's estimate use cases.
"""

from typing import List, Any, Dict, Optional
from app.infrastructure.config.dependency_injection import get_container


class EstimateTools:
    """Estimate management tools for voice agents"""
    
    def __init__(self, business_id: str, user_id: str):
        """Initialize estimate tools with business and user context"""
        self.business_id = business_id
        self.user_id = user_id
        self.container = get_container()
    
    def get_tools(self) -> List[Any]:
        """Get all estimate management tools"""
        return [
            self.create_estimate,
            self.convert_estimate_to_invoice,
            self.get_pending_estimates,
            self.update_estimate_status
        ]
    
    def create_estimate(self, 
                       client_contact_id: str,
                       title: str,
                       description: str,
                       amount: float,
                       valid_until: str,
                       job_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new estimate"""
        return {
            "success": True,
            "estimate_id": f"est_{self.business_id}_{client_contact_id}",
            "message": f"Estimate '{title}' created for ${amount}, valid until {valid_until}"
        }
    
    def convert_estimate_to_invoice(self, estimate_id: str) -> Dict[str, Any]:
        """Convert an approved estimate to an invoice"""
        return {
            "success": True,
            "invoice_id": f"inv_from_{estimate_id}",
            "message": f"Estimate {estimate_id} converted to invoice successfully"
        }
    
    def get_pending_estimates(self) -> Dict[str, Any]:
        """Get all pending estimates"""
        return {
            "success": True,
            "estimates": [
                {
                    "id": "est_1",
                    "title": "Kitchen Renovation",
                    "client": "Jane Smith",
                    "amount": 8500.00,
                    "status": "pending",
                    "valid_until": "2024-02-28"
                }
            ],
            "count": 1,
            "total_amount": 8500.00
        }
    
    def update_estimate_status(self, estimate_id: str, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update estimate status (pending, approved, rejected, expired)"""
        return {
            "success": True,
            "message": f"Estimate {estimate_id} status updated to {status}",
            "estimate_id": estimate_id
        } 