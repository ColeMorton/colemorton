#!/usr/bin/env python3
"""
Trade History Synthesize - Atomic Data Synthesis Tool

Atomic utility tool for trade history data synthesis. Focuses on:
- Loading discovery and analysis phase data
- Extracting and transforming key metrics for report generation
- Aggregating data structures for multi-audience reporting
- Schema-compliant synthesis output generation

This tool is designed to be called by the synthesize command via researcher sub-agent.
Report generation and templating is handled by the command specifications.

Usage:
    python scripts/trade_history_synthesize.py --portfolio {portfolio_name}
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

# import numpy as np
import pandas as pd


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AtomicSynthesisTool:
    """Atomic tool for trade history data synthesis"""

    def __init__(self, portfolio_name: str):
        self.portfolio_name = portfolio_name
        self.execution_date = datetime.now()
        self.data_dir = Path(__file__).parent.parent / "data"
        self.discovery_dir = self.data_dir / "outputs" / "trade_history" / "discovery"
        self.analysis_dir = self.data_dir / "outputs" / "trade_history" / "analysis"
        self.output_dir = self.data_dir / "outputs" / "trade_history" / "synthesis"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_phase_data(self) -> dict[str, Any]:
        """
        Load discovery and analysis data from previous DASV phases
        """
        logger.info(f"Loading phase data for portfolio: {self.portfolio_name}")

        # Find latest discovery file
        discovery_pattern = f"{self.portfolio_name}_*.json"
        discovery_files = list(self.discovery_dir.glob(discovery_pattern))
        if not discovery_files:
            raise FileNotFoundError(f"No discovery files found for portfolio '{self.portfolio_name}'")

        latest_discovery = max(discovery_files, key=lambda f: f.stat().st_mtime)

        # Find latest analysis file
        analysis_pattern = f"{self.portfolio_name}_*.json"
        analysis_files = list(self.analysis_dir.glob(analysis_pattern))
        if not analysis_files:
            raise FileNotFoundError(f"No analysis files found for portfolio '{self.portfolio_name}'")

        latest_analysis = max(analysis_files, key=lambda f: f.stat().st_mtime)

        # Load JSON data
        with open(latest_discovery, encoding="utf-8") as f:
            discovery_data = json.load(f)

        with open(latest_analysis, encoding="utf-8") as f:
            analysis_data = json.load(f)

        logger.info(f"Loaded discovery data from: {latest_discovery}")
        logger.info(f"Loaded analysis data from: {latest_analysis}")

        return {
            "discovery": discovery_data,
            "analysis": analysis_data,
            "discovery_file": str(latest_discovery),
            "analysis_file": str(latest_analysis),
        }

    def extract_key_metrics(self, phase_data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract and transform key metrics for report generation
        """
        logger.info("Extracting key metrics for synthesis...")

        discovery = phase_data["discovery"]
        analysis = phase_data["analysis"]

        # Extract core portfolio metrics
        portfolio_summary = discovery.get("portfolio_summary", {})
        performance_metrics = discovery.get("performance_metrics", {})
        analysis_performance = analysis.get("performance_metrics", {})

        # Merge and validate metrics
        key_metrics = {
            "portfolio_overview": {
                "total_trades": portfolio_summary.get("total_trades", 0),
                "closed_trades": portfolio_summary.get("closed_trades", 0),
                "active_trades": portfolio_summary.get("active_trades", 0),
                "unique_tickers": portfolio_summary.get("unique_tickers", 0),
            },
            "performance_summary": {
                "win_rate": analysis_performance.get("win_rate", performance_metrics.get("win_rate", 0)),
                "total_wins": analysis_performance.get("total_wins", performance_metrics.get("total_wins", 0)),
                "total_losses": analysis_performance.get("total_losses", performance_metrics.get("total_losses", 0)),
                "total_pnl": analysis_performance.get("total_pnl", performance_metrics.get("total_pnl", 0)),
                "profit_factor": analysis_performance.get("profit_factor", performance_metrics.get("profit_factor", 0)),
                "expectancy": analysis_performance.get("expectancy", 0),
            },
            "statistical_analysis": analysis.get("statistical_analysis", {}),
            "signal_effectiveness": analysis.get("signal_effectiveness", {}),
            "confidence_assessment": {
                "overall_confidence": analysis.get("analysis_metadata", {}).get("confidence_score", 0),
                "sample_size_adequate": portfolio_summary.get("closed_trades", 0) >= 25,
                "statistical_significance": analysis.get("statistical_analysis", {})
                .get("statistical_significance", {})
                .get("return_vs_zero", {})
                .get("significant_at_95", False),
            },
        }

        return key_metrics

    def generate_report_data_structures(
        self, key_metrics: dict[str, Any], phase_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate data structures optimized for different report types
        """
        logger.info("Generating report data structures...")

        # Use enhanced discovery data with X Links
        discovery = phase_data["discovery"]

        # Get detailed trades with X Links from unified calculation engine
        detailed_trades = discovery.get("detailed_trades", [])
        closed_trades_with_xlinks = pd.DataFrame(detailed_trades) if detailed_trades else pd.DataFrame()

        # Get active positions from discovery data
        active_positions = discovery.get("active_positions", [])
        active_trades = pd.DataFrame(active_positions) if active_positions else pd.DataFrame()

        # Generate report-specific data structures
        report_data = {
            "executive_dashboard": {
                "key_metrics": key_metrics["performance_summary"],
                "portfolio_health_score": self._calculate_health_score(key_metrics),
                "critical_issues": self._identify_critical_issues(key_metrics, closed_trades_with_xlinks),
                "trend_indicators": self._generate_trend_indicators(key_metrics),
            },
            "historical_analysis": {
                "closed_trades_summary": {
                    "count": len(closed_trades_with_xlinks),
                    "top_winners": self._get_top_trades(closed_trades_with_xlinks, "winners", 5),
                    "top_losers": self._get_top_trades(closed_trades_with_xlinks, "losers", 5),
                    "strategy_breakdown": self._analyze_strategy_performance(closed_trades_with_xlinks),
                    "monthly_performance": self._analyze_monthly_performance(closed_trades_with_xlinks),
                },
                "statistical_summary": key_metrics["statistical_analysis"],
                "confidence_disclosure": self._generate_confidence_disclosure(key_metrics),
            },
            "live_monitoring": {
                "active_positions": {
                    "count": len(active_trades),
                    "positions_summary": self._summarize_active_positions(active_trades),
                    "risk_indicators": self._assess_portfolio_risk(active_trades),
                },
                "real_time_metrics": {
                    "platform_status": ("ACTIVE" if self.portfolio_name == "live_signals" else "N/A"),
                    "last_signal": self._get_last_signal_info(active_trades),
                    "market_context": self._get_market_context(),
                },
            },
        }

        return report_data

    def _calculate_health_score(self, key_metrics: dict[str, Any]) -> dict[str, Any]:
        """Calculate portfolio health score (0-100)"""
        performance = key_metrics["performance_summary"]
        win_rate = performance.get("win_rate", 0)
        total_pnl = performance.get("total_pnl", 0)
        profit_factor = performance.get("profit_factor", 0)

        # Simple health score calculation
        score = min(
            100,
            max(
                0,
                50 + (total_pnl / 1000) * 10 + win_rate * 30 + min(profit_factor, 5) * 4,
            ),
        )

        if score >= 80:
            interpretation = "Excellent"
        elif score >= 60:
            interpretation = "Good"
        elif score >= 40:
            interpretation = "Fair"
        else:
            interpretation = "Needs Improvement"

        return {"score": score, "interpretation": interpretation}

    def _identify_critical_issues(self, key_metrics: dict[str, Any], trades_df: pd.DataFrame) -> list[dict[str, Any]]:
        """Identify critical issues requiring attention"""
        issues = []

        performance = key_metrics["performance_summary"]
        win_rate = performance.get("win_rate", 0)

        if win_rate < 0.4:
            issues.append(
                {
                    "priority": "HIGH",
                    "issue": "Low win rate",
                    "details": f"Win rate ({win_rate:.1%}) below 40% threshold",
                    "recommendation": "Review entry signal quality and market conditions",
                }
            )

        if not trades_df.empty and "pnl" in trades_df.columns:
            max_loss = trades_df["pnl"].min()
            if max_loss < -50:
                issues.append(
                    {
                        "priority": "MEDIUM",
                        "issue": "Large single loss",
                        "details": f"Maximum loss (${max_loss:.2f}) exceeds risk tolerance",
                        "recommendation": "Implement stricter stop-loss protocols",
                    }
                )

        sample_size = key_metrics["portfolio_overview"].get("closed_trades", 0)
        if sample_size < 25:
            issues.append(
                {
                    "priority": "LOW",
                    "issue": "Insufficient sample size",
                    "details": "Need more closed trades for robust statistical analysis",
                    "recommendation": "Continue trading to build sample size",
                }
            )

        return issues

    def _generate_trend_indicators(self, key_metrics: dict[str, Any]) -> dict[str, str]:
        """Generate trend indicators for metrics"""
        # Simplified trend analysis (would be enhanced with historical comparison)
        win_rate = key_metrics["performance_summary"].get("win_rate", 0)
        total_pnl = key_metrics["performance_summary"].get("total_pnl", 0)

        return {
            "win_rate_trend": "↗️" if win_rate > 0.6 else "→" if win_rate > 0.4 else "↘️",
            "pnl_trend": "↗️" if total_pnl > 0 else "↘️",
            "overall_trend": ("↗️" if win_rate > 0.5 and total_pnl > 0 else "→" if total_pnl >= 0 else "↘️"),
        }

    def _get_top_trades(self, trades_df: pd.DataFrame, trade_type: str, count: int) -> list[dict[str, Any]]:
        """Extract top performing trades with X Links"""
        if trades_df.empty or "pnl" not in trades_df.columns:
            return []

        if trade_type == "winners":
            top_trades = trades_df.nlargest(count, "pnl")
        else:  # losers
            top_trades = trades_df.nsmallest(count, "pnl")

        trades_list = []
        for _, trade in top_trades.iterrows():
            trades_list.append(
                {
                    "ticker": trade.get("ticker", "N/A"),
                    "strategy": trade.get("strategy_type", "N/A"),
                    "pnl": float(trade.get("pnl", 0)),
                    "return_pct": float(trade.get("return_pct", 0)),
                    "duration_days": (
                        float(trade.get("duration_days", 0)) if pd.notna(trade.get("duration_days")) else 0
                    ),
                    "quality": trade.get("quality", "N/A"),
                    "x_link": trade.get("x_link", "N/A"),
                    "entry_date": trade.get("entry_date", "N/A"),
                    "exit_date": trade.get("exit_date", "N/A"),
                }
            )

        return trades_list

    def _analyze_strategy_performance(self, trades_df: pd.DataFrame) -> dict[str, Any]:
        """Analyze performance by strategy"""
        if trades_df.empty:
            return {}

        strategy_performance = {}
        if "strategy_type" in trades_df.columns:
            for strategy in trades_df["strategy_type"].unique():
                strategy_trades = trades_df[trades_df["strategy_type"] == strategy]
                if "pnl" in strategy_trades.columns:
                    wins = len(strategy_trades[strategy_trades["pnl"] > 0])
                    total = len(strategy_trades)

                    strategy_performance[strategy] = {
                        "total_trades": total,
                        "win_rate": wins / total if total > 0 else 0,
                        "total_pnl": float(strategy_trades["pnl"].sum()),
                        "avg_return": (
                            float(strategy_trades["return_pct"].mean())
                            if "return_pct" in strategy_trades.columns
                            else 0
                        ),
                    }

        return strategy_performance

    def _analyze_monthly_performance(self, trades_df: pd.DataFrame) -> dict[str, Any]:
        """Analyze performance by month (simplified)"""
        # Placeholder for monthly analysis
        return {"note": "Monthly analysis requires date parsing implementation"}

    def _summarize_active_positions(self, active_trades: pd.DataFrame) -> list[dict[str, Any]]:
        """Summarize active positions"""
        positions = []
        if not active_trades.empty:
            for _, trade in active_trades.iterrows():
                positions.append(
                    {
                        "ticker": trade.get("Ticker", "N/A"),
                        "strategy": trade.get("Strategy_Type", "N/A"),
                        "entry_date": str(trade.get("Entry_Timestamp", "N/A")),
                        "days_held": (
                            float(trade.get("Days_Since_Entry", 0)) if pd.notna(trade.get("Days_Since_Entry")) else 0
                        ),
                        "unrealized_pnl": (
                            float(trade.get("Current_Unrealized_PnL", 0))
                            if pd.notna(trade.get("Current_Unrealized_PnL"))
                            else 0
                        ),
                    }
                )
        return positions

    def _assess_portfolio_risk(self, active_trades: pd.DataFrame) -> dict[str, Any]:
        """Assess current portfolio risk"""
        return {
            "position_count": len(active_trades),
            "concentration_risk": ("LOW" if len(active_trades) > 5 else "MEDIUM" if len(active_trades) > 2 else "HIGH"),
            "status": "ACTIVE" if len(active_trades) > 0 else "NO_POSITIONS",
        }

    def _get_last_signal_info(self, active_trades: pd.DataFrame) -> dict[str, Any]:
        """Get information about the last signal"""
        if active_trades.empty:
            return {"status": "NO_ACTIVE_SIGNALS"}

        # Get most recent entry
        latest_trade = active_trades.iloc[-1] if not active_trades.empty else None
        if latest_trade is not None:
            return {
                "ticker": latest_trade.get("Ticker", "N/A"),
                "strategy": latest_trade.get("Strategy_Type", "N/A"),
                "entry_date": str(latest_trade.get("Entry_Timestamp", "N/A")),
            }

        return {"status": "NO_RECENT_SIGNALS"}

    def _get_market_context(self) -> dict[str, Any]:
        """Get current market context (simplified)"""
        return {
            "market_regime": "ANALYSIS_PENDING",
            "volatility_environment": "ANALYSIS_PENDING",
            "last_updated": self.execution_date.isoformat(),
        }

    def _generate_confidence_disclosure(self, key_metrics: dict[str, Any]) -> dict[str, Any]:
        """Generate confidence and limitation disclosures"""
        confidence = key_metrics["confidence_assessment"]
        sample_size = key_metrics["portfolio_overview"]["closed_trades"]

        limitations = []
        if sample_size < 25:
            limitations.append("Sample size below recommended minimum of 25 trades")
        if not confidence["statistical_significance"]:
            limitations.append("Returns lack statistical significance at 95% confidence level")
        if confidence["overall_confidence"] < 0.8:
            limitations.append("Overall analysis confidence below institutional grade")

        return {
            "overall_confidence": confidence["overall_confidence"],
            "sample_adequacy": confidence["sample_size_adequate"],
            "statistical_significance": confidence["statistical_significance"],
            "limitations": limitations,
        }

    def execute_synthesis(self) -> dict[str, Any]:
        """
        Execute atomic data synthesis
        """
        logger.info(f"Starting atomic synthesis for portfolio: {self.portfolio_name}")

        try:
            # Step 1: Load discovery and analysis data
            phase_data = self.load_phase_data()

            # Step 2: Extract key metrics
            key_metrics = self.extract_key_metrics(phase_data)

            # Step 3: Generate report data structures
            report_data = self.generate_report_data_structures(key_metrics, phase_data)

            # Step 4: Create synthesis output
            synthesis_output = {
                "portfolio": self.portfolio_name,
                "synthesis_metadata": {
                    "execution_timestamp": self.execution_date.isoformat(),
                    "confidence_score": key_metrics["confidence_assessment"]["overall_confidence"],
                    "reports_ready": True,
                },
                "key_metrics": key_metrics,
                "report_data_structures": report_data,
                "data_sources": {
                    "discovery_file": phase_data["discovery_file"],
                    "analysis_file": phase_data["analysis_file"],
                    "csv_source": phase_data["discovery"]["discovery_metadata"]["data_source"],
                },
                "next_phase_inputs": {
                    "validation_ready": True,
                    "reports_generated": 3,
                    "synthesis_confidence": key_metrics["confidence_assessment"]["overall_confidence"],
                },
            }

            # Step 5: Save synthesis output
            output_filename = f"{self.portfolio_name}_{self.execution_date.strftime('%Y%m%d')}.json"
            output_file = self.output_dir / output_filename

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(synthesis_output, f, indent=2, ensure_ascii=False)

            logger.info(f"Synthesis output saved to: {output_file}")

            # Log summary
            logger.info(
                f"Synthesis complete - Report structures generated: {len(report_data)}, "
                f"Key metrics extracted, "
                f"Confidence: {key_metrics['confidence_assessment']['overall_confidence']:.3f}"
            )

            return synthesis_output

        except Exception as e:
            logger.error(f"Atomic synthesis failed: {e}")
            raise


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Atomic trade history synthesis tool")
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

    # Execute synthesis
    synthesis_tool = AtomicSynthesisTool(portfolio_name=args.portfolio)
    result = synthesis_tool.execute_synthesis()

    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Print summary
        print("\n" + "=" * 60)
        print("ATOMIC SYNTHESIS COMPLETE")
        print("=" * 60)
        print("Portfolio: {result['portfolio']}")
        print("Execution: {result['synthesis_metadata']['execution_timestamp']}")
        print(f"Confidence Score: {result['synthesis_metadata']['confidence_score']:.3f}")

        print("\nKEY METRICS:")
        metrics = result["key_metrics"]["performance_summary"]
        print("  Win Rate: {metrics.get('win_rate', 0):.1%}")
        print("  Total P&L: ${metrics.get('total_pnl', 0):.2f}")
        print("  Profit Factor: {metrics.get('profit_factor', 0):.2f}")

        print("\nREPORT DATA STRUCTURES:")
        report_data = result["report_data_structures"]
        print("  Executive Dashboard: Ready")
        print(
            f"  Historical Analysis: {report_data['historical_analysis']['closed_trades_summary']['count']} closed trades"
        )
        print(f"  Live Monitoring: {report_data['live_monitoring']['active_positions']['count']} active positions")

        print("\nCONFIDENCE ASSESSMENT:")
        confidence = result["key_metrics"]["confidence_assessment"]
        print("  Overall Confidence: {confidence['overall_confidence']:.3f}")
        print("  Sample Size Adequate: {confidence['sample_size_adequate']}")
        print("  Statistical Significance: {confidence['statistical_significance']}")

        print("\nOutput saved to: {synthesis_tool.output_dir}")
        print("=" * 60)


if __name__ == "__main__":
    main()
