"""
CoinMetrics Service

Production-grade CoinMetrics institutional-grade cryptocurrency data integration with:
- Network data and on-chain metrics for Bitcoin and other cryptocurrencies
- Market data with institutional-grade quality standards
- Historical data with comprehensive coverage since genesis blocks
- Academic-rigor data validation and methodology transparency
- Free tier available with generous limits for Bitcoin analysis
"""

import sys
from datetime import datetime, timedelta
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


class CoinMetricsService(BaseFinancialService):
    """
    CoinMetrics service extending BaseFinancialService

    Provides access to CoinMetrics' institutional-grade cryptocurrency data including:
    - Network data and on-chain metrics with academic rigor
    - Market data with institutional-grade quality standards
    - Historical data with comprehensive coverage
    - Bitcoin cycle analysis metrics (MVRV, NUPL, etc.)
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # CoinMetrics free tier available, API key optional but recommended
        if not self.config.base_url:
            self.config.base_url = "https://community-api.coinmetrics.io/v4"

        # Add API key to headers if provided
        if config.api_key:
            self.config.headers["api_key"] = config.api_key

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate CoinMetrics response data"""

        if not data:
            raise DataNotFoundError(f"No data returned from CoinMetrics {endpoint}")

        # CoinMetrics returns structured data with 'data' field
        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return data

    def get_supported_assets(self) -> list[dict[str, Any]]:
        """Get list of supported assets"""
        endpoint = "/catalog/assets"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "supported assets")

    def get_available_metrics(self, asset: str = "btc") -> list[dict[str, Any]]:
        """Get available metrics for an asset"""
        endpoint = "/catalog/asset-metrics"
        params = {"assets": asset.lower()}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"metrics for {asset}")

    def get_network_data(
        self,
        asset: str = "btc",
        metrics: str = "AdrActCnt,BlkCnt,TxCnt,TxTfrValUSD",
        start_date: str = "2024-01-01",
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get network data for specified asset and metrics"""

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        endpoint = "/timeseries/asset-metrics"
        params = {
            "assets": asset.lower(),
            "metrics": metrics,
            "start_time": start_date,
            "end_time": end_date,
            "frequency": "1d",
        }

        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"network data for {asset}")

    def get_market_data(
        self,
        asset: str = "btc",
        start_date: str = "2024-01-01",
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get market data for specified asset"""

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        endpoint = "/timeseries/market-data"
        params = {
            "assets": asset.lower(),
            "metrics": "PriceUSD,VolTrusted24hUSD,CapMrktCurUSD",
            "start_time": start_date,
            "end_time": end_date,
            "frequency": "1d",
        }

        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"market data for {asset}")

    def get_bitcoin_cycle_metrics(
        self, start_date: str = "2024-01-01", end_date: str | None = None
    ) -> list[dict[str, Any]]:
        """Get Bitcoin cycle-specific metrics using Community API available metrics"""

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Bitcoin cycle analysis metrics (Community API compatible)
        cycle_metrics = [
            "PriceUSD",  # Bitcoin Price in USD
            "CapMrktCurUSD",  # Market Capitalization
            "TxCnt",  # Transaction Count
            "AdrActCnt",  # Active Addresses
            "TxTfrValUSD",  # Transfer Value in USD
            "BlkCnt",  # Block Count
        ]

        endpoint = "/timeseries/asset-metrics"
        params = {
            "assets": "btc",
            "metrics": ",".join(cycle_metrics),
            "start_time": start_date,
            "end_time": end_date,
            "frequency": "1d",
        }

        try:
            data = self._make_request_with_retry(endpoint, params=params)
            return self._validate_response(data, "Bitcoin cycle metrics")
        except Exception:
            # If the full request fails, try with basic metrics only
            basic_metrics = ["PriceUSD", "CapMrktCurUSD", "TxCnt"]
            params["metrics"] = ",".join(basic_metrics)

            self.logger.warning(f"Full metrics request failed, trying with basic metrics: {basic_metrics}")
            data = self._make_request_with_retry(endpoint, params=params)
            return self._validate_response(data, "Bitcoin basic cycle metrics")

    def get_supply_data(
        self,
        asset: str = "btc",
        start_date: str = "2024-01-01",
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get supply-related data for specified asset"""

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        supply_metrics = [
            "SplyCur",  # Current Supply
            "SplyAct1d",  # Active Supply 1d
            "SplyAct7d",  # Active Supply 7d
            "SplyAct30d",  # Active Supply 30d
            "SplyAct90d",  # Active Supply 90d
            "SplyAct1yr",  # Active Supply 1yr
        ]

        endpoint = "/timeseries/asset-metrics"
        params = {
            "assets": asset.lower(),
            "metrics": ",".join(supply_metrics),
            "start_time": start_date,
            "end_time": end_date,
            "frequency": "1d",
        }

        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"supply data for {asset}")

    def get_mining_data(
        self,
        asset: str = "btc",
        start_date: str = "2024-01-01",
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get mining-related data (hash rate, difficulty, etc.)"""

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Bitcoin-specific mining metrics
        if asset.lower() == "btc":
            mining_metrics = [
                "HashRate",  # Hash Rate
                "DiffMean",  # Mining Difficulty
                "BlkCnt",  # Block Count
                "BlkSizeByte",  # Block Size
                "RevUSD",  # Revenue USD
                "FeeMeanUSD",  # Mean Fee USD
            ]
        else:
            mining_metrics = ["HashRate", "DiffMean", "BlkCnt"]

        endpoint = "/timeseries/asset-metrics"
        params = {
            "assets": asset.lower(),
            "metrics": ",".join(mining_metrics),
            "start_time": start_date,
            "end_time": end_date,
            "frequency": "1d",
        }

        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"mining data for {asset}")

    def get_exchange_data(self, asset: str = "btc") -> list[dict[str, Any]]:
        """Get exchange-related data and metrics"""
        endpoint = "/catalog/exchanges"
        params = {"assets": asset.lower()}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"exchange data for {asset}")

    def get_institutional_data(self, asset: str = "btc") -> dict[str, Any]:
        """Get institutional holdings and flow data"""
        # Note: Institutional data might be limited in free tier
        # This is a placeholder for institutional metrics

        institutional_metrics = [
            "SplyAct1yr",  # Long-term holdings proxy
            "TxTfrValUSD",  # Transfer value (institutional flows)
            "TxCnt",  # Transaction count
        ]

        # Get last 30 days of data
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        endpoint = "/timeseries/asset-metrics"
        params = {
            "assets": asset.lower(),
            "metrics": ",".join(institutional_metrics),
            "start_time": start_date,
            "end_time": end_date,
            "frequency": "1d",
        }

        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"institutional data for {asset}")

    def get_realized_cap_data(
        self,
        asset: str = "btc",
        start_date: str = "2024-01-01",
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get realized capitalization data for Bitcoin cycle analysis"""

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Realized cap and related metrics for cycle analysis (MVRV removed - use web search)
        realized_cap_metrics = [
            "CapRealUSD",  # Realized Cap
            "CapMrktCurUSD",  # Market Cap
            "PriceUSD",  # Price USD
        ]

        endpoint = "/timeseries/asset-metrics"
        params = {
            "assets": asset.lower(),
            "metrics": ",".join(realized_cap_metrics),
            "start_time": start_date,
            "end_time": end_date,
            "frequency": "1d",
        }

        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"realized cap data for {asset}")

    def get_enhanced_bitcoin_cycle_metrics(
        self, start_date: str = "2024-01-01", end_date: str | None = None
    ) -> list[dict[str, Any]]:
        """Get enhanced Bitcoin cycle metrics (MVRV and NUPL acquired via web search)"""

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Note: MVRV Z-Score and NUPL must be acquired via web search only
        # Return basic cycle metrics from API, web search will supplement MVRV/NUPL data
        return self.get_bitcoin_cycle_metrics(start_date, end_date)


def create_coinmetrics_service(env: str = "dev") -> CoinMetricsService:
    """
    Factory function to create CoinMetricsService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured CoinMetricsService instance
    """
    try:
        # Load configuration
        config_loader = ConfigLoader()

        # Try to get API key from config (optional for free tier)
        api_key = None
        try:
            api_key = config_loader.get_api_key("coinmetrics", env)
        except Exception:
            pass  # API key is optional for free tier

        # Create service config
        service_config = ServiceConfig(
            name="coinmetrics",
            api_key=api_key,
            base_url="https://community-api.coinmetrics.io/v4",
            timeout_seconds=30,
            max_retries=3,
        )

        return CoinMetricsService(service_config)

    except Exception:
        # Fallback configuration for free tier
        service_config = ServiceConfig(
            name="coinmetrics",
            api_key=None,  # Free tier
            base_url="https://community-api.coinmetrics.io/v4",
            timeout_seconds=30,
            max_retries=3,
        )

        return CoinMetricsService(service_config)
