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

  const services = [
    {
      title: "Emergency AC Repair",
      description: "24/7 emergency air conditioning repair throughout Austin metro. Fast response, expert diagnosis, and reliable repairs for all AC brands and models.",
      price: "From $99",
      features: ["Same-day service", "All major brands", "Parts warranty", "Upfront pricing"],
      isPopular: true,
      isEmergency: true
    },
    {
      title: "Heating System Service",
      description: "Complete heating system repair and maintenance in Austin. Furnace repair, heat pump service, and emergency heating solutions.",
      price: "From $89",
      features: ["Safety inspection", "Energy efficiency check", "Emergency service", "All heating types"]
    },
    {
      title: "HVAC Installation",
      description: "Professional HVAC system installation in Austin. Energy-efficient systems with expert installation and comprehensive warranties.",
      price: "Free Quote",
      features: ["Energy-efficient systems", "Professional installation", "10-year warranty", "Financing available"]
    },
    {
      title: "Preventive Maintenance",
      description: "Comprehensive HVAC maintenance plans for Austin homes and businesses. Extend system life and improve efficiency with regular service.",
      price: "$25/month",
      features: ["Bi-annual tune-ups", "Priority service", "20% off repairs", "Energy savings"]
    },
    {
      title: "Air Quality Solutions",
      description: "Indoor air quality testing and improvement solutions. Air purifiers, humidity control, and duct cleaning services.",
      price: "From $149",
      features: ["Air quality testing", "Purification systems", "Humidity control", "Duct cleaning"]
    },
    {
      title: "Ductwork Services",
      description: "Professional ductwork installation, repair, and cleaning. Improve efficiency and air quality with proper ductwork.",
      price: "Free Inspection",
      features: ["Duct inspection", "Sealing & repair", "New installation", "Energy efficiency"]
    }
  ];

  const serviceCategories = [
    {
      name: "Emergency Services",
      description: "24/7 emergency HVAC repair and service",
      services: services.filter(s => s.isEmergency),
      icon: <Clock className="w-8 h-8" />
    },
    {
      name: "Repair Services",
      description: "Professional HVAC repair and troubleshooting",
      services: services.filter(s => s.title.includes("Repair") || s.title.includes("Service")),
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
      services: services.filter(s => s.title.includes("Maintenance") || s.title.includes("Air Quality") || s.title.includes("Ductwork")),
      icon: <CheckCircle className="w-8 h-8" />
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

  return (
    <Layout seo={seo} business={business}>
      <Navigation business={business} />
      
      {/* Page Header */}
      <section className="bg-gradient-to-r from-blue-600 to-green-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Our HVAC Services</h1>
          <p className="text-xl md:text-2xl mb-6 max-w-3xl mx-auto">
            Complete heating, cooling, and air quality solutions for Austin homes and businesses
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-lg">
            <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full">✓ Licensed & Insured</span>
            <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full">✓ 24/7 Emergency Service</span>
            <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full">✓ 100% Satisfaction Guarantee</span>
          </div>
        </div>
      </section>

      {/* Service Categories */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Service Categories</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              We offer comprehensive HVAC services organized by category to help you find exactly what you need
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {serviceCategories.map((category, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300">
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

      {/* Service Guarantees */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-8">Our Service Guarantees</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <Shield className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">100% Satisfaction</h3>
              <p>We guarantee your complete satisfaction with our work or we'll make it right.</p>
            </div>
            <div>
              <Clock className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">On-Time Service</h3>
              <p>We arrive when scheduled and complete work within the estimated timeframe.</p>
            </div>
            <div>
              <CheckCircle className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Quality Parts</h3>
              <p>We use only high-quality parts and materials backed by comprehensive warranties.</p>
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
