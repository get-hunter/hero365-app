import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
  seo?: {
    title?: string;
    description?: string;
    keywords?: string[];
    ogImage?: string;
  };
  business?: {
    name: string;
    phone?: string;
    email?: string;
    address?: string;
  };
  theme?: {
    primaryColor?: string;
    secondaryColor?: string;
    fontFamily?: string;
  };
}

export default function Layout({ children, seo, business, theme }: LayoutProps) {
  const title = seo?.title || `${business?.name || 'Hero365'} - Professional Services`;
  const description = seo?.description || `Professional services from ${business?.name || 'Hero365'}`;
  
  return (
    <>
      {/* For Next.js 13+ App Router, metadata should be handled differently */}
      {/* We'll inject these as inline elements for now */}
      {theme && (
        <style>{`
          :root {
            --primary-color: ${theme.primaryColor || '#3B82F6'};
            --secondary-color: ${theme.secondaryColor || '#10B981'};
            --font-family: ${theme.fontFamily || 'system-ui, -apple-system, sans-serif'};
          }
        `}</style>
      )}
      
      {/* Schema.org markup for local business */}
      {business && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'LocalBusiness',
              name: business.name,
              telephone: business.phone,
              email: business.email,
              address: {
                '@type': 'PostalAddress',
                streetAddress: business.address,
              },
            }),
          }}
        />
      )}
      
      <div className="min-h-screen flex flex-col" style={{ fontFamily: 'var(--font-family)' }}>
        {children}
      </div>
    </>
  );
}
