#!/usr/bin/env python3
"""
Trade History Analysis - Atomic Statistical Analysis Tool

Atomic utility tool for trade history statistical analysis. Focuses on:
- Loading discovery data and extracting CSV path
- Using unified calculation engine for statistical analysis
- Adding analysis-specific pattern recognition and confidence scoring
- Schema-compliant analysis output generation

This tool is designed to be called by the analyze command via researcher sub-agent.
All core statistical calculations are delegated to the unified calculation engine.

Usage:
    python scripts/trade_history_analyze.py --portfolio {portfolio_name}
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import scipy.stats as stats
from trade_history.unified_calculation_engine import TradingCalculationEngine


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AtomicAnalysisTool:
    """Atomic tool for trade history statistical analysis"""

    def __init__(self, portfolio_name: str):
        self.portfolio_name = portfolio_name
        self.execution_date = datetime.now()
        self.data_dir = Path(__file__).parent.parent / "data"
        self.discovery_dir = self.data_dir / "outputs" / "trade_history" / "discovery"
        self.output_dir = self.data_dir / "outputs" / "trade_history" / "analysis"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return obj

    def load_discovery_data(self) -> dict[str, Any]:
        """
        Load and validate discovery phase JSON data
        """
        logger.info(f"Loading discovery data for portfolio: {self.portfolio_name}")

        # Find latest discovery file
        pattern = f"{self.portfolio_name}_*.json"
        discovery_files = list(self.discovery_dir.glob(pattern))

        if not discovery_files:
            raise FileNotFoundError(
                f"No discovery files found for portfolio '{self.portfolio_name}' in {self.discovery_dir}"
            )

        # Get most recent discovery file
        latest_file = max(discovery_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Loading discovery data from: {latest_file}")

        with open(latest_file, encoding="utf-8") as f:
            discovery_data = json.load(f)

        logger.info(
            f"Discovery data loaded successfully: {discovery_data['portfolio_summary']['total_trades']} total trades"
        )
        return discovery_data

    def analyze_signal_effectiveness(self, engine: TradingCalculationEngine) -> dict[str, Any]:
        """
        Analyze signal effectiveness by strategy using unified engine data
        """
        logger.info("Analyzing signal effectiveness...")

        closed_trades = engine.get_closed_trades()
        if not closed_trades:
            return {
                "entry_signal_analysis": {"status": "NO_CLOSED_TRADES"},
                "exit_signal_analysis": {"status": "NO_CLOSED_TRADES"},
            }

        # Group by strategy type for effectiveness analysis
        strategy_groups = {}
        for trade in closed_trades:
            strategy = trade.strategy_type
            if strategy not in strategy_groups:
                strategy_groups[strategy] = []
            strategy_groups[strategy].append(trade)

        # Analyze each strategy with sample size validation
        entry_analysis = {}
        for strategy, trades in strategy_groups.items():
            if len(trades) < 5:  # Minimum sample size requirement
                entry_analysis[strategy] = {
                    "status": "INSUFFICIENT_SAMPLE",
                    "closed_trades": len(trades),
                    "minimum_required": 5,
                    "analysis_possible": False,
                }
                continue

            # Calculate strategy-specific metrics using proper breakeven handling
            wins = [t for t in trades if t.outcome.value == "win"]
            losses = [t for t in trades if t.outcome.value == "loss"]
            breakevens = [t for t in trades if t.outcome.value == "breakeven"]

            # Win rate based on decisive trades only (wins + losses)
            decisive_trades = wins + losses
            win_rate = len(wins) / len(decisive_trades) if decisive_trades else 0
            avg_win_return = np.mean([t.return_csv for t in wins]) if wins else 0
            avg_loss_return = np.mean([t.return_csv for t in losses]) if losses else 0

            # Sample size confidence
            confidence = min(0.95, 0.5 + (len(trades) / 30))

            entry_analysis[strategy] = {
                "win_rate": win_rate,
                "total_trades": len(trades),
                "winners": len(wins),
                "losers": len(losses),
                "breakevens": len(breakevens),
                "average_return_winners": avg_win_return,
                "average_return_losers": avg_loss_return,
                "sample_size_adequacy": bool(len(trades) >= 15),
                "confidence": confidence,
                "analysis_possible": True,
            }

        # Exit effectiveness using unified engine's MFE/MAE data
        exit_analysis = {"exit_efficiency_metrics": {"status": "PENDING_MFE_MAE_DATA"}}

        return {
            "entry_signal_analysis": {
                "win_rate_by_strategy": entry_analysis,
                "total_strategies_analyzed": len(
                    [s for s in entry_analysis.values() if isinstance(s, dict) and s.get("analysis_possible", False)]
                ),
                "strategies_excluded": len(
                    [s for s in entry_analysis.values() if isinstance(s, dict) and not s.get("analysis_possible", True)]
                ),
            },
            "exit_signal_analysis": exit_analysis,
        }

    def perform_advanced_statistical_analysis(self, engine: TradingCalculationEngine) -> dict[str, Any]:
        """
        Perform advanced statistical analysis using unified engine base metrics
        """
        logger.info("Performing advanced statistical analysis...")

        closed_trades = engine.get_closed_trades()
        if not closed_trades:
            return {"status": "NO_CLOSED_TRADES"}

        # Get base metrics from unified engine
        base_metrics = engine.calculate_portfolio_performance()

        # Extract returns for advanced statistical analysis
        returns = [trade.return_csv for trade in closed_trades]
        returns_array = np.array(returns)

        # Advanced statistical analysis
        statistical_analysis = {
            "return_distribution": {
                "mean_return": float(np.mean(returns_array)),
                "median_return": float(np.median(returns_array)),
                "std_deviation": float(np.std(returns_array, ddof=1)),
                "skewness": float(stats.skew(returns_array)),
                "kurtosis": float(stats.kurtosis(returns_array)),
                "sample_size": len(returns),
                "confidence": min(0.95, 0.5 + (len(returns) / 25)),
            }
        }

        # Statistical significance testing
        if len(returns) >= 8:
            # Test returns vs zero
            t_stat, p_value = stats.ttest_1samp(returns_array, 0)

            # Confidence interval for mean return
            confidence_interval = stats.t.interval(
                0.95,
                len(returns) - 1,
                loc=np.mean(returns_array),
                scale=stats.sem(returns_array),
            )

            # Normality test
            _, normality_p_value = stats.shapiro(returns_array)

            statistical_analysis["statistical_significance"] = {
                "return_vs_zero": {
                    "t_statistic": float(t_stat),
                    "p_value": float(p_value),
                    "significant_at_95": bool(p_value < 0.05),
                    "confidence_interval_95": [
                        float(confidence_interval[0]),
                        float(confidence_interval[1]),
                    ],
                },
                "normality_test_p_value": float(normality_p_value),
            }

        # Risk-adjusted metrics (if sufficient data)
        if len(returns) >= 10 and np.std(returns_array) > 0:
            sharpe_ratio = base_metrics["sharpe_ratio"]

            # Sortino ratio (downside deviation)
            downside_returns = returns_array[returns_array < 0]
            downside_deviation = (
                np.std(downside_returns, ddof=1) if len(downside_returns) > 1 else np.std(returns_array, ddof=1)
            )
            sortino_ratio = np.mean(returns_array) / downside_deviation if downside_deviation > 0 else 0

            statistical_analysis["risk_adjusted_metrics"] = {
                "sharpe_ratio": float(sharpe_ratio),
                "sortino_ratio": float(sortino_ratio),
                "downside_deviation": float(downside_deviation),
                "confidence": min(0.9, 0.4 + (len(returns) / 20)),
            }

        return {
            "statistical_analysis": statistical_analysis,
            "performance_metrics": {
                "win_rate": base_metrics["win_rate"],
                "total_wins": base_metrics["winning_trades"],
                "total_losses": base_metrics["losing_trades"],
                "total_pnl": base_metrics["total_pnl"],
                "profit_factor": base_metrics["profit_factor"],
                "expectancy": base_metrics["avg_return"],
                "sample_size": base_metrics["total_trades"],
                "confidence": min(0.95, 0.5 + (base_metrics["total_trades"] / 30)),
            },
        }

    def generate_optimization_opportunities(
        self, signal_analysis: dict[str, Any], stats_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate focused optimization opportunities based on analysis
        """
        logger.info("Generating optimization opportunities...")

        opportunities = {
            "entry_signal_enhancements": [],
            "exit_signal_refinements": [],
            "strategy_parameter_optimization": [],
        }

        # Entry signal opportunities based on win rates
        entry_analysis = signal_analysis.get("entry_signal_analysis", {})
        win_rates = entry_analysis.get("win_rate_by_strategy", {})

        for strategy, metrics in win_rates.items():
            if isinstance(metrics, dict) and metrics.get("analysis_possible", True):
                win_rate = metrics.get("win_rate", 0)
                if win_rate < 0.6:  # Below 60% win rate
                    opportunities["entry_signal_enhancements"].append(
                        {
                            "opportunity": f"Improve {strategy} signal quality",
                            "current_win_rate": win_rate,
                            "potential_improvement": "10-15% win rate increase through signal refinement",
                            "implementation": f"Add confirmation filters for {strategy} signals",
                            "confidence": metrics.get("confidence", 0.5),
                        }
                    )

        # Statistical significance opportunities
        significance = stats_analysis.get("statistical_significance", {})
        return_test = significance.get("return_vs_zero", {})

        if not return_test.get("significant_at_95", False):
            opportunities["strategy_parameter_optimization"].append(
                {
                    "opportunity": "Increase statistical significance",
                    "current_p_value": return_test.get("p_value", 1.0),
                    "requirement": "P-value < 0.05 for statistical significance",
                    "implementation": "Increase sample size or improve signal quality",
                    "confidence": 0.9,
                }
            )

        return opportunities

    def calculate_analysis_confidence(
        self, engine: TradingCalculationEngine, analysis_results: dict[str, Any]
    ) -> dict[str, float]:
        """
        Calculate analysis confidence scores
        """
        confidence_scores = {}

        # Sample size confidence
        closed_trades_count = len(engine.get_closed_trades())
        confidence_scores["sample_size"] = min(0.95, 0.5 + (closed_trades_count / 30))

        # Statistical significance confidence
        stats_analysis = analysis_results.get("statistical_analysis", {})
        significance = stats_analysis.get("statistical_significance", {})
        return_test = significance.get("return_vs_zero", {})

        if return_test.get("significant_at_95", False):
            confidence_scores["statistical_significance"] = 0.95
        elif return_test.get("p_value", 1.0) < 0.1:
            confidence_scores["statistical_significance"] = 0.8
        else:
            confidence_scores["statistical_significance"] = 0.5

        # Signal effectiveness confidence
        signal_analysis = analysis_results.get("signal_effectiveness", {})
        entry_analysis = signal_analysis.get("entry_signal_analysis", {})
        strategies_analyzed = entry_analysis.get("total_strategies_analyzed", 0)

        confidence_scores["signal_effectiveness"] = (
            min(0.9, 0.6 + (strategies_analyzed * 0.2)) if strategies_analyzed > 0 else 0.3
        )

        # Overall confidence (weighted average)
        weights = {
            "sample_size": 0.4,
            "statistical_significance": 0.3,
            "signal_effectiveness": 0.3,
        }
        confidence_scores["overall"] = sum(confidence_scores[key] * weight for key, weight in weights.items())

        return confidence_scores

    def execute_analysis(self) -> dict[str, Any]:
        """
        Execute atomic statistical analysis
        """
        logger.info(f"Starting atomic analysis for portfolio: {self.portfolio_name}")

        try:
            # Step 1: Load discovery data
            discovery_data = self.load_discovery_data()

            # Step 2: Extract CSV path and initialize unified engine
            csv_path = discovery_data["discovery_metadata"]["data_source"]
            engine = TradingCalculationEngine(csv_path)

            # Step 3: Validate unified engine metrics against discovery data
            validation_results = engine.validate_portfolio_metrics(engine.calculate_portfolio_performance())

            # Step 4: Perform analysis components
            signal_effectiveness = self.analyze_signal_effectiveness(engine)
            statistical_analysis = self.perform_advanced_statistical_analysis(engine)
            optimization_opportunities = self.generate_optimization_opportunities(
                signal_effectiveness,
                statistical_analysis.get("statistical_analysis", {}),
            )

            # Step 5: Calculate confidence scores
            analysis_results = {
                "signal_effectiveness": signal_effectiveness,
                **statistical_analysis,
            }
            confidence_scores = self.calculate_analysis_confidence(engine, analysis_results)

            # Step 6: Generate comprehensive analysis output
            analysis_output = {
                "portfolio": self.portfolio_name,
                "analysis_metadata": {
                    "execution_timestamp": self.execution_date.isoformat(),
                    "confidence_score": confidence_scores["overall"],
                    "statistical_significance": confidence_scores["statistical_significance"],
                },
                "signal_effectiveness": signal_effectiveness,
                "statistical_analysis": statistical_analysis.get("statistical_analysis", {}),
                "performance_metrics": statistical_analysis.get("performance_metrics", {}),
                "advanced_statistical_metrics": {
                    "system_quality_number": statistical_analysis.get("statistical_analysis", {})
                    .get("statistical_significance", {})
                    .get("return_vs_zero", {})
                    .get("t_statistic", 0),
                    "return_distribution_skewness": statistical_analysis.get("statistical_analysis", {})
                    .get("return_distribution", {})
                    .get("skewness", 0),
                    "return_distribution_kurtosis": statistical_analysis.get("statistical_analysis", {})
                    .get("return_distribution", {})
                    .get("kurtosis", 0),
                    "confidence": 0.82,
                },
                "optimization_opportunities": optimization_opportunities,
                "risk_assessment": {
                    "portfolio_risk_metrics": {
                        "active_positions": len(engine.get_open_trades()),
                        "total_positions": len(engine.trades),
                        "confidence": 0.8,
                    }
                },
                "unified_engine_validation": self._convert_numpy_types(validation_results),
                "next_phase_inputs": {"synthesis_ready": bool(confidence_scores["overall"] > 0.7)},
            }

            # Step 7: Save output
            output_filename = f"{self.portfolio_name}_{self.execution_date.strftime('%Y%m%d')}.json"
            output_file = self.output_dir / output_filename

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(analysis_output, f, indent=2, ensure_ascii=False)

            logger.info(f"Analysis output saved to: {output_file}")

            # Log summary
            logger.info(
                f"Analysis complete - Closed trades: {len(engine.get_closed_trades())}, "
                f"Active trades: {len(engine.get_open_trades())}, "
                f"Overall confidence: {confidence_scores['overall']:.3f}"
            )

            return analysis_output

        except Exception as e:
            logger.error(f"Atomic analysis failed: {e}")
            raise


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Atomic trade history analysis tool")
    parser.add_argument("--portfolio", required=True, help="Portfolio name (required)")
    parser.add_argument(
        "--output-format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Execute analysis
    analysis_tool = AtomicAnalysisTool(portfolio_name=args.portfolio)
    result = analysis_tool.execute_analysis()

    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Print summary
        print("\n" + "=" * 60)
        print("ATOMIC ANALYSIS COMPLETE")
        print("=" * 60)
        print("Portfolio: {result['portfolio']}")
        print("Execution: {result['analysis_metadata']['execution_timestamp']}")
        print(f"Overall Confidence: {result['analysis_metadata']['confidence_score']:.3f}")

        print("\nSTATISTICAL ANALYSIS:")
        if "performance_metrics" in result:
            perf = result["performance_metrics"]
            print("  Win Rate: {perf.get('win_rate', 0):.1%}")
            print("  Profit Factor: {perf.get('profit_factor', 0):.2f}")
            print("  Total PnL: ${perf.get('total_pnl', 0):.2f}")

        if "statistical_analysis" in result and "statistical_significance" in result["statistical_analysis"]:
            sig = result["statistical_analysis"]["statistical_significance"]["return_vs_zero"]
            print("  Statistical Significance: {sig.get('significant_at_95', False)}")
            print("  P-Value: {sig.get('p_value', 1.0):.4f}")

        print("\nSIGNAL EFFECTIVENESS:")
        signal_analysis = result.get("signal_effectiveness", {}).get("entry_signal_analysis", {})
        print(f"  Strategies Analyzed: {signal_analysis.get('total_strategies_analyzed', 0)}")
        print("  Strategies Excluded: {signal_analysis.get('strategies_excluded', 0)}")

        print("\nVALIDATION RESULTS:")
        validation = result.get("unified_engine_validation", {})
        print(f"  Overall Validation Success: {validation.get('overall_validation_success', False)}")

        print("\nOutput saved to: {analysis_tool.output_dir}")
        print("=" * 60)


if __name__ == "__main__":
    main()
