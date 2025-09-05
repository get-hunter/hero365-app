/**
 * Hero365 Server Header Component
 * 
 * Server-safe header that renders static content and accepts client components via slots
 * Designed for SSR compatibility with Cloudflare Workers
 */

import React from 'react';

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

interface Hero365HeaderServerProps {
  businessName: string;
  city: string;
  state: string;
  phone: string;
  supportHours?: string;
  logo?: string;
  primaryColor?: string;
  ctaSlot?: React.ReactNode; // Client components passed as children
  cartSlot?: React.ReactNode; // Cart indicator slot
}

interface ServiceCategory {
  name: string;
  description: string;
  services: Array<{
    name: string;
    description: string;
    href: string;
  }>;
}

export default function Header({
  businessName,
  city,
  state,
  phone,
  supportHours = "24/7",
  logo,
  primaryColor = "#3b82f6",
  ctaSlot,
  cartSlot
}: Hero365HeaderServerProps) {
  const displayPhone = phone ? formatPhoneForDisplay(phone) : null;
  const telPhone = phone ? phone.replace(/\D/g, '') : null; // Simple phone normalization for tel: links

  // Static service categories for server rendering
  const serviceCategories: ServiceCategory[] = [
    {
      name: "Air Conditioning",
      description: "Complete AC services",
      services: [
        { name: "Heat Pump Installation", description: "Energy-efficient heat pump systems", href: "/services/heat-pump-service" },
        { name: "Ductless Split System", description: "Flexible cooling solutions", href: "/services/ductless-split-system" },
        { name: "Air Conditioner Repair", description: "Fast AC repair service", href: "/services/ac-repair" },
        { name: "Duct Inspection", description: "Professional ductwork inspection", href: "/services/duct-inspection" }
      ]
    },
    {
      name: "Heating",
      description: "Heating system services",
      services: [
        { name: "Furnace Installation", description: "New furnace installation", href: "/services/furnace-installation" },
        { name: "Heater Repair", description: "Emergency heater repair", href: "/services/furnace-repair" },
        { name: "Heating Installation", description: "Complete heating systems", href: "/services/heating-installation" }
      ]
    },
    {
      name: "Electrical",
      description: "Electrical services",
      services: [
        { name: "Panel Installation", description: "Electrical panel upgrade", href: "/services/panel-upgrades" },
        { name: "Electrical Repair", description: "Emergency electrical repair", href: "/services/electrical-repair" },
        { name: "Lighting Installation", description: "Interior and exterior lighting", href: "/services/lighting-installation" }
      ]
    },
    {
      name: "Plumbing",
      description: "Plumbing services",
      services: [
        { name: "Water Heater Service", description: "Water heater repair and maintenance", href: "/services/water-heater-service" },
        { name: "Plumbing Repair", description: "Emergency plumbing repair", href: "/services/plumbing-repair" },
        { name: "Drain Cleaning", description: "Drain clearing and cleaning", href: "/services/drain-cleaning" }
      ]
    }
  ];

  const companyLinks = [
    { name: "About Us", href: "/about" },
    { name: "Service Area", href: "/service-area" },
    { name: "Why Choose Us", href: "/why-us" },
    { name: "Our Work", href: "/projects" },
    { name: "Customer Reviews", href: "/reviews" },
    { name: "Careers", href: "/careers" },
    { name: "Blog", href: "/blog" }
  ];

  return (
    <>
      {/* Top Bar */}
      <div className="bg-gray-900 text-white py-2 px-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="font-medium">{city}, {state}</span>
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
            {ctaSlot}
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header className="sticky top-0 z-40 bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <a href="/" className="flex items-center">
                {logo ? (
                  <img src={logo} alt={businessName} className="h-10 w-auto" />
                ) : (
                  <div className="text-2xl font-bold" style={{ color: primaryColor }}>
                    {businessName}
                  </div>
                )}
              </a>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-8">
              
              {/* Services Mega Menu */}
              <div className="relative group">
                <button className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2">
                  Services
                  <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                <div className="absolute top-full left-0 mt-0 w-screen max-w-4xl bg-white shadow-xl border rounded-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                  <div className="p-6">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                      {serviceCategories.map((category) => (
                        <div key={category.name}>
                          <h3 className="font-semibold text-gray-900 mb-3">
                            {category.name}
                          </h3>
                          <ul className="space-y-2">
                            {category.services.map((service) => (
                              <li key={service.name}>
                                <a 
                                  href={service.href}
                                  className="block text-sm text-gray-600 hover:text-blue-600 transition-colors"
                                >
                                  {service.name}
                                </a>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                    <div className="mt-6 pt-6 border-t border-gray-200">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold text-gray-900">Need Help Choosing?</h4>
                          <p className="text-sm text-gray-600">Our experts are here to help - call the number above</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Products Link */}
              <a href="/products" className="text-gray-700 hover:text-gray-900 font-medium py-2">
                Products
              </a>

              {/* Projects Link */}
              <a href="/projects" className="text-gray-700 hover:text-gray-900 font-medium py-2">
                Projects
              </a>

              {/* Company Dropdown */}
              <div className="relative group">
                <button className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2">
                  Company
                  <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                <div className="absolute top-full left-0 mt-0 w-64 bg-white shadow-xl border rounded-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                  <div className="py-2">
                    {companyLinks.map((link) => (
                      <a
                        key={link.name}
                        href={link.href}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                      >
                        {link.name}
                      </a>
                    ))}
                  </div>
                </div>
              </div>

              <a href="/pricing" className="text-gray-700 hover:text-gray-900 font-medium">
                Pricing
              </a>
              <a href="/contact" className="text-gray-700 hover:text-gray-900 font-medium">
                Contact
              </a>
            </nav>

            {/* Desktop CTAs */}
            <div className="hidden lg:flex items-center space-x-3">
              {cartSlot}
            </div>

            {/* Mobile Menu Button - Client component will handle this */}
            <div className="lg:hidden flex items-center space-x-3">
              {cartSlot}
              {/* Mobile menu toggle will be handled by client component */}
            </div>
          </div>
        </div>

        {/* Mobile Menu - Static version for server rendering */}
        <div className="lg:hidden bg-white border-t border-gray-200 hidden">
          <div className="px-4 py-6 space-y-6">
            <div className="space-y-4">
              <div>
                <div className="text-gray-900 font-semibold mb-2">Services</div>
                {serviceCategories.map((category) => (
                  <div key={category.name} className="ml-4 mb-3">
                    <div className="font-medium text-gray-800 mb-1">{category.name}</div>
                    {category.services.map((service) => (
                      <a
                        key={service.name}
                        href={service.href}
                        className="block text-sm text-gray-600 py-1"
                      >
                        {service.name}
                      </a>
                    ))}
                  </div>
                ))}
              </div>
              <a href="/products" className="block text-gray-700 font-medium">
                Products
              </a>
              <a href="/projects" className="block text-gray-700 font-medium">
                Projects
              </a>
              <div>
                <div className="text-gray-900 font-semibold mb-2">Company</div>
                <div className="ml-4 space-y-1">
                  {companyLinks.map((link) => (
                    <a
                      key={link.name}
                      href={link.href}
                      className="block text-sm text-gray-600 py-1"
                    >
                      {link.name}
                    </a>
                  ))}
                </div>
              </div>
              <a href="/pricing" className="block text-gray-700 font-medium">
                Pricing
              </a>
              <a href="/contact" className="block text-gray-700 font-medium">
                Contact
              </a>
            </div>
            
            <div className="pt-6 border-t border-gray-200 space-y-3">
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-3">
                  Ready to get started? Call the number above or book online!
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  );
}
