import puppeteer, { type Browser, type Page } from "puppeteer";
import { setTimeout } from "node:timers/promises";
import { getGlobalBaseURL, isGlobalServerReady } from "../e2e/globalSetup";

export interface E2ETestContext {
  browser: Browser;
  page: Page;
  baseURL: string;
}

export class PhotoBoothE2EHelper {
  private browser: Browser | null = null;
  private pages: Page[] = [];

  get baseURL(): string {
    return getGlobalBaseURL();
  }

  // Check if global server is ready and validate PhotoBooth feature availability
  async ensureServerReady(): Promise<void> {
    if (!isGlobalServerReady()) {
      throw new Error(
        "Global server not ready. Ensure globalSetup is configured properly.",
      );
    }

    // Also verify server is actually responding
    try {
      const response = await fetch(this.baseURL, {
        method: "HEAD",
        timeout: 5000,
      } as any);
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
    } catch (e: any) {
      throw new Error(`Global server not accessible: ${e.message}`);
    }

    // Validate PhotoBooth feature availability
    await this.validatePhotoBoothFeature();
  }

  // Validate that PhotoBooth feature is available in current environment
  async validatePhotoBoothFeature(): Promise<void> {
    const isDevelopmentMode =
      process.env.PHOTOBOOTH_E2E_DEV === "true" ||
      process.env.NODE_ENV === "development";

    if (!isDevelopmentMode) {
      throw new Error(
        "PhotoBooth E2E tests require development environment. Set PHOTOBOOTH_E2E_DEV=true or NODE_ENV=development",
      );
    }

    // Test PhotoBooth page accessibility
    try {
      const response = await fetch(`${this.baseURL}/photo-booth`, {
        method: "HEAD",
        timeout: 5000,
      } as any);

      if (!response.ok) {
        throw new Error(
          `PhotoBooth page returned ${response.status}. Feature may not be enabled in current environment.`,
        );
      }
    } catch (e: any) {
      throw new Error(`PhotoBooth feature validation failed: ${e.message}`);
    }
  }

  async getBrowser(): Promise<Browser> {
    if (this.browser) {
      return this.browser;
    }

    console.log("🌐 Starting browser for E2E test worker...");

    this.browser = await puppeteer.launch({
      headless: process.env.CI ? true : "new",
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-web-security", // Disable for E2E testing
        "--disable-features=TranslateUI",
        "--disable-background-networking",
        "--disable-background-timer-throttling",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-hang-monitor",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--metrics-recording-only",
        "--no-first-run",
        "--safebrowsing-disable-auto-update",
        "--enable-automation",
        "--password-store=basic",
      ],
      defaultViewport: {
        width: 1280,
        height: 720,
      },
    });

    return this.browser;
  }

  async createPage(): Promise<Page> {
    const browser = await this.getBrowser();
    const page = await browser.newPage();

    // Enhanced error handling with filtering
    page.on("console", (msg) => {
      const text = msg.text();
      if (
        msg.type() === "error" &&
        !text.includes("Failed to load resource") &&
        !text.includes("WebSocket connection") &&
        !text.includes("vite") &&
        !text.includes("JSHandle@error")
      ) {
        console.error("Browser console error:", text);
      }
    });

    page.on("pageerror", (error) => {
      const message = error.message;
      if (
        !message.includes("textContent") &&
        !message.includes("querySelector")
      ) {
        console.error("Page error:", message);
      }
    });

    // Set more generous timeouts for shared server environment
    page.setDefaultTimeout(15000);
    page.setDefaultNavigationTimeout(20000);

    this.pages.push(page);
    return page;
  }

  // Navigate to photo booth page with optional parameters (legacy method)
  async navigateToPhotoBooth(
    page: Page,
    params?: Record<string, string>,
  ): Promise<void> {
    const searchParams = new URLSearchParams(params);
    const url = `${this.baseURL}/photo-booth${searchParams.toString() ? "?" + searchParams.toString() : ""}`;

    await page.goto(url, {
      waitUntil: "networkidle0",
      timeout: 15000,
    });
  }

  // Resilient navigation with multiple fallback strategies
  async navigateToPhotoBoothWithFallbacks(
    page: Page,
    params?: Record<string, string>,
    timeout = 30000,
  ): Promise<void> {
    const searchParams = new URLSearchParams(params);
    const url = `${this.baseURL}/photo-booth${searchParams.toString() ? "?" + searchParams.toString() : ""}`;

    console.log(`Navigating to: ${url}`);

    // Strategy 1: Enhanced robust navigation
    try {
      await this.navigateToPhotoBoothRobust(page, params, timeout);
      return;
    } catch (e) {
      console.warn("Robust navigation failed, trying fallback:", e);
    }

    // Strategy 2: Basic navigation with longer timeout
    try {
      await page.goto(url, {
        waitUntil: "domcontentloaded",
        timeout: timeout + 10000,
      });
      await page.waitForFunction(
        () => document.querySelector(".photo-booth-container"),
        { timeout: 10000 },
      );
      return;
    } catch (e) {
      console.warn("Basic navigation failed, trying final fallback:", e);
    }

    // Strategy 3: Last resort - minimal navigation
    await page.goto(url, {
      waitUntil: "load",
      timeout: timeout + 20000,
    });

    // Give page time to initialize
    await PhotoBoothE2EHelper.sleep(5000);
  }

  // Wait for photo booth to be ready with development-specific optimizations
  async waitForPhotoBoothReady(page: Page, timeout = 30000): Promise<void> {
    console.log("⏳ Waiting for PhotoBooth component to be ready...");

    // Step 1: Debug page content and environment
    console.log("🔍 Checking page content and environment...");

    const pageInfo = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        bodyText: document.body
          ? document.body.textContent?.substring(0, 200)
          : "No body",
        hasPhotoBoothContainer: !!document.querySelector(
          ".photo-booth-container",
        ),
        allContainers: Array.from(
          document.querySelectorAll("[class*='photo-booth']"),
        ).map((el) => el.className),
        allDivs: Array.from(document.querySelectorAll("div"))
          .map((el) => el.className)
          .filter((c) => c)
          .slice(0, 10),
        scriptCount: document.querySelectorAll("script").length,
        isAstroPresent: !!(window as any).astro || !!(window as any).Astro,
        customElements: Array.from(
          document.querySelectorAll("astro-island"),
        ).map((el) => el.getAttribute("component-url")),
        isDevelopmentMode:
          !!(window as any).__DEV__ ||
          document.querySelector("[data-astro-dev-toolbar]"),
        viteHmr:
          !!(window as any).__vite_plugin_react_preamble_installed__ ||
          !!(window as any).__vite__,
      };
    });

    const environmentType =
      process.env.PHOTOBOOTH_E2E_DEV === "true" ? "development" : "production";
    console.log(
      `📋 Page info (${environmentType} mode):`,
      JSON.stringify(pageInfo, null, 2),
    );

    // Check if we're being redirected to 404 (indicates PhotoBooth not available)
    if (
      pageInfo.title.includes("Redirecting") ||
      pageInfo.bodyText.includes("Redirecting")
    ) {
      throw new Error(
        `PhotoBooth page is redirecting to 404. This indicates the feature is not available in the current environment. Ensure development server is running and PhotoBooth feature is enabled.`,
      );
    }

    // Wait for PhotoBooth container with more patience for production build
    const containerFound = await page.waitForFunction(
      () => {
        const container = document.querySelector(".photo-booth-container");
        const anyPhotoBooth = document.querySelector("[class*='photo-booth']");
        return container !== null || anyPhotoBooth !== null;
      },
      { timeout: 30000 },
    );

    if (containerFound) {
      console.log("✅ PhotoBooth container (or related element) found");
    } else {
      throw new Error("PhotoBooth container not found in production build");
    }

    // Step 2: Debug what's actually on the page and wait for expected states
    let attempts = 0;
    const maxAttempts = 20;

    while (attempts < maxAttempts) {
      const pageState = await page.evaluate(() => {
        const body = document.body;
        const hasLoadingText =
          body &&
          body.textContent &&
          body.textContent.includes("Loading dashboards...");
        const hasDashboard = document.querySelector(".photo-booth-dashboard");
        const hasErrorState =
          body &&
          body.textContent &&
          (body.textContent.includes("Failed to Load Dashboards") ||
            body.textContent.includes("Dashboard Not Found"));
        const hasControls = document.querySelector(".photo-booth-controls");
        const hasContainer = document.querySelector(".photo-booth-container");

        return {
          hasLoadingText,
          hasDashboard: !!hasDashboard,
          hasErrorState,
          hasControls: !!hasControls,
          hasContainer: !!hasContainer,
          bodyText: body ? body.textContent?.substring(0, 500) : "No body",
          containerClasses: hasContainer
            ? typeof hasContainer.className === "string"
              ? hasContainer.className
              : "No string className"
            : "No container",
          dashboardCount: document.querySelectorAll(".photo-booth-dashboard")
            .length,
          allElements: Array.from(document.querySelectorAll("*"))
            .map(
              (el) =>
                el.tagName +
                (el.className && typeof el.className === "string"
                  ? `.${el.className.split(" ").join(".")}`
                  : ""),
            )
            .slice(0, 20),
        };
      });

      console.log(
        `📊 Page state (attempt ${attempts + 1}):`,
        JSON.stringify(pageState, null, 2),
      );

      if (
        pageState.hasLoadingText ||
        pageState.hasDashboard ||
        pageState.hasErrorState
      ) {
        console.log("✅ Component state detected");
        break;
      }

      await PhotoBoothE2EHelper.sleep(500);
      attempts++;
    }

    if (attempts >= maxAttempts) {
      throw new Error(
        "Component never reached expected state (loading, dashboard, or error) after detailed debugging",
      );
    }

    // Step 3: If we were in loading state, wait for it to complete
    try {
      const isInLoadingState = await page.evaluate(() => {
        const body = document.body;
        return (
          body &&
          body.textContent &&
          body.textContent.includes("Loading dashboards...")
        );
      });

      if (isInLoadingState) {
        console.log("📥 Waiting for loading to complete...");
        await page.waitForFunction(
          () => {
            const body = document.body;
            return (
              body &&
              body.textContent &&
              !body.textContent.includes("Loading dashboards...")
            );
          },
          { timeout: 20000 },
        );
        console.log("✅ Dashboard loading completed");
      }
    } catch {
      console.log("⚠️ Loading completion check failed, proceeding...");
    }

    // Step 4: Ensure we're not in error state
    const isInErrorState = await page.evaluate(() => {
      const body = document.body;
      return (
        body &&
        body.textContent &&
        (body.textContent.includes("Failed to Load Dashboards") ||
          body.textContent.includes("Dashboard Not Found"))
      );
    });

    if (isInErrorState) {
      throw new Error(
        "PhotoBooth component is in error state - dashboards failed to load or dashboard not found",
      );
    }

    // Step 5: Wait for photo-booth-ready class and dashboard content simultaneously
    await page.waitForFunction(
      () => {
        const hasReadyClass = document.querySelector(".photo-booth-ready");
        const hasDashboard = document.querySelector(".photo-booth-dashboard");
        return hasReadyClass && hasDashboard;
      },
      { timeout: timeout - 20000 },
    );
    console.log("✅ Both photo-booth-ready class and dashboard element found");

    // Step 6: Additional stability check - ensure dashboard has content
    await page.waitForFunction(
      () => {
        const dashboard = document.querySelector(".photo-booth-dashboard");
        return dashboard && dashboard.children.length > 0;
      },
      { timeout: 5000 },
    );
    console.log("✅ Dashboard content rendered");

    // Step 7: Brief additional wait for full rendering stability
    await PhotoBoothE2EHelper.sleep(1000);
    console.log("✅ PhotoBooth component fully ready");
  }

  // Enhanced navigation optimized for development/production environments
  async navigateToPhotoBoothRobust(
    page: Page,
    params?: Record<string, string>,
    timeout = 30000,
  ): Promise<void> {
    const searchParams = new URLSearchParams(params);
    const url = `${this.baseURL}/photo-booth${searchParams.toString() ? "?" + searchParams.toString() : ""}`;

    console.log(`Navigating to: ${url}`);

    const isDevelopmentMode =
      process.env.PHOTOBOOTH_E2E_DEV === "true" ||
      process.env.NODE_ENV === "development";

    if (isDevelopmentMode) {
      // Development mode: adjust strategy based on timeout (indicates slow network)
      if (timeout > 45000) {
        // For slow/throttled networks, use domcontentloaded
        await page.goto(url, {
          waitUntil: "domcontentloaded",
          timeout,
        });
      } else {
        // Normal network: wait for network idle
        await page.goto(url, {
          waitUntil: "networkidle0",
          timeout,
        });
      }

      // Wait for hot reload stability and React hydration
      await PhotoBoothE2EHelper.sleep(3000);
    } else {
      // Production mode: faster navigation
      await page.goto(url, {
        waitUntil: "domcontentloaded",
        timeout,
      });

      // Brief wait for initial render
      await PhotoBoothE2EHelper.sleep(2000);
    }
  }

  // Take screenshot with consistent naming
  async takeScreenshot(page: Page, name: string): Promise<string> {
    const fs = await import("fs");
    const path = await import("path");

    // Use absolute path to avoid working directory issues
    const frontendDir = path.resolve(process.cwd(), "frontend");
    const screenshotDir = path.join(
      frontendDir,
      "src/test/photo-booth/e2e/screenshots",
    );

    if (!fs.existsSync(screenshotDir)) {
      try {
        fs.mkdirSync(screenshotDir, { recursive: true });
      } catch (e: any) {
        console.error(`Failed to create screenshot directory: ${e.message}`);
        throw new Error(
          `Cannot create screenshot directory at ${screenshotDir}`,
        );
      }
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const filename = path.join(screenshotDir, `${name}-${timestamp}.png`);

    await page.screenshot({
      path: filename,
      fullPage: true,
      type: "png",
    });

    return filename;
  }

  // Hide controls for clean export screenshots
  async hideControls(page: Page): Promise<void> {
    await page.evaluate(() => {
      const controls = document.querySelectorAll(".photo-booth-controls");
      controls.forEach((control) => {
        (control as HTMLElement).style.display = "none";
        (control as HTMLElement).style.visibility = "hidden";
      });

      // Also hide any dev toolbar elements
      const devElements = document.querySelectorAll(
        "[data-astro-dev-toolbar], astro-dev-toolbar, #dev-toolbar-root",
      );
      devElements.forEach((element) => {
        (element as HTMLElement).style.display = "none";
        (element as HTMLElement).style.visibility = "hidden";
      });
    });
  }

  // Clean up test worker resources (pages and browser)
  async cleanup(): Promise<void> {
    // Close all pages created by this helper
    for (const page of this.pages) {
      try {
        if (!page.isClosed()) {
          await page.close();
        }
      } catch {
        // Silently handle page closure errors
      }
    }
    this.pages = [];

    // Close browser instance for this worker
    if (this.browser) {
      try {
        await this.browser.close();
        this.browser = null;
      } catch (e) {
        console.warn("Failed to close worker browser:", e);
      }
    }
  }

  // Helper to sleep
  static async sleep(ms: number): Promise<void> {
    await setTimeout(ms);
  }

  // Improved error recovery for flaky tests
  static async retryWithBackoff<T>(
    operation: () => Promise<T>,
    maxAttempts = 3,
    baseDelay = 1000,
  ): Promise<T> {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await operation();
      } catch (error) {
        if (attempt === maxAttempts) {
          throw error;
        }

        const delay = baseDelay * Math.pow(2, attempt - 1);
        console.warn(
          `Attempt ${attempt} failed, retrying in ${delay}ms:`,
          error,
        );
        await this.sleep(delay);
      }
    }

    throw new Error("Should not reach here");
  }

  // Enhanced element waiting with multiple strategies
  static async waitForElement(
    page: Page,
    selector: string,
    timeout = 10000,
    visible = true,
  ): Promise<void> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      try {
        const element = await page.$(selector);
        if (element) {
          if (!visible) {
            return; // Element exists, visibility doesn't matter
          }

          // Check if element is visible
          const isVisible = await element.evaluate((el) => {
            const style = window.getComputedStyle(el);
            return (
              style.display !== "none" &&
              style.visibility !== "hidden" &&
              style.opacity !== "0"
            );
          });

          if (isVisible) {
            return;
          }
        }

        await this.sleep(500);
      } catch {
        await this.sleep(500);
      }
    }

    throw new Error(
      `Element ${selector} not ${visible ? "visible" : "found"} after ${timeout}ms`,
    );
  }
}

// Global test helper instance
export const photoBoothE2EHelper = new PhotoBoothE2EHelper();

// Environment validation helper for PhotoBooth E2E tests
export function skipIfNotDevelopmentMode(): void {
  const isDevelopmentMode =
    process.env.PHOTOBOOTH_E2E_DEV === "true" ||
    process.env.NODE_ENV === "development";

  if (!isDevelopmentMode) {
    console.warn(
      "⚠️  Skipping PhotoBooth test - development environment required",
    );
    console.warn("   Run with: yarn test:photo-booth:e2e:dev");
    return;
  }
}

export function isPhotoBoothDevelopmentMode(): boolean {
  return (
    process.env.PHOTOBOOTH_E2E_DEV === "true" ||
    process.env.NODE_ENV === "development"
  );
}

// Setup function for tests using shared resources
export async function setupPhotoBoothE2E(): Promise<E2ETestContext> {
  await photoBoothE2EHelper.ensureServerReady();
  const browser = await photoBoothE2EHelper.getBrowser();
  const page = await photoBoothE2EHelper.createPage();

  return {
    browser,
    page,
    baseURL: photoBoothE2EHelper.baseURL,
  };
}

// Cleanup function for tests
export async function cleanupPhotoBoothE2E(): Promise<void> {
  await photoBoothE2EHelper.cleanup();
}
