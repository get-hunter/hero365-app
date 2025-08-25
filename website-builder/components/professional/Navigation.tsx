import { useState } from 'react';
import { Phone, Clock, MapPin, Star, Menu, X, ChevronDown } from 'lucide-react';

interface NavigationProps {
  business: {
    name: string;
    phone: string;
    email: string;
    address: string;
    hours: string;
    serviceAreas?: string[];
  };
  serviceCategories: {
    name: string;
    services: any[];
    slug: string;
  }[];
}

export default function Navigation({ business, serviceCategories }: NavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [servicesDropdownOpen, setServicesDropdownOpen] = useState(false);

  return (
    <>
      {/* Top Info Bar - Professional Style */}
      <div className="bg-gray-900 text-white py-2 px-4 text-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-2">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{business.hours}</span>
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              <span>{business.address}</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 text-yellow-400" />
              <span>4.9 Rating • 450+ Reviews</span>
            </div>
            <span className="text-orange-400 font-semibold">24/7 Emergency Service</span>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <div className="flex items-center">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-xl">{business.name.charAt(0)}</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">{business.name}</h1>
                  <p className="text-sm text-gray-600">Licensed & Insured HVAC Experts</p>
                </div>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-8">
              <a href="/" className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200">
                Home
              </a>
              
              {/* Services Dropdown */}
              <div 
                className="relative"
                onMouseEnter={() => setServicesDropdownOpen(true)}
                onMouseLeave={() => setServicesDropdownOpen(false)}
              >
                <button className="flex items-center gap-1 text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200">
                  Services
                  <ChevronDown className="w-4 h-4" />
                </button>
                
                {servicesDropdownOpen && (
                  <div className="absolute top-full left-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-100 py-4 z-50">
                    <div className="px-4 pb-2">
                      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Our Services</h3>
                    </div>
                    {serviceCategories.map((category) => (
                      <a
                        key={category.slug}
                        href={`/services/${category.slug}`}
                        className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
                      >
                        <div>
                          <div className="font-medium text-gray-900">{category.name}</div>
                          <div className="text-sm text-gray-500">{category.services.length} services available</div>
                        </div>
                        <div className="text-blue-600 font-semibold text-sm">
                          View All →
                        </div>
                      </a>
                    ))}
                    <div className="border-t border-gray-100 mt-2 pt-2">
                      <a
                        href="/services"
                        className="block px-4 py-2 text-blue-600 font-semibold hover:bg-blue-50 transition-colors"
                      >
                        View All Services →
                      </a>
                    </div>
                  </div>
                )}
              </div>

              <a href="/about" className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200">
                About Us
              </a>
              <a href="/reviews" className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200">
                Reviews
              </a>
              <a href="/service-areas" className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200">
                Service Areas
              </a>
              <a href="/contact" className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200">
                Contact
              </a>
            </div>

            {/* CTA Buttons */}
            <div className="hidden lg:flex items-center gap-4">
              <a
                href={`tel:${business.phone}`}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors duration-200"
              >
                <Phone className="w-5 h-5" />
                {business.phone}
              </a>
              <button className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200">
                Get Quote
              </button>
            </div>

            {/* Mobile menu button */}
            <div className="lg:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-700 hover:text-blue-600 p-2"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="lg:hidden border-t border-gray-200">
              <div className="px-2 pt-2 pb-3 space-y-1">
                <a href="/" className="block px-3 py-2 text-gray-700 hover:text-blue-600 font-medium">
                  Home
                </a>
                <a href="/services" className="block px-3 py-2 text-gray-700 hover:text-blue-600 font-medium">
                  Services
                </a>
                {serviceCategories.map((category) => (
                  <a
                    key={category.slug}
                    href={`/services/${category.slug}`}
                    className="block px-6 py-2 text-gray-600 hover:text-blue-600 text-sm"
                  >
                    {category.name} ({category.services.length})
                  </a>
                ))}
                <a href="/about" className="block px-3 py-2 text-gray-700 hover:text-blue-600 font-medium">
                  About Us
                </a>
                <a href="/reviews" className="block px-3 py-2 text-gray-700 hover:text-blue-600 font-medium">
                  Reviews
                </a>
                <a href="/service-areas" className="block px-3 py-2 text-gray-700 hover:text-blue-600 font-medium">
                  Service Areas
                </a>
                <a href="/contact" className="block px-3 py-2 text-gray-700 hover:text-blue-600 font-medium">
                  Contact
                </a>
                <div className="px-3 py-4 border-t border-gray-200 mt-4">
                  <a
                    href={`tel:${business.phone}`}
                    className="block w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-semibold text-center mb-2 transition-colors duration-200"
                  >
                    Call {business.phone}
                  </a>
                  <button className="block w-full border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-4 py-3 rounded-lg font-semibold transition-all duration-200">
                    Get Free Quote
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>
    </>
  );
}
