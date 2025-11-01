#!/usr/bin/env python3
"""
Comprehensive Signal Effectiveness Analysis
Analyzes trade history data to evaluate signal performance and optimization
opportunities
"""

import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, cast

import numpy as np
import numpy.typing as npt
import pandas as pd
import scipy.stats as stats


@dataclass
class SignalMetrics:
    """Container for signal performance metrics"""

    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    total_return: float
    sample_size: int
    confidence_interval: tuple[float, float]
    statistical_significance: bool


class SignalEffectivenessAnalyzer:
    """Comprehensive signal effectiveness analysis"""

    def __init__(self, csv_path: str) -> None:
        """Initialize analyzer with CSV data"""
        self.csv_path = csv_path
        self.df: pd.DataFrame = pd.read_csv(csv_path)
        self.prepare_data()

    def prepare_data(self) -> None:
        """Prepare and clean data for analysis"""
        # Convert timestamps
        self.df["Entry_Timestamp"] = pd.to_datetime(self.df["Entry_Timestamp"])
        self.df["Exit_Timestamp"] = pd.to_datetime(self.df["Exit_Timestamp"], errors="coerce")

        # Filter for closed positions for most metrics
        self.closed_trades: pd.DataFrame = self.df[self.df["Status"] == "Closed"].copy()
        self.open_trades: pd.DataFrame = self.df[self.df["Status"] == "Open"].copy()

        # Calculate year-to-date filter
        self.ytd_start = datetime(2025, 1, 1)
        self.ytd_trades: pd.DataFrame = self.closed_trades[
            self.closed_trades["Entry_Timestamp"] >= self.ytd_start
        ].copy()

        print("Total trades loaded: {len(self.df)}")
        print("Closed trades: {len(self.closed_trades)}")
        print("Open trades: {len(self.open_trades)}")
        print("YTD trades (since 2025-01-01): {len(self.ytd_trades)}")

    def calculate_signal_metrics(self, trades_df: pd.DataFrame) -> SignalMetrics:
        """Calculate comprehensive signal metrics for a dataset"""
        if len(trades_df) == 0:
            return SignalMetrics(
                win_rate=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
                total_return=0.0,
                sample_size=0,
                confidence_interval=(0.0, 0.0),
                statistical_significance=False,
            )

        returns: npt.NDArray[np.floating[Any]] = trades_df["Return"].values.astype(np.float64)
        wins: npt.NDArray[np.floating[Any]] = returns[returns > 0]
        losses: npt.NDArray[np.floating[Any]] = returns[returns < 0]

        win_rate: float = float(len(wins) / len(returns) if len(returns) > 0 else 0)
        avg_win: float = float(np.mean(wins) if len(wins) > 0 else 0)
        avg_loss: float = float(np.mean(losses) if len(losses) > 0 else 0)

        # Profit factor calculation
        total_wins: float = float(np.sum(wins) if len(wins) > 0 else 0)
        total_losses: float = float(abs(np.sum(losses)) if len(losses) > 0 else 0)
        profit_factor: float = float(total_wins / total_losses if total_losses > 0 else float("inf"))

        total_return: float = float(np.sum(returns))

        # Statistical significance
        sample_adequate: bool = len(returns) >= 10

        # Confidence interval for win rate (Wilson score interval)
        if len(returns) > 0:
            p: float = win_rate
            n: int = len(returns)
            z: float = 1.96  # 95% confidence

            denominator: float = 1 + z**2 / n
            centre_adjusted_probability: float = p + z * z / (2 * n)
            adjusted_standard_deviation: float = float(np.sqrt((p * (1 - p) + z * z / (4 * n)) / n))

            lower_bound: float = (centre_adjusted_probability - z * adjusted_standard_deviation) / denominator
            upper_bound: float = (centre_adjusted_probability + z * adjusted_standard_deviation) / denominator

            ci: tuple[float, float] = (max(0, lower_bound), min(1, upper_bound))
        else:
            ci = (0.0, 0.0)

        return SignalMetrics(
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            total_return=total_return,
            sample_size=len(returns),
            confidence_interval=ci,
            statistical_significance=sample_adequate,
        )

    def analyze_by_strategy(self) -> dict[str, SignalMetrics]:
        """Analyze performance by strategy type (SMA vs EMA)"""
        strategy_analysis: dict[str, SignalMetrics] = {}

        for strategy in ["SMA", "EMA"]:
            strategy_trades: pd.DataFrame = self.closed_trades[self.closed_trades["Strategy_Type"] == strategy]
            strategy_analysis[strategy] = self.calculate_signal_metrics(strategy_trades)

        return strategy_analysis

    def analyze_exit_efficiency(
        self,
    ) -> dict[str, str | int | float | dict[str, float]]:
        """Analyze exit efficiency and MFE capture rates"""
        # Only analyze closed trades with valid exit efficiency
        valid_exits: pd.DataFrame = self.closed_trades[self.closed_trades["Exit_Efficiency_Fixed"].notna()].copy()

        if len(valid_exits) == 0:
            return {"error": "No valid exit efficiency data"}

        exit_eff: npt.NDArray[np.floating[Any]] = valid_exits["Exit_Efficiency_Fixed"].values.astype(np.float64)
        mfe_mae_ratios: npt.NDArray[np.floating[Any]] = valid_exits["MFE_MAE_Ratio"].values.astype(np.float64)

        # MFE capture rate (exit efficiency > 0 means captured some of MFE)
        positive_capture: npt.NDArray[np.floating[Any]] = exit_eff[exit_eff > 0]
        mfe_capture_rate: float = float(len(positive_capture) / len(exit_eff) if len(exit_eff) > 0 else 0)

        return {
            "total_trades_analyzed": len(valid_exits),
            "mfe_capture_rate": mfe_capture_rate,
            "avg_exit_efficiency": float(np.mean(exit_eff)),
            "median_exit_efficiency": float(np.median(exit_eff)),
            "avg_mfe_mae_ratio": float(np.mean(mfe_mae_ratios)),
            "excellent_exits_pct": float(len(exit_eff[exit_eff > 0.5]) / len(exit_eff)),
            "poor_exits_pct": float(len(exit_eff[exit_eff < 0]) / len(exit_eff)),
            "exit_efficiency_distribution": {
                "min": float(np.min(exit_eff)),
                "max": float(np.max(exit_eff)),
                "std": float(np.std(exit_eff)),
            },
        }

    def analyze_trade_quality(
        self,
    ) -> dict[str, int | dict[str, int | float | dict[str, int | float]]]:
        """Analyze trade quality distribution"""
        quality_counts: pd.Series = self.closed_trades["Trade_Quality"].value_counts()
        total_trades: int = len(self.closed_trades)

        quality_analysis: dict[str, int | dict[str, int | float | dict[str, int | float]]] = {
            "total_closed_trades": total_trades,
            "quality_distribution": {},
            "quality_performance": {},
        }

        quality_index: pd.Index = cast(pd.Index, quality_counts.index)
        for quality in quality_index:
            count: int = int(quality_counts[quality])
            pct: float = float(count / total_trades * 100)

            cast(
                dict[str, dict[str, int | float]],
                quality_analysis["quality_distribution"],
            )[quality] = {
                "count": count,
                "percentage": round(pct, 2),
            }

            # Performance by quality
            quality_trades: pd.DataFrame = self.closed_trades[self.closed_trades["Trade_Quality"] == quality]
            quality_metrics: SignalMetrics = self.calculate_signal_metrics(quality_trades)

            cast(dict[str, dict[str, float]], quality_analysis["quality_performance"])[quality] = {
                "win_rate": round(quality_metrics.win_rate * 100, 2),
                "avg_return": round(
                    (quality_metrics.avg_win if quality_metrics.avg_win > 0 else quality_metrics.avg_loss),
                    4,
                ),
                "total_return": round(quality_metrics.total_return, 4),
            }

        return quality_analysis

    def analyze_signal_timing(
        self,
    ) -> dict[str, dict[str, float] | dict[str, dict[str, int | float]]]:
        """Analyze signal timing effectiveness"""
        timing_analysis: dict[str, dict[str, float] | dict[str, dict[str, int | float]]] = {
            "duration_analysis": {},
            "entry_timing_patterns": {},
        }

        # Duration analysis
        durations: npt.NDArray[np.floating[Any]] = self.closed_trades["Duration_Days"].values.astype(np.float64)
        if len(durations) > 0:
            cast(dict[str, dict[str, float]], timing_analysis)["duration_analysis"] = {
                "avg_duration_days": float(np.mean(durations)),
                "median_duration_days": float(np.median(durations)),
                "min_duration_days": float(np.min(durations)),
                "max_duration_days": float(np.max(durations)),
                "quick_trades_pct": float(len(durations[durations <= 7]) / len(durations) * 100),
                "long_trades_pct": float(len(durations[durations > 30]) / len(durations) * 100),
            }

        # Performance by duration buckets
        duration_buckets: dict[str, pd.DataFrame] = {
            "Quick (≤7 days)": self.closed_trades[self.closed_trades["Duration_Days"] <= 7],
            "Medium (8-30 days)": self.closed_trades[
                (self.closed_trades["Duration_Days"] > 7) & (self.closed_trades["Duration_Days"] <= 30)
            ],
            "Long (>30 days)": self.closed_trades[self.closed_trades["Duration_Days"] > 30],
        }

        cast(dict[str, dict[str, dict[str, int | float]]], timing_analysis)["performance_by_duration"] = {}
        for bucket_name, bucket_trades in duration_buckets.items():
            if len(bucket_trades) > 0:
                bucket_metrics: SignalMetrics = self.calculate_signal_metrics(bucket_trades)
                cast(dict[str, dict[str, dict[str, int | float]]], timing_analysis)["performance_by_duration"][
                    bucket_name
                ] = {
                    "trade_count": bucket_metrics.sample_size,
                    "win_rate": round(bucket_metrics.win_rate * 100, 2),
                    "avg_return": round(bucket_metrics.total_return / bucket_metrics.sample_size, 4),
                    "profit_factor": round(bucket_metrics.profit_factor, 2),
                }

        return timing_analysis

    def statistical_analysis(
        self,
    ) -> dict[
        str,
        dict[str, int | bool] | dict[str, int | float | bool | str] | dict[str, list[float] | int | bool],
    ]:
        """Perform statistical analysis and significance tests"""
        stats_analysis: dict[
            str,
            dict[str, int | bool] | dict[str, int | float | bool | str] | dict[str, list[float] | int | bool],
        ] = {
            "sample_adequacy": {},
            "strategy_comparison": {},
            "confidence_metrics": {},
        }

        # Sample adequacy analysis
        cast(dict[str, dict[str, int | bool]], stats_analysis)["sample_adequacy"] = {
            "total_closed_trades": len(self.closed_trades),
            "ytd_trades": len(self.ytd_trades),
            "adequate_sample_threshold": 10,
            "overall_adequate": len(self.closed_trades) >= 10,
            "ytd_adequate": len(self.ytd_trades) >= 10,
        }

        # Strategy comparison
        sma_trades: pd.DataFrame = self.closed_trades[self.closed_trades["Strategy_Type"] == "SMA"]
        ema_trades: pd.DataFrame = self.closed_trades[self.closed_trades["Strategy_Type"] == "EMA"]

        if len(sma_trades) > 0 and len(ema_trades) > 0:
            sma_returns: npt.NDArray[np.floating[Any]] = sma_trades["Return"].values.astype(np.float64)
            ema_returns: npt.NDArray[np.floating[Any]] = ema_trades["Return"].values.astype(np.float64)

            # Welch's t-test (unequal variances)
            t_stat: float
            p_value: float
            t_stat, p_value = stats.ttest_ind(sma_returns, ema_returns, equal_var=False)

            cast(dict[str, dict[str, int | float | bool | str]], stats_analysis)["strategy_comparison"] = {
                "sma_sample_size": len(sma_returns),
                "ema_sample_size": len(ema_returns),
                "sma_mean_return": float(np.mean(sma_returns)),
                "ema_mean_return": float(np.mean(ema_returns)),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "statistically_significant": bool(p_value < 0.05),
                "interpretation": ("Significant difference" if p_value < 0.05 else "No significant difference"),
            }

        # Overall performance confidence intervals
        overall_metrics: SignalMetrics = self.calculate_signal_metrics(self.closed_trades)
        cast(dict[str, dict[str, list[float] | int | bool]], stats_analysis)["confidence_metrics"] = {
            "win_rate_95_ci": [
                round(overall_metrics.confidence_interval[0] * 100, 2),
                round(overall_metrics.confidence_interval[1] * 100, 2),
            ],
            "sample_size": overall_metrics.sample_size,
            "statistically_reliable": overall_metrics.statistical_significance,
        }

        return stats_analysis

    def identify_optimization_opportunities(self) -> dict[str, list[str]]:
        """Identify specific optimization opportunities"""
        opportunities: dict[str, list[str]] = {
            "signal_optimization": [],
            "exit_optimization": [],
            "parameter_optimization": [],
            "risk_management": [],
        }

        # Signal optimization opportunities
        strategy_metrics: dict[str, SignalMetrics] = self.analyze_by_strategy()

        if "SMA" in strategy_metrics and "EMA" in strategy_metrics:
            sma_win_rate: float = strategy_metrics["SMA"].win_rate
            ema_win_rate: float = strategy_metrics["EMA"].win_rate

            if abs(sma_win_rate - ema_win_rate) > 0.15:  # 15% difference
                better_strategy: str = "EMA" if ema_win_rate > sma_win_rate else "SMA"
                opportunities["signal_optimization"].append(
                    f"Focus on {better_strategy} signals - showing "
                    f"{abs(sma_win_rate - ema_win_rate) * 100:.1f}% higher win rate"
                )

        # Exit optimization
        exit_analysis: dict[str, str | int | float | dict[str, float]] = self.analyze_exit_efficiency()
        if "poor_exits_pct" in exit_analysis:
            poor_exits_pct: str | int | float | dict[str, float] = exit_analysis["poor_exits_pct"]
            if isinstance(poor_exits_pct, (int, float)) and poor_exits_pct > 0.3:  # >30% poor exits
                opportunities["exit_optimization"].append(
                    f"High percentage of poor exits ({poor_exits_pct * 100:.1f}%) - review exit criteria"
                )

        # Parameter optimization
        # Analyze window parameters for patterns
        closed_with_windows: pd.DataFrame = self.closed_trades[
            ["Short_Window", "Long_Window", "Return", "Trade_Quality"]
        ].dropna()

        if len(closed_with_windows) > 5:
            # Find best performing window combinations
            window_performance: pd.DataFrame = (
                closed_with_windows.groupby(["Short_Window", "Long_Window"])
                .agg(
                    {
                        "Return": ["mean", "count"],
                        "Trade_Quality": lambda x: (x.isin(["Excellent", "Good"])).mean(),
                    }
                )
                .round(4)
            )

            # Flatten column names
            window_performance.columns = ["avg_return", "trade_count", "quality_rate"]

            # Filter for adequate sample size and good performance
            good_combos: pd.DataFrame = window_performance[
                (window_performance["trade_count"] >= 2)
                & (window_performance["avg_return"] > 0.02)
                & (  # >2% average return
                    window_performance["quality_rate"] > 0.5
                )  # >50% good/excellent
            ]

            if len(good_combos) > 0:
                best_combo_idx = good_combos["avg_return"].idxmax()
                best_combo: pd.Series[Any] = good_combos.loc[best_combo_idx]
                opportunities["parameter_optimization"].append(
                    f"Promising window combination found: {best_combo.name} "
                    f"with {float(best_combo['avg_return']) * 100:.1f}% avg return"
                )

        # Risk management opportunities
        poor_quality_pct: float = float(
            len(
                self.closed_trades[
                    self.closed_trades["Trade_Quality"].isin(
                        [
                            "Poor",
                            "Failed to Capture Upside",
                            "Poor Setup - High Risk, Low Reward",
                        ]
                    )
                ]
            )
            / len(self.closed_trades)
        )

        if poor_quality_pct > 0.4:  # >40% poor quality
            opportunities["risk_management"].append(
                f"High percentage of poor quality trades "
                f"({poor_quality_pct * 100:.1f}%) - "
                "implement stricter entry filters"
            )

        return opportunities

    def generate_comprehensive_report(self) -> dict[str, Any]:
        """Generate comprehensive signal effectiveness report"""
        report: dict[str, Any] = {
            "analysis_metadata": {
                "analysis_date": datetime.now().isoformat(),
                "data_source": self.csv_path,
                "total_trades": len(self.df),
                "closed_trades": len(self.closed_trades),
                "open_trades": len(self.open_trades),
                "ytd_date_range": f"2025-01-01 to {date.today().isoformat()}",
            },
            "overall_performance": {},
            "strategy_comparison": {},
            "exit_efficiency_analysis": {},
            "trade_quality_analysis": {},
            "signal_timing_analysis": {},
            "statistical_analysis": {},
            "ytd_performance": {},
            "optimization_opportunities": {},
        }

        # Overall performance
        overall_metrics = self.calculate_signal_metrics(self.closed_trades)
        report["overall_performance"] = {
            "total_closed_trades": overall_metrics.sample_size,
            "win_rate_pct": round(overall_metrics.win_rate * 100, 2),
            "avg_winning_return_pct": round(overall_metrics.avg_win * 100, 2),
            "avg_losing_return_pct": round(overall_metrics.avg_loss * 100, 2),
            "profit_factor": round(overall_metrics.profit_factor, 2),
            "total_return_pct": round(overall_metrics.total_return * 100, 2),
            "win_rate_confidence_interval": [
                round(overall_metrics.confidence_interval[0] * 100, 2),
                round(overall_metrics.confidence_interval[1] * 100, 2),
            ],
            "sample_adequate": overall_metrics.statistical_significance,
        }

        # Strategy comparison
        strategy_metrics = self.analyze_by_strategy()
        report["strategy_comparison"] = {}
        for strategy, metrics in strategy_metrics.items():
            report["strategy_comparison"][strategy] = {
                "sample_size": metrics.sample_size,
                "win_rate_pct": round(metrics.win_rate * 100, 2),
                "avg_return_pct": round(
                    (metrics.total_return / metrics.sample_size if metrics.sample_size > 0 else 0) * 100,
                    2,
                ),
                "profit_factor": round(metrics.profit_factor, 2),
                "sample_adequate": metrics.statistical_significance,
            }

        # Other analyses
        report["exit_efficiency_analysis"] = self.analyze_exit_efficiency()
        report["trade_quality_analysis"] = self.analyze_trade_quality()
        report["signal_timing_analysis"] = self.analyze_signal_timing()
        report["statistical_analysis"] = self.statistical_analysis()

        # YTD performance
        ytd_metrics = self.calculate_signal_metrics(self.ytd_trades)
        report["ytd_performance"] = {
            "ytd_trades": ytd_metrics.sample_size,
            "ytd_win_rate_pct": round(ytd_metrics.win_rate * 100, 2),
            "ytd_total_return_pct": round(ytd_metrics.total_return * 100, 2),
            "ytd_profit_factor": round(ytd_metrics.profit_factor, 2),
            "ytd_sample_adequate": ytd_metrics.statistical_significance,
        }

        # Optimization opportunities
        report["optimization_opportunities"] = self.identify_optimization_opportunities()

        return report


def main() -> dict[str, Any]:
    """Main analysis execution"""
    csv_path = "/Users/colemorton/Projects/colemorton/data/raw/trade_history/20250626.csv"

    print("=== COMPREHENSIVE SIGNAL EFFECTIVENESS ANALYSIS ===")
    print("Analyzing trade history data from: {csv_path}")
    print("Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        analyzer = SignalEffectivenessAnalyzer(csv_path)
        report = analyzer.generate_comprehensive_report()

        # Save detailed report to JSON
        output_path = "/Users/colemorton/Projects/colemorton/data/outputs/signal_effectiveness_analysis_20250626.json"
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print("✅ Detailed analysis saved to: {output_path}")

        # Print executive summary
        print("\n" + "=" * 60)
        print("EXECUTIVE SUMMARY")
        print("=" * 60)

        overall = report["overall_performance"]
        print("📊 Total Closed Trades: {overall['total_closed_trades']}")
        print(
            f"🎯 Win Rate: {overall['win_rate_pct']:.1f}% "
            f"(CI: {overall['win_rate_confidence_interval'][0]:.1f}%-"
            f"{overall['win_rate_confidence_interval'][1]:.1f}%)"
        )
        print("💰 Total Return: {overall['total_return_pct']:.2f}%")
        print("📈 Profit Factor: {overall['profit_factor']:.2f}")
        print("✅ Sample Adequate: {'Yes' if overall['sample_adequate'] else 'No'}")

        print("\n📅 YTD Performance (2025):")
        ytd = report["ytd_performance"]
        print("   Trades: {ytd['ytd_trades']}")
        print("   Win Rate: {ytd['ytd_win_rate_pct']:.1f}%")
        print("   Total Return: {ytd['ytd_total_return_pct']:.2f}%")

        print("\n🔄 Strategy Comparison:")
        for strategy, metrics in report["strategy_comparison"].items():
            print(
                f"   {strategy}: {metrics['win_rate_pct']:.1f}% win rate, "
                f"{metrics['avg_return_pct']:.2f}% avg return "
                f"({metrics['sample_size']} trades)"
            )

        print("\n📋 Trade Quality Distribution:")
        for quality, data in report["trade_quality_analysis"]["quality_distribution"].items():
            print("   {quality}: {data['count']} trades ({data['percentage']:.1f}%)")

        print("\n🚀 Top Optimization Opportunities:")
        opps = report["optimization_opportunities"]
        all_opportunities = []
        for category, items in opps.items():
            all_opportunities.extend(items)

        for i, opp in enumerate(all_opportunities[:5], 1):
            print("   {i}. {opp}")

        if not all_opportunities:
            print("   No major optimization opportunities identified")

        print("\n🔗 Full detailed analysis available in: {output_path}")
        print("=" * 60)

        return report

    except Exception:
        print("❌ Analysis failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
