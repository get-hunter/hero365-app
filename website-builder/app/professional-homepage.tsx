'use client';

import { Star, Phone, Shield, Clock, Thermometer, Wind, Wrench, CheckCircle, Award, Users, ThumbsUp, MapPin } from 'lucide-react';
import ProfessionalLayout from './layout-professional';
import Navigation from '../components/professional/Navigation';

interface Service {
  id: string;
  name: string;
  description: string;
  price?: string;
  features?: string[];
  isPopular?: boolean;
  isEmergency?: boolean;
}

interface Business {
  name: string;
  phone: string;
  email: string;
  address: string;
  hours: string;
  serviceAreas?: string[];
  description?: string;
}

interface HomePageProps {
  business: Business;
  services: Service[];
}

// Service categorization logic based on service names
function categorizeServices(services: Service[]) {
  const categories = [
    {
      name: "Air Conditioning",
      slug: "air-conditioning", 
      icon: <Thermometer className="w-8 h-8" />,
      description: "Professional AC repair, installation and maintenance services",
      services: services.filter(s => 
        s.name.toLowerCase().includes('ac') || 
        s.name.toLowerCase().includes('air conditioning') ||
        s.name.toLowerCase().includes('cooling')
      )
    },
    {
      name: "Heating",
      slug: "heating",
      icon: <Wind className="w-8 h-8" />,
      description: "Expert heating system repair, installation and maintenance",
      services: services.filter(s => 
        s.name.toLowerCase().includes('heating') || 
        s.name.toLowerCase().includes('furnace') ||
        s.name.toLowerCase().includes('heat pump')
      )
    },
    {
      name: "Installation",  
      slug: "installation",
      icon: <Shield className="w-8 h-8" />,
      description: "Complete HVAC system installation and replacement services",
      services: services.filter(s => 
        s.name.toLowerCase().includes('installation') ||
        s.name.toLowerCase().includes('thermostat')
      )
    },
    {
      name: "Maintenance",
      slug: "maintenance", 
      icon: <Wrench className="w-8 h-8" />,
      description: "Preventive maintenance and cleaning services",
      services: services.filter(s => 
        s.name.toLowerCase().includes('maintenance') ||
        s.name.toLowerCase().includes('cleaning') ||
        s.name.toLowerCase().includes('tune-up')
      )
    }
  ].filter(category => category.services.length > 0); // Only include categories with services

  return categories;
}

export default function ProfessionalHomepage({ business, services }: HomePageProps) {
  const serviceCategories = categorizeServices(services);
  
  const seo = {
    title: `${business.name} - #1 HVAC Services | Heating & Air Conditioning Experts`,
    description: `${business.name} provides professional HVAC services including air conditioning repair, heating installation, and 24/7 emergency service. Licensed & insured with 4.9-star rating.`,
    keywords: ["hvac services", "air conditioning repair", "heating installation", "hvac maintenance", "emergency hvac", business.name.toLowerCase()]
  };

  return (
    <ProfessionalLayout seo={seo} business={business}>
      <Navigation business={business} serviceCategories={serviceCategories} />

      {/* Promotional Banner */}
      <section className="bg-gradient-to-r from-orange-600 to-red-600 text-white py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="font-bold text-lg flex items-center justify-center gap-2">
            🔥 <span>Enjoy Up to $1,500 Rebate on New HVAC Systems - Limited Time!</span>
          </p>
        </div>
      </section>

      {/* Hero Section - Professional Style */}
      <section className="bg-gradient-to-br from-blue-50 to-blue-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            
            {/* Left Column - Main Content */}
            <div>
              <div className="mb-6">
                <span className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                  BEST SERVICE
                </span>
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                HVAC Services in <br />
                <span className="text-blue-600">Austin, TX</span>
              </h1>
              
              <p className="text-xl text-gray-700 mb-8 leading-relaxed">
                {business.description || `${business.name} provides professional HVAC services including air conditioning repair, heating installation, and 24/7 emergency service throughout Austin and surrounding areas.`}
              </p>

              {/* Trust Badges */}
              <div className="flex flex-wrap items-center gap-6 mb-8">
                <div className="flex items-center gap-2">
                  <Shield className="w-6 h-6 text-green-600" />
                  <span className="font-semibold text-gray-700">Licensed & Insured</span>
                </div>
                <div className="flex items-center gap-2">
                  <Award className="w-6 h-6 text-blue-600" />  
                  <span className="font-semibold text-gray-700">15+ Years Experience</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-6 h-6 text-orange-600" />
                  <span className="font-semibold text-gray-700">Same-Day Service</span>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <a
                  href={`tel:${business.phone}`}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-bold text-xl transition-colors text-center flex items-center justify-center gap-2"
                >
                  <Phone className="w-6 h-6" />
                  Call {business.phone}
                </a>
                <button className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-4 rounded-lg font-bold text-xl transition-all text-center">
                  Get Free Quote
                </button>
              </div>
            </div>

            {/* Right Column - Trust Signals */}
            <div className="text-center lg:text-right">
              {/* Rating Card */}
              <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
                <div className="text-center">
                  <div className="text-6xl font-bold text-blue-600 mb-2">4.9</div>
                  <div className="text-yellow-400 text-2xl mb-2">★★★★★</div>
                  <div className="text-gray-600 font-semibold mb-4">Average Trust Rating Among Our Customers</div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-blue-600">Google</div>
                      <div className="flex items-center gap-1">
                        <span className="text-yellow-400">★★★★★</span>
                        <span className="text-sm text-gray-600">4.9 from 200+ reviews</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-red-600">Yelp</div>
                      <div className="flex items-center gap-1">
                        <span className="text-yellow-400">★★★★★</span>
                        <span className="text-sm text-gray-600">4.8 from 150+ reviews</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-blue-800">Facebook</div>
                      <div className="flex items-center gap-1">
                        <span className="text-yellow-400">★★★★★</span>
                        <span className="text-sm text-gray-600">4.9 from 100+ reviews</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Special Offer Card */}
              <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-2xl p-6 text-center">
                <h3 className="text-xl font-bold mb-2">🌡️ HOT NEW OFFER</h3>
                <div className="text-3xl font-bold mb-2">Just $99</div>
                <div className="text-lg mb-3">Smart Thermostats</div>
                <p className="text-sm opacity-90 mb-4">
                  Incredible offer from your favorite contractor—smart thermostats starting at $99.
                </p>
                <button className="bg-white text-orange-600 px-6 py-2 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                  Details Here
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Special Offers Grid - Professional Style */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Rebate Offer */}
            <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">💰 Quality Guaranteed</h3>
              <div className="text-4xl font-bold mb-2">Up to $1,500</div>
              <div className="text-xl mb-4">{business.name} Rebate</div>
              <p className="mb-6 opacity-90">
                Your friends at {business.name} offer incredible rebates for your new efficient equipment. Reach out today to learn more!
              </p>
              <button className="bg-white text-green-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                More Details
              </button>
            </div>

            {/* Warranty Offer */} 
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">🛡️ Top Quality</h3>
              <div className="text-4xl font-bold mb-2">Up to 12 Years</div>
              <div className="text-xl mb-4">Extended Warranty</div>
              <p className="mb-6 opacity-90">
                {business.name} offers up to 12 years of labor warranty and up to 12 years of parts warranty for your residential HVAC installations.
              </p>
              <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                More Details
              </button>
            </div>

            {/* Emergency Service */}
            <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">⚡ Emergency Service</h3>
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-xl mb-4">Same-Day Service</div>
              <p className="mb-6 opacity-90">
                We provide same-day HVAC service 7 days a week. Any type of service available — residential or commercial.
              </p>
              <button className="bg-white text-red-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                Call Now
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Best HVAC Services in Austin
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              <strong>Heating and Air Conditioning Services Austin, TX</strong><br />
              We got you covered with all your heating and cooling needs. {business.name} provides top-notch HVAC services 
              including installation, repair and maintenance of highest quality.
            </p>
          </div>

          {/* Service Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            {serviceCategories.map((category, index) => (
              <div key={index} className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border-b-4 border-blue-500">
                <div className="text-blue-600 mb-4">
                  {category.icon}
                </div>
                <h3 className="text-xl font-bold mb-3">{category.name}</h3>
                <p className="text-gray-600 mb-4">{category.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-blue-600 font-semibold">
                    {category.services.length} Services Available
                  </span>
                  <a href={`/services/${category.slug}`} className="text-blue-600 hover:text-blue-800 font-semibold text-sm">
                    Learn More →
                  </a>
                </div>
              </div>
            ))}
          </div>

          {/* Featured Services */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.slice(0, 6).map((service) => (
              <div key={service.id} className={`bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${service.isPopular ? 'ring-2 ring-blue-500' : ''}`}>
                {service.isPopular && (
                  <div className="bg-blue-500 text-white text-center py-2 font-bold text-sm">
                    MOST POPULAR
                  </div>
                )}
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3">{service.name}</h3>
                  <p className="text-gray-600 mb-4">{service.description}</p>
                  {service.price && (
                    <div className="text-2xl font-bold text-blue-600 mb-4">
                      {service.price}
                    </div>
                  )}
                  <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors">
                    Get Quote
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Reviews Section - Professional Style */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Don't Take Our Word for It — Check Out Our Reviews!
            </h2>
            <div className="inline-flex items-center gap-4">
              <span className="bg-green-600 text-white px-6 py-2 rounded-full font-bold text-lg">
                EXCELLENT
              </span>
              <span className="text-gray-600 text-lg">Based on 450+ reviews</span>
            </div>
          </div>

          {/* Review Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <div className="bg-gray-50 rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                  JD
                </div>
                <div className="ml-4">
                  <h4 className="font-bold">John D.</h4>
                  <div className="text-yellow-400">★★★★★</div>
                </div>
              </div>
              <p className="text-gray-700">
                "Very professional service! The technician was knowledgeable, on time, and provided clear explanations. 
                Fixed our AC in no time. Would definitely recommend!"
              </p>
            </div>

            <div className="bg-gray-50 rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center text-white font-bold">
                  SM
                </div>
                <div className="ml-4">
                  <h4 className="font-bold">Sarah M.</h4>
                  <div className="text-yellow-400">★★★★★</div>
                </div>
              </div>
              <p className="text-gray-700">
                "Outstanding work on our HVAC installation. The team was professional, clean, and completed the job efficiently. 
                Great pricing and excellent warranty too!"
              </p>
            </div>

            <div className="bg-gray-50 rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center text-white font-bold">
                  MR
                </div>
                <div className="ml-4">
                  <h4 className="font-bold">Mike R.</h4>
                  <div className="text-yellow-400">★★★★★</div>
                </div>
              </div>
              <p className="text-gray-700">
                "Emergency service at 10 PM - they actually came! Fixed our heating system quickly and professionally. 
                Highly recommend for emergency needs."
              </p>
            </div>
          </div>

          {/* Platform Ratings */}
          <div className="text-center">
            <div className="inline-flex items-center space-x-12 bg-gray-50 rounded-2xl p-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 mb-2">Google</div>
                <div className="text-yellow-400 text-lg mb-1">★★★★★</div>
                <div className="text-sm text-gray-600">4.9 Rating from 200+ Reviews</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600 mb-2">Yelp</div>
                <div className="text-yellow-400 text-lg mb-1">★★★★★</div>
                <div className="text-sm text-gray-600">4.8 Rating from 150+ Reviews</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-800 mb-2">Facebook</div>
                <div className="text-yellow-400 text-lg mb-1">★★★★★</div>
                <div className="text-sm text-gray-600">4.9 Rating from 100+ Reviews</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About/Why Choose Us Section */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">About {business.name}</h2>
              <p className="text-xl mb-6 opacity-95">
                We Are Your Best Solution for Accurate, Immediate, and Professional Help with All of Your Major Service Needs.
              </p>
              <p className="text-lg mb-8 opacity-90">
                {business.name}, a reputable HVAC company in Austin, has over 15 years of experience servicing the local area 
                and it's no wonder we're one of most sought-out HVAC contractors in Austin.
              </p>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <span className="font-semibold">24/7 Friendly Support</span>
                </div>
                <div className="flex items-center gap-3">
                  <Users className="w-6 h-6 text-green-400" />
                  <span className="font-semibold">Professional Specialists</span>
                </div>
                <div className="flex items-center gap-3">
                  <Award className="w-6 h-6 text-green-400" />
                  <span className="font-semibold">15+ Years Experience</span>
                </div>
                <div className="flex items-center gap-3">
                  <Shield className="w-6 h-6 text-green-400" />
                  <span className="font-semibold">Up to 12 Years of HVAC Labor Warranty</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="w-6 h-6 text-green-400" />
                  <span className="font-semibold">Same-day HVAC Service</span>
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className="bg-white bg-opacity-10 rounded-2xl p-8">
                <div className="text-6xl font-bold mb-4">4.9</div>
                <div className="text-2xl font-semibold mb-4">Average Trust Rating</div>
                <div className="text-lg opacity-90">Based on 450+ verified customer reviews across Google, Yelp, and Facebook</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gray-900 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-4">We are Always in Touch to Help You with Any Issues</h2>
          <p className="text-xl mb-8 opacity-90">
            Ready to experience the best HVAC service in Austin? Contact us today for your free estimate!
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href={`tel:${business.phone}`}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-bold text-xl transition-colors flex items-center justify-center gap-2"
            >
              <Phone className="w-6 h-6" />
              Call {business.phone}
            </a>
            <button className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-8 py-4 rounded-lg font-bold text-xl transition-all">
              Get Free Quote
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">{business.name}</h3>
              <p className="text-gray-300 mb-4">
                Your best solution for accurate, immediate, and professional help with all of your major HVAC service needs.
              </p>
              <div className="flex items-center gap-2 text-yellow-400 mb-2">
                <Star className="w-5 h-5 fill-current" />
                <span className="font-semibold">4.9 Average Rating</span>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Services</h4>
              <ul className="space-y-2 text-gray-300">
                {serviceCategories.map((category) => (
                  <li key={category.slug}>
                    <a href={`/services/${category.slug}`} className="hover:text-white transition-colors">
                      {category.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-300">
                <li><a href="/about" className="hover:text-white transition-colors">About</a></li>
                <li><a href="/reviews" className="hover:text-white transition-colors">Reviews</a></li>
                <li><a href="/service-areas" className="hover:text-white transition-colors">Service Areas</a></li>
                <li><a href="/contact" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-semibold mb-4">Contact Info</h4>
              <div className="space-y-2 text-gray-300">
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  <span>{business.phone}</span>
                </div>
                <div className="flex items-start gap-2">
                  <Clock className="w-4 h-4 mt-1" />
                  <span>{business.hours}</span>
                </div>
                <div className="flex items-start gap-2">
                  <MapPin className="w-4 h-4 mt-1" />
                  <span>{business.address}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 {business.name}. All Rights Reserved.</p>
          </div>
        </div>
      </footer>
    </ProfessionalLayout>
  );
}
