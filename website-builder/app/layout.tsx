import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import PerformanceOptimizer from "../components/performance/PerformanceOptimizer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Professional HVAC Services | 24/7 Emergency Repair & Installation",
  description: "Expert HVAC services with 20+ years of experience. Same-day repairs, energy-efficient installations, and preventive maintenance. Licensed & insured. Book online or call (555) 123-4567.",
  manifest: "/manifest.json",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#667eea",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const businessName = process.env.NEXT_PUBLIC_BUSINESS_NAME || "Professional Services";
  
  return (
    <html lang="en">
      <head>
        <PerformanceOptimizer
          businessName={businessName}
          criticalResources={['/globals.css']}
          preloadFonts={[
            'https://fonts.gstatic.com/s/geist/v1/UcC73FwrK3iLTeHuS_fvQtMwCp50KnMa2JL7W0Q5n-wU.woff2'
          ]}
          enableServiceWorker={true}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning={true}
      >
        {children}
      </body>
    </html>
  );
}
