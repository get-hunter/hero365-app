"""
Default Services Mapping for Trades
Provides comprehensive default service lists for each trade category
"""

from typing import Dict, List, Set
from app.domain.entities.business import CommercialTrade, ResidentialTrade, MarketFocus


class DefaultServicesMapping:
    """
    Maps trades to their default services for better onboarding experience.
    Users get pre-selected services based on their primary/secondary trades,
    then can unselect what they don't offer.
    """
    
    # Commercial trade default services
    COMMERCIAL_SERVICES: Dict[CommercialTrade, List[str]] = {
        CommercialTrade.MECHANICAL: [
            "hvac_installation",
            "hvac_repair", 
            "hvac_maintenance",
            "boiler_service",
            "chiller_service",
            "ventilation_systems",
            "air_quality_systems",
            "energy_audits"
        ],
        CommercialTrade.REFRIGERATION: [
            "commercial_refrigeration",
            "walk_in_coolers",
            "freezer_repair",
            "ice_machine_service",
            "refrigeration_maintenance",
            "temperature_monitoring",
            "refrigerant_recovery",
            "energy_efficiency_upgrades"
        ],
        CommercialTrade.PLUMBING: [
            "commercial_plumbing",
            "pipe_installation",
            "drain_cleaning",
            "water_heater_commercial",
            "backflow_prevention",
            "grease_trap_service",
            "hydro_jetting",
            "plumbing_maintenance"
        ],
        CommercialTrade.ELECTRICAL: [
            "electrical_installation",
            "electrical_repair",
            "panel_upgrades",
            "lighting_systems",
            "power_distribution",
            "electrical_maintenance",
            "code_compliance",
            "energy_management"
        ],
        CommercialTrade.SECURITY_SYSTEMS: [
            "security_cameras",
            "access_control",
            "alarm_systems",
            "fire_safety_systems",
            "intercom_systems",
            "security_monitoring",
            "system_maintenance",
            "security_consulting"
        ],
        CommercialTrade.LANDSCAPING: [
            "commercial_landscaping",
            "lawn_maintenance",
            "irrigation_systems",
            "tree_service",
            "landscape_design",
            "snow_removal",
            "grounds_maintenance",
            "pest_control_outdoor"
        ],
        CommercialTrade.ROOFING: [
            "commercial_roofing",
            "roof_repair",
            "roof_maintenance",
            "roof_inspection",
            "gutter_systems",
            "waterproofing",
            "roof_coatings",
            "emergency_repairs"
        ],
        CommercialTrade.KITCHEN_EQUIPMENT: [
            "kitchen_equipment_repair",
            "equipment_installation",
            "equipment_maintenance",
            "hood_cleaning",
            "equipment_consulting",
            "warranty_service",
            "equipment_upgrades",
            "safety_inspections"
        ],
        CommercialTrade.WATER_TREATMENT: [
            "water_filtration",
            "water_softening",
            "water_testing",
            "system_maintenance",
            "reverse_osmosis",
            "water_quality_consulting",
            "equipment_installation",
            "system_monitoring"
        ],
        CommercialTrade.POOL_SPA: [
            "commercial_pool_service",
            "pool_maintenance",
            "chemical_balancing",
            "equipment_repair",
            "pool_cleaning",
            "spa_service",
            "pool_inspections",
            "equipment_upgrades"
        ]
    }
    
    # Residential trade default services
    RESIDENTIAL_SERVICES: Dict[ResidentialTrade, List[str]] = {
        ResidentialTrade.HVAC: [
            "ac_installation",
            "ac_repair",
            "furnace_repair",
            "heat_pump_service",
            "duct_cleaning",
            "hvac_maintenance",
            "thermostat_installation",
            "indoor_air_quality",
            "emergency_hvac"
        ],
        ResidentialTrade.PLUMBING: [
            "plumbing_repair",
            "drain_cleaning",
            "water_heater_service",
            "pipe_installation",
            "fixture_installation",
            "leak_detection",
            "sewer_line_service",
            "emergency_plumbing",
            "bathroom_remodeling"
        ],
        ResidentialTrade.ELECTRICAL: [
            "electrical_repair",
            "outlet_installation",
            "panel_upgrades",
            "ceiling_fan_installation",
            "lighting_installation",
            "electrical_inspection",
            "generator_installation",
            "smart_home_wiring",
            "emergency_electrical"
        ],
        ResidentialTrade.CHIMNEY: [
            "chimney_cleaning",
            "chimney_inspection",
            "chimney_repair",
            "fireplace_service",
            "chimney_cap_installation",
            "creosote_removal",
            "damper_repair",
            "chimney_relining"
        ],
        ResidentialTrade.ROOFING: [
            "roof_repair",
            "roof_replacement",
            "roof_inspection",
            "gutter_installation",
            "gutter_cleaning",
            "shingle_replacement",
            "leak_repair",
            "storm_damage_repair",
            "roof_maintenance"
        ],
        ResidentialTrade.GARAGE_DOOR: [
            "garage_door_repair",
            "garage_door_installation",
            "opener_repair",
            "opener_installation",
            "spring_replacement",
            "track_repair",
            "remote_programming",
            "safety_inspection"
        ],
        ResidentialTrade.SEPTIC: [
            "septic_pumping",
            "septic_inspection",
            "septic_repair",
            "drain_field_service",
            "septic_installation",
            "system_maintenance",
            "emergency_service",
            "system_upgrades"
        ],
        ResidentialTrade.PEST_CONTROL: [
            "general_pest_control",
            "termite_treatment",
            "rodent_control",
            "ant_control",
            "spider_control",
            "bee_removal",
            "preventive_treatment",
            "inspection_service"
        ],
        ResidentialTrade.IRRIGATION: [
            "sprinkler_installation",
            "sprinkler_repair",
            "system_maintenance",
            "winterization",
            "spring_startup",
            "controller_programming",
            "leak_detection",
            "system_upgrades"
        ],
        ResidentialTrade.PAINTING: [
            "interior_painting",
            "exterior_painting",
            "cabinet_painting",
            "deck_staining",
            "drywall_repair",
            "pressure_washing",
            "color_consultation",
            "wallpaper_removal"
        ]
    }
    
    @classmethod
    def get_default_services_for_trade(cls, trade: str, market_focus: MarketFocus) -> List[str]:
        """
        Get default services for a specific trade based on market focus
        """
        services = []
        
        if market_focus in [MarketFocus.COMMERCIAL, MarketFocus.BOTH]:
            # Try to find commercial trade
            try:
                commercial_trade = CommercialTrade(trade.lower())
                services.extend(cls.COMMERCIAL_SERVICES.get(commercial_trade, []))
            except ValueError:
                pass
        
        if market_focus in [MarketFocus.RESIDENTIAL, MarketFocus.BOTH]:
            # Try to find residential trade
            try:
                residential_trade = ResidentialTrade(trade.lower())
                services.extend(cls.RESIDENTIAL_SERVICES.get(residential_trade, []))
            except ValueError:
                pass
        
        return list(set(services))  # Remove duplicates
    
    @classmethod
    def get_default_services_for_business(
        cls, 
        primary_trade: str, 
        secondary_trades: List[str], 
        market_focus: MarketFocus
    ) -> Dict[str, List[str]]:
        """
        Get comprehensive default services for a business based on all their trades
        Returns dict with 'residential' and 'commercial' service lists
        """
        residential_services = set()
        commercial_services = set()
        
        # Get all trades (primary + secondary)
        all_trades = [primary_trade] + secondary_trades
        
        for trade in all_trades:
            if not trade:
                continue
                
            # Get commercial services if applicable
            if market_focus in [MarketFocus.COMMERCIAL, MarketFocus.BOTH]:
                try:
                    commercial_trade = CommercialTrade(trade.lower())
                    commercial_services.update(cls.COMMERCIAL_SERVICES.get(commercial_trade, []))
                except ValueError:
                    pass
            
            # Get residential services if applicable
            if market_focus in [MarketFocus.RESIDENTIAL, MarketFocus.BOTH]:
                try:
                    residential_trade = ResidentialTrade(trade.lower())
                    residential_services.update(cls.RESIDENTIAL_SERVICES.get(residential_trade, []))
                except ValueError:
                    pass
        
        return {
            'residential': sorted(list(residential_services)),
            'commercial': sorted(list(commercial_services))
        }
    
    @classmethod
    def get_all_available_services(cls) -> Dict[str, List[str]]:
        """
        Get all available services organized by market type
        """
        all_residential = set()
        all_commercial = set()
        
        # Collect all residential services
        for services in cls.RESIDENTIAL_SERVICES.values():
            all_residential.update(services)
        
        # Collect all commercial services
        for services in cls.COMMERCIAL_SERVICES.values():
            all_commercial.update(services)
        
        return {
            'residential': sorted(list(all_residential)),
            'commercial': sorted(list(all_commercial))
        }
    
    @classmethod
    def get_service_display_name(cls, service_key: str) -> str:
        """
        Convert service key to display name
        """
        return service_key.replace('_', ' ').title()
    
    @classmethod
    def get_services_by_category(cls, market_type: str) -> Dict[str, List[str]]:
        """
        Get services organized by trade category
        """
        if market_type == 'residential':
            return {
                trade.value: services 
                for trade, services in cls.RESIDENTIAL_SERVICES.items()
            }
        elif market_type == 'commercial':
            return {
                trade.value: services 
                for trade, services in cls.COMMERCIAL_SERVICES.items()
            }
        else:
            return {}
