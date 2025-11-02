#!/usr/bin/env python3
"""
FRED Economic CLI

Command-line interface for Federal Reserve Economic Data with:
- Comprehensive economic indicators and time series data
- Sector-specific economic analysis
- Inflation, interest rates, employment, and GDP data
- Historical economic data with flexible date ranges
- Real-time economic indicators
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.fred_economic import create_fred_economic_service
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError


class FREDEconomicCLI(BaseFinancialCLI):
    """CLI for FRED Economic service"""

    def __init__(self):
        super().__init__(
            service_name="fred",
            description="Federal Reserve Economic Data (FRED) service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_fred_economic_service(env)
        return self.service

    def _add_service_commands(self) -> None:
        """Add FRED Economic specific commands"""

        @self.app.command("indicator")
        def get_economic_indicator(
            series_id: str = typer.Argument(..., help="FRED series ID (e.g., GDP, UNRATE, FEDFUNDS)"),
            date_range: str = typer.Option("1y", help="Time period (1y, 2y, 5y, 10y, ytd)"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get economic indicator data with analysis"""
            try:
                service = self._get_service(env)

                result = service.get_economic_indicator(series_id, date_range)
                self._output_result(result, output_format, f"Economic Indicator: {series_id}")

            except Exception as e:
                self._handle_error(e, f"Failed to get economic indicator {series_id}")

        @self.app.command("series")
        def get_series_data(
            series_id: str = typer.Argument(..., help="FRED series ID"),
            start_date: str = typer.Option(None, help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option(None, help="End date (YYYY-MM-DD)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get raw time series data for a FRED series"""
            try:
                service = self._get_service(env)

                result = service.get_series_data(series_id, start_date, end_date)
                self._output_result(result, output_format, f"Time Series: {series_id}")

            except Exception as e:
                self._handle_error(e, f"Failed to get series data for {series_id}")

        @self.app.command("info")
        def get_series_info(
            series_id: str = typer.Argument(..., help="FRED series ID"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get series information and metadata"""
            try:
                service = self._get_service(env)

                result = service.get_series_info(series_id)
                self._output_result(result, output_format, f"Series Info: {series_id}")

            except Exception as e:
                self._handle_error(e, f"Failed to get series info for {series_id}")

        @self.app.command("search")
        def search_series(
            search_text: str = typer.Argument(..., help="Search terms"),
            limit: int = typer.Option(10, help="Maximum number of results"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Search for FRED series by text"""
            try:
                service = self._get_service(env)

                result = service.search_series(search_text, limit)
                self._output_result(result, output_format, f"Search Results: {search_text}")

            except Exception as e:
                self._handle_error(e, f"Failed to search for '{search_text}'")

        @self.app.command("sector")
        def get_sector_indicators(
            sector: str = typer.Argument(
                ...,
                help="Sector (technology, healthcare, financial, energy, retail, housing)",
            ),
            indicators: str = typer.Option("", help="Comma-separated specific indicators"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get economic indicators for a specific sector"""
            try:
                service = self._get_service(env)

                result = service.get_sector_indicators(sector, indicators)
                self._output_result(result, output_format, f"Sector Indicators: {sector}")

            except Exception as e:
                self._handle_error(e, f"Failed to get sector indicators for {sector}")

        @self.app.command("inflation")
        def get_inflation_data(
            period: str = typer.Option("1y", help="Time period (1y, 2y, 5y)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive inflation data from multiple measures"""
            try:
                service = self._get_service(env)

                result = service.get_inflation_data(period)
                self._output_result(result, output_format, f"Inflation Data ({period})")

            except Exception as e:
                self._handle_error(e, f"Failed to get inflation data for {period}")

        @self.app.command("rates")
        def get_interest_rates(
            rate_type: str = typer.Option(
                "all",
                help="Rate type (all, Federal_Funds_Rate, 10_Year_Treasury, etc.)",
            ),
            period: str = typer.Option("1y", help="Time period (1y, 2y, 5y)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get interest rate data"""
            try:
                service = self._get_service(env)

                result = service.get_interest_rates(rate_type, period)
                self._output_result(result, output_format, f"Interest Rates: {rate_type} ({period})")

            except Exception as e:
                self._handle_error(e, f"Failed to get interest rates for {rate_type}")

        @self.app.command("indicators")
        def list_available_indicators(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """List all available economic indicators by category"""
            try:
                service = self._get_service(env)

                result = service.get_available_indicators()
                self._output_result(result, output_format, "Available Economic Indicators")

            except Exception as e:
                self._handle_error(e, "Failed to get available indicators")

        @self.app.command("analyze")
        def economic_analysis(
            categories: str = typer.Option(
                "inflation,interest_rates,employment",
                help="Comma-separated categories to analyze",
            ),
            period: str = typer.Option("1y", help="Analysis period"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Comprehensive economic analysis across categories"""
            try:
                service = self._get_service(env)

                category_list = [cat.strip() for cat in categories.split(",")]

                analysis = {
                    "analysis_timestamp": service.get_economic_indicator("FEDFUNDS", period).get("timestamp"),
                    "analysis_period": period,
                    "categories_analyzed": category_list,
                    "economic_data": {},
                }

                # Get data for each category
                for category in category_list:
                    try:
                        if category == "inflation":
                            analysis["economic_data"]["inflation"] = service.get_inflation_data(period)
                        elif category == "interest_rates":
                            analysis["economic_data"]["interest_rates"] = service.get_interest_rates("all", period)
                        elif category == "employment":
                            analysis["economic_data"]["employment"] = service.get_economic_indicator("UNRATE", period)
                        elif category == "gdp":
                            analysis["economic_data"]["gdp"] = service.get_economic_indicator("GDP", period)
                        else:
                            # Try as direct series ID
                            analysis["economic_data"][category] = service.get_economic_indicator(category, period)

                    except Exception as e:
                        analysis["economic_data"][category] = {"error": str(e)}

                self._output_result(analysis, output_format, f"Economic Analysis ({period})")

            except Exception as e:
                self._handle_error(e, "Failed to perform economic analysis")

        @self.app.command("batch")
        def batch_indicators(
            series_ids: str = typer.Argument(..., help="Comma-separated FRED series IDs"),
            date_range: str = typer.Option("1y", help="Time period"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get data for multiple economic indicators"""
            try:
                service = self._get_service(env)
                series_list = [s.strip().upper() for s in series_ids.split(",")]

                results = []
                for series_id in series_list:
                    try:
                        indicator_data = service.get_economic_indicator(series_id, date_range)
                        stats = indicator_data.get("statistics", {})

                        row = {
                            "series_id": series_id,
                            "series_title": indicator_data.get("series_title", "Unknown"),
                            "latest_value": stats.get("latest_value", "N/A"),
                            "trend": stats.get("trend", "N/A"),
                            "observations": stats.get("observations_count", 0),
                        }
                        results.append(row)

                    except Exception as e:
                        row = {
                            "series_id": series_id,
                            "series_title": "ERROR",
                            "latest_value": "ERROR",
                            "trend": "ERROR",
                            "observations": 0,
                            "error": str(e),
                        }
                        results.append(row)

                self._output_result(results, output_format, f"Batch Economic Indicators ({date_range})")

            except Exception as e:
                self._handle_error(e, "Batch indicator operation failed")

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform FRED Economic service health check"""
        service = self._get_service(env)
        return service.health_check()

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        service = self._get_service(env)

        if action == "clear":
            service.clear_cache()
            return {"action": "clear", "status": "success", "message": "Cache cleared"}
        if action == "cleanup":
            service.cleanup_cache()
            return {
                "action": "cleanup",
                "status": "success",
                "message": "Expired cache entries removed",
            }
        if action == "stats":
            return {
                "action": "stats",
                "cache_info": service.get_service_info(),
                "cache_directory": str(service.cache.cache_dir),
            }
        raise ValidationError(f"Unknown cache action: {action}")


def main():
    """Main entry point for FRED Economic CLI"""
    cli = FREDEconomicCLI()
    cli.run()


if __name__ == "__main__":
    main()
