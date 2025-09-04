/**
 * Structured Data Renderer Component
 * 
 * Renders JSON-LD structured data schemas for SEO.
 */

'use client';

import React from 'react';

interface StructuredDataRendererProps {
  schemas: Array<Record<string, any>>;
}

export function StructuredDataRenderer({ schemas }: StructuredDataRendererProps) {
  if (!schemas || schemas.length === 0) {
    return null;
  }

  return (
    <>
      {schemas.map((schema, index) => (
        <script
          key={index}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(schema, null, 0)
          }}
        />
      ))}
    </>
  );
}
