import { describe, it, expect, beforeEach, afterEach, beforeAll } from "vitest";
import {
  photoBoothE2EHelper,
  setupPhotoBoothE2E,
  cleanupPhotoBoothE2E,
  type E2ETestContext,
  skipIfNotDevelopmentMode,
  isPhotoBoothDevelopmentMode,
} from "../utils/e2e-setup";
import { existsSync } from "fs";

describe("Focused Visual Regression Tests", () => {
  let context: E2ETestContext;

  beforeAll(async () => {
    // Validate environment before running PhotoBooth E2E tests
    if (!isPhotoBoothDevelopmentMode()) {
      console.warn(
        "⚠️  PhotoBooth E2E tests are skipped - development environment required",
      );
      console.warn("   Run with: yarn test:photo-booth:e2e:dev");
    }
  });

  beforeEach(async () => {
    // Skip tests if not in development mode
    if (!isPhotoBoothDevelopmentMode()) {
      return; // Skip setup for production mode
    }

    // Use shared server and browser from globalSetup
    context = await setupPhotoBoothE2E();
  });

  afterEach(async () => {
    // Skip cleanup if not in development mode
    if (!isPhotoBoothDevelopmentMode()) {
      return; // Skip cleanup for production mode
    }

    // Only cleanup test-specific resources (pages)
    await cleanupPhotoBoothE2E();
  });

  describe("Core Visual Consistency", () => {
    // Test aspect ratio and theme combinations for visual consistency
    const testCombinations = [
      { aspectRatio: "16:9", mode: "light" },
      { aspectRatio: "16:9", mode: "dark" },
      { aspectRatio: "3:4", mode: "light" },
      { aspectRatio: "3:4", mode: "dark" },
    ];

    testCombinations.forEach(({ aspectRatio, mode }) => {
      it(`validates visual consistency for ${aspectRatio} ${mode} mode`, async () => {
        // Skip test if not in development mode
        if (!isPhotoBoothDevelopmentMode()) {
          skipIfNotDevelopmentMode();
          return;
        }

        const { page } = context;

        await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
          dashboard: "portfolio_history_portrait",
          aspect_ratio: aspectRatio,
          mode,
        });

        // Wait for component to be ready with enhanced robustness
        await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

        // Additional wait for dashboard-specific elements (only for portfolio_history_portrait)
        await page.waitForSelector(".dashboard-header", { timeout: 10000 });
        await page.waitForSelector(".dashboard-footer", { timeout: 5000 });
        await page.waitForSelector(".photo-booth-chart", { timeout: 5000 });

        // Hide controls for clean screenshots
        await photoBoothE2EHelper.hideControls(page);

        // Take screenshot
        const screenshotPath = await photoBoothE2EHelper.takeScreenshot(
          page,
          `visual-${aspectRatio.replace(":", "x")}-${mode}`,
        );

        expect(existsSync(screenshotPath)).toBe(true);
      });
    });
  });

  describe("Export Mode Visual Validation", () => {
    it("validates clean export screenshots without UI controls", async () => {
      // Skip test if not in development mode
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        aspect_ratio: "3:4",
        mode: "light",
      });

      // Wait for component to be ready with enhanced robustness
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Hide all controls for export mode
      await photoBoothE2EHelper.hideControls(page);

      // Take clean export screenshot
      const exportScreenshot = await photoBoothE2EHelper.takeScreenshot(
        page,
        "export-mode-clean",
      );

      expect(existsSync(exportScreenshot)).toBe(true);

      // Verify no controls are visible
      const controls = await page.$$(".photo-booth-controls");
      for (const control of controls) {
        const isVisible = await control.evaluate((el) => {
          const style = window.getComputedStyle(el);
          return style.display !== "none" && style.visibility !== "hidden";
        });
        expect(isVisible).toBe(false);
      }
    });
  });

  describe("Responsive Visual Testing", () => {
    const viewports = [
      { name: "desktop-fhd", width: 1920, height: 1080 },
      { name: "laptop-standard", width: 1440, height: 900 },
      { name: "tablet", width: 768, height: 1024 },
    ];

    viewports.forEach((viewport) => {
      it(`validates visual consistency at ${viewport.name} (${viewport.width}x${viewport.height})`, async () => {
        // Skip test if not in development mode
        if (!isPhotoBoothDevelopmentMode()) {
          skipIfNotDevelopmentMode();
          return;
        }

        const { page } = context;

        // Set viewport
        await page.setViewport({
          width: viewport.width,
          height: viewport.height,
        });

        await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
          dashboard: "portfolio_history_portrait",
          aspect_ratio: "16:9",
          mode: "light",
        });

        // Wait for component to be ready with enhanced robustness
        await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

        // Take screenshot
        const screenshotPath = await photoBoothE2EHelper.takeScreenshot(
          page,
          `responsive-${viewport.name}`,
        );

        expect(existsSync(screenshotPath)).toBe(true);

        // Verify dashboard renders properly at this viewport size
        const dashboard = await page.$(".photo-booth-dashboard");
        expect(dashboard).toBeTruthy();

        const boundingBox = await dashboard!.boundingBox();
        expect(boundingBox!.width).toBeGreaterThan(100);
        expect(boundingBox!.height).toBeGreaterThan(100);
      });
    });
  });
});
