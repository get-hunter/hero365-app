/**
 * Hook for fetching website context data from the new API
 * 
 * This hook integrates with the Website Context Aggregator endpoint
 * to fetch all data needed for website generation in a single call.
 */

'use client';

import { useState, useEffect } from 'react';

export interface WebsiteBusinessInfo {
  id: string;
  name: string;
  description?: string;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  website?: string;
  primary_trade_slug?: string;
  service_areas: string[];
}

export interface WebsiteBookingField {
  key: string;
  type: string;
  label: string;
  options?: string[];
  required: boolean;
  placeholder?: string;
  help_text?: string;
}

export interface WebsiteActivityInfo {
  slug: string;
  name: string;
  trade_slug: string;
  trade_name: string;
  synonyms: string[];
  tags: string[];
  default_booking_fields: WebsiteBookingField[];
  required_booking_fields: WebsiteBookingField[];
}

export interface WebsiteServiceTemplate {
  template_slug: string;
  name: string;
  description?: string;
  pricing_model: string;
  pricing_config: Record<string, any>;
  unit_of_measure?: string;
  is_emergency: boolean;
  activity_slug?: string;
}

export interface WebsiteTradeInfo {
  slug: string;
  name: string;
  description?: string;
  segments: string;
  icon?: string;
}

export interface WebsiteContextData {
  business: WebsiteBusinessInfo;
  activities: WebsiteActivityInfo[];
  service_templates: WebsiteServiceTemplate[];
  trades: WebsiteTradeInfo[];
  metadata: {
    generated_at?: string;
    total_activities: number;
    total_templates: number;
    total_trades: number;
    primary_trade?: string;
  };
}

interface UseWebsiteContextOptions {
  include_templates?: boolean;
  include_trades?: boolean;
  activity_limit?: number;
  template_limit?: number;
}

interface UseWebsiteContextReturn {
  data: WebsiteContextData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Custom hook to fetch website context data
 */
export function useWebsiteContext(
  businessId: string,
  options: UseWebsiteContextOptions = {}
): UseWebsiteContextReturn {
  const [data, setData] = useState<WebsiteContextData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!businessId) {
      setError('Business ID is required');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (options.include_templates !== undefined) {
        params.append('include_templates', options.include_templates.toString());
      }
      if (options.include_trades !== undefined) {
        params.append('include_trades', options.include_trades.toString());
      }
      if (options.activity_limit !== undefined) {
        params.append('activity_limit', options.activity_limit.toString());
      }
      if (options.template_limit !== undefined) {
        params.append('template_limit', options.template_limit.toString());
      }

      const { getBackendUrl, getDefaultHeaders } = await import('@/lib/shared/config/api-config');
      const backendUrl = getBackendUrl();
      const url = `${backendUrl}/api/v1/public/contractors/website/context/${businessId}${
        params.toString() ? `?${params.toString()}` : ''
      }`;

      const response = await fetch(url, { headers: getDefaultHeaders() });
      if (!response.ok) {
        throw new Error(`Failed to fetch website context: ${response.statusText}`);
      }

      const contextData = await response.json();
      setData(contextData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [businessId, JSON.stringify(options)]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

/**
 * Hook to fetch only activities (lightweight)
 */
export function useWebsiteActivities(
  businessId: string,
  limit?: number
): UseWebsiteContextReturn {
  const [data, setData] = useState<WebsiteContextData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!businessId) {
      setError('Business ID is required');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (limit !== undefined) {
        params.append('limit', limit.toString());
      }

      const { getBackendUrl, getDefaultHeaders } = await import('@/lib/shared/config/api-config');
      const backendUrl = getBackendUrl();
      const url = `${backendUrl}/api/v1/public/contractors/website/context/${businessId}/activities${
        params.toString() ? `?${params.toString()}` : ''
      }`;

      const response = await fetch(url, { headers: getDefaultHeaders() });
      if (!response.ok) {
        throw new Error(`Failed to fetch activities: ${response.statusText}`);
      }

      const activitiesData = await response.json();
      setData({
        business: { id: businessId } as WebsiteBusinessInfo,
        activities: activitiesData.activities,
        service_templates: [],
        trades: [],
        metadata: {
          total_activities: activitiesData.total_activities,
          total_templates: 0,
          total_trades: 0
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [businessId, limit]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

/**
 * Hook to fetch activity content pack
 */
export function useActivityContentPack(activitySlug: string) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!activitySlug) {
      setError('Activity slug is required');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const { getBackendUrl, getDefaultHeaders } = await import('@/lib/shared/config/api-config');
      const backendUrl = getBackendUrl();
      const response = await fetch(`${backendUrl}/api/v1/activity-content/public/content-packs/${activitySlug}`, {
        headers: getDefaultHeaders()
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch content pack: ${response.statusText}`);
      }

      const contentPack = await response.json();
      setData(contentPack);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activitySlug]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}
