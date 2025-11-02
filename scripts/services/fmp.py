"""
Financial Modeling Prep Service

Production-grade Financial Modeling Prep (FMP) integration with:
- 70,000+ stocks with 30 years historical data
- Real-time stock prices and financial statements
- Insider trading data and earnings transcripts
- Company profiles and financial ratios
- Economic calendar and market news
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
    ValidationError,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config_loader import ConfigLoader


class FMPService(BaseFinancialService):
    """
    Financial Modeling Prep service extending BaseFinancialService

    Provides access to FMP's comprehensive financial data including:
    - Real-time stock quotes and company profiles
    - Financial statements (income, balance sheet, cash flow)
    - Key metrics and financial ratios
    - Historical price data
    - Insider trading information
    - Stock screening capabilities
    - Market movers and earnings calendar
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        if not config.api_key:
            raise ValidationError("FMP API key is required")

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate FMP response data"""

        # FMP often returns lists for many endpoints
        if isinstance(data, list):
            # Check if it's an empty list (no data)
            if not data:
                raise DataNotFoundError(f"No data found for {endpoint}")
            # Add timestamp to first item if list
            if isinstance(data[0], dict) and "timestamp" not in data[0]:
                data[0]["timestamp"] = datetime.now().isoformat()
            return data

        # Handle dictionary responses
        if isinstance(data, dict):
            # Check for API errors
            if "Error Message" in data:
                raise DataNotFoundError(data["Error Message"])

            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()

        return data

    def get_stock_quote(self, symbol: str) -> list[dict[str, Any]]:
        """
        Get real-time stock quote with comprehensive market data

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            List containing real-time stock quote data
        """
        result = self._make_request_with_retry(f"quote/{symbol.upper()}")

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update({"source": "fmp", "timestamp": datetime.now().isoformat()})

        return result

    def get_company_profile(self, symbol: str) -> list[dict[str, Any]]:
        """
        Get comprehensive company profile and business information

        Args:
            symbol: Stock symbol

        Returns:
            List containing company profile data
        """
        result = self._make_request_with_retry(f"profile/{symbol.upper()}")

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update({"source": "fmp", "timestamp": datetime.now().isoformat()})

        return result

    def get_financial_statements(
        self,
        symbol: str,
        statement_type: str = "income-statement",
        period: str = "annual",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get detailed financial statements with historical data

        Args:
            symbol: Stock symbol
            statement_type: Type of statement ('income-statement', 'balance-sheet-statement', 'cash-flow-statement')
            period: Period type ('annual', 'quarter')
            limit: Number of periods to retrieve

        Returns:
            List containing financial statement data
        """
        valid_statements = [
            "income-statement",
            "balance-sheet-statement",
            "cash-flow-statement",
        ]
        if statement_type not in valid_statements:
            raise ValidationError(f"statement_type must be one of: {valid_statements}")

        params = {"period": period, "limit": limit}
        result = self._make_request_with_retry(f"{statement_type}/{symbol.upper()}", params)

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update(
                    {
                        "statement_type": statement_type,
                        "period": period,
                        "source": "fmp",
                    }
                )

        return result

    def get_key_metrics(self, symbol: str, period: str = "annual", limit: int = 10) -> list[dict[str, Any]]:
        """
        Get key financial metrics and ratios

        Args:
            symbol: Stock symbol
            period: Period type ('annual', 'quarter')
            limit: Number of periods to retrieve

        Returns:
            List containing key financial metrics
        """
        params = {"period": period, "limit": limit}
        result = self._make_request_with_retry(f"key-metrics/{symbol.upper()}", params)

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update({"period": period, "source": "fmp"})

        return result

    def get_financial_ratios(self, symbol: str, period: str = "annual", limit: int = 10) -> list[dict[str, Any]]:
        """
        Get financial ratios

        Args:
            symbol: Stock symbol
            period: Period type ('annual', 'quarter')
            limit: Number of periods to retrieve

        Returns:
            List containing financial ratios
        """
        params = {"period": period, "limit": limit}
        result = self._make_request_with_retry(f"ratios/{symbol.upper()}", params)

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update({"period": period, "source": "fmp"})

        return result

    def get_historical_prices(self, symbol: str, from_date: str = None, to_date: str = None) -> dict[str, Any]:
        """
        Get historical stock price data

        Args:
            symbol: Stock symbol
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Dictionary containing historical price data
        """
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        result = self._make_request_with_retry(f"historical-price-full/{symbol.upper()}", params)

        # Add metadata
        if isinstance(result, dict):
            result.update(
                {
                    "from_date": from_date,
                    "to_date": to_date,
                    "source": "fmp",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_insider_trading(self, symbol: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get insider trading data for a company

        Args:
            symbol: Stock symbol
            limit: Maximum number of insider trades to retrieve

        Returns:
            List containing insider trading data
        """
        params = {"symbol": symbol.upper(), "limit": limit}
        result = self._make_request_with_retry("insider-trading", params)

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update({"symbol": symbol.upper(), "source": "fmp"})

        return result

    def get_stock_screener(
        self,
        market_cap_more_than: int = None,
        market_cap_lower_than: int = None,
        beta_more_than: float = None,
        beta_lower_than: float = None,
        volume_more_than: int = None,
        volume_lower_than: int = None,
        dividend_more_than: float = None,
        dividend_lower_than: float = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Screen stocks based on financial criteria

        Args:
            market_cap_more_than: Minimum market capitalization
            market_cap_lower_than: Maximum market capitalization
            beta_more_than: Minimum beta value
            beta_lower_than: Maximum beta value
            volume_more_than: Minimum trading volume
            volume_lower_than: Maximum trading volume
            dividend_more_than: Minimum dividend yield
            dividend_lower_than: Maximum dividend yield
            limit: Maximum number of results

        Returns:
            List containing stock screening results
        """
        params = {"limit": limit}

        if market_cap_more_than:
            params["marketCapMoreThan"] = market_cap_more_than
        if market_cap_lower_than:
            params["marketCapLowerThan"] = market_cap_lower_than
        if beta_more_than:
            params["betaMoreThan"] = beta_more_than
        if beta_lower_than:
            params["betaLowerThan"] = beta_lower_than
        if volume_more_than:
            params["volumeMoreThan"] = volume_more_than
        if volume_lower_than:
            params["volumeLowerThan"] = volume_lower_than
        if dividend_more_than:
            params["dividendMoreThan"] = dividend_more_than
        if dividend_lower_than:
            params["dividendLowerThan"] = dividend_lower_than

        result = self._make_request_with_retry("stock-screener", params)

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item["source"] = "fmp"

        return result

    def get_market_gainers(self) -> list[dict[str, Any]]:
        """
        Get market gainers

        Returns:
            List containing market gainers
        """
        result = self._make_request_with_retry("gainers")

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update(
                    {
                        "mover_type": "gainers",
                        "source": "fmp",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return result

    def get_market_losers(self) -> list[dict[str, Any]]:
        """
        Get market losers

        Returns:
            List containing market losers
        """
        result = self._make_request_with_retry("losers")

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update(
                    {
                        "mover_type": "losers",
                        "source": "fmp",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return result

    def get_market_most_active(self) -> list[dict[str, Any]]:
        """
        Get most active stocks

        Returns:
            List containing most active stocks
        """
        result = self._make_request_with_retry("actives")

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update(
                    {
                        "mover_type": "actives",
                        "source": "fmp",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return result

    def get_earnings_calendar(self, from_date: str = None, to_date: str = None) -> list[dict[str, Any]]:
        """
        Get earnings calendar for upcoming earnings releases

        Args:
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List containing earnings calendar data
        """
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        result = self._make_request_with_retry("earning_calendar", params)

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update({"from_date": from_date, "to_date": to_date, "source": "fmp"})

        return result

    def get_economic_calendar(self, from_date: str = None, to_date: str = None) -> list[dict[str, Any]]:
        """
        Get economic calendar

        Args:
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List containing economic calendar data
        """
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        result = self._make_request_with_retry("economic_calendar", params)

        # Add metadata
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                item.update({"from_date": from_date, "to_date": to_date, "source": "fmp"})

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
                    "70,000+ stocks with 30 years historical data",
                    "Real-time stock prices and financial statements",
                    "Insider trading data and earnings transcripts",
                    "Company profiles and financial ratios",
                    "Economic calendar and market news",
                    "Stock screening and market movers",
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


def create_fmp_service(env: str = "dev") -> FMPService:
    """
    Factory function to create FMP service with configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured FMP service instance
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
    service_config = config_loader.get_service_config("fmp", env)

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
            store_financials=True,
            store_fundamentals=True,
            store_news_sentiment=True,
            auto_detect_data_type=True,
        ),
        headers=service_config.headers,
    )

    return FMPService(config)
