
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
                <section className="hero">\n          <h1>Welcome</h1>\n        </section>
        <section className="emergency-banner">\n          <h2>Emergency-Banner</h2>\n        </section>
        <section className="services-grid">\n          <h2>Services-Grid</h2>\n        </section>
        <section className="quick-quote">\n          <h2>Quick-Quote</h2>\n        </section>
      </main>
    </>
  );
}