import "@testing-library/jest-dom";
import { vi } from "vitest";

// Standardized test environment variables for deterministic testing
const TEST_ENV_VARIABLES = {
  DEV: true,
  PROD: false, // Explicitly false for test environment
  MODE: "test",
  PUBLIC_ENV: "test",
  // Feature flags - using explicit test values for consistency
  PUBLIC_FEATURE_SEARCH: "false", // Match static config default
  PUBLIC_FEATURE_THEME_SWITCHER: "true", // Match static config default
  PUBLIC_FEATURE_COMMENTS: "false", // Test environment should be false
  PUBLIC_FEATURE_GTM: "false", // Test environment should be false
  PUBLIC_FEATURE_CALCULATORS: "true", // Default true
  PUBLIC_FEATURE_CALCULATOR_ADVANCED: "false", // Default false
  PUBLIC_FEATURE_ELEMENTS_PAGE: "true", // Default true
  PUBLIC_FEATURE_AUTHORS_PAGE: "true", // Default true
  PUBLIC_FEATURE_CHARTS_PAGE: "false", // Test environment should be false
  PUBLIC_FEATURE_PHOTO_BOOTH: "true", // Enable for testing
};

// Set up global environment mock that persists across all tests
vi.stubGlobal("import.meta.env", TEST_ENV_VARIABLES);

// Ensure environment variables are available in process.env for consistency
Object.entries(TEST_ENV_VARIABLES).forEach(([key, value]) => {
  process.env[key] = String(value);
});

// Force override of vitest's own environment detection
Object.defineProperty(globalThis, "import.meta", {
  value: {
    env: TEST_ENV_VARIABLES,
  },
  writable: true,
  configurable: true,
});

// Mock JSON data for tests
const mockSearchData = [
  {
    group: "blog",
    slug: "test-post-1",
    frontmatter: {
      title: "Test Post 1",
      description: "This is a test post for search functionality",
      categories: ["technology", "web"],
      tags: ["astro", "react"],
      author: "Test Author",
      date: new Date("2024-01-01"),
    },
    content: "Test content for post 1",
  },
  {
    group: "blog",
    slug: "test-post-2",
    frontmatter: {
      title: "Another Test Post",
      description: "Second test post for comprehensive testing",
      categories: ["design"],
      tags: ["ui", "ux"],
      author: "Test Author 2",
      date: new Date("2024-01-02"),
    },
    content: "Test content for post 2",
  },
];

// Mock the JSON import that SearchModal depends on
vi.mock(".json/search.json", () => ({
  default: mockSearchData,
}));

// Mock browser APIs that aren't available in JSDOM
Object.defineProperty(window, "matchMedia", {
  writable: true,
  configurable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }),
});

// Mock ResizeObserver for chart components
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver for visibility tracking
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock getComputedStyle for chart measurements
Object.defineProperty(window, "getComputedStyle", {
  value: vi.fn().mockImplementation(() => ({
    getPropertyValue: vi.fn().mockReturnValue("16px"),
    fontSize: "16px",
    width: "800px",
    height: "600px",
    marginTop: "0px",
    marginRight: "0px",
    marginBottom: "0px",
    marginLeft: "0px",
    paddingTop: "0px",
    paddingRight: "0px",
    paddingBottom: "0px",
    paddingLeft: "0px",
  })),
});

// Mock document.documentElement for dark mode detection
Object.defineProperty(document, "documentElement", {
  value: {
    ...document.documentElement,
    classList: {
      contains: vi.fn().mockReturnValue(false),
      add: vi.fn(),
      remove: vi.fn(),
      toggle: vi.fn(),
    },
  },
  writable: true,
  configurable: true,
});

// Mock MutationObserver for theme changes and testing library
global.MutationObserver = class MutationObserver {
  callback: MutationCallback;
  observe = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn().mockReturnValue([]);

  constructor(callback: MutationCallback) {
    this.callback = callback;
  }
} as any;

// Global test utilities
global.mockSearchData = mockSearchData;
global.TEST_ENV_VARIABLES = TEST_ENV_VARIABLES;
