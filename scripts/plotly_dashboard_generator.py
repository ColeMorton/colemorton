#!/usr/bin/env python3
"""
Plotly-native dashboard generator for creating interactive performance visualizations.

This script generates high-resolution dashboard images using Plotly's native
subplot system, following Sensylate design system specifications.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.config_loader import ConfigLoader
from scripts.utils.config_validator import (
    validate_dashboard_config,
    validate_input_file,
)
from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    QualityDistribution,
    TradeData,
    parse_dashboard_data,
)
from scripts.utils.logging_setup import setup_logging
from scripts.utils.plotly_theme_mapper import PlotlyThemeMapper
from scripts.utils.scalability_manager import (
    create_scalability_manager,
)
from scripts.utils.theme_manager import create_theme_manager


class PlotlyDashboardGenerator:
    """Plotly-native dashboard generation class."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Plotly dashboard generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.theme_manager = create_theme_manager()
        self.scalability_manager = create_scalability_manager(config)
        self.theme_mapper = PlotlyThemeMapper(self.theme_manager)

        # Configure Plotly for high-quality exports
        self._configure_plotly()

    def _configure_plotly(self):
        """Configure Plotly for high-quality dashboard exports."""
        # Set default renderer for static export
        pio.renderers.default = "png"

        # Configure kaleido for high-DPI exports
        try:
            import kaleido

            if hasattr(pio, "kaleido") and pio.kaleido.scope is not None:
                pio.kaleido.scope.default_width = 1600
                pio.kaleido.scope.default_height = 1200
                pio.kaleido.scope.default_scale = 3  # 3x scale = ~300 DPI
        except ImportError:
            self.logger.warning("Kaleido not available, using browser-based rendering")

    def generate_dashboard(self, input_file, mode: str = "light") -> Path:
        """
        Generate Plotly dashboard visualization.

        Args:
            input_file: Path or string to the input markdown file
            mode: 'light' or 'dark' mode

        Returns:
            Path to the generated dashboard image
        """
        # Convert to Path object if needed
        input_path = Path(input_file) if isinstance(input_file, str) else input_file
        self.logger.info(f"Generating {mode} mode Plotly dashboard from {input_path}")

        # Parse the input data
        data = parse_dashboard_data(str(input_path))

        # Create the dashboard figure
        fig = self._create_dashboard_figure(data, mode)

        # Save the output
        output_path = self._save_dashboard(fig, mode)

        self.logger.info(f"Plotly dashboard saved to {output_path}")
        return output_path

    def _create_dashboard_figure(self, data: dict[str, Any], mode: str) -> go.Figure:
        """
        Create the complete dashboard figure using Plotly subplots.

        Args:
            data: Parsed performance data
            mode: 'light' or 'dark' mode

        Returns:
            Plotly figure object
        """
        # Create subplot layout: metrics row + 2x2 chart grid
        fig = make_subplots(
            rows=3,
            cols=2,
            row_heights=[0.15, 0.425, 0.425],  # 15% metrics, 42.5% each for chart rows
            subplot_titles=[
                # Metrics row (row 1) - will be handled separately
                "",
                "",
                # Chart titles (rows 2-3)
                "Monthly Performance",
                "Quality Distribution",
                "Trade Performance",
                "Duration vs Return",
            ],
            specs=[
                # Row 1: Empty for custom metrics layout
                [{"secondary_y": False}, {"secondary_y": False}],
                # Row 2: Top chart row
                [{"type": "xy"}, {"type": "pie"}],
                # Row 3: Bottom chart row
                [{"type": "xy"}, {"type": "xy"}],
            ],
            horizontal_spacing=0.12,
            vertical_spacing=0.15,
        )

        # Get theme colors
        theme = self.theme_manager.get_theme_colors(mode)

        # Add custom metrics layout at the top
        self._add_custom_metrics_layout(fig, data["performance_metrics"], mode)

        # Add main charts (rows 2-3)
        self._add_monthly_performance(fig, data.get("monthly_performance", []), mode, row=2, col=1)
        self._add_quality_distribution(fig, data.get("quality_distribution", []), mode, row=2, col=2)
        self._add_trade_performance(fig, data.get("trades", []), mode, row=3, col=1)
        self._add_duration_scatter(fig, data.get("trades", []), mode, row=3, col=2)

        # Apply theme and layout
        self._apply_dashboard_theme(fig, data, mode)

        return fig

    def _add_custom_metrics_layout(self, fig: go.Figure, metrics, mode: str):
        """Add key performance metrics as custom annotations."""
        theme = self.theme_manager.get_theme_colors(mode)

        # Define metric positions (4 metrics across the top)
        metric_positions = [
            {
                "x": 0.125,
                "title": "Win Rate",
                "value": f"{getattr(metrics, 'win_rate', 0):.1f}%",
                "color": "#26c6da",
            },
            {
                "x": 0.375,
                "title": "Total Return",
                "value": f"{getattr(metrics, 'total_return', 0):+.1f}%",
                "color": ("#26c6da" if getattr(metrics, "total_return", 0) >= 0 else "#ff7043"),
            },
            {
                "x": 0.625,
                "title": "Profit Factor",
                "value": f"{getattr(metrics, 'profit_factor', 0):.2f}",
                "color": "#7e57c2",
            },
            {
                "x": 0.875,
                "title": "Total Trades",
                "value": f"{getattr(metrics, 'total_trades', 0)}",
                "color": "#3179f5",
            },
        ]

        # Add metric annotations
        for metric in metric_positions:
            # Add title
            fig.add_annotation(
                x=metric["x"],
                y=0.95,
                text=metric["title"],
                showarrow=False,
                font=dict(size=14, color=theme.primary_text, family="Heebo"),
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="bottom",
            )

            # Add value
            fig.add_annotation(
                x=metric["x"],
                y=0.85,
                text=metric["value"],
                showarrow=False,
                font=dict(size=32, color=metric["color"], family="Heebo", weight="bold"),
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
            )

    def _add_monthly_performance(
        self,
        fig: go.Figure,
        monthly_data: list[MonthlyPerformance],
        mode: str,
        row: int,
        col: int,
    ):
        """Add monthly performance bar chart."""
        if not monthly_data:
            fig.add_annotation(
                text="No monthly data available",
                xref="paper",
                yref="paper",
                x=0.25,
                y=0.6,  # Approximate position for top-left chart
                showarrow=False,
                font=dict(size=12),
            )
            return

        # Apply scalability optimizations
        if self.scalability_manager:
            timeline_category = self.scalability_manager.detect_monthly_timeline_category(monthly_data)
            months = self.scalability_manager.optimize_monthly_labels(monthly_data, timeline_category)
        else:
            months = [f"{data.month[:3]} {str(data.year)[2:]}" for data in monthly_data]

        win_rates = [data.win_rate for data in monthly_data]
        returns = [data.average_return for data in monthly_data]

        # Get colors
        colors = self.theme_mapper.get_monthly_colors_list()
        bar_colors = (colors * ((len(months) // len(colors)) + 1))[: len(months)]

        # Add bar chart
        fig.add_trace(
            go.Bar(
                x=months,
                y=win_rates,
                name="Win Rate",
                marker=dict(
                    color=bar_colors,
                    opacity=0.8,
                    line=dict(color=self.theme_manager.get_theme_colors(mode).borders, width=1),
                ),
                text=[f"{rate:.0f}%" for rate in win_rates],
                textposition="outside",
                showlegend=False,
                hovertemplate="Month: %{x}<br>Win Rate: %{y:.0f}%<extra></extra>",
            ),
            row=row,
            col=col,
        )

        # Add return annotations
        theme = self.theme_manager.get_theme_colors(mode)
        performance_colors = self.theme_mapper.get_performance_colors_mapping()

        for i, ret in enumerate(returns):
            return_color = performance_colors["positive"] if ret >= 0 else performance_colors["negative"]
            fig.add_annotation(
                x=months[i],
                y=win_rates[i] / 2,
                text=f"{ret:+.1f}%",
                showarrow=False,
                font=dict(size=8, color=return_color),
                xref=f"x{col}",
                yref=f"y{col}",
            )

    def _add_quality_distribution(
        self,
        fig: go.Figure,
        quality_data: list[QualityDistribution],
        mode: str,
        row: int,
        col: int,
    ):
        """Add quality distribution donut chart."""
        if not quality_data:
            # For pie charts, add annotation using paper coordinates
            fig.add_annotation(
                text="No quality data available",
                xref="paper",
                yref="paper",
                x=0.75,
                y=0.6,  # Approximate position for top-right chart
                showarrow=False,
                font=dict(size=12),
            )
            return

        categories = [q.category for q in quality_data]
        percentages = [q.percentage for q in quality_data]

        # Get quality colors
        quality_colors = self.theme_mapper.get_quality_colors_mapping()
        colors = [quality_colors.get(cat, "#999999") for cat in categories]

        # Add donut chart
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=percentages,
                hole=0.4,
                marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
                textinfo="label+percent",
                textposition="outside",
                showlegend=False,
                hovertemplate="%{label}: %{percent}<extra></extra>",
            ),
            row=row,
            col=col,
        )

    def _add_trade_performance(self, fig: go.Figure, trades: list[TradeData], mode: str, row: int, col: int):
        """Add trade performance waterfall or distribution chart based on trade count."""
        if not trades:
            fig.add_annotation(
                text="No trade data available",
                xref="paper",
                yref="paper",
                x=0.25,
                y=0.25,  # Approximate position for bottom-left chart
                showarrow=False,
                font=dict(size=12),
            )
            return

        # Determine visualization based on trade count
        trade_count = len(trades)

        if trade_count <= 50:
            # Individual trade waterfall
            self._add_waterfall_chart(fig, trades, mode, row, col)
        elif trade_count <= 100:
            # Performance bands
            self._add_performance_bands(fig, trades, mode, row, col)
        else:
            # Statistical distribution
            self._add_distribution_histogram(fig, trades, mode, row, col)

    def _add_waterfall_chart(self, fig: go.Figure, trades: list[TradeData], mode: str, row: int, col: int):
        """Add individual trade waterfall chart."""
        returns = [trade.return_pct for trade in trades]
        cumulative_returns = np.cumsum([0] + returns)

        performance_colors = self.theme_mapper.get_performance_colors_mapping()
        colors = [(performance_colors["positive"] if ret >= 0 else performance_colors["negative"]) for ret in returns]

        # Add waterfall bars
        for i, ret in enumerate(returns):
            fig.add_trace(
                go.Bar(
                    x=[f"T{i + 1}"],
                    y=[ret],
                    base=cumulative_returns[i],
                    marker_color=colors[i],
                    name=f"Trade {i + 1}",
                    showlegend=False,
                    hovertemplate=f"Trade {i + 1}: {ret:+.1f}%<extra></extra>",
                ),
                row=row,
                col=col,
            )

    def _add_performance_bands(self, fig: go.Figure, trades: list[TradeData], mode: str, row: int, col: int):
        """Add performance bands for medium datasets."""
        returns = [trade.return_pct for trade in trades]

        # Create performance bands
        excellent = [r for r in returns if r > 5]
        good = [r for r in returns if 0 < r <= 5]
        poor = [r for r in returns if -5 <= r <= 0]
        failed = [r for r in returns if r < -5]

        bands = ["Excellent (>5%)", "Good (0-5%)", "Poor (-5-0%)", "Failed (<-5%)"]
        counts = [len(excellent), len(good), len(poor), len(failed)]
        colors = ["#26c6da", "#3179f5", "#7e57c2", "#ff7043"]

        fig.add_trace(
            go.Bar(
                x=bands,
                y=counts,
                marker_color=colors,
                showlegend=False,
                hovertemplate="%{x}: %{y} trades<extra></extra>",
            ),
            row=row,
            col=col,
        )

    def _add_distribution_histogram(self, fig: go.Figure, trades: list[TradeData], mode: str, row: int, col: int):
        """Add statistical distribution histogram for large datasets."""
        returns = [trade.return_pct for trade in trades]

        fig.add_trace(
            go.Histogram(
                x=returns,
                nbinsx=20,
                marker_color="#26c6da",
                opacity=0.7,
                showlegend=False,
                hovertemplate="Return Range: %{x}<br>Count: %{y}<extra></extra>",
            ),
            row=row,
            col=col,
        )

    def _add_duration_scatter(self, fig: go.Figure, trades: list[TradeData], mode: str, row: int, col: int):
        """Add duration vs return scatter plot."""
        if not trades:
            fig.add_annotation(
                text="No trade data available",
                xref="paper",
                yref="paper",
                x=0.75,
                y=0.25,  # Approximate position for bottom-right chart
                showarrow=False,
                font=dict(size=12),
            )
            return

        durations = [trade.duration_days for trade in trades]
        returns = [trade.return_pct for trade in trades]

        # Apply density management based on trade count
        trade_count = len(trades)
        if trade_count <= 50:
            opacity = 0.8
            size = 8
        elif trade_count <= 150:
            opacity = 0.6
            size = 6
        else:
            opacity = 0.4
            size = 4

        # Color by performance
        performance_colors = self.theme_mapper.get_performance_colors_mapping()
        colors = [(performance_colors["positive"] if ret >= 0 else performance_colors["negative"]) for ret in returns]

        fig.add_trace(
            go.Scatter(
                x=durations,
                y=returns,
                mode="markers",
                marker=dict(
                    color=colors,
                    size=size,
                    opacity=opacity,
                    line=dict(width=1, color="white"),
                ),
                showlegend=False,
                hovertemplate="Duration: %{x} days<br>Return: %{y:.1f}%<extra></extra>",
            ),
            row=row,
            col=col,
        )

    def _apply_dashboard_theme(self, fig: go.Figure, data: dict[str, Any], mode: str):
        """Apply theme and layout to the complete dashboard."""
        theme = self.theme_manager.get_theme_colors(mode)

        # Get trade count for subtitle
        trade_count = len(data.get("trades", []))
        current_year = datetime.now().year

        fig.update_layout(
            title={
                "text": f"Historical Trading Performance Dashboard<br><sub>Year-to-Date {current_year}</sub>",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 24, "color": theme.primary_text, "family": "Heebo"},
            },
            plot_bgcolor=theme.background,
            paper_bgcolor=theme.background,
            font={"family": "Heebo", "color": theme.primary_text},
            showlegend=False,
            margin=dict(t=100, b=50, l=50, r=50),
            height=1200,
            width=1600,
        )

        # Update subplot titles
        for i in range(1, 5):  # Update chart titles (skip metrics row)
            fig.layout.annotations[i + 3].update(font=dict(size=14, color=theme.primary_text, family="Heebo"))

        # Update axes for charts
        fig.update_xaxes(gridcolor=theme.borders, linecolor=theme.borders, tickcolor=theme.body_text)
        fig.update_yaxes(gridcolor=theme.borders, linecolor=theme.borders, tickcolor=theme.body_text)

    def _save_dashboard(self, fig: go.Figure, mode: str) -> Path:
        """Save the dashboard figure to file."""
        timestamp = datetime.now().strftime("%Y%m%d")
        output_dir = Path(self.config["output"]["directory"])
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = self.config["output"]["filename_template"].format(mode=mode, date=timestamp)
        output_path = output_dir / filename

        # Export with high-DPI settings
        export_config = {
            "width": 1600,
            "height": 1200,
            "scale": 3,  # 3x scale = ~300 DPI
            "format": "png",
        }

        try:
            fig.write_image(str(output_path), **export_config)
        except Exception as e:
            self.logger.error(f"High-quality export failed: {e}")
            # Fallback to standard export
            fig.write_image(str(output_path), format="png")

        return output_path


def main(
    config: dict[str, Any],
    input_file: str,
    mode: str = "both",
    output_dir: str | None = None,
) -> list[Path]:
    """
    Main function for generating Plotly dashboards.

    Args:
        config: Configuration dictionary
        input_file: Path to input markdown file
        mode: Generation mode ('light', 'dark', or 'both')
        output_dir: Optional output directory override

    Returns:
        List of generated dashboard file paths
    """
    if output_dir:
        config["output"]["directory"] = output_dir

    generator = PlotlyDashboardGenerator(config)
    generated_files = []

    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if mode in ["light", "both"]:
        light_path = generator.generate_dashboard(input_path, "light")
        generated_files.append(light_path)

    if mode in ["dark", "both"]:
        dark_path = generator.generate_dashboard(input_path, "dark")
        generated_files.append(dark_path)

    return generated_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Plotly-powered trading performance dashboards")
    parser.add_argument("--input", required=True, help="Path to input markdown file")
    parser.add_argument(
        "--config",
        default="config/pipelines/dashboard_generation.yaml",
        help="Configuration file",
    )
    parser.add_argument(
        "--mode",
        choices=["light", "dark", "both"],
        default="both",
        help="Dashboard mode",
    )
    parser.add_argument("--output-dir", help="Output directory override")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], default="dev", help="Environment")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(level=args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load_with_environment(args.config, args.env)

        # Validate configuration and input
        validate_dashboard_config(config)
        validate_input_file(args.input)

        # Generate dashboards
        generated_files = main(config, args.input, args.mode, args.output_dir)

        logger.info(f"Successfully generated {len(generated_files)} dashboard(s):")
        for file_path in generated_files:
            logger.info(f"  - {file_path}")

    except Exception as e:
        logger.error(f"Dashboard generation failed: {e}")
        sys.exit(1)
