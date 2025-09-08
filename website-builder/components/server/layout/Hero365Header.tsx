/**
 * Hero365 Server Header Component
 * 
 * SSR/CSR hybrid header that loads data on server and renders interactive client component
 * Designed for optimal performance with Cloudflare Workers
 */

import React from 'react';
import { loadNavigationData } from '@/lib/server/navigation-loader';
import Hero365HeaderClient from '@/components/client/layout/Hero365HeaderClient';
import { ShoppingBag, Menu } from 'lucide-react';

// Helper function to group services by category (not trade) and limit items per group
function groupServicesByCategory(services: any[]) {
  const categories: Record<string, any[]> = {};

  const titleCase = (str?: string) => {
    if (!str) return '';
    return String(str)
      .toLowerCase()
      .replace(/\b\w/g, (m) => m.toUpperCase());
  };

  for (const service of services) {
    // Prefer normalized category values; fallback to trade-derived label
    const rawCategory: string = service.category || service.category_slug || '';
    const categoryName = rawCategory ? titleCase(rawCategory) : getCategoryDisplayName(service.trade_slug);

    if (!categories[categoryName]) {
      categories[categoryName] = [];
    }

    // Push simplified item shape expected by the client/menu renderers
    categories[categoryName].push({
      name: service.name,
      description: `Professional ${String(service.name).toLowerCase()} services`,
      href: service.href,
      is_emergency: service.is_emergency
    });
  }

  // Sort categories by a sensible priority, then alphabetically
  const priority = ['Installation', 'Repair', 'Maintenance', 'Emergency', 'Inspection', 'Cleaning', 'Upgrade', 'General'];
  const sortKey = (name: string) => {
    const idx = priority.indexOf(name);
    return idx === -1 ? 999 : idx;
  };

  // Convert to array and limit items per category to keep menu compact
  return Object.entries(categories)
    .sort(([a], [b]) => sortKey(a) - sortKey(b) || a.localeCompare(b))
    .map(([name, list]) => ({
      name,
      description: `${name} services`,
      services: list.slice(0, 6) // cap items shown per category in the mega menu
    }));
}

function getCategoryDisplayName(tradeSlug?: string): string {
  const tradeMap: Record<string, string> = {
    'hvac': 'HVAC',
    'plumbing': 'Plumbing', 
    'electrical': 'Electrical',
    'roofing': 'Roofing',
    'general-contractor': 'General',
    'landscaping': 'Landscaping',
    'security-systems': 'Security',
    'pool-spa': 'Pool & Spa'
  };
  
  return tradeMap[tradeSlug || ''] || 'Services';
}

// SSR-safe phone formatting
function formatPhoneForDisplay(phone: string): string {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  if (cleaned.length === 11 && cleaned[0] === '1') {
    return `(${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  return phone;
}

interface BusinessProfile {
  business_id: string;
  business_name: string;
  phone: string;
  phone_display?: string;
  email: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  logo_url?: string;
}

interface Hero365HeaderProps {
  // Option 1: Accept business profile directly
  businessProfile?: BusinessProfile | null;
  // Option 2: Accept individual props (for backward compatibility)
  businessName?: string;
  city?: string;
  state?: string;
  phone?: string;
  supportHours?: string;
  logo?: string;
  primaryColor?: string;
  ctaSlot?: React.ReactNode;
  cartSlot?: React.ReactNode;
  showCTA?: boolean;
  showCart?: boolean;
}

export default async function Hero365Header({
  businessProfile,
  businessName,
  city,
  state,
  phone,
  supportHours = "24/7",
  logo,
  primaryColor = "#3b82f6",
  ctaSlot,
  cartSlot,
  showCTA = false,
  showCart = false
}: Hero365HeaderProps) {
  // Extract data from business profile or use individual props
  const finalBusinessName = businessProfile?.business_name || businessName || 'Professional Services';
  const finalCity = businessProfile?.city || city || 'Austin';
  const finalState = businessProfile?.state || state || 'TX';
  const finalPhone = businessProfile?.phone_display || businessProfile?.phone || phone || '';
  const finalLogo = businessProfile?.logo_url || logo;
  
  const displayPhone = finalPhone ? formatPhoneForDisplay(finalPhone) : null;
  const telPhone = finalPhone ? finalPhone.replace(/\D/g, '') : null;

  // Load dynamic navigation data from backend
  const { serviceCategories: services, locations } = await loadNavigationData();
  
  // Group services by trade/category for mega menu
  const serviceCategories = groupServicesByCategory(services);

  // Simplified: only keep prioritized nav in client; companyLinks not used
  const companyLinks: Array<{ name: string; href: string }> = [];

  return (
    <>
      {/* Top Bar - Server rendered */}
      <div className="bg-gray-900 text-white py-2 px-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="font-medium">{finalCity}, {finalState}</span>
            </div>
            
            {/* Desktop Phone Display */}
            {displayPhone && telPhone && (
              <div className="hidden md:flex items-center">
                <span className="text-green-400 font-medium">Support {supportHours}:</span>
                <a 
                  href={`tel:${telPhone}`}
                  className="ml-2 text-white hover:text-blue-400 transition-colors font-bold text-lg"
                >
                  {displayPhone}
                </a>
              </div>
            )}
            
            {/* Mobile Phone Display */}
            {displayPhone && telPhone && (
              <div className="md:hidden flex items-center">
                <svg className="w-4 h-4 mr-1 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <a 
                  href={`tel:${telPhone}`}
                  className="text-white hover:text-blue-400 transition-colors font-bold"
                >
                  {displayPhone}
                </a>
              </div>
            )}
          </div>
          <div className="flex items-center space-x-4">
            <button className="px-3 py-1 text-xs border border-white text-white hover:bg-white hover:text-gray-900 rounded transition-colors font-medium">
              Get a Quote Now
            </button>
            {showCTA && ctaSlot}
          </div>
        </div>
      </div>

      {/* Main Header - Server structure with client interactivity */}
      <header className="sticky top-0 z-40 bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo - Server rendered */}
            <div className="flex items-center">
              <a href="/" className="flex items-center">
                {finalLogo ? (
                  <img src={finalLogo} alt={finalBusinessName} className="h-10 w-auto" />
                ) : (
                  <div className="text-2xl font-bold" style={{ color: primaryColor }}>
                    {finalBusinessName}
                  </div>
                )}
              </a>
            </div>

            {/* Interactive Navigation - Client component (desktop only visible) */}
            <Hero365HeaderClient
              businessName={finalBusinessName}
              displayPhone={displayPhone}
              telPhone={telPhone}
              serviceCategories={serviceCategories}
              companyLinks={companyLinks}
              ctaSlot={ctaSlot}
              cartSlot={cartSlot}
              showCTA={showCTA}
              showCart={showCart}
            />

            {/* Mobile actions: cart + burger (SSR) */}
            <div className="flex items-center space-x-2 lg:hidden">
              {showCart && (
                cartSlot || (
                  <a href="/cart" className="p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100" aria-label="View cart">
                    <ShoppingBag className="w-5 h-5" />
                  </a>
                )
              )}

              <details className="relative">
                <summary className="p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 list-none" aria-label="Open menu">
                  <Menu className="h-6 w-6" />
                </summary>
                <div className="absolute right-0 mt-2 w-80 max-h-[80vh] overflow-auto bg-white border rounded-lg shadow-lg p-4 space-y-4">
                  <div className="space-y-4">
                    <div>
                      <div className="text-gray-900 font-semibold mb-2">Services</div>
                      {serviceCategories.map((category) => (
                        <div key={category.name} className="ml-2 mb-3">
                          <div className="font-medium text-gray-800 mb-1">{category.name}</div>
                          {category.services.map((service: any) => (
                            <a
                              key={service.name}
                              href={service.href}
                              className="block text-sm text-gray-600 py-1 hover:text-blue-600"
                            >
                              {service.name}
                              {service.is_emergency && (
                                <span className="ml-2 text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">24/7</span>
                              )}
                            </a>
                          ))}
                        </div>
                      ))}
                    </div>

                    <a href="/locations" className="block text-gray-700 font-medium">Service Areas</a>
                    <a href="/projects" className="block text-gray-700 font-medium">Projects</a>
                    <a href="/products" className="block text-gray-700 font-medium">Products</a>
                  </div>
                  <div className="pt-4 border-t border-gray-200">
                    {showCTA && (
                      <div className="flex items-center gap-3">
                        <a href="/contact?action=quote" className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors">Get a Quote Now</a>
                        <a href="/booking" className="px-4 py-2 bg-white text-blue-600 font-medium rounded-md border border-blue-600 hover:bg-blue-50 transition-colors">Book Now</a>
                      </div>
                    )}
                  </div>
                </div>
              </details>
            </div>
          </div>
        </div>
      </header>
    </>
  );
}
