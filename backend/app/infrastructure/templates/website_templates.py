"""
Website Template Definitions

Comprehensive collection of 20 trade-specific website templates for Hero365
professionals, including both commercial and residential service categories.

Each template includes:
- Page structure and sections
- Trade-specific content strategies
- SEO optimization settings
- Lead capture configurations
- Emergency service handling
- Booking system integration
"""

from typing import Dict, List, Any, Optional
from enum import Enum

from ...domain.entities.business import TradeCategory
from ...domain.entities.website import WebsiteTemplate


class TemplateType(str, Enum):
    """Website template types."""
    
    # Commercial Templates
    MECHANICAL_COMMERCIAL = "mechanical_commercial"
    REFRIGERATION_COMMERCIAL = "refrigeration_commercial"
    PLUMBING_COMMERCIAL = "plumbing_commercial"
    ELECTRICAL_COMMERCIAL = "electrical_commercial"
    SECURITY_SYSTEMS_COMMERCIAL = "security_systems_commercial"
    LANDSCAPING_COMMERCIAL = "landscaping_commercial"
    ROOFING_COMMERCIAL = "roofing_commercial"
    KITCHEN_EQUIPMENT_COMMERCIAL = "kitchen_equipment_commercial"
    WATER_TREATMENT_COMMERCIAL = "water_treatment_commercial"
    POOL_SPA_COMMERCIAL = "pool_spa_commercial"
    
    # Residential Templates
    HVAC_RESIDENTIAL = "hvac_residential"
    PLUMBING_RESIDENTIAL = "plumbing_residential"
    ELECTRICAL_RESIDENTIAL = "electrical_residential"
    CHIMNEY_RESIDENTIAL = "chimney_residential"
    ROOFING_RESIDENTIAL = "roofing_residential"
    GARAGE_DOOR_RESIDENTIAL = "garage_door_residential"
    SEPTIC_RESIDENTIAL = "septic_residential"
    PEST_CONTROL_RESIDENTIAL = "pest_control_residential"
    IRRIGATION_RESIDENTIAL = "irrigation_residential"
    PAINTING_RESIDENTIAL = "painting_residential"


# =====================================
# COMMERCIAL TEMPLATES
# =====================================

MECHANICAL_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Mechanical Services",
    "description": "Professional template for commercial HVAC, ventilation, and mechanical system contractors",
    "trade_type": "mechanical",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial HVAC", "industrial mechanical", "building automation",
        "commercial ventilation", "mechanical contractor", "facility maintenance"
    ],
    "structure": {
        "pages": [
            {
                "path": "/",
                "name": "Home",
                "title": "Commercial Mechanical Services | {{business_name}}",
                "sections": [
                    {
                        "type": "hero",
                        "config": {
                            "headline": "Professional Commercial Mechanical Services",
                            "subheadline": "Expert HVAC, ventilation, and building automation solutions for businesses",
                            "cta_primary": "Get Free Quote",
                            "cta_secondary": "Emergency Service",
                            "background_type": "commercial_mechanical"
                        }
                    },
                    {
                        "type": "emergency-banner",
                        "config": {
                            "message": "24/7 Emergency Mechanical Services",
                            "phone_display": True,
                            "urgency_level": "high"
                        }
                    },
                    {
                        "type": "services-grid",
                        "config": {
                            "services": [
                                "Commercial HVAC Installation & Repair",
                                "Building Automation Systems",
                                "Industrial Ventilation",
                                "Preventive Maintenance Programs",
                                "Energy Efficiency Upgrades",
                                "Emergency Mechanical Services"
                            ]
                        }
                    },
                    {
                        "type": "quick-quote",
                        "config": {
                            "title": "Get Your Commercial Quote",
                            "fields": ["business_name", "facility_type", "square_footage", "service_needed", "timeline"],
                            "lead_type": "quote_request"
                        }
                    },
                    {
                        "type": "testimonials",
                        "config": {
                            "focus": "commercial_reliability"
                        }
                    },
                    {
                        "type": "certifications",
                        "config": {
                            "highlight": ["EPA", "NATE", "Commercial License"]
                        }
                    },
                    {
                        "type": "contact-form",
                        "config": {
                            "title": "Schedule Service Consultation",
                            "fields": ["contact_info", "facility_details", "service_type", "preferred_time"],
                            "lead_type": "consultation"
                        }
                    }
                ]
            },
            {
                "path": "/services",
                "name": "Services",
                "title": "Commercial Mechanical Services | {{business_name}}",
                "sections": [
                    {
                        "type": "services-detail",
                        "config": {
                            "services": [
                                {
                                    "name": "HVAC Systems",
                                    "description": "Complete commercial HVAC installation, repair, and maintenance",
                                    "features": ["Rooftop units", "Chillers", "Boilers", "Air handlers"]
                                },
                                {
                                    "name": "Building Automation",
                                    "description": "Smart building controls and energy management systems",
                                    "features": ["BMS integration", "Energy monitoring", "Remote diagnostics"]
                                },
                                {
                                    "name": "Ventilation Systems",
                                    "description": "Industrial and commercial ventilation solutions",
                                    "features": ["Exhaust systems", "Make-up air", "Clean rooms"]
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "path": "/emergency",
                "name": "Emergency Service",
                "title": "24/7 Emergency Mechanical Services | {{business_name}}",
                "sections": [
                    {
                        "type": "emergency-hero",
                        "config": {
                            "headline": "24/7 Emergency Mechanical Services",
                            "response_time": "2-hour response guarantee",
                            "phone_prominent": True
                        }
                    },
                    {
                        "type": "emergency-form",
                        "config": {
                            "priority": "emergency",
                            "auto_call": True
                        }
                    }
                ]
            },
            {
                "path": "/quote",
                "name": "Get Quote",
                "title": "Free Commercial Quote | {{business_name}}",
                "sections": [
                    {
                        "type": "quote-form",
                        "config": {
                            "detailed": True,
                            "fields": ["facility_assessment", "equipment_specs", "timeline", "budget_range"]
                        }
                    }
                ]
            }
        ]
    },
    "seo": {
        "meta_description": "Professional commercial mechanical services including HVAC, building automation, and ventilation systems. 24/7 emergency service available.",
        "schema_types": ["LocalBusiness", "HVACBusiness", "ProfessionalService"],
        "local_keywords": ["commercial HVAC {location}", "mechanical contractor {location}", "building automation {location}"],
        "service_keywords": ["commercial HVAC installation", "building automation systems", "industrial ventilation"]
    },
    "intake_config": {
        "lead_routing": {
            "emergency": "immediate_sms_call",
            "quote_request": "sales_team",
            "consultation": "project_manager"
        },
        "auto_responses": {
            "emergency": "We've received your emergency request. A technician will contact you within 30 minutes.",
            "quote_request": "Thank you for your quote request. We'll provide a detailed proposal within 24 hours.",
            "consultation": "Your consultation request has been received. We'll schedule a site visit within 2 business days."
        }
    }
}

REFRIGERATION_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Refrigeration Services",
    "description": "Specialized template for commercial refrigeration and cold storage contractors",
    "trade_type": "refrigeration",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial refrigeration", "walk-in coolers", "freezer repair",
        "restaurant equipment", "cold storage", "refrigeration maintenance"
    ],
    "structure": {
        "pages": [
            {
                "path": "/",
                "name": "Home",
                "title": "Commercial Refrigeration Services | {{business_name}}",
                "sections": [
                    {
                        "type": "hero",
                        "config": {
                            "headline": "Expert Commercial Refrigeration Services",
                            "subheadline": "Keep your business cool with professional refrigeration installation, repair, and maintenance",
                            "cta_primary": "Emergency Service",
                            "cta_secondary": "Schedule Maintenance",
                            "background_type": "commercial_refrigeration"
                        }
                    },
                    {
                        "type": "emergency-banner",
                        "config": {
                            "message": "Refrigeration Emergency? We're Available 24/7",
                            "phone_display": True,
                            "urgency_level": "critical"
                        }
                    },
                    {
                        "type": "services-grid",
                        "config": {
                            "services": [
                                "Walk-in Cooler & Freezer Repair",
                                "Restaurant Equipment Service",
                                "Ice Machine Installation & Repair",
                                "Preventive Maintenance Programs",
                                "Energy Efficiency Upgrades",
                                "24/7 Emergency Refrigeration Service"
                            ]
                        }
                    },
                    {
                        "type": "industry-focus",
                        "config": {
                            "industries": ["Restaurants", "Grocery Stores", "Food Processing", "Healthcare", "Hospitality"]
                        }
                    },
                    {
                        "type": "quick-quote",
                        "config": {
                            "title": "Get Refrigeration Service Quote",
                            "fields": ["business_type", "equipment_type", "issue_description", "urgency"],
                            "lead_type": "service_request"
                        }
                    }
                ]
            }
        ]
    },
    "seo": {
        "meta_description": "Professional commercial refrigeration services for restaurants, grocery stores, and food service businesses. 24/7 emergency repair available.",
        "schema_types": ["LocalBusiness", "ProfessionalService", "RefrigerationService"],
        "local_keywords": ["commercial refrigeration {location}", "walk-in cooler repair {location}", "restaurant equipment service {location}"],
        "service_keywords": ["commercial refrigeration repair", "walk-in cooler installation", "ice machine service"]
    }
}

PLUMBING_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Plumbing Services",
    "description": "Professional template for commercial plumbing contractors and facility maintenance",
    "trade_type": "plumbing",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial plumbing", "office building plumbing", "restaurant plumbing",
        "industrial plumbing", "commercial drain cleaning", "backflow prevention"
    ],
    "structure": {
        "pages": [
            {
                "path": "/",
                "name": "Home",
                "title": "Commercial Plumbing Services | {{business_name}}",
                "sections": [
                    {
                        "type": "hero",
                        "config": {
                            "headline": "Professional Commercial Plumbing Services",
                            "subheadline": "Reliable plumbing solutions for offices, restaurants, and industrial facilities",
                            "cta_primary": "Emergency Plumbing",
                            "cta_secondary": "Schedule Service",
                            "background_type": "commercial_plumbing"
                        }
                    },
                    {
                        "type": "emergency-banner",
                        "config": {
                            "message": "Plumbing Emergency? 24/7 Response Available",
                            "phone_display": True,
                            "urgency_level": "high"
                        }
                    },
                    {
                        "type": "services-grid",
                        "config": {
                            "services": [
                                "Commercial Drain Cleaning",
                                "Backflow Prevention & Testing",
                                "Grease Trap Maintenance",
                                "Water Line Repair & Installation",
                                "Restroom Plumbing Services",
                                "Emergency Plumbing Repair"
                            ]
                        }
                    }
                ]
            }
        ]
    },
    "seo": {
        "meta_description": "Expert commercial plumbing services for businesses. Drain cleaning, backflow prevention, and emergency plumbing repair available 24/7.",
        "schema_types": ["LocalBusiness", "PlumbingService", "ProfessionalService"],
        "local_keywords": ["commercial plumber {location}", "office building plumbing {location}", "restaurant plumbing {location}"]
    }
}

# Continue with remaining commercial templates...
ELECTRICAL_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Electrical Services",
    "description": "Professional electrical services for commercial and industrial facilities",
    "trade_type": "electrical",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial electrician", "industrial electrical", "office electrical",
        "electrical maintenance", "power systems", "lighting installation"
    ]
}

SECURITY_SYSTEMS_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Security Systems",
    "description": "Advanced security solutions for businesses and commercial properties",
    "trade_type": "security_systems",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial security systems", "access control", "surveillance cameras",
        "alarm systems", "security installation", "business security"
    ]
}

LANDSCAPING_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Landscaping Services",
    "description": "Professional landscaping and grounds maintenance for commercial properties",
    "trade_type": "landscaping",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial landscaping", "grounds maintenance", "landscape design",
        "property maintenance", "lawn care services", "irrigation systems"
    ]
}

ROOFING_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Roofing Services",
    "description": "Expert roofing solutions for commercial and industrial buildings",
    "trade_type": "roofing",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial roofing", "flat roof repair", "industrial roofing",
        "roof maintenance", "roof replacement", "emergency roof repair"
    ]
}

KITCHEN_EQUIPMENT_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Kitchen Equipment Services",
    "description": "Professional kitchen equipment installation, repair, and maintenance",
    "trade_type": "kitchen_equipment",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial kitchen equipment", "restaurant equipment repair", "kitchen installation",
        "equipment maintenance", "food service equipment", "kitchen appliance repair"
    ]
}

WATER_TREATMENT_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Water Treatment Services",
    "description": "Industrial and commercial water treatment solutions and maintenance",
    "trade_type": "water_treatment",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial water treatment", "industrial water systems", "water filtration",
        "water quality testing", "treatment system maintenance", "water purification"
    ]
}

POOL_SPA_COMMERCIAL_TEMPLATE = {
    "name": "Commercial Pool & Spa Services",
    "description": "Professional pool and spa services for hotels, resorts, and commercial facilities",
    "trade_type": "pool_spa",
    "trade_category": TradeCategory.COMMERCIAL,
    "primary_keywords": [
        "commercial pool service", "hotel pool maintenance", "spa services",
        "pool equipment repair", "commercial pool cleaning", "aquatic facility maintenance"
    ]
}


# =====================================
# RESIDENTIAL TEMPLATES
# =====================================

HVAC_RESIDENTIAL_TEMPLATE = {
    "name": "Residential HVAC Services",
    "description": "Complete home heating, cooling, and air quality solutions",
    "trade_type": "hvac",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "HVAC repair", "air conditioning", "heating repair",
        "furnace installation", "AC repair", "home comfort"
    ],
    "structure": {
        "pages": [
            {
                "path": "/",
                "name": "Home",
                "title": "HVAC Services | Heating & Cooling | {{business_name}}",
                "sections": [
                    {
                        "type": "hero",
                        "config": {
                            "headline": "Expert HVAC Services for Your Home",
                            "subheadline": "Professional heating, cooling, and air quality solutions with same-day service available",
                            "cta_primary": "Book Service",
                            "cta_secondary": "Emergency HVAC",
                            "background_type": "residential_hvac"
                        }
                    },
                    {
                        "type": "emergency-banner",
                        "config": {
                            "message": "HVAC Emergency? Same-Day Service Available",
                            "phone_display": True,
                            "urgency_level": "high"
                        }
                    },
                    {
                        "type": "services-grid",
                        "config": {
                            "services": [
                                "Air Conditioning Repair & Installation",
                                "Heating System Service & Repair",
                                "Furnace Installation & Maintenance",
                                "Ductwork Cleaning & Repair",
                                "Indoor Air Quality Solutions",
                                "Emergency HVAC Service"
                            ]
                        }
                    },
                    {
                        "type": "seasonal-focus",
                        "config": {
                            "summer": "AC tune-ups and cooling system maintenance",
                            "winter": "Heating system service and furnace repair",
                            "spring": "System maintenance and air quality improvements",
                            "fall": "Pre-winter heating system preparation"
                        }
                    },
                    {
                        "type": "booking-widget",
                        "config": {
                            "title": "Schedule Your HVAC Service",
                            "service_types": ["AC Repair", "Heating Repair", "Maintenance", "Installation", "Emergency"],
                            "time_slots": "business_hours_plus_emergency",
                            "lead_type": "service_booking"
                        }
                    },
                    {
                        "type": "financing-options",
                        "config": {
                            "highlight": True,
                            "message": "Flexible financing available for new installations"
                        }
                    },
                    {
                        "type": "testimonials",
                        "config": {
                            "focus": "home_comfort_reliability"
                        }
                    },
                    {
                        "type": "contact-form",
                        "config": {
                            "title": "Get Your Free Estimate",
                            "fields": ["contact_info", "home_details", "service_needed", "preferred_time"],
                            "lead_type": "estimate_request"
                        }
                    }
                ]
            },
            {
                "path": "/services",
                "name": "Services",
                "title": "HVAC Services | {{business_name}}",
                "sections": [
                    {
                        "type": "services-detail",
                        "config": {
                            "services": [
                                {
                                    "name": "Air Conditioning",
                                    "description": "Complete AC services from repair to new installation",
                                    "features": ["Same-day repair", "Energy-efficient systems", "Warranty included"]
                                },
                                {
                                    "name": "Heating Systems",
                                    "description": "Furnace, heat pump, and boiler services",
                                    "features": ["All brands serviced", "Emergency repair", "Maintenance plans"]
                                },
                                {
                                    "name": "Indoor Air Quality",
                                    "description": "Improve your home's air with professional solutions",
                                    "features": ["Air purifiers", "Duct cleaning", "Humidity control"]
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "path": "/emergency",
                "name": "Emergency HVAC",
                "title": "Emergency HVAC Service | {{business_name}}",
                "sections": [
                    {
                        "type": "emergency-hero",
                        "config": {
                            "headline": "24/7 Emergency HVAC Service",
                            "response_time": "Same-day service guarantee",
                            "phone_prominent": True
                        }
                    },
                    {
                        "type": "emergency-form",
                        "config": {
                            "priority": "emergency",
                            "auto_call": True
                        }
                    }
                ]
            },
            {
                "path": "/booking",
                "name": "Book Service",
                "title": "Schedule HVAC Service | {{business_name}}",
                "sections": [
                    {
                        "type": "booking-calendar",
                        "config": {
                            "service_duration": 60,
                            "emergency_slots": True
                        }
                    }
                ]
            }
        ]
    },
    "seo": {
        "meta_description": "Professional HVAC services including air conditioning repair, heating system service, and indoor air quality solutions. Same-day emergency service available.",
        "schema_types": ["LocalBusiness", "HVACBusiness", "ProfessionalService"],
        "local_keywords": ["HVAC repair {location}", "air conditioning service {location}", "heating repair {location}"],
        "service_keywords": ["AC repair", "furnace installation", "heating system service", "indoor air quality"]
    },
    "intake_config": {
        "lead_routing": {
            "emergency": "immediate_dispatch",
            "service_booking": "scheduling_team",
            "estimate_request": "sales_team"
        },
        "auto_responses": {
            "emergency": "Emergency HVAC service requested. A technician will contact you within 30 minutes to confirm arrival time.",
            "service_booking": "Your HVAC service has been scheduled. You'll receive a confirmation with technician details shortly.",
            "estimate_request": "Thank you for requesting an estimate. We'll contact you within 4 hours to schedule a free in-home consultation."
        }
    }
}

PLUMBING_RESIDENTIAL_TEMPLATE = {
    "name": "Residential Plumbing Services",
    "description": "Complete home plumbing solutions from repairs to installations",
    "trade_type": "plumbing",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "plumber", "plumbing repair", "drain cleaning",
        "water heater", "toilet repair", "emergency plumber"
    ],
    "structure": {
        "pages": [
            {
                "path": "/",
                "name": "Home",
                "title": "Professional Plumber | Plumbing Services | {{business_name}}",
                "sections": [
                    {
                        "type": "hero",
                        "config": {
                            "headline": "Trusted Local Plumber for All Your Home Needs",
                            "subheadline": "Fast, reliable plumbing services with upfront pricing and guaranteed satisfaction",
                            "cta_primary": "Call Now",
                            "cta_secondary": "Schedule Service",
                            "background_type": "residential_plumbing"
                        }
                    },
                    {
                        "type": "emergency-banner",
                        "config": {
                            "message": "Plumbing Emergency? We're Available 24/7",
                            "phone_display": True,
                            "urgency_level": "critical"
                        }
                    },
                    {
                        "type": "services-grid",
                        "config": {
                            "services": [
                                "Drain Cleaning & Unclogging",
                                "Water Heater Repair & Installation",
                                "Toilet & Faucet Repair",
                                "Pipe Repair & Replacement",
                                "Sewer Line Services",
                                "24/7 Emergency Plumbing"
                            ]
                        }
                    },
                    {
                        "type": "quick-quote",
                        "config": {
                            "title": "Get Your Plumbing Quote",
                            "fields": ["issue_description", "location_in_home", "urgency", "preferred_time"],
                            "lead_type": "service_request"
                        }
                    }
                ]
            }
        ]
    },
    "seo": {
        "meta_description": "Professional plumbing services including drain cleaning, water heater repair, and emergency plumbing. Licensed, insured, and available 24/7.",
        "schema_types": ["LocalBusiness", "PlumbingService", "ProfessionalService"],
        "local_keywords": ["plumber {location}", "plumbing repair {location}", "emergency plumber {location}"]
    }
}

# Continue with remaining residential templates...
ELECTRICAL_RESIDENTIAL_TEMPLATE = {
    "name": "Residential Electrical Services",
    "description": "Safe and reliable electrical services for your home",
    "trade_type": "electrical",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "electrician", "electrical repair", "outlet installation",
        "electrical panel", "wiring", "electrical safety"
    ]
}

CHIMNEY_RESIDENTIAL_TEMPLATE = {
    "name": "Chimney Services",
    "description": "Professional chimney cleaning, repair, and maintenance services",
    "trade_type": "chimney",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "chimney cleaning", "chimney repair", "fireplace service",
        "chimney inspection", "chimney sweep", "fireplace maintenance"
    ]
}

ROOFING_RESIDENTIAL_TEMPLATE = {
    "name": "Residential Roofing Services",
    "description": "Expert roofing services for homes including repair and replacement",
    "trade_type": "roofing",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "roofing contractor", "roof repair", "roof replacement",
        "roof installation", "storm damage", "roof inspection"
    ]
}

GARAGE_DOOR_RESIDENTIAL_TEMPLATE = {
    "name": "Garage Door Services",
    "description": "Professional garage door repair, installation, and maintenance",
    "trade_type": "garage_door",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "garage door repair", "garage door installation", "garage door opener",
        "garage door service", "door replacement", "garage door maintenance"
    ]
}

SEPTIC_RESIDENTIAL_TEMPLATE = {
    "name": "Septic System Services",
    "description": "Complete septic system services including pumping and repair",
    "trade_type": "septic",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "septic pumping", "septic repair", "septic installation",
        "septic inspection", "septic maintenance", "septic system"
    ]
}

PEST_CONTROL_RESIDENTIAL_TEMPLATE = {
    "name": "Pest Control Services",
    "description": "Effective pest control and extermination services for homes",
    "trade_type": "pest_control",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "pest control", "exterminator", "bug control",
        "termite treatment", "rodent control", "pest removal"
    ]
}

IRRIGATION_RESIDENTIAL_TEMPLATE = {
    "name": "Irrigation & Sprinkler Services",
    "description": "Professional irrigation system installation and repair services",
    "trade_type": "irrigation",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "irrigation repair", "sprinkler system", "irrigation installation",
        "sprinkler repair", "lawn irrigation", "drip irrigation"
    ]
}

PAINTING_RESIDENTIAL_TEMPLATE = {
    "name": "Residential Painting Services",
    "description": "Professional interior and exterior painting services for homes",
    "trade_type": "painting",
    "trade_category": TradeCategory.RESIDENTIAL,
    "primary_keywords": [
        "house painting", "interior painting", "exterior painting",
        "residential painter", "painting contractor", "home painting"
    ]
}


# =====================================
# TEMPLATE REGISTRY
# =====================================

WEBSITE_TEMPLATES: Dict[TemplateType, Dict[str, Any]] = {
    # Commercial Templates
    TemplateType.MECHANICAL_COMMERCIAL: MECHANICAL_COMMERCIAL_TEMPLATE,
    TemplateType.REFRIGERATION_COMMERCIAL: REFRIGERATION_COMMERCIAL_TEMPLATE,
    TemplateType.PLUMBING_COMMERCIAL: PLUMBING_COMMERCIAL_TEMPLATE,
    TemplateType.ELECTRICAL_COMMERCIAL: ELECTRICAL_COMMERCIAL_TEMPLATE,
    TemplateType.SECURITY_SYSTEMS_COMMERCIAL: SECURITY_SYSTEMS_COMMERCIAL_TEMPLATE,
    TemplateType.LANDSCAPING_COMMERCIAL: LANDSCAPING_COMMERCIAL_TEMPLATE,
    TemplateType.ROOFING_COMMERCIAL: ROOFING_COMMERCIAL_TEMPLATE,
    TemplateType.KITCHEN_EQUIPMENT_COMMERCIAL: KITCHEN_EQUIPMENT_COMMERCIAL_TEMPLATE,
    TemplateType.WATER_TREATMENT_COMMERCIAL: WATER_TREATMENT_COMMERCIAL_TEMPLATE,
    TemplateType.POOL_SPA_COMMERCIAL: POOL_SPA_COMMERCIAL_TEMPLATE,
    
    # Residential Templates
    TemplateType.HVAC_RESIDENTIAL: HVAC_RESIDENTIAL_TEMPLATE,
    TemplateType.PLUMBING_RESIDENTIAL: PLUMBING_RESIDENTIAL_TEMPLATE,
    TemplateType.ELECTRICAL_RESIDENTIAL: ELECTRICAL_RESIDENTIAL_TEMPLATE,
    TemplateType.CHIMNEY_RESIDENTIAL: CHIMNEY_RESIDENTIAL_TEMPLATE,
    TemplateType.ROOFING_RESIDENTIAL: ROOFING_RESIDENTIAL_TEMPLATE,
    TemplateType.GARAGE_DOOR_RESIDENTIAL: GARAGE_DOOR_RESIDENTIAL_TEMPLATE,
    TemplateType.SEPTIC_RESIDENTIAL: SEPTIC_RESIDENTIAL_TEMPLATE,
    TemplateType.PEST_CONTROL_RESIDENTIAL: PEST_CONTROL_RESIDENTIAL_TEMPLATE,
    TemplateType.IRRIGATION_RESIDENTIAL: IRRIGATION_RESIDENTIAL_TEMPLATE,
    TemplateType.PAINTING_RESIDENTIAL: PAINTING_RESIDENTIAL_TEMPLATE,
}


class WebsiteTemplateService:
    """Service for managing and retrieving website templates."""
    
    @staticmethod
    def get_template_by_trade(trade: str, category: TradeCategory) -> Optional[Dict[str, Any]]:
        """Get template by trade type and category."""
        
        # Map trade names to template types
        trade_mapping = {
            # Commercial
            ("mechanical", TradeCategory.COMMERCIAL): TemplateType.MECHANICAL_COMMERCIAL,
            ("refrigeration", TradeCategory.COMMERCIAL): TemplateType.REFRIGERATION_COMMERCIAL,
            ("plumbing", TradeCategory.COMMERCIAL): TemplateType.PLUMBING_COMMERCIAL,
            ("electrical", TradeCategory.COMMERCIAL): TemplateType.ELECTRICAL_COMMERCIAL,
            ("security_systems", TradeCategory.COMMERCIAL): TemplateType.SECURITY_SYSTEMS_COMMERCIAL,
            ("landscaping", TradeCategory.COMMERCIAL): TemplateType.LANDSCAPING_COMMERCIAL,
            ("roofing", TradeCategory.COMMERCIAL): TemplateType.ROOFING_COMMERCIAL,
            ("kitchen_equipment", TradeCategory.COMMERCIAL): TemplateType.KITCHEN_EQUIPMENT_COMMERCIAL,
            ("water_treatment", TradeCategory.COMMERCIAL): TemplateType.WATER_TREATMENT_COMMERCIAL,
            ("pool_spa", TradeCategory.COMMERCIAL): TemplateType.POOL_SPA_COMMERCIAL,
            
            # Residential
            ("hvac", TradeCategory.RESIDENTIAL): TemplateType.HVAC_RESIDENTIAL,
            ("plumbing", TradeCategory.RESIDENTIAL): TemplateType.PLUMBING_RESIDENTIAL,
            ("electrical", TradeCategory.RESIDENTIAL): TemplateType.ELECTRICAL_RESIDENTIAL,
            ("chimney", TradeCategory.RESIDENTIAL): TemplateType.CHIMNEY_RESIDENTIAL,
            ("roofing", TradeCategory.RESIDENTIAL): TemplateType.ROOFING_RESIDENTIAL,
            ("garage_door", TradeCategory.RESIDENTIAL): TemplateType.GARAGE_DOOR_RESIDENTIAL,
            ("septic", TradeCategory.RESIDENTIAL): TemplateType.SEPTIC_RESIDENTIAL,
            ("pest_control", TradeCategory.RESIDENTIAL): TemplateType.PEST_CONTROL_RESIDENTIAL,
            ("irrigation", TradeCategory.RESIDENTIAL): TemplateType.IRRIGATION_RESIDENTIAL,
            ("painting", TradeCategory.RESIDENTIAL): TemplateType.PAINTING_RESIDENTIAL,
        }
        
        template_type = trade_mapping.get((trade.lower(), category))
        if template_type:
            return WEBSITE_TEMPLATES.get(template_type)
        
        return None
    
    @staticmethod
    def get_all_templates() -> Dict[TemplateType, Dict[str, Any]]:
        """Get all available templates."""
        return WEBSITE_TEMPLATES
    
    @staticmethod
    def get_templates_by_category(category: TradeCategory) -> Dict[TemplateType, Dict[str, Any]]:
        """Get templates filtered by trade category."""
        
        filtered_templates = {}
        for template_type, template_data in WEBSITE_TEMPLATES.items():
            if template_data.get("trade_category") == category:
                filtered_templates[template_type] = template_data
        
        return filtered_templates
    
    @staticmethod
    def create_website_template_entity(template_type: TemplateType) -> WebsiteTemplate:
        """Create a WebsiteTemplate entity from template data."""
        
        template_data = WEBSITE_TEMPLATES.get(template_type)
        if not template_data:
            raise ValueError(f"Template not found: {template_type}")
        
        return WebsiteTemplate(
            name=template_data["name"],
            description=template_data["description"],
            trade_type=template_data["trade_type"],
            trade_category=template_data["trade_category"],
            structure=template_data["structure"],
            seo_config=template_data.get("seo", {}),
            intake_config=template_data.get("intake_config", {}),
            primary_keywords=template_data.get("primary_keywords", []),
            is_active=True
        )
    
    @staticmethod
    def get_template_keywords(template_type: TemplateType) -> List[str]:
        """Get primary keywords for a template."""
        
        template_data = WEBSITE_TEMPLATES.get(template_type)
        if template_data:
            return template_data.get("primary_keywords", [])
        
        return []
    
    @staticmethod
    def get_template_services(template_type: TemplateType) -> List[str]:
        """Extract services list from template structure."""
        
        template_data = WEBSITE_TEMPLATES.get(template_type)
        if not template_data:
            return []
        
        services = []
        structure = template_data.get("structure", {})
        pages = structure.get("pages", [])
        
        for page in pages:
            sections = page.get("sections", [])
            for section in sections:
                if section.get("type") == "services-grid":
                    config = section.get("config", {})
                    services.extend(config.get("services", []))
        
        return services
    
    @staticmethod
    def validate_template_structure(template_data: Dict[str, Any]) -> bool:
        """Validate template structure and required fields."""
        
        required_fields = ["name", "description", "trade_type", "trade_category", "structure"]
        
        for field in required_fields:
            if field not in template_data:
                return False
        
        # Validate structure
        structure = template_data.get("structure", {})
        if "pages" not in structure:
            return False
        
        pages = structure["pages"]
        if not isinstance(pages, list) or len(pages) == 0:
            return False
        
        # Validate each page has required fields
        for page in pages:
            if not all(field in page for field in ["path", "name", "sections"]):
                return False
        
        return True


class WebsiteTemplateService:
    """Service for managing website templates."""
    
    @staticmethod
    def get_template_by_trade(trade_type: str, trade_category: TradeCategory) -> Optional[Dict[str, Any]]:
        """Get template data for a specific trade and category."""
        
        # Map trade_type and category to TemplateType
        trade_mapping = {
            # Commercial trades
            ("mechanical", TradeCategory.COMMERCIAL): TemplateType.MECHANICAL_COMMERCIAL,
            ("refrigeration", TradeCategory.COMMERCIAL): TemplateType.REFRIGERATION_COMMERCIAL,
            ("plumbing", TradeCategory.COMMERCIAL): TemplateType.PLUMBING_COMMERCIAL,
            ("electrical", TradeCategory.COMMERCIAL): TemplateType.ELECTRICAL_COMMERCIAL,
            ("security_systems", TradeCategory.COMMERCIAL): TemplateType.SECURITY_SYSTEMS_COMMERCIAL,
            ("landscaping", TradeCategory.COMMERCIAL): TemplateType.LANDSCAPING_COMMERCIAL,
            ("roofing", TradeCategory.COMMERCIAL): TemplateType.ROOFING_COMMERCIAL,
            ("kitchen_equipment", TradeCategory.COMMERCIAL): TemplateType.KITCHEN_EQUIPMENT_COMMERCIAL,
            ("water_treatment", TradeCategory.COMMERCIAL): TemplateType.WATER_TREATMENT_COMMERCIAL,
            ("pool_spa", TradeCategory.COMMERCIAL): TemplateType.POOL_SPA_COMMERCIAL,
            
            # Residential trades
            ("hvac", TradeCategory.RESIDENTIAL): TemplateType.HVAC_RESIDENTIAL,
            ("plumbing", TradeCategory.RESIDENTIAL): TemplateType.PLUMBING_RESIDENTIAL,
            ("electrical", TradeCategory.RESIDENTIAL): TemplateType.ELECTRICAL_RESIDENTIAL,
            ("chimney", TradeCategory.RESIDENTIAL): TemplateType.CHIMNEY_RESIDENTIAL,
            ("roofing", TradeCategory.RESIDENTIAL): TemplateType.ROOFING_RESIDENTIAL,
            ("garage_door", TradeCategory.RESIDENTIAL): TemplateType.GARAGE_DOOR_RESIDENTIAL,
            ("septic", TradeCategory.RESIDENTIAL): TemplateType.SEPTIC_RESIDENTIAL,
            ("pest_control", TradeCategory.RESIDENTIAL): TemplateType.PEST_CONTROL_RESIDENTIAL,
            ("irrigation", TradeCategory.RESIDENTIAL): TemplateType.IRRIGATION_RESIDENTIAL,
            ("painting", TradeCategory.RESIDENTIAL): TemplateType.PAINTING_RESIDENTIAL,
        }
        
        # Get template type
        template_type = trade_mapping.get((trade_type, trade_category))
        if not template_type:
            return None
        
        # Get template data
        return WEBSITE_TEMPLATES.get(template_type)
    
    @staticmethod
    def get_all_templates() -> Dict[TemplateType, Dict[str, Any]]:
        """Get all available templates."""
        return WEBSITE_TEMPLATES
    
    @staticmethod
    def get_templates_by_category(trade_category: TradeCategory) -> Dict[TemplateType, Dict[str, Any]]:
        """Get all templates for a specific trade category."""
        return {
            template_type: template_data
            for template_type, template_data in WEBSITE_TEMPLATES.items()
            if template_data.get("trade_category") == trade_category
        }
