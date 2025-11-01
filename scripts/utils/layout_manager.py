#!/usr/bin/env python3
"""
Layout manager for responsive dashboard grid systems.

This module provides sophisticated layout management for dashboard visualizations,
supporting responsive grids, spacing, and component positioning.
"""

from dataclasses import dataclass
from typing import Any

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


@dataclass
class LayoutComponent:
    """Represents a dashboard component with position and styling."""

    name: str
    component_type: str  # 'chart', 'metric', 'text'
    position: tuple[int, int]  # (row, col)
    span: tuple[int, int] = (1, 1)  # (row_span, col_span)
    padding: float = 0.02
    background_color: str | None = None
    border_color: str | None = None
    border_width: float = 0


@dataclass
class GridConfig:
    """Configuration for grid layout."""

    rows: int
    cols: int
    figure_size: tuple[float, float]
    height_ratios: list[float] | None = None
    width_ratios: list[float] | None = None
    hspace: float = 0.3
    wspace: float = 0.2
    top_margin: float = 0.95
    bottom_margin: float = 0.05
    left_margin: float = 0.05
    right_margin: float = 0.95


class LayoutManager:
    """Advanced layout manager for dashboard generation."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize layout manager.

        Args:
            config: Layout configuration dictionary
        """
        self.config = config
        self.layout_config = config.get("layout", {})
        self.grid_config = self._create_grid_config()
        self.components: list[LayoutComponent] = []

    def _create_grid_config(self) -> GridConfig:
        """Create grid configuration from layout config."""
        grid = self.layout_config.get("grid", {})

        return GridConfig(
            rows=grid.get("rows", 3),
            cols=grid.get("cols", 2),
            figure_size=tuple(self.layout_config.get("figure_size", [16, 12])),
            height_ratios=grid.get("height_ratios", [0.2, 0.4, 0.4]),
            width_ratios=grid.get("width_ratios", None),
            hspace=self.layout_config.get("spacing", {}).get("vertical", 0.3),
            wspace=self.layout_config.get("spacing", {}).get("horizontal", 0.2),
            top_margin=1.0 - self.layout_config.get("spacing", {}).get("padding", 0.05),
            bottom_margin=self.layout_config.get("spacing", {}).get("padding", 0.05),
            left_margin=self.layout_config.get("spacing", {}).get("padding", 0.05),
            right_margin=1.0 - self.layout_config.get("spacing", {}).get("padding", 0.05),
        )

    def create_dashboard_figure(self) -> tuple[plt.Figure, gridspec.GridSpec]:
        """
        Create optimized dashboard figure with grid layout.

        Returns:
            Tuple of (figure, gridspec) for component placement
        """
        # Create figure with optimal DPI and size
        fig = plt.figure(
            figsize=self.grid_config.figure_size,
            dpi=100,  # Will be overridden at save time
            facecolor="white",
        )

        # Create sophisticated grid specification
        gs = gridspec.GridSpec(
            self.grid_config.rows,
            self.grid_config.cols,
            figure=fig,
            height_ratios=self.grid_config.height_ratios,
            width_ratios=self.grid_config.width_ratios,
            hspace=self.grid_config.hspace,
            wspace=self.grid_config.wspace,
            top=self.grid_config.top_margin,
            bottom=self.grid_config.bottom_margin,
            left=self.grid_config.left_margin,
            right=self.grid_config.right_margin,
        )

        return fig, gs

    def create_metrics_row(self, fig: plt.Figure, gs: gridspec.GridSpec) -> plt.Axes:
        """
        Create enhanced metrics row spanning full width.

        Args:
            fig: Figure object
            gs: GridSpec object

        Returns:
            Axes object for metrics row
        """
        # Metrics span entire first row
        metrics_ax = fig.add_subplot(gs[0, :])
        metrics_ax.set_xlim(0, 1)
        metrics_ax.set_ylim(0, 1)
        metrics_ax.axis("off")

        return metrics_ax

    def create_chart_subplot(
        self,
        fig: plt.Figure,
        gs: gridspec.GridSpec,
        position: tuple[int, int],
        span: tuple[int, int] = (1, 1),
    ) -> plt.Axes:
        """
        Create individual chart subplot with enhanced styling.

        Args:
            fig: Figure object
            gs: GridSpec object
            position: (row, col) position
            span: (row_span, col_span) for multi-cell components

        Returns:
            Configured axes object
        """
        row, col = position
        row_span, col_span = span

        # Create subplot with proper spanning
        if row_span == 1 and col_span == 1:
            ax = fig.add_subplot(gs[row, col])
        else:
            ax = fig.add_subplot(gs[row : row + row_span, col : col + col_span])

        return ax

    def add_component_background(self, ax: plt.Axes, component: LayoutComponent, theme_colors: dict[str, str]):
        """
        Add background styling to component.

        Args:
            ax: Axes object
            component: Component configuration
            theme_colors: Theme color mapping
        """
        if component.background_color or component.border_color:
            # Get axes position in figure coordinates
            bbox = ax.get_position()

            # Create background rectangle
            bg_color = component.background_color or theme_colors.get("card_backgrounds", "white")
            border_color = component.border_color or theme_colors.get("borders", "gray")

            rect = Rectangle(
                (bbox.x0 - component.padding, bbox.y0 - component.padding),
                bbox.width + 2 * component.padding,
                bbox.height + 2 * component.padding,
                facecolor=bg_color,
                edgecolor=border_color,
                linewidth=component.border_width,
                transform=ax.figure.transFigure,
                zorder=-1,
            )

            ax.figure.patches.append(rect)

    def create_metric_cards(
        self,
        ax: plt.Axes,
        metrics_data: list[dict[str, Any]],
        theme_colors: dict[str, str],
    ) -> None:
        """
        Create sophisticated metric cards with enhanced styling.

        Args:
            ax: Metrics row axes
            metrics_data: List of metric configurations
            theme_colors: Theme color mapping
        """
        num_metrics = len(metrics_data)
        card_width = 0.22  # Slightly wider cards
        card_height = 0.6
        card_spacing = 0.04

        # Calculate starting position for centering
        total_width = num_metrics * card_width + (num_metrics - 1) * card_spacing
        start_x = (1.0 - total_width) / 2

        for i, metric in enumerate(metrics_data):
            x_pos = start_x + i * (card_width + card_spacing)
            y_pos = 0.2

            # Enhanced card background with subtle shadow effect
            # Shadow
            shadow_rect = Rectangle(
                (x_pos + 0.005, y_pos - 0.005),
                card_width,
                card_height,
                facecolor="black",
                alpha=0.1,
                zorder=1,
            )
            ax.add_patch(shadow_rect)

            # Main card
            card_rect = Rectangle(
                (x_pos, y_pos),
                card_width,
                card_height,
                facecolor=theme_colors.get("card_backgrounds", "#f6f6f6"),
                edgecolor=theme_colors.get("borders", "#eaeaea"),
                linewidth=1.5,
                zorder=2,
            )
            ax.add_patch(card_rect)

            # Card content positioning
            center_x = x_pos + card_width / 2

            # Value (large, bold)
            ax.text(
                center_x,
                y_pos + card_height * 0.65,
                metric["value"],
                ha="center",
                va="center",
                fontsize=16,
                fontweight="bold",
                color=theme_colors.get("primary_text", "#121212"),
                zorder=3,
            )

            # Label (smaller, muted)
            ax.text(
                center_x,
                y_pos + card_height * 0.35,
                metric["label"],
                ha="center",
                va="center",
                fontsize=11,
                fontweight="normal",
                color=theme_colors.get("body_text", "#444444"),
                zorder=3,
            )

            # Optional indicator (small accent)
            if "indicator" in metric:
                indicator_color = self._get_indicator_color(metric["indicator"], theme_colors)
                indicator_y = y_pos + card_height * 0.85
                ax.plot(
                    [center_x - 0.02, center_x + 0.02],
                    [indicator_y, indicator_y],
                    color=indicator_color,
                    linewidth=3,
                    zorder=3,
                )

    def _get_indicator_color(self, indicator: str, theme_colors: dict[str, str]) -> str:
        """Get color for metric indicators."""
        indicator_colors = {
            "positive": "#26c6da",  # Cole Morton cyan
            "negative": "#7e57c2",  # Cole Morton purple
            "neutral": "#3179f5",  # Cole Morton blue
            "warning": "#ff7043",  # Orange
            "good": "#66bb6a",  # Green
        }
        return indicator_colors.get(indicator, theme_colors.get("body_text", "#444444"))

    def add_title_and_subtitle(
        self,
        fig: plt.Figure,
        title: str,
        subtitle: str = "",
        theme_colors: dict[str, str] = None,
    ) -> None:
        """
        Add enhanced title and subtitle to dashboard.

        Args:
            fig: Figure object
            title: Main title text
            subtitle: Optional subtitle text
            theme_colors: Theme color mapping
        """
        if theme_colors is None:
            theme_colors = {}

        # Main title
        fig.suptitle(
            title,
            fontsize=18,
            fontweight="bold",
            color=theme_colors.get("primary_text", "#121212"),
            y=0.97,
            ha="center",
        )

        # Subtitle
        if subtitle:
            fig.text(
                0.5,
                0.94,
                subtitle,
                ha="center",
                va="center",
                fontsize=12,
                style="italic",
                color=theme_colors.get("body_text", "#444444"),
                alpha=0.8,
            )

    def optimize_chart_spacing(self, ax: plt.Axes, chart_type: str) -> None:
        """
        Optimize spacing and margins for specific chart types.

        Args:
            ax: Axes object
            chart_type: Type of chart ('bar', 'scatter', 'pie', 'line')
        """
        if chart_type == "pie":
            # Ensure pie charts are circular
            ax.set_aspect("equal")
        elif chart_type == "bar":
            # Optimize bar chart margins
            ax.margins(x=0.02, y=0.05)
        elif chart_type == "scatter":
            # Add slight margins for scatter plots
            ax.margins(0.05)

        # Common optimizations
        ax.tick_params(labelsize=9)
        ax.grid(True, alpha=0.3, linewidth=0.5)

    def apply_responsive_font_sizing(self, ax: plt.Axes, base_size: int = 10) -> None:
        """
        Apply responsive font sizing based on figure dimensions.

        Args:
            ax: Axes object
            base_size: Base font size for scaling
        """
        fig_width, fig_height = ax.figure.get_size_inches()
        scale_factor = min(fig_width / 16, fig_height / 12)  # Scale relative to 16x12 base

        scaled_size = max(8, int(base_size * scale_factor))

        ax.tick_params(labelsize=scaled_size - 2)
        # Title sizing is now handled by theme_manager - don't override

    def finalize_layout(self, fig: plt.Figure) -> None:
        """
        Apply final layout optimizations.

        Args:
            fig: Figure object
        """
        # Ensure tight layout without overlapping
        fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.92])

        # Additional spacing adjustments if needed
        plt.subplots_adjust(
            top=self.grid_config.top_margin,
            bottom=self.grid_config.bottom_margin,
            left=self.grid_config.left_margin,
            right=self.grid_config.right_margin,
        )


def create_layout_manager(config: dict[str, Any]) -> LayoutManager:
    """
    Factory function to create a LayoutManager instance.

    Args:
        config: Configuration dictionary

    Returns:
        Configured LayoutManager instance
    """
    return LayoutManager(config)


if __name__ == "__main__":
    # Test layout manager
    test_config = {
        "layout": {
            "figure_size": [16, 12],
            "grid": {"rows": 3, "cols": 2, "height_ratios": [0.2, 0.4, 0.4]},
            "spacing": {"horizontal": 0.2, "vertical": 0.3, "padding": 0.05},
        }
    }

    layout_manager = create_layout_manager(test_config)
    fig, gs = layout_manager.create_dashboard_figure()

    print("Created figure: {fig.get_size_inches()}")
    print("Grid shape: {gs.get_geometry()}")

    plt.close(fig)
