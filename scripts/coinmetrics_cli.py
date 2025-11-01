#!/usr/bin/env python3
"""
CoinMetrics CLI

Command-line interface for CoinMetrics institutional-grade cryptocurrency data with:
- Network data and on-chain metrics for Bitcoin and other cryptocurrencies
- Market data with institutional-grade quality standards
- Historical data with comprehensive coverage since genesis blocks
- Academic-rigor data validation and methodology transparency
- Free tier available with generous limits for Bitcoin analysis
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.coinmetrics import create_coinmetrics_service
from utils.cli_base import BaseFinancialCLI, OutputFormat


class CoinMetricsCLI(BaseFinancialCLI):
    """CLI for CoinMetrics institutional-grade crypto data service"""

    def __init__(self):
        super().__init__(
            service_name="coinmetrics",
            description="CoinMetrics institutional-grade cryptocurrency data service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_coinmetrics_service(env)
        return self.service

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform CoinMetrics service health check"""
        try:
            service = self._get_service(env)
            service.get_supported_assets()
            return {"status": "healthy", "service": "coinmetrics", "env": env}
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "coinmetrics",
                "env": env,
                "error": str(e),
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        return {
            "action": action,
            "service": "coinmetrics",
            "env": env,
            "status": "no_cache_implemented",
        }

    def _add_service_commands(self) -> None:
        """Add CoinMetrics specific commands"""

        @self.app.command("assets")
        def get_supported_assets(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get list of supported assets"""
            try:
                service = self._get_service(env)

                result = service.get_supported_assets()
                self._output_result(result, output_format, "Supported Assets")

            except Exception as e:
                self._handle_error(e, "Failed to get supported assets")

        @self.app.command("metrics")
        def get_available_metrics(
            asset: str = typer.Option("btc", help="Asset symbol (e.g., btc, eth)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get available metrics for an asset"""
            try:
                service = self._get_service(env)

                result = service.get_available_metrics(asset)
                self._output_result(result, output_format, f"Available Metrics: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get metrics for {asset}")

        @self.app.command("network-data")
        def get_network_data(
            asset: str = typer.Option("btc", help="Asset symbol (e.g., btc, eth)"),
            metrics: str = typer.Option(
                "AdrActCnt,BlkCnt,TxCnt,TxTfrValUSD",
                help="Comma-separated metrics (e.g., AdrActCnt,BlkCnt,TxCnt)",
            ),
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get network data for specified asset and metrics"""
            try:
                service = self._get_service(env)

                result = service.get_network_data(asset, metrics, start_date, end_date)
                self._output_result(result, output_format, f"Network Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get network data for {asset}")

        @self.app.command("market-data")
        def get_market_data(
            asset: str = typer.Option("btc", help="Asset symbol (e.g., btc, eth)"),
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get market data for specified asset"""
            try:
                service = self._get_service(env)

                result = service.get_market_data(asset, start_date, end_date)
                self._output_result(result, output_format, f"Market Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get market data for {asset}")

        @self.app.command("bitcoin-metrics")
        def get_bitcoin_cycle_metrics(
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin cycle-specific metrics (MVRV, NUPL, etc.)"""
            try:
                service = self._get_service(env)

                result = service.get_bitcoin_cycle_metrics(start_date, end_date)
                self._output_result(result, output_format, "Bitcoin Cycle Metrics")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin cycle metrics")

        @self.app.command("nupl")
        def get_nupl_data(
            asset: str = typer.Option("btc", help="Asset symbol (default: btc)"),
            start_date: str = typer.Option("2025-08-01", help="Start date for trend analysis (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get NUPL (Net Unrealized Profit/Loss) data for Bitcoin cycle analysis"""
            try:
                service = self._get_service(env)

                result = service.get_nupl_data(asset, start_date, end_date)
                self._output_result(result, output_format, "Bitcoin NUPL Data")

            except Exception as e:
                self._handle_error(e, "Failed to get NUPL data")

        @self.app.command("supply-data")
        def get_supply_data(
            asset: str = typer.Option("btc", help="Asset symbol (e.g., btc, eth)"),
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get supply-related data for specified asset"""
            try:
                service = self._get_service(env)

                result = service.get_supply_data(asset, start_date, end_date)
                self._output_result(result, output_format, f"Supply Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get supply data for {asset}")

        @self.app.command("mining-data")
        def get_mining_data(
            asset: str = typer.Option("btc", help="Asset symbol (currently supports btc)"),
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get mining-related data (hash rate, difficulty, etc.)"""
            try:
                service = self._get_service(env)

                result = service.get_mining_data(asset, start_date, end_date)
                self._output_result(result, output_format, f"Mining Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get mining data for {asset}")

        @self.app.command("exchanges")
        def get_exchange_data(
            asset: str = typer.Option("btc", help="Asset symbol (e.g., btc, eth)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get exchange-related data and metrics"""
            try:
                service = self._get_service(env)

                result = service.get_exchange_data(asset)
                self._output_result(result, output_format, f"Exchange Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get exchange data for {asset}")

        @self.app.command("institutions")
        def get_institutional_data(
            asset: str = typer.Option("btc", help="Asset symbol (e.g., btc, eth)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get institutional holdings and flow data"""
            try:
                service = self._get_service(env)

                result = service.get_institutional_data(asset)
                self._output_result(result, output_format, f"Institutional Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get institutional data for {asset}")

        @self.app.command("realizedcap")
        def get_realized_cap_data(
            asset: str = typer.Option("btc", help="Asset symbol (currently supports btc)"),
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get realized capitalization data for Bitcoin cycle analysis"""
            try:
                service = self._get_service(env)

                result = service.get_realized_cap_data(asset, start_date, end_date)
                self._output_result(result, output_format, f"Realized Cap Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get realized cap data for {asset}")

        @self.app.command("mvrv")
        def get_mvrv_data(
            asset: str = typer.Option("btc", help="Asset symbol (currently supports btc)"),
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get MVRV (Market Value to Realized Value) data with cycle analysis"""
            try:
                service = self._get_service(env)

                result = service.get_mvrv_data(asset, start_date, end_date if end_date else None)
                self._output_result(result, output_format, f"MVRV Data: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get MVRV data for {asset}")

        @self.app.command("enhanced-bitcoin-metrics")
        def get_enhanced_bitcoin_cycle_metrics(
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get enhanced Bitcoin cycle metrics including MVRV analysis"""
            try:
                service = self._get_service(env)

                result = service.get_enhanced_bitcoin_cycle_metrics(start_date, end_date if end_date else None)
                self._output_result(result, output_format, "Enhanced Bitcoin Cycle Metrics")

            except Exception as e:
                self._handle_error(e, "Failed to get enhanced Bitcoin cycle metrics")

        @self.app.command("mvrv-zscore")
        def get_mvrv_z_score(
            asset: str = typer.Option("btc", help="Asset symbol (currently supports btc)"),
            start_date: str = typer.Option("2020-01-01", help="Start date for historical baseline (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            lookback_days: int = typer.Option(
                1460,
                help="Days of historical data for Z-Score calculation (default: 4 years)",
            ),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get MVRV Z-Score analysis for Bitcoin cycle intelligence framework

            Provides comprehensive MVRV Z-Score analysis including:
            - Current MVRV Z-Score with historical statistical baseline
            - Historical percentile ranking
            - Schema-compliant zone classification for cycle intelligence
            - Statistical confidence metrics and trend analysis
            """
            try:
                service = self._get_service(env)

                result = service.get_mvrv_z_score_data(asset, start_date, end_date if end_date else None, lookback_days)
                self._output_result(result, output_format, f"MVRV Z-Score Analysis: {asset.upper()}")

            except Exception as e:
                self._handle_error(e, f"Failed to get MVRV Z-Score data for {asset}")

        @self.app.command("cycle-intelligence-mvrv")
        def get_cycle_intelligence_mvrv(
            analysis_date: str = typer.Option("", help="Analysis date (YYYY-MM-DD, default: today)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get MVRV data formatted for Bitcoin cycle intelligence discovery phase

            Returns MVRV Z-Score data structured to match the Bitcoin cycle intelligence
            discovery schema requirements, including all required fields for institutional-grade
            cycle analysis.
            """
            try:
                service = self._get_service(env)

                # Use today if no analysis date provided
                import datetime

                if not analysis_date:
                    analysis_date = datetime.datetime.now().strftime("%Y-%m-%d")

                # Get comprehensive MVRV Z-Score analysis
                mvrv_analysis = service.get_mvrv_z_score_data(
                    asset="btc",
                    start_date="2020-01-01",  # 4+ year baseline for reliability
                    end_date=analysis_date,
                    lookback_days=1460,
                )

                # Format for Bitcoin cycle intelligence schema compliance
                cycle_intelligence_format = {
                    "current_score": mvrv_analysis["current_score"],
                    "historical_percentile": mvrv_analysis["historical_percentile"],
                    "zone_classification": mvrv_analysis["zone_classification"],
                    "confidence": mvrv_analysis["confidence"],
                    "statistical_validation": {
                        "data_points": mvrv_analysis["statistical_metrics"]["data_points"],
                        "baseline_period_days": mvrv_analysis["statistical_metrics"]["lookback_days"],
                        "mean_mvrv": mvrv_analysis["statistical_metrics"]["mean"],
                        "std_deviation": mvrv_analysis["statistical_metrics"]["std_dev"],
                    },
                    "trend_analysis": mvrv_analysis["trend_analysis"],
                    "analysis_metadata": {
                        "analysis_date": mvrv_analysis["analysis_date"],
                        "current_mvrv_ratio": mvrv_analysis["current_mvrv_ratio"],
                        "data_quality": "institutional_grade"
                        if mvrv_analysis["confidence"] >= 0.9
                        else "standard_grade",
                    },
                }

                self._output_result(
                    cycle_intelligence_format,
                    output_format,
                    "Bitcoin Cycle Intelligence MVRV Analysis",
                )

            except Exception as e:
                self._handle_error(e, "Failed to get cycle intelligence MVRV data")


def main():
    """Main entry point for the CoinMetrics CLI"""
    cli = CoinMetricsCLI()
    cli.run()


if __name__ == "__main__":
    main()
