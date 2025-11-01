#!/usr/bin/env python3
"""
Automated Path Synchronizer

Maintains path consistency across all command files by automatically detecting
and fixing path reference inconsistencies. Provides both validation and
auto-fix capabilities with dry-run mode for safety.
"""

import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class PathIssue:
    """Represents a path consistency issue"""

    file_path: str
    line_number: int
    issue_type: str  # 'hardcoded', 'incorrect_variable', 'missing_variable'
    original_text: str
    suggested_fix: str
    context: str


@dataclass
class SyncReport:
    """Path synchronization report"""

    timestamp: datetime
    total_files_scanned: int
    files_with_issues: int
    total_issues: int
    issues_fixed: int
    issues_by_type: dict[str, int] = field(default_factory=dict)
    file_issues: dict[str, list[PathIssue]] = field(default_factory=dict)
    validation_passed: bool = False


class PathSynchronizer:
    """
    Automated path synchronizer for maintaining consistency across command files.

    Features:
    - Detects hardcoded paths that should use variables
    - Identifies incorrect variable usage
    - Provides auto-fix capability with backup
    - Dry-run mode for validation
    - Comprehensive reporting
    """

    def __init__(self, commands_dir: str = None, registry_path: str = None):
        """Initialize the path synchronizer"""
        if commands_dir is None:
            commands_dir = project_root / ".claude" / "commands"
        if registry_path is None:
            registry_path = project_root / "scripts" / "command_script_registry.json"

        self.commands_dir = Path(commands_dir)
        self.registry_path = Path(registry_path)

        # Load path variables from registry
        self._load_path_variables()

        # Define path patterns and their correct variables
        self.path_patterns = {
            "scripts/": "{SCRIPTS_BASE}/",
            "./scripts/": "{SCRIPTS_BASE}/",
            "templates/": "{TEMPLATES_BASE}/",
            "./templates/": "{TEMPLATES_BASE}/",
            "data/outputs/": "{DATA_OUTPUTS}/",
            "./data/outputs/": "{DATA_OUTPUTS}/",
            "schemas/": "{SCHEMAS_BASE}/",
            "./schemas/": "{SCHEMAS_BASE}/",
        }

        # Regex patterns for detection
        self.detection_patterns = [
            # Detect hardcoded paths
            (r'(?<!")(?<!{)\b(scripts|templates|schemas|data/outputs)/', "hardcoded"),
            (r"`(scripts|templates|schemas|data/outputs)/", "hardcoded_backtick"),
            (r'"(scripts|templates|schemas|data/outputs)/', "hardcoded_quoted"),
            (r"'(scripts|templates|schemas|data/outputs)/", "hardcoded_single_quoted"),
            # Detect incorrect variable usage
            (r"{SCRIPTS_BASE}/base_{SCRIPTS_BASE}/", "double_variable"),
            (r"{[A-Z_]+}/{[A-Z_]+}/", "adjacent_variables"),
            # Detect mixed patterns
            (r"{SCRIPTS_BASE}/scripts/", "redundant_path"),
            (r"scripts/{SCRIPTS_BASE}/", "inverted_pattern"),
        ]

    def _load_path_variables(self):
        """Load path variables from registry"""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                registry_data = json.load(f)
                self.path_variables = registry_data.get("path_variables", {})
        else:
            # Default path variables
            self.path_variables = {
                "SCRIPTS_BASE": "scripts",
                "TEMPLATES_BASE": "scripts/templates",
                "DATA_OUTPUTS": "data/outputs",
                "SCHEMAS_BASE": "scripts/schemas",
            }

    def scan_file(self, file_path: Path) -> list[PathIssue]:
        """Scan a single file for path issues"""
        issues = []

        try:
            with open(file_path) as f:
                content = f.read()
                lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # Check each detection pattern
                for pattern, issue_type in self.detection_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Generate suggested fix
                        original = match.group(0)
                        suggested = self._generate_fix(original, issue_type)

                        if suggested != original:
                            issues.append(
                                PathIssue(
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    issue_type=issue_type,
                                    original_text=original,
                                    suggested_fix=suggested,
                                    context=line.strip(),
                                )
                            )

            # Additional validation for specific patterns
            issues.extend(self._validate_variable_usage(file_path, content))

        except Exception:
            print("Error scanning {file_path}: {e}")

        return issues

    def _generate_fix(self, original: str, issue_type: str) -> str:
        """Generate suggested fix for a path issue"""
        suggested = original

        if issue_type in [
            "hardcoded",
            "hardcoded_backtick",
            "hardcoded_quoted",
            "hardcoded_single_quoted",
        ]:
            # Replace hardcoded paths with variables
            for pattern, variable in self.path_patterns.items():
                if pattern in original:
                    suggested = original.replace(pattern, variable)
                    break

        elif issue_type == "double_variable":
            # Fix double variable patterns
            suggested = re.sub(r"{SCRIPTS_BASE}/base_{SCRIPTS_BASE}/", "{SCRIPTS_BASE}/", original)

        elif issue_type == "redundant_path":
            # Fix redundant paths
            suggested = re.sub(r"{SCRIPTS_BASE}/scripts/", "{SCRIPTS_BASE}/", original)
            suggested = re.sub(r"{TEMPLATES_BASE}/templates/", "{TEMPLATES_BASE}/", suggested)
            suggested = re.sub(r"{SCHEMAS_BASE}/schemas/", "{SCHEMAS_BASE}/", suggested)

        elif issue_type == "inverted_pattern":
            # Fix inverted patterns
            suggested = re.sub(r"scripts/{SCRIPTS_BASE}/", "{SCRIPTS_BASE}/", original)
            suggested = re.sub(r"templates/{TEMPLATES_BASE}/", "{TEMPLATES_BASE}/", suggested)
            suggested = re.sub(r"schemas/{SCHEMAS_BASE}/", "{SCHEMAS_BASE}/", suggested)

        return suggested

    def _validate_variable_usage(self, file_path: Path, content: str) -> list[PathIssue]:
        """Validate correct variable usage in content"""
        issues = []

        # Check for variables used in wrong contexts
        variable_contexts = {
            "{SCRIPTS_BASE}": ["scripts/", "python", "py"],
            "{TEMPLATES_BASE}": ["templates/", "j2", "jinja"],
            "{SCHEMAS_BASE}": ["schemas/", "json", "schema"],
            "{DATA_OUTPUTS}": ["outputs/", "data/", "results"],
        }

        for variable, expected_contexts in variable_contexts.items():
            if variable in content:
                # Find all occurrences
                pattern = re.escape(variable) + r'/([^\s"\'\`]+)'
                matches = re.finditer(pattern, content)

                for match in matches:
                    path_after_var = match.group(1)
                    context_found = False

                    for context in expected_contexts:
                        if context in path_after_var.lower():
                            context_found = True
                            break

                    if not context_found and "test" not in path_after_var.lower():
                        # Potential incorrect usage
                        line_num = content[: match.start()].count("\n") + 1
                        lines = content.split("\n")
                        line_content = lines[line_num - 1] if line_num <= len(lines) else ""

                        issues.append(
                            PathIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type="suspicious_variable_usage",
                                original_text=match.group(0),
                                suggested_fix=match.group(0),  # No auto-fix for suspicious usage
                                context=line_content.strip(),
                            )
                        )

        return issues

    def scan_all_commands(self, file_pattern: str = "*.txt") -> SyncReport:
        """Scan all command files for path issues"""
        print("🔍 Scanning command files in {self.commands_dir}")

        report = SyncReport(
            timestamp=datetime.now(),
            total_files_scanned=0,
            files_with_issues=0,
            total_issues=0,
            issues_fixed=0,
        )

        # Scan all matching files
        for file_path in self.commands_dir.glob(file_pattern):
            report.total_files_scanned += 1
            issues = self.scan_file(file_path)

            if issues:
                report.files_with_issues += 1
                report.file_issues[str(file_path)] = issues
                report.total_issues += len(issues)

                # Count issues by type
                for issue in issues:
                    report.issues_by_type[issue.issue_type] = report.issues_by_type.get(issue.issue_type, 0) + 1

        # Determine if validation passed
        report.validation_passed = report.total_issues == 0

        return report

    def fix_file(self, file_path: Path, issues: list[PathIssue], dry_run: bool = True) -> int:
        """Fix path issues in a file"""
        if not issues:
            return 0

        try:
            with open(file_path) as f:
                content = f.read()

            original_content = content
            fixes_applied = 0

            # Sort issues by line number in reverse to avoid offset problems
            sorted_issues = sorted(issues, key=lambda x: x.line_number, reverse=True)

            for issue in sorted_issues:
                if issue.original_text != issue.suggested_fix:
                    # Apply fix
                    content = content.replace(issue.original_text, issue.suggested_fix)
                    fixes_applied += 1

            if fixes_applied > 0 and not dry_run:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                shutil.copy2(file_path, backup_path)

                # Write fixed content
                with open(file_path, "w") as f:
                    f.write(content)

                print("  ✅ Fixed {fixes_applied} issues in {file_path.name}")
            elif fixes_applied > 0:
                print(f"  🔍 Would fix {fixes_applied} issues in {file_path.name} (dry-run)")

            return fixes_applied

        except Exception:
            print("  ❌ Error fixing {file_path}: {e}")
            return 0

    def synchronize_paths(self, dry_run: bool = True, file_pattern: str = "*.txt") -> SyncReport:
        """Run full path synchronization"""
        print(f"{'🔍' if dry_run else '🔧'} Path Synchronization {'(DRY RUN)' if dry_run else '(APPLYING FIXES)'}")
        print("=" * 70)

        # Scan for issues
        report = self.scan_all_commands(file_pattern)

        # Apply fixes if not dry run
        if not dry_run and report.file_issues:
            print("\n🔧 Applying fixes to {len(report.file_issues)} files...")

            for file_path, issues in report.file_issues.items():
                fixes = self.fix_file(Path(file_path), issues, dry_run=False)
                report.issues_fixed += fixes

        return report

    def print_report(self, report: SyncReport):
        """Print detailed synchronization report"""
        print("\n" + "=" * 70)
        print("PATH SYNCHRONIZATION REPORT")
        print("=" * 70)
        print("📅 Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("📁 Files scanned: {report.total_files_scanned}")
        print("⚠️  Files with issues: {report.files_with_issues}")
        print("🔍 Total issues found: {report.total_issues}")

        if report.issues_fixed > 0:
            print("✅ Issues fixed: {report.issues_fixed}")

        if report.issues_by_type:
            print("\n📊 Issues by Type:")
            for issue_type, count in sorted(report.issues_by_type.items(), key=lambda x: x[1], reverse=True):
                print("  {issue_type}: {count}")

        if report.file_issues:
            print("\n📋 Detailed Issues:")
            for file_path, issues in sorted(report.file_issues.items()):
                file_name = Path(file_path).name
                print("\n  {file_name} ({len(issues)} issues):")

                # Group issues by type
                issues_by_type = {}
                for issue in issues:
                    if issue.issue_type not in issues_by_type:
                        issues_by_type[issue.issue_type] = []
                    issues_by_type[issue.issue_type].append(issue)

                for issue_type, typed_issues in issues_by_type.items():
                    print("    {issue_type}:")
                    for issue in typed_issues[:3]:  # Show first 3 of each type
                        print(f"      Line {issue.line_number}: {issue.original_text} → {issue.suggested_fix}")
                    if len(typed_issues) > 3:
                        print("      ... and {len(typed_issues) - 3} more")

        print("\n✅ Validation: {'PASSED' if report.validation_passed else 'FAILED'}")

    def validate_consistency(self) -> bool:
        """Quick validation check for CI/CD integration"""
        report = self.scan_all_commands()
        return report.validation_passed

    def export_report(self, report: SyncReport, output_path: str = None) -> str:
        """Export synchronization report to JSON"""
        if output_path is None:
            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            output_path = project_root / f"data/outputs/path_sync_report_{timestamp}.json"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert report to JSON-serializable format
        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "total_files_scanned": report.total_files_scanned,
            "files_with_issues": report.files_with_issues,
            "total_issues": report.total_issues,
            "issues_fixed": report.issues_fixed,
            "issues_by_type": report.issues_by_type,
            "validation_passed": report.validation_passed,
            "file_issues": {},
        }

        # Convert PathIssue objects to dicts
        for file_path, issues in report.file_issues.items():
            report_data["file_issues"][file_path] = [
                {
                    "line_number": issue.line_number,
                    "issue_type": issue.issue_type,
                    "original_text": issue.original_text,
                    "suggested_fix": issue.suggested_fix,
                    "context": issue.context,
                }
                for issue in issues
            ]

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        return str(output_file)


def main():
    """CLI interface for path synchronization"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Path Synchronizer")
    parser.add_argument("--scan", action="store_true", help="Scan for path issues (dry-run)")
    parser.add_argument("--fix", action="store_true", help="Apply fixes to path issues")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Quick validation check (returns exit code)",
    )
    parser.add_argument("--pattern", default="*.txt", help="File pattern to scan (default: *.txt)")
    parser.add_argument("--export", help="Export report to JSON file")
    parser.add_argument("--commands-dir", help="Commands directory path")
    parser.add_argument("--registry", help="Registry JSON path")

    args = parser.parse_args()

    # Initialize synchronizer
    synchronizer = PathSynchronizer(args.commands_dir, args.registry)

    if args.validate:
        # Quick validation mode
        is_valid = synchronizer.validate_consistency()
        sys.exit(0 if is_valid else 1)

    elif args.fix:
        # Apply fixes mode
        report = synchronizer.synchronize_paths(dry_run=False, file_pattern=args.pattern)
        synchronizer.print_report(report)

        if args.export:
            export_path = synchronizer.export_report(report, args.export)
            print("\n📄 Report exported to: {export_path}")

    else:
        # Default scan mode (dry-run)
        report = synchronizer.synchronize_paths(dry_run=True, file_pattern=args.pattern)
        synchronizer.print_report(report)

        if args.export:
            export_path = synchronizer.export_report(report, args.export)
            print("\n📄 Report exported to: {export_path}")

        if not report.validation_passed:
            print("\n💡 Run with --fix to apply {report.total_issues} fixes")


if __name__ == "__main__":
    main()
