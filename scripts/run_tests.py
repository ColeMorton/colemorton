#!/usr/bin/env python3
"""
Bitcoin CLI Services Test Runner

Provides organized test execution with proper separation between unit and integration tests.
Supports different test modes for different development and CI/CD scenarios.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code"""
    print("\n{'='*60}")
    print("🔄 {description}")
    print("{'='*60}")

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except Exception:
        print("❌ Error running {description}: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Bitcoin CLI Services Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Types:
  unit        - Fast, isolated tests with mocks (no network calls)
  integration - Real API tests (requires network connectivity)
  all         - Run all tests (unit first, then integration)

Examples:
  python run_tests.py unit                    # Run only unit tests
  python run_tests.py integration             # Run only integration tests
  python run_tests.py all                     # Run all tests
  python run_tests.py unit -v                 # Run unit tests with verbose output
  python run_tests.py integration --failfast  # Stop on first integration test failure
        """,
    )

    parser.add_argument("test_type", choices=["unit", "integration", "all"], help="Type of tests to run")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose test output")

    parser.add_argument("--failfast", action="store_true", help="Stop on first test failure")

    parser.add_argument("--pattern", help="Run tests matching this pattern")

    args = parser.parse_args()

    # Build pytest command args
    pytest_args = ["python", "-m", "pytest"]

    if args.verbose:
        pytest_args.append("-v")

    if args.failfast:
        pytest_args.append("-x")

    if args.pattern:
        pytest_args.extend(["-k", args.pattern])

    exit_codes = []

    print("🧪 Bitcoin CLI Services Test Runner")
    print("Test Type: {args.test_type}")

    if args.test_type in ["unit", "all"]:
        # Unit tests - fast, isolated, no network calls
        unit_cmd = pytest_args + ["tests/unit/"]
        exit_code = run_command(unit_cmd, "Running Unit Tests (Fast, Isolated)")
        exit_codes.append(exit_code)

        if exit_code == 0:
            print("✅ Unit tests passed!")
        else:
            print("❌ Unit tests failed!")
            if args.test_type == "all" and args.failfast:
                print("⏹️ Stopping due to --failfast flag")
                return exit_code

    if args.test_type in ["integration", "all"]:
        # Integration tests - real APIs, slower, requires network
        integration_cmd = pytest_args + ["tests/integration/"]
        exit_code = run_command(integration_cmd, "Running Integration Tests (Real APIs, Network Required)")
        exit_codes.append(exit_code)

        if exit_code == 0:
            print("✅ Integration tests passed!")
        else:
            print("❌ Integration tests failed!")
            print("ℹ️ Integration test failures may be due to:")
            print("  - Network connectivity issues")
            print("  - API rate limiting or temporary unavailability")
            print("  - API response format changes")
            print("  - External service maintenance")

    # Summary
    print("\n{'='*60}")
    print("📊 Test Summary")
    print("{'='*60}")

    if args.test_type == "unit":
        total_exit_code = exit_codes[0] if exit_codes else 1
        if total_exit_code == 0:
            print("🎉 All unit tests passed! Services are working correctly with mocks.")
        else:
            print("💥 Unit tests failed! Check service logic and mocking setup.")

    elif args.test_type == "integration":
        total_exit_code = exit_codes[0] if exit_codes else 1
        if total_exit_code == 0:
            print("🎉 All integration tests passed! Services work with real APIs.")
        else:
            print("⚠️ Integration tests failed! Check network connectivity and API status.")

    elif args.test_type == "all":
        unit_code = exit_codes[0] if len(exit_codes) > 0 else 1
        integration_code = exit_codes[1] if len(exit_codes) > 1 else 1
        total_exit_code = max(unit_code, integration_code)

        if unit_code == 0 and integration_code == 0:
            print("🎉 All tests passed! Services are production-ready.")
        elif unit_code == 0 and integration_code != 0:
            print("⚠️ Unit tests passed, integration tests failed.")
            print("   Service logic is sound, but API connectivity issues exist.")
        elif unit_code != 0 and integration_code == 0:
            print("⚠️ Integration tests passed, unit tests failed.")
            print("   APIs work but service logic or mocking has issues.")
        else:
            print("💥 Both unit and integration tests failed!")
            print("   Service implementation needs attention.")

    return total_exit_code


if __name__ == "__main__":
    sys.exit(main())
