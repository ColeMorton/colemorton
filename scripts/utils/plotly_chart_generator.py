#!/usr/bin/env python3
"""
Plotly implementation of the abstract chart generator interface.

This module provides Plotly-based chart generation with JSON schema support
for unified backend/frontend chart definitions.
"""

from typing import Any

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
import plotly.io as pio

from scripts.utils.abstract_chart_generator import AbstractChartGenerator
from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    QualityDistribution,
    TradeData,
)
from scripts.utils.plotly_theme_mapper import PlotlyThemeMapper


class PlotlyChartGenerator(AbstractChartGenerator):
    """Plotly implementation of the chart generator interface."""

    def __init__(self, theme_manager, scalability_manager=None):
        """
        Initialize Plotly chart generator.

        Args:
            theme_manager: Theme manager instance
            scalability_manager: Optional scalability manager for volume optimization
        """
        super().__init__(theme_manager, scalability_manager)
        # Create theme mapper
        self.theme_mapper = PlotlyThemeMapper(theme_manager)
        # Configure Plotly settings
        self._configure_plotly()

    def _configure_plotly(self):
        """Configure Plotly default settings and templates for high-quality exports."""
        # Set default renderer for static export
        pio.renderers.default = "png"

        # Configure kaleido for high-quality exports (300+ DPI equivalent)
        try:
            # kaleido import handled elsewhere

            # Configure Kaleido scope for high-DPI exports
            if hasattr(pio, "kaleido") and pio.kaleido.scope is not None:
                # High-DPI settings (equivalent to 300+ DPI)
                pio.kaleido.scope.default_width = 1600  # Base width
                pio.kaleido.scope.default_height = 1200  # Base height
                pio.kaleido.scope.default_scale = 3  # 3x scale = ~300 DPI
                pio.kaleido.scope.default_format = "png"

                # Quality settings
                pio.kaleido.scope.chromium_args = [
                    "--disable-web-security",
                    "--allow-running-insecure-content",
                    "--disable-features=VizDisplayCompositor",
                    "--force-device-scale-factor=3",  # Force high DPI
                ]

        except ImportError:
            # Kaleido not available - will fall back to browser-based rendering
            print("Warning: Kaleido not available, using browser-based rendering")
        except Exception as e:
            # Kaleido configuration failed - continue with defaults
            print(f"Warning: Kaleido configuration failed: {e}")

    def configure_export_settings(
        self,
        width: int = 1600,
        height: int = 1200,
        scale: float = 3.0,
        format: str = "png",
    ) -> dict[str, Any]:
        """
        Configure high-quality export settings.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            scale: Scale factor (3.0 = ~300 DPI)
            format: Export format ('png', 'pdf', 'svg')

        Returns:
            Export configuration dictionary
        """
        return {
            "width": width,
            "height": height,
            "scale": scale,
            "format": format,
            "engine": "kaleido",
        }

    def export_high_quality_chart(
        self,
        fig: go.Figure,
        filepath: str,
        format: str = "png",
        dpi_equivalent: int = 300,
    ) -> str:
        """
        Export chart with high-quality settings optimized for print and web.

        Args:
            fig: Plotly figure to export
            filepath: Output file path
            format: Export format ('png', 'pdf', 'svg')
            dpi_equivalent: Target DPI equivalent (300 for print quality)

        Returns:
            Path to exported file
        """
        # Calculate scale factor for target DPI
        # Standard web DPI is ~96, so scale = target_dpi / 96
        scale = max(1.0, dpi_equivalent / 96)

        # Export configuration
        export_config = self.configure_export_settings(width=1600, height=1200, scale=scale, format=format)

        try:
            if format.lower() == "html":
                # HTML export for interactive charts
                fig.write_html(filepath, include_plotlyjs="cdn")
            else:
                # Static image export with high-DPI
                fig.write_image(filepath, **export_config)

        except Exception as e:
            print(f"Warning: High-quality export failed, using standard settings: {e}")
            # Fallback to standard export
            fig.write_image(filepath, format=format)

        return filepath

    def create_enhanced_gauge(
        self,
        ax: Any,  # Will be a Plotly figure or subplot
        value: float,
        title: str,
        max_value: float = 100,
        mode: str = "light",
    ) -> None:
        """
        Create sophisticated gauge chart for metrics using Plotly.

        Args:
            ax: Plotly figure or subplot (implementation pending)
            value: Current value
            title: Chart title
            max_value: Maximum value for gauge
            mode: 'light' or 'dark' mode
        """
        # TODO: Implement in Phase 2
        raise NotImplementedError("Plotly gauge chart implementation pending")

    def create_enhanced_monthly_bars(
        self, ax: Any, monthly_data: list[MonthlyPerformance], mode: str = "light"
    ) -> None:
        """
        Create enhanced monthly performance bar chart using Plotly.

        Args:
            ax: Plotly figure or subplot
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """
        if not monthly_data:
            # For empty data, create empty figure
            if isinstance(ax, go.Figure):
                ax.add_annotation(
                    text="No monthly data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=12),
                )
            return None

        # Apply scalability optimizations if available
        if self.scalability_manager:
            timeline_category = self.scalability_manager.detect_monthly_timeline_category(monthly_data)
            months = self.scalability_manager.optimize_monthly_labels(monthly_data, timeline_category)
        else:
            months = [f"{data.month[:3]} {str(data.year)[2:]}" for data in monthly_data]

        win_rates = [data.win_rate for data in monthly_data]
        returns = [data.average_return for data in monthly_data]

        # Get theme and colors
        theme = self.theme_manager.get_theme_colors(mode)
        colors = self.theme_mapper.get_monthly_colors_list()
        performance_colors = self.theme_mapper.get_performance_colors_mapping()

        # Create bar chart
        fig = go.Figure()

        # Add bars with custom colors
        bar_colors = colors[: len(months)] * (len(months) // len(colors) + 1)
        bar_colors = bar_colors[: len(months)]

        fig.add_trace(
            go.Bar(
                x=list(range(len(months))),
                y=win_rates,
                name="Win Rate",
                marker=dict(
                    color=bar_colors,
                    opacity=0.8,
                    line=dict(color=theme.borders, width=1),
                ),
                text=[f"{rate:.0f}%" for rate in win_rates],
                textposition="outside",
                textfont=dict(size=9, color=theme.primary_text, family="bold"),
                hovertemplate="Month: %{x}<br>Win Rate: %{y:.0f}%<extra></extra>",
            )
        )

        # Add return labels inside bars
        for i, (month, win_rate, ret) in enumerate(zip(months, win_rates, returns, strict=False)):
            return_color = performance_colors["positive"] if ret >= 0 else performance_colors["negative"]
            fig.add_annotation(
                x=i,
                y=win_rate / 2,
                text=f"{ret:+.1f}%",
                showarrow=False,
                font=dict(size=8, color=return_color, family="bold"),
                xref="x",
                yref="y",
            )

        # Update layout
        self.theme_mapper.apply_theme_to_figure(fig, mode, "Monthly Win Rate & Returns")

        fig.update_xaxes(
            ticktext=months,
            tickvals=list(range(len(months))),
            tickangle=-45 if len(months) > 6 else 0,
            tickfont=dict(size=9),
        )

        fig.update_yaxes(title="Win Rate (%)", range=[0, 110], gridcolor=theme.borders, gridwidth=0.5)

        # Handle different ax types
        if isinstance(ax, dict) and "row" in ax and "col" in ax:
            # This is for subplot integration (future use)
            return fig
        if isinstance(ax, go.Figure):
            # Update the provided figure by adding traces
            for trace in fig.data:
                ax.add_trace(trace)
            ax.update_layout(fig.layout)
            return ax
        # Return the figure for flexibility
        return fig

    def create_enhanced_donut_chart(
        self, ax: Any, quality_data: list[QualityDistribution], mode: str = "light"
    ) -> None:
        """
        Create sophisticated donut chart for quality distribution using Plotly.

        Args:
            ax: Plotly figure or subplot
            quality_data: Quality distribution data
            mode: 'light' or 'dark' mode
        """
        if not quality_data:
            # For empty data, create empty figure
            if isinstance(ax, go.Figure):
                ax.add_annotation(
                    text="No quality data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=12),
                )
            return None

        categories = [q.category for q in quality_data]
        percentages = [q.percentage for q in quality_data]
        win_rates = [q.win_rate for q in quality_data]

        # Get theme and colors
        theme = self.theme_manager.get_theme_colors(mode)
        quality_colors = self.theme_mapper.get_quality_colors_mapping()
        colors = [quality_colors.get(cat, theme.borders) for cat in categories]

        # Create donut chart
        fig = go.Figure()

        # Create custom text for each slice
        custom_text = []
        hover_text = []
        for cat, pct, wr in zip(categories, percentages, win_rates, strict=False):
            custom_text.append(f"{cat}<br>{pct:.1f}%")
            hover_text.append(f"{cat}<br>Percentage: {pct:.1f}%<br>Win Rate: {wr:.0f}%")

        fig.add_trace(
            go.Pie(
                labels=categories,
                values=percentages,
                hole=0.6,  # Create donut effect
                marker=dict(colors=colors, line=dict(color=theme.background, width=2)),
                text=custom_text,
                textposition="outside",
                textinfo="text",
                textfont=dict(size=9, color=theme.body_text, family="bold"),
                hovertext=hover_text,
                hoverinfo="text",
                pull=[0.05 if cat == "Excellent" else 0 for cat in categories],  # Slight pull for excellent trades
                rotation=90,  # Start from top
            )
        )

        # Add center text
        fig.add_annotation(
            text="Quality<br>Distribution",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=11, color=theme.primary_text, family="bold"),
        )

        # Add win rate indicators
        for i, (category, percentage, win_rate) in enumerate(zip(categories, percentages, win_rates, strict=False)):
            # Calculate angle for positioning
            angle_sum = sum(percentages[:i]) + percentage / 2
            angle = 90 - (angle_sum / 100 * 360)  # Convert to radians from top
            angle_rad = np.radians(angle)

            # Position for win rate text (inside the donut)
            r = 0.45  # Radius for text placement
            x = 0.5 + r * np.cos(angle_rad)
            y = 0.5 + r * np.sin(angle_rad)

            fig.add_annotation(
                x=x,
                y=y,
                text=f"{win_rate:.0f}%",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=7, color="white", family="bold"),
                bgcolor=colors[i],
                borderpad=2,
            )

        # Update layout
        self.theme_mapper.apply_theme_to_figure(fig, mode, "Trade Quality Analysis")

        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=80, b=20))

        # Handle different ax types
        if isinstance(ax, dict) and "row" in ax and "col" in ax:
            return fig
        if isinstance(ax, go.Figure):
            # Update the provided figure by adding traces
            for trace in fig.data:
                ax.add_trace(trace)
            ax.update_layout(fig.layout)
            return ax
        return fig

    def create_waterfall_chart(self, ax: Any, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create sophisticated waterfall chart using Plotly.

        Args:
            ax: Plotly figure or subplot
            trades: Trade data
            mode: 'light' or 'dark' mode
        """
        if not trades:
            if isinstance(ax, go.Figure):
                ax.add_annotation(
                    text="No trade data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=12),
                )
            return None

        # Check for scalability optimization
        if self.scalability_manager:
            trade_category = self.scalability_manager.detect_trade_volume_category(trades)

            # For large datasets, use performance bands instead
            if trade_category in ["large", "medium"]:
                return self._create_performance_bands_chart(ax, trades, mode)

        theme = self.theme_manager.get_theme_colors(mode)
        performance_colors = self.theme_mapper.get_performance_colors_mapping()

        # Sort trades by return for better visualization
        sorted_trades = sorted(trades, key=lambda x: x.return_pct, reverse=True)
        returns = [trade.return_pct for trade in sorted_trades]
        tickers = [trade.ticker for trade in sorted_trades]

        # Calculate cumulative returns for waterfall effect
        cumulative: npt.NDArray[np.float64] = np.cumsum(np.array([0] + returns[:-1]))
        final_cumulative = cumulative + np.array(returns)

        # Create figure
        fig = go.Figure()

        # Create waterfall bars using separate bar traces for positive/negative
        for i, (ret, cum, ticker) in enumerate(zip(returns, cumulative, tickers, strict=False)):
            color = performance_colors["positive"] if ret >= 0 else performance_colors["negative"]

            # Add individual bar
            fig.add_trace(
                go.Bar(
                    x=[i],
                    y=[abs(ret)],
                    base=[cum if ret >= 0 else cum + ret],
                    marker=dict(
                        color=color,
                        opacity=0.8,
                        line=dict(color=theme.borders, width=0.5),
                    ),
                    name=f"{ticker}: {ret:+.1f}%",
                    showlegend=False,
                    hovertemplate=f"<b>{ticker}</b><br>Return: {ret:+.1f}%<br>Cumulative: {cum + ret:.1f}%<extra></extra>",
                )
            )

            # Add value labels for significant trades
            if abs(ret) > 2:  # Only label trades > 2%
                label_y = cum + ret / 2 if ret >= 0 else cum + ret / 2
                fig.add_annotation(
                    x=i,
                    y=label_y,
                    text=f"{ret:+.1f}%",
                    showarrow=False,
                    font=dict(size=8, color="white", family="bold"),
                    xref="x",
                    yref="y",
                )

        # Add cumulative line with enhanced styling
        fig.add_trace(
            go.Scatter(
                x=list(range(len(returns))),
                y=final_cumulative.tolist(),
                mode="lines+markers",
                line=dict(color=self.theme_manager.color_palette.tertiary_data, width=3),
                marker=dict(
                    size=6,
                    color=self.theme_manager.color_palette.tertiary_data,
                    line=dict(color="white", width=1),
                ),
                name="Cumulative Return",
                showlegend=False,
                hovertemplate="Cumulative: %{y:.1f}%<extra></extra>",
            )
        )

        # Add zero line
        fig.add_hline(y=0, line=dict(color=theme.body_text, dash="solid", width=1), opacity=0.5)

        # Add performance zones
        self._add_performance_zones_plotly(fig, final_cumulative.tolist(), theme)

        # Update layout
        self.theme_mapper.apply_theme_to_figure(fig, mode, "Trade Performance Waterfall")

        # Configure axes
        fig.update_xaxes(
            title="Trade Rank (by Performance)",
            ticktext=[tickers[i] for i in range(0, len(trades), max(1, len(trades) // 8))],
            tickvals=list(range(0, len(trades), max(1, len(trades) // 8))),
            tickangle=-45,
            tickfont=dict(size=8),
        )

        fig.update_yaxes(title="Return (%)", gridcolor=theme.borders, gridwidth=0.5)

        # Handle different ax types
        if isinstance(ax, dict) and "row" in ax and "col" in ax:
            return fig
        if isinstance(ax, go.Figure):
            for trace in fig.data:
                ax.add_trace(trace)
            ax.update_layout(fig.layout)
            return ax
        return fig

    def create_enhanced_scatter(self, ax: Any, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create enhanced scatter plot using Plotly with clustering for high-density management.

        Args:
            ax: Plotly figure or subplot
            trades: Trade data
            mode: 'light' or 'dark' mode
        """
        if not trades:
            if isinstance(ax, go.Figure):
                ax.add_annotation(
                    text="No trade data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=12),
                )
            return None

        theme = self.theme_manager.get_theme_colors(mode)
        quality_colors = self.theme_mapper.get_quality_colors_mapping()

        # Check for clustering optimization
        if self.scalability_manager:
            density_category = self.scalability_manager.detect_scatter_density_category(trades)

            if density_category == "high":
                # Use clustering for high-density plots
                cluster_info = self.scalability_manager.cluster_scatter_points(trades)
                return self._create_clustered_scatter(ax, cluster_info, mode)
            if density_category == "medium":
                base_alpha = 0.6
            else:
                base_alpha = 0.8
        else:
            base_alpha = 0.8

        durations = [trade.duration_days for trade in trades]
        returns = [trade.return_pct for trade in trades]

        # Create figure
        fig = go.Figure()

        # Enhanced color, size, and labeling by trade significance
        colors = []
        sizes = []
        alphas = []
        hover_texts = []

        # Calculate sizing based on return magnitude and position significance
        max_return = max(abs(t.return_pct) for t in trades) if trades else 1

        for trade in trades:
            # Color by quality
            color = quality_colors.get(trade.quality, theme.borders)
            colors.append(color)

            # Enhanced sizing: base size + magnitude scaling + outlier boost
            magnitude_factor = abs(trade.return_pct) / max(max_return, 1) if max_return > 0 else 0
            base_size = 15  # Base size for Plotly (different scale than matplotlib)
            magnitude_size = magnitude_factor * 20
            outlier_boost = 5 if abs(trade.return_pct) > 5 else 0

            sizes.append(base_size + magnitude_size + outlier_boost)

            # Alpha based on quality with density adjustment
            quality_alpha = {
                "Excellent": 0.9,
                "Good": 0.8,
                "Poor": 0.6,
                "Failed": 0.5,
                "Poor Setup": 0.4,
            }.get(trade.quality, 0.6)
            alphas.append(quality_alpha * base_alpha)

            # Create hover text
            hover_texts.append(
                f"<b>{trade.ticker}</b><br>"
                f"Duration: {trade.duration_days} days<br>"
                f"Return: {trade.return_pct:+.1f}%<br>"
                f"Quality: {trade.quality}"
            )

        # Group trades by quality for separate traces (better legend control)
        quality_groups = {}
        for i, trade in enumerate(trades):
            quality = trade.quality
            if quality not in quality_groups:
                quality_groups[quality] = {
                    "durations": [],
                    "returns": [],
                    "sizes": [],
                    "alphas": [],
                    "hover_texts": [],
                    "color": quality_colors.get(quality, theme.borders),
                }

            quality_groups[quality]["durations"].append(durations[i])
            quality_groups[quality]["returns"].append(returns[i])
            quality_groups[quality]["sizes"].append(sizes[i])
            quality_groups[quality]["alphas"].append(alphas[i])
            quality_groups[quality]["hover_texts"].append(hover_texts[i])

        # Add scatter traces for each quality group
        for quality, group in quality_groups.items():
            fig.add_trace(
                go.Scatter(
                    x=group["durations"],
                    y=group["returns"],
                    mode="markers",
                    marker=dict(
                        size=group["sizes"],
                        color=group["color"],
                        opacity=(
                            group["alphas"][0] if group["alphas"] else base_alpha
                        ),  # Use first alpha as representative
                        line=dict(color=theme.borders, width=0.8),
                    ),
                    name=quality,
                    text=group["hover_texts"],
                    hovertemplate="%{text}<extra></extra>",
                    showlegend=False,  # Disable legend for cleaner look
                )
            )

        # Add trend line if we have enough data
        if len(durations) > 1:
            z = np.polyfit(durations, returns, 1)
            p = np.poly1d(z)
            trend_x = np.linspace(min(durations), max(durations), 100)
            trend_y = p(trend_x)

            fig.add_trace(
                go.Scatter(
                    x=trend_x,
                    y=trend_y,
                    mode="lines",
                    line=dict(
                        color=self.theme_manager.color_palette.tertiary_data,
                        width=2,
                        dash="dash",
                    ),
                    name="Trend",
                    opacity=0.7,
                    showlegend=False,
                    hovertemplate="Trend Line<extra></extra>",
                )
            )

        # Add zero line for returns
        fig.add_hline(y=0, line=dict(color=theme.body_text, dash="solid", width=1), opacity=0.3)

        # Add annotations for significant trades
        self._add_ticker_labels_plotly(fig, trades, durations, returns, sizes, theme)

        # Update layout
        self.theme_mapper.apply_theme_to_figure(fig, mode, "Duration vs Return Analysis")

        fig.update_xaxes(title="Duration (days)", gridcolor=theme.borders, gridwidth=0.5)

        fig.update_yaxes(title="Return (%)", gridcolor=theme.borders, gridwidth=0.5)

        # Handle different ax types
        if isinstance(ax, dict) and "row" in ax and "col" in ax:
            return fig
        if isinstance(ax, go.Figure):
            for trace in fig.data:
                ax.add_trace(trace)
            ax.update_layout(fig.layout)
            return ax
        return fig

    def create_performance_summary_panel(
        self,
        ax: Any,
        trades: list[TradeData],
        monthly_data: list[MonthlyPerformance],
        mode: str = "light",
    ) -> None:
        """
        Create summary performance panel with key insights using Plotly.

        Args:
            ax: Plotly figure or subplot (implementation pending)
            trades: Trade data
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """
        # TODO: Implement in Phase 3
        raise NotImplementedError("Plotly performance panel implementation pending")

    def export_chart_config(self, chart_type: str, config: dict[str, Any]) -> dict[str, Any]:
        """
        Export chart configuration as JSON schema for frontend consumption.

        Args:
            chart_type: Type of chart
            config: Chart configuration

        Returns:
            JSON-serializable chart configuration
        """
        mode = config.get("mode", "light")
        theme = self.theme_manager.get_theme_colors(mode)

        # Base schema structure
        schema = {
            "engine": "plotly",
            "chart_type": chart_type,
            "version": "1.0.0",
            "theme": {
                "mode": mode,
                "colors": {
                    "primary_data": self.theme_manager.color_palette.primary_data,
                    "secondary_data": self.theme_manager.color_palette.secondary_data,
                    "tertiary_data": self.theme_manager.color_palette.tertiary_data,
                    "background": theme.background,
                    "text": theme.primary_text,
                    "borders": theme.borders,
                },
                "typography": {
                    "font_family": ", ".join(self.theme_manager._get_font_list()),
                    "title_size": 18,
                    "label_size": 10,
                    "annotation_size": 9,
                },
            },
            "layout": {
                "margin": {"l": 60, "r": 60, "t": 80, "b": 60},
                "showlegend": False,
                "hovermode": "closest",
            },
        }

        # Add chart-specific configuration
        if chart_type == "enhanced_monthly_bars":
            schema["chart_config"] = {
                "type": "bar",
                "orientation": "vertical",
                "opacity": 0.8,
                "text_position": "outside",
                "show_grid": True,
                "y_range": [0, 110],
            }
        elif chart_type == "enhanced_donut_chart":
            schema["chart_config"] = {
                "type": "pie",
                "hole": 0.6,
                "text_position": "outside",
                "rotation": 90,
                "pull_excellent": 0.05,
            }
        elif chart_type == "waterfall_chart":
            schema["chart_config"] = {
                "type": "waterfall",
                "cumulative_line": True,
                "performance_zones": True,
                "label_threshold": 2.0,
                "scalability_bands": True,
            }
        elif chart_type == "enhanced_scatter":
            schema["chart_config"] = {
                "type": "scatter",
                "trend_line": True,
                "clustering": True,
                "bubble_sizing": True,
                "ticker_labels": True,
                "density_optimization": True,
            }

        # Add data requirements
        schema["data_requirements"] = self._get_data_requirements(chart_type)

        return schema

    def _get_data_requirements(self, chart_type: str) -> dict[str, Any]:
        """Get data requirements for specific chart type."""
        if chart_type == "enhanced_monthly_bars":
            return {
                "fields": [
                    {"name": "month", "type": "string", "required": True},
                    {"name": "year", "type": "number", "required": True},
                    {
                        "name": "win_rate",
                        "type": "number",
                        "required": True,
                        "range": [0, 100],
                    },
                    {"name": "average_return", "type": "number", "required": True},
                ],
                "format": "array_of_objects",
            }
        if chart_type == "enhanced_donut_chart":
            return {
                "fields": [
                    {"name": "category", "type": "string", "required": True},
                    {
                        "name": "percentage",
                        "type": "number",
                        "required": True,
                        "range": [0, 100],
                    },
                    {
                        "name": "win_rate",
                        "type": "number",
                        "required": True,
                        "range": [0, 100],
                    },
                ],
                "format": "array_of_objects",
            }
        if chart_type == "waterfall_chart":
            return {
                "fields": [
                    {"name": "ticker", "type": "string", "required": True},
                    {"name": "return_pct", "type": "number", "required": True},
                    {"name": "duration_days", "type": "number", "required": True},
                    {"name": "quality", "type": "string", "required": True},
                ],
                "format": "array_of_objects",
            }
        if chart_type == "enhanced_scatter":
            return {
                "fields": [
                    {"name": "ticker", "type": "string", "required": True},
                    {"name": "duration_days", "type": "number", "required": True},
                    {"name": "return_pct", "type": "number", "required": True},
                    {"name": "quality", "type": "string", "required": True},
                ],
                "format": "array_of_objects",
            }
        return {}

    def _add_performance_zones_plotly(self, fig: go.Figure, cumulative_returns: list, theme) -> None:
        """Add performance zones to Plotly waterfall chart."""
        if not cumulative_returns:
            return

        max_cum = max(cumulative_returns)
        min_cum = min(cumulative_returns)

        # Only add breakeven line if we have both positive and negative returns
        if max_cum > 0 and min_cum < 0:
            fig.add_annotation(
                x=len(cumulative_returns) * 0.02,
                y=0.5,
                text="Breakeven",
                showarrow=False,
                font=dict(size=8, color=theme.body_text),
                bgcolor=theme.background,
                bordercolor=theme.borders,
                borderwidth=1,
                opacity=0.8,
            )

    def _create_performance_bands_chart(self, ax: Any, trades: list[TradeData], mode: str = "light") -> None:
        """Create performance bands chart for medium/large datasets using Plotly."""
        if not self.scalability_manager:
            # Fallback to waterfall if no scalability manager
            return self.create_waterfall_chart(ax, trades, mode)

        theme = self.theme_manager.get_theme_colors(mode)
        performance_colors = self.theme_mapper.get_performance_colors_mapping()

        # Get performance bands
        bands = self.scalability_manager.create_performance_bands(trades)

        if not bands:
            if isinstance(ax, go.Figure):
                ax.add_annotation(
                    text="No performance data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=12),
                )
            return None

        # Create figure
        fig = go.Figure()

        # Create horizontal bar chart of performance bands
        band_names = list(bands.keys())
        band_counts = [len(band_trades) for band_trades in bands.values()]

        # Color mapping for bands
        band_colors = []
        for name in band_names:
            if "Winner" in name:
                band_colors.append(performance_colors["positive"])
            elif "Loser" in name:
                band_colors.append(performance_colors["negative"])
            else:
                band_colors.append(theme.borders)

        # Create horizontal bars
        fig.add_trace(
            go.Bar(
                x=band_counts,
                y=band_names,
                orientation="h",
                marker=dict(
                    color=band_colors,
                    opacity=0.8,
                    line=dict(color=theme.borders, width=1),
                ),
                text=[str(count) for count in band_counts],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Trades: %{x}<extra></extra>",
            )
        )

        # Update layout
        self.theme_mapper.apply_theme_to_figure(fig, mode, "Performance Distribution by Bands")

        fig.update_xaxes(title="Number of Trades", gridcolor=theme.borders, gridwidth=0.5)

        fig.update_yaxes(categoryorder="total ascending")  # Show best performers at top

        # Handle different ax types
        if isinstance(ax, dict) and "row" in ax and "col" in ax:
            return fig
        if isinstance(ax, go.Figure):
            for trace in fig.data:
                ax.add_trace(trace)
            ax.update_layout(fig.layout)
            return ax
        return fig

    def _create_clustered_scatter(self, ax: Any, cluster_info: dict[str, Any], mode: str = "light") -> None:
        """Create clustered scatter plot for high-density datasets using Plotly."""
        theme = self.theme_manager.get_theme_colors(mode)
        quality_colors = self.theme_mapper.get_quality_colors_mapping()

        # Create figure
        fig = go.Figure()

        # Plot cluster centroids
        for cluster in cluster_info["clusters"]:
            centroid_dur, centroid_ret = cluster["centroid"]
            cluster_size = cluster["size"]

            # Size based on cluster size
            marker_size = 25 + cluster_size * 2  # Adjusted for Plotly scale

            # Color based on average return
            color = (
                self.theme_manager.color_palette.primary_data
                if centroid_ret >= 0
                else self.theme_manager.color_palette.secondary_data
            )

            # Plot centroid
            fig.add_trace(
                go.Scatter(
                    x=[centroid_dur],
                    y=[centroid_ret],
                    mode="markers+text",
                    marker=dict(
                        size=marker_size,
                        color=color,
                        opacity=0.7,
                        line=dict(color=theme.borders, width=2),
                    ),
                    text=[str(cluster_size)],
                    textfont=dict(color="white", size=8),
                    textposition="middle center",
                    name=f"Cluster ({cluster_size} trades)",
                    showlegend=False,
                    hovertemplate=f"<b>Cluster Center</b><br>Duration: {centroid_dur:.1f} days<br>Return: {centroid_ret:.1f}%<br>Size: {cluster_size} trades<extra></extra>",
                )
            )

        # Plot noise points (individual trades not in clusters)
        if cluster_info["noise"]:
            noise_durations = [t.duration_days for t in cluster_info["noise"]]
            noise_returns = [t.return_pct for t in cluster_info["noise"]]
            noise_colors = [quality_colors.get(t.quality, theme.borders) for t in cluster_info["noise"]]
            noise_tickers = [t.ticker for t in cluster_info["noise"]]

            fig.add_trace(
                go.Scatter(
                    x=noise_durations,
                    y=noise_returns,
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=noise_colors,
                        opacity=0.6,
                        line=dict(color=theme.borders, width=0.5),
                    ),
                    text=[
                        f"<b>{ticker}</b><br>Duration: {dur} days<br>Return: {ret:+.1f}%"
                        for ticker, dur, ret in zip(noise_tickers, noise_durations, noise_returns, strict=False)
                    ],
                    hovertemplate="%{text}<extra></extra>",
                    name="Individual Trades",
                    showlegend=False,
                )
            )

        # Add clustering statistics annotation
        stats_text = f"Clusters: {cluster_info['total_clusters']}<br>Grouped: {cluster_info['clustered_points']}<br>Individual: {cluster_info['noise_points']}"
        fig.add_annotation(
            x=0.02,
            y=0.98,
            text=stats_text,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=8, color=theme.primary_text),
            bgcolor=theme.card_backgrounds,
            bordercolor=theme.borders,
            borderwidth=1,
            opacity=0.8,
        )

        # Add zero line for returns
        fig.add_hline(y=0, line=dict(color=theme.body_text, dash="solid", width=1), opacity=0.3)

        # Update layout
        self.theme_mapper.apply_theme_to_figure(fig, mode, "Duration vs Return Analysis (Clustered)")

        fig.update_xaxes(title="Duration (days)", gridcolor=theme.borders, gridwidth=0.5)

        fig.update_yaxes(title="Return (%)", gridcolor=theme.borders, gridwidth=0.5)

        # Handle different ax types
        if isinstance(ax, dict) and "row" in ax and "col" in ax:
            return fig
        if isinstance(ax, go.Figure):
            for trace in fig.data:
                ax.add_trace(trace)
            ax.update_layout(fig.layout)
            return ax
        return fig

    def _add_ticker_labels_plotly(
        self,
        fig: go.Figure,
        trades: list[TradeData],
        durations: list,
        returns: list,
        sizes: list,
        theme,
    ) -> None:
        """Add ticker labels to significant trades in Plotly scatter plot."""
        if not trades:
            return

        # Determine which trades are significant enough for labeling
        significant_trades = []
        for i, trade in enumerate(trades):
            # Label trades that are outliers or highly significant
            is_outlier = abs(returns[i]) > 5.0  # High return magnitude
            is_extreme_duration = durations[i] > 45 or durations[i] < 3  # Extreme holding periods
            is_large_bubble = sizes[i] > 30  # Large bubble indicates significance

            if is_outlier or is_extreme_duration or is_large_bubble:
                significant_trades.append((trade, durations[i], returns[i]))

        # Add annotations for significant trades
        for trade, dur, ret in significant_trades[:10]:  # Limit to 10 labels to avoid clutter
            # Calculate label position with offset
            label_offset_x = 2.0
            label_offset_y = 0.5 if ret >= 0 else -0.5

            fig.add_annotation(
                x=dur + label_offset_x,
                y=ret + label_offset_y,
                text=trade.ticker,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor=theme.borders,
                ax=dur,
                ay=ret,
                font=dict(size=9, color=theme.primary_text),
                bgcolor=theme.card_backgrounds,
                bordercolor=theme.borders,
                borderwidth=0.5,
                opacity=0.8,
            )
