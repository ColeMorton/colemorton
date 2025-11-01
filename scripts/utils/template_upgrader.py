#!/usr/bin/env python3
"""
Template Upgrade Tool

Automated tool for upgrading existing Jinja2 templates to use standardized patterns.
Provides analysis, backup, upgrade, and validation capabilities to ensure
safe and consistent template standardization.
"""

import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.template_consistency_optimizer import TemplateConsistencyOptimizer


@dataclass
class TemplateUpgradePlan:
    """Upgrade plan for a single template"""

    source_path: str
    target_path: str
    template_domain: str
    template_type: str
    upgrades_required: list[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high
    backup_path: str | None = None
    upgrade_status: str = "pending"  # pending, in_progress, completed, failed


@dataclass
class UpgradeReport:
    """Overall template upgrade report"""

    timestamp: datetime
    total_templates: int
    templates_upgraded: int
    templates_failed: int
    templates_skipped: int
    upgrade_plans: list[TemplateUpgradePlan] = field(default_factory=list)
    validation_results: dict[str, Any] = field(default_factory=dict)
    rollback_available: bool = False
    backup_directory: str | None = None


class TemplateUpgrader:
    """
    Automated template upgrade tool for standardizing DASV templates.

    Features:
    - Analyzes existing templates against standards
    - Creates upgrade plans with risk assessment
    - Backs up original templates before upgrade
    - Applies standardized patterns and structure
    - Validates upgraded templates
    - Provides rollback capability
    """

    def __init__(self, templates_dir: str = None, standardized_dir: str = None):
        """Initialize the template upgrader"""
        if templates_dir is None:
            templates_dir = project_root / "scripts" / "templates"
        if standardized_dir is None:
            standardized_dir = project_root / "scripts" / "standardized_templates"

        self.templates_dir = Path(templates_dir)
        self.standardized_dir = Path(standardized_dir)
        self.backup_dir = self.templates_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize template optimizer for standards
        self.template_optimizer = TemplateConsistencyOptimizer()

        # Define standard patterns to enforce
        self.standard_patterns = {
            "base_template_extends": "{% extends 'shared/base_analysis_template.j2' %}",
            "standard_imports": [
                "{% import 'shared/macros/confidence_scoring_macro.j2' as confidence %}",
                "{% import 'shared/macros/data_quality_macro.j2' as quality %}",
                "{% import 'shared/macros/risk_assessment_macro.j2' as risk %}",
            ],
            "metadata_block": """{% block metadata %}
## {{ metadata.command_name }} - {{ metadata.framework_phase|title }} Phase
**Execution**: {{ metadata.execution_timestamp|strftime('%Y-%m-%d %H:%M:%S') }}
**Domain**: {{ metadata.domain_identifier }}
**Confidence**: {{ metadata.confidence_level|round(2) if metadata.confidence_level else 'N/A' }}
{% endblock %}""",
            "formatting_patterns": {
                "confidence": r"{{ (\w+)\.confidence_score\|round\(2\) }}",
                "currency": r"{{ (\w+)\|currency }}",
                "percentage": r"{{ (\w+)\|percentage }}",
                "date": r'{{ (\w+)\|strftime\([\'"]%Y-%m-%d[\'\"]\) }}',
            },
        }

        # Define upgrade rules
        self.upgrade_rules = {
            "add_base_template": {
                "pattern": r"^(?!{% extends)",
                "risk": "medium",
                "description": "Add base template inheritance",
            },
            "standardize_imports": {
                "pattern": r"{% import .* %}",
                "risk": "low",
                "description": "Standardize macro imports",
            },
            "add_metadata_block": {
                "pattern": r"metadata\.",
                "risk": "medium",
                "description": "Add standardized metadata block",
            },
            "fix_confidence_formatting": {
                "pattern": r"confidence[_\w]*\s*[:=]\s*\d",
                "risk": "low",
                "description": "Standardize confidence score formatting",
            },
            "standardize_variable_names": {
                "pattern": r"{{ [^}]+ }}",
                "risk": "medium",
                "description": "Standardize variable naming conventions",
            },
        }

    def analyze_template(self, template_path: Path) -> TemplateUpgradePlan:
        """Analyze a template and create upgrade plan"""
        try:
            with open(template_path) as f:
                content = f.read()
        except Exception as e:
            return TemplateUpgradePlan(
                source_path=str(template_path),
                target_path=str(template_path),
                template_domain="unknown",
                template_type="unknown",
                upgrades_required=[f"Failed to load template: {e}"],
                risk_level="high",
                upgrade_status="failed",
            )

        # Analyze template using optimizer
        analysis = self.template_optimizer.analyze_template_file(template_path)

        # Create upgrade plan
        plan = TemplateUpgradePlan(
            source_path=str(template_path),
            target_path=str(template_path),
            template_domain=analysis.domain,
            template_type=analysis.template_type,
            upgrades_required=[],
            risk_level="low",
        )

        # Check for required upgrades
        self._check_base_template(content, plan)
        self._check_imports(content, plan)
        self._check_metadata_structure(content, plan)
        self._check_formatting_patterns(content, plan)
        self._check_block_structure(content, plan)

        # Add upgrades from consistency analysis
        if analysis.inconsistencies:
            for inconsistency in analysis.inconsistencies:
                if "metadata" in inconsistency.lower():
                    plan.upgrades_required.append(f"Fix: {inconsistency}")
                    plan.risk_level = "medium"

        # Determine overall risk level
        if len(plan.upgrades_required) > 5:
            plan.risk_level = "high"
        elif len(plan.upgrades_required) > 2:
            plan.risk_level = "medium"

        return plan

    def _check_base_template(self, content: str, plan: TemplateUpgradePlan):
        """Check if template extends base template"""
        if plan.template_type in ["analysis", "synthesis", "validation"]:
            if not re.search(r'{% extends [\'"].*base.*\.j2[\'"] %}', content):
                plan.upgrades_required.append("Add base template inheritance")
                plan.risk_level = "medium"

    def _check_imports(self, content: str, plan: TemplateUpgradePlan):
        """Check for standard macro imports"""
        required_imports = {
            "confidence_scoring_macro": "confidence",
            "data_quality_macro": "quality",
        }

        for macro_file, alias in required_imports.items():
            if macro_file not in content:
                plan.upgrades_required.append(f"Add import for {macro_file}")

    def _check_metadata_structure(self, content: str, plan: TemplateUpgradePlan):
        """Check metadata block structure"""
        if "metadata" in content:
            # Check for proper metadata block
            if not re.search(r"{% block metadata %}", content):
                plan.upgrades_required.append("Wrap metadata in proper block structure")

            # Check metadata fields
            required_fields = [
                "command_name",
                "execution_timestamp",
                "framework_phase",
                "domain_identifier",
            ]
            for field in required_fields:
                if f"metadata.{field}" not in content:
                    plan.upgrades_required.append(f"Add metadata.{field} reference")

    def _check_formatting_patterns(self, content: str, plan: TemplateUpgradePlan):
        """Check for standard formatting patterns"""
        # Check confidence formatting
        confidence_patterns = re.findall(r"confidence[_\w]*\s*[:=]\s*(\d+\.?\d*)", content)
        if confidence_patterns and not re.search(r"\|round\(2\)", content):
            plan.upgrades_required.append("Add proper confidence score formatting with round(2)")

        # Check date formatting
        date_patterns = re.findall(r"(timestamp|date)[_\w]*\s*[:=]", content)
        if date_patterns and not re.search(r"\|strftime", content):
            plan.upgrades_required.append("Add proper date formatting with strftime")

    def _check_block_structure(self, content: str, plan: TemplateUpgradePlan):
        """Check for proper block structure"""
        expected_blocks = {
            "analysis": [
                "executive_summary",
                "key_findings",
                "detailed_analysis",
                "investment_recommendation",
            ],
            "discovery": [
                "data_summary",
                "key_metrics",
                "cli_validation",
                "data_quality_assessment",
            ],
            "synthesis": [
                "investment_thesis",
                "portfolio_allocation",
                "risk_profile",
                "action_items",
            ],
            "validation": [
                "validation_summary",
                "quality_certification",
                "audit_trail",
                "confidence_assessment",
            ],
        }

        if plan.template_type in expected_blocks:
            for block_name in expected_blocks[plan.template_type]:
                if f"block {block_name}" not in content:
                    plan.upgrades_required.append(f"Add {block_name} block")

    def create_backup(self, template_path: Path) -> str | None:
        """Create backup of template before upgrade"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Preserve directory structure in backup
            relative_path = template_path.relative_to(self.templates_dir)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(template_path, backup_path)
            return str(backup_path)
        except Exception:
            print("Failed to backup {template_path}: {e}")
            return None

    def upgrade_template(self, plan: TemplateUpgradePlan, dry_run: bool = True) -> bool:
        """Upgrade a single template according to plan"""
        if plan.upgrade_status == "failed":
            return False

        try:
            # Load current template
            with open(plan.source_path) as f:
                content = f.read()

            # Apply upgrades
            upgraded_content = self._apply_upgrades(content, plan)

            if not dry_run:
                # Create backup
                backup_path = self.create_backup(Path(plan.source_path))
                plan.backup_path = backup_path

                if backup_path:
                    # Write upgraded template
                    with open(plan.target_path, "w") as f:
                        f.write(upgraded_content)

                    plan.upgrade_status = "completed"
                    return True
                plan.upgrade_status = "failed"
                return False
            # Dry run - just validate
            plan.upgrade_status = "validated"
            return True

        except Exception:
            print("Upgrade failed for {plan.source_path}: {e}")
            plan.upgrade_status = "failed"
            return False

    def _apply_upgrades(self, content: str, plan: TemplateUpgradePlan) -> str:
        """Apply upgrades to template content"""
        upgraded = content

        # Add base template if needed
        if "Add base template inheritance" in plan.upgrades_required:
            if plan.template_type in ["analysis", "synthesis", "validation"]:
                upgraded = self.standard_patterns["base_template_extends"] + "\n\n" + upgraded

        # Add standard imports
        imports_to_add = []
        for upgrade in plan.upgrades_required:
            if "Add import for" in upgrade:
                for std_import in self.standard_patterns["standard_imports"]:
                    if upgrade.split()[-1].replace("_macro", "") in std_import:
                        imports_to_add.append(std_import)

        if imports_to_add:
            # Find position after extends or at beginning
            extends_match = re.search(r"({% extends [^%]+ %})", upgraded)
            if extends_match:
                insert_pos = extends_match.end()
                upgraded = upgraded[:insert_pos] + "\n\n" + "\n".join(imports_to_add) + upgraded[insert_pos:]
            else:
                upgraded = "\n".join(imports_to_add) + "\n\n" + upgraded

        # Add metadata block if needed
        if "Wrap metadata in proper block structure" in plan.upgrades_required:
            # Find existing metadata usage
            metadata_match = re.search(r"(## .*metadata.*)", upgraded, re.IGNORECASE)
            if metadata_match:
                # Replace with standard block
                upgraded = upgraded.replace(metadata_match.group(0), self.standard_patterns["metadata_block"])

        # Standardize confidence formatting
        if "Add proper confidence score formatting" in plan.upgrades_required:
            # Find confidence patterns
            upgraded = re.sub(
                r"(confidence[_\w]*)\s*[:=]\s*(\d+\.?\d*)",
                r"{{ \1|round(2) }}",
                upgraded,
            )

        # Standardize date formatting
        if "Add proper date formatting" in plan.upgrades_required:
            # Find date/timestamp patterns
            upgraded = re.sub(
                r"(timestamp|date)[_\w]*\s*[:=]\s*([^}\n]+)",
                r'{{ \1|strftime("%Y-%m-%d %H:%M:%S") }}',
                upgraded,
            )

        # Add missing blocks
        blocks_to_add = [u for u in plan.upgrades_required if u.startswith("Add") and "block" in u]
        if blocks_to_add:
            for block_upgrade in blocks_to_add:
                block_name = block_upgrade.split()[-2]  # Extract block name
                block_content = f"\n{{% block {block_name} %}}\n## {block_name.replace('_', ' ').title()}\n{{# Content for {block_name} #}}\n{{% endblock %}}\n"

                # Add at end of template
                upgraded += block_content

        return upgraded

    def validate_upgrade(self, original_path: str, upgraded_path: str) -> dict[str, Any]:
        """Validate upgraded template"""
        try:
            with open(original_path) as f:
                original = f.read()

            with open(upgraded_path) as f:
                upgraded = f.read()

            # Check content preservation
            content_preserved = self._check_content_preservation(original, upgraded)

            # Check standard compliance
            standard_compliant = self._check_upgrade_compliance(upgraded)

            # Calculate validation score
            validation_score = (content_preserved["score"] + standard_compliant["score"]) / 2

            return {
                "valid": validation_score >= 0.7,
                "score": validation_score,
                "content_preservation": content_preserved,
                "standard_compliance": standard_compliant,
            }

        except Exception as e:
            return {"valid": False, "score": 0.0, "error": str(e)}

    def _check_content_preservation(self, original: str, upgraded: str) -> dict[str, Any]:
        """Check if original content is preserved in upgrade"""
        # Extract key content patterns
        original_vars = set(re.findall(r"{{ ([^}]+) }}", original))
        upgraded_vars = set(re.findall(r"{{ ([^}]+) }}", upgraded))

        # Check variable preservation (ignoring formatting)
        original_var_names = {v.split("|")[0].strip() for v in original_vars}
        upgraded_var_names = {v.split("|")[0].strip() for v in upgraded_vars}

        preserved = original_var_names.intersection(upgraded_var_names)
        lost = original_var_names - upgraded_var_names

        preservation_rate = len(preserved) / len(original_var_names) if original_var_names else 1.0

        return {
            "score": preservation_rate,
            "preserved_variables": len(preserved),
            "lost_variables": list(lost),
            "preservation_rate": preservation_rate,
        }

    def _check_upgrade_compliance(self, content: str) -> dict[str, Any]:
        """Check compliance with upgrade standards"""
        issues = []
        score = 1.0

        # Check base template
        if not re.search(r'{% extends [\'"].*base.*\.j2[\'"] %}', content):
            if any(keyword in content.lower() for keyword in ["analysis", "synthesis", "validation"]):
                issues.append("Missing base template inheritance")
                score -= 0.2

        # Check imports
        required_imports = ["confidence_scoring_macro", "data_quality_macro"]
        for import_name in required_imports:
            if import_name not in content:
                issues.append(f"Missing import: {import_name}")
                score -= 0.1

        # Check metadata block
        if "metadata" in content and not re.search(r"{% block metadata %}", content):
            issues.append("Metadata not in proper block")
            score -= 0.15

        # Check formatting
        if re.search(r"confidence[_\w]*\s*[:=]\s*\d", content):
            if not re.search(r"\|round\(2\)", content):
                issues.append("Unformatted confidence scores")
                score -= 0.1

        return {
            "score": max(0.0, score),
            "compliant": len(issues) == 0,
            "issues": issues,
        }

    def upgrade_all_templates(self, dry_run: bool = True, pattern: str = "*.j2") -> UpgradeReport:
        """Upgrade all templates in directory"""
        print(f"{'🔍' if dry_run else '🔧'} Template Upgrade {'(DRY RUN)' if dry_run else '(APPLYING UPGRADES)'}")
        print("=" * 70)

        report = UpgradeReport(
            timestamp=datetime.now(),
            total_templates=0,
            templates_upgraded=0,
            templates_failed=0,
            templates_skipped=0,
            rollback_available=not dry_run,
            backup_directory=str(self.backup_dir) if not dry_run else None,
        )

        # Process all templates
        for template_file in self.templates_dir.rglob(pattern):
            # Skip standardized templates and backups
            if "standard" in template_file.name or "backup" in str(template_file):
                continue

            report.total_templates += 1

            # Create upgrade plan
            plan = self.analyze_template(template_file)
            report.upgrade_plans.append(plan)

            # Skip if no upgrades required
            if not plan.upgrades_required:
                report.templates_skipped += 1
                print(f"  ✓ {template_file.relative_to(self.templates_dir)} - No upgrades needed")
                continue

            # Upgrade template
            print(
                f"  {'🔍' if dry_run else '🔧'} {template_file.relative_to(self.templates_dir)} - {len(plan.upgrades_required)} upgrades"
            )

            if self.upgrade_template(plan, dry_run=dry_run):
                report.templates_upgraded += 1

                # Validate if not dry run
                if not dry_run:
                    validation = self.validate_upgrade(plan.source_path, plan.target_path)
                    report.validation_results[template_file.name] = validation

                    if validation["valid"]:
                        print(f"    ✅ Upgrade successful (score: {validation['score']:.2f})")
                    else:
                        print("    ⚠️  Upgrade completed with warnings")
            else:
                report.templates_failed += 1
                print("    ❌ Upgrade failed")

        return report

    def rollback_upgrades(self, report: UpgradeReport) -> bool:
        """Rollback upgrades using backups"""
        if not report.rollback_available or not report.backup_directory:
            print("❌ No rollback available")
            return False

        print("🔄 Rolling back template upgrades...")

        backup_dir = Path(report.backup_directory)
        if not backup_dir.exists():
            print("❌ Backup directory not found")
            return False

        success_count = 0
        for plan in report.upgrade_plans:
            if plan.backup_path and Path(plan.backup_path).exists():
                try:
                    shutil.copy2(plan.backup_path, plan.target_path)
                    success_count += 1
                    print("  ✅ Restored {Path(plan.target_path).name}")
                except Exception:
                    print("  ❌ Failed to restore {Path(plan.target_path).name}: {e}")

        print(f"✅ Rollback complete: {success_count}/{len(report.upgrade_plans)} templates restored")
        return success_count > 0

    def print_report(self, report: UpgradeReport):
        """Print detailed upgrade report"""
        print("\n" + "=" * 70)
        print("TEMPLATE UPGRADE REPORT")
        print("=" * 70)
        print("📅 Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("📁 Total templates: {report.total_templates}")
        print("✅ Upgraded: {report.templates_upgraded}")
        print("⏭️  Skipped: {report.templates_skipped}")
        print("❌ Failed: {report.templates_failed}")

        if report.backup_directory:
            print("💾 Backup directory: {report.backup_directory}")

        # Risk summary
        risk_summary = {"low": 0, "medium": 0, "high": 0}
        for plan in report.upgrade_plans:
            risk_summary[plan.risk_level] += 1

        print("\n📊 Risk Assessment:")
        print("  Low risk: {risk_summary['low']}")
        print("  Medium risk: {risk_summary['medium']}")
        print("  High risk: {risk_summary['high']}")

        # Validation summary
        if report.validation_results:
            print("\n✅ Validation Results:")
            total_score = 0
            for template, validation in report.validation_results.items():
                if "score" in validation:
                    total_score += validation["score"]
                    status = "✅" if validation["valid"] else "⚠️"
                    print("  {status} {template}: {validation['score']:.2f}")

            avg_score = total_score / len(report.validation_results) if report.validation_results else 0
            print("  Average validation score: {avg_score:.2f}")

        # Common upgrades
        upgrade_frequency = {}
        for plan in report.upgrade_plans:
            for upgrade in plan.upgrades_required:
                upgrade_type = upgrade.split(":")[0] if ":" in upgrade else upgrade
                upgrade_frequency[upgrade_type] = upgrade_frequency.get(upgrade_type, 0) + 1

        if upgrade_frequency:
            print("\n📋 Most Common Upgrades:")
            for upgrade_type, count in sorted(upgrade_frequency.items(), key=lambda x: x[1], reverse=True)[:5]:
                print("  {upgrade_type}: {count} templates")


def main():
    """CLI interface for template upgrade"""
    import argparse

    parser = argparse.ArgumentParser(description="Template Upgrade Tool")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze templates and create upgrade plan",
    )
    parser.add_argument("--upgrade", action="store_true", help="Apply template upgrades")
    parser.add_argument("--rollback", help="Rollback upgrades using report JSON")
    parser.add_argument("--templates-dir", help="Templates directory path")
    parser.add_argument("--pattern", default="*.j2", help="File pattern to process (default: *.j2)")
    parser.add_argument("--export", help="Export upgrade report to JSON")

    args = parser.parse_args()

    # Initialize upgrader
    upgrader = TemplateUpgrader(args.templates_dir)

    if args.analyze:
        # Analyze mode (dry run)
        report = upgrader.upgrade_all_templates(dry_run=True, pattern=args.pattern)
        upgrader.print_report(report)

        if args.export:
            # Export report
            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            export_path = Path(args.export) if args.export else f"template_upgrade_report_{timestamp}.json"

            report_data = {
                "timestamp": report.timestamp.isoformat(),
                "total_templates": report.total_templates,
                "templates_upgraded": report.templates_upgraded,
                "templates_failed": report.templates_failed,
                "templates_skipped": report.templates_skipped,
                "upgrade_plans": [
                    {
                        "source_path": plan.source_path,
                        "target_path": plan.target_path,
                        "template_domain": plan.template_domain,
                        "template_type": plan.template_type,
                        "upgrades_required": plan.upgrades_required,
                        "risk_level": plan.risk_level,
                        "upgrade_status": plan.upgrade_status,
                    }
                    for plan in report.upgrade_plans
                ],
            }

            with open(export_path, "w") as f:
                import json

                json.dump(report_data, f, indent=2)

            print("\n📄 Report exported to: {export_path}")

    elif args.upgrade:
        # Apply upgrades
        report = upgrader.upgrade_all_templates(dry_run=False, pattern=args.pattern)
        upgrader.print_report(report)

        if report.templates_failed > 0:
            print(f"\n⚠️  {report.templates_failed} upgrades failed. Rollback available.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
