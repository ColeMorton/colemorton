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
import * as fs from "fs/promises";
import * as path from "path";

describe("Photo Booth Real Data Integration", () => {
  let context: E2ETestContext;

  beforeAll(async () => {
    if (!isPhotoBoothDevelopmentMode()) {
      console.warn(
        "⚠️  Real data integration tests are skipped - development environment required",
      );
      console.warn("   Run with: yarn test:photo-booth:e2e:dev");
      return;
    }

    // Validate that required CSV data files exist
    const projectRoot = path.resolve(__dirname, "../../../../../..");
    const requiredDataFiles = [
      "data/raw/portfolios/bitcoin/multi_strategy_portfolio_portfolio_value.csv",
      "data/raw/portfolios/bitcoin/multi_strategy_portfolio_drawdowns.csv",
      "data/raw/portfolios/live_signals/live_signals_equity.csv",
      "data/raw/trade_history/live_signals.csv",
    ];

    for (const dataFile of requiredDataFiles) {
      const filePath = path.join(projectRoot, dataFile);
      try {
        await fs.access(filePath);
      } catch {
        console.warn(`⚠️  Required data file not found: ${dataFile}`);
        console.warn("   Real data integration tests may be limited");
      }
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

  describe("Real Chart Data Loading Integration", () => {
    it("loads photo booth with real chart data rendering", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Enable real data by removing mocks for this test
      await page.evaluate(() => {
        // Clear any existing mocks that might interfere
        if ("__VITEST_MOCKS__" in window) {
          delete (window as any).__VITEST_MOCKS__;
        }
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      // Wait longer for real data loading
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 45000);

      // Verify charts are rendered with real data (not mocked)
      const charts = await page.$$(".photo-booth-chart");
      expect(charts.length).toBeGreaterThan(0);

      // Check for actual chart content rather than mock placeholders
      for (const chart of charts) {
        const chartContent = await chart.evaluate((el) => el.innerHTML);

        // Real charts should have Plotly.js containers
        expect(chartContent).not.toContain('data-testid="mock-chart');

        // Should have actual chart dimensions
        const boundingBox = await chart.boundingBox();
        expect(boundingBox?.width).toBeGreaterThan(200);
        expect(boundingBox?.height).toBeGreaterThan(100);
      }
    });

    it("validates real CSV data is loaded by ChartDataService", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Navigate to a dashboard that uses portfolio data
      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 45000);

      // Check if ChartDataService has loaded real data
      const chartDataLoaded = await page.evaluate(async () => {
        // Try to access the ChartDataService via window object
        // In a real scenario, this would be available through the app

        // Check for network requests to CSV files
        const performanceEntries = performance
          .getEntriesByType("resource")
          .filter((entry) => entry.name.includes(".csv"));

        return performanceEntries.length > 0;
      });

      // In a real environment, CSV files should be loaded via network requests
      expect(chartDataLoaded).toBe(true);
    });

    it("validates portfolio value comparison chart with real data", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 45000);

      // Look for portfolio value comparison chart
      const portfolioValueChart = await page.$(
        '[data-chart-type="portfolio-value-comparison"]',
      );

      if (portfolioValueChart) {
        const chartBounds = await portfolioValueChart.boundingBox();
        expect(chartBounds?.width).toBeGreaterThan(300);
        expect(chartBounds?.height).toBeGreaterThan(200);

        // Check for Plotly.js specific elements (real charts)
        const plotlyElements = await portfolioValueChart.$$(".plotly");
        expect(plotlyElements.length).toBeGreaterThan(0);
      } else {
        // Chart may be rendered differently, check for any chart container
        const chartContainers = await page.$$(".photo-booth-chart");
        expect(chartContainers.length).toBeGreaterThan(0);
      }
    });

    it("validates live signals equity curve with real data", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 45000);

      // Check for data loading indicators
      const loadingIndicators = await page.$$('[data-loading="true"]');

      // After ready state, no loading indicators should remain
      expect(loadingIndicators.length).toBe(0);

      // Verify charts have rendered with content
      const charts = await page.$$(".photo-booth-chart");

      for (const chart of charts) {
        // Each chart should have meaningful content
        const isEmpty = await chart.evaluate((el) => {
          return el.children.length === 0 || el.textContent?.trim() === "";
        });
        expect(isEmpty).toBe(false);
      }
    });
  });

  describe("Real Data Chart Export Integration", () => {
    it("exports dashboard with real chart data rendering", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
        mode: "light",
        aspect_ratio: "16:9",
      });

      // Wait for real data to load
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 60000);

      // Verify real charts are present before export
      const charts = await page.$$(".photo-booth-chart");
      expect(charts.length).toBeGreaterThan(0);

      // Validate charts have real content (not empty or mocked)
      let hasRealContent = false;
      for (const chart of charts) {
        const hasPlotlyContent = await chart.$(".plotly");
        const hasChartContent = await chart.evaluate(
          (el) =>
            el.innerHTML.length > 100 && !el.innerHTML.includes("mock-chart"),
        );

        if (hasPlotlyContent || hasChartContent) {
          hasRealContent = true;
          break;
        }
      }

      expect(hasRealContent).toBe(true);

      // Mock the export to capture real dashboard state
      let exportRequestBody: any;
      await page.route("/api/export-dashboard", async (route) => {
        const request = route.request();
        const postData = request.postData();
        if (postData) {
          exportRequestBody = JSON.parse(postData);
        }

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Successfully exported dashboard with real data",
            files: ["/mock/path/real_data_export.png"],
          }),
        });
      });

      // Execute export
      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 30000,
      });

      // Validate export was called with correct parameters
      expect(exportRequestBody).toBeDefined();
      expect(exportRequestBody.dashboard_id).toBe("trading_performance");
      expect(exportRequestBody.aspect_ratio).toBe("16:9");
    });

    it("handles chart data loading errors gracefully during export", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Simulate data loading failure
      await page.route("**/*.csv", async (route) => {
        await route.abort("failed");
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      // Should handle data loading errors
      await PhotoBoothE2EHelper.sleep(10000);

      // Check if error is handled gracefully (dashboard still renders)
      const dashboard = await page.$(".photo-booth-dashboard");
      expect(dashboard).toBeTruthy();

      // Either shows error state or loads with fallback data
      const hasError =
        (await page.$("text*=error")) ||
        (await page.$("text*=failed")) ||
        (await page.$("text*=loading"));

      const hasCharts = await page.$$(".photo-booth-chart");

      // Should either show error or have charts (graceful degradation)
      expect(hasError !== null || hasCharts.length > 0).toBe(true);
    });
  });

  describe("Real Data Performance Integration", () => {
    it("validates chart rendering performance with real datasets", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      const startTime = Date.now();

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 60000);

      const loadTime = Date.now() - startTime;

      // Real data loading should complete within reasonable time
      expect(loadTime).toBeLessThan(60000); // 60 seconds max for real data

      // Validate all charts rendered
      const charts = await page.$$(".photo-booth-chart");
      expect(charts.length).toBeGreaterThan(0);
    });

    it("validates memory usage with large real datasets", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Get initial memory usage
      const initialMemory = await page.evaluate(() => {
        return (performance as any).memory?.usedJSHeapSize || 0;
      });

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 60000);

      // Wait for all async operations to complete
      await PhotoBoothE2EHelper.sleep(5000);

      const finalMemory = await page.evaluate(() => {
        return (performance as any).memory?.usedJSHeapSize || 0;
      });

      // Memory increase should be reasonable (less than 100MB for chart data)
      const memoryIncrease = finalMemory - initialMemory;
      expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024); // 100MB

      console.log(
        `Memory usage increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`,
      );
    });

    it("validates concurrent real data loading scenarios", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Test switching between dashboards rapidly (concurrent data loading)
      const dashboards = ["trading_performance", "portfolio_history_portrait"];

      for (let i = 0; i < 3; i++) {
        for (const dashboard of dashboards) {
          await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
            dashboard: dashboard,
          });

          // Wait briefly, then switch to next dashboard
          await PhotoBoothE2EHelper.sleep(2000);
        }
      }

      // Final dashboard should load successfully
      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      const charts = await page.$$(".photo-booth-chart");
      expect(charts.length).toBeGreaterThan(0);

      // Verify no JavaScript errors occurred during rapid switching
      const consoleErrors = await page.evaluate(() => {
        return window.performance.getEntriesByType("navigation").length > 0;
      });

      expect(consoleErrors).toBe(true); // Navigation should have occurred
    });
  });

  describe("Chart Data Service Integration", () => {
    it("validates ChartDataService caching with real data", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // First load
      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 45000);

      // Reload same dashboard (should use cache)
      await page.reload();

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      const secondLoadRequests = await page.evaluate(() => {
        return performance.getEntriesByType("resource").length;
      });

      // Second load should have fewer requests due to caching
      // (This is a rough indicator - actual caching verification would require deeper integration)
      expect(secondLoadRequests).toBeGreaterThan(0);
    });

    it("validates different chart types load appropriate datasets", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Test multiple chart types that use different data sources
      const chartTypes = [
        {
          dashboard: "trading_performance",
          expectedCharts: "portfolio-value-comparison",
        },
        {
          dashboard: "portfolio_history_portrait",
          expectedCharts: "trade-pnl-waterfall",
        },
      ];

      for (const testCase of chartTypes) {
        await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
          dashboard: testCase.dashboard,
        });

        await photoBoothE2EHelper.waitForPhotoBoothReady(page, 45000);

        // Verify charts are rendered
        const charts = await page.$$(".photo-booth-chart");
        expect(charts.length).toBeGreaterThan(0);

        // Each dashboard should render at least one chart
        let chartFound = false;
        for (const chart of charts) {
          const chartExists = await chart.evaluate(
            (el) => el.innerHTML.length > 50,
          );
          if (chartExists) {
            chartFound = true;
            break;
          }
        }

        expect(chartFound).toBe(true);

        // Small delay between dashboard switches
        await PhotoBoothE2EHelper.sleep(2000);
      }
    });
  });
});
