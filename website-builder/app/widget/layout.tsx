/**
 * Widget Layout
 * 
 * Minimal layout for embeddable widgets
 */

import type { Metadata } from 'next';
import '../globals.css';

export const metadata: Metadata = {
  title: 'Hero365 Booking Widget',
  description: 'Book your service appointment online',
  robots: 'noindex, nofollow', // Prevent indexing of widget pages
};

export default function WidgetLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Prevent iframe clickjacking */}
        <meta httpEquiv="X-Frame-Options" content="SAMEORIGIN" />
        <meta httpEquiv="Content-Security-Policy" content="frame-ancestors 'self' *" />
        
        {/* Widget-specific meta tags */}
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#3b82f6" />
      </head>
      <body className="font-sans antialiased">
        {children}
        
        {/* Widget communication script */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Listen for messages from parent window
              window.addEventListener('message', function(event) {
                if (event.data.type === 'HERO365_WIDGET_CONFIG') {
                  // Handle configuration updates from parent
                  console.log('Widget config received:', event.data.config);
                }
              });
              
              // Notify parent that widget is ready
              if (window.parent !== window) {
                window.parent.postMessage({
                  type: 'HERO365_WIDGET_READY'
                }, '*');
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
