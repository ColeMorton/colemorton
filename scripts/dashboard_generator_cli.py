#!/usr/bin/env python3
"""
Dashboard Generator CLI

Command-line interface for dashboard generation with:
- High-resolution performance overview visualizations
- Scalable Sensylate design system integration
- Light/dark mode generation
- Production-ready chart generation
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard_generator import main as dashboard_main  # noqa: E402
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError  # noqa: E402
from utils.config_loader import ConfigLoader  # noqa: E402


class DashboardGeneratorCLI(BaseFinancialCLI):
    """CLI for Dashboard Generator service"""

    def __init__(self):
        super().__init__(
            service_name="dashboard_generator",
            description="Scalable dashboard generation service CLI",
        )
        self.config_loader = ConfigLoader()
        self._add_service_commands()

    def _add_service_commands(self) -> None:
        """Add Dashboard Generator specific commands"""

        @self.app.command("generate")
        def generate_dashboard(
            input_file: str = typer.Argument(..., help="Input historical performance markdown file"),
            mode: str = typer.Option("both", help="Dashboard mode (light/dark/both)"),
            output_dir: str = typer.Option(None, help="Output directory override"),
            config_file: str = typer.Option(
                "config/pipelines/dashboard_generation.yaml",
                help="Path to YAML configuration file",
            ),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Generate dashboard images from historical performance data"""
            try:
                # Validate inputs
                input_path = Path(input_file)
                if not input_path.exists():
                    raise ValidationError(f"Input file does not exist: {input_file}")

                if mode not in ["light", "dark", "both"]:
                    raise ValidationError(f"Invalid mode: {mode}. Must be light, dark, or both")

                # Load configuration
                config_path = Path(config_file)
                if not config_path.exists():
                    raise ValidationError(f"Config file does not exist: {config_file}")

                # Load and validate configuration
                config = self._load_dashboard_config(config_path, env)

                # Set output directory if provided
                output_path = Path(output_dir) if output_dir else None

                # Generate dashboard
                generated_files = dashboard_main(
                    config=config,
                    input_file=input_path,
                    mode=mode,
                    output_dir=output_path,
                )

                result = {
                    "status": "success",
                    "mode": mode,
                    "input_file": str(input_path),
                    "output_directory": output_dir or config.get("output", {}).get("directory", ""),
                    "generated_files": [str(f) for f in generated_files],
                    "file_count": len(generated_files),
                }

                self._output_result(result, output_format, f"Dashboard Generation: {mode} mode")

            except Exception as e:
                self._handle_error(e, f"Failed to generate dashboard for {input_file}")

        @self.app.command("validate")
        def validate_config(
            config_file: str = typer.Option(
                "config/pipelines/dashboard_generation.yaml",
                help="Path to YAML configuration file",
            ),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Validate dashboard generation configuration"""
            try:
                config_path = Path(config_file)
                if not config_path.exists():
                    raise ValidationError(f"Config file does not exist: {config_file}")

                # Load and validate configuration
                config = self._load_dashboard_config(config_path, env)

                result = {
                    "status": "valid",
                    "config_file": str(config_path),
                    "environment": env,
                    "output_directory": config.get("output", {}).get("directory", ""),
                    "theme_settings": config.get("theme", {}),
                    "chart_engine": config.get("chart_engine", "matplotlib"),
                    "validation_passed": True,
                }

                self._output_result(result, output_format, "Configuration Validation")

            except Exception as e:
                self._handle_error(e, f"Failed to validate config {config_file}")

        @self.app.command("list-themes")
        def list_themes(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """List available dashboard themes"""
            try:
                themes = {
                    "available_themes": ["light", "dark"],
                    "default_theme": "light",
                    "theme_features": {
                        "light": {
                            "background": "white",
                            "text_color": "dark",
                            "accent_color": "blue",
                        },
                        "dark": {
                            "background": "dark",
                            "text_color": "white",
                            "accent_color": "cyan",
                        },
                    },
                    "font_system": "Heebo with fallbacks",
                }

                self._output_result(themes, output_format, "Available Dashboard Themes")

            except Exception as e:
                self._handle_error(e, "Failed to list dashboard themes")

    def _load_dashboard_config(self, config_path: Path, env: str) -> dict[str, Any]:
        """Load and validate dashboard configuration"""
        import yaml
        from utils.config_validator import validate_dashboard_config

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Apply environment-specific overrides
        if env in config:
            config.update(config[env])

        # Validate configuration
        validate_dashboard_config(config)

        return config

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Dashboard Generator service health check"""
        try:
            # Check if required dependencies are available
            import matplotlib
            import numpy as np

            # Check if configuration files exist
            config_path = Path("config/pipelines/dashboard_generation.yaml")
            config_exists = config_path.exists()

            # Check output directory permissions
            health_status = {
                "service": "dashboard_generator",
                "status": "healthy",
                "dependencies": {
                    "matplotlib": matplotlib.__version__,
                    "numpy": np.__version__,
                },
                "configuration": {
                    "config_file_exists": config_exists,
                    "config_path": str(config_path),
                },
                "theme_system": {
                    "theme_manager_available": True,
                    "font_system": "Heebo with fallbacks",
                },
                "environment": env,
            }

            return health_status

        except Exception as e:
            return {
                "service": "dashboard_generator",
                "status": "unhealthy",
                "error": str(e),
                "environment": env,
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        cache_dir = Path("data/cache/dashboard_generation")

        if action == "clear":
            if cache_dir.exists():
                import shutil

                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
            return {
                "action": "clear",
                "status": "success",
                "message": "Dashboard generation cache cleared",
            }
        if action == "cleanup":
            # Remove old generated files (older than 7 days)
            import os
            import time

            if cache_dir.exists():
                current_time = time.time()
                for file_path in cache_dir.rglob("*"):
                    if file_path.is_file():
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > 7 * 24 * 3600:  # 7 days
                            file_path.unlink()

            return {
                "action": "cleanup",
                "status": "success",
                "message": "Old dashboard files removed",
            }
        if action == "stats":
            stats = {
                "cache_directory": str(cache_dir),
                "cache_exists": cache_dir.exists(),
                "cache_size_mb": 0,
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
    """Main entry point for Dashboard Generator CLI"""
    cli = DashboardGeneratorCLI()
    cli.run()


if __name__ == "__main__":
    main()
