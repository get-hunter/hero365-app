/**
 * Elite Header Component
 * 
 * Professional header with 24/7 support, location, CTAs, and mega-menu navigation
 * Inspired by elite service websites like the reference site
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Phone, MapPin, Menu, X, ChevronDown, ShoppingBag } from 'lucide-react';
import { Button } from '../ui/button';
import { BookingCTAButton } from '../booking/BookingWidgetProvider';
import { CartIndicator } from '../cart/CartIndicator';

interface EliteHeaderProps {
  businessName: string;
  city: string;
  state: string;
  phone: string;
  supportHours?: string;
  logo?: string;
  primaryColor?: string;
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

export default function EliteHeader({
  businessName,
  city,
  state,
  phone,
  supportHours = "24/7",
  logo,
  primaryColor = "#3b82f6"
}: EliteHeaderProps) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Improved hover handlers with delay
  const handleMouseEnter = (dropdown: string) => {
    if (hoverTimeout) {
      clearTimeout(hoverTimeout);
      setHoverTimeout(null);
    }
    setActiveDropdown(dropdown);
  };

  const handleMouseLeave = () => {
    const timeout = setTimeout(() => {
      setActiveDropdown(null);
    }, 150); // 150ms delay before closing
    setHoverTimeout(timeout);
  };

  // Service categories for mega menu
  const serviceCategories: ServiceCategory[] = [
    {
      name: "Air Conditioning",
      description: "Complete AC services",
      services: [
        { name: "Heat Pump Installation", description: "Energy-efficient heat pump systems", href: "/services/heat-pump" },
        { name: "Ductless Split System", description: "Flexible cooling solutions", href: "/services/ductless" },
        { name: "Air Conditioner Repair", description: "Fast AC repair service", href: "/services/ac-repair" },
        { name: "Duct Inspection", description: "Professional ductwork inspection", href: "/services/duct-inspection" }
      ]
    },
    {
      name: "Heating",
      description: "Heating system services",
      services: [
        { name: "Furnace Installation", description: "New furnace installation", href: "/services/furnace-install" },
        { name: "Heater Repair", description: "Emergency heater repair", href: "/services/heater-repair" },
        { name: "Rooftop Package Unit", description: "Commercial heating units", href: "/services/rooftop-unit" }
      ]
    },
    {
      name: "Electrical",
      description: "Electrical services",
      services: [
        { name: "Panel Installation", description: "Electrical panel upgrade", href: "/services/panel-install" },
        { name: "EV Charger Installation", description: "Electric vehicle charging", href: "/services/ev-charger" },
        { name: "Electrical Repair", description: "Emergency electrical repair", href: "/services/electrical-repair" }
      ]
    },
    {
      name: "Plumbing",
      description: "Plumbing services",
      services: [
        { name: "Water Heater Installation", description: "New water heater systems", href: "/services/water-heater" },
        { name: "Plumbing Repair", description: "Emergency plumbing repair", href: "/services/plumbing-repair" },
        { name: "Pipe Restoration", description: "Pipe repair and replacement", href: "/services/pipe-restoration" }
      ]
    }
  ];

  const companyLinks = [
    { name: "About Us", href: "/about" },
    { name: "Service Area", href: "/service-area" },
    { name: "Why Choose Us", href: "/why-us" },
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
              <MapPin className="w-4 h-4 mr-2 text-blue-400" />
              <span className="font-medium">{city}, {state}</span>
            </div>
            <div className="hidden md:flex items-center">
              <span className="text-green-400 font-medium">Support {supportHours}:</span>
              <a 
                href={`tel:${phone}`}
                className="ml-2 text-white hover:text-blue-400 transition-colors font-bold"
              >
                {phone}
              </a>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button className="px-3 py-1 text-xs border border-white text-white hover:bg-white hover:text-gray-900 rounded transition-colors font-medium">
              Get a Quote Now
            </button>
            <BookingCTAButton 
              size="sm"
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1"
            >
              Book Now
            </BookingCTAButton>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header 
        className={`sticky top-0 z-40 transition-all duration-300 ${
          isScrolled 
            ? 'bg-white shadow-lg border-b' 
            : 'bg-white border-b border-gray-200'
        }`}
      >
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
              <div 
                className="relative"
                onMouseEnter={() => handleMouseEnter('services')}
                onMouseLeave={handleMouseLeave}
              >
                <button className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2">
                  Services
                  <ChevronDown className="ml-1 h-4 w-4" />
                </button>
                
                {activeDropdown === 'services' && (
                  <div className="absolute top-full left-0 mt-0 w-screen max-w-4xl bg-white shadow-xl border rounded-lg z-50">
                    <div className="p-6">
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                        {serviceCategories.map((category) => (
                          <div key={category.name}>
                            <h3 className="font-semibold text-gray-900 mb-3">
                              {category.name}
                            </h3>
                            <p className="text-sm text-gray-600 mb-3">
                              {category.description}
                            </p>
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
                            <p className="text-sm text-gray-600">Our experts are here to help</p>
                          </div>
                          <div className="flex space-x-3">
                            <a 
                              href={`tel:${phone}`}
                              className="px-3 py-1 text-sm border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
                            >
                              Call {phone}
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Products Link */}
              <a href="/products" className="text-gray-700 hover:text-gray-900 font-medium py-2">
                Products
              </a>

              {/* Company Dropdown */}
              <div 
                className="relative"
                onMouseEnter={() => handleMouseEnter('company')}
                onMouseLeave={handleMouseLeave}
              >
                <button className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2">
                  Company
                  <ChevronDown className="ml-1 h-4 w-4" />
                </button>
                
                {activeDropdown === 'company' && (
                  <div className="absolute top-full left-0 mt-0 w-64 bg-white shadow-xl border rounded-lg z-50">
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
                )}
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
              <a 
                href={`tel:${phone}`}
                className="flex items-center text-gray-700 hover:text-gray-900 font-medium"
              >
                <Phone className="w-4 h-4 mr-2" />
                {phone}
              </a>
              <CartIndicator />
              <BookingCTAButton>
                Book Now
              </BookingCTAButton>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden bg-white border-t border-gray-200">
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
                <a 
                  href={`tel:${phone}`}
                  className="flex items-center text-gray-700 font-medium"
                >
                  <Phone className="w-4 h-4 mr-2" />
                  {phone}
                </a>
                <CartIndicator />
                <div className="flex space-x-3">
                  <BookingCTAButton className="flex-1">
                    Book Now
                  </BookingCTAButton>
                </div>
              </div>
            </div>
          </div>
        )}
      </header>
    </>
  );
}
