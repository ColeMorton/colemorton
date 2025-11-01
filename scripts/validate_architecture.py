#!/usr/bin/env python3
"""
Architecture Validation Script

Validates CLI-centric architecture compliance according to the engineering assessment:
- Verifies CLI wrapper pattern usage
- Checks for direct import violations
- Validates service layer abstractions
- Ensures BaseFinancialCLI compliance
"""

import re
import subprocess
import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ArchitectureValidator:
    """Validates CLI-centric architecture compliance"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.commands_dir = self.project_root / ".claude" / "commands"
        self.scripts_dir = self.project_root / "scripts"

        self.validation_results = {
            "direct_imports": {"violations": [], "status": "unknown"},
            "cli_usage": {"count": 0, "status": "unknown"},
            "base_cli_compliance": {
                "compliant": [],
                "non_compliant": [],
                "status": "unknown",
            },
            "service_factories": {"found": [], "status": "unknown"},
            "test_coverage": {"cli_tests": 0, "service_tests": 0, "status": "unknown"},
            "overall_score": 0.0,
        }

    def validate_direct_imports(self) -> tuple[list[str], bool]:
        """Check for direct Python import violations in command files"""
        violations = []

        if not self.commands_dir.exists():
            return violations, True

        for cmd_file in self.commands_dir.glob("*.md"):
            with open(cmd_file) as f:
                content = f.read()

            # Check for direct script imports
            import_patterns = [
                r"from scripts\.",
                r"import scripts\.",
                r"from \.\.scripts\.",
                r"import \.\.scripts\.",
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    violations.append(f"{cmd_file.name}: {len(matches)} direct imports")

        self.validation_results["direct_imports"]["violations"] = violations
        self.validation_results["direct_imports"]["status"] = "pass" if not violations else "fail"

        return violations, len(violations) == 0

    def count_cli_usage(self) -> int:
        """Count CLI pattern usage in command files"""
        cli_usage_count = 0

        if not self.commands_dir.exists():
            return cli_usage_count

        for cmd_file in self.commands_dir.glob("*.md"):
            with open(cmd_file) as f:
                content = f.read()

            # Count CLI usage patterns
            cli_patterns = [
                r"python\s+\w+_cli\.py",
                r"python\s+scripts/\w+_cli\.py",
                r"\w+_cli\.py",
            ]

            for pattern in cli_patterns:
                matches = re.findall(pattern, content)
                cli_usage_count += len(matches)

        self.validation_results["cli_usage"]["count"] = cli_usage_count
        self.validation_results["cli_usage"]["status"] = "pass" if cli_usage_count > 100 else "warning"

        return cli_usage_count

    def validate_base_cli_compliance(self) -> tuple[list[str], list[str]]:
        """Check CLI scripts for BaseFinancialCLI compliance"""
        compliant = []
        non_compliant = []

        for cli_file in self.scripts_dir.glob("*_cli.py"):
            with open(cli_file) as f:
                content = f.read()

            if "BaseFinancialCLI" in content:
                compliant.append(cli_file.name)
            else:
                non_compliant.append(cli_file.name)

        self.validation_results["base_cli_compliance"]["compliant"] = compliant
        self.validation_results["base_cli_compliance"]["non_compliant"] = non_compliant
        self.validation_results["base_cli_compliance"]["status"] = "pass" if len(non_compliant) <= 1 else "warning"

        return compliant, non_compliant

    def find_service_factories(self) -> list[str]:
        """Find service factory pattern implementations"""
        factories = []

        services_dir = self.scripts_dir / "services"
        if services_dir.exists():
            for service_file in services_dir.glob("*.py"):
                with open(service_file) as f:
                    content = f.read()

                # Look for factory functions
                factory_patterns = [
                    r"def create_\w+_service",
                    r"def get_\w+_service",
                    r"class \w+ServiceFactory",
                ]

                for pattern in factory_patterns:
                    if re.search(pattern, content):
                        factories.append(f"{service_file.name}: {pattern}")

        self.validation_results["service_factories"]["found"] = factories
        self.validation_results["service_factories"]["status"] = "pass" if len(factories) > 3 else "warning"

        return factories

    def count_test_coverage(self) -> tuple[int, int]:
        """Count CLI and service layer tests"""
        cli_tests = 0
        service_tests = 0

        tests_dir = self.scripts_dir / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.glob("test_*.py"):
                with open(test_file) as f:
                    content = f.read()

                if "cli" in test_file.name.lower():
                    cli_tests += len(re.findall(r"def test_", content))
                elif "service" in test_file.name.lower():
                    service_tests += len(re.findall(r"def test_", content))

        self.validation_results["test_coverage"]["cli_tests"] = cli_tests
        self.validation_results["test_coverage"]["service_tests"] = service_tests
        self.validation_results["test_coverage"]["status"] = "pass" if (cli_tests + service_tests) > 10 else "warning"

        return cli_tests, service_tests

    def run_cli_health_checks(self) -> dict[str, bool]:
        """Run health checks on CLI scripts"""
        health_results = {}

        cli_scripts = ["dashboard_generator_cli.py", "trade_history_cli.py"]

        for script in cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                try:
                    result = subprocess.run(
                        ["python", str(script_path), "health", "--env", "test"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=str(self.project_root),
                    )
                    health_results[script] = result.returncode == 0
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    health_results[script] = False
            else:
                health_results[script] = False

        return health_results

    def calculate_architecture_score(self) -> float:
        """Calculate overall architecture compliance score"""
        score = 0.0
        max_score = 100.0

        # Direct imports compliance (25 points)
        if self.validation_results["direct_imports"]["status"] == "pass":
            score += 25.0

        # CLI usage patterns (20 points)
        cli_count = self.validation_results["cli_usage"]["count"]
        if cli_count > 150:
            score += 20.0
        elif cli_count > 100:
            score += 15.0
        elif cli_count > 50:
            score += 10.0

        # BaseFinancialCLI compliance (20 points)
        compliant_count = len(self.validation_results["base_cli_compliance"]["compliant"])
        non_compliant_count = len(self.validation_results["base_cli_compliance"]["non_compliant"])

        if non_compliant_count == 0:
            score += 20.0
        elif non_compliant_count <= 2:
            score += 15.0
        elif non_compliant_count <= 5:
            score += 10.0

        # Service factories (15 points)
        factory_count = len(self.validation_results["service_factories"]["found"])
        if factory_count > 5:
            score += 15.0
        elif factory_count > 3:
            score += 10.0
        elif factory_count > 1:
            score += 5.0

        # Test coverage (20 points)
        total_tests = (
            self.validation_results["test_coverage"]["cli_tests"]
            + self.validation_results["test_coverage"]["service_tests"]
        )
        if total_tests > 20:
            score += 20.0
        elif total_tests > 10:
            score += 15.0
        elif total_tests > 5:
            score += 10.0

        self.validation_results["overall_score"] = round(score / max_score * 10.0, 1)

        return self.validation_results["overall_score"]

    def run_full_validation(self) -> dict:
        """Run complete architecture validation"""
        print("🔍 Running CLI-Centric Architecture Validation...")
        print("=" * 60)

        # 1. Direct imports validation
        print("\n1. Checking for direct import violations...")
        violations, imports_clean = self.validate_direct_imports()
        if imports_clean:
            print("   ✅ No direct import violations found")
        else:
            print("   ❌ Found {len(violations)} direct import violations:")
            for violation in violations:
                print("      - {violation}")

        # 2. CLI usage count
        print("\n2. Counting CLI usage patterns...")
        cli_count = self.count_cli_usage()
        print("   📊 Found {cli_count} CLI usage patterns in command files")

        # 3. BaseFinancialCLI compliance
        print("\n3. Validating BaseFinancialCLI compliance...")
        compliant, non_compliant = self.validate_base_cli_compliance()
        print("   ✅ {len(compliant)} CLI scripts are compliant")
        if non_compliant:
            print("   ⚠️  {len(non_compliant)} CLI scripts need BaseFinancialCLI:")
            for script in non_compliant:
                print("      - {script}")

        # 4. Service factories
        print("\n4. Finding service factory patterns...")
        factories = self.find_service_factories()
        print("   🏭 Found {len(factories)} service factory patterns")

        # 5. Test coverage
        print("\n5. Analyzing test coverage...")
        cli_tests, service_tests = self.count_test_coverage()
        print("   🧪 CLI tests: {cli_tests}, Service tests: {service_tests}")

        # 6. Health checks
        print("\n6. Running CLI health checks...")
        health_results = self.run_cli_health_checks()
        for script, healthy in health_results.items():
            status = "✅" if healthy else "❌"
            print("   {status} {script}: {'healthy' if healthy else 'failed'}")

        # 7. Calculate overall score
        print("\n7. Calculating architecture score...")
        score = self.calculate_architecture_score()
        print("   🎯 Overall Architecture Score: {score}/10")

        # Print summary
        print("\n" + "=" * 60)
        print("📋 ARCHITECTURE VALIDATION SUMMARY")
        print("=" * 60)

        if score >= 8.0:
            print("🏆 EXCELLENT: Architecture meets professional standards")
        elif score >= 7.0:
            print("✅ GOOD: Architecture is solid with minor improvements needed")
        elif score >= 6.0:
            print("⚠️  ACCEPTABLE: Architecture needs some improvements")
        else:
            print("❌ NEEDS WORK: Architecture requires significant improvements")

        # Detailed breakdown
        print("\nDetailed Breakdown:")
        print("- Direct Import Compliance: {'✅' if imports_clean else '❌'}")
        print("- CLI Usage Patterns: {cli_count} instances")
        print(f"- BaseFinancialCLI Compliance: {len(compliant)}/{len(compliant) + len(non_compliant)} scripts")
        print("- Service Factory Patterns: {len(factories)} found")
        print("- Test Coverage: {cli_tests + service_tests} tests")
        print("- Overall Score: {score}/10")

        return self.validation_results


def main():
    """Main execution function"""
    validator = ArchitectureValidator()
    results = validator.run_full_validation()

    # Exit with appropriate code
    score = results["overall_score"]
    if score >= 7.0:
        sys.exit(0)  # Success
    elif score >= 6.0:
        sys.exit(1)  # Warning
    else:
        sys.exit(2)  # Error


if __name__ == "__main__":
    main()
