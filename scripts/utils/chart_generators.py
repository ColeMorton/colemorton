#!/usr/bin/env python3
"""
Advanced chart generators for dashboard visualization.

This module provides sophisticated chart generation capabilities with enhanced
styling, animations, and interactive features for trading performance dashboards.
"""

# Add project root to Python path for imports
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle


# Configure path before imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Local imports after path configuration
from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    QualityDistribution,
    TradeData,
)


@dataclass
class ChartConfig:
    """Configuration for individual charts."""

    title: str
    chart_type: str
    colors: list[str]
    background_color: str = "white"
    grid_alpha: float = 0.3
    title_fontsize: int = 12
    label_fontsize: int = 10


class AdvancedChartGenerator:
    """Advanced chart generation with enhanced styling and features."""

    def __init__(self, theme_manager, scalability_manager=None):
        """
        Initialize chart generator.

        Args:
            theme_manager: Theme manager instance
            scalability_manager: Optional scalability manager for volume optimization
        """
        self.theme_manager = theme_manager
        self.scalability_manager = scalability_manager

    def create_enhanced_gauge(
        self,
        ax: plt.Axes,
        value: float,
        title: str,
        max_value: float = 100,
        mode: str = "light",
    ) -> None:
        """
        Create sophisticated gauge chart for metrics.

        Args:
            ax: Axes object
            value: Current value
            title: Chart title
            max_value: Maximum value for gauge
            mode: 'light' or 'dark' mode
        """
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.2, 1.2)
        ax.set_aspect("equal")
        ax.axis("off")

        theme = self.theme_manager.get_theme_colors(mode)

        # Background arc
        bg_arc = patches.Arc(
            (0, 0),
            2,
            2,
            angle=0,
            theta1=0,
            theta2=180,
            linewidth=8,
            color=theme.borders,
            alpha=0.3,
        )
        ax.add_patch(bg_arc)

        # Value arc
        value_angle = (value / max_value) * 180
        value_arc = patches.Arc(
            (0, 0),
            2,
            2,
            angle=0,
            theta1=0,
            theta2=value_angle,
            linewidth=8,
            color=self.theme_manager.color_palette.primary_data,
        )
        ax.add_patch(value_arc)

        # Center circle
        center = Circle(
            (0, 0),
            0.1,
            facecolor=theme.card_backgrounds,
            edgecolor=theme.borders,
            linewidth=2,
        )
        ax.add_patch(center)

        # Value text
        ax.text(
            0,
            -0.3,
            f"{value:.1f}%",
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            color=theme.primary_text,
        )

        # Title
        ax.text(0, -0.5, title, ha="center", va="center", fontsize=10, color=theme.body_text)

    def create_enhanced_monthly_bars(
        self, ax: plt.Axes, monthly_data: list[MonthlyPerformance], mode: str = "light"
    ) -> None:
        """
        Create enhanced monthly performance bar chart with scalability optimization.

        Args:
            ax: Axes object
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """
        if not monthly_data:
            # Hide empty chart by turning off axis
            ax.axis("off")
            return

        # Apply scalability optimizations if available
        if self.scalability_manager:
            timeline_category = self.scalability_manager.detect_monthly_timeline_category(monthly_data)
            months = self.scalability_manager.optimize_monthly_labels(monthly_data, timeline_category)
        else:
            months = [f"{data.month[:3]} {str(data.year)[2:]}" for data in monthly_data]
        win_rates = [data.win_rate for data in monthly_data]
        returns = [data.average_return for data in monthly_data]

        theme = self.theme_manager.get_theme_colors(mode)
        colors = self.theme_manager.get_monthly_colors()

        # Create bars with gradient effect
        x_pos = np.arange(len(months))
        bars = ax.bar(
            x_pos,
            win_rates,
            color=colors[: len(months)],
            alpha=0.8,
            edgecolor=theme.borders,
            linewidth=1,
        )

        # Add value labels on bars
        for i, (bar, rate, ret) in enumerate(zip(bars, win_rates, returns, strict=False)):
            height = bar.get_height()

            # Win rate label
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 2,
                f"{rate:.0f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=theme.primary_text,
            )

            # Return label (smaller, below)
            return_color = (
                self.theme_manager.color_palette.primary_data
                if ret >= 0
                else self.theme_manager.color_palette.secondary_data
            )
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height / 2,
                f"{ret:+.1f}%",
                ha="center",
                va="center",
                fontsize=8,
                color=return_color,
                fontweight="bold",
            )

        # Styling
        ax.set_xticks(x_pos)
        ax.set_xticklabels(months, fontsize=9)
        ax.set_ylabel("Win Rate (%)", fontsize=10, color=theme.body_text)
        # Apply standardized title styling
        self.theme_manager.apply_title_style(ax, "Monthly Win Rate & Returns", mode)
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3, axis="y")

        # Color axes and ticks
        ax.spines["bottom"].set_color(theme.borders)
        ax.spines["left"].set_color(theme.borders)
        ax.tick_params(colors=theme.body_text)

    def create_enhanced_donut_chart(
        self, ax: plt.Axes, quality_data: list[QualityDistribution], mode: str = "light"
    ) -> None:
        """
        Create sophisticated donut chart for quality distribution.

        Args:
            ax: Axes object
            quality_data: Quality distribution data
            mode: 'light' or 'dark' mode
        """
        if not quality_data:
            # Hide empty chart by turning off axis
            ax.axis("off")
            return

        categories = [q.category for q in quality_data]
        percentages = [q.percentage for q in quality_data]
        win_rates = [q.win_rate for q in quality_data]

        theme = self.theme_manager.get_theme_colors(mode)
        quality_colors = self.theme_manager.get_quality_colors()
        colors = [quality_colors.get(cat, theme.borders) for cat in categories]

        # Create donut chart with enhanced styling
        # Handle conditional return signature based on autopct parameter
        pie_result = ax.pie(
            percentages,
            labels=None,  # We'll add custom labels
            colors=colors,
            autopct="",  # We'll add custom percentage labels
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor=theme.background, linewidth=2),
            pctdistance=0.85,
        )

        # Unpack result safely - autopct="" returns 2-tuple, others return 3-tuple
        if len(pie_result) == 3:
            wedges, texts, _ = pie_result  # Ignore autotexts
        else:
            wedges, texts = pie_result

        # Add custom labels outside the donut
        for i, (wedge, category, percentage, win_rate) in enumerate(
            zip(wedges, categories, percentages, win_rates, strict=False)
        ):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = 1.2 * np.cos(np.radians(angle))
            y = 1.2 * np.sin(np.radians(angle))

            # Category label
            ax.text(
                x,
                y,
                f"{category}\n{percentage:.1f}%",
                ha="center",
                va="center",
                fontsize=9,
                color=theme.body_text,
                fontweight="bold",
            )

            # Win rate indicator (small)
            win_rate_x = 0.9 * np.cos(np.radians(angle))
            win_rate_y = 0.9 * np.sin(np.radians(angle))
            ax.text(
                win_rate_x,
                win_rate_y,
                f"{win_rate:.0f}%",
                ha="center",
                va="center",
                fontsize=7,
                color="white",
                fontweight="bold",
            )

        # Center text
        ax.text(
            0,
            0,
            "Quality\nDistribution",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=theme.primary_text,
        )

        # Apply standardized title styling
        self.theme_manager.apply_title_style(ax, "Trade Quality Analysis", mode)

    def create_waterfall_chart(self, ax: plt.Axes, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create sophisticated waterfall chart with scalability optimization.

        Args:
            ax: Axes object
            trades: Trade data
            mode: 'light' or 'dark' mode
        """
        if not trades:
            # Hide empty chart by turning off axis
            ax.axis("off")
            return

        # Check for scalability optimization
        if self.scalability_manager:
            trade_category = self.scalability_manager.detect_trade_volume_category(trades)

            # For large datasets, use performance bands instead of waterfall
            if trade_category == "large":
                self._create_performance_bands_chart(ax, trades, mode)
                return
            if trade_category == "medium":
                # Use performance bands for medium datasets too
                self._create_performance_bands_chart(ax, trades, mode)
                return

        theme = self.theme_manager.get_theme_colors(mode)
        performance_colors = self.theme_manager.get_performance_colors()

        # Sort trades by return for better visualization
        sorted_trades = sorted(trades, key=lambda x: x.return_pct, reverse=True)
        returns = [trade.return_pct for trade in sorted_trades]
        tickers = [trade.ticker for trade in sorted_trades]

        # Calculate cumulative returns for waterfall effect
        cumulative: np.ndarray = np.cumsum(np.array([0] + returns[:-1]))

        # Create waterfall bars
        for i, (ret, cum, ticker) in enumerate(zip(returns, cumulative, tickers, strict=False)):
            color = performance_colors["positive"] if ret >= 0 else performance_colors["negative"]

            # Bar from cumulative to cumulative + return
            ax.bar(
                i,
                abs(ret),
                bottom=cum if ret >= 0 else cum + ret,
                color=color,
                alpha=0.8,
                edgecolor=theme.borders,
                linewidth=0.5,
            )

            # Add value labels for significant trades
            if abs(ret) > 2:  # Only label trades > 2%
                label_y = cum + ret / 2 if ret >= 0 else cum + ret / 2
                ax.text(
                    i,
                    label_y,
                    f"{ret:+.1f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                )

        # Zero line
        ax.axhline(y=0, color=theme.body_text, linestyle="-", alpha=0.5)

        # Cumulative line with enhanced styling
        final_cumulative = cumulative + np.array(returns)
        ax.plot(
            range(len(returns)),
            final_cumulative,
            color=self.theme_manager.color_palette.tertiary_data,
            linewidth=3,
            alpha=0.8,
            marker="o",
            markersize=4,
            markerfacecolor=self.theme_manager.color_palette.tertiary_data,
            markeredgecolor="white",
            markeredgewidth=1,
            label="Cumulative Return",
        )

        # Add performance zones - convert to list to avoid array ambiguity
        self._add_performance_zones(ax, final_cumulative.tolist(), theme)

        # Styling
        ax.set_xlabel("Trade Rank (by Performance)", fontsize=10, color=theme.body_text)
        ax.set_ylabel("Return (%)", fontsize=10, color=theme.body_text)
        # Apply standardized title styling
        self.theme_manager.apply_title_style(ax, "Trade Performance Waterfall", mode)

        # Limit x-axis labels for readability
        if self.scalability_manager:
            label_freq = self.scalability_manager.calculate_adaptive_label_frequency(len(trades))
            ax.set_xticks(range(0, len(trades), label_freq))
            ax.set_xticklabels(
                [tickers[i] for i in range(0, len(trades), label_freq)],
                rotation=45,
                ha="right",
                fontsize=8,
            )
        else:
            step = max(1, len(trades) // 8)
            ax.set_xticks(range(0, len(trades), step))
            ax.set_xticklabels(
                [tickers[i] for i in range(0, len(trades), step)],
                rotation=45,
                ha="right",
                fontsize=8,
            )

        ax.grid(True, alpha=0.3, axis="y")
        ax.tick_params(colors=theme.body_text)

    def _create_performance_bands_chart(self, ax: plt.Axes, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create performance bands chart for medium/large datasets.

        Args:
            ax: Axes object
            trades: Trade data
            mode: 'light' or 'dark' mode
        """
        if not self.scalability_manager:
            # Fallback to waterfall if no scalability manager
            self.create_waterfall_chart(ax, trades, mode)
            return

        theme = self.theme_manager.get_theme_colors(mode)
        performance_colors = self.theme_manager.get_performance_colors()

        # Get performance bands
        bands = self.scalability_manager.create_performance_bands(trades)

        if not bands:
            ax.text(
                0.5,
                0.5,
                "No performance data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return

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
        y_pos = np.arange(len(band_names))
        bars = ax.barh(
            y_pos,
            band_counts,
            color=band_colors,
            alpha=0.8,
            edgecolor=theme.borders,
            linewidth=1,
        )

        # Add count labels
        for i, (bar, count) in enumerate(zip(bars, band_counts, strict=False)):
            ax.text(
                bar.get_width() + 0.1,
                bar.get_y() + bar.get_height() / 2,
                f"{count}",
                ha="left",
                va="center",
                fontsize=10,
                color=theme.primary_text,
                fontweight="bold",
            )

        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(band_names, fontsize=9)
        ax.set_xlabel("Number of Trades", fontsize=10, color=theme.body_text)
        # Apply standardized title styling
        self.theme_manager.apply_title_style(ax, "Performance Distribution by Bands", mode)

        ax.grid(True, alpha=0.3, axis="x")
        ax.tick_params(colors=theme.body_text)

        # Invert y-axis to show best performers at top
        ax.invert_yaxis()

    def create_enhanced_scatter(self, ax: plt.Axes, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create enhanced scatter plot with clustering for high-density management.

        Args:
            ax: Axes object
            trades: Trade data
            mode: 'light' or 'dark' mode
        """
        if not trades:
            # Hide empty chart by turning off axis
            ax.axis("off")
            return

        theme = self.theme_manager.get_theme_colors(mode)
        quality_colors = self.theme_manager.get_quality_colors()

        # Check for clustering optimization
        if self.scalability_manager:
            density_category = self.scalability_manager.detect_scatter_density_category(trades)

            if density_category == "high":
                # Use clustering for high-density plots
                cluster_info = self.scalability_manager.cluster_scatter_points(trades)
                self._create_clustered_scatter(ax, cluster_info, mode)
                return
            if density_category == "medium":
                # Reduce opacity for medium density
                base_alpha = 0.6
            else:
                base_alpha = 0.8
        else:
            base_alpha = 0.8

        durations = [trade.duration_days for trade in trades]
        returns = [trade.return_pct for trade in trades]

        # Enhanced color, size, and labeling by trade significance
        colors = []
        sizes = []
        alphas = []

        # Calculate sizing based on both return magnitude and position significance
        max_return = max(abs(t.return_pct) for t in trades) if trades else 1

        for trade in trades:
            colors.append(quality_colors.get(trade.quality, theme.borders))

            # Enhanced sizing: base size + magnitude scaling + outlier boost
            magnitude_factor = abs(trade.return_pct) / max(max_return, 1) if max_return > 0 else 0
            base_size = 60  # Larger base size for better visibility
            magnitude_size = magnitude_factor * 80  # More pronounced size scaling
            outlier_boost = 20 if abs(trade.return_pct) > 5 else 0  # Boost for significant trades

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

        # Create scatter plot with enhanced styling
        scatter_points = []
        for i, (trade, dur, ret, color, size, alpha) in enumerate(
            zip(trades, durations, returns, colors, sizes, alphas, strict=False)
        ):
            ax.scatter(
                dur,
                ret,
                c=color,
                s=size,
                alpha=alpha,
                edgecolors=theme.borders,
                linewidth=0.8,
                zorder=3,
            )
            scatter_points.append((trade, dur, ret, size))

        # Add ticker labels for significant trades
        self._add_ticker_labels(ax, scatter_points, theme)

        # Add trend line
        if len(durations) > 1:
            z = np.polyfit(durations, returns, 1)
            p = np.poly1d(z)
            trend_x = np.linspace(min(durations), max(durations), 100)
            ax.plot(
                trend_x,
                p(trend_x),
                "--",
                color=self.theme_manager.color_palette.tertiary_data,
                alpha=0.7,
                linewidth=2,
            )

        # Zero line for returns
        ax.axhline(y=0, color=theme.body_text, linestyle="-", alpha=0.3)

        # Quadrant labels removed for cleaner visual presentation

        # Styling
        ax.set_xlabel("Duration (days)", fontsize=10, color=theme.body_text)
        ax.set_ylabel("Return (%)", fontsize=10, color=theme.body_text)
        # Apply standardized title styling
        self.theme_manager.apply_title_style(ax, "Duration vs Return Analysis", mode)

        ax.grid(True, alpha=0.3)
        ax.tick_params(colors=theme.body_text)

        # Legend removed for better visual clarity and space efficiency

    def _add_ticker_labels(self, ax: plt.Axes, scatter_points: list, theme) -> None:
        """Add ticker labels to significant trades in scatter plot."""
        if not scatter_points:
            return

        # Determine which trades are significant enough for labeling
        significant_trades = []
        for trade, dur, ret, size in scatter_points:
            # Label trades that are outliers or highly significant
            is_outlier = abs(ret) > 5.0  # High return magnitude
            is_extreme_duration = dur > 45 or dur < 3  # Extreme holding periods
            is_large_bubble = size > 120  # Large bubble indicates significance

            if is_outlier or is_extreme_duration or is_large_bubble:
                significant_trades.append((trade, dur, ret))

        # Add labels with intelligent positioning to avoid overlap
        labeled_positions: list[tuple[float, float]] = []

        for trade, dur, ret in significant_trades:
            # Calculate label position with offset to avoid overlapping bubble
            label_offset_x = 2.0  # Horizontal offset
            label_offset_y = 0.5 if ret >= 0 else -0.5  # Vertical offset based on return sign

            label_x = dur + label_offset_x
            label_y = ret + label_offset_y

            # Adjust position if it would overlap with existing labels
            for prev_x, prev_y in labeled_positions:
                if abs(label_x - prev_x) < 8 and abs(label_y - prev_y) < 2:
                    label_y += 1.5 if ret >= 0 else -1.5

            # Add the ticker label with enhanced styling
            ax.annotate(
                trade.ticker,
                xy=(dur, ret),
                xytext=(label_x, label_y),
                fontsize=9,
                fontweight="bold",
                color=theme.primary_text,
                ha="left",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor=theme.card_backgrounds,
                    edgecolor=theme.borders,
                    alpha=0.8,
                    linewidth=0.5,
                ),
                arrowprops=dict(
                    arrowstyle="->",
                    connectionstyle="arc3,rad=0.1",
                    color=theme.borders,
                    alpha=0.6,
                    linewidth=1,
                ),
                zorder=4,
            )

            labeled_positions.append((label_x, label_y))

    def _add_performance_zones(self, ax: plt.Axes, cumulative_returns: list, theme) -> None:
        """Add minimal reference lines to waterfall chart."""
        if not cumulative_returns or len(cumulative_returns) == 0:
            return

        # Convert to numpy array for proper handling
        cum_array = np.array(cumulative_returns)
        max_cum = float(np.max(cum_array))
        min_cum = float(np.min(cum_array))

        # Only add breakeven line if we have both positive and negative returns
        if max_cum > 0 and min_cum < 0:
            # Breakeven line - keep this as it's a critical reference
            ax.axhline(y=0, color=theme.borders, linestyle="-", alpha=0.6, linewidth=1.5)
            ax.text(
                len(cumulative_returns) * 0.02,
                0.5,
                "Breakeven",
                fontsize=8,
                color=theme.body_text,
                alpha=0.7,
                bbox=dict(boxstyle="round,pad=0.2", facecolor=theme.background, alpha=0.8),
            )

    def _create_clustered_scatter(self, ax: plt.Axes, cluster_info: dict[str, Any], mode: str = "light") -> None:
        """
        Create clustered scatter plot for high-density datasets.

        Args:
            ax: Axes object
            cluster_info: Clustering information from scalability manager
            mode: 'light' or 'dark' mode
        """
        theme = self.theme_manager.get_theme_colors(mode)
        quality_colors = self.theme_manager.get_quality_colors()

        # Plot cluster centroids
        for cluster in cluster_info["clusters"]:
            centroid_dur, centroid_ret = cluster["centroid"]
            cluster_size = cluster["size"]

            # Size based on cluster size
            marker_size = 100 + cluster_size * 10

            # Color based on average return
            color = (
                self.theme_manager.color_palette.primary_data
                if centroid_ret >= 0
                else self.theme_manager.color_palette.secondary_data
            )

            # Plot centroid
            ax.scatter(
                centroid_dur,
                centroid_ret,
                c=color,
                s=marker_size,
                alpha=0.7,
                edgecolors=theme.borders,
                linewidth=2,
                marker="o",
            )

            # Add cluster size label
            ax.text(
                centroid_dur,
                centroid_ret,
                str(cluster_size),
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

        # Plot noise points (individual trades not in clusters)
        if cluster_info["noise"]:
            noise_durations = [t.duration_days for t in cluster_info["noise"]]
            noise_returns = [t.return_pct for t in cluster_info["noise"]]
            noise_colors = [quality_colors.get(t.quality, theme.borders) for t in cluster_info["noise"]]

            for dur, ret, color in zip(noise_durations, noise_returns, noise_colors, strict=False):
                ax.scatter(
                    dur,
                    ret,
                    c=color,
                    s=30,
                    alpha=0.6,
                    edgecolors=theme.borders,
                    linewidth=0.5,
                )

        # Add clustering statistics text
        stats_text = f"Clusters: {cluster_info['total_clusters']}\nGrouped: {cluster_info['clustered_points']}\nIndividual: {cluster_info['noise_points']}"
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=theme.card_backgrounds,
                edgecolor=theme.borders,
                alpha=0.8,
            ),
        )

        # Zero line for returns
        ax.axhline(y=0, color=theme.body_text, linestyle="-", alpha=0.3)

        # Styling
        ax.set_xlabel("Duration (days)", fontsize=10, color=theme.body_text)
        ax.set_ylabel("Return (%)", fontsize=10, color=theme.body_text)
        # Apply standardized title styling
        self.theme_manager.apply_title_style(ax, "Duration vs Return Analysis (Clustered)", mode)

        ax.grid(True, alpha=0.3)
        ax.tick_params(colors=theme.body_text)

    def create_performance_summary_panel(
        self,
        ax: plt.Axes,
        trades: list[TradeData],
        monthly_data: list[MonthlyPerformance],
        mode: str = "light",
    ) -> None:
        """
        Create summary performance panel with key insights.

        Args:
            ax: Axes object
            trades: Trade data
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        theme = self.theme_manager.get_theme_colors(mode)

        # Calculate key insights
        if trades:
            total_return = sum(trade.return_pct for trade in trades)
            win_rate = len([t for t in trades if t.return_pct > 0]) / len(trades) * 100
            avg_winner = np.mean([t.return_pct for t in trades if t.return_pct > 0])
            avg_loser = np.mean([t.return_pct for t in trades if t.return_pct < 0])

            # Best and worst months
            if monthly_data:
                best_month = max(monthly_data, key=lambda x: x.win_rate)
                worst_month = min(monthly_data, key=lambda x: x.win_rate)

            # Summary text
            summary_text = f"""KEY INSIGHTS

Total Return: {total_return:+.1f}%
Win Rate: {win_rate:.1f}%
Avg Winner: {avg_winner:.1f}%
Avg Loser: {avg_loser:.1f}%

Best Month: {best_month.month if monthly_data else "N/A"}
Worst Month: {worst_month.month if monthly_data else "N/A"}"""

            ax.text(
                0.05,
                0.95,
                summary_text,
                ha="left",
                va="top",
                fontsize=10,
                color=theme.body_text,
                family="monospace",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor=theme.card_backgrounds,
                    edgecolor=theme.borders,
                    alpha=0.8,
                ),
            )


def create_chart_generator(theme_manager, scalability_manager=None) -> AdvancedChartGenerator:
    """
    Factory function to create chart generator.

    Args:
        theme_manager: Theme manager instance
        scalability_manager: Optional scalability manager for volume optimization

    Returns:
        Configured chart generator
    """
    return AdvancedChartGenerator(theme_manager, scalability_manager)


if __name__ == "__main__":
    # Test chart generator
    from scripts.utils.theme_manager import create_theme_manager

    theme_manager = create_theme_manager()
    chart_gen = create_chart_generator(theme_manager)

    # Create test figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # Test gauge
    chart_gen.create_enhanced_gauge(ax, 75.5, "Test Gauge")

    print("Chart generator test completed")
    plt.close(fig)
