#!/usr/bin/env python3
"""
DASV Consistency Validator

Comprehensive validator that ensures ongoing consistency across schemas, templates,
commands, and the unified execution system. Provides real-time validation,
drift detection, and automated consistency maintenance.
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

from scripts.utils.command_script_resolver import CommandScriptResolver
from scripts.utils.schema_consistency_optimizer import SchemaConsistencyOptimizer
from scripts.utils.template_consistency_optimizer import TemplateConsistencyOptimizer


@dataclass
class ValidationResult:
    """Result of a consistency validation check"""

    check_name: str
    status: str  # "pass", "warning", "fail"
    score: float  # 0.0 to 1.0
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemConsistencyReport:
    """Comprehensive system consistency report"""

    timestamp: datetime
    overall_score: float
    validation_results: dict[str, ValidationResult] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    action_items: list[str] = field(default_factory=list)
    drift_indicators: list[str] = field(default_factory=list)


class DASVConsistencyValidator:
    """
    Comprehensive consistency validator for the entire DASV system.

    Validates:
    - Schema consistency across domains and phases
    - Template consistency and standardization
    - Command-script-schema mapping integrity
    - Path reference consistency
    - Quality gate enforcement
    - Institutional standards compliance
    """

    def __init__(self):
        """Initialize the consistency validator"""
        self.project_root = project_root
        self.schema_optimizer = SchemaConsistencyOptimizer()
        self.template_optimizer = TemplateConsistencyOptimizer()
        self.command_resolver = CommandScriptResolver()

        # Consistency thresholds
        self.thresholds = {
            "schema_quality_minimum": 0.8,
            "template_quality_minimum": 0.7,
            "command_mapping_coverage": 0.95,
            "path_consistency_minimum": 0.98,
            "overall_system_minimum": 0.85,
        }

        # Load system configuration
        self._load_system_configuration()

    def _load_system_configuration(self):
        """Load system configuration and standards"""
        registry_path = self.project_root / "scripts" / "command_script_registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                self.registry_data = json.load(f)
        else:
            self.registry_data = {}

        # Expected system standards
        self.system_standards = {
            "dasv_phases": ["discover", "analyze", "synthesize", "validate"],
            "analysis_domains": [
                "fundamental_analysis",
                "sector_analysis",
                "industry_analysis",
                "comparative_analysis",
                "macro_analysis",
                "trade_history",
            ],
            "required_path_variables": [
                "SCRIPTS_BASE",
                "TEMPLATES_BASE",
                "DATA_OUTPUTS",
                "SCHEMAS_BASE",
            ],
            "quality_confidence_minimum": 0.9,
            "institutional_confidence_minimum": 0.95,
        }

    def validate_schema_consistency(self) -> ValidationResult:
        """Validate schema consistency across all domains"""
        print("🔍 Validating schema consistency...")

        # Run schema analysis
        schema_report = self.schema_optimizer.analyze_all_schemas()

        # Calculate score based on quality and coverage
        schema_score = schema_report.quality_score

        # Determine status
        if schema_score >= self.thresholds["schema_quality_minimum"]:
            status = "pass"
        elif schema_score >= 0.6:
            status = "warning"
        else:
            status = "fail"

        # Collect issues and recommendations
        issues = []
        recommendations = []

        # Check coverage
        expected_schemas = len(self.system_standards["analysis_domains"]) * len(self.system_standards["dasv_phases"])
        actual_schemas = schema_report.total_schemas
        coverage = actual_schemas / expected_schemas if expected_schemas > 0 else 0

        if coverage < 0.8:
            issues.append(f"Schema coverage low: {actual_schemas}/{expected_schemas} schemas")

        # Add schema-specific issues
        for domain_phase, schema_issues in schema_report.inconsistencies.items():
            if len(schema_issues) > 3:
                issues.append(f"High inconsistency count in {domain_phase}: {len(schema_issues)} issues")

        # Add recommendations
        recommendations.extend(schema_report.recommendations)

        return ValidationResult(
            check_name="Schema Consistency",
            status=status,
            score=schema_score,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "total_schemas": schema_report.total_schemas,
                "domains_covered": len(schema_report.domains_analyzed),
                "inconsistent_schemas": len(schema_report.inconsistencies),
                "coverage_percentage": coverage * 100,
            },
        )

    def validate_template_consistency(self) -> ValidationResult:
        """Validate template consistency across all domains"""
        print("🔍 Validating template consistency...")

        # Run template analysis
        template_report = self.template_optimizer.analyze_all_templates()

        # Calculate score
        template_score = template_report.quality_score

        # Determine status
        if template_score >= self.thresholds["template_quality_minimum"]:
            status = "pass"
        elif template_score >= 0.5:
            status = "warning"
        else:
            status = "fail"

        # Collect issues and recommendations
        issues = []
        recommendations = []

        # Check base template usage
        base_template_usage = sum(
            1
            for analysis in self.template_optimizer.template_analyses
            if any("base_" in inc for inc in analysis.includes_extends)
        )
        base_usage_rate = (
            base_template_usage / template_report.total_templates if template_report.total_templates > 0 else 0
        )

        if base_usage_rate < 0.6:
            issues.append(f"Low base template usage: {base_usage_rate:.1%}")

        # Check macro consistency
        templates_with_macros = sum(
            1 for analysis in self.template_optimizer.template_analyses if analysis.macro_imports
        )
        macro_usage_rate = (
            templates_with_macros / template_report.total_templates if template_report.total_templates > 0 else 0
        )

        if macro_usage_rate < 0.7:
            issues.append(f"Low macro usage: {macro_usage_rate:.1%}")

        # Add template-specific issues
        for template, template_issues in template_report.inconsistencies.items():
            if len(template_issues) > 2:
                issues.append(f"High inconsistency count in {template}: {len(template_issues)} issues")

        recommendations.extend(template_report.recommendations)

        return ValidationResult(
            check_name="Template Consistency",
            status=status,
            score=template_score,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "total_templates": template_report.total_templates,
                "domains_covered": len(template_report.domains_analyzed),
                "template_types": len(template_report.template_types),
                "base_template_usage": base_usage_rate * 100,
                "macro_usage": macro_usage_rate * 100,
            },
        )

    def validate_command_mapping_integrity(self) -> ValidationResult:
        """Validate command-script-schema mapping integrity"""
        print("🔍 Validating command mapping integrity...")

        issues = []
        recommendations = []

        # Check registry structure
        if not self.registry_data:
            return ValidationResult(
                check_name="Command Mapping Integrity",
                status="fail",
                score=0.0,
                issues=["Registry data not loaded"],
                recommendations=["Ensure command_script_registry.json exists and is valid"],
            )

        command_mappings = self.registry_data.get("command_mappings", {})

        # Check coverage across domains and phases
        total_expected = len(self.system_standards["analysis_domains"]) * len(self.system_standards["dasv_phases"])
        total_actual = 0

        for domain in self.system_standards["analysis_domains"]:
            if domain in command_mappings:
                domain_phases = command_mappings[domain]
                for phase in self.system_standards["dasv_phases"]:
                    if phase in domain_phases:
                        total_actual += 1

                        # Validate mapping structure
                        mapping = domain_phases[phase]
                        required_fields = [
                            "sub_agent",
                            "primary_script",
                            "schema",
                            "output_dir",
                            "file_pattern",
                        ]

                        for field in required_fields:
                            if field not in mapping:
                                issues.append(f"Missing {field} in {domain}:{phase} mapping")
                    else:
                        issues.append(f"Missing phase {phase} in {domain} mapping")
            else:
                issues.append(f"Missing domain {domain} in command mappings")

        coverage = total_actual / total_expected if total_expected > 0 else 0

        # Validate path references
        path_issues = self._validate_path_references(command_mappings)
        issues.extend(path_issues)

        # Calculate score
        mapping_score = coverage * (1.0 - len(issues) * 0.05)  # Penalize for issues
        mapping_score = max(0.0, min(1.0, mapping_score))

        # Determine status
        if mapping_score >= self.thresholds["command_mapping_coverage"]:
            status = "pass"
        elif mapping_score >= 0.8:
            status = "warning"
        else:
            status = "fail"

        if coverage < 1.0:
            recommendations.append(f"Improve command mapping coverage from {coverage:.1%} to 100%")

        if path_issues:
            recommendations.append("Standardize path references using {VARIABLE} syntax")

        return ValidationResult(
            check_name="Command Mapping Integrity",
            status=status,
            score=mapping_score,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "mapping_coverage": coverage * 100,
                "total_commands": total_actual,
                "expected_commands": total_expected,
                "path_consistency_issues": len(path_issues),
            },
        )

    def _validate_path_references(self, command_mappings: dict[str, Any]) -> list[str]:
        """Validate path references use consistent variable syntax"""
        path_issues = []
        expected_variables = set(self.system_standards["required_path_variables"])

        for domain, phases in command_mappings.items():
            for phase, mapping in phases.items():
                # Check script paths
                script_path = mapping.get("primary_script", "")
                if script_path and not any(f"{{{var}}}" in script_path for var in expected_variables):
                    if "scripts/" in script_path:
                        path_issues.append(f"Hardcoded script path in {domain}:{phase}")

                # Check schema paths
                schema_path = mapping.get("schema", "")
                if schema_path and not any(f"{{{var}}}" in schema_path for var in expected_variables):
                    if "schemas/" in schema_path:
                        path_issues.append(f"Hardcoded schema path in {domain}:{phase}")

                # Check template paths
                template_path = mapping.get("template", "")
                if template_path and not any(f"{{{var}}}" in template_path for var in expected_variables):
                    if "templates/" in template_path:
                        path_issues.append(f"Hardcoded template path in {domain}:{phase}")

        return path_issues

    def validate_quality_standards_compliance(self) -> ValidationResult:
        """Validate compliance with institutional quality standards"""
        print("🔍 Validating quality standards compliance...")

        issues = []
        recommendations = []

        # Check schema quality standards
        schema_report = self.schema_optimizer.analyze_all_schemas()

        # Check for confidence scoring in schemas
        schemas_with_confidence = 0
        for analysis in self.schema_optimizer.schema_analyses:
            if analysis.confidence_patterns:
                schemas_with_confidence += 1

        confidence_coverage = (
            schemas_with_confidence / len(self.schema_optimizer.schema_analyses)
            if self.schema_optimizer.schema_analyses
            else 0
        )

        if confidence_coverage < 0.9:
            issues.append(f"Low confidence scoring coverage in schemas: {confidence_coverage:.1%}")

        # Check template quality standards
        template_report = self.template_optimizer.analyze_all_templates()

        # Check for quality indicators in templates
        templates_with_quality = sum(
            1 for analysis in self.template_optimizer.template_analyses if analysis.quality_indicators
        )
        quality_coverage = (
            templates_with_quality / template_report.total_templates if template_report.total_templates > 0 else 0
        )

        if quality_coverage < 0.8:
            issues.append(f"Low quality indicator coverage in templates: {quality_coverage:.1%}")

        # Calculate overall quality score
        quality_score = (confidence_coverage + quality_coverage) / 2

        # Determine status
        if quality_score >= 0.9:
            status = "pass"
        elif quality_score >= 0.7:
            status = "warning"
        else:
            status = "fail"

        if confidence_coverage < 0.9:
            recommendations.append("Add confidence scoring to all schemas")

        if quality_coverage < 0.8:
            recommendations.append("Add quality indicators to all templates")

        return ValidationResult(
            check_name="Quality Standards Compliance",
            status=status,
            score=quality_score,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "confidence_coverage": confidence_coverage * 100,
                "quality_indicator_coverage": quality_coverage * 100,
                "institutional_threshold": 95.0,
            },
        )

    def validate_execution_system_integrity(self) -> ValidationResult:
        """Validate unified execution system integrity"""
        print("🔍 Validating execution system integrity...")

        issues = []
        recommendations = []

        # Check if execution system components exist
        components = [
            "scripts/utils/command_execution_service.py",
            "scripts/utils/dasv_workflow_orchestrator.py",
            "scripts/utils/unified_command_interface.py",
            "scripts/utils/command_script_resolver.py",
        ]

        missing_components = []
        for component in components:
            if not (self.project_root / component).exists():
                missing_components.append(component)

        if missing_components:
            issues.extend([f"Missing component: {comp}" for comp in missing_components])

        # Check registry integration
        try:
            commands = self.command_resolver.get_available_commands()
            if not commands:
                issues.append("Command resolver returns no available commands")
        except Exception as e:
            issues.append(f"Command resolver error: {e}")

        # Calculate score
        execution_score = 1.0 - (len(issues) * 0.2)
        execution_score = max(0.0, execution_score)

        # Determine status
        if execution_score >= 0.9:
            status = "pass"
        elif execution_score >= 0.7:
            status = "warning"
        else:
            status = "fail"

        if missing_components:
            recommendations.append("Restore missing execution system components")

        if not commands:
            recommendations.append("Verify command registry integration")

        return ValidationResult(
            check_name="Execution System Integrity",
            status=status,
            score=execution_score,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "components_present": len(components) - len(missing_components),
                "total_components": len(components),
                "available_commands": len(commands) if "commands" in locals() else 0,
            },
        )

    def run_comprehensive_validation(self) -> SystemConsistencyReport:
        """Run comprehensive system consistency validation"""
        print("🚀 Running comprehensive DASV system consistency validation...")
        print("=" * 70)

        validation_results = {}

        # Run all validation checks
        validation_checks = [
            self.validate_schema_consistency,
            self.validate_template_consistency,
            self.validate_command_mapping_integrity,
            self.validate_quality_standards_compliance,
            self.validate_execution_system_integrity,
        ]

        for check in validation_checks:
            try:
                result = check()
                validation_results[result.check_name] = result

                # Print immediate feedback
                status_emoji = "✅" if result.status == "pass" else "⚠️" if result.status == "warning" else "❌"
                print(f"{status_emoji} {result.check_name}: {result.status} ({result.score:.2f})")

                if result.issues:
                    for issue in result.issues[:2]:  # Show first 2 issues
                        print("    • {issue}")
                    if len(result.issues) > 2:
                        print("    • ... and {len(result.issues) - 2} more")

            except Exception as e:
                error_result = ValidationResult(
                    check_name=check.__name__.replace("validate_", "").replace("_", " ").title(),
                    status="fail",
                    score=0.0,
                    issues=[f"Validation check failed: {e}"],
                    recommendations=["Fix validation check implementation"],
                )
                validation_results[error_result.check_name] = error_result
                print("❌ {error_result.check_name}: failed ({e})")

        # Calculate overall score
        scores = [result.score for result in validation_results.values()]
        overall_score = sum(scores) / len(scores) if scores else 0.0

        # Generate summary
        summary = {
            "total_checks": len(validation_results),
            "passed_checks": sum(1 for r in validation_results.values() if r.status == "pass"),
            "warning_checks": sum(1 for r in validation_results.values() if r.status == "warning"),
            "failed_checks": sum(1 for r in validation_results.values() if r.status == "fail"),
            "overall_score": overall_score,
            "system_health": (
                "excellent"
                if overall_score >= 0.9
                else ("good" if overall_score >= 0.8 else "needs_attention" if overall_score >= 0.7 else "critical")
            ),
        }

        # Generate action items
        action_items = []
        for result in validation_results.values():
            if result.status in ["fail", "warning"]:
                action_items.extend(result.recommendations[:2])  # Top 2 recommendations per check

        # Detect drift indicators
        drift_indicators = []
        if overall_score < self.thresholds["overall_system_minimum"]:
            drift_indicators.append(
                f"Overall system score {overall_score:.2f} below minimum {self.thresholds['overall_system_minimum']}"
            )

        for result in validation_results.values():
            if result.status == "fail":
                drift_indicators.append(f"{result.check_name} failing - immediate attention required")

        return SystemConsistencyReport(
            timestamp=datetime.now(),
            overall_score=overall_score,
            validation_results=validation_results,
            summary=summary,
            action_items=action_items,
            drift_indicators=drift_indicators,
        )

    def print_comprehensive_report(self, report: SystemConsistencyReport):
        """Print detailed comprehensive validation report"""
        print("\n" + "=" * 70)
        print("DASV SYSTEM CONSISTENCY VALIDATION REPORT")
        print("=" * 70)
        print("📅 Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Overall Score: {report.overall_score:.2f}/1.0 ({report.summary['system_health'].upper()})")

        # Summary
        print("\n📊 Summary:")
        print("  Total Checks: {report.summary['total_checks']}")
        print("  ✅ Passed: {report.summary['passed_checks']}")
        print("  ⚠️  Warnings: {report.summary['warning_checks']}")
        print("  ❌ Failed: {report.summary['failed_checks']}")

        # Detailed results
        print("\n🔍 Detailed Results:")
        for check_name, result in report.validation_results.items():
            status_emoji = "✅" if result.status == "pass" else "⚠️" if result.status == "warning" else "❌"
            print(f"  {status_emoji} {check_name}: {result.score:.2f} ({result.status})")

            if result.metadata:
                key_metrics = list(result.metadata.items())[:2]  # Show top 2 metrics
                for key, value in key_metrics:
                    print("    📈 {key}: {value}")

        # Action items
        if report.action_items:
            print("\n🔧 Priority Action Items:")
            for i, item in enumerate(report.action_items[:5], 1):  # Top 5 actions
                print("  {i}. {item}")

        # Drift indicators
        if report.drift_indicators:
            print("\n⚠️  System Drift Indicators:")
            for indicator in report.drift_indicators:
                print("  • {indicator}")

        # Recommendations
        print("\n💡 Next Steps:")
        if report.overall_score >= 0.9:
            print("  🎉 System is performing excellently - maintain current standards")
        elif report.overall_score >= 0.8:
            print("  ✨ System is in good shape - address warnings to achieve excellence")
        elif report.overall_score >= 0.7:
            print("  🔧 System needs attention - prioritize failed checks and high-impact improvements")
        else:
            print("  🚨 System requires immediate attention - focus on critical failures")

    def export_validation_report(self, report: SystemConsistencyReport, output_path: str = None):
        """Export validation report to JSON file"""
        if output_path is None:
            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f"data/outputs/system_consistency_report_{timestamp}.json"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert report to JSON-serializable format
        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "overall_score": report.overall_score,
            "summary": report.summary,
            "validation_results": {},
            "action_items": report.action_items,
            "drift_indicators": report.drift_indicators,
        }

        for check_name, result in report.validation_results.items():
            report_data["validation_results"][check_name] = {
                "status": result.status,
                "score": result.score,
                "issues": result.issues,
                "recommendations": result.recommendations,
                "metadata": result.metadata,
            }

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print("\n📄 Validation report exported to: {output_file}")
        return str(output_file)


def main():
    """CLI interface for DASV consistency validation"""
    import argparse

    parser = argparse.ArgumentParser(description="DASV System Consistency Validator")
    parser.add_argument(
        "--check",
        choices=["schemas", "templates", "commands", "quality", "execution", "all"],
        default="all",
        help="Specific check to run",
    )
    parser.add_argument("--export", action="store_true", help="Export validation report to JSON")
    parser.add_argument("--output", help="Output file path for report")
    parser.add_argument("--quiet", action="store_true", help="Minimize output (scores only)")

    args = parser.parse_args()

    # Initialize validator
    validator = DASVConsistencyValidator()

    if args.check == "all":
        # Run comprehensive validation
        report = validator.run_comprehensive_validation()

        if not args.quiet:
            validator.print_comprehensive_report(report)
        else:
            print("Overall Score: {report.overall_score:.2f}/1.0")

        if args.export:
            validator.export_validation_report(report, args.output)

    else:
        # Run specific check
        check_methods = {
            "schemas": validator.validate_schema_consistency,
            "templates": validator.validate_template_consistency,
            "commands": validator.validate_command_mapping_integrity,
            "quality": validator.validate_quality_standards_compliance,
            "execution": validator.validate_execution_system_integrity,
        }

        result = check_methods[args.check]()

        if not args.quiet:
            print("{result.check_name}: {result.status} ({result.score:.2f})")
            if result.issues:
                print("Issues:")
                for issue in result.issues:
                    print("  • {issue}")
            if result.recommendations:
                print("Recommendations:")
                for rec in result.recommendations:
                    print("  • {rec}")
        else:
            print("{result.score:.2f}")


if __name__ == "__main__":
    main()
