#!/usr/bin/env python3
"""
Schema Migration Tool

Automated tool for migrating existing schemas to standardized format.
Provides analysis, backup, migration, and validation capabilities
to ensure safe and consistent schema standardization.
"""

import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# Removed deepdiff import - using custom comparison

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.schema_consistency_optimizer import SchemaConsistencyOptimizer


@dataclass
class SchemaMigrationPlan:
    """Migration plan for a single schema"""

    source_path: str
    target_path: str
    schema_domain: str
    schema_phase: str
    changes_required: list[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high
    backup_path: str | None = None
    migration_status: str = "pending"  # pending, in_progress, completed, failed


@dataclass
class MigrationReport:
    """Overall schema migration report"""

    timestamp: datetime
    total_schemas: int
    schemas_migrated: int
    schemas_failed: int
    schemas_skipped: int
    migration_plans: list[SchemaMigrationPlan] = field(default_factory=list)
    validation_results: dict[str, Any] = field(default_factory=dict)
    rollback_available: bool = False
    backup_directory: str | None = None


class SchemaMigrator:
    """
    Automated schema migration tool for standardizing DASV schemas.

    Features:
    - Analyzes existing schemas against standards
    - Creates migration plans with risk assessment
    - Backs up original schemas before migration
    - Applies standardized structure and fields
    - Validates migrated schemas
    - Provides rollback capability
    """

    def __init__(self, schemas_dir: str = None, standardized_dir: str = None):
        """Initialize the schema migrator"""
        if schemas_dir is None:
            schemas_dir = project_root / "scripts" / "schemas"
        if standardized_dir is None:
            standardized_dir = project_root / "scripts" / "standardized_schemas"

        self.schemas_dir = Path(schemas_dir)
        self.standardized_dir = Path(standardized_dir)
        self.backup_dir = self.schemas_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize schema optimizer for standards
        self.schema_optimizer = SchemaConsistencyOptimizer()

        # Define required fields for each phase
        self.phase_requirements = {
            "discover": {
                "required_sections": [
                    "metadata",
                    "discovery_results",
                    "cli_service_integration",
                ],
                "metadata_fields": [
                    "command_name",
                    "execution_timestamp",
                    "framework_phase",
                    "domain_identifier",
                ],
                "quality_fields": [
                    "data_completeness_score",
                    "source_reliability_score",
                    "data_freshness_score",
                ],
            },
            "analyze": {
                "required_sections": [
                    "metadata",
                    "analytical_results",
                    "confidence_scoring",
                ],
                "metadata_fields": [
                    "command_name",
                    "execution_timestamp",
                    "framework_phase",
                    "domain_identifier",
                ],
                "quality_fields": [
                    "analysis_confidence_score",
                    "calculation_accuracy_score",
                    "methodology_consistency_score",
                ],
            },
            "synthesize": {
                "required_sections": [
                    "metadata",
                    "synthesis_output",
                    "quality_certification",
                ],
                "metadata_fields": [
                    "command_name",
                    "execution_timestamp",
                    "framework_phase",
                    "domain_identifier",
                ],
                "quality_fields": [
                    "synthesis_confidence_score",
                    "template_compliance_score",
                    "presentation_quality_score",
                ],
            },
            "validate": {
                "required_sections": [
                    "metadata",
                    "validation_results",
                    "quality_assessment",
                ],
                "metadata_fields": [
                    "command_name",
                    "execution_timestamp",
                    "framework_phase",
                    "domain_identifier",
                ],
                "quality_fields": [
                    "overall_reliability_score",
                    "validation_confidence_score",
                    "institutional_quality_certified",
                ],
            },
        }

    def analyze_schema(self, schema_path: Path) -> SchemaMigrationPlan:
        """Analyze a schema and create migration plan"""
        try:
            with open(schema_path) as f:
                current_schema = json.load(f)
        except Exception as e:
            return SchemaMigrationPlan(
                source_path=str(schema_path),
                target_path=str(schema_path),
                schema_domain="unknown",
                schema_phase="unknown",
                changes_required=[f"Failed to load schema: {e}"],
                risk_level="high",
                migration_status="failed",
            )

        # Parse domain and phase from filename
        filename = schema_path.stem
        domain, phase = self._parse_schema_name(filename)

        # Generate standardized schema
        standardized = self.schema_optimizer.generate_standardized_schema_template(phase)

        # Analyze differences
        changes_required = []
        risk_level = "low"

        # Check structure
        current_properties = current_schema.get("properties", {})
        standard_properties = standardized.get("properties", {})

        # Missing sections
        for section in standard_properties:
            if section not in current_properties:
                changes_required.append(f"Add missing section: {section}")
                risk_level = "medium"

        # Check metadata structure
        if "metadata" in current_properties:
            current_metadata = current_properties["metadata"].get("properties", {})
            standard_metadata = standard_properties["metadata"]["properties"]

            for field in standard_metadata:
                if field not in current_metadata:
                    changes_required.append(f"Add metadata field: {field}")
        else:
            changes_required.append("Add complete metadata section")
            risk_level = "high"

        # Check for deprecated patterns
        if self._has_deprecated_patterns(current_schema):
            changes_required.append("Remove deprecated patterns")
            risk_level = "medium"

        # Create migration plan
        return SchemaMigrationPlan(
            source_path=str(schema_path),
            target_path=str(schema_path),
            schema_domain=domain,
            schema_phase=phase,
            changes_required=changes_required,
            risk_level=risk_level,
            migration_status="pending",
        )

    def _parse_schema_name(self, filename: str) -> tuple[str, str]:
        """Parse domain and phase from schema filename"""
        parts = filename.split("_")

        # Handle different naming patterns
        if "discovery" in filename:
            phase = "discover"
        elif "analysis" in filename:
            phase = "analyze"
        elif "synthesis" in filename:
            phase = "synthesize"
        elif "validation" in filename:
            phase = "validate"
        else:
            phase = "unknown"

        # Extract domain
        domain_map = {
            "fundamental": "fundamental_analysis",
            "sector": "sector_analysis",
            "industry": "industry_analysis",
            "comparative": "comparative_analysis",
            "macro": "macro_analysis",
            "trade": "trade_history",
        }

        domain = "unknown"
        for key, value in domain_map.items():
            if key in filename:
                domain = value
                break

        return domain, phase

    def _has_deprecated_patterns(self, schema: dict[str, Any]) -> bool:
        """Check if schema contains deprecated patterns"""
        deprecated_indicators = [
            "cli_service_validation",  # Old pattern
            "cli_comprehensive_analysis",  # Old pattern
            "data_quality_assessment",  # Should be in quality_assessment section
        ]

        schema_str = json.dumps(schema)
        for pattern in deprecated_indicators:
            if pattern in schema_str:
                return True

        return False

    def create_backup(self, schema_path: Path) -> str | None:
        """Create backup of schema before migration"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.backup_dir / schema_path.name
            shutil.copy2(schema_path, backup_path)
            return str(backup_path)
        except Exception:
            print("Failed to backup {schema_path}: {e}")
            return None

    def migrate_schema(self, plan: SchemaMigrationPlan, dry_run: bool = True) -> bool:
        """Migrate a single schema according to plan"""
        if plan.migration_status == "failed":
            return False

        try:
            # Load current schema
            with open(plan.source_path) as f:
                current_schema = json.load(f)

            # Generate standardized template
            standardized = self.schema_optimizer.generate_standardized_schema_template(plan.schema_phase)

            # Merge current data into standardized structure
            migrated_schema = self._merge_schemas(current_schema, standardized, plan)

            # Add domain-specific customizations
            migrated_schema = self._apply_domain_customizations(migrated_schema, plan.schema_domain, plan.schema_phase)

            if not dry_run:
                # Create backup
                backup_path = self.create_backup(Path(plan.source_path))
                plan.backup_path = backup_path

                if backup_path:
                    # Write migrated schema
                    with open(plan.target_path, "w") as f:
                        json.dump(migrated_schema, f, indent=2)

                    plan.migration_status = "completed"
                    return True
                plan.migration_status = "failed"
                return False
            # Dry run - just validate
            plan.migration_status = "validated"
            return True

        except Exception:
            print("Migration failed for {plan.source_path}: {e}")
            plan.migration_status = "failed"
            return False

    def _merge_schemas(
        self,
        current: dict[str, Any],
        standard: dict[str, Any],
        plan: SchemaMigrationPlan,
    ) -> dict[str, Any]:
        """Merge current schema data into standardized structure"""
        # Start with standard structure
        merged = json.loads(json.dumps(standard))  # Deep copy

        # Preserve existing valid data
        current_props = current.get("properties", {})
        merged_props = merged.get("properties", {})

        # Merge properties intelligently
        for prop_name, prop_def in current_props.items():
            if prop_name in merged_props:
                # Merge existing property
                merged_props[prop_name] = self._merge_property(merged_props[prop_name], prop_def, prop_name)
            else:
                # Preserve additional properties if valid
                if self._is_valid_additional_property(prop_name, plan.schema_phase):
                    merged_props[prop_name] = prop_def

        # Update schema metadata
        merged["title"] = f"{plan.schema_domain.replace('_', ' ').title()} - {plan.schema_phase.title()} Schema"
        merged["description"] = current.get("description", merged.get("description", ""))

        # Preserve required fields
        if "required" in current:
            existing_required = set(current["required"])
            standard_required = set(merged.get("required", []))
            merged["required"] = sorted(list(existing_required.union(standard_required)))

        return merged

    def _merge_property(
        self,
        standard_prop: dict[str, Any],
        current_prop: dict[str, Any],
        prop_name: str,
    ) -> dict[str, Any]:
        """Merge a single property definition"""
        merged = json.loads(json.dumps(standard_prop))  # Deep copy

        # Preserve type if compatible
        if current_prop.get("type") == merged.get("type"):
            # Preserve description if more detailed
            if len(current_prop.get("description", "")) > len(merged.get("description", "")):
                merged["description"] = current_prop["description"]

            # For objects, merge properties
            if merged.get("type") == "object":
                current_sub_props = current_prop.get("properties", {})
                merged_sub_props = merged.get("properties", {})

                for sub_prop, sub_def in current_sub_props.items():
                    if sub_prop not in merged_sub_props:
                        merged_sub_props[sub_prop] = sub_def

        return merged

    def _is_valid_additional_property(self, prop_name: str, phase: str) -> bool:
        """Check if additional property should be preserved"""
        # Common valid additional properties
        valid_patterns = [
            "cli_",
            "data_",
            "quality_",
            "confidence_",
            "validation_",
            "assessment_",
            "methodology_",
        ]

        for pattern in valid_patterns:
            if prop_name.startswith(pattern):
                return True

        # Phase-specific properties
        phase_specific = {
            "discover": ["discovery_", "source_", "collection_"],
            "analyze": ["analysis_", "calculation_", "quantitative_"],
            "synthesize": ["synthesis_", "investment_", "portfolio_"],
            "validate": ["validation_", "certification_", "institutional_"],
        }

        if phase in phase_specific:
            for pattern in phase_specific[phase]:
                if prop_name.startswith(pattern):
                    return True

        return False

    def _apply_domain_customizations(self, schema: dict[str, Any], domain: str, phase: str) -> dict[str, Any]:
        """Apply domain-specific customizations to schema"""
        # Domain-specific required fields
        domain_requirements = {
            "fundamental_analysis": {
                "discover": ["ticker", "company_name", "market_cap"],
                "analyze": ["financial_metrics", "valuation_analysis"],
                "synthesize": ["investment_thesis", "price_target"],
                "validate": ["recommendation", "confidence_level"],
            },
            "sector_analysis": {
                "discover": ["sector", "etf_symbol", "constituents"],
                "analyze": ["sector_performance", "industry_breakdown"],
                "synthesize": ["sector_outlook", "allocation_recommendation"],
                "validate": ["sector_validation", "cross_sector_comparison"],
            },
            "industry_analysis": {
                "discover": ["industry", "key_players", "market_size"],
                "analyze": ["competitive_landscape", "growth_drivers"],
                "synthesize": ["industry_thesis", "investment_opportunities"],
                "validate": ["industry_certification", "peer_validation"],
            },
        }

        if domain in domain_requirements and phase in domain_requirements[domain]:
            # Add domain-specific required fields
            props = schema.get("properties", {})

            # Add to appropriate section based on phase
            if phase == "discover" and "discovery_results" in props:
                section = props["discovery_results"].get("properties", {})
                for field in domain_requirements[domain][phase]:
                    if field not in section:
                        section[field] = {
                            "type": "string",
                            "description": f"Domain-specific field: {field}",
                        }

            elif phase == "analyze" and "analytical_results" in props:
                section = props["analytical_results"].get("properties", {})
                for field in domain_requirements[domain][phase]:
                    if field not in section:
                        section[field] = {
                            "type": "object",
                            "description": f"Domain-specific analysis: {field}",
                        }

        return schema

    def validate_migration(self, original_path: str, migrated_path: str) -> dict[str, Any]:
        """Validate migrated schema against original"""
        try:
            with open(original_path) as f:
                original = json.load(f)

            with open(migrated_path) as f:
                migrated = json.load(f)

            # Check data preservation
            data_preserved = self._check_data_preservation(original, migrated)

            # Check standard compliance
            standard_compliant = self._check_standard_compliance(migrated)

            # Calculate validation score
            validation_score = (data_preserved["score"] + standard_compliant["score"]) / 2

            return {
                "valid": validation_score >= 0.8,
                "score": validation_score,
                "data_preservation": data_preserved,
                "standard_compliance": standard_compliant,
            }

        except Exception as e:
            return {"valid": False, "score": 0.0, "error": str(e)}

    def _check_data_preservation(self, original: dict[str, Any], migrated: dict[str, Any]) -> dict[str, Any]:
        """Check if original data is preserved in migration"""
        original_props = set(original.get("properties", {}).keys())
        migrated_props = set(migrated.get("properties", {}).keys())

        # Check property preservation
        preserved = original_props.intersection(migrated_props)
        lost = original_props - migrated_props

        preservation_rate = len(preserved) / len(original_props) if original_props else 1.0

        return {
            "score": preservation_rate,
            "preserved_properties": len(preserved),
            "lost_properties": list(lost),
            "preservation_rate": preservation_rate,
        }

    def _check_standard_compliance(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Check compliance with standards"""
        issues = []
        score = 1.0

        # Check required sections
        properties = schema.get("properties", {})

        # Must have metadata
        if "metadata" not in properties:
            issues.append("Missing metadata section")
            score -= 0.3
        else:
            # Check metadata fields
            metadata_props = properties["metadata"].get("properties", {})
            required_metadata = [
                "command_name",
                "execution_timestamp",
                "framework_phase",
                "domain_identifier",
            ]

            for field in required_metadata:
                if field not in metadata_props:
                    issues.append(f"Missing metadata field: {field}")
                    score -= 0.05

        # Must have CLI integration
        if "cli_service_integration" not in properties:
            issues.append("Missing CLI service integration section")
            score -= 0.2

        # Phase-specific checks
        phase = self._extract_phase_from_schema(schema)
        if phase:
            phase_reqs = self.phase_requirements.get(phase, {})
            for section in phase_reqs.get("required_sections", []):
                if section not in properties:
                    issues.append(f"Missing required {phase} section: {section}")
                    score -= 0.1

        return {
            "score": max(0.0, score),
            "compliant": len(issues) == 0,
            "issues": issues,
        }

    def _extract_phase_from_schema(self, schema: dict[str, Any]) -> str | None:
        """Extract phase from schema content"""
        title = schema.get("title", "").lower()

        if "discover" in title:
            return "discover"
        if "analy" in title:
            return "analyze"
        if "synthe" in title:
            return "synthesize"
        if "validat" in title:
            return "validate"

        return None

    def migrate_all_schemas(self, dry_run: bool = True) -> MigrationReport:
        """Migrate all schemas in directory"""
        print(f"{'🔍' if dry_run else '🔧'} Schema Migration {'(DRY RUN)' if dry_run else '(APPLYING MIGRATIONS)'}")
        print("=" * 70)

        report = MigrationReport(
            timestamp=datetime.now(),
            total_schemas=0,
            schemas_migrated=0,
            schemas_failed=0,
            schemas_skipped=0,
            rollback_available=not dry_run,
            backup_directory=str(self.backup_dir) if not dry_run else None,
        )

        # Analyze all schemas
        for schema_file in self.schemas_dir.glob("*.json"):
            # Skip standardized schemas
            if "standard" in schema_file.name:
                continue

            report.total_schemas += 1

            # Create migration plan
            plan = self.analyze_schema(schema_file)
            report.migration_plans.append(plan)

            # Skip if no changes required
            if not plan.changes_required:
                report.schemas_skipped += 1
                print("  ✓ {schema_file.name} - No migration needed")
                continue

            # Migrate schema
            print(f"  {'🔍' if dry_run else '🔧'} {schema_file.name} - {len(plan.changes_required)} changes")

            if self.migrate_schema(plan, dry_run=dry_run):
                report.schemas_migrated += 1

                # Validate if not dry run
                if not dry_run:
                    validation = self.validate_migration(plan.source_path, plan.target_path)
                    report.validation_results[schema_file.name] = validation

                    if validation["valid"]:
                        print(f"    ✅ Migration successful (score: {validation['score']:.2f})")
                    else:
                        print("    ⚠️  Migration completed with warnings")
            else:
                report.schemas_failed += 1
                print("    ❌ Migration failed")

        return report

    def rollback_migrations(self, report: MigrationReport) -> bool:
        """Rollback migrations using backups"""
        if not report.rollback_available or not report.backup_directory:
            print("❌ No rollback available")
            return False

        print("🔄 Rolling back migrations...")

        backup_dir = Path(report.backup_directory)
        if not backup_dir.exists():
            print("❌ Backup directory not found")
            return False

        success_count = 0
        for plan in report.migration_plans:
            if plan.backup_path and Path(plan.backup_path).exists():
                try:
                    shutil.copy2(plan.backup_path, plan.target_path)
                    success_count += 1
                    print("  ✅ Restored {Path(plan.target_path).name}")
                except Exception:
                    print("  ❌ Failed to restore {Path(plan.target_path).name}: {e}")

        print(f"✅ Rollback complete: {success_count}/{len(report.migration_plans)} schemas restored")
        return success_count > 0

    def print_report(self, report: MigrationReport):
        """Print detailed migration report"""
        print("\n" + "=" * 70)
        print("SCHEMA MIGRATION REPORT")
        print("=" * 70)
        print("📅 Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("📁 Total schemas: {report.total_schemas}")
        print("✅ Migrated: {report.schemas_migrated}")
        print("⏭️  Skipped: {report.schemas_skipped}")
        print("❌ Failed: {report.schemas_failed}")

        if report.backup_directory:
            print("💾 Backup directory: {report.backup_directory}")

        # Risk summary
        risk_summary = {"low": 0, "medium": 0, "high": 0}
        for plan in report.migration_plans:
            risk_summary[plan.risk_level] += 1

        print("\n📊 Risk Assessment:")
        print("  Low risk: {risk_summary['low']}")
        print("  Medium risk: {risk_summary['medium']}")
        print("  High risk: {risk_summary['high']}")

        # Validation summary
        if report.validation_results:
            print("\n✅ Validation Results:")
            total_score = 0
            for schema, validation in report.validation_results.items():
                if "score" in validation:
                    total_score += validation["score"]
                    status = "✅" if validation["valid"] else "⚠️"
                    print("  {status} {schema}: {validation['score']:.2f}")

            avg_score = total_score / len(report.validation_results) if report.validation_results else 0
            print("  Average validation score: {avg_score:.2f}")

        # Detailed plans
        if report.migration_plans:
            print("\n📋 Migration Details:")
            for plan in report.migration_plans:
                if plan.changes_required:
                    print(f"\n  {Path(plan.source_path).name} ({plan.risk_level} risk):")
                    for change in plan.changes_required[:3]:
                        print("    • {change}")
                    if len(plan.changes_required) > 3:
                        print(f"    • ... and {len(plan.changes_required) - 3} more changes")


def main():
    """CLI interface for schema migration"""
    import argparse

    parser = argparse.ArgumentParser(description="Schema Migration Tool")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze schemas and create migration plan",
    )
    parser.add_argument("--migrate", action="store_true", help="Apply schema migrations")
    parser.add_argument("--rollback", help="Rollback migrations using report JSON")
    parser.add_argument("--schemas-dir", help="Schemas directory path")
    parser.add_argument("--export", help="Export migration report to JSON")

    args = parser.parse_args()

    # Initialize migrator
    migrator = SchemaMigrator(args.schemas_dir)

    if args.analyze:
        # Analyze mode (dry run)
        report = migrator.migrate_all_schemas(dry_run=True)
        migrator.print_report(report)

        if args.export:
            # Export report
            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            export_path = Path(args.export) if args.export else f"schema_migration_report_{timestamp}.json"

            report_data = {
                "timestamp": report.timestamp.isoformat(),
                "total_schemas": report.total_schemas,
                "schemas_migrated": report.schemas_migrated,
                "schemas_failed": report.schemas_failed,
                "schemas_skipped": report.schemas_skipped,
                "migration_plans": [
                    {
                        "source_path": plan.source_path,
                        "target_path": plan.target_path,
                        "schema_domain": plan.schema_domain,
                        "schema_phase": plan.schema_phase,
                        "changes_required": plan.changes_required,
                        "risk_level": plan.risk_level,
                        "migration_status": plan.migration_status,
                    }
                    for plan in report.migration_plans
                ],
            }

            with open(export_path, "w") as f:
                json.dump(report_data, f, indent=2)

            print("\n📄 Report exported to: {export_path}")

    elif args.migrate:
        # Apply migrations
        report = migrator.migrate_all_schemas(dry_run=False)
        migrator.print_report(report)

        if report.schemas_failed > 0:
            print(f"\n⚠️  {report.schemas_failed} migrations failed. Rollback available.")

    elif args.rollback:
        # Load report and rollback
        with open(args.rollback) as f:
            report_data = json.load(f)

        # Recreate report object
        report = MigrationReport(
            timestamp=datetime.fromisoformat(report_data["timestamp"]),
            total_schemas=report_data["total_schemas"],
            schemas_migrated=report_data["schemas_migrated"],
            schemas_failed=report_data["schemas_failed"],
            schemas_skipped=report_data["schemas_skipped"],
            rollback_available=True,
            backup_directory=report_data.get("backup_directory"),
        )

        migrator.rollback_migrations(report)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
