#!/usr/bin/env python3
"""
Alternative.me CLI

Command-line interface for Alternative.me Crypto Fear & Greed Index with:
- Most popular crypto sentiment indicator with daily updates
- 0-100 scale sentiment scoring with historical data
- Multiple data sources integration for comprehensive sentiment analysis
- Completely free API with no authentication required
- Perfect for Bitcoin cycle analysis and market sentiment tracking
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.alternative_me import create_alternative_me_service
from utils.cli_base import BaseFinancialCLI, OutputFormat


class AlternativeMeCLI(BaseFinancialCLI):
    """CLI for Alternative.me Crypto Fear & Greed Index service"""

    def __init__(self):
        super().__init__(
            service_name="alternative_me",
            description="Alternative.me Crypto Fear & Greed Index service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_alternative_me_service(env)
        return self.service

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Alternative.me service health check"""
        try:
            service = self._get_service(env)
            service.get_current_fear_greed()
            return {"status": "healthy", "service": "alternative_me", "env": env}
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "alternative_me",
                "env": env,
                "error": str(e),
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        return {
            "action": action,
            "service": "alternative_me",
            "env": env,
            "status": "no_cache_implemented",
        }

    def _add_service_commands(self) -> None:
        """Add Alternative.me specific commands"""

        @self.app.command("current")
        def get_current_fear_greed(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current Fear & Greed Index value"""
            try:
                service = self._get_service(env)

                result = service.get_current_fear_greed()
                self._output_result(result, output_format, "Current Fear & Greed Index")

            except Exception as e:
                self._handle_error(e, "Failed to get current Fear & Greed Index")

        @self.app.command("historical")
        def get_historical_fear_greed(
            limit: int = typer.Option(10, help="Number of historical days (max 1000)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get historical Fear & Greed Index values"""
            try:
                service = self._get_service(env)

                if limit > 1000:
                    limit = 1000
                elif limit < 1:
                    limit = 1

                result = service.get_historical_fear_greed(limit)
                self._output_result(result, output_format, f"Historical Fear & Greed ({limit} days)")

            except Exception as e:
                self._handle_error(e, "Failed to get historical Fear & Greed data")

        @self.app.command("date")
        def get_fear_greed_by_date(
            date: str = typer.Argument(..., help="Date in DD-MM-YYYY or YYYY-MM-DD format"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Fear & Greed Index for a specific date"""
            try:
                service = self._get_service(env)

                result = service.get_fear_greed_by_date(date)
                self._output_result(result, output_format, f"Fear & Greed Index for {date}")

            except Exception as e:
                self._handle_error(e, f"Failed to get Fear & Greed data for {date}")

        @self.app.command("range")
        def get_fear_greed_range(
            start_date: str = typer.Argument(..., help="Start date (DD-MM-YYYY or YYYY-MM-DD)"),
            end_date: str = typer.Argument(..., help="End date (DD-MM-YYYY or YYYY-MM-DD)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get Fear & Greed Index for a date range"""
            try:
                service = self._get_service(env)

                result = service.get_fear_greed_range(start_date, end_date)
                self._output_result(result, output_format, f"Fear & Greed ({start_date} to {end_date})")

            except Exception as e:
                self._handle_error(e, "Failed to get Fear & Greed range data")

        @self.app.command("analysis")
        def get_sentiment_analysis(
            days: int = typer.Option(30, help="Number of days for analysis"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get sentiment analysis with statistics over specified period"""
            try:
                service = self._get_service(env)

                result = service.get_sentiment_analysis(days)
                self._output_result(result, output_format, f"Sentiment Analysis ({days} days)")

            except Exception as e:
                self._handle_error(e, "Failed to get sentiment analysis")

        @self.app.command("extremes")
        def get_extreme_values(
            days: int = typer.Option(365, help="Period for finding extremes (days)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get extreme fear and greed values over specified period"""
            try:
                service = self._get_service(env)

                result = service.get_extreme_values(days)
                self._output_result(result, output_format, f"Extreme Values ({days} days)")

            except Exception as e:
                self._handle_error(e, "Failed to get extreme values")

        @self.app.command("bitcoin-correlation")
        def get_bitcoin_correlation(
            days: int = typer.Option(90, help="Period for correlation analysis (days)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Analyze correlation between Fear & Greed and Bitcoin price movements"""
            try:
                service = self._get_service(env)

                result = service.get_bitcoin_correlation(days)
                self._output_result(result, output_format, f"Bitcoin Correlation ({days} days)")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin correlation analysis")

        @self.app.command("zones")
        def get_zone_distribution(
            days: int = typer.Option(365, help="Period for zone analysis (days)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get distribution of time spent in different Fear & Greed zones"""
            try:
                service = self._get_service(env)

                result = service.get_zone_distribution(days)
                self._output_result(result, output_format, f"Zone Distribution ({days} days)")

            except Exception as e:
                self._handle_error(e, "Failed to get zone distribution")

        @self.app.command("summary")
        def get_market_summary(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive market sentiment summary"""
            try:
                service = self._get_service(env)

                result = service.get_market_summary()
                self._output_result(result, output_format, "Market Sentiment Summary")

            except Exception as e:
                self._handle_error(e, "Failed to get market sentiment summary")


def main():
    """Main entry point for the Alternative.me CLI"""
    cli = AlternativeMeCLI()
    cli.run()


if __name__ == "__main__":
    main()
