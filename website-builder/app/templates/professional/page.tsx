'use client'

import React from 'react'
import { Business, ServiceCategory } from '../../lib/types/business'
import ProfessionalHero from '../../../components/professional/ProfessionalHero'
import TrustRatingDisplay from '../../../components/professional/TrustRatingDisplay'
import PromotionalBanners from '../../../components/professional/PromotionalBanners'
import ServicesGrid from '../../../components/professional/ServicesGrid'
import ContactSection from '../../../components/professional/ContactSection'
import CustomerReviews from '../../../components/professional/CustomerReviews'
import AwardsAndCertifications from '../../../components/professional/AwardsAndCertifications'
import ServiceAreas from '../../../components/professional/ServiceAreas'
import DealerPartnerships from '../../../components/professional/DealerPartnerships'
import ProfessionalFooter from '../../../components/professional/ProfessionalFooter'
import DynamicNavigation from '../../../components/professional/DynamicNavigation'

interface ProfessionalTemplateProps {
  business: Business
  serviceCategories: ServiceCategory[]
  websiteData?: {
    heroContent?: {
      title?: string
      subtitle?: string
      features?: string[]
    }
    promotionalBanners?: Array<{
      title: string
      subtitle: string
      buttonText: string
      buttonLink: string
      theme: 'primary' | 'secondary' | 'accent'
    }>
    trustRatings?: {
      google?: { rating: number; reviews: number }
      yelp?: { rating: number; reviews: number }
      facebook?: { rating: number; reviews: number }
    }
    awards?: string[]
    dealerLogos?: string[]
  }
}

export default function ProfessionalTemplate({ 
  business, 
  serviceCategories,
  websiteData = {} 
}: ProfessionalTemplateProps) {
  const {
    heroContent = {
      title: `Quality ${business.residential_trades?.join(', ') || business.commercial_trades?.join(', ') || 'Home Services'} in ${business.city}, ${business.state}`,
      subtitle: `${business.name} - Your trusted partner for professional ${business.trade_category?.toLowerCase()} services`,
      features: ['24/7 Emergency Service', 'Licensed & Insured', 'Same-Day Service', 'Satisfaction Guaranteed']
    },
    promotionalBanners = [
      {
        title: 'Quality Guaranteed',
        subtitle: 'Extended Warranty Up to 12 Years',
        buttonText: 'More Details',
        buttonLink: '#warranty',
        theme: 'primary' as const
      },
      {
        title: 'Emergency Service',
        subtitle: '24/7 Rapid Response Available',
        buttonText: 'Call Now',
        buttonLink: `tel:${business.phone_number}`,
        theme: 'secondary' as const
      },
      {
        title: 'Special Offer',
        subtitle: 'New Customer Discount Available',
        buttonText: 'Get Quote',
        buttonLink: '#contact',
        theme: 'accent' as const
      }
    ],
    trustRatings = {
      google: { rating: 4.9, reviews: 797 },
      yelp: { rating: 4.8, reviews: 1067 },
      facebook: { rating: 4.9, reviews: 427 }
    },
    awards = [
      'Licensed & Insured',
      'Better Business Bureau A+',
      'Angie\'s List Super Service Award',
      'Home Advisor Elite Service'
    ],
    dealerLogos = []
  } = websiteData

  // Calculate total services for display
  const totalServices = serviceCategories.reduce((total, category) => 
    total + (category.services?.length || 0), 0
  )

  // Get featured services across all categories
  const featuredServices = serviceCategories.flatMap(category => 
    category.services?.filter(service => service.is_featured) || []
  ).slice(0, 6) // Limit to top 6 featured services

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <DynamicNavigation 
        business={business} 
        serviceCategories={serviceCategories}
      />

      {/* Hero Section */}
      <ProfessionalHero
        business={business}
        heroContent={heroContent}
        totalServices={totalServices}
      />

      {/* Trust Ratings */}
      <TrustRatingDisplay trustRatings={trustRatings} />

      {/* Promotional Banners */}
      <PromotionalBanners banners={promotionalBanners} />

      {/* Services Section */}
      <ServicesGrid
        serviceCategories={serviceCategories}
        featuredServices={featuredServices}
        business={business}
      />

      {/* Contact Section */}
      <ContactSection business={business} />

      {/* Customer Reviews */}
      <CustomerReviews 
        business={business}
        trustRatings={trustRatings}
      />

      {/* Awards and Certifications */}
      <AwardsAndCertifications 
        awards={awards}
        business={business}
      />

      {/* Service Areas */}
      <ServiceAreas 
        business={business}
        serviceAreas={business.service_areas || []}
      />

      {/* Dealer Partnerships */}
      {dealerLogos.length > 0 && (
        <DealerPartnerships dealerLogos={dealerLogos} />
      )}

      {/* Footer */}
      <ProfessionalFooter 
        business={business}
        serviceCategories={serviceCategories}
      />
    </div>
  )
}
