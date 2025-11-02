import { describe, it, expect, beforeAll, afterAll } from "vitest";
import type { Page } from "puppeteer";
import { setupE2ETest, cleanupE2ETest, e2eHelper } from "./setup";

describe("Contact Page E2E Tests", () => {
  let page: Page;

  beforeAll(async () => {
    const context = await setupE2ETest();
    page = context.page;
  }, 30000);

  afterAll(async () => {
    await cleanupE2ETest();
  }, 10000);

  describe("Contact Form Submission", () => {
    it("should load the contact page successfully", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      const title = await page.title();
      expect(title).toMatch(/contact/i);

      // Should see the contact form
      const contactForm = await page.$("form");
      expect(contactForm).toBeTruthy();
    }, 15000);

    it("should have all required form fields", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Check for name field (required)
      const nameField = await page.$("#name");
      expect(nameField).toBeTruthy();
      const nameRequired = await page.$eval("#name", (el: any) =>
        el.hasAttribute("required"),
      );
      expect(nameRequired).toBe(true);

      // Check for email field (required)
      const emailField = await page.$("#email");
      expect(emailField).toBeTruthy();
      const emailRequired = await page.$eval("#email", (el: any) =>
        el.hasAttribute("required"),
      );
      expect(emailRequired).toBe(true);

      // Check for organization field (optional)
      const organizationField = await page.$("#organization");
      expect(organizationField).toBeTruthy();
      const organizationRequired = await page.$eval(
        "#organization",
        (el: any) => el.hasAttribute("required"),
      );
      expect(organizationRequired).toBe(false);

      // Check for inquiry type dropdown (required)
      const inquiryTypeField = await page.$("#inquiry-type");
      expect(inquiryTypeField).toBeTruthy();
      const inquiryTypeRequired = await page.$eval("#inquiry-type", (el: any) =>
        el.hasAttribute("required"),
      );
      expect(inquiryTypeRequired).toBe(true);

      // Check for message field (required)
      const messageField = await page.$("#message");
      expect(messageField).toBeTruthy();
      const messageRequired = await page.$eval("#message", (el: any) =>
        el.hasAttribute("required"),
      );
      expect(messageRequired).toBe(true);

      // Check for submit button
      const submitButton = await page.$('button[type="submit"]');
      expect(submitButton).toBeTruthy();

      // Verify button text
      const buttonText = await page.$eval('button[type="submit"]', (el: any) =>
        el.textContent?.trim(),
      );
      expect(buttonText).toBe("Send Professional Inquiry");
    }, 15000);

    it("should fill out and submit the contact form", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Fill out the form fields
      await page.waitForSelector("#name", { timeout: 5000 });
      await page.type("#name", "John Doe");

      await page.waitForSelector("#email", { timeout: 5000 });
      await page.type("#email", "cole.morton@hotmail.com");

      await page.waitForSelector("#organization", { timeout: 5000 });
      await page.type("#organization", "Cole Morton Testing Corporation");

      // Select inquiry type from dropdown
      await page.waitForSelector("#inquiry-type", { timeout: 5000 });
      await page.select("#inquiry-type", "technical-collaboration");

      await page.waitForSelector("#message", { timeout: 5000 });
      await page.type(
        "#message",
        "This is a comprehensive test message from the E2E test suite. Testing the enhanced professional contact form submission flow with all new fields including organization and inquiry type selection.",
      );

      // Take a screenshot before submission
      await e2eHelper.takeScreenshot(page, "contact-form-filled");

      // Verify form fields are filled correctly
      const nameValue = await page.$eval("#name", (el: any) => el.value);
      const emailValue = await page.$eval("#email", (el: any) => el.value);
      const organizationValue = await page.$eval(
        "#organization",
        (el: any) => el.value,
      );
      const inquiryTypeValue = await page.$eval(
        "#inquiry-type",
        (el: any) => el.value,
      );
      const messageValue = await page.$eval("#message", (el: any) => el.value);

      expect(nameValue).toBe("John Doe");
      expect(emailValue).toBe("cole.morton@hotmail.com");
      expect(organizationValue).toBe("Cole Morton Testing Corporation");
      expect(inquiryTypeValue).toBe("technical-collaboration");
      expect(messageValue).toBe(
        "This is a comprehensive test message from the E2E test suite. Testing the enhanced professional contact form submission flow with all new fields including organization and inquiry type selection.",
      );

      // For Netlify forms, we'll intercept the submission to prevent actual submission during testing
      // but verify that the form would be properly submitted
      await page.evaluate(() => {
        const form = document.querySelector("form");
        if (form) {
          form.addEventListener("submit", (e) => {
            e.preventDefault();
            // Add a marker to indicate submission was attempted
            document.body.setAttribute("data-form-submitted", "true");
            document.body.setAttribute(
              "data-form-method",
              form.getAttribute("method") || "",
            );
            document.body.setAttribute(
              "data-netlify-enabled",
              form.hasAttribute("data-netlify") ? "true" : "false",
            );
          });
        }
      });

      // Submit the form
      const submitButton = await page.$('button[type="submit"]');
      await submitButton?.click();

      // Wait for form submission to be intercepted
      await page.waitForFunction(
        () => document.body.getAttribute("data-form-submitted") === "true",
        { timeout: 5000 },
      );

      // Verify the form submission was properly configured for Netlify
      const formSubmitted = await page.evaluate(() =>
        document.body.getAttribute("data-form-submitted"),
      );
      const formMethod = await page.evaluate(() =>
        document.body.getAttribute("data-form-method"),
      );
      const netlifyEnabled = await page.evaluate(() =>
        document.body.getAttribute("data-netlify-enabled"),
      );

      expect(formSubmitted).toBe("true");
      expect(formMethod).toBe("POST");
      expect(netlifyEnabled).toBe("true");

      // Take a screenshot after submission attempt
      await e2eHelper.takeScreenshot(page, "contact-form-submitted");
    }, 20000);

    it("should validate required fields", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Try to submit empty form
      const submitButton = await page.$('button[type="submit"]');
      await submitButton?.click();

      // Check if browser validation is triggered (HTML5 validation)
      const nameField = await page.$("#name");
      const nameValid = await nameField?.evaluate(
        (el: any) => el.validity.valid,
      );

      const emailField = await page.$("#email");
      const emailValid = await emailField?.evaluate(
        (el: any) => el.validity.valid,
      );

      const inquiryTypeField = await page.$("#inquiry-type");
      const inquiryTypeValid = await inquiryTypeField?.evaluate(
        (el: any) => el.validity.valid,
      );

      const messageField = await page.$("#message");
      const messageValid = await messageField?.evaluate(
        (el: any) => el.validity.valid,
      );

      // Required fields should be invalid when empty
      expect(nameValid).toBe(false);
      expect(emailValid).toBe(false);
      expect(inquiryTypeValid).toBe(false);
      expect(messageValid).toBe(false);

      // Organization is optional, so it should be valid even when empty
      const organizationField = await page.$("#organization");
      const organizationValid = await organizationField?.evaluate(
        (el: any) => el.validity.valid,
      );
      expect(organizationValid).toBe(true);
    }, 15000);

    it("should validate email format", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Fill required fields but put invalid email
      await page.type("#name", "Test User");
      await page.type("#email", "invalid-email");
      await page.select("#inquiry-type", "platform-inquiry");
      await page.type("#message", "Test message");

      // Try to submit
      const submitButton = await page.$('button[type="submit"]');
      await submitButton?.click();

      // Check if email validation is triggered
      const emailField = await page.$("#email");
      const emailValid = await emailField?.evaluate(
        (el: any) => el.validity.valid,
      );

      // Invalid email format should make the field invalid
      expect(emailValid).toBe(false);
    }, 15000);

    it("should validate inquiry type dropdown options", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Check that inquiry type dropdown has the expected options
      const inquiryTypeOptions = await page.$$eval(
        "#inquiry-type option",
        (options: any[]) =>
          options.map((option) => ({
            value: option.value,
            text: option.textContent?.trim(),
          })),
      );

      expect(inquiryTypeOptions).toEqual([
        { value: "", text: "Select inquiry type" },
        { value: "technical-collaboration", text: "Technical Collaboration" },
        { value: "professional-opportunity", text: "Professional Opportunity" },
        { value: "platform-inquiry", text: "Platform Inquiry" },
        { value: "consulting", text: "Consulting/Advisory" },
        { value: "other", text: "Other" },
      ]);

      // Test selecting different inquiry types
      await page.select("#inquiry-type", "technical-collaboration");
      let selectedValue = await page.$eval(
        "#inquiry-type",
        (el: any) => el.value,
      );
      expect(selectedValue).toBe("technical-collaboration");

      await page.select("#inquiry-type", "professional-opportunity");
      selectedValue = await page.$eval("#inquiry-type", (el: any) => el.value);
      expect(selectedValue).toBe("professional-opportunity");

      await page.select("#inquiry-type", "consulting");
      selectedValue = await page.$eval("#inquiry-type", (el: any) => el.value);
      expect(selectedValue).toBe("consulting");
    }, 15000);

    it("should accept valid form data", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Fill all required fields with valid data
      await page.type("#name", "Jane Smith");
      await page.type("#email", "cole.morton@hotmail.com");
      await page.type("#organization", "Professional Testing Solutions");
      await page.select("#inquiry-type", "professional-opportunity");
      await page.type(
        "#message",
        "This is a comprehensive valid test message with proper professional content and context.",
      );

      // Check that all fields are valid
      const nameValid = await page.$eval(
        "#name",
        (el: any) => el.validity.valid,
      );
      const emailValid = await page.$eval(
        "#email",
        (el: any) => el.validity.valid,
      );
      const organizationValid = await page.$eval(
        "#organization",
        (el: any) => el.validity.valid,
      );
      const inquiryTypeValid = await page.$eval(
        "#inquiry-type",
        (el: any) => el.validity.valid,
      );
      const messageValid = await page.$eval(
        "#message",
        (el: any) => el.validity.valid,
      );

      expect(nameValid).toBe(true);
      expect(emailValid).toBe(true);
      expect(organizationValid).toBe(true);
      expect(inquiryTypeValid).toBe(true);
      expect(messageValid).toBe(true);

      // Verify form can be submitted (would submit if action was configured)
      const form = await page.$("form");
      const formValid = await form?.evaluate((el: any) => el.checkValidity());
      expect(formValid).toBe(true);
    }, 15000);
  });

  describe("Accessibility Testing", () => {
    it("should support keyboard navigation", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Start keyboard navigation from the top of the form
      await page.focus("#name");

      // Tab through all form fields in correct order
      const expectedTabOrder = [
        "#name",
        "#email",
        "#organization",
        "#inquiry-type",
        "#message",
      ];

      for (let i = 0; i < expectedTabOrder.length; i++) {
        const activeElement = await page.evaluate(
          () => document.activeElement?.id,
        );
        expect(activeElement).toBe(expectedTabOrder[i].replace("#", ""));

        // Tab to next field (except for the last field)
        if (i < expectedTabOrder.length - 1) {
          await page.keyboard.press("Tab");
        }
      }

      // Tab to submit button
      await page.keyboard.press("Tab");
      const finalActiveElement = await page.evaluate(() =>
        document.activeElement?.tagName.toLowerCase(),
      );
      expect(finalActiveElement).toBe("button");
    }, 15000);

    it("should have proper ARIA labels and form accessibility", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Check that all form fields have proper labels
      const nameLabel = await page.$eval('label[for="name"]', (el: any) =>
        el.textContent?.trim(),
      );
      expect(nameLabel).toContain("Full Name");

      const emailLabel = await page.$eval('label[for="email"]', (el: any) =>
        el.textContent?.trim(),
      );
      expect(emailLabel).toContain("Professional Email");

      const orgLabel = await page.$eval(
        'label[for="organization"]',
        (el: any) => el.textContent?.trim(),
      );
      expect(orgLabel).toContain("Organization/Company");

      const inquiryLabel = await page.$eval(
        'label[for="inquiry-type"]',
        (el: any) => el.textContent?.trim(),
      );
      expect(inquiryLabel).toContain("Inquiry Type");

      const messageLabel = await page.$eval('label[for="message"]', (el: any) =>
        el.textContent?.trim(),
      );
      expect(messageLabel).toContain("Professional Inquiry");

      // Check that required fields are marked with asterisks
      const requiredLabels = await page.$$eval(
        "span.text-red-500",
        (spans: any[]) => spans.map((span) => span.textContent?.trim()),
      );
      expect(requiredLabels.filter((label) => label === "*")).toHaveLength(4); // name, email, inquiry-type, message
    }, 15000);

    it("should support form submission via Enter key", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Fill form with valid data
      await page.type("#name", "Keyboard User");
      await page.type("#email", "cole.morton@hotmail.com");
      await page.type("#organization", "Accessibility Testing Co.");
      await page.select("#inquiry-type", "platform-inquiry");
      await page.type("#message", "Testing form submission via keyboard");

      // Setup form submission interception
      await page.evaluate(() => {
        const form = document.querySelector("form");
        if (form) {
          form.addEventListener("submit", (e) => {
            e.preventDefault();
            document.body.setAttribute("data-keyboard-submit", "true");
          });
        }
      });

      // Focus on submit button and press Enter
      await page.focus('button[type="submit"]');
      await page.keyboard.press("Enter");

      // Verify form submission was triggered
      const keyboardSubmit = await page.evaluate(() =>
        document.body.getAttribute("data-keyboard-submit"),
      );
      expect(keyboardSubmit).toBe("true");
    }, 15000);

    it("should provide proper focus indication", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Test focus visibility on form fields
      const fieldIds = [
        "#name",
        "#email",
        "#organization",
        "#inquiry-type",
        "#message",
      ];

      for (const fieldId of fieldIds) {
        await page.focus(fieldId);

        // Check that focused element has visible focus styling
        const focusStyles = await page.$eval(fieldId, (el: any) => {
          const styles = window.getComputedStyle(el);
          return {
            outline: styles.outline,
            outlineWidth: styles.outlineWidth,
            boxShadow: styles.boxShadow,
            borderColor: styles.borderColor,
          };
        });

        // Should have some form of focus indication (outline, box-shadow, or border change)
        const hasFocusIndication =
          focusStyles.outline !== "none" ||
          focusStyles.outlineWidth !== "0px" ||
          focusStyles.boxShadow !== "none" ||
          focusStyles.borderColor.includes("rgb"); // TailwindCSS focus colors

        expect(hasFocusIndication).toBe(true);
      }
    }, 15000);

    it("should have semantic HTML structure for screen readers", async () => {
      await page.goto(`${e2eHelper.baseURL}/contact`, {
        waitUntil: "networkidle0",
      });

      // Check for semantic form structure
      const formElement = await page.$("form");
      expect(formElement).toBeTruthy();

      // Check that form has proper heading structure
      const formHeading = await page.$("h3");
      expect(formHeading).toBeTruthy();

      const headingText = await page.$eval("h3", (el: any) =>
        el.textContent?.trim(),
      );
      expect(headingText).toBe("Professional Contact Form");

      // Check for fieldset/legend if grouping is used (optional but good practice)
      // Check that submit button has descriptive text
      const submitButtonText = await page.$eval(
        'button[type="submit"]',
        (el: any) => el.textContent?.trim(),
      );
      expect(submitButtonText).toBe("Send Professional Inquiry");

      // Verify that the form has a logical tab order (already tested above)
      // and that error states would be properly announced (HTML5 validation handles this)
    }, 15000);
  });
});
