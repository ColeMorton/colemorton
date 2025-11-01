import { describe, it, expect, beforeAll, afterAll } from "vitest";
import type { Page } from "puppeteer";
import { setupE2ETest, cleanupE2ETest, e2eHelper } from "./setup";

describe("Homepage Footer Links E2E Tests", () => {
  let page: Page;

  beforeAll(async () => {
    const context = await setupE2ETest();
    page = context.page;
  }, 30000);

  afterAll(async () => {
    await cleanupE2ETest();
  }, 10000);

  describe("Footer Links Functionality", () => {
    it("should navigate to homepage and wait for cards to be visible", async () => {
      await page.goto(`${e2eHelper.baseURL}/`, {
        waitUntil: "networkidle0",
      });

      // Wait for homepage components to load
      await page.waitForSelector("#main-galaxy-section", { timeout: 10000 });

      // Scroll down to reveal the cards
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });

      // Wait for cards to animate in
      await page.waitForSelector(".pinned-cards-container.visible", {
        timeout: 15000,
      });

      // Take screenshot for debugging
      await e2eHelper.takeScreenshot(page, "homepage-cards-visible");
    }, 20000);

    it("should have clickable social links when cards are visible", async () => {
      await page.goto(`${e2eHelper.baseURL}/`, {
        waitUntil: "networkidle0",
      });

      // Scroll to reveal cards
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });

      // Wait for cards to be visible
      await page.waitForSelector(".pinned-cards-container.visible", {
        timeout: 15000,
      });

      // Test each social link is clickable
      const socialLinks = [
        { name: "substack", expectedUrl: "https://colemorton.substack.com/" },
        { name: "twitter", expectedUrl: "https://x.com/colemorton7" },
        { name: "github", expectedUrl: "https://github.com/ColeMorton" },
        {
          name: "linkedin",
          expectedUrl: "https://www.linkedin.com/in/colemorton-72300745/",
        },
      ];

      for (const social of socialLinks) {
        // Find the social link by href
        const linkSelector = `a[href="${social.expectedUrl}"]`;

        // Verify the link exists and is visible
        const link = await page.$(linkSelector);
        expect(link).toBeTruthy();

        // Check if link is clickable (not covered by other elements)
        const isClickable = await page.evaluate((selector) => {
          const element = document.querySelector(selector) as HTMLElement;
          if (!element) {
            return false;
          }

          const rect = element.getBoundingClientRect();
          const centerX = rect.left + rect.width / 2;
          const centerY = rect.top + rect.height / 2;

          // Get the element at the click position
          const elementAtPoint = document.elementFromPoint(centerX, centerY);

          // Check if the element at the click point is the link or a child of the link
          return element.contains(elementAtPoint) || element === elementAtPoint;
        }, linkSelector);

        expect(isClickable).toBe(true);
        console.log(`✓ ${social.name} link is clickable`);
      }
    }, 25000);

    it("should have clickable RSS, Atom, and JSON feed links when cards are visible", async () => {
      await page.goto(`${e2eHelper.baseURL}/`, {
        waitUntil: "networkidle0",
      });

      // Scroll to reveal cards
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });

      // Wait for cards to be visible
      await page.waitForSelector(".pinned-cards-container.visible", {
        timeout: 15000,
      });

      // Test each feed link is clickable
      const feedLinks = [
        { name: "RSS", expectedUrl: "/rss.xml" },
        { name: "Atom", expectedUrl: "/atom.xml" },
        { name: "JSON", expectedUrl: "/feed.json" },
      ];

      for (const feed of feedLinks) {
        // Find the feed link by href
        const linkSelector = `a[href="${feed.expectedUrl}"]`;

        // Verify the link exists and is visible
        const link = await page.$(linkSelector);
        expect(link).toBeTruthy();

        // Check if link is clickable (not covered by other elements)
        const isClickable = await page.evaluate((selector) => {
          const element = document.querySelector(selector) as HTMLElement;
          if (!element) {
            return false;
          }

          const rect = element.getBoundingClientRect();
          const centerX = rect.left + rect.width / 2;
          const centerY = rect.top + rect.height / 2;

          // Get the element at the click position
          const elementAtPoint = document.elementFromPoint(centerX, centerY);

          // Check if the element at the click point is the link or a child of the link
          return element.contains(elementAtPoint) || element === elementAtPoint;
        }, linkSelector);

        expect(isClickable).toBe(true);
        console.log(`✓ ${feed.name} feed link is clickable`);
      }
    }, 25000);

    it("should successfully navigate to external social links", async () => {
      await page.goto(`${e2eHelper.baseURL}/`, {
        waitUntil: "networkidle0",
      });

      // Scroll to reveal cards
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });

      // Wait for cards to be visible
      await page.waitForSelector(".pinned-cards-container.visible", {
        timeout: 15000,
      });

      // Test GitHub link navigation (as it's most reliable for testing)
      const githubLinkSelector = 'a[href="https://github.com/ColeMorton"]';

      // Set up new page listener for external link
      const newPagePromise = new Promise((resolve) => {
        page.once("popup", resolve);
      });

      // Click the GitHub link
      await page.click(githubLinkSelector);

      // Wait for new page to open
      const newPage = (await newPagePromise) as Page;

      // Verify the new page has the correct URL
      (await newPage.waitForLoadState?.("networkidle")) ||
        (await new Promise((resolve) => setTimeout(resolve, 2000)));
      const url = newPage.url();
      expect(url).toMatch(/github\.com/);

      // Close the new page
      await newPage.close();
    }, 30000);
  });
});
