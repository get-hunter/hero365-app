"""
Public Professional API Routes

Public endpoints for retrieving professional information, services, products,
and availability for website integration. These endpoints are designed to be
consumed by deployed professional websites.
"""

from fastapi import APIRouter, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/professional", tags=["Public Professional"])


# Response Models
class ServiceResponse(BaseModel):
    """Professional service information."""
    
    id: str = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    description: str = Field(..., description="Service description")
    category: str = Field(..., description="Service category")
    
    # Pricing information
    base_price: Optional[float] = Field(None, description="Base price")
    price_range_min: Optional[float] = Field(None, description="Minimum price")
    price_range_max: Optional[float] = Field(None, description="Maximum price")
    pricing_unit: Optional[str] = Field("service", description="Pricing unit (per hour, per service, etc.)")
    
    # Service details
    duration_minutes: Optional[int] = Field(None, description="Estimated duration in minutes")
    is_emergency: bool = Field(False, description="Emergency service available")
    requires_quote: bool = Field(False, description="Requires custom quote")
    
    # Availability
    available: bool = Field(True, description="Currently available")
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    
    # SEO and display
    keywords: List[str] = Field(default_factory=list, description="SEO keywords")
    image_url: Optional[HttpUrl] = Field(None, description="Service image URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "hvac-repair-001",
                "name": "AC Repair",
                "description": "Professional air conditioning repair service",
                "category": "HVAC Repair",
                "base_price": 99.0,
                "price_range_min": 99.0,
                "price_range_max": 299.0,
                "pricing_unit": "service call",
                "duration_minutes": 120,
                "is_emergency": True,
                "requires_quote": False,
                "available": True,
                "service_areas": ["Austin", "Round Rock", "Cedar Park"],
                "keywords": ["ac repair", "air conditioning", "hvac emergency"]
            }
        }


class ProductResponse(BaseModel):
    """Professional product information."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    brand: Optional[str] = Field(None, description="Product brand")
    model: Optional[str] = Field(None, description="Product model")
    
    # Pricing
    price: Optional[float] = Field(None, description="Product price")
    msrp: Optional[float] = Field(None, description="Manufacturer suggested retail price")
    
    # Availability
    in_stock: bool = Field(True, description="Currently in stock")
    stock_quantity: Optional[int] = Field(None, description="Stock quantity")
    
    # Product details
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Product specifications")
    warranty_years: Optional[int] = Field(None, description="Warranty period in years")
    energy_rating: Optional[str] = Field(None, description="Energy efficiency rating")
    
    # Display
    image_url: Optional[HttpUrl] = Field(None, description="Product image URL")
    datasheet_url: Optional[HttpUrl] = Field(None, description="Product datasheet URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "trane-xr14-3ton",
                "name": "Trane XR14 3-Ton Heat Pump",
                "description": "Energy-efficient heat pump system",
                "category": "Heat Pumps",
                "brand": "Trane",
                "model": "XR14",
                "price": 3299.99,
                "msrp": 3599.99,
                "in_stock": True,
                "stock_quantity": 5,
                "specifications": {
                    "capacity": "3 tons",
                    "seer": "14.5",
                    "refrigerant": "R-410A"
                },
                "warranty_years": 10,
                "energy_rating": "14.5 SEER"
            }
        }


class AvailabilitySlot(BaseModel):
    """Available time slot."""
    
    slot_date: date = Field(..., description="Available date")
    start_time: str = Field(..., description="Start time (HH:MM format)")
    end_time: str = Field(..., description="End time (HH:MM format)")
    slot_type: str = Field(..., description="Slot type (regular, emergency, consultation)")
    duration_minutes: int = Field(..., description="Slot duration in minutes")
    available: bool = Field(True, description="Slot is available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "slot_date": "2024-01-20",
                "start_time": "09:00:00",
                "end_time": "11:00:00",
                "slot_type": "regular",
                "duration_minutes": 120,
                "available": True
            }
        }


class AvailabilityResponse(BaseModel):
    """Professional availability information."""
    
    business_id: str = Field(..., description="Business ID")
    available_dates: List[date] = Field(..., description="Available dates")
    slots: List[AvailabilitySlot] = Field(..., description="Available time slots")
    emergency_available: bool = Field(True, description="Emergency service available")
    next_available: Optional[datetime] = Field(None, description="Next available appointment")
    
    # Service area availability
    service_areas: List[Dict[str, Any]] = Field(default_factory=list, description="Service area availability")
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "business-123",
                "available_dates": ["2024-01-20", "2024-01-21", "2024-01-22"],
                "slots": [],
                "emergency_available": True,
                "next_available": "2024-01-20T09:00:00Z",
                "service_areas": [
                    {"area": "Austin", "available": True, "response_time": "30 min"},
                    {"area": "Round Rock", "available": True, "response_time": "45 min"}
                ]
            }
        }


class ProfessionalProfileResponse(BaseModel):
    """Complete professional profile."""
    
    business_id: str = Field(..., description="Business ID")
    business_name: str = Field(..., description="Business name")
    trade_type: str = Field(..., description="Primary trade type")
    description: str = Field(..., description="Business description")
    
    # Contact information
    phone: str = Field(..., description="Business phone")
    email: str = Field(..., description="Business email")
    address: str = Field(..., description="Business address")
    website: Optional[HttpUrl] = Field(None, description="Business website")
    
    # Service information
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    emergency_service: bool = Field(False, description="24/7 emergency service available")
    
    # Business details
    years_in_business: Optional[int] = Field(None, description="Years in business")
    license_number: Optional[str] = Field(None, description="License number")
    insurance_verified: bool = Field(False, description="Insurance verified")
    
    # Ratings and reviews
    average_rating: Optional[float] = Field(None, description="Average customer rating")
    total_reviews: Optional[int] = Field(None, description="Total number of reviews")
    
    # Certifications
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "business-123",
                "business_name": "Austin Elite HVAC",
                "trade_type": "hvac",
                "description": "Professional HVAC services in Austin",
                "phone": "(512) 555-COOL",
                "email": "service@austinelitehvac.com",
                "address": "456 Tech Ridge Blvd, Austin, TX 78753",
                "service_areas": ["Austin", "Round Rock", "Cedar Park"],
                "emergency_service": True,
                "years_in_business": 25,
                "license_number": "TACLA123456",
                "insurance_verified": True,
                "average_rating": 4.9,
                "total_reviews": 247,
                "certifications": ["NATE Certified", "EPA Certified"]
            }
        }


# Mock data for testing (in production, this would come from database)
def get_mock_professional_data(business_id: str) -> Dict[str, Any]:
    """Get mock professional data for testing."""
    
    # Mock data for different business types
    mock_businesses = {
        "a1b2c3d4-e5f6-7890-1234-567890abcdef": {
            "profile": {
                "business_id": business_id,
                "business_name": "Austin Elite HVAC",
                "trade_type": "hvac",
                "description": "Premier HVAC services for Austin homes and businesses. Specializing in energy-efficient installations, emergency repairs, and preventative maintenance.",
                "phone": "(512) 555-COOL",
                "email": "info@austinelitehvac.com",
                "address": "123 Main St, Austin, TX 78701",
                "website": "https://www.austinelitehvac.com",
                "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville", "Georgetown"],
                "emergency_service": True,
                "years_in_business": 15,
                "license_number": "TACLA123456",
                "insurance_verified": True,
                "average_rating": 4.9,
                "total_reviews": 187,
                "certifications": ["NATE Certified", "EPA Universal", "BBB A+ Rating"]
            },
            "services": [
                {
                    "id": "emergency-ac-repair",
                    "name": "Emergency AC Repair",
                    "description": "24/7 rapid response for all AC breakdowns",
                    "category": "Repair",
                    "base_price": 149.0,
                    "price_range_min": 149.0,
                    "price_range_max": 599.0,
                    "pricing_unit": "service call",
                    "duration_minutes": 90,
                    "is_emergency": True,
                    "requires_quote": False,
                    "available": True,
                    "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville"],
                    "keywords": ["emergency ac repair", "air conditioning repair", "hvac emergency"]
                },
                {
                    "id": "hvac-installation",
                    "name": "HVAC System Installation",
                    "description": "New energy-efficient HVAC system installation and replacement",
                    "category": "Installation",
                    "base_price": None,
                    "price_range_min": 3000.0,
                    "price_range_max": 12000.0,
                    "pricing_unit": "complete system",
                    "duration_minutes": 240,
                    "is_emergency": False,
                    "requires_quote": True,
                    "available": True,
                    "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville"],
                    "keywords": ["hvac installation", "new ac system", "heating installation"]
                },
                {
                    "id": "maintenance-plan",
                    "name": "Preventative Maintenance Plan",
                    "description": "Annual tune-ups to ensure optimal system performance and longevity",
                    "category": "Maintenance",
                    "base_price": 199.0,
                    "price_range_min": 199.0,
                    "price_range_max": 399.0,
                    "pricing_unit": "annual plan",
                    "duration_minutes": 60,
                    "is_emergency": False,
                    "requires_quote": False,
                    "available": True,
                    "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville"],
                    "keywords": ["hvac maintenance", "ac tune up", "preventive service"]
                },
                {
                    "id": "duct-cleaning",
                    "name": "Duct Cleaning",
                    "description": "Improve air quality and system efficiency with professional duct cleaning",
                    "category": "Air Quality",
                    "base_price": 250.0,
                    "price_range_min": 250.0,
                    "price_range_max": 450.0,
                    "pricing_unit": "complete service",
                    "duration_minutes": 180,
                    "is_emergency": False,
                    "requires_quote": False,
                    "available": True,
                    "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville"],
                    "keywords": ["duct cleaning", "air quality", "hvac cleaning"]
                }
            ],
            "products": [
                {
                    "id": "smart-thermostat-ecobee",
                    "name": "Smart Thermostat (Ecobee)",
                    "description": "Energy-saving smart thermostat with remote control and voice integration",
                    "category": "Thermostats",
                    "brand": "Ecobee",
                    "model": "SmartThermostat",
                    "price": 249.99,
                    "msrp": 299.99,
                    "in_stock": True,
                    "stock_quantity": 15,
                    "specifications": {
                        "features": "Wi-Fi, Voice Control, Room Sensors",
                        "compatibility": "Most HVAC systems",
                        "warranty": "3 years"
                    },
                    "warranty_years": 3,
                    "energy_rating": "ENERGY STAR Certified"
                },
                {
                    "id": "hepa-air-filter",
                    "name": "HEPA Air Filter (MERV 13)",
                    "description": "High-efficiency particulate air filter for superior air purification",
                    "category": "Air Filters",
                    "brand": "FilterBuy",
                    "model": "MERV 13",
                    "price": 39.99,
                    "msrp": 49.99,
                    "in_stock": True,
                    "stock_quantity": 100,
                    "specifications": {
                        "size": "20x20x1",
                        "merv_rating": "13",
                        "efficiency": "99.97% at 0.3 microns"
                    },
                    "warranty_years": 1,
                    "energy_rating": "High Efficiency"
                },
                {
                    "id": "central-ac-unit-3ton",
                    "name": "Central AC Unit (3 Ton)",
                    "description": "Energy-efficient central air conditioning system for medium homes",
                    "category": "AC Units",
                    "brand": "Trane",
                    "model": "XR14",
                    "price": 2499.99,
                    "msrp": 2799.99,
                    "in_stock": True,
                    "stock_quantity": 5,
                    "specifications": {
                        "capacity": "3 tons",
                        "seer": "14.5",
                        "refrigerant": "R-410A"
                    },
                    "warranty_years": 10,
                    "energy_rating": "14.5 SEER"
                }
            ]
        }
    }
    
    # Return the data for the requested business_id, or default HVAC data
    return mock_businesses.get(business_id, mock_businesses["a1b2c3d4-e5f6-7890-1234-567890abcdef"])


# API Endpoints
@router.get("/profile/{business_id}", response_model=ProfessionalProfileResponse)
async def get_professional_profile(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get complete professional profile information.
    
    Returns business details, contact information, service areas, and credentials.
    """
    
    try:
        # In production, this would query the database
        mock_data = get_mock_professional_data(business_id)
        
        return ProfessionalProfileResponse(**mock_data["profile"])
        
    except Exception as e:
        logger.error(f"Failed to get professional profile {business_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )


@router.get("/services/{business_id}", response_model=List[ServiceResponse])
async def get_professional_services(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    emergency_only: bool = Query(False, description="Show only emergency services"),
    available_only: bool = Query(True, description="Show only available services")
):
    """
    Get all services offered by a professional.
    
    Returns detailed service information including pricing, availability, and descriptions.
    """
    
    try:
        # In production, this would query the database
        mock_data = get_mock_professional_data(business_id)
        services = mock_data["services"]
        
        # Apply filters
        if category:
            services = [s for s in services if s["category"].lower() == category.lower()]
        
        if emergency_only:
            services = [s for s in services if s["is_emergency"]]
        
        if available_only:
            services = [s for s in services if s["available"]]
        
        return [ServiceResponse(**service) for service in services]
        
    except Exception as e:
        logger.error(f"Failed to get services for {business_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve services"
        )


@router.get("/products/{business_id}", response_model=List[ProductResponse])
async def get_professional_products(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    in_stock_only: bool = Query(True, description="Show only in-stock products"),
    max_price: Optional[float] = Query(None, description="Maximum price filter")
):
    """
    Get all products available from a professional.
    
    Returns product catalog with pricing, availability, and specifications.
    """
    
    try:
        # In production, this would query the database
        mock_data = get_mock_professional_data(business_id)
        products = mock_data["products"]
        
        # Apply filters
        if category:
            products = [p for p in products if p["category"].lower() == category.lower()]
        
        if brand:
            products = [p for p in products if p.get("brand", "").lower() == brand.lower()]
        
        if in_stock_only:
            products = [p for p in products if p["in_stock"]]
        
        if max_price:
            products = [p for p in products if p.get("price", 0) <= max_price]
        
        return [ProductResponse(**product) for product in products]
        
    except Exception as e:
        logger.error(f"Failed to get products for {business_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )


@router.get("/availability/{business_id}", response_model=AvailabilityResponse)
async def get_professional_availability(
    business_id: str = Path(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date for availability check"),
    end_date: Optional[date] = Query(None, description="End date for availability check"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    service_area: Optional[str] = Query(None, description="Filter by service area")
):
    """
    Get professional availability for scheduling.
    
    Returns available time slots, emergency availability, and service area coverage.
    """
    
    try:
        # Generate mock availability data
        from datetime import timedelta
        
        today = date.today()
        if not start_date:
            start_date = today
        if not end_date:
            end_date = today + timedelta(days=14)
        
        # Generate available dates
        available_dates = []
        current_date = start_date
        while current_date <= end_date:
            # Skip Sundays for regular service
            if current_date.weekday() != 6:
                available_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Generate time slots for next few days
        slots = []
        for i in range(3):  # Next 3 available days
            slot_date = available_dates[i] if i < len(available_dates) else None
            if slot_date:
                # Morning slots
                slots.append(AvailabilitySlot(
                    date=slot_date,
                    start_time="09:00",
                    end_time="11:00",
                    slot_type="regular",
                    duration_minutes=120,
                    available=True
                ))
                # Afternoon slots
                slots.append(AvailabilitySlot(
                    date=slot_date,
                    start_time="13:00",
                    end_time="15:00",
                    slot_type="regular",
                    duration_minutes=120,
                    available=True
                ))
        
        # Service area availability
        service_areas = [
            {"area": "Austin", "available": True, "response_time": "30 min"},
            {"area": "Round Rock", "available": True, "response_time": "45 min"},
            {"area": "Cedar Park", "available": True, "response_time": "45 min"},
            {"area": "Pflugerville", "available": True, "response_time": "40 min"},
            {"area": "Georgetown", "available": True, "response_time": "50 min"}
        ]
        
        if service_area:
            service_areas = [sa for sa in service_areas if sa["area"].lower() == service_area.lower()]
        
        next_available = datetime.combine(available_dates[0], time(9, 0)) if available_dates else None
        
        return AvailabilityResponse(
            business_id=business_id,
            available_dates=available_dates[:14],  # Next 2 weeks
            slots=slots,
            emergency_available=True,
            next_available=next_available,
            service_areas=service_areas
        )
        
    except Exception as e:
        logger.error(f"Failed to get availability for {business_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve availability"
        )


@router.get("/search")
async def search_professionals(
    trade_type: Optional[str] = Query(None, description="Filter by trade type"),
    location: Optional[str] = Query(None, description="Search by location/service area"),
    service: Optional[str] = Query(None, description="Search by service type"),
    emergency_only: bool = Query(False, description="Show only emergency service providers"),
    radius_miles: int = Query(25, description="Search radius in miles")
):
    """
    Search for professionals by criteria.
    
    Returns list of professionals matching search criteria.
    """
    
    try:
        # Mock search results
        professionals = [
            {
                "business_id": "austin-elite-hvac",
                "business_name": "Austin Elite HVAC",
                "trade_type": "hvac",
                "phone": "(512) 555-COOL",
                "service_areas": ["Austin", "Round Rock", "Cedar Park"],
                "emergency_service": True,
                "average_rating": 4.9,
                "total_reviews": 247,
                "distance_miles": 5.2
            },
            {
                "business_id": "texas-comfort-hvac",
                "business_name": "Texas Comfort HVAC",
                "trade_type": "hvac",
                "phone": "(512) 555-HEAT",
                "service_areas": ["Austin", "Pflugerville", "Manor"],
                "emergency_service": True,
                "average_rating": 4.7,
                "total_reviews": 189,
                "distance_miles": 8.1
            }
        ]
        
        # Apply filters
        if trade_type:
            professionals = [p for p in professionals if p["trade_type"] == trade_type.lower()]
        
        if location:
            professionals = [p for p in professionals if any(location.lower() in area.lower() for area in p["service_areas"])]
        
        if emergency_only:
            professionals = [p for p in professionals if p["emergency_service"]]
        
        return {
            "results": professionals,
            "total_count": len(professionals),
            "search_criteria": {
                "trade_type": trade_type,
                "location": location,
                "service": service,
                "emergency_only": emergency_only,
                "radius_miles": radius_miles
            }
        }
        
    except Exception as e:
        logger.error(f"Professional search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )
