'use client';

import { useState } from 'react';
import { Phone, Clock, MapPin, Star, Menu, X, ChevronDown } from 'lucide-react';

interface NavigationItem {
  label: string;
  url: string;
  type: 'page' | 'dropdown';
  children?: NavigationItem[];
  service_count?: number;
}

interface Business {
  name: string;
  phone: string;
  email: string;
  address: string;
  hours?: string;
  service_areas?: string[];
}

interface DynamicNavigationProps {
  business: Business;
  navigationItems: NavigationItem[];
  primaryColor?: string;
  secondaryColor?: string;
}

export default function DynamicNavigation({ 
  business, 
  navigationItems, 
  primaryColor = '#3B82F6',
  secondaryColor = '#10B981'
}: DynamicNavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  const toggleDropdown = (label: string) => {
    setActiveDropdown(activeDropdown === label ? null : label);
  };

  const handleCallClick = () => {
    window.location.href = `tel:${business.phone}`;
  };

  return (
    <>
      {/* Top Info Bar */}
      <div className="bg-gray-900 text-white py-2 px-4 text-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-2">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Phone size={14} />
              <a href={`tel:${business.phone}`} className="hover:text-blue-300">
                {business.phone}
              </a>
            </div>
            {business.hours && (
              <div className="hidden md:flex items-center gap-1">
                <Clock size={14} />
                <span>{business.hours}</span>
              </div>
            )}
            {business.service_areas && business.service_areas.length > 0 && (
              <div className="hidden lg:flex items-center gap-1">
                <MapPin size={14} />
                <span>Serving {business.service_areas.slice(0, 3).join(', ')}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Star className="text-yellow-400" size={14} fill="currentColor" />
            <span className="text-xs">Licensed & Insured</span>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <a 
                href="/" 
                className="text-2xl font-bold"
                style={{ color: primaryColor }}
              >
                {business.name}
              </a>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {navigationItems.map((item, index) => (
                <div key={index} className="relative">
                  {item.type === 'dropdown' && item.children ? (
                    <div className="relative">
                      <button
                        onClick={() => toggleDropdown(item.label)}
                        className="flex items-center text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors duration-200"
                      >
                        {item.label}
                        <ChevronDown 
                          size={16} 
                          className={`ml-1 transition-transform duration-200 ${
                            activeDropdown === item.label ? 'rotate-180' : ''
                          }`} 
                        />
                      </button>
                      
                      {activeDropdown === item.label && (
                        <div className="absolute left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                          <div className="py-2">
                            {item.children.map((child, childIndex) => (
                              <a
                                key={childIndex}
                                href={child.url}
                                className="flex justify-between items-center px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors duration-150"
                                onClick={() => setActiveDropdown(null)}
                              >
                                <span className="font-medium">{child.label}</span>
                                {child.service_count && (
                                  <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full">
                                    {child.service_count} services
                                  </span>
                                )}
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <a
                      href={item.url}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors duration-200"
                    >
                      {item.label}
                    </a>
                  )}
                </div>
              ))}
              
              {/* CTA Button */}
              <button
                onClick={handleCallClick}
                className="px-6 py-2 text-white font-semibold rounded-lg transition-colors duration-200"
                style={{ backgroundColor: secondaryColor }}
              >
                Call Now
              </button>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-700 hover:text-blue-600"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-2 space-y-1">
              {navigationItems.map((item, index) => (
                <div key={index}>
                  {item.type === 'dropdown' && item.children ? (
                    <div>
                      <button
                        onClick={() => toggleDropdown(item.label)}
                        className="flex justify-between items-center w-full text-left px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md"
                      >
                        {item.label}
                        <ChevronDown 
                          size={16} 
                          className={`transition-transform duration-200 ${
                            activeDropdown === item.label ? 'rotate-180' : ''
                          }`} 
                        />
                      </button>
                      
                      {activeDropdown === item.label && (
                        <div className="pl-4 space-y-1">
                          {item.children.map((child, childIndex) => (
                            <a
                              key={childIndex}
                              href={child.url}
                              className="flex justify-between items-center px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md"
                              onClick={() => {
                                setActiveDropdown(null);
                                setMobileMenuOpen(false);
                              }}
                            >
                              <span>{child.label}</span>
                              {child.service_count && (
                                <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full">
                                  {child.service_count}
                                </span>
                              )}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <a
                      href={item.url}
                      className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.label}
                    </a>
                  )}
                </div>
              ))}
              
              <div className="pt-4 pb-2">
                <button
                  onClick={() => {
                    handleCallClick();
                    setMobileMenuOpen(false);
                  }}
                  className="w-full px-4 py-3 text-white font-semibold rounded-lg"
                  style={{ backgroundColor: secondaryColor }}
                >
                  Call Now - {business.phone}
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>
    </>
  );
}
