#!/usr/bin/env python3
"""
JSON Schema Generator for Plotly chart configurations.

This module creates comprehensive JSON schemas for all chart types to enable
seamless frontend integration and configuration sharing between Python backend
and JavaScript frontend.
"""

import json
from pathlib import Path
from typing import Any


class JSONSchemaGenerator:
    """Generates JSON schemas for chart configurations and data structures."""

    def __init__(self, theme_manager=None):
        """
        Initialize JSON schema generator.

        Args:
            theme_manager: Optional theme manager for color schema generation
        """
        self.theme_manager = theme_manager
        self.schemas = {}
        self._generate_all_schemas()

    def _generate_all_schemas(self):
        """Generate all JSON schemas for chart types and data structures."""
        # Data structure schemas
        self.schemas["MonthlyPerformance"] = self._generate_monthly_performance_schema()
        self.schemas["QualityDistribution"] = self._generate_quality_distribution_schema()
        self.schemas["TradeData"] = self._generate_trade_data_schema()

        # Chart configuration schemas
        self.schemas["EnhancedMonthlyBars"] = self._generate_monthly_bars_config_schema()
        self.schemas["EnhancedDonutChart"] = self._generate_donut_chart_config_schema()
        self.schemas["WaterfallChart"] = self._generate_waterfall_chart_config_schema()
        self.schemas["EnhancedScatter"] = self._generate_scatter_chart_config_schema()

        # Dashboard and layout schemas
        self.schemas["DashboardLayout"] = self._generate_dashboard_layout_schema()
        self.schemas["ThemeConfiguration"] = self._generate_theme_config_schema()
        self.schemas["ExportConfiguration"] = self._generate_export_config_schema()

    def _generate_monthly_performance_schema(self) -> dict[str, Any]:
        """Generate schema for MonthlyPerformance data structure."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Monthly Performance Data",
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "description": "Month name (e.g., 'January')",
                },
                "year": {"type": "integer", "description": "Year (e.g., 2024)"},
                "trades": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of trades in the month",
                },
                "win_rate": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Win rate percentage (0-100)",
                },
                "return_pct": {
                    "type": "number",
                    "description": "Monthly return percentage",
                },
                "market_condition": {
                    "type": "string",
                    "enum": ["Bullish", "Bearish", "Sideways", "Volatile"],
                    "description": "Market condition assessment",
                },
            },
            "required": [
                "month",
                "year",
                "trades",
                "win_rate",
                "return_pct",
                "market_condition",
            ],
            "additionalProperties": False,
        }

    def _generate_quality_distribution_schema(self) -> dict[str, Any]:
        """Generate schema for QualityDistribution data structure."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Quality Distribution Data",
            "type": "object",
            "properties": {
                "quality": {
                    "type": "string",
                    "enum": ["Excellent", "Good", "Poor", "Failed", "Poor Setup"],
                    "description": "Trade quality category",
                },
                "count": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of trades in this quality category",
                },
                "percentage": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Percentage of total trades",
                },
                "win_rate": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Win rate for this quality category",
                },
                "avg_return": {
                    "type": "number",
                    "description": "Average return for this quality category",
                },
            },
            "required": ["quality", "count", "percentage", "win_rate", "avg_return"],
            "additionalProperties": False,
        }

    def _generate_trade_data_schema(self) -> dict[str, Any]:
        """Generate schema for TradeData structure."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Trade Data",
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "entry_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Trade entry date (YYYY-MM-DD)",
                },
                "exit_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Trade exit date (YYYY-MM-DD)",
                },
                "duration": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Trade duration in days",
                },
                "return_pct": {
                    "type": "number",
                    "description": "Trade return percentage",
                },
                "quality": {
                    "type": "string",
                    "enum": ["Excellent", "Good", "Poor", "Failed", "Poor Setup"],
                    "description": "Trade quality assessment",
                },
                "entry_price": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Entry price per share",
                },
                "exit_price": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Exit price per share",
                },
                "position_size": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Position size in dollars",
                },
            },
            "required": [
                "ticker",
                "entry_date",
                "exit_date",
                "duration",
                "return_pct",
                "quality",
            ],
            "additionalProperties": False,
        }

    def _generate_monthly_bars_config_schema(self) -> dict[str, Any]:
        """Generate schema for enhanced monthly bars chart configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Enhanced Monthly Bars Chart Configuration",
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "const": "enhanced_monthly_bars"},
                "data": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/MonthlyPerformance"},
                    "minItems": 1,
                    "description": "Array of monthly performance data",
                },
                "theme": {"$ref": "#/$defs/ThemeConfig"},
                "layout": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "width": {"type": "integer", "minimum": 100},
                        "height": {"type": "integer", "minimum": 100},
                        "show_dual_axis": {"type": "boolean", "default": True},
                        "show_market_conditions": {"type": "boolean", "default": True},
                        "bar_spacing": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.1,
                        },
                    },
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "opacity": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.8,
                        },
                        "border_width": {"type": "number", "minimum": 0, "default": 1},
                        "text_threshold": {"type": "number", "default": 5.0},
                        "gradient_intensity": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.3,
                        },
                    },
                },
                "export": {"$ref": "#/$defs/ExportConfig"},
            },
            "required": ["chart_type", "data"],
            "$defs": {
                "MonthlyPerformance": self.schemas.get("MonthlyPerformance", {}),
                "ThemeConfig": self._get_theme_config_def(),
                "ExportConfig": self._get_export_config_def(),
            },
        }

    def _generate_donut_chart_config_schema(self) -> dict[str, Any]:
        """Generate schema for enhanced donut chart configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Enhanced Donut Chart Configuration",
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "const": "enhanced_donut_chart"},
                "data": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/QualityDistribution"},
                    "minItems": 1,
                    "description": "Array of quality distribution data",
                },
                "theme": {"$ref": "#/$defs/ThemeConfig"},
                "layout": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "width": {"type": "integer", "minimum": 100},
                        "height": {"type": "integer", "minimum": 100},
                        "show_center_text": {"type": "boolean", "default": True},
                        "show_legend": {"type": "boolean", "default": True},
                        "donut_hole_size": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 0.9,
                            "default": 0.4,
                        },
                    },
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "pull_effect": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 0.3,
                            "default": 0.05,
                        },
                        "text_font_size": {
                            "type": "integer",
                            "minimum": 8,
                            "default": 12,
                        },
                        "border_width": {"type": "number", "minimum": 0, "default": 2},
                        "hover_effect": {"type": "boolean", "default": True},
                    },
                },
                "export": {"$ref": "#/$defs/ExportConfig"},
            },
            "required": ["chart_type", "data"],
            "$defs": {
                "QualityDistribution": self.schemas.get("QualityDistribution", {}),
                "ThemeConfig": self._get_theme_config_def(),
                "ExportConfig": self._get_export_config_def(),
            },
        }

    def _generate_waterfall_chart_config_schema(self) -> dict[str, Any]:
        """Generate schema for waterfall chart configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Waterfall Chart Configuration",
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "const": "waterfall_chart"},
                "data": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/TradeData"},
                    "minItems": 1,
                    "description": "Array of trade data",
                },
                "theme": {"$ref": "#/$defs/ThemeConfig"},
                "layout": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "width": {"type": "integer", "minimum": 100},
                        "height": {"type": "integer", "minimum": 100},
                        "show_cumulative_line": {"type": "boolean", "default": True},
                        "show_performance_zones": {"type": "boolean", "default": True},
                        "show_breakeven_line": {"type": "boolean", "default": True},
                    },
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "bar_opacity": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.8,
                        },
                        "line_width": {"type": "number", "minimum": 1, "default": 3},
                        "annotation_threshold": {"type": "number", "default": 2.0},
                        "marker_size": {"type": "number", "minimum": 2, "default": 6},
                    },
                },
                "scalability": {
                    "type": "object",
                    "properties": {
                        "max_bars": {"type": "integer", "minimum": 10, "default": 50},
                        "use_performance_bands": {"type": "boolean", "default": False},
                        "volume_threshold": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 100,
                        },
                    },
                },
                "export": {"$ref": "#/$defs/ExportConfig"},
            },
            "required": ["chart_type", "data"],
            "$defs": {
                "TradeData": self.schemas.get("TradeData", {}),
                "ThemeConfig": self._get_theme_config_def(),
                "ExportConfig": self._get_export_config_def(),
            },
        }

    def _generate_scatter_chart_config_schema(self) -> dict[str, Any]:
        """Generate schema for enhanced scatter chart configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Enhanced Scatter Chart Configuration",
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "const": "enhanced_scatter"},
                "data": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/TradeData"},
                    "minItems": 1,
                    "description": "Array of trade data",
                },
                "theme": {"$ref": "#/$defs/ThemeConfig"},
                "layout": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "width": {"type": "integer", "minimum": 100},
                        "height": {"type": "integer", "minimum": 100},
                        "show_trend_line": {"type": "boolean", "default": True},
                        "show_quality_legend": {"type": "boolean", "default": True},
                        "show_outlier_labels": {"type": "boolean", "default": True},
                    },
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "base_marker_size": {
                            "type": "number",
                            "minimum": 5,
                            "default": 15,
                        },
                        "size_scaling_factor": {
                            "type": "number",
                            "minimum": 1,
                            "default": 20,
                        },
                        "opacity": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.8,
                        },
                        "border_width": {
                            "type": "number",
                            "minimum": 0,
                            "default": 0.8,
                        },
                    },
                },
                "clustering": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "min_samples": {"type": "integer", "minimum": 2, "default": 5},
                        "eps": {"type": "number", "minimum": 0.1, "default": 2.5},
                        "show_centroids": {"type": "boolean", "default": True},
                        "volume_threshold": {
                            "type": "integer",
                            "minimum": 50,
                            "default": 100,
                        },
                    },
                },
                "export": {"$ref": "#/$defs/ExportConfig"},
            },
            "required": ["chart_type", "data"],
            "$defs": {
                "TradeData": self.schemas.get("TradeData", {}),
                "ThemeConfig": self._get_theme_config_def(),
                "ExportConfig": self._get_export_config_def(),
            },
        }

    def _generate_dashboard_layout_schema(self) -> dict[str, Any]:
        """Generate schema for dashboard layout configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Dashboard Layout Configuration",
            "type": "object",
            "properties": {
                "layout_type": {"type": "string", "const": "dashboard_layout"},
                "grid": {
                    "type": "object",
                    "properties": {
                        "rows": {"type": "integer", "minimum": 1, "default": 3},
                        "cols": {"type": "integer", "minimum": 1, "default": 2},
                        "height_ratios": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0},
                            "default": [0.2, 0.4, 0.4],
                        },
                        "width_ratios": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0},
                            "default": None,
                        },
                    },
                    "required": ["rows", "cols"],
                },
                "spacing": {
                    "type": "object",
                    "properties": {
                        "horizontal": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.15,
                        },
                        "vertical": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.1,
                        },
                    },
                },
                "figure_size": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 1},
                    "minItems": 2,
                    "maxItems": 2,
                    "default": [16, 12],
                    "description": "Figure size in inches [width, height]",
                },
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": ["chart", "metrics", "text"],
                            },
                            "position": {
                                "type": "array",
                                "items": {"type": "integer", "minimum": 1},
                                "minItems": 2,
                                "maxItems": 2,
                                "description": "Grid position [row, col] (1-indexed)",
                            },
                            "chart_config": {"type": "object"},
                            "metrics_data": {"type": "array"},
                        },
                        "required": ["name", "type", "position"],
                    },
                },
                "responsive": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "breakpoints": {
                            "type": "object",
                            "properties": {
                                "mobile": {"type": "integer", "default": 480},
                                "tablet": {"type": "integer", "default": 768},
                                "desktop": {"type": "integer", "default": 1200},
                                "large": {"type": "integer", "default": 1920},
                            },
                        },
                    },
                },
            },
            "required": ["layout_type", "grid"],
        }

    def _generate_theme_config_schema(self) -> dict[str, Any]:
        """Generate schema for theme configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Theme Configuration",
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["light", "dark"],
                    "default": "light",
                    "description": "Theme mode",
                },
                "template": {
                    "type": "string",
                    "enum": [
                        "colemorton_light",
                        "colemorton_dark",
                        "colemorton_light_hd",
                        "colemorton_dark_hd",
                        "sensylate_dashboard",
                    ],
                    "description": "Plotly template name",
                },
                "colors": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                        "secondary": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                        "background": {
                            "type": "string",
                            "pattern": "^#[0-9A-Fa-f]{6}$",
                        },
                        "text": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                        "borders": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                    },
                },
                "typography": {
                    "type": "object",
                    "properties": {
                        "font_family": {
                            "type": "string",
                            "default": "Heebo, sans-serif",
                        },
                        "font_sizes": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "integer",
                                    "minimum": 8,
                                    "default": 20,
                                },
                                "subtitle": {
                                    "type": "integer",
                                    "minimum": 8,
                                    "default": 16,
                                },
                                "body": {
                                    "type": "integer",
                                    "minimum": 8,
                                    "default": 12,
                                },
                                "axis_labels": {
                                    "type": "integer",
                                    "minimum": 6,
                                    "default": 10,
                                },
                            },
                        },
                    },
                },
                "high_dpi": {"type": "boolean", "default": False},
                "dashboard_optimized": {"type": "boolean", "default": False},
            },
            "required": ["mode"],
        }

    def _generate_export_config_schema(self) -> dict[str, Any]:
        """Generate schema for export configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Export Configuration",
            "type": "object",
            "properties": {
                "formats": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["png", "pdf", "svg", "html", "webp"],
                    },
                    "default": ["png"],
                    "description": "Export formats",
                },
                "quality": {
                    "type": "object",
                    "properties": {
                        "width": {"type": "integer", "minimum": 100, "default": 1600},
                        "height": {"type": "integer", "minimum": 100, "default": 1200},
                        "scale": {
                            "type": "number",
                            "minimum": 0.5,
                            "maximum": 5,
                            "default": 2,
                        },
                        "dpi_equivalent": {
                            "type": "integer",
                            "minimum": 72,
                            "default": 192,
                        },
                    },
                },
                "output": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "default": "data/outputs/charts",
                        },
                        "filename_pattern": {
                            "type": "string",
                            "default": "{chart_type}_{timestamp}",
                        },
                        "include_timestamp": {"type": "boolean", "default": True},
                    },
                },
            },
        }

    def _get_theme_config_def(self) -> dict[str, Any]:
        """Get theme configuration definition for schema references."""
        return self.schemas.get("ThemeConfiguration", {})

    def _get_export_config_def(self) -> dict[str, Any]:
        """Get export configuration definition for schema references."""
        return self.schemas.get("ExportConfiguration", {})

    def get_schema(self, schema_name: str) -> dict[str, Any]:
        """
        Get a specific schema by name.

        Args:
            schema_name: Name of the schema to retrieve

        Returns:
            JSON schema dictionary
        """
        return self.schemas.get(schema_name, {})

    def get_all_schemas(self) -> dict[str, dict[str, Any]]:
        """
        Get all generated schemas.

        Returns:
            Dictionary mapping schema names to schema definitions
        """
        return self.schemas.copy()

    def export_schemas(self, output_dir: str = "data/outputs/schemas") -> dict[str, str]:
        """
        Export all schemas to JSON files.

        Args:
            output_dir: Directory to save schema files

        Returns:
            Dictionary mapping schema names to file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files = {}

        for schema_name, schema_content in self.schemas.items():
            filename = f"{schema_name.lower()}_schema.json"
            filepath = output_path / filename

            with open(filepath, "w") as f:
                json.dump(schema_content, f, indent=2)

            exported_files[schema_name] = str(filepath)

        return exported_files

    def validate_chart_config(self, config: dict[str, Any], chart_type: str) -> tuple[bool, list[str]]:
        """
        Validate a chart configuration against its schema.

        Args:
            config: Chart configuration to validate
            chart_type: Type of chart (e.g., 'EnhancedMonthlyBars')

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            import jsonschema

            schema = self.get_schema(chart_type)
            if not schema:
                return False, [f"Schema not found for chart type: {chart_type}"]

            jsonschema.validate(instance=config, schema=schema)
            return True, []

        except ImportError:
            return False, ["jsonschema library not available for validation"]
        except jsonschema.exceptions.ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    def generate_example_configs(self) -> dict[str, dict[str, Any]]:
        """
        Generate example configurations for all chart types.

        Returns:
            Dictionary mapping chart types to example configurations
        """
        examples = {}

        # Monthly bars example
        examples["EnhancedMonthlyBars"] = {
            "chart_type": "enhanced_monthly_bars",
            "data": [
                {
                    "month": "January",
                    "year": 2024,
                    "trades": 15,
                    "win_rate": 73.3,
                    "return_pct": 4.2,
                    "market_condition": "Bullish",
                },
                {
                    "month": "February",
                    "year": 2024,
                    "trades": 12,
                    "win_rate": 58.3,
                    "return_pct": -1.1,
                    "market_condition": "Bearish",
                },
            ],
            "theme": {"mode": "light"},
            "layout": {
                "title": "Monthly Trading Performance",
                "width": 800,
                "height": 600,
                "show_dual_axis": True,
            },
        }

        # Donut chart example
        examples["EnhancedDonutChart"] = {
            "chart_type": "enhanced_donut_chart",
            "data": [
                {
                    "quality": "Excellent",
                    "count": 25,
                    "percentage": 35.7,
                    "win_rate": 92.0,
                    "avg_return": 3.8,
                },
                {
                    "quality": "Good",
                    "count": 30,
                    "percentage": 42.9,
                    "win_rate": 70.0,
                    "avg_return": 1.5,
                },
            ],
            "theme": {"mode": "light"},
            "layout": {
                "title": "Trade Quality Distribution",
                "width": 600,
                "height": 600,
                "show_center_text": True,
            },
        }

        # Waterfall chart example
        examples["WaterfallChart"] = {
            "chart_type": "waterfall_chart",
            "data": [
                {
                    "ticker": "AAPL",
                    "entry_date": "2024-01-15",
                    "exit_date": "2024-01-22",
                    "duration": 7,
                    "return_pct": 3.2,
                    "quality": "Excellent",
                    "entry_price": 185.50,
                    "exit_price": 191.44,
                    "position_size": 10000,
                }
            ],
            "theme": {"mode": "light"},
            "layout": {
                "title": "Trading Waterfall Analysis",
                "width": 1000,
                "height": 600,
                "show_cumulative_line": True,
            },
        }

        # Scatter chart example
        examples["EnhancedScatter"] = {
            "chart_type": "enhanced_scatter",
            "data": [
                {
                    "ticker": "AAPL",
                    "entry_date": "2024-01-15",
                    "exit_date": "2024-01-22",
                    "duration": 7,
                    "return_pct": 3.2,
                    "quality": "Excellent",
                    "entry_price": 185.50,
                    "exit_price": 191.44,
                    "position_size": 10000,
                }
            ],
            "theme": {"mode": "light"},
            "layout": {
                "title": "Duration vs Return Analysis",
                "width": 800,
                "height": 600,
                "show_trend_line": True,
            },
        }

        return examples


def create_json_schema_generator(theme_manager=None) -> JSONSchemaGenerator:
    """
    Factory function to create a JSONSchemaGenerator instance.

    Args:
        theme_manager: Optional theme manager instance

    Returns:
        Configured JSONSchemaGenerator instance
    """
    return JSONSchemaGenerator(theme_manager)


if __name__ == "__main__":
    # Test JSON schema generation
    generator = create_json_schema_generator()

    print("📋 Generated JSON Schemas:")
    for schema_name in generator.get_all_schemas().keys():
        print("  - {schema_name}")

    # Export schemas
    exported = generator.export_schemas()
    print("\n💾 Exported {len(exported)} schema files:")
    for name, path in exported.items():
        print("  - {name}: {path}")

    # Generate examples
    examples = generator.generate_example_configs()
    print("\n🔧 Generated {len(examples)} example configurations")
