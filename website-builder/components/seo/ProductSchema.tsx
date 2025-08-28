import React from 'react';
import Script from 'next/script';

type ProductSchemaProps = {
  product: any;
  offer?: any;
  seller?: any;
  review?: any;
  pageUrl?: string;
};

export default function ProductSchema({ product, offer, seller, review, pageUrl }: ProductSchemaProps) {
  if (!product) return null;

  const images: string[] = [];
  if (Array.isArray(product.images)) images.push(...product.images);
  if (product.featuredImage) images.unshift(product.featuredImage);
  if (product.featured_image_url) images.unshift(product.featured_image_url);

  const data: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description || product.long_description || '',
    brand: product.brand ? { '@type': 'Brand', name: product.brand } : undefined,
    model: product.model || product.sku,
    sku: product.sku,
    category: product.category || product.category_name,
    image: images.length ? images : undefined,
    url: pageUrl,
    additionalProperty: product.specifications || product.technical_specs || undefined,
  };

  if (offer) {
    data.offers = {
      '@type': 'Offer',
      priceCurrency: offer.priceCurrency || 'USD',
      price: offer.price,
      availability:
        typeof offer.availability === 'string' && offer.availability.startsWith('http')
          ? offer.availability
          : `https://schema.org/${offer.availability || 'InStock'}`,
      priceValidUntil: offer.priceValidUntil,
      seller: seller
        ? { '@type': 'Organization', name: seller.name, telephone: seller.telephone, url: seller.url }
        : undefined,
      url: pageUrl,
    };
  }

  if (review) {
    data.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: review.rating,
      reviewCount: review.reviewCount,
      bestRating: review.bestRating || 5,
      worstRating: review.worstRating || 1,
    };
  }

  return (
    <Script
      id={`product-schema-${product.sku || product.id || 'product'}`}
      type="application/ld+json"
      strategy="afterInteractive"
    >
      {JSON.stringify(data)}
    </Script>
  );
}


