// Schema generators for JSON-LD structured data
// Implements Schema.org markup for SEO optimization

import config from "@/config/config.json";

// Base schema interfaces for type safety
export interface BaseSchema {
  "@context": string;
  "@type": string;
}

export interface Person extends BaseSchema {
  "@type": "Person";
  name: string;
  jobTitle: string;
  url: string;
  description?: string;
  sameAs?: string[];
}

export interface Organization extends BaseSchema {
  "@type": "Organization";
  name: string;
  url: string;
  logo?: {
    "@type": "ImageObject";
    url: string;
  };
  description?: string;
  sameAs?: string[];
}

export interface Article extends BaseSchema {
  "@type": "Article";
  headline: string;
  author: Person;
  publisher: Organization;
  datePublished: string;
  dateModified?: string;
  description: string;
  image?: string;
  articleSection?: string;
  keywords?: string;
  url: string;
}

export interface BreadcrumbList extends BaseSchema {
  "@type": "BreadcrumbList";
  itemListElement: Array<{
    "@type": "ListItem";
    position: number;
    name: string;
    item: string;
  }>;
}

// Schema generators
export function generatePersonSchema(): Person {
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    name: "Cole Morton",
    jobTitle: "Software Engineer & Quantitative Trader",
    url: config.site.base_url,
    description:
      "Creator of AI Command Collaboration Framework - The Engineer's Approach to Trading",
    sameAs: [
      "https://twitter.com/ColeMoreton",
      "https://github.com/ColeMorton",
      "https://www.linkedin.com/in/colemorton-72300745/",
      "https://colemorton.substack.com/",
    ],
  };
}

export function generateOrganizationSchema(): Organization {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Cole Morton - The Engineer's Approach to Trading",
    url: config.site.base_url,
    logo: {
      "@type": "ImageObject",
      url: `${config.site.base_url}/images/logo.png`,
    },
    description:
      "Institutional-quality trading analysis through systematic AI-enhanced processes",
    sameAs: [
      "https://twitter.com/ColeMoreton",
      "https://github.com/ColeMorton",
      "https://www.linkedin.com/in/colemorton-72300745/",
      "https://colemorton.substack.com/",
    ],
  };
}

export function generateArticleSchema(
  title: string,
  description: string,
  datePublished: Date,
  dateModified?: Date,
  image?: string,
  categories?: string[],
  tags?: string[],
  slug?: string,
): Article {
  const person = generatePersonSchema();
  const organization = generateOrganizationSchema();

  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: title,
    author: person,
    publisher: organization,
    datePublished: datePublished.toISOString(),
    dateModified: dateModified
      ? dateModified.toISOString()
      : datePublished.toISOString(),
    description: description,
    image: image
      ? `${config.site.base_url}${image}`
      : `${config.site.base_url}${config.metadata.meta_image}`,
    articleSection: categories?.[0] || "Trading Analysis",
    keywords: tags?.join(", ") || "",
    url: slug ? `${config.site.base_url}/${slug}` : config.site.base_url,
  };
}

export function generateBreadcrumbSchema(
  breadcrumbs: Array<{ name: string; url: string }>,
): BreadcrumbList {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: breadcrumbs.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: `${config.site.base_url}${item.url}`,
    })),
  };
}

// Utility function to safely serialize JSON-LD
export function serializeSchema(schema: BaseSchema): string {
  try {
    return JSON.stringify(schema, null, 0);
  } catch {
    // Error serializing schema
    return "{}";
  }
}

// Validation helper for development
export function validateSchema(schema: BaseSchema): boolean {
  try {
    // Basic validation checks
    if (!schema["@context"] || !schema["@type"]) {
      // Schema missing required @context or @type
      return false;
    }

    if (schema["@context"] !== "https://schema.org") {
      // Schema @context should be https://schema.org
      return false;
    }

    return true;
  } catch {
    // Schema validation error
    return false;
  }
}
