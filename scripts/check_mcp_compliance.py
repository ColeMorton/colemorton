#!/usr/bin/env python3
"""
MCP Compliance Checking Script

This script enforces MCP-first development patterns and context decoupling
standards across the Sensylate codebase. It identifies violations of the
MCP architecture and helps maintain consistency with established patterns.

Usage:
    python scripts/check_mcp_compliance.py                    # Check all files
    python scripts/check_mcp_compliance.py file.py           # Check specific file
    python scripts/check_mcp_compliance.py --fix             # Auto-fix issues
    python scripts/check_mcp_compliance.py --report          # Generate report
"""

import argparse
import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of MCP compliance violations"""

    DIRECT_SERVICE_IMPORT = "direct_service_import"
    HARDCODED_PATH = "hardcoded_path"
    NO_CONTEXT_INJECTION = "no_context_injection"
    MIXED_MCP_DIRECT = "mixed_mcp_direct"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    CONTEXT_COUPLING = "context_coupling"
    ANTI_PATTERN = "anti_pattern"


class Severity(Enum):
    """Violation severity levels"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ComplianceViolation:
    """Represents a compliance violation"""

    file_path: Path
    line_number: int
    violation_type: ViolationType
    severity: Severity
    message: str
    line_content: str
    suggested_fix: str | None = None
    code: str | None = None


class MCPComplianceChecker:
    """
    Comprehensive MCP compliance checker for Sensylate codebase.

    This checker enforces:
    1. MCP-first development patterns
    2. Context decoupling standards
    3. Proper error handling
    4. Consistent architecture patterns

    It scans Python files, command markdown files, and configuration
    files for violations and provides suggestions for fixes.
    """

    def __init__(self):
        self.violations: list[ComplianceViolation] = []
        self.patterns = self._load_violation_patterns()
        self.context_patterns = self._load_context_patterns()

    def _load_violation_patterns(self) -> dict[ViolationType, list[dict[str, Any]]]:
        """Load patterns that indicate violations"""
        return {
            ViolationType.DIRECT_SERVICE_IMPORT: [
                {
                    "pattern": r"from\s+yahoo_finance_service\s+import",
                    "message": "Direct yahoo_finance_service import violates MCP-first pattern",
                    "suggested_fix": "from context.providers import MCPContextProvider",
                },
                {
                    "pattern": r"from\s+.*_service\s+import",
                    "message": "Direct service import bypasses MCP protocol",
                    "suggested_fix": "Use MCP client wrapper instead",
                },
                {
                    "pattern": r"YahooFinanceService\(\)",
                    "message": "Direct service instantiation violates MCP pattern",
                    "suggested_fix": "Use mcp_provider.get_client('yahoo-finance')",
                },
                {
                    "pattern": r"\.get_stock_info\(",
                    "message": "Direct service method call bypasses MCP",
                    "suggested_fix": "Use client.call_tool('get_stock_fundamentals', ...)",
                },
            ],
            ViolationType.HARDCODED_PATH: [
                {
                    "pattern": r"['\"]\.\/data\/outputs\/[^'\"]*['\"]",
                    "message": "Hardcoded output path violates context decoupling",
                    "suggested_fix": "Use context.data.get_output_path(...)",
                },
                {
                    "pattern": r"['\"]\.\/mcp-servers\.json['\"]",
                    "message": "Hardcoded MCP config path",
                    "suggested_fix": "Use context.mcp.config_path",
                },
                {
                    "pattern": r"Path\(['\"]data\/outputs['\"]",
                    "message": "Hardcoded Path construction for outputs",
                    "suggested_fix": "Use context.data.base_output_path",
                },
            ],
            ViolationType.NO_CONTEXT_INJECTION: [
                {
                    "pattern": r"def\s+\w+\([^)]*\):\s*\n.*yahoo.*finance",
                    "message": "Function uses financial data without context injection",
                    "suggested_fix": "Add context parameter and use context providers",
                }
            ],
            ViolationType.MIXED_MCP_DIRECT: [
                {
                    "pattern": r"(from.*mcp.*import.*).*\n.*from.*_service.*import",
                    "message": "Mixing MCP and direct service imports",
                    "suggested_fix": "Use only MCP patterns consistently",
                }
            ],
            ViolationType.MISSING_ERROR_HANDLING: [
                {
                    "pattern": r"call_tool\([^)]+\)\s*(?!\s*except)",
                    "message": "MCP tool call without error handling",
                    "suggested_fix": "Add try/except with MCPError handling",
                }
            ],
            ViolationType.CONTEXT_COUPLING: [
                {
                    "pattern": r"**Output Location**: `\./[^`]+`",
                    "message": "Command has hardcoded output location",
                    "suggested_fix": "Use {{context.data.output_path}}/{{context.command.category}}/",
                },
                {
                    "pattern": r"**File Naming**: `[^{][^}]*\.(json|md)`",
                    "message": "Command has hardcoded file naming",
                    "suggested_fix": "Use {{context.command.file_template}}",
                },
            ],
        }

    def _load_context_patterns(self) -> dict[str, list[str]]:
        """Load patterns that indicate proper context usage"""
        return {
            "good_patterns": [
                r"from\s+context\s+import",
                r"from\s+context\.providers\s+import",
                r"MCPContextProvider",
                r"DataContextProvider",
                r"ValidationContextProvider",
                r"context\.data\.get_output_path",
                r"context\.mcp\.get_client",
                r"with\s+.*\.get_client\(",
                r"try:.*except\s+MCPError",
            ],
            "required_for_financial": [r"context", r"mcp.*provider|provider.*mcp"],
        }

    def check_file(self, file_path: Path) -> list[ComplianceViolation]:
        """
        Check single file for MCP compliance violations.

        Args:
            file_path: Path to file to check

        Returns:
            List of violations found in file
        """
        if not file_path.exists():
            return []

        file_violations = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return []

        # Check based on file type
        if file_path.suffix == ".py":
            file_violations.extend(self._check_python_file(file_path, content, lines))
        elif file_path.suffix == ".md" and ".claude/commands/" in str(file_path):
            file_violations.extend(self._check_command_file(file_path, content, lines))

        return file_violations

    def _check_python_file(self, file_path: Path, content: str, lines: list[str]) -> list[ComplianceViolation]:
        """Check Python file for violations"""
        violations = []

        # Check for direct service imports
        violations.extend(
            self._check_patterns(
                file_path,
                lines,
                self.patterns[ViolationType.DIRECT_SERVICE_IMPORT],
                ViolationType.DIRECT_SERVICE_IMPORT,
                Severity.ERROR,
            )
        )

        # Check for hardcoded paths
        violations.extend(
            self._check_patterns(
                file_path,
                lines,
                self.patterns[ViolationType.HARDCODED_PATH],
                ViolationType.HARDCODED_PATH,
                Severity.WARNING,
            )
        )

        # Check for missing error handling
        violations.extend(
            self._check_patterns(
                file_path,
                lines,
                self.patterns[ViolationType.MISSING_ERROR_HANDLING],
                ViolationType.MISSING_ERROR_HANDLING,
                Severity.WARNING,
            )
        )

        # Check for financial code without context
        if self._is_financial_code(content):
            if not self._has_context_usage(content):
                violations.append(
                    ComplianceViolation(
                        file_path=file_path,
                        line_number=1,
                        violation_type=ViolationType.NO_CONTEXT_INJECTION,
                        severity=Severity.ERROR,
                        message="Financial code without context injection",
                        line_content="",
                        suggested_fix="Add context parameter and use context providers",
                    )
                )

        return violations

    def _check_command_file(self, file_path: Path, content: str, lines: list[str]) -> list[ComplianceViolation]:
        """Check command markdown file for violations"""
        violations = []

        # Check for context coupling patterns
        violations.extend(
            self._check_patterns(
                file_path,
                lines,
                self.patterns[ViolationType.CONTEXT_COUPLING],
                ViolationType.CONTEXT_COUPLING,
                Severity.WARNING,
            )
        )

        # Check for hardcoded MCP tool usage patterns
        mcp_tool_pattern = r"Use\s+the\s+following\s+MCP\s+tools.*:\s*\n.*get_\w+"
        for i, line in enumerate(lines):
            if re.search(mcp_tool_pattern, line, re.IGNORECASE):
                # This is actually good - commands should specify MCP tools
                continue

        return violations

    def _check_patterns(
        self,
        file_path: Path,
        lines: list[str],
        patterns: list[dict[str, Any]],
        violation_type: ViolationType,
        severity: Severity,
    ) -> list[ComplianceViolation]:
        """Check file lines against violation patterns"""
        violations = []

        for i, line in enumerate(lines, 1):
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                if re.search(pattern, line):
                    violations.append(
                        ComplianceViolation(
                            file_path=file_path,
                            line_number=i,
                            violation_type=violation_type,
                            severity=severity,
                            message=pattern_info["message"],
                            line_content=line.strip(),
                            suggested_fix=pattern_info.get("suggested_fix"),
                            code=pattern_info.get("code"),
                        )
                    )

        return violations

    def _is_financial_code(self, content: str) -> bool:
        """Check if file contains financial/trading code"""
        financial_indicators = [
            r"\bticker\b",
            r"\bstock\b",
            r"\bmarket\b",
            r"\bfinancial\b",
            r"\byahoo.*finance\b",
            r"\bfundamental\b",
            r"\btrading\b",
            r"\banalysis\b",
            r"\bearnings\b",
            r"\bpe_ratio\b",
        ]

        for indicator in financial_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True

        return False

    def _has_context_usage(self, content: str) -> bool:
        """Check if file uses context patterns"""
        for pattern in self.context_patterns["good_patterns"]:
            if re.search(pattern, content):
                return True
        return False

    def check_directory(self, directory: Path, exclude_patterns: list[str] = None) -> list[ComplianceViolation]:
        """
        Check entire directory for violations.

        Args:
            directory: Directory to scan
            exclude_patterns: Patterns to exclude from checking

        Returns:
            List of all violations found
        """
        if exclude_patterns is None:
            exclude_patterns = [
                r"__pycache__",
                r"\.git",
                r"\.pytest_cache",
                r"node_modules",
                r"\.venv",
                r"venv",
            ]

        all_violations = []

        # Find files to check
        file_patterns = ["**/*.py", "**/*.md"]
        files_to_check = []

        for pattern in file_patterns:
            files_to_check.extend(directory.glob(pattern))

        # Filter out excluded files
        filtered_files = []
        for file_path in files_to_check:
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if re.search(exclude_pattern, str(file_path)):
                    should_exclude = True
                    break

            if not should_exclude:
                filtered_files.append(file_path)

        # Check each file
        for file_path in filtered_files:
            violations = self.check_file(file_path)
            all_violations.extend(violations)

        logger.info(f"Checked {len(filtered_files)} files, found {len(all_violations)} violations")
        return all_violations

    def generate_report(self, violations: list[ComplianceViolation]) -> dict[str, Any]:
        """Generate compliance report"""
        if not violations:
            return {
                "status": "COMPLIANT",
                "total_violations": 0,
                "summary": "No MCP compliance violations found",
                "violations_by_type": {},
                "violations_by_severity": {},
                "files_affected": 0,
            }

        # Group violations
        by_type = {}
        by_severity = {}
        by_file = {}

        for violation in violations:
            # By type
            type_name = violation.violation_type.value
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(violation)

            # By severity
            severity_name = violation.severity.value
            if severity_name not in by_severity:
                by_severity[severity_name] = []
            by_severity[severity_name].append(violation)

            # By file
            file_name = str(violation.file_path)
            if file_name not in by_file:
                by_file[file_name] = []
            by_file[file_name].append(violation)

        # Determine overall status
        has_errors = any(v.severity == Severity.ERROR for v in violations)
        status = "FAILED" if has_errors else "WARNING"

        return {
            "status": status,
            "total_violations": len(violations),
            "summary": f"Found {len(violations)} violations across {len(by_file)} files",
            "violations_by_type": {type_name: len(violations) for type_name, violations in by_type.items()},
            "violations_by_severity": {
                severity_name: len(violations) for severity_name, violations in by_severity.items()
            },
            "files_affected": len(by_file),
            "most_problematic_files": sorted(
                [(file, len(violations)) for file, violations in by_file.items()],
                key=lambda x: x[1],
                reverse=True,
            )[:10],
        }

    def print_violations(self, violations: list[ComplianceViolation], verbose: bool = False):
        """Print violations in human-readable format"""
        if not violations:
            print("✅ No MCP compliance violations found!")
            return

        print("\n❌ Found {len(violations)} MCP compliance violations:\n")

        # Group by file
        by_file = {}
        for violation in violations:
            file_key = str(violation.file_path)
            if file_key not in by_file:
                by_file[file_key] = []
            by_file[file_key].append(violation)

        for file_path, file_violations in by_file.items():
            print("📁 {file_path}")

            for violation in file_violations:
                severity_icon = {
                    Severity.ERROR: "🔴",
                    Severity.WARNING: "🟡",
                    Severity.INFO: "🔵",
                }[violation.severity]

                print(f"  {severity_icon} Line {violation.line_number}: {violation.message}")

                if verbose:
                    print("     Code: {violation.line_content}")
                    if violation.suggested_fix:
                        print("     Fix:  {violation.suggested_fix}")

            print()

    def auto_fix_violations(self, violations: list[ComplianceViolation]) -> int:
        """
        Attempt to automatically fix violations.

        Args:
            violations: List of violations to fix

        Returns:
            Number of violations fixed
        """
        logger.warning("Auto-fix functionality not yet implemented")
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Check MCP compliance for Sensylate codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to check (default: current directory)",
    )

    parser.add_argument("--report", action="store_true", help="Generate detailed compliance report")

    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix violations")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parser.add_argument("--exclude", nargs="*", default=[], help="Patterns to exclude from checking")

    args = parser.parse_args()

    # Initialize checker
    checker = MCPComplianceChecker()

    # Determine paths to check
    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        paths = [Path.cwd()]

    # Collect all violations
    all_violations = []

    for path in paths:
        if path.is_file():
            violations = checker.check_file(path)
        elif path.is_dir():
            violations = checker.check_directory(path, args.exclude)
        else:
            logger.error(f"Path does not exist: {path}")
            continue

        all_violations.extend(violations)

    # Generate report
    report = checker.generate_report(all_violations)

    # Output results
    if args.json:
        print(
            json.dumps(
                {
                    "report": report,
                    "violations": [
                        {
                            "file": str(v.file_path),
                            "line": v.line_number,
                            "type": v.violation_type.value,
                            "severity": v.severity.value,
                            "message": v.message,
                            "line_content": v.line_content,
                            "suggested_fix": v.suggested_fix,
                        }
                        for v in all_violations
                    ],
                },
                indent=2,
            )
        )
    else:
        # Print human-readable output
        if args.report:
            print("📊 MCP Compliance Report")
            print("=" * 50)
            print("Status: {report['status']}")
            print("Total Violations: {report['total_violations']}")
            print("Files Affected: {report['files_affected']}")
            print()

            if report["violations_by_severity"]:
                print("Violations by Severity:")
                for severity, count in report["violations_by_severity"].items():
                    print("  {severity}: {count}")
                print()

            if report["violations_by_type"]:
                print("Violations by Type:")
                for vtype, count in report["violations_by_type"].items():
                    print("  {vtype}: {count}")
                print()

        checker.print_violations(all_violations, args.verbose)

    # Auto-fix if requested
    if args.fix:
        fixed_count = checker.auto_fix_violations(all_violations)
        print("🔧 Fixed {fixed_count} violations")

    # Exit code based on status
    if report["status"] == "FAILED":
        exit(1)
    elif report["status"] == "WARNING":
        exit(0)  # Warnings don't fail CI
    else:
        exit(0)


if __name__ == "__main__":
    main()
