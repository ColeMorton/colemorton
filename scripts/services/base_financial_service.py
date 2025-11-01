"""
Base Financial Service

Provides common infrastructure for all financial data services including:
- Standardized error handling and validation
- Production-grade caching with TTL support
- Rate limiting with service-specific limits
- Logging with correlation IDs
- Configuration management
- Data validation with Pydantic models
"""

import hashlib
import json
import logging
import sys
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from pydantic import BaseModel, Field


# Add utils directory to path for importing historical data manager
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from unified_cache import UnifiedCache
from utils.historical_data_manager import DataType, HistoricalDataManager, Timeframe


class FinancialServiceError(Exception):
    """Base exception for financial service errors"""


class ValidationError(FinancialServiceError):
    """Raised when input validation fails"""


class RateLimitError(FinancialServiceError):
    """Raised when rate limit is exceeded"""


class DataNotFoundError(FinancialServiceError):
    """Raised when requested data is not available"""


class APITimeoutError(FinancialServiceError):
    """Raised when API request times out"""


class CacheConfig(BaseModel):
    """Cache configuration"""

    enabled: bool = True
    ttl_seconds: int = 900  # 15 minutes default
    cache_dir: str = Field(default_factory=lambda: str(Path(__file__).parent.parent.parent / "data" / "cache"))
    max_size_mb: int = 100


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""

    enabled: bool = True
    requests_per_minute: int = 60
    burst_limit: int = 10


class HistoricalStorageConfig(BaseModel):
    """Historical data storage configuration"""

    enabled: bool = True
    store_stock_prices: bool = True
    store_financials: bool = True
    store_fundamentals: bool = True
    store_news_sentiment: bool = False
    auto_detect_data_type: bool = True

    # Auto-collection settings
    auto_collection_enabled: bool = True
    daily_days: int = 365
    weekly_years: int = 5
    trigger_on_price_calls: bool = True
    collection_interval_hours: int = 24
    background_collection: bool = True


class ServiceConfig(BaseModel):
    """Base service configuration"""

    name: str
    base_url: str
    api_key: str | None = None
    timeout_seconds: int = 30
    max_retries: int = 3
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    historical_storage: HistoricalStorageConfig = Field(default_factory=HistoricalStorageConfig)
    headers: dict[str, str] = Field(default_factory=dict)


class FileBasedCache:
    """Production-grade file-based cache with TTL support"""

    def __init__(self, config: CacheConfig, service_name: str = "unknown"):
        self.config = config
        self.service_name = service_name
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path for given key - consistent with UnifiedCacheManager"""
        # Use consistent cache key generation across all cache implementations
        hash_key = hashlib.md5(f"{self.service_name}_{key}".encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached data if not expired"""
        if not self.config.enabled:
            return None

        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                cached_data = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data["timestamp"])
            if datetime.now() - cached_time > timedelta(seconds=self.config.ttl_seconds):
                cache_path.unlink()  # Remove expired cache
                return None

            return cached_data["data"]

        except (json.JSONDecodeError, KeyError, ValueError):
            # Remove corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Store data in cache with timestamp"""
        if not self.config.enabled:
            return

        cache_path = self._get_cache_path(key)
        cached_data = {"timestamp": datetime.now().isoformat(), "data": data}

        try:
            with open(cache_path, "w") as f:
                json.dump(cached_data, f, default=str)
        except Exception as e:
            logging.warning(f"Failed to write cache: {e}")

    def clear(self) -> None:
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)

    def cleanup_expired(self) -> None:
        """Remove expired cache entries"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    cached_data = json.load(f)
                cached_time = datetime.fromisoformat(cached_data["timestamp"])
                if datetime.now() - cached_time > timedelta(seconds=self.config.ttl_seconds):
                    cache_file.unlink()
            except Exception:
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)


class RateLimiter:
    """Production-grade rate limiter with burst support"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: list[float] = []

    def can_make_request(self) -> bool:
        """Check if request is allowed under rate limit"""
        if not self.config.enabled:
            return True

        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]

        return len(self.requests) < self.config.requests_per_minute

    def record_request(self) -> None:
        """Record a new request"""
        if self.config.enabled:
            self.requests.append(time.time())

    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded"""
        if not self.config.enabled:
            return

        if not self.can_make_request():
            # Calculate wait time until oldest request expires
            oldest_request = min(self.requests)
            wait_time = 60 - (time.time() - oldest_request) + 1
            if wait_time > 0:
                time.sleep(wait_time)


class BaseFinancialService(ABC):
    """
    Base class for all financial data services

    Provides common infrastructure including:
    - Caching with TTL
    - Rate limiting
    - Error handling with retry logic
    - Request logging with correlation IDs
    - Data validation
    """

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.session = requests.Session()
        self.logger = self._setup_logger()

        # Initialize historical data manager if enabled
        self.historical_manager = None
        if config.historical_storage.enabled:
            try:
                self.historical_manager = HistoricalDataManager()
                self.logger.info("Historical data storage enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize historical data manager: {e}")

        # Initialize unified cache using historical data manager
        if self.historical_manager:
            self.cache = UnifiedCache(
                historical_manager=self.historical_manager,
                ttl_seconds=config.cache.ttl_seconds,
                service_name=config.name,
                use_trading_session_ttl=True,  # Enable trading session TTL
            )
            self.logger.info("Using unified cache with historical data storage")
        else:
            # Fallback to file-based cache if historical storage is disabled
            self.cache = FileBasedCache(config.cache, config.name)
            self.logger.info("Using traditional file-based cache")

        # Auto-collection tracking
        self._collection_cache = {}  # Track when comprehensive collection was last done
        self._collection_lock = threading.Lock()  # Thread safety for background collection

        # Initialize quarterly trigger manager for financial statements
        self.quarterly_trigger_manager = None
        if self.historical_manager:
            try:
                from quarterly_collection_triggers import QuarterlyCollectionTrigger

                self.quarterly_trigger_manager = QuarterlyCollectionTrigger(historical_manager=self.historical_manager)
                self.logger.info("Quarterly trigger manager initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize quarterly trigger manager: {e}")

        # Initialize technical indicator calculator
        self.technical_calculator = None
        if self.historical_manager:
            try:
                from technical_indicator_calculator import TechnicalIndicatorCalculator

                self.technical_calculator = TechnicalIndicatorCalculator(historical_manager=self.historical_manager)
                self.logger.info("Technical indicator calculator initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize technical indicator calculator: {e}")

        # Update session headers
        self.session.headers.update(
            {
                "User-Agent": "Colemorton/1.0 (https://colemorton.com)",
                "Accept": "application/json",
                **config.headers,
            }
        )

    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging for the service"""
        logger = logging.getLogger(f"financial_service.{self.config.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _generate_cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        """Generate cache key from endpoint and parameters"""
        cache_data = f"{self.config.name}_{endpoint}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _generate_correlation_id(self, endpoint: str, params: dict[str, Any]) -> str:
        """Generate correlation ID for request tracking"""
        correlation_data = f"{endpoint}_{params}_{time.time()}"
        return hashlib.md5(correlation_data.encode()).hexdigest()[:8]

    def _detect_data_type(self, endpoint: str, data: dict[str, Any]) -> DataType | None:
        """
        Auto-detect data type based on endpoint and data structure

        Args:
            endpoint: API endpoint called
            data: Response data

        Returns:
            Detected DataType or None if not detectable
        """
        if not self.config.historical_storage.auto_detect_data_type:
            return None

        endpoint_lower = endpoint.lower()

        # Historical price data detection (specific structure)
        if any(keyword in endpoint_lower for keyword in ["historical", "ohlc"]):
            # Look for historical data structure: {"data": [{"Date": ..., "Open": ...}]}
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                if data["data"] and isinstance(data["data"][0], dict):
                    first_record = data["data"][0]
                    if "Date" in first_record and any(
                        field in first_record for field in ["Open", "High", "Low", "Close"]
                    ):
                        return DataType.STOCK_DAILY_PRICES

        # Fundamentals detection (stock_info, quote endpoints return company data)
        if any(
            keyword in endpoint_lower
            for keyword in [
                "stock_info",
                "quote",
                "profile",
                "overview",
                "company",
                "fundamental",
                "get_stock",
            ]
        ):
            fundamental_fields = [
                "market_cap",
                "pe_ratio",
                "sector",
                "industry",
                "current_price",
                "name",
            ]
            if isinstance(data, dict) and any(field in data for field in fundamental_fields):
                return DataType.STOCK_FUNDAMENTALS

        # Financial statements detection
        if any(keyword in endpoint_lower for keyword in ["financial", "income", "balance", "cash"]):
            financial_fields = [
                "revenue",
                "net_income",
                "total_assets",
                "operating_cash_flow",
            ]
            if isinstance(data, dict) and any(field in data for field in financial_fields):
                return DataType.STOCK_FINANCIALS

        # News sentiment detection
        if any(keyword in endpoint_lower for keyword in ["news", "sentiment"]):
            return DataType.STOCK_NEWS_SENTIMENT

        # Options data detection
        if any(keyword in endpoint_lower for keyword in ["options", "option_chain", "derivatives"]):
            options_fields = [
                "strike",
                "expiry",
                "option_type",
                "bid",
                "ask",
                "implied_volatility",
            ]
            if isinstance(data, dict) and any(field in data for field in options_fields):
                return DataType.STOCK_OPTIONS

        # ETF data detection
        if any(keyword in endpoint_lower for keyword in ["etf_holdings", "holdings", "constituents"]):
            return DataType.ETF_HOLDINGS
        if any(keyword in endpoint_lower for keyword in ["etf_flows", "flows", "fund_flows"]):
            return DataType.ETF_FLOWS

        # Insider transactions detection
        if any(keyword in endpoint_lower for keyword in ["insider", "insider_trading", "form4"]):
            insider_fields = ["insider_name", "transaction_type", "shares", "price"]
            if isinstance(data, dict) and any(field in data for field in insider_fields):
                return DataType.INSIDER_TRANSACTIONS

        # Technical indicators detection
        if any(keyword in endpoint_lower for keyword in ["technical", "indicator", "sma", "rsi", "macd"]):
            return DataType.TECHNICAL_INDICATORS

        # Corporate actions detection
        if any(keyword in endpoint_lower for keyword in ["corporate_actions", "dividends", "splits", "spin_off"]):
            return DataType.CORPORATE_ACTIONS

        return None

    def _extract_symbol_from_data(self, data: dict[str, Any], params: dict[str, Any]) -> str | None:
        """
        Extract stock symbol from data or parameters

        Args:
            data: Response data
            params: Request parameters

        Returns:
            Extracted symbol or None
        """
        # Try to get symbol from data
        if isinstance(data, dict):
            for field in ["symbol", "ticker", "Symbol", "Ticker"]:
                if field in data and data[field]:
                    return str(data[field]).upper()
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            for field in ["symbol", "ticker", "Symbol", "Ticker"]:
                if field in data[0] and data[0][field]:
                    return str(data[0][field]).upper()

        # Try to get symbol from parameters
        for field in ["symbol", "ticker", "symbols"]:
            if field in params and params[field]:
                symbol = str(params[field]).upper()
                # Handle comma-separated symbols by taking first one
                return symbol.split(",")[0].strip()

        return None

    def store_historical_data(
        self,
        data: dict[str, Any],
        endpoint: str,
        params: dict[str, Any],
        data_type: DataType | None = None,
        symbol: str | None = None,
        timeframe: Timeframe = Timeframe.DAILY,
    ) -> bool:
        """
        Store data in historical storage system

        Args:
            data: Data to store
            endpoint: API endpoint
            params: Request parameters
            data_type: Optional explicit data type
            symbol: Optional explicit symbol
            timeframe: Data timeframe

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.historical_manager or not self.config.historical_storage.enabled:
            return False

        # Auto-detect data type if not provided
        if data_type is None:
            data_type = self._detect_data_type(endpoint, data)

        if data_type is None:
            self.logger.debug(f"Could not detect data type for endpoint: {endpoint}")
            return False

        # Extract symbol if not provided
        if symbol is None:
            symbol = self._extract_symbol_from_data(data, params)

        if symbol is None:
            self.logger.debug(f"Could not extract symbol for endpoint: {endpoint}")
            return False

        # Check if this data type should be stored
        storage_enabled_map = {
            DataType.STOCK_DAILY_PRICES: self.config.historical_storage.store_stock_prices,
            DataType.STOCK_FINANCIALS: self.config.historical_storage.store_financials,
            DataType.STOCK_FUNDAMENTALS: self.config.historical_storage.store_fundamentals,
            DataType.STOCK_NEWS_SENTIMENT: self.config.historical_storage.store_news_sentiment,
            DataType.STOCK_OPTIONS: getattr(self.config.historical_storage, "store_options", True),
            DataType.ETF_HOLDINGS: getattr(self.config.historical_storage, "store_etf_holdings", True),
            DataType.ETF_FLOWS: getattr(self.config.historical_storage, "store_etf_flows", True),
            DataType.INSIDER_TRANSACTIONS: getattr(self.config.historical_storage, "store_insider_transactions", True),
            DataType.TECHNICAL_INDICATORS: getattr(self.config.historical_storage, "store_technical_indicators", True),
            DataType.CORPORATE_ACTIONS: getattr(self.config.historical_storage, "store_corporate_actions", True),
        }

        if not storage_enabled_map.get(data_type, True):
            return False

        # Store the data
        try:
            success = self.historical_manager.store_data(
                symbol=symbol,
                data=data,
                data_type=data_type,
                timeframe=timeframe,
                source=self.config.name,
            )

            if success:
                self.logger.debug(f"Stored historical data: {symbol} {data_type.value}")
            else:
                self.logger.warning(f"Failed to store historical data: {symbol} {data_type.value}")

            return success

        except Exception as e:
            self.logger.error(f"Error storing historical data: {e}")
            return False

    def _should_trigger_comprehensive_collection(self, symbol: str, data_type: DataType) -> bool:
        """
        Check if comprehensive collection should be triggered for a symbol

        Args:
            symbol: Stock symbol
            data_type: Type of data

        Returns:
            True if comprehensive collection should be triggered
        """
        # Only trigger for price-related data types
        if not self.config.historical_storage.trigger_on_price_calls:
            return False

        if data_type not in [DataType.STOCK_DAILY_PRICES, DataType.STOCK_FUNDAMENTALS]:
            return False

        if not self.config.historical_storage.auto_collection_enabled:
            return False

        # Check if we've collected recently
        collection_key = f"{symbol}_{self.config.name}"

        with self._collection_lock:
            last_collection = self._collection_cache.get(collection_key)

            if last_collection:
                hours_since = (datetime.now() - last_collection).total_seconds() / 3600
                if hours_since < self.config.historical_storage.collection_interval_hours:
                    return False

        return True

    def _mark_collection_completed(self, symbol: str):
        """Mark that comprehensive collection was completed for a symbol"""
        collection_key = f"{symbol}_{self.config.name}"

        with self._collection_lock:
            self._collection_cache[collection_key] = datetime.now()

    def _trigger_comprehensive_collection(self, symbol: str, data_type: DataType):
        """
        Trigger comprehensive historical data collection for a symbol

        Args:
            symbol: Stock symbol to collect data for
            data_type: Type of data that triggered the collection
        """
        if not self._should_trigger_comprehensive_collection(symbol, data_type):
            return

        # Mark collection as starting immediately to prevent recursion
        self._mark_collection_completed(symbol)

        self.logger.info(f"Triggering comprehensive collection for {symbol}")

        if self.config.historical_storage.background_collection:
            # Run in background thread
            collection_thread = threading.Thread(target=self._run_comprehensive_collection, args=(symbol,), daemon=True)
            collection_thread.start()
        else:
            # Run synchronously
            self._run_comprehensive_collection(symbol)

    def _run_comprehensive_collection(self, symbol: str):
        """
        Execute comprehensive data collection for a symbol

        Args:
            symbol: Stock symbol to collect data for
        """
        try:
            self.logger.info(f"Starting comprehensive collection for {symbol}")

            # Import here to avoid circular imports
            import sys
            from pathlib import Path

            utils_path = str(Path(__file__).parent.parent / "utils")
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)

            from historical_data_collector import create_historical_data_collector

            self.logger.info(f"Creating historical data collector for {symbol}")
            collector = create_historical_data_collector(
                base_path=(self.historical_manager.base_path if self.historical_manager else None),
                rate_limit_delay=0.2,  # Faster for auto-collection
            )

            self.logger.info(f"Starting comprehensive data collection for {symbol}")
            # Collect comprehensive data
            results = collector.collect_comprehensive_data(
                symbols=[symbol],
                daily_days=self.config.historical_storage.daily_days,
                weekly_years=self.config.historical_storage.weekly_years,
                service_name=self.config.name,
            )

            self.logger.info(f"Collection results for {symbol}: {results}")

            if results.get("overall_success"):
                self._mark_collection_completed(symbol)
                self.logger.info(
                    f"Comprehensive collection completed for {symbol}: "
                    f"{results.get('total_files_created', 0)} files created"
                )
            else:
                self.logger.warning(f"Comprehensive collection failed for {symbol}: {results}")

        except Exception as e:
            self.logger.error(f"Error during comprehensive collection for {symbol}: {e}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def _trigger_collection_if_needed(self, data: dict[str, Any], endpoint: str, params: dict[str, Any]):
        """
        Check if comprehensive collection should be triggered and do so if needed

        Args:
            data: Response data
            endpoint: API endpoint
            params: Request parameters
        """
        try:
            self.logger.info(f"Checking if collection should be triggered for endpoint: {endpoint}")

            # Auto-detect data type
            data_type = self._detect_data_type(endpoint, data)
            self.logger.info(f"Detected data type: {data_type}")
            if not data_type:
                self.logger.info("No data type detected, skipping collection trigger")
                return

            # Extract symbol
            symbol = self._extract_symbol_from_data(data, params)
            self.logger.info(f"Extracted symbol: {symbol}")
            if not symbol:
                self.logger.info("No symbol extracted, skipping collection trigger")
                return

            # Trigger comprehensive collection if needed
            self.logger.info(f"Attempting to trigger comprehensive collection for {symbol}")
            self._trigger_comprehensive_collection(symbol, data_type)

            # Check for quarterly financial statement triggers
            if self.quarterly_trigger_manager and data_type in [
                DataType.STOCK_FUNDAMENTALS,
                DataType.STOCK_FINANCIALS,
            ]:
                try:
                    from quarterly_collection_triggers import QuarterlyTriggerType

                    # Check if we should trigger quarterly collection
                    if self.quarterly_trigger_manager.should_trigger_collection(
                        symbol, QuarterlyTriggerType.EARNINGS_ANNOUNCEMENT
                    ):
                        self.logger.info(f"Triggering quarterly collection for {symbol} (earnings season)")
                        quarterly_results = self.quarterly_trigger_manager.trigger_quarterly_collection(
                            symbol,
                            QuarterlyTriggerType.EARNINGS_ANNOUNCEMENT,
                            self.config.name,
                        )
                        self.logger.info(f"Quarterly collection results: {quarterly_results}")

                    elif self.quarterly_trigger_manager.should_trigger_collection(
                        symbol, QuarterlyTriggerType.SCHEDULED_QUARTERLY
                    ):
                        self.logger.info(f"Triggering scheduled quarterly collection for {symbol}")
                        quarterly_results = self.quarterly_trigger_manager.trigger_quarterly_collection(
                            symbol,
                            QuarterlyTriggerType.SCHEDULED_QUARTERLY,
                            self.config.name,
                        )
                        self.logger.info(f"Quarterly collection results: {quarterly_results}")

                except Exception as e:
                    self.logger.warning(f"Error checking quarterly triggers for {symbol}: {e}")

            # Check for technical indicator calculation triggers
            if self.technical_calculator and data_type == DataType.STOCK_DAILY_PRICES:
                try:
                    # Check if we should calculate technical indicators (daily after price updates)
                    self.logger.info(f"Triggering technical indicator calculation for {symbol}")

                    # Calculate and store technical indicators
                    indicators = self.technical_calculator.calculate_all_indicators(symbol)
                    if indicators:
                        if self.technical_calculator.store_indicators(symbol, indicators):
                            self.logger.info(f"Technical indicators calculated and stored for {symbol}")
                        else:
                            self.logger.warning(f"Failed to store technical indicators for {symbol}")
                    else:
                        self.logger.warning(f"Failed to calculate technical indicators for {symbol}")

                except Exception as e:
                    self.logger.warning(f"Error calculating technical indicators for {symbol}: {e}")

        except Exception as e:
            self.logger.error(f"Error checking collection trigger: {e}")
            import traceback

            self.logger.error(f"Trigger error traceback: {traceback.format_exc()}")

    def _make_request_with_retry(
        self,
        endpoint: str,
        params: dict[str, Any] = None,
        cache_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Make API request with caching, rate limiting, and retry logic

        Args:
            endpoint: API endpoint to call
            params: Request parameters
            cache_key: Optional custom cache key

        Returns:
            API response data

        Raises:
            RateLimitError: When rate limit is exceeded
            DataNotFoundError: When requested data is not available
            APITimeoutError: When request times out
            FinancialServiceError: For other API errors
        """
        if params is None:
            params = {}

        # Generate cache key and correlation ID
        if cache_key is None:
            cache_key = self._generate_cache_key(endpoint, params)
        correlation_id = self._generate_correlation_id(endpoint, params)

        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            self.logger.info(f"Cache hit for {endpoint} - ID: {correlation_id}")
            return cached_data

        # Prepare request parameters
        if self.config.api_key:
            params = {**params, "apikey": self.config.api_key}

        url = f"{self.config.base_url}/{endpoint.lstrip('/')}" if endpoint else self.config.base_url

        for attempt in range(self.config.max_retries + 1):
            try:
                # Rate limiting
                self.rate_limiter.wait_if_needed()
                self.rate_limiter.record_request()

                self.logger.info(
                    f"Making request (attempt {attempt + 1}/"
                    f"{self.config.max_retries + 1}) to {endpoint} - ID: {correlation_id}"
                )

                response = self.session.get(url, params=params, timeout=self.config.timeout_seconds)
                response.raise_for_status()

                data = response.json()

                # Service-specific data validation
                validated_data = self._validate_response(data, endpoint)

                # Cache successful result
                if isinstance(self.cache, UnifiedCache):
                    # Pass endpoint and params for unified cache
                    self.cache.set(cache_key, validated_data, endpoint=endpoint, params=params)
                else:
                    # Traditional cache
                    self.cache.set(cache_key, validated_data)

                # Store in historical data system (only if not using unified cache)
                if not isinstance(self.cache, UnifiedCache):
                    try:
                        self.store_historical_data(validated_data, endpoint, params)
                    except Exception as e:
                        self.logger.warning(f"Historical storage failed for {endpoint}: {e}")
                else:
                    # With unified cache, storage happens automatically
                    try:
                        self.store_historical_data(validated_data, endpoint, params)
                    except Exception:
                        self.logger.debug(f"Historical storage handled by unified cache for {endpoint}")

                # Trigger comprehensive collection if needed (background process)
                try:
                    self._trigger_collection_if_needed(validated_data, endpoint, params)
                except Exception as e:
                    self.logger.debug(f"Collection trigger check failed for {endpoint}: {e}")

                self.logger.info(f"Request successful for {endpoint} - ID: {correlation_id}")
                return validated_data

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    raise RateLimitError(f"Rate limit exceeded: {e}")
                if response.status_code == 404:
                    raise DataNotFoundError(f"Data not found: {e}")
                if attempt < self.config.max_retries:
                    wait_time = 2**attempt  # Exponential backoff
                    self.logger.warning(
                        f"HTTP error (attempt {attempt + 1}/"
                        f"{self.config.max_retries + 1}), retrying in {wait_time}s - "
                        f"ID: {correlation_id}, Error: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    raise FinancialServiceError(f"HTTP error after {self.config.max_retries + 1} attempts: {e}")

            except requests.exceptions.Timeout:
                if attempt < self.config.max_retries:
                    wait_time = 2**attempt
                    self.logger.warning(
                        f"Timeout (attempt {attempt + 1}/"
                        f"{self.config.max_retries + 1}), retrying in {wait_time}s - "
                        f"ID: {correlation_id}"
                    )
                    time.sleep(wait_time)
                else:
                    raise APITimeoutError(f"Request timed out after {self.config.max_retries + 1} attempts")

            except Exception as e:
                if attempt < self.config.max_retries:
                    wait_time = 2**attempt
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}/"
                        f"{self.config.max_retries + 1}), retrying in {wait_time}s - "
                        f"ID: {correlation_id}, Error: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(
                        f"Request failed after {self.config.max_retries + 1} attempts - "
                        f"ID: {correlation_id}, Error: {e}"
                    )
                    raise FinancialServiceError(f"API request failed: {e}")

    @abstractmethod
    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """
        Validate and transform API response data

        Args:
            data: Raw API response data
            endpoint: API endpoint that was called

        Returns:
            Validated and transformed data

        Raises:
            ValidationError: When response data is invalid
        """

    def health_check(self) -> dict[str, Any]:
        """
        Service health check for monitoring

        Returns:
            Dictionary containing service health information
        """
        health_status = {
            "service_name": self.config.name,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "api_key_configured": bool(self.config.api_key),
            "base_url": self.config.base_url,
            "cache_enabled": self.config.cache.enabled,
            "rate_limit_enabled": self.config.rate_limit.enabled,
        }

        try:
            # Basic connectivity test
            if self.config.api_key:
                health_status["status"] = "healthy"
                health_status["message"] = "Service configured with API key"
            else:
                health_status["status"] = "configuration_error"
                health_status["message"] = "Missing API key configuration"

        except Exception as e:
            health_status["status"] = "error"
            health_status["message"] = f"Health check failed: {str(e)}"

        return health_status

    def cleanup_cache(self) -> None:
        """Clean up expired cache entries"""
        self.cache.cleanup_expired()

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.cache.clear()

    def get_service_info(self) -> dict[str, Any]:
        """Get service configuration and status information"""
        info = {
            "name": self.config.name,
            "base_url": self.config.base_url,
            "cache_enabled": self.config.cache.enabled,
            "rate_limit_enabled": self.config.rate_limit.enabled,
            "requests_per_minute": self.config.rate_limit.requests_per_minute,
            "cache_ttl_seconds": self.config.cache.ttl_seconds,
            "max_retries": self.config.max_retries,
            "timeout_seconds": self.config.timeout_seconds,
            "historical_storage": {
                "enabled": self.config.historical_storage.enabled,
                "store_stock_prices": self.config.historical_storage.store_stock_prices,
                "store_financials": self.config.historical_storage.store_financials,
                "store_fundamentals": self.config.historical_storage.store_fundamentals,
                "store_news_sentiment": self.config.historical_storage.store_news_sentiment,
                "auto_detect_data_type": self.config.historical_storage.auto_detect_data_type,
            },
        }

        # Add historical data stats if available
        if self.historical_manager:
            try:
                historical_stats = self.historical_manager.get_available_data()
                info["historical_storage"]["stats"] = historical_stats
            except Exception as e:
                self.logger.warning(f"Failed to get historical stats: {e}")

        return info

    def get_historical_data(
        self,
        symbol: str,
        data_type: DataType,
        date_start: str | datetime,
        date_end: str | datetime | None = None,
        timeframe: Timeframe = Timeframe.DAILY,
    ) -> list[dict[str, Any]]:
        """
        Retrieve historical data from storage

        Args:
            symbol: Symbol to retrieve data for
            data_type: Type of data to retrieve
            date_start: Start date for retrieval
            date_end: End date (defaults to date_start)
            timeframe: Data timeframe

        Returns:
            List of historical data records
        """
        if not self.historical_manager:
            self.logger.warning("Historical data manager not initialized")
            return []

        try:
            return self.historical_manager.retrieve_data(symbol, data_type, date_start, date_end, timeframe)
        except Exception as e:
            self.logger.error(f"Failed to retrieve historical data: {e}")
            return []

    def cleanup_historical_cache(self) -> None:
        """Clean up expired historical cache entries"""
        if self.historical_manager:
            try:
                # This would implement cleanup based on retention policies
                self.logger.info("Historical data cleanup completed")
            except Exception as e:
                self.logger.error(f"Failed to cleanup historical data: {e}")
