#!/usr/bin/env python3
"""
Wrapper script for generating reports with integrated dashboard visualization.

This script combines the existing report generation workflow with dashboard
generation to provide a complete reporting solution.

Usage:
    python scripts/generate_report_with_dashboard.py \\
        --config config/pipelines/report_generation.yaml \\
        --input data/processed/features.parquet \\
        --env prod
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from scripts.dashboard_generator import main as generate_dashboard
from scripts.report_generation import main as generate_report
from scripts.utils.config_loader import ConfigLoader
from scripts.utils.logging_setup import setup_logging


class IntegratedReportGenerator:
    """Integrated report and dashboard generation."""

    def __init__(self, report_config: dict[str, Any], dashboard_config: dict[str, Any]):
        """
        Initialize integrated generator.

        Args:
            report_config: Report generation configuration
            dashboard_config: Dashboard generation configuration
        """
        self.report_config = report_config
        self.dashboard_config = dashboard_config
        self.logger = logging.getLogger(__name__)

    def generate_integrated_report(self, input_file: Path, output_dir: Path | None = None) -> dict[str, list[Path]]:
        """
        Generate report with integrated dashboard.

        Args:
            input_file: Input data file
            output_dir: Optional output directory override

        Returns:
            Dictionary with report and dashboard file paths
        """
        generated_files = {"reports": [], "dashboards": []}

        # Step 1: Generate standard report
        self.logger.info("Generating standard report...")
        try:
            report_file = generate_report(self.report_config, input_file)
            generated_files["reports"].append(report_file)
            self.logger.info(f"Report generated: {report_file}")
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

        # Step 2: Check if we have historical performance data for dashboard
        historical_files = self._find_historical_performance_files()

        if not historical_files:
            self.logger.warning("No historical performance files found for dashboard generation")
            return generated_files

        # Step 3: Generate dashboards for available historical data
        self.logger.info("Generating performance dashboards...")
        for hist_file in historical_files:
            try:
                dashboard_files = generate_dashboard(
                    self.dashboard_config, hist_file, mode="both", output_dir=output_dir
                )
                generated_files["dashboards"].extend(dashboard_files)
                self.logger.info(f"Dashboards generated from {hist_file}: {len(dashboard_files)} files")
            except Exception as e:
                self.logger.warning(f"Dashboard generation failed for {hist_file}: {e}")
                # Continue with other files

        return generated_files

    def _find_historical_performance_files(self) -> list[Path]:
        """Find available historical performance markdown files."""
        hist_dir = Path("data/outputs/trade_history")

        if not hist_dir.exists():
            return []

        # Look for historical performance report files
        patterns = ["HISTORICAL_PERFORMANCE_REPORT_*.md", "historical_performance_*.md"]

        files = []
        for pattern in patterns:
            files.extend(hist_dir.glob(pattern))

        # Sort by modification time, newest first
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return files[:3]  # Limit to 3 most recent files


def main(
    report_config: dict[str, Any],
    dashboard_config: dict[str, Any],
    input_file: Path,
    output_dir: Path | None = None,
) -> dict[str, list[Path]]:
    """
    Main execution function.

    Args:
        report_config: Report generation configuration
        dashboard_config: Dashboard generation configuration
        input_file: Input data file
        output_dir: Optional output directory override

    Returns:
        Dictionary with generated file paths
    """
    generator = IntegratedReportGenerator(report_config, dashboard_config)
    generated_files = generator.generate_integrated_report(input_file, output_dir)

    # Print Make-compatible output
    total_files = len(generated_files["reports"]) + len(generated_files["dashboards"])
    print("TOTAL_FILES_GENERATED={total_files}")

    for i, report_file in enumerate(generated_files["reports"]):
        print("REPORT_FILE_{i+1}={report_file}")

    for i, dashboard_file in enumerate(generated_files["dashboards"]):
        print("DASHBOARD_FILE_{i+1}={dashboard_file}")

    return generated_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-config",
        default="config/pipelines/report_generation.yaml",
        help="Path to report generation YAML configuration file",
    )
    parser.add_argument(
        "--dashboard-config",
        default="config/pipelines/dashboard_generation.yaml",
        help="Path to dashboard generation YAML configuration file",
    )
    parser.add_argument("--input", required=True, help="Input data file for report generation")
    parser.add_argument("--output-dir", help="Output directory override (default from configs)")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment configuration",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress non-essential output")

    args = parser.parse_args()

    try:
        # Load configurations
        config_loader = ConfigLoader()
        report_config = config_loader.load_with_environment(args.report_config, args.env)
        dashboard_config = config_loader.load_with_environment(args.dashboard_config, args.env)

        # Setup logging
        if args.quiet:
            logging.getLogger().setLevel(logging.WARNING)
        else:
            setup_logging(level=args.log_level)

        # Validate input
        input_path = Path(args.input)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        output_dir = Path(args.output_dir) if args.output_dir else None

        # Generate integrated report
        generated_files = main(report_config, dashboard_config, input_path, output_dir)

        total_reports = len(generated_files["reports"])
        total_dashboards = len(generated_files["dashboards"])

        if not args.quiet:
            print(f"✅ Successfully generated {total_reports} report(s) and {total_dashboards} dashboard(s)")

    except Exception as e:
        logging.error(f"Integrated report generation failed: {e}")
        sys.exit(1)
