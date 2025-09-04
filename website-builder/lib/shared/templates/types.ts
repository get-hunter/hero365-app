export interface ActivityContentPack {
  hero: {
    title: string;
    subtitle?: string;
    ctaLabel?: string;
    icon?: string;
  };
  benefits: {
    heading: string;
    bullets: string[];
  };
  process: {
    heading: string;
    steps: string[];
  };
  faqs: {
    q: string;
    a: string;
  }[];
  seo: {
    titleTemplate: string;
    descriptionTemplate: string;
    keywords: string[];
  };
  schema: {
    serviceType: string;
    description: string;
    category?: string;
  };
  pricing?: {
    startingPrice?: number;
    priceRange?: string;
    unit?: string;
  };
}

export interface BusinessActivityData {
  activity_slug: string;
  activity_name: string;
  trade_slug: string;
  trade_name: string;
  service_templates: {
    template_slug: string;
    name: string;
    pricing_model: string;
    pricing_config: any;
  }[];
  booking_fields: {
    key: string;
    type: string;
    label: string;
    options?: string[];
    required?: boolean;
  }[];
}

export interface ActivityPageData {
  activity: BusinessActivityData;
  content: ActivityContentPack;
  business: {
    name: string;
    phone: string;
    email: string;
    address: string;
    city: string;
    state: string;
    postal_code: string;
    service_areas: string[];
  };
}