import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
  readdirSync,
} from "fs";
import { join, dirname } from "path";
import { execSync } from "child_process";

export interface BaselineConfig {
  name: string;
  aspectRatio: string;
  mode: "light" | "dark";
  viewport: { width: number; height: number };
  dashboard: string;
}

export interface BaselineMetadata {
  createdAt: string;
  config: BaselineConfig;
  hash: string;
  version: string;
}

export class ScreenshotBaselineManager {
  private baselineDir: string;
  private comparisonDir: string;
  private metadataFile: string;

  constructor(testDir: string = "./src/test/e2e/screenshots") {
    this.baselineDir = join(testDir, "baselines");
    this.comparisonDir = join(testDir, "comparisons");
    this.metadataFile = join(testDir, "baseline-metadata.json");

    this.ensureDirectoriesExist();
  }

  private ensureDirectoriesExist(): void {
    [this.baselineDir, this.comparisonDir, dirname(this.metadataFile)].forEach(
      (dir) => {
        if (!existsSync(dir)) {
          mkdirSync(dir, { recursive: true });
        }
      },
    );
  }

  /**
   * Get baseline configurations for standard test scenarios
   */
  getStandardBaselines(): BaselineConfig[] {
    return [
      // Portfolio History Portrait - All aspect ratios in both themes
      {
        name: "portfolio-history-portrait-16x9-light",
        aspectRatio: "16:9",
        mode: "light",
        viewport: { width: 1920, height: 1080 },
        dashboard: "portfolio_history_portrait",
      },
      {
        name: "portfolio-history-portrait-16x9-dark",
        aspectRatio: "16:9",
        mode: "dark",
        viewport: { width: 1920, height: 1080 },
        dashboard: "portfolio_history_portrait",
      },
      {
        name: "portfolio-history-portrait-4x3-light",
        aspectRatio: "4:3",
        mode: "light",
        viewport: { width: 1440, height: 1080 },
        dashboard: "portfolio_history_portrait",
      },
      {
        name: "portfolio-history-portrait-4x3-dark",
        aspectRatio: "4:3",
        mode: "dark",
        viewport: { width: 1440, height: 1080 },
        dashboard: "portfolio_history_portrait",
      },
      {
        name: "portfolio-history-portrait-3x4-light",
        aspectRatio: "3:4",
        mode: "light",
        viewport: { width: 1080, height: 1440 },
        dashboard: "portfolio_history_portrait",
      },
      {
        name: "portfolio-history-portrait-3x4-dark",
        aspectRatio: "3:4",
        mode: "dark",
        viewport: { width: 1080, height: 1440 },
        dashboard: "portfolio_history_portrait",
      },
      // Export mode scenarios (no controls visible)
      {
        name: "export-mode-3x4-light-clean",
        aspectRatio: "3:4",
        mode: "light",
        viewport: { width: 1080, height: 1440 },
        dashboard: "portfolio_history_portrait",
      },
      {
        name: "export-mode-16x9-dark-clean",
        aspectRatio: "16:9",
        mode: "dark",
        viewport: { width: 1920, height: 1080 },
        dashboard: "portfolio_history_portrait",
      },
    ];
  }

  /**
   * Load metadata for existing baselines
   */
  loadMetadata(): Record<string, BaselineMetadata> {
    if (!existsSync(this.metadataFile)) {
      return {};
    }

    try {
      const content = readFileSync(this.metadataFile, "utf-8");
      return JSON.parse(content);
    } catch (error) {
      console.warn("Failed to load baseline metadata:", error);
      return {};
    }
  }

  /**
   * Save metadata for baselines
   */
  saveMetadata(metadata: Record<string, BaselineMetadata>): void {
    writeFileSync(this.metadataFile, JSON.stringify(metadata, null, 2));
  }

  /**
   * Generate baseline screenshot filename
   */
  getBaselineFilename(config: BaselineConfig): string {
    return `baseline-${config.name}.png`;
  }

  /**
   * Generate comparison screenshot filename
   */
  getComparisonFilename(config: BaselineConfig): string {
    return `current-${config.name}.png`;
  }

  /**
   * Generate difference screenshot filename
   */
  getDifferenceFilename(config: BaselineConfig): string {
    return `diff-${config.name}.png`;
  }

  /**
   * Get full path to baseline file
   */
  getBaselinePath(config: BaselineConfig): string {
    return join(this.baselineDir, this.getBaselineFilename(config));
  }

  /**
   * Get full path to comparison file
   */
  getComparisonPath(config: BaselineConfig): string {
    return join(this.comparisonDir, this.getComparisonFilename(config));
  }

  /**
   * Get full path to difference file
   */
  getDifferencePath(config: BaselineConfig): string {
    return join(this.comparisonDir, this.getDifferenceFilename(config));
  }

  /**
   * Check if baseline exists for given configuration
   */
  hasBaseline(config: BaselineConfig): boolean {
    return existsSync(this.getBaselinePath(config));
  }

  /**
   * Generate image hash for comparison
   */
  generateImageHash(imagePath: string): string {
    if (!existsSync(imagePath)) {
      throw new Error(`Image file not found: ${imagePath}`);
    }

    try {
      // Use system command to generate hash (fallback to simple approach)
      const hash = execSync(`shasum -a 256 "${imagePath}"`, {
        encoding: "utf-8",
      });
      return hash.split(" ")[0];
    } catch {
      // Fallback: use file size and modification time as pseudo-hash
      const stats = require("fs").statSync(imagePath);
      return `${stats.size}-${stats.mtime.getTime()}`;
    }
  }

  /**
   * Create or update baseline
   */
  updateBaseline(config: BaselineConfig, screenshotPath: string): void {
    const baselinePath = this.getBaselinePath(config);
    const metadata = this.loadMetadata();

    // Copy screenshot to baseline location
    const imageBuffer = readFileSync(screenshotPath);
    writeFileSync(baselinePath, imageBuffer);

    // Update metadata
    metadata[config.name] = {
      createdAt: new Date().toISOString(),
      config,
      hash: this.generateImageHash(baselinePath),
      version: process.env.npm_package_version || "1.0.0",
    };

    this.saveMetadata(metadata);
    console.log(`Updated baseline: ${config.name}`);
  }

  /**
   * Compare screenshot with baseline
   */
  async compareWithBaseline(
    config: BaselineConfig,
    screenshotPath: string,
  ): Promise<{
    matches: boolean;
    baselinePath: string;
    comparisonPath: string;
    differencePath?: string;
    similarity?: number;
  }> {
    const baselinePath = this.getBaselinePath(config);
    const comparisonPath = this.getComparisonPath(config);

    if (!existsSync(baselinePath)) {
      throw new Error(
        `No baseline found for ${config.name}. Run with UPDATE_BASELINES=true to create it.`,
      );
    }

    // Copy current screenshot to comparison location
    const imageBuffer = readFileSync(screenshotPath);
    writeFileSync(comparisonPath, imageBuffer);

    // Simple hash comparison (in production, you might use a more sophisticated image diff tool)
    const baselineHash = this.generateImageHash(baselinePath);
    const comparisonHash = this.generateImageHash(comparisonPath);

    const matches = baselineHash === comparisonHash;

    const result = {
      matches,
      baselinePath,
      comparisonPath,
    };

    if (!matches) {
      // In a real implementation, you might generate a visual diff image here
      // For now, we'll just note that they're different
      console.log(`Visual difference detected for ${config.name}`);
      console.log(`Baseline: ${baselinePath}`);
      console.log(`Current: ${comparisonPath}`);

      return {
        ...result,
        differencePath: this.getDifferencePath(config),
        similarity: this.calculateSimilarity(baselinePath, comparisonPath),
      };
    }

    return result;
  }

  /**
   * Calculate simple similarity score between two images
   * In production, you'd use a proper image comparison library
   */
  private calculateSimilarity(baseline: string, comparison: string): number {
    try {
      const baselineStats = require("fs").statSync(baseline);
      const comparisonStats = require("fs").statSync(comparison);

      // Simple size-based similarity (not accurate but serves as placeholder)
      const sizeDiff = Math.abs(baselineStats.size - comparisonStats.size);
      const maxSize = Math.max(baselineStats.size, comparisonStats.size);

      return Math.max(0, 1 - sizeDiff / maxSize);
    } catch {
      return 0;
    }
  }

  /**
   * Clean up old comparison and difference files
   */
  cleanupComparisons(): void {
    if (existsSync(this.comparisonDir)) {
      const files = readdirSync(this.comparisonDir);
      files.forEach((file) => {
        const filePath = join(this.comparisonDir, file);
        require("fs").unlinkSync(filePath);
      });
      console.log(`Cleaned up ${files.length} comparison files`);
    }
  }

  /**
   * List all available baselines
   */
  listBaselines(): BaselineConfig[] {
    const metadata = this.loadMetadata();
    return Object.values(metadata).map((m) => m.config);
  }

  /**
   * Generate URL for given configuration
   */
  generateTestURL(baseURL: string, config: BaselineConfig): string {
    return `${baseURL}/photo-booth?dashboard=${config.dashboard}&aspect_ratio=${config.aspectRatio}&mode=${config.mode}`;
  }

  /**
   * Validate baseline integrity
   */
  validateBaselines(): {
    valid: string[];
    invalid: string[];
    missing: string[];
  } {
    const metadata = this.loadMetadata();
    const valid: string[] = [];
    const invalid: string[] = [];
    const missing: string[] = [];

    for (const [name, meta] of Object.entries(metadata)) {
      const baselinePath = this.getBaselinePath(meta.config);

      if (!existsSync(baselinePath)) {
        missing.push(name);
        continue;
      }

      try {
        const currentHash = this.generateImageHash(baselinePath);
        if (currentHash === meta.hash) {
          valid.push(name);
        } else {
          invalid.push(name);
        }
      } catch {
        invalid.push(name);
      }
    }

    return { valid, invalid, missing };
  }
}

// Export singleton instance
export const baselineManager = new ScreenshotBaselineManager();
