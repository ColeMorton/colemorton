#!/usr/bin/env python3
"""
Trade History CLI

Command-line interface for trade history image generation with:
- Automated chart selection for trade reports
- Cole Morton design system compliance
- Multiple report type support
- Production-ready visualization generation
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from trade_history_images import TradeHistoryImageGenerator  # noqa: E402
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError  # noqa: E402
from utils.config_loader import ConfigLoader  # noqa: E402


class TradeHistoryCLI(BaseFinancialCLI):
    """CLI for Trade History Image Generator service"""

    def __init__(self):
        super().__init__(
            service_name="trade_history",
            description="Trade history image generation service CLI",
        )
        self.config_loader = ConfigLoader()
        self._add_service_commands()

    def _add_service_commands(self) -> None:
        """Add Trade History specific commands"""

        @self.app.command("generate")
        def generate_images(
            date: str = typer.Argument(..., help="Date in YYYYMMDD format"),
            report_type: str = typer.Option(None, help="Specific report type to process"),
            config_file: str = typer.Option(
                "config/pipelines/dashboard_generation.yaml",
                help="Path to configuration file",
            ),
            validate_only: bool = typer.Option(False, help="Only validate setup, do not generate images"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Generate trade history images for specified date"""
            try:
                # Validate date format
                self._validate_date_format(date)

                # Validate report type if specified
                if report_type and report_type not in TradeHistoryImageGenerator.REPORT_PATTERNS:
                    available_types = list(TradeHistoryImageGenerator.REPORT_PATTERNS.keys())
                    raise ValidationError(
                        f"Invalid report type: {report_type}. Available types: {', '.join(available_types)}"
                    )

                # Load configuration
                config_path = Path(config_file)
                if not config_path.exists():
                    raise ValidationError(f"Config file does not exist: {config_file}")

                config = self._load_trade_history_config(config_path, env)

                # Initialize generator
                generator = TradeHistoryImageGenerator(config)

                if validate_only:
                    # Perform validation only
                    validation_result = generator.validate_setup(date, report_type)
                    result = {
                        "status": "validation_complete",
                        "date": date,
                        "report_type": report_type or "all",
                        "validation_passed": validation_result.get("valid", False),
                        "issues": validation_result.get("issues", []),
                    }
                else:
                    # Generate images
                    generated_files = generator.generate_images_for_date(date, report_type)

                    result = {
                        "status": "success",
                        "date": date,
                        "report_type": report_type or "all",
                        "generated_files": [str(f) for f in generated_files],
                        "file_count": len(generated_files),
                        "config_file": str(config_path),
                    }

                self._output_result(result, output_format, f"Trade History Generation: {date}")

            except Exception as e:
                self._handle_error(e, f"Failed to generate trade history images for {date}")

        @self.app.command("list-types")
        def list_report_types(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """List available report types"""
            try:
                report_types = {
                    "available_types": list(TradeHistoryImageGenerator.REPORT_PATTERNS.keys()),
                    "type_descriptions": {
                        "HISTORICAL_PERFORMANCE_REPORT": "Performance dashboard visualizations",
                        "LIVE_SIGNALS_MONITOR": "Signal chart visualizations",
                        "TRADE_ANALYSIS": "Trade distribution analysis",
                        "PORTFOLIO_SUMMARY": "Portfolio composition charts",
                        "INTERNAL_TRADING_REPORT": "Internal dashboard generation",
                    },
                    "default_behavior": "All types processed if none specified",
                }

                self._output_result(report_types, output_format, "Available Report Types")

            except Exception as e:
                self._handle_error(e, "Failed to list report types")

        @self.app.command("validate")
        def validate_setup(
            date: str = typer.Argument(..., help="Date in YYYYMMDD format"),
            report_type: str = typer.Option(None, help="Specific report type to validate"),
            config_file: str = typer.Option(
                "config/pipelines/dashboard_generation.yaml",
                help="Path to configuration file",
            ),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Validate trade history generation setup"""
            try:
                # Validate date format
                self._validate_date_format(date)

                # Load configuration
                config_path = Path(config_file)
                if not config_path.exists():
                    raise ValidationError(f"Config file does not exist: {config_file}")

                config = self._load_trade_history_config(config_path, env)

                # Initialize generator and validate
                generator = TradeHistoryImageGenerator(config)
                validation_result = generator.validate_setup(date, report_type)

                result = {
                    "status": "validation_complete",
                    "date": date,
                    "report_type": report_type or "all",
                    "config_file": str(config_path),
                    "validation_passed": validation_result.get("valid", False),
                    "issues": validation_result.get("issues", []),
                    "dependencies_available": validation_result.get("dependencies", {}),
                    "environment": env,
                }

                self._output_result(result, output_format, f"Validation: {date}")

            except Exception as e:
                self._handle_error(e, f"Failed to validate setup for {date}")

    def _validate_date_format(self, date: str) -> None:
        """Validate date format is YYYYMMDD"""
        import re

        if not re.match(r"^\d{8}$", date):
            raise ValidationError(f"Invalid date format: {date}. Expected YYYYMMDD format")

        # Try to parse as actual date
        try:
            from datetime import datetime

            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValidationError(f"Invalid date: {date}. Must be a valid date in YYYYMMDD format")

    def _load_trade_history_config(self, config_path: Path, env: str) -> dict[str, Any]:
        """Load and validate trade history configuration"""
        import yaml

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Apply environment-specific overrides
        if env in config:
            config.update(config[env])

        # Ensure required sections exist
        required_sections = ["output", "theme", "chart_engine"]
        for section in required_sections:
            if section not in config:
                raise ValidationError(f"Missing required config section: {section}")

        return config

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Trade History service health check"""
        try:
            # Check if required dependencies are available
            import matplotlib
            import numpy as np

            # Check if configuration files exist
            config_path = Path("config/pipelines/dashboard_generation.yaml")
            config_exists = config_path.exists()

            # Check if trade history directories exist
            data_dir = Path("data/outputs/trade_history")
            data_dir_exists = data_dir.exists()

            health_status = {
                "service": "trade_history",
                "status": "healthy",
                "dependencies": {
                    "matplotlib": matplotlib.__version__,
                    "numpy": np.__version__,
                },
                "configuration": {
                    "config_file_exists": config_exists,
                    "config_path": str(config_path),
                },
                "data_directories": {
                    "data_dir_exists": data_dir_exists,
                    "data_path": str(data_dir),
                },
                "report_types_available": len(TradeHistoryImageGenerator.REPORT_PATTERNS),
                "environment": env,
            }

            return health_status

        except Exception as e:
            return {
                "service": "trade_history",
                "status": "unhealthy",
                "error": str(e),
                "environment": env,
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        cache_dir = Path("data/cache/trade_history")

        if action == "clear":
            if cache_dir.exists():
                import shutil

                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
            return {
                "action": "clear",
                "status": "success",
                "message": "Trade history cache cleared",
            }
        if action == "cleanup":
            # Remove old generated files (older than 14 days)
            import os
            import time

            if cache_dir.exists():
                current_time = time.time()
                for file_path in cache_dir.rglob("*"):
                    if file_path.is_file():
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > 14 * 24 * 3600:  # 14 days
                            file_path.unlink()

            return {
                "action": "cleanup",
                "status": "success",
                "message": "Old trade history files removed",
            }
        if action == "stats":
            stats = {
                "cache_directory": str(cache_dir),
                "cache_exists": cache_dir.exists(),
                "cache_size_mb": 0,
                "report_types": list(TradeHistoryImageGenerator.REPORT_PATTERNS.keys()),
            }

            if cache_dir.exists():
                total_size = sum(file_path.stat().st_size for file_path in cache_dir.rglob("*") if file_path.is_file())
                stats["cache_size_mb"] = round(total_size / (1024 * 1024), 2)

            return {
                "action": "stats",
                "cache_info": stats,
            }
        raise ValidationError(f"Unknown cache action: {action}")


def main():
    """Main entry point for Trade History CLI"""
    cli = TradeHistoryCLI()
    cli.run()


if __name__ == "__main__":
    main()
