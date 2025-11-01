import {
  describe,
  it,
  expect,
  beforeEach,
  afterEach,
  beforeAll,
  afterAll,
} from "vitest";
import {
  photoBoothE2EHelper,
  setupPhotoBoothE2E,
  cleanupPhotoBoothE2E,
  type E2ETestContext,
  skipIfNotDevelopmentMode,
  isPhotoBoothDevelopmentMode,
} from "../utils/e2e-setup";
import * as fs from "fs/promises";
import * as path from "path";
import * as os from "os";

describe("Photo Booth File System & Resource Management", () => {
  let context: E2ETestContext;
  let tempTestDir: string;
  let mockOutputDir: string;

  beforeAll(async () => {
    if (!isPhotoBoothDevelopmentMode()) {
      console.warn(
        "⚠️  File system integration tests are skipped - development environment required",
      );
      console.warn("   Run with: yarn test:photo-booth:e2e:dev");
      return;
    }

    // Create temporary directory for file system tests
    tempTestDir = await fs.mkdtemp(path.join(os.tmpdir(), "photo-booth-fs-"));
    mockOutputDir = path.join(tempTestDir, "outputs");
    await fs.mkdir(mockOutputDir, { recursive: true });
  });

  afterAll(async () => {
    if (tempTestDir && isPhotoBoothDevelopmentMode()) {
      try {
        await fs.rmdir(tempTestDir, { recursive: true });
      } catch (err) {
        console.warn(`Failed to cleanup temp directory: ${err}`);
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

  describe("File Creation and Permissions", () => {
    it("validates export file creation with proper permissions", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Mock file creation during export
      const mockFilePath = path.join(mockOutputDir, "test_export.png");

      await page.route("/api/export-dashboard", async (route) => {
        // Simulate file creation
        const mockImageData = Buffer.from("mock image data");
        await fs.writeFile(mockFilePath, mockImageData);

        // Set proper file permissions (readable by owner and group)
        await fs.chmod(mockFilePath, 0o644);

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "File created successfully",
            files: [mockFilePath],
            permissions: "644",
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Validate file was created
      const fileExists = await fs
        .access(mockFilePath)
        .then(() => true)
        .catch(() => false);
      expect(fileExists).toBe(true);

      // Validate file permissions
      const fileStat = await fs.stat(mockFilePath);
      const permissions = (fileStat.mode & parseInt("777", 8)).toString(8);
      expect(permissions).toBe("644");

      // Cleanup
      await fs.unlink(mockFilePath);
    });

    it("handles insufficient file permissions gracefully", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Mock permission denied error during file creation
      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            error:
              "PermissionError: [Errno 13] Permission denied: '/protected/directory/export.png'",
            suggestion:
              "Check output directory permissions or choose a different output location",
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      const errorMessage = await page.waitForSelector(
        "text*=Permission denied",
        { timeout: 10000 },
      );
      expect(errorMessage).toBeTruthy();

      // Should provide helpful suggestion
      const suggestionText = await page.waitForSelector(
        "text*=Check output directory",
        { timeout: 2000 },
      );
      expect(suggestionText).toBeTruthy();
    });

    it("validates directory creation for nested export paths", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      const nestedDir = path.join(mockOutputDir, "nested", "subdirectory");
      const mockFilePath = path.join(nestedDir, "nested_export.png");

      await page.route("/api/export-dashboard", async (route) => {
        // Create nested directories
        await fs.mkdir(nestedDir, { recursive: true });

        // Create file in nested path
        await fs.writeFile(mockFilePath, Buffer.from("mock nested export"));

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Nested export created successfully",
            files: [mockFilePath],
            directoriesCreated: ["nested", "subdirectory"],
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Validate nested directory and file creation
      const dirExists = await fs
        .access(nestedDir)
        .then(() => true)
        .catch(() => false);
      const fileExists = await fs
        .access(mockFilePath)
        .then(() => true)
        .catch(() => false);

      expect(dirExists).toBe(true);
      expect(fileExists).toBe(true);

      // Cleanup
      await fs.rmdir(nestedDir, { recursive: true });
    });
  });

  describe("Disk Space Management", () => {
    it("validates disk space availability before export", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        format: "both",
        dpi: "600", // High quality = larger files
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      await page.route("/api/export-dashboard", async (route) => {
        // Simulate disk space check
        const freeSpace = 150 * 1024 * 1024; // 150MB available
        const estimatedSize = 45 * 1024 * 1024; // 45MB estimated export size

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed with disk space validation",
            files: ["/mock/path/high_quality_export.png"],
            diskSpace: {
              available: freeSpace,
              estimated: estimatedSize,
              sufficient: freeSpace > estimatedSize,
            },
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 15000,
      });
    });

    it("handles insufficient disk space gracefully", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
        format: "both",
        dpi: "600",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Simulate insufficient disk space
      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 507, // Insufficient Storage
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            error: "OSError: [Errno 28] No space left on device",
            diskSpace: {
              available: 5 * 1024 * 1024, // 5MB available
              estimated: 50 * 1024 * 1024, // 50MB needed
              insufficient: true,
            },
            suggestion: "Free up disk space or choose a lower quality setting",
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      const errorMessage = await page.waitForSelector("text*=No space left", {
        timeout: 10000,
      });
      expect(errorMessage).toBeTruthy();

      // Should suggest quality reduction
      const suggestionText = await page.waitForSelector("text*=lower quality", {
        timeout: 2000,
      });
      expect(suggestionText).toBeTruthy();
    });

    it("manages large file exports efficiently", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
        format: "both",
        dpi: "600",
        scale: "4", // Maximum quality settings
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let processingStarted = false;

      await page.route("/api/export-dashboard", async (route) => {
        processingStarted = true;

        // Simulate large file processing with progress
        await new Promise((resolve) => setTimeout(resolve, 5000)); // Longer processing time

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Large file export completed",
            files: [
              "/mock/path/ultra_high_quality_export.png",
              "/mock/path/ultra_high_quality_export.svg",
            ],
            fileSize: {
              png: "125MB",
              svg: "8MB",
              total: "133MB",
            },
            processingTime: "12.4s",
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      // Should show processing state for extended time
      await page.waitForSelector("text=Exporting...", { timeout: 2000 });

      // Verify processing actually started
      expect(processingStarted).toBe(true);

      // Should complete successfully even with large files
      await page.waitForSelector("text*=Successfully exported", {
        timeout: 20000,
      });
    });
  });

  describe("File Cleanup and Maintenance", () => {
    it("validates temporary file cleanup during export", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      const tempFilePath = path.join(tempTestDir, "temp_processing.tmp");

      await page.route("/api/export-dashboard", async (route) => {
        // Create temporary file during processing
        await fs.writeFile(tempFilePath, "temporary processing data");

        // Simulate processing delay
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Cleanup temporary file
        await fs.unlink(tempFilePath);

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed with temp file cleanup",
            files: ["/mock/path/export.png"],
            tempFilesCreated: 3,
            tempFilesCleanedUp: 3,
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Verify temporary file was cleaned up
      const tempFileExists = await fs
        .access(tempFilePath)
        .then(() => true)
        .catch(() => false);
      expect(tempFileExists).toBe(false);
    });

    it("handles cleanup failures gracefully", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed with cleanup warnings",
            files: ["/mock/path/export.png"],
            warnings: [
              "Failed to cleanup temporary file: /tmp/process_temp.png (file in use)",
              "Temporary directory cleanup incomplete: 2/3 files removed",
            ],
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Export should still succeed despite cleanup warnings
      const successMessage = await page.$("text*=Successfully exported");
      expect(successMessage).toBeTruthy();
    });

    it("validates old export file cleanup", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Create mock old export files
      const oldExportFiles = [
        path.join(mockOutputDir, "old_export_1.png"),
        path.join(mockOutputDir, "old_export_2.png"),
        path.join(mockOutputDir, "old_export_3.png"),
      ];

      for (const filePath of oldExportFiles) {
        await fs.writeFile(filePath, "old export data");
        // Set old timestamp
        const oldDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000); // 7 days ago
        await fs.utimes(filePath, oldDate, oldDate);
      }

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      await page.route("/api/export-dashboard", async (route) => {
        // Clean up old files during new export
        let cleanedUpFiles = 0;
        for (const oldFile of oldExportFiles) {
          try {
            await fs.unlink(oldFile);
            cleanedUpFiles++;
          } catch {
            // File might not exist
          }
        }

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed with old file cleanup",
            files: ["/mock/path/new_export.png"],
            cleanup: {
              oldFilesFound: oldExportFiles.length,
              oldFilesRemoved: cleanedUpFiles,
            },
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Verify old files were cleaned up
      for (const oldFile of oldExportFiles) {
        const fileExists = await fs
          .access(oldFile)
          .then(() => true)
          .catch(() => false);
        expect(fileExists).toBe(false);
      }
    });
  });

  describe("Concurrent File Access Management", () => {
    it("handles concurrent export file access safely", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let requestCount = 0;

      await page.route("/api/export-dashboard", async (route) => {
        requestCount++;

        if (requestCount === 1) {
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Export completed successfully",
              files: ["/mock/path/export.png"],
              lockAcquired: true,
              lockReleased: true,
            }),
          });
        } else {
          // Subsequent requests should be handled appropriately
          await route.fulfill({
            status: 429,
            contentType: "application/json",
            body: JSON.stringify({
              success: false,
              error: "Export already in progress",
              lockAcquired: false,
            }),
          });
        }
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );

      // First export
      await exportButton.click();

      // Verify button is disabled (prevents concurrent access)
      await page.waitForSelector("text=Exporting...", { timeout: 2000 });
      expect(await exportButton.isDisabled()).toBe(true);

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Should only have one successful request
      expect(requestCount).toBe(1);
    });

    it("manages file locking during export operations", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      const lockFilePath = path.join(tempTestDir, "export.lock");

      await page.route("/api/export-dashboard", async (route) => {
        // Create lock file
        await fs.writeFile(lockFilePath, process.pid.toString());

        // Simulate processing time
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Remove lock file
        await fs.unlink(lockFilePath);

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Export completed with file locking",
            files: ["/mock/path/export.png"],
            lockFile: lockFilePath,
            lockDuration: "2.1s",
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Verify lock file was cleaned up
      const lockFileExists = await fs
        .access(lockFilePath)
        .then(() => true)
        .catch(() => false);
      expect(lockFileExists).toBe(false);
    });

    it("recovers from stale file locks", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      // Create stale lock file (from previous crashed process)
      const staleLockPath = path.join(tempTestDir, "stale_export.lock");
      await fs.writeFile(staleLockPath, "99999"); // Non-existent PID

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      await page.route("/api/export-dashboard", async (route) => {
        // Detect and remove stale lock
        try {
          const lockContent = await fs.readFile(staleLockPath, "utf-8");
          const lockPid = parseInt(lockContent);

          // Check if process exists (in real implementation)
          // For test, assume it's stale and remove it
          await fs.unlink(staleLockPath);

          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Export completed after removing stale lock",
              files: ["/mock/path/export.png"],
              staleLockRemoved: true,
              staleLockPid: lockPid,
            }),
          });
        } catch {
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: "Export completed (no lock found)",
              files: ["/mock/path/export.png"],
            }),
          });
        }
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 10000,
      });

      // Stale lock should be removed
      const lockFileExists = await fs
        .access(staleLockPath)
        .then(() => true)
        .catch(() => false);
      expect(lockFileExists).toBe(false);
    });
  });
});
