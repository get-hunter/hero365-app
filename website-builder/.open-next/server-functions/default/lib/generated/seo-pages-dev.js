// Development-only SEO pages for server-side rendering
const seoPages = {
  "/services/hvac-repair/austin-tx": {
    title: "HVAC Repair in Austin, TX | Fast, Professional Service",
    meta_description: "Professional HVAC repair in Austin, TX. Same-day service. Licensed & insured technicians. Call now for a free estimate.",
    h1_heading: "Expert HVAC Repair in Austin, TX",
    content: "<p>Need reliable HVAC repair in Austin? Our licensed technicians provide same-day service, transparent pricing, and quality workmanship.</p>",
    schema_markup: [],
    target_keywords: ["hvac repair austin", "austin hvac repair"],
    page_url: "/services/hvac-repair/austin-tx",
    generation_method: "template",
    page_type: "service_location",
    word_count: 120,
    created_at: new Date().toISOString()
  }
}

const contentBlocks = {
  "/services/hvac-repair/austin-tx": {
    hero: { heading: "HVAC Repair in Austin, TX", subheading: "Same-day service available" },
    benefits: { items: ["Licensed & insured", "Transparent pricing", "Fast response"] },
    process: {},
    offers: {},
    guarantees: {},
    faqs: [],
    cta_sections: []
  }
}

export function getAllSEOPages() {
  return seoPages
}

export function getAllContentBlocks() {
  return contentBlocks
}


