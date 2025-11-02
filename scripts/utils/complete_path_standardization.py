#!/usr/bin/env python3
"""
Complete Path Standardization Script

Fixes all remaining hardcoded path references to achieve 100% consistency.
This script handles the more complex patterns that the basic standardizer missed.
"""

import re
import sys
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class CompletePathStandardizer:
    """Completes path standardization across all command files"""

    def __init__(self, commands_dir: str = None):
        if commands_dir is None:
            commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
        self.commands_dir = Path(commands_dir)

        # Comprehensive path replacement patterns
        self.path_replacements = [
            # Scripts patterns (various contexts)
            (r"\bscripts/", "{SCRIPTS_BASE}/"),
            (r"`scripts/", "`{SCRIPTS_BASE}/"),
            (r'"scripts/', '"{SCRIPTS_BASE}/'),
            (r"'scripts/", "'{SCRIPTS_BASE}/"),
            # Templates patterns (various contexts)
            (r"\btemplates/", "{TEMPLATES_BASE}/"),
            (r"`templates/", "`{TEMPLATES_BASE}/"),
            (r'"templates/', '"{TEMPLATES_BASE}/'),
            (r"'templates/", "'{TEMPLATES_BASE}/"),
            # Data outputs patterns (various contexts)
            (r"\bdata/outputs/", "{DATA_OUTPUTS}/"),
            (r"`data/outputs/", "`{DATA_OUTPUTS}/"),
            (r'"data/outputs/', '"{DATA_OUTPUTS}/'),
            (r"'data/outputs/", "'{DATA_OUTPUTS}/"),
            # Path with leading dots
            (r"\./data/outputs/", "{DATA_OUTPUTS}/"),
            (r"\./templates/", "{TEMPLATES_BASE}/"),
            (r"\./scripts/", "{SCRIPTS_BASE}/"),
        ]

        # Patterns that should NOT be changed (already correct)
        self.preserve_patterns = [
            r"\{SCRIPTS_BASE\}/",
            r"\{TEMPLATES_BASE\}/",
            r"\{DATA_OUTPUTS\}/",
            r"\{SCHEMAS_BASE\}/",
        ]

    def _should_preserve_line(self, line: str) -> bool:
        """Check if a line already has correct variable syntax"""
        for pattern in self.preserve_patterns:
            if re.search(pattern, line):
                return True
        return False

    def _is_already_variable_path(self, match_text: str, line: str) -> bool:
        """Check if the match is already part of a variable path"""
        # Find the position of the match in the line
        match_pos = line.find(match_text)
        if match_pos == -1:
            return False

        # Look backwards from the match to see if it's preceded by {VARIABLE_BASE}
        prefix = line[:match_pos]
        for preserve_pattern in self.preserve_patterns:
            # Remove the trailing / from preserve pattern for this check
            var_pattern = preserve_pattern.rstrip("/")
            if re.search(var_pattern + r"\}$", prefix):
                return True

        return False

    def standardize_file(self, file_path: Path) -> tuple[bool, list[str]]:
        """
        Standardize a single command file with comprehensive pattern matching

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
        for pattern, replacement in self.path_replacements:
            # Find all matches
            matches = list(re.finditer(pattern, content))
            if not matches:
                continue

            lines = content.split("\n")
            new_lines = []
            line_changes = 0

            for line in lines:
                original_line = line

                # Check each match in this line
                line_matches = list(re.finditer(pattern, line))
                for match in reversed(line_matches):  # Process from right to left
                    match_text = match.group(0)

                    # Skip if already part of a variable path
                    if self._is_already_variable_path(match_text, line):
                        continue

                    # Skip if line should be preserved entirely
                    if self._should_preserve_line(line):
                        continue

                    # Apply replacement
                    start, end = match.span()
                    line = line[:start] + replacement + line[end:]
                    line_changes += 1

                if line != original_line:
                    changes_made.append(f"  {pattern} → {replacement}")
                    changes_made.append(f"    OLD: {original_line.strip()[:100]}")
                    changes_made.append(f"    NEW: {line.strip()[:100]}")

                new_lines.append(line)

            if line_changes > 0:
                content = "\n".join(new_lines)

        # Write back if changed
        changed = content != original_content
        if changed:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception:
                print("Error writing {file_path}: {e}")
                return False, []

        return changed, changes_made

    def standardize_all_files(self) -> dict[str, list[str]]:
        """
        Standardize all command files

        Returns:
            Dictionary mapping file paths to changes made
        """
        print("🔧 Completing path standardization across all command files...")
        print("Scanning commands directory: {self.commands_dir}")

        results = {}
        total_files = 0
        changed_files = 0

        # Process all .md files
        for file_path in self.commands_dir.rglob("*.md"):
            total_files += 1
            changed, changes = self.standardize_file(file_path)

            if changed:
                changed_files += 1
                results[str(file_path)] = changes
                relative_path = file_path.relative_to(self.commands_dir)
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

    def validate_completion(self) -> dict[str, list[str]]:
        """
        Validate that all path references are now standardized

        Returns:
            Dictionary of files that still have inconsistent references
        """
        print("🔍 Final validation check...")

        issues = {}

        # Enhanced problem patterns for thorough detection
        problem_patterns = [
            # Scripts references (excluding already correct ones)
            (
                r"(?<!\{SCRIPTS_BASE\}/)(?<!\{SCRIPTS_BASE\})scripts/",
                "Hardcoded scripts/ reference",
            ),
            # Templates references (excluding already correct ones)
            (
                r"(?<!\{TEMPLATES_BASE\}/)(?<!\{TEMPLATES_BASE\})templates/",
                "Hardcoded templates/ reference",
            ),
            # Data outputs references (excluding already correct ones)
            (
                r"(?<!\{DATA_OUTPUTS\}/)(?<!\{DATA_OUTPUTS\})data/outputs/",
                "Hardcoded data/outputs/ reference",
            ),
            # Direct python commands
            (r"python scripts/", "Direct python scripts/ call"),
        ]

        for file_path in self.commands_dir.rglob("*.md"):
            file_issues = []

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                for pattern, description in problem_patterns:
                    try:
                        matches = re.findall(pattern, content)
                        if matches:
                            file_issues.append(f"{description}: {len(matches)} occurrences")
                    except re.error:
                        print("Regex error with pattern {pattern}: {e}")
                        continue

                if file_issues:
                    relative_path = file_path.relative_to(self.commands_dir)
                    issues[str(relative_path)] = file_issues

            except Exception:
                print("Error validating {file_path}: {e}")
                continue

        return issues


def main():
    """Main execution function"""
    standardizer = CompletePathStandardizer()

    # Run complete standardization
    results = standardizer.standardize_all_files()

    print("\n" + "=" * 60)

    # Validate completion
    issues = standardizer.validate_completion()

    if not issues:
        print("🎉 **COMPLETE: All command files now use consistent path variables!**")
        print("\nAll references now use:")
        print("- `{SCRIPTS_BASE}/` for script paths")
        print("- `{TEMPLATES_BASE}/` for template paths")
        print("- `{DATA_OUTPUTS}/` for output directories")
        print("- `{SCHEMAS_BASE}/` for schema paths")
    else:
        print("⚠️  Still found {len(issues)} files with inconsistent references:")
        for file, problems in list(issues.items())[:10]:  # Show first 10
            print("  {file}:")
            for problem in problems:
                print("    {problem}")

        if len(issues) > 10:
            print("  ... and {len(issues) - 10} more files")

    return len(issues) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
