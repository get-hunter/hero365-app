'use client';

import React from 'react';
import { Gift, Zap, Shield, Clock, Phone } from 'lucide-react';

interface PromotionalOffer {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  ctaText: string;
  ctaAction: string;
  backgroundColor: string;
  textColor: string;
  accentColor: string;
  icon: React.ReactNode;
  isActive: boolean;
}

interface PromotionalBannersProps {
  business: {
    name: string;
    phone: string;
  };
  offers?: PromotionalOffer[];
  primaryColor?: string;
}

export default function PromotionalBanners({ 
  business, 
  offers,
  primaryColor = '#1E40AF'
}: PromotionalBannersProps) {
  
  // Default offers based on Fuse Service model
  const defaultOffers: PromotionalOffer[] = [
    {
      id: 'rebate',
      title: 'Quality Guaranteed',
      subtitle: 'Enjoy Up to $1500 Rebate',
      description: `Your friends at ${business.name} offer incredible rebates for your new efficient equipment. Reach out today to learn more!`,
      ctaText: 'More Details',
      ctaAction: 'rebate_details',
      backgroundColor: 'bg-gradient-to-r from-green-600 to-green-700',
      textColor: 'text-white',
      accentColor: 'text-green-200',
      icon: <Gift size={24} className="text-green-200" />,
      isActive: true
    },
    {
      id: 'thermostat',
      title: 'Hot New Offer',
      subtitle: 'Just $50 for a Thermostat',
      description: `Incredible offer from your favorite contractor—smart thermostats for $50 only. Limited time offer!`,
      ctaText: 'Details here',
      ctaAction: 'thermostat_offer',
      backgroundColor: 'bg-gradient-to-r from-orange-600 to-red-600',
      textColor: 'text-white',
      accentColor: 'text-orange-200',
      icon: <Zap size={24} className="text-orange-200" />,
      isActive: true
    },
    {
      id: 'warranty',
      title: 'Top Quality',
      subtitle: 'Extended Warranty Up to 12 Years',
      description: `${business.name} offers up to 12 years of labor warranty and up to 12 years of parts warranty for your installations`,
      ctaText: 'More Details',
      ctaAction: 'warranty_details',
      backgroundColor: 'bg-gradient-to-r from-blue-600 to-blue-700',
      textColor: 'text-white',
      accentColor: 'text-blue-200',
      icon: <Shield size={24} className="text-blue-200" />,
      isActive: true
    }
  ];

  const activeOffers = offers || defaultOffers.filter(offer => offer.isActive);

  const handleOfferClick = (action: string) => {
    switch (action) {
      case 'rebate_details':
        // Open rebate details modal or page
        break;
      case 'thermostat_offer':
        // Open thermostat offer details
        break;
      case 'warranty_details':
        // Open warranty information
        break;
      default:
        window.location.href = `tel:${business.phone}`;
    }
  };

  if (activeOffers.length === 0) return null;

  return (
    <section className="py-8 bg-gray-100">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeOffers.map((offer, index) => (
            <div
              key={offer.id}
              className={`${offer.backgroundColor} rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-pointer transform hover:-translate-y-1`}
              onClick={() => handleOfferClick(offer.ctaAction)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {offer.icon}
                  <span className={`text-sm font-medium ${offer.accentColor}`}>
                    {offer.title}
                  </span>
                </div>
              </div>
              
              <h3 className={`text-2xl font-bold mb-3 ${offer.textColor}`}>
                {offer.subtitle}
              </h3>
              
              <p className={`text-sm mb-4 ${offer.accentColor} leading-relaxed`}>
                {offer.description}
              </p>
              
              <button className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 backdrop-blur-sm border border-white border-opacity-20">
                {offer.ctaText}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Emergency Banner Component (separate from promotional banners)
export function EmergencyBanner({ 
  business, 
  message = "🚨 HVAC Emergency? We're Available 24/7 - No Overtime Charges!",
  isVisible = true 
}: {
  business: { phone: string };
  message?: string;
  isVisible?: boolean;
}) {
  if (!isVisible) return null;

  return (
    <div className="bg-red-600 text-white py-3 px-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Clock size={20} className="text-red-200" />
          <span className="font-semibold text-center md:text-left">
            {message}
          </span>
        </div>
        <button
          onClick={() => window.location.href = `tel:${business.phone}`}
          className="bg-white text-red-600 px-4 py-2 rounded-lg font-semibold hover:bg-red-50 transition-colors duration-200 flex items-center gap-2"
        >
          <Phone size={16} />
          Call Now
        </button>
      </div>
    </div>
  );
}
