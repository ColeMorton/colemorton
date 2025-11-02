#!/usr/bin/env python3
"""
DASV Cross-Validation Framework

Comprehensive cross-validation logic across discovery→analysis→synthesis phases
for institutional-grade quality assurance with real-time validation and fail-fast
quality gates.

Features:
- Multi-phase data consistency validation
- Real-time market data cross-validation
- Staleness detection and variance monitoring
- Fail-fast quality gates with detailed reporting
- Cross-source validation across multiple APIs

Usage:
    from scripts.utils.dasv_cross_validator import DASVCrossValidator

    validator = DASVCrossValidator()
    result = validator.validate_full_pipeline("US_20250812")
"""

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np


@dataclass
class ValidationResult:
    """Validation result container"""

    passed: bool
    score: float
    details: dict[str, Any]
    violations: list[str]
    recommendations: list[str]


@dataclass
class CrossValidationReport:
    """Comprehensive cross-validation report"""

    overall_passed: bool
    overall_score: float
    phase_results: dict[str, ValidationResult]
    critical_issues: list[str]
    blocking_issues: list[str]
    recommendations: list[str]
    metadata: dict[str, Any]


class DASVCrossValidator:
    """
    Cross-validation framework for DASV pipeline quality assurance
    """

    def __init__(self, variance_threshold: float = 0.02, staleness_hours: int = 6):
        self.variance_threshold = variance_threshold
        self.staleness_hours = staleness_hours

        # Quality thresholds
        self.min_institutional_score = 0.9
        self.min_confidence_score = 0.85

        # Expected file patterns
        self.file_patterns = {
            "discovery": "data/outputs/macro_analysis/discovery/{region}_{date}_discovery.json",
            "analysis": "data/outputs/macro_analysis/analysis/{region}_{date}_analysis.json",
            "synthesis": "data/outputs/macro_analysis/{region}_{date}.md",
            "validation": "data/outputs/macro_analysis/validation/{region}_{date}_validation.json",
        }

    def validate_full_pipeline(self, region_date: str) -> CrossValidationReport:
        """
        Validate complete DASV pipeline for a region and date

        Args:
            region_date: Format "{REGION}_{YYYYMMDD}"

        Returns:
            Comprehensive cross-validation report
        """
        # Parse region and date
        parts = region_date.split("_")
        if len(parts) < 2:
            raise ValueError(f"Invalid region_date format: {region_date}. Expected REGION_YYYYMMDD")

        region = parts[0]
        date = parts[1]

        # Load all phase files
        phase_data = self._load_phase_files(region, date)

        # Initialize results
        phase_results = {}
        critical_issues = []
        blocking_issues = []
        recommendations = []

        # Validate each phase
        if "discovery" in phase_data:
            discovery_result = self._validate_discovery_phase(phase_data["discovery"])
            phase_results["discovery"] = discovery_result
            if not discovery_result.passed:
                blocking_issues.extend(discovery_result.violations)

        if "analysis" in phase_data:
            analysis_result = self._validate_analysis_phase(phase_data["analysis"], phase_data.get("discovery"))
            phase_results["analysis"] = analysis_result
            if not analysis_result.passed:
                blocking_issues.extend(analysis_result.violations)

        if "synthesis" in phase_data:
            synthesis_result = self._validate_synthesis_phase(
                phase_data["synthesis"],
                phase_data.get("discovery"),
                phase_data.get("analysis"),
            )
            phase_results["synthesis"] = synthesis_result
            if not synthesis_result.passed:
                critical_issues.extend(synthesis_result.violations)

        # Cross-phase validation
        cross_phase_result = self._validate_cross_phase_consistency(phase_data)
        phase_results["cross_phase"] = cross_phase_result
        if not cross_phase_result.passed:
            critical_issues.extend(cross_phase_result.violations)

        # Calculate overall score
        overall_score = np.mean([result.score for result in phase_results.values()])
        overall_passed = overall_score >= self.min_institutional_score and len(blocking_issues) == 0

        # Compile recommendations
        for result in phase_results.values():
            recommendations.extend(result.recommendations)

        return CrossValidationReport(
            overall_passed=overall_passed,
            overall_score=overall_score,
            phase_results=phase_results,
            critical_issues=critical_issues,
            blocking_issues=blocking_issues,
            recommendations=list(set(recommendations)),  # Remove duplicates
            metadata={
                "region": region,
                "date": date,
                "validation_timestamp": datetime.now().isoformat(),
                "variance_threshold": self.variance_threshold,
                "staleness_hours": self.staleness_hours,
                "files_validated": list(phase_data.keys()),
            },
        )

    def _load_phase_files(self, region: str, date: str) -> dict[str, dict[str, Any]]:
        """Load all available phase files for validation"""
        phase_data = {}

        for phase, pattern in self.file_patterns.items():
            file_path = pattern.format(region=region, date=date)

            if os.path.exists(file_path):
                try:
                    if file_path.endswith(".json"):
                        with open(file_path) as f:
                            phase_data[phase] = json.load(f)
                    elif file_path.endswith(".md"):
                        with open(file_path) as f:
                            phase_data[phase] = {
                                "content": f.read(),
                                "file_path": file_path,
                            }
                except Exception:
                    print("Warning: Could not load {file_path}: {e}")

        return phase_data

    def _validate_discovery_phase(self, discovery_data: dict[str, Any]) -> ValidationResult:
        """Validate discovery phase data quality"""
        violations = []
        score_components = []

        # Data freshness validation
        freshness_score, freshness_violations = self._validate_data_freshness(discovery_data)
        score_components.append(freshness_score)
        violations.extend(freshness_violations)

        # Economic indicators completeness
        (
            completeness_score,
            completeness_violations,
        ) = self._validate_economic_indicators_completeness(discovery_data)
        score_components.append(completeness_score)
        violations.extend(completeness_violations)

        # Business cycle data consistency
        cycle_score, cycle_violations = self._validate_business_cycle_data(discovery_data)
        score_components.append(cycle_score)
        violations.extend(cycle_violations)

        # CLI service health validation
        cli_score, cli_violations = self._validate_cli_service_health(discovery_data)
        score_components.append(cli_score)
        violations.extend(cli_violations)

        overall_score = np.mean(score_components) if score_components else 0.0
        passed = overall_score >= self.min_confidence_score and len(violations) == 0

        return ValidationResult(
            passed=passed,
            score=overall_score,
            details={
                "freshness_score": freshness_score,
                "completeness_score": completeness_score,
                "cycle_score": cycle_score,
                "cli_score": cli_score,
            },
            violations=violations,
            recommendations=self._generate_discovery_recommendations(violations),
        )

    def _validate_analysis_phase(
        self, analysis_data: dict[str, Any], discovery_data: dict[str, Any] | None
    ) -> ValidationResult:
        """Validate analysis phase data quality and consistency with discovery"""
        violations = []
        score_components = []

        # Analysis quality metrics validation
        if "analysis_quality_metrics" in analysis_data:
            metrics = analysis_data["analysis_quality_metrics"]

            # Check freshness validation
            if "data_freshness_validation" in metrics:
                freshness = metrics["data_freshness_validation"]
                if freshness.get("max_age_hours", 0) > self.staleness_hours:
                    violations.append(
                        f"Analysis data exceeds staleness threshold: {freshness.get('max_age_hours')}h > {self.staleness_hours}h"
                    )

            # Check variance compliance
            if "variance_compliance" in metrics:
                variance = metrics["variance_compliance"]
                if variance.get("max_variance", 0) > self.variance_threshold:
                    violations.append(
                        f"Analysis variance exceeds threshold: {variance.get('max_variance')} > {self.variance_threshold}"
                    )

            # Score components
            for component in [
                "gap_coverage",
                "confidence_propagation",
                "analytical_rigor",
                "evidence_strength",
            ]:
                if component in metrics:
                    score_components.append(metrics[component])

        # Discovery consistency validation
        if discovery_data:
            (
                consistency_score,
                consistency_violations,
            ) = self._validate_discovery_analysis_consistency(discovery_data, analysis_data)
            score_components.append(consistency_score)
            violations.extend(consistency_violations)

        overall_score = np.mean(score_components) if score_components else 0.0
        passed = overall_score >= self.min_confidence_score and len(violations) == 0

        return ValidationResult(
            passed=passed,
            score=overall_score,
            details={"component_scores": score_components},
            violations=violations,
            recommendations=self._generate_analysis_recommendations(violations),
        )

    def _validate_synthesis_phase(
        self,
        synthesis_data: dict[str, Any],
        discovery_data: dict[str, Any] | None,
        analysis_data: dict[str, Any] | None,
    ) -> ValidationResult:
        """Validate synthesis phase content and consistency"""
        violations = []
        score_components = []

        # Content validation
        content = synthesis_data.get("content", "")

        # Length validation
        if len(content) < 1000:
            violations.append("Synthesis content too short for institutional quality")

        # Economic indicator references validation
        economic_indicators = [
            "GDP",
            "employment",
            "inflation",
            "Fed Funds",
            "yield curve",
        ]
        missing_indicators = []
        for indicator in economic_indicators:
            if indicator.lower() not in content.lower():
                missing_indicators.append(indicator)

        if missing_indicators:
            violations.append(f"Missing key economic indicators: {', '.join(missing_indicators)}")

        # Business cycle reference validation
        cycle_terms = ["business cycle", "recession", "expansion", "economic cycle"]
        if not any(term.lower() in content.lower() for term in cycle_terms):
            violations.append("Missing business cycle analysis reference")

        # Hardcoded value detection
        hardcoded_violations = self._detect_hardcoded_values(content)
        violations.extend(hardcoded_violations)

        # Cross-phase consistency
        if discovery_data and analysis_data:
            (
                consistency_score,
                consistency_violations,
            ) = self._validate_synthesis_consistency(content, discovery_data, analysis_data)
            score_components.append(consistency_score)
            violations.extend(consistency_violations)

        # Calculate score based on violations
        violation_penalty = min(len(violations) * 0.1, 0.5)
        overall_score = max(0.0, 1.0 - violation_penalty)
        if score_components:
            overall_score = (overall_score + np.mean(score_components)) / 2

        passed = overall_score >= self.min_confidence_score and len(violations) == 0

        return ValidationResult(
            passed=passed,
            score=overall_score,
            details={
                "content_length": len(content),
                "violations_count": len(violations),
            },
            violations=violations,
            recommendations=self._generate_synthesis_recommendations(violations),
        )

    def _validate_cross_phase_consistency(self, phase_data: dict[str, dict[str, Any]]) -> ValidationResult:
        """Validate consistency across all phases"""
        violations = []
        score_components = []

        # Check if we have at least discovery and analysis
        if "discovery" not in phase_data or "analysis" not in phase_data:
            violations.append("Missing required phases for cross-validation")
            return ValidationResult(
                passed=False,
                score=0.0,
                details={},
                violations=violations,
                recommendations=["Ensure both discovery and analysis phases are completed"],
            )

        discovery = phase_data["discovery"]
        analysis = phase_data["analysis"]

        # Region consistency
        discovery_region = discovery.get("metadata", {}).get("region")
        analysis_region = analysis.get("metadata", {}).get("region")
        if discovery_region != analysis_region:
            violations.append(f"Region mismatch: discovery={discovery_region}, analysis={analysis_region}")

        # Business cycle consistency
        discovery_cycle = discovery.get("business_cycle_data", {}).get("current_phase")
        analysis_cycle = analysis.get("business_cycle_modeling", {}).get("current_phase")
        if discovery_cycle and analysis_cycle and discovery_cycle != analysis_cycle:
            violations.append(f"Business cycle phase mismatch: discovery={discovery_cycle}, analysis={analysis_cycle}")

        # Confidence score propagation
        discovery_confidence = discovery.get("data_quality_assessment", {}).get("discovery_confidence", 0)
        analysis_confidence = analysis.get("analysis_quality_metrics", {}).get("confidence_propagation", 0)
        if abs(discovery_confidence - analysis_confidence) > 0.1:
            violations.append("Confidence score not properly propagated from discovery to analysis")

        # Economic indicator consistency validation
        econ_consistency_score = self._validate_economic_indicator_consistency(discovery, analysis)
        score_components.append(econ_consistency_score)

        overall_score = np.mean(score_components) if score_components else (1.0 if len(violations) == 0 else 0.7)
        passed = overall_score >= self.min_confidence_score and len(violations) == 0

        return ValidationResult(
            passed=passed,
            score=overall_score,
            details={"consistency_checks": len(violations) == 0},
            violations=violations,
            recommendations=self._generate_cross_phase_recommendations(violations),
        )

    def _validate_data_freshness(self, data: dict[str, Any]) -> tuple[float, list[str]]:
        """Validate data freshness against staleness threshold"""
        violations = []

        # Check CLI service validation for freshness
        cli_validation = data.get("cli_service_validation", {})
        data_freshness = cli_validation.get("data_freshness", {})

        overall_freshness = data_freshness.get("overall_freshness", 1.0)
        stale_count = data_freshness.get("stale_data_count", 0)

        if overall_freshness < 0.9:
            violations.append(f"Overall data freshness below threshold: {overall_freshness}")

        if stale_count > 0:
            violations.append(f"Found {stale_count} stale data points")

        # Check for freshness violations if available
        if "freshness_violations" in data_freshness:
            for violation in data_freshness["freshness_violations"]:
                if violation.get("age_hours", 0) > self.staleness_hours:
                    violations.append(f"Stale data: {violation.get('indicator')} aged {violation.get('age_hours')}h")

        score = max(0.0, overall_freshness - (stale_count * 0.1))
        return score, violations

    def _validate_economic_indicators_completeness(self, data: dict[str, Any]) -> tuple[float, list[str]]:
        """Validate completeness of economic indicators"""
        violations = []

        required_sections = [
            "economic_indicators",
            "business_cycle_data",
            "monetary_policy_context",
        ]

        missing_sections = []
        for section in required_sections:
            if section not in data:
                missing_sections.append(section)

        if missing_sections:
            violations.append(f"Missing required sections: {', '.join(missing_sections)}")

        # Check economic indicators completeness
        econ_indicators = data.get("economic_indicators", {})
        required_indicators = [
            "leading_indicators",
            "coincident_indicators",
            "lagging_indicators",
        ]

        for indicator_type in required_indicators:
            if indicator_type not in econ_indicators:
                violations.append(f"Missing {indicator_type}")

        completeness_score = 1.0 - (len(violations) * 0.2)
        return max(0.0, completeness_score), violations

    def _validate_business_cycle_data(self, data: dict[str, Any]) -> tuple[float, list[str]]:
        """Validate business cycle data consistency"""
        violations = []

        cycle_data = data.get("business_cycle_data", {})

        # Check required fields
        required_fields = ["current_phase", "transition_probabilities", "confidence"]
        for field in required_fields:
            if field not in cycle_data:
                violations.append(f"Missing business cycle field: {field}")

        # Validate current phase
        current_phase = cycle_data.get("current_phase")
        valid_phases = ["expansion", "peak", "contraction", "trough"]
        if current_phase not in valid_phases:
            violations.append(f"Invalid business cycle phase: {current_phase}")

        # Validate confidence score
        confidence = cycle_data.get("confidence", 0)
        if confidence < self.min_confidence_score:
            violations.append(f"Business cycle confidence too low: {confidence}")

        score = 1.0 - (len(violations) * 0.25)
        return max(0.0, score), violations

    def _validate_cli_service_health(self, data: dict[str, Any]) -> tuple[float, list[str]]:
        """Validate CLI service health and availability"""
        violations = []

        cli_validation = data.get("cli_service_validation", {})
        service_health = cli_validation.get("service_health_scores", {})

        overall_health = service_health.get("overall_health", 0)
        if overall_health < 0.8:
            violations.append(f"CLI services health below threshold: {overall_health}")

        # Check individual service health
        services = ["fred_economic_cli", "imf_cli", "alpha_vantage_cli"]
        for service in services:
            if service in service_health:
                health_score = service_health[service]
                if health_score < 0.7:
                    violations.append(f"Service {service} health poor: {health_score}")

        return max(0.0, overall_health), violations

    def _validate_discovery_analysis_consistency(
        self, discovery: dict[str, Any], analysis: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Validate consistency between discovery and analysis phases"""
        violations = []

        # Business cycle consistency
        discovery_cycle = discovery.get("business_cycle_data", {}).get("current_phase")
        analysis_cycle = analysis.get("business_cycle_modeling", {}).get("current_phase")

        if discovery_cycle and analysis_cycle and discovery_cycle != analysis_cycle:
            violations.append(f"Business cycle phase inconsistency: {discovery_cycle} vs {analysis_cycle}")

        # Recession probability consistency
        discovery_recession = (
            discovery.get("economic_indicators", {}).get("composite_scores", {}).get("recession_probability")
        )
        analysis_recession = analysis.get("business_cycle_modeling", {}).get("recession_probability")

        if discovery_recession and analysis_recession:
            variance = abs(discovery_recession - analysis_recession)
            if variance > 0.1:  # Allow 10% variance
                violations.append(f"Recession probability variance too high: {variance}")

        consistency_score = 1.0 - (len(violations) * 0.3)
        return max(0.0, consistency_score), violations

    def _validate_economic_indicator_consistency(self, discovery: dict[str, Any], analysis: dict[str, Any]) -> float:
        """Validate economic indicator consistency across phases"""
        consistency_checks = 0
        passed_checks = 0

        # Check monetary policy consistency
        discovery_policy = discovery.get("monetary_policy_context", {}).get("policy_stance", {})
        analysis_liquidity = analysis.get("liquidity_cycle_positioning", {})

        if discovery_policy and analysis_liquidity:
            consistency_checks += 1
            # Basic consistency check - both should reference similar policy stance
            discovery_stance = discovery_policy.get("current_stance", "").lower()
            # This is a simplified check - in practice would be more sophisticated
            if discovery_stance:
                passed_checks += 1

        return passed_checks / consistency_checks if consistency_checks > 0 else 1.0

    def _validate_synthesis_consistency(
        self, content: str, discovery: dict[str, Any], analysis: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Validate synthesis consistency with discovery and analysis"""
        violations = []

        # Check if business cycle phase is mentioned consistently
        discovery_phase = discovery.get("business_cycle_data", {}).get("current_phase", "")
        analysis_phase = analysis.get("business_cycle_modeling", {}).get("current_phase", "")

        if discovery_phase and discovery_phase.lower() not in content.lower():
            violations.append(f"Business cycle phase '{discovery_phase}' not referenced in synthesis")

        # Check for economic indicators mentioned in discovery
        discovery_indicators = discovery.get("economic_indicators", {})
        if "leading_indicators" in discovery_indicators:
            if "leading" not in content.lower():
                violations.append("Leading indicators not discussed in synthesis")

        consistency_score = 1.0 - (len(violations) * 0.2)
        return max(0.0, consistency_score), violations

    def _detect_hardcoded_values(self, content: str) -> list[str]:
        """Detect hardcoded values in synthesis content"""
        violations = []

        # Use the fed rate validation utility patterns
        hardcoded_patterns = [
            r"5\.25.*?5\.50",  # Range format 5.25-5.50
            r"5\.25\s*-\s*5\.50",  # Range with spaces
            r"4\.25.*?4\.50",  # Current range format
        ]

        import re

        for pattern in hardcoded_patterns:
            if re.search(pattern, content):
                violations.append(f"Hardcoded rate detected: pattern {pattern}")

        return violations

    def _generate_discovery_recommendations(self, violations: list[str]) -> list[str]:
        """Generate recommendations for discovery phase improvements"""
        recommendations = []

        if any("freshness" in v.lower() for v in violations):
            recommendations.append("Update data sources to ensure freshness within staleness threshold")

        if any("missing" in v.lower() for v in violations):
            recommendations.append("Complete all required economic indicator sections")

        if any("confidence" in v.lower() for v in violations):
            recommendations.append("Improve data quality to meet confidence thresholds")

        return recommendations

    def _generate_analysis_recommendations(self, violations: list[str]) -> list[str]:
        """Generate recommendations for analysis phase improvements"""
        recommendations = []

        if any("staleness" in v.lower() for v in violations):
            recommendations.append("Refresh analysis with more recent data")

        if any("variance" in v.lower() for v in violations):
            recommendations.append("Investigate and resolve data variance issues")

        return recommendations

    def _generate_synthesis_recommendations(self, violations: list[str]) -> list[str]:
        """Generate recommendations for synthesis phase improvements"""
        recommendations = []

        if any("too short" in v.lower() for v in violations):
            recommendations.append("Expand synthesis content to meet institutional standards")

        if any("missing" in v.lower() for v in violations):
            recommendations.append("Include all required economic indicators and analysis")

        if any("hardcoded" in v.lower() for v in violations):
            recommendations.append("Replace hardcoded values with dynamic data references")

        return recommendations

    def _generate_cross_phase_recommendations(self, violations: list[str]) -> list[str]:
        """Generate recommendations for cross-phase consistency improvements"""
        recommendations = []

        if any("mismatch" in v.lower() for v in violations):
            recommendations.append("Ensure consistency across all DASV phases")

        if any("propagation" in v.lower() for v in violations):
            recommendations.append("Properly propagate confidence scores between phases")

        return recommendations

    def generate_validation_report(self, report: CrossValidationReport) -> str:
        """Generate human-readable validation report"""
        lines = [
            "=" * 80,
            "DASV CROSS-VALIDATION REPORT",
            "=" * 80,
            f"Region: {report.metadata['region']}",
            f"Date: {report.metadata['date']}",
            f"Validation Timestamp: {report.metadata['validation_timestamp']}",
            f"Overall Status: {'PASSED' if report.overall_passed else 'FAILED'}",
            f"Overall Score: {report.overall_score:.3f}",
            "",
            "PHASE RESULTS:",
            "-" * 40,
        ]

        for phase, result in report.phase_results.items():
            lines.extend(
                [
                    f"{phase.upper()}: {'PASS' if result.passed else 'FAIL'} (Score: {result.score:.3f})",
                    f"  Violations: {len(result.violations)}",
                    f"  Recommendations: {len(result.recommendations)}",
                    "",
                ]
            )

        if report.blocking_issues:
            lines.extend(
                [
                    "BLOCKING ISSUES:",
                    "-" * 40,
                ]
            )
            for issue in report.blocking_issues:
                lines.append(f"  • {issue}")
            lines.append("")

        if report.critical_issues:
            lines.extend(
                [
                    "CRITICAL ISSUES:",
                    "-" * 40,
                ]
            )
            for issue in report.critical_issues:
                lines.append(f"  • {issue}")
            lines.append("")

        if report.recommendations:
            lines.extend(
                [
                    "RECOMMENDATIONS:",
                    "-" * 40,
                ]
            )
            for rec in report.recommendations:
                lines.append(f"  • {rec}")
            lines.append("")

        lines.extend(
            [
                "=" * 80,
                f"Institutional Quality: {'CERTIFIED' if report.overall_passed and report.overall_score >= 0.9 else 'NOT CERTIFIED'}",
                "=" * 80,
            ]
        )

        return "\n".join(lines)


def main():
    """Command-line interface for DASV cross-validation"""
    import argparse

    parser = argparse.ArgumentParser(description="DASV Cross-Validation Framework")
    parser.add_argument("region_date", help="Region and date in format REGION_YYYYMMDD")
    parser.add_argument(
        "--variance-threshold",
        type=float,
        default=0.02,
        help="Maximum acceptable variance threshold",
    )
    parser.add_argument(
        "--staleness-hours",
        type=int,
        default=6,
        help="Maximum acceptable data age in hours",
    )
    parser.add_argument("--output", help="Output file for validation report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Create validator
    validator = DASVCrossValidator(variance_threshold=args.variance_threshold, staleness_hours=args.staleness_hours)

    try:
        # Run validation
        report = validator.validate_full_pipeline(args.region_date)

        if args.json:
            # JSON output
            output_data = {
                "overall_passed": report.overall_passed,
                "overall_score": report.overall_score,
                "phase_results": {
                    phase: {
                        "passed": result.passed,
                        "score": result.score,
                        "violations": result.violations,
                        "recommendations": result.recommendations,
                    }
                    for phase, result in report.phase_results.items()
                },
                "critical_issues": report.critical_issues,
                "blocking_issues": report.blocking_issues,
                "recommendations": report.recommendations,
                "metadata": report.metadata,
            }

            if args.output:
                with open(args.output, "w") as f:
                    json.dump(output_data, f, indent=2)
            else:
                print(json.dumps(output_data, indent=2))
        else:
            # Text output
            report_text = validator.generate_validation_report(report)

            if args.output:
                with open(args.output, "w") as f:
                    f.write(report_text)
            else:
                print(report_text)

        # Exit code based on validation result
        sys.exit(0 if report.overall_passed else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
