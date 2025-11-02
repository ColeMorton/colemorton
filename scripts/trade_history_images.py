#!/usr/bin/env python3
"""
Trade History Images Generator

Generate visualization images for trade history reports with automated chart selection
and Cole Morton design system compliance.

Usage:
    python scripts/trade_history_images.py YYYYMMDD [--report-type TYPE] [--debug] [--validate-only]
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import matplotlib


matplotlib.use("Agg")  # Use non-interactive backend

from scripts.dashboard_generator import DashboardGenerator
from scripts.utils.chart_generators import create_chart_generator

# Import existing infrastructure
from scripts.utils.config_loader import ConfigLoader
from scripts.utils.dashboard_parser import DashboardDataParser
from scripts.utils.logging_setup import setup_logging
from scripts.utils.scalability_manager import create_scalability_manager
from scripts.utils.theme_manager import create_theme_manager


class TradeHistoryImageGenerator:
    """Generator for trade history report visualizations."""

    # Report type mapping to visualization functions
    REPORT_PATTERNS = {
        "HISTORICAL_PERFORMANCE_REPORT": "performance_dashboard",
        "LIVE_SIGNALS_MONITOR": "signal_charts",
        "TRADE_ANALYSIS": "trade_distribution",
        "PORTFOLIO_SUMMARY": "portfolio_composition",
        "INTERNAL_TRADING_REPORT": "internal_dashboard",
    }

    def __init__(self, config: dict[str, Any], debug: bool = False):
        """
        Initialize the image generator.

        Args:
            config: Configuration dictionary
            debug: Enable debug logging
        """
        self.config = config
        self.debug = debug
        self.logger = logging.getLogger(__name__)

        # Initialize managers
        self.theme_manager = create_theme_manager()
        self.scalability_manager = create_scalability_manager(config)
        self.chart_generator = create_chart_generator(self.theme_manager, self.scalability_manager)
        self.parser = DashboardDataParser()

        # Base directories
        self.reports_dir = Path("data/outputs/trade_history")

    def generate_images_for_date(self, date_str: str, report_type: str | None = None) -> list[Path]:
        """
        Generate images for all reports matching the specified date.

        Args:
            date_str: Date in YYYYMMDD format
            report_type: Optional specific report type to process

        Returns:
            List of generated image file paths
        """
        # Validate date format
        try:
            datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYYMMDD.")

        # Discover reports for the date
        reports = self._discover_reports(date_str, report_type)

        if not reports:
            self.logger.warning(f"No reports found for date {date_str}")
            return []

        self.logger.info(f"Found {len(reports)} report(s) for {date_str}")

        generated_images = []

        # Process each report
        for report_path in reports:
            try:
                report_images = self._generate_images_for_report(report_path)
                generated_images.extend(report_images)

            except Exception as e:
                self.logger.error(f"Failed to generate images for {report_path.name}: {e}")
                if self.debug:
                    raise

        return generated_images

    def _discover_reports(self, date_str: str, report_type: str | None = None) -> list[Path]:
        """
        Discover trade history reports for the specified date.

        Args:
            date_str: Date string in YYYYMMDD format
            report_type: Optional specific report type filter

        Returns:
            List of report file paths
        """
        if not self.reports_dir.exists():
            self.logger.error(f"Reports directory not found: {self.reports_dir}")
            return []

        # Build search patterns
        patterns = []

        if report_type:
            if report_type in self.REPORT_PATTERNS:
                if report_type == "HISTORICAL_PERFORMANCE_REPORT":
                    # Look for historical reports in the historical subdirectory
                    patterns.append(f"historical/*{date_str}.md")
                else:
                    patterns.append(f"{report_type}*{date_str}.md")
            else:
                self.logger.warning(f"Unknown report type: {report_type}")
                return []
        else:
            # Search for all known report types
            for report_prefix in self.REPORT_PATTERNS.keys():
                if report_prefix == "HISTORICAL_PERFORMANCE_REPORT":
                    patterns.append(f"historical/*{date_str}.md")
                else:
                    patterns.append(f"{report_prefix}*{date_str}.md")

        # Find matching files (search recursively in subdirectories)
        found_reports = []
        for pattern in patterns:
            found_reports.extend(self.reports_dir.glob(pattern))
            # Also search in subdirectories
            found_reports.extend(self.reports_dir.glob(f"*/{pattern}"))

        # Sort by filename for consistent processing order
        return sorted(found_reports)

    def _generate_images_for_report(self, report_path: Path) -> list[Path]:
        """
        Generate visualization images for a single report.

        Args:
            report_path: Path to the report file

        Returns:
            List of generated image file paths
        """
        self.logger.info(f"Processing report: {report_path.name}")

        # Determine report type
        report_type = self._identify_report_type(str(report_path))
        if not report_type:
            self.logger.warning(f"Could not identify report type for: {report_path.name}")
            return []

        visualization_type = self.REPORT_PATTERNS[report_type]

        # Generate visualizations based on report type
        if visualization_type == "performance_dashboard":
            return self._generate_performance_dashboard(report_path)
        if visualization_type == "signal_charts":
            return self._generate_signal_charts(report_path)
        if visualization_type == "trade_distribution":
            return self._generate_trade_distribution(report_path)
        if visualization_type == "internal_dashboard":
            return self._generate_performance_dashboard(report_path)  # Same as performance
        self.logger.warning(f"Visualization type not implemented: {visualization_type}")
        return []

    def _identify_report_type(self, filepath: str) -> str | None:
        """
        Identify the report type from file path.

        Args:
            filepath: Report file path (can be filename or full path)

        Returns:
            Report type identifier or None
        """
        # Check if it's in the historical directory
        if "historical/" in filepath:
            return "HISTORICAL_PERFORMANCE_REPORT"

        # Check other patterns by filename
        filename = Path(filepath).name
        for report_type in self.REPORT_PATTERNS.keys():
            if filename.startswith(report_type):
                return report_type
        return None

    def _generate_performance_dashboard(self, report_path: Path) -> list[Path]:
        """
        Generate performance dashboard images using existing dashboard generator.

        Args:
            report_path: Path to the historical performance report

        Returns:
            List of generated image file paths
        """
        try:
            # Use existing dashboard generator
            generator = DashboardGenerator(self.config)

            # Generate both light and dark mode images
            generated_files = []
            output_config = self.config.get("output", {})
            dual_mode = output_config.get("dual_mode", True)

            modes = ["light", "dark"] if dual_mode else ["light"]

            for mode in modes:
                # Generate dashboard
                dashboard_path = generator.generate_dashboard(report_path, mode)

                # Create target filename based on original report
                target_path = self._create_target_path(report_path, mode)

                # Move/copy to target location with report-based naming
                if dashboard_path != target_path:
                    # Copy to target location
                    import shutil

                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(dashboard_path, target_path)
                    generated_files.append(target_path)

                    # Log the generation
                    self.logger.info(f"Generated {mode} mode dashboard: {target_path}")
                else:
                    generated_files.append(dashboard_path)

            return generated_files

        except Exception as e:
            self.logger.error(f"Failed to generate performance dashboard: {e}")
            raise

    def _generate_signal_charts(self, report_path: Path) -> list[Path]:
        """
        Generate signal monitoring charts (placeholder implementation).

        Args:
            report_path: Path to the signals report

        Returns:
            List of generated image file paths
        """
        # TODO: Implement signal-specific visualizations
        self.logger.info(f"Signal charts generation not yet implemented for {report_path.name}")
        return []

    def _generate_trade_distribution(self, report_path: Path) -> list[Path]:
        """
        Generate trade distribution charts (placeholder implementation).

        Args:
            report_path: Path to the trade analysis report

        Returns:
            List of generated image file paths
        """
        # TODO: Implement trade distribution visualizations
        self.logger.info(f"Trade distribution charts not yet implemented for {report_path.name}")
        return []

    def _create_target_path(self, report_path: Path, mode: str) -> Path:
        """
        Create target path for generated image based on original report filename.

        Args:
            report_path: Original report path
            mode: Visualization mode ('light' or 'dark')

        Returns:
            Target path for the generated image
        """
        # Extract date from report filename (for potential future use)
        # date_match = re.search(r"(\d{8})", report_path.name)

        # Create filename based on report type
        base_name = report_path.stem  # filename without .md extension

        if mode == "dark":
            image_name = f"{base_name}-dark.png"
        else:
            image_name = f"{base_name}-light.png"

        # Place images in same directory as reports
        return report_path.parent / image_name

    def validate_setup(self) -> bool:
        """
        Validate that all required components are properly configured.

        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Check reports directory
            if not self.reports_dir.exists():
                self.logger.error(f"Reports directory not found: {self.reports_dir}")
                return False

            # Validate theme manager
            if not self.theme_manager.validate_colors():
                self.logger.error("Theme manager color validation failed")
                return False

            # Check configuration
            if not self.config.get("design_system"):
                self.logger.warning("Design system configuration not found")

            self.logger.info("Setup validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Setup validation failed: {e}")
            return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", help="Date in YYYYMMDD format")
    parser.add_argument(
        "--report-type",
        choices=list(TradeHistoryImageGenerator.REPORT_PATTERNS.keys()),
        help="Specific report type to process",
    )
    parser.add_argument(
        "--config",
        default="config/pipelines/dashboard_generation.yaml",
        help="Path to configuration file",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate setup, do not generate images",
    )
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment configuration",
    )

    args = parser.parse_args()

    try:
        # Setup logging
        log_level = "DEBUG" if args.debug else "INFO"
        setup_logging(level=log_level)

        # Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load_with_environment(args.config, args.env)

        # Initialize generator
        generator = TradeHistoryImageGenerator(config, debug=args.debug)

        # Validate setup
        if not generator.validate_setup():
            print("❌ Setup validation failed")
            sys.exit(1)

        if args.validate_only:
            print("✅ Setup validation successful")
            sys.exit(0)

        # Generate images
        generated_images = generator.generate_images_for_date(args.date, args.report_type)

        if generated_images:
            print("✅ Successfully generated {len(generated_images)} image(s):")
            for image_path in generated_images:
                print("   {image_path}")
        else:
            print("⚠️  No images generated")

    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
