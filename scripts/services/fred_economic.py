"""
FRED Economic Service

Production-grade Federal Reserve Economic Data (FRED) integration with:
- Comprehensive economic indicators and time series data
- Sector-specific economic analysis
- Inflation, interest rates, employment, and GDP data
- Historical economic data with flexible date ranges
- Real-time economic indicators
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


sys.path.append(os.path.join(os.path.dirname(__file__)))
from base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
    ValidationError,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config_loader import ConfigLoader


class FREDEconomicService(BaseFinancialService):
    """
    FRED Economic service extending BaseFinancialService

    Provides access to Federal Reserve Economic Data including:
    - Economic indicators (GDP, inflation, unemployment)
    - Interest rates and monetary policy data
    - Sector-specific economic metrics
    - Historical time series data
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Common economic indicators mapping
        self.indicators = {
            "inflation": {
                "CPI": "CPIAUCSL",
                "Core_CPI": "CPILFESL",
                "PCE": "PCEPI",
                "Core_PCE": "PCEPILFE",
            },
            "interest_rates": {
                "Federal_Funds_Rate": "FEDFUNDS",
                "10_Year_Treasury": "GS10",
                "30_Year_Fixed_Mortgage": "MORTGAGE30US",
                "3_Month_Treasury": "GS3M",
            },
            "employment": {
                "Unemployment_Rate": "UNRATE",
                "Nonfarm_Payrolls": "PAYEMS",
                "Labor_Force_Participation": "CIVPART",
                "Initial_Claims": "ICSA",
            },
            "gdp": {
                "GDP": "GDP",
                "Real_GDP": "GDPC1",
                "GDP_Growth": "A191RL1Q225SBEA",
                "GDP_Per_Capita": "GDPCA",
            },
            "housing": {
                "Housing_Starts": "HOUST",
                "New_Home_Sales": "HSN1F",
                "Existing_Home_Sales": "EXHOSLUSM495S",
                "Case_Shiller_Index": "CSUSHPISA",
            },
            "manufacturing": {
                "Industrial_Production": "INDPRO",
                "Capacity_Utilization": "TCU",
                "ISM_Manufacturing": "NAPM",
                "Durable_Goods_Orders": "DGORDER",
            },
        }

    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """Validate FRED response data"""

        if not isinstance(data, dict):
            raise ValidationError(f"Invalid response format for {endpoint}")

        # Check for API errors
        if "error_message" in data:
            raise DataNotFoundError(data["error_message"])

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        return data

    def _make_request_with_retry(self, endpoint: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """Override to use 'api_key' parameter instead of 'apikey' for FRED API"""
        if params is None:
            params = {}

        # FRED uses 'api_key' not 'apikey' - temporarily store API key and set to None
        original_api_key = self.config.api_key
        self.config.api_key = None

        # Add FRED-specific API key parameter
        if original_api_key:
            params = {**params, "api_key": original_api_key}

        try:
            # Call parent method without API key auto-addition
            result = super()._make_request_with_retry(endpoint, params)
        finally:
            # Restore original API key
            self.config.api_key = original_api_key

        return result

    def get_series_data(self, series_id: str, start_date: str = None, end_date: str = None) -> dict[str, Any]:
        """
        Get time series data for a specific FRED series

        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'FEDFUNDS')
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Dictionary containing time series data
        """
        params = {"series_id": series_id, "file_type": "json"}

        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date

        result = self._make_request_with_retry("series/observations", params)

        # Add metadata
        result.update(
            {
                "series_id": series_id,
                "start_date": start_date,
                "end_date": end_date,
                "source": "fred",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_series_info(self, series_id: str) -> dict[str, Any]:
        """
        Get series information and metadata

        Args:
            series_id: FRED series ID

        Returns:
            Dictionary containing series metadata
        """
        params = {"series_id": series_id, "file_type": "json"}

        result = self._make_request_with_retry("series", params)

        # Add metadata
        result.update(
            {
                "series_id": series_id,
                "source": "fred",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def search_series(self, search_text: str, limit: int = 10) -> dict[str, Any]:
        """
        Search for FRED series by text

        Args:
            search_text: Search term
            limit: Maximum number of results

        Returns:
            Dictionary containing search results
        """
        params = {"search_text": search_text, "limit": limit, "file_type": "json"}

        result = self._make_request_with_retry("series/search", params)

        # Add metadata
        result.update(
            {
                "search_text": search_text,
                "limit": limit,
                "source": "fred",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_economic_indicator(self, series_id: str, date_range: str = "1y") -> dict[str, Any]:
        """
        Get economic indicator data for specified period with analysis

        Args:
            series_id: FRED series ID
            date_range: Time period ('1y', '2y', '5y', '10y', 'ytd')

        Returns:
            Dictionary containing indicator data with analysis
        """
        # Calculate date range (use a few days ago as end date to avoid future date issues)
        end_date = datetime.now() - timedelta(days=3)

        if date_range == "1y":
            start_date = end_date - timedelta(days=365)
        elif date_range == "2y":
            start_date = end_date - timedelta(days=730)
        elif date_range == "5y":
            start_date = end_date - timedelta(days=1825)
        elif date_range == "10y":
            start_date = end_date - timedelta(days=3650)
        elif date_range == "ytd":
            start_date = end_date.replace(month=1, day=1)
        else:
            start_date = end_date - timedelta(days=365)

        # Get series data and info
        data = self.get_series_data(series_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        series_info = self.get_series_info(series_id)

        # Process observations for analysis
        observations = data.get("observations", [])
        valid_observations = [obs for obs in observations if obs.get("value") and obs["value"] != "."]

        # Calculate statistics
        statistics = {"trend": "no_data"}
        if valid_observations:
            values = [float(obs["value"]) for obs in valid_observations]
            latest_value = values[-1] if values else None
            avg_value = sum(values) / len(values) if values else None
            min_value = min(values) if values else None
            max_value = max(values) if values else None

            # Calculate trend (simple linear regression)
            if len(values) >= 2:
                x = list(range(len(values)))
                n = len(values)
                sum_x = sum(x)
                sum_y = sum(values)
                sum_xy = sum(x[i] * values[i] for i in range(n))
                sum_x2 = sum(x[i] ** 2 for i in range(n))

                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            else:
                trend = "insufficient_data"

            statistics = {
                "latest_value": str(latest_value),
                "average_value": str(round(avg_value, 2)) if avg_value else None,
                "min_value": str(min_value),
                "max_value": str(max_value),
                "trend": trend,
                "observations_count": str(len(valid_observations)),
            }

        return {
            "series_id": series_id,
            "series_title": series_info.get("seriess", [{}])[0].get("title", "Unknown"),
            "date_range": date_range,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "statistics": statistics,
            "recent_observations": valid_observations[-10:],  # Last 10 observations
            "series_metadata": series_info,
            "data_source": "FRED",
            "timestamp": datetime.now().isoformat(),
        }

    def get_sector_indicators(self, sector: str, indicators: str = "") -> dict[str, Any]:
        """
        Get economic indicators relevant to a specific sector

        Args:
            sector: Sector name (technology, healthcare, financial, energy, retail, housing)
            indicators: Comma-separated list of specific indicators (optional)

        Returns:
            Dictionary containing sector-specific indicators
        """
        # Define sector-specific indicators
        sector_indicators = {
            "technology": {
                "GDP": "GDP",
                "Industrial_Production": "INDPRO",
                "Consumer_Confidence": "UMCSENT",
                "Federal_Funds_Rate": "FEDFUNDS",
            },
            "healthcare": {
                "GDP": "GDP",
                "Personal_Income": "PI",
                "Healthcare_Spending": "HLTHSCPCHP",
                "Unemployment_Rate": "UNRATE",
            },
            "financial": {
                "Federal_Funds_Rate": "FEDFUNDS",
                "10_Year_Treasury": "GS10",
                "Credit_Spreads": "BAMLC0A0CM",
                "Bank_Credit": "TOTLL",
            },
            "energy": {
                "Oil_Price": "DCOILWTICO",
                "Natural_Gas_Price": "DHHNGSP",
                "Industrial_Production": "INDPRO",
                "CPI_Energy": "CPIENGSL",
            },
            "retail": {
                "Retail_Sales": "RSAFS",
                "Consumer_Confidence": "UMCSENT",
                "Personal_Income": "PI",
                "Unemployment_Rate": "UNRATE",
            },
            "housing": {
                "Housing_Starts": "HOUST",
                "30_Year_Mortgage": "MORTGAGE30US",
                "New_Home_Sales": "HSN1F",
                "Case_Shiller_Index": "CSUSHPISA",
            },
        }

        sector_lower = sector.lower()
        if sector_lower not in sector_indicators:
            available_sectors = list(sector_indicators.keys())
            raise ValidationError(f"Sector '{sector}' not supported. Available: {available_sectors}")

        # Get indicator data
        sector_data = {}
        target_indicators = sector_indicators[sector_lower]

        # Filter indicators if specified
        if indicators:
            requested_indicators = [i.strip() for i in indicators.split(",")]
            target_indicators = {k: v for k, v in target_indicators.items() if k in requested_indicators}

        for indicator_name, series_id in target_indicators.items():
            try:
                # Get last 1 year of data
                data = self.get_series_data(
                    series_id,
                    (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                )

                observations = data.get("observations", [])
                valid_observations = [obs for obs in observations if obs.get("value") and obs["value"] != "."]

                if valid_observations:
                    latest_value = float(valid_observations[-1]["value"])
                    sector_data[indicator_name] = {
                        "series_id": series_id,
                        "latest_value": latest_value,
                        "latest_date": valid_observations[-1]["date"],
                        "observations_count": len(valid_observations),
                    }

            except Exception as e:
                sector_data[indicator_name] = {"series_id": series_id, "error": str(e)}

        return {
            "sector": sector,
            "indicators": sector_data,
            "total_indicators": len(target_indicators),
            "successful_indicators": len([v for v in sector_data.values() if "error" not in v]),
            "data_source": "FRED",
            "timestamp": datetime.now().isoformat(),
        }

    def get_inflation_data(self, period: str = "1y") -> dict[str, Any]:
        """
        Get comprehensive inflation data from multiple measures

        Args:
            period: Time period ('1y', '2y', '5y')

        Returns:
            Dictionary containing inflation analysis
        """
        # Get multiple inflation measures
        inflation_series = self.indicators["inflation"]

        # Calculate date range
        end_date = datetime.now()

        if period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)

        inflation_data = {}

        for measure_name, series_id in inflation_series.items():
            try:
                data = self.get_series_data(
                    series_id,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )

                observations = data.get("observations", [])
                valid_observations = [obs for obs in observations if obs.get("value") and obs["value"] != "."]

                if valid_observations:
                    values = [float(obs["value"]) for obs in valid_observations]
                    latest_value = values[-1]

                    # Calculate year-over-year change
                    yoy_change = None
                    if len(values) >= 12:  # Monthly data
                        yoy_change = ((latest_value - values[-13]) / values[-13]) * 100

                    inflation_data[measure_name] = {
                        "series_id": series_id,
                        "latest_value": latest_value,
                        "latest_date": valid_observations[-1]["date"],
                        "yoy_change": round(yoy_change, 2) if yoy_change else None,
                        "recent_trend": (
                            "increasing" if len(values) >= 3 and values[-1] > values[-3] else "decreasing"
                        ),
                    }

            except Exception as e:
                inflation_data[measure_name] = {"error": str(e)}

        return {
            "period": period,
            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "inflation_measures": inflation_data,
            "analysis": {
                "primary_measure": "CPI",
                "federal_reserve_target": 2.0,
                "interpretation": "Federal Reserve targets 2% inflation rate",
            },
            "data_source": "FRED",
            "timestamp": datetime.now().isoformat(),
        }

    def get_interest_rates(self, rate_type: str = "all", period: str = "1y") -> dict[str, Any]:
        """
        Get interest rate data

        Args:
            rate_type: Type of rate ('all' or specific rate name)
            period: Time period

        Returns:
            Dictionary containing interest rate data
        """
        # Get interest rate series
        rate_series = self.indicators["interest_rates"]

        # Filter by rate type if specified
        if rate_type != "all" and rate_type in rate_series:
            rate_series = {rate_type: rate_series[rate_type]}
        elif rate_type != "all":
            available_types = list(rate_series.keys())
            raise ValidationError(f"Rate type '{rate_type}' not supported. Available: {available_types}")

        # Calculate date range
        end_date = datetime.now()

        if period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)

        rates_data = {}

        for rate_name, series_id in rate_series.items():
            try:
                data = self.get_series_data(
                    series_id,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )

                observations = data.get("observations", [])
                valid_observations = [obs for obs in observations if obs.get("value") and obs["value"] != "."]

                if valid_observations:
                    values = [float(obs["value"]) for obs in valid_observations]
                    latest_value = values[-1]

                    # Calculate change from start of period
                    period_change = latest_value - values[0] if len(values) > 1 else 0

                    rates_data[rate_name] = {
                        "series_id": series_id,
                        "latest_value": latest_value,
                        "latest_date": valid_observations[-1]["date"],
                        "period_change": round(period_change, 2),
                        "min_in_period": min(values),
                        "max_in_period": max(values),
                    }

            except Exception as e:
                rates_data[rate_name] = {"error": str(e)}

        return {
            "rate_type": rate_type,
            "period": period,
            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "interest_rates": rates_data,
            "analysis": {
                "yield_curve": "Check spread between short and long-term rates",
                "federal_reserve_policy": "Monitor Federal Funds Rate for monetary policy changes",
            },
            "data_source": "FRED",
            "timestamp": datetime.now().isoformat(),
        }

    def get_available_indicators(self) -> dict[str, Any]:
        """Get available economic indicators organized by category"""
        return {
            "available_indicators": self.indicators,
            "total_categories": len(self.indicators),
            "supported_periods": ["1y", "2y", "5y", "10y", "ytd"],
            "data_source": "Federal Reserve Economic Data (FRED)",
            "timestamp": datetime.now().isoformat(),
        }

    def health_check(self) -> dict[str, Any]:
        """Service health check"""
        try:
            # Test API connectivity with Federal Funds Rate
            result = self.get_economic_indicator("FEDFUNDS", "1y")

            return {
                "service_name": self.config.name,
                "status": "healthy",
                "api_connection": "ok",
                "test_series": "FEDFUNDS",
                "test_result": "success" if result else "failed",
                "configuration": {
                    "cache_enabled": self.config.cache.enabled,
                    "rate_limit_enabled": self.config.rate_limit.enabled,
                    "requests_per_minute": self.config.rate_limit.requests_per_minute,
                    "cache_ttl_seconds": self.config.cache.ttl_seconds,
                },
                "capabilities": [
                    "Economic indicators (GDP, inflation, unemployment)",
                    "Interest rates and monetary policy data",
                    "Sector-specific economic metrics",
                    "Historical time series data",
                    "Real-time economic indicators",
                ],
                "data_categories": len(self.indicators),
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


def create_fred_economic_service(env: str = "dev") -> FREDEconomicService:
    """
    Factory function to create FRED Economic service with configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured FRED Economic service instance
    """
    # Ensure environment variables are loaded first
    try:
        # Add scripts directory to path for load_env import
        import sys

        scripts_dir = Path(__file__).parent.parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from load_env import ensure_env_loaded

        ensure_env_loaded()
    except ImportError:
        pass  # Continue if load_env not available

    # Use absolute path to config directory
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_loader = ConfigLoader(str(config_dir), auto_load_env=True)
    service_config = config_loader.get_service_config("fred", env)

    # Convert to ServiceConfig format
    from base_financial_service import CacheConfig, RateLimitConfig, ServiceConfig

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

    return FREDEconomicService(config)
