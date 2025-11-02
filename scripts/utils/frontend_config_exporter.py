#!/usr/bin/env python3
"""
Frontend Configuration Exporter for chart configurations.

This module exports chart configurations in frontend-consumable format,
enabling seamless integration between Python chart generation and
JavaScript/React frontend components.
"""

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    QualityDistribution,
    TradeData,
)
from scripts.utils.json_schema_generator import create_json_schema_generator


class FrontendConfigExporter:
    """Exports chart configurations for frontend consumption."""

    def __init__(self, theme_manager=None, schema_generator=None):
        """
        Initialize frontend configuration exporter.

        Args:
            theme_manager: Optional theme manager instance
            schema_generator: Optional JSON schema generator instance
        """
        self.theme_manager = theme_manager
        self.schema_generator = schema_generator or create_json_schema_generator(theme_manager)
        self.export_history = []

    def export_chart_config(
        self,
        chart_type: str,
        data: list[MonthlyPerformance] | list[QualityDistribution] | list[TradeData],
        theme_mode: str = "light",
        layout_options: dict[str, Any] | None = None,
        styling_options: dict[str, Any] | None = None,
        export_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Export chart configuration for frontend consumption.

        Args:
            chart_type: Type of chart to configure
            data: Chart data
            theme_mode: Theme mode ('light' or 'dark')
            layout_options: Optional layout configuration
            styling_options: Optional styling configuration
            export_options: Optional export configuration

        Returns:
            Frontend-ready chart configuration
        """
        # Convert data to dictionary format
        data_dict = []
        for item in data:
            if hasattr(item, "__dict__"):
                data_dict.append(asdict(item))
            elif isinstance(item, dict):
                data_dict.append(item)
            else:
                # Try to convert to dict
                try:
                    data_dict.append(dict(item))
                except:
                    data_dict.append(str(item))

        # Build base configuration
        config = {
            "chart_type": self._normalize_chart_type(chart_type),
            "data": data_dict,
            "theme": self._build_theme_config(theme_mode),
            "layout": self._build_layout_config(chart_type, layout_options),
            "styling": self._build_styling_config(chart_type, styling_options),
            "export": self._build_export_config(export_options),
            "metadata": self._build_metadata_config(chart_type),
        }

        # Add chart-specific configurations
        if chart_type.lower() in ["waterfall", "waterfall_chart"]:
            config["scalability"] = self._build_scalability_config()
        elif chart_type.lower() in ["scatter", "enhanced_scatter"]:
            config["clustering"] = self._build_clustering_config()

        return config

    def _normalize_chart_type(self, chart_type: str) -> str:
        """Normalize chart type name for frontend consistency."""
        type_mapping = {
            "monthly_bars": "enhanced_monthly_bars",
            "donut": "enhanced_donut_chart",
            "donut_chart": "enhanced_donut_chart",
            "waterfall": "waterfall_chart",
            "scatter": "enhanced_scatter",
            "scatter_plot": "enhanced_scatter",
        }

        normalized = chart_type.lower().replace("create_", "").replace("enhanced_", "")
        return type_mapping.get(normalized, chart_type)

    def _build_theme_config(self, mode: str) -> dict[str, Any]:
        """Build theme configuration section."""
        theme_config = {
            "mode": mode,
            "template": f"sensylate_{mode}",
            "high_dpi": False,
            "dashboard_optimized": False,
        }

        # Add color configuration if theme manager available
        if self.theme_manager:
            try:
                colors = self.theme_manager.get_theme_colors(mode)
                theme_config["colors"] = {
                    "primary": getattr(colors, "primary_data", "#3179f5"),
                    "secondary": getattr(colors, "secondary_data", "#26c6da"),
                    "background": getattr(colors, "background", "#ffffff"),
                    "text": getattr(colors, "primary_text", "#121212"),
                    "borders": getattr(colors, "borders", "#eaeaea"),
                }
            except:
                # Fallback color configuration
                theme_config["colors"] = {
                    "primary": "#3179f5",
                    "secondary": "#26c6da",
                    "background": "#ffffff" if mode == "light" else "#121212",
                    "text": "#121212" if mode == "light" else "#ffffff",
                    "borders": "#eaeaea" if mode == "light" else "#333333",
                }

        # Add typography configuration
        theme_config["typography"] = {
            "font_family": "Heebo, -apple-system, BlinkMacSystemFont, sans-serif",
            "font_sizes": {"title": 20, "subtitle": 16, "body": 12, "axis_labels": 10},
        }

        return theme_config

    def _build_layout_config(self, chart_type: str, options: dict[str, Any] | None) -> dict[str, Any]:
        """Build layout configuration section."""
        defaults = {
            "width": 800,
            "height": 600,
            "title": f"{chart_type.replace('_', ' ').title()} Analysis",
            "responsive": True,
        }

        # Chart-specific layout defaults
        if "monthly" in chart_type.lower():
            defaults.update(
                {
                    "show_dual_axis": True,
                    "show_market_conditions": True,
                    "bar_spacing": 0.1,
                }
            )
        elif "donut" in chart_type.lower():
            defaults.update({"show_center_text": True, "show_legend": True, "donut_hole_size": 0.4})
        elif "waterfall" in chart_type.lower():
            defaults.update(
                {
                    "show_cumulative_line": True,
                    "show_performance_zones": True,
                    "show_breakeven_line": True,
                }
            )
        elif "scatter" in chart_type.lower():
            defaults.update(
                {
                    "show_trend_line": True,
                    "show_quality_legend": True,
                    "show_outlier_labels": True,
                }
            )

        # Merge with provided options
        if options:
            defaults.update(options)

        return defaults

    def _build_styling_config(self, chart_type: str, options: dict[str, Any] | None) -> dict[str, Any]:
        """Build styling configuration section."""
        defaults = {"opacity": 0.8, "border_width": 1}

        # Chart-specific styling defaults
        if "monthly" in chart_type.lower():
            defaults.update({"text_threshold": 5.0, "gradient_intensity": 0.3})
        elif "donut" in chart_type.lower():
            defaults.update(
                {
                    "pull_effect": 0.05,
                    "text_font_size": 12,
                    "border_width": 2,
                    "hover_effect": True,
                }
            )
        elif "waterfall" in chart_type.lower():
            defaults.update(
                {
                    "bar_opacity": 0.8,
                    "line_width": 3,
                    "annotation_threshold": 2.0,
                    "marker_size": 6,
                }
            )
        elif "scatter" in chart_type.lower():
            defaults.update({"base_marker_size": 15, "size_scaling_factor": 20, "border_width": 0.8})

        # Merge with provided options
        if options:
            defaults.update(options)

        return defaults

    def _build_export_config(self, options: dict[str, Any] | None) -> dict[str, Any]:
        """Build export configuration section."""
        defaults = {
            "formats": ["png"],
            "quality": {
                "width": 1600,
                "height": 1200,
                "scale": 2,
                "dpi_equivalent": 192,
            },
            "output": {
                "directory": "data/outputs/charts",
                "filename_pattern": "{chart_type}_{timestamp}",
                "include_timestamp": True,
            },
        }

        # Merge with provided options
        if options:
            defaults.update(options)

        return defaults

    def _build_scalability_config(self) -> dict[str, Any]:
        """Build scalability configuration for waterfall charts."""
        return {"max_bars": 50, "use_performance_bands": False, "volume_threshold": 100}

    def _build_clustering_config(self) -> dict[str, Any]:
        """Build clustering configuration for scatter charts."""
        return {
            "enabled": False,
            "min_samples": 5,
            "eps": 2.5,
            "show_centroids": True,
            "volume_threshold": 100,
        }

    def _build_metadata_config(self, chart_type: str) -> dict[str, Any]:
        """Build metadata configuration section."""
        return {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "schema_version": "1.0.0",
            "chart_engine": "plotly",
            "export_format": "frontend_config",
            "compatible_frameworks": ["react", "vue", "angular"],
            "plotly_version": "5.24.1",
        }

    def export_dashboard_config(
        self,
        charts: list[dict[str, Any]],
        layout_options: dict[str, Any] | None = None,
        theme_mode: str = "light",
    ) -> dict[str, Any]:
        """
        Export complete dashboard configuration.

        Args:
            charts: List of chart configurations
            layout_options: Optional dashboard layout options
            theme_mode: Theme mode for dashboard

        Returns:
            Complete dashboard configuration
        """
        dashboard_config = {
            "dashboard_type": "multi_chart_dashboard",
            "layout": self._build_dashboard_layout_config(layout_options),
            "theme": self._build_theme_config(theme_mode),
            "charts": charts,
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_charts": len(charts),
                "schema_version": "1.0.0",
                "dashboard_engine": "plotly_subplots",
            },
        }

        return dashboard_config

    def _build_dashboard_layout_config(self, options: dict[str, Any] | None) -> dict[str, Any]:
        """Build dashboard layout configuration."""
        defaults = {
            "grid": {
                "rows": 3,
                "cols": 2,
                "height_ratios": [0.2, 0.4, 0.4],
                "width_ratios": None,
            },
            "spacing": {"horizontal": 0.15, "vertical": 0.1},
            "figure_size": [16, 12],
            "responsive": {
                "enabled": True,
                "breakpoints": {
                    "mobile": 480,
                    "tablet": 768,
                    "desktop": 1200,
                    "large": 1920,
                },
            },
        }

        if options:
            defaults.update(options)

        return defaults

    def save_config_to_file(
        self,
        config: dict[str, Any],
        filename: str,
        output_dir: str = "data/outputs/frontend_configs",
    ) -> str:
        """
        Save configuration to JSON file.

        Args:
            config: Configuration to save
            filename: Output filename
            output_dir: Output directory

        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / filename

        with open(filepath, "w") as f:
            json.dump(config, f, indent=2, default=str)

        # Track export history
        self.export_history.append(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "filename": filename,
                "filepath": str(filepath),
                "config_type": config.get("chart_type", "unknown"),
            }
        )

        return str(filepath)

    def batch_export_configs(
        self,
        chart_configs: dict[str, dict[str, Any]],
        output_dir: str = "data/outputs/frontend_configs",
    ) -> dict[str, str]:
        """
        Export multiple chart configurations in batch.

        Args:
            chart_configs: Dictionary mapping names to configurations
            output_dir: Output directory

        Returns:
            Dictionary mapping config names to file paths
        """
        exported_files = {}

        for name, config in chart_configs.items():
            filename = f"{name.lower().replace(' ', '_')}_config.json"
            filepath = self.save_config_to_file(config, filename, output_dir)
            exported_files[name] = filepath

        return exported_files

    def validate_config(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration against schema.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        chart_type = config.get("chart_type", "")

        # Map to schema names
        schema_mapping = {
            "enhanced_monthly_bars": "EnhancedMonthlyBars",
            "enhanced_donut_chart": "EnhancedDonutChart",
            "waterfall_chart": "WaterfallChart",
            "enhanced_scatter": "EnhancedScatter",
        }

        schema_name = schema_mapping.get(chart_type)
        if not schema_name:
            return False, [f"Unknown chart type: {chart_type}"]

        return self.schema_generator.validate_chart_config(config, schema_name)

    def generate_react_component_props(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Generate React component props from configuration.

        Args:
            config: Chart configuration

        Returns:
            React component props
        """
        props = {
            "chartType": config.get("chart_type"),
            "data": config.get("data", []),
            "theme": config.get("theme", {}),
            "layout": config.get("layout", {}),
            "styling": config.get("styling", {}),
            "responsive": config.get("layout", {}).get("responsive", True),
            "exportOptions": config.get("export", {}),
        }

        # Add chart-specific props
        chart_type = config.get("chart_type", "")

        if "waterfall" in chart_type:
            props["scalabilityOptions"] = config.get("scalability", {})
        elif "scatter" in chart_type:
            props["clusteringOptions"] = config.get("clustering", {})

        return props

    def get_export_history(self) -> list[dict[str, Any]]:
        """
        Get export history.

        Returns:
            List of export history entries
        """
        return self.export_history.copy()


def create_frontend_config_exporter(theme_manager=None) -> FrontendConfigExporter:
    """
    Factory function to create a FrontendConfigExporter instance.

    Args:
        theme_manager: Optional theme manager instance

    Returns:
        Configured FrontendConfigExporter instance
    """
    return FrontendConfigExporter(theme_manager)


if __name__ == "__main__":
    # Test frontend configuration export
    from scripts.utils.theme_manager import create_theme_manager

    theme_manager = create_theme_manager()
    exporter = create_frontend_config_exporter(theme_manager)

    # Test monthly performance data
    monthly_data = [
        MonthlyPerformance("January", 2024, 15, 73.3, 4.2, "Bullish"),
        MonthlyPerformance("February", 2024, 12, 58.3, -1.1, "Bearish"),
    ]

    # Export configuration
    config = exporter.export_chart_config(chart_type="enhanced_monthly_bars", data=monthly_data, theme_mode="light")

    print("📊 Generated Frontend Configuration:")
    print("  Chart Type: {config['chart_type']}")
    print("  Data Points: {len(config['data'])}")
    print("  Theme Mode: {config['theme']['mode']}")
    print("  Layout Options: {len(config['layout'])} settings")

    # Validate configuration
    is_valid, errors = exporter.validate_config(config)
    print("\n✅ Configuration Valid: {is_valid}")
    if errors:
        print("❌ Validation Errors: {errors}")

    # Generate React props
    react_props = exporter.generate_react_component_props(config)
    print("\n⚛️  React Props Generated: {len(react_props)} properties")
