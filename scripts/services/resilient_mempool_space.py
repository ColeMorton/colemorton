#!/usr/bin/env python3
"""
Resilient Mempool.space Service

Enhanced version of the Mempool.space service with comprehensive network resilience patterns:
- Circuit breaker protection against cascade failures
- Exponential backoff retry logic with jitter
- Graceful degradation with fallback responses
- Health monitoring and metrics collection
- Timeout management with configurable limits

This demonstrates how to integrate network resilience into Bitcoin CLI services.
"""

import logging
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
from network_resilience import (
    CircuitBreakerConfig,
    CircuitBreakerException,
    NetworkResilienceManager,
    RetryConfig,
    RetryExhaustedException,
    with_network_resilience,
)


class ResilientMempoolSpaceService(BaseFinancialService):
    """
    Mempool.space service with network resilience patterns

    Provides access to Mempool.space Bitcoin blockchain data with:
    - Production-grade error handling and recovery
    - Circuit breaker protection against service failures
    - Intelligent retry logic with exponential backoff
    - Graceful degradation when APIs are unavailable
    - Comprehensive health monitoring and metrics
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Initialize network resilience manager
        self.resilience_manager = NetworkResilienceManager()

        # Configure circuit breaker for Mempool.space
        self.circuit_config = CircuitBreakerConfig(
            failure_threshold=3,  # Open after 3 failures
            recovery_timeout=30,  # Try recovery after 30 seconds
            success_threshold=2,  # Close after 2 successes
            timeout_seconds=15.0,  # 15 second timeout
        )

        # Configure retry behavior
        self.retry_config = RetryConfig(
            max_retries=2,  # Maximum 2 retries
            initial_delay=1.0,  # Start with 1 second delay
            max_delay=10.0,  # Maximum 10 second delay
            exponential_base=2.0,  # Double delay each time
            jitter=True,  # Add randomization
        )

        self.service_name = "mempool_space"
        self.logger = logging.getLogger(f"resilient_service.{self.service_name}")

    def _resilient_request(self, endpoint: str, params: dict[str, Any] = None) -> Any:
        """Make resilient request with circuit breaker and retry protection"""

        def make_request():
            return self._make_request_with_retry(endpoint, params)

        try:
            return self.resilience_manager.execute_with_resilience(
                service_name=self.service_name,
                func=make_request,
                circuit_config=self.circuit_config,
                retry_config=self.retry_config,
            )
        except CircuitBreakerException as e:
            self.logger.warning(f"Circuit breaker open for {self.service_name}: {e}")
            return self._get_fallback_response(endpoint)
        except RetryExhaustedException as e:
            self.logger.error(f"All retries exhausted for {self.service_name}/{endpoint}: {e}")
            return self._get_fallback_response(endpoint)

    def _get_fallback_response(self, endpoint: str) -> dict[str, Any]:
        """
        Provide fallback response when service is unavailable

        This implements graceful degradation by returning reasonable
        fallback data instead of failing completely.
        """
        fallback_data = {
            "timestamp": datetime.now().isoformat(),
            "service_status": "degraded",
            "fallback_reason": "Service temporarily unavailable",
            "endpoint": endpoint,
        }

        # Endpoint-specific fallbacks
        if endpoint == "/v1/fees/recommended":
            fallback_data.update(
                {
                    "fastestFee": 20,  # Conservative high fee
                    "halfHourFee": 15,  # Reasonable medium fee
                    "hourFee": 10,  # Standard low fee
                    "economyFee": 8,  # Economy fee
                    "minimumFee": 6,  # Minimum fee
                    "fallback": True,
                }
            )
        elif endpoint == "/mempool":
            fallback_data.update({"count": 0, "vsize": 0, "total_fee": 0, "fallback": True})
        elif endpoint.startswith("/v1/blocks"):
            fallback_data.update({"blocks": [], "fallback": True})
        else:
            fallback_data.update({"data": None, "fallback": True})

        self.logger.info(f"Returning fallback response for {endpoint}")
        return fallback_data

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate response data with enhanced error handling"""

        # Handle fallback responses
        if isinstance(data, dict) and data.get("fallback"):
            return data

        if not data:
            raise DataNotFoundError(f"No data returned from Mempool.space {endpoint}")

        # Mempool.space returns clean data, minimal validation needed
        return data

    # Enhanced API methods with resilience patterns

    def get_fee_estimates(self) -> dict[str, Any]:
        """Get recommended Bitcoin transaction fees with resilience"""
        endpoint = "/v1/fees/recommended"
        data = self._resilient_request(endpoint)
        return self._validate_response(data, "fee estimates")

    def get_mempool_info(self) -> dict[str, Any]:
        """Get current mempool statistics with resilience"""
        endpoint = "/mempool"
        data = self._resilient_request(endpoint)
        return self._validate_response(data, "mempool info")

    def get_recent_blocks(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent Bitcoin blocks with resilience"""
        if limit > 25:
            limit = 25

        endpoint = "/v1/blocks"
        data = self._resilient_request(endpoint)

        if isinstance(data, list):
            return data[:limit]
        return self._validate_response(data, "recent blocks")

    def get_bitcoin_price(self) -> dict[str, Any]:
        """Get current Bitcoin price with resilience"""
        endpoint = "/v1/prices"
        data = self._resilient_request(endpoint)
        return self._validate_response(data, "Bitcoin price")

    def get_network_stats(self) -> dict[str, Any]:
        """Get comprehensive Bitcoin network statistics with resilience"""
        # Combine multiple endpoints for comprehensive network health
        stats = {
            "timestamp": datetime.now().isoformat(),
            "service_health": self.get_service_health(),
            "mempool": {},
            "fees": {},
            "difficulty": {},
            "price": {},
            "errors": [],
        }

        # Get mempool info with error handling
        try:
            mempool_info = self.get_mempool_info()
            if not mempool_info.get("fallback"):
                stats["mempool"] = mempool_info
        except Exception as e:
            stats["errors"].append(f"Mempool error: {str(e)}")

        # Get fee estimates with error handling
        try:
            fee_estimates = self.get_fee_estimates()
            if not fee_estimates.get("fallback"):
                stats["fees"] = fee_estimates
        except Exception as e:
            stats["errors"].append(f"Fee estimates error: {str(e)}")

        # Get price with error handling
        try:
            price_info = self.get_bitcoin_price()
            if not price_info.get("fallback"):
                stats["price"] = price_info
        except Exception as e:
            stats["errors"].append(f"Price error: {str(e)}")

        return stats

    def get_service_health(self) -> dict[str, Any]:
        """Get detailed service health metrics"""
        circuit_breaker = self.resilience_manager.get_circuit_breaker(self.service_name)
        status = circuit_breaker.get_status()

        # Add service-specific health information
        health_info = {
            "service_name": self.service_name,
            "circuit_breaker_state": status["state"],
            "success_rate": status["metrics"]["success_rate"],
            "availability": status["metrics"]["availability"],
            "average_response_time": status["metrics"]["average_response_time"],
            "total_requests": status["metrics"]["total_requests"],
            "circuit_breaker_trips": status["metrics"]["circuit_breaker_trips"],
            "last_success": status["metrics"]["last_success"],
            "last_failure": status["metrics"]["last_failure"],
            "health_status": self._determine_health_status(status),
        }

        return health_info

    def _determine_health_status(self, circuit_status: dict[str, Any]) -> str:
        """Determine overall health status"""
        state = circuit_status["state"]
        metrics = circuit_status["metrics"]

        if state == "open":
            return "unhealthy"
        if state == "half_open":
            return "recovering"
        if metrics["success_rate"] >= 95.0:
            return "healthy"
        if metrics["success_rate"] >= 80.0:
            return "degraded"
        return "poor"

    def reset_circuit_breaker(self):
        """Manually reset the circuit breaker"""
        self.resilience_manager.reset_circuit_breaker(self.service_name)
        self.logger.info(f"Circuit breaker reset for {self.service_name}")

    def get_resilience_metrics(self) -> dict[str, Any]:
        """Get comprehensive resilience metrics"""
        all_status = self.resilience_manager.get_all_status()

        return {
            "timestamp": datetime.now().isoformat(),
            "services": all_status,
            "summary": {
                "total_services": len(all_status),
                "healthy_services": len(
                    [s for s in all_status.values() if s["state"] == "closed" and s["metrics"]["success_rate"] >= 95.0]
                ),
                "degraded_services": len(
                    [
                        s
                        for s in all_status.values()
                        if s["state"] in ["half_open", "open"] or s["metrics"]["success_rate"] < 95.0
                    ]
                ),
            },
        }


def create_resilient_mempool_space_service(
    env: str = "dev",
) -> ResilientMempoolSpaceService:
    """
    Factory function to create ResilientMempoolSpaceService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured ResilientMempoolSpaceService instance
    """
    try:
        # Load configuration
        from config_loader import ConfigLoader

        config_loader = ConfigLoader()

        # Create service config - Mempool.space is free, no API key needed
        service_config = ServiceConfig(
            name="mempool_space_resilient",
            api_key=None,  # No API key required
            base_url="https://mempool.space/api",
            timeout_seconds=15,  # Shorter timeout for resilience
            max_retries=1,  # Let resilience manager handle retries
        )

        return ResilientMempoolSpaceService(service_config)

    except Exception:
        # Fallback configuration
        service_config = ServiceConfig(
            name="mempool_space_resilient",
            api_key=None,
            base_url="https://mempool.space/api",
            timeout_seconds=15,
            max_retries=1,
        )

        return ResilientMempoolSpaceService(service_config)


# Demonstration decorator usage
class DecoratorExampleService:
    """Example of using decorator-based resilience patterns"""

    @with_network_resilience(
        service_name="mempool_space_decorator",
        circuit_config=CircuitBreakerConfig(failure_threshold=2, recovery_timeout=20),
        retry_config=RetryConfig(max_retries=1, initial_delay=0.5),
    )
    def get_fees_with_decorator(self) -> dict[str, Any]:
        """Example of decorator-based resilience"""
        # Simulate API call
        import requests

        response = requests.get("https://mempool.space/api/v1/fees/recommended", timeout=10)
        response.raise_for_status()
        return response.json()
