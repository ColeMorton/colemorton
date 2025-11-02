#!/usr/bin/env python3
"""
DASV Phase Cross-Analysis Validation for Analysis Files
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class AnalysisCrossValidator:
    def __init__(self, analysis_dir: str):
        self.analysis_dir = Path(analysis_dir)
        self.files_analyzed = []
        self.structural_issues = []
        self.hardcoded_values = defaultdict(list)
        self.ticker_specificity_issues = []
        self.cli_consistency_issues = []

    def get_latest_files(self, count: int = 7) -> list[Path]:
        """Get the latest N analysis files by modification time"""
        analysis_files = list(self.analysis_dir.glob("*_analysis.json"))
        # Sort by modification time, newest first
        analysis_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return analysis_files[:count]

    def load_json_file(self, filepath: Path) -> dict[str, Any]:
        """Load and parse JSON file"""
        try:
            with open(filepath) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}

    def extract_ticker_from_filename(self, filepath: Path) -> str:
        """Extract ticker symbol from filename"""
        # Pattern: TICKER_YYYYMMDD_analysis.json
        match = re.match(r"([A-Z]+)_\d{8}_analysis\.json", filepath.name)
        return match.group(1) if match else "UNKNOWN"

    def analyze_structural_consistency(self, files_data: list[dict[str, Any]]) -> float:
        """Analyze structural consistency across files"""
        # Define expected structure
        expected_keys = {
            "metadata",
            "discovery_data_inheritance",
            "market_data",
            "company_overview",
            "economic_context",
            "cli_service_validation",
            "peer_group_analysis",
            "financial_health_analysis",
            "competitive_position_assessment",
            "growth_analysis",
            "risk_assessment",
            "valuation_model_inputs",
            "analytical_insights",
            "quality_metrics",
        }

        # Check each file for structural compliance
        structural_scores = []
        for idx, data in enumerate(files_data):
            file_keys = set(data.keys())
            missing_keys = expected_keys - file_keys
            extra_keys = file_keys - expected_keys

            score = len(expected_keys & file_keys) / len(expected_keys)
            structural_scores.append(score)

            if missing_keys or extra_keys:
                self.structural_issues.append(
                    {
                        "file_index": idx,
                        "filename": self.files_analyzed[idx]["filename"],
                        "missing_keys": list(missing_keys),
                        "extra_keys": list(extra_keys),
                        "compliance_score": score,
                    }
                )

        return sum(structural_scores) / len(structural_scores) if structural_scores else 0.0

    def detect_hardcoded_values(self, files_data: list[dict[str, Any]]) -> float:
        """Detect potential hardcoded or template values"""
        # Common patterns that might indicate hardcoded values
        suspicious_patterns = [
            (r"\b(example|test|demo|placeholder|todo|fixme)\b", "template_keywords"),
            (r"\b(lorem ipsum|sample text)\b", "placeholder_text"),
            (r"\b(12345|99999|00000)\b", "placeholder_numbers"),
            (r"(N/A|TBD|XXX|\?\?\?)", "incomplete_values"),
        ]

        # Track repeated non-ticker-specific values
        value_occurrences = defaultdict(lambda: defaultdict(list))

        def extract_values(obj, path=""):
            """Recursively extract all string and numeric values"""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    extract_values(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_values(item, f"{path}[{i}]")
            elif isinstance(obj, (str, int, float)) and obj:
                # Skip common expected values
                if not isinstance(obj, str) or (
                    len(str(obj)) > 3 and str(obj) not in ["true", "false", "null", "stable", "improving", "declining"]
                ):
                    value_occurrences[str(obj)][path].append(self.files_analyzed[files_data.index(obj)])

        # Analyze each file
        for idx, data in enumerate(files_data):
            ticker = self.extract_ticker_from_filename(Path(self.files_analyzed[idx]["filename"]))

            # Check for suspicious patterns
            data_str = json.dumps(data, default=str).lower()
            for pattern, pattern_type in suspicious_patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    self.hardcoded_values[pattern_type].append(
                        {
                            "file": self.files_analyzed[idx]["filename"],
                            "pattern": pattern,
                            "ticker": ticker,
                        }
                    )

        # Find values that appear across multiple files (potential hardcoded values)
        suspicious_repeated_values = []
        for value, locations in value_occurrences.items():
            unique_files = set()
            for path, file_refs in locations.items():
                unique_files.update(f["filename"] for f in file_refs)

            if len(unique_files) >= 3:  # Value appears in 3+ files
                # Check if it's not a common expected value
                if not any(
                    expected in value.lower()
                    for expected in [
                        "healthy",
                        "operational",
                        "stable",
                        "moderate",
                        "high",
                        "low",
                        "improving",
                        "declining",
                        "neutral",
                        "analysis",
                        "validation",
                    ]
                ):
                    suspicious_repeated_values.append(
                        {
                            "value": value,
                            "occurrences": len(unique_files),
                            "files_affected": list(unique_files)[:3] + (["..."] if len(unique_files) > 3 else []),
                        }
                    )

        if suspicious_repeated_values:
            self.hardcoded_values["repeated_values"] = suspicious_repeated_values

        # Calculate score (lower is better)
        total_issues = sum(len(issues) for issues in self.hardcoded_values.values())
        max_expected_issues = len(files_data) * 5  # Assume max 5 issues per file
        score = max(0, (max_expected_issues - total_issues) / max_expected_issues)

        return score

    def validate_ticker_specificity(self, files_data: list[dict[str, Any]]) -> float:
        """Validate that data is appropriately ticker-specific"""
        specificity_scores = []

        for idx, data in enumerate(files_data):
            ticker = self.extract_ticker_from_filename(Path(self.files_analyzed[idx]["filename"]))
            issues = []

            # Check company name matches ticker
            company_name = data.get("company_overview", {}).get("name", "")
            if ticker not in ["XYZ"] and company_name and ticker not in company_name:
                # Some flexibility for company names that might not contain ticker
                if not any(word in company_name.upper() for word in ticker.split("_")):
                    issues.append(f"Company name '{company_name}' doesn't match ticker {ticker}")

            # Check market data specificity
            market_data = data.get("market_data", {})
            if market_data:
                # Verify price data is unique (not repeated across files)
                current_price = market_data.get("current_price")
                if current_price:
                    price_count = sum(
                        1 for d in files_data if d.get("market_data", {}).get("current_price") == current_price
                    )
                    if price_count > 1:
                        issues.append(f"Current price {current_price} appears in {price_count} files")

            # Check financial metrics uniqueness
            financial_health = data.get("financial_health_analysis", {})
            if financial_health:
                profitability = financial_health.get("profitability_assessment", {})
                if isinstance(profitability, dict):
                    gross_margin = profitability.get("gross_margin_analysis", {})
                    if isinstance(gross_margin, dict):
                        margin_value = gross_margin.get("gross_margin") or gross_margin.get("gross_margin_2024")
                        if margin_value:
                            margin_count = sum(
                                1
                                for d in files_data
                                for prof in [d.get("financial_health_analysis", {}).get("profitability_assessment", {})]
                                for gm in [prof.get("gross_margin_analysis", {})]
                                if (
                                    gm.get("gross_margin") == margin_value
                                    or gm.get("gross_margin_2024") == margin_value
                                )
                            )
                            if margin_count > 1:
                                issues.append(f"Gross margin {margin_value} appears in {margin_count} files")

            if issues:
                self.ticker_specificity_issues.append(
                    {
                        "file": self.files_analyzed[idx]["filename"],
                        "ticker": ticker,
                        "issues": issues,
                    }
                )

            score = 1.0 - (len(issues) * 0.2)  # Deduct 20% per issue
            specificity_scores.append(max(0, score))

        return sum(specificity_scores) / len(specificity_scores) if specificity_scores else 0.0

    def assess_cli_integration_consistency(self, files_data: list[dict[str, Any]]) -> float:
        """Assess consistency of CLI services integration"""
        cli_scores = []

        expected_services = {
            "yahoo_finance_cli",
            "alpha_vantage_cli",
            "fmp_cli",
            "fred_economic_cli",
            "coingecko_cli",
            "sec_edgar_cli",
            "imf_cli",
        }

        for idx, data in enumerate(files_data):
            issues = []

            # Check CLI services utilized
            cli_services = data.get("metadata", {}).get("cli_services_utilized", [])
            if not cli_services:
                issues.append("No CLI services documented in metadata")
            else:
                # Check for consistency in service usage
                missing_services = expected_services - set(cli_services)
                if len(missing_services) > 2:  # Allow some flexibility
                    issues.append(f"Missing expected CLI services: {missing_services}")

            # Check CLI service validation section
            cli_validation = data.get("cli_service_validation", {})
            if not cli_validation:
                issues.append("Missing cli_service_validation section")
            else:
                # Check service health reporting
                service_health = cli_validation.get("service_health", {})
                if not service_health:
                    issues.append("Missing service health information")

                # Check data quality scores
                quality_scores = cli_validation.get("data_quality_scores", {})
                if not quality_scores:
                    issues.append("Missing data quality scores")

            # Check price validation consistency
            price_validation = data.get("market_data", {}).get("price_validation", {})
            if price_validation:
                # Verify multi-source validation
                expected_price_sources = [
                    "yahoo_finance_price",
                    "alpha_vantage_price",
                    "fmp_price",
                ]
                missing_sources = [s for s in expected_price_sources if s not in price_validation]
                if missing_sources:
                    issues.append(f"Missing price validation sources: {missing_sources}")

            if issues:
                self.cli_consistency_issues.append({"file": self.files_analyzed[idx]["filename"], "issues": issues})

            score = 1.0 - (len(issues) * 0.15)  # Deduct 15% per issue
            cli_scores.append(max(0, score))

        return sum(cli_scores) / len(cli_scores) if cli_scores else 0.0

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive cross-analysis validation report"""
        # Load and analyze files
        latest_files = self.get_latest_files(7)
        files_data = []

        for filepath in latest_files:
            data = self.load_json_file(filepath)
            if data:
                self.files_analyzed.append(
                    {
                        "filename": filepath.name,
                        "ticker": self.extract_ticker_from_filename(filepath),
                        "modification_timestamp": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                        "file_size_bytes": filepath.stat().st_size,
                        "structural_compliance": None,  # Will be calculated
                    }
                )
                files_data.append(data)

        # Run analyses
        structural_score = self.analyze_structural_consistency(files_data)
        hardcoded_score = self.detect_hardcoded_values(files_data)
        ticker_specificity_score = self.validate_ticker_specificity(files_data)
        cli_integration_score = self.assess_cli_integration_consistency(files_data)

        # Update structural compliance scores
        for idx, issue in enumerate(self.structural_issues):
            file_idx = issue["file_index"]
            self.files_analyzed[file_idx]["structural_compliance"] = f"{issue['compliance_score']:.1f}/10.0"

        # Calculate overall score
        overall_score = (
            structural_score * 0.25
            + hardcoded_score * 0.25
            + ticker_specificity_score * 0.25
            + cli_integration_score * 0.25
        )

        # Generate recommendations
        immediate_fixes = []
        if structural_score < 0.9:
            immediate_fixes.append("Standardize JSON structure across all analysis files")
        if hardcoded_score < 0.9:
            immediate_fixes.append("Replace hardcoded values with ticker-specific data")
        if ticker_specificity_score < 0.9:
            immediate_fixes.append("Ensure all financial data is unique to each ticker")
        if cli_integration_score < 0.9:
            immediate_fixes.append("Standardize CLI service integration and validation")

        return {
            "metadata": {
                "command_name": "fundamental_analyst_validate_dasv_cross_analysis",
                "execution_timestamp": datetime.now().isoformat(),
                "framework_phase": "dasv_phase_cross_analysis",
                "dasv_phase_analyzed": "analysis",
                "files_analyzed_count": len(self.files_analyzed),
                "analysis_methodology": "comprehensive_cross_phase_consistency_validation",
            },
            "files_analyzed": self.files_analyzed,
            "cross_analysis_results": {
                "structural_consistency_score": f"{structural_score * 10:.1f}/10.0",
                "hardcoded_values_score": f"{hardcoded_score * 10:.1f}/10.0",
                "ticker_specificity_score": f"{ticker_specificity_score * 10:.1f}/10.0",
                "cli_integration_score": f"{cli_integration_score * 10:.1f}/10.0",
                "overall_cross_analysis_score": f"{overall_score * 10:.1f}/10.0",
            },
            "detected_issues": {
                "structural_inconsistencies": self.structural_issues,
                "hardcoded_values": dict(self.hardcoded_values),
                "ticker_specificity_violations": self.ticker_specificity_issues,
                "cli_integration_inconsistencies": self.cli_consistency_issues,
            },
            "quality_assessment": {
                "institutional_quality_certified": overall_score >= 0.95,
                "minimum_threshold_met": overall_score >= 0.90,
                "phase_consistency_grade": self._calculate_grade(overall_score),
                "ready_for_production": overall_score >= 0.90,
            },
            "recommendations": {
                "immediate_fixes": immediate_fixes,
                "template_improvements": [
                    "Add automated ticker-specific data validation",
                    "Implement structural compliance checking in analysis phase",
                    "Enhance CLI service integration documentation",
                ],
                "validation_enhancements": [
                    "Add real-time data validation against CLI sources",
                    "Implement cross-file uniqueness validation",
                    "Create automated template artifact detection",
                ],
                "cli_integration_optimizations": [
                    "Standardize CLI service health monitoring",
                    "Implement consistent multi-source validation patterns",
                    "Add CLI service fallback mechanisms",
                ],
            },
        }

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 0.97:
            return "A+"
        if score >= 0.93:
            return "A"
        if score >= 0.90:
            return "A-"
        if score >= 0.87:
            return "B+"
        if score >= 0.83:
            return "B"
        if score >= 0.80:
            return "B-"
        if score >= 0.77:
            return "C+"
        if score >= 0.73:
            return "C"
        return "F"


def main():
    # Set up paths
    analysis_dir = "/Users/colemorton/Projects/colemorton.com/data/outputs/fundamental_analysis/analysis"
    output_dir = "/Users/colemorton/Projects/colemorton.com/data/outputs/fundamental_analysis/validation"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Run validation
    validator = AnalysisCrossValidator(analysis_dir)
    report = validator.generate_report()

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(output_dir, f"analysis_cross_analysis_{timestamp}_validation.json")

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print("Cross-analysis validation complete. Report saved to: {output_file}")
    print(f"Overall Score: {report['cross_analysis_results']['overall_cross_analysis_score']}")
    print("Files Analyzed: {report['metadata']['files_analyzed_count']}")


if __name__ == "__main__":
    main()
