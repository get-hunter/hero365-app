"""
Fixed-Price Installation Templates for Hero365

Optimized for home service contractors who need fast, competitive quotes.
Based on analysis of target user needs: 80% fixed pricing, 20% time-based.
"""

from typing import Dict, List, Optional
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
import uuid


class InstallationType(str, Enum):
    """Types of installations"""
    FIXED = "fixed"           # Standard jobs with predictable scope
    HOURLY = "hourly"         # Complex jobs with variable scope
    DIAGNOSTIC = "diagnostic" # Troubleshooting and assessment


class ComplexityLevel(str, Enum):
    """Installation complexity levels"""
    SIMPLE = "simple"       # Easy access, standard conditions
    STANDARD = "standard"   # Normal installation conditions  
    COMPLEX = "complex"     # Difficult access, modifications required
    CUSTOM = "custom"       # Unique requirements, engineering needed


class TradeType(str, Enum):
    """Home service trade types"""
    HVAC = "hvac"
    PLUMBING = "plumbing" 
    ELECTRICAL = "electrical"
    GENERAL = "general"


@dataclass
class InstallationTemplate:
    """Fixed-price installation template for common jobs"""
    
    id: str
    name: str
    description: str
    trade_type: TradeType
    installation_type: InstallationType
    
    # Pricing
    base_price: Decimal
    estimated_hours: Decimal
    hourly_equivalent: Decimal  # What this equals per hour
    
    # Smart adjustments
    complexity_adjustments: Dict[ComplexityLevel, Decimal]
    timing_adjustments: Dict[str, Decimal] 
    location_adjustments: Dict[str, Decimal]
    
    # Inclusions and requirements
    includes: List[str]
    requirements: List[str]
    materials_included: bool
    warranty_years: int
    
    # Business rules
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    requires_permit: bool = False
    requires_inspection: bool = False


# Standard HVAC Installation Templates
HVAC_TEMPLATES = {
    "water_heater_replace": InstallationTemplate(
        id="water_heater_replace",
        name="Water Heater Replacement",
        description="Standard water heater replacement (gas or electric)",
        trade_type=TradeType.HVAC,
        installation_type=InstallationType.FIXED,
        base_price=Decimal("250.00"),
        estimated_hours=Decimal("3.0"),
        hourly_equivalent=Decimal("83.33"),
        complexity_adjustments={
            ComplexityLevel.SIMPLE: Decimal("0.9"),    # -10% easy access
            ComplexityLevel.STANDARD: Decimal("1.0"),  # Base price
            ComplexityLevel.COMPLEX: Decimal("1.4"),   # +40% tight space/complications
            ComplexityLevel.CUSTOM: Decimal("1.8")     # +80% major modifications
        },
        timing_adjustments={
            "business_hours": Decimal("1.0"),
            "evening": Decimal("1.2"),
            "weekend": Decimal("1.5"), 
            "emergency": Decimal("2.0")
        },
        location_adjustments={
            "local": Decimal("1.0"),        # < 15 miles
            "regional": Decimal("1.15"),    # 15-30 miles
            "distant": Decimal("1.3")       # > 30 miles
        },
        includes=[
            "Remove old water heater",
            "Install new water heater", 
            "Connect gas/electric lines",
            "Connect water lines",
            "Test for leaks and proper operation",
            "Basic cleanup"
        ],
        requirements=[
            "Adequate clearance for installation",
            "Existing gas/electric connections compatible",
            "Proper venting in place (gas units)"
        ],
        materials_included=False,
        warranty_years=1,
        requires_permit=False,
        requires_inspection=True
    ),
    
    "hvac_system_install": InstallationTemplate(
        id="hvac_system_install",
        name="Complete HVAC System Installation",
        description="Full HVAC system installation with ductwork connections",
        trade_type=TradeType.HVAC,
        installation_type=InstallationType.FIXED,
        base_price=Decimal("1200.00"),
        estimated_hours=Decimal("8.0"),
        hourly_equivalent=Decimal("150.00"),
        complexity_adjustments={
            ComplexityLevel.SIMPLE: Decimal("0.85"),   # -15% existing ductwork good
            ComplexityLevel.STANDARD: Decimal("1.0"),  # Base price
            ComplexityLevel.COMPLEX: Decimal("1.6"),   # +60% major ductwork
            ComplexityLevel.CUSTOM: Decimal("2.2")     # +120% complete redesign
        },
        timing_adjustments={
            "business_hours": Decimal("1.0"),
            "evening": Decimal("1.3"),
            "weekend": Decimal("1.8"),
            "emergency": Decimal("2.5")
        },
        location_adjustments={
            "local": Decimal("1.0"),
            "regional": Decimal("1.2"), 
            "distant": Decimal("1.4")
        },
        includes=[
            "Remove old system",
            "Install new indoor and outdoor units",
            "Connect refrigerant lines", 
            "Connect ductwork",
            "Install thermostat",
            "Test and commission system",
            "Customer training"
        ],
        requirements=[
            "Electrical service adequate for new system",
            "Proper permits obtained",
            "Clear access to installation areas"
        ],
        materials_included=False,
        warranty_years=2,
        requires_permit=True,
        requires_inspection=True
    ),
    
    "thermostat_install": InstallationTemplate(
        id="thermostat_install",
        name="Thermostat Installation", 
        description="Standard or smart thermostat installation",
        trade_type=TradeType.HVAC,
        installation_type=InstallationType.FIXED,
        base_price=Decimal("125.00"),
        estimated_hours=Decimal("1.5"),
        hourly_equivalent=Decimal("83.33"),
        complexity_adjustments={
            ComplexityLevel.SIMPLE: Decimal("0.8"),    # -20% basic replacement
            ComplexityLevel.STANDARD: Decimal("1.0"),  # Base price
            ComplexityLevel.COMPLEX: Decimal("1.6"),   # +60% new wiring needed
            ComplexityLevel.CUSTOM: Decimal("2.0")     # +100% system integration
        },
        timing_adjustments={
            "business_hours": Decimal("1.0"),
            "evening": Decimal("1.2"),
            "weekend": Decimal("1.4"),
            "emergency": Decimal("1.8")
        },
        location_adjustments={
            "local": Decimal("1.0"),
            "regional": Decimal("1.1"),
            "distant": Decimal("1.2")
        },
        includes=[
            "Remove old thermostat",
            "Install new thermostat",
            "Program settings",
            "Test heating and cooling",
            "Customer training on operation"
        ],
        requirements=[
            "Compatible HVAC system",
            "Adequate wiring (24V for smart thermostats)"
        ],
        materials_included=True,
        warranty_years=1,
        requires_permit=False,
        requires_inspection=False
    ),
    
    "ac_repair_standard": InstallationTemplate(
        id="ac_repair_standard", 
        name="Standard AC Repair Service",
        description="Typical AC repair (non-diagnostic)",
        trade_type=TradeType.HVAC,
        installation_type=InstallationType.FIXED,
        base_price=Decimal("150.00"),
        estimated_hours=Decimal("2.0"),
        hourly_equivalent=Decimal("75.00"),
        complexity_adjustments={
            ComplexityLevel.SIMPLE: Decimal("0.9"),    # -10% simple fix
            ComplexityLevel.STANDARD: Decimal("1.0"),  # Base price  
            ComplexityLevel.COMPLEX: Decimal("1.5"),   # +50% multiple issues
            ComplexityLevel.CUSTOM: Decimal("2.0")     # +100% major repair
        },
        timing_adjustments={
            "business_hours": Decimal("1.0"),
            "evening": Decimal("1.3"),
            "weekend": Decimal("1.6"),
            "emergency": Decimal("2.2")
        },
        location_adjustments={
            "local": Decimal("1.0"),
            "regional": Decimal("1.15"),
            "distant": Decimal("1.3")
        },
        includes=[
            "Diagnose specific issue",
            "Repair or replace faulty component", 
            "Test system operation",
            "Clean and inspect related components"
        ],
        requirements=[
            "Problem identified (not general diagnostic)",
            "Standard repair parts available"
        ],
        materials_included=False,
        warranty_years=1,
        requires_permit=False,
        requires_inspection=False
    )
}

# Time-Based Service Templates (20% of jobs)
HOURLY_TEMPLATES = {
    "hvac_diagnostic": InstallationTemplate(
        id="hvac_diagnostic",
        name="HVAC System Diagnostic",
        description="Comprehensive troubleshooting and assessment",
        trade_type=TradeType.HVAC,
        installation_type=InstallationType.DIAGNOSTIC,
        base_price=Decimal("125.00"),  # Per hour
        estimated_hours=Decimal("1.0"), # Minimum charge
        hourly_equivalent=Decimal("125.00"),
        complexity_adjustments={
            ComplexityLevel.SIMPLE: Decimal("1.0"),    # Standard rate
            ComplexityLevel.STANDARD: Decimal("1.0"),  # Standard rate
            ComplexityLevel.COMPLEX: Decimal("1.2"),   # +20% complex systems
            ComplexityLevel.CUSTOM: Decimal("1.4")     # +40% specialty systems
        },
        timing_adjustments={
            "business_hours": Decimal("1.0"),
            "evening": Decimal("1.2"),
            "weekend": Decimal("1.5"),
            "emergency": Decimal("2.0")
        },
        location_adjustments={
            "local": Decimal("1.0"),
            "regional": Decimal("1.15"),
            "distant": Decimal("1.3")
        },
        includes=[
            "Complete system inspection",
            "Performance testing",
            "Detailed diagnosis report",
            "Repair recommendations with pricing"
        ],
        requirements=[
            "Access to all system components",
            "System operational for testing"
        ],
        materials_included=True,
        warranty_years=0,
        requires_permit=False,
        requires_inspection=False
    ),
    
    "custom_ductwork": InstallationTemplate(
        id="custom_ductwork",
        name="Custom Ductwork Installation",
        description="Custom ductwork design and installation", 
        trade_type=TradeType.HVAC,
        installation_type=InstallationType.HOURLY,
        base_price=Decimal("95.00"),   # Per hour
        estimated_hours=Decimal("4.0"), # Minimum estimate
        hourly_equivalent=Decimal("95.00"),
        complexity_adjustments={
            ComplexityLevel.SIMPLE: Decimal("1.0"),    # Standard rate
            ComplexityLevel.STANDARD: Decimal("1.0"),  # Standard rate
            ComplexityLevel.COMPLEX: Decimal("1.3"),   # +30% difficult access
            ComplexityLevel.CUSTOM: Decimal("1.6")     # +60% engineering required
        },
        timing_adjustments={
            "business_hours": Decimal("1.0"),
            "evening": Decimal("1.2"),
            "weekend": Decimal("1.4"),
            "emergency": Decimal("1.8")
        },
        location_adjustments={
            "local": Decimal("1.0"),
            "regional": Decimal("1.1"),
            "distant": Decimal("1.25")
        },
        includes=[
            "Design and layout",
            "Fabrication and installation",
            "Connection to existing system",
            "Testing and balancing"
        ],
        requirements=[
            "Detailed project scope",
            "Access for installation",
            "Materials and permits as needed"
        ],
        materials_included=False,
        warranty_years=2,
        requires_permit=True,
        requires_inspection=True
    )
}

# Plumbing Templates
PLUMBING_TEMPLATES = {
    "toilet_install": InstallationTemplate(
        id="toilet_install", 
        name="Toilet Installation",
        description="Standard toilet installation or replacement",
        trade_type=TradeType.PLUMBING,
        installation_type=InstallationType.FIXED,
        base_price=Decimal("200.00"),
        estimated_hours=Decimal("2.5"),
        hourly_equivalent=Decimal("80.00"),
        complexity_adjustments={
            ComplexityLevel.SIMPLE: Decimal("0.85"),   # -15% straight replacement
            ComplexityLevel.STANDARD: Decimal("1.0"),  # Base price
            ComplexityLevel.COMPLEX: Decimal("1.4"),   # +40% floor repair needed
            ComplexityLevel.CUSTOM: Decimal("1.8")     # +80% plumbing modifications
        },
        timing_adjustments={
            "business_hours": Decimal("1.0"),
            "evening": Decimal("1.25"),
            "weekend": Decimal("1.5"),
            "emergency": Decimal("2.0")
        },
        location_adjustments={
            "local": Decimal("1.0"),
            "regional": Decimal("1.1"),
            "distant": Decimal("1.25")
        },
        includes=[
            "Remove old toilet",
            "Install new wax ring and bolts",
            "Install new toilet", 
            "Connect water supply",
            "Test for leaks",
            "Caulk around base"
        ],
        requirements=[
            "Existing plumbing compatible",
            "Floor in good condition",
            "Standard toilet dimensions"
        ],
        materials_included=True,  # Wax ring, bolts, etc.
        warranty_years=1,
        requires_permit=False,
        requires_inspection=False
    )
}

# Master template registry
ALL_TEMPLATES = {
    **HVAC_TEMPLATES,
    **HOURLY_TEMPLATES, 
    **PLUMBING_TEMPLATES
}


def get_template_by_id(template_id: str) -> Optional[InstallationTemplate]:
    """Get installation template by ID"""
    return ALL_TEMPLATES.get(template_id)


def get_templates_by_trade(trade_type: TradeType) -> Dict[str, InstallationTemplate]:
    """Get all templates for a specific trade"""
    return {
        template_id: template 
        for template_id, template in ALL_TEMPLATES.items()
        if template.trade_type == trade_type
    }


def get_templates_by_type(installation_type: InstallationType) -> Dict[str, InstallationTemplate]:
    """Get all templates for a specific installation type"""
    return {
        template_id: template
        for template_id, template in ALL_TEMPLATES.items()
        if template.installation_type == installation_type
    }


def calculate_adjusted_price(
    template: InstallationTemplate,
    complexity: ComplexityLevel = ComplexityLevel.STANDARD,
    timing: str = "business_hours",
    location: str = "local",
    quantity: int = 1
) -> Decimal:
    """
    Calculate final price with all adjustments applied
    
    Args:
        template: Installation template
        complexity: Job complexity level
        timing: Time of service (business_hours, evening, weekend, emergency) 
        location: Service location (local, regional, distant)
        quantity: Number of units (for applicable jobs)
        
    Returns:
        Final adjusted price
    """
    base_price = template.base_price
    
    # Apply adjustments
    complexity_mult = template.complexity_adjustments.get(complexity, Decimal("1.0"))
    timing_mult = template.timing_adjustments.get(timing, Decimal("1.0"))
    location_mult = template.location_adjustments.get(location, Decimal("1.0"))
    
    # Calculate adjusted price
    adjusted_price = base_price * complexity_mult * timing_mult * location_mult * quantity
    
    # Apply min/max limits if specified
    if template.min_price and adjusted_price < template.min_price:
        adjusted_price = template.min_price
    if template.max_price and adjusted_price > template.max_price:
        adjusted_price = template.max_price
        
    return adjusted_price.quantize(Decimal('0.01'))
