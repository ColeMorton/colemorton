#!/usr/bin/env python3
"""
Standardize Command References

Systematically updates all command files to use consistent path variable syntax.
Converts hardcoded paths to {VARIABLE} syntax across all 47 command files.
"""

import re
import sys
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class CommandReferenceStandardizer:
    """Standardizes path references across all command files"""

    def __init__(self, commands_dir: str = None):
        if commands_dir is None:
            commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
        self.commands_dir = Path(commands_dir)

        # Path standardization mappings
        self.path_replacements = {
            # Script references
            r"python scripts/": "python {SCRIPTS_BASE}/",
            r"scripts/": "{SCRIPTS_BASE}/",
            r"\./scripts/": "{SCRIPTS_BASE}/",
            # Template references
            r"\./templates/": "{TEMPLATES_BASE}/",
            r"templates/": "{TEMPLATES_BASE}/",
            # Fix templates inside SCRIPTS_BASE
            r"\{SCRIPTS_BASE\}/templates/": "{TEMPLATES_BASE}/",
            # Data output references
            r"\./data/outputs/": "{DATA_OUTPUTS}/",
            r"data/outputs/": "{DATA_OUTPUTS}/",
            # Schema references (more specific patterns)
            r"/scripts/schemas/": "{SCHEMAS_BASE}/",
            r"\./scripts/schemas/": "{SCHEMAS_BASE}/",
            r"scripts/schemas/": "{SCHEMAS_BASE}/",
        }

        # Patterns that should NOT be changed (already correct)
        # Be more specific - only preserve if the whole path structure is correct
        self.preserve_patterns = [
            r"\{TEMPLATES_BASE\}/",  # Correct template references
            r"\{DATA_OUTPUTS\}/",  # Correct data output references
            r"\{SCHEMAS_BASE\}/",  # Correct schema references
        ]

    def _should_preserve_line(self, line: str) -> bool:
        """Check if a line already has correct variable syntax"""
        for pattern in self.preserve_patterns:
            if re.search(pattern, line):
                return True
        return False

    def standardize_file(self, file_path: Path) -> tuple[bool, list[str]]:
        """
        Standardize a single command file

        Returns:
            (changed, changes_made) - bool indicating if file was changed, list of changes
        """
        if not file_path.exists() or file_path.suffix != ".md":
            return False, []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            print("Error reading {file_path}: {e}")
            return False, []

        original_content = content
        changes_made = []

        # Apply each replacement pattern
        for pattern, replacement in self.path_replacements.items():
            # Find all matches before replacement for logging
            matches = re.findall(pattern, content)
            if matches:
                # Only apply replacement to lines that don't already have variable syntax
                lines = content.split("\n")
                new_lines = []

                for line in lines:
                    if re.search(pattern, line) and not self._should_preserve_line(line):
                        old_line = line
                        new_line = re.sub(pattern, replacement, line)
                        if old_line != new_line:
                            changes_made.append(f"  {pattern} → {replacement}")
                            changes_made.append(f"    OLD: {old_line.strip()}")
                            changes_made.append(f"    NEW: {new_line.strip()}")
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)

                content = "\n".join(new_lines)

        # Write back if changed
        if content != original_content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True, changes_made
            except Exception:
                print("Error writing {file_path}: {e}")
                return False, []

        return False, []

    def standardize_all_commands(self) -> dict[str, list[str]]:
        """
        Standardize all command files

        Returns:
            Dictionary mapping file paths to lists of changes made
        """
        results = {}
        total_files = 0
        changed_files = 0

        print("Scanning commands directory: {self.commands_dir}")

        # Find all .md files recursively
        for file_path in self.commands_dir.rglob("*.md"):
            total_files += 1
            changed, changes = self.standardize_file(file_path)

            if changed:
                changed_files += 1
                relative_path = file_path.relative_to(self.commands_dir)
                results[str(relative_path)] = changes
                print("✅ Updated: {relative_path}")
                for change in changes[:6]:  # Show first 6 changes
                    print("    {change}")
                if len(changes) > 6:
                    print("    ... and {len(changes) - 6} more changes")
            else:
                relative_path = file_path.relative_to(self.commands_dir)
                print("⚡ No changes needed: {relative_path}")

        print("\n📊 Summary:")
        print("  Total files processed: {total_files}")
        print("  Files updated: {changed_files}")
        print("  Files unchanged: {total_files - changed_files}")

        return results

    def validate_standardization(self) -> dict[str, list[str]]:
        """
        Validate that all path references are now standardized

        Returns:
            Dictionary of files that still have inconsistent references
        """
        issues = {}

        # Patterns that indicate non-standardized references
        # Look for patterns that DON'T have the correct variable prefix
        problem_patterns = [
            # Scripts references that aren't preceded by {SCRIPTS_BASE}
            (
                r"(?<!\{SCRIPTS_BASE\})\/scripts\/",
                "Hardcoded scripts/ reference (should be {SCRIPTS_BASE}/)",
            ),
            (r"^scripts\/", "Hardcoded scripts/ reference (should be {SCRIPTS_BASE}/)"),
            (
                r'["\']scripts\/',
                "Hardcoded scripts/ reference (should be {SCRIPTS_BASE}/)",
            ),
            (
                r"python scripts\/",
                "Direct python scripts/ call (should use {SCRIPTS_BASE}/)",
            ),
            # Templates references
            (
                r"(?<!\{TEMPLATES_BASE\})\/templates\/",
                "Hardcoded templates/ reference (should be {TEMPLATES_BASE}/)",
            ),
            (
                r"^templates\/",
                "Hardcoded templates/ reference (should be {TEMPLATES_BASE}/)",
            ),
            (
                r'["\']templates\/',
                "Hardcoded templates/ reference (should be {TEMPLATES_BASE}/)",
            ),
            # Data outputs references
            (
                r"(?<!\{DATA_OUTPUTS\})\/data\/outputs\/",
                "Hardcoded data/outputs/ reference (should be {DATA_OUTPUTS}/)",
            ),
            (
                r"^data\/outputs\/",
                "Hardcoded data/outputs/ reference (should be {DATA_OUTPUTS}/)",
            ),
            (
                r'["\']data\/outputs\/',
                "Hardcoded data/outputs/ reference (should be {DATA_OUTPUTS}/)",
            ),
        ]

        for file_path in self.commands_dir.rglob("*.md"):
            file_issues = []

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                for pattern, description in problem_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        file_issues.append(f"{description}: {len(matches)} occurrences")

                if file_issues:
                    relative_path = file_path.relative_to(self.commands_dir)
                    issues[str(relative_path)] = file_issues

            except Exception:
                print("Error validating {file_path}: {e}")

        return issues

    def generate_report(self) -> str:
        """Generate a comprehensive standardization report"""
        print("🔍 Generating standardization report...\n")

        # Run validation
        issues = self.validate_standardization()

        report = []
        report.append("# Command Reference Standardization Report")
        report.append(f"Generated: {Path(__file__).name}")
        report.append("")

        if not issues:
            report.append("✅ **All command files use consistent path variables!**")
            report.append("")
            report.append("All references now use:")
            report.append("- `{SCRIPTS_BASE}/` for script paths")
            report.append("- `{TEMPLATES_BASE}/` for template paths")
            report.append("- `{DATA_OUTPUTS}/` for output directories")
            report.append("- `{SCHEMAS_BASE}/` for schema paths")
        else:
            report.append(f"❌ **Found {len(issues)} files with inconsistent references:**")
            report.append("")

            for file_path, file_issues in issues.items():
                report.append(f"### {file_path}")
                for issue in file_issues:
                    report.append(f"- {issue}")
                report.append("")

        return "\n".join(report)


def main():
    """CLI interface for the standardizer"""
    import argparse

    parser = argparse.ArgumentParser(description="Standardize Command Path References")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Only validate current state, don't make changes",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate and display standardization report",
    )
    parser.add_argument("--commands-dir", help="Path to commands directory (default: .claude/commands)")

    args = parser.parse_args()

    standardizer = CommandReferenceStandardizer(args.commands_dir)

    if args.validate or args.report:
        print("🔍 Validating command reference consistency...")
        report = standardizer.generate_report()
        print(report)

    elif args.dry_run:
        print("🧪 DRY RUN - Showing what would be changed...")
        print("(Not implemented - use --validate to see current state)")

    else:
        print("🔧 Standardizing all command path references...")
        results = standardizer.standardize_all_commands()

        if results:
            print("\n📋 Detailed changes made:")
            for file_path, changes in results.items():
                print("\n📄 {file_path}:")
                for change in changes:
                    print("  {change}")

        # Run validation after changes
        print("\n" + "=" * 60)
        print("🔍 Post-standardization validation:")
        report = standardizer.generate_report()
        print(report)


if __name__ == "__main__":
    main()
