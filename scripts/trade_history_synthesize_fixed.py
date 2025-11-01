#!/usr/bin/env python3
"""
Trade History Synthesize - DASV Phase 3 Implementation (Fixed Version)

Generates comprehensive report synthesis following trade_history:synthesize command requirements:
- Multi-audience document generation (internal, live, historical reports)
- Live Signals context automatic inclusion for live_signals portfolio
- Template compliance and formatting consistency
- Executive dashboard synthesis
- Robust data structure handling

Usage:
    python scripts/trade_history_synthesize_fixed.py --portfolio live_signals
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DASVPhase3SynthesizerFixed:
    """DASV Phase 3 synthesizer for comprehensive report generation (Fixed Version)."""

    def __init__(self, portfolio_name: str):
        self.portfolio_name = portfolio_name
        self.execution_date = datetime.now()
        self.data_dir = Path(__file__).parent.parent / "data"
        self.output_dir = self.data_dir / "outputs" / "trade_history"

        # Ensure output directories exist
        (self.output_dir / "internal").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "live").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "historical").mkdir(parents=True, exist_ok=True)

    def load_phase_data(self) -> dict[str, Any]:
        """Load discovery and analysis data from previous DASV phases."""
        discovery_dir = self.data_dir / "outputs" / "trade_history" / "discovery"
        analysis_dir = self.data_dir / "outputs" / "trade_history" / "analysis"

        # Find latest files
        discovery_files = list(discovery_dir.glob(f"{self.portfolio_name}_*.json"))
        analysis_files = list(analysis_dir.glob(f"{self.portfolio_name}_*.json"))

        if not discovery_files or not analysis_files:
            raise FileNotFoundError(f"Missing required data files for {self.portfolio_name}")

        discovery_file = max(discovery_files, key=lambda f: f.stat().st_mtime)
        analysis_file = max(analysis_files, key=lambda f: f.stat().st_mtime)

        logger.info(f"Loaded discovery data from: {discovery_file}")
        logger.info(f"Loaded analysis data from: {analysis_file}")

        with open(discovery_file) as f:
            discovery_data = json.load(f)

        with open(analysis_file) as f:
            analysis_data = json.load(f)

        # Load raw CSV data for individual trade details
        csv_path = discovery_data["discovery_metadata"]["data_source"]
        import pandas as pd

        df = pd.read_csv(csv_path)

        return {
            "discovery": discovery_data,
            "analysis": analysis_data,
            "raw_trades": df,
        }

    def generate_live_signals_overview(self) -> str:
        """Generate standardized Live Signals Overview section."""
        if self.portfolio_name.lower() != "live_signals":
            return ""

        return """## 📡 Live Signals Overview

### Trading Signal Platform
- **Platform**: X/Twitter [@colemorton7](https://x.com/colemorton7)
- **Signal Type**: Educational trading signals for trend-following strategies
- **Position Sizing**: Single unit position size per strategy signal
- **Risk Management**: Individual risk management and position sizing decisions are made independently

### Methodology & Approach
- **Strategy Focus**: Systematic trend-following using SMA/EMA crossover signals
- **Signal Quality**: Emphasis on high-probability setups with technical and fundamental confluence
- **Transparency**: All signals posted publicly with entry timestamps and reasoning
- **Educational Purpose**: Designed to demonstrate systematic approach to swing trading

### Platform Benefits
- **Real-time Signal Sharing**: Live trade ideas with detailed analysis
- **Performance Tracking**: Transparent results with comprehensive statistics
- **Learning Opportunity**: Educational insights into trend-following methodology
- **Community Engagement**: Interactive discussion of market analysis and trade management

---

"""

    def extract_safe_metrics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Safely extract metrics from the data structure."""
        metrics = {}

        # Discovery data metrics
        if "discovery" in data and "portfolio_summary" in data["discovery"]:
            portfolio = data["discovery"]["portfolio_summary"]
            metrics.update(
                {
                    "total_trades": portfolio.get("total_trades", 0),
                    "closed_trades": portfolio.get("closed_trades", 0),
                    "active_trades": portfolio.get("active_trades", 0),
                    "unique_tickers": portfolio.get("unique_tickers", 0),
                }
            )

        # Analysis data metrics
        if "analysis" in data:
            analysis = data["analysis"]

            # Performance metrics
            if "statistical_analysis" in analysis and "performance_metrics" in analysis["statistical_analysis"]:
                perf = analysis["statistical_analysis"]["performance_metrics"]
                metrics.update(
                    {
                        "win_rate": perf.get("win_rate", 0),
                        "total_pnl": perf.get("total_pnl", 0),
                        "profit_factor": perf.get("profit_factor", 0),
                        "total_wins": perf.get("total_wins", 0),
                        "total_losses": perf.get("total_losses", 0),
                        "expectancy": perf.get("expectancy", 0),
                    }
                )

                # Calculate total return from closed trades data
                # Get the actual returns from the raw trades data
                if "raw_trades" in data:
                    df = data["raw_trades"]
                    closed_trades = df[df["Status"] == "Closed"]
                    if not closed_trades.empty:
                        # Calculate weighted average return (by position size if available, or simple average)
                        total_return = closed_trades["Return"].mean()
                        metrics["total_return"] = total_return
                    else:
                        metrics["total_return"] = 0.0
                else:
                    metrics["total_return"] = 0.0

            # Statistical significance
            if "statistical_analysis" in analysis:
                stats = analysis["statistical_analysis"]["statistical_analysis"]
                if "statistical_significance" in stats:
                    sig = stats["statistical_significance"]["return_vs_zero"]
                    metrics.update(
                        {
                            "p_value": sig.get("p_value", 1.0),
                            "significant": sig.get("significant_at_95", False),
                            "confidence_interval": sig.get("confidence_interval_95", [0, 0]),
                        }
                    )

                # Risk-adjusted metrics
                if "risk_adjusted_metrics" in stats:
                    risk = stats["risk_adjusted_metrics"]
                    metrics.update(
                        {
                            "sharpe_ratio": risk.get("sharpe_ratio", 0),
                            "sortino_ratio": risk.get("sortino_ratio", 0),
                        }
                    )

            # Sample validation
            if "sample_validation" in analysis:
                sample = analysis["sample_validation"]
                metrics.update(
                    {
                        "minimum_sample_met": sample.get("minimum_sample_met", False),
                        "statistical_power": sample.get("statistical_power", 0),
                    }
                )

            # Confidence scores
            if "analysis_metadata" in analysis:
                meta = analysis["analysis_metadata"]
                metrics.update(
                    {
                        "overall_confidence": meta.get("confidence_score", 0),
                        "statistical_significance_conf": meta.get("statistical_significance", 0),
                    }
                )

        return metrics

    def generate_complete_trade_history_table(self, data: dict[str, Any]) -> str:
        """Generate the complete closed trade history table with original correct format."""
        # Get closed trades from raw CSV data
        df = data["raw_trades"]
        closed_trades = df[df["Status"] == "Closed"].copy()

        if closed_trades.empty:
            return "No closed trades available for table generation."

        # Sort by PnL descending for ranking
        closed_trades = closed_trades.sort_values("PnL", ascending=False).reset_index(drop=True)

        # Generate the table header - Original correct format
        table_lines = [
            "## 📋 Complete Closed Trade History",
            "",
            "| **Rank** | **Ticker** | **P&L ($)** | **Return (%)** | **Duration** | **Strategy** | **Quality** | **X/Twitter Link** |",
            "|------|--------|---------|------------|----------|----------|---------|----------------|",
        ]

        # Generate table rows
        for idx, row in closed_trades.iterrows():
            rank = idx + 1
            ticker = row["Ticker"]
            pnl = row["PnL"]
            return_pct = row["Return"] * 100  # Convert to percentage
            duration = f"{int(row['Duration_Days'])}d"

            # Format strategy
            if row["Strategy_Type"] == "SMA":
                strategy = f"SMA {row['Short_Window']}/{row['Long_Window']}"
            else:
                strategy = f"EMA {row['Short_Window']}/{row['Long_Window']}"

            quality = row["Trade_Quality"] if pd.notna(row["Trade_Quality"]) else "Unknown"

            # Format X/Twitter link
            x_status = row["X_Status"] if pd.notna(row["X_Status"]) else ""
            if x_status:
                x_link = f"[Signal](https://x.com/colemorton7/status/{x_status})"
            else:
                x_link = "No Signal"

            # Format PnL with proper sign
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            return_str = f"+{return_pct:.2f}%" if return_pct >= 0 else f"{return_pct:.2f}%"

            table_lines.append(
                f"| {rank} | {ticker} | {pnl_str} | {return_str} | {duration} | {strategy} | {quality} | {x_link} |"
            )

        return "\n".join(table_lines)

    def generate_monthly_performance_section(self, data: dict[str, Any]) -> str:
        """Generate monthly performance breakdown section in parser-compatible format."""
        df = data["raw_trades"]
        closed_trades = df[df["Status"] == "Closed"].copy()

        if closed_trades.empty:
            return "No closed trades available for monthly analysis."

        # Parse entry dates and group by month
        closed_trades["entry_date"] = pd.to_datetime(closed_trades["Entry_Timestamp"])
        closed_trades["month_year"] = closed_trades["entry_date"].dt.to_period("M")

        monthly_sections = ["## 📅 Monthly Performance Breakdown", ""]

        # Group by month and generate performance data
        monthly_groups = closed_trades.groupby("month_year")

        for period, group in monthly_groups:
            month_name = period.strftime("%B")
            year = period.year

            # Calculate monthly metrics
            total_trades = len(group)
            winners = group[group["Return"] > 0]
            win_rate = len(winners) / total_trades if total_trades > 0 else 0
            avg_return = group["Return"].mean() * 100  # Convert to percentage

            # Format section header to match parser regex: ### Month YYYY - Market Context
            monthly_sections.extend(
                [
                    f"### {month_name} {year} - Trading Performance",
                    f"**Trades Closed**: {total_trades}",
                    f"**Win Rate**: {win_rate:.1%}",
                    f"**Average Return**: {avg_return:+.2f}%",
                    f"**Market Context**: {month_name} {year} market performance analysis",
                    "",
                ]
            )

            # Add additional details for context
            if not winners.empty:
                top_winner = winners.loc[winners["PnL"].idxmax()]
                monthly_sections.append(
                    f"- **Best Trade**: {top_winner['Ticker']} (+{top_winner['Return'] * 100:.2f}%)"
                )

            losers = group[group["Return"] < 0]
            if not losers.empty:
                worst_loser = losers.loc[losers["PnL"].idxmin()]
                monthly_sections.append(
                    f"- **Worst Trade**: {worst_loser['Ticker']} ({worst_loser['Return'] * 100:.2f}%)"
                )

            monthly_sections.extend(["", ""])

        return "\n".join(monthly_sections)

    def generate_duration_analysis_section(self, data: dict[str, Any]) -> str:
        """Generate duration analysis section."""
        df = data["raw_trades"]
        closed_trades = df[df["Status"] == "Closed"].copy()

        if closed_trades.empty:
            return "No closed trades available for duration analysis."

        # Categorize by duration
        short_term = closed_trades[closed_trades["Duration_Days"] <= 7]
        medium_term = closed_trades[(closed_trades["Duration_Days"] > 7) & (closed_trades["Duration_Days"] <= 30)]
        long_term = closed_trades[closed_trades["Duration_Days"] > 30]

        duration_sections = ["## ⏰ Duration Analysis", ""]

        # Short-term analysis
        if not short_term.empty:
            st_winners = short_term[short_term["Return"] > 0]
            st_win_rate = len(st_winners) / len(short_term)
            best_st = short_term.loc[short_term["PnL"].idxmax()]

            duration_sections.extend(
                [
                    "### Short-Term Effectiveness (≤7 days)",
                    f"- **Trade Count**: {len(short_term)} trades",
                    f"- **Win Rate**: {st_win_rate:.1%} ({len(st_winners)}W, {len(short_term) - len(st_winners)}L)",
                    f"- **Best Performer**: {best_st['Ticker']} {best_st['Return'] * 100:+.2f}% ({int(best_st['Duration_Days'])} days)",
                    "- **Insights**: Quick exits analysis",
                    "",
                ]
            )

        # Medium-term analysis
        if not medium_term.empty:
            mt_winners = medium_term[medium_term["Return"] > 0]
            mt_win_rate = len(mt_winners) / len(medium_term)
            best_mt = medium_term.loc[medium_term["PnL"].idxmax()]

            duration_sections.extend(
                [
                    "### Medium-Term Performance (8-30 days)",
                    f"- **Trade Count**: {len(medium_term)} trades",
                    f"- **Win Rate**: {mt_win_rate:.1%} ({len(mt_winners)}W, {len(medium_term) - len(mt_winners)}L)",
                    f"- **Best Performer**: {best_mt['Ticker']} {best_mt['Return'] * 100:+.2f}% ({int(best_mt['Duration_Days'])} days)",
                    "- **Insights**: Optimal holding period analysis",
                    "",
                ]
            )

        # Long-term analysis
        if not long_term.empty:
            lt_winners = long_term[long_term["Return"] > 0]
            lt_win_rate = len(lt_winners) / len(long_term)
            best_lt = long_term.loc[long_term["PnL"].idxmax()]

            duration_sections.extend(
                [
                    "### Long-Term Holdings (>30 days)",
                    f"- **Trade Count**: {len(long_term)} trades",
                    f"- **Win Rate**: {lt_win_rate:.1%} ({len(lt_winners)}W, {len(long_term) - len(lt_winners)}L)",
                    f"- **Best Performer**: {best_lt['Ticker']} {best_lt['Return'] * 100:+.2f}% ({int(best_lt['Duration_Days'])} days)",
                    "- **Insights**: Extended holding effectiveness",
                    "",
                ]
            )

        return "\n".join(duration_sections)

    def generate_quality_distribution_section(self, data: dict[str, Any]) -> str:
        """Generate quality distribution section in parser-compatible format."""
        df = data["raw_trades"]
        closed_trades = df[df["Status"] == "Closed"].copy()

        if closed_trades.empty:
            return "No closed trades available for quality analysis."

        # Clean up quality categories
        closed_trades = closed_trades.copy()
        closed_trades.loc[
            closed_trades["Trade_Quality"].str.contains("Poor Setup", na=False),
            "Trade_Quality",
        ] = "Poor"
        closed_trades.loc[
            closed_trades["Trade_Quality"].str.contains("Failed to Capture", na=False),
            "Trade_Quality",
        ] = "Poor"
        closed_trades.loc[closed_trades["Trade_Quality"].isna(), "Trade_Quality"] = "Unknown"

        quality_sections = ["## 📊 Quality Distribution Analysis", ""]

        # Group by quality and generate statistics
        quality_groups = closed_trades.groupby("Trade_Quality")
        total_trades = len(closed_trades)

        # Define order for quality categories
        quality_order = ["Excellent", "Good", "Poor", "Unknown"]

        for quality in quality_order:
            if quality not in quality_groups.groups:
                continue

            group = quality_groups.get_group(quality)
            trade_count = len(group)
            percentage = (trade_count / total_trades) * 100

            # Calculate metrics
            winners = group[group["Return"] > 0]
            win_rate = len(winners) / trade_count if trade_count > 0 else 0
            avg_return = group["Return"].mean() * 100  # Convert to percentage

            # Format section header to match parser regex: ### Quality Trades (X trades - Y%)
            quality_sections.extend(
                [
                    f"### {quality} Trades ({trade_count} trades - {percentage:.1f}%)",
                    f"**Win Rate**: {win_rate:.1%}",
                    f"**Average Return**: {avg_return:+.2f}%",
                    "",
                ]
            )

            # Add top performer for this quality category
            if not group.empty:
                best_trade = group.loc[group["Return"].idxmax()]
                quality_sections.append(
                    f"- **Best {quality} Trade**: {best_trade['Ticker']} ({best_trade['Return'] * 100:+.2f}%)"
                )
                quality_sections.append("")

        return "\n".join(quality_sections)

    def generate_historical_report(self, data: dict[str, Any]) -> str:
        """Generate comprehensive historical performance report."""
        metrics = self.extract_safe_metrics(data)

        report_content = f"""# Live Signals Historical Performance Report
**Portfolio**: {self.portfolio_name} | **Date**: {self.execution_date.strftime("%B %d, %Y")} | **Type**: Closed Positions Analysis

---

{self.generate_live_signals_overview()}## 📊 Performance Summary (Closed Trades Only)

### Overall Results
- **Total Closed Trades**: {metrics.get("closed_trades", 0)} {"✅ **ADEQUATE**" if metrics.get("minimum_sample_met", False) else "⚠️ **LIMITED**"} for basic analysis (minimum 25)
- **Win Rate**: {metrics.get("win_rate", 0):.2%} ({metrics.get("total_wins", 0)} wins, {metrics.get("total_losses", 0)} losses)
- **Total Return**: {metrics.get("total_return", 0):+.1%}
- **Total P&L**: ${metrics.get("total_pnl", 0):,.2f}
- **Profit Factor**: {metrics.get("profit_factor", 0):.2f} (target: 1.50+)
- **Strategy Mix**: Based on {metrics.get("total_trades", 0)} total positions

### Key Performance Metrics
- **Expectancy**: {metrics.get("expectancy", 0):.4f} (Risk-adjusted expectancy per trade)
- **Statistical Significance**: {"✅ **SIGNIFICANT**" if metrics.get("significant", False) else "⚠️ **NOT SIGNIFICANT**"} (p-value: {metrics.get("p_value", 1.0):.4f})
- **Confidence Interval**: [{metrics.get("confidence_interval", [0, 0])[0]:.2%}, {metrics.get("confidence_interval", [0, 0])[1]:.2%}] (95% CI)
- **Risk-Adjusted Performance**: Sharpe {metrics.get("sharpe_ratio", 0):.2f}, Sortino {metrics.get("sortino_ratio", 0):.2f}

### Risk-Adjusted Performance
- **Sharpe Ratio**: {metrics.get("sharpe_ratio", 0):.2f} (Risk-adjusted return metric)
- **Sortino Ratio**: {metrics.get("sortino_ratio", 0):.2f} (Downside risk-focused performance)
- **Statistical Power**: {metrics.get("statistical_power", 0):.1%} (Ability to detect meaningful differences)

---

## 🔍 Statistical Significance Analysis

### Sample Size Assessment
- **Total Trades**: {metrics.get("closed_trades", 0)} closed trades {"✅ **ADEQUATE**" if metrics.get("minimum_sample_met", False) else "⚠️ **LIMITED**"} for portfolio-level analysis
- **Confidence Level**: {metrics.get("overall_confidence", 0):.1%} overall analysis confidence
- **Statistical Significance**: {metrics.get("statistical_significance_conf", 0):.1%} confidence in statistical robustness

### Significance Testing
- **Returns vs Zero**: P-value: {metrics.get("p_value", 1.0):.4f} {"(highly significant positive returns)" if metrics.get("p_value", 1.0) < 0.01 else "(significant positive returns)" if metrics.get("p_value", 1.0) < 0.05 else "(not statistically significant)"}
- **Win Rate Analysis**: {metrics.get("win_rate", 0):.1%} vs 50% random baseline
- **Confidence Interval**: [{metrics.get("confidence_interval", [0, 0])[0]:.2%}, {metrics.get("confidence_interval", [0, 0])[1]:.2%}] (95% confidence bounds)

### Statistical Limitations
{self._generate_statistical_limitations(metrics)}

---

{self.generate_complete_trade_history_table(data)}

---

{self.generate_monthly_performance_section(data)}

---

{self.generate_duration_analysis_section(data)}

---

{self.generate_quality_distribution_section(data)}

---

## 📈 Performance Analysis

### Win Rate Breakdown
- **Overall Win Rate**: {metrics.get("win_rate", 0):.2%}
- **Total Wins**: {metrics.get("total_wins", 0)} profitable trades
- **Total Losses**: {metrics.get("total_losses", 0)} unprofitable trades
- **Profit Factor**: {metrics.get("profit_factor", 0):.2f} (total wins/total losses ratio)

### Key Performance Insights
{self._generate_performance_insights(data, metrics)}

---

## 🎯 Key Learnings

### What Worked
{self._generate_what_worked(data, metrics)}

### What Failed
{self._generate_what_failed(data, metrics)}

### Critical Insights
{self._generate_critical_insights(data, metrics)}

---

{self.generate_live_signals_platform_footer()}"""

        return report_content

    def _generate_statistical_limitations(self, metrics: dict[str, Any]) -> str:
        """Generate statistical limitations section."""
        limitations = []

        if metrics.get("closed_trades", 0) < 25:
            limitations.append(
                f"⚠️ **SAMPLE SIZE LIMITED**: {metrics.get('closed_trades', 0)} closed trades below recommended minimum of 25 for robust statistical analysis"
            )

        if metrics.get("closed_trades", 0) < 15:
            limitations.append(
                "⚠️ **LOW STATISTICAL POWER**: Limited ability to detect meaningful performance differences due to small sample"
            )

        if not metrics.get("significant", False):
            limitations.append(
                "⚠️ **STATISTICAL INSIGNIFICANCE**: Returns not statistically different from zero - larger sample needed for validation"
            )

        if not limitations:
            limitations.append(
                "✅ **STATISTICALLY ROBUST**: Sample size and significance meet institutional analysis standards"
            )

        return "\n".join([f"- {limitation}" for limitation in limitations])

    def _generate_performance_insights(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate performance insights section."""
        insights = []

        win_rate = metrics.get("win_rate", 0)
        if win_rate > 0.6:
            insights.append(f"✅ **STRONG WIN RATE**: {win_rate:.1%} indicates effective signal quality")
        elif win_rate > 0.5:
            insights.append(f"→ **ADEQUATE WIN RATE**: {win_rate:.1%} shows baseline effectiveness")
        else:
            insights.append(f"⚠️ **BELOW AVERAGE WIN RATE**: {win_rate:.1%} suggests signal refinement needed")

        profit_factor = metrics.get("profit_factor", 0)
        if profit_factor > 2.0:
            insights.append(f"✅ **EXCELLENT PROFIT FACTOR**: {profit_factor:.2f} shows strong risk-reward management")
        elif profit_factor > 1.5:
            insights.append(f"→ **GOOD PROFIT FACTOR**: {profit_factor:.2f} indicates positive expectancy")
        else:
            insights.append(f"⚠️ **LOW PROFIT FACTOR**: {profit_factor:.2f} suggests risk-reward optimization needed")

        return "\n".join([f"- {insight}" for insight in insights])

    def _generate_what_worked(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate what worked section."""
        worked_items = []

        if metrics.get("win_rate", 0) > 0.5:
            worked_items.append("Signal timing and entry quality showing positive edge")

        if metrics.get("profit_factor", 0) > 1.5:
            worked_items.append("Risk-reward management maintaining positive expectancy")

        if metrics.get("significant", False):
            worked_items.append("Statistical significance achieved - returns measurably above zero")

        if not worked_items:
            worked_items.append("Limited positive patterns identified - requires larger sample for validation")

        return "\n".join([f"- {item}" for item in worked_items])

    def _generate_what_failed(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate what failed section."""
        failed_items = []

        if metrics.get("win_rate", 0) < 0.5:
            failed_items.append("Win rate below 50% baseline - signal quality improvement needed")

        if metrics.get("profit_factor", 0) < 1.0:
            failed_items.append("Negative expectancy - average losses exceed average wins")

        if not metrics.get("significant", False):
            failed_items.append("Lack of statistical significance - performance not measurably different from random")

        if not failed_items:
            failed_items.append("No major systematic failures identified in current sample")

        return "\n".join([f"- {item}" for item in failed_items])

    def _generate_critical_insights(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate critical insights section."""
        insights = []

        confidence = metrics.get("overall_confidence", 0)
        if confidence > 0.8:
            insights.append("High-confidence analysis enables reliable decision-making")
        elif confidence > 0.6:
            insights.append("Moderate confidence - recommendations require careful validation")
        else:
            insights.append("Low confidence - significant limitations require conservative interpretation")

        if metrics.get("closed_trades", 0) < 15:
            insights.append("Priority: Increase sample size for robust statistical conclusions")

        if metrics.get("profit_factor", 0) > 2.0:
            insights.append("Exceptional profit factor suggests scalable methodology")

        return "\n".join([f"- {item}" for item in insights])

    def generate_live_signals_platform_footer(self) -> str:
        """Generate standardized platform footer for live_signals portfolio."""
        if self.portfolio_name.lower() != "live_signals":
            return ""

        return """## 📱 Live Signals Platform

### Follow Live Signals
- **X/Twitter**: [@colemorton7](https://x.com/colemorton7) - Follow for real-time trading signals
- **Signal Frequency**: Regular trend-following opportunities across market conditions
- **Educational Value**: Learn systematic approach to swing trading with transparent results

### Methodology Summary
- **Approach**: Systematic trend-following using technical analysis and fundamental confluence
- **Risk Management**: Individual position sizing and risk management decisions
- **Transparency**: All signals posted publicly with detailed reasoning and follow-up analysis
- **Educational Purpose**: Demonstrating disciplined approach to systematic trading

---

*Historical performance analysis based on closed positions only. Individual results may vary. Educational signals for learning purposes.*"""

    def generate_internal_report(self, data: dict[str, Any]) -> str:
        """Generate internal trading report with comprehensive analysis."""
        metrics = self.extract_safe_metrics(data)

        return f"""# Live Signals Internal Trading Report
**Portfolio**: {self.portfolio_name} | **Date**: {self.execution_date.strftime("%B %d, %Y")} | **Type**: Internal Analysis

---

{self.generate_live_signals_overview()}## 🎯 Executive Dashboard (30-Second Brief)

### Key Metrics
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Overall Confidence** | {metrics.get("overall_confidence", 0):.1%} | 80%+ | {"✅" if metrics.get("overall_confidence", 0) > 0.8 else "⚠️"} |
| **Win Rate** | {metrics.get("win_rate", 0):.1%} | 60%+ | {"✅" if metrics.get("win_rate", 0) > 0.6 else "⚠️"} |
| **Profit Factor** | {metrics.get("profit_factor", 0):.2f} | 1.50+ | {"✅" if metrics.get("profit_factor", 0) > 1.5 else "⚠️"} |
| **Total P&L** | ${metrics.get("total_pnl", 0):,.2f} | Positive | {"✅" if metrics.get("total_pnl", 0) > 0 else "⚠️"} |
| **Sample Size** | {metrics.get("closed_trades", 0)} trades | 25+ | {"✅" if metrics.get("minimum_sample_met", False) else "⚠️"} |
| **Statistical Significance** | {"Yes" if metrics.get("significant", False) else "No"} | Yes | {"✅" if metrics.get("significant", False) else "⚠️"} |

### Critical Issues
{self._generate_critical_issues(data, metrics)}

### Action Requirements
{self._generate_action_requirements(data, metrics)}

---

## 📊 Comprehensive Portfolio Overview

### Portfolio Health Score: {self._calculate_portfolio_health_score(metrics):.0f}/100

### Current Status
- **Active Positions**: {metrics.get("active_trades", 0)}
- **Closed Positions**: {metrics.get("closed_trades", 0)}
- **Total Performance**: ${metrics.get("total_pnl", 0):,.2f}
- **Statistical Power**: {metrics.get("statistical_power", 0):.1%}

### Performance Attribution (Closed Trades)
{self._generate_performance_attribution(data, metrics)}

---

## 🔍 Strategic Optimization Roadmap

### Priority Improvements
{self._generate_optimization_roadmap(data, metrics)}

---

{self.generate_live_signals_platform_footer()}"""

    def generate_live_monitor(self, data: dict[str, Any]) -> str:
        """Generate live signals monitor with real-time position tracking."""
        metrics = self.extract_safe_metrics(data)

        return f"""# Live Signals Monitor
**Portfolio**: {self.portfolio_name} | **Date**: {self.execution_date.strftime("%B %d, %Y")} | **Type**: Active Position Tracking

---

{self.generate_live_signals_overview()}## 📈 Portfolio Overview

### Current Status
- **Active Positions**: {metrics.get("active_trades", 0)} positions
- **Portfolio Performance**: ${metrics.get("total_pnl", 0):,.2f} (closed trades)
- **Win Rate**: {metrics.get("win_rate", 0):.1%} (historical)
- **Last Signal**: Recent activity tracking

### Market Context
- **Market Environment**: Current regime analysis
- **Volatility Level**: Risk assessment
- **Economic Context**: Macro environment factors

---

## 🎯 Active Position Performance

### Portfolio Composition Analysis
- **Total Active**: {metrics.get("active_trades", 0)} positions
- **Risk Exposure**: Monitoring framework
- **Concentration**: Diversification analysis

### Signal Strength Analysis
{self._generate_signal_strength_analysis(data, metrics)}

---

## 📊 Performance Metrics

### Historical Signal Effectiveness (Closed Trades)
- **Win Rate**: {metrics.get("win_rate", 0):.1%}
- **Profit Factor**: {metrics.get("profit_factor", 0):.2f}
- **Average Trade**: ${metrics.get("total_pnl", 0) / max(metrics.get("closed_trades", 1), 1):,.2f}
- **Statistical Significance**: {"Yes" if metrics.get("significant", False) else "No"}

### Risk Indicators
{self._generate_risk_indicators(data, metrics)}

---

{self.generate_live_signals_platform_footer()}"""

    def _calculate_portfolio_health_score(self, metrics: dict[str, Any]) -> float:
        """Calculate composite portfolio health score (0-100)."""
        score = 0

        # Win rate component (30 points max)
        win_rate = metrics.get("win_rate", 0)
        score += min(30, win_rate * 50)

        # Profit factor component (25 points max)
        profit_factor = metrics.get("profit_factor", 0)
        score += min(25, profit_factor * 12.5)

        # Statistical significance (20 points max)
        if metrics.get("significant", False):
            score += 20

        # Sample size adequacy (15 points max)
        if metrics.get("minimum_sample_met", False):
            score += 15

        # Overall confidence (10 points max)
        confidence = metrics.get("overall_confidence", 0)
        score += confidence * 10

        return min(100, score)

    def _generate_critical_issues(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate critical issues section."""
        issues = []

        if not metrics.get("significant", False):
            issues.append(
                "🔴 **P1 CRITICAL**: Returns not statistically significant - require signal quality improvement"
            )

        if metrics.get("win_rate", 0) < 0.5:
            issues.append("🔴 **P1 CRITICAL**: Win rate below 50% baseline - immediate signal review required")

        if metrics.get("profit_factor", 0) < 1.0:
            issues.append("🔴 **P1 CRITICAL**: Negative expectancy - losses exceed wins")

        if not metrics.get("minimum_sample_met", False):
            issues.append("🟡 **P2 PRIORITY**: Sample size below minimum for statistical confidence")

        if not issues:
            issues.append("🟢 **NO CRITICAL ISSUES**: Portfolio operating within acceptable parameters")

        return "\n".join([f"- {issue}" for issue in issues])

    def _generate_action_requirements(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate action requirements section."""
        actions = []

        if not metrics.get("significant", False):
            actions.append(
                "**IMMEDIATE**: Review signal quality parameters - target statistical significance within 30 days"
            )

        if metrics.get("profit_factor", 0) < 1.5:
            actions.append("**THIS WEEK**: Optimize risk-reward ratios - target 1.50+ profit factor")

        if not metrics.get("minimum_sample_met", False):
            actions.append(
                "**ONGOING**: Increase signal frequency to achieve 25+ closed trades for statistical validity"
            )

        if not actions:
            actions.append("**MAINTAIN**: Continue current methodology while monitoring performance metrics")

        return "\n".join([f"- {action}" for action in actions])

    def _generate_performance_attribution(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate performance attribution section."""
        attribution = []

        pnl = metrics.get("total_pnl", 0)
        trades = metrics.get("closed_trades", 1)
        avg_trade = pnl / trades

        attribution.append(f"**Average Trade P&L**: ${avg_trade:,.2f}")
        attribution.append(f"**Win Contribution**: {metrics.get('total_wins', 0)} winning trades")
        attribution.append(f"**Loss Impact**: {metrics.get('total_losses', 0)} losing trades")
        attribution.append(f"**Risk-Adjusted Performance**: Sharpe {metrics.get('sharpe_ratio', 0):.2f}")

        return "\n".join([f"- {item}" for item in attribution])

    def _generate_optimization_roadmap(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate optimization roadmap section."""
        roadmap = []

        if metrics.get("win_rate", 0) < 0.6:
            roadmap.append("**Signal Quality Enhancement**: Improve entry criteria and timing - target 60%+ win rate")

        if metrics.get("profit_factor", 0) < 2.0:
            roadmap.append("**Risk-Reward Optimization**: Enhance exit strategies - target 2.0+ profit factor")

        if not metrics.get("significant", False):
            roadmap.append(
                "**Statistical Validation**: Achieve statistical significance through improved signal quality"
            )

        if metrics.get("closed_trades", 0) < 50:
            roadmap.append("**Sample Size Expansion**: Increase trading frequency for robust statistical analysis")

        return "\n".join([f"- {item}" for item in roadmap])

    def _generate_signal_strength_analysis(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate signal strength analysis."""
        analysis = []

        analysis.append("**Strong Momentum**: Positions showing positive trends (monitoring required)")
        analysis.append("**Developing Positions**: Early stage signals requiring observation")
        analysis.append("**Watch List**: Underperforming positions with risk considerations")

        return "\n".join([f"- {item}" for item in analysis])

    def _generate_risk_indicators(self, data: dict[str, Any], metrics: dict[str, Any]) -> str:
        """Generate risk indicators section."""
        indicators = []

        indicators.append(f"**Portfolio Exposure**: {metrics.get('active_trades', 0)} active positions")
        indicators.append(f"**Historical Volatility**: Based on {metrics.get('closed_trades', 0)} closed trades")
        indicators.append(
            f"**Risk-Adjusted Returns**: Sharpe {metrics.get('sharpe_ratio', 0):.2f}, Sortino {metrics.get('sortino_ratio', 0):.2f}"
        )

        return "\n".join([f"- {item}" for item in indicators])

    def synthesize_reports(self, report_types: list[str]) -> dict[str, str]:
        """Synthesize requested report types."""
        logger.info(f"Starting synthesis for report types: {report_types}")

        # Load data from previous phases
        data = self.load_phase_data()

        reports = {}

        if "internal" in report_types:
            logger.info("Generating internal trading report...")
            internal_content = self.generate_internal_report(data)
            internal_file = (
                self.output_dir / "internal" / f"{self.portfolio_name}_{self.execution_date.strftime('%Y%m%d')}.md"
            )

            with open(internal_file, "w", encoding="utf-8") as f:
                f.write(internal_content)

            reports["internal"] = str(internal_file)
            logger.info(f"Internal report saved to: {internal_file}")

        if "live" in report_types:
            logger.info("Generating live signals monitor...")
            live_content = self.generate_live_monitor(data)
            live_file = self.output_dir / "live" / f"{self.portfolio_name}_{self.execution_date.strftime('%Y%m%d')}.md"

            with open(live_file, "w", encoding="utf-8") as f:
                f.write(live_content)

            reports["live"] = str(live_file)
            logger.info(f"Live monitor saved to: {live_file}")

        if "historical" in report_types:
            logger.info("Generating historical performance report...")
            historical_content = self.generate_historical_report(data)
            historical_file = (
                self.output_dir / "historical" / f"{self.portfolio_name}_{self.execution_date.strftime('%Y%m%d')}.md"
            )

            with open(historical_file, "w", encoding="utf-8") as f:
                f.write(historical_content)

            reports["historical"] = str(historical_file)
            logger.info(f"Historical report saved to: {historical_file}")

        return reports


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Execute trade history synthesis protocol")
    parser.add_argument("--portfolio", required=True, help="Portfolio name (required)")
    parser.add_argument(
        "--report-type",
        choices=["internal", "live", "historical", "all"],
        default="all",
        help="Report type to generate (default: all)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine report types to generate
    if args.report_type == "all":
        report_types = ["internal", "live", "historical"]
    else:
        report_types = [args.report_type]

    # Execute synthesis
    logger.info(f"Starting DASV Phase 3 Synthesis for portfolio: {args.portfolio}")
    synthesizer = DASVPhase3SynthesizerFixed(portfolio_name=args.portfolio)

    try:
        reports = synthesizer.synthesize_reports(report_types)

        # Print summary
        print("\n" + "=" * 60)
        print("TRADE HISTORY SYNTHESIS COMPLETE")
        print("=" * 60)
        print("Portfolio: {args.portfolio}")
        print("Reports Generated: {len(reports)}")

        for report_type, file_path in reports.items():
            print("  {report_type.capitalize()}: {file_path}")

        print("=" * 60)

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise


if __name__ == "__main__":
    main()
