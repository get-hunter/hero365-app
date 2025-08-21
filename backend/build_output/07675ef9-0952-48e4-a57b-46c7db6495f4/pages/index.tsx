
import React from 'react';
import Head from 'next/head';

export default function HomePage() {
  return (
    <>
      <Head>
        <title>QuickFix Plumbing - Home</title>
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
                Call Now: (555) TEST-123
              </button>
              <button className="btn btn-secondary" onClick={() => window.location.href = '#contact'}>
                Schedule Service Online
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
        <section className="services">
          <div className="container">
            <h2>Our Comprehensive Plumbing Services</h2>
            <div className="services-grid">
              
            <div className="service-item">
              <h3>Emergency Plumbing</h3>
              <p>24/7 emergency response for urgent plumbing issues. Fast service when you need it most.</p>
            </div>
            <div className="service-item">
              <h3>Drain Cleaning</h3>
              <p>Professional drain cleaning services using advanced equipment and techniques.</p>
            </div>
            <div className="service-item">
              <h3>Water Heater Services</h3>
              <p>Installation, repair, and maintenance for all types of water heaters.</p>
            </div>
            <div className="service-item">
              <h3>Fixture Installation</h3>
              <p>Expert installation of all bathroom and kitchen fixtures.</p>
            </div>
            <div className="service-item">
              <h3>Leak Detection</h3>
              <p>Advanced leak detection and repair services for all plumbing systems.</p>
            </div>
            <div className="service-item">
              <h3>Pipe Services</h3>
              <p>Complete pipe repair, replacement, and installation services.</p>
            </div>
            </div>
          </div>
        </section>
        <section className="quick-quote">
          <div className="container">
            <h2>Tell Us About Your Project</h2>
            <p>Contact us for a free estimate</p>
            <button className="btn btn-primary" onClick={() => window.location.href = 'tel:+1-555-TEST-123'}>
              Call Now
            </button>
          </div>
        </section>
      </main>
    </>
  );
}