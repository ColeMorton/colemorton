#!/usr/bin/env python3
"""
Dashboard data parser for extracting trading performance data from markdown reports.

This module provides functionality to parse historical trading performance reports
and extract structured data for dashboard visualization.
"""

import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class TradeData:
    """Represents individual trade information."""

    rank: int
    ticker: str
    strategy: str
    entry_date: str
    exit_date: str
    return_pct: float
    duration_days: int
    quality: str


@dataclass
class MonthlyPerformance:
    """Represents monthly performance metrics."""

    month: str
    year: int
    trades_closed: int
    win_rate: float
    average_return: float
    market_context: str


@dataclass
class QualityDistribution:
    """Represents quality category distribution."""

    category: str
    count: int
    percentage: float
    win_rate: float
    average_return: float


@dataclass
class PerformanceMetrics:
    """Represents overall performance metrics."""

    total_trades: int
    win_rate: float
    total_return: float
    average_duration: float
    profit_factor: float
    average_winner: float
    average_loser: float
    best_trade: str
    worst_trade: str


class DashboardDataParser:
    """Parser for extracting dashboard data from markdown trading reports."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def parse_report(self, file_path: Path) -> dict[str, Any]:
        """
        Parse a historical performance markdown report.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary containing structured performance data
        """
        try:
            with open(file_path, encoding="utf-8") as file:
                content = file.read()

            return {
                "performance_metrics": self._extract_performance_metrics(content),
                "trades": self._extract_trade_data(content),
                "monthly_performance": self._extract_monthly_performance(content),
                "quality_distribution": self._extract_quality_distribution(content),
                "metadata": self._extract_metadata(content),
            }

        except Exception as e:
            self.logger.error(f"Failed to parse report {file_path}: {e}")
            raise

    def _extract_performance_metrics(self, content: str) -> PerformanceMetrics:
        """Extract overall performance metrics from the content."""

        # Extract total trades
        total_trades_match = re.search(r"\*\*Total Closed Trades\*\*:\s*(\d+)", content)
        total_trades = int(total_trades_match.group(1)) if total_trades_match else 0

        # Extract win rate
        win_rate_match = re.search(r"\*\*Win Rate\*\*:\s*([\d.]+)%", content)
        win_rate = float(win_rate_match.group(1)) if win_rate_match else 0.0

        # Extract total return
        total_return_match = re.search(r"\*\*Total Return\*\*:\s*([+-]?[\d.]+)%", content)
        total_return = float(total_return_match.group(1)) if total_return_match else 0.0

        # Extract average duration
        avg_duration_match = re.search(r"\*\*Average Trade Duration\*\*:\s*([\d.]+)\s*days", content)
        avg_duration = float(avg_duration_match.group(1)) if avg_duration_match else 0.0

        # Extract profit factor
        profit_factor_match = re.search(r"\*\*Profit Factor\*\*:\s*([\d.]+)", content)
        profit_factor = float(profit_factor_match.group(1)) if profit_factor_match else 0.0

        # Extract average winner/loser
        avg_winner_match = re.search(r"\*\*Average Winner\*\*:\s*([+-]?[\d.]+)%", content)
        avg_winner = float(avg_winner_match.group(1)) if avg_winner_match else 0.0

        avg_loser_match = re.search(r"\*\*Average Loser\*\*:\s*([+-]?[\d.]+)%", content)
        avg_loser = float(avg_loser_match.group(1)) if avg_loser_match else 0.0

        # Extract best/worst trades
        best_trade_match = re.search(r"\*\*Best Trade\*\*:\s*([^(]+\([^)]+\))", content)
        best_trade = best_trade_match.group(1).strip() if best_trade_match else ""

        worst_trade_match = re.search(r"\*\*Worst Trade\*\*:\s*([^(]+\([^)]+\))", content)
        worst_trade = worst_trade_match.group(1).strip() if worst_trade_match else ""

        return PerformanceMetrics(
            total_trades=total_trades,
            win_rate=win_rate,
            total_return=total_return,
            average_duration=avg_duration,
            profit_factor=profit_factor,
            average_winner=avg_winner,
            average_loser=avg_loser,
            best_trade=best_trade,
            worst_trade=worst_trade,
        )

    def _extract_trade_data(self, content: str) -> list[TradeData]:
        """Extract individual trade data from the markdown table."""
        trades = []

        # Find the trade table section
        table_match = re.search(r"\|\s*\*\*Rank\*\*.*?\n((?:\|.*?\n)*)", content, re.MULTILINE | re.DOTALL)

        if not table_match:
            self.logger.warning("Could not find trade data table")
            return trades

        table_content = table_match.group(1)

        # Parse each row
        for line in table_content.split("\n"):
            if "|" in line and line.strip() and not line.strip().startswith("|---"):
                parts = [part.strip() for part in line.split("|") if part.strip()]

                if len(parts) >= 8:
                    try:
                        # Original table format: | Rank | Ticker | P&L ($) | Return (%) | Duration | Strategy | Quality | X/Twitter Link |
                        rank = int(parts[0])
                        ticker = parts[1].replace("**", "").strip()
                        # parts[2] is P&L ($) - skip for now

                        # Extract return percentage from column 3
                        return_str = parts[3].replace("**", "").replace("%", "").replace("+", "")
                        return_pct = float(return_str)

                        # Extract duration from column 4
                        duration_str = parts[4].replace("d", "").strip()
                        duration_days = int(duration_str)

                        # Strategy is in column 5
                        strategy = parts[5]

                        # Quality is in column 6
                        quality = parts[6]

                        # Use placeholder dates since original format doesn't include them
                        entry_date = "N/A"
                        exit_date = "N/A"

                        trades.append(
                            TradeData(
                                rank=rank,
                                ticker=ticker,
                                strategy=strategy,
                                entry_date=entry_date,
                                exit_date=exit_date,
                                return_pct=return_pct,
                                duration_days=duration_days,
                                quality=quality,
                            )
                        )

                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"Could not parse trade row: {line} - {e}")
                        continue

        return trades

    def _extract_monthly_performance(self, content: str) -> list[MonthlyPerformance]:
        """Extract monthly performance data."""
        monthly_data = []

        # Fixed pattern to match monthly sections - properly captures section content
        monthly_pattern = r"###\s*(\w+)\s*(\d+)\s*-\s*[^\n]+\n(.*?)(?=###|\Z)"

        for match in re.finditer(monthly_pattern, content, re.DOTALL):
            month = match.group(1)
            year = int(match.group(2))
            section_content = match.group(3)

            # Debug logging for troubleshooting
            self.logger.debug(f"Parsing monthly section: {month} {year}")
            self.logger.debug(f"Section content length: {len(section_content)}")
            self.logger.debug(f"Section content preview: {repr(section_content[:100])}")

            # Extract metrics from the section with improved patterns
            trades_match = re.search(r"\*\*Trades Closed\*\*:\s*(\d+)", section_content)
            trades_closed = int(trades_match.group(1)) if trades_match else 0
            if not trades_match:
                self.logger.warning(f"Could not extract trades closed for {month} {year}")

            win_rate_match = re.search(r"\*\*Win Rate\*\*:\s*([\d.]+)%?", section_content)
            win_rate = float(win_rate_match.group(1)) if win_rate_match else 0.0
            if not win_rate_match:
                self.logger.warning(f"Could not extract win rate for {month} {year}")

            avg_return_match = re.search(r"\*\*Average Return\*\*:\s*([+-]?[\d.]+)%?", section_content)
            avg_return = float(avg_return_match.group(1)) if avg_return_match else 0.0
            if not avg_return_match:
                self.logger.warning(f"Could not extract average return for {month} {year}")

            # Extract market context
            context_match = re.search(r"\*\*Market Context\*\*:\s*([^\n]*)", section_content)
            market_context = context_match.group(1).strip() if context_match else ""

            # Log extracted values for validation
            self.logger.debug(
                f"Extracted: {month} {year} - Trades: {trades_closed}, Win Rate: {win_rate}%, Avg Return: {avg_return}%"
            )

            monthly_data.append(
                MonthlyPerformance(
                    month=month,
                    year=year,
                    trades_closed=trades_closed,
                    win_rate=win_rate,
                    average_return=avg_return,
                    market_context=market_context,
                )
            )

        return monthly_data

    def _extract_quality_distribution(self, content: str) -> list[QualityDistribution]:
        """Extract quality distribution data."""
        quality_data = []

        # Pattern to match quality sections
        quality_pattern = r"###\s*(\w+)\s*Trades\s*\((\d+)\s*trades?\s*-\s*([\d.]+)%\)"

        for match in re.finditer(quality_pattern, content):
            category = match.group(1)
            count = int(match.group(2))
            percentage = float(match.group(3))

            # Find the section content
            section_start = match.end()
            section_end = content.find("###", section_start)
            if section_end == -1:
                section_end = content.find("---", section_start)
            if section_end == -1:
                section_end = len(content)

            section_content = content[section_start:section_end]

            # Extract win rate and average return
            win_rate_match = re.search(r"\*\*Win Rate\*\*:\s*([\d.]+)%", section_content)
            win_rate = float(win_rate_match.group(1)) if win_rate_match else 0.0

            avg_return_match = re.search(r"\*\*Average Return\*\*:\s*([+-]?[\d.]+)%", section_content)
            avg_return = float(avg_return_match.group(1)) if avg_return_match else 0.0

            quality_data.append(
                QualityDistribution(
                    category=category,
                    count=count,
                    percentage=percentage,
                    win_rate=win_rate,
                    average_return=avg_return,
                )
            )

        return quality_data

    def _extract_metadata(self, content: str) -> dict[str, Any]:
        """Extract metadata from the report."""
        metadata = {}

        # Extract title and date range
        title_match = re.search(r"#\s*([^\n]+)", content)
        metadata["title"] = title_match.group(1).strip() if title_match else "Historical Performance"

        date_range_match = re.search(r"\*\*.*?\|\s*([^*]+)\*\*", content)
        metadata["date_range"] = date_range_match.group(1).strip() if date_range_match else ""

        # Extract generation timestamp
        metadata["parsed_at"] = datetime.now().isoformat()

        return metadata


def parse_dashboard_data(file_path: str) -> dict[str, Any]:
    """
    Convenience function to parse dashboard data from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dictionary containing structured performance data
    """
    parser = DashboardDataParser()
    return parser.parse_report(Path(file_path))


if __name__ == "__main__":
    # Test parsing with the current historical report
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/outputs/trade_history/HISTORICAL_PERFORMANCE_REPORT_20250626.md"

    try:
        data = parse_dashboard_data(file_path)
        print("Successfully parsed {data['performance_metrics'].total_trades} trades")
        print("Monthly data points: {len(data['monthly_performance'])}")
        print("Quality categories: {len(data['quality_distribution'])}")
    except Exception:
        print("Error parsing file: {e}")
        sys.exit(1)
