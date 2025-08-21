
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
                <section className="hero-gradient section-padding min-h-screen flex items-center">
          <div className="container-custom">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div className="text-center lg:text-left">
                <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 animate-fade-in">
                  New York's Trusted Plumbing Experts - 24/7 Emergency Service
                </h1>
                <p className="text-xl text-gray-600 mb-8 max-w-2xl animate-fade-in-up">
                  Licensed, insured, and ready to solve your plumbing problems fast. Serving NYC and Brooklyn with upfront pricing and guaranteed workmanship since 2010.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start animate-fade-in-up">
                  <button 
                    className="btn btn-primary"
                    onClick={() => window.location.href = 'tel:555-123-4567'}
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                    </svg>
                    Call (555) 123-4567
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Get Free Quote
                  </button>
                </div>
              </div>
              <div className="hidden lg:block">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-2xl transform rotate-6"></div>
                  <div className="relative bg-white p-8 rounded-2xl shadow-2xl">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Professional Service</h3>
                      <p className="text-gray-600">Licensed & Insured</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="emergency">\n          <h2>Emergency Service</h2>\n        </section>
        <section className="section-padding bg-gray-50">
          <div className="container-custom">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Our Services</h2>
            </div>
          </div>
        </section>
        <section id="contact" className="section-padding bg-primary-600">
          <div className="container-custom">
            <div className="text-center text-white">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Get a Quote</h2>
              <p className="text-xl mb-8">Contact us for a free estimate</p>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}