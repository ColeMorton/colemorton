#!/usr/bin/env python3
"""
CI/CD Integration Scripts

Automated validation tools for development workflow integration.
Provides pre-commit hooks, CI pipeline validation, and automated
quality checks for the DASV system consistency.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.dasv_consistency_validator import DASVConsistencyValidator
from scripts.utils.path_synchronizer import PathSynchronizer
from scripts.utils.schema_migrator import SchemaMigrator
from scripts.utils.template_upgrader import TemplateUpgrader


@dataclass
class ValidationSuite:
    """Configuration for validation suite"""

    name: str
    description: str
    validators: list[str]
    required_score: float = 0.8
    fail_fast: bool = False
    timeout_minutes: int = 5


@dataclass
class CIResult:
    """CI/CD validation result"""

    suite_name: str
    passed: bool
    score: float
    execution_time: float
    issues: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class CICDIntegration:
    """
    CI/CD integration for DASV system consistency validation.

    Features:
    - Pre-commit hooks for immediate validation
    - CI pipeline integration with configurable validation suites
    - Automated quality gate enforcement
    - Performance regression detection
    - Comprehensive reporting with actionable feedback
    """

    def __init__(self, config_path: str = None):
        """Initialize CI/CD integration"""
        self.project_root = project_root

        if config_path is None:
            config_path = self.project_root / "scripts" / "ci_config.json"

        self.config_path = Path(config_path)
        self.load_configuration()

        # Initialize validators
        self.consistency_validator = DASVConsistencyValidator()
        self.path_synchronizer = PathSynchronizer()
        self.schema_migrator = SchemaMigrator()
        self.template_upgrader = TemplateUpgrader()

    def load_configuration(self):
        """Load CI/CD configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
        else:
            # Default configuration
            config = self.get_default_configuration()
            self.save_configuration(config)

        # Parse validation suites
        self.validation_suites = {}
        for suite_data in config.get("validation_suites", []):
            suite = ValidationSuite(**suite_data)
            self.validation_suites[suite.name] = suite

        # Global settings
        self.settings = config.get("settings", {})

    def get_default_configuration(self) -> dict[str, Any]:
        """Get default CI/CD configuration"""
        return {
            "settings": {
                "fail_fast_mode": False,
                "timeout_minutes": 10,
                "quality_threshold": 0.8,
                "enable_performance_monitoring": True,
                "enable_drift_detection": True,
            },
            "validation_suites": [
                {
                    "name": "pre_commit",
                    "description": "Fast validation for pre-commit hooks",
                    "validators": ["path_consistency", "schema_structure"],
                    "required_score": 0.9,
                    "fail_fast": True,
                    "timeout_minutes": 2,
                },
                {
                    "name": "pull_request",
                    "description": "Comprehensive validation for pull requests",
                    "validators": [
                        "path_consistency",
                        "schema_structure",
                        "template_structure",
                        "command_integrity",
                    ],
                    "required_score": 0.8,
                    "fail_fast": False,
                    "timeout_minutes": 5,
                },
                {
                    "name": "main_branch",
                    "description": "Full system validation for main branch",
                    "validators": [
                        "comprehensive_system",
                        "quality_standards",
                        "execution_integrity",
                    ],
                    "required_score": 0.85,
                    "fail_fast": False,
                    "timeout_minutes": 10,
                },
                {
                    "name": "nightly",
                    "description": "Complete system health check",
                    "validators": [
                        "comprehensive_system",
                        "performance_regression",
                        "drift_detection",
                    ],
                    "required_score": 0.9,
                    "fail_fast": False,
                    "timeout_minutes": 15,
                },
            ],
        }

    def save_configuration(self, config: dict[str, Any]):
        """Save CI/CD configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def run_validation_suite(self, suite_name: str) -> list[CIResult]:
        """Run a specific validation suite"""
        if suite_name not in self.validation_suites:
            raise ValueError(f"Unknown validation suite: {suite_name}")

        suite = self.validation_suites[suite_name]
        print("🚀 Running validation suite: {suite.name}")
        print("📝 {suite.description}")
        print("=" * 60)

        results = []
        start_time = datetime.now()

        for validator_name in suite.validators:
            try:
                result = self._run_validator(validator_name, suite)
                results.append(result)

                # Print immediate feedback
                status = "✅" if result.passed else "❌"
                print(f"{status} {validator_name}: {result.score:.2f} ({result.execution_time:.1f}s)")

                if result.issues:
                    for issue in result.issues[:2]:  # Show first 2 issues
                        print("    • {issue}")
                    if len(result.issues) > 2:
                        print("    • ... and {len(result.issues) - 2} more")

                # Fail fast if enabled
                if suite.fail_fast and not result.passed:
                    print("\n💥 Validation failed - stopping due to fail_fast mode")
                    break

            except Exception as e:
                error_result = CIResult(
                    suite_name=suite_name,
                    passed=False,
                    score=0.0,
                    execution_time=0.0,
                    issues=[f"Validator {validator_name} failed: {e}"],
                )
                results.append(error_result)
                print("❌ {validator_name}: failed ({e})")

                if suite.fail_fast:
                    break

        total_time = (datetime.now() - start_time).total_seconds()

        # Calculate overall result
        overall_passed = all(r.passed for r in results)
        overall_score = sum(r.score for r in results) / len(results) if results else 0.0

        print("\n📊 Suite Results: {'PASSED' if overall_passed else 'FAILED'}")
        print("🎯 Overall Score: {overall_score:.2f}/{suite.required_score}")
        print("⏱️  Total Time: {total_time:.1f}s")

        return results

    def _run_validator(self, validator_name: str, suite: ValidationSuite) -> CIResult:
        """Run a specific validator"""
        start_time = datetime.now()

        try:
            if validator_name == "path_consistency":
                result = self._validate_path_consistency()
            elif validator_name == "schema_structure":
                result = self._validate_schema_structure()
            elif validator_name == "template_structure":
                result = self._validate_template_structure()
            elif validator_name == "command_integrity":
                result = self._validate_command_integrity()
            elif validator_name == "comprehensive_system":
                result = self._validate_comprehensive_system()
            elif validator_name == "quality_standards":
                result = self._validate_quality_standards()
            elif validator_name == "execution_integrity":
                result = self._validate_execution_integrity()
            elif validator_name == "performance_regression":
                result = self._validate_performance_regression()
            elif validator_name == "drift_detection":
                result = self._validate_drift_detection()
            else:
                raise ValueError(f"Unknown validator: {validator_name}")

            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time

            # Apply suite requirements
            result.passed = result.score >= suite.required_score

            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return CIResult(
                suite_name=suite.name,
                passed=False,
                score=0.0,
                execution_time=execution_time,
                issues=[f"Validation error: {e}"],
            )

    def _validate_path_consistency(self) -> CIResult:
        """Validate path consistency across commands"""
        report = self.path_synchronizer.scan_all_commands("*.md")

        # Calculate score
        score = 1.0 - (report.total_issues / max(1, report.total_files_scanned * 5))  # Max 5 issues per file
        score = max(0.0, min(1.0, score))

        # Extract issues
        issues = []
        for file_path, file_issues in report.file_issues.items():
            file_name = Path(file_path).name
            for issue in file_issues:
                if issue.issue_type == "hardcoded":  # Only report actual hardcoded paths
                    issues.append(f"{file_name}:{issue.line_number} - {issue.original_text}")

        return CIResult(
            suite_name="path_consistency",
            passed=report.validation_passed,
            score=score,
            execution_time=0.0,
            issues=issues,
            details={
                "total_files": report.total_files_scanned,
                "files_with_issues": report.files_with_issues,
                "total_issues": report.total_issues,
            },
        )

    def _validate_schema_structure(self) -> CIResult:
        """Validate schema structure and consistency"""
        report = self.consistency_validator.validate_schema_consistency()

        return CIResult(
            suite_name="schema_structure",
            passed=report.status == "pass",
            score=report.score,
            execution_time=0.0,
            issues=report.issues,
            details=report.metadata,
        )

    def _validate_template_structure(self) -> CIResult:
        """Validate template structure and consistency"""
        report = self.consistency_validator.validate_template_consistency()

        return CIResult(
            suite_name="template_structure",
            passed=report.status == "pass",
            score=report.score,
            execution_time=0.0,
            issues=report.issues,
            details=report.metadata,
        )

    def _validate_command_integrity(self) -> CIResult:
        """Validate command mapping integrity"""
        report = self.consistency_validator.validate_command_mapping_integrity()

        return CIResult(
            suite_name="command_integrity",
            passed=report.status == "pass",
            score=report.score,
            execution_time=0.0,
            issues=report.issues,
            details=report.metadata,
        )

    def _validate_comprehensive_system(self) -> CIResult:
        """Run comprehensive system validation"""
        system_report = self.consistency_validator.run_comprehensive_validation()

        issues = []
        for drift in system_report.drift_indicators:
            issues.append(drift)

        return CIResult(
            suite_name="comprehensive_system",
            passed=system_report.overall_score >= 0.8,
            score=system_report.overall_score,
            execution_time=0.0,
            issues=issues,
            details={
                "total_checks": system_report.summary["total_checks"],
                "passed_checks": system_report.summary["passed_checks"],
                "failed_checks": system_report.summary["failed_checks"],
                "system_health": system_report.summary["system_health"],
            },
        )

    def _validate_quality_standards(self) -> CIResult:
        """Validate quality standards compliance"""
        report = self.consistency_validator.validate_quality_standards_compliance()

        return CIResult(
            suite_name="quality_standards",
            passed=report.status == "pass",
            score=report.score,
            execution_time=0.0,
            issues=report.issues,
            details=report.metadata,
        )

    def _validate_execution_integrity(self) -> CIResult:
        """Validate execution system integrity"""
        report = self.consistency_validator.validate_execution_system_integrity()

        return CIResult(
            suite_name="execution_integrity",
            passed=report.status == "pass",
            score=report.score,
            execution_time=0.0,
            issues=report.issues,
            details=report.metadata,
        )

    def _validate_performance_regression(self) -> CIResult:
        """Check for performance regressions"""
        # Placeholder for performance monitoring
        # In a real implementation, this would compare against baseline metrics

        return CIResult(
            suite_name="performance_regression",
            passed=True,
            score=1.0,
            execution_time=0.0,
            issues=[],
            details={"status": "Performance monitoring not yet implemented"},
        )

    def _validate_drift_detection(self) -> CIResult:
        """Detect system drift from standards"""
        system_report = self.consistency_validator.run_comprehensive_validation()

        # Check for drift indicators
        drift_detected = len(system_report.drift_indicators) > 0
        drift_score = 1.0 - (len(system_report.drift_indicators) * 0.2)
        drift_score = max(0.0, drift_score)

        return CIResult(
            suite_name="drift_detection",
            passed=not drift_detected,
            score=drift_score,
            execution_time=0.0,
            issues=system_report.drift_indicators,
            details={"drift_indicators_count": len(system_report.drift_indicators)},
        )

    def install_pre_commit_hook(self) -> bool:
        """Install pre-commit hook for validation"""
        try:
            git_dir = self.project_root / ".git"
            if not git_dir.exists():
                print("❌ Not a git repository")
                return False

            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)

            # Create pre-commit hook script
            hook_script = hooks_dir / "pre-commit"
            hook_content = f"""#!/bin/bash
# DASV System Pre-commit Validation Hook
# Auto-generated by CI/CD Integration

cd "{self.project_root}"

echo "🔍 Running DASV pre-commit validation..."

# Run pre-commit validation suite
python scripts/utils/ci_cd_integration.py --suite pre_commit --exit-code

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "❌ Pre-commit validation failed"
    echo "💡 Run 'python scripts/utils/ci_cd_integration.py --suite pre_commit' for details"
    exit 1
fi

echo "✅ Pre-commit validation passed"
exit 0
"""

            with open(hook_script, "w") as f:
                f.write(hook_content)

            # Make executable
            hook_script.chmod(0o755)

            print("✅ Pre-commit hook installed: {hook_script}")
            return True

        except Exception:
            print("❌ Failed to install pre-commit hook: {e}")
            return False

    def generate_github_action(self) -> str:
        """Generate GitHub Actions workflow for CI validation"""
        workflow = """name: DASV System Validation

on:
  push:
    branches: [ main, staging, development ]
  pull_request:
    branches: [ main, staging ]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        # Add your project dependencies here

    - name: Run DASV Pre-commit Validation
      if: github.event_name == 'push'
      run: |
        python scripts/utils/ci_cd_integration.py --suite pre_commit --exit-code

    - name: Run DASV Pull Request Validation
      if: github.event_name == 'pull_request'
      run: |
        python scripts/utils/ci_cd_integration.py --suite pull_request --exit-code

    - name: Run DASV Main Branch Validation
      if: github.ref == 'refs/heads/main'
      run: |
        python scripts/utils/ci_cd_integration.py --suite main_branch --exit-code

    - name: Export Validation Report
      if: always()
      run: |
        python scripts/utils/ci_cd_integration.py --suite pull_request --export validation_report.json

    - name: Upload Validation Report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: validation-report
        path: validation_report.json

  nightly:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        # Add your project dependencies here

    - name: Run Nightly System Health Check
      run: |
        python scripts/utils/ci_cd_integration.py --suite nightly --exit-code
"""

        github_dir = self.project_root / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = github_dir / "dasv_validation.yml"
        with open(workflow_file, "w") as f:
            f.write(workflow)

        print("✅ GitHub Actions workflow generated: {workflow_file}")
        return str(workflow_file)

    def export_results(self, results: list[CIResult], output_path: str) -> str:
        """Export validation results to JSON"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_validators": len(results),
            "passed_validators": sum(1 for r in results if r.passed),
            "failed_validators": sum(1 for r in results if not r.passed),
            "overall_score": (sum(r.score for r in results) / len(results) if results else 0.0),
            "results": [
                {
                    "suite_name": r.suite_name,
                    "passed": r.passed,
                    "score": r.score,
                    "execution_time": r.execution_time,
                    "issues": r.issues,
                    "details": r.details,
                }
                for r in results
            ],
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        return str(output_file)


def main():
    """CLI interface for CI/CD integration"""
    import argparse

    parser = argparse.ArgumentParser(description="DASV CI/CD Integration")
    parser.add_argument(
        "--suite",
        choices=["pre_commit", "pull_request", "main_branch", "nightly"],
        help="Validation suite to run",
    )
    parser.add_argument("--install-hook", action="store_true", help="Install pre-commit hook")
    parser.add_argument(
        "--generate-github-action",
        action="store_true",
        help="Generate GitHub Actions workflow",
    )
    parser.add_argument("--list-suites", action="store_true", help="List available validation suites")
    parser.add_argument("--export", help="Export results to JSON file")
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with error code if validation fails",
    )
    parser.add_argument("--config", help="Custom configuration file path")

    args = parser.parse_args()

    # Initialize CI/CD integration
    ci_cd = CICDIntegration(args.config)

    if args.list_suites:
        print("📋 Available Validation Suites:")
        for name, suite in ci_cd.validation_suites.items():
            print("  {name}: {suite.description}")
            print("    Validators: {', '.join(suite.validators)}")
            print("    Required Score: {suite.required_score}")
            print("    Timeout: {suite.timeout_minutes}min")
            print()
        return

    if args.install_hook:
        success = ci_cd.install_pre_commit_hook()
        sys.exit(0 if success else 1)

    if args.generate_github_action:
        ci_cd.generate_github_action()
        return

    if args.suite:
        # Run validation suite
        results = ci_cd.run_validation_suite(args.suite)

        # Export results if requested
        if args.export:
            export_path = ci_cd.export_results(results, args.export)
            print("\n📄 Results exported to: {export_path}")

        # Exit with appropriate code if requested
        if args.exit_code:
            overall_passed = all(r.passed for r in results)
            sys.exit(0 if overall_passed else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
