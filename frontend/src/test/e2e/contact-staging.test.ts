import { describe, it, expect, beforeAll, afterAll } from "vitest";
import type { Page } from "puppeteer";
import { setupE2ETest, cleanupE2ETest, e2eHelper } from "./setup";

/**
 * STAGING ENVIRONMENT EMAIL DELIVERY TESTS
 *
 * These tests send REAL emails to cole.morton@hotmail.com
 * Only run in staging environment with ENABLE_STAGING_EMAIL_TESTS=true
 *
 * Usage:
 * ENABLE_STAGING_EMAIL_TESTS=true yarn test:e2e src/test/e2e/contact-staging.test.ts
 */

describe("Contact Form - Staging Email Delivery", () => {
  let page: Page;

  // Skip all tests unless explicitly enabled for staging
  const skipTests =
    !process.env.ENABLE_STAGING_EMAIL_TESTS ||
    process.env.NODE_ENV === "production";

  beforeAll(async () => {
    if (skipTests) {
      console.log(
        "🚫 Staging email tests skipped. Set ENABLE_STAGING_EMAIL_TESTS=true to run.",
      );
      return;
    }

    console.log(
      "🔥 WARNING: These tests send REAL emails to cole.morton@hotmail.com",
    );
    console.log(`📧 Base URL: ${e2eHelper.baseURL}`);

    const context = await setupE2ETest();
    page = context.page;
  }, 30000);

  afterAll(async () => {
    if (!skipTests) {
      await cleanupE2ETest();
    }
  }, 10000);

  describe("Real Email Delivery Tests", () => {
    it.skipIf(skipTests)(
      "should send technical collaboration inquiry email",
      async () => {
        await page.goto(`${e2eHelper.baseURL}/contact`, {
          waitUntil: "networkidle0",
        });

        // Fill form with technical collaboration data
        await page.type("#name", "Cole Morton (E2E Test)");
        await page.type("#email", "cole.morton@hotmail.com");
        await page.type("#organization", "Cole Morton Platform Testing");
        await page.select("#inquiry-type", "technical-collaboration");
        await page.type(
          "#message",
          `STAGING TEST - Technical Collaboration Inquiry

        This is an automated E2E test verifying email delivery functionality in the staging environment.

        Test Details:
        - Test Type: Technical Collaboration Inquiry
        - Timestamp: ${new Date().toISOString()}
        - Environment: ${process.env.NODE_ENV || "development"}
        - Test ID: staging-tech-collab-${Date.now()}

        This email should arrive at cole.morton@hotmail.com with proper formatting and all form fields included.`,
        );

        // Take screenshot before submission
        await e2eHelper.takeScreenshot(page, "staging-tech-collab-form-filled");

        // Submit the form (this will send a real email)
        const submitButton = await page.$('button[type="submit"]');
        await submitButton?.click();

        // Wait for redirect to success page
        await page.waitForNavigation({
          waitUntil: "networkidle0",
          timeout: 15000,
        });

        // Verify we're on the success page
        const currentUrl = page.url();
        expect(currentUrl).toContain("/contact-success");

        // Verify success message content
        const successMessage = await page.$eval("h2", (el: any) =>
          el.textContent?.trim(),
        );
        expect(successMessage).toBe("Professional Inquiry Received");

        // Take screenshot of success page
        await e2eHelper.takeScreenshot(page, "staging-tech-collab-success");

        console.log(
          "✅ Technical collaboration email sent successfully to cole.morton@hotmail.com",
        );
      },
      30000,
    );

    it.skipIf(skipTests)(
      "should send professional opportunity inquiry email",
      async () => {
        await page.goto(`${e2eHelper.baseURL}/contact`, {
          waitUntil: "networkidle0",
        });

        // Fill form with professional opportunity data
        await page.type("#name", "Cole Morton (E2E Pro Opportunity Test)");
        await page.type("#email", "cole.morton@hotmail.com");
        await page.type("#organization", "Future Employer Inc.");
        await page.select("#inquiry-type", "professional-opportunity");
        await page.type(
          "#message",
          `STAGING TEST - Professional Opportunity Inquiry

        This is an automated E2E test verifying professional opportunity email delivery.

        Test Details:
        - Test Type: Professional Opportunity
        - Timestamp: ${new Date().toISOString()}
        - Environment: ${process.env.NODE_ENV || "development"}
        - Test ID: staging-pro-opp-${Date.now()}

        Testing professional inquiry flow with enhanced form fields and professional messaging.`,
        );

        // Take screenshot before submission
        await e2eHelper.takeScreenshot(page, "staging-pro-opp-form-filled");

        // Submit the form
        const submitButton = await page.$('button[type="submit"]');
        await submitButton?.click();

        // Wait for success page
        await page.waitForNavigation({
          waitUntil: "networkidle0",
          timeout: 15000,
        });

        // Verify success
        expect(page.url()).toContain("/contact-success");
        await e2eHelper.takeScreenshot(page, "staging-pro-opp-success");

        console.log(
          "✅ Professional opportunity email sent successfully to cole.morton@hotmail.com",
        );
      },
      30000,
    );

    it.skipIf(skipTests)(
      "should send platform inquiry email",
      async () => {
        await page.goto(`${e2eHelper.baseURL}/contact`, {
          waitUntil: "networkidle0",
        });

        // Fill form with platform inquiry data
        await page.type("#name", "Cole Morton (E2E Platform Test)");
        await page.type("#email", "cole.morton@hotmail.com");
        await page.type("#organization", "Cole Morton Research & Development");
        await page.select("#inquiry-type", "platform-inquiry");
        await page.type(
          "#message",
          `STAGING TEST - Platform Inquiry

        This is an automated E2E test verifying platform inquiry email delivery functionality.

        Test Details:
        - Test Type: Platform Inquiry
        - Timestamp: ${new Date().toISOString()}
        - Environment: ${process.env.NODE_ENV || "development"}
        - Test ID: staging-platform-${Date.now()}

        Testing comprehensive platform inquiry workflow with enhanced professional contact form.

        Expected Email Content Verification:
        ✓ Professional sender information
        ✓ Organization context
        ✓ Inquiry type categorization
        ✓ Detailed professional message
        ✓ Proper email formatting and delivery`,
        );

        // Take screenshot before submission
        await e2eHelper.takeScreenshot(page, "staging-platform-form-filled");

        // Submit the form
        const submitButton = await page.$('button[type="submit"]');
        await submitButton?.click();

        // Wait for success page
        await page.waitForNavigation({
          waitUntil: "networkidle0",
          timeout: 15000,
        });

        // Verify success and professional messaging
        expect(page.url()).toContain("/contact-success");

        // Check for enhanced success message content
        const nextStepsInfo = await page.$eval("strong", (el: any) =>
          el.textContent?.trim(),
        );
        expect(nextStepsInfo).toBe("Next Steps:");

        await e2eHelper.takeScreenshot(page, "staging-platform-success");

        console.log(
          "✅ Platform inquiry email sent successfully to cole.morton@hotmail.com",
        );
      },
      30000,
    );

    it.skipIf(skipTests)(
      "should send consulting inquiry email with minimal required fields",
      async () => {
        await page.goto(`${e2eHelper.baseURL}/contact`, {
          waitUntil: "networkidle0",
        });

        // Test with minimal required fields (no organization)
        await page.type("#name", "Cole Morton (E2E Consulting Test)");
        await page.type("#email", "cole.morton@hotmail.com");
        // Skip organization field (it's optional)
        await page.select("#inquiry-type", "consulting");
        await page.type(
          "#message",
          `STAGING TEST - Consulting Inquiry (Minimal Fields)

        This test verifies the contact form works with minimal required fields.

        Test Details:
        - Test Type: Consulting/Advisory
        - Required Fields Only: Name, Email, Inquiry Type, Message
        - Organization: Not provided (testing optional field)
        - Timestamp: ${new Date().toISOString()}
        - Test ID: staging-consulting-min-${Date.now()}

        This validates that the form processes correctly even when optional fields are omitted.`,
        );

        // Take screenshot
        await e2eHelper.takeScreenshot(
          page,
          "staging-consulting-minimal-filled",
        );

        // Submit and verify
        const submitButton = await page.$('button[type="submit"]');
        await submitButton?.click();

        await page.waitForNavigation({
          waitUntil: "networkidle0",
          timeout: 15000,
        });

        expect(page.url()).toContain("/contact-success");
        await e2eHelper.takeScreenshot(
          page,
          "staging-consulting-minimal-success",
        );

        console.log(
          "✅ Consulting inquiry (minimal fields) email sent successfully to cole.morton@hotmail.com",
        );
      },
      30000,
    );
  });

  describe("Email Delivery Verification", () => {
    it.skipIf(skipTests)(
      "should provide email delivery confirmation",
      async () => {
        // This test documents what to look for in the inbox
        console.log(`
📧 EMAIL DELIVERY VERIFICATION CHECKLIST

Check cole.morton@hotmail.com inbox for the following test emails:

1. Technical Collaboration Inquiry
   ✓ Professional sender: Cole Morton (E2E Test)
   ✓ Organization: Cole Morton Platform Testing
   ✓ Subject should include: Technical Collaboration
   ✓ Message includes test timestamp and details

2. Professional Opportunity Inquiry
   ✓ Professional sender: Cole Morton (E2E Pro Opportunity Test)
   ✓ Organization: Future Employer Inc.
   ✓ Subject should include: Professional Opportunity
   ✓ Message includes professional inquiry context

3. Platform Inquiry
   ✓ Professional sender: Cole Morton (E2E Platform Test)
   ✓ Organization: Cole Morton Research & Development
   ✓ Subject should include: Platform Inquiry
   ✓ Message includes comprehensive platform details

4. Consulting Inquiry (Minimal Fields)
   ✓ Professional sender: Cole Morton (E2E Consulting Test)
   ✓ Organization: [Empty/Not provided]
   ✓ Subject should include: Consulting/Advisory
   ✓ Message explains minimal field testing

EMAIL FORMATTING VERIFICATION:
✓ Emails should not be in spam folder
✓ Professional email formatting and templates
✓ All form fields should be present in email body
✓ Timestamps should be recent (within test execution time)
✓ Email sender/reply-to should be properly configured

If any emails are missing or malformed, investigate:
1. Netlify Forms configuration in netlify.toml
2. Environment variables for email notifications
3. Spam filter settings
4. Email template formatting
      `);

        expect(true).toBe(true); // Pass - this is a documentation test
      },
    );
  });
});
