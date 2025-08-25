import { Inter, Poppins } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap'
})

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-poppins',
  display: 'swap'
})

interface LayoutProps {
  children: React.ReactNode;
  seo?: {
    title: string;
    description: string;
    keywords?: string[];
  };
  business: {
    name: string;
    phone: string;
    email: string;
    address: string;
    hours: string;
    serviceAreas?: string[];
  };
}

export default function ProfessionalLayout({ children, seo, business }: LayoutProps) {
  const title = seo?.title || `${business.name} - Professional HVAC Services`
  const description = seo?.description || `${business.name} provides professional HVAC services including air conditioning, heating, installation and maintenance. Licensed & insured with 24/7 emergency service.`

  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <head>
        <title>{title}</title>
        <meta name="description" content={description} />
        {seo?.keywords && (
          <meta name="keywords" content={seo.keywords.join(', ')} />
        )}
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Structured Data for Local Business */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "LocalBusiness",
              "name": business.name,
              "telephone": business.phone,
              "email": business.email,
              "address": {
                "@type": "PostalAddress",
                "streetAddress": business.address
              }
            })
          }}
        />
      </head>
      <body className={`${inter.className} antialiased bg-white text-gray-900`}>
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  )
}
