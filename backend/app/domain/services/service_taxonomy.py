"""
Service taxonomy mapping for categorizing services by trade/category.
Maps service slugs to display categories for navigation and SEO organization.
"""

from typing import Dict, List, Set
from enum import Enum


class ServiceCategory(Enum):
    """Service categories for navigation organization."""
    AIR_CONDITIONING = "Air Conditioning"
    HEATING = "Heating"
    ELECTRICAL = "Electrical"
    PLUMBING = "Plumbing"
    COMMERCIAL_HVAC = "Commercial HVAC"
    EMERGENCY = "Emergency Services"
    MAINTENANCE = "Maintenance"


# Service slug to category mapping
SERVICE_CATEGORY_MAP: Dict[str, ServiceCategory] = {
    # Air Conditioning
    "ac-installation": ServiceCategory.AIR_CONDITIONING,
    "ac-repair": ServiceCategory.AIR_CONDITIONING,
    "air-conditioner-repair": ServiceCategory.AIR_CONDITIONING,
    "ductless-split-system": ServiceCategory.AIR_CONDITIONING,
    "heat-pump-service": ServiceCategory.AIR_CONDITIONING,
    "cooling-system-installation": ServiceCategory.AIR_CONDITIONING,
    "central-air-installation": ServiceCategory.AIR_CONDITIONING,
    
    # Heating
    "furnace-repair": ServiceCategory.HEATING,
    "furnace-installation": ServiceCategory.HEATING,
    "heater-repair": ServiceCategory.HEATING,
    "heating-installation": ServiceCategory.HEATING,
    "boiler-service": ServiceCategory.HEATING,
    "heat-pump-installation": ServiceCategory.HEATING,
    "radiant-heating": ServiceCategory.HEATING,
    
    # HVAC General (categorize as most relevant)
    "hvac-repair": ServiceCategory.AIR_CONDITIONING,
    "hvac-installation": ServiceCategory.AIR_CONDITIONING,
    "hvac-maintenance": ServiceCategory.MAINTENANCE,
    "duct-cleaning": ServiceCategory.MAINTENANCE,
    "duct-inspection": ServiceCategory.MAINTENANCE,
    "thermostat-installation": ServiceCategory.MAINTENANCE,
    "indoor-air-quality": ServiceCategory.MAINTENANCE,
    
    # Electrical
    "electrical-repair": ServiceCategory.ELECTRICAL,
    "electrical-installation": ServiceCategory.ELECTRICAL,
    "panel-upgrades": ServiceCategory.ELECTRICAL,
    "outlet-installation": ServiceCategory.ELECTRICAL,
    "lighting-installation": ServiceCategory.ELECTRICAL,
    "electrical-inspection": ServiceCategory.ELECTRICAL,
    "ev-charger-installation": ServiceCategory.ELECTRICAL,
    "electrical-maintenance": ServiceCategory.ELECTRICAL,
    "lighting-systems": ServiceCategory.ELECTRICAL,
    "power-distribution": ServiceCategory.ELECTRICAL,
    
    # Plumbing
    "plumbing-repair": ServiceCategory.PLUMBING,
    "plumbing-installation": ServiceCategory.PLUMBING,
    "drain-cleaning": ServiceCategory.PLUMBING,
    "water-heater-service": ServiceCategory.PLUMBING,
    "water-heater-installation": ServiceCategory.PLUMBING,
    "pipe-installation": ServiceCategory.PLUMBING,
    "fixture-installation": ServiceCategory.PLUMBING,
    "leak-detection": ServiceCategory.PLUMBING,
    "sewer-line-service": ServiceCategory.PLUMBING,
    "backflow-prevention": ServiceCategory.PLUMBING,
    "grease-trap-service": ServiceCategory.PLUMBING,
    "water-line-service": ServiceCategory.PLUMBING,
    
    # Commercial HVAC
    "commercial-hvac": ServiceCategory.COMMERCIAL_HVAC,
    "building-automation": ServiceCategory.COMMERCIAL_HVAC,
    "energy-management": ServiceCategory.COMMERCIAL_HVAC,
    "commercial-plumbing": ServiceCategory.COMMERCIAL_HVAC,
    "chiller-service": ServiceCategory.COMMERCIAL_HVAC,
    "rooftop-units": ServiceCategory.COMMERCIAL_HVAC,
    "ventilation-systems": ServiceCategory.COMMERCIAL_HVAC,
    "air-quality-systems": ServiceCategory.COMMERCIAL_HVAC,
    
    # Emergency Services
    "emergency-hvac": ServiceCategory.EMERGENCY,
    "emergency-service": ServiceCategory.EMERGENCY,
    "emergency-plumbing": ServiceCategory.EMERGENCY,
    "emergency-electrical": ServiceCategory.EMERGENCY,
    
    # Maintenance
    "preventive-maintenance": ServiceCategory.MAINTENANCE,
    "seasonal-maintenance": ServiceCategory.MAINTENANCE,
    "maintenance-contracts": ServiceCategory.MAINTENANCE,
    "energy-audits": ServiceCategory.MAINTENANCE,
}

# Category display order for navigation
CATEGORY_DISPLAY_ORDER: List[ServiceCategory] = [
    ServiceCategory.AIR_CONDITIONING,
    ServiceCategory.HEATING,
    ServiceCategory.ELECTRICAL,
    ServiceCategory.PLUMBING,
    ServiceCategory.COMMERCIAL_HVAC,
    ServiceCategory.MAINTENANCE,
    ServiceCategory.EMERGENCY,
]

# Category descriptions for SEO and navigation
CATEGORY_DESCRIPTIONS: Dict[ServiceCategory, str] = {
    ServiceCategory.AIR_CONDITIONING: "Complete AC services",
    ServiceCategory.HEATING: "Heating system services", 
    ServiceCategory.ELECTRICAL: "Electrical services",
    ServiceCategory.PLUMBING: "Plumbing services",
    ServiceCategory.COMMERCIAL_HVAC: "Commercial HVAC solutions",
    ServiceCategory.MAINTENANCE: "Preventive maintenance services",
    ServiceCategory.EMERGENCY: "24/7 emergency services",
}


def get_service_category(service_slug: str) -> ServiceCategory:
    """Get the category for a service slug."""
    return SERVICE_CATEGORY_MAP.get(service_slug, ServiceCategory.MAINTENANCE)


def get_services_by_category(service_slugs: List[str]) -> Dict[ServiceCategory, List[str]]:
    """Group service slugs by category."""
    categories: Dict[ServiceCategory, List[str]] = {}
    
    for slug in service_slugs:
        category = get_service_category(slug)
        if category not in categories:
            categories[category] = []
        categories[category].append(slug)
    
    return categories


def get_ordered_categories(categories: Dict[ServiceCategory, List[str]]) -> List[ServiceCategory]:
    """Get categories in display order, filtering to only those with services."""
    return [cat for cat in CATEGORY_DISPLAY_ORDER if cat in categories and categories[cat]]


def get_category_info(category: ServiceCategory) -> Dict[str, str]:
    """Get display information for a category."""
    return {
        "name": category.value,
        "description": CATEGORY_DESCRIPTIONS.get(category, "Professional services"),
        "slug": category.name.lower().replace("_", "-")
    }
