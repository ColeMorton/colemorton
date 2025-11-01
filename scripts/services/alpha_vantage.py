"""
Alpha Vantage Service

Production-grade Alpha Vantage data integration with:
- Real-time stock quotes with comprehensive market data
- 60+ technical indicators
- AI-powered news sentiment analysis
- Global market coverage (stocks, forex, cryptocurrencies)
- Economic indicators and market news
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    RateLimitError,
    ServiceConfig,
    ValidationError,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config_loader import ConfigLoader


class AlphaVantageService(BaseFinancialService):
    """
    Alpha Vantage service extending BaseFinancialService

    Provides access to Alpha Vantage's comprehensive financial data including:
    - Real-time stock quotes
    - Technical indicators
    - News sentiment analysis
    - Economic indicators
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Use ConfigManager for enhanced API key management
        try:
            from utils.config_manager import ConfigManager

            config_manager = ConfigManager()
            # Get API key with validation - mark as required
            api_key = config_manager.get_api_key("ALPHA_VANTAGE_API_KEY", required=True)
            if api_key and api_key != "not_required":
                config.api_key = api_key
            else:
                raise ValidationError("Alpha Vantage API key is required but not configured")
        except ImportError:
            # Fallback to original validation if ConfigManager not available
            if not config.api_key:
                raise ValidationError("Alpha Vantage API key is required")

    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """Validate Alpha Vantage response data"""

        if not isinstance(data, dict):
            raise ValidationError(f"Invalid response format for {endpoint}")

        # Check for API errors
        if "Error Message" in data:
            raise DataNotFoundError(data["Error Message"])
        if "Note" in data and "API call frequency" in data["Note"]:
            raise RateLimitError(data["Note"])
        if "Information" in data and "Thank you for using Alpha Vantage" in data["Information"]:
            raise RateLimitError("API call frequency exceeded")

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        return data

    def get_stock_quote(self, symbol: str) -> dict[str, Any]:
        """
        Get real-time stock quote with comprehensive market data

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Dictionary containing real-time stock quote
        """
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol.upper()}

        result = self._make_request_with_retry("", params)

        # Transform Alpha Vantage response format
        if "Global Quote" in result:
            quote = result["Global Quote"]
            standardized_result = {
                "symbol": symbol.upper(),
                "current_price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "volume": int(quote.get("06. volume", 0)),
                "previous_close": float(quote.get("08. previous close", 0)),
                "open_price": float(quote.get("02. open", 0)),
                "high_price": float(quote.get("03. high", 0)),
                "low_price": float(quote.get("04. low", 0)),
                "latest_trading_day": quote.get("07. latest trading day"),
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
            return standardized_result
        raise DataNotFoundError("Invalid response from Alpha Vantage")

    def get_daily_data(self, symbol: str, outputsize: str = "compact") -> dict[str, Any]:
        """
        Get daily stock price data

        Args:
            symbol: Stock symbol
            outputsize: Data size ('compact' for last 100 days, 'full' for all available)

        Returns:
            Dictionary containing daily stock data
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper(),
            "outputsize": outputsize,
        }

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "symbol": symbol.upper(),
                "outputsize": outputsize,
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_intraday_data(self, symbol: str, interval: str = "5min") -> dict[str, Any]:
        """
        Get intraday stock data

        Args:
            symbol: Stock symbol
            interval: Time interval ('1min', '5min', '15min', '30min', '60min')

        Returns:
            Dictionary containing intraday stock data
        """
        valid_intervals = ["1min", "5min", "15min", "30min", "60min"]
        if interval not in valid_intervals:
            raise ValidationError(f"Invalid interval. Must be one of: {valid_intervals}")

        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol.upper(),
            "interval": interval,
        }

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "symbol": symbol.upper(),
                "interval": interval,
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_technical_indicator(
        self,
        symbol: str,
        function: str,
        interval: str = "daily",
        time_period: int = 20,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Get technical indicator data

        Args:
            symbol: Stock symbol
            function: Technical indicator function (e.g., 'SMA', 'RSI', 'MACD')
            interval: Time interval
            time_period: Number of periods for calculation
            **kwargs: Additional parameters for specific indicators

        Returns:
            Dictionary containing technical indicator data
        """
        params = {
            "function": function.upper(),
            "symbol": symbol.upper(),
            "interval": interval,
            "time_period": time_period,
        }
        params.update(kwargs)

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "symbol": symbol.upper(),
                "function": function.upper(),
                "interval": interval,
                "time_period": time_period,
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_company_overview(self, symbol: str) -> dict[str, Any]:
        """
        Get company overview and fundamental data

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing company overview
        """
        params = {"function": "OVERVIEW", "symbol": symbol.upper()}

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "symbol": symbol.upper(),
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_financial_statements(self, symbol: str, statement_type: str = "income") -> dict[str, Any]:
        """
        Get company financial statements

        Args:
            symbol: Stock symbol
            statement_type: Type of statement ('income', 'balance', 'cash_flow')

        Returns:
            Dictionary containing financial statement data
        """
        function_map = {
            "income": "INCOME_STATEMENT",
            "balance": "BALANCE_SHEET",
            "cash_flow": "CASH_FLOW",
        }

        if statement_type not in function_map:
            raise ValidationError(f"Invalid statement type. Must be one of: {list(function_map.keys())}")

        params = {"function": function_map[statement_type], "symbol": symbol.upper()}

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "symbol": symbol.upper(),
                "statement_type": statement_type,
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_earnings(self, symbol: str) -> dict[str, Any]:
        """
        Get company earnings data

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing earnings data
        """
        params = {"function": "EARNINGS", "symbol": symbol.upper()}

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "symbol": symbol.upper(),
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_news_sentiment(self, tickers: str = None, topics: str = None, limit: int = 50) -> dict[str, Any]:
        """
        Get AI-powered news sentiment analysis

        Args:
            tickers: Comma-separated list of stock tickers (optional)
            topics: Comma-separated list of topics (optional)
            limit: Maximum number of news articles to return

        Returns:
            Dictionary containing news sentiment data
        """
        params = {"function": "NEWS_SENTIMENT", "limit": limit}

        if tickers:
            params["tickers"] = tickers
        if topics:
            params["topics"] = topics

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "tickers": tickers,
                "topics": topics,
                "limit": limit,
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_economic_indicator(self, function: str, interval: str = "monthly") -> dict[str, Any]:
        """
        Get economic indicator data

        Args:
            function: Economic indicator function (e.g., 'GDP', 'INFLATION', 'UNEMPLOYMENT')
            interval: Data interval ('monthly', 'quarterly', 'annual')

        Returns:
            Dictionary containing economic indicator data
        """
        params = {"function": function.upper(), "interval": interval}

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "function": function.upper(),
                "interval": interval,
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_forex_rate(self, from_currency: str, to_currency: str) -> dict[str, Any]:
        """
        Get foreign exchange rate

        Args:
            from_currency: Source currency code (e.g., 'USD', 'EUR')
            to_currency: Target currency code (e.g., 'EUR', 'GBP')

        Returns:
            Dictionary containing forex rate data
        """
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
        }

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "from_currency": from_currency.upper(),
                "to_currency": to_currency.upper(),
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_crypto_daily(self, symbol: str, market: str = "USD") -> dict[str, Any]:
        """
        Get daily cryptocurrency data

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            market: Market currency (default: 'USD')

        Returns:
            Dictionary containing cryptocurrency data
        """
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol.upper(),
            "market": market.upper(),
        }

        result = self._make_request_with_retry("", params)

        # Add metadata
        result.update(
            {
                "symbol": symbol.upper(),
                "market": market.upper(),
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def health_check(self) -> dict[str, Any]:
        """Service health check"""
        try:
            # Test API connectivity with a simple quote request
            result = self.get_stock_quote("AAPL")

            return {
                "service_name": self.config.name,
                "status": "healthy",
                "api_connection": "ok",
                "test_symbol": "AAPL",
                "test_result": "success" if result else "failed",
                "configuration": {
                    "cache_enabled": self.config.cache.enabled,
                    "rate_limit_enabled": self.config.rate_limit.enabled,
                    "requests_per_minute": self.config.rate_limit.requests_per_minute,
                    "cache_ttl_seconds": self.config.cache.ttl_seconds,
                },
                "capabilities": [
                    "Real-time stock quotes",
                    "60+ technical indicators",
                    "AI-powered news sentiment",
                    "Global market coverage",
                    "Economic indicators",
                    "Forex rates",
                    "Cryptocurrency data",
                ],
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


def create_alpha_vantage_service(env: str = "dev") -> AlphaVantageService:
    """
    Factory function to create Alpha Vantage service with configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured Alpha Vantage service instance
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
    service_config = config_loader.get_service_config("alpha_vantage", env)

    # Convert to ServiceConfig format
    from .base_financial_service import (
        CacheConfig,
        HistoricalStorageConfig,
        RateLimitConfig,
        ServiceConfig,
    )

    config = ServiceConfig(
        name=service_config.name,
        base_url=service_config.base_url,
        api_key=service_config.api_key,
        timeout_seconds=service_config.timeout_seconds,
        max_retries=service_config.max_retries,
        cache=CacheConfig(**service_config.cache),
        rate_limit=RateLimitConfig(**service_config.rate_limit),
        historical_storage=HistoricalStorageConfig(
            enabled=True,
            store_stock_prices=True,
            store_financials=False,  # Alpha Vantage doesn't provide detailed financials
            store_fundamentals=True,
            store_news_sentiment=True,
            auto_detect_data_type=True,
        ),
        headers=service_config.headers,
    )

    return AlphaVantageService(config)
