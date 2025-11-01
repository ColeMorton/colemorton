import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

// Mock config.json
vi.mock("@/config/config.json", () => ({
  default: {
    settings: {
      search: false,
      theme_switcher: true, // Keep original snake_case for compatibility
      sticky_header: true,
      default_theme: "system",
      pagination: 2,
      summary_length: 200,
      blog_folder: "blog",
    },
    disqus: {
      enable: false,
    },
    google_tag_manager: {
      enable: false,
    },
    site: {},
    params: {},
    navigation_button: {},
    metadata: {},
  },
}));

describe("Feature Flags Configuration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset modules to ensure fresh imports
    vi.resetModules();
    // Restore standardized test environment before each test
    vi.stubGlobal("import.meta.env", global.TEST_ENV_VARIABLES);
  });

  afterEach(() => {
    // Ensure environment is restored after each test
    vi.stubGlobal("import.meta.env", global.TEST_ENV_VARIABLES);
    vi.resetModules();
  });

  describe("Environment Variable Override", () => {
    it("should use environment variables when provided", async () => {
      const { enhancedConfig } = await import("@/lib/config");

      // Based on standardized test environment variables
      expect(enhancedConfig.features.search).toBe(false); // env: false, config: false
      expect(enhancedConfig.features.themeSwitcher).toBe(true); // env: true, config: true
      expect(enhancedConfig.features.comments).toBe(false); // env: false (test environment)
      expect(enhancedConfig.features.gtm).toBe(false); // env: false, config: false
      expect(enhancedConfig.features.calculatorAdvanced).toBe(false); // env: false, default: false
      expect(enhancedConfig.features.elementsPage).toBe(true); // env: true, default: true
      expect(enhancedConfig.features.authorsPage).toBe(true); // env: true, default: true
    });

    it.skip("should fall back to static config when environment variable is undefined", async () => {
      // Clear module cache and mock environment without some variables
      vi.resetModules();

      // Set up a completely new environment with minimal variables
      const _testEnv = {
        DEV: true,
        PROD: false,
        MODE: "test",
        PUBLIC_ENV: "test",
        PUBLIC_FEATURE_SEARCH: undefined, // Should fallback to config (false)
        PUBLIC_FEATURE_THEME_SWITCHER: "false", // Explicit env override
        // Remove all other feature flags to force fallback behavior
      };

      vi.stubGlobal("import.meta.env", _testEnv);

      // Also set globalThis for more complete environment override
      Object.defineProperty(globalThis, "import.meta", {
        value: { env: _testEnv },
        writable: true,
        configurable: true,
      });

      // Import fresh module after environment setup
      const { enhancedConfig } = await import("@/lib/config");

      // Should fall back to static config for search (config.settings.search = false)
      expect(enhancedConfig.features.search).toBe(false); // fallback to config
      expect(enhancedConfig.features.themeSwitcher).toBe(false); // env override
    });
  });

  describe("Feature Flag Utilities", () => {
    it("should provide correct feature flag status", async () => {
      const { isFeatureEnabled, features } = await import("@/lib/featureFlags");

      // Based on standardized test environment
      expect(isFeatureEnabled("search")).toBe(false);
      expect(isFeatureEnabled("themeSwitcher")).toBe(true);
      expect(isFeatureEnabled("calculatorAdvanced")).toBe(false);
      expect(isFeatureEnabled("elementsPage")).toBe(true);
      expect(isFeatureEnabled("authorsPage")).toBe(true);

      expect(features.search).toBe(false);
      expect(features.themeSwitcher).toBe(true);
      expect(features.elementsPage).toBe(true);
      expect(features.authorsPage).toBe(true);
    });

    it("should handle multiple feature flag checks", async () => {
      const { areAllFeaturesEnabled, isAnyFeatureEnabled } = await import(
        "@/lib/featureFlags"
      );

      // Based on standardized test environment: search=false, comments=false, themeSwitcher=true
      expect(areAllFeaturesEnabled(["themeSwitcher", "elementsPage"])).toBe(
        true,
      );
      expect(areAllFeaturesEnabled(["search", "themeSwitcher"])).toBe(false);

      expect(isAnyFeatureEnabled(["search", "themeSwitcher"])).toBe(true);
      expect(isAnyFeatureEnabled(["search", "comments"])).toBe(false);
    });
  });

  describe("Environment Detection", () => {
    it.skip("should correctly detect environment", async () => {
      // Ensure we have a fresh module with standardized test environment
      vi.resetModules();
      vi.stubGlobal("import.meta.env", global.TEST_ENV_VARIABLES);

      const { env } = await import("@/lib/config");

      expect(env.isDevelopment()).toBe(true);
      // In test environment with vitest, PROD should be false
      expect(env.isProduction()).toBe(false);
      expect(env.current).toBe("test");
    });
  });

  describe("Configuration Validation", () => {
    it("should have all required feature flags as booleans", async () => {
      const { enhancedConfig } = await import("@/lib/config");

      const requiredFlags = [
        "search",
        "themeSwitcher",
        "comments",
        "gtm",
        "calculatorAdvanced",
        "elementsPage",
        "authorsPage",
      ];

      requiredFlags.forEach((flag) => {
        expect(
          typeof enhancedConfig.features[
            flag as keyof typeof enhancedConfig.features
          ],
        ).toBe("boolean");
      });
    });

    it("should maintain backward compatibility with original config", async () => {
      const { enhancedConfig } = await import("@/lib/config");

      // Should still have all original config properties
      expect(enhancedConfig.settings).toBeDefined();
      expect(enhancedConfig.disqus).toBeDefined();
      expect(enhancedConfig.google_tag_manager).toBeDefined();
      expect(enhancedConfig.site).toBeDefined();
    });
  });
});
