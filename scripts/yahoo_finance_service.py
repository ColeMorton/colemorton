#!/usr/bin/env python3
"""
Yahoo Finance Service - Production-Grade Financial Data Integration

Unified service class for reliable Yahoo Finance data access with comprehensive
error handling, validation, caching, and rate limiting.

Replaces fragmented integration approaches with single source of truth.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yfinance as yf


# Import trading session manager for session-aware caching
try:
    import sys

    sys.path.insert(0, str(Path(__file__).parent / "utils"))
    from trading_session_manager import TradingSessionManager

    TRADING_SESSION_AVAILABLE = True
except ImportError:
    TradingSessionManager = None
    TRADING_SESSION_AVAILABLE = False


class YahooFinanceError(Exception):
    """Base exception for Yahoo Finance service errors"""


class ValidationError(YahooFinanceError):
    """Raised when input validation fails"""


class RateLimitError(YahooFinanceError):
    """Raised when rate limit is exceeded"""


class DataNotFoundError(YahooFinanceError):
    """Raised when requested data is not available"""


class APITimeoutError(YahooFinanceError):
    """Raised when API request times out"""


class FileBasedCache:
    """Simple file-based cache with TTL support"""

    def __init__(
        self,
        cache_dir: str = "/tmp/yahoo_finance_cache",
        ttl: int = 900,
        use_trading_session_ttl: bool = True,  # nosec B108
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl  # Fallback TTL in seconds
        self.use_trading_session_ttl = use_trading_session_ttl

        # Initialize trading session manager if available
        if self.use_trading_session_ttl and TRADING_SESSION_AVAILABLE:
            self.trading_session_manager = TradingSessionManager()
        else:
            self.trading_session_manager = None

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path for given key"""
        hash_key = hashlib.md5(key.encode()).hexdigest()  # nosec B324
        return self.cache_dir / f"{hash_key}.json"

    def _get_effective_ttl(self, key: str) -> int:
        """Get effective TTL based on key content and trading session"""
        if self.trading_session_manager and self.use_trading_session_ttl:
            # Check if this is market data based on key content
            is_market_data = any(term in key.lower() for term in ["historical", "quote", "price", "stock_info"])

            if is_market_data:
                try:
                    session_ttl = self.trading_session_manager.get_cache_ttl_seconds()
                    return session_ttl
                except Exception:
                    # Fallback to static TTL on error
                    pass

        return self.ttl

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached data if not expired using dynamic TTL"""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                cached_data = json.load(f)

            # Check if cache is expired using effective TTL
            cached_time = datetime.fromisoformat(cached_data["timestamp"])
            effective_ttl = self._get_effective_ttl(key)

            if datetime.now() - cached_time > timedelta(seconds=effective_ttl):
                cache_path.unlink()  # Remove expired cache
                return None

            return cached_data["data"]  # type: ignore[no-any-return]

        except (json.JSONDecodeError, KeyError, ValueError):
            # Remove corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Store data in cache with timestamp"""
        cache_path = self._get_cache_path(key)

        cached_data = {"timestamp": datetime.now().isoformat(), "data": data}

        try:
            with open(cache_path, "w") as f:
                json.dump(cached_data, f, default=str)
        except Exception as e:
            # Log cache write failure but don't raise
            logging.warning(f"Failed to write cache: {e}")


class RateLimiter:
    """Simple rate limiter to prevent API abuse"""

    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests: list[float] = []

    def can_make_request(self) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]

        return len(self.requests) < self.requests_per_minute

    def record_request(self) -> None:
        """Record a new request"""
        self.requests.append(time.time())

    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded"""
        if not self.can_make_request():
            # Calculate wait time until oldest request expires
            oldest_request = min(self.requests)
            wait_time = 60 - (time.time() - oldest_request) + 1
            if wait_time > 0:
                time.sleep(wait_time)


class YahooFinanceService:
    """Production-grade Yahoo Finance integration service"""

    VALID_PERIODS = [
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "ytd",
        "max",
    ]

    VALID_INTERVALS = [
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "90m",
        "1h",
        "1d",
        "5d",
        "1wk",
        "1mo",
        "3mo",
    ]

    def __init__(self, cache_ttl: int = 900, rate_limit: int = 10):
        """
        Initialize Yahoo Finance service

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 15 minutes)
            rate_limit: Maximum requests per minute (default: 10)
        """
        self.cache = FileBasedCache(ttl=cache_ttl)
        self.rate_limiter = RateLimiter(requests_per_minute=rate_limit)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging with correlation IDs"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize stock symbol"""
        if not symbol:
            raise ValidationError("Symbol cannot be empty")

        # Normalize to uppercase and strip whitespace
        symbol = symbol.strip().upper()

        # Basic validation - alphanumeric plus common symbol characters
        if not all(c.isalnum() or c in ".-" for c in symbol):
            raise ValidationError(f"Invalid symbol format: {symbol}")

        if len(symbol) > 10:  # Reasonable limit for stock symbols
            raise ValidationError(f"Symbol too long: {symbol}")

        return symbol

    def _validate_period(self, period: str) -> str:
        """Validate period parameter"""
        if period not in self.VALID_PERIODS:
            raise ValidationError(f"Invalid period '{period}'. Valid periods: {', '.join(self.VALID_PERIODS)}")
        return period

    def _validate_interval(self, interval: str) -> str:
        """Validate interval parameter"""
        if interval not in self.VALID_INTERVALS:
            raise ValidationError(f"Invalid interval '{interval}'. Valid intervals: {', '.join(self.VALID_INTERVALS)}")
        return interval

    def _make_request_with_retry(self, request_func: Any, *args: Any, max_retries: int = 3, **kwargs: Any) -> Any:
        """Execute request with exponential backoff retry logic"""
        correlation_id = hashlib.md5(  # nosec B324
            f"{request_func.__name__}{str(args)}{str(kwargs)}".encode()
        ).hexdigest()[:8]

        for attempt in range(max_retries + 1):
            try:
                # Rate limiting
                self.rate_limiter.wait_if_needed()
                self.rate_limiter.record_request()

                self.logger.info(f"Making request (attempt {attempt + 1}/{max_retries + 1}) - ID: {correlation_id}")

                result = request_func(*args, **kwargs)

                self.logger.info(f"Request successful - ID: {correlation_id}")
                return result

            except Exception as e:
                wait_time = 2**attempt  # Exponential backoff: 1, 2, 4 seconds

                if attempt < max_retries:
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}/"
                        f"{max_retries + 1}), retrying in {wait_time}s - "
                        f"ID: {correlation_id}, Error: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(
                        f"Request failed after {max_retries + 1} attempts - ID: {correlation_id}, Error: {str(e)}"
                    )

                    # Classify and raise appropriate exception
                    if "timeout" in str(e).lower():
                        raise APITimeoutError(f"Request timed out after {max_retries + 1} attempts: {str(e)}")
                    if "not found" in str(e).lower() or "invalid" in str(e).lower():
                        raise DataNotFoundError(f"Data not available: {str(e)}")
                    raise YahooFinanceError(f"API request failed: {str(e)}")

    def get_stock_info(self, symbol: str) -> dict[str, Any]:
        """
        Get comprehensive stock information with validation and caching

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Dictionary containing stock information

        Raises:
            ValidationError: If symbol format is invalid
            DataNotFoundError: If stock data is not available
            YahooFinanceError: For other API-related errors
        """
        symbol = self._validate_symbol(symbol)
        cache_key = f"stock_info_{symbol}"

        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            self.logger.info(f"Cache hit for stock info: {symbol}")
            return cached_data

        def _fetch_stock_info() -> dict[str, Any]:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or "symbol" not in info:
                raise DataNotFoundError(f"No data available for symbol: {symbol}")

            return {
                "symbol": symbol,
                "name": info.get("longName", "N/A"),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "volume": info.get("volume"),
                "avg_volume": info.get("averageVolume"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "recommendation": info.get("recommendationKey"),
                "target_price": info.get("targetMeanPrice"),
                "timestamp": datetime.now().isoformat(),
            }

        try:
            result = self._make_request_with_retry(_fetch_stock_info)

            # Cache successful result
            self.cache.set(cache_key, result)

            return result  # type: ignore[no-any-return]

        except (DataNotFoundError, ValidationError):
            # Don't retry these errors
            raise
        except Exception as e:
            raise YahooFinanceError(f"Failed to fetch stock info for {symbol}: {str(e)}")

    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> dict[str, Any]:
        """
        Get historical price data with period and interval validation

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y',
                   '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m',
                     '1h', '1d', '5d', '1wk', '1mo', '3mo')

        Returns:
            Dictionary containing historical price data

        Raises:
            ValidationError: If symbol, period, or interval format is invalid
            DataNotFoundError: If historical data is not available
            YahooFinanceError: For other API-related errors
        """
        symbol = self._validate_symbol(symbol)
        period = self._validate_period(period)
        interval = self._validate_interval(interval)
        cache_key = f"historical_{symbol}_{period}_{interval}"

        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            self.logger.info(f"Cache hit for historical data: {symbol} ({period}, {interval})")
            return cached_data

        def _fetch_historical_data() -> dict[str, Any]:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                raise DataNotFoundError(
                    f"No historical data available for symbol: {symbol} (period: {period}, interval: {interval})"
                )

            # Reset index to make Date a column, then convert to records
            hist_reset = hist.reset_index()

            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": hist_reset.to_dict(orient="records"),
                "timestamp": datetime.now().isoformat(),
            }

        try:
            result = self._make_request_with_retry(_fetch_historical_data)

            # Cache successful result
            self.cache.set(cache_key, result)

            return result  # type: ignore[no-any-return]

        except (DataNotFoundError, ValidationError):
            # Don't retry these errors
            raise
        except Exception as e:
            raise YahooFinanceError(f"Failed to fetch historical data for {symbol}: {str(e)}")

    def get_financials(self, symbol: str) -> dict[str, Any]:
        """
        Get financial statements with data quality validation

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Dictionary containing financial statements

        Raises:
            ValidationError: If symbol format is invalid
            DataNotFoundError: If financial data is not available
            YahooFinanceError: For other API-related errors
        """
        symbol = self._validate_symbol(symbol)
        cache_key = f"financials_{symbol}"

        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            self.logger.info(f"Cache hit for financials: {symbol}")
            return cached_data

        def _fetch_financials() -> dict[str, Any]:
            ticker = yf.Ticker(symbol)

            # Validate that we can get basic info first
            info = ticker.info
            if not info or "symbol" not in info:
                raise DataNotFoundError(f"No data available for symbol: {symbol}")

            # Helper function to safely convert DataFrames to JSON-serializable format
            def safe_dataframe_to_dict(df: Any) -> dict[str, Any]:
                if df.empty:
                    return {}
                # Convert DataFrame to dict with string keys for JSON serialization
                df_copy = df.copy()
                df_copy.columns = df_copy.columns.astype(str)
                return df_copy.to_dict()  # type: ignore[no-any-return]

            return {
                "symbol": symbol,
                "income_statement": safe_dataframe_to_dict(ticker.financials),
                "balance_sheet": safe_dataframe_to_dict(ticker.balance_sheet),
                "cash_flow": safe_dataframe_to_dict(ticker.cashflow),
                "timestamp": datetime.now().isoformat(),
            }

        try:
            result = self._make_request_with_retry(_fetch_financials)

            # Cache successful result
            self.cache.set(cache_key, result)

            return result  # type: ignore[no-any-return]

        except (DataNotFoundError, ValidationError):
            # Don't retry these errors
            raise
        except Exception as e:
            raise YahooFinanceError(f"Failed to fetch financials for {symbol}: {str(e)}")

    def health_check(self) -> dict[str, Any]:
        """
        Service health check for monitoring and debugging

        Returns:
            Dictionary containing service health information
        """
        try:
            # Test with a known stable symbol
            self.get_stock_info("AAPL")

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "cache_directory": str(self.cache.cache_dir),
                "rate_limit": self.rate_limiter.requests_per_minute,
                "cache_ttl": self.cache.ttl,
                "test_symbol": "AAPL",
                "test_result": "success",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "error_type": type(e).__name__,
            }


def main() -> None:
    """Command line interface for the service (backward compatibility)"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python yahoo_finance_service.py <command> [symbol] [options]")
        print("Commands: info, history, financials, health")
        print("Examples:")
        print("  python yahoo_finance_service.py info AAPL")
        print("  python yahoo_finance_service.py history AAPL 1y")
        print("  python yahoo_finance_service.py financials AAPL")
        print("  python yahoo_finance_service.py health")
        sys.exit(1)

    command = sys.argv[1]
    service = YahooFinanceService()

    try:
        if command == "health":
            result = service.health_check()
        elif command == "info":
            if len(sys.argv) < 3:
                result = {"error": "Symbol required for info command"}
            else:
                symbol = sys.argv[2]
                result = service.get_stock_info(symbol)
        elif command == "history":
            if len(sys.argv) < 3:
                result = {"error": "Symbol required for history command"}
            else:
                symbol = sys.argv[2]
                period = sys.argv[3] if len(sys.argv) > 3 else "1y"
                result = service.get_historical_data(symbol, period)
        elif command == "financials":
            if len(sys.argv) < 3:
                result = {"error": "Symbol required for financials command"}
            else:
                symbol = sys.argv[2]
                result = service.get_financials(symbol)
        else:
            result = {"error": f"Unknown command: {command}"}

    except YahooFinanceError as e:
        result = {
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        result = {
            "error": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat(),
        }

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
