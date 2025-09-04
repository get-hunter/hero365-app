"""
Contractor Checkout API Routes

Public endpoints for processing cart checkout and creating estimates/bookings.
"""

from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any, List
import logging
import os
import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client

from .schemas import CheckoutRequest, CheckoutResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/{business_id}/checkout/process",
    response_model=CheckoutResponse,
    summary="Process Cart Checkout",
    description="Convert shopping cart to estimate and schedule installation appointments"
)
async def process_checkout(
    business_id: str = Path(..., description="Business ID"),
    checkout_request: CheckoutRequest = Body(..., description="Checkout details")
) -> CheckoutResponse:
    """
    Process cart checkout by:
    1. Creating an estimate from cart items
    2. Creating customer contact if needed
    3. Scheduling installation appointments
    4. Updating cart status to completed
    """
    
    try:
        # Get Supabase client
        supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Validate business exists
        business_result = supabase.table("businesses").select("*").eq("id", business_id).eq("is_active", True).single().execute()
        if not business_result.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        business = business_result.data
        
        # Get cart items
        cart_result = supabase.table("shopping_carts").select("""
            *,
            cart_items (
                id,
                product_id,
                installation_option_id,
                quantity,
                membership_type,
                unit_price,
                total_price,
                products (
                    name,
                    sku,
                    description,
                    unit_price
                ),
                product_installation_options (
                    option_name,
                    description,
                    estimated_duration_hours,
                    base_install_price,
                    residential_install_price,
                    commercial_install_price,
                    premium_install_price
                )
            )
        """).eq("id", checkout_request.cart_id).single().execute()
        
        if not cart_result.data:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        cart = cart_result.data
        cart_items = cart["cart_items"]
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Create or find customer contact
        contact_id = await _create_or_find_contact(
            supabase,
            business_id,
            checkout_request.customer
        )
        
        # Create estimate
        estimate_id, estimate_number = await _create_estimate_from_cart(
            supabase,
            business_id,
            contact_id,
            checkout_request.customer,
            cart,
            checkout_request.notes
        )
        
        # Schedule installations for items that require them
        booking_id, booking_number = await _schedule_installations(
            supabase,
            business_id,
            checkout_request.customer,
            checkout_request.installation,
            cart_items,
            estimate_id
        )
        
        # Mark cart as completed
        supabase.table("shopping_carts").update({
            "cart_status": "completed",
            "updated_at": datetime.now().isoformat()
        }).eq("id", checkout_request.cart_id).execute()
        
        return CheckoutResponse(
            success=True,
            estimate_id=estimate_id,
            booking_id=booking_id,
            estimate_number=estimate_number,
            booking_number=booking_number,
            total_amount=float(cart["total_amount"]),
            message="Checkout completed successfully! Your estimate and installation appointments have been created."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing checkout for business {business_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process checkout: {str(e)}"
        )


# ======================================
# CHECKOUT HELPER FUNCTIONS
# ======================================

async def _create_or_find_contact(
    supabase: Client,
    business_id: str,
    customer
) -> str:
    """Create or find customer contact."""
    
    # Try to find existing contact by email
    existing_contact = supabase.table("contacts").select("id").eq(
        "business_id", business_id
    ).eq("email", customer.email).execute()
    
    if existing_contact.data:
        return existing_contact.data[0]["id"]
    
    # Create new contact
    name_parts = customer.name.split(" ", 1)
    first_name = name_parts[0] if name_parts else customer.name
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    contact_data = {
        "business_id": business_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": {
            "street": customer.address,
            "city": customer.city,
            "state": customer.state,
            "zip": customer.postal_code
        },
        "contact_type": "customer",
        "is_active": True,
        "created_date": datetime.now().isoformat()
    }
    
    result = supabase.table("contacts").insert(contact_data).execute()
    return result.data[0]["id"]


async def _create_estimate_from_cart(
    supabase: Client,
    business_id: str,
    contact_id: str,
    customer,
    cart: Dict[str, Any],
    notes: str
) -> tuple[str, str]:
    """Create estimate from cart items."""
    
    # Generate estimate number
    estimate_number = f"EST-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create estimate
    estimate_data = {
        "business_id": business_id,
        "contact_id": contact_id,
        "estimate_number": estimate_number,
        "title": "Product Installation Estimate",
        "description": "Estimate for product purchase and installation services",
        "status": "draft",
        "currency": "USD",
        "subtotal": float(cart["subtotal"]),
        "tax_amount": float(cart["tax_amount"]),
        "total_amount": float(cart["total_amount"]),
        "discount_amount": float(cart.get("total_savings", 0)),
        "client_name": customer.name,
        "client_email": customer.email,
        "client_phone": customer.phone,
        "client_address": {
            "street": customer.address,
            "city": customer.city,
            "state": customer.state,
            "zip": customer.postal_code
        },
        "notes": notes,
        "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        "created_by": "system",
        "created_date": datetime.now().isoformat()
    }
    
    estimate_result = supabase.table("estimates").insert(estimate_data).execute()
    estimate_id = estimate_result.data[0]["id"]
    
    # Create estimate line items
    for item in cart["cart_items"]:
        product = item["products"]
        installation = item["product_installation_options"]
        
        # Product line item
        product_line = {
            "estimate_id": estimate_id,
            "sort_order": len(cart["cart_items"]) * 2,
            "name": product["name"],
            "description": f"{product['description']}\nSKU: {product['sku']}",
            "quantity": float(item["quantity"]),
            "unit": "each",
            "unit_price": float(product["unit_price"]),
            "total_amount": float(product["unit_price"]) * float(item["quantity"])
        }
        
        # Installation line item
        installation_price = _get_installation_price_for_membership(
            installation,
            item["membership_type"]
        )
        
        installation_line = {
            "estimate_id": estimate_id,
            "sort_order": len(cart["cart_items"]) * 2 + 1,
            "name": f"{installation['option_name']} - {product['name']}",
            "description": installation["description"],
            "quantity": float(item["quantity"]),
            "unit": "installation",
            "unit_price": installation_price,
            "total_amount": installation_price * float(item["quantity"])
        }
        
        # Insert both line items
        supabase.table("estimate_line_items").insert([product_line, installation_line]).execute()
    
    return estimate_id, estimate_number


async def _schedule_installations(
    supabase: Client,
    business_id: str,
    customer,
    installation_prefs,
    cart_items: List[Dict[str, Any]],
    estimate_id: str
) -> tuple[str, str]:
    """Schedule installation appointments."""
    
    # Generate booking number
    booking_number = f"BK-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:6].upper()}"
    
    # Calculate total installation duration
    total_duration = 0
    service_description = []
    
    for item in cart_items:
        installation = item["product_installation_options"]
        duration = installation.get("estimated_duration_hours", 2) * 60  # Convert to minutes
        total_duration += duration * item["quantity"]
        service_description.append(f"{item['products']['name']} - {installation['option_name']}")
    
    # Parse preferred date
    try:
        preferred_date = datetime.strptime(installation_prefs.preferred_date, "%Y-%m-%d")
        
        # Set time based on preference
        if installation_prefs.preferred_time == "morning":
            preferred_date = preferred_date.replace(hour=8, minute=0)
        elif installation_prefs.preferred_time == "afternoon":
            preferred_date = preferred_date.replace(hour=13, minute=0)
        else:  # evening
            preferred_date = preferred_date.replace(hour=17, minute=0)
            
    except ValueError:
        # Default to tomorrow morning if date parsing fails
        preferred_date = datetime.now() + timedelta(days=1)
        preferred_date = preferred_date.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Create booking
    booking_data = {
        "business_id": business_id,
        "booking_number": booking_number,
        "service_name": "Product Installation Service",
        "estimated_duration_minutes": min(total_duration, 480),  # Cap at 8 hours
        "requested_at": preferred_date.isoformat(),
        "customer_name": customer.name,
        "customer_email": customer.email,
        "customer_phone": customer.phone,
        "service_address": customer.address,
        "service_city": customer.city,
        "service_state": customer.state,
        "service_zip": customer.postal_code,
        "problem_description": f"Installation of: {', '.join(service_description[:3])}{'...' if len(service_description) > 3 else ''}",
        "special_instructions": installation_prefs.special_instructions,
        "access_instructions": installation_prefs.access_instructions,
        "status": "pending",
        "source": "website_checkout",
        "created_at": datetime.now().isoformat()
    }
    
    booking_result = supabase.table("bookings").insert(booking_data).execute()
    booking_id = booking_result.data[0]["id"]
    
    return booking_id, booking_number


def _get_installation_price_for_membership(
    installation: Dict[str, Any],
    membership_type: str
) -> float:
    """Get installation price based on membership type."""
    
    if membership_type == "residential":
        return float(installation.get("residential_install_price", installation["base_install_price"]))
    elif membership_type == "commercial":
        return float(installation.get("commercial_install_price", installation["base_install_price"]))
    elif membership_type == "premium":
        return float(installation.get("premium_install_price", installation["base_install_price"]))
    else:
        return float(installation["base_install_price"])
