#!/usr/bin/env python3
"""
Generate interactive Plotly dashboard visualizations using template system.
Web developer approach: analyze, iterate, improve.
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    import plotly.graph_objects as go
    import plotly.io as pio

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.error("Plotly not available. Install with: pip install plotly kaleido")
    sys.exit(1)


class TemplateBasedDashboardGenerator:
    """Generate dashboards using reusable template system."""

    def __init__(self, date_str: str, debug: bool = False):
        """Initialize the generator with a specific date."""
        self.date_str = date_str
        self.debug = debug
        self.report_dir = Path("/Users/colemorton/Projects/colemorton/data/outputs/trade_history")
        self.template_dir = Path("/Users/colemorton/Projects/colemorton/templates/dashboards")

        # Load template
        self.template = self._load_template("historical_performance_template.json")

        # Setup Plotly templates
        self._setup_plotly_templates()

    def _load_template(self, template_name: str) -> dict[str, Any]:
        """Load template configuration."""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path) as f:
            template = json.load(f)

        logger.info(f"Loaded template: {template['template_name']} v{template['version']}")
        return template

    def _setup_plotly_templates(self):
        """Set up custom Plotly templates from template configuration."""
        colors = self.template["color_scheme"]

        # Light theme template
        light_template = go.layout.Template()
        light_template.layout = go.Layout(
            plot_bgcolor=colors["backgrounds"]["light"],
            paper_bgcolor=colors["backgrounds"]["light"],
            font=dict(
                family=self.template["styling"]["fonts"]["family"],
                size=self.template["styling"]["fonts"]["text_size"],
                color=colors["text"]["light_mode"],
            ),
            xaxis=dict(
                gridcolor=colors["grids"]["light_mode"],
                gridwidth=1,
                showgrid=True,
                zeroline=False,
            ),
            yaxis=dict(
                gridcolor=colors["grids"]["light_mode"],
                gridwidth=1,
                showgrid=True,
                zeroline=False,
            ),
            colorway=[
                colors["colemorton_palette"]["primary_data"],
                colors["colemorton_palette"]["secondary_data"],
                colors["colemorton_palette"]["tertiary_data"],
            ],
        )
        pio.templates["colemorton_light"] = light_template

        # Dark theme template
        dark_template = go.layout.Template()
        dark_template.layout = go.Layout(
            plot_bgcolor=colors["backgrounds"]["dark"],
            paper_bgcolor=colors["backgrounds"]["dark"],
            font=dict(
                family=self.template["styling"]["fonts"]["family"],
                size=self.template["styling"]["fonts"]["text_size"],
                color=colors["text"]["dark_mode"],
            ),
            xaxis=dict(
                gridcolor=colors["grids"]["dark_mode"],
                gridwidth=1,
                showgrid=True,
                zeroline=False,
            ),
            yaxis=dict(
                gridcolor=colors["grids"]["dark_mode"],
                gridwidth=1,
                showgrid=True,
                zeroline=False,
            ),
            colorway=[
                colors["colemorton_palette"]["primary_data"],
                colors["colemorton_palette"]["secondary_data"],
                colors["colemorton_palette"]["tertiary_data"],
            ],
        )
        pio.templates["colemorton_dark"] = dark_template

    def run(self):
        """Main execution method."""
        logger.info(f"Starting template-based dashboard generation for date: {self.date_str}")

        # Find HISTORICAL_PERFORMANCE reports only
        reports = self._find_historical_performance_reports()
        if not reports:
            logger.warning(f"No HISTORICAL_PERFORMANCE reports found for date {self.date_str}")
            return

        logger.info(f"Found {len(reports)} HISTORICAL_PERFORMANCE report(s) to process")

        # Process each report
        for report_path in reports:
            try:
                self._process_report(report_path)
            except Exception as e:
                logger.error(f"Error processing {report_path}: {str(e)}")
                if self.debug:
                    raise

    def _find_historical_performance_reports(self) -> list[Path]:
        """Find only HISTORICAL_PERFORMANCE reports matching the date pattern."""
        pattern = f"HISTORICAL_PERFORMANCE_REPORT_*{self.date_str}*.md"
        reports = list(self.report_dir.glob(pattern))
        return sorted(reports)

    def _process_report(self, report_path: Path):
        """Process a single report and generate visualizations."""
        logger.info(f"Processing report: {report_path.name}")

        # Parse report data
        data = self._parse_report(report_path)
        if not data:
            logger.error(f"Failed to parse data from {report_path.name}")
            return

        # Generate performance dashboard with dual mode
        self._generate_dashboard_dual_mode(data, report_path)

    def _parse_report(self, report_path: Path) -> dict[str, Any]:
        """Parse report data from markdown file."""
        try:
            with open(report_path) as f:
                content = f.read()

            data = {
                "content": content,
                "filename": report_path.name,
                "date": self.date_str,
            }

            # Extract comprehensive data
            data["metrics"] = self._extract_metrics(content)
            data["all_trades"] = self._extract_all_trades(content)  # ALL trades for waterfall
            data["weekly_data"] = self._extract_weekly_performance(
                data["all_trades"]
            )  # Weekly performance from entry dates

            return data

        except Exception as e:
            logger.error(f"Error parsing report: {str(e)}")
            return {}

    def _extract_metrics(self, content: str) -> dict[str, Any]:
        """Extract key metrics from report content."""
        metrics = {}

        # Win rate with wins/losses - updated pattern for the actual format
        win_rate_match = re.search(r"Win Rate[:\*\s]+(\d+\.?\d*)%\s*\((\d+)\s*wins?,\s*(\d+)\s*loss", content)
        if win_rate_match:
            metrics["win_rate"] = float(win_rate_match.group(1))
            metrics["wins"] = int(win_rate_match.group(2))
            metrics["losses"] = int(win_rate_match.group(3))

        # Total return - updated pattern
        return_match = re.search(r"Total Return[:\*\s]+([+-]?\d+\.?\d*)%", content)
        if return_match:
            metrics["total_return"] = float(return_match.group(1))

        # Trade count - updated pattern for "completed signals"
        trade_count_match = re.search(r"Total Closed Trades[:\*\s]+(\d+)", content)
        if trade_count_match:
            metrics["trade_count"] = int(trade_count_match.group(1))
        else:
            # Try alternate pattern
            alt_trade_count = re.search(r"(\d+)\s+completed signals", content)
            if alt_trade_count:
                metrics["trade_count"] = int(alt_trade_count.group(1))

        # Profit factor - updated pattern
        pf_match = re.search(r"Profit Factor[:\*\s]+(\d+\.?\d*)", content)
        if pf_match:
            metrics["profit_factor"] = float(pf_match.group(1))

        logger.info(f"Extracted metrics: {metrics}")
        return metrics

    def _extract_all_trades(self, content: str) -> list[dict[str, Any]]:
        """Extract ALL trade data including duration for waterfall chart."""
        trades = []

        # Extract from the complete trade history table with entry/exit dates
        # Pattern: | 1 | **TSLA** | SMA 15-23 | 2025-05-01 | 2025-06-11 | **+16.58%** | 41d | Excellent |
        table_pattern = r"\|\s*\d+\s*\|\s*(?:\*\*)?([A-Z]+)(?:\*\*)?\s*\|.*?\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(?:\*\*)?([+-]?\d+\.?\d*)%(?:\*\*)?\s*\|\s*(\d+)d\s*\|"
        matches = re.finditer(table_pattern, content)

        for match in matches:
            trades.append(
                {
                    "symbol": match.group(1),
                    "entry_date": match.group(2),
                    "exit_date": match.group(3),
                    "return": float(match.group(4)),
                    "duration": int(match.group(5)),
                    "type": "table",
                }
            )
            logger.debug(f"Extracted trade: {match.group(1)} {match.group(4)}% {match.group(5)}d")

        # If no trades found in main table, try alternate patterns
        if not trades:
            # Try individual trade sections
            trade_section_pattern = (
                r"###\s*(?:🥇|🥈|🥉)?\s*([A-Z]+)\s*-\s*\*\*([+-]?\d+\.?\d*)%\*\*.*?Duration:\s*(\d+)\s*days?"
            )
            matches = re.finditer(trade_section_pattern, content, re.DOTALL)

            for match in matches:
                trades.append(
                    {
                        "symbol": match.group(1),
                        "return": float(match.group(2)),
                        "duration": int(match.group(3)),
                        "type": "individual",
                    }
                )

        # If still no trades, try simpler pattern without bold formatting
        if not trades:
            simple_table_pattern = r"\|\s*\d+\s*\|\s*([A-Z]+)\s*\|.*?\|\s*([+-]?\d+\.?\d*)%\s*\|\s*(\d+)d\s*\|"
            matches = re.finditer(simple_table_pattern, content)

            for match in matches:
                trades.append(
                    {
                        "symbol": match.group(1),
                        "return": float(match.group(2)),
                        "duration": int(match.group(3)),
                        "type": "simple_table",
                    }
                )

        # Sort by return value for waterfall (descending: highest to lowest)
        trades.sort(key=lambda x: x["return"], reverse=True)

        logger.info(f"Extracted {len(trades)} total trades for waterfall chart")
        return trades

    def _extract_weekly_performance(self, trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate weekly performance data based on entry dates."""
        from datetime import datetime

        weekly_data = {}

        for trade in trades:
            if "entry_date" in trade:
                try:
                    entry_date = datetime.strptime(trade["entry_date"], "%Y-%m-%d")
                    # Get week number and year
                    year, week, _ = entry_date.isocalendar()
                    week_key = f"{year}-W{week:02d}"

                    if week_key not in weekly_data:
                        weekly_data[week_key] = {
                            "week": week_key,
                            "returns": [],
                            "trade_count": 0,
                        }

                    weekly_data[week_key]["returns"].append(trade["return"])
                    weekly_data[week_key]["trade_count"] += 1
                except ValueError:
                    continue

        # Calculate average return per week
        result = []
        for week_key in sorted(weekly_data.keys()):
            data = weekly_data[week_key]
            avg_return = sum(data["returns"]) / len(data["returns"]) if data["returns"] else 0
            result.append({"week": week_key, "return": avg_return, "trades": data["trade_count"]})

        logger.info(f"Generated weekly performance data for {len(result)} weeks")
        return result

    def _generate_dashboard_dual_mode(self, data: dict[str, Any], report_path: Path):
        """Generate dashboard in both light and dark modes using template."""
        # Generate light mode
        logger.info("Generating light mode dashboard")
        fig_light = self._create_dashboard_from_template(data, "light")
        output_base_light = report_path.parent / f"{report_path.stem}_dashboard_light"
        self._export_figure(fig_light, output_base_light, "light")

        # Generate dark mode
        logger.info("Generating dark mode dashboard")
        fig_dark = self._create_dashboard_from_template(data, "dark")
        output_base_dark = report_path.parent / f"{report_path.stem}_dashboard_dark"
        self._export_figure(fig_dark, output_base_dark, "dark")

    def _create_dashboard_from_template(self, data: dict[str, Any], theme_mode: str) -> go.Figure:
        """Create dashboard using template layout."""
        template_name = f"sensylate_{theme_mode}"
        colors = self.template["color_scheme"]
        is_dark = theme_mode == "dark"

        # Create figure with simple layout to avoid subplot conflicts
        fig = go.Figure()

        # We'll manually position everything using domain specifications

        metrics = data.get("metrics", {})

        # 1. Metrics Gauges (Top Right - 2x2 Grid) - NO RED/GREEN, equal sized gauges
        metric_configs = self.template["chart_definitions"]["metrics_cards"]["metrics"]
        styling = self.template["styling"]

        # 2x2 Grid configuration from template with chart spacing
        top_right_config = self.template["layout"]["structure"]["top_right"]
        gauge_spacing = top_right_config["spacing"]  # 0.05 spacing within gauge grid

        # Get inter-chart spacing from template
        chart_spacing = styling["spacing"]["inter_chart"]  # Template: 2% spacing between main chart areas

        # Calculate 2x2 grid positioning with spacing
        # Right half: 50% + spacing to 100%
        quadrant_x_start = 0.50 + chart_spacing
        quadrant_x_end = 1.0
        # Top half: 50% + spacing to 100%
        quadrant_y_start = 0.50 + chart_spacing
        quadrant_y_end = 1.0

        # Calculate individual gauge dimensions within the quadrant
        gauge_width = (quadrant_x_end - quadrant_x_start - gauge_spacing) / 2  # 2 columns
        gauge_height = (quadrant_y_end - quadrant_y_start - gauge_spacing) / 2  # 2 rows

        # Define 2x2 positions: [top-left, top-right, bottom-left, bottom-right]
        gauge_positions = [
            # Top row
            [
                quadrant_x_start,
                quadrant_x_start + gauge_width,
                quadrant_y_start + gauge_height + gauge_spacing,
                quadrant_y_end,
            ],  # Top-left gauge
            [
                quadrant_x_start + gauge_width + gauge_spacing,
                quadrant_x_end,
                quadrant_y_start + gauge_height + gauge_spacing,
                quadrant_y_end,
            ],  # Top-right gauge
            # Bottom row
            [
                quadrant_x_start,
                quadrant_x_start + gauge_width,
                quadrant_y_start,
                quadrant_y_start + gauge_height,
            ],  # Bottom-left gauge
            [
                quadrant_x_start + gauge_width + gauge_spacing,
                quadrant_x_end,
                quadrant_y_start,
                quadrant_y_start + gauge_height,
            ],  # Bottom-right gauge
        ]

        for i, metric_config in enumerate(metric_configs):
            metric_key = metric_config["key"]
            metric_value = metrics.get(metric_key, 0)

            # Format based on template specification
            if metric_config["format"] == "percentage":
                suffix = "%"
            elif metric_config["format"] == "decimal":
                suffix = ""
            else:  # integer
                suffix = ""

            color_key = metric_config["color"]
            color = colors["colemorton_palette"][color_key]

            # Get position from 2x2 grid
            x_start, x_end, y_start, y_end = gauge_positions[i]

            # Create gauge with ranges from template - NO RED/GREEN
            gauge_range = metric_config.get("range", [0, 100])
            threshold = metric_config.get("threshold", 50)
            gauge_colors = metric_config.get("gauge_colors", {"low": "neutral", "high": "primary_data"})

            low_color = colors["colemorton_palette"][gauge_colors["low"]]
            high_color = colors["colemorton_palette"][gauge_colors["high"]]

            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=metric_value,
                    number={
                        "suffix": suffix,
                        "font": {
                            "size": styling["fonts"]["subtitle_size"],  # Smaller for 2x2 grid
                            "color": color,
                            "family": styling["fonts"]["family"],
                        },
                    },
                    title={
                        "text": metric_config["title"],
                        "font": {
                            "size": styling["fonts"]["text_size"],  # Smaller for 2x2 grid
                            "family": styling["fonts"]["family"],
                        },
                    },
                    gauge={
                        "axis": {
                            "range": gauge_range,
                            "tickwidth": styling["gauges"]["border_width"],
                            "tickfont": {"size": styling["fonts"]["small_text_size"]},  # Smaller ticks
                        },
                        "bar": {
                            "color": color,
                            "thickness": styling["gauges"]["bar_thickness"],
                        },
                        "bgcolor": colors["grids"]["dark_mode" if is_dark else "light_mode"],
                        "borderwidth": styling["gauges"]["border_width"],
                        "bordercolor": colors["text"]["dark_mode" if is_dark else "light_mode"],
                        "steps": [
                            {
                                "range": [gauge_range[0], threshold],
                                "color": f"rgba({int(low_color[1:3], 16)}, {int(low_color[3:5], 16)}, {int(low_color[5:7], 16)}, 0.1)",
                            },
                            {
                                "range": [threshold, gauge_range[1]],
                                "color": f"rgba({int(high_color[1:3], 16)}, {int(high_color[3:5], 16)}, {int(high_color[5:7], 16)}, 0.1)",
                            },
                        ],
                        "threshold": {
                            "line": {
                                "color": colors["text"]["dark_mode" if is_dark else "light_mode"],
                                "width": styling["gauges"]["border_width"],
                            },
                            "thickness": 0.75,
                            "value": threshold,
                        },
                    },
                    domain={
                        "x": [x_start, x_end],
                        "y": [y_start, y_end],
                    },
                )
            )

        # 2. Waterfall Chart - Top Left Quadrant
        if data.get("all_trades"):
            trades = data["all_trades"]
            symbols = [t["symbol"] for t in trades]
            values = [t["return"] for t in trades]
            waterfall_config = styling["waterfall"]

            # Enhanced text positioning with template thresholds
            text_positions = []
            large_threshold = waterfall_config["text_positioning"]["large_threshold"]
            small_threshold = waterfall_config["text_positioning"]["small_threshold"]

            for i, v in enumerate(values):
                if abs(v) > large_threshold:
                    text_positions.append("outside")
                elif abs(v) < small_threshold:
                    text_positions.append("inside")
                else:
                    text_positions.append("auto")

            # ABSOLUTE FIX: Pure individual bars - NO cumulative/waterfall effect
            # This completely eliminates any possibility of total/cumulative bars
            fig.add_trace(
                go.Bar(
                    x=symbols,
                    y=values,  # Raw values, no cumulative calculation
                    text=[f"{v:+.1f}%" for v in values],
                    textposition=text_positions,
                    textfont=dict(
                        size=styling["fonts"]["chart_text_size"],
                        color=colors["text"]["dark_mode" if is_dark else "light_mode"],
                        family=styling["fonts"]["family"],
                    ),
                    marker=dict(
                        color=[
                            (
                                colors["colemorton_palette"]["positive"]
                                if v >= 0
                                else colors["colemorton_palette"]["negative"]
                            )
                            for v in values
                        ],
                        line=dict(
                            color=colors["grids"]["dark_mode" if is_dark else "light_mode"],
                            width=1,
                        ),
                    ),
                    width=1.0 - waterfall_config["bar_gap"],
                    showlegend=False,
                    xaxis="x1",
                    yaxis="y1",
                    name="Trade Returns",
                )
            )

        # 3. Scatter Plot with Trend Line: Return vs Duration (Bottom Left)
        if data.get("all_trades") and any("duration" in t for t in data["all_trades"]):
            trades_with_duration = [t for t in data["all_trades"] if "duration" in t]

            returns = [t["return"] for t in trades_with_duration]
            durations = [t["duration"] for t in trades_with_duration]
            symbols = [t["symbol"] for t in trades_with_duration]

            # Color by profit/loss using template colors
            marker_colors = [
                (colors["colemorton_palette"]["positive"] if r > 0 else colors["colemorton_palette"]["negative"])
                for r in returns
            ]

            # Dramatic visual improvements for scatter plot
            scatter_config = styling["scatter"]

            # Enhanced text positioning with more dramatic offset
            scatter_text_positions = []
            for i, (d, r) in enumerate(zip(durations, returns, strict=False)):
                # Dramatic positioning with template offset
                if r > 0:
                    scatter_text_positions.append("top center")
                else:
                    scatter_text_positions.append("bottom center")

            fig.add_trace(
                go.Scatter(
                    x=durations,
                    y=returns,
                    mode="markers+text",
                    marker=dict(
                        size=scatter_config["marker_size"],  # Template: 14px markers
                        color=marker_colors,
                        line=dict(
                            width=2,
                            color=colors["text"]["dark_mode" if is_dark else "light_mode"],
                        ),
                        symbol="circle",
                    ),
                    text=symbols,
                    textposition=scatter_text_positions,
                    textfont=dict(
                        size=styling["fonts"]["chart_text_size"],  # Template: 14px text
                        color=colors["text"]["dark_mode" if is_dark else "light_mode"],
                        family=styling["fonts"]["family"],  # Heebo font
                    ),
                    showlegend=False,
                    xaxis="x2",
                    yaxis="y2",
                    name="Trades",
                )
            )

            # Add trend line (linear regression)
            try:
                import numpy as np

                z = np.polyfit(durations, returns, 1)
                p = np.poly1d(z)

                # Create trend line points
                x_trend = [min(durations), max(durations)]
                y_trend = [p(x) for x in x_trend]

                fig.add_trace(
                    go.Scatter(
                        x=x_trend,
                        y=y_trend,
                        mode="lines",
                        line=dict(
                            color=colors["colemorton_palette"]["tertiary_data"],
                            width=scatter_config["trend_line_width"],  # Template: 4px trend line
                            dash="dash",
                        ),
                        opacity=scatter_config["trend_line_opacity"],  # Template: 0.85 opacity
                        showlegend=False,
                        xaxis="x2",
                        yaxis="y2",
                        name="Trend",
                    )
                )
            except ImportError:
                # Fallback: simple average line
                avg_return = sum(returns) / len(returns) if returns else 0
                fig.add_trace(
                    go.Scatter(
                        x=[min(durations), max(durations)],
                        y=[avg_return, avg_return],
                        mode="lines",
                        line=dict(
                            color=colors["colemorton_palette"]["tertiary_data"],
                            width=2,
                            dash="dash",
                        ),
                        showlegend=False,
                        xaxis="x2",
                        yaxis="y2",
                        name="Average",
                    )
                )

        # 4. Weekly Performance Bar Chart (Bottom Right) - Based on Entry Dates
        if data.get("weekly_data"):
            weeks = [d["week"] for d in data["weekly_data"]]
            returns = [d["return"] for d in data["weekly_data"]]
            bar_colors = [
                (colors["colemorton_palette"]["positive"] if r > 0 else colors["colemorton_palette"]["negative"])
                for r in returns
            ]

            # Dramatic visual improvements for bar chart
            bar_config = styling["bar_chart"]

            # Enhanced text positioning with template threshold
            bar_text_positions = []
            threshold = bar_config["text_positioning"]["threshold"]
            for r in returns:
                if abs(r) > threshold:  # Template-based threshold
                    bar_text_positions.append("outside")
                else:
                    bar_text_positions.append("inside")

            fig.add_trace(
                go.Bar(
                    x=weeks,
                    y=returns,
                    marker_color=bar_colors,
                    text=[f"{r:+.1f}%" for r in returns],
                    textposition=bar_text_positions,
                    textfont=dict(
                        size=styling["fonts"]["chart_text_size"],  # Template: 14px text
                        color=colors["text"]["dark_mode" if is_dark else "light_mode"],
                        family=styling["fonts"]["family"],  # Heebo font
                    ),
                    width=bar_config["bar_width"],  # Template: 0.75 bar width
                    showlegend=False,
                    xaxis="x3",
                    yaxis="y3",
                )
            )

        # CYCLE 10: Calculate 2x2 grid positioning with equal quadrants

        # 2x2 Grid positioning with chart spacing from template
        chart_spacing = styling["spacing"]["inter_chart"]  # Template: 2% spacing between chart areas

        # Calculate ranges with spacing
        # Vertical ranges: bottom half [0, 0.50-spacing], top half [0.50+spacing, 1.0]
        top_vertical_range = [0.50 + chart_spacing, 1.0]
        bottom_vertical_range = [0.0, 0.50 - chart_spacing]

        # Horizontal ranges: left half [0, 0.50-spacing], right half [0.50+spacing, 1.0]
        left_horizontal_range = [0.0, 0.50 - chart_spacing]
        right_horizontal_range = [0.50 + chart_spacing, 1.0]

        # Annotation positioning for 2x2 grid - ALL ALIGNED AT SAME HEIGHT
        # All top section labels should be at exact same vertical position
        top_label_y = top_vertical_range[1] + 0.02  # Same height for all top labels
        bottom_label_y = bottom_vertical_range[1] + 0.05  # Higher offset for bottom labels to avoid overlap

        waterfall_x = (left_horizontal_range[0] + left_horizontal_range[1]) / 2  # Center of left half
        scatter_x = waterfall_x  # Same as waterfall (left half center)
        weekly_x = (right_horizontal_range[0] + right_horizontal_range[1]) / 2  # Center of right half

        # CYCLE 9: Template-driven layout with NO TEXT CLIPPING
        fig.update_layout(
            template=template_name,
            title={
                "text": f"Historical Trading Performance Dashboard - {self.date_str}",
                "font": {
                    "size": styling["fonts"]["title_size"],  # Template: 34px title
                    "family": styling["fonts"]["family"],  # Heebo font
                },
                "x": 0.5,
                "xanchor": "center",
            },
            showlegend=False,
            height=styling["dimensions"]["height"],  # Template: 1000px
            width=styling["dimensions"]["width"],  # Template: 1600px
            margin=dict(
                l=styling["margins"]["left"],  # Template: 160px margins
                r=styling["margins"]["right"],  # Template: 160px margins
                t=styling["margins"]["top"],  # Template: 200px top margin
                b=styling["margins"]["bottom"],  # Template: 160px bottom margin
            ),
            # Axis definitions using 2x2 grid positioning with spacing
            xaxis1=dict(
                domain=left_horizontal_range,  # [0.0, 0.48] - Left half for waterfall
                anchor="y1",
                title=dict(
                    text="Symbol",
                    font=dict(
                        size=styling["fonts"]["text_size"],
                        family=styling["fonts"]["family"],
                    ),
                ),
                tickangle=45,
                tickfont=dict(
                    size=styling["fonts"]["chart_text_size"],
                    family=styling["fonts"]["family"],
                ),
            ),
            yaxis1=dict(
                domain=top_vertical_range,  # [0.52, 1.0] - Top half for waterfall
                anchor="x1",
                title=dict(
                    text="Return (%)",
                    font=dict(
                        size=styling["fonts"]["text_size"],
                        family=styling["fonts"]["family"],
                    ),
                ),
                tickfont=dict(
                    size=styling["fonts"]["chart_text_size"],
                    family=styling["fonts"]["family"],
                ),
            ),
            xaxis2=dict(
                domain=left_horizontal_range,  # [0.0, 0.48] - Left half for scatter
                anchor="y2",
                title=dict(
                    text="Duration (days)",
                    font=dict(
                        size=styling["fonts"]["text_size"],
                        family=styling["fonts"]["family"],
                    ),
                ),
                tickfont=dict(
                    size=styling["fonts"]["chart_text_size"],
                    family=styling["fonts"]["family"],
                ),
            ),
            yaxis2=dict(
                domain=bottom_vertical_range,  # [0.0, 0.48] - Bottom half for scatter
                anchor="x2",
                title=dict(
                    text="Return (%)",
                    font=dict(
                        size=styling["fonts"]["text_size"],
                        family=styling["fonts"]["family"],
                    ),
                ),
                tickfont=dict(
                    size=styling["fonts"]["chart_text_size"],
                    family=styling["fonts"]["family"],
                ),
            ),
            xaxis3=dict(
                domain=right_horizontal_range,  # [0.52, 1.0] - Right half for weekly
                anchor="y3",
                title=dict(
                    text="Week",
                    font=dict(
                        size=styling["fonts"]["text_size"],
                        family=styling["fonts"]["family"],
                    ),
                ),
                tickangle=25,
                tickfont=dict(
                    size=styling["fonts"]["chart_text_size"],
                    family=styling["fonts"]["family"],
                ),
            ),
            yaxis3=dict(
                domain=bottom_vertical_range,  # [0.0, 0.48] - Bottom half for weekly
                anchor="x3",
                title=dict(
                    text="Return (%)",
                    font=dict(
                        size=styling["fonts"]["text_size"],
                        family=styling["fonts"]["family"],
                    ),
                ),
                tickfont=dict(
                    size=styling["fonts"]["chart_text_size"],
                    family=styling["fonts"]["family"],
                ),
            ),
        )

        # 2x2 Grid annotations - ALL PROPERLY ALIGNED
        annotations = [
            dict(
                text="All Trade Performance",
                x=waterfall_x,  # Center of left half
                y=top_label_y,  # ALIGNED: Same height as gauge labels
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    size=styling["fonts"]["text_size"],
                    family=styling["fonts"]["family"],
                    color=colors["text"]["dark_mode" if is_dark else "light_mode"],
                ),
                xanchor="center",
            ),
            dict(
                text="Return vs Duration",
                x=scatter_x,  # Center of left half
                y=bottom_label_y,  # FIXED: Higher offset to avoid overlap with waterfall x-axis
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    size=styling["fonts"]["text_size"],
                    family=styling["fonts"]["family"],
                    color=colors["text"]["dark_mode" if is_dark else "light_mode"],
                ),
                xanchor="center",
            ),
            dict(
                text="Weekly Performance",
                x=weekly_x,  # Center of right half
                y=bottom_label_y,  # ALIGNED: Same height as Return vs Duration
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    size=styling["fonts"]["text_size"],
                    family=styling["fonts"]["family"],
                    color=colors["text"]["dark_mode" if is_dark else "light_mode"],
                ),
                xanchor="center",
            ),
        ]

        # Add zero line for scatter plot
        if data.get("all_trades"):
            fig.add_hline(
                y=0,
                line_dash="dash",
                line_color=colors["grids"]["dark_mode" if is_dark else "light_mode"],
                xref="x2",
                yref="y2",
            )

        fig.update_layout(annotations=annotations)

        return fig

    def _export_figure(self, fig: go.Figure, output_base: Path, theme_mode: str):
        """Export figure using template export settings."""
        export_settings = self.template["export_settings"]

        try:
            # Export PNG with template DPI scale
            png_path = f"{output_base}.png"
            dpi_scale = self.template["styling"]["dimensions"]["dpi_scale"]
            fig.write_image(png_path, scale=dpi_scale)
            logger.info(f"Exported high-DPI PNG to {png_path}")

            # Generate frontend configuration if enabled
            if export_settings["config_export"]:
                self._generate_frontend_config(fig, output_base, theme_mode)

        except Exception as e:
            logger.error(f"Failed to export PNG: {str(e)}")
            if self.debug:
                raise

    def _generate_frontend_config(self, fig: go.Figure, output_base: Path, theme_mode: str):
        """Generate frontend-ready JSON configuration."""
        config = {
            "chartType": "plotly",
            "template": self.template["template_name"],
            "version": self.template["version"],
            "title": fig.layout.title.text if fig.layout.title else "",
            "data": fig.to_dict(),
            "exportPath": str(output_base),
            "generatedAt": datetime.now().isoformat(),
            "theme": f"sensylate_{theme_mode}",
            "specification": "trade_history_images_v2_template_based",
            "template_config": self.template,
        }

        config_path = f"{output_base}_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Generated frontend config: {config_path}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_trade_history_images_v2.py YYYYMMDD [--debug]")
        sys.exit(1)

    date_str = sys.argv[1]
    debug = "--debug" in sys.argv

    # Validate date format
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        print("Invalid date format: {date_str}. Use YYYYMMDD")
        sys.exit(1)

    # Run generator
    generator = TemplateBasedDashboardGenerator(date_str, debug=debug)
    generator.run()


if __name__ == "__main__":
    main()
