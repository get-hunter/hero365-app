
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
                <section className="hero">\n          <h1>Welcome</h1>\n        </section>
        <section className="emergency-banner">\n          <h2>Emergency-Banner</h2>\n        </section>
        <section className="services-grid">\n          <h2>Services-Grid</h2>\n        </section>
        <section className="seasonal-focus">\n          <h2>Seasonal-Focus</h2>\n        </section>
        <section className="booking-widget">\n          <h2>Booking-Widget</h2>\n        </section>
        <section className="financing-options">\n          <h2>Financing-Options</h2>\n        </section>
        <section className="testimonials">\n          <h2>Testimonials</h2>\n        </section>
        <section className="contact-form">\n          <h2>Contact-Form</h2>\n        </section>
      </main>
    </>
  );
}