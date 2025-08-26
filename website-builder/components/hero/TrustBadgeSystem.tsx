/**
 * Trust Badge Display System
 * 
 * Displays certifications, awards, ratings, and trust indicators
 */

'use client';

import React from 'react';
import { Star, Shield, Award, Clock, Users, CheckCircle, Phone, MapPin } from 'lucide-react';
import { Badge } from '../ui/badge';

export interface TrustBadge {
  id: string;
  type: 'certification' | 'award' | 'rating' | 'guarantee' | 'experience' | 'availability';
  title: string;
  subtitle?: string;
  value?: string | number;
  icon?: React.ReactNode;
  logo_url?: string;
  description?: string;
  verification_url?: string;
  display_order: number;
  is_featured: boolean;
  applicable_trades?: string[];
}

interface TrustBadgeSystemProps {
  badges: TrustBadge[];
  layout: 'horizontal' | 'grid' | 'compact' | 'featured';
  currentTrade?: string;
  showLogos?: boolean;
  maxDisplay?: number;
  className?: string;
}

export default function TrustBadgeSystem({
  badges,
  layout = 'horizontal',
  currentTrade,
  showLogos = true,
  maxDisplay = 6,
  className = ""
}: TrustBadgeSystemProps) {
  
  // Filter and sort badges
  const filteredBadges = badges
    .filter(badge => {
      // Filter by trade if specified
      if (currentTrade && badge.applicable_trades?.length) {
        return badge.applicable_trades.includes(currentTrade);
      }
      return true;
    })
    .sort((a, b) => {
      // Featured badges first, then by display order
      if (a.is_featured && !b.is_featured) return -1;
      if (!a.is_featured && b.is_featured) return 1;
      return a.display_order - b.display_order;
    })
    .slice(0, maxDisplay);

  const getDefaultIcon = (type: string) => {
    switch (type) {
      case 'certification':
        return <Shield className="w-5 h-5" />;
      case 'award':
        return <Award className="w-5 h-5" />;
      case 'rating':
        return <Star className="w-5 h-5" />;
      case 'guarantee':
        return <CheckCircle className="w-5 h-5" />;
      case 'experience':
        return <Users className="w-5 h-5" />;
      case 'availability':
        return <Clock className="w-5 h-5" />;
      default:
        return <Shield className="w-5 h-5" />;
    }
  };

  const renderBadge = (badge: TrustBadge, index: number) => {
    const icon = badge.icon || getDefaultIcon(badge.type);
    
    const badgeContent = (
      <div className="flex items-center space-x-2 group">
        {/* Icon or Logo */}
        <div className="flex-shrink-0">
          {showLogos && badge.logo_url ? (
            <img 
              src={badge.logo_url} 
              alt={badge.title}
              className="w-8 h-8 object-contain"
            />
          ) : (
            <div className="text-blue-600 group-hover:text-blue-700 transition-colors">
              {icon}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-gray-900 text-sm">
              {badge.title}
            </span>
            {badge.value && (
              <Badge variant="secondary" className="text-xs">
                {badge.value}
              </Badge>
            )}
          </div>
          {badge.subtitle && (
            <p className="text-xs text-gray-600 truncate">
              {badge.subtitle}
            </p>
          )}
        </div>

        {/* Rating Stars for rating type */}
        {badge.type === 'rating' && badge.value && (
          <div className="flex items-center space-x-1">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-4 h-4 ${
                  i < Number(badge.value) 
                    ? 'text-yellow-400 fill-current' 
                    : 'text-gray-300'
                }`}
              />
            ))}
          </div>
        )}
      </div>
    );

    // Wrap with link if verification URL exists
    if (badge.verification_url) {
      return (
        <a
          key={badge.id}
          href={badge.verification_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block hover:bg-gray-50 rounded-lg p-2 transition-colors"
          title={badge.description}
        >
          {badgeContent}
        </a>
      );
    }

    return (
      <div
        key={badge.id}
        className="block p-2 rounded-lg"
        title={badge.description}
      >
        {badgeContent}
      </div>
    );
  };

  const getLayoutClasses = () => {
    switch (layout) {
      case 'horizontal':
        return "flex flex-wrap items-center gap-4 justify-center lg:justify-start";
      case 'grid':
        return "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4";
      case 'compact':
        return "flex flex-wrap items-center gap-2 justify-center";
      case 'featured':
        return "flex flex-col space-y-3";
      default:
        return "flex flex-wrap items-center gap-4";
    }
  };

  if (filteredBadges.length === 0) {
    return null;
  }

  return (
    <div className={`trust-badges ${className}`}>
      {layout === 'featured' && (
        <div className="text-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Why Choose Us
          </h3>
          <p className="text-sm text-gray-600">
            Trusted by thousands of customers across the region
          </p>
        </div>
      )}
      
      <div className={getLayoutClasses()}>
        {filteredBadges.map((badge, index) => renderBadge(badge, index))}
      </div>
    </div>
  );
}

// Default trust badges for different trades
export const getDefaultTrustBadges = (trade: string): TrustBadge[] => {
  const commonBadges: TrustBadge[] = [
    {
      id: 'licensed-insured',
      type: 'certification',
      title: 'Licensed & Insured',
      subtitle: 'Fully licensed and insured',
      display_order: 1,
      is_featured: true,
      applicable_trades: ['HVAC', 'Plumbing', 'Electrical', 'Roofing']
    },
    {
      id: 'satisfaction-guarantee',
      type: 'guarantee',
      title: '100% Satisfaction',
      subtitle: 'Guaranteed or your money back',
      display_order: 2,
      is_featured: true
    },
    {
      id: 'same-day-service',
      type: 'availability',
      title: 'Same-Day Service',
      subtitle: 'Available when you need us',
      display_order: 3,
      is_featured: true
    },
    {
      id: 'experience',
      type: 'experience',
      title: '25+ Years Experience',
      subtitle: 'Serving the community since 1999',
      value: '25+ Years',
      display_order: 4,
      is_featured: true
    }
  ];

  const tradeSpecificBadges: Record<string, TrustBadge[]> = {
    'HVAC': [
      {
        id: 'nate-certified',
        type: 'certification',
        title: 'NATE Certified',
        subtitle: 'North American Technician Excellence',
        display_order: 5,
        is_featured: false,
        applicable_trades: ['HVAC']
      },
      {
        id: 'energy-star',
        type: 'certification',
        title: 'Energy Star Partner',
        subtitle: 'Certified energy efficient installations',
        display_order: 6,
        is_featured: false,
        applicable_trades: ['HVAC']
      }
    ],
    'Plumbing': [
      {
        id: 'master-plumber',
        type: 'certification',
        title: 'Master Plumber',
        subtitle: 'State certified master plumber',
        display_order: 5,
        is_featured: false,
        applicable_trades: ['Plumbing']
      }
    ],
    'Electrical': [
      {
        id: 'master-electrician',
        type: 'certification',
        title: 'Master Electrician',
        subtitle: 'State licensed master electrician',
        display_order: 5,
        is_featured: false,
        applicable_trades: ['Electrical']
      }
    ]
  };

  return [
    ...commonBadges,
    ...(tradeSpecificBadges[trade] || [])
  ];
};

// Rating badge component for displaying review aggregations
export const RatingBadge: React.FC<{
  rating: number;
  reviewCount: number;
  platform?: string;
  className?: string;
}> = ({ rating, reviewCount, platform = "Google", className = "" }) => {
  return (
    <div className={`inline-flex items-center space-x-2 bg-white rounded-lg px-3 py-2 shadow-sm border ${className}`}>
      <div className="flex items-center space-x-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-4 h-4 ${
              i < Math.floor(rating) 
                ? 'text-yellow-400 fill-current' 
                : 'text-gray-300'
            }`}
          />
        ))}
      </div>
      <div className="text-sm">
        <span className="font-semibold text-gray-900">{rating.toFixed(1)}</span>
        <span className="text-gray-600 ml-1">
          ({reviewCount.toLocaleString()}) {platform}
        </span>
      </div>
    </div>
  );
};
