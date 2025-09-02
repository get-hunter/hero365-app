"""
Content Template Service for Category-Specific SEO Content

Provides deterministic scaffolds and templates for different service categories
to ensure consistent, high-quality content generation across all services.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ServiceCategoryTemplate(str, Enum):
    """Service category templates for content generation."""
    HVAC = "hvac"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    ROOFING = "roofing"
    LANDSCAPING = "landscaping"
    SECURITY = "security"
    KITCHEN_EQUIPMENT = "kitchen_equipment"
    WATER_TREATMENT = "water_treatment"
    POOL_SPA = "pool_spa"
    MECHANICAL = "mechanical"
    REFRIGERATION = "refrigeration"
    GARAGE_DOOR = "garage_door"
    SEPTIC = "septic"
    PEST_CONTROL = "pest_control"
    IRRIGATION = "irrigation"
    PAINTING = "painting"
    CHIMNEY = "chimney"
    GENERAL = "general"


class ContentTemplateService:
    """Service for providing category-specific content templates and scaffolds."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def get_category_template(self, category: str) -> ServiceCategoryTemplate:
        """Map service category to template category."""
        category_mapping = {
            # HVAC related
            "hvac": ServiceCategoryTemplate.HVAC,
            "heating": ServiceCategoryTemplate.HVAC,
            "cooling": ServiceCategoryTemplate.HVAC,
            "air_conditioning": ServiceCategoryTemplate.HVAC,
            "ductwork": ServiceCategoryTemplate.HVAC,
            "indoor_air_quality": ServiceCategoryTemplate.HVAC,
            
            # Plumbing related
            "plumbing": ServiceCategoryTemplate.PLUMBING,
            "drain_cleaning": ServiceCategoryTemplate.PLUMBING,
            "water_heater": ServiceCategoryTemplate.PLUMBING,
            "pipe_repair": ServiceCategoryTemplate.PLUMBING,
            "fixture_installation": ServiceCategoryTemplate.PLUMBING,
            
            # Electrical related
            "electrical": ServiceCategoryTemplate.ELECTRICAL,
            "panel_upgrade": ServiceCategoryTemplate.ELECTRICAL,
            "wiring": ServiceCategoryTemplate.ELECTRICAL,
            "lighting": ServiceCategoryTemplate.ELECTRICAL,
            "outlet_installation": ServiceCategoryTemplate.ELECTRICAL,
            
            # Other categories
            "roofing": ServiceCategoryTemplate.ROOFING,
            "landscaping": ServiceCategoryTemplate.LANDSCAPING,
            "security": ServiceCategoryTemplate.SECURITY,
            "kitchen_equipment": ServiceCategoryTemplate.KITCHEN_EQUIPMENT,
            "water_treatment": ServiceCategoryTemplate.WATER_TREATMENT,
            "pool_spa": ServiceCategoryTemplate.POOL_SPA,
            "mechanical": ServiceCategoryTemplate.MECHANICAL,
            "refrigeration": ServiceCategoryTemplate.REFRIGERATION,
            "garage_door": ServiceCategoryTemplate.GARAGE_DOOR,
            "septic": ServiceCategoryTemplate.SEPTIC,
            "pest_control": ServiceCategoryTemplate.PEST_CONTROL,
            "irrigation": ServiceCategoryTemplate.IRRIGATION,
            "painting": ServiceCategoryTemplate.PAINTING,
            "chimney": ServiceCategoryTemplate.CHIMNEY,
        }
        
        return category_mapping.get((category or 'general').lower(), ServiceCategoryTemplate.GENERAL)
    
    def get_hero_template(self, category: ServiceCategoryTemplate, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get hero section template for category."""
        return self.templates[category]["hero"](context)
    
    def get_benefits_template(self, category: ServiceCategoryTemplate, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get benefits template for category."""
        return self.templates[category]["benefits"](context)
    
    def get_process_steps_template(self, category: ServiceCategoryTemplate, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get process steps template for category."""
        return self.templates[category]["process_steps"](context)
    
    def get_faq_template(self, category: ServiceCategoryTemplate, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get FAQ template for category."""
        return self.templates[category]["faq"](context)
    
    def get_keywords_for_category(self, category: ServiceCategoryTemplate, service_name: str, city: str) -> List[str]:
        """Get SEO keywords for category and location."""
        base_keywords = self.templates[category]["keywords"]
        
        # Combine with service and location
        keywords = []
        for keyword in base_keywords:
            keywords.extend([
                f"{keyword} {city}",
                f"{service_name} {city}",
                f"{keyword} near me",
                f"{service_name} near me",
                f"best {keyword} {city}",
                f"professional {keyword}",
                f"{keyword} service",
                f"{keyword} repair",
                f"{keyword} installation"
            ])
        
        return list(set(keywords))  # Remove duplicates
    
    def _initialize_templates(self) -> Dict[ServiceCategoryTemplate, Dict[str, Any]]:
        """Initialize all category templates."""
        return {
            ServiceCategoryTemplate.HVAC: self._get_hvac_templates(),
            ServiceCategoryTemplate.PLUMBING: self._get_plumbing_templates(),
            ServiceCategoryTemplate.ELECTRICAL: self._get_electrical_templates(),
            ServiceCategoryTemplate.ROOFING: self._get_roofing_templates(),
            ServiceCategoryTemplate.LANDSCAPING: self._get_landscaping_templates(),
            ServiceCategoryTemplate.SECURITY: self._get_security_templates(),
            ServiceCategoryTemplate.KITCHEN_EQUIPMENT: self._get_kitchen_equipment_templates(),
            ServiceCategoryTemplate.WATER_TREATMENT: self._get_water_treatment_templates(),
            ServiceCategoryTemplate.POOL_SPA: self._get_pool_spa_templates(),
            ServiceCategoryTemplate.MECHANICAL: self._get_mechanical_templates(),
            ServiceCategoryTemplate.REFRIGERATION: self._get_refrigeration_templates(),
            ServiceCategoryTemplate.GARAGE_DOOR: self._get_garage_door_templates(),
            ServiceCategoryTemplate.SEPTIC: self._get_septic_templates(),
            ServiceCategoryTemplate.PEST_CONTROL: self._get_pest_control_templates(),
            ServiceCategoryTemplate.IRRIGATION: self._get_irrigation_templates(),
            ServiceCategoryTemplate.PAINTING: self._get_painting_templates(),
            ServiceCategoryTemplate.CHIMNEY: self._get_chimney_templates(),
            ServiceCategoryTemplate.GENERAL: self._get_general_templates(),
        }
    
    def _get_hvac_templates(self) -> Dict[str, Any]:
        """HVAC-specific templates."""
        return {
            "hero": lambda ctx: {
                "h1": f"{ctx.get('service_name', 'HVAC Service')} in {ctx.get('city', 'Your Area')}",
                "subheading": "Expert HVAC solutions for year-round comfort",
                "description": f"Professional {(ctx.get('service_name') or 'HVAC service').lower()} from {ctx.get('business_name', 'our certified technicians')}. Licensed, insured, and committed to your comfort in {ctx.get('city', 'your area')}."
            },
            "benefits": lambda ctx: {
                "title": f"Why Choose {ctx.get('business_name', 'Our HVAC Team')}",
                "benefits": [
                    {"title": "NATE Certified Technicians", "description": "Our technicians are NATE certified and continuously trained on the latest HVAC technology.", "icon": "certificate"},
                    {"title": "Energy Efficiency Focus", "description": "We prioritize energy-efficient solutions to reduce your utility bills and environmental impact.", "icon": "leaf"},
                    {"title": "24/7 Emergency Service", "description": "HVAC emergencies don't wait. Neither do we. Available 24/7 for urgent repairs.", "icon": "phone"},
                    {"title": "Preventive Maintenance", "description": "Regular maintenance plans to keep your system running efficiently year-round.", "icon": "wrench"},
                    {"title": "Manufacturer Warranties", "description": "We're authorized dealers offering full manufacturer warranties on equipment.", "icon": "shield"},
                    {"title": "Indoor Air Quality", "description": "Comprehensive solutions for cleaner, healthier indoor air for your family.", "icon": "air"}
                ]
            },
            "process_steps": lambda ctx: {
                "title": "Our HVAC Service Process",
                "description": "Professional service from diagnosis to completion",
                "steps": [
                    {"name": "System Diagnosis", "text": "Comprehensive inspection and testing of your HVAC system to identify issues."},
                    {"name": "Detailed Assessment", "text": "We explain findings and provide detailed recommendations with upfront pricing."},
                    {"name": "Professional Repair", "text": "Expert repair or installation using quality parts and proven techniques."},
                    {"name": "System Testing", "text": "Thorough testing to ensure optimal performance and efficiency."},
                    {"name": "Maintenance Plan", "text": "Optional maintenance plan to keep your system running at peak performance."},
                    {"name": "Follow-Up Service", "text": "We follow up to ensure your complete satisfaction with our work."}
                ]
            },
            "faq": lambda ctx: {
                "title": "HVAC Frequently Asked Questions",
                "faqs": [
                    {"question": "How often should I service my HVAC system?", "answer": "We recommend professional maintenance twice a year - spring for cooling and fall for heating systems."},
                    {"question": "What are signs my HVAC system needs repair?", "answer": "Strange noises, poor airflow, inconsistent temperatures, high energy bills, or frequent cycling on/off."},
                    {"question": "How long do HVAC systems typically last?", "answer": "With proper maintenance, heating systems last 15-20 years and cooling systems last 10-15 years."},
                    {"question": "Do you offer emergency HVAC service?", "answer": "Yes, we provide 24/7 emergency service for urgent heating and cooling issues."},
                    {"question": "What HVAC brands do you work with?", "answer": "We service all major brands and are authorized dealers for leading manufacturers like Carrier, Trane, and Lennox."},
                    {"question": "Do you offer financing for HVAC installations?", "answer": "Yes, we offer flexible financing options to make HVAC installations more affordable."},
                    {"question": "How can I improve my home's energy efficiency?", "answer": "Regular maintenance, proper insulation, programmable thermostats, and upgrading to high-efficiency equipment."},
                    {"question": "What size HVAC system do I need?", "answer": "System size depends on home size, insulation, windows, and other factors. We perform load calculations to determine the right size."}
                ]
            },
            "keywords": ["hvac", "heating", "cooling", "air conditioning", "furnace", "heat pump", "ductwork", "indoor air quality"]
        }
    
    def _get_plumbing_templates(self) -> Dict[str, Any]:
        """Plumbing-specific templates."""
        return {
            "hero": lambda ctx: {
                "h1": f"{ctx.get('service_name', 'Plumbing Service')} in {ctx.get('city', 'Your Area')}",
                "subheading": "Reliable plumbing solutions when you need them most",
                "description": f"Expert {(ctx.get('service_name') or 'plumbing service').lower()} from {ctx.get('business_name', 'our licensed plumbers')}. Fast, reliable, and guaranteed work in {ctx.get('city', 'your area')}."
            },
            "benefits": lambda ctx: {
                "title": f"Why Choose {ctx.get('business_name', 'Our Plumbing Team')}",
                "benefits": [
                    {"title": "Licensed Master Plumbers", "description": "Our team includes licensed master plumbers with years of experience.", "icon": "certificate"},
                    {"title": "Same-Day Service", "description": "Most plumbing issues resolved the same day with our rapid response team.", "icon": "clock"},
                    {"title": "Upfront Pricing", "description": "No surprises - we provide clear, upfront pricing before any work begins.", "icon": "dollar"},
                    {"title": "Quality Guarantees", "description": "All work is guaranteed and backed by our commitment to quality.", "icon": "check"},
                    {"title": "Modern Equipment", "description": "State-of-the-art tools and equipment for efficient, lasting repairs.", "icon": "wrench"},
                    {"title": "Clean Work Areas", "description": "We respect your home and always clean up after completing our work.", "icon": "home"}
                ]
            },
            "process_steps": lambda ctx: {
                "title": "Our Plumbing Service Process",
                "description": "Professional plumbing service from start to finish",
                "steps": [
                    {"name": "Problem Assessment", "text": "Thorough inspection to identify the root cause of your plumbing issue."},
                    {"name": "Clear Explanation", "text": "We explain the problem and all available solutions in plain language."},
                    {"name": "Upfront Quote", "text": "Detailed pricing provided before any work begins - no hidden fees."},
                    {"name": "Expert Repair", "text": "Professional repair using quality materials and proven techniques."},
                    {"name": "System Testing", "text": "Complete testing to ensure the repair is working properly."},
                    {"name": "Cleanup & Guarantee", "text": "We clean up our work area and provide guarantees on all repairs."}
                ]
            },
            "faq": lambda ctx: {
                "title": "Plumbing Frequently Asked Questions",
                "faqs": [
                    {"question": "What should I do in a plumbing emergency?", "answer": "Turn off the main water supply, avoid using electrical appliances near water, and call us immediately for emergency service."},
                    {"question": "How can I prevent clogged drains?", "answer": "Avoid putting grease, hair, and food scraps down drains. Use drain screens and schedule regular drain cleaning."},
                    {"question": "When should I replace my water heater?", "answer": "Consider replacement if your water heater is over 8-10 years old, needs frequent repairs, or isn't heating efficiently."},
                    {"question": "What causes low water pressure?", "answer": "Common causes include mineral buildup, pipe corrosion, leaks, or issues with the municipal water supply."},
                    {"question": "Do you offer 24/7 emergency plumbing service?", "answer": "Yes, we provide round-the-clock emergency service for urgent plumbing issues."},
                    {"question": "How often should I have my plumbing inspected?", "answer": "Annual plumbing inspections can help prevent major issues and extend the life of your plumbing system."},
                    {"question": "What's the difference between a plumber and a master plumber?", "answer": "Master plumbers have additional training, experience, and licensing to handle complex installations and supervise other plumbers."},
                    {"question": "Do you provide warranties on plumbing work?", "answer": "Yes, we guarantee all our work and provide warranties on parts and labor."}
                ]
            },
            "keywords": ["plumbing", "plumber", "drain cleaning", "water heater", "pipe repair", "leak repair", "fixture installation", "emergency plumbing"]
        }
    
    def _get_electrical_templates(self) -> Dict[str, Any]:
        """Electrical-specific templates."""
        return {
            "hero": lambda ctx: {
                "h1": f"{ctx.get('service_name', 'Electrical Service')} in {ctx.get('city', 'Your Area')}",
                "subheading": "Safe, reliable electrical solutions for your home or business",
                "description": f"Professional {(ctx.get('service_name') or 'electrical service').lower()} from {ctx.get('business_name', 'our licensed electricians')}. Safety-focused, code-compliant work in {ctx.get('city', 'your area')}."
            },
            "benefits": lambda ctx: {
                "title": f"Why Choose {ctx.get('business_name', 'Our Electrical Team')}",
                "benefits": [
                    {"title": "Licensed Electricians", "description": "All our electricians are fully licensed and continuously trained on electrical codes.", "icon": "certificate"},
                    {"title": "Safety First", "description": "We prioritize safety in every job, following all electrical codes and best practices.", "icon": "shield"},
                    {"title": "Code Compliance", "description": "All work meets or exceeds local electrical codes and passes inspection.", "icon": "check"},
                    {"title": "Modern Technology", "description": "We stay current with smart home technology and energy-efficient solutions.", "icon": "zap"},
                    {"title": "Emergency Service", "description": "24/7 emergency electrical service for urgent safety issues.", "icon": "phone"},
                    {"title": "Warranty Protection", "description": "Comprehensive warranties on all electrical work and materials.", "icon": "award"}
                ]
            },
            "process_steps": lambda ctx: {
                "title": "Our Electrical Service Process",
                "description": "Safe, professional electrical work every time",
                "steps": [
                    {"name": "Safety Assessment", "text": "Comprehensive electrical safety inspection and problem diagnosis."},
                    {"name": "Code Review", "text": "We ensure all work will meet current electrical codes and safety standards."},
                    {"name": "Detailed Estimate", "text": "Clear pricing and timeline for all electrical work before we begin."},
                    {"name": "Professional Installation", "text": "Expert electrical work using quality materials and proven techniques."},
                    {"name": "Testing & Inspection", "text": "Thorough testing to ensure safe operation and code compliance."},
                    {"name": "Permit & Documentation", "text": "We handle permits and provide documentation for your records."}
                ]
            },
            "faq": lambda ctx: {
                "title": "Electrical Frequently Asked Questions",
                "faqs": [
                    {"question": "When should I upgrade my electrical panel?", "answer": "Consider upgrading if your panel is over 20 years old, uses fuses instead of breakers, or can't handle your electrical needs."},
                    {"question": "What are signs of electrical problems?", "answer": "Flickering lights, burning smells, warm outlets, frequent breaker trips, or outlets that don't work properly."},
                    {"question": "Do you handle electrical permits?", "answer": "Yes, we obtain all necessary permits and ensure all work passes electrical inspection."},
                    {"question": "Can you install smart home devices?", "answer": "Absolutely! We specialize in smart home installations including switches, outlets, and automation systems."},
                    {"question": "What's involved in whole-house rewiring?", "answer": "Complete replacement of old wiring, outlets, switches, and electrical panel to meet modern safety standards."},
                    {"question": "Do you offer emergency electrical service?", "answer": "Yes, we provide 24/7 emergency service for electrical safety issues and power outages."},
                    {"question": "How can I make my home more energy efficient?", "answer": "LED lighting, smart switches, energy-efficient appliances, and proper electrical load management."},
                    {"question": "What should I do if my breaker keeps tripping?", "answer": "Don't reset it repeatedly. This indicates an overload or short circuit that needs professional attention."}
                ]
            },
            "keywords": ["electrical", "electrician", "panel upgrade", "wiring", "outlet installation", "lighting", "electrical repair", "smart home"]
        }
    
    # Add placeholder methods for other categories
    def _get_roofing_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_landscaping_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_security_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_kitchen_equipment_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_water_treatment_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_pool_spa_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_mechanical_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_refrigeration_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_garage_door_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_septic_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_pest_control_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_irrigation_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_painting_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_chimney_templates(self) -> Dict[str, Any]:
        return self._get_general_templates()
    
    def _get_general_templates(self) -> Dict[str, Any]:
        """General templates for services without specific category templates."""
        return {
            "hero": lambda ctx: {
                "h1": f"{ctx.get('service_name', 'Professional Service')} in {ctx.get('city', 'Your Area')}",
                "subheading": f"Expert {(ctx.get('service_name') or 'service').lower()} you can trust",
                "description": f"Professional {(ctx.get('service_name') or 'service').lower()} from {ctx.get('business_name', 'our experienced team')}. Licensed, insured, and committed to quality in {ctx.get('city', 'your area')}."
            },
            "benefits": lambda ctx: {
                "title": f"Why Choose {ctx.get('business_name', 'Our Team')}",
                "benefits": [
                    {"title": "Licensed & Insured", "description": "Fully licensed professionals with comprehensive insurance coverage.", "icon": "shield"},
                    {"title": "Experienced Team", "description": "Years of experience providing quality service to satisfied customers.", "icon": "award"},
                    {"title": "Quality Guarantee", "description": "We stand behind our work with comprehensive service guarantees.", "icon": "check"},
                    {"title": "Upfront Pricing", "description": "Transparent pricing with no hidden fees or surprise charges.", "icon": "dollar"},
                    {"title": "Professional Service", "description": "Courteous, professional service that respects your time and property.", "icon": "star"},
                    {"title": "Customer Satisfaction", "description": "Your satisfaction is our priority - we're not done until you're happy.", "icon": "heart"}
                ]
            },
            "process_steps": lambda ctx: {
                "title": "Our Service Process",
                "description": "Professional service from start to finish",
                "steps": [
                    {"name": "Initial Consultation", "text": "We discuss your needs and assess the scope of work required."},
                    {"name": "Detailed Estimate", "text": "Comprehensive estimate with clear pricing and timeline."},
                    {"name": "Professional Work", "text": "Expert service using quality materials and proven techniques."},
                    {"name": "Quality Inspection", "text": "Thorough inspection to ensure work meets our high standards."},
                    {"name": "Customer Walkthrough", "text": "We review completed work and answer any questions you have."},
                    {"name": "Follow-Up Service", "text": "We follow up to ensure your complete satisfaction."}
                ]
            },
            "faq": lambda ctx: {
                "title": "Frequently Asked Questions",
                "faqs": [
                    {"question": "Are you licensed and insured?", "answer": "Yes, we are fully licensed and carry comprehensive insurance for your protection."},
                    {"question": "Do you provide free estimates?", "answer": "Yes, we provide free, no-obligation estimates for all services."},
                    {"question": "What areas do you serve?", "answer": f"We serve {ctx.get('city', 'the local area')} and surrounding communities."},
                    {"question": "Do you guarantee your work?", "answer": "Absolutely. We stand behind all our work with comprehensive guarantees."},
                    {"question": "How quickly can you respond?", "answer": "We strive to respond to all service requests as quickly as possible, often same-day."},
                    {"question": "What payment methods do you accept?", "answer": "We accept cash, check, and all major credit cards for your convenience."}
                ]
            },
            "keywords": ["service", "professional", "licensed", "insured", "quality", "reliable"]
        }
