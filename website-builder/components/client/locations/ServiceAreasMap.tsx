'use client';

import React, { useEffect, useMemo, useRef } from 'react';

declare global {
  interface Window {
    L: any;
  }
}

interface BasicLocation {
  slug: string;
  name?: string;
  city?: string;
  state?: string;
  service_radius_miles?: number;
  is_primary?: boolean;
  postal_codes?: string[] | null;
}

interface ServiceAreasMapProps {
  locations: BasicLocation[];
  className?: string;
  defaultCenter?: { lat: number; lng: number };
  defaultRadiusMiles?: number;
}

/**
 * Lightweight Leaflet map (CDN-loaded) to render colored service areas as circles.
 * Avoids bundling dependencies; runs only on client.
 */
export default function ServiceAreasMap({
  locations,
  className = '',
  defaultCenter = { lat: 30.2672, lng: -97.7431 }, // Austin, TX
  defaultRadiusMiles = 25
}: ServiceAreasMapProps) {
  const mapRef = useRef<HTMLDivElement | null>(null);

  // Known Austin-metro coordinates for common slugs
  const slugToLatLng: Record<string, { lat: number; lng: number }> = useMemo(() => ({
    'austin-tx': { lat: 30.2672, lng: -97.7431 },
    'round-rock-tx': { lat: 30.5083, lng: -97.6789 },
    'cedar-park-tx': { lat: 30.5052, lng: -97.8203 },
    'pflugerville-tx': { lat: 30.4394, lng: -97.6200 },
    'leander-tx': { lat: 30.5780, lng: -97.8531 },
    'georgetown-tx': { lat: 30.6333, lng: -97.6770 },
    'lakeway-tx': { lat: 30.3679, lng: -97.9961 },
    'bee-cave-tx': { lat: 30.3099, lng: -97.9411 },
    'west-lake-hills-tx': { lat: 30.2877, lng: -97.8017 },
    'rollingwood-tx': { lat: 30.2758, lng: -97.7897 }
  }), []);

  // Palette for area fills
  const palette = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316', '#22c55e'];

  useEffect(() => {
    if (!mapRef.current) return;
    if (typeof window === 'undefined') return;

    // Inject Leaflet CSS & JS via CDN if not already present
    const ensureLeafletAssets = async () => {
      const cssId = 'leaflet-css-cdn';
      const jsId = 'leaflet-js-cdn';

      if (!document.getElementById(cssId)) {
        const link = document.createElement('link');
        link.id = cssId;
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
      }

      if (!document.getElementById(jsId)) {
        await new Promise<void>((resolve, reject) => {
          const script = document.createElement('script');
          script.id = jsId;
          script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
          script.async = true;
          script.onload = () => resolve();
          script.onerror = () => reject(new Error('Failed to load Leaflet JS'));
          document.body.appendChild(script);
        });
      }
    };

    let map: any;
    let layers: any[] = [];

    const initMap = () => {
      const L = window.L;
      if (!L) return;

      // Create map
      map = L.map(mapRef.current!, {
        center: [defaultCenter.lat, defaultCenter.lng],
        zoom: 10,
        scrollWheelZoom: false
      });

      // Tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      // Draw service areas
      const bounds = L.latLngBounds();
      const meterPerMile = 1609.34;

      locations.forEach((loc, index) => {
        const slug = (loc.slug || '').toLowerCase();
        const center = slugToLatLng[slug] || defaultCenter;
        const radiusMiles = loc.service_radius_miles || defaultRadiusMiles;
        const color = palette[index % palette.length];

        // If we have postal codes, attempt to shade them using GeoJSON
        const postalCodes = Array.isArray(loc.postal_codes) ? loc.postal_codes : [];
        if (postalCodes.length > 0) {
          console.log(`🗺️ Loading postal codes for ${loc.name}:`, postalCodes);
          
          // Try multiple GeoJSON sources for Texas postal codes
          const geoUrls = [
            'https://cdn.jsdelivr.net/gh/OpenDataDE/State-zip-code-GeoJSON/tx_texas_zip_codes_geo.min.json',
            'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/tx_texas_zip_codes_geo.min.json'
          ];
          
          const tryLoadGeoJSON = async (urls: string[]): Promise<any> => {
            for (const url of urls) {
              try {
                console.log(`🌐 Trying GeoJSON source: ${url}`);
                const response = await fetch(url);
                if (response.ok) {
                  const data = await response.json();
                  console.log(`✅ Successfully loaded GeoJSON from: ${url}`);
                  return data;
                }
              } catch (error) {
                console.warn(`⚠️ Failed to load from ${url}:`, error);
              }
            }
            throw new Error('All GeoJSON sources failed');
          };
          
          tryLoadGeoJSON(geoUrls)
            .then((geo) => {
              // Try different property names for postal codes
              const features = geo.features.filter((f: any) => {
                const zipCode = f.properties.ZCTA5CE10 || f.properties.ZIPCODE || f.properties.ZIP || f.properties.GEOID10;
                return zipCode && postalCodes.includes(String(zipCode));
              });
              
              console.log(`🎯 Found ${features.length} matching postal code polygons out of ${postalCodes.length} requested`);
              
              if (features.length > 0) {
                const geoLayer = L.geoJSON({ type: 'FeatureCollection', features }, {
                  style: {
                    color,
                    weight: 2,
                    fillColor: color,
                    fillOpacity: 0.3,
                    opacity: 0.8
                  },
                  onEachFeature: (feature, layer) => {
                    const zipCode = feature.properties.ZCTA5CE10 || feature.properties.ZIPCODE || feature.properties.ZIP || feature.properties.GEOID10;
                    layer.bindPopup(`${loc.name}<br>Postal Code: ${zipCode}`);
                  }
                }).addTo(map);
                layers.push(geoLayer);
                geoLayer.getLayers().forEach((layer: any) => bounds.extend(layer.getBounds()));
              } else {
                console.log(`⚠️ No postal code polygons found, falling back to circle for ${loc.name}`);
                const circle = L.circle([center.lat, center.lng], {
                  radius: radiusMiles * meterPerMile,
                  color,
                  weight: 2,
                  fillColor: color,
                  fillOpacity: 0.2
                }).addTo(map);
                layers.push(circle);
                bounds.extend(circle.getBounds());
              }
            })
            .catch((error) => {
              console.error(`❌ Failed to load postal code data for ${loc.name}:`, error);
              console.log(`🔄 Falling back to circle coverage for ${loc.name}`);
              const circle = L.circle([center.lat, center.lng], {
                radius: radiusMiles * meterPerMile,
                color,
                weight: 2,
                fillColor: color,
                fillOpacity: 0.2
              }).addTo(map);
              layers.push(circle);
              bounds.extend(circle.getBounds());
            });
        } else {
          console.log(`📍 No postal codes for ${loc.name}, using radius coverage`);
          const circle = L.circle([center.lat, center.lng], {
            radius: radiusMiles * meterPerMile,
            color,
            weight: 2,
            fillColor: color,
            fillOpacity: 0.2
          }).addTo(map);
          layers.push(circle);
          bounds.extend(circle.getBounds());
        }

        // Markers removed - postal code polygons provide better visual representation
      });

      if (locations.length > 0) {
        map.fitBounds(bounds.pad(0.1));
      }

      // Add a simple legend
      const legend = L.control({ position: 'bottomright' });
      legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'leaflet-control-layers');
        div.style.backgroundColor = 'white';
        div.style.padding = '8px';
        div.style.borderRadius = '4px';
        div.style.fontSize = '12px';
        div.style.boxShadow = '0 1px 5px rgba(0,0,0,0.2)';
        
        let legendHTML = '<strong>Service Areas</strong><br>';
        locations.forEach((loc, index) => {
          const color = palette[index % palette.length];
          const hasPostalCodes = Array.isArray(loc.postal_codes) && loc.postal_codes.length > 0;
          const shape = hasPostalCodes ? '■' : '●';
          legendHTML += `<div style="margin: 2px 0;"><span style="color: ${color}; font-size: 14px;">${shape}</span> ${loc.name}</div>`;
        });
        
        div.innerHTML = legendHTML;
        return div;
      };
      legend.addTo(map);
    };

    ensureLeafletAssets()
      .then(() => {
        initMap();
      })
      .catch(() => {
        // Fail silently; keep page functional without map
      });

    return () => {
      try {
        if (layers.length) {
          layers.forEach((l) => l.remove());
        }
        if (map) {
          map.remove();
        }
      } catch {}
    };
  }, [locations, defaultCenter, slugToLatLng, palette, defaultRadiusMiles]);

  return (
    <div className={className}>
      <div ref={mapRef} className="w-full h-96 rounded-lg border border-gray-200 shadow-sm overflow-hidden" />
    </div>
  );
}


