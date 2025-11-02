#!/usr/bin/env python3
"""
Unified Cache Manager
Centralized caching implementation for all financial services
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


class CacheStats:
    """Cache performance statistics tracking"""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.errors = 0
        self.start_time = time.time()

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "errors": self.errors,
            "hit_ratio": self.hit_ratio,
            "total_requests": self.total_requests,
            "uptime_seconds": time.time() - self.start_time,
        }


class UnifiedCacheManager:
    """
    Production-grade cache manager with unified configuration
    """

    def __init__(self, service_name: str, config_path: str | None = None):
        self.service_name = service_name
        self.config = self._load_config(config_path)
        self.cache_dir = Path(self.config["global_cache"]["directory"]) / service_name
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Service-specific TTL
        self.ttl = self.config["service_ttl_settings"].get(service_name, self.config["service_ttl_settings"]["default"])

        # Performance tracking
        self.stats = CacheStats()
        self.logger = self._setup_logger()

        # Configuration
        self.max_size_mb = self.config["global_cache"]["max_size_mb"]
        self.compression_enabled = self.config["global_cache"]["compression_enabled"]
        self.monitoring_enabled = self.config["cache_optimization"]["monitoring_enabled"]

        self.logger.info(f"Cache manager initialized for {service_name} with {self.ttl}s TTL")

    def _load_config(self, config_path: str | None = None) -> dict[str, Any]:
        """Load unified cache configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "cache_config.yaml"

        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Cache config not found at {config_path}, using defaults")
            return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Default configuration if config file not found"""
        return {
            "global_cache": {
                "enabled": True,
                "directory": "data/cache",
                "max_size_mb": 500,
                "cleanup_interval_seconds": 3600,
                "compression_enabled": False,
            },
            "service_ttl_settings": {
                "default": 900,
                "fred_economic": 7200,
                "sec_edgar": 3600,
            },
            "cache_optimization": {"monitoring_enabled": True, "log_cache_stats": True},
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup cache-specific logging"""
        logger = logging.getLogger(f"cache.{self.service_name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path for given key"""
        hash_key = hashlib.md5(f"{self.service_name}_{key}".encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached data if not expired"""
        if not self.config["global_cache"]["enabled"]:
            self.stats.misses += 1
            return None

        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            self.stats.misses += 1
            return None

        try:
            with open(cache_path) as f:
                cached_data = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data["timestamp"])
            if datetime.now() - cached_time > timedelta(seconds=self.ttl):
                cache_path.unlink()  # Remove expired cache
                self.stats.misses += 1
                if self.monitoring_enabled:
                    self.logger.debug(f"Cache expired for key: {key}")
                return None

            self.stats.hits += 1
            if self.monitoring_enabled:
                self.logger.debug(f"Cache hit for key: {key}")
            return cached_data["data"]

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Remove corrupted cache file
            cache_path.unlink(missing_ok=True)
            self.stats.errors += 1
            self.logger.warning(f"Cache corruption detected for {key}: {e}")
            return None

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Store data in cache with timestamp"""
        if not self.config["global_cache"]["enabled"]:
            return

        cache_path = self._get_cache_path(key)
        cached_data = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "ttl_seconds": self.ttl,
            "data": data,
        }

        try:
            with open(cache_path, "w") as f:
                json.dump(cached_data, f, default=str)

            if self.monitoring_enabled:
                self.logger.debug(f"Cache set for key: {key}")

        except Exception as e:
            self.stats.errors += 1
            self.logger.warning(f"Failed to write cache for {key}: {e}")

    def clear(self) -> None:
        """Clear all cached data for this service"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)
        self.logger.info(f"Cache cleared for service: {self.service_name}")

    def cleanup_expired(self) -> int:
        """Remove expired cache entries and return count"""
        expired_count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    cached_data = json.load(f)
                cached_time = datetime.fromisoformat(cached_data["timestamp"])
                if datetime.now() - cached_time > timedelta(seconds=self.ttl):
                    cache_file.unlink()
                    expired_count += 1
            except Exception:
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)
                expired_count += 1

        if expired_count > 0:
            self.logger.info(f"Cleaned up {expired_count} expired cache entries")
        return expired_count

    def get_cache_size_mb(self) -> float:
        """Get current cache size in MB"""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        return total_size / (1024 * 1024)

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "service_name": self.service_name,
            "ttl_seconds": self.ttl,
            "cache_size_mb": self.get_cache_size_mb(),
            "cache_entries": len(list(self.cache_dir.glob("*.json"))),
            **self.stats.to_dict(),
        }

    def warm_cache(self, warm_keys: list[str], warm_function: callable) -> None:
        """Proactively warm cache with frequently accessed data"""
        if not self.config["cache_optimization"].get("warm_cache_enabled", False):
            return

        self.logger.info(f"Warming cache for {len(warm_keys)} keys")
        warmed = 0
        for key in warm_keys:
            try:
                if not self.get(key):  # Only warm if not already cached
                    data = warm_function(key)
                    if data:
                        self.set(key, data)
                        warmed += 1
            except Exception as e:
                self.logger.warning(f"Failed to warm cache for {key}: {e}")

        self.logger.info(f"Cache warming completed: {warmed}/{len(warm_keys)} keys warmed")

    def log_stats(self) -> None:
        """Log current cache statistics"""
        if self.config["cache_optimization"].get("log_cache_stats", False):
            stats = self.get_stats()
            self.logger.info(f"Cache stats: {stats}")


def create_cache_manager(service_name: str, config_path: str | None = None) -> UnifiedCacheManager:
    """Factory function to create cache manager instances"""
    return UnifiedCacheManager(service_name, config_path)


if __name__ == "__main__":
    # Example usage
    cache = create_cache_manager("yahoo_finance")

    # Set some test data
    cache.set("test_key", {"test": "data", "timestamp": "2025-07-08"})

    # Retrieve data
    data = cache.get("test_key")
    print("Retrieved: {data}")

    # Show stats
    print("Cache stats: {cache.get_stats()}")

    # Cleanup
    cache.cleanup_expired()
