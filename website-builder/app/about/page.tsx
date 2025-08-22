'use client';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import AboutUs from '@/components/base/AboutUs';
import ContactForm from '@/components/base/ContactForm';

export default function AboutPage() {
  const business = {
    name: "Austin Elite HVAC",
    phone: "(512) 555-COOL",
    email: "service@austinelitehvac.com",
    address: "456 Tech Ridge Blvd, Austin, TX 78753",
    hours: "Mon-Fri 7AM-8PM, Sat-Sun 8AM-6PM, 24/7 Emergency Service"
  };

  const seo = {
    title: "About Austin Elite HVAC | 25+ Years of Professional HVAC Service",
    description: "Learn about Austin Elite HVAC's 25+ years of professional HVAC service in Austin, TX. Licensed, insured, and NATE-certified technicians you can trust.",
    keywords: ["about austin elite hvac", "hvac company austin", "licensed hvac contractor", "nate certified technicians"]
  };

  return (
    <Layout seo={seo} business={business}>
      <Navigation business={business} />
      
      {/* Page Header */}
      <section className="bg-gradient-to-r from-blue-600 to-green-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">About {business.name}</h1>
          <p className="text-xl md:text-2xl mb-6 max-w-3xl mx-auto">
            Your trusted HVAC partner in Austin for over 25 years
          </p>
        </div>
      </section>

      {/* About Us Component */}
      <AboutUs 
        business={{
          name: business.name,
          description: "For over 25 years, Austin Elite HVAC has been Austin's trusted HVAC experts, providing reliable heating and cooling solutions for homes and businesses throughout the area."
        }}
        stats={{
          yearsInBusiness: 25,
          customersServed: 5000,
          projectsCompleted: 8500,
          satisfactionRate: 98
        }}
      />

      {/* Contact Form */}
      <ContactForm
        title="Ready to Experience the Austin Elite Difference?"
        subtitle="Contact us today to learn more about our services or schedule your appointment"
        services={["AC Repair", "Heating Repair", "New Installation", "Maintenance", "Consultation"]}
        urgencyOptions={["Emergency (ASAP)", "Today", "Tomorrow", "This Week", "Just Planning"]}
      />
    </Layout>
  );
}
