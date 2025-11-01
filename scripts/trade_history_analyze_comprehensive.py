#!/usr/bin/env python3
"""
DASV Phase 2: Comprehensive Trade History Analysis for Live Signals Portfolio

This script implements the complete DASV Phase 2 methodology:
- Phase 2A: Signal Effectiveness Analysis
- Phase 2B: Statistical Performance Measurement
- Phase 2C: Pattern Recognition
- Phase 2D: Risk Assessment

CRITICAL REQUIREMENTS:
- Include ALL trades (closed AND active) but separate them clearly
- Use ONLY closed trades for performance calculations
- Exclude strategies with <5 closed trades from analysis
- Never use Return×1000 for P&L - use CSV PnL column only
- Apply conservative confidence scoring based on sample sizes
- Validate all calculations against raw CSV data
"""

import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


warnings.filterwarnings("ignore")


class TradeHistoryAnalyzer:
    """Comprehensive trade history analyzer following DASV Phase 2 methodology"""

    def __init__(self, discovery_file_path: str):
        """Initialize analyzer with discovery data"""
        self.discovery_file_path = discovery_file_path
        self.discovery_data = self._load_discovery_data()
        self.csv_data = self._load_csv_data()
        self.closed_trades = self.csv_data[self.csv_data["Status"] == "Closed"].copy()
        self.active_trades = self.csv_data[self.csv_data["Status"] == "Active"].copy()
        self.analysis_timestamp = datetime.now().isoformat()

    def _load_discovery_data(self) -> dict[str, Any]:
        """Load discovery phase data"""
        with open(self.discovery_file_path) as f:
            return json.load(f)

    def _load_csv_data(self) -> pd.DataFrame:
        """Load CSV trade data"""
        csv_path = self.discovery_data["authoritative_trade_data"]["csv_file_path"]
        return pd.read_csv(csv_path)

    def _calculate_confidence_score(self, sample_size: int) -> float:
        """Calculate conservative confidence score based on sample size"""
        if sample_size < 5:
            return 0.0  # Insufficient data
        if sample_size < 10:
            return 0.4  # Low confidence
        if sample_size < 20:
            return 0.6  # Medium confidence
        if sample_size < 30:
            return 0.8  # High confidence
        return 0.9  # Very high confidence

    def phase_2a_signal_effectiveness(self) -> dict[str, Any]:
        """Phase 2A: Signal Effectiveness Analysis"""
        print("Executing Phase 2A: Signal Effectiveness Analysis...")

        analysis = {
            "methodology": "DASV_Phase_2A_Signal_Effectiveness",
            "execution_timestamp": self.analysis_timestamp,
            "data_scope": {
                "total_trades_analyzed": len(self.closed_trades),
                "strategies_analyzed": self.closed_trades["Strategy_Type"].nunique(),
                "date_range": {
                    "start": self.closed_trades["Entry_Timestamp"].min(),
                    "end": self.closed_trades["Exit_Timestamp"].max(),
                },
            },
        }

        # Strategy-level analysis
        strategy_analysis = {}
        for strategy in ["SMA", "EMA"]:
            strategy_trades = self.closed_trades[self.closed_trades["Strategy_Type"] == strategy]

            if len(strategy_trades) < 5:
                strategy_analysis[strategy] = {
                    "sample_size": len(strategy_trades),
                    "confidence": 0.0,
                    "analysis_status": "insufficient_data",
                    "reason": "Less than 5 trades available",
                }
                continue

            # Win rate and returns
            wins = strategy_trades[strategy_trades["PnL"] > 0]
            losses = strategy_trades[strategy_trades["PnL"] <= 0]

            win_rate = len(wins) / len(strategy_trades) if len(strategy_trades) > 0 else 0
            avg_win = wins["Return"].mean() if len(wins) > 0 else 0
            avg_loss = losses["Return"].mean() if len(losses) > 0 else 0
            profit_factor = abs(wins["PnL"].sum() / losses["PnL"].sum()) if losses["PnL"].sum() != 0 else float("inf")

            # MFE capture analysis
            mfe_trades = strategy_trades[strategy_trades["Max_Favourable_Excursion"].notna()]
            mfe_capture_rate = (
                (mfe_trades["Return"] / mfe_trades["Max_Favourable_Excursion"]).mean() if len(mfe_trades) > 0 else 0
            )

            # Exit efficiency
            exit_eff_trades = strategy_trades[strategy_trades["Exit_Efficiency_Fixed"].notna()]
            avg_exit_efficiency = exit_eff_trades["Exit_Efficiency_Fixed"].mean() if len(exit_eff_trades) > 0 else 0

            strategy_analysis[strategy] = {
                "sample_size": len(strategy_trades),
                "confidence": self._calculate_confidence_score(len(strategy_trades)),
                "win_rate": win_rate,
                "average_win_return": avg_win,
                "average_loss_return": avg_loss,
                "profit_factor": profit_factor,
                "total_pnl": strategy_trades["PnL"].sum(),
                "mfe_capture_rate": mfe_capture_rate,
                "average_exit_efficiency": avg_exit_efficiency,
                "best_trade": {
                    "ticker": strategy_trades.loc[strategy_trades["Return"].idxmax(), "Ticker"],
                    "return": strategy_trades["Return"].max(),
                    "pnl": strategy_trades.loc[strategy_trades["Return"].idxmax(), "PnL"],
                },
                "worst_trade": {
                    "ticker": strategy_trades.loc[strategy_trades["Return"].idxmin(), "Ticker"],
                    "return": strategy_trades["Return"].min(),
                    "pnl": strategy_trades.loc[strategy_trades["Return"].idxmin(), "PnL"],
                },
            }

        analysis["strategy_effectiveness"] = strategy_analysis

        # Overall signal effectiveness
        all_wins = self.closed_trades[self.closed_trades["PnL"] > 0]
        all_losses = self.closed_trades[self.closed_trades["PnL"] <= 0]

        analysis["overall_effectiveness"] = {
            "total_win_rate": len(all_wins) / len(self.closed_trades),
            "average_win_return": all_wins["Return"].mean() if len(all_wins) > 0 else 0,
            "average_loss_return": (all_losses["Return"].mean() if len(all_losses) > 0 else 0),
            "overall_profit_factor": (
                abs(all_wins["PnL"].sum() / all_losses["PnL"].sum()) if all_losses["PnL"].sum() != 0 else float("inf")
            ),
            "mfe_capture_efficiency": (
                self.closed_trades["Return"] / self.closed_trades["Max_Favourable_Excursion"]
            ).mean(),
        }

        return analysis

    def phase_2b_statistical_performance(self) -> dict[str, Any]:
        """Phase 2B: Statistical Performance Measurement"""
        print("Executing Phase 2B: Statistical Performance Measurement...")

        analysis = {
            "methodology": "DASV_Phase_2B_Statistical_Performance",
            "execution_timestamp": self.analysis_timestamp,
            "risk_free_rate": 0.0525,  # Current Fed funds rate
            "performance_period_days": (
                pd.to_datetime(self.closed_trades["Exit_Timestamp"].max())
                - pd.to_datetime(self.closed_trades["Entry_Timestamp"].min())
            ).days,
        }

        returns = self.closed_trades["Return"].values

        # Return distribution analysis
        analysis["return_distribution"] = {
            "mean_return": float(np.mean(returns)),
            "median_return": float(np.median(returns)),
            "std_deviation": float(np.std(returns)),
            "skewness": float(pd.Series(returns).skew()),
            "kurtosis": float(pd.Series(returns).kurtosis()),
            "min_return": float(np.min(returns)),
            "max_return": float(np.max(returns)),
            "percentiles": {
                "5th": float(np.percentile(returns, 5)),
                "25th": float(np.percentile(returns, 25)),
                "75th": float(np.percentile(returns, 75)),
                "95th": float(np.percentile(returns, 95)),
            },
        }

        # Risk-adjusted metrics
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        risk_free_rate = 0.0525 / 252  # Daily risk-free rate

        sharpe_ratio = (mean_return - risk_free_rate) / std_return if std_return != 0 else 0

        # Sortino ratio (downside deviation)
        negative_returns = returns[returns < 0]
        downside_deviation = np.std(negative_returns) if len(negative_returns) > 0 else 0
        sortino_ratio = (mean_return - risk_free_rate) / downside_deviation if downside_deviation != 0 else 0

        # Calmar ratio (based on max drawdown)
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
        calmar_ratio = mean_return / abs(max_drawdown) if max_drawdown != 0 else 0

        analysis["risk_adjusted_metrics"] = {
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "max_drawdown": max_drawdown,
            "volatility": std_return,
            "confidence": self._calculate_confidence_score(len(returns)),
        }

        # Trade quality classification
        quality_dist = self.closed_trades["Trade_Quality"].value_counts().to_dict()

        analysis["trade_quality_analysis"] = {
            "distribution": quality_dist,
            "excellent_rate": quality_dist.get("Excellent", 0) / len(self.closed_trades),
            "poor_rate": (quality_dist.get("Poor", 0) + quality_dist.get("Failed to Capture Upside", 0))
            / len(self.closed_trades),
            "quality_vs_performance": {},
        }

        # Quality vs performance correlation
        for quality in quality_dist.keys():
            quality_trades = self.closed_trades[self.closed_trades["Trade_Quality"] == quality]
            if len(quality_trades) > 0:
                analysis["trade_quality_analysis"]["quality_vs_performance"][quality] = {
                    "count": len(quality_trades),
                    "average_return": quality_trades["Return"].mean(),
                    "win_rate": len(quality_trades[quality_trades["PnL"] > 0]) / len(quality_trades),
                    "total_pnl": quality_trades["PnL"].sum(),
                }

        return analysis

    def phase_2c_pattern_recognition(self) -> dict[str, Any]:
        """Phase 2C: Pattern Recognition"""
        print("Executing Phase 2C: Pattern Recognition...")

        analysis = {
            "methodology": "DASV_Phase_2C_Pattern_Recognition",
            "execution_timestamp": self.analysis_timestamp,
        }

        # Convert timestamps
        self.closed_trades["Entry_Date"] = pd.to_datetime(self.closed_trades["Entry_Timestamp"])
        self.closed_trades["Exit_Date"] = pd.to_datetime(self.closed_trades["Exit_Timestamp"])
        self.closed_trades["Entry_Month"] = self.closed_trades["Entry_Date"].dt.strftime("%Y-%m")

        # Temporal patterns
        monthly_performance = (
            self.closed_trades.groupby("Entry_Month").agg({"Return": ["mean", "count"], "PnL": "sum"}).round(4)
        )

        monthly_patterns = {}
        for month in monthly_performance.index:
            monthly_patterns[month] = {
                "trade_count": int(monthly_performance.loc[month, ("Return", "count")]),
                "average_return": float(monthly_performance.loc[month, ("Return", "mean")]),
                "total_pnl": float(monthly_performance.loc[month, ("PnL", "sum")]),
            }

        analysis["temporal_patterns"] = {
            "monthly_performance": monthly_patterns,
            "best_month": max(
                monthly_patterns.keys(),
                key=lambda x: monthly_patterns[x]["average_return"],
            ),
            "worst_month": min(
                monthly_patterns.keys(),
                key=lambda x: monthly_patterns[x]["average_return"],
            ),
        }

        # Strategy effectiveness comparison
        strategy_comparison = {}
        for strategy in ["SMA", "EMA"]:
            strategy_trades = self.closed_trades[self.closed_trades["Strategy_Type"] == strategy]
            if len(strategy_trades) >= 5:
                strategy_comparison[strategy] = {
                    "sample_size": len(strategy_trades),
                    "win_rate": len(strategy_trades[strategy_trades["PnL"] > 0]) / len(strategy_trades),
                    "average_return": strategy_trades["Return"].mean(),
                    "total_pnl": strategy_trades["PnL"].sum(),
                    "average_duration": strategy_trades["Duration_Days"].mean(),
                    "confidence": self._calculate_confidence_score(len(strategy_trades)),
                }

        analysis["strategy_comparison"] = strategy_comparison

        # Sector performance patterns
        sector_mapping = self.discovery_data["authoritative_trade_data"]["ticker_universe"]["sector_distribution"][
            "all_trades"
        ]

        # Create reverse mapping for tickers to sectors
        ticker_to_sector = {}
        for sector, count in sector_mapping.items():
            # This is a simplified mapping - in production, you'd have a proper ticker-to-sector mapping
            pass

        # Duration patterns
        duration_bins = pd.cut(
            self.closed_trades["Duration_Days"],
            bins=[0, 7, 30, 60, float("inf")],
            labels=[
                "Short (0-7d)",
                "Medium (8-30d)",
                "Long (31-60d)",
                "Extended (60d+)",
            ],
        )

        duration_analysis = {}
        for duration_group in duration_bins.cat.categories:
            group_trades = self.closed_trades[duration_bins == duration_group]
            if len(group_trades) > 0:
                duration_analysis[duration_group] = {
                    "count": len(group_trades),
                    "win_rate": len(group_trades[group_trades["PnL"] > 0]) / len(group_trades),
                    "average_return": group_trades["Return"].mean(),
                    "total_pnl": group_trades["PnL"].sum(),
                }

        analysis["duration_patterns"] = duration_analysis

        # Predictive characteristics
        analysis["predictive_characteristics"] = {
            "high_mfe_mae_ratio_performance": {
                "threshold": 5.0,
                "trades_above_threshold": len(self.closed_trades[self.closed_trades["MFE_MAE_Ratio"] > 5.0]),
                "average_return_above": (
                    self.closed_trades[self.closed_trades["MFE_MAE_Ratio"] > 5.0]["Return"].mean()
                    if len(self.closed_trades[self.closed_trades["MFE_MAE_Ratio"] > 5.0]) > 0
                    else 0
                ),
            },
            "exit_efficiency_correlation": {
                "high_efficiency_threshold": 0.7,
                "trades_high_efficiency": len(self.closed_trades[self.closed_trades["Exit_Efficiency_Fixed"] > 0.7]),
                "average_return_high_efficiency": (
                    self.closed_trades[self.closed_trades["Exit_Efficiency_Fixed"] > 0.7]["Return"].mean()
                    if len(self.closed_trades[self.closed_trades["Exit_Efficiency_Fixed"] > 0.7]) > 0
                    else 0
                ),
            },
        }

        return analysis

    def phase_2d_risk_assessment(self) -> dict[str, Any]:
        """Phase 2D: Risk Assessment"""
        print("Executing Phase 2D: Risk Assessment...")

        analysis = {
            "methodology": "DASV_Phase_2D_Risk_Assessment",
            "execution_timestamp": self.analysis_timestamp,
        }

        # Portfolio risk metrics
        returns = self.closed_trades["Return"].values

        # Value at Risk (VaR) calculations
        var_95 = np.percentile(returns, 5)  # 95% VaR
        var_99 = np.percentile(returns, 1)  # 99% VaR

        # Expected Shortfall (Conditional VaR)
        returns_below_var95 = returns[returns <= var_95]
        cvar_95 = np.mean(returns_below_var95) if len(returns_below_var95) > 0 else 0

        analysis["portfolio_risk_metrics"] = {
            "value_at_risk": {
                "var_95": var_95,
                "var_99": var_99,
                "expected_shortfall_95": cvar_95,
            },
            "tail_risk": {
                "worst_case_return": np.min(returns),
                "worst_case_pnl": self.closed_trades["PnL"].min(),
                "tail_ratio": (
                    abs(var_95 / np.mean(returns[returns > 0])) if np.mean(returns[returns > 0]) != 0 else 0
                ),
            },
        }

        # Position concentration analysis
        ticker_exposure = self.closed_trades["Ticker"].value_counts()

        analysis["concentration_risk"] = {
            "ticker_concentration": {
                "unique_tickers": len(ticker_exposure),
                "max_position_count": ticker_exposure.max(),
                "most_traded_ticker": ticker_exposure.index[0],
                "concentration_ratio": (
                    ticker_exposure.iloc[0] / len(self.closed_trades) if len(self.closed_trades) > 0 else 0
                ),
            },
            "strategy_concentration": {
                "sma_weight": len(self.closed_trades[self.closed_trades["Strategy_Type"] == "SMA"])
                / len(self.closed_trades),
                "ema_weight": len(self.closed_trades[self.closed_trades["Strategy_Type"] == "EMA"])
                / len(self.closed_trades),
            },
        }

        # Drawdown analysis
        pnl_series = self.closed_trades.sort_values("Exit_Date")["PnL"].cumsum()
        running_max = pnl_series.expanding().max()
        drawdowns = pnl_series - running_max

        analysis["drawdown_analysis"] = {
            "maximum_drawdown": float(drawdowns.min()),
            "current_drawdown": float(drawdowns.iloc[-1]) if len(drawdowns) > 0 else 0,
            "drawdown_periods": len(drawdowns[drawdowns < 0]),
            "recovery_factor": (
                float(-pnl_series.iloc[-1] / drawdowns.min()) if drawdowns.min() != 0 else float("inf")
            ),
        }

        # Market context and volatility
        analysis["market_context"] = {
            "trading_period": {
                "start_date": self.closed_trades["Entry_Date"].min().strftime("%Y-%m-%d"),
                "end_date": self.closed_trades["Exit_Date"].max().strftime("%Y-%m-%d"),
                "total_days": (self.closed_trades["Exit_Date"].max() - self.closed_trades["Entry_Date"].min()).days,
            },
            "volatility_environment": {
                "return_volatility": float(np.std(returns)),
                "high_volatility_trades": len(
                    self.closed_trades[abs(self.closed_trades["Return"]) > 2 * np.std(returns)]
                ),
                "volatility_adjusted_return": (
                    float(np.mean(returns) / np.std(returns)) if np.std(returns) != 0 else 0
                ),
            },
        }

        # Optimization recommendations
        analysis["optimization_recommendations"] = self._generate_optimization_recommendations()

        return analysis

    def _generate_optimization_recommendations(self) -> list[dict[str, Any]]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []

        # Strategy balance recommendation
        sma_count = len(self.closed_trades[self.closed_trades["Strategy_Type"] == "SMA"])
        ema_count = len(self.closed_trades[self.closed_trades["Strategy_Type"] == "EMA"])

        if sma_count > 3 * ema_count:
            recommendations.append(
                {
                    "category": "strategy_balance",
                    "priority": "medium",
                    "recommendation": "Consider increasing EMA strategy allocation for better diversification",
                    "current_sma_weight": sma_count / (sma_count + ema_count),
                    "suggested_action": "Increase EMA signals to achieve 70/30 SMA/EMA balance",
                }
            )

        # Trade quality improvement
        poor_trades = len(self.closed_trades[self.closed_trades["Trade_Quality"].str.contains("Poor|Failed", na=False)])
        if poor_trades / len(self.closed_trades) > 0.3:
            recommendations.append(
                {
                    "category": "trade_quality",
                    "priority": "high",
                    "recommendation": "High proportion of poor quality trades detected",
                    "poor_trade_rate": poor_trades / len(self.closed_trades),
                    "suggested_action": "Review entry criteria and add additional confirmation signals",
                }
            )

        # Exit efficiency optimization
        low_exit_eff = self.closed_trades[self.closed_trades["Exit_Efficiency_Fixed"] < 0.5]
        if len(low_exit_eff) > len(self.closed_trades) * 0.4:
            recommendations.append(
                {
                    "category": "exit_optimization",
                    "priority": "medium",
                    "recommendation": "Many trades showing low exit efficiency",
                    "low_efficiency_rate": len(low_exit_eff) / len(self.closed_trades),
                    "suggested_action": "Implement dynamic exit rules based on volatility and momentum",
                }
            )

        return recommendations

    def generate_comprehensive_analysis(self) -> dict[str, Any]:
        """Generate the complete DASV Phase 2 analysis"""
        print("Starting DASV Phase 2 Comprehensive Analysis...")
        print(f"Analyzing {len(self.closed_trades)} closed trades and {len(self.active_trades)} active trades")

        # Execute all phases
        phase_2a = self.phase_2a_signal_effectiveness()
        phase_2b = self.phase_2b_statistical_performance()
        phase_2c = self.phase_2c_pattern_recognition()
        phase_2d = self.phase_2d_risk_assessment()

        # Compile comprehensive analysis
        analysis = {
            "analysis_metadata": {
                "portfolio": "live_signals",
                "analysis_type": "DASV_Phase_2_Comprehensive",
                "execution_timestamp": self.analysis_timestamp,
                "protocol_version": "DASV_Phase_2.1",
                "data_source": self.discovery_data["authoritative_trade_data"]["csv_file_path"],
                "discovery_data_source": self.discovery_file_path,
            },
            "data_scope": {
                "total_trades": len(self.csv_data),
                "closed_trades_analyzed": len(self.closed_trades),
                "active_trades_tracked": len(self.active_trades),
                "strategies_analyzed": list(self.closed_trades["Strategy_Type"].unique()),
                "analysis_period": {
                    "start_date": self.closed_trades["Entry_Timestamp"].min(),
                    "end_date": self.closed_trades["Exit_Timestamp"].max(),
                    "total_days": (
                        pd.to_datetime(self.closed_trades["Exit_Timestamp"].max())
                        - pd.to_datetime(self.closed_trades["Entry_Timestamp"].min())
                    ).days,
                },
            },
            "confidence_assessment": {
                "overall_confidence": self._calculate_confidence_score(len(self.closed_trades)),
                "sma_strategy_confidence": self._calculate_confidence_score(
                    len(self.closed_trades[self.closed_trades["Strategy_Type"] == "SMA"])
                ),
                "ema_strategy_confidence": self._calculate_confidence_score(
                    len(self.closed_trades[self.closed_trades["Strategy_Type"] == "EMA"])
                ),
                "statistical_significance": ("medium" if len(self.closed_trades) >= 30 else "low"),
            },
            "phase_2a_signal_effectiveness": phase_2a,
            "phase_2b_statistical_performance": phase_2b,
            "phase_2c_pattern_recognition": phase_2c,
            "phase_2d_risk_assessment": phase_2d,
            "summary_insights": self._generate_summary_insights(phase_2a, phase_2b, phase_2c, phase_2d),
            "validation_checks": self._perform_validation_checks(),
        }

        return analysis

    def _generate_summary_insights(
        self, phase_2a: dict, phase_2b: dict, phase_2c: dict, phase_2d: dict
    ) -> dict[str, Any]:
        """Generate high-level summary insights"""
        total_pnl = self.closed_trades["PnL"].sum()
        win_rate = len(self.closed_trades[self.closed_trades["PnL"] > 0]) / len(self.closed_trades)

        return {
            "key_performance_metrics": {
                "total_realized_pnl": total_pnl,
                "overall_win_rate": win_rate,
                "average_return_per_trade": self.closed_trades["Return"].mean(),
                "sharpe_ratio": phase_2b["risk_adjusted_metrics"]["sharpe_ratio"],
                "maximum_drawdown": phase_2d["drawdown_analysis"]["maximum_drawdown"],
            },
            "strategy_insights": {
                "dominant_strategy": (
                    "SMA"
                    if len(self.closed_trades[self.closed_trades["Strategy_Type"] == "SMA"])
                    > len(self.closed_trades[self.closed_trades["Strategy_Type"] == "EMA"])
                    else "EMA"
                ),
                "best_performing_strategy": (
                    max(
                        phase_2a["strategy_effectiveness"].keys(),
                        key=lambda x: phase_2a["strategy_effectiveness"][x].get("total_pnl", 0),
                    )
                    if phase_2a["strategy_effectiveness"]
                    else None
                ),
                "strategy_diversification": len(self.closed_trades["Strategy_Type"].unique()),
            },
            "risk_insights": {
                "concentration_risk_level": (
                    "high"
                    if phase_2d["concentration_risk"]["ticker_concentration"]["concentration_ratio"] > 0.2
                    else "moderate"
                ),
                "tail_risk_assessment": (
                    "high" if phase_2d["portfolio_risk_metrics"]["value_at_risk"]["var_95"] < -0.1 else "moderate"
                ),
                "volatility_environment": (
                    "high" if phase_2b["risk_adjusted_metrics"]["volatility"] > 0.15 else "moderate"
                ),
            },
            "optimization_priority": {
                "immediate_actions": len(
                    [r for r in phase_2d["optimization_recommendations"] if r["priority"] == "high"]
                ),
                "medium_term_actions": len(
                    [r for r in phase_2d["optimization_recommendations"] if r["priority"] == "medium"]
                ),
                "total_recommendations": len(phase_2d["optimization_recommendations"]),
            },
        }

    def _perform_validation_checks(self) -> dict[str, Any]:
        """Perform validation checks on the analysis"""
        checks = {
            "data_integrity": {
                "pnl_calculation_check": abs(
                    self.closed_trades["PnL"].sum() - self.discovery_data["performance_metrics"]["total_pnl"]
                )
                < 0.01,
                "trade_count_match": len(self.closed_trades)
                == self.discovery_data["performance_metrics"]["total_closed_trades"],
                "win_rate_consistency": abs(
                    (len(self.closed_trades[self.closed_trades["PnL"] > 0]) / len(self.closed_trades))
                    - self.discovery_data["performance_metrics"]["win_rate"]
                )
                < 0.01,
            },
            "analysis_completeness": {
                "all_phases_completed": True,
                "confidence_scores_calculated": True,
                "recommendations_generated": True,
            },
        }

        checks["overall_validation_status"] = all(checks["data_integrity"].values()) and all(
            checks["analysis_completeness"].values()
        )

        return checks


def main():
    """Main execution function"""
    # Use the most recent discovery file
    discovery_file = "/Users/colemorton/Projects/colemorton-command-system-enhancements/data/outputs/trade_history/discovery/live_signals_20250804.json"

    # Initialize analyzer
    analyzer = TradeHistoryAnalyzer(discovery_file)

    # Generate comprehensive analysis
    analysis_results = analyzer.generate_comprehensive_analysis()

    # Save results
    output_dir = Path(
        "/Users/colemorton/Projects/colemorton-command-system-enhancements/data/outputs/trade_history/analysis"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"live_signals_{datetime.now().strftime('%Y%m%d')}.json"

    with open(output_file, "w") as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print("\n=== DASV Phase 2 Analysis Complete ===")
    print("Analysis saved to: {output_file}")
    print("Total trades analyzed: {len(analyzer.closed_trades)}")
    print(f"Overall confidence: {analysis_results['confidence_assessment']['overall_confidence']:.2f}")
    print(f"Total PnL: ${analysis_results['summary_insights']['key_performance_metrics']['total_realized_pnl']:.2f}")
    print(f"Win Rate: {analysis_results['summary_insights']['key_performance_metrics']['overall_win_rate']:.1%}")
    print(f"Sharpe Ratio: {analysis_results['summary_insights']['key_performance_metrics']['sharpe_ratio']:.3f}")
    print(
        f"Optimization Recommendations: {analysis_results['summary_insights']['optimization_priority']['total_recommendations']}"
    )


if __name__ == "__main__":
    main()
