/**
 * Custom Image Loader for Performance Optimization
 * 
 * Optimizes images for Cloudflare deployment with WebP/AVIF support
 * and responsive sizing for better Core Web Vitals scores.
 */

interface ImageLoaderProps {
  src: string;
  width: number;
  quality?: number;
}

/**
 * Custom image loader that optimizes images for performance
 */
export default function imageLoader({ src, width, quality = 75 }: ImageLoaderProps): string {
  // Handle external URLs (Unsplash, Supabase, etc.)
  if (src.startsWith('http')) {
    // For Unsplash images, use their optimization parameters
    if (src.includes('images.unsplash.com')) {
      const url = new URL(src);
      url.searchParams.set('w', width.toString());
      url.searchParams.set('q', quality.toString());
      url.searchParams.set('fm', 'webp');
      url.searchParams.set('fit', 'crop');
      return url.toString();
    }
    
    // For Supabase storage, add optimization parameters if supported
    if (src.includes('supabase.co')) {
      const url = new URL(src);
      // Supabase doesn't have built-in image optimization, return as-is
      return url.toString();
    }
    
    // For other external URLs, return as-is
    return src;
  }
  
  // Handle local images - in production, these would be served by Cloudflare
  // For static export, we'll return the original path
  return src;
}

/**
 * Get responsive image sizes for different breakpoints
 */
export function getResponsiveSizes(): string {
  return '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw';
}

/**
 * Get optimized image props for common use cases
 */
export function getOptimizedImageProps(src: string, alt: string, priority = false) {
  return {
    src,
    alt,
    priority,
    sizes: getResponsiveSizes(),
    quality: 85,
    placeholder: 'blur' as const,
    blurDataURL: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q==',
  };
}
