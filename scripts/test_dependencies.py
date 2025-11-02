#!/usr/bin/env python3
"""
Dependency Compatibility Testing Framework

Tests critical dependency combinations to ensure compatibility
across the multi-component system.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any


class DependencyTester:
    """Tests dependency compatibility and functionality."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = self.project_root / "frontend"

    def run_python_tests(self) -> bool:
        """Run Python test suite to validate dependency compatibility."""
        try:
            self.logger.info("Running Python tests...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self.logger.info("Python tests passed")
                return True
            self.logger.error(f"Python tests failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error("Python tests timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error running Python tests: {e}")
            return False

    def run_frontend_tests(self) -> bool:
        """Run frontend test suite to validate dependency compatibility."""
        try:
            self.logger.info("Running frontend tests...")
            result = subprocess.run(
                ["yarn", "test"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self.logger.info("Frontend tests passed")
                return True
            self.logger.error(f"Frontend tests failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error("Frontend tests timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error running frontend tests: {e}")
            return False

    def test_python_build(self) -> bool:
        """Test Python module imports and basic functionality."""
        try:
            self.logger.info("Testing Python dependencies...")

            # Test core dependencies
            critical_imports = [
                "pandas",
                "numpy",
                "yaml",
                "sklearn",
                "requests",
                "sqlalchemy",
            ]

            for module in critical_imports:
                try:
                    __import__(module)
                    self.logger.debug(f"Successfully imported {module}")
                except ImportError as e:
                    self.logger.error(f"Failed to import {module}: {e}")
                    return False

            self.logger.info("Python dependencies test passed")
            return True

        except Exception as e:
            self.logger.error(f"Error testing Python dependencies: {e}")
            return False

    def test_frontend_build(self) -> bool:
        """Test frontend build process."""
        try:
            self.logger.info("Testing frontend build...")
            result = subprocess.run(
                ["yarn", "build"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.logger.info("Frontend build succeeded")
                return True
            self.logger.error(f"Frontend build failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error("Frontend build timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error testing frontend build: {e}")
            return False

    def run_security_scans(self) -> dict[str, Any]:
        """Run security scans on dependencies."""
        results = {
            "python_safety": False,
            "python_bandit": False,
            "frontend_audit": False,
        }

        try:
            # Python safety check
            safety_result = subprocess.run(
                [sys.executable, "-m", "safety", "scan"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            results["python_safety"] = safety_result.returncode == 0

            # Python bandit check
            bandit_result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", "scripts/", "-f", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if bandit_result.returncode == 0:
                bandit_output = json.loads(bandit_result.stdout)
                results["python_bandit"] = len(bandit_output.get("results", [])) == 0

            # Frontend audit
            audit_result = subprocess.run(
                ["yarn", "audit", "--level", "moderate"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            results["frontend_audit"] = audit_result.returncode == 0

        except Exception as e:
            self.logger.error(f"Error running security scans: {e}")

        return results

    def generate_compatibility_report(self) -> dict[str, Any]:
        """Generate comprehensive compatibility report."""
        report = {
            "timestamp": subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip(),
            "python_build": self.test_python_build(),
            "frontend_build": self.test_frontend_build(),
            "python_tests": self.run_python_tests(),
            "frontend_tests": self.run_frontend_tests(),
            "security_scans": self.run_security_scans(),
        }

        # Overall compatibility status
        report["overall_status"] = all(
            [
                report["python_build"],
                report["frontend_build"],
                report["python_tests"],
                report["frontend_tests"],
            ]
        )

        return report


def main() -> int:
    """Main function to run dependency compatibility tests."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    tester = DependencyTester()

    print("Running Dependency Compatibility Tests...")
    print("=" * 50)

    report = tester.generate_compatibility_report()

    # Print summary
    print("\nCompatibility Test Results ({report['timestamp']})")
    print("-" * 50)
    print("Python Build:     {'✅ PASS' if report['python_build'] else '❌ FAIL'}")
    print("Frontend Build:   {'✅ PASS' if report['frontend_build'] else '❌ FAIL'}")
    print("Python Tests:     {'✅ PASS' if report['python_tests'] else '❌ FAIL'}")
    print("Frontend Tests:   {'✅ PASS' if report['frontend_tests'] else '❌ FAIL'}")

    security = report["security_scans"]
    print(f"Python Safety:    {'✅ PASS' if security['python_safety'] else '⚠️  ISSUES'}")
    print(f"Python Bandit:    {'✅ PASS' if security['python_bandit'] else '⚠️  ISSUES'}")
    print(f"Frontend Audit:   {'✅ PASS' if security['frontend_audit'] else '⚠️  ISSUES'}")

    print(f"\nOverall Status:   {'✅ COMPATIBLE' if report['overall_status'] else '❌ ISSUES FOUND'}")

    # Save detailed report
    report_file = Path("dependency_compatibility_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print("\nDetailed report saved to: {report_file}")

    return 0 if report["overall_status"] else 1


if __name__ == "__main__":
    sys.exit(main())
