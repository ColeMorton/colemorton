#!/usr/bin/env python3
"""
Macro-Economic Analysis Cross-Validation Module - DASV Phase Cross-Analysis Mode
Comprehensive cross-analysis validation for multiple regional analysis files
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))


class MacroAnalysisCrossValidation:
    """Cross-analysis validation for macro-economic analysis files"""

    def __init__(
        self,
        analysis_dir: str = "./data/outputs/macro_analysis/analysis/",
        output_dir: str = "./data/outputs/macro_analysis/validation/",
        max_files: int = 7,
    ):
        """
        Initialize macro-economic cross-analysis validation

        Args:
            analysis_dir: Directory containing analysis files
            output_dir: Directory to save validation outputs
            max_files: Maximum number of files to analyze (default 7)
        """
        self.analysis_dir = analysis_dir
        self.output_dir = output_dir
        self.max_files = max_files
        self.timestamp = datetime.now()

        # Load analysis files
        self.analysis_files = self._discover_analysis_files()
        self.analysis_data = self._load_analysis_data()

        # Validation results
        self.validation_results = {}
        self.cross_analysis_score = 0.0
        self.detected_issues = []

    def _discover_analysis_files(self) -> list[str]:
        """Discover analysis files in the target directory"""
        if not os.path.exists(self.analysis_dir):
            raise FileNotFoundError(f"Analysis directory not found: {self.analysis_dir}")

        analysis_files = []
        for file in os.listdir(self.analysis_dir):
            if file.endswith("_analysis.json"):
                file_path = os.path.join(self.analysis_dir, file)
                analysis_files.append(file_path)

        # Sort by modification time (latest first) and take max_files
        analysis_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        selected_files = analysis_files[: self.max_files]

        print("📁 Discovered {len(analysis_files)} analysis files")
        print("🎯 Selected {len(selected_files)} latest files for cross-validation")

        return selected_files

    def _load_analysis_data(self) -> dict[str, dict[str, Any]]:
        """Load analysis data from discovered files"""
        analysis_data = {}

        for file_path in self.analysis_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    filename = os.path.basename(file_path)
                    analysis_data[filename] = data
                    print("✅ Loaded: {filename}")
            except Exception:
                print("⚠️  Failed to load {file_path}: {e}")

        return analysis_data

    def validate_structural_consistency(self) -> dict[str, Any]:
        """Analyze structural consistency across files"""
        consistency_results = {
            "schema_consistency": self._check_schema_consistency(),
            "metadata_consistency": self._check_metadata_consistency(),
            "section_completeness": self._check_section_completeness(),
            "confidence_score_consistency": self._check_confidence_consistency(),
            "analysis_methodology_consistency": self._check_methodology_consistency(),
            "regional_specificity_validation": self._check_regional_specificity(),
            "overall_structural_score": 0.0,
        }

        # Calculate overall structural score
        scores = [
            v for k, v in consistency_results.items() if isinstance(v, (int, float)) and k != "overall_structural_score"
        ]
        consistency_results["overall_structural_score"] = np.mean(scores) if scores else 0.0

        return consistency_results

    def detect_hardcoded_magic_values(self) -> dict[str, Any]:
        """Detect hardcoded/magic values across analysis files"""
        magic_value_issues = {
            "hardcoded_rates": self._detect_hardcoded_rates(),
            "magic_thresholds": self._detect_magic_thresholds(),
            "template_artifacts": self._detect_template_artifacts(),
            "inconsistent_numeric_values": self._detect_inconsistent_values(),
            "placeholder_values": self._detect_placeholder_values(),
            "overall_magic_value_score": 0.0,
        }

        # Calculate overall magic value score (higher is better, means less issues)
        issue_counts = [
            len(v) if isinstance(v, list) else v
            for k, v in magic_value_issues.items()
            if k != "overall_magic_value_score"
        ]
        total_issues = sum(issue_counts)
        magic_value_issues["overall_magic_value_score"] = max(1.0 - (total_issues / 50), 0.0)

        return magic_value_issues

    def validate_region_specificity(self) -> dict[str, Any]:
        """Validate region-specific content and avoid generic templates"""
        region_validation = {
            "region_specific_indicators": self._validate_regional_indicators(),
            "currency_specificity": self._validate_currency_specificity(),
            "policy_context_specificity": self._validate_policy_specificity(),
            "economic_data_regionalization": self._validate_economic_regionalization(),
            "cross_regional_consistency": self._validate_cross_regional_consistency(),
            "template_generalization_detection": self._detect_template_generalization(),
            "overall_region_specificity_score": 0.0,
        }

        # Calculate overall region specificity score
        scores = [
            v
            for k, v in region_validation.items()
            if isinstance(v, (int, float)) and k != "overall_region_specificity_score"
        ]
        region_validation["overall_region_specificity_score"] = np.mean(scores) if scores else 0.0

        return region_validation

    def validate_cli_services_integration(self) -> dict[str, Any]:
        """Validate CLI services integration consistency"""
        cli_validation = {
            "service_utilization_consistency": self._validate_service_consistency(),
            "data_source_alignment": self._validate_data_source_alignment(),
            "service_specific_indicators": self._validate_service_indicators(),
            "cross_service_validation": self._validate_cross_service_data(),
            "cli_methodology_consistency": self._validate_cli_methodology(),
            "overall_cli_integration_score": 0.0,
        }

        # Calculate overall CLI integration score
        scores = [
            v for k, v in cli_validation.items() if isinstance(v, (int, float)) and k != "overall_cli_integration_score"
        ]
        cli_validation["overall_cli_integration_score"] = np.mean(scores) if scores else 0.0

        return cli_validation

    def calculate_cross_analysis_score(self) -> float:
        """Calculate overall cross-analysis validation score"""
        validation_components = [
            self.validate_structural_consistency(),
            self.detect_hardcoded_magic_values(),
            self.validate_region_specificity(),
            self.validate_cli_services_integration(),
        ]

        component_scores = []
        for component in validation_components:
            for key, value in component.items():
                if "overall" in key and isinstance(value, (int, float)):
                    component_scores.append(value)

        self.cross_analysis_score = np.mean(component_scores) if component_scores else 0.0
        return self.cross_analysis_score

    def identify_critical_issues(self) -> list[dict[str, Any]]:
        """Identify critical issues requiring attention"""
        issues = []

        # Structural consistency issues
        structural = self.validate_structural_consistency()
        if structural.get("overall_structural_score", 0) < 0.8:
            issues.append(
                {
                    "severity": "high",
                    "category": "structural_consistency",
                    "finding": f"Structural consistency below threshold: {structural.get('overall_structural_score', 0):.2f}",
                    "recommendation": "Review and align structural consistency across analysis files",
                }
            )

        # Magic value issues
        magic_values = self.detect_hardcoded_magic_values()
        if magic_values.get("overall_magic_value_score", 0) < 0.8:
            issues.append(
                {
                    "severity": "medium",
                    "category": "hardcoded_values",
                    "finding": "High number of hardcoded/magic values detected",
                    "recommendation": "Replace hardcoded values with dynamic data-driven calculations",
                }
            )

        # Region specificity issues
        region_spec = self.validate_region_specificity()
        if region_spec.get("overall_region_specificity_score", 0) < 0.8:
            issues.append(
                {
                    "severity": "high",
                    "category": "region_specificity",
                    "finding": f"Region specificity below threshold: {region_spec.get('overall_region_specificity_score', 0):.2f}",
                    "recommendation": "Enhance region-specific content and avoid generic templates",
                }
            )

        # CLI services issues
        cli_services = self.validate_cli_services_integration()
        if cli_services.get("overall_cli_integration_score", 0) < 0.8:
            issues.append(
                {
                    "severity": "medium",
                    "category": "cli_services_integration",
                    "finding": "CLI services integration inconsistent across files",
                    "recommendation": "Standardize CLI service usage patterns and data integration",
                }
            )

        self.detected_issues = issues
        return issues

    def generate_validation_report(self) -> dict[str, Any]:
        """Generate comprehensive cross-analysis validation report"""
        cross_analysis_score = self.calculate_cross_analysis_score()
        critical_issues = self.identify_critical_issues()

        report_data = {
            "metadata": {
                "command_name": "macro_analysis_cross_validation",
                "execution_timestamp": self.timestamp.isoformat(),
                "framework_phase": "cross_analysis_validation",
                "analysis_directory": self.analysis_dir,
                "files_analyzed": len(self.analysis_files),
                "analysis_files": [os.path.basename(f) for f in self.analysis_files],
                "validation_methodology": "dasv_phase_cross_analysis_comprehensive_validation",
                "cross_analysis_mode": "enabled",
                "max_files_analyzed": self.max_files,
            },
            "cross_analysis_summary": {
                "overall_cross_analysis_score": cross_analysis_score,
                "validation_status": ("PASS" if cross_analysis_score >= 9.0 else "REVIEW_REQUIRED"),
                "target_score": 9.0,
                "score_achievement": cross_analysis_score >= 9.0,
                "critical_issues_count": len([i for i in critical_issues if i["severity"] == "high"]),
                "medium_issues_count": len([i for i in critical_issues if i["severity"] == "medium"]),
                "low_issues_count": len([i for i in critical_issues if i["severity"] == "low"]),
                "files_processed": len(self.analysis_data),
                "validation_date": self.timestamp.strftime("%Y%m%d"),
            },
            "structural_consistency_analysis": self.validate_structural_consistency(),
            "hardcoded_magic_value_detection": self.detect_hardcoded_magic_values(),
            "region_specificity_validation": self.validate_region_specificity(),
            "cli_services_integration_consistency": self.validate_cli_services_integration(),
            "detected_issues": critical_issues,
            "quality_assessment": self._generate_quality_assessment(),
            "recommendations": self._generate_recommendations(),
            "file_specific_analysis": self._generate_file_specific_analysis(),
            "cross_file_comparison": self._generate_cross_file_comparison(),
            "validation_confidence": self._calculate_validation_confidence(),
        }

        self.validation_results = report_data
        return report_data

    def save_validation_output(self, data: dict[str, Any]) -> str:
        """Save validation output to file"""
        os.makedirs(self.output_dir, exist_ok=True)

        filename = f"analysis_cross_analysis_{self.timestamp.strftime('%Y%m%d')}_validation.json"
        filepath = os.path.join(self.output_dir, filename)

        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj

        serializable_data = convert_numpy_types(data)

        with open(filepath, "w") as f:
            json.dump(serializable_data, f, indent=2)

        print("✅ Saved cross-analysis validation output to: {filepath}")
        return filepath

    # Helper methods for structural consistency validation
    def _check_schema_consistency(self) -> float:
        """Check schema consistency across files"""
        if not self.analysis_data:
            return 0.0

        # Get all top-level keys from each file
        all_schemas = []
        for filename, data in self.analysis_data.items():
            schema = set(data.keys())
            all_schemas.append(schema)

        if not all_schemas:
            return 0.0

        # Calculate intersection consistency
        base_schema = all_schemas[0]
        consistent_keys = base_schema
        for schema in all_schemas[1:]:
            consistent_keys = consistent_keys.intersection(schema)

        # Score based on consistency ratio
        total_unique_keys = set()
        for schema in all_schemas:
            total_unique_keys.update(schema)

        consistency_ratio = len(consistent_keys) / len(total_unique_keys) if total_unique_keys else 0
        return round(consistency_ratio, 3)

    def _check_metadata_consistency(self) -> float:
        """Check metadata consistency across files"""
        metadata_consistency = []

        for filename, data in self.analysis_data.items():
            metadata = data.get("metadata", {})
            required_fields = [
                "command_name",
                "framework_phase",
                "region",
                "analysis_methodology",
            ]

            present_fields = sum(1 for field in required_fields if field in metadata)
            consistency_score = present_fields / len(required_fields)
            metadata_consistency.append(consistency_score)

        return np.mean(metadata_consistency) if metadata_consistency else 0.0

    def _check_section_completeness(self) -> float:
        """Check section completeness across files"""
        required_sections = [
            "business_cycle_modeling",
            "liquidity_cycle_positioning",
            "quantified_risk_assessment",
            "enhanced_economic_sensitivity",
            "macroeconomic_risk_scoring",
        ]

        completeness_scores = []
        for filename, data in self.analysis_data.items():
            present_sections = sum(1 for section in required_sections if section in data)
            completeness_score = present_sections / len(required_sections)
            completeness_scores.append(completeness_score)

        return np.mean(completeness_scores) if completeness_scores else 0.0

    def _check_confidence_consistency(self) -> float:
        """Check confidence score consistency"""
        confidence_scores = []

        for filename, data in self.analysis_data.items():
            # Check metadata confidence
            metadata_confidence = data.get("metadata", {}).get("confidence_threshold", 0)
            if metadata_confidence:
                confidence_scores.append(metadata_confidence)

            # Check section-level confidence scores
            for section_name, section_data in data.items():
                if isinstance(section_data, dict) and "confidence" in section_data:
                    confidence_scores.append(section_data["confidence"])

        if not confidence_scores:
            return 0.0

        # Check if confidence scores are in reasonable range and consistent
        numeric_scores = []
        for score in confidence_scores:
            try:
                if isinstance(score, (int, float)):
                    numeric_scores.append(float(score))
                elif isinstance(score, str):
                    # Try to parse string numbers
                    numeric_scores.append(float(score))
            except (ValueError, TypeError):
                continue

        if not numeric_scores:
            return 0.0

        reasonable_range = all(0.7 <= score <= 1.0 for score in numeric_scores)
        variance = np.var(numeric_scores)

        if reasonable_range and variance <= 0.05:
            return 0.95
        if reasonable_range:
            return 0.8
        return 0.5

    def _check_methodology_consistency(self) -> float:
        """Check analysis methodology consistency"""
        methodologies = []

        for filename, data in self.analysis_data.items():
            methodology = data.get("metadata", {}).get("analysis_methodology", "")
            if methodology:
                methodologies.append(methodology)

        if not methodologies:
            return 0.0

        # Check for consistent methodology patterns
        consistent_methodology = len(set(methodologies)) <= 2  # Allow for minor variations
        return 0.9 if consistent_methodology else 0.6

    def _check_regional_specificity(self) -> float:
        """Check regional specificity in analysis"""
        specificity_scores = []

        for filename, data in self.analysis_data.items():
            region = data.get("metadata", {}).get("region", "")

            # Look for region-specific indicators in the analysis
            region_specific_indicators = 0

            # Check for region-specific references in key sections
            business_cycle = data.get("business_cycle_modeling", {})
            if isinstance(business_cycle, dict):
                business_cycle_str = json.dumps(business_cycle).lower()
                if region.lower() in business_cycle_str:
                    region_specific_indicators += 1

            liquidity_cycle = data.get("liquidity_cycle_positioning", {})
            if isinstance(liquidity_cycle, dict):
                liquidity_str = json.dumps(liquidity_cycle).lower()
                if any(term in liquidity_str for term in ["fed", "ecb", "boj", "pboc"]):
                    region_specific_indicators += 1

            specificity_score = min(region_specific_indicators / 5, 1.0)  # Scale to 0-1
            specificity_scores.append(specificity_score)

        return np.mean(specificity_scores) if specificity_scores else 0.0

    # Helper methods for magic value detection
    def _detect_hardcoded_rates(self) -> list[dict[str, Any]]:
        """Detect hardcoded interest rates and economic values"""
        hardcoded_issues = []

        common_hardcoded_patterns = [
            "5.375",
            "4.25",
            "2.5",
            "3.0",
            "4.0",
            "5.0",  # Common rate values
            "0.9",
            "0.85",
            "0.8",
            "0.75",  # Common confidence thresholds
        ]

        for filename, data in self.analysis_data.items():
            data_str = json.dumps(data)

            for pattern in common_hardcoded_patterns:
                if pattern in data_str:
                    # Count occurrences
                    count = data_str.count(pattern)
                    if count > 3:  # Threshold for considering it hardcoded
                        hardcoded_issues.append(
                            {
                                "file": filename,
                                "value": pattern,
                                "occurrences": count,
                                "type": "potential_hardcoded_rate",
                            }
                        )

        return hardcoded_issues

    def _detect_magic_thresholds(self) -> list[dict[str, Any]]:
        """Detect magic number thresholds"""
        magic_issues = []

        # Common magic numbers in economic analysis
        magic_patterns = [
            ("100", "percentage_base"),
            ("1000", "scaling_factor"),
            ("365", "days_in_year"),
            ("12", "months_in_year"),
            ("4", "quarters_in_year"),
        ]

        for filename, data in self.analysis_data.items():
            data_str = json.dumps(data)

            for pattern, pattern_type in magic_patterns:
                count = data_str.count(f'"{pattern}"')  # Look for quoted numbers
                if count > 2:
                    magic_issues.append(
                        {
                            "file": filename,
                            "value": pattern,
                            "type": pattern_type,
                            "occurrences": count,
                        }
                    )

        return magic_issues

    def _detect_template_artifacts(self) -> list[dict[str, Any]]:
        """Detect template artifacts and placeholder text"""
        template_issues = []

        template_patterns = [
            "template",
            "placeholder",
            "example",
            "sample",
            "TODO",
            "FIXME",
            "TBD",
            "lorem_ipsum",
        ]

        for filename, data in self.analysis_data.items():
            data_str = json.dumps(data).lower()

            for pattern in template_patterns:
                if pattern.lower() in data_str:
                    template_issues.append(
                        {
                            "file": filename,
                            "artifact": pattern,
                            "type": "template_artifact",
                        }
                    )

        return template_issues

    def _detect_inconsistent_values(self) -> list[dict[str, Any]]:
        """Detect inconsistent numeric values across files"""
        inconsistent_issues = []

        # Collect similar metrics across files
        value_collections = {}

        for filename, data in self.analysis_data.items():
            # Extract numeric values from key sections
            if "business_cycle_modeling" in data:
                recession_prob = data["business_cycle_modeling"].get("recession_probability")
                if recession_prob:
                    if "recession_probability" not in value_collections:
                        value_collections["recession_probability"] = []
                    value_collections["recession_probability"].append({"file": filename, "value": recession_prob})

        # Check for inconsistencies
        for metric, values in value_collections.items():
            if len(values) > 1:
                numeric_values = []
                for item in values:
                    try:
                        if isinstance(item["value"], (int, float)):
                            numeric_values.append(float(item["value"]))
                        elif isinstance(item["value"], str):
                            # Try to extract numeric value from string
                            import re

                            matches = re.findall(r"0\.\d+|\d+\.\d+", item["value"])
                            if matches:
                                numeric_values.append(float(matches[0]))
                    except:
                        pass

                if len(numeric_values) > 1:
                    value_range = max(numeric_values) - min(numeric_values)
                    if value_range > 0.2:  # Threshold for inconsistency
                        inconsistent_issues.append(
                            {
                                "metric": metric,
                                "files": [item["file"] for item in values],
                                "values": numeric_values,
                                "range": value_range,
                                "type": "inconsistent_cross_file_values",
                            }
                        )

        return inconsistent_issues

    def _detect_placeholder_values(self) -> list[dict[str, Any]]:
        """Detect placeholder values"""
        placeholder_issues = []

        placeholder_patterns = [
            "0.0",
            "1.0",
            "null",
            "undefined",
            "n/a",
            "tbd",
            "pending",
        ]

        for filename, data in self.analysis_data.items():
            data_str = json.dumps(data).lower()

            # Count placeholder occurrences
            placeholder_count = sum(data_str.count(pattern) for pattern in placeholder_patterns)

            if placeholder_count > 10:  # Threshold for excessive placeholders
                placeholder_issues.append(
                    {
                        "file": filename,
                        "placeholder_count": placeholder_count,
                        "type": "excessive_placeholders",
                    }
                )

        return placeholder_issues

    # Helper methods for region specificity validation
    def _validate_regional_indicators(self) -> float:
        """Validate region-specific economic indicators"""
        region_scores = []

        regional_indicators = {
            "US": ["fed", "dollar", "treasury", "gdp", "unemployment", "cpi"],
            "EUROPE": ["ecb", "euro", "eurozone", "bund", "pmi"],
            "ASIA": ["boj", "pboc", "yen", "yuan", "nikkei"],
            "GLOBAL": ["imf", "world", "international", "cross_border"],
            "AMERICAS": ["fed", "nafta", "usmca", "americas"],
        }

        for filename, data in self.analysis_data.items():
            region = data.get("metadata", {}).get("region", "").upper()
            data_str = json.dumps(data).lower()

            if region in regional_indicators:
                expected_indicators = regional_indicators[region]
                found_indicators = sum(1 for indicator in expected_indicators if indicator in data_str)
                region_score = found_indicators / len(expected_indicators)
                region_scores.append(region_score)
            else:
                region_scores.append(0.5)  # Unknown region

        return np.mean(region_scores) if region_scores else 0.0

    def _validate_currency_specificity(self) -> float:
        """Validate currency-specific references"""
        currency_scores = []

        currency_mapping = {
            "US": ["usd", "dollar", "$"],
            "EUROPE": ["eur", "euro", "€"],
            "ASIA": ["yen", "yuan", "rmb", "¥"],
            "GLOBAL": ["usd", "eur", "yen", "cross_currency"],
            "AMERICAS": ["usd", "cad", "mxn", "dollar"],
        }

        for filename, data in self.analysis_data.items():
            region = data.get("metadata", {}).get("region", "").upper()
            data_str = json.dumps(data).lower()

            if region in currency_mapping:
                expected_currencies = currency_mapping[region]
                found_currencies = sum(1 for currency in expected_currencies if currency in data_str)
                currency_score = min(found_currencies / 2, 1.0)  # Need at least 2 currency refs
                currency_scores.append(currency_score)
            else:
                currency_scores.append(0.5)

        return np.mean(currency_scores) if currency_scores else 0.0

    def _validate_policy_specificity(self) -> float:
        """Validate policy context specificity"""
        policy_scores = []

        policy_contexts = {
            "US": ["fed", "fomc", "federal_reserve", "fed_funds"],
            "EUROPE": ["ecb", "european_central_bank", "main_rate"],
            "ASIA": ["boj", "pboc", "bank_of_japan", "peoples_bank"],
            "GLOBAL": ["central_bank", "monetary_policy", "coordination"],
            "AMERICAS": ["fed", "bank_of_canada", "banco_de_mexico"],
        }

        for filename, data in self.analysis_data.items():
            region = data.get("metadata", {}).get("region", "").upper()

            # Check liquidity cycle positioning section for policy context
            liquidity_section = data.get("liquidity_cycle_positioning", {})
            policy_str = json.dumps(liquidity_section).lower()

            if region in policy_contexts:
                expected_policies = policy_contexts[region]
                found_policies = sum(1 for policy in expected_policies if policy in policy_str)
                policy_score = min(found_policies / 2, 1.0)
                policy_scores.append(policy_score)
            else:
                policy_scores.append(0.5)

        return np.mean(policy_scores) if policy_scores else 0.0

    def _validate_economic_regionalization(self) -> float:
        """Validate economic data regionalization"""
        regionalization_scores = []

        for filename, data in self.analysis_data.items():
            region = data.get("metadata", {}).get("region", "")

            # Check for region-specific economic data references
            region_specific_count = 0

            # Check business cycle modeling
            business_cycle = data.get("business_cycle_modeling", {})
            if isinstance(business_cycle, dict):
                bc_str = json.dumps(business_cycle).lower()
                if any(term in bc_str for term in [region.lower(), "regional", "domestic"]):
                    region_specific_count += 1

            # Check economic sensitivity
            economic_sensitivity = data.get("enhanced_economic_sensitivity", {})
            if isinstance(economic_sensitivity, dict):
                es_str = json.dumps(economic_sensitivity).lower()
                if region.lower() in es_str:
                    region_specific_count += 1

            regionalization_score = min(region_specific_count / 3, 1.0)
            regionalization_scores.append(regionalization_score)

        return np.mean(regionalization_scores) if regionalization_scores else 0.0

    def _validate_cross_regional_consistency(self) -> float:
        """Validate consistency in cross-regional analysis"""
        if len(self.analysis_data) < 2:
            return 1.0  # Can't validate consistency with single file

        # Check for consistent analysis frameworks across regions
        frameworks = []
        for filename, data in self.analysis_data.items():
            methodology = data.get("metadata", {}).get("analysis_methodology", "")
            frameworks.append(methodology)

        # Allow for reasonable variations while checking for consistency
        unique_frameworks = set(frameworks)
        consistency_score = 1.0 if len(unique_frameworks) <= 2 else 0.7

        return consistency_score

    def _detect_template_generalization(self) -> list[dict[str, Any]]:
        """Detect overly generic template usage"""
        generic_issues = []

        generic_patterns = [
            "generic",
            "standard",
            "typical",
            "general",
            "universal",
            "common",
        ]

        for filename, data in self.analysis_data.items():
            data_str = json.dumps(data).lower()

            generic_count = sum(data_str.count(pattern) for pattern in generic_patterns)

            if generic_count > 5:  # Threshold for excessive generic language
                generic_issues.append(
                    {
                        "file": filename,
                        "generic_references": generic_count,
                        "type": "excessive_generic_language",
                    }
                )

        return generic_issues

    # Helper methods for CLI services validation
    def _validate_service_consistency(self) -> float:
        """Validate CLI service utilization consistency"""
        service_usage = []

        for filename, data in self.analysis_data.items():
            services = data.get("metadata", {}).get("cli_services_utilized", [])
            service_usage.append(set(services) if services else set())

        if not service_usage:
            return 0.0

        # Check for consistent service usage patterns
        common_services = service_usage[0]
        for services in service_usage[1:]:
            common_services = common_services.intersection(services)

        # Calculate consistency based on common services
        total_unique_services = set()
        for services in service_usage:
            total_unique_services.update(services)

        consistency_ratio = len(common_services) / len(total_unique_services) if total_unique_services else 0
        return consistency_ratio

    def _validate_data_source_alignment(self) -> float:
        """Validate data source alignment across files"""
        # Check for consistent discovery file references
        discovery_refs = []

        for filename, data in self.analysis_data.items():
            discovery_ref = data.get("metadata", {}).get("discovery_file_reference", "")
            if discovery_ref:
                discovery_refs.append(discovery_ref)

        if not discovery_refs:
            return 0.5  # No discovery references found

        # Check for consistent referencing patterns
        consistent_patterns = len(set(discovery_refs)) <= len(discovery_refs) * 0.5
        return 0.9 if consistent_patterns else 0.6

    def _validate_service_indicators(self) -> float:
        """Validate service-specific indicators"""
        service_indicator_scores = []

        expected_indicators = {
            "fred_economic": ["gdp", "unemployment", "inflation", "interest_rate"],
            "imf": ["global", "international", "cross_border"],
            "alpha_vantage": ["equity", "market", "volatility"],
            "eia": ["energy", "oil", "gas", "commodities"],
        }

        for filename, data in self.analysis_data.items():
            services = data.get("metadata", {}).get("cli_services_utilized", [])
            data_str = json.dumps(data).lower()

            service_score = 0
            service_count = 0

            for service in services:
                service_name = service.replace("_cli", "")
                if service_name in expected_indicators:
                    service_count += 1
                    indicators = expected_indicators[service_name]
                    found_indicators = sum(1 for indicator in indicators if indicator in data_str)
                    service_score += found_indicators / len(indicators)

            avg_service_score = service_score / service_count if service_count > 0 else 0
            service_indicator_scores.append(avg_service_score)

        return np.mean(service_indicator_scores) if service_indicator_scores else 0.0

    def _validate_cross_service_data(self) -> float:
        """Validate cross-service data consistency"""
        # This is a complex validation that would require actual data comparison
        # For now, return a reasonable score based on service usage

        total_services = set()
        for filename, data in self.analysis_data.items():
            services = data.get("metadata", {}).get("cli_services_utilized", [])
            total_services.update(services)

        # Score based on diversity and coverage of services
        service_diversity = len(total_services)
        if service_diversity >= 5:
            return 0.9
        if service_diversity >= 3:
            return 0.8
        if service_diversity >= 2:
            return 0.7
        return 0.5

    def _validate_cli_methodology(self) -> float:
        """Validate CLI methodology consistency"""
        methodologies = []

        for filename, data in self.analysis_data.items():
            methodology = data.get("metadata", {}).get("analysis_methodology", "")
            if "cli" in methodology.lower():
                methodologies.append(methodology)

        # Check for consistent CLI integration methodology
        if not methodologies:
            return 0.5  # No CLI methodology found

        unique_methodologies = set(methodologies)
        consistency_score = 0.9 if len(unique_methodologies) <= 2 else 0.7

        return consistency_score

    # Helper methods for quality assessment and recommendations
    def _generate_quality_assessment(self) -> dict[str, Any]:
        """Generate overall quality assessment"""
        cross_analysis_score = self.cross_analysis_score

        quality_level = (
            "EXCELLENT"
            if cross_analysis_score >= 0.95
            else (
                "GOOD"
                if cross_analysis_score >= 0.9
                else ("ACCEPTABLE" if cross_analysis_score >= 0.8 else "NEEDS_IMPROVEMENT")
            )
        )

        return {
            "overall_quality_level": quality_level,
            "cross_analysis_score": cross_analysis_score,
            "target_achievement": cross_analysis_score >= 0.9,
            "institutional_ready": cross_analysis_score >= 0.9,
            "critical_issues": len([i for i in self.detected_issues if i["severity"] == "high"]),
            "areas_of_strength": self._identify_strengths(),
            "areas_for_improvement": self._identify_improvement_areas(),
        }

    def _generate_recommendations(self) -> list[dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []

        # Based on cross-analysis score
        if self.cross_analysis_score < 0.9:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "overall_quality",
                    "recommendation": "Improve overall cross-analysis consistency to achieve target score of 9.0+",
                    "actions": [
                        "Review and align structural consistency across all analysis files",
                        "Eliminate hardcoded values and template artifacts",
                        "Enhance region-specific content and analysis",
                    ],
                }
            )

        # Based on detected issues
        high_priority_issues = [i for i in self.detected_issues if i["severity"] == "high"]
        if high_priority_issues:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "critical_issues",
                    "recommendation": "Address critical issues identified in cross-analysis validation",
                    "actions": [issue["recommendation"] for issue in high_priority_issues],
                }
            )

        # CLI services recommendations
        cli_validation = self.validate_cli_services_integration()
        if cli_validation.get("overall_cli_integration_score", 0) < 0.8:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "cli_services",
                    "recommendation": "Improve CLI services integration consistency",
                    "actions": [
                        "Standardize CLI service usage patterns across all analysis files",
                        "Ensure consistent data source alignment",
                        "Validate service-specific indicators for accuracy",
                    ],
                }
            )

        return recommendations

    def _identify_strengths(self) -> list[str]:
        """Identify strengths in the cross-analysis"""
        strengths = []

        structural = self.validate_structural_consistency()
        if structural.get("overall_structural_score", 0) >= 0.9:
            strengths.append("Excellent structural consistency across analysis files")

        region_spec = self.validate_region_specificity()
        if region_spec.get("overall_region_specificity_score", 0) >= 0.9:
            strengths.append("Strong region-specific content and analysis")

        cli_integration = self.validate_cli_services_integration()
        if cli_integration.get("overall_cli_integration_score", 0) >= 0.9:
            strengths.append("Comprehensive CLI services integration")

        if len(self.analysis_files) >= 5:
            strengths.append("Comprehensive cross-analysis coverage with multiple files")

        return strengths

    def _identify_improvement_areas(self) -> list[str]:
        """Identify areas for improvement"""
        improvements = []

        magic_values = self.detect_hardcoded_magic_values()
        if magic_values.get("overall_magic_value_score", 0) < 0.8:
            improvements.append("Reduce hardcoded values and implement dynamic calculations")

        structural = self.validate_structural_consistency()
        if structural.get("schema_consistency", 0) < 0.8:
            improvements.append("Improve schema consistency across analysis files")

        region_spec = self.validate_region_specificity()
        if region_spec.get("template_generalization_detection"):
            improvements.append("Reduce generic template usage and enhance region specificity")

        return improvements

    def _generate_file_specific_analysis(self) -> dict[str, Any]:
        """Generate file-specific analysis details"""
        file_analysis = {}

        for filename, data in self.analysis_data.items():
            file_analysis[filename] = {
                "metadata_quality": self._assess_file_metadata_quality(data),
                "section_completeness": self._assess_file_completeness(data),
                "region_specificity": self._assess_file_region_specificity(data),
                "confidence_scores": self._extract_file_confidence_scores(data),
                "issues_identified": self._identify_file_specific_issues(filename, data),
            }

        return file_analysis

    def _generate_cross_file_comparison(self) -> dict[str, Any]:
        """Generate cross-file comparison analysis"""
        if len(self.analysis_data) < 2:
            return {"comparison": "insufficient_files_for_comparison"}

        comparison = {
            "files_compared": len(self.analysis_data),
            "common_sections": self._find_common_sections(),
            "unique_sections": self._find_unique_sections(),
            "confidence_score_variance": self._calculate_confidence_variance(),
            "methodology_consistency": self._assess_methodology_consistency(),
            "cross_regional_insights": self._extract_cross_regional_insights(),
        }

        return comparison

    def _calculate_validation_confidence(self) -> float:
        """Calculate validation confidence score"""
        factors = [
            self.cross_analysis_score,
            1.0 - (len(self.detected_issues) * 0.1),  # Penalty for issues
            min(len(self.analysis_files) / 5, 1.0),  # Reward for more files
        ]

        return max(np.mean(factors), 0.0)

    # Additional helper methods
    def _assess_file_metadata_quality(self, data: dict[str, Any]) -> float:
        """Assess metadata quality for a specific file"""
        metadata = data.get("metadata", {})
        required_fields = [
            "command_name",
            "execution_timestamp",
            "framework_phase",
            "region",
            "analysis_methodology",
            "confidence_threshold",
        ]

        present_fields = sum(1 for field in required_fields if field in metadata)
        return present_fields / len(required_fields)

    def _assess_file_completeness(self, data: dict[str, Any]) -> float:
        """Assess completeness for a specific file"""
        required_sections = [
            "business_cycle_modeling",
            "liquidity_cycle_positioning",
            "quantified_risk_assessment",
            "enhanced_economic_sensitivity",
            "macroeconomic_risk_scoring",
        ]

        present_sections = sum(1 for section in required_sections if section in data)
        return present_sections / len(required_sections)

    def _assess_file_region_specificity(self, data: dict[str, Any]) -> float:
        """Assess region specificity for a specific file"""
        region = data.get("metadata", {}).get("region", "").lower()
        data_str = json.dumps(data).lower()

        region_mentions = data_str.count(region)
        return min(region_mentions / 5, 1.0)  # Normalize to 0-1 scale

    def _extract_file_confidence_scores(self, data: dict[str, Any]) -> list[float]:
        """Extract confidence scores from a specific file"""
        confidence_scores = []

        # Extract metadata confidence
        metadata_confidence = data.get("metadata", {}).get("confidence_threshold")
        if metadata_confidence is not None:
            try:
                if isinstance(metadata_confidence, (int, float)) or isinstance(metadata_confidence, str):
                    confidence_scores.append(float(metadata_confidence))
            except (ValueError, TypeError):
                pass

        # Extract section-level confidence scores
        for section_data in data.values():
            if isinstance(section_data, dict) and "confidence" in section_data:
                try:
                    confidence_value = section_data["confidence"]
                    if isinstance(confidence_value, (int, float)) or isinstance(confidence_value, str):
                        confidence_scores.append(float(confidence_value))
                except (ValueError, TypeError):
                    pass

        return confidence_scores

    def _identify_file_specific_issues(self, filename: str, data: dict[str, Any]) -> list[str]:
        """Identify issues specific to a file"""
        issues = []

        # Check for missing required sections
        required_sections = ["business_cycle_modeling", "liquidity_cycle_positioning"]
        missing_sections = [section for section in required_sections if section not in data]
        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")

        # Check for low confidence scores
        confidence_scores = self._extract_file_confidence_scores(data)
        if confidence_scores and min(confidence_scores) < 0.8:
            issues.append("Contains confidence scores below 0.8 threshold")

        return issues

    def _find_common_sections(self) -> list[str]:
        """Find sections common across all files"""
        if not self.analysis_data:
            return []

        common_sections = set(next(iter(self.analysis_data.values())).keys())
        for data in self.analysis_data.values():
            common_sections = common_sections.intersection(set(data.keys()))

        return list(common_sections)

    def _find_unique_sections(self) -> dict[str, list[str]]:
        """Find unique sections per file"""
        unique_sections = {}
        all_sections = set()

        # Collect all sections
        for data in self.analysis_data.values():
            all_sections.update(data.keys())

        # Find unique sections per file
        for filename, data in self.analysis_data.items():
            file_sections = set(data.keys())
            unique_to_file = []

            for section in file_sections:
                appears_in_count = sum(1 for other_data in self.analysis_data.values() if section in other_data)
                if appears_in_count == 1:
                    unique_to_file.append(section)

            unique_sections[filename] = unique_to_file

        return unique_sections

    def _calculate_confidence_variance(self) -> float:
        """Calculate variance in confidence scores across files"""
        all_confidence_scores = []

        for data in self.analysis_data.values():
            scores = self._extract_file_confidence_scores(data)
            all_confidence_scores.extend(scores)

        return np.var(all_confidence_scores) if all_confidence_scores else 0.0

    def _assess_methodology_consistency(self) -> float:
        """Assess methodology consistency across files"""
        methodologies = []

        for data in self.analysis_data.values():
            methodology = data.get("metadata", {}).get("analysis_methodology", "")
            methodologies.append(methodology)

        unique_methodologies = set(methodologies)
        return 0.9 if len(unique_methodologies) <= 2 else 0.6

    def _extract_cross_regional_insights(self) -> dict[str, Any]:
        """Extract insights from cross-regional analysis"""
        regions = []
        recession_probs = []

        for data in self.analysis_data.values():
            region = data.get("metadata", {}).get("region", "")
            if region:
                regions.append(region)

            # Extract recession probabilities for comparison
            business_cycle = data.get("business_cycle_modeling", {})
            recession_prob = business_cycle.get("recession_probability")
            if recession_prob:
                if isinstance(recession_prob, str):
                    try:
                        recession_prob = float(recession_prob)
                    except:
                        recession_prob = None
                if recession_prob is not None:
                    recession_probs.append(recession_prob)

        insights = {
            "regions_analyzed": list(set(regions)),
            "recession_probability_range": {
                "min": min(recession_probs) if recession_probs else None,
                "max": max(recession_probs) if recession_probs else None,
                "variance": (np.var(recession_probs) if len(recession_probs) > 1 else None),
            },
            "cross_regional_consistency": len(set(regions)) > 1,
        }

        return insights


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Macro-Economic Analysis Cross-Validation - DASV Phase Cross-Analysis Mode"
    )
    parser.add_argument(
        "--analysis-dir",
        type=str,
        default="./data/outputs/macro_analysis/analysis/",
        help="Directory containing analysis files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./data/outputs/macro_analysis/validation/",
        help="Output directory for validation results",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=7,
        help="Maximum number of files to analyze (default 7)",
    )

    args = parser.parse_args()

    try:
        # Initialize cross-validation
        validator = MacroAnalysisCrossValidation(
            analysis_dir=args.analysis_dir,
            output_dir=args.output_dir,
            max_files=args.max_files,
        )

        print("\n🔍 Starting macro-economic cross-analysis validation")
        print("📁 Analysis directory: {args.analysis_dir}")
        print("📊 Maximum files to analyze: {args.max_files}")

        # Generate validation report
        validation_report = validator.generate_validation_report()

        # Save validation output
        output_path = validator.save_validation_output(validation_report)

        # Display results
        cross_analysis_score = validation_report["cross_analysis_summary"]["overall_cross_analysis_score"]
        validation_status = validation_report["cross_analysis_summary"]["validation_status"]
        critical_issues = validation_report["cross_analysis_summary"]["critical_issues_count"]

        print("\n✅ Cross-analysis validation complete!")
        print("📊 Cross-Analysis Score: {cross_analysis_score:.3f}/1.0")
        print(f"🎯 Target Achievement: {'✅ PASS' if cross_analysis_score >= 0.9 else '❌ REVIEW REQUIRED'}")
        print("🏆 Validation Status: {validation_status}")
        print("⚠️  Critical Issues: {critical_issues}")
        print("📁 Validation report saved to: {output_path}")

        # Display critical findings if any
        if validation_report["detected_issues"]:
            print("\n🚨 Issues Detected:")
            for issue in validation_report["detected_issues"]:
                severity_icon = "🔴" if issue["severity"] == "high" else "🟡" if issue["severity"] == "medium" else "🟢"
                print("  {severity_icon} {issue['category']}: {issue['finding']}")

        # Display recommendations
        if validation_report["recommendations"]:
            print("\n💡 Key Recommendations:")
            for rec in validation_report["recommendations"]:
                priority_icon = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
                print("  {priority_icon} {rec['recommendation']}")

    except Exception:
        print("❌ Cross-validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
