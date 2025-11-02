#!/usr/bin/env python3
"""
Comprehensive Trade History Performance Analysis

This script analyzes the trade history CSV data to calculate comprehensive
performance metrics including trade counts, win rates, returns, profit factors,
strategy breakdowns, and advanced metrics like SQN.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class ComprehensivePerformanceAnalyzer:
    """Analyzes trade history data to calculate comprehensive performance metrics."""

    def __init__(self, csv_file_path: str):
        """Initialize the analyzer with trade history data."""
        self.csv_file_path = csv_file_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.load_data()

    def load_data(self) -> None:
        """Load and prepare trade history data."""
        try:
            self.df = pd.read_csv(self.csv_file_path)

            # Convert timestamp columns to datetime
            self.df["Entry_Timestamp"] = pd.to_datetime(self.df["Entry_Timestamp"])
            self.df["Exit_Timestamp"] = pd.to_datetime(self.df["Exit_Timestamp"])

            # Ensure Return column is numeric
            self.df["Return"] = pd.to_numeric(self.df["Return"], errors="coerce")
            self.df["PnL"] = pd.to_numeric(self.df["PnL"], errors="coerce")
            self.df["Duration_Days"] = pd.to_numeric(self.df["Duration_Days"], errors="coerce")

            print("Loaded {len(self.df)} trades from {self.csv_file_path}")

        except Exception as e:
            print("Error loading data: {e}")
            sys.exit(1)

    def calculate_trade_counts(self) -> dict[str, int]:
        """Calculate total trades by status."""
        total_trades = len(self.df)
        closed_trades = len(self.df[self.df["Status"] == "Closed"])
        open_trades = len(self.df[self.df["Status"] == "Open"])

        return {
            "total_trades": total_trades,
            "closed_trades": closed_trades,
            "open_trades": open_trades,
        }

    def calculate_win_loss_rates(self) -> dict[str, float]:
        """Calculate win rate, loss rate, and breakeven rate."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        if len(closed_trades) == 0:
            return {"win_rate": 0.0, "loss_rate": 0.0, "breakeven_rate": 0.0}

        winners = len(closed_trades[closed_trades["Return"] > 0])
        losers = len(closed_trades[closed_trades["Return"] < 0])
        breakevens = len(closed_trades[closed_trades["Return"] == 0])

        total_closed = len(closed_trades)

        return {
            "win_rate": winners / total_closed,
            "loss_rate": losers / total_closed,
            "breakeven_rate": breakevens / total_closed,
            "total_winners": winners,
            "total_losers": losers,
            "total_breakevens": breakevens,
        }

    def calculate_average_returns(self) -> dict[str, float]:
        """Calculate average returns overall and by winners/losers."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        if len(closed_trades) == 0:
            return {
                "avg_return_overall": 0.0,
                "avg_return_winners": 0.0,
                "avg_return_losers": 0.0,
            }

        winners = closed_trades[closed_trades["Return"] > 0]
        losers = closed_trades[closed_trades["Return"] < 0]

        return {
            "avg_return_overall": closed_trades["Return"].mean(),
            "avg_return_winners": winners["Return"].mean() if len(winners) > 0 else 0.0,
            "avg_return_losers": losers["Return"].mean() if len(losers) > 0 else 0.0,
        }

    def calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profits / gross losses)."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        gross_profits = closed_trades[closed_trades["PnL"] > 0]["PnL"].sum()
        gross_losses = abs(closed_trades[closed_trades["PnL"] < 0]["PnL"].sum())

        if gross_losses == 0:
            return float("inf") if gross_profits > 0 else 0.0

        return gross_profits / gross_losses

    def calculate_biggest_winner_loser(self) -> dict[str, dict[str, Any]]:
        """Calculate biggest winner and loser in both % and $."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        if len(closed_trades) == 0:
            return {
                "biggest_winner": {
                    "return_pct": 0.0,
                    "pnl_dollar": 0.0,
                    "ticker_pct": "",
                    "ticker_dollar": "",
                },
                "biggest_loser": {
                    "return_pct": 0.0,
                    "pnl_dollar": 0.0,
                    "ticker_pct": "",
                    "ticker_dollar": "",
                },
            }

        biggest_winner_pct = closed_trades.loc[closed_trades["Return"].idxmax()]
        biggest_loser_pct = closed_trades.loc[closed_trades["Return"].idxmin()]

        biggest_winner_dollar = closed_trades.loc[closed_trades["PnL"].idxmax()]
        biggest_loser_dollar = closed_trades.loc[closed_trades["PnL"].idxmin()]

        return {
            "biggest_winner": {
                "return_pct": float(biggest_winner_pct["Return"]),
                "pnl_dollar": float(biggest_winner_dollar["PnL"]),
                "ticker_pct": str(biggest_winner_pct["Ticker"]),
                "ticker_dollar": str(biggest_winner_dollar["Ticker"]),
            },
            "biggest_loser": {
                "return_pct": float(biggest_loser_pct["Return"]),
                "pnl_dollar": float(biggest_loser_dollar["PnL"]),
                "ticker_pct": str(biggest_loser_pct["Ticker"]),
                "ticker_dollar": str(biggest_loser_dollar["Ticker"]),
            },
        }

    def calculate_strategy_breakdown(self) -> dict[str, dict[str, Any]]:
        """Calculate performance breakdown by strategy type (SMA vs EMA)."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        strategies = {}

        for strategy_type in closed_trades["Strategy_Type"].unique():
            strategy_trades = closed_trades[closed_trades["Strategy_Type"] == strategy_type]

            winners = len(strategy_trades[strategy_trades["Return"] > 0])
            total = len(strategy_trades)

            strategies[strategy_type] = {
                "total_trades": total,
                "win_rate": winners / total if total > 0 else 0.0,
                "avg_return": strategy_trades["Return"].mean(),
                "total_pnl": strategy_trades["PnL"].sum(),
                "best_trade": strategy_trades["Return"].max(),
                "worst_trade": strategy_trades["Return"].min(),
            }

        return strategies

    def calculate_average_holding_time(self) -> dict[str, float]:
        """Calculate average holding time."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        if len(closed_trades) == 0:
            return {"avg_holding_days": 0.0, "median_holding_days": 0.0}

        return {
            "avg_holding_days": closed_trades["Duration_Days"].mean(),
            "median_holding_days": closed_trades["Duration_Days"].median(),
        }

    def calculate_trade_quality_distribution(self) -> dict[str, int]:
        """Calculate distribution of trade quality."""
        quality_counts = self.df["Trade_Quality"].value_counts().to_dict()
        return quality_counts

    def calculate_consecutive_wins_losses(self) -> dict[str, int]:
        """Calculate maximum consecutive wins and losses."""
        closed_trades = self.df[self.df["Status"] == "Closed"].sort_values("Exit_Timestamp")

        if len(closed_trades) == 0:
            return {"max_consecutive_wins": 0, "max_consecutive_losses": 0}

        # Create win/loss sequence
        results = (closed_trades["Return"] > 0).astype(int)

        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0

        for result in results:
            if result == 1:  # Win
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:  # Loss
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)

        return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}

    def calculate_return_statistics(self) -> dict[str, float]:
        """Calculate return statistics including standard deviation."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        if len(closed_trades) == 0:
            return {
                "std_deviation": 0.0,
                "variance": 0.0,
                "skewness": 0.0,
                "kurtosis": 0.0,
            }

        returns = closed_trades["Return"]

        try:
            std_val = returns.std()
            var_val = returns.var()
            skew_val = returns.skew()
            kurt_val = returns.kurtosis()

            return {
                "std_deviation": float(std_val) if pd.notna(std_val) else 0.0,
                "variance": float(var_val) if pd.notna(var_val) else 0.0,
                "skewness": float(skew_val) if pd.notna(skew_val) else 0.0,
                "kurtosis": float(kurt_val) if pd.notna(kurt_val) else 0.0,
            }
        except (ValueError, TypeError):
            return {
                "std_deviation": 0.0,
                "variance": 0.0,
                "skewness": 0.0,
                "kurtosis": 0.0,
            }

    def calculate_sqn(self) -> float:
        """Calculate System Quality Number (SQN)."""
        closed_trades = self.df[self.df["Status"] == "Closed"]

        if len(closed_trades) == 0:
            return 0.0

        returns = closed_trades["Return"]

        if len(returns) < 2 or returns.std() == 0:
            return 0.0

        avg_return = returns.mean()
        std_return = returns.std()
        n_trades = len(returns)

        sqn = (avg_return / std_return) * np.sqrt(n_trades)
        return sqn

    def calculate_monthly_performance(self) -> dict[str, dict[str, Any]]:
        """Calculate monthly performance breakdown."""
        closed_trades = self.df[self.df["Status"] == "Closed"].copy()

        if len(closed_trades) == 0:
            return {}

        # Extract year-month from exit timestamp
        closed_trades["year_month"] = closed_trades["Exit_Timestamp"].dt.to_period("M")

        monthly_stats = {}

        for period in closed_trades["year_month"].unique():
            month_trades = closed_trades[closed_trades["year_month"] == period]

            winners = len(month_trades[month_trades["Return"] > 0])
            total = len(month_trades)

            monthly_stats[str(period)] = {
                "total_trades": total,
                "win_rate": winners / total if total > 0 else 0.0,
                "total_return": month_trades["Return"].sum(),
                "avg_return": month_trades["Return"].mean(),
                "total_pnl": month_trades["PnL"].sum(),
                "best_trade": month_trades["Return"].max(),
                "worst_trade": month_trades["Return"].min(),
            }

        return monthly_stats

    def identify_open_trades(self) -> list[dict[str, Any]]:
        """Identify all trades that are still open."""
        open_trades = self.df[self.df["Status"] == "Open"]

        open_trade_list = []
        for _, trade in open_trades.iterrows():
            open_trade_list.append(
                {
                    "ticker": trade["Ticker"],
                    "strategy": trade["Strategy_Type"],
                    "entry_date": trade["Entry_Timestamp"].strftime("%Y-%m-%d"),
                    "entry_price": trade["Avg_Entry_Price"],
                    "days_since_entry": trade["Days_Since_Entry"],
                    "current_unrealized_pnl": trade["Current_Unrealized_PnL"],
                }
            )

        return open_trade_list

    def get_date_range_info(self) -> dict[str, str]:
        """Get date range information from the data."""
        min_entry_date = self.df["Entry_Timestamp"].min()
        max_exit_date = self.df["Exit_Timestamp"].max()
        most_recent_trade = self.df["Exit_Timestamp"].max()

        return {
            "earliest_entry_date": min_entry_date.strftime("%Y-%m-%d"),
            "latest_exit_date": max_exit_date.strftime("%Y-%m-%d"),
            "most_recent_trade_date": most_recent_trade.strftime("%Y-%m-%d"),
            "data_span_days": (max_exit_date - min_entry_date).days,
        }

    def run_comprehensive_analysis(self) -> dict[str, Any]:
        """Run comprehensive analysis and return all metrics."""
        print("Running comprehensive trade history analysis...")

        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": self.csv_file_path,
            "trade_counts": self.calculate_trade_counts(),
            "win_loss_rates": self.calculate_win_loss_rates(),
            "average_returns": self.calculate_average_returns(),
            "profit_factor": self.calculate_profit_factor(),
            "biggest_winner_loser": self.calculate_biggest_winner_loser(),
            "strategy_breakdown": self.calculate_strategy_breakdown(),
            "holding_time": self.calculate_average_holding_time(),
            "trade_quality_distribution": self.calculate_trade_quality_distribution(),
            "consecutive_streaks": self.calculate_consecutive_wins_losses(),
            "return_statistics": self.calculate_return_statistics(),
            "system_quality_number": self.calculate_sqn(),
            "monthly_performance": self.calculate_monthly_performance(),
            "open_trades": self.identify_open_trades(),
            "date_range": self.get_date_range_info(),
        }

        return results


def main():
    """Main function to run the comprehensive analysis."""
    parser = argparse.ArgumentParser(description="Comprehensive Trade History Performance Analysis")
    parser.add_argument(
        "--csv-file",
        default="/Users/colemorton/Projects/colemorton/data/raw/trade_history/live_signals.csv",
        help="Path to the trade history CSV file",
    )
    parser.add_argument(
        "--output-file",
        default="/Users/colemorton/Projects/colemorton/data/outputs/comprehensive_performance_analysis.json",
        help="Path to save the analysis results JSON file",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)

    # Run analysis
    analyzer = ComprehensivePerformanceAnalyzer(args.csv_file)
    results = analyzer.run_comprehensive_analysis()

    # Save results to JSON file
    with open(args.output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\nAnalysis complete! Results saved to: {args.output_file}")

    # Print summary to console
    print("\n" + "=" * 80)
    print("COMPREHENSIVE PERFORMANCE ANALYSIS SUMMARY")
    print("=" * 80)

    trade_counts = results["trade_counts"]
    win_loss = results["win_loss_rates"]
    returns = results["average_returns"]

    print("Total Trades: {trade_counts['total_trades']}")
    print("Closed Trades: {trade_counts['closed_trades']}")
    print("Open Trades: {trade_counts['open_trades']}")
    print("Win Rate: {win_loss['win_rate']:.2%}")
    print("Loss Rate: {win_loss['loss_rate']:.2%}")
    print("Breakeven Rate: {win_loss['breakeven_rate']:.2%}")
    print("Average Return: {returns['avg_return_overall']:.2%}")
    print("Profit Factor: {results['profit_factor']:.2f}")
    print("System Quality Number: {results['system_quality_number']:.2f}")

    biggest = results["biggest_winner_loser"]
    print(f"Biggest Winner: {biggest['biggest_winner']['return_pct']:.2%} ({biggest['biggest_winner']['ticker_pct']})")
    print(f"Biggest Loser: {biggest['biggest_loser']['return_pct']:.2%} ({biggest['biggest_loser']['ticker_pct']})")

    print("\nStrategy Performance:")
    for strategy, stats in results["strategy_breakdown"].items():
        print(
            f"  {strategy}: {stats['total_trades']} trades, {stats['win_rate']:.2%} win rate, {stats['avg_return']:.2%} avg return"
        )

    print(
        f"\nData Range: {results['date_range']['earliest_entry_date']} to {results['date_range']['latest_exit_date']}"
    )
    print("Most Recent Trade: {results['date_range']['most_recent_trade_date']}")

    if results["open_trades"]:
        print("\nOpen Trades: {len(results['open_trades'])}")
        for trade in results["open_trades"]:
            print(
                f"  {trade['ticker']} ({trade['strategy']}): Entry {trade['entry_date']}, {trade['days_since_entry']} days ago"
            )


if __name__ == "__main__":
    main()
