import type { Metadata, Viewport } from "next";
import "./globals.css";
// Use system fonts to avoid next/font server manifest during build

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

export const runtime: 'edge' | 'nodejs' = 'nodejs'
export const dynamic = 'force-dynamic'
export const revalidate = 0

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head></head>
      <body
        className={`antialiased`}
        suppressHydrationWarning={true}
      >
        {children}
      </body>
    </html>
  );
}
