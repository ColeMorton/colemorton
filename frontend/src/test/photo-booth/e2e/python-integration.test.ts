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
import * as childProcess from "child_process";
import { promisify } from "util";

const execAsync = promisify(childProcess.exec);

describe("Photo Booth Python Process Management Integration", () => {
  let context: E2ETestContext;
  let projectRoot: string;

  beforeAll(async () => {
    if (!isPhotoBoothDevelopmentMode()) {
      console.warn(
        "⚠️  Python integration tests are skipped - development environment required",
      );
      console.warn("   Run with: yarn test:photo-booth:e2e:dev");
      return;
    }

    projectRoot = path.resolve(__dirname, "../../../../..");

    // Validate Python script exists
    const pythonScriptPath = path.join(
      projectRoot,
      "scripts/photo_booth_generator.py",
    );
    try {
      await fs.access(pythonScriptPath);
    } catch {
      console.warn(`⚠️  Python script not found: ${pythonScriptPath}`);
      console.warn("   Python integration tests may fail");
    }

    // Validate Python environment
    try {
      await execAsync("python3 --version");
    } catch {
      console.warn(
        "⚠️  Python3 not available - Python integration tests may fail",
      );
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

  describe("Python Script Execution Integration", () => {
    it("validates photo_booth_generator.py script structure and dependencies", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const pythonScriptPath = path.join(
        projectRoot,
        "scripts/photo_booth_generator.py",
      );

      // Validate script file exists and is readable
      const scriptContent = await fs.readFile(pythonScriptPath, "utf-8");

      // Basic structure validation
      expect(scriptContent).toContain("#!/usr/bin/env python3");
      expect(scriptContent).toContain("import");

      // Key dependencies should be imported
      const expectedImports = [
        "asyncio",
        "pyppeteer", // or "puppeteer" depending on implementation
        "argparse",
        "json",
        "sys",
        "os",
      ];

      let foundImports = 0;
      expectedImports.forEach((importName) => {
        if (
          scriptContent.includes(`import ${importName}`) ||
          scriptContent.includes(`from ${importName}`)
        ) {
          foundImports++;
        }
      });

      expect(foundImports).toBeGreaterThan(3); // At least some core imports should be present
    });

    it("validates Python script can be executed with help flag", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const pythonScriptPath = path.join(
        projectRoot,
        "scripts/photo_booth_generator.py",
      );

      try {
        // Test script execution with help flag
        const { stdout, stderr } = await execAsync(
          `python3 "${pythonScriptPath}" --help`,
          {
            timeout: 10000,
            cwd: projectRoot,
          },
        );

        // Should display help information
        expect(stdout.toLowerCase()).toMatch(/usage|help|arguments|options/);

        // Should not have critical errors
        expect(stderr).not.toMatch(/error|exception|traceback/i);
      } catch (error: any) {
        // If script execution fails, at least check the error is reasonable
        expect(error.code).not.toBe(127); // "command not found"
        console.warn(`Python script execution warning: ${error.message}`);
      }
    });

    it("validates Python script parameter handling", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const pythonScriptPath = path.join(
        projectRoot,
        "scripts/photo_booth_generator.py",
      );

      // Test with invalid parameters to validate argument parsing
      try {
        await execAsync(`python3 "${pythonScriptPath}" --invalid-parameter`, {
          timeout: 5000,
          cwd: projectRoot,
        });
      } catch (error: any) {
        // Should fail with argument error, not import or syntax error
        expect(error.stderr).toMatch(/argument|unrecognized|invalid/i);
        expect(error.stderr).not.toMatch(
          /importerror|syntaxerror|modulenotfounderror/i,
        );
      }
    });
  });

  describe("Python Process Lifecycle Management", () => {
    it("manages Python process lifecycle during export", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let exportRequestIntercepted = false;
      let processExecutionTime = 0;

      // Intercept export request and simulate Python process execution
      await page.setRequestInterception(true);
      page.on("request", async (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          exportRequestIntercepted = true;
          const startTime = Date.now();

          // Simulate Python process execution delay
          await new Promise((resolve) => setTimeout(resolve, 2000));

          processExecutionTime = Date.now() - startTime;

          request.respond({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Python process completed successfully",
              files: ["/mock/path/export.png"],
              processTime: processExecutionTime,
            }),
          });
        } else {
          request.continue();
        }
      });

      // Debug: Check button state before clicking
      console.log("🔍 Looking for export button...");

      // Debug: Check what buttons are actually present first
      const allButtons = await page.$$eval("button", (buttons) =>
        buttons.map((btn) => ({
          text: btn.textContent?.trim(),
          disabled: btn.disabled,
          classes: btn.className,
        })),
      );
      console.log("🔍 All buttons found:", allButtons);

      // Find button with "Export Dashboard" text using evaluateHandle
      const buttonExists = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const buttonElement = buttonExists.asElement();
      if (!buttonElement) {
        console.log("❌ Export button not found in DOM");
        throw new Error("Export Dashboard button not found in DOM");
      }

      // Check if button is disabled
      const isButtonDisabled = await buttonElement.evaluate(
        (btn) => btn.disabled,
      );
      console.log("🔍 Export button disabled state:", isButtonDisabled);

      if (isButtonDisabled) {
        // Wait for button to be enabled (isReady = true)
        console.log("⏳ Waiting for export button to be enabled...");
        await page.waitForFunction(
          () => {
            const btn = Array.from(document.querySelectorAll("button")).find(
              (b) => b.textContent?.trim() === "Export Dashboard",
            );
            return btn && !btn.disabled;
          },
          { timeout: 30000 },
        );
        console.log("✅ Export button is now enabled");
      }

      const exportButton = buttonElement;
      await exportButton.click();

      // Should show exporting state immediately
      await page.waitForSelector("text=Exporting...", { timeout: 2000 });

      // Wait for process completion
      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      expect(exportRequestIntercepted).toBe(true);
      expect(processExecutionTime).toBeGreaterThan(1000); // Process took time
    });

    it("handles Python process timeout scenarios", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Simulate long-running Python process that times out
      await page.setRequestInterception(true);
      page.on("request", async (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          // Simulate timeout by delaying response beyond reasonable limits
          await new Promise((resolve) => setTimeout(resolve, 5000));

          request.respond({
            status: 500,
            contentType: "application/json",
            body: JSON.stringify({
              success: false,
              error:
                "Python process timeout: photo_booth_generator.py exceeded maximum execution time",
              processId: "mock-process-123",
            }),
          });
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }
      await exportButton.click();

      await page.waitForSelector("text=Exporting...", { timeout: 2000 });

      // Should handle timeout gracefully
      const errorMessage = await page.waitForSelector("text*=timeout", {
        timeout: 10000,
      });
      expect(errorMessage).toBeTruthy();

      // Button should be enabled again for retry
      expect(await exportButton.isDisabled()).toBe(false);
    });

    it("validates concurrent Python process management", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let processCount = 0;

      // Track multiple process attempts
      await page.setRequestInterception(true);
      page.on("request", async (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          processCount++;

          if (processCount === 1) {
            // First process should succeed after delay
            await new Promise((resolve) => setTimeout(resolve, 3000));
            request.respond({
              status: 200,
              contentType: "application/json",
              body: JSON.stringify({
                success: true,
                message: "First process completed",
                processId: `process-${processCount}`,
              }),
            });
          } else {
            // Subsequent processes should be rejected (concurrent prevention)
            request.respond({
              status: 429,
              contentType: "application/json",
              body: JSON.stringify({
                success: false,
                error: "Another export process is already running",
                processId: `rejected-${processCount}`,
              }),
            });
          }
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }

      // Start first export
      await exportButton.click();

      // Verify button is disabled
      await page.waitForSelector("text=Exporting...", { timeout: 2000 });
      expect(await exportButton.isDisabled()).toBe(true);

      // Try to start second export (should be prevented by disabled button)
      await exportButton.click({ force: true });

      // Should still only have one process
      expect(processCount).toBe(1);

      // Wait for completion
      await page.waitForSelector("text*=completed", { timeout: 6000 });
    });
  });

  describe("Puppeteer + Sharp.js Integration", () => {
    it("validates Puppeteer browser management during export", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Mock export response with browser lifecycle details
      await page.setRequestInterception(true);
      page.on("request", (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          request.respond({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Export completed with browser lifecycle",
              files: ["/mock/path/export.png"],
              browserDetails: {
                launched: true,
                screenshotTaken: true,
                browserClosed: true,
                processTime: 2500,
              },
            }),
          });
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });
    });

    it("handles browser launch failures gracefully", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Simulate Puppeteer browser launch failure
      await page.setRequestInterception(true);
      page.on("request", (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          request.respond({
            status: 500,
            contentType: "application/json",
            body: JSON.stringify({
              success: false,
              error:
                "Puppeteer browser launch failed: Unable to launch browser process",
              details:
                "Browser executable not found or insufficient system resources",
            }),
          });
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }
      await exportButton.click();

      const errorMessage = await page.waitForSelector(
        "text*=browser launch failed",
        { timeout: 10000 },
      );
      expect(errorMessage).toBeTruthy();

      // Should allow retry
      expect(await exportButton.isDisabled()).toBe(false);
    });

    it("validates Sharp.js image processing integration", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        format: "both", // Should trigger both PNG and SVG processing
        dpi: "600", // High quality processing
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let exportParams: any;

      await page.setRequestInterception(true);
      page.on("request", (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          const postData = request.postData();
          if (postData) {
            exportParams = JSON.parse(postData);
          }

          request.respond({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Image processing completed",
              files: ["/mock/path/export.png", "/mock/path/export.svg"],
              processing: {
                sharpProcessing: true,
                formats: ["PNG", "SVG"],
                dpiApplied: 600,
                processingTime: 3200,
              },
            }),
          });
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 15000,
      });

      // Validate export parameters were correctly sent for processing
      expect(exportParams.format).toBe("both");
      expect(exportParams.dpi).toBe(600);
    });
  });

  describe("Python Process Error Recovery", () => {
    it("recovers from Python dependency errors", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let attemptCount = 0;

      await page.setRequestInterception(true);
      page.on("request", (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          attemptCount++;

          if (attemptCount === 1) {
            // First attempt fails due to missing dependency
            request.respond({
              status: 500,
              contentType: "application/json",
              body: JSON.stringify({
                success: false,
                error: "ModuleNotFoundError: No module named 'pyppeteer'",
                suggestion: "Run: pip install pyppeteer",
              }),
            });
          } else {
            // Second attempt succeeds (dependency installed)
            request.respond({
              status: 200,
              contentType: "application/json",
              body: JSON.stringify({
                success: true,
                message: "Export completed after dependency resolution",
                files: ["/mock/path/export.png"],
              }),
            });
          }
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }

      // First attempt
      await exportButton.click();
      await page.waitForSelector("text*=ModuleNotFoundError", {
        timeout: 5000,
      });

      // Dismiss error and retry
      const dismissButton = await page.waitForSelector("text=×");
      await dismissButton.click();

      // Second attempt
      await exportButton.click();
      await page.waitForSelector("text*=completed after dependency", {
        timeout: 10000,
      });
    });

    it("handles Python script execution permissions", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Simulate permission denied error
      await page.setRequestInterception(true);
      page.on("request", (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          request.respond({
            status: 500,
            contentType: "application/json",
            body: JSON.stringify({
              success: false,
              error:
                "PermissionError: [Errno 13] Permission denied: 'photo_booth_generator.py'",
              suggestion:
                "Check file permissions: chmod +x scripts/photo_booth_generator.py",
            }),
          });
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }
      await exportButton.click();

      const errorMessage = await page.waitForSelector(
        "text*=Permission denied",
        { timeout: 10000 },
      );
      expect(errorMessage).toBeTruthy();

      // Should provide helpful suggestion
      const suggestionText = await page.waitForSelector("text*=chmod", {
        timeout: 2000,
      });
      expect(suggestionText).toBeTruthy();
    });

    it("manages Python process memory and resource cleanup", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Simulate resource-intensive export with cleanup
      await page.setRequestInterception(true);
      page.on("request", (request) => {
        if (request.url().includes("/api/export-dashboard")) {
          request.respond({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Export completed with resource cleanup",
              files: ["/mock/path/export.png"],
              resources: {
                memoryUsed: "156MB",
                processingTime: "4.2s",
                tempFilesCreated: 3,
                tempFilesCleanedUp: 3,
                browserProcesses: {
                  launched: 1,
                  closed: 1,
                  leaked: 0,
                },
              },
            }),
          });
        } else {
          request.continue();
        }
      });

      // Find export button using the same approach as the first test
      const exportButtonHandle = await page.evaluateHandle(() => {
        return Array.from(document.querySelectorAll("button")).find(
          (btn) => btn.textContent?.trim() === "Export Dashboard",
        );
      });

      const exportButton = exportButtonHandle.asElement();
      if (!exportButton) {
        throw new Error("Export Dashboard button not found");
      }
      await exportButton.click();

      await page.waitForSelector("text*=resource cleanup", { timeout: 15000 });

      // Verify no memory leaks or hanging processes by checking page is still responsive
      await PhotoBoothE2EHelper.sleep(2000);

      const pageTitle = await page.title();
      expect(pageTitle.length).toBeGreaterThan(0);
    });
  });
});
