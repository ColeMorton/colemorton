"""
CoinGecko Service

Production-grade CoinGecko cryptocurrency data integration with:
- Real-time prices for 17,000+ cryptocurrencies
- Market data across 1,000+ exchanges and 200+ blockchain networks
- Historical data and trending cryptocurrencies
- Global market statistics and search capabilities
- Optional API key for Pro tier (free tier: 30 calls/min)
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


class CoinGeckoService(BaseFinancialService):
    """
    CoinGecko service extending BaseFinancialService

    Provides access to CoinGecko's comprehensive cryptocurrency data including:
    - Real-time prices for 17,000+ cryptocurrencies
    - Detailed coin information and market data
    - Historical price charts and trending coins
    - Global market statistics and search capabilities
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Optional API key (free tier doesn't require one)
        if config.api_key:
            self.config.headers["X-Cg-Pro-Api-Key"] = config.api_key

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate CoinGecko response data"""

        # CoinGecko typically returns lists or dictionaries
        if isinstance(data, list):
            # For list responses, add timestamp to metadata if possible
            if data:  # Check if list is not empty
                return data
            raise DataNotFoundError(f"No data found for {endpoint}")

        # Handle dictionary responses
        if isinstance(data, dict):
            # Check for API errors
            if "error" in data or "status" in data:
                error_msg = data.get("error", data.get("status", "Unknown error"))
                raise DataNotFoundError(f"CoinGecko API error: {error_msg}")

            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()

        return data

    def get_price(self, coin_ids: str, vs_currencies: str = "usd") -> dict[str, Any]:
        """
        Get current price of cryptocurrencies

        Args:
            coin_ids: Comma-separated list of coin IDs (e.g., 'bitcoin,ethereum')
            vs_currencies: Comma-separated list of currencies (default: 'usd')

        Returns:
            Dictionary containing current prices and market data
        """
        params = {
            "ids": coin_ids.strip().lower(),
            "vs_currencies": vs_currencies,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        }

        result = self._make_request_with_retry("simple/price", params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "coin_ids": coin_ids,
                    "vs_currencies": vs_currencies,
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_coin_data(self, coin_id: str, localization: bool = False) -> dict[str, Any]:
        """
        Get detailed information about a specific cryptocurrency

        Args:
            coin_id: Coin ID (e.g., 'bitcoin', 'ethereum')
            localization: Include localized data

        Returns:
            Dictionary containing detailed coin information
        """
        params = {
            "localization": str(localization).lower(),
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "true",
        }

        result = self._make_request_with_retry(f"coins/{coin_id.strip().lower()}", params)

        # Extract key information and simplify
        if isinstance(result, dict):
            simplified_data = {
                "id": result.get("id"),
                "symbol": result.get("symbol"),
                "name": result.get("name"),
                "current_price": result.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": result.get("market_data", {}).get("market_cap", {}).get("usd"),
                "market_cap_rank": result.get("market_data", {}).get("market_cap_rank"),
                "total_volume": result.get("market_data", {}).get("total_volume", {}).get("usd"),
                "high_24h": result.get("market_data", {}).get("high_24h", {}).get("usd"),
                "low_24h": result.get("market_data", {}).get("low_24h", {}).get("usd"),
                "price_change_24h": result.get("market_data", {}).get("price_change_24h"),
                "price_change_percentage_24h": result.get("market_data", {}).get("price_change_percentage_24h"),
                "circulating_supply": result.get("market_data", {}).get("circulating_supply"),
                "total_supply": result.get("market_data", {}).get("total_supply"),
                "max_supply": result.get("market_data", {}).get("max_supply"),
                "description": result.get("description", {}).get("en", ""),
                "homepage": result.get("links", {}).get("homepage", []),
                "blockchain_site": result.get("links", {}).get("blockchain_site", []),
                "coin_id": coin_id,
                "source": "coingecko",
                "timestamp": datetime.now().isoformat(),
            }
            return simplified_data

        return result

    def get_market_data(
        self,
        vs_currency: str = "usd",
        order: str = "market_cap_desc",
        per_page: int = 100,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Get market data for cryptocurrencies

        Args:
            vs_currency: Currency for prices (default: 'usd')
            order: Sorting order
            per_page: Number of results per page (max 250)
            page: Page number

        Returns:
            List containing market data for cryptocurrencies
        """
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": min(per_page, 250),  # API limit
            "page": page,
            "sparkline": "false",
        }

        result = self._make_request_with_retry("coins/markets", params)

        # Add metadata to each item
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    item.update(
                        {
                            "vs_currency": vs_currency,
                            "source": "coingecko",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

        return result

    def get_historical_data(self, coin_id: str, vs_currency: str = "usd", days: int = 30) -> dict[str, Any]:
        """
        Get historical market data

        Args:
            coin_id: Coin ID
            vs_currency: Currency for prices
            days: Number of days of historical data

        Returns:
            Dictionary containing historical price data
        """
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily" if days > 1 else "hourly",
        }

        result = self._make_request_with_retry(f"coins/{coin_id.strip().lower()}/market_chart", params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "coin_id": coin_id,
                    "vs_currency": vs_currency,
                    "days": days,
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def search_coins(self, query: str) -> dict[str, Any]:
        """
        Search for cryptocurrencies by name or symbol

        Args:
            query: Search query (coin name or symbol)

        Returns:
            Dictionary containing search results
        """
        params = {"query": query.strip()}

        result = self._make_request_with_retry("search", params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "query": query,
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_trending(self) -> dict[str, Any]:
        """
        Get trending cryptocurrencies

        Returns:
            Dictionary containing trending cryptocurrencies
        """
        result = self._make_request_with_retry("search/trending")

        # Add metadata
        if isinstance(result, dict):
            result.update({"source": "coingecko", "timestamp": datetime.now().isoformat()})

        return result

    def get_global_data(self) -> dict[str, Any]:
        """
        Get global cryptocurrency market statistics

        Returns:
            Dictionary containing global market data
        """
        result = self._make_request_with_retry("global")

        # Add metadata
        if isinstance(result, dict):
            result.update({"source": "coingecko", "timestamp": datetime.now().isoformat()})

        return result

    def get_bitcoin_sentiment(self) -> dict[str, Any]:
        """
        Get Bitcoin price and sentiment for market analysis

        Returns:
            Dictionary containing Bitcoin market sentiment data
        """
        try:
            # Get Bitcoin price data
            bitcoin_details = self.get_coin_data("bitcoin")

            # Calculate sentiment indicators
            sentiment_data = {
                "bitcoin_price": bitcoin_details.get("current_price", 0),
                "price_change_24h": bitcoin_details.get("price_change_24h", 0),
                "price_change_percentage_24h": bitcoin_details.get("price_change_percentage_24h", 0),
                "market_cap": bitcoin_details.get("market_cap", 0),
                "market_cap_rank": bitcoin_details.get("market_cap_rank", 1),
                "volume_24h": bitcoin_details.get("total_volume", 0),
                "market_sentiment": "neutral",  # Default
            }

            # Determine market sentiment based on price change
            price_change_pct = sentiment_data.get("price_change_percentage_24h", 0)
            if price_change_pct > 5:
                sentiment_data["market_sentiment"] = "very_bullish"
            elif price_change_pct > 2:
                sentiment_data["market_sentiment"] = "bullish"
            elif price_change_pct > 0:
                sentiment_data["market_sentiment"] = "slightly_bullish"
            elif price_change_pct > -2:
                sentiment_data["market_sentiment"] = "neutral"
            elif price_change_pct > -5:
                sentiment_data["market_sentiment"] = "bearish"
            else:
                sentiment_data["market_sentiment"] = "very_bearish"

            sentiment_data.update(
                {
                    "analysis_timestamp": datetime.now().isoformat(),
                    "source": "coingecko",
                    "methodology": "bitcoin_price_change_analysis",
                }
            )

            return sentiment_data

        except Exception as e:
            return {
                "error": str(e),
                "bitcoin_price": 0,
                "market_sentiment": "unknown",
                "source": "coingecko",
                "timestamp": datetime.now().isoformat(),
            }

    def health_check(self) -> dict[str, Any]:
        """Service health check"""
        try:
            # Test API connectivity with global data endpoint
            result = self.get_global_data()

            return {
                "service_name": self.config.name,
                "status": "healthy",
                "api_connection": "ok",
                "test_endpoint": "global",
                "test_result": "success" if result else "failed",
                "configuration": {
                    "cache_enabled": self.config.cache.enabled,
                    "rate_limit_enabled": self.config.rate_limit.enabled,
                    "requests_per_minute": self.config.rate_limit.requests_per_minute,
                    "cache_ttl_seconds": self.config.cache.ttl_seconds,
                    "api_key_configured": bool(self.config.api_key),
                },
                "capabilities": [
                    "Real-time prices for 17,000+ cryptocurrencies",
                    "Market data across 1,000+ exchanges",
                    "Historical data and trending cryptocurrencies",
                    "Global market statistics and search capabilities",
                    "Bitcoin sentiment analysis for broader market context",
                ],
                "coverage": {
                    "cryptocurrencies": "17,000+",
                    "exchanges": "1,000+",
                    "blockchain_networks": "200+",
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


def create_coingecko_service(env: str = "dev") -> CoinGeckoService:
    """
    Factory function to create CoinGecko service with configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured CoinGecko service instance
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
    service_config = config_loader.get_service_config("coingecko", env)

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

    return CoinGeckoService(config)
