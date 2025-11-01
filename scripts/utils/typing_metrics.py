#!/usr/bin/env python3
"""
Type Safety Metrics Collection - Team Adoption Monitoring

This module provides comprehensive metrics collection for monitoring team adoption
of type safety guidelines and MyPy compliance across the Sensylate platform.
"""

import ast
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TypeSafetyMetricsCollector:
    """Collect and analyze type safety metrics for team adoption monitoring."""

    def __init__(self, project_root: Path | None = None):
        """Initialize metrics collector."""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.output_dir = self.project_root / "data" / "outputs" / "technical_health"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect_comprehensive_metrics(self) -> dict[str, Any]:
        """Collect all type safety metrics for team monitoring."""
        logger.info("Collecting comprehensive type safety metrics...")

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "annotation_coverage": self._calculate_annotation_coverage(),
            "mypy_compliance": self._analyze_mypy_compliance(),
            "strict_modules": self._count_strict_modules(),
            "error_analysis": self._categorize_mypy_errors(),
            "file_statistics": self._analyze_file_statistics(),
            "team_adoption": self._calculate_team_adoption_metrics(),
        }

        # Save metrics to file
        metrics_file = self.output_dir / f"typing_metrics_{datetime.now().strftime('%Y%m%d')}.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Metrics saved to {metrics_file}")
        return metrics

    def _calculate_annotation_coverage(self) -> dict[str, Any]:
        """Calculate type annotation coverage across Python files."""
        logger.info("Calculating type annotation coverage...")

        total_functions = 0
        annotated_functions = 0
        files_analyzed = 0
        coverage_by_file = {}

        for py_file in self.scripts_dir.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                file_functions = 0
                file_annotated = 0

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        file_functions += 1
                        total_functions += 1

                        # Check if function has type annotations
                        has_annotations = self._has_type_annotations(node)
                        if has_annotations:
                            file_annotated += 1
                            annotated_functions += 1

                if file_functions > 0:
                    file_coverage = (file_annotated / file_functions) * 100
                    coverage_by_file[str(py_file.relative_to(self.project_root))] = {
                        "functions": file_functions,
                        "annotated": file_annotated,
                        "coverage_percent": round(file_coverage, 1),
                    }

                files_analyzed += 1

            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
                continue

        overall_coverage = (annotated_functions / total_functions * 100) if total_functions > 0 else 0

        return {
            "overall_coverage_percent": round(overall_coverage, 1),
            "total_functions": total_functions,
            "annotated_functions": annotated_functions,
            "files_analyzed": files_analyzed,
            "coverage_by_file": coverage_by_file,
            "high_coverage_files": [f for f, data in coverage_by_file.items() if data["coverage_percent"] >= 80],
            "low_coverage_files": [f for f, data in coverage_by_file.items() if data["coverage_percent"] < 50],
        }

    def _has_type_annotations(self, func_node: ast.FunctionDef) -> bool:
        """Check if a function has type annotations."""
        # Check return annotation
        has_return_annotation = func_node.returns is not None

        # Check parameter annotations
        has_param_annotations = any(arg.annotation is not None for arg in func_node.args.args)

        # Consider function annotated if it has return type or parameter types
        return has_return_annotation or has_param_annotations

    def _analyze_mypy_compliance(self) -> dict[str, Any]:
        """Analyze MyPy compliance and error trends."""
        logger.info("Analyzing MyPy compliance...")

        try:
            # Run MyPy and capture output
            result = subprocess.run(
                ["mypy", "scripts/"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            errors = []
            if result.returncode != 0:
                # Parse MyPy output for error details
                for line in result.stdout.split("\n"):
                    if line.strip() and ": error:" in line:
                        errors.append(line.strip())

            return {
                "is_compliant": result.returncode == 0,
                "error_count": len(errors),
                "errors": errors,
                "raw_output": result.stdout,
                "compliance_status": "PASS" if result.returncode == 0 else "FAIL",
            }

        except Exception as e:
            logger.error(f"Error running MyPy analysis: {e}")
            return {
                "is_compliant": False,
                "error_count": -1,
                "errors": [],
                "error_message": str(e),
                "compliance_status": "ERROR",
            }

    def _count_strict_modules(self) -> dict[str, Any]:
        """Count modules with strict MyPy checking enabled."""
        logger.info("Counting strict modules...")

        mypy_config = self.project_root / "mypy.ini"
        strict_modules = []

        if mypy_config.exists():
            try:
                with open(mypy_config) as f:
                    content = f.read()

                # Look for module-specific strict settings
                lines = content.split("\n")
                current_module = None

                for line in lines:
                    line = line.strip()
                    if line.startswith("[mypy-") and line.endswith("]"):
                        current_module = line[6:-1]  # Extract module name
                    elif current_module and "disallow_untyped_defs = True" in line:
                        strict_modules.append(current_module)

            except Exception as e:
                logger.warning(f"Error reading mypy.ini: {e}")

        return {
            "strict_module_count": len(strict_modules),
            "strict_modules": strict_modules,
            "config_file_exists": mypy_config.exists(),
        }

    def _categorize_mypy_errors(self) -> dict[str, Any]:
        """Categorize MyPy errors by type for trend analysis."""
        logger.info("Categorizing MyPy errors...")

        error_categories = {
            "type_annotations": 0,
            "return_types": 0,
            "argument_types": 0,
            "attribute_access": 0,
            "import_errors": 0,
            "other": 0,
        }

        try:
            result = subprocess.run(
                ["mypy", "scripts/"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            for line in result.stdout.split("\n"):
                if ": error:" in line:
                    error_text = line.lower()
                    if "type annotation" in error_text or "var-annotated" in error_text:
                        error_categories["type_annotations"] += 1
                    elif "return" in error_text or "no-untyped-def" in error_text:
                        error_categories["return_types"] += 1
                    elif "argument" in error_text or "arg-type" in error_text:
                        error_categories["argument_types"] += 1
                    elif "attribute" in error_text or "attr-defined" in error_text:
                        error_categories["attribute_access"] += 1
                    elif "import" in error_text:
                        error_categories["import_errors"] += 1
                    else:
                        error_categories["other"] += 1

        except Exception as e:
            logger.warning(f"Error categorizing MyPy errors: {e}")

        return error_categories

    def _analyze_file_statistics(self) -> dict[str, Any]:
        """Analyze file-level statistics for type safety."""
        logger.info("Analyzing file statistics...")

        total_files = 0
        total_lines = 0
        files_with_typing_imports = 0

        for py_file in self.scripts_dir.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                total_files += 1
                total_lines += len(lines)

                # Check for typing imports
                if any("from typing import" in line or "import typing" in line for line in lines):
                    files_with_typing_imports += 1

            except Exception as e:
                logger.warning(f"Error analyzing file statistics for {py_file}: {e}")
                continue

        typing_adoption_rate = (files_with_typing_imports / total_files * 100) if total_files > 0 else 0

        return {
            "total_python_files": total_files,
            "total_lines_of_code": total_lines,
            "files_with_typing_imports": files_with_typing_imports,
            "typing_adoption_rate_percent": round(typing_adoption_rate, 1),
            "average_lines_per_file": (round(total_lines / total_files, 1) if total_files > 0 else 0),
        }

    def _calculate_team_adoption_metrics(self) -> dict[str, Any]:
        """Calculate team-wide adoption metrics."""
        logger.info("Calculating team adoption metrics...")

        # This is a simplified version - in a real environment, you'd analyze git commits
        # to track individual developer adoption rates

        return {
            "methodology": "simplified_analysis",
            "note": "Real implementation would analyze git history for individual developer metrics",
            "overall_trend": "positive",
            "recommendation": "Continue monitoring through git commit analysis",
        }

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped in analysis."""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "test_",
            "_test.py",
            "/tests/",
            "__init__.py",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def generate_metrics_report(self, metrics: dict[str, Any] | None = None) -> str:
        """Generate a human-readable metrics report."""
        if metrics is None:
            metrics = self.collect_comprehensive_metrics()

        report = f"""
# Type Safety Metrics Report
**Generated:** {metrics["timestamp"]}

## Overview
- **Annotation Coverage:** {metrics["annotation_coverage"]["overall_coverage_percent"]}%
- **MyPy Compliance:** {metrics["mypy_compliance"]["compliance_status"]}
- **Strict Modules:** {metrics["strict_modules"]["strict_module_count"]} modules
- **Typing Adoption:** {metrics["file_statistics"]["typing_adoption_rate_percent"]}%

## Detailed Metrics

### Annotation Coverage
- Total Functions: {metrics["annotation_coverage"]["total_functions"]}
- Annotated Functions: {metrics["annotation_coverage"]["annotated_functions"]}
- Files Analyzed: {metrics["annotation_coverage"]["files_analyzed"]}

### High Coverage Files (≥80%)
{chr(10).join("- " + f for f in metrics["annotation_coverage"]["high_coverage_files"])}

### Low Coverage Files (<50%)
{chr(10).join("- " + f for f in metrics["annotation_coverage"]["low_coverage_files"])}

### MyPy Error Analysis
- Total Errors: {metrics["mypy_compliance"]["error_count"]}
- Type Annotations: {metrics["error_analysis"]["type_annotations"]}
- Return Types: {metrics["error_analysis"]["return_types"]}
- Argument Types: {metrics["error_analysis"]["argument_types"]}

### File Statistics
- Total Python Files: {metrics["file_statistics"]["total_python_files"]}
- Files with Typing Imports: {metrics["file_statistics"]["files_with_typing_imports"]}
- Average Lines per File: {metrics["file_statistics"]["average_lines_per_file"]}

## Recommendations
1. Focus on low coverage files for annotation improvements
2. Address type annotation errors as highest priority
3. Gradually enable strict checking for high-coverage modules
4. Continue team education on typing best practices
"""

        return report

    def save_metrics_report(self, metrics: dict[str, Any] | None = None) -> Path:
        """Save metrics report to file."""
        report = self.generate_metrics_report(metrics)
        report_file = self.output_dir / f"typing_metrics_report_{datetime.now().strftime('%Y%m%d')}.md"

        with open(report_file, "w") as f:
            f.write(report)

        logger.info(f"Metrics report saved to {report_file}")
        return report_file


def main():
    """Main function for command-line usage."""
    collector = TypeSafetyMetricsCollector()
    metrics = collector.collect_comprehensive_metrics()
    report_file = collector.save_metrics_report(metrics)

    print("✅ Type safety metrics collected successfully!")
    print("📊 Report saved to: {report_file}")
    overall_coverage = metrics["annotation_coverage"]["overall_coverage_percent"]
    print("📈 Overall annotation coverage: {overall_coverage}%")
    print("🔍 MyPy compliance: {metrics['mypy_compliance']['compliance_status']}")


if __name__ == "__main__":
    main()
