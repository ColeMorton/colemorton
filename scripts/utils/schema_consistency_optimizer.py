#!/usr/bin/env python3
"""
Schema Consistency Optimizer

Analyzes, standardizes, and validates JSON schemas across all DASV domains
to ensure maximum consistency in data structures, validation patterns,
and quality standards.
"""

import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class SchemaAnalysis:
    """Analysis results for a single schema"""

    file_path: str
    domain: str
    phase: str
    schema_content: dict[str, Any]
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    field_types: dict[str, str] = field(default_factory=dict)
    confidence_patterns: list[str] = field(default_factory=list)
    validation_patterns: list[str] = field(default_factory=list)
    quality_indicators: list[str] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)


@dataclass
class ConsistencyReport:
    """Overall consistency analysis report"""

    total_schemas: int
    domains_analyzed: list[str]
    common_patterns: dict[str, int] = field(default_factory=dict)
    inconsistencies: dict[str, list[str]] = field(default_factory=dict)
    standardization_opportunities: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    recommendations: list[str] = field(default_factory=list)


class SchemaConsistencyOptimizer:
    """
    Comprehensive schema consistency optimizer for DASV framework.

    Analyzes all schemas across domains to identify:
    - Common patterns and inconsistencies
    - Standardization opportunities
    - Quality improvement areas
    - Validation framework enhancements
    """

    def __init__(self, schemas_dir: str = None):
        """Initialize the schema optimizer"""
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent.parent / "schemas"

        self.schemas_dir = Path(schemas_dir)
        self.schema_analyses = []

        # Standard field patterns expected across all schemas
        self.standard_patterns = {
            "metadata": {
                "required_fields": [
                    "command_name",
                    "execution_timestamp",
                    "framework_phase",
                ],
                "field_types": {
                    "command_name": "string",
                    "execution_timestamp": "string",
                    "framework_phase": "string",
                },
            },
            "confidence_scoring": {
                "patterns": [
                    "confidence_score",
                    "confidence_level",
                    "data_quality_score",
                    "overall_confidence",
                    "validation_confidence",
                ],
                "format": "number between 0.0 and 1.0",
            },
            "cli_integration": {
                "patterns": [
                    "cli_services_utilized",
                    "api_health_status",
                    "data_sources",
                    "service_responses",
                    "cli_validation",
                ]
            },
            "validation": {
                "patterns": [
                    "validation_status",
                    "validation_errors",
                    "quality_gates",
                    "validation_timestamp",
                    "validation_methodology",
                ]
            },
        }

        # DASV phase requirements
        self.phase_requirements = {
            "discovery": {
                "required_sections": [
                    "metadata",
                    "discovery_results",
                    "data_collection",
                    "quality_assessment",
                    "cli_service_integration",
                ],
                "quality_indicators": [
                    "data_completeness_score",
                    "source_reliability_score",
                    "data_freshness_score",
                ],
            },
            "analysis": {
                "required_sections": [
                    "metadata",
                    "analytical_results",
                    "quantitative_analysis",
                    "qualitative_assessment",
                    "confidence_scoring",
                ],
                "quality_indicators": [
                    "analysis_confidence_score",
                    "calculation_accuracy_score",
                    "methodology_consistency_score",
                ],
            },
            "synthesis": {
                "required_sections": [
                    "metadata",
                    "synthesis_output",
                    "template_compliance",
                    "quality_certification",
                    "investment_summary",
                ],
                "quality_indicators": [
                    "synthesis_confidence_score",
                    "template_compliance_score",
                    "presentation_quality_score",
                ],
            },
            "validation": {
                "required_sections": [
                    "metadata",
                    "validation_results",
                    "quality_assessment",
                    "decision_confidence",
                    "audit_trail",
                ],
                "quality_indicators": [
                    "overall_reliability_score",
                    "validation_confidence_score",
                    "institutional_quality_certified",
                ],
            },
        }

    def analyze_schema_file(self, file_path: Path) -> SchemaAnalysis:
        """Analyze a single schema file for consistency patterns"""
        try:
            with open(file_path) as f:
                schema_content = json.load(f)
        except Exception as e:
            return SchemaAnalysis(
                file_path=str(file_path),
                domain="unknown",
                phase="unknown",
                schema_content={},
                inconsistencies=[f"Failed to load schema: {e}"],
            )

        # Parse domain and phase from filename
        filename = file_path.stem
        parts = filename.split("_")

        # Extract domain and phase
        domain = "unknown"
        phase = "unknown"

        if len(parts) >= 3:
            if parts[-1] == "schema":
                # Format: domain_analysis_phase_schema.json
                domain = "_".join(parts[:-2])
                phase = parts[-2]
            else:
                # Format: domain_phase_schema.json
                domain = "_".join(parts[:-2])
                phase = parts[-2]

        analysis = SchemaAnalysis(
            file_path=str(file_path),
            domain=domain,
            phase=phase,
            schema_content=schema_content,
        )

        # Analyze schema structure
        self._analyze_schema_structure(schema_content, analysis)

        # Check for standard patterns
        self._check_standard_patterns(schema_content, analysis)

        # Validate phase requirements
        self._validate_phase_requirements(schema_content, analysis)

        return analysis

    def _analyze_schema_structure(self, schema: dict[str, Any], analysis: SchemaAnalysis):
        """Analyze the structure of a schema"""
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        analysis.required_fields = required
        analysis.optional_fields = [k for k in properties.keys() if k not in required]

        # Analyze field types
        for field_name, field_def in properties.items():
            field_type = field_def.get("type", "unknown")
            analysis.field_types[field_name] = field_type

            # Look for confidence-related fields
            if "confidence" in field_name.lower() or "score" in field_name.lower():
                analysis.confidence_patterns.append(field_name)

            # Look for validation-related fields
            if "validation" in field_name.lower() or "quality" in field_name.lower():
                analysis.validation_patterns.append(field_name)

            # Look for quality indicators
            if any(
                indicator in field_name.lower() for indicator in ["quality", "accuracy", "reliability", "completeness"]
            ):
                analysis.quality_indicators.append(field_name)

    def _check_standard_patterns(self, schema: dict[str, Any], analysis: SchemaAnalysis):
        """Check schema against standard patterns"""
        properties = schema.get("properties", {})

        # Check metadata section
        if "metadata" not in properties:
            analysis.inconsistencies.append("Missing standard 'metadata' section")
        else:
            metadata_props = properties["metadata"].get("properties", {})
            for required_field in self.standard_patterns["metadata"]["required_fields"]:
                if required_field not in metadata_props:
                    analysis.inconsistencies.append(f"Missing required metadata field: {required_field}")

        # Check confidence scoring patterns
        confidence_fields = [f for f in properties.keys() if "confidence" in f.lower()]
        if not confidence_fields:
            analysis.inconsistencies.append("No confidence scoring fields found")

        # Check CLI integration patterns
        cli_fields = [
            f for f in properties.keys() if any(pattern in f.lower() for pattern in ["cli", "service", "api"])
        ]
        if not cli_fields:
            analysis.inconsistencies.append("No CLI integration fields found")

    def _validate_phase_requirements(self, schema: dict[str, Any], analysis: SchemaAnalysis):
        """Validate schema against phase-specific requirements"""
        if analysis.phase not in self.phase_requirements:
            return

        properties = schema.get("properties", {})
        requirements = self.phase_requirements[analysis.phase]

        # Check required sections
        for section in requirements["required_sections"]:
            if section not in properties:
                analysis.inconsistencies.append(f"Missing required {analysis.phase} section: {section}")

        # Check quality indicators
        quality_indicators = requirements["quality_indicators"]
        found_indicators = [f for f in properties.keys() if any(indicator in f for indicator in quality_indicators)]

        if len(found_indicators) < len(quality_indicators) / 2:  # At least half should be present
            analysis.inconsistencies.append(f"Insufficient quality indicators for {analysis.phase} phase")

    def analyze_all_schemas(self) -> ConsistencyReport:
        """Analyze all schemas for consistency"""
        if not self.schemas_dir.exists():
            return ConsistencyReport(
                total_schemas=0,
                domains_analyzed=[],
                inconsistencies={"system": ["Schemas directory not found"]},
            )

        print("🔍 Analyzing schemas in {self.schemas_dir}")

        # Analyze each schema file
        self.schema_analyses = []
        for schema_file in self.schemas_dir.glob("*.json"):
            analysis = self.analyze_schema_file(schema_file)
            self.schema_analyses.append(analysis)
            print(f"  📋 Analyzed: {schema_file.name} ({analysis.domain}:{analysis.phase})")

        # Generate consistency report
        return self._generate_consistency_report()

    def _generate_consistency_report(self) -> ConsistencyReport:
        """Generate comprehensive consistency report"""
        report = ConsistencyReport(
            total_schemas=len(self.schema_analyses),
            domains_analyzed=list(set(a.domain for a in self.schema_analyses if a.domain != "unknown")),
        )

        # Analyze common patterns
        field_frequency = defaultdict(int)
        pattern_frequency = defaultdict(int)

        for analysis in self.schema_analyses:
            # Count field usage
            for field in analysis.required_fields + analysis.optional_fields:
                field_frequency[field] += 1

            # Count confidence patterns
            for pattern in analysis.confidence_patterns:
                pattern_frequency[f"confidence:{pattern}"] += 1

            # Count validation patterns
            for pattern in analysis.validation_patterns:
                pattern_frequency[f"validation:{pattern}"] += 1

        report.common_patterns = dict(field_frequency)

        # Collect inconsistencies by category
        for analysis in self.schema_analyses:
            if analysis.inconsistencies:
                key = f"{analysis.domain}:{analysis.phase}"
                report.inconsistencies[key] = analysis.inconsistencies

        # Generate standardization opportunities
        report.standardization_opportunities = self._identify_standardization_opportunities()

        # Calculate quality score
        report.quality_score = self._calculate_quality_score()

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _identify_standardization_opportunities(self) -> list[str]:
        """Identify opportunities for schema standardization"""
        opportunities = []

        # Check for missing metadata consistency
        schemas_without_metadata = [
            a for a in self.schema_analyses if "metadata" not in a.schema_content.get("properties", {})
        ]
        if schemas_without_metadata:
            opportunities.append(f"Standardize metadata section across {len(schemas_without_metadata)} schemas")

        # Check for confidence scoring consistency
        confidence_patterns = set()
        for analysis in self.schema_analyses:
            confidence_patterns.update(analysis.confidence_patterns)

        if len(confidence_patterns) > 5:  # Too many different patterns
            opportunities.append("Standardize confidence scoring field names")

        # Check for CLI integration consistency
        cli_patterns = []
        for analysis in self.schema_analyses:
            schema_props = analysis.schema_content.get("properties", {})
            cli_fields = [
                f for f in schema_props.keys() if any(term in f.lower() for term in ["cli", "service", "api"])
            ]
            cli_patterns.extend(cli_fields)

        unique_cli_patterns = set(cli_patterns)
        if len(unique_cli_patterns) > 10:  # Too fragmented
            opportunities.append("Consolidate CLI integration field patterns")

        # Check for phase-specific standardization
        phases = set(a.phase for a in self.schema_analyses if a.phase != "unknown")
        for phase in phases:
            phase_schemas = [a for a in self.schema_analyses if a.phase == phase]
            if len(phase_schemas) > 1:
                # Check consistency within phase
                required_fields_sets = [set(a.required_fields) for a in phase_schemas]
                if len(set(tuple(s) for s in required_fields_sets)) > 1:  # Different required fields
                    opportunities.append(f"Standardize {phase} phase required fields across domains")

        return opportunities

    def _calculate_quality_score(self) -> float:
        """Calculate overall schema quality score"""
        if not self.schema_analyses:
            return 0.0

        total_score = 0.0

        for analysis in self.schema_analyses:
            schema_score = 1.0

            # Penalize for inconsistencies
            schema_score -= len(analysis.inconsistencies) * 0.1

            # Reward for standard patterns
            if "metadata" in analysis.schema_content.get("properties", {}):
                schema_score += 0.1

            if analysis.confidence_patterns:
                schema_score += 0.1

            if analysis.validation_patterns:
                schema_score += 0.1

            # Ensure score doesn't go below 0
            schema_score = max(0.0, schema_score)
            total_score += schema_score

        return total_score / len(self.schema_analyses)

    def _generate_recommendations(self, report: ConsistencyReport) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # High-level recommendations
        if report.quality_score < 0.8:
            recommendations.append("🔴 PRIORITY: Address major schema inconsistencies to improve quality score")

        if len(report.inconsistencies) > len(report.domains_analyzed):
            recommendations.append("🟡 Standardize common schema patterns across domains")

        # Specific recommendations based on analysis
        confidence_schemas = sum(1 for a in self.schema_analyses if a.confidence_patterns)
        if confidence_schemas < len(self.schema_analyses) * 0.8:
            recommendations.append("🟢 Add confidence scoring fields to all schemas")

        validation_schemas = sum(1 for a in self.schema_analyses if a.validation_patterns)
        if validation_schemas < len(self.schema_analyses) * 0.8:
            recommendations.append("🟢 Add validation tracking fields to all schemas")

        # Domain-specific recommendations
        domains = set(a.domain for a in self.schema_analyses if a.domain != "unknown")
        for domain in domains:
            domain_analyses = [a for a in self.schema_analyses if a.domain == domain]
            domain_inconsistencies = sum(len(a.inconsistencies) for a in domain_analyses)

            if domain_inconsistencies > 5:
                recommendations.append(f"🔵 Focus on {domain} domain - high inconsistency count")

        return recommendations

    def generate_standardized_schema_template(self, phase: str) -> dict[str, Any]:
        """Generate a standardized schema template for a specific phase"""
        # Base schema structure
        template = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"DASV {phase.capitalize()} Phase Schema",
            "description": f"Standardized schema for {phase} phase across all DASV domains",
            "type": "object",
            "required": ["metadata"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "required": [
                        "command_name",
                        "execution_timestamp",
                        "framework_phase",
                        "domain_identifier",
                    ],
                    "properties": {
                        "command_name": {
                            "type": "string",
                            "description": "Full command name (e.g., 'fundamental_analyst_discover')",
                        },
                        "execution_timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "ISO 8601 timestamp of execution",
                        },
                        "framework_phase": {
                            "type": "string",
                            "enum": ["discover", "analyze", "synthesize", "validate"],
                            "description": "DASV framework phase",
                        },
                        "domain_identifier": {
                            "type": "string",
                            "description": "Analysis domain (e.g., ticker, sector, industry, region)",
                        },
                        "confidence_level": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Overall confidence score for this phase",
                        },
                    },
                }
            },
        }

        # Add phase-specific sections
        if phase in self.phase_requirements:
            requirements = self.phase_requirements[phase]

            # Add required sections
            for section in requirements["required_sections"]:
                if section not in template["properties"]:
                    template["properties"][section] = {
                        "type": "object",
                        "description": f"Standard {section} section for {phase} phase",
                    }

                    if section not in template["required"]:
                        template["required"].append(section)

            # Add quality indicators
            quality_section = template["properties"].get("quality_assessment", {})
            if "properties" not in quality_section:
                quality_section["properties"] = {}

            for indicator in requirements["quality_indicators"]:
                quality_section["properties"][indicator] = {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": f"Quality indicator: {indicator}",
                }

        # Add CLI integration section
        template["properties"]["cli_service_integration"] = {
            "type": "object",
            "properties": {
                "services_utilized": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of CLI services successfully utilized",
                },
                "service_health_status": {
                    "type": "object",
                    "description": "Health status of each CLI service",
                },
                "data_quality_scores": {
                    "type": "object",
                    "description": "Quality scores from each data source",
                },
                "multi_source_consistency": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Consistency score across multiple data sources",
                },
            },
        }

        return template

    def export_standardized_schemas(self, output_dir: str = None) -> list[str]:
        """Export standardized schema templates for all phases"""
        if output_dir is None:
            output_dir = self.schemas_dir.parent / "standardized_schemas"

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        exported_files = []

        phases = ["discover", "analyze", "synthesize", "validate"]
        for phase in phases:
            template = self.generate_standardized_schema_template(phase)

            output_file = output_path / f"dasv_{phase}_standard_schema.json"
            with open(output_file, "w") as f:
                json.dump(template, f, indent=2)

            exported_files.append(str(output_file))
            print("  📄 Exported: {output_file.name}")

        return exported_files

    def print_consistency_report(self, report: ConsistencyReport):
        """Print detailed consistency report"""
        print("\n" + "=" * 60)
        print("SCHEMA CONSISTENCY ANALYSIS REPORT")
        print("=" * 60)

        print("📊 Analysis Summary:")
        print("  Total schemas analyzed: {report.total_schemas}")
        print("  Domains covered: {', '.join(report.domains_analyzed)}")
        print("  Overall quality score: {report.quality_score:.2f}/1.0")

        if report.common_patterns:
            print("\n🔧 Most Common Field Patterns:")
            sorted_patterns = sorted(report.common_patterns.items(), key=lambda x: x[1], reverse=True)
            for pattern, count in sorted_patterns[:10]:
                print("  {pattern}: {count} schemas")

        if report.inconsistencies:
            print(f"\n⚠️  Inconsistencies Found ({len(report.inconsistencies)} schemas):")
            for schema, issues in report.inconsistencies.items():
                print("  {schema}:")
                for issue in issues[:3]:  # Show first 3 issues
                    print("    • {issue}")
                if len(issues) > 3:
                    print("    • ... and {len(issues) - 3} more")

        if report.standardization_opportunities:
            print("\n🎯 Standardization Opportunities:")
            for i, opportunity in enumerate(report.standardization_opportunities, 1):
                print("  {i}. {opportunity}")

        if report.recommendations:
            print("\n📋 Recommendations:")
            for rec in report.recommendations:
                print("  {rec}")


def main():
    """CLI interface for schema consistency optimization"""
    import argparse

    parser = argparse.ArgumentParser(description="Schema Consistency Optimizer")
    parser.add_argument("--schemas-dir", help="Directory containing schemas")
    parser.add_argument("--analyze", action="store_true", help="Analyze schema consistency")
    parser.add_argument(
        "--export-templates",
        action="store_true",
        help="Export standardized schema templates",
    )
    parser.add_argument("--output-dir", help="Output directory for exported templates")

    args = parser.parse_args()

    # Initialize optimizer
    optimizer = SchemaConsistencyOptimizer(args.schemas_dir)

    if args.analyze:
        # Analyze schemas
        report = optimizer.analyze_all_schemas()
        optimizer.print_consistency_report(report)

    if args.export_templates:
        # Export standardized templates
        print("\n📤 Exporting standardized schema templates...")
        exported_files = optimizer.export_standardized_schemas(args.output_dir)
        print("✅ Exported {len(exported_files)} standardized schema templates")


if __name__ == "__main__":
    main()
