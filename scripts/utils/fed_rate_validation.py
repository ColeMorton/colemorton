#!/usr/bin/env python3
"""
Fed Funds Rate Validation Utility

Detects hardcoded Fed funds rates in analysis files and templates
to prevent data staleness and ensure real-time accuracy.

Usage:
    python scripts/utils/fed_rate_validation.py --check-all
    python scripts/utils/fed_rate_validation.py --file path/to/file.json
    python scripts/utils/fed_rate_validation.py --directory data/outputs/
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime
from typing import Any


class FedRateValidator:
    """
    Validator to detect hardcoded Federal funds rates in analysis files
    """

    def __init__(self):
        self.hardcoded_patterns = [
            # Common hardcoded Fed rate patterns
            r"5\.25-5\.50%?",  # Range format 5.25-5.50 or 5.25-5.50%
            r"5\.25\s*-\s*5\.50%?",  # Range with spaces
            r"Fed\s+Funds:\s*5\.25-5\.50%?",  # Specific Fed Funds range format
            r"fed.*?fund.*?5\.[0-9][0-9]%?",  # Fed funds specific rates (case insensitive)
            r"fed.*?fund.*?4\.[0-9][0-9]%?",  # Catch any specific Fed rate
            r'"fed_funds_rate":\s*"[0-9]\.[0-9][0-9]%?"',  # JSON format
            r"Fed\s+Funds:\s*[0-9]\.[0-9][0-9]%?",  # Markdown format
            r"Fed\s+Funds[^|]*[0-9]\.[0-9][0-9]%?",  # Fed Funds followed by rate
            r"\|\s*Fed\s+Funds:\s*[0-9]\.[0-9][0-9]%?",  # Table format
            r"Restrictive.*Fed\s+Funds.*[0-9]\.[0-9]",  # Environment + rate combo
        ]

        self.acceptable_patterns = [
            # These patterns are OK (templates/placeholders)
            r"\[X\.XX\]%?",  # Template placeholders
            r"\{\{\s*data\.fed_funds_rate\s*\}\}%?",  # Jinja2 template variables
            r"\{\{\s*fed_funds_rate\s*\}\}%?",  # Jinja2 template variables
            r"self\.econ_data\.get_fed_funds_rate\(\)",  # Dynamic calls
            r"RealTimeEconomicData",  # Service usage
            r"fred_economic_cli",  # CLI service usage
            r"FRED.*CLI.*validation",  # Validation script references
            r"data\.fed_funds_rate",  # Template data references
        ]

        self.file_extensions = [".py", ".json", ".md", ".j2", ".txt"]
        self.exclude_directories = [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "htmlcov",
            ".pytest_cache",
            "build",
            "dist",
        ]

        self.issues = []

    def is_acceptable_pattern(self, text: str) -> bool:
        """Check if the detected pattern is acceptable (template/dynamic)"""
        for pattern in self.acceptable_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def check_file(self, file_path: str) -> list[dict[str, Any]]:
        """
        Check a single file for hardcoded Fed rates

        Returns:
            List of issues found in the file
        """
        file_issues = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check each pattern
            for i, pattern in enumerate(self.hardcoded_patterns):
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    matched_text = match.group(0)

                    # Skip if it's an acceptable pattern
                    if self.is_acceptable_pattern(matched_text):
                        continue

                    # Find line number
                    line_num = content[: match.start()].count("\n") + 1

                    # Get context (surrounding lines)
                    lines = content.split("\n")
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 1)
                    context = "\n".join(lines[start_line:end_line])

                    issue = {
                        "file": file_path,
                        "line": line_num,
                        "pattern_index": i,
                        "matched_text": matched_text,
                        "context": context,
                        "severity": self._assess_severity(file_path, matched_text),
                    }

                    file_issues.append(issue)

        except Exception:
            print("Warning: Could not read file {file_path}: {e}")

        return file_issues

    def _assess_severity(self, file_path: str, matched_text: str) -> str:
        """Assess severity of the hardcoded rate issue"""
        if "synthesis" in file_path.lower() or file_path.endswith(".md"):
            return "HIGH"  # Customer-facing documents
        if "analysis" in file_path.lower() or file_path.endswith(".json"):
            return "MEDIUM"  # Analysis pipeline
        if "template" in file_path.lower():
            return "LOW"  # Templates (might be intentional examples)
        return "MEDIUM"

    def check_directory(self, directory: str, recursive: bool = True) -> list[dict[str, Any]]:
        """
        Check all files in a directory for hardcoded Fed rates

        Returns:
            List of all issues found
        """
        all_issues = []

        if recursive:
            pattern = f"{directory}/**/*"
        else:
            pattern = f"{directory}/*"

        for file_path in glob.glob(pattern, recursive=recursive):
            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Skip excluded directories
            if any(excluded in file_path for excluded in self.exclude_directories):
                continue

            # Check file extension
            if not any(file_path.endswith(ext) for ext in self.file_extensions):
                continue

            # Check the file
            file_issues = self.check_file(file_path)
            all_issues.extend(file_issues)

        return all_issues

    def format_report(self, issues: list[dict[str, Any]]) -> str:
        """Format validation report"""
        if not issues:
            return "✅ No hardcoded Fed funds rates detected!"

        report = [
            "🚨 Fed Funds Rate Validation Report",
            "=" * 50,
            f"Found {len(issues)} potential hardcoded Fed funds rates:\n",
        ]

        # Group by severity
        high_issues = [i for i in issues if i["severity"] == "HIGH"]
        medium_issues = [i for i in issues if i["severity"] == "MEDIUM"]
        low_issues = [i for i in issues if i["severity"] == "LOW"]

        for severity, issue_list in [
            ("HIGH", high_issues),
            ("MEDIUM", medium_issues),
            ("LOW", low_issues),
        ]:
            if issue_list:
                report.append(f"{severity} PRIORITY ({len(issue_list)} issues):")
                report.append("-" * 30)

                for issue in issue_list:
                    report.extend(
                        [
                            f"File: {issue['file']}",
                            f"Line: {issue['line']}",
                            f"Found: {issue['matched_text']}",
                            "Context:",
                            f"  {issue['context'].replace(chr(10), chr(10) + '  ')}",
                            "",
                        ]
                    )

        report.extend(
            [
                "💡 RECOMMENDATIONS:",
                "1. Replace hardcoded rates with RealTimeEconomicData service calls",
                "2. Use self.econ_data.get_fed_funds_rate() in analysis scripts",
                "3. Update templates to use dynamic placeholders",
                "4. Run this validator before commits to prevent hardcoding",
                "",
            ]
        )

        return "\n".join(report)

    def get_suggested_fixes(self, issues: list[dict[str, Any]]) -> dict[str, list[str]]:
        """Generate suggested fixes for detected issues"""
        fixes = {}

        for issue in issues:
            file_path = issue["file"]
            matched_text = issue["matched_text"]

            if file_path not in fixes:
                fixes[file_path] = []

            # Generate fix suggestions based on file type
            if file_path.endswith(".py"):
                fix = f"Replace '{matched_text}' with self.econ_data.get_fed_funds_rate()"
            elif file_path.endswith(".json"):
                fix = f"Replace '{matched_text}' with dynamic rate from RealTimeEconomicData"
            elif file_path.endswith(".md"):
                fix = f"Replace '{matched_text}' with template variable or dynamic rate"
            else:
                fix = f"Replace '{matched_text}' with dynamic rate source"

            fixes[file_path].append(fix)

        return fixes


def main():
    parser = argparse.ArgumentParser(description="Validate files for hardcoded Fed funds rates")
    parser.add_argument("--check-all", action="store_true", help="Check all analysis and template files")
    parser.add_argument("--file", type=str, help="Check specific file")
    parser.add_argument("--directory", type=str, help="Check specific directory")
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (text or json)",
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Include fix suggestions in output",
    )

    args = parser.parse_args()

    validator = FedRateValidator()
    all_issues = []

    if args.check_all:
        # Check common directories
        directories = [
            "data/outputs/fundamental_analysis",
            "templates/analysis",
            "scripts/fundamental_analysis",
            "scripts/services",
        ]

        for directory in directories:
            if os.path.exists(directory):
                issues = validator.check_directory(directory)
                all_issues.extend(issues)

    elif args.file:
        if os.path.exists(args.file):
            all_issues = validator.check_file(args.file)
        else:
            print("Error: File not found: {args.file}")
            sys.exit(1)

    elif args.directory:
        if os.path.exists(args.directory):
            all_issues = validator.check_directory(args.directory)
        else:
            print("Error: Directory not found: {args.directory}")
            sys.exit(1)

    else:
        print("Error: Must specify --check-all, --file, or --directory")
        parser.print_help()
        sys.exit(1)

    # Output results
    if args.output_format == "json":
        result = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(all_issues),
            "issues": all_issues,
        }

        if args.fix_suggestions:
            result["suggested_fixes"] = validator.get_suggested_fixes(all_issues)

        print(json.dumps(result, indent=2))
    else:
        # Text format
        print(validator.format_report(all_issues))

        if args.fix_suggestions and all_issues:
            print("\n🔧 SUGGESTED FIXES:")
            print("=" * 30)
            fixes = validator.get_suggested_fixes(all_issues)
            for file_path, file_fixes in fixes.items():
                print("\n{file_path}:")
                for fix in file_fixes:
                    print("  - {fix}")

    # Exit with error code if issues found
    if all_issues:
        high_priority = [i for i in all_issues if i["severity"] == "HIGH"]
        if high_priority:
            print("\n❌ {len(high_priority)} HIGH priority issues found!")
            sys.exit(2)  # High priority issues
        else:
            print("\n⚠️  {len(all_issues)} issues found (no high priority)")
            sys.exit(1)  # Medium/low priority issues
    else:
        print("\n✅ Validation passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
