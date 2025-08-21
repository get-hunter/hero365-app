
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
                Schedule Service Now
              </button>
              <button className="btn btn-secondary" onClick={() => window.location.href = '#contact'}>
                View Our Services
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
        <section className="quick-quote">\n          <h2>Get a Quote</h2>\n        </section>
      </main>
    </>
  );
}