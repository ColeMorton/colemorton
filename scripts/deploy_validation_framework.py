#!/usr/bin/env python3
"""
Enhanced Validation Framework Deployment

Deploys the comprehensive validation framework with fail-fast quality gates,
real-time data validation, and cross-phase consistency checks.

Features:
- Fail-fast validation with immediate feedback
- Real-time data staleness detection
- Variance threshold monitoring
- Cross-validation across DASV phases
- Quality gate enforcement for institutional standards

Usage:
    python scripts/deploy_validation_framework.py --check-installation
    python scripts/deploy_validation_framework.py --validate-region US_20250812
    python scripts/deploy_validation_framework.py --full-pipeline-check
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.services.macro_economic import create_macro_economic_service
    from scripts.utils.dasv_cross_validator import DASVCrossValidator
    from scripts.utils.fed_rate_validation import FedRateValidator
except ImportError:
    print("Error importing validation components: {e}")
    print("Please ensure all validation utilities are properly installed")
    sys.exit(1)


class ValidationFrameworkDeployer:
    """
    Deployment manager for enhanced validation framework
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_config = {
            "variance_threshold": 0.02,
            "staleness_hours": 6,
            "min_institutional_score": 0.9,
            "fail_fast_enabled": True,
        }

        # Quality gates configuration
        self.quality_gates = {
            "data_freshness": {
                "threshold": 0.9,
                "blocking": True,
                "description": "Data must be fresh within staleness threshold",
            },
            "variance_compliance": {
                "threshold": 0.02,
                "blocking": True,
                "description": "Data variance must be within acceptable limits",
            },
            "cross_validation": {
                "threshold": 0.85,
                "blocking": True,
                "description": "Cross-phase validation must pass",
            },
            "institutional_quality": {
                "threshold": 0.9,
                "blocking": True,
                "description": "Must meet institutional quality standards",
            },
        }

    def check_installation(self) -> dict[str, bool]:
        """Check if all validation components are properly installed"""
        results = {}

        # Check validation utilities
        try:
            from scripts.utils.dasv_cross_validator import DASVCrossValidator

            results["dasv_cross_validator"] = True
        except ImportError:
            results["dasv_cross_validator"] = False

        try:
            from scripts.utils.fed_rate_validation import FedRateValidator

            results["fed_rate_validator"] = True
        except ImportError:
            results["fed_rate_validator"] = False

        # Check schemas
        schema_files = [
            "scripts/schemas/macro_analysis_discovery_schema.json",
            "scripts/schemas/macro_analysis_analysis_schema.json",
            "scripts/schemas/macro_analysis_validation_schema.json",
        ]

        for schema_file in schema_files:
            schema_path = self.project_root / schema_file
            results[f"schema_{Path(schema_file).stem}"] = schema_path.exists()

        # Check services
        try:
            service = create_macro_economic_service("dev")
            results["macro_economic_service"] = True
        except Exception:
            results["macro_economic_service"] = False

        # Check output directories
        output_dirs = [
            "data/outputs/macro_analysis/discovery",
            "data/outputs/macro_analysis/analysis",
            "data/outputs/macro_analysis/validation",
        ]

        for output_dir in output_dirs:
            dir_path = self.project_root / output_dir
            results[f"output_dir_{output_dir.split('/')[-1]}"] = dir_path.exists()

        return results

    def validate_region(self, region_date: str) -> dict[str, any]:
        """Validate a specific region using the enhanced framework"""
        try:
            # Initialize cross-validator
            validator = DASVCrossValidator(
                variance_threshold=self.validation_config["variance_threshold"],
                staleness_hours=self.validation_config["staleness_hours"],
            )

            # Run full pipeline validation
            report = validator.validate_full_pipeline(region_date)

            # Apply quality gates
            gate_results = self._apply_quality_gates(report)

            # Generate deployment status
            deployment_status = {
                "validation_passed": report.overall_passed,
                "overall_score": report.overall_score,
                "quality_gates": gate_results,
                "institutional_certified": report.overall_score >= self.validation_config["min_institutional_score"],
                "blocking_issues": report.blocking_issues,
                "critical_issues": report.critical_issues,
                "recommendations": report.recommendations,
                "metadata": {
                    "region_date": region_date,
                    "validation_timestamp": datetime.now().isoformat(),
                    "framework_version": "enhanced_v1.0",
                    "fail_fast_enabled": self.validation_config["fail_fast_enabled"],
                },
            }

            return deployment_status

        except Exception as e:
            return {
                "validation_passed": False,
                "error": str(e),
                "metadata": {
                    "region_date": region_date,
                    "validation_timestamp": datetime.now().isoformat(),
                    "framework_version": "enhanced_v1.0",
                },
            }

    def run_full_pipeline_check(self) -> dict[str, any]:
        """Run comprehensive pipeline validation check"""
        results = {
            "installation_check": self.check_installation(),
            "validation_framework_status": {},
            "quality_gates_status": {},
            "recommendations": [],
        }

        # Check installation status
        installation_issues = [component for component, status in results["installation_check"].items() if not status]

        if installation_issues:
            results["validation_framework_status"]["status"] = "degraded"
            results["validation_framework_status"]["missing_components"] = installation_issues
            results["recommendations"].extend(
                [f"Install missing component: {component}" for component in installation_issues]
            )
        else:
            results["validation_framework_status"]["status"] = "operational"
            results["validation_framework_status"]["all_components_installed"] = True

        # Check quality gates configuration
        for gate_name, gate_config in self.quality_gates.items():
            results["quality_gates_status"][gate_name] = {
                "configured": True,
                "threshold": gate_config["threshold"],
                "blocking": gate_config["blocking"],
                "description": gate_config["description"],
            }

        # Check for existing validation outputs
        validation_dir = self.project_root / "data/outputs/macro_analysis/validation"
        if validation_dir.exists():
            validation_files = list(validation_dir.glob("*.json"))
            results["validation_framework_status"]["existing_validations"] = len(validation_files)

            if validation_files:
                # Check latest validation
                latest_validation = max(validation_files, key=os.path.getctime)
                results["validation_framework_status"]["latest_validation"] = {
                    "file": latest_validation.name,
                    "timestamp": datetime.fromtimestamp(os.path.getctime(latest_validation)).isoformat(),
                }

        # Check hardcoded value detection
        try:
            fed_validator = FedRateValidator()
            hardcoded_check = fed_validator.check_directory("data/outputs/")
            results["hardcoded_detection"] = {
                "issues_found": len(hardcoded_check),
                "status": ("clean" if len(hardcoded_check) == 0 else "violations_detected"),
            }

            if len(hardcoded_check) > 0:
                results["recommendations"].append("Address hardcoded value violations")

        except Exception as e:
            results["hardcoded_detection"] = {"status": "error", "error": str(e)}

        # Overall framework status
        if results["validation_framework_status"]["status"] == "operational" and not installation_issues:
            results["overall_status"] = "ready"
        elif installation_issues:
            results["overall_status"] = "installation_required"
        else:
            results["overall_status"] = "degraded"

        results["timestamp"] = datetime.now().isoformat()

        return results

    def _apply_quality_gates(self, report) -> dict[str, dict[str, any]]:
        """Apply quality gates to validation report"""
        gate_results = {}

        for gate_name, gate_config in self.quality_gates.items():
            gate_result = {
                "passed": True,
                "score": 1.0,
                "threshold": gate_config["threshold"],
                "blocking": gate_config["blocking"],
                "description": gate_config["description"],
            }

            # Apply gate-specific logic
            if gate_name == "data_freshness":
                # Check for freshness issues in any phase
                freshness_issues = any(
                    "freshness" in violation.lower() or "stale" in violation.lower()
                    for violations in [result.violations for result in report.phase_results.values()]
                    for violation in violations
                )
                gate_result["passed"] = not freshness_issues
                gate_result["score"] = 0.0 if freshness_issues else 1.0

            elif gate_name == "variance_compliance":
                # Check for variance issues
                variance_issues = any(
                    "variance" in violation.lower()
                    for violations in [result.violations for result in report.phase_results.values()]
                    for violation in violations
                )
                gate_result["passed"] = not variance_issues
                gate_result["score"] = 0.0 if variance_issues else 1.0

            elif gate_name == "cross_validation":
                # Check cross-phase validation
                cross_phase_result = report.phase_results.get("cross_phase")
                if cross_phase_result:
                    gate_result["passed"] = cross_phase_result.passed
                    gate_result["score"] = cross_phase_result.score
                else:
                    gate_result["passed"] = False
                    gate_result["score"] = 0.0

            elif gate_name == "institutional_quality":
                gate_result["passed"] = report.overall_score >= gate_config["threshold"]
                gate_result["score"] = report.overall_score

            gate_results[gate_name] = gate_result

        return gate_results

    def generate_deployment_report(self, status: dict[str, any]) -> str:
        """Generate human-readable deployment report"""
        lines = [
            "=" * 80,
            "ENHANCED VALIDATION FRAMEWORK DEPLOYMENT REPORT",
            "=" * 80,
            f"Timestamp: {status.get('timestamp', 'N/A')}",
            "Framework Version: enhanced_v1.0",
            "",
        ]

        if "installation_check" in status:
            lines.extend(["INSTALLATION STATUS:", "-" * 40])

            for component, installed in status["installation_check"].items():
                status_text = "✓ INSTALLED" if installed else "✗ MISSING"
                lines.append(f"  {component}: {status_text}")

            lines.append("")

        if "validation_framework_status" in status:
            framework_status = status["validation_framework_status"]
            lines.extend(
                [
                    "VALIDATION FRAMEWORK STATUS:",
                    "-" * 40,
                    f"  Status: {framework_status.get('status', 'unknown').upper()}",
                ]
            )

            if "missing_components" in framework_status:
                lines.append(f"  Missing Components: {len(framework_status['missing_components'])}")

            if "existing_validations" in framework_status:
                lines.append(f"  Existing Validations: {framework_status['existing_validations']}")

            lines.append("")

        if "quality_gates_status" in status:
            lines.extend(["QUALITY GATES:", "-" * 40])

            for gate_name, gate_status in status["quality_gates_status"].items():
                blocking_text = "BLOCKING" if gate_status.get("blocking") else "NON-BLOCKING"
                lines.append(f"  {gate_name}: Threshold {gate_status.get('threshold')} ({blocking_text})")

            lines.append("")

        if "hardcoded_detection" in status:
            hardcoded = status["hardcoded_detection"]
            lines.extend(
                [
                    "HARDCODED VALUE DETECTION:",
                    "-" * 40,
                    f"  Status: {hardcoded.get('status', 'unknown').upper()}",
                ]
            )

            if "issues_found" in hardcoded:
                lines.append(f"  Issues Found: {hardcoded['issues_found']}")

            lines.append("")

        if "recommendations" in status and status["recommendations"]:
            lines.extend(["RECOMMENDATIONS:", "-" * 40])
            for rec in status["recommendations"]:
                lines.append(f"  • {rec}")
            lines.append("")

        # Overall status
        overall_status = status.get("overall_status", "unknown")
        status_emoji = {
            "ready": "✅",
            "degraded": "⚠️",
            "installation_required": "🔧",
            "unknown": "❓",
        }.get(overall_status, "❓")

        lines.extend(
            [
                "=" * 80,
                f"OVERALL FRAMEWORK STATUS: {status_emoji} {overall_status.upper()}",
                "=" * 80,
            ]
        )

        return "\n".join(lines)


def main():
    """Command-line interface for validation framework deployment"""
    parser = argparse.ArgumentParser(description="Enhanced Validation Framework Deployment")

    parser.add_argument(
        "--check-installation",
        action="store_true",
        help="Check if all validation components are installed",
    )

    parser.add_argument(
        "--validate-region",
        metavar="REGION_DATE",
        help="Validate specific region (format: REGION_YYYYMMDD)",
    )

    parser.add_argument(
        "--full-pipeline-check",
        action="store_true",
        help="Run comprehensive pipeline validation check",
    )

    parser.add_argument("--output", help="Output file for results")

    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if not any([args.check_installation, args.validate_region, args.full_pipeline_check]):
        parser.print_help()
        sys.exit(1)

    deployer = ValidationFrameworkDeployer()

    try:
        if args.check_installation:
            results = deployer.check_installation()

        elif args.validate_region:
            results = deployer.validate_region(args.validate_region)

        elif args.full_pipeline_check:
            results = deployer.run_full_pipeline_check()

        # Output results
        if args.json:
            output_text = json.dumps(results, indent=2)
        else:
            if args.check_installation:
                output_text = "Installation Check Results:\n" + "\n".join(
                    f"  {component}: {'✓' if status else '✗'}" for component, status in results.items()
                )
            else:
                output_text = deployer.generate_deployment_report(results)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output_text)
            print("Results written to {args.output}")
        else:
            print(output_text)

        # Exit code
        if args.validate_region:
            sys.exit(0 if results.get("validation_passed", False) else 1)
        elif args.full_pipeline_check:
            sys.exit(0 if results.get("overall_status") == "ready" else 1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
