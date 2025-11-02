#!/usr/bin/env python3
"""
Template Consistency Optimizer

Analyzes, standardizes, and validates Jinja2 templates across all DASV domains
to ensure maximum consistency in output formatting, content structure,
and presentation quality.
"""

import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class TemplateAnalysis:
    """Analysis results for a single template"""

    file_path: str
    domain: str
    template_type: str
    template_content: str
    variables_used: set[str] = field(default_factory=set)
    macro_imports: set[str] = field(default_factory=set)
    conditional_blocks: list[str] = field(default_factory=list)
    loop_blocks: list[str] = field(default_factory=list)
    includes_extends: list[str] = field(default_factory=list)
    content_sections: list[str] = field(default_factory=list)
    quality_indicators: list[str] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)


@dataclass
class TemplateConsistencyReport:
    """Overall template consistency analysis report"""

    total_templates: int
    domains_analyzed: list[str]
    template_types: list[str]
    common_variables: dict[str, int] = field(default_factory=dict)
    common_macros: dict[str, int] = field(default_factory=dict)
    inconsistencies: dict[str, list[str]] = field(default_factory=dict)
    standardization_opportunities: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    recommendations: list[str] = field(default_factory=list)


class TemplateConsistencyOptimizer:
    """
    Comprehensive template consistency optimizer for DASV framework.

    Analyzes all Jinja2 templates across domains to identify:
    - Common patterns and inconsistencies
    - Standardization opportunities
    - Macro usage and organization
    - Content structure standardization
    """

    def __init__(self, templates_dir: str = None):
        """Initialize the template optimizer"""
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"

        self.templates_dir = Path(templates_dir)
        self.template_analyses = []

        # Standard template patterns expected across all templates
        self.standard_patterns = {
            "metadata_variables": {
                "required": [
                    "metadata",
                    "command_name",
                    "execution_timestamp",
                    "framework_phase",
                ],
                "recommended": [
                    "domain_identifier",
                    "confidence_level",
                    "data_quality_score",
                ],
            },
            "content_structure": {
                "analysis_templates": [
                    "executive_summary",
                    "key_findings",
                    "detailed_analysis",
                    "investment_recommendation",
                    "risk_assessment",
                ],
                "discovery_templates": [
                    "data_summary",
                    "key_metrics",
                    "cli_validation",
                    "data_quality_assessment",
                ],
                "synthesis_templates": [
                    "investment_thesis",
                    "portfolio_allocation",
                    "risk_profile",
                    "action_items",
                    "monitoring_framework",
                ],
                "validation_templates": [
                    "validation_summary",
                    "quality_certification",
                    "audit_trail",
                    "confidence_assessment",
                ],
            },
            "macro_imports": {
                "confidence_scoring": "confidence_scoring_macro.j2",
                "data_quality": "data_quality_macro.j2",
                "risk_assessment": "risk_assessment_macro.j2",
                "valuation_framework": "valuation_framework_macro.j2",
            },
            "formatting_standards": {
                "confidence_format": r"{{ confidence_.*\|round\(2\) }}",
                "currency_format": r"{{ .*\|currency }}",
                "percentage_format": r"{{ .*\|percentage }}",
                "date_format": r"{{ .*\|strftime\(.*\) }}",
            },
        }

        # Template type classification patterns
        self.template_types = {
            "analysis": ["_analysis", "_enhanced"],
            "discovery": ["_discovery"],
            "synthesis": ["_synthesis", "_blog"],
            "validation": ["_validation"],
            "twitter": ["twitter_", "_tweet"],
            "shared": ["base_", "macro", "component"],
        }

    def analyze_template_file(self, file_path: Path) -> TemplateAnalysis:
        """Analyze a single template file for consistency patterns"""
        try:
            with open(file_path) as f:
                template_content = f.read()
        except Exception as e:
            return TemplateAnalysis(
                file_path=str(file_path),
                domain="unknown",
                template_type="unknown",
                template_content="",
                inconsistencies=[f"Failed to load template: {e}"],
            )

        # Parse domain and type from filename and path
        filename = file_path.stem
        relative_path = file_path.relative_to(self.templates_dir)

        # Extract domain and template type
        domain = self._extract_domain(filename, relative_path)
        template_type = self._classify_template_type(filename, relative_path)

        analysis = TemplateAnalysis(
            file_path=str(file_path),
            domain=domain,
            template_type=template_type,
            template_content=template_content,
        )

        # Analyze template structure
        self._analyze_template_structure(template_content, analysis)

        # Check for standard patterns
        self._check_standard_patterns(template_content, analysis)

        # Validate template type requirements
        self._validate_template_requirements(template_content, analysis)

        return analysis

    def _extract_domain(self, filename: str, relative_path: Path) -> str:
        """Extract domain from filename and path"""
        # Check path components
        path_parts = list(relative_path.parts)

        # Look for domain indicators in path
        for part in path_parts:
            if any(
                domain in part
                for domain in [
                    "fundamental",
                    "sector",
                    "industry",
                    "comparative",
                    "macro",
                    "trade",
                ]
            ):
                if "fundamental" in part:
                    return "fundamental_analysis"
                if "sector" in part:
                    return "sector_analysis"
                if "industry" in part:
                    return "industry_analysis"
                if "comparative" in part:
                    return "comparative_analysis"
                if "macro" in part:
                    return "macro_analysis"
                if "trade" in part:
                    return "trade_history"

        # Check filename
        if "fundamental" in filename:
            return "fundamental_analysis"
        if "sector" in filename:
            return "sector_analysis"
        if "industry" in filename:
            return "industry_analysis"
        if "comparative" in filename:
            return "comparative_analysis"
        if "macro" in filename:
            return "macro_analysis"
        if "trade" in filename:
            return "trade_history"
        if "twitter" in filename or "twitter" in str(relative_path):
            return "twitter_content"
        if "shared" in str(relative_path) or "base_" in filename:
            return "shared"

        return "unknown"

    def _classify_template_type(self, filename: str, relative_path: Path) -> str:
        """Classify template type based on filename and path"""
        full_path = str(relative_path).lower()
        filename_lower = filename.lower()

        # Check specific patterns
        for template_type, patterns in self.template_types.items():
            for pattern in patterns:
                if pattern in filename_lower or pattern in full_path:
                    return template_type

        # Check by directory structure
        if "twitter" in full_path:
            return "twitter"
        if "shared" in full_path or "macros" in full_path:
            return "shared"
        if "validation" in full_path:
            return "validation"
        if "blog" in filename_lower:
            return "synthesis"
        if "enhanced" in filename_lower:
            return "analysis"

        return "unknown"

    def _analyze_template_structure(self, content: str, analysis: TemplateAnalysis):
        """Analyze the structure of a template"""
        # Extract variables used
        variable_pattern = r"{{\s*([^}]+)\s*}}"
        variables = re.findall(variable_pattern, content)
        analysis.variables_used = set(var.split("|")[0].split(".")[0].strip() for var in variables)

        # Extract macro imports
        import_pattern = r'{%\s*import\s+["\']([^"\']+)["\']'
        imports = re.findall(import_pattern, content)
        analysis.macro_imports = set(imports)

        # Extract conditional blocks
        if_pattern = r"{%\s*if\s+([^%]+)\s*%}"
        conditionals = re.findall(if_pattern, content)
        analysis.conditional_blocks = conditionals

        # Extract loop blocks
        for_pattern = r"{%\s*for\s+([^%]+)\s*%}"
        loops = re.findall(for_pattern, content)
        analysis.loop_blocks = loops

        # Extract includes/extends
        include_pattern = r'{%\s*(?:include|extends)\s+["\']([^"\']+)["\']'
        includes = re.findall(include_pattern, content)
        analysis.includes_extends = includes

        # Identify content sections (headers and major blocks)
        header_patterns = [
            r"#+\s*([^\n]+)",  # Markdown headers
            r"<h[1-6][^>]*>([^<]+)</h[1-6]>",  # HTML headers
            r"## ([^\n]+)",  # Section markers
        ]

        sections = []
        for pattern in header_patterns:
            sections.extend(re.findall(pattern, content, re.IGNORECASE))
        analysis.content_sections = sections

        # Look for quality indicators
        quality_keywords = [
            "confidence",
            "quality",
            "validation",
            "assessment",
            "score",
        ]
        for keyword in quality_keywords:
            if keyword in content.lower():
                analysis.quality_indicators.append(keyword)

    def _check_standard_patterns(self, content: str, analysis: TemplateAnalysis):
        """Check template against standard patterns"""
        # Check metadata variables
        required_metadata = self.standard_patterns["metadata_variables"]["required"]
        missing_metadata = []
        for var in required_metadata:
            if var not in analysis.variables_used:
                missing_metadata.append(var)

        if missing_metadata:
            analysis.inconsistencies.append(f"Missing required metadata variables: {', '.join(missing_metadata)}")

        # Check macro imports for domain-specific templates
        if analysis.template_type in ["analysis", "synthesis", "validation"]:
            expected_macros = ["confidence_scoring_macro.j2", "data_quality_macro.j2"]
            missing_macros = []
            for macro in expected_macros:
                if not any(macro in imp for imp in analysis.macro_imports):
                    missing_macros.append(macro)

            if missing_macros:
                analysis.inconsistencies.append(f"Missing recommended macro imports: {', '.join(missing_macros)}")

        # Check formatting standards
        format_patterns = self.standard_patterns["formatting_standards"]
        for format_type, pattern in format_patterns.items():
            if format_type.split("_")[0] in content.lower():
                if not re.search(pattern, content):
                    analysis.inconsistencies.append(f"Inconsistent {format_type} usage")

    def _validate_template_requirements(self, content: str, analysis: TemplateAnalysis):
        """Validate template against type-specific requirements"""
        template_type = analysis.template_type

        if template_type in self.standard_patterns["content_structure"]:
            required_sections = self.standard_patterns["content_structure"][f"{template_type}_templates"]
            missing_sections = []

            for section in required_sections:
                # Check if section is present (case-insensitive)
                if not re.search(section.replace("_", "[-_\\s]*"), content, re.IGNORECASE):
                    missing_sections.append(section)

            if missing_sections:
                analysis.inconsistencies.append(
                    f"Missing recommended {template_type} sections: {', '.join(missing_sections)}"
                )

    def analyze_all_templates(self) -> TemplateConsistencyReport:
        """Analyze all templates for consistency"""
        if not self.templates_dir.exists():
            return TemplateConsistencyReport(
                total_templates=0,
                domains_analyzed=[],
                template_types=[],
                inconsistencies={"system": ["Templates directory not found"]},
            )

        print("🔍 Analyzing templates in {self.templates_dir}")

        # Analyze each template file
        self.template_analyses = []
        for template_file in self.templates_dir.rglob("*.j2"):
            analysis = self.analyze_template_file(template_file)
            self.template_analyses.append(analysis)
            print(f"  📋 Analyzed: {template_file.name} ({analysis.domain}:{analysis.template_type})")

        # Generate consistency report
        return self._generate_consistency_report()

    def _generate_consistency_report(self) -> TemplateConsistencyReport:
        """Generate comprehensive consistency report"""
        report = TemplateConsistencyReport(
            total_templates=len(self.template_analyses),
            domains_analyzed=list(set(a.domain for a in self.template_analyses if a.domain != "unknown")),
            template_types=list(set(a.template_type for a in self.template_analyses if a.template_type != "unknown")),
        )

        # Analyze common patterns
        variable_frequency = defaultdict(int)
        macro_frequency = defaultdict(int)

        for analysis in self.template_analyses:
            # Count variable usage
            for var in analysis.variables_used:
                variable_frequency[var] += 1

            # Count macro usage
            for macro in analysis.macro_imports:
                macro_frequency[macro] += 1

        report.common_variables = dict(variable_frequency)
        report.common_macros = dict(macro_frequency)

        # Collect inconsistencies by template
        for analysis in self.template_analyses:
            if analysis.inconsistencies:
                key = f"{analysis.domain}:{analysis.template_type}"
                report.inconsistencies[key] = analysis.inconsistencies

        # Generate standardization opportunities
        report.standardization_opportunities = self._identify_standardization_opportunities()

        # Calculate quality score
        report.quality_score = self._calculate_quality_score()

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _identify_standardization_opportunities(self) -> list[str]:
        """Identify opportunities for template standardization"""
        opportunities = []

        # Check for missing base template usage
        templates_without_base = [
            a for a in self.template_analyses if not any("base_" in inc for inc in a.includes_extends)
        ]
        if len(templates_without_base) > 5:
            opportunities.append(f"Standardize base template usage across {len(templates_without_base)} templates")

        # Check for macro consistency
        all_macros = set()
        for analysis in self.template_analyses:
            all_macros.update(analysis.macro_imports)

        if len(all_macros) > 10:  # Too many different macros
            opportunities.append("Consolidate and standardize macro imports")

        # Check for variable naming consistency
        variable_patterns = defaultdict(set)
        for analysis in self.template_analyses:
            for var in analysis.variables_used:
                # Group by pattern
                if "confidence" in var.lower():
                    variable_patterns["confidence"].add(var)
                elif "quality" in var.lower():
                    variable_patterns["quality"].add(var)
                elif "metadata" in var.lower():
                    variable_patterns["metadata"].add(var)

        for pattern_type, vars_set in variable_patterns.items():
            if len(vars_set) > 3:  # Too many variations
                opportunities.append(f"Standardize {pattern_type} variable naming patterns")

        # Check for template type standardization
        template_types = set(a.template_type for a in self.template_analyses if a.template_type != "unknown")
        for template_type in template_types:
            type_templates = [a for a in self.template_analyses if a.template_type == template_type]
            if len(type_templates) > 1:
                # Check consistency within type
                variable_sets = [a.variables_used for a in type_templates]
                if len(set(tuple(sorted(s)) for s in variable_sets)) > 1:  # Different variable sets
                    opportunities.append(f"Standardize {template_type} template variable usage across domains")

        return opportunities

    def _calculate_quality_score(self) -> float:
        """Calculate overall template quality score"""
        if not self.template_analyses:
            return 0.0

        total_score = 0.0

        for analysis in self.template_analyses:
            template_score = 1.0

            # Penalize for inconsistencies
            template_score -= len(analysis.inconsistencies) * 0.15

            # Reward for standard patterns
            if any("base_" in inc for inc in analysis.includes_extends):
                template_score += 0.1

            if analysis.macro_imports:
                template_score += 0.1

            if analysis.quality_indicators:
                template_score += 0.1

            if len(analysis.content_sections) >= 3:
                template_score += 0.1

            # Ensure score doesn't go below 0
            template_score = max(0.0, template_score)
            total_score += template_score

        return total_score / len(self.template_analyses)

    def _generate_recommendations(self, report: TemplateConsistencyReport) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # High-level recommendations
        if report.quality_score < 0.7:
            recommendations.append("🔴 PRIORITY: Address major template inconsistencies to improve quality score")

        if len(report.inconsistencies) > len(report.domains_analyzed):
            recommendations.append("🟡 Standardize common template patterns across domains")

        # Specific recommendations based on analysis
        base_template_usage = sum(
            1 for a in self.template_analyses if any("base_" in inc for inc in a.includes_extends)
        )
        if base_template_usage < len(self.template_analyses) * 0.6:
            recommendations.append("🟢 Increase base template usage for consistency")

        macro_usage = sum(1 for a in self.template_analyses if a.macro_imports)
        if macro_usage < len(self.template_analyses) * 0.8:
            recommendations.append("🟢 Add macro imports to all domain templates")

        # Domain-specific recommendations
        domains = set(a.domain for a in self.template_analyses if a.domain != "unknown")
        for domain in domains:
            domain_analyses = [a for a in self.template_analyses if a.domain == domain]
            domain_inconsistencies = sum(len(a.inconsistencies) for a in domain_analyses)

            if domain_inconsistencies > 3:
                recommendations.append(f"🔵 Focus on {domain} domain - high inconsistency count")

        return recommendations

    def generate_standardized_template(self, template_type: str, domain: str = None) -> str:
        """Generate a standardized template for a specific type and domain"""
        # Base template structure
        template_parts = [
            "{% extends 'shared/base_analysis_template.j2' %}",
            "",
            "{% import 'shared/macros/confidence_scoring_macro.j2' as confidence %}",
            "{% import 'shared/macros/data_quality_macro.j2' as quality %}",
            "",
            "{% block metadata %}",
            "## {{ metadata.command_name }} - {{ metadata.framework_phase|title }} Phase",
            "**Execution**: {{ metadata.execution_timestamp|strftime('%Y-%m-%d %H:%M:%S') }}",
            "**Domain**: {{ metadata.domain_identifier }}",
            "**Confidence**: {{ metadata.confidence_level|round(2) if metadata.confidence_level else 'N/A' }}",
            "{% endblock %}",
            "",
        ]

        # Add type-specific content blocks
        if template_type == "analysis":
            template_parts.extend(
                [
                    "{% block executive_summary %}",
                    "## Executive Summary",
                    "{{ executive_summary if executive_summary else 'Executive summary not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block key_findings %}",
                    "## Key Findings",
                    "{% for finding in key_findings %}",
                    "- {{ finding }}",
                    "{% endfor %}",
                    "{% endblock %}",
                    "",
                    "{% block detailed_analysis %}",
                    "## Detailed Analysis",
                    "{{ detailed_analysis if detailed_analysis else 'Detailed analysis not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block investment_recommendation %}",
                    "## Investment Recommendation",
                    "{{ investment_recommendation if investment_recommendation else 'Investment recommendation not available.' }}",
                    "",
                    "**Confidence Score**: {{ confidence.render_score(analysis_confidence_score) }}",
                    "{% endblock %}",
                ]
            )

        elif template_type == "discovery":
            template_parts.extend(
                [
                    "{% block data_summary %}",
                    "## Data Summary",
                    "{{ data_summary if data_summary else 'Data summary not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block key_metrics %}",
                    "## Key Metrics",
                    "{% for metric in key_metrics %}",
                    "- **{{ metric.name }}**: {{ metric.value }}",
                    "{% endfor %}",
                    "{% endblock %}",
                    "",
                    "{% block cli_validation %}",
                    "## CLI Service Validation",
                    "{{ quality.render_cli_validation(cli_service_integration) }}",
                    "{% endblock %}",
                    "",
                    "{% block data_quality_assessment %}",
                    "## Data Quality Assessment",
                    "{{ quality.render_quality_assessment(data_quality_assessment) }}",
                    "{% endblock %}",
                ]
            )

        elif template_type == "synthesis":
            template_parts.extend(
                [
                    "{% block investment_thesis %}",
                    "## Investment Thesis",
                    "{{ investment_thesis if investment_thesis else 'Investment thesis not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block portfolio_allocation %}",
                    "## Portfolio Allocation",
                    "{{ portfolio_allocation if portfolio_allocation else 'Portfolio allocation not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block risk_profile %}",
                    "## Risk Profile",
                    "{{ risk_profile if risk_profile else 'Risk profile not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block action_items %}",
                    "## Action Items",
                    "{% for item in action_items %}",
                    "- {{ item }}",
                    "{% endfor %}",
                    "{% endblock %}",
                ]
            )

        elif template_type == "validation":
            template_parts.extend(
                [
                    "{% block validation_summary %}",
                    "## Validation Summary",
                    "{{ validation_summary if validation_summary else 'Validation summary not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block quality_certification %}",
                    "## Quality Certification",
                    "{{ quality.render_certification(quality_certification) }}",
                    "{% endblock %}",
                    "",
                    "{% block audit_trail %}",
                    "## Audit Trail",
                    "{{ audit_trail if audit_trail else 'Audit trail not available.' }}",
                    "{% endblock %}",
                    "",
                    "{% block confidence_assessment %}",
                    "## Confidence Assessment",
                    "{{ confidence.render_assessment(confidence_assessment) }}",
                    "{% endblock %}",
                ]
            )

        return "\n".join(template_parts)

    def export_standardized_templates(self, output_dir: str = None) -> list[str]:
        """Export standardized template files for all types"""
        if output_dir is None:
            output_dir = self.templates_dir.parent / "standardized_templates"

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        exported_files = []

        template_types = ["discovery", "analysis", "synthesis", "validation"]
        domains = [
            "fundamental_analysis",
            "sector_analysis",
            "industry_analysis",
            "comparative_analysis",
            "macro_analysis",
            "trade_history",
        ]

        for template_type in template_types:
            for domain in domains:
                template_content = self.generate_standardized_template(template_type, domain)

                output_file = output_path / f"{domain}_{template_type}_standard.j2"
                with open(output_file, "w") as f:
                    f.write(template_content)

                exported_files.append(str(output_file))
                print("  📄 Exported: {output_file.name}")

        return exported_files

    def print_consistency_report(self, report: TemplateConsistencyReport):
        """Print detailed consistency report"""
        print("\n" + "=" * 60)
        print("TEMPLATE CONSISTENCY ANALYSIS REPORT")
        print("=" * 60)

        print("📊 Analysis Summary:")
        print("  Total templates analyzed: {report.total_templates}")
        print("  Domains covered: {', '.join(report.domains_analyzed)}")
        print("  Template types: {', '.join(report.template_types)}")
        print("  Overall quality score: {report.quality_score:.2f}/1.0")

        if report.common_variables:
            print("\n🔧 Most Common Variables:")
            sorted_variables = sorted(report.common_variables.items(), key=lambda x: x[1], reverse=True)
            for variable, count in sorted_variables[:10]:
                print("  {variable}: {count} templates")

        if report.common_macros:
            print("\n🧩 Most Common Macros:")
            sorted_macros = sorted(report.common_macros.items(), key=lambda x: x[1], reverse=True)
            for macro, count in sorted_macros:
                print("  {macro}: {count} templates")

        if report.inconsistencies:
            print(f"\n⚠️  Inconsistencies Found ({len(report.inconsistencies)} templates):")
            for template, issues in report.inconsistencies.items():
                print("  {template}:")
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
    """CLI interface for template consistency optimization"""
    import argparse

    parser = argparse.ArgumentParser(description="Template Consistency Optimizer")
    parser.add_argument("--templates-dir", help="Directory containing templates")
    parser.add_argument("--analyze", action="store_true", help="Analyze template consistency")
    parser.add_argument(
        "--export-templates",
        action="store_true",
        help="Export standardized template files",
    )
    parser.add_argument("--output-dir", help="Output directory for exported templates")

    args = parser.parse_args()

    # Initialize optimizer
    optimizer = TemplateConsistencyOptimizer(args.templates_dir)

    if args.analyze:
        # Analyze templates
        report = optimizer.analyze_all_templates()
        optimizer.print_consistency_report(report)

    if args.export_templates:
        # Export standardized templates
        print("\n📤 Exporting standardized template files...")
        exported_files = optimizer.export_standardized_templates(args.output_dir)
        print("✅ Exported {len(exported_files)} standardized template files")


if __name__ == "__main__":
    main()
