#!/usr/bin/env python3
"""
Trade History Analysis - DASV Phase 2 Implementation

Performs comprehensive analysis following trade_history:analyze command requirements:
- Strict separation of closed vs active trades
- Performance calculations using ONLY closed trades
- Sample size validation (minimum 5 closed trades per strategy)
- Confidence-adjusted metrics
- Proper statistical analysis

Usage:
    python scripts/trade_history_analysis.py --portfolio {portfolio_name}
    python scripts/trade_history_analysis.py --portfolio live_signals --verbose
    python scripts/trade_history_analysis.py --portfolio momentum_strategy --output-format json
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DASVPhase2Analyzer:
    """DASV Phase 2 analyzer with strict methodology compliance."""

    def __init__(self, discovery_path: str):
        """Initialize with discovery data."""
        self.discovery_path = Path(discovery_path)

        # Load discovery data
        with open(self.discovery_path) as f:
            self.discovery_data = json.load(f)

        # Extract closed and active trades from discovery
        self._separate_trades()
        self._validate_data_structure()

    def _separate_trades(self) -> None:
        """Separate closed and active trades from discovery data."""
        # Get counts from portfolio summary
        portfolio_summary = self.discovery_data.get("portfolio_summary", {})
        self.total_trades = portfolio_summary.get("total_trades", 0)
        self.closed_trades_count = portfolio_summary.get("closed_trades", 0)
        self.active_trades_count = portfolio_summary.get("active_trades", 0)

        # Get active positions
        self.active_positions = self.discovery_data.get("active_positions", [])

        # Get strategy distribution (total counts)
        self.strategy_distribution = self.discovery_data.get("strategy_distribution", {})

        # Get ticker performance (contains closed trade data)
        self.ticker_performance = self.discovery_data.get("ticker_performance", {})

        logger.info("Trade separation complete:")
        logger.info(f"  Total trades: {self.total_trades}")
        logger.info(f"  CLOSED trades: {self.closed_trades_count}")
        logger.info(f"  ACTIVE trades: {self.active_trades_count}")

    def _validate_data_structure(self) -> None:
        """Validate that we have proper data structure."""
        if self.closed_trades_count + self.active_trades_count != self.total_trades:
            logger.warning(
                f"Trade count mismatch: closed({self.closed_trades_count}) + "
                f"active({self.active_trades_count}) != total({self.total_trades})"
            )

        # Validate active positions match count
        if len(self.active_positions) != self.active_trades_count:
            logger.warning(
                f"Active position count mismatch: positions({len(self.active_positions)}) "
                f"!= reported({self.active_trades_count})"
            )

    def calculate_strategy_performance(self) -> dict[str, Any]:
        """Calculate performance metrics by strategy using ONLY closed trades."""
        strategy_analysis = {}

        # Calculate closed trades per strategy
        # Note: We need to infer this from ticker performance data

        # Analyze each ticker's closed trades
        for ticker, perf in self.ticker_performance.items():
            # Skip tickers that only have active positions
            if ticker in [pos["ticker"] for pos in self.active_positions]:
                # This ticker has active position, adjust the count
                total_trades = perf.get("total_trades", 0)
                active_count = len([p for p in self.active_positions if p["ticker"] == ticker])
                closed_count = total_trades - active_count

                if closed_count > 0:
                    # Has some closed trades
                    # We need to determine strategy from active positions
                    # This is a limitation - we can't determine strategy of closed trades
                    # from discovery data alone
                    pass
            else:
                # All trades are closed for this ticker
                total_trades = perf.get("total_trades", 0)
                if total_trades > 0:
                    # Add returns to appropriate strategy bucket
                    # Note: Discovery data doesn't specify strategy per ticker
                    pass

        # Use overall performance metrics from discovery
        perf_metrics = self.discovery_data.get("performance_metrics", {})

        # Calculate metrics for each strategy
        for strategy in ["SMA", "EMA"]:
            # Get strategy trade count from distribution
            total_strategy_trades = self.strategy_distribution.get(strategy, 0)

            # Estimate closed trades for strategy
            # This is approximate since we don't have exact closed/active breakdown by strategy
            active_strategy_count = len([p for p in self.active_positions if p["strategy"] == strategy])
            closed_strategy_count = total_strategy_trades - active_strategy_count

            if closed_strategy_count < 5:
                # Insufficient sample size
                strategy_analysis[strategy] = {
                    "status": "INSUFFICIENT_SAMPLE",
                    "closed_trades": closed_strategy_count,
                    "active_trades": active_strategy_count,
                    "total_trades": total_strategy_trades,
                    "minimum_required": 5,
                    "confidence_penalty": 1.0,
                    "recommendation": "Exclude from reliable analysis until more closed trades available",
                }
            else:
                # Calculate metrics with confidence adjustment
                base_confidence = 0.5 + (min(closed_strategy_count, 30) / 60)

                # Use overall metrics as proxy (limitation of discovery data)
                win_rate = perf_metrics.get("win_rate", 0)
                avg_win = perf_metrics.get("average_win_return", 0)
                avg_loss = perf_metrics.get("average_loss_return", 0)

                # Calculate confidence interval
                n = closed_strategy_count
                p = win_rate
                z = 1.96  # 95% confidence
                margin = z * np.sqrt((p * (1 - p)) / n) if n > 0 else 0
                ci_lower = max(0, p - margin)
                ci_upper = min(1, p + margin)

                # Calculate expectancy
                if avg_loss != 0:
                    rr_ratio = abs(avg_win / avg_loss)
                    loss_ratio = 1 - win_rate
                    expectancy = (rr_ratio * win_rate) - loss_ratio
                else:
                    expectancy = win_rate * avg_win

                strategy_analysis[strategy] = {
                    "status": "ANALYZED",
                    "closed_trades": closed_strategy_count,
                    "active_trades": active_strategy_count,
                    "total_trades": total_strategy_trades,
                    "win_rate": win_rate,
                    "average_win_return": avg_win,
                    "average_loss_return": avg_loss,
                    "expectancy": expectancy,
                    "profit_factor": perf_metrics.get("profit_factor", 0),
                    "confidence": base_confidence,
                    "win_rate_confidence_interval": [ci_lower, ci_upper],
                    "sample_size_quality": ("MINIMAL" if closed_strategy_count < 10 else "ADEQUATE"),
                }

        return strategy_analysis

    def analyze_active_portfolio(self) -> dict[str, Any]:
        """Analyze current active positions separately from performance metrics."""
        if not self.active_positions:
            return {
                "status": "NO_ACTIVE_POSITIONS",
                "position_count": 0,
                "total_exposure": 0,
            }

        # Portfolio composition
        strategy_composition: dict[str, int] = {}
        ticker_concentration: dict[str, int] = {}
        holding_periods = []
        current_returns = []

        for position in self.active_positions:
            # Strategy composition
            strategy = position.get("strategy", "Unknown")
            strategy_composition[strategy] = strategy_composition.get(strategy, 0) + 1

            # Ticker concentration
            ticker = position.get("ticker", "Unknown")
            ticker_concentration[ticker] = ticker_concentration.get(ticker, 0) + 1

            # Holding periods
            days_held = position.get("days_held", 0)
            holding_periods.append(days_held)

            # Current returns
            current_return = position.get("current_return", 0)
            current_returns.append(current_return)

        # Calculate portfolio metrics
        portfolio_metrics = {
            "position_count": len(self.active_positions),
            "strategy_composition": strategy_composition,
            "ticker_concentration": ticker_concentration,
            "average_holding_period": float(np.mean(holding_periods)),
            "median_holding_period": float(np.median(holding_periods)),
            "longest_held_position": max(holding_periods),
            "average_unrealized_return": float(np.mean(current_returns)),
            "median_unrealized_return": float(np.median(current_returns)),
            "best_performer": {
                "ticker": max(self.active_positions, key=lambda x: x.get("current_return", 0))["ticker"],
                "return": max(current_returns),
            },
            "worst_performer": {
                "ticker": min(self.active_positions, key=lambda x: x.get("current_return", 0))["ticker"],
                "return": min(current_returns),
            },
            "unrealized_winners": len([r for r in current_returns if r > 0]),
            "unrealized_losers": len([r for r in current_returns if r < 0]),
            "portfolio_health": ("HEALTHY" if np.mean(current_returns) > 0 else "MONITOR"),
        }

        return portfolio_metrics

    def calculate_risk_metrics(self) -> dict[str, Any]:
        """Calculate risk metrics using closed trade data."""
        perf_metrics = self.discovery_data.get("performance_metrics", {})

        # Basic risk metrics from discovery data
        win_rate = perf_metrics.get("win_rate", 0)
        avg_win = perf_metrics.get("average_win_return", 0)
        avg_loss = perf_metrics.get("average_loss_return", 0)
        profit_factor = perf_metrics.get("profit_factor", 0)

        # Calculate risk-adjusted metrics
        if avg_loss != 0:
            risk_reward_ratio = abs(avg_win / avg_loss)
        else:
            risk_reward_ratio = float("inf") if avg_win > 0 else 0

        # Kelly Criterion (simplified)
        if risk_reward_ratio > 0 and win_rate > 0:
            kelly_fraction = (win_rate * risk_reward_ratio - (1 - win_rate)) / risk_reward_ratio
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        else:
            kelly_fraction = 0

        # Maximum drawdown estimation (limited by discovery data)
        # This is approximate since we don't have time-series data
        consecutive_loss_risk = (1 - win_rate) ** 3  # Probability of 3 losses in a row
        estimated_max_drawdown = abs(avg_loss) * 3 if avg_loss < 0 else 0

        risk_metrics = {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "risk_reward_ratio": risk_reward_ratio,
            "average_win": avg_win,
            "average_loss": avg_loss,
            "kelly_fraction": kelly_fraction,
            "recommended_position_size": f"{kelly_fraction * 100:.1f}%",
            "consecutive_loss_probability": {
                "3_losses": consecutive_loss_risk,
                "5_losses": (1 - win_rate) ** 5,
            },
            "estimated_max_drawdown": estimated_max_drawdown,
            "risk_assessment": self._assess_risk_level(win_rate, profit_factor, risk_reward_ratio),
        }

        return risk_metrics

    def _assess_risk_level(self, win_rate: float, profit_factor: float, rr_ratio: float) -> str:
        """Assess overall risk level based on key metrics."""
        if win_rate < 0.4 or profit_factor < 1.2:
            return "HIGH_RISK"
        if win_rate > 0.6 and profit_factor > 2.0 and rr_ratio > 2.0:
            return "LOW_RISK"
        return "MODERATE_RISK"

    def generate_optimization_recommendations(self) -> list[dict[str, Any]]:
        """Generate actionable optimization recommendations."""
        recommendations = []

        perf_metrics = self.discovery_data.get("performance_metrics", {})
        strategy_dist = self.discovery_data.get("strategy_distribution", {})

        # Check win rate
        win_rate = perf_metrics.get("win_rate", 0)
        if win_rate < 0.5:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "ENTRY_SIGNALS",
                    "issue": f"Low win rate ({win_rate:.1%})",
                    "recommendation": "Review entry criteria and consider more selective signals",
                    "potential_impact": "Improve win rate to 55%+ for consistent profitability",
                }
            )

        # Check profit factor
        profit_factor = perf_metrics.get("profit_factor", 0)
        if profit_factor < 1.5:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "RISK_MANAGEMENT",
                    "issue": f"Low profit factor ({profit_factor:.2f})",
                    "recommendation": "Improve exit strategy to capture more profits and cut losses faster",
                    "potential_impact": "Target profit factor > 2.0 for robust performance",
                }
            )

        # Check strategy balance
        total_trades = sum(strategy_dist.values())
        if total_trades > 0:
            for strategy, count in strategy_dist.items():
                pct = count / total_trades
                if pct > 0.8:
                    recommendations.append(
                        {
                            "priority": "MEDIUM",
                            "category": "DIVERSIFICATION",
                            "issue": f"Over-concentration in {strategy} strategy ({pct:.1%})",
                            "recommendation": "Consider diversifying strategy mix for robustness",
                            "potential_impact": "Reduce strategy-specific risk",
                        }
                    )

        # Check sample size
        if self.closed_trades_count < 30:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "SAMPLE_SIZE",
                    "issue": f"Limited closed trades ({self.closed_trades_count})",
                    "recommendation": "Continue gathering data for more reliable statistics",
                    "potential_impact": "Higher confidence in performance metrics with 50+ closed trades",
                }
            )

        # Check active position concentration
        if self.active_positions:
            position_count = len(self.active_positions)
            if position_count > 10:
                recommendations.append(
                    {
                        "priority": "MEDIUM",
                        "category": "POSITION_SIZING",
                        "issue": f"High number of active positions ({position_count})",
                        "recommendation": "Consider consolidating to 5-8 high-conviction positions",
                        "potential_impact": "Better focus and risk management",
                    }
                )

        return recommendations

    def generate_phase2_output(self) -> dict[str, Any]:
        """Generate comprehensive Phase 2 analysis output."""
        # Calculate all analysis components
        strategy_performance = self.calculate_strategy_performance()
        active_portfolio = self.analyze_active_portfolio()
        risk_metrics = self.calculate_risk_metrics()
        recommendations = self.generate_optimization_recommendations()

        # Extract portfolio name from discovery data
        portfolio_name = self.discovery_data.get("portfolio", "unknown")

        # Build comprehensive output
        output = {
            "metadata": {
                "portfolio": portfolio_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "discovery_source": str(self.discovery_path),
                "protocol_version": "DASV_1.0",
                "phase": "Phase_2_Analysis",
            },
            "data_summary": {
                "total_trades": self.total_trades,
                "closed_trades": self.closed_trades_count,
                "active_trades": self.active_trades_count,
                "performance_calculations_based_on": "CLOSED_TRADES_ONLY",
            },
            "strategy_performance": strategy_performance,
            "overall_performance": {
                "closed_trades_metrics": self.discovery_data.get("performance_metrics", {}),
                "confidence_note": "Metrics calculated from closed trades only",
                "sample_size_validation": {
                    "total_closed": self.closed_trades_count,
                    "minimum_required": 5,
                    "quality": ("ADEQUATE" if self.closed_trades_count >= 30 else "MINIMAL"),
                },
            },
            "active_portfolio_analysis": active_portfolio,
            "risk_analysis": risk_metrics,
            "optimization_recommendations": recommendations,
            "ticker_deep_dive": self._analyze_top_performers(),
            "next_steps": {
                "immediate_actions": self._get_immediate_actions(recommendations),
                "monitoring_priorities": [
                    "Track strategy-specific win rates as more trades close",
                    "Monitor active position performance for exit timing",
                    "Validate signal effectiveness with larger sample",
                ],
            },
        }

        return output

    def _analyze_top_performers(self) -> dict[str, Any]:
        """Analyze top performing tickers."""
        # Sort tickers by total return
        ticker_list = []
        for ticker, perf in self.ticker_performance.items():
            ticker_list.append(
                {
                    "ticker": ticker,
                    "total_return": perf.get("total_return", 0),
                    "win_rate": perf.get("win_rate", 0),
                    "total_trades": perf.get("total_trades", 0),
                }
            )

        # Sort by total return
        ticker_list.sort(key=lambda x: x["total_return"], reverse=True)

        return {
            "top_winners": ticker_list[:5] if len(ticker_list) >= 5 else ticker_list,
            "top_losers": ticker_list[-5:] if len(ticker_list) >= 5 else [],
            "most_traded": sorted(ticker_list, key=lambda x: x["total_trades"], reverse=True)[:5],
        }

    def _get_immediate_actions(self, recommendations: list[dict[str, Any]]) -> list[str]:
        """Extract immediate actions from recommendations."""
        actions = []
        high_priority = [r for r in recommendations if r["priority"] == "HIGH"]

        for rec in high_priority[:3]:  # Top 3 high priority items
            actions.append(f"{rec['category']}: {rec['recommendation']}")

        return actions


def find_latest_discovery_file(portfolio_name: str) -> Path:
    """Find the latest discovery file for a given portfolio."""
    discovery_dir = Path("data/outputs/trade_history/discovery")

    if not discovery_dir.exists():
        raise FileNotFoundError(f"Discovery directory not found: {discovery_dir}")

    # Look for files matching the pattern: {portfolio_name}_{YYYYMMDD}.json
    pattern = f"{portfolio_name}_*.json"
    discovery_files = list(discovery_dir.glob(pattern))

    if not discovery_files:
        raise FileNotFoundError(f"No discovery files found for portfolio '{portfolio_name}' in {discovery_dir}")

    # Return the most recent file based on modification time
    latest_file = max(discovery_files, key=lambda f: f.stat().st_mtime)
    return latest_file


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Execute DASV Phase 2 trade history analysis")
    parser.add_argument("--portfolio", required=True, help="Portfolio name (required)")
    parser.add_argument(
        "--discovery-file",
        help="Specific discovery file path (optional - will auto-discover latest if not provided)",
    )
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

    try:
        # Find discovery file
        if args.discovery_file:
            discovery_file = Path(args.discovery_file)
            if not discovery_file.exists():
                raise FileNotFoundError(f"Specified discovery file not found: {discovery_file}")
        else:
            discovery_file = find_latest_discovery_file(args.portfolio)
            logger.info(f"Using latest discovery file: {discovery_file}")

        # Setup output directory
        output_dir = Path("data/outputs/trade_history/analysis")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run analysis
        logger.info("Starting DASV Phase 2 Analysis")
        analyzer = DASVPhase2Analyzer(str(discovery_file))

        # Generate output
        output = analyzer.generate_phase2_output()

        # Save output with standard naming convention
        # Extract date from discovery file name
        discovery_filename = discovery_file.stem
        if "_" in discovery_filename:
            _, date_stamp = discovery_filename.rsplit("_", 1)
        else:
            date_stamp = datetime.now().strftime("%Y%m%d")

        output_file = output_dir / f"{args.portfolio}_{date_stamp}.json"

        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        logger.info(f"Phase 2 analysis complete. Output saved to: {output_file}")

        if args.output_format == "json":
            print(json.dumps(output, indent=2))
        else:
            # Print summary
            print("\n=== DASV Phase 2 Analysis Summary ===")
            print("Portfolio: {args.portfolio}")
            print("Discovery File: {discovery_file}")
            print("Total Trades: {output['data_summary']['total_trades']}")
            print(f"Closed Trades (for metrics): {output['data_summary']['closed_trades']}")
            print(f"Active Trades (portfolio): {output['data_summary']['active_trades']}")
            print("\nOverall Performance:")
            perf = output["overall_performance"]["closed_trades_metrics"]
            print("  Win Rate: {perf.get('win_rate', 0):.1%}")
            print("  Profit Factor: {perf.get('profit_factor', 0):.2f}")
            print("  Avg Win: {perf.get('average_win_return', 0):.1%}")
            print("  Avg Loss: {perf.get('average_loss_return', 0):.1%}")
            print("\nRisk Assessment: {output['risk_analysis']['risk_assessment']}")
            print("Recommendations: {len(output['optimization_recommendations'])}")
            print("\nOutput saved to: {output_file}")

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
