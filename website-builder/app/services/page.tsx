'use client';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import ServiceCard from '@/components/base/ServiceCard';
import ContactForm from '@/components/base/ContactForm';
import { Thermometer, Wind, Shield, Wrench, Clock, CheckCircle, Star } from 'lucide-react';

export default function ServicesPage() {
  // This would normally come from API/props
  const business = {
    name: "Austin Elite HVAC",
    phone: "(512) 555-COOL",
    email: "service@austinelitehvac.com",
    address: "456 Tech Ridge Blvd, Austin, TX 78753",
    hours: "Mon-Fri 7AM-8PM, Sat-Sun 8AM-6PM, 24/7 Emergency Service"
  };

  const seo = {
    title: "HVAC Services - Austin Elite HVAC | Professional Heating & Cooling",
    description: "Complete HVAC services in Austin, TX. AC repair, heating installation, maintenance plans, and 24/7 emergency service. Licensed & insured technicians.",
    keywords: ["hvac services austin", "ac repair", "heating installation", "hvac maintenance", "emergency hvac"]
  };

    // Real services from database - injected by deployment script
  const services = [
    {
        "title": "Duct Cleaning Service",
        "description": "Professional duct cleaning and sanitization to improve air quality and system efficiency. Removes dust, debris, and allergens.",
        "price": "From $299",
        "features": [
            "Professional service",
            "Licensed & insured",
            "3.0 hour service"
        ],
        "isPopular": false
    },
    {
        "title": "Emergency AC Repair",
        "description": "24/7 rapid response for all AC breakdowns. Our certified technicians diagnose and fix AC issues quickly to restore your comfort.",
        "price": "From $149",
        "features": [
            "Professional service",
            "Licensed & insured",
            "24/7 emergency available",
            "1.5 hour service"
        ],
        "isPopular": true
    },
    {
        "title": "HVAC System Installation",
        "description": "Complete HVAC system installation and replacement. Energy-efficient systems with professional installation and warranty.",
        "price": "Free Quote",
        "features": [
            "Professional service",
            "Licensed & insured",
            "4.0 hour service"
        ],
        "isPopular": false
    },
    {
        "title": "Preventative Maintenance Plan",
        "description": "Annual tune-ups to ensure optimal system performance and longevity. Includes filter changes, system cleaning, and efficiency checks.",
        "price": "From $199",
        "features": [
            "Professional service",
            "Licensed & insured",
            "1.0 hour service"
        ],
        "isPopular": false
    },
    {
        "title": "Thermostat Installation",
        "description": "Smart thermostat installation and setup. Includes programming and training on optimal usage for energy savings.",
        "price": "Free Quote",
        "features": [
            "Professional service",
            "Licensed & insured",
            "2.0 hour service"
        ],
        "isPopular": false
    }
];

  const serviceIcons = {
    'Emergency AC Repair': <Thermometer className="w-6 h-6" />,
    'Heating System Service': <Wind className="w-6 h-6" />,
    'HVAC Installation': <Shield className="w-6 h-6" />,
    'Preventive Maintenance': <Wrench className="w-6 h-6" />,
    'Air Quality Solutions': <Wind className="w-6 h-6" />,
    'Ductwork Services': <CheckCircle className="w-6 h-6" />
  };

  // Service categories - defined after services to avoid deployment script override
  const serviceCategories = [
    {
      name: "Emergency Services",
      description: "24/7 emergency HVAC repair and service",
      services: services.filter(s => s.isPopular), // Use popular services as emergency
      icon: <Clock className="w-8 h-8" />
    },
    {
      name: "Repair Services", 
      description: "Professional HVAC repair and troubleshooting",
      services: services.filter(s => s.title.includes("Repair") || s.title.includes("Maintenance")),
      icon: <Wrench className="w-8 h-8" />
    },
    {
      name: "Installation Services",
      description: "New HVAC system installation and replacement", 
      services: services.filter(s => s.title.includes("Installation")),
      icon: <Shield className="w-8 h-8" />
    },
    {
      name: "Maintenance Services",
      description: "Preventive maintenance and tune-up services",
      services: services.filter(s => s.title.includes("Cleaning") || s.title.includes("Thermostat")),
      icon: <CheckCircle className="w-8 h-8" />
    }
  ];

  return (
    <Layout seo={seo} business={business}>
      <Navigation business={business} />
      
      {/* Promotional Banner - Like Fuse Service */}
      <section className="bg-gradient-to-r from-red-600 to-red-700 text-white py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="font-bold text-lg">🔥 LIMITED TIME: Up to $1,200 Rebates + FREE Estimates on New HVAC Systems!</p>
        </div>
      </section>

      {/* Page Header */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl md:text-6xl font-bold mb-6">HVAC Services in Austin, TX</h1>
              <p className="text-xl md:text-2xl mb-8 opacity-95">
                Complete heating, cooling, and air quality solutions for Austin homes and businesses. 
                <span className="font-semibold"> Same-day service available!</span>
              </p>
              <div className="flex flex-wrap gap-4 text-lg mb-8">
                <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full">✓ Licensed & Insured</span>
                <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full">✓ 15+ Years Experience</span>
                <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full">✓ Up to 10 Year Warranty</span>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <a href={`tel:${business.phone}`} className="bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-lg font-bold text-xl transition-colors text-center">
                  Call {business.phone}
                </a>
                <button className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-bold text-xl transition-colors">
                  Get Free Quote
                </button>
              </div>
            </div>
            <div className="text-center">
              <div className="bg-white bg-opacity-10 rounded-2xl p-8">
                <h3 className="text-3xl font-bold mb-4">⭐ 4.9 Rating</h3>
                <p className="text-lg mb-4">Average Trust Rating Among Our Customers</p>
                <div className="grid grid-cols-1 gap-4">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">Google</span>
                    <span>4.9 ★★★★★ (200+ Reviews)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">Yelp</span>
                    <span>4.8 ★★★★★ (150+ Reviews)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">Facebook</span>
                    <span>4.9 ★★★★★ (100+ Reviews)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Special Offers - Like Fuse Service */}
      <section className="py-16 bg-yellow-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            
            {/* Rebate Offer */}
            <div className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">💰 Quality Guaranteed</h3>
              <h4 className="text-3xl font-bold mb-2">Up to $1,200</h4>
              <p className="text-lg mb-4">Austin Elite Rebate</p>
              <p className="mb-6">Your friends at Austin Elite HVAC offer incredible rebates for your new efficient equipment.</p>
              <button className="bg-white text-green-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                More Details
              </button>
            </div>

            {/* Thermostat Offer */}
            <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">🌡️ Summer Offer</h3>
              <h4 className="text-3xl font-bold mb-2">Just $99</h4>
              <p className="text-lg mb-4">Smart Thermostats</p>
              <p className="mb-6">Incredible offer from your favorite contractor—smart thermostats starting at $99.</p>
              <button className="bg-white text-orange-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                Details Here
              </button>
            </div>

            {/* Warranty Offer */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">🛡️ Top Quality</h3>
              <h4 className="text-3xl font-bold mb-2">Up to 10 Years</h4>
              <p className="text-lg mb-4">Extended Warranty</p>
              <p className="mb-6">Austin Elite HVAC offers up to 10 years of labor warranty for your residential HVAC installations.</p>
              <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                More Details
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Service Categories */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Best HVAC Services Austin</h2>
            <p className="text-gray-600 max-w-3xl mx-auto text-lg">
              <strong>Heating and Air Conditioning Services Austin, TX</strong><br/>
              We got you covered with all your heating and cooling needs. Austin Elite HVAC provides top-notch HVAC services 
              including installation, repair and maintenance of highest quality.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {serviceCategories.map((category, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border-b-4 border-blue-600">
                <div className="text-blue-600 mb-4">{category.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{category.name}</h3>
                <p className="text-gray-600 mb-4">{category.description}</p>
                <p className="text-sm text-blue-600 font-medium">{category.services.length} Services Available</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* All Services Grid */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Complete Service List</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Professional HVAC services with transparent pricing and guaranteed satisfaction
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service, index) => (
              <ServiceCard
                key={index}
                {...service}
                icon={serviceIcons[service.title as keyof typeof serviceIcons]}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Service Process */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Our Service Process</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Simple, transparent process from initial contact to completed service
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              {
                step: "1",
                title: "Contact Us",
                description: "Call, text, or book online. We respond quickly to all service requests.",
                icon: <Clock className="w-8 h-8" />
              },
              {
                step: "2", 
                title: "Schedule Service",
                description: "Choose a convenient time. We offer same-day and emergency service options.",
                icon: <CheckCircle className="w-8 h-8" />
              },
              {
                step: "3",
                title: "Expert Service",
                description: "Our certified technicians arrive on time with the tools and parts needed.",
                icon: <Wrench className="w-8 h-8" />
              },
              {
                step: "4",
                title: "Satisfaction Guaranteed",
                description: "We ensure you're completely satisfied with our work before we leave.",
                icon: <Star className="w-8 h-8" />
              }
            ].map((step, index) => (
              <div key={index} className="text-center">
                <div className="bg-blue-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                  {step.step}
                </div>
                <div className="text-blue-600 mb-4 flex justify-center">{step.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Customer Reviews - Like Fuse Service */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Don't Take Our Word for It — Check Out Our Reviews!</h2>
            <div className="text-center">
              <span className="bg-green-600 text-white px-4 py-2 rounded font-bold text-lg">EXCELLENT</span>
              <p className="text-gray-600 mt-2">Based on 450+ reviews</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <div className="bg-gray-50 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">JD</div>
                <div className="ml-4">
                  <h4 className="font-semibold">John D.</h4>
                  <div className="text-yellow-400">★★★★★</div>
                </div>
              </div>
              <p className="text-gray-700">"Very professional service! The technician was knowledgeable, on time, and provided clear explanations. Fixed our AC in no time. Would definitely recommend!"</p>
            </div>

            <div className="bg-gray-50 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center text-white font-bold">SM</div>
                <div className="ml-4">
                  <h4 className="font-semibold">Sarah M.</h4>
                  <div className="text-yellow-400">★★★★★</div>
                </div>
              </div>
              <p className="text-gray-700">"Outstanding work on our HVAC installation. The team was professional, clean, and completed the job efficiently. Great pricing too!"</p>
            </div>

            <div className="bg-gray-50 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center text-white font-bold">MR</div>
                <div className="ml-4">
                  <h4 className="font-semibold">Mike R.</h4>
                  <div className="text-yellow-400">★★★★★</div>
                </div>
              </div>
              <p className="text-gray-700">"Emergency service at 10 PM - they actually came! Fixed our heating system quickly and professionally. Highly recommend for emergency needs."</p>
            </div>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center space-x-8 bg-gray-50 rounded-xl p-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">Google</div>
                <div className="text-yellow-400 text-lg">★★★★★</div>
                <div className="text-sm text-gray-600">4.9/5 (200+ reviews)</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">Yelp</div>
                <div className="text-yellow-400 text-lg">★★★★★</div>
                <div className="text-sm text-gray-600">4.8/5 (150+ reviews)</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-800">Facebook</div>
                <div className="text-yellow-400 text-lg">★★★★★</div>
                <div className="text-sm text-gray-600">4.9/5 (100+ reviews)</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Service Guarantees */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-8">Why Choose Austin Elite HVAC</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <Shield className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Licensed & Insured</h3>
              <p>Full licensing and insurance for your protection and peace of mind.</p>
            </div>
            <div>
              <Clock className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Same-Day Service</h3>
              <p>We provide same-day HVAC service, 7 days a week, including emergencies.</p>
            </div>
            <div>
              <CheckCircle className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Up to 10 Year Warranty</h3>
              <p>Extended warranty on parts and labor for residential HVAC installations.</p>
            </div>
            <div>
              <Star className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">15+ Years Experience</h3>
              <p>Over 15 years servicing Austin and surrounding areas with 5-star service.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <ContactForm
        title="Request Service Today"
        subtitle="Get started with professional HVAC service - contact us for a free quote"
        services={services.map(s => s.title)}
        urgencyOptions={["Emergency (ASAP)", "Today", "Tomorrow", "This Week", "Just Planning"]}
      />
    </Layout>
  );
}
