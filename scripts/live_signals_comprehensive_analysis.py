#!/usr/bin/env python3
"""
Live Signals Comprehensive Statistical Analysis - DASV Phase 2
Generates comprehensive performance measurement and statistical analysis following DASV requirements.

Key Features:
- Uses ONLY closed trades for all performance calculations (38 trades confirmed)
- Separates analysis by strategy type - SMA (31 trades) and EMA (7 trades)
- Calculates metrics using actual CSV P&L values - NEVER Return × 1000
- Applies confidence penalties for small sample sizes (EMA only 7 trades)
- Generates comprehensive JSON output following specified schema
"""

import datetime
import json
import logging
import os
import sys
from typing import Any

import numpy as np
from scipy import stats


# Add the trade_history directory to the path to import the unified engine
sys.path.append(os.path.join(os.path.dirname(__file__), "trade_history"))

from unified_calculation_engine import TradeOutcome, TradingCalculationEngine


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveSignalsAnalyzer:
    """
    Comprehensive statistical analysis engine for live_signals trading data.
    Implements DASV Phase 2 requirements with focus on closed trades only.
    """

    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.engine = TradingCalculationEngine(csv_file_path)
        self.closed_trades = self.engine.get_closed_trades()
        self.analysis_timestamp = datetime.datetime.now(datetime.UTC)

        logger.info(f"✅ Initialized analyzer with {len(self.closed_trades)} closed trades")

    def calculate_confidence_penalty(self, sample_size: int, base_confidence: float = 0.95) -> float:
        """Calculate confidence penalty for small sample sizes"""
        if sample_size >= 30:
            return base_confidence
        if sample_size >= 15:
            return base_confidence * 0.85  # 15% penalty
        if sample_size >= 10:
            return base_confidence * 0.70  # 30% penalty
        return base_confidence * 0.50  # 50% penalty for very small samples

    def calculate_system_quality_number(self, trades: list) -> dict[str, Any]:
        """Calculate System Quality Number (SQN) for trading system evaluation"""
        if len(trades) < 10:
            return {
                "sqn": 0.0,
                "sqn_rating": "Insufficient Data",
                "confidence": 0.3,
                "sample_adequacy": False,
            }

        returns = [t.return_csv for t in trades]
        avg_return = np.mean(returns)
        std_return = np.std(returns, ddof=1)

        if std_return == 0:
            sqn = 0.0
        else:
            sqn = (avg_return / std_return) * np.sqrt(len(trades))

        # SQN Rating System
        if sqn >= 2.5:
            rating = "Excellent"
        elif sqn >= 1.6:
            rating = "Good"
        elif sqn >= 1.0:
            rating = "Average"
        elif sqn >= 0.6:
            rating = "Below Average"
        else:
            rating = "Poor"

        return {
            "sqn": sqn,
            "sqn_rating": rating,
            "confidence": self.calculate_confidence_penalty(len(trades)),
            "sample_adequacy": len(trades) >= 15,
            "trades_used": len(trades),
        }

    def calculate_expectancy(self, trades: list) -> dict[str, Any]:
        """Calculate expectancy - average amount won per dollar risked"""
        if not trades:
            return {"expectancy": 0.0, "confidence": 0.0}

        wins = [t for t in trades if t.outcome == TradeOutcome.WIN]
        losses = [t for t in trades if t.outcome == TradeOutcome.LOSS]

        if len(wins) == 0 and len(losses) == 0:
            return {"expectancy": 0.0, "confidence": 0.0}

        win_rate = len(wins) / len(trades) if len(trades) > 0 else 0.0
        avg_win = np.mean([t.return_csv for t in wins]) if wins else 0.0
        avg_loss = np.mean([t.return_csv for t in losses]) if losses else 0.0

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        return {
            "expectancy": expectancy,
            "win_rate": win_rate,
            "avg_win_return": avg_win,
            "avg_loss_return": avg_loss,
            "confidence": self.calculate_confidence_penalty(len(trades)),
        }

    def calculate_drawdown_analysis(self, trades: list) -> dict[str, Any]:
        """Calculate maximum drawdown and drawdown periods"""
        if not trades:
            return {
                "max_drawdown": 0.0,
                "max_drawdown_duration": 0,
                "current_drawdown": 0.0,
            }

        # Sort trades by exit date for chronological analysis
        sorted_trades = sorted(trades, key=lambda t: t.exit_date if t.exit_date else t.entry_date)

        # Calculate cumulative returns
        cumulative_returns = []
        running_total = 0.0

        for trade in sorted_trades:
            running_total += trade.return_csv
            cumulative_returns.append(running_total)

        # Calculate running maximum (peak)
        running_max = []
        current_max = cumulative_returns[0] if cumulative_returns else 0.0

        for ret in cumulative_returns:
            current_max = max(current_max, ret)
            running_max.append(current_max)

        # Calculate drawdowns
        drawdowns = [cum - peak for cum, peak in zip(cumulative_returns, running_max, strict=False)]
        max_drawdown = min(drawdowns) if drawdowns else 0.0
        current_drawdown = drawdowns[-1] if drawdowns else 0.0

        # Calculate maximum drawdown duration
        max_drawdown_duration = 0
        current_duration = 0

        for dd in drawdowns:
            if dd < 0:
                current_duration += 1
            else:
                max_drawdown_duration = max(max_drawdown_duration, current_duration)
                current_duration = 0

        max_drawdown_duration = max(max_drawdown_duration, current_duration)

        return {
            "max_drawdown": abs(max_drawdown),
            "max_drawdown_duration": max_drawdown_duration,
            "current_drawdown": abs(current_drawdown),
            "recovery_factor": (abs(cumulative_returns[-1] / max_drawdown) if max_drawdown != 0 else float("inf")),
            "confidence": self.calculate_confidence_penalty(len(trades)),
        }

    def calculate_consecutive_performance(self, trades: list) -> dict[str, Any]:
        """Calculate consecutive wins/losses analysis"""
        if not trades:
            return {"max_consecutive_wins": 0, "max_consecutive_losses": 0}

        # Sort trades chronologically
        sorted_trades = sorted(trades, key=lambda t: t.exit_date if t.exit_date else t.entry_date)

        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0

        for trade in sorted_trades:
            if trade.outcome == TradeOutcome.WIN:
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            elif trade.outcome == TradeOutcome.LOSS:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
            else:  # Breakeven
                current_wins = 0
                current_losses = 0

        return {
            "max_consecutive_wins": max_consecutive_wins,
            "max_consecutive_losses": max_consecutive_losses,
            "current_streak_type": ("win" if current_wins > 0 else ("loss" if current_losses > 0 else "neutral")),
            "current_streak_length": max(current_wins, current_losses),
            "confidence": self.calculate_confidence_penalty(len(trades)),
        }

    def analyze_temporal_patterns(self, trades: list) -> dict[str, Any]:
        """Analyze temporal patterns in trading performance"""
        if not trades:
            return {"monthly_performance": {}, "quarterly_performance": {}}

        # Monthly performance breakdown
        monthly_performance = {}
        quarterly_performance = {}

        for trade in trades:
            if trade.exit_date:
                month_key = trade.exit_date.strftime("%Y-%m")
                quarter_key = f"{trade.exit_date.year}-Q{(trade.exit_date.month - 1) // 3 + 1}"

                # Monthly aggregation
                if month_key not in monthly_performance:
                    monthly_performance[month_key] = {
                        "trades": 0,
                        "wins": 0,
                        "losses": 0,
                        "total_return": 0.0,
                        "total_pnl": 0.0,
                    }

                monthly_performance[month_key]["trades"] += 1
                monthly_performance[month_key]["total_return"] += trade.return_csv
                monthly_performance[month_key]["total_pnl"] += trade.pnl_csv

                if trade.outcome == TradeOutcome.WIN:
                    monthly_performance[month_key]["wins"] += 1
                elif trade.outcome == TradeOutcome.LOSS:
                    monthly_performance[month_key]["losses"] += 1

                # Quarterly aggregation
                if quarter_key not in quarterly_performance:
                    quarterly_performance[quarter_key] = {
                        "trades": 0,
                        "wins": 0,
                        "losses": 0,
                        "total_return": 0.0,
                        "total_pnl": 0.0,
                    }

                quarterly_performance[quarter_key]["trades"] += 1
                quarterly_performance[quarter_key]["total_return"] += trade.return_csv
                quarterly_performance[quarter_key]["total_pnl"] += trade.pnl_csv

                if trade.outcome == TradeOutcome.WIN:
                    quarterly_performance[quarter_key]["wins"] += 1
                elif trade.outcome == TradeOutcome.LOSS:
                    quarterly_performance[quarter_key]["losses"] += 1

        # Calculate win rates for each period
        for period_data in monthly_performance.values():
            decisive = period_data["wins"] + period_data["losses"]
            period_data["win_rate"] = period_data["wins"] / decisive if decisive > 0 else 0.0

        for period_data in quarterly_performance.values():
            decisive = period_data["wins"] + period_data["losses"]
            period_data["win_rate"] = period_data["wins"] / decisive if decisive > 0 else 0.0

        return {
            "monthly_performance": monthly_performance,
            "quarterly_performance": quarterly_performance,
            "confidence": self.calculate_confidence_penalty(len(trades)),
        }

    def calculate_position_correlations(self, trades: list) -> dict[str, Any]:
        """Calculate position correlations and diversification metrics"""
        if len(trades) < 5:
            return {
                "avg_correlation": 0.0,
                "max_correlation": 0.0,
                "diversification_ratio": 1.0,
                "confidence": 0.3,
            }

        # Group trades by ticker for correlation analysis
        ticker_returns = {}
        for trade in trades:
            if trade.ticker not in ticker_returns:
                ticker_returns[trade.ticker] = []
            ticker_returns[trade.ticker].append(trade.return_csv)

        # Calculate correlations between tickers with sufficient data
        correlations = []
        tickers_with_data = [ticker for ticker, returns in ticker_returns.items() if len(returns) >= 2]

        for i, ticker1 in enumerate(tickers_with_data):
            for ticker2 in tickers_with_data[i + 1 :]:
                if len(ticker_returns[ticker1]) >= 2 and len(ticker_returns[ticker2]) >= 2:
                    # Pad shorter series with zeros for correlation calculation
                    max_len = max(len(ticker_returns[ticker1]), len(ticker_returns[ticker2]))
                    padded1 = ticker_returns[ticker1] + [0.0] * (max_len - len(ticker_returns[ticker1]))
                    padded2 = ticker_returns[ticker2] + [0.0] * (max_len - len(ticker_returns[ticker2]))

                    if len(set(padded1)) > 1 and len(set(padded2)) > 1:  # Avoid constant sequences
                        corr_coef = np.corrcoef(padded1, padded2)[0, 1]
                        if not np.isnan(corr_coef):
                            correlations.append(abs(corr_coef))

        avg_correlation = np.mean(correlations) if correlations else 0.0
        max_correlation = np.max(correlations) if correlations else 0.0

        # Diversification ratio calculation
        individual_volatilities = []
        for returns in ticker_returns.values():
            if len(returns) > 1:
                individual_volatilities.append(np.std(returns, ddof=1))

        if individual_volatilities:
            avg_individual_vol = np.mean(individual_volatilities)
            all_returns = [r for returns in ticker_returns.values() for r in returns]
            portfolio_vol = np.std(all_returns, ddof=1) if len(all_returns) > 1 else 0.0
            diversification_ratio = avg_individual_vol / portfolio_vol if portfolio_vol > 0 else 1.0
        else:
            diversification_ratio = 1.0

        return {
            "avg_correlation": avg_correlation,
            "max_correlation": max_correlation,
            "diversification_ratio": diversification_ratio,
            "unique_positions": len(ticker_returns),
            "correlation_pairs": len(correlations),
            "confidence": self.calculate_confidence_penalty(len(correlations) * 2),
        }

    def identify_optimization_opportunities(self, sma_trades: list, ema_trades: list) -> list[dict[str, Any]]:
        """Identify quantified optimization opportunities"""
        opportunities = []

        # Strategy performance comparison
        if sma_trades and ema_trades:
            sma_returns = [t.return_csv for t in sma_trades]
            ema_returns = [t.return_csv for t in ema_trades]

            sma_avg = np.mean(sma_returns)
            ema_avg = np.mean(ema_returns)

            if abs(sma_avg - ema_avg) > 0.05:  # 5% difference threshold
                better_strategy = "EMA" if ema_avg > sma_avg else "SMA"
                # worse_strategy = "SMA" if better_strategy == "EMA" else "EMA"
                improvement_potential = abs(ema_avg - sma_avg) * 100

                opportunities.append(
                    {
                        "opportunity_type": "Strategy Rebalancing",
                        "description": f"Increase allocation to {better_strategy} strategy",
                        "current_performance_gap": f"{improvement_potential:.1f}% average return difference",
                        "quantified_impact": f"Potential {improvement_potential:.1f}% improvement in average returns",
                        "implementation_difficulty": "Medium",
                        "confidence": min(
                            self.calculate_confidence_penalty(len(sma_trades)),
                            self.calculate_confidence_penalty(len(ema_trades)),
                        ),
                        "priority": "High" if improvement_potential > 10 else "Medium",
                    }
                )

        # Duration optimization
        all_trades = sma_trades + ema_trades
        if all_trades:
            durations = [t.duration_days for t in all_trades if t.duration_days is not None]
            returns = [t.return_csv for t in all_trades if t.duration_days is not None]

            if len(durations) >= 10:
                # Analyze return per day efficiency
                efficiency_ratios = [ret / max(dur, 1) for ret, dur in zip(returns, durations, strict=False)]
                high_efficiency_trades = [
                    i for i, ratio in enumerate(efficiency_ratios) if ratio > np.percentile(efficiency_ratios, 75)
                ]

                if high_efficiency_trades:
                    avg_duration_efficient = np.mean([durations[i] for i in high_efficiency_trades])
                    avg_duration_all = np.mean(durations)

                    if avg_duration_efficient < avg_duration_all * 0.8:  # 20% shorter
                        opportunities.append(
                            {
                                "opportunity_type": "Duration Optimization",
                                "description": "Exit positions earlier to improve capital efficiency",
                                "current_performance_gap": f"High-efficiency trades average {avg_duration_efficient:.1f} days vs {avg_duration_all:.1f} days overall",
                                "quantified_impact": f"Potential {((avg_duration_all - avg_duration_efficient) / avg_duration_all * 100):.1f}% reduction in holding period",
                                "implementation_difficulty": "High",
                                "confidence": self.calculate_confidence_penalty(len(high_efficiency_trades)),
                                "priority": "Medium",
                            }
                        )

        # Risk management optimization
        if all_trades:
            losses = [t for t in all_trades if t.outcome == TradeOutcome.LOSS]
            if losses:
                loss_returns = [abs(t.return_csv) for t in losses]
                large_losses = [loss for loss in loss_returns if loss > np.percentile(loss_returns, 75)]

                if large_losses and len(large_losses) > 2:
                    avg_large_loss = np.mean(large_losses)
                    avg_all_losses = np.mean(loss_returns)

                    opportunities.append(
                        {
                            "opportunity_type": "Risk Management Enhancement",
                            "description": "Implement tighter stop-losses to reduce tail risk",
                            "current_performance_gap": f"Top quartile losses average {avg_large_loss * 100:.1f}% vs {avg_all_losses * 100:.1f}% overall",
                            "quantified_impact": f"Potential {((avg_large_loss - avg_all_losses) * len(large_losses) * 100):.1f}% reduction in total loss amount",
                            "implementation_difficulty": "Low",
                            "confidence": self.calculate_confidence_penalty(len(losses)),
                            "priority": ("High" if len(large_losses) > len(losses) * 0.3 else "Medium"),
                        }
                    )

        return opportunities

    def generate_comprehensive_analysis(self) -> dict[str, Any]:
        """Generate comprehensive statistical analysis following DASV Phase 2 requirements"""

        # Separate trades by strategy with confidence penalties
        sma_trades = [t for t in self.closed_trades if t.strategy_type == "SMA"]
        ema_trades = [t for t in self.closed_trades if t.strategy_type == "EMA"]

        logger.info(f"📊 Analyzing SMA: {len(sma_trades)} trades, EMA: {len(ema_trades)} trades")

        # Get base portfolio metrics from unified engine
        portfolio_metrics = self.engine.calculate_portfolio_performance()

        # 1. Signal Effectiveness Analysis
        signal_effectiveness = {
            "overall_metrics": {
                "win_rate": portfolio_metrics["win_rate"],
                "total_return": portfolio_metrics["total_return"],
                "sharpe_ratio": portfolio_metrics["sharpe_ratio"],
                "profit_factor": portfolio_metrics["profit_factor"],
                "confidence": self.calculate_confidence_penalty(len(self.closed_trades), 0.95),
            },
            "sma_strategy": {
                "trade_count": len(sma_trades),
                "win_rate": portfolio_metrics["strategy_performance"]["SMA"]["win_rate"],
                "total_return": sum(t.return_csv for t in sma_trades),
                "avg_return": portfolio_metrics["strategy_performance"]["SMA"]["avg_return"],
                "confidence": self.calculate_confidence_penalty(len(sma_trades), 0.90),
            },
            "ema_strategy": {
                "trade_count": len(ema_trades),
                "win_rate": portfolio_metrics["strategy_performance"]["EMA"]["win_rate"],
                "total_return": sum(t.return_csv for t in ema_trades),
                "avg_return": portfolio_metrics["strategy_performance"]["EMA"]["avg_return"],
                "confidence": self.calculate_confidence_penalty(len(ema_trades), 0.90),  # Heavy penalty for 7 trades
            },
        }

        # 2. Statistical Performance Measurement
        statistical_performance = {
            "return_distribution": {
                "overall": {
                    "mean": np.mean([t.return_csv for t in self.closed_trades]),
                    "median": np.median([t.return_csv for t in self.closed_trades]),
                    "std_dev": np.std([t.return_csv for t in self.closed_trades], ddof=1),
                    "skewness": stats.skew([t.return_csv for t in self.closed_trades]),
                    "kurtosis": stats.kurtosis([t.return_csv for t in self.closed_trades]),
                    "confidence": self.calculate_confidence_penalty(len(self.closed_trades)),
                },
                "sma": {
                    "mean": (np.mean([t.return_csv for t in sma_trades]) if sma_trades else 0.0),
                    "std_dev": (np.std([t.return_csv for t in sma_trades], ddof=1) if len(sma_trades) > 1 else 0.0),
                    "confidence": self.calculate_confidence_penalty(len(sma_trades)),
                },
                "ema": {
                    "mean": (np.mean([t.return_csv for t in ema_trades]) if ema_trades else 0.0),
                    "std_dev": (np.std([t.return_csv for t in ema_trades], ddof=1) if len(ema_trades) > 1 else 0.0),
                    "confidence": self.calculate_confidence_penalty(len(ema_trades)),
                },
            },
            "risk_metrics": {
                "overall": self.calculate_drawdown_analysis(self.closed_trades),
                "sma": self.calculate_drawdown_analysis(sma_trades),
                "ema": self.calculate_drawdown_analysis(ema_trades),
            },
        }

        # 3. Pattern Recognition
        pattern_recognition = {
            "temporal_analysis": self.analyze_temporal_patterns(self.closed_trades),
            "consecutive_performance": {
                "overall": self.calculate_consecutive_performance(self.closed_trades),
                "sma": self.calculate_consecutive_performance(sma_trades),
                "ema": self.calculate_consecutive_performance(ema_trades),
            },
        }

        # 4. Risk Assessment
        risk_assessment = {
            "position_correlations": self.calculate_position_correlations(self.closed_trades),
            "concentration_analysis": {
                "unique_tickers": len(set(t.ticker for t in self.closed_trades)),
                "max_ticker_exposure": max(
                    [
                        len([t for t in self.closed_trades if t.ticker == ticker])
                        for ticker in set(t.ticker for t in self.closed_trades)
                    ]
                )
                / len(self.closed_trades),
                "strategy_concentration": {
                    "sma_percentage": len(sma_trades) / len(self.closed_trades),
                    "ema_percentage": len(ema_trades) / len(self.closed_trades),
                },
            },
        }

        # 5. Advanced Metrics
        advanced_metrics = {
            "system_quality": {
                "overall": self.calculate_system_quality_number(self.closed_trades),
                "sma": self.calculate_system_quality_number(sma_trades),
                "ema": self.calculate_system_quality_number(ema_trades),
            },
            "expectancy": {
                "overall": self.calculate_expectancy(self.closed_trades),
                "sma": self.calculate_expectancy(sma_trades),
                "ema": self.calculate_expectancy(ema_trades),
            },
        }

        # 6. Optimization Opportunities
        optimization_opportunities = self.identify_optimization_opportunities(sma_trades, ema_trades)

        # Calculate overall confidence score
        confidence_scores = [
            signal_effectiveness["overall_metrics"]["confidence"],
            signal_effectiveness["sma_strategy"]["confidence"],
            signal_effectiveness["ema_strategy"]["confidence"],
            statistical_performance["return_distribution"]["overall"]["confidence"],
            pattern_recognition["temporal_analysis"]["confidence"],
            risk_assessment["position_correlations"]["confidence"],
            advanced_metrics["system_quality"]["overall"]["confidence"],
        ]
        overall_confidence = np.mean([c for c in confidence_scores if c > 0])

        return {
            "portfolio": "live_signals",
            "analysis_metadata": {
                "execution_timestamp": self.analysis_timestamp.isoformat(),
                "protocol_version": "DASV_Phase_2_Comprehensive",
                "closed_trades_analyzed": len(self.closed_trades),
                "sma_trades": len(sma_trades),
                "ema_trades": len(ema_trades),
                "confidence_threshold": 0.70,
                "overall_confidence": overall_confidence,
                "data_source": self.csv_file_path,
            },
            "signal_effectiveness": signal_effectiveness,
            "statistical_performance": statistical_performance,
            "pattern_recognition": pattern_recognition,
            "risk_assessment": risk_assessment,
            "advanced_metrics": advanced_metrics,
            "optimization_opportunities": optimization_opportunities,
            "validation_summary": {
                "closed_trades_only": True,
                "strategy_separation": True,
                "csv_pnl_used": True,
                "confidence_penalties_applied": True,
                "small_sample_warning": len(ema_trades) < 15,
                "analysis_completeness": 1.0,
            },
        }


def main():
    """Main execution function"""
    # File paths
    csv_file_path = "/Users/colemorton/Projects/colemorton/data/raw/trade_history/live_signals.csv"
    output_file_path = (
        "/Users/colemorton/Projects/colemorton/data/outputs/trade_history/analysis/live_signals_20250807.json"
    )

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # Initialize analyzer
        analyzer = LiveSignalsAnalyzer(csv_file_path)

        # Generate comprehensive analysis
        logger.info("🚀 Starting comprehensive statistical analysis...")
        analysis_result = analyzer.generate_comprehensive_analysis()

        # Save to JSON file
        with open(output_file_path, "w") as f:
            json.dump(analysis_result, f, indent=2, default=str)

        logger.info(f"✅ Analysis complete! Output saved to: {output_file_path}")
        logger.info(f"📊 Overall confidence score: {analysis_result['analysis_metadata']['overall_confidence']:.2f}")
        logger.info(f"🎯 Analyzed {analysis_result['analysis_metadata']['closed_trades_analyzed']} closed trades")
        logger.info(f"📈 SMA: {analysis_result['analysis_metadata']['sma_trades']} trades")
        logger.info(f"📉 EMA: {analysis_result['analysis_metadata']['ema_trades']} trades (small sample warning)")

        return analysis_result

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()
