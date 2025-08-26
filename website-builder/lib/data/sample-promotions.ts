/**
 * Sample Promotions Data
 * 
 * Enhanced promotional system with seasonal offers
 */

import { Promotion } from '../../components/hero/PromotionalBannerSystem';

export const samplePromotions: Promotion[] = [
  {
    id: "rebate-2025",
    title: "Enjoy Up to $1500 Rebate",
    subtitle: "Your friends at Austin Elite HVAC offer incredible rebates for your new efficient equipment. Reach out today to learn more!",
    offer_type: "seasonal_special",
    price_label: "Up to $1500",
    badge_text: "Limited Time",
    cta_text: "More Details",
    placement: "hero_banner",
    priority: 10,
    is_active: true,
    is_featured: true,
    target_trades: ["HVAC"],
    banner_style: "gradient",
    background_color: "#10b981"
  },
  {
    id: "thermostat-offer",
    title: "Just $50 for a Thermostat",
    subtitle: "Incredible offer from your favorite contractor—smart thermostats for $50 only.",
    offer_type: "fixed_amount",
    price_label: "$50",
    badge_text: "Hot Offer",
    cta_text: "Details Here",
    placement: "hero_banner",
    priority: 8,
    is_active: true,
    is_featured: false,
    target_trades: ["HVAC"],
    banner_style: "seasonal",
    background_color: "#ea580c"
  },
  {
    id: "warranty-offer",
    title: "Extended Warranty Up to 12 Years",
    subtitle: "Austin Elite HVAC offers up to 12 years of labor warranty and up to 12 years of parts warranty for your residential HVAC installations",
    offer_type: "free_service",
    price_label: "12 Years",
    badge_text: "Extended",
    cta_text: "Learn More",
    placement: "hero_banner",
    priority: 6,
    is_active: true,
    is_featured: false,
    target_trades: ["HVAC"],
    banner_style: "pattern",
    background_color: "#2563eb"
  },
  {
    id: "emergency-service",
    title: "24/7 Emergency Service Available",
    subtitle: "No overtime charges for emergency calls",
    offer_type: "free_service",
    badge_text: "Emergency Ready",
    cta_text: "Call Now",
    placement: "hero_banner",
    priority: 9,
    is_active: true,
    is_featured: false,
    target_trades: ["HVAC"],
    banner_style: "seasonal",
    background_color: "#dc2626"
  }
];


