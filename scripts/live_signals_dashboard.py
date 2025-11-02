#!/usr/bin/env python3
"""
Live Signals Dashboard Generator

Generates interactive Plotly dashboards for live signals trade history with:
- 2x2 grid layout for comprehensive signal analysis
- High-DPI PNG export with dual-mode variants
- Frontend-ready JSON configurations
- Cole Morton design system compliance
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


class LiveSignalsDashboard:
    """Generate interactive Plotly dashboards for live signals data"""

    def __init__(self, sensylate_theme: dict[str, Any] | None = None):
        """Initialize dashboard generator with Cole Morton theme"""
        self.theme = sensylate_theme or self._default_sensylate_theme()
        self._setup_plotly_theme()

    def _default_sensylate_theme(self) -> dict[str, Any]:
        """Default Cole Morton design system theme"""
        return {
            "colors": {
                "primary": "#26c6da",
                "secondary": "#7e57c2",
                "tertiary": "#3179f5",
                "success": "#4caf50",
                "warning": "#ff9800",
                "danger": "#f44336",
                "background_light": "#ffffff",
                "background_dark": "#1a1a1a",
                "text_light": "#333333",
                "text_dark": "#ffffff",
            },
            "fonts": {"primary": "Heebo", "fallback": "Arial, sans-serif"},
            "spacing": {"margin": 60, "padding": 20},
        }

    def _setup_plotly_theme(self):
        """Setup custom Plotly themes for Cole Morton design system"""
        # Light theme
        light_template = go.layout.Template(
            layout=go.Layout(
                font=dict(family=self.theme["fonts"]["primary"], size=12),
                plot_bgcolor="white",
                paper_bgcolor="white",
                colorway=[
                    self.theme["colors"]["primary"],
                    self.theme["colors"]["secondary"],
                    self.theme["colors"]["tertiary"],
                    self.theme["colors"]["success"],
                    self.theme["colors"]["warning"],
                    self.theme["colors"]["danger"],
                ],
                margin=dict(
                    l=self.theme["spacing"]["margin"],
                    r=self.theme["spacing"]["margin"],
                    t=self.theme["spacing"]["margin"],
                    b=self.theme["spacing"]["margin"],
                ),
            )
        )
        pio.templates["colemorton_light"] = light_template

        # Dark theme
        dark_template = go.layout.Template(
            layout=go.Layout(
                font=dict(
                    family=self.theme["fonts"]["primary"],
                    size=12,
                    color=self.theme["colors"]["text_dark"],
                ),
                plot_bgcolor=self.theme["colors"]["background_dark"],
                paper_bgcolor=self.theme["colors"]["background_dark"],
                colorway=[
                    self.theme["colors"]["primary"],
                    self.theme["colors"]["secondary"],
                    self.theme["colors"]["tertiary"],
                    self.theme["colors"]["success"],
                    self.theme["colors"]["warning"],
                    self.theme["colors"]["danger"],
                ],
                margin=dict(
                    l=self.theme["spacing"]["margin"],
                    r=self.theme["spacing"]["margin"],
                    t=self.theme["spacing"]["margin"],
                    b=self.theme["spacing"]["margin"],
                ),
            )
        )
        pio.templates["colemorton_dark"] = dark_template

    def parse_live_signals_report(self, file_path: Path) -> dict[str, Any]:
        """Parse live signals markdown report and extract structured data"""
        with open(file_path) as f:
            content = f.read()

        data = {
            "metadata": self._extract_metadata(content),
            "portfolio_overview": self._extract_portfolio_overview(content),
            "positions": self._extract_positions_table(content),
            "performance_metrics": self._extract_performance_metrics(content),
            "composition": self._extract_composition_data(content),
        }

        return data

    def _extract_metadata(self, content: str) -> dict[str, Any]:
        """Extract report metadata"""
        lines = content.split("\n")
        header_line = lines[1] if len(lines) > 1 else ""

        metadata = {}
        # Extract portfolio, date, type from header
        if "Portfolio" in header_line:
            portfolio_match = re.search(r"\*\*Portfolio\*\*:\s*([^|]+)", header_line)
            if portfolio_match:
                metadata["portfolio"] = portfolio_match.group(1).strip()

        if "Date" in header_line:
            date_match = re.search(r"\*\*Date\*\*:\s*([^|]+)", header_line)
            if date_match:
                metadata["date"] = date_match.group(1).strip()

        if "Type" in header_line:
            type_match = re.search(r"\*\*Type\*\*:\s*(.+)", header_line)
            if type_match:
                metadata["type"] = type_match.group(1).strip()

        return metadata

    def _extract_portfolio_overview(self, content: str) -> dict[str, Any]:
        """Extract portfolio overview metrics"""
        overview = {}

        # Extract key metrics using regex patterns
        patterns = {
            "active_positions": r"Active Positions\*\*:\s*(\d+)",
            "portfolio_performance": r"Portfolio Performance\*\*:\s*([+\-]?\d+\.?\d*%)",
            "unrealized_pnl": r"Unrealized P&L\*\*:\s*([+\-]?\$[\d,]+\.?\d*)",
            "average_position_age": r"Average Position Age\*\*:\s*(\d+\.?\d*)\s*days",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                # Clean numeric values
                if key == "portfolio_performance":
                    overview[key] = float(value.replace("%", ""))
                elif key == "unrealized_pnl":
                    overview[key] = float(value.replace("$", "").replace(",", ""))
                elif key == "average_position_age":
                    overview[key] = float(value)
                else:
                    overview[key] = value

        return overview

    def _extract_positions_table(self, content: str) -> list[dict[str, Any]]:
        """Extract positions from the complete active positions table"""
        positions = []

        # Find the table section
        table_start = content.find("## 📋 Complete Active Positions Table")
        if table_start == -1:
            return positions

        table_section = content[table_start:]
        lines = table_section.split("\n")

        # Find the actual table data (skip headers and separators)
        table_data_started = False
        for line in lines:
            if "|" in line and not line.strip().startswith("|---"):
                if "Rank" in line and "Ticker" in line:
                    table_data_started = True
                    continue
                if table_data_started and line.strip().startswith("|"):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 8:  # Ensure we have all columns
                        try:
                            position = {
                                "rank": int(parts[1]) if parts[1].isdigit() else 0,
                                "ticker": parts[2],
                                "strategy": parts[3],
                                "entry_date": parts[4],
                                "days_held": int(parts[5]) if parts[5].isdigit() else 0,
                                "current_return": self._parse_percentage(parts[6]),
                                "trend_status": parts[7],
                                "risk_level": parts[8] if len(parts) > 8 else "Medium",
                            }
                            positions.append(position)
                        except (ValueError, IndexError):
                            continue

        return positions

    def _extract_performance_metrics(self, content: str) -> dict[str, Any]:
        """Extract historical performance metrics"""
        metrics = {}

        patterns = {
            "total_closed_signals": r"Total Closed Signals\*\*:\s*(\d+)",
            "win_rate": r"Win Rate\*\*:\s*([\d.]+)%",
            "profit_factor": r"Profit Factor\*\*:\s*([\d.]+)",
            "average_win": r"Average Win\*\*:\s*([+\-]?[\d.]+)%",
            "average_loss": r"Average Loss\*\*:\s*([+\-]?[\d.]+)%",
            "best_trade": r"Best Closed Trade\*\*:\s*\w+\s*([+\-]?[\d.]+)%",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                if key in ["win_rate", "average_win", "average_loss", "best_trade"] or key == "profit_factor":
                    metrics[key] = float(value)
                else:
                    metrics[key] = int(value) if value.isdigit() else value

        return metrics

    def _extract_composition_data(self, content: str) -> dict[str, Any]:
        """Extract portfolio composition data"""
        composition = {}

        # Extract sector exposure
        if "Technology-heavy" in content:
            tech_match = re.search(r"Technology-heavy \((\d+)/(\d+) positions\)", content)
            if tech_match:
                tech_positions = int(tech_match.group(1))
                total_positions = int(tech_match.group(2))
                composition["technology_exposure"] = tech_positions / total_positions * 100

        # Extract strategy mix
        sma_match = re.search(r"(\d+\.?\d*)% SMA", content)
        ema_match = re.search(r"(\d+\.?\d*)% EMA", content)
        if sma_match and ema_match:
            composition["sma_percentage"] = float(sma_match.group(1))
            composition["ema_percentage"] = float(ema_match.group(1))

        return composition

    def _parse_percentage(self, value: str) -> float:
        """Parse percentage string to float"""
        if isinstance(value, str):
            return float(value.replace("%", "").replace("+", ""))
        return float(value)

    def generate_dashboard(self, data: dict[str, Any], mode: str = "both") -> tuple[go.Figure | None, go.Figure | None]:
        """Generate 2x2 grid dashboard with dual-mode variants"""
        light_fig = None
        dark_fig = None

        if mode in ["light", "both"]:
            light_fig = self._create_dashboard_figure(data, "light")

        if mode in ["dark", "both"]:
            dark_fig = self._create_dashboard_figure(data, "dark")

        return light_fig, dark_fig

    def _create_dashboard_figure(self, data: dict[str, Any], theme_mode: str) -> go.Figure:
        """Create 2x2 grid dashboard figure"""
        # Create subplots with 2x2 grid
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                "Active Positions Performance",
                "Portfolio Metrics Overview",
                "Position Duration vs Return",
                "Strategy Distribution",
            ],
            specs=[
                [{"type": "bar"}, {"type": "indicator"}],
                [{"type": "scatter"}, {"type": "pie"}],
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1,
        )

        positions = data.get("positions", [])
        metrics = data.get("performance_metrics", {})
        composition = data.get("composition", {})

        # Top Left: Active Positions Performance (Bar Chart)
        if positions:
            tickers = [pos["ticker"] for pos in positions]
            returns = [pos["current_return"] for pos in positions]
            colors = [(self.theme["colors"]["success"] if r > 0 else self.theme["colors"]["danger"]) for r in returns]

            fig.add_trace(
                go.Bar(x=tickers, y=returns, marker_color=colors, name="Position Returns"),
                row=1,
                col=1,
            )

        # Top Right: Portfolio Metrics (Gauge-style indicators)
        portfolio_overview = data.get("portfolio_overview", {})
        win_rate = metrics.get("win_rate", 0)
        portfolio_perf = portfolio_overview.get("portfolio_performance", 0)

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=win_rate,
                domain={"x": [0.6, 1], "y": [0.6, 1]},
                title={"text": "Win Rate (%)"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": self.theme["colors"]["primary"]},
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 75], "color": "yellow"},
                        {"range": [75, 100], "color": "green"},
                    ],
                },
            ),
            row=1,
            col=2,
        )

        # Bottom Left: Duration vs Return Scatter
        if positions:
            days_held = [pos["days_held"] for pos in positions]
            returns = [pos["current_return"] for pos in positions]
            tickers = [pos["ticker"] for pos in positions]

            fig.add_trace(
                go.Scatter(
                    x=days_held,
                    y=returns,
                    mode="markers+text",
                    text=tickers,
                    textposition="top center",
                    marker=dict(
                        size=10,
                        color=self.theme["colors"]["tertiary"],
                        line=dict(width=2, color="white"),
                    ),
                    name="Positions",
                ),
                row=2,
                col=1,
            )

        # Bottom Right: Strategy Distribution (Pie Chart)
        if composition:
            sma_pct = composition.get("sma_percentage", 0)
            ema_pct = composition.get("ema_percentage", 0)

            if sma_pct > 0 or ema_pct > 0:
                fig.add_trace(
                    go.Pie(
                        labels=["SMA", "EMA"],
                        values=[sma_pct, ema_pct],
                        marker_colors=[
                            self.theme["colors"]["primary"],
                            self.theme["colors"]["secondary"],
                        ],
                        name="Strategy Mix",
                    ),
                    row=2,
                    col=2,
                )

        # Apply theme template
        template = f"sensylate_{theme_mode}"
        fig.update_layout(
            template=template,
            title=f"Live Signals Dashboard - {data.get('metadata', {}).get('date', 'Current')}",
            height=800,
            width=1200,
            showlegend=False,
        )

        return fig

    def export_dashboard(
        self,
        light_fig: go.Figure | None,
        dark_fig: go.Figure | None,
        output_dir: Path,
        filename_base: str,
    ) -> list[Path]:
        """Export dashboard figures as high-DPI PNG files"""
        exported_files = []
        output_dir.mkdir(parents=True, exist_ok=True)

        # Configure high-DPI export settings
        export_config = {
            "format": "png",
            "width": 1600,
            "height": 1600,
            "scale": 2,  # High-DPI scaling
        }

        if light_fig:
            light_path = output_dir / f"{filename_base}_light.png"
            light_fig.write_image(str(light_path), **export_config)
            exported_files.append(light_path)

        if dark_fig:
            dark_path = output_dir / f"{filename_base}_dark.png"
            dark_fig.write_image(str(dark_path), **export_config)
            exported_files.append(dark_path)

        return exported_files

    def generate_frontend_config(self, data: dict[str, Any], output_dir: Path) -> Path:
        """Generate frontend-ready JSON configuration"""
        config = {
            "dashboard_type": "live_signals",
            "metadata": data.get("metadata", {}),
            "chart_config": {
                "layout": "2x2_grid",
                "charts": [
                    {
                        "position": "top_left",
                        "type": "bar",
                        "title": "Active Positions Performance",
                        "data_source": "positions",
                    },
                    {
                        "position": "top_right",
                        "type": "gauge",
                        "title": "Portfolio Metrics",
                        "data_source": "metrics",
                    },
                    {
                        "position": "bottom_left",
                        "type": "scatter",
                        "title": "Duration vs Return",
                        "data_source": "positions",
                    },
                    {
                        "position": "bottom_right",
                        "type": "pie",
                        "title": "Strategy Distribution",
                        "data_source": "composition",
                    },
                ],
            },
            "theme": {
                "primary_color": self.theme["colors"]["primary"],
                "font_family": self.theme["fonts"]["primary"],
                "dual_mode_support": True,
            },
            "data": data,
            "generated_at": datetime.now().isoformat(),
        }

        config_path = output_dir / "live_signals_dashboard_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2, default=str)

        return config_path


def main():
    """Main execution function for live signals dashboard generation"""
    # Find the latest live signals report
    live_signals_dir = Path("data/outputs/trade_history/live")
    if not live_signals_dir.exists():
        print("❌ Live signals directory not found")
        return

    # Get the most recent file
    md_files = list(live_signals_dir.glob("live_signals_*.md"))
    if not md_files:
        print("❌ No live signals reports found")
        return

    latest_file = max(md_files, key=lambda x: x.stat().st_mtime)
    print("📊 Processing: {latest_file.name}")

    # Initialize dashboard generator
    dashboard = LiveSignalsDashboard()

    try:
        # Parse the report
        data = dashboard.parse_live_signals_report(latest_file)
        print("✅ Parsed {len(data.get('positions', []))} positions")

        # Generate dashboard
        light_fig, dark_fig = dashboard.generate_dashboard(data, mode="both")
        print("✅ Generated dashboard figures")

        # Export images
        output_dir = latest_file.parent
        filename_base = f"live_signals_dashboard_{datetime.now().strftime('%Y%m%d')}"
        exported_files = dashboard.export_dashboard(light_fig, dark_fig, output_dir, filename_base)

        # Generate frontend config
        config_path = dashboard.generate_frontend_config(data, output_dir)

        print("🎉 Dashboard generation complete!")
        print(f"📸 Exported images: {[f.name for f in exported_files]}")
        print(f"⚙️  Frontend config: {config_path.name}")

    except Exception as e:
        print(f"❌ Dashboard generation failed: {e}")
        raise


if __name__ == "__main__":
    main()
