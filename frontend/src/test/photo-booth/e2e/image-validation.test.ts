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
  PhotoBoothE2EHelper,
  skipIfNotDevelopmentMode,
  isPhotoBoothDevelopmentMode,
} from "../utils/e2e-setup";
import * as fs from "fs/promises";
import * as path from "path";
import * as os from "os";

// Image processing utilities
interface ImageMetadata {
  width: number;
  height: number;
  format: string;
  fileSize: number;
  isValid: boolean;
}

// PNG file signature validation
function validatePngSignature(buffer: Buffer): boolean {
  const pngSignature = buffer.subarray(0, 8);
  const expectedSignature = Buffer.from([
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
  ]);
  return pngSignature.equals(expectedSignature);
}

// Basic PNG metadata extraction
function extractPngMetadata(buffer: Buffer): Partial<ImageMetadata> {
  if (!validatePngSignature(buffer)) {
    return { isValid: false };
  }

  // PNG IHDR chunk starts at byte 12, dimensions at bytes 16-23
  const width = buffer.readUInt32BE(16);
  const height = buffer.readUInt32BE(20);

  return {
    width,
    height,
    format: "PNG",
    fileSize: buffer.length,
    isValid: true,
  };
}

// SVG validation and basic metadata
function extractSvgMetadata(buffer: Buffer): Partial<ImageMetadata> {
  const svgContent = buffer.toString("utf-8");

  // Validate SVG format
  if (!svgContent.includes("<svg") || !svgContent.includes("</svg>")) {
    return { isValid: false };
  }

  // Extract dimensions from SVG attributes
  const widthMatch = svgContent.match(/width=["']?(\d+)["']?/);
  const heightMatch = svgContent.match(/height=["']?(\d+)["']?/);
  const viewBoxMatch = svgContent.match(
    /viewBox=["']?\d+\s+\d+\s+(\d+)\s+(\d+)["']?/,
  );

  let width: number | undefined;
  let height: number | undefined;

  if (widthMatch && heightMatch) {
    width = parseInt(widthMatch[1]);
    height = parseInt(heightMatch[1]);
  } else if (viewBoxMatch) {
    width = parseInt(viewBoxMatch[1]);
    height = parseInt(viewBoxMatch[2]);
  }

  return {
    width,
    height,
    format: "SVG",
    fileSize: buffer.length,
    isValid: true,
  };
}

// Helper function to mock export API responses
async function mockExportAPI(
  page: Page,
  responseData: any,
  captureParams?: { exportParams: any },
) {
  await page.setRequestInterception(true);

  page.on("request", (request) => {
    if (request.url().includes("/api/export-dashboard")) {
      const postData = request.postData();
      if (postData && captureParams) {
        try {
          captureParams.exportParams = JSON.parse(postData);
        } catch (e) {
          console.warn("Failed to parse POST data:", e);
        }
      }

      request.respond({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(responseData),
      });
    } else {
      request.continue();
    }
  });
}

describe("Photo Booth Image Quality & Metadata Validation", () => {
  let context: E2ETestContext;
  let tempDir: string;

  beforeAll(async () => {
    if (!isPhotoBoothDevelopmentMode()) {
      console.warn(
        "⚠️  Image validation tests are skipped - development environment required",
      );
      return;
    }

    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "image-validation-"));
  });

  afterAll(async () => {
    if (tempDir && isPhotoBoothDevelopmentMode()) {
      try {
        await fs.rmdir(tempDir, { recursive: true });
      } catch (error) {
        console.warn(`Failed to cleanup temp directory: ${error}`);
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

  describe("PNG Export Quality Validation", () => {
    it("validates 16:9 aspect ratio PNG export dimensions", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        mode: "light",
        aspect_ratio: "16:9",
        format: "png",
        dpi: "300",
        scale: "3",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Mock the export API to capture the actual request parameters
      const captureParams = { exportParams: null as any };
      await mockExportAPI(
        page,
        {
          success: true,
          message: "Successfully exported dashboard",
          files: ["/mock/path/export.png"],
          metadata: {
            dimensions: { width: 1920, height: 1080 },
            dpi: 300,
            format: "PNG",
          },
        },
        captureParams,
      );

      // Execute export
      const exportButton = await page.waitForSelector(
        'button:has-text("Export Dashboard")',
        { timeout: 20000 },
      );
      await exportButton.click();

      // Wait for export completion
      await page.waitForSelector("text*=Successfully exported", {
        timeout: 30000,
      });

      // Validate export parameters were correctly sent
      expect(captureParams.exportParams).toBeDefined();
      expect(captureParams.exportParams.aspect_ratio).toBe("16:9");
      expect(captureParams.exportParams.format).toBe("png");
      expect(captureParams.exportParams.dpi).toBe(300);
      expect(captureParams.exportParams.scale_factor).toBe(3);

      // Validate that CSS dimensions were correctly set during export
      const dashboard = await page.waitForSelector(".photo-booth-dashboard");
      const computedStyle = await page.evaluate((el) => {
        return {
          width: el.style.getPropertyValue("--photo-booth-width"),
          height: el.style.getPropertyValue("--photo-booth-height"),
        };
      }, dashboard);

      expect(computedStyle.width).toBe("1920px");
      expect(computedStyle.height).toBe("1080px");
    });

    it("validates 3:4 portrait aspect ratio PNG export dimensions", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        aspect_ratio: "3:4",
        format: "png",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Validate dimensions are applied correctly for portrait mode
      const dashboard = await page.waitForSelector(".photo-booth-dashboard");
      const computedStyle = await page.evaluate((el) => {
        return {
          width: el.style.getPropertyValue("--photo-booth-width"),
          height: el.style.getPropertyValue("--photo-booth-height"),
        };
      }, dashboard);

      expect(computedStyle.width).toBe("1080px");
      expect(computedStyle.height).toBe("1440px");

      // Mock export with correct portrait dimensions
      await page.route("/api/export-dashboard", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Successfully exported dashboard",
            files: ["/mock/path/portrait_export.png"],
            metadata: {
              dimensions: { width: 1080, height: 1440 },
              aspectRatio: "3:4",
            },
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 30000,
      });
    });

    it("validates high DPI export configuration", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        format: "png",
        dpi: "600", // Ultra high DPI
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let exportParams: any;
      await page.route("/api/export-dashboard", async (route) => {
        const request = route.request();
        const postData = request.postData();
        if (postData) {
          exportParams = JSON.parse(postData);
        }

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Successfully exported high DPI dashboard",
            files: ["/mock/path/high_dpi_export.png"],
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 45000,
      });

      // Validate high DPI was requested
      expect(exportParams.dpi).toBe(600);
    });
  });

  describe("SVG Export Quality Validation", () => {
    it("validates SVG export format and structure", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "trading_performance",
        format: "svg",
        aspect_ratio: "16:9",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      let exportParams: any;
      await page.route("/api/export-dashboard", async (route) => {
        const request = route.request();
        const postData = request.postData();
        if (postData) {
          exportParams = JSON.parse(postData);
        }

        // Mock SVG export response
        const mockSvgContent = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1920" height="1080" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
  <title>Trading Performance Dashboard</title>
  <rect width="1920" height="1080" fill="#ffffff"/>
  <g class="chart-container">
    <text x="960" y="50" text-anchor="middle" font-size="24">Trading Performance</text>
  </g>
</svg>`;

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Successfully exported SVG dashboard",
            files: ["/mock/path/export.svg"],
            content: mockSvgContent,
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 30000,
      });

      expect(exportParams.format).toBe("svg");
      expect(exportParams.aspect_ratio).toBe("16:9");
    });

    it("validates both PNG and SVG export when format is 'both'", async () => {
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

      let exportParams: any;
      await page.route("/api/export-dashboard", async (route) => {
        const request = route.request();
        const postData = request.postData();
        if (postData) {
          exportParams = JSON.parse(postData);
        }

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Successfully exported both formats",
            files: ["/mock/path/export.png", "/mock/path/export.svg"],
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 45000,
      });

      expect(exportParams.format).toBe("both");
    });
  });

  describe("File System Integration for Image Validation", () => {
    it("validates export file creation and basic properties", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      // Create a mock export file for validation
      const mockExportPath = path.join(tempDir, "test_export.png");

      // Create minimal valid PNG file for testing
      const pngSignature = Buffer.from([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
      ]);
      const ihdrHeader = Buffer.from([
        0x00,
        0x00,
        0x00,
        0x0d, // IHDR chunk length
        0x49,
        0x48,
        0x44,
        0x52, // "IHDR"
        0x00,
        0x00,
        0x07,
        0x80, // Width: 1920
        0x00,
        0x00,
        0x04,
        0x38, // Height: 1080
        0x08,
        0x02,
        0x00,
        0x00,
        0x00, // Bit depth, color type, compression, filter, interlace
      ]);

      // Simple PNG structure (minimal valid file)
      const mockPngData = Buffer.concat([
        pngSignature,
        ihdrHeader,
        Buffer.from([0x9d, 0xd2, 0xdb, 0xa0]), // CRC for IHDR
        Buffer.from([0x00, 0x00, 0x00, 0x00]), // IEND chunk length
        Buffer.from([0x49, 0x45, 0x4e, 0x44]), // "IEND"
        Buffer.from([0xae, 0x42, 0x60, 0x82]), // CRC for IEND
      ]);

      await fs.writeFile(mockExportPath, mockPngData);

      // Validate file was created
      const fileStats = await fs.stat(mockExportPath);
      expect(fileStats.size).toBeGreaterThan(0);

      // Validate PNG structure
      const fileBuffer = await fs.readFile(mockExportPath);
      const metadata = extractPngMetadata(fileBuffer);

      expect(metadata.isValid).toBe(true);
      expect(metadata.width).toBe(1920);
      expect(metadata.height).toBe(1080);
      expect(metadata.format).toBe("PNG");

      // Cleanup
      await fs.unlink(mockExportPath);
    });

    it("validates SVG file structure and metadata", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const mockSvgPath = path.join(tempDir, "test_export.svg");
      const mockSvgContent = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1080" height="1440" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <title>Portfolio History Portrait</title>
  <rect width="1080" height="1440" fill="#f8fafc"/>
  <g class="dashboard-content">
    <text x="540" y="50" text-anchor="middle" font-size="24">Dashboard Export</text>
  </g>
</svg>`;

      await fs.writeFile(mockSvgPath, mockSvgContent, "utf-8");

      // Validate file creation
      const fileStats = await fs.stat(mockSvgPath);
      expect(fileStats.size).toBeGreaterThan(0);

      // Validate SVG structure
      const fileBuffer = await fs.readFile(mockSvgPath);
      const metadata = extractSvgMetadata(fileBuffer);

      expect(metadata.isValid).toBe(true);
      expect(metadata.width).toBe(1080);
      expect(metadata.height).toBe(1440);
      expect(metadata.format).toBe("SVG");

      // Validate SVG contains expected elements
      const svgContent = fileBuffer.toString("utf-8");
      expect(svgContent).toContain('<?xml version="1.0"');
      expect(svgContent).toContain("<svg");
      expect(svgContent).toContain("</svg>");
      expect(svgContent).toContain('viewBox="0 0 1080 1440"');

      // Cleanup
      await fs.unlink(mockSvgPath);
    });
  });

  describe("Scale Factor and Quality Validation", () => {
    it("validates different scale factors produce appropriate export requests", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;
      const scaleFactors = [2, 3, 4];

      for (const scale of scaleFactors) {
        await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
          dashboard: "portfolio_history_portrait",
          scale: scale.toString(),
        });

        await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

        let exportParams: any;
        await page.route("/api/export-dashboard", async (route) => {
          const request = route.request();
          const postData = request.postData();
          if (postData) {
            exportParams = JSON.parse(postData);
          }

          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              success: true,
              message: `Successfully exported with ${scale}x scale`,
              files: [`/mock/path/export_${scale}x.png`],
            }),
          });
        });

        const exportButton = await page.waitForSelector(
          '[role="button"]:has-text("Export Dashboard")',
        );
        await exportButton.click();

        await page.waitForSelector("text*=Successfully exported", {
          timeout: 30000,
        });

        expect(exportParams.scale_factor).toBe(scale);

        // Small delay between tests
        await PhotoBoothE2EHelper.sleep(1000);
      }
    });

    it("validates quality settings are preserved across theme changes", async () => {
      if (!isPhotoBoothDevelopmentMode()) {
        skipIfNotDevelopmentMode();
        return;
      }

      const { page } = context;

      await photoBoothE2EHelper.navigateToPhotoBoothRobust(page, {
        dashboard: "portfolio_history_portrait",
        dpi: "600",
        scale: "4",
      });

      await photoBoothE2EHelper.waitForPhotoBoothReady(page, 30000);

      // Switch to dark theme
      const darkButton = await page.waitForSelector(
        '[role="button"]:has-text("Dark")',
      );
      await darkButton.click();

      await PhotoBoothE2EHelper.sleep(2000);

      // Verify quality settings are preserved
      const dpiSelect = await page.waitForSelector(
        'select[aria-label*="dpi" i]',
      );
      const scaleSelect = await page.waitForSelector(
        'select[aria-label*="scale" i]',
      );

      expect(await dpiSelect.inputValue()).toBe("600");
      expect(await scaleSelect.inputValue()).toBe("4");

      let exportParams: any;
      await page.route("/api/export-dashboard", async (route) => {
        const request = route.request();
        const postData = request.postData();
        if (postData) {
          exportParams = JSON.parse(postData);
        }

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Successfully exported dark theme with quality settings",
            files: ["/mock/path/dark_high_quality_export.png"],
          }),
        });
      });

      const exportButton = await page.waitForSelector(
        '[role="button"]:has-text("Export Dashboard")',
      );
      await exportButton.click();

      await page.waitForSelector("text*=Successfully exported", {
        timeout: 30000,
      });

      expect(exportParams.mode).toBe("dark");
      expect(exportParams.dpi).toBe(600);
      expect(exportParams.scale_factor).toBe(4);
    });
  });
});
