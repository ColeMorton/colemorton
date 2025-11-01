#!/usr/bin/env python3
"""
Unified Cache Adapter

Provides a cache interface using HistoricalDataManager as the single source of truth,
eliminating the need for a separate cache directory.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from historical_data_manager import DataType, HistoricalDataManager, Timeframe
from trading_session_manager import TradingSessionManager


class UnifiedCache:
    """
    Adapter to use HistoricalDataManager as both cache and long-term storage.

    This eliminates the dual-cache architecture by using data/raw/ as the sole
    storage location for all financial data, with TTL-based cache semantics.
    """

    def __init__(
        self,
        historical_manager: HistoricalDataManager,
        ttl_seconds: int = 900,  # 15 minutes default
        service_name: str = "unknown",
        use_trading_session_ttl: bool = True,
    ):
        """
        Initialize UnifiedCache adapter.

        Args:
            historical_manager: HistoricalDataManager instance
            ttl_seconds: Time-to-live for cache entries (fallback for non-market data)
            service_name: Name of the service using this cache
            use_trading_session_ttl: Use trading session-aware TTL for market data
        """
        self.hdm = historical_manager
        self.ttl_seconds = ttl_seconds
        self.service_name = service_name
        self.use_trading_session_ttl = use_trading_session_ttl
        self.logger = self._setup_logger()

        # Initialize trading session manager for market-aware caching
        if self.use_trading_session_ttl:
            self.trading_session_manager = TradingSessionManager()
        else:
            self.trading_session_manager = None

        # In-memory cache for recent lookups (avoids file I/O)
        self._memory_cache: dict[str, Any] = {}
        self._memory_cache_size = 100  # Max entries in memory

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for unified cache"""
        logger = logging.getLogger(f"unified_cache.{self.service_name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _parse_cache_key(self, key: str) -> tuple[str | None, DataType | None, str | None]:
        """
        Parse cache key to extract symbol, data type, and endpoint.

        Cache keys are MD5 hashes of: service_name + endpoint + params
        We need to extract meaningful information from the endpoint/params.

        Returns:
            Tuple of (symbol, data_type, endpoint)
        """
        # Check memory cache for key mapping
        if key in self._memory_cache:
            cached_entry = self._memory_cache[key]
            if "key_info" in cached_entry:
                info = cached_entry["key_info"]
                return info.get("symbol"), info.get("data_type"), info.get("endpoint")

        # Without stored key info, we can't parse the MD5 hash
        return None, None, None

    def _get_dynamic_ttl(self, data_type: DataType | None = None, endpoint: str = "") -> int:
        """
        Get dynamic TTL based on data type and trading session

        Args:
            data_type: Type of data being cached
            endpoint: API endpoint for additional context

        Returns:
            TTL in seconds
        """
        # Use trading session TTL for market data
        if self.use_trading_session_ttl and self.trading_session_manager:
            # Check if this is market-related data
            is_market_data = data_type in [
                DataType.STOCK_DAILY_PRICES,
                DataType.STOCK_FUNDAMENTALS,
            ] or any(term in endpoint.lower() for term in ["historical", "quote", "price", "market"])

            if is_market_data:
                try:
                    session_ttl = self.trading_session_manager.get_cache_ttl_seconds()
                    self.logger.debug(f"Using trading session TTL: {session_ttl}s for {endpoint}")
                    return session_ttl
                except Exception as e:
                    self.logger.warning(f"Failed to get trading session TTL: {e}, using fallback")

        # Fallback to static TTL
        return self.ttl_seconds

    def get(self, key: str) -> dict[str, Any] | None:
        """
        Retrieve cached data if not expired.

        Args:
            key: Cache key (MD5 hash)

        Returns:
            Cached data if found and not expired, None otherwise
        """
        # Parse key to determine data type for dynamic TTL
        symbol, data_type, endpoint = self._parse_cache_key(key)
        effective_ttl = self._get_dynamic_ttl(data_type, endpoint or "")

        # Check in-memory cache first
        if key in self._memory_cache:
            cached_entry = self._memory_cache[key]
            cached_time = datetime.fromisoformat(cached_entry["timestamp"])

            # Check TTL using dynamic TTL
            if datetime.now() - cached_time <= timedelta(seconds=effective_ttl):
                self.logger.debug(f"Memory cache hit for key: {key[:8]}... (TTL: {effective_ttl}s)")
                return cached_entry["data"]
            # Expired, remove from memory cache
            self.logger.debug(f"Memory cache expired for key: {key[:8]}... (TTL: {effective_ttl}s)")
            del self._memory_cache[key]

        # Try to retrieve from historical data (already parsed above)
        if not symbol or not data_type:
            # Can't retrieve without knowing what to look for
            return None

        try:
            # Query recent data from historical storage using dynamic TTL
            end_date = datetime.now()
            start_date = end_date - timedelta(seconds=effective_ttl)

            results = self.hdm.retrieve_data(
                symbol=symbol,
                data_type=data_type,
                date_start=start_date,
                date_end=end_date,
                timeframe=Timeframe.DAILY,  # Most cache queries are for daily data
            )

            if results:
                # Return the most recent result
                latest_result = results[-1]

                # Check if it's within dynamic TTL
                result_date = datetime.fromisoformat(latest_result["date"])
                if datetime.now() - result_date <= timedelta(seconds=effective_ttl):
                    self.logger.debug(f"Historical cache hit for {symbol} {data_type.value} (TTL: {effective_ttl}s)")

                    # Store in memory cache for faster access
                    self._add_to_memory_cache(
                        key,
                        latest_result["data"],
                        {
                            "symbol": symbol,
                            "data_type": data_type,
                            "endpoint": endpoint,
                        },
                    )

                    return latest_result["data"]

        except Exception as e:
            self.logger.warning(f"Failed to retrieve from historical storage: {e}")

        return None

    def set(
        self,
        key: str,
        data: dict[str, Any],
        endpoint: str = None,
        params: dict[str, Any] = None,
    ) -> None:
        """
        Store data in cache (which is now historical storage).

        Args:
            key: Cache key (MD5 hash)
            data: Data to cache
            endpoint: API endpoint (helps determine data type)
            params: Request parameters (helps extract symbol)
        """
        try:
            # Extract symbol and data type from data and endpoint
            symbol = self._extract_symbol(data, params)
            data_type = self._detect_data_type(endpoint, data)

            if not symbol or not data_type:
                self.logger.warning("Cannot determine symbol or data type for caching")
                return

            # Store in memory cache for fast retrieval
            self._add_to_memory_cache(
                key,
                data,
                {"symbol": symbol, "data_type": data_type, "endpoint": endpoint},
            )

            # Store in historical data system
            # Note: The historical data manager will handle the actual storage
            # We don't need to call it here as BaseFinancialService already does
            self.logger.debug(f"Data marked for historical storage: {symbol} {data_type.value}")

        except Exception as e:
            self.logger.warning(f"Failed to process cache set operation: {e}")

    def _add_to_memory_cache(self, key: str, data: dict[str, Any], key_info: dict[str, Any]) -> None:
        """Add entry to memory cache with LRU eviction"""
        # Implement simple LRU by removing oldest entry if cache is full
        if len(self._memory_cache) >= self._memory_cache_size:
            # Remove oldest entry (first in dict)
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]

        self._memory_cache[key] = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "key_info": key_info,
        }

    def _extract_symbol(self, data: dict[str, Any], params: dict[str, Any] | None) -> str | None:
        """Extract symbol from data or parameters"""
        # Try data first
        if isinstance(data, dict):
            for field in ["symbol", "ticker", "Symbol", "Ticker"]:
                if field in data:
                    return str(data[field]).upper()

        # Try params
        if params:
            for field in ["symbol", "ticker", "symbols"]:
                if field in params:
                    symbol = str(params[field]).upper()
                    return symbol.split(",")[0].strip()  # Handle comma-separated

        return None

    def _detect_data_type(self, endpoint: str | None, data: dict[str, Any]) -> DataType | None:
        """Detect data type from endpoint and data structure"""
        if not endpoint:
            return None

        endpoint_lower = endpoint.lower()

        # Historical price data
        if any(keyword in endpoint_lower for keyword in ["historical", "ohlc"]):
            return DataType.STOCK_DAILY_PRICES

        # Fundamentals (stock info, quotes)
        if any(keyword in endpoint_lower for keyword in ["stock_info", "quote", "profile"]):
            return DataType.STOCK_FUNDAMENTALS

        # Financial statements
        if any(keyword in endpoint_lower for keyword in ["financial", "income", "balance", "cash"]):
            return DataType.STOCK_FINANCIALS

        return None

    def clear(self) -> None:
        """Clear memory cache only (historical data is permanent)"""
        self._memory_cache.clear()
        self.logger.info("Memory cache cleared")

    def cleanup_expired(self) -> None:
        """Remove expired entries from memory cache using dynamic TTL"""
        now = datetime.now()
        expired_keys = []

        for key, entry in self._memory_cache.items():
            cached_time = datetime.fromisoformat(entry["timestamp"])

            # Get dynamic TTL for this specific entry
            key_info = entry.get("key_info", {})
            data_type = key_info.get("data_type")
            endpoint = key_info.get("endpoint", "")
            effective_ttl = self._get_dynamic_ttl(data_type, endpoint)

            if now - cached_time > timedelta(seconds=effective_ttl):
                expired_keys.append(key)

        for key in expired_keys:
            del self._memory_cache[key]

        if expired_keys:
            self.logger.info(f"Removed {len(expired_keys)} expired entries from memory cache (dynamic TTL)")

    @property
    def enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.hdm.config.get("enabled", True)
