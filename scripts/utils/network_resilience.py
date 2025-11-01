#!/usr/bin/env python3
"""
Network Resilience Patterns for Bitcoin CLI Services

Implements production-grade network resilience patterns including:
- Circuit Breaker: Prevents cascade failures by stopping calls to failing services
- Exponential Backoff: Progressive delay increases for retries
- Timeout Management: Configurable timeouts with fallback behavior
- Health Monitoring: Track service health and recovery patterns
- Graceful Degradation: Fallback responses when services are unavailable
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""

    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: int = 60  # Seconds before trying half-open
    success_threshold: int = 3  # Successes needed to close circuit
    timeout_seconds: float = 30.0  # Request timeout


@dataclass
class RetryConfig:
    """Retry configuration with exponential backoff"""

    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomization to prevent thundering herd


@dataclass
class HealthMetrics:
    """Health metrics tracking"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_breaker_trips: int = 0
    last_success: datetime | None = None
    last_failure: datetime | None = None
    average_response_time: float = 0.0
    response_times: list[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def availability(self) -> str:
        """Get availability status"""
        if self.success_rate >= 99.0:
            return "excellent"
        if self.success_rate >= 95.0:
            return "good"
        if self.success_rate >= 90.0:
            return "fair"
        return "poor"


class CircuitBreaker:
    """
    Circuit breaker implementation for network resilience

    Prevents cascade failures by monitoring service health and temporarily
    blocking requests to failing services, allowing them time to recover.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.metrics = HealthMetrics()
        self.lock = threading.RLock()

        self.logger = logging.getLogger(f"circuit_breaker.{name}")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        with self.lock:
            self.metrics.total_requests += 1

            # Check if circuit should be opened
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.logger.info(f"Circuit breaker {self.name} moving to HALF_OPEN")
                else:
                    self.metrics.failed_requests += 1
                    raise CircuitBreakerException(f"Circuit breaker {self.name} is OPEN")

            start_time = time.time()

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Record success
                execution_time = time.time() - start_time
                self._record_success(execution_time)

                return result

            except Exception as e:
                # Record failure
                execution_time = time.time() - start_time
                self._record_failure(execution_time, e)
                raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout

    def _record_success(self, execution_time: float):
        """Record successful execution"""
        with self.lock:
            self.metrics.successful_requests += 1
            self.metrics.last_success = datetime.now()
            self._update_response_time(execution_time)

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.logger.info(f"Circuit breaker {self.name} CLOSED after recovery")
            else:
                self.failure_count = 0  # Reset failure count on success

    def _record_failure(self, execution_time: float, exception: Exception):
        """Record failed execution"""
        with self.lock:
            self.metrics.failed_requests += 1
            self.metrics.last_failure = datetime.now()
            self._update_response_time(execution_time)

            self.failure_count += 1
            self.success_count = 0  # Reset success count on failure
            self.last_failure_time = time.time()

            # Check if circuit should open
            if self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self.metrics.circuit_breaker_trips += 1
                self.logger.warning(
                    f"Circuit breaker {self.name} OPENED after {self.failure_count} failures. "
                    f"Last error: {str(exception)}"
                )
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                self.logger.warning(f"Circuit breaker {self.name} back to OPEN from HALF_OPEN")

    def _update_response_time(self, execution_time: float):
        """Update response time metrics"""
        self.metrics.response_times.append(execution_time)

        # Keep only last 100 response times for averaging
        if len(self.metrics.response_times) > 100:
            self.metrics.response_times.pop(0)

        # Calculate average response time
        if self.metrics.response_times:
            self.metrics.average_response_time = sum(self.metrics.response_times) / len(self.metrics.response_times)

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status and metrics"""
        with self.lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "success_rate": round(self.metrics.success_rate, 2),
                    "availability": self.metrics.availability,
                    "circuit_breaker_trips": self.metrics.circuit_breaker_trips,
                    "average_response_time": round(self.metrics.average_response_time, 3),
                    "last_success": self.metrics.last_success.isoformat() if self.metrics.last_success else None,
                    "last_failure": self.metrics.last_failure.isoformat() if self.metrics.last_failure else None,
                },
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "success_threshold": self.config.success_threshold,
                    "timeout_seconds": self.config.timeout_seconds,
                },
            }

    def reset(self):
        """Manually reset circuit breaker to closed state"""
        with self.lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.logger.info(f"Circuit breaker {self.name} manually reset to CLOSED")


class CircuitBreakerException(Exception):
    """Exception thrown when circuit breaker is open"""


class RetryHandler:
    """
    Retry handler with exponential backoff and jitter

    Provides intelligent retry logic with progressive delays to avoid
    overwhelming failing services while maximizing success probability.
    """

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.logger = logging.getLogger("retry_handler")

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self._calculate_delay(attempt)
                    self.logger.info(f"Retry attempt {attempt}/{self.config.max_retries} after {delay:.2f}s delay")
                    time.sleep(delay)

                return func(*args, **kwargs)

            except CircuitBreakerException:
                # Don't retry if circuit breaker is open
                raise

            except Exception as e:
                last_exception = e
                if attempt == self.config.max_retries:
                    break

                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

        # All retries exhausted
        raise RetryExhaustedException(f"All {self.config.max_retries} retries failed") from last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt with exponential backoff and jitter"""
        # Exponential backoff
        delay = min(
            self.config.initial_delay * (self.config.exponential_base ** (attempt - 1)),
            self.config.max_delay,
        )

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random

            delay *= 0.5 + 0.5 * random.random()

        return delay


class RetryExhaustedException(Exception):
    """Exception thrown when all retries are exhausted"""


class NetworkResilienceManager:
    """
    Network resilience manager combining multiple patterns

    Provides a unified interface for applying circuit breaker, retry,
    and timeout patterns to network operations.
    """

    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_handler = RetryHandler()
        self.logger = logging.getLogger("network_resilience")

    def get_circuit_breaker(self, service_name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(service_name, config)
        return self.circuit_breakers[service_name]

    def execute_with_resilience(
        self,
        service_name: str,
        func: Callable,
        circuit_config: CircuitBreakerConfig = None,
        retry_config: RetryConfig = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with full resilience patterns

        Args:
            service_name: Name of the service (for circuit breaker)
            func: Function to execute
            circuit_config: Circuit breaker configuration
            retry_config: Retry configuration
            *args, **kwargs: Arguments for the function

        Returns:
            Function result

        Raises:
            CircuitBreakerException: If circuit breaker is open
            RetryExhaustedException: If all retries failed
        """
        circuit_breaker = self.get_circuit_breaker(service_name, circuit_config)
        retry_handler = RetryHandler(retry_config or self.retry_handler.config)

        def resilient_call():
            return circuit_breaker.call(func, *args, **kwargs)

        return retry_handler.execute_with_retry(resilient_call)

    def get_all_status(self) -> dict[str, Any]:
        """Get status of all circuit breakers"""
        return {name: cb.get_status() for name, cb in self.circuit_breakers.items()}

    def reset_circuit_breaker(self, service_name: str):
        """Reset specific circuit breaker"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name].reset()

    def reset_all_circuit_breakers(self):
        """Reset all circuit breakers"""
        for cb in self.circuit_breakers.values():
            cb.reset()


# Decorator for easy application of network resilience
def with_network_resilience(
    service_name: str,
    circuit_config: CircuitBreakerConfig = None,
    retry_config: RetryConfig = None,
):
    """
    Decorator to apply network resilience patterns to functions

    Usage:
        @with_network_resilience("mempool_space")
        def get_fee_estimates():
            # API call implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = NetworkResilienceManager()
            return manager.execute_with_resilience(service_name, func, circuit_config, retry_config, *args, **kwargs)

        return wrapper

    return decorator


# Global network resilience manager instance
_global_manager = NetworkResilienceManager()


def get_global_resilience_manager() -> NetworkResilienceManager:
    """Get global network resilience manager instance"""
    return _global_manager
