import React from 'react'

interface SEOPageData {
  title: string
  meta_description: string
  h1_heading: string
  content: string
  schema_markup: any
  target_keywords: string[]
  page_url: string
  generation_method: 'template' | 'llm' | 'fallback'
  page_type: string
  word_count: number
  created_at: string
}

interface SEOPageProps {
  data: SEOPageData
}

export default function SEOPage({ data }: SEOPageProps) {
  return (
    <>
      {/* Schema Markup for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(data.schema_markup) }}
      />
      
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <article className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
            {/* Page Header */}
            <header className="mb-8">
              <h1 className="text-4xl font-bold text-gray-900 mb-4 leading-tight">
                {data.h1_heading}
              </h1>
              
              {/* Generation Method Badge */}
              <div className="flex items-center gap-2 mb-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  data.generation_method === 'llm' 
                    ? 'bg-purple-100 text-purple-800' 
                    : data.generation_method === 'template'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {data.generation_method === 'llm' ? '🧠 AI Enhanced' : 
                   data.generation_method === 'template' ? '⚡ Smart Template' : 
                   '🔄 Fallback'}
                </span>
                <span className="text-sm text-gray-500">
                  {data.word_count} words • {data.page_type}
                </span>
              </div>
            </header>
            
            {/* Page Content */}
            <div 
              className="prose prose-lg max-w-none mb-8"
              dangerouslySetInnerHTML={{ __html: data.content }}
            />
            
            {/* Call-to-Action Section */}
            <div className="mt-12 p-6 bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg text-white">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-4">Ready to Get Started?</h3>
                <p className="text-lg mb-6 opacity-90">
                  Contact us today for professional service and a free estimate.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <a 
                    href="tel:(512) 555-0100" 
                    className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-3 px-8 rounded-lg text-lg transition-colors"
                  >
                    📞 Call Now: (512) 555-0100
                  </a>
                  <a 
                    href="#contact" 
                    className="bg-white hover:bg-gray-100 text-blue-800 font-bold py-3 px-8 rounded-lg text-lg transition-colors"
                  >
                    💬 Get Free Estimate
                  </a>
                </div>
              </div>
            </div>
            
            {/* Trust Signals */}
            <div className="mt-8 grid md:grid-cols-3 gap-6 text-center">
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl mb-2">✅</div>
                <h4 className="font-bold text-green-800">Licensed & Insured</h4>
                <p className="text-sm text-green-600">Fully licensed and insured for your protection</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl mb-2">🏆</div>
                <h4 className="font-bold text-blue-800">15+ Years Experience</h4>
                <p className="text-sm text-blue-600">Trusted by thousands of satisfied customers</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl mb-2">⚡</div>
                <h4 className="font-bold text-purple-800">Same-Day Service</h4>
                <p className="text-sm text-purple-600">Fast response when you need it most</p>
              </div>
            </div>
            
            {/* SEO Keywords (hidden, for SEO purposes) */}
            <div className="sr-only">
              Keywords: {data.target_keywords.join(', ')}
            </div>
          </article>
          
          {/* Contact Form Section */}
          <div id="contact" className="max-w-2xl mx-auto mt-12 bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-3xl font-bold text-center mb-8 text-gray-900">
              Get Your Free Estimate
            </h2>
            
            <form className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                    First Name *
                  </label>
                  <input
                    type="text"
                    id="firstName"
                    name="firstName"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your first name"
                  />
                </div>
                <div>
                  <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    id="lastName"
                    name="lastName"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your last name"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your email address"
                />
              </div>
              
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="(555) 123-4567"
                />
              </div>
              
              <div>
                <label htmlFor="service" className="block text-sm font-medium text-gray-700 mb-2">
                  Service Needed
                </label>
                <select
                  id="service"
                  name="service"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select a service</option>
                  <option value="hvac-repair">HVAC Repair</option>
                  <option value="ac-repair">AC Repair</option>
                  <option value="heating-repair">Heating Repair</option>
                  <option value="installation">New Installation</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="emergency">Emergency Service</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                  Project Description
                </label>
                <textarea
                  id="message"
                  name="message"
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Please describe your project or service needs..."
                />
              </div>
              
              <div className="text-center">
                <button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors"
                >
                  🚀 Get My Free Estimate
                </button>
                <p className="mt-2 text-sm text-gray-500">
                  We'll respond within 1 hour during business hours
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  )
}
