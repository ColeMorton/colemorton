"""
IMF Data Service

Production-grade International Monetary Fund (IMF) Data Portal integration with:
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

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config_loader import ConfigLoader


class IMFService(BaseFinancialService):
    """
    IMF Data Portal service extending BaseFinancialService

    Provides access to IMF's comprehensive global economic data including:
    - GDP, inflation, unemployment data for 196 countries
    - World Economic Outlook indicators
    - Regional economic analysis (World, Advanced Economies, Emerging Markets)
    - Historical time series data and macroeconomic trends
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # IMF dataset codes with descriptions
        self.datasets = {
            "NGDP_RPCH": "Real GDP Growth",
            "NGDPD": "GDP (Nominal)",
            "NGDP_D": "GDP Deflator",
            "PCPIPCH": "Inflation Rate",
            "LUR": "Unemployment Rate",
            "GGX_NGDP": "Government Expenditure",
            "GGR_NGDP": "Government Revenue",
            "GGXCNL_NGDP": "Government Net Lending",
            "BCA_NGDPD": "Current Account Balance",
            "TXG_RPCH": "Volume of Exports",
            "TMG_RPCH": "Volume of Imports",
            "TX_RPCH": "Export Prices",
            "TM_RPCH": "Import Prices",
        }

        # Country codes mapping (ISO 3166-1 alpha-3)
        self.major_countries = {
            "US": "USA",
            "CN": "CHN",
            "JP": "JPN",
            "DE": "DEU",
            "IN": "IND",
            "UK": "GBR",
            "FR": "FRA",
            "IT": "ITA",
            "BR": "BRA",
            "CA": "CAN",
            "RU": "RUS",
            "KR": "KOR",
            "AU": "AUS",
            "ES": "ESP",
            "MX": "MEX",
            "ID": "IDN",
            "NL": "NLD",
            "SA": "SAU",
            "TR": "TUR",
            "TW": "TWN",
        }

        # Regional codes
        self.regions = {
            "WEO": "World",
            "AE": "Advanced Economies",
            "EMD": "Emerging Markets and Developing Economies",
        }

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate IMF response data"""

        # IMF typically returns dictionaries
        if isinstance(data, dict):
            # Check for API errors
            if "error" in data or "status" in data:
                error_msg = data.get("error", data.get("status", "Unknown error"))
                raise DataNotFoundError(f"IMF API error: {error_msg}")

            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()

        # Handle list responses
        elif isinstance(data, list):
            if not data:  # Empty list
                raise DataNotFoundError(f"No data found for {endpoint}")

        return data

    def get_country_data(
        self,
        indicator: str,
        country_code: str,
        start_year: int = None,
        end_year: int = None,
    ) -> dict[str, Any]:
        """
        Get economic data for a specific country

        Args:
            indicator: Economic indicator code (e.g., 'NGDP_RPCH' for GDP growth)
            country_code: ISO 3166-1 alpha-3 country code (e.g., 'USA', 'CHN')
            start_year: Starting year for data (not supported by IMF API - returns all data)
            end_year: Ending year for data (not supported by IMF API - returns all data)

        Returns:
            Dictionary containing country economic data
        """
        endpoint = f"{indicator.upper()}/{country_code.upper()}"
        # Note: IMF API rejects requests with parameters, so we get all data
        params = {}

        result = self._make_request_with_retry(endpoint, params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "indicator": indicator.upper(),
                    "indicator_description": self.datasets.get(indicator.upper(), "Unknown"),
                    "country_code": country_code.upper(),
                    "start_year": start_year,
                    "end_year": end_year,
                    "source": "imf",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_global_data(self, indicator: str, start_year: int = None, end_year: int = None) -> dict[str, Any]:
        """
        Get global economic data for an indicator

        Args:
            indicator: Economic indicator code
            start_year: Starting year for data (not supported by IMF API - returns all data)
            end_year: Ending year for data (not supported by IMF API - returns all data)

        Returns:
            Dictionary containing global economic data
        """
        endpoint = indicator.upper()
        # Note: IMF API rejects requests with parameters, so we get all data
        params = {}

        result = self._make_request_with_retry(endpoint, params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "indicator": indicator.upper(),
                    "indicator_description": self.datasets.get(indicator.upper(), "Unknown"),
                    "scope": "global",
                    "start_year": start_year,
                    "end_year": end_year,
                    "source": "imf",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_regional_data(
        self, indicator: str, region: str, start_year: int = None, end_year: int = None
    ) -> dict[str, Any]:
        """
        Get regional economic data

        Args:
            indicator: Economic indicator code
            region: Region code ('WEO' for World, 'AE' for Advanced Economies, 'EMD' for Emerging Markets)
            start_year: Starting year for data (not supported by IMF API - returns all data)
            end_year: Ending year for data (not supported by IMF API - returns all data)

        Returns:
            Dictionary containing regional economic data
        """
        endpoint = f"{indicator.upper()}/{region.upper()}"
        # Note: IMF API rejects requests with parameters, so we get all data
        params = {}

        result = self._make_request_with_retry(endpoint, params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "indicator": indicator.upper(),
                    "indicator_description": self.datasets.get(indicator.upper(), "Unknown"),
                    "region": region.upper(),
                    "region_description": self.regions.get(region.upper(), "Unknown"),
                    "start_year": start_year,
                    "end_year": end_year,
                    "source": "imf",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_multiple_countries(
        self,
        indicator: str,
        country_codes: list[str],
        start_year: int = None,
        end_year: int = None,
    ) -> dict[str, Any]:
        """
        Get economic data for multiple countries

        Args:
            indicator: Economic indicator code
            country_codes: List of country codes
            start_year: Starting year for data (not supported by IMF API - returns all data)
            end_year: Ending year for data (not supported by IMF API - returns all data)

        Returns:
            Dictionary containing multi-country economic data
        """
        countries = "+".join([code.upper() for code in country_codes])
        endpoint = f"{indicator.upper()}/{countries}"
        # Note: IMF API rejects requests with parameters, so we get all data
        params = {}

        result = self._make_request_with_retry(endpoint, params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "indicator": indicator.upper(),
                    "indicator_description": self.datasets.get(indicator.upper(), "Unknown"),
                    "countries": [code.upper() for code in country_codes],
                    "start_year": start_year,
                    "end_year": end_year,
                    "source": "imf",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_available_datasets(self) -> dict[str, Any]:
        """
        Get available economic indicators

        Returns:
            Dictionary containing available indicators and descriptions
        """
        return {
            "datasets": self.datasets.copy(),
            "count": len(self.datasets),
            "source": "imf",
            "timestamp": datetime.now().isoformat(),
        }

    def get_country_codes(self) -> dict[str, Any]:
        """
        Get major country codes

        Returns:
            Dictionary containing country codes and their ISO 3166-1 alpha-3 codes
        """
        return {
            "country_codes": self.major_countries.copy(),
            "count": len(self.major_countries),
            "note": "ISO 3166-1 alpha-3 country codes",
            "source": "imf",
            "timestamp": datetime.now().isoformat(),
        }

    def get_region_codes(self) -> dict[str, Any]:
        """
        Get available region codes

        Returns:
            Dictionary containing region codes and descriptions
        """
        return {
            "regions": self.regions.copy(),
            "count": len(self.regions),
            "source": "imf",
            "timestamp": datetime.now().isoformat(),
        }

    def get_gdp_growth_comparison(
        self, country_codes: list[str], start_year: int = None, end_year: int = None
    ) -> dict[str, Any]:
        """
        Get GDP growth comparison for multiple countries

        Args:
            country_codes: List of country codes
            start_year: Starting year for data
            end_year: Ending year for data

        Returns:
            Dictionary containing GDP growth comparison data
        """
        result = self.get_multiple_countries("NGDP_RPCH", country_codes, start_year, end_year)

        # Add specific metadata for GDP growth
        if isinstance(result, dict):
            result.update(
                {
                    "indicator_name": "Real GDP Growth",
                    "analysis_type": "gdp_growth_comparison",
                }
            )

        return result

    def get_inflation_comparison(
        self, country_codes: list[str], start_year: int = None, end_year: int = None
    ) -> dict[str, Any]:
        """
        Get inflation rate comparison for multiple countries

        Args:
            country_codes: List of country codes
            start_year: Starting year for data
            end_year: Ending year for data

        Returns:
            Dictionary containing inflation rate comparison data
        """
        result = self.get_multiple_countries("PCPIPCH", country_codes, start_year, end_year)

        # Add specific metadata for inflation
        if isinstance(result, dict):
            result.update(
                {
                    "indicator_name": "Inflation Rate",
                    "analysis_type": "inflation_comparison",
                }
            )

        return result

    def get_unemployment_comparison(
        self, country_codes: list[str], start_year: int = None, end_year: int = None
    ) -> dict[str, Any]:
        """
        Get unemployment rate comparison for multiple countries

        Args:
            country_codes: List of country codes
            start_year: Starting year for data
            end_year: Ending year for data

        Returns:
            Dictionary containing unemployment rate comparison data
        """
        result = self.get_multiple_countries("LUR", country_codes, start_year, end_year)

        # Add specific metadata for unemployment
        if isinstance(result, dict):
            result.update(
                {
                    "indicator_name": "Unemployment Rate",
                    "analysis_type": "unemployment_comparison",
                }
            )

        return result

    def get_global_economic_overview(self, year: int = None) -> dict[str, Any]:
        """
        Get comprehensive global economic overview

        Args:
            year: Specific year for data (optional)

        Returns:
            Dictionary containing global economic overview
        """
        try:
            overview = {
                "global_gdp_growth": self.get_regional_data("NGDP_RPCH", "WEO", year, year),
                "global_inflation": self.get_regional_data("PCPIPCH", "WEO", year, year),
                "advanced_economies_gdp": self.get_regional_data("NGDP_RPCH", "AE", year, year),
                "emerging_markets_gdp": self.get_regional_data("NGDP_RPCH", "EMD", year, year),
                "analysis_year": year,
                "analysis_type": "global_economic_overview",
                "source": "imf",
                "timestamp": datetime.now().isoformat(),
            }

            return overview

        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": "global_economic_overview",
                "source": "imf",
                "timestamp": datetime.now().isoformat(),
            }

    def health_check(self) -> dict[str, Any]:
        """Service health check"""
        try:
            # Test API connectivity with a simple request for US GDP growth
            result = self.get_country_data("NGDP_RPCH", "USA", 2023, 2023)

            return {
                "service_name": self.config.name,
                "status": "healthy",
                "api_connection": "ok",
                "test_endpoint": "NGDP_RPCH/USA",
                "test_result": "success" if result else "failed",
                "configuration": {
                    "cache_enabled": self.config.cache.enabled,
                    "rate_limit_enabled": self.config.rate_limit.enabled,
                    "requests_per_minute": self.config.rate_limit.requests_per_minute,
                    "cache_ttl_seconds": self.config.cache.ttl_seconds,
                },
                "capabilities": [
                    "13 key IMF datasets with global coverage (196 countries)",
                    "World Economic Outlook data and real-time indicators",
                    "GDP, inflation, unemployment, and trade data",
                    "Historical time series and macroeconomic indicators",
                    "Regional analysis (World, Advanced Economies, Emerging Markets)",
                ],
                "coverage": {
                    "countries": "196",
                    "indicators": len(self.datasets),
                    "regions": len(self.regions),
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "service_name": self.config.name,
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
            }


def create_imf_service(env: str = "dev") -> IMFService:
    """
    Factory function to create IMF service with configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured IMF service instance
    """
    # Use absolute path to config directory
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_loader = ConfigLoader(str(config_dir), auto_load_env=True)
    service_config = config_loader.get_service_config("imf", env)

    # Convert to ServiceConfig format
    from .base_financial_service import CacheConfig, RateLimitConfig, ServiceConfig

    config = ServiceConfig(
        name=service_config.name,
        base_url=service_config.base_url,
        api_key=service_config.api_key,
        timeout_seconds=service_config.timeout_seconds,
        max_retries=service_config.max_retries,
        cache=CacheConfig(**service_config.cache),
        rate_limit=RateLimitConfig(**service_config.rate_limit),
        headers=service_config.headers,
    )

    return IMFService(config)
