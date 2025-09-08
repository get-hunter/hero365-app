#!/usr/bin/env python3
"""
Populate sample product-service associations for testing.

This script creates associations between existing products and services
to demonstrate the service-driven product filtering.
"""

import asyncio
import sys
import os
from uuid import UUID

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.config.dependency_injection import get_container
from app.domain.entities.product_service_association import AssociationType


async def populate_associations():
    """Create sample product-service associations."""
    
    print("🔧 Populating product-service associations...")
    
    # Get Supabase client
    container = get_container()
    client = container._get_supabase_client()
    
    # Sample business and IDs (from the logs we saw)
    business_id = "550e8400-e29b-41d4-a716-446655440010"
    
    # Get existing products
    products_response = client.table("products").select("*").eq("business_id", business_id).execute()
    products = products_response.data
    print(f"📦 Found {len(products)} products")
    
    # Get existing services  
    services_response = client.table("business_services").select("*").eq("business_id", business_id).limit(5).execute()
    services = services_response.data
    print(f"🔧 Found {len(services)} services")
    
    if not products or not services:
        print("❌ No products or services found. Cannot create associations.")
        return
    
    # Create sample associations
    associations = []
    
    # Associate first product with installation services
    if len(products) > 0 and len(services) > 0:
        associations.append({
            "business_id": business_id,
            "product_id": products[0]["id"],
            "service_id": services[0]["id"],
            "association_type": AssociationType.REQUIRED.value,
            "display_order": 1,
            "is_featured": True,
            "notes": "Essential component for this service"
        })
    
    # Associate second product with repair services
    if len(products) > 1 and len(services) > 1:
        associations.append({
            "business_id": business_id,
            "product_id": products[1]["id"],
            "service_id": services[1]["id"],
            "association_type": AssociationType.RECOMMENDED.value,
            "display_order": 2,
            "is_featured": False,
            "notes": "Recommended upgrade for better performance"
        })
    
    # Associate third product with multiple services
    if len(products) > 2:
        for i, service in enumerate(services[:3]):
            associations.append({
                "business_id": business_id,
                "product_id": products[2]["id"],
                "service_id": service["id"],
                "association_type": AssociationType.OPTIONAL.value,
                "display_order": i + 3,
                "is_featured": i == 0,
                "notes": f"Optional add-on for {service.get('service_name', 'service')}"
            })
    
    # Insert associations
    if associations:
        try:
            result = client.table("product_service_associations").insert(associations).execute()
            print(f"✅ Created {len(associations)} product-service associations")
            
            # Show what was created
            for assoc in associations:
                product_name = next((p["name"] for p in products if p["id"] == assoc["product_id"]), "Unknown")
                service_name = next((s.get("service_name", "Unknown") for s in services if s["id"] == assoc["service_id"]), "Unknown")
                print(f"   📦 {product_name} ↔️ 🔧 {service_name} ({assoc['association_type']})")
                
        except Exception as e:
            print(f"❌ Error creating associations: {e}")
    else:
        print("❌ No associations to create")


if __name__ == "__main__":
    asyncio.run(populate_associations())
