#!/usr/bin/env python3
"""
Dashboard generator for creating scalable performance overview visualizations.

This script generates high-resolution dashboard images from historical trading
performance data, following Cole Morton design system specifications.
"""

import argparse
import logging
import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import matplotlib


matplotlib.use("Agg")  # Use non-interactive backend for server environments
from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt

from scripts.utils.chart_generator_factory import ChartGeneratorFactory

# Import our custom modules
from scripts.utils.config_loader import ConfigLoader
from scripts.utils.config_validator import (
    ConfigValidationError,
    validate_dashboard_config,
    validate_input_file,
)
from scripts.utils.dashboard_parser import parse_dashboard_data
from scripts.utils.layout_manager import create_layout_manager
from scripts.utils.logging_setup import setup_logging
from scripts.utils.scalability_manager import create_scalability_manager
from scripts.utils.theme_manager import create_theme_manager


class DashboardGenerator:
    """Main dashboard generation class."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize dashboard generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.theme_manager = create_theme_manager()

        # Configure font fallbacks for proper Heebo font integration
        self.theme_manager.configure_font_fallbacks()

        self.scalability_manager = create_scalability_manager(config)
        self.layout_manager = create_layout_manager(config)

        # Get chart engine from config (default to matplotlib)
        self.chart_engine = ChartGeneratorFactory.get_default_engine(config)
        self.logger.info(f"Using chart engine: {self.chart_engine}")

        # Create chart generator using factory
        self.chart_generator = ChartGeneratorFactory.create_chart_generator(
            self.chart_engine, self.theme_manager, self.scalability_manager
        )

        # Validate theme colors
        if not self.theme_manager.validate_colors():
            raise ValueError("Invalid color configuration in theme manager")

    def generate_dashboard(self, input_file: Path, mode: str = "light") -> Path:
        """
        Generate dashboard visualization.

        Args:
            input_file: Path to the input markdown file
            mode: 'light' or 'dark' mode

        Returns:
            Path to the generated dashboard image
        """
        self.logger.info(f"Generating {mode} mode dashboard from {input_file}")

        # Use Plotly-native generator for Plotly engine
        if self.chart_engine == "plotly":
            from scripts.plotly_dashboard_generator import PlotlyDashboardGenerator

            plotly_generator = PlotlyDashboardGenerator(self.config)
            return plotly_generator.generate_dashboard(input_file, mode)

        # Fall back to matplotlib implementation
        # Parse the input data
        data = parse_dashboard_data(str(input_file))

        # Set up matplotlib with theme
        self._setup_matplotlib(mode)

        # Create the dashboard
        fig = self._create_dashboard_figure(data, mode)

        # Save the output
        output_path = self._save_dashboard(fig, mode)

        plt.close(fig)

        self.logger.info(f"Dashboard saved to {output_path}")
        return output_path

    def _setup_matplotlib(self, mode: str):
        """Setup matplotlib with Cole Morton theme."""
        style_config = self.theme_manager.get_matplotlib_style(mode)

        # Apply style configuration
        for key, value in style_config.items():
            plt.rcParams[key] = value

    def _create_dashboard_figure(self, data: dict[str, Any], mode: str) -> plt.Figure:
        """
        Create the enhanced dashboard figure with adaptive layout.

        Args:
            data: Parsed performance data
            mode: 'light' or 'dark' mode

        Returns:
            Matplotlib figure object
        """
        # Determine layout strategy based on available data
        has_monthly_data = data.get("monthly_performance") and len(data["monthly_performance"]) > 0
        has_quality_data = data.get("quality_distribution") and len(data["quality_distribution"]) > 0

        if has_monthly_data and has_quality_data:
            # Use standard 2x2 grid layout
            return self._create_standard_layout(data, mode)
        # Use adaptive stacked layout
        return self._create_adaptive_layout(data, mode, has_monthly_data, has_quality_data)

    def _create_standard_layout(self, data: dict[str, Any], mode: str) -> plt.Figure:
        """Create standard 2x2 grid layout when all data is available."""
        # Create enhanced layout
        fig, gs = self.layout_manager.create_dashboard_figure()

        # Get theme colors
        theme = self.theme_manager.get_theme_colors(mode)

        # Set figure background
        fig.patch.set_facecolor(theme.background)

        # Create enhanced subplots
        metrics_ax = self.layout_manager.create_metrics_row(fig, gs)
        monthly_ax = self.layout_manager.create_chart_subplot(fig, gs, (1, 0))
        quality_ax = self.layout_manager.create_chart_subplot(fig, gs, (1, 1))
        trades_ax = self.layout_manager.create_chart_subplot(fig, gs, (2, 0))
        duration_ax = self.layout_manager.create_chart_subplot(fig, gs, (2, 1))

        # Generate enhanced chart components
        self._create_enhanced_key_metrics(metrics_ax, data["performance_metrics"], mode)
        self.chart_generator.create_enhanced_monthly_bars(monthly_ax, data["monthly_performance"], mode)
        self.chart_generator.create_enhanced_donut_chart(quality_ax, data["quality_distribution"], mode)
        self.chart_generator.create_waterfall_chart(trades_ax, data["trades"], mode)
        self.chart_generator.create_enhanced_scatter(duration_ax, data["trades"], mode)

        self._add_dashboard_title(fig, data, theme)
        self.layout_manager.finalize_layout(fig)

        return fig

    def _create_adaptive_layout(
        self,
        data: dict[str, Any],
        mode: str,
        has_monthly_data: bool,
        has_quality_data: bool,
    ) -> plt.Figure:
        """Create adaptive stacked layout when some data is missing."""
        # Create custom gridspec for stacked layout
        fig = plt.figure(figsize=(16, 12), dpi=100)

        # Get theme colors
        theme = self.theme_manager.get_theme_colors(mode)
        fig.patch.set_facecolor(theme.background)

        # Define stacked layout with improved spacing and symmetry for larger headers
        gs = fig.add_gridspec(
            3,
            2,
            height_ratios=[
                0.16,
                0.32,
                0.52,
            ],  # Reduced middle row, increased bottom row for better title spacing
            hspace=0.80,
            wspace=0.20,  # Further increased vertical spacing for clear separation
            top=0.89,
            bottom=0.12,
            left=0.06,
            right=0.94,
        )  # Reduced bottom margin to accommodate increased spacing

        # Create subplots with enhanced positioning
        metrics_ax = fig.add_subplot(gs[0, :])  # Full width metrics
        waterfall_ax = fig.add_subplot(gs[1, :])  # Full width waterfall
        duration_ax = fig.add_subplot(gs[2, 0])  # Left: enhanced scatter plot

        # Right side: quality chart or trade statistics based on available data
        if has_quality_data:
            stats_ax = fig.add_subplot(gs[2, 1])
            self.chart_generator.create_enhanced_donut_chart(stats_ax, data["quality_distribution"], mode)
        else:
            stats_ax = fig.add_subplot(gs[2, 1])
            self._create_trade_statistics_panel(stats_ax, data["trades"], mode)

        # Generate enhanced chart components
        self._create_enhanced_key_metrics(metrics_ax, data["performance_metrics"], mode)
        self.chart_generator.create_waterfall_chart(waterfall_ax, data["trades"], mode)
        self.chart_generator.create_enhanced_scatter(duration_ax, data["trades"], mode)

        self._add_dashboard_title(fig, data, theme)

        # Apply enhanced spacing and typography with improved margins
        self._apply_enhanced_styling(fig, [metrics_ax, waterfall_ax, duration_ax, stats_ax], mode)

        return fig

    def _create_trade_statistics_panel(self, ax: plt.Axes, trades: list, mode: str) -> None:
        """Create a trade statistics panel when quality data is not available."""
        # Remove axis limits to allow full utilization of allocated grid space
        ax.axis("off")

        theme = self.theme_manager.get_theme_colors(mode)

        if not trades:
            ax.text(
                0.5,
                0.5,
                "No trade data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=12,
                color=theme.body_text,
            )
            return

        # Calculate trade statistics
        total_trades = len(trades)
        winners = [t for t in trades if t.return_pct > 0]
        losers = [t for t in trades if t.return_pct < 0]
        avg_winner = sum(t.return_pct for t in winners) / len(winners) if winners else 0
        avg_loser = sum(t.return_pct for t in losers) / len(losers) if losers else 0
        avg_duration = sum(t.duration_days for t in trades) / total_trades if trades else 0

        # Calculate comprehensive statistics for institutional-grade display
        profit_factor = abs(avg_winner * len(winners) / avg_loser / len(losers)) if losers and avg_loser != 0 else 0
        largest_winner = max(t.return_pct for t in winners) if winners else 0
        largest_loser = min(t.return_pct for t in losers) if losers else 0
        win_loss_ratio = len(winners) / len(losers) if losers else float("inf")
        total_return = sum(t.return_pct for t in trades)

        # Advanced statistical metrics
        max_duration = max(t.duration_days for t in trades) if trades else 0
        min_duration = min(t.duration_days for t in trades) if trades else 0
        returns = [t.return_pct for t in trades]
        median_return = sorted(returns)[len(returns) // 2] if returns else 0
        total_gross_profit = sum(t.return_pct for t in winners) if winners else 0
        total_gross_loss = sum(t.return_pct for t in losers) if losers else 0
        expectancy = (
            (avg_winner * len(winners) / total_trades) + (avg_loser * len(losers) / total_trades)
            if total_trades > 0
            else 0
        )

        # Additional professional metrics
        consecutive_wins = self._calculate_consecutive_runs(trades, True)
        consecutive_losses = self._calculate_consecutive_runs(trades, False)
        recovery_factor = total_return / abs(largest_loser) if largest_loser != 0 else 0
        sharpe_approximation = (
            (total_return / len(trades))
            / (sum([(r - total_return / len(trades)) ** 2 for r in returns]) / len(trades)) ** 0.5
            if len(trades) > 1
            else 0
        )
        win_rate_pct = len(winners) / total_trades * 100 if total_trades > 0 else 0
        avg_trade_return = total_return / total_trades if total_trades > 0 else 0
        breakeven_trades = len([t for t in trades if abs(t.return_pct) < 0.1])
        total_trades_over_5pct = len([t for t in trades if abs(t.return_pct) > 5])

        # Create expanded institutional-grade two-column layout
        left_column = f"""Total Trades: {total_trades}
Winners: {len(winners)} ({win_rate_pct:.1f}%)
Losers: {len(losers)} ({(100 - win_rate_pct):.1f}%)
Breakeven: {breakeven_trades}
Win/Loss Ratio: {win_loss_ratio:.2f}
Total Return: {total_return:+.1f}%
Avg Trade: {avg_trade_return:+.2f}%
Gross Profit: {total_gross_profit:+.1f}%
Gross Loss: {total_gross_loss:+.1f}%
Expectancy: {expectancy:+.2f}%
Max Consec Wins: {consecutive_wins}
Max Consec Losses: {consecutive_losses}"""

        right_column = f"""Profit Factor: {profit_factor:.2f}
Recovery Factor: {recovery_factor:.2f}
Risk-Adj Return: {sharpe_approximation:.2f}
Avg Winner: {avg_winner:.1f}%
Avg Loser: {avg_loser:.1f}%
Largest Winner: {largest_winner:+.1f}%
Largest Loser: {largest_loser:+.1f}%
Median Return: {median_return:+.1f}%
Avg Duration: {avg_duration:.1f} days
Duration Range: {min_duration}-{max_duration} days
Trades >5%: {total_trades_over_5pct}
Trade Efficiency: {(len(winners) / total_trades * 100):.0f}%"""

        # Create a large background rectangle to fill the entire allocated space for true symmetry
        from matplotlib.patches import Rectangle

        bg_rect = Rectangle(
            (0, 0),
            1,
            1,
            transform=ax.transAxes,
            facecolor=theme.card_backgrounds,
            edgecolor=theme.borders,
            alpha=0.95,
            linewidth=2,
        )
        ax.add_patch(bg_rect)

        # Place left column text with left alignment for better readability
        ax.text(
            0.05,
            0.5,
            left_column,
            ha="left",
            va="center",
            transform=ax.transAxes,
            fontsize=12,  # Increased font size to better fill the space
            color=theme.primary_text,
            family="monospace",
            weight="bold",
            linespacing=1.2,
        )  # Slightly more spacing for readability

        # Place right column text with left alignment for better readability
        ax.text(
            0.52,
            0.5,
            right_column,
            ha="left",
            va="center",
            transform=ax.transAxes,
            fontsize=12,  # Increased font size to better fill the space
            color=theme.primary_text,
            family="monospace",
            weight="bold",
            linespacing=1.2,
        )  # Slightly more spacing for readability

        # Apply standardized title styling
        self.theme_manager.apply_title_style(ax, "Trade Statistics", mode)

    def _calculate_consecutive_runs(self, trades: list, winning: bool) -> int:
        """Calculate maximum consecutive wins or losses."""
        if not trades:
            return 0

        max_consecutive = 0
        current_consecutive = 0

        for trade in trades:
            is_winner = trade.return_pct > 0
            if (winning and is_winner) or (not winning and not is_winner):
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def _add_dashboard_title(self, fig: plt.Figure, data: dict[str, Any], theme) -> None:
        """Add enhanced title and subtitle to dashboard."""
        metadata = data.get("metadata", {})
        title = "Historical Trading Performance Dashboard"
        subtitle = metadata.get("date_range", "")

        self.layout_manager.add_title_and_subtitle(fig, title, subtitle, theme.__dict__)

    def _apply_enhanced_styling(self, fig: plt.Figure, axes: list, mode: str) -> None:
        """Apply enhanced typography and spacing improvements."""
        theme = self.theme_manager.get_theme_colors(mode)

        for ax in axes:
            # Title styling is handled by theme_manager.apply_title_style() - don't override
            # Just handle other styling aspects

            # Improve tick label formatting
            ax.tick_params(labelsize=10, colors=theme.body_text)

            # Enhanced grid styling
            ax.grid(True, alpha=0.25, linewidth=0.8, linestyle="-")

            # Optimize spacing around charts
            if hasattr(ax, "margins"):
                ax.margins(0.02)

        # Apply tight layout with generous spacing for professional presentation and larger headers
        fig.tight_layout(
            rect=[0.04, 0.10, 0.96, 0.83], pad=8.0
        )  # Adjusted margins for 18px headers and increased padding

    def _create_enhanced_key_metrics(self, ax: plt.Axes, metrics, mode: str):
        """Create enhanced key metrics display with Phase 2 features."""
        theme = self.theme_manager.get_theme_colors(mode)

        # Completely hide all axis elements including scales, ticks, and labels
        ax.axis("off")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # Enhanced metrics data with indicators
        metrics_data = [
            {
                "label": "Win Rate",
                "value": f"{metrics.win_rate:.1f}%",
                "indicator": "positive" if metrics.win_rate > 50 else "negative",
            },
            {
                "label": "Total Return",
                "value": f"{metrics.total_return:+.2f}%",
                "indicator": "positive" if metrics.total_return > 0 else "negative",
            },
            {
                "label": "Profit Factor",
                "value": f"{metrics.profit_factor:.2f}",
                "indicator": "positive" if metrics.profit_factor > 1 else "negative",
            },
            {
                "label": "Total Trades",
                "value": f"{metrics.total_trades}",
                "indicator": "neutral",
            },
        ]

        # Use enhanced layout manager for metric cards
        self.layout_manager.create_metric_cards(ax, metrics_data, theme.__dict__)

    def _save_dashboard(self, fig: plt.Figure, mode: str) -> Path:
        """Save the dashboard figure to file."""
        output_config = self.config.get("output", {})
        base_path = Path(output_config.get("base_path", "data/outputs/dashboards"))

        # Ensure output directory exists
        base_path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d")
        if mode == "light":
            filename = output_config.get("light_mode_file", "dashboard-light-{timestamp}.png")
        else:
            filename = output_config.get("dark_mode_file", "dashboard-dark-{timestamp}.png")

        filename = filename.format(timestamp=timestamp)
        output_path = base_path / filename

        # Save with high DPI
        dpi = output_config.get("dpi", 300)
        fig.savefig(
            output_path,
            dpi=dpi,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
            edgecolor="none",
        )

        return output_path


def main(
    config: dict[str, Any],
    input_file: Path,
    mode: str = "both",
    output_dir: Path | None = None,
) -> list[Path]:
    """
    Main execution function.

    Args:
        config: Configuration dictionary
        input_file: Input historical performance markdown file
        mode: Dashboard mode ('light', 'dark', or 'both')
        output_dir: Optional output directory override

    Returns:
        List of generated dashboard file paths
    """
    generator = DashboardGenerator(config)

    # Override output directory if provided
    if output_dir:
        config["output"]["directory"] = str(output_dir)

    modes_to_generate = ["light", "dark"] if mode == "both" else [mode]
    generated_files = []

    for dashboard_mode in modes_to_generate:
        output_file = generator.generate_dashboard(input_file, dashboard_mode)
        generated_files.append(output_file)
        print("Generated {dashboard_mode} mode dashboard: {output_file}")

    # Print Make-compatible output for pipeline integration
    if len(generated_files) == 1:
        print("OUTPUT_FILE={generated_files[0]}")
    else:
        for i, file_path in enumerate(generated_files):
            print("OUTPUT_FILE_{i+1}={file_path}")

    return generated_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="config/pipelines/dashboard_generation.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument("--input", required=True, help="Input historical performance markdown file")
    parser.add_argument(
        "--mode",
        choices=["light", "dark", "both"],
        default="both",
        help="Dashboard mode to generate",
    )
    parser.add_argument("--output-dir", help="Output directory override (default from config)")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment configuration",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate configuration and input, don't generate dashboards",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-essential output (useful for Make integration)",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load_with_environment(args.config, args.env)

        # Setup logging
        if args.quiet:
            # Suppress INFO and lower for quiet mode
            logging.getLogger().setLevel(logging.WARNING)
        else:
            setup_logging(level=args.log_level, log_file=config.get("logging", {}).get("file"))

        # Validate configuration
        try:
            validation_summary = validate_dashboard_config(config)
            if not args.quiet:
                if validation_summary["warning_count"] > 0:
                    print(f"⚠️  Configuration validation passed with {validation_summary['warning_count']} warning(s)")
        except ConfigValidationError:
            print("❌ Configuration validation failed: {e}")
            sys.exit(1)

        # Validate input file
        input_path = Path(args.input)
        try:
            validate_input_file(input_path)
        except ConfigValidationError:
            print("❌ Input file validation failed: {e}")
            sys.exit(1)

        output_dir = Path(args.output_dir) if args.output_dir else None

        if args.validate_only:
            if not args.quiet:
                print("✅ Configuration and input validation successful")
            sys.exit(0)

        # Generate dashboards
        generated_files = main(config, input_path, args.mode, output_dir)

        if not args.quiet:
            print("✅ Successfully generated {len(generated_files)} dashboard file(s)")

    except Exception as e:
        logging.error(f"Dashboard generation failed: {e}")
        sys.exit(1)
