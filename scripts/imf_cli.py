#!/usr/bin/env python3
"""
IMF Data CLI

Command-line interface for International Monetary Fund (IMF) Data Portal with:
- 13 key IMF datasets with global coverage (196 countries)
- World Economic Outlook data and real-time economic indicators
- GDP, inflation, unemployment, and trade data
- Historical time series data and macroeconomic indicators
- Country and regional economic metrics
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.imf import create_imf_service
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError


class IMFCLI(BaseFinancialCLI):
    """CLI for IMF Data service"""

    def __init__(self):
        super().__init__(service_name="imf", description="IMF Data Portal service CLI")
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_imf_service(env)
        return self.service

    def _add_service_commands(self) -> None:
        """Add IMF specific commands"""

        @self.app.command("country")
        def get_country_data(
            indicator: str = typer.Argument(..., help="Economic indicator (e.g., NGDP_RPCH, PCPIPCH, LUR)"),
            country_code: str = typer.Argument(..., help="Country code (e.g., USA, CHN, DEU)"),
            start_year: int = typer.Option(None, help="Starting year for data"),
            end_year: int = typer.Option(None, help="Ending year for data"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get economic data for a specific country"""
            try:
                service = self._get_service(env)

                result = service.get_country_data(indicator, country_code, start_year, end_year)
                self._output_result(result, output_format, f"Country Data: {country_code} - {indicator}")

            except Exception as e:
                self._handle_error(e, f"Failed to get country data for {country_code}")

        @self.app.command("global")
        def get_global_data(
            indicator: str = typer.Argument(..., help="Economic indicator (e.g., NGDP_RPCH, PCPIPCH, LUR)"),
            start_year: int = typer.Option(None, help="Starting year for data"),
            end_year: int = typer.Option(None, help="Ending year for data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get global economic data for an indicator"""
            try:
                service = self._get_service(env)

                result = service.get_global_data(indicator, start_year, end_year)
                self._output_result(result, output_format, f"Global Data: {indicator}")

            except Exception as e:
                self._handle_error(e, f"Failed to get global data for {indicator}")

        @self.app.command("regional")
        def get_regional_data(
            indicator: str = typer.Argument(..., help="Economic indicator"),
            region: str = typer.Argument(
                ...,
                help="Region code (WEO=World, AE=Advanced Economies, EMD=Emerging Markets)",
            ),
            start_year: int = typer.Option(None, help="Starting year for data"),
            end_year: int = typer.Option(None, help="Ending year for data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get regional economic data"""
            try:
                service = self._get_service(env)

                result = service.get_regional_data(indicator, region, start_year, end_year)
                self._output_result(result, output_format, f"Regional Data: {region} - {indicator}")

            except Exception as e:
                self._handle_error(e, f"Failed to get regional data for {region}")

        @self.app.command("multiple")
        def get_multiple_countries(
            indicator: str = typer.Argument(..., help="Economic indicator"),
            country_codes: str = typer.Argument(..., help="Comma-separated country codes (e.g., USA,CHN,JPN)"),
            start_year: int = typer.Option(None, help="Starting year for data"),
            end_year: int = typer.Option(None, help="Ending year for data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get economic data for multiple countries"""
            try:
                service = self._get_service(env)
                country_list = [code.strip().upper() for code in country_codes.split(",")]

                result = service.get_multiple_countries(indicator, country_list, start_year, end_year)
                self._output_result(result, output_format, f"Multi-Country Data: {indicator}")

            except Exception as e:
                self._handle_error(e, "Failed to get multi-country data")

        @self.app.command("datasets")
        def get_available_datasets(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get list of available economic indicators"""
            try:
                service = self._get_service(env)

                result = service.get_available_datasets()

                # Convert for table display
                if output_format == OutputFormat.TABLE and isinstance(result, dict):
                    datasets = result.get("datasets", {})
                    table_data = [{"code": code, "description": desc} for code, desc in datasets.items()]
                    result = table_data

                self._output_result(result, output_format, "Available IMF Economic Indicators")

            except Exception as e:
                self._handle_error(e, "Failed to get available datasets")

        @self.app.command("countries")
        def get_country_codes(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get list of major country codes"""
            try:
                service = self._get_service(env)

                result = service.get_country_codes()

                # Convert for table display
                if output_format == OutputFormat.TABLE and isinstance(result, dict):
                    countries = result.get("country_codes", {})
                    table_data = [{"country_code": iso2, "iso3_code": iso3} for iso2, iso3 in countries.items()]
                    result = table_data

                self._output_result(result, output_format, "Major Country Codes")

            except Exception as e:
                self._handle_error(e, "Failed to get country codes")

        @self.app.command("regions")
        def get_region_codes(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get available region codes"""
            try:
                service = self._get_service(env)

                result = service.get_region_codes()

                # Convert for table display
                if output_format == OutputFormat.TABLE and isinstance(result, dict):
                    regions = result.get("regions", {})
                    table_data = [{"region_code": code, "description": desc} for code, desc in regions.items()]
                    result = table_data

                self._output_result(result, output_format, "Available Regions")

            except Exception as e:
                self._handle_error(e, "Failed to get region codes")

        @self.app.command("gdp-growth")
        def get_gdp_growth_comparison(
            country_codes: str = typer.Argument(..., help="Comma-separated country codes"),
            start_year: int = typer.Option(None, help="Starting year for data"),
            end_year: int = typer.Option(None, help="Ending year for data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get GDP growth comparison for multiple countries"""
            try:
                service = self._get_service(env)
                country_list = [code.strip().upper() for code in country_codes.split(",")]

                result = service.get_gdp_growth_comparison(country_list, start_year, end_year)
                self._output_result(result, output_format, "GDP Growth Comparison")

            except Exception as e:
                self._handle_error(e, "Failed to get GDP growth comparison")

        @self.app.command("inflation")
        def get_inflation_comparison(
            country_codes: str = typer.Argument(..., help="Comma-separated country codes"),
            start_year: int = typer.Option(None, help="Starting year for data"),
            end_year: int = typer.Option(None, help="Ending year for data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get inflation rate comparison for multiple countries"""
            try:
                service = self._get_service(env)
                country_list = [code.strip().upper() for code in country_codes.split(",")]

                result = service.get_inflation_comparison(country_list, start_year, end_year)
                self._output_result(result, output_format, "Inflation Rate Comparison")

            except Exception as e:
                self._handle_error(e, "Failed to get inflation comparison")

        @self.app.command("unemployment")
        def get_unemployment_comparison(
            country_codes: str = typer.Argument(..., help="Comma-separated country codes"),
            start_year: int = typer.Option(None, help="Starting year for data"),
            end_year: int = typer.Option(None, help="Ending year for data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get unemployment rate comparison for multiple countries"""
            try:
                service = self._get_service(env)
                country_list = [code.strip().upper() for code in country_codes.split(",")]

                result = service.get_unemployment_comparison(country_list, start_year, end_year)
                self._output_result(result, output_format, "Unemployment Rate Comparison")

            except Exception as e:
                self._handle_error(e, "Failed to get unemployment comparison")

        @self.app.command("overview")
        def get_global_economic_overview(
            year: int = typer.Option(None, help="Specific year for analysis"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive global economic overview"""
            try:
                service = self._get_service(env)

                result = service.get_global_economic_overview(year)
                self._output_result(result, output_format, "Global Economic Overview")

            except Exception as e:
                self._handle_error(e, "Failed to get global economic overview")

        @self.app.command("compare")
        def compare_countries(
            country_codes: str = typer.Argument(..., help="Comma-separated country codes"),
            indicators: str = typer.Option("NGDP_RPCH,PCPIPCH,LUR", help="Comma-separated indicators"),
            year: int = typer.Option(None, help="Specific year for comparison"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Compare multiple economic indicators across countries"""
            try:
                service = self._get_service(env)
                country_list = [code.strip().upper() for code in country_codes.split(",")]
                indicator_list = [ind.strip().upper() for ind in indicators.split(",")]

                comparison_data = []
                for indicator in indicator_list:
                    try:
                        result = service.get_multiple_countries(indicator, country_list, year, year)
                        if result:
                            comparison_data.append({"indicator": indicator, "data": result})
                    except Exception as e:
                        comparison_data.append({"indicator": indicator, "error": str(e)})

                final_result = {
                    "comparison_data": comparison_data,
                    "countries": country_list,
                    "indicators": indicator_list,
                    "year": year,
                    "source": "imf",
                    "timestamp": datetime.now().isoformat(),
                }

                self._output_result(final_result, output_format, "Country Economic Comparison")

            except Exception as e:
                self._handle_error(e, "Failed to compare countries")

        @self.app.command("quick")
        def quick_country_overview(
            country_code: str = typer.Argument(..., help="Country code (e.g., USA, CHN, DEU)"),
            year: int = typer.Option(None, help="Specific year for data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get quick economic overview for a country (GDP, inflation, unemployment)"""
            try:
                service = self._get_service(env)

                # Get key indicators
                indicators = [
                    "NGDP_RPCH",
                    "PCPIPCH",
                    "LUR",
                ]  # GDP growth, inflation, unemployment

                overview_data = []
                for indicator in indicators:
                    try:
                        result = service.get_country_data(indicator, country_code, year, year)
                        overview_data.append(
                            {
                                "indicator": indicator,
                                "description": service.datasets.get(indicator, "Unknown"),
                                "data": result,
                            }
                        )
                    except Exception as e:
                        overview_data.append(
                            {
                                "indicator": indicator,
                                "description": service.datasets.get(indicator, "Unknown"),
                                "error": str(e),
                            }
                        )

                # Simplify for table display
                if output_format == OutputFormat.TABLE:
                    table_data = []
                    for item in overview_data:
                        table_data.append(
                            {
                                "indicator": item["indicator"],
                                "description": item["description"],
                                "status": "success" if "data" in item else "error",
                            }
                        )
                    final_result = table_data
                else:
                    final_result = {
                        "country_code": country_code,
                        "year": year,
                        "overview": overview_data,
                        "source": "imf",
                        "timestamp": datetime.now().isoformat(),
                    }

                self._output_result(final_result, output_format, f"Quick Overview: {country_code}")

            except Exception as e:
                self._handle_error(e, f"Failed to get overview for {country_code}")

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform IMF service health check"""
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
    """Main entry point for IMF CLI"""
    cli = IMFCLI()
    cli.run()


if __name__ == "__main__":
    main()
