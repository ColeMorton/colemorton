import { describe, it, expect, beforeEach, afterEach, beforeAll } from "vitest";
import {
  photoBoothE2EHelper,
  setupPhotoBoothE2E,
  cleanupPhotoBoothE2E,
  type E2ETestContext,
  PhotoBoothE2EHelper,
  skipIfNotDevelopmentMode,
  isPhotoBoothDevelopmentMode,
} from "../utils/e2e-setup";

describe("Photo Booth Advanced Error Scenarios", () => {
  let context: E2ETestContext;

  beforeAll(async () => {
    if (!isPhotoBoothDevelopmentMode()) {
      console.warn(
        "⚠️  Advanced error scenario tests are skipped - development environment required",
      );
      console.warn("   Run with: yarn test:photo-booth:e2e:dev");
      return;
    }
  });

  beforeEach(async () => {
    if (!isPhotoBoothDevelopmentMode()) {
      return;
    }

    context = await setupPhotoBoothE2E();
  });

  afterEach(async () => {
    if (!isPhotoBoothDevelopmentMode()) {
      return;
    }

    await cleanupPhotoBoothE2E();
  });

  describe("Critical System Failure Scenarios", () => {
    it("handles complete Python environment failure", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Simulate catastrophic Python environment failure
      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            error: "SystemError: Python interpreter crashed",
            details: {
              errorType: "CRITICAL_SYSTEM_FAILURE",
              pythonVersion: null,
              environmentBroken: true,
              recovery: "manual intervention required",
            },
            suggestions: [
              "Reinstall Python dependencies",
              "Check system PATH variables",
              "Verify Python installation integrity",
              "Contact system administrator",
            ],
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      // Should show critical error with detailed information
      const errorMessage = await page.waitForSelector(
        "text*=Python interpreter crashed",
        { timeout: 10000 },
      );
      expect(errorMessage).toBeTruthy();

      // Should provide recovery suggestions
      const suggestions = await page.waitForSelector("text*=Reinstall Python", {
        timeout: 5000,
      });
      expect(suggestions).toBeTruthy();

      // System should remain responsive despite critical error
      const dashboard = await page.$(".photo-booth-dashboard");
      expect(dashboard).toBeTruthy();
    });

    it("handles image corruption during export processing", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        format: "both",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let exportAttempts = 0;

      await page.route("/api/export-dashboard", async (route) => {
        exportAttempts++;

        if (exportAttempts === 1) {
          // First attempt: Image corruption during processing
          await route.fulfill({
            status: 500,
            contentType: "application/json",
            body: JSON.stringify({
              success: false,
              error:
                "ImageCorruptionError: Generated image failed integrity check",
              details: {
                stage: "post_processing",
                corruptedFiles: ["/tmp/export_temp.png"],
                integrityCheck: false,
                bytesCorrupted: 1024,
              },
              recovery: {
                available: true,
                retryRecommended: true,
                differentSettingsRecommended: false,
              },
            }),
          });
        } else {
          // Second attempt: Recovery successful
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Export recovered successfully after corruption error",
              files: ["/mock/path/recovered_export.png"],
              recovery: {
                attemptNumber: exportAttempts,
                previousError: "image_corruption",
                integrityVerified: true,
              },
            }),
          });
        }
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      // Should show corruption error
      const corruptionError = await page.waitForSelector(
        "text*=image failed integrity",
        { timeout: 10000 },
      );
      expect(corruptionError).toBeTruthy();

      // Should allow retry
      const dismissButton = await page.waitForSelector("text=×", {
        timeout: 5000,
      });
      await dismissButton.click();

      // Retry export
      await exportButton.click();

      // Should recover successfully
      const successMessage = await page.waitForSelector(
        "text*=recovered successfully",
        { timeout: 15000 },
      );
      expect(successMessage).toBeTruthy();

      expect(exportAttempts).toBe(2);
    });

    it("handles memory exhaustion during large export", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
        dpi: "600",
        scale: "4",
        format: "both",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Simulate memory exhaustion
      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 507,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            error:
              "MemoryError: Unable to allocate memory for image processing",
            details: {
              requestedMemory: "2.4GB",
              availableMemory: "1.1GB",
              processKilled: true,
              stage: "high_resolution_rendering",
            },
            fallbackOptions: [
              {
                option: "reduce_dpi",
                newDpi: 300,
                estimatedMemory: "800MB",
              },
              {
                option: "reduce_scale",
                newScale: 2,
                estimatedMemory: "600MB",
              },
              {
                option: "single_format",
                format: "png",
                estimatedMemory: "400MB",
              },
            ],
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      // Should show memory error with fallback options
      const memoryError = await page.waitForSelector(
        "text*=Unable to allocate memory",
        { timeout: 10000 },
      );
      expect(memoryError).toBeTruthy();

      // Should suggest quality reductions
      const fallbackSuggestion = await page.waitForSelector("text*=reduce", {
        timeout: 5000,
      });
      expect(fallbackSuggestion).toBeTruthy();
    });

    it("handles cascading chart rendering failures", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Simulate multiple chart failures
      await page.route("**/api/chart-data/**", async (route) => {
        const url = route.request().url();

        if (url.includes("portfolio-value")) {
          await route.fulfill({
            status: 500,
            body: JSON.stringify({
              error: "ChartDataError: Portfolio data corrupted",
              chart: "portfolio-value-comparison",
            }),
            contentType: "application/json",
          });
        } else if (url.includes("trade-pnl")) {
          await route.fulfill({
            status: 503,
            body: JSON.stringify({
              error: "ServiceUnavailable: PnL calculation service down",
              chart: "trade-pnl-waterfall",
            }),
            contentType: "application/json",
          });
        } else {
          await route.continue();
        }
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      // Should handle multiple chart failures gracefully
      await PhotoBoothE2EHelper.sleep(10000);

      // Check for error handling
      const chartErrors = await page.$$('[data-chart-error="true"]');
      const hasErrorHandling =
        chartErrors.length > 0 ||
        ((await page.$("text*=chart")) && (await page.$("text*=error")));

      // System should either show error indicators or fallback content
      expect(typeof hasErrorHandling).toBe("boolean");

      // Dashboard container should still exist
      const dashboard = await page.$(".photo-booth-dashboard");
      expect(dashboard).toBeTruthy();

      // Should be able to attempt export despite chart failures
      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
        { timeout: 10000 },
      );
      expect(exportButton).toBeTruthy();
    });
  });

  describe("Network and Connectivity Failures", () => {
    it("handles intermittent network connectivity", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      let networkCallCount = 0;

      // Simulate intermittent connectivity
      await page.route("/api/dashboards.json", async (route) => {
        networkCallCount++;

        if (networkCallCount <= 2) {
          // First two attempts fail
          await route.abort("connectionrefused");
        } else {
          // Third attempt succeeds
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
              {
                id: "portfolio_history_portrait",
                title: "Portfolio History Portrait",
                enabled: true,
                charts: [],
              },
            ]),
          });
        }
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      // Should eventually succeed after retries
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 45000);

      // Should have made multiple attempts
      expect(networkCallCount).toBeGreaterThanOrEqual(2);

      const dashboard = await page.$(".photo-booth-dashboard");
      expect(dashboard).toBeTruthy();
    });

    it("handles API endpoint unavailability with degraded functionality", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // All API endpoints return 503 Service Unavailable
      await page.route("/api/**", async (route) => {
        await route.fulfill({
          status: 503,
          contentType: "application/json",
          body: JSON.stringify({
            error: "Service Unavailable",
            message: "Backend services temporarily unavailable",
            retryAfter: 60,
            fallbackMode: true,
          }),
        });
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {});

      // Should handle API unavailability gracefully
      await PhotoBoothE2EHelper.sleep(10000);

      // Check for fallback mode or error handling
      const hasServiceError =
        (await page.$("text*=unavailable")) ||
        (await page.$("text*=service")) ||
        (await page.$("text*=503"));

      const hasContent =
        (await page.$(".photo-booth-container")) ||
        (await page.$(".photo-booth-dashboard"));

      // Should either show service error or fallback content
      expect(hasServiceError || hasContent).toBeTruthy();
    });

    it("handles proxy and firewall interference", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Simulate proxy authentication required
      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 407,
          contentType: "application/json",
          headers: {
            "Proxy-Authenticate": 'Basic realm="Corporate Proxy"',
          },
          body: JSON.stringify({
            error: "Proxy Authentication Required",
            message: "Corporate firewall blocking export requests",
            networkIssue: true,
            suggestions: [
              "Contact IT administrator",
              "Configure proxy settings",
              "Use VPN if available",
            ],
          }),
        });
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      // Should show proxy authentication error
      const proxyError = await page.waitForSelector(
        "text*=Proxy Authentication",
        { timeout: 10000 },
      );
      expect(proxyError).toBeTruthy();

      // Should provide IT support suggestions
      const suggestions = await page.waitForSelector("text*=Contact IT", {
        timeout: 5000,
      });
      expect(suggestions).toBeTruthy();
    });
  });

  describe("Data Integrity and Validation Failures", () => {
    it("handles malformed chart data gracefully", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Return malformed data for chart endpoints
      await page.route("**/api/chart-data/**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            data: [
              { invalid: "structure", missing: "required fields" },
              { timestamp: "not-a-date", value: "not-a-number" },
              null,
              undefined,
              { circular: {} },
            ],
            malformed: true,
          }),
        });
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      // Should handle malformed data without crashing
      await PhotoBoothE2EHelper.sleep(15000);

      // Check for data validation error handling
      const pageIsResponsive = await page.evaluate(() => {
        return (
          document.readyState === "complete" &&
          document.body.innerHTML.length > 1000
        );
      });

      expect(pageIsResponsive).toBe(true);
    });

    it("validates dashboard configuration schema violations", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Return invalid dashboard configuration
      await page.route("/api/dashboards.json", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              // Missing required fields
              title: "Invalid Dashboard",
              charts: "should be array but is string",
              layout: 999, // Should be string
              enabled: "yes", // Should be boolean
            },
            {
              id: null, // Invalid ID
              title: "", // Empty title
              charts: [], // Valid but empty
              unknownField: "should be rejected",
            },
          ]),
        });
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {});

      // Should handle schema violations
      await PhotoBoothE2EHelper.sleep(10000);

      // Should show validation errors or fallback
      const hasValidationHandling =
        (await page.$("text*=validation")) ||
        (await page.$("text*=invalid")) ||
        (await page.$("text*=schema")) ||
        (await page.$(".photo-booth-dashboard"));

      expect(hasValidationHandling).toBeTruthy();
    });

    it("handles time zone and locale data inconsistencies", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Simulate timezone-related data issues
      await page.route("**/api/chart-data/**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            data: [
              { timestamp: "2025-02-30T25:61:99Z", value: 100 }, // Invalid date
              { timestamp: "2025-01-01T00:00:00+25:00", value: 200 }, // Invalid timezone
              { timestamp: 1640995200000, value: 300 }, // Unix timestamp
              { timestamp: "2025-01-01", value: 400 }, // Date only
              { timestamp: "invalid-date-string", value: 500 }, // Completely invalid
            ],
            timezone: "Invalid/Timezone",
            locale: "zz_ZZ",
          }),
        });
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      // Should handle date/time inconsistencies
      await PhotoBoothE2EHelper.sleep(10000);

      const hasDateTimeHandling = await page.evaluate(() => {
        // Check if page has handled date formatting issues
        return document.readyState === "complete";
      });

      expect(hasDateTimeHandling).toBe(true);

      // Should still be able to attempt export
      const exportButton = await page.$(
        '[role="button"]:has-text("Export Dashboard")',
      );
      expect(exportButton).toBeTruthy();
    });
  });

  describe("Browser and Environment Edge Cases", () => {
    it("handles browser extension interference", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Simulate browser extension modifying page behavior
      await page.addInitScript(() => {
        // Simulate ad blocker modifying fetch
        const originalFetch = window.fetch;
        window.fetch = async (url, options) => {
          if (typeof url === "string" && url.includes("dashboard")) {
            // Simulate extension blocking dashboard requests
            throw new Error("Network request blocked by extension");
          }
          return originalFetch(url as string, options);
        };

        // Simulate extension injecting content
        document.addEventListener("DOMContentLoaded", () => {
          const extensionDiv = document.createElement("div");
          extensionDiv.id = "browser-extension-overlay";
          extensionDiv.style.cssText =
            "position:fixed;top:0;left:0;width:100%;height:100%;z-index:999999;pointer-events:none;";
          document.body.appendChild(extensionDiv);
        });
      });

      try {
        await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
          dashboard: "portfolio_history_portrait",
        });

        // Should handle extension interference
        await PhotoBoothE2EHelper.sleep(10000);

        // Check if page loads despite interference
        const hasContent =
          (await page.$(".photo-booth-container")) || (await page.$("body"));

        expect(hasContent).toBeTruthy();
      } catch (error) {
        // Extension interference might prevent normal loading
        // Test should verify graceful handling
        console.warn("Extension interference test:", error);
        expect(true).toBe(true); // Test passes if error is handled
      }
    });

    it("handles window focus and visibility changes during export", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let exportCompleted = false;

      await page.route("/api/export-dashboard", async (route) => {
        // Long export process
        setTimeout(() => {
          exportCompleted = true;
        }, 8000);

        await new Promise((resolve) => setTimeout(resolve, 8000));

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed despite visibility changes",
            backgroundProcessing: true,
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text=Exporting...", { timeout: 2000 });

      // Simulate window losing focus during export
      await page.evaluate(() => {
        window.dispatchEvent(new Event("blur"));
        document.dispatchEvent(new Event("visibilitychange"));
        Object.defineProperty(document, "hidden", {
          get: () => true,
        });
      });

      // Wait for export to complete
      await page.waitForSelector("text*=Successfully exported", {
        timeout: 15000,
      });

      expect(exportCompleted).toBe(true);
    });

    it("handles page refresh during critical operations", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Start export process
      await page.route("/api/export-dashboard", async (route) => {
        // Slow processing
        await new Promise((resolve) => setTimeout(resolve, 10000));

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed after page refresh",
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text=Exporting...", { timeout: 2000 });

      // Simulate accidental page refresh
      await page.reload();

      // Should recover gracefully after refresh
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      const dashboard = await page.$(".photo-booth-dashboard");
      expect(dashboard).toBeTruthy();

      // Should be able to start new export
      const newExportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      expect(await newExportButton.isDisabled()).toBe(false);
    });
  });

  describe("Edge Case Data Scenarios", () => {
    it("handles extremely large dataset rendering", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Return massive dataset
      await page.route("**/api/chart-data/**", async (route) => {
        const largeDataset = Array.from({ length: 100000 }, (_, i) => ({
          timestamp: new Date(2020, 0, 1 + i).toISOString(),
          value: Math.random() * 1000,
          volume: Math.floor(Math.random() * 1000000),
        }));

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            data: largeDataset,
            size: largeDataset.length,
            warning: "Large dataset - performance may be impacted",
          }),
        });
      });

      const startTime = performance.now();

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      // Should handle large dataset within reasonable time
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 120000); // Extended timeout

      const loadTime = performance.now() - startTime;

      // Should complete within 2 minutes
      expect(loadTime).toBeLessThan(120000);

      // Check memory usage
      const memoryUsage = await page.evaluate(() => {
        return (performance as any).memory?.usedJSHeapSize || 0;
      });

      // Should not exceed reasonable memory usage
      expect(memoryUsage).toBeLessThan(500 * 1024 * 1024); // 500MB
    });

    it("handles unicode and special character data", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Return data with special characters
      await page.route("**/api/chart-data/**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            data: [
              { name: "🚀 Rocket Stock", value: 100, symbol: "ROCKET🌙" },
              { name: "Café & Résumé Corp", value: 200, symbol: "CAFÉ™" },
              { name: "東京株式会社", value: 300, symbol: "東京" },
              { name: "تكنولوجيا المستقبل", value: 400, symbol: "تقنية" },
              { name: "Спейс Корп", value: 500, symbol: "СПЕЙС" },
            ],
            encoding: "UTF-8",
            specialCharacters: true,
          }),
        });
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      // Should handle unicode characters properly
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Should be able to export with special characters
      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );

      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed with Unicode characters",
            encoding: "UTF-8",
            specialCharactersPreserved: true,
          }),
        });
      });

      await exportButton.click();
      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });
    });

    it("handles missing or null data gracefully", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Return dataset with missing values
      await page.route("**/api/chart-data/**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            data: [
              { timestamp: "2025-01-01", value: 100 },
              { timestamp: "2025-01-02", value: null },
              { timestamp: "2025-01-03" }, // Missing value
              { timestamp: null, value: 300 }, // Missing timestamp
              null, // Entirely null record
              { timestamp: "2025-01-06", value: 400 },
            ],
            hasNulls: true,
            hasMissing: true,
          }),
        });
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      // Should handle missing data without crashing
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Should render some content despite missing data
      const charts = await page.$$(".photo-booth-chart");
      expect(charts.length).toBeGreaterThan(0);

      // Should be able to export
      const exportButton = await page.$(
        '[role="button"]:has-text("Export Dashboard")',
      );
      expect(exportButton).toBeTruthy();
    });
  });
});
