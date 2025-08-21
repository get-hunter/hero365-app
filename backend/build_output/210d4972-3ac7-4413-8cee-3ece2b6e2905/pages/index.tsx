
import React from 'react';
import Head from 'next/head';

export default function HomePage() {
  return (
    <>
      <Head>
        <title>ComfortZone HVAC - Home</title>
        <meta name="description" content="" />
        <meta name="keywords" content="" />
        <meta property="og:title" content="" />
        <meta property="og:description" content="" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        
      </Head>
      
      <main className="page-home">
                <section className="hero">
          <div className="hero-content">
            <h1 className="hero-headline">Welcome</h1>
            <p className="hero-subtitle"></p>
            <div className="hero-cta">
              <button className="btn btn-primary" onClick={() => window.location.href = 'tel:+1-555-TEST-123'}>
                Schedule Service
              </button>
              <button className="btn btn-secondary" onClick={() => window.location.href = '#contact'}>
                Free Estimate
              </button>
            </div>
          </div>
        </section>
        <section className="emergency">
          <div className="container">
            <h2>24/7 Emergency Service</h2>
            <p>Available for emergency repairs</p>
            <button className="btn btn-emergency" onClick={() => window.location.href = 'tel:+1-555-TEST-123'}>
              Call Now: +1-555-TEST-123
            </button>
          </div>
        </section>
        <section className="services">\n          <h2>Our Services</h2>\n        </section>
        <section className="seasonal-focus">\n          <h2>Seasonal-Focus</h2>\n        </section>
        <section className="booking-widget">\n          <h2>Booking-Widget</h2>\n        </section>
        <section className="financing-options">\n          <h2>Financing-Options</h2>\n        </section>
        <section className="testimonials">\n          <h2>Testimonials</h2>\n        </section>
        <section className="contact-form">\n          <h2>Contact-Form</h2>\n        </section>
      </main>
    </>
  );
}