#!/usr/bin/env python3
"""
Bitcoin Network Statistics CLI

Command-line interface for comprehensive Bitcoin network statistics with:
- Comprehensive network health metrics from multiple free sources
- Real-time mempool and mining data aggregation
- Historical network statistics and trend analysis
- Multi-source data validation and reliability
- Completely free service using public APIs (Mempool.space, Blockchain.com, CoinMetrics)
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.bitcoin_network_stats import create_bitcoin_network_stats_service
from utils.cli_base import BaseFinancialCLI, OutputFormat


class BitcoinNetworkStatsCLI(BaseFinancialCLI):
    """CLI for Bitcoin Network Statistics aggregation service"""

    def __init__(self):
        super().__init__(
            service_name="bitcoin_network_stats",
            description="Bitcoin Network Statistics aggregation service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_bitcoin_network_stats_service(env)
        return self.service

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Bitcoin Network Stats service health check"""
        try:
            service = self._get_service(env)
            overview = service.get_network_overview()
            return {
                "status": "healthy",
                "service": "bitcoin_network_stats",
                "env": env,
                "sources": len(overview.get("sources", [])),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "bitcoin_network_stats",
                "env": env,
                "error": str(e),
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        return {
            "action": action,
            "service": "bitcoin_network_stats",
            "env": env,
            "status": "no_cache_implemented",
        }

    def _add_service_commands(self) -> None:
        """Add Bitcoin Network Statistics specific commands"""

        @self.app.command("overview")
        def get_network_overview(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive Bitcoin network overview"""
            try:
                service = self._get_service(env)

                result = service.get_network_overview()
                self._output_result(result, output_format, "Bitcoin Network Overview")

            except Exception as e:
                self._handle_error(e, "Failed to get network overview")

        @self.app.command("mempool")
        def get_mempool_analysis(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get detailed mempool analysis"""
            try:
                service = self._get_service(env)

                result = service.get_mempool_analysis()
                self._output_result(result, output_format, "Bitcoin Mempool Analysis")

            except Exception as e:
                self._handle_error(e, "Failed to get mempool analysis")

        @self.app.command("mining")
        def get_mining_statistics(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive mining and difficulty statistics"""
            try:
                service = self._get_service(env)

                result = service.get_mining_statistics()
                self._output_result(result, output_format, "Bitcoin Mining Statistics")

            except Exception as e:
                self._handle_error(e, "Failed to get mining statistics")

        @self.app.command("health")
        def get_network_health_metrics(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get network health and activity metrics"""
            try:
                service = self._get_service(env)

                result = service.get_network_health_metrics()
                self._output_result(result, output_format, "Bitcoin Network Health Metrics")

            except Exception as e:
                self._handle_error(e, "Failed to get network health metrics")

        @self.app.command("price")
        def get_price_and_market_data(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin price and market data from multiple sources"""
            try:
                service = self._get_service(env)

                result = service.get_price_and_market_data()
                self._output_result(result, output_format, "Bitcoin Price and Market Data")

            except Exception as e:
                self._handle_error(e, "Failed to get price and market data")

        @self.app.command("report")
        def get_comprehensive_report(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive Bitcoin network statistics report"""
            try:
                service = self._get_service(env)

                result = service.get_comprehensive_report()
                self._output_result(result, output_format, "Comprehensive Bitcoin Network Report")

            except Exception as e:
                self._handle_error(e, "Failed to get comprehensive report")


def main():
    """Main entry point for the Bitcoin Network Statistics CLI"""
    cli = BitcoinNetworkStatsCLI()
    cli.run()


if __name__ == "__main__":
    main()
