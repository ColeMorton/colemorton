#!/usr/bin/env python3
"""
Plotly layout manager for responsive dashboard grid systems.

This module provides sophisticated layout management for Plotly dashboard visualizations,
supporting subplot systems, spacing, and component positioning.
"""

from dataclasses import dataclass
from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots


@dataclass
class PlotlyLayoutComponent:
    """Represents a dashboard component with position and styling for Plotly."""

    name: str
    component_type: str  # 'chart', 'metric', 'text'
    position: tuple[int, int]  # (row, col)
    span: tuple[int, int] = (1, 1)  # (row_span, col_span)
    secondary_y: bool = False
    subplot_type: str = "xy"  # 'xy', 'pie', 'indicator'


@dataclass
class PlotlyGridConfig:
    """Configuration for Plotly subplot grid layout."""

    rows: int
    cols: int
    figure_size: tuple[int, int]  # (width, height) in pixels
    row_heights: list[float] | None = None
    column_widths: list[float] | None = None
    vertical_spacing: float = 0.1
    horizontal_spacing: float = 0.1
    subplot_titles: list[str] | None = None
    specs: list[list[dict[str, Any]]] | None = None


class PlotlyLayoutManager:
    """Advanced layout manager for Plotly dashboard generation."""

    def __init__(self, config: dict[str, Any], theme_manager=None):
        """
        Initialize Plotly layout manager.

        Args:
            config: Layout configuration dictionary
            theme_manager: Optional theme manager for styling
        """
        self.config = config
        self.layout_config = config.get("layout", {})
        self.theme_manager = theme_manager
        self.grid_config = self._create_grid_config()
        self.components: list[PlotlyLayoutComponent] = []

    def _create_grid_config(self) -> PlotlyGridConfig:
        """Create Plotly grid configuration from layout config."""
        grid = self.layout_config.get("grid", {})

        # Convert matplotlib figure size to Plotly pixel dimensions
        mpl_size = self.layout_config.get("figure_size", [16, 12])
        pixel_width = int(mpl_size[0] * 100)  # Convert inches to pixels (100 DPI base)
        pixel_height = int(mpl_size[1] * 100)

        return PlotlyGridConfig(
            rows=grid.get("rows", 3),
            cols=grid.get("cols", 2),
            figure_size=(pixel_width, pixel_height),
            row_heights=grid.get("height_ratios", [0.2, 0.4, 0.4]),
            column_widths=grid.get("width_ratios", None),
            vertical_spacing=self.layout_config.get("spacing", {}).get("vertical", 0.1),
            horizontal_spacing=self.layout_config.get("spacing", {}).get("horizontal", 0.1),
        )

    def create_dashboard_subplot(
        self,
        subplot_titles: list[str] | None = None,
        specs: list[list[dict[str, Any]]] | None = None,
    ) -> go.Figure:
        """
        Create optimized dashboard figure with subplot layout.

        Args:
            subplot_titles: Optional titles for subplots
            specs: Optional subplot specifications

        Returns:
            Plotly Figure with configured subplots
        """
        # Default specs for mixed chart types
        if specs is None:
            specs = []
            for row in range(self.grid_config.rows):
                spec_row = []
                for col in range(self.grid_config.cols):
                    if row == 0:  # Metrics row - use indicator type
                        spec_row.append({"type": "indicator"})
                    elif row == 2 and col == 1:  # Bottom right position for pie charts
                        spec_row.append({"type": "domain"})
                    else:  # Chart rows - use standard xy
                        spec_row.append({"secondary_y": False})
                specs.append(spec_row)

        # Create subplot figure
        fig = make_subplots(
            rows=self.grid_config.rows,
            cols=self.grid_config.cols,
            row_heights=self.grid_config.row_heights,
            column_widths=self.grid_config.column_widths,
            vertical_spacing=self.grid_config.vertical_spacing,
            horizontal_spacing=self.grid_config.horizontal_spacing,
            subplot_titles=subplot_titles,
            specs=specs,
        )

        # Configure figure dimensions
        fig.update_layout(
            width=self.grid_config.figure_size[0],
            height=self.grid_config.figure_size[1],
            margin=dict(l=60, r=60, t=100, b=60),
            showlegend=False,
        )

        return fig

    def add_chart_to_subplot(
        self,
        fig: go.Figure,
        chart_traces: list[Any],
        row: int,
        col: int,
        chart_title: str | None = None,
    ) -> go.Figure:
        """
        Add chart traces to specific subplot position.

        Args:
            fig: Plotly figure with subplots
            chart_traces: List of Plotly traces to add
            row: Row position (1-indexed)
            col: Column position (1-indexed)
            chart_title: Optional chart title

        Returns:
            Updated figure with chart traces
        """
        # Add each trace to the specified subplot
        for trace in chart_traces:
            fig.add_trace(trace, row=row, col=col)

        # Note: Subplot titles are handled by make_subplots subplot_titles parameter
        # Individual chart titles can be set via trace names or annotations

        return fig

    def _get_subplot_index(self, row: int, col: int) -> int:
        """Calculate subplot index from row/col position."""
        return (row - 1) * self.grid_config.cols + col

    def create_metrics_row(self, fig: go.Figure, metrics_data: list[dict[str, Any]], mode: str = "light") -> go.Figure:
        """
        Create enhanced metrics row using Plotly indicators.

        Args:
            fig: Plotly figure with subplots
            metrics_data: List of metric configurations
            mode: Theme mode ('light' or 'dark')

        Returns:
            Updated figure with metrics
        """
        theme = self.theme_manager.get_theme_colors(mode) if self.theme_manager else {}

        # Calculate positions for metrics across the top row
        num_metrics = len(metrics_data)
        metrics_per_col = max(1, num_metrics // self.grid_config.cols)

        for i, metric in enumerate(metrics_data):
            col = (i % self.grid_config.cols) + 1

            # Create indicator trace
            indicator = go.Indicator(
                mode="number+delta" if "delta" in metric else "number",
                value=metric["value"],
                title={"text": metric["label"], "font": {"size": 14}},
                delta=metric.get("delta", {}),
                number={
                    "font": {
                        "size": 24,
                        "color": theme.primary_text if theme else "#121212",
                    }
                },
                domain={"x": [0, 1], "y": [0, 1]},
            )

            # Add to first row
            fig.add_trace(indicator, row=1, col=col)

        return fig

    def apply_dashboard_theme(self, fig: go.Figure, title: str, subtitle: str = "", mode: str = "light") -> go.Figure:
        """
        Apply comprehensive dashboard theme to figure.

        Args:
            fig: Plotly figure
            title: Main dashboard title
            subtitle: Optional subtitle
            mode: Theme mode ('light' or 'dark')

        Returns:
            Themed figure
        """
        if not self.theme_manager:
            return fig

        theme = self.theme_manager.get_theme_colors(mode)
        fonts = self.theme_manager._get_font_list()

        # Apply global theme
        fig.update_layout(
            title={
                "text": (f"<b>{title}</b><br><sub>{subtitle}</sub>" if subtitle else f"<b>{title}</b>"),
                "x": 0.5,
                "xanchor": "center",
                "font": {
                    "family": ", ".join(fonts),
                    "size": 20,
                    "color": theme.primary_text,
                },
            },
            plot_bgcolor=theme.background,
            paper_bgcolor=theme.background,
            font={"family": ", ".join(fonts), "size": 12, "color": theme.body_text},
        )

        # Update all subplot axes
        for i in range(1, self.grid_config.rows * self.grid_config.cols + 1):
            axis_suffix = "" if i == 1 else str(i)

            fig.update_layout(
                {
                    f"xaxis{axis_suffix}": {
                        "showgrid": True,
                        "gridcolor": theme.borders,
                        "gridwidth": 0.5,
                        "zeroline": True,
                        "zerolinecolor": theme.borders,
                        "linecolor": theme.borders,
                        "tickfont": {"size": 10, "color": theme.body_text},
                        "titlefont": {"size": 12, "color": theme.body_text},
                    },
                    f"yaxis{axis_suffix}": {
                        "showgrid": True,
                        "gridcolor": theme.borders,
                        "gridwidth": 0.5,
                        "zeroline": True,
                        "zerolinecolor": theme.borders,
                        "linecolor": theme.borders,
                        "tickfont": {"size": 10, "color": theme.body_text},
                        "titlefont": {"size": 12, "color": theme.body_text},
                    },
                }
            )

        return fig

    def optimize_chart_layout(self, fig: go.Figure, chart_type: str, row: int, col: int) -> go.Figure:
        """
        Optimize layout for specific chart types.

        Args:
            fig: Plotly figure
            chart_type: Type of chart ('bar', 'scatter', 'pie', 'line', 'waterfall')
            row: Chart row position
            col: Chart column position

        Returns:
            Optimized figure
        """
        subplot_index = self._get_subplot_index(row, col)
        axis_suffix = "" if subplot_index == 1 else str(subplot_index)

        if chart_type == "pie":
            # Ensure proper aspect ratio for pie charts
            fig.update_layout(
                {
                    f"xaxis{axis_suffix}": {
                        "showgrid": False,
                        "showticklabels": False,
                        "zeroline": False,
                    },
                    f"yaxis{axis_suffix}": {
                        "showgrid": False,
                        "showticklabels": False,
                        "zeroline": False,
                        "scaleanchor": f"x{axis_suffix}",
                    },
                }
            )
        elif chart_type == "bar":
            # Optimize bar chart spacing
            fig.update_layout(
                {
                    f"xaxis{axis_suffix}": {"categoryorder": "total descending"},
                    f"yaxis{axis_suffix}": {"range": [0, None]},  # Start from 0
                }
            )
        elif chart_type == "scatter":
            # Add slight margins for scatter plots
            fig.update_layout(
                {
                    f"xaxis{axis_suffix}": {"range": None},  # Auto-range with margins
                    f"yaxis{axis_suffix}": {"range": None},
                }
            )

        return fig

    def configure_high_dpi_export(self, scale: float = 2.0) -> dict[str, Any]:
        """
        Configure high-DPI export settings for Plotly.

        Args:
            scale: Scale factor for high-DPI (2.0 = 2x, 3.0 = 3x)

        Returns:
            Export configuration dictionary
        """
        return {
            "width": int(self.grid_config.figure_size[0] * scale),
            "height": int(self.grid_config.figure_size[1] * scale),
            "scale": scale,
            "engine": "kaleido",
        }

    def export_dashboard(
        self,
        fig: go.Figure,
        filepath: str,
        format: str = "png",
        high_dpi: bool = True,
        scale: float = 2.0,
    ) -> str:
        """
        Export dashboard with optimized settings.

        Args:
            fig: Plotly figure to export
            filepath: Output file path
            format: Export format ('png', 'pdf', 'svg', 'html')
            high_dpi: Whether to use high-DPI settings
            scale: Scale factor for high-DPI

        Returns:
            Path to exported file
        """
        if format.lower() == "html":
            # HTML export
            fig.write_html(filepath)
        else:
            # Static image export
            export_config = self.configure_high_dpi_export(scale) if high_dpi else {}
            fig.write_image(filepath, format=format, **export_config)

        return filepath

    def create_responsive_layout(self, breakpoints: dict[str, int] = None) -> dict[str, Any]:
        """
        Create responsive layout configuration for different screen sizes.

        Args:
            breakpoints: Screen size breakpoints in pixels

        Returns:
            Responsive layout configuration
        """
        if breakpoints is None:
            breakpoints = {"mobile": 480, "tablet": 768, "desktop": 1200, "large": 1920}

        base_width, base_height = self.grid_config.figure_size

        layouts = {}
        for size, width in breakpoints.items():
            # Scale figure proportionally
            scale_factor = width / base_width
            scaled_height = int(base_height * scale_factor)

            layouts[size] = {
                "width": width,
                "height": scaled_height,
                "font_scale": min(1.0, scale_factor),
                "margin_scale": scale_factor,
            }

        return layouts


def create_plotly_layout_manager(config: dict[str, Any], theme_manager=None) -> PlotlyLayoutManager:
    """
    Factory function to create a PlotlyLayoutManager instance.

    Args:
        config: Configuration dictionary
        theme_manager: Optional theme manager

    Returns:
        Configured PlotlyLayoutManager instance
    """
    return PlotlyLayoutManager(config, theme_manager)


if __name__ == "__main__":
    # Test Plotly layout manager
    test_config = {
        "layout": {
            "figure_size": [16, 12],
            "grid": {"rows": 3, "cols": 2, "height_ratios": [0.2, 0.4, 0.4]},
            "spacing": {"horizontal": 0.15, "vertical": 0.1},
        }
    }

    layout_manager = create_plotly_layout_manager(test_config)
    fig = layout_manager.create_dashboard_subplot()

    print("Created Plotly figure: {fig.layout.width}x{fig.layout.height}")
    print(f"Subplot grid: {layout_manager.grid_config.rows}x{layout_manager.grid_config.cols}")

    # Test export configuration
    export_config = layout_manager.configure_high_dpi_export(scale=2.0)
    print("High-DPI export: {export_config}")
