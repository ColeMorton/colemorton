#!/usr/bin/env node

/**
 * Photo Booth Test Suite Runner
 *
 * This script provides a unified interface for running all photo-booth related tests.
 * It can run unit tests, integration tests, E2E tests, or all tests together.
 *
 * Usage:
 *   npm run test:photo-booth              # Run all photo-booth tests
 *   npm run test:photo-booth unit         # Run only unit tests
 *   npm run test:photo-booth integration  # Run only integration tests
 *   npm run test:photo-booth e2e          # Run only E2E tests
 *   npm run test:photo-booth --coverage   # Run all tests with coverage
 *   npm run test:photo-booth --watch      # Run tests in watch mode
 */

import { spawn } from "child_process";
import { dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface TestConfig {
  name: string;
  description: string;
  patterns: string[];
  options?: string[];
}

const TEST_CONFIGS: Record<string, TestConfig> = {
  unit: {
    name: "Unit Tests",
    description: "Component and utility unit tests",
    patterns: ["src/test/photo-booth/unit/**/*.test.{ts,tsx}"],
  },
  integration: {
    name: "Integration Tests",
    description: "Workflow and component integration tests",
    patterns: ["src/test/photo-booth/integration/**/*.test.{ts,tsx}"],
  },
  e2e: {
    name: "E2E Tests",
    description: "End-to-end browser tests",
    patterns: ["src/test/photo-booth/e2e/**/*.test.{ts,tsx}"],
    options: ["--testTimeout=60000"], // Longer timeout for E2E tests
  },
  all: {
    name: "All Photo-Booth Tests",
    description: "All photo-booth related tests",
    patterns: ["src/test/photo-booth/**/*.test.{ts,tsx}"],
  },
};

function parseArgs(): {
  testType: string;
  coverage: boolean;
  watch: boolean;
  verbose: boolean;
  help: boolean;
} {
  const args = process.argv.slice(2);

  const testType = args.find((arg) => !arg.startsWith("--")) || "all";
  const coverage = args.includes("--coverage");
  const watch = args.includes("--watch");
  const verbose = args.includes("--verbose") || args.includes("-v");
  const help = args.includes("--help") || args.includes("-h");

  return { testType, coverage, watch, verbose, help };
}

function printHelp(): void {
  console.log(`
Photo Booth Test Suite Runner

USAGE:
  npm run test:photo-booth [TEST_TYPE] [OPTIONS]

TEST TYPES:
  unit         ${TEST_CONFIGS.unit.description}
  integration  ${TEST_CONFIGS.integration.description}
  e2e          ${TEST_CONFIGS.e2e.description}
  all          ${TEST_CONFIGS.all.description} (default)

OPTIONS:
  --coverage   Generate test coverage report
  --watch      Run tests in watch mode
  --verbose    Enable verbose output
  --help       Show this help message

EXAMPLES:
  npm run test:photo-booth                # Run all photo-booth tests
  npm run test:photo-booth unit           # Run only unit tests
  npm run test:photo-booth e2e --coverage # Run E2E tests with coverage
  npm run test:photo-booth --watch        # Run all tests in watch mode
`);
}

async function runTests(
  testType: string,
  coverage: boolean,
  watch: boolean,
  verbose: boolean,
): Promise<number> {
  const config = TEST_CONFIGS[testType];

  if (!config) {
    console.error(`❌ Unknown test type: ${testType}`);
    console.error(`Available types: ${Object.keys(TEST_CONFIGS).join(", ")}`);
    return 1;
  }

  console.log(`🧪 Running ${config.name}: ${config.description}\n`);

  const vitestArgs = [...config.patterns, "--run"];

  if (watch) {
    vitestArgs.pop(); // Remove --run
    vitestArgs.push("--watch");
  }

  if (coverage) {
    vitestArgs.push("--coverage");
  }

  if (verbose) {
    vitestArgs.push("--reporter=verbose");
  }

  if (config.options) {
    vitestArgs.push(...config.options);
  }

  if (verbose) {
    console.log(`🔧 Running command: vitest ${vitestArgs.join(" ")}\n`);
  }

  return new Promise((resolve) => {
    const child = spawn("npx", ["vitest", ...vitestArgs], {
      stdio: "inherit",
      shell: true,
      cwd: resolve(__dirname, "../../../.."),
    });

    child.on("close", (code) => {
      if (code === 0) {
        console.log(`\n✅ ${config.name} completed successfully`);
      } else {
        console.log(`\n❌ ${config.name} failed with exit code ${code}`);
      }
      resolve(code || 0);
    });

    child.on("error", (error) => {
      console.error(`❌ Failed to start tests: ${error.message}`);
      resolve(1);
    });
  });
}

async function main(): Promise<void> {
  const { testType, coverage, watch, verbose, help } = parseArgs();

  if (help) {
    printHelp();
    process.exit(0);
  }

  const startTime = Date.now();
  const exitCode = await runTests(testType, coverage, watch, verbose);
  const duration = Math.round((Date.now() - startTime) / 1000);

  console.log(`\n⏱️  Total duration: ${duration}s`);

  process.exit(exitCode);
}

// Handle graceful shutdown
process.on("SIGINT", () => {
  console.log("\n👋 Test run interrupted");
  process.exit(130);
});

process.on("SIGTERM", () => {
  console.log("\n👋 Test run terminated");
  process.exit(143);
});

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error("❌ Unexpected error:", error);
    process.exit(1);
  });
}
