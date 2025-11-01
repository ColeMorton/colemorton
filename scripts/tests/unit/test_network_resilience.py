#!/usr/bin/env python3
"""
Unit Tests for Network Resilience Patterns

Tests circuit breaker, retry logic, timeout management, and graceful degradation
patterns without external API dependencies.
"""

import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.network_resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerException,
    CircuitBreakerState,
    NetworkResilienceManager,
    RetryConfig,
    RetryExhaustedException,
    RetryHandler,
    with_network_resilience,
)


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality"""

    def setUp(self):
        """Set up test circuit breaker"""
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,  # Short timeout for testing
            success_threshold=2,
            timeout_seconds=5.0,
        )
        self.circuit_breaker = CircuitBreaker("test_service", self.config)

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker starts in closed state"""
        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
        self.assertEqual(self.circuit_breaker.success_count, 0)

    def test_successful_calls(self):
        """Test circuit breaker handles successful calls"""
        mock_func = Mock(return_value="success")

        result = self.circuit_breaker.call(mock_func, "arg1", kwarg="value")

        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
        self.assertEqual(self.circuit_breaker.metrics.successful_requests, 1)

    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures"""
        mock_func = Mock(side_effect=Exception("Test error"))

        # First two failures should keep circuit closed
        for i in range(2):
            with self.assertRaises(Exception):
                self.circuit_breaker.call(mock_func)
            self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.CLOSED)

        # Third failure should open the circuit
        with self.assertRaises(Exception):
            self.circuit_breaker.call(mock_func)
        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.OPEN)

    def test_open_circuit_blocks_calls(self):
        """Test open circuit breaker blocks calls"""
        # Force circuit to open
        mock_func = Mock(side_effect=Exception("Test error"))
        for _ in range(3):
            with self.assertRaises(Exception):
                self.circuit_breaker.call(mock_func)

        # Verify circuit is open
        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.OPEN)

        # New call should be blocked
        working_func = Mock(return_value="success")
        with self.assertRaises(CircuitBreakerException):
            self.circuit_breaker.call(working_func)

        # Working function should not have been called
        working_func.assert_not_called()

    def test_circuit_recovery_to_half_open(self):
        """Test circuit breaker recovery to half-open state"""
        # Open the circuit
        mock_func = Mock(side_effect=Exception("Test error"))
        for _ in range(3):
            with self.assertRaises(Exception):
                self.circuit_breaker.call(mock_func)

        # Wait for recovery timeout
        time.sleep(1.1)

        # Next call should move to half-open
        working_func = Mock(return_value="success")
        result = self.circuit_breaker.call(working_func)

        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.HALF_OPEN)

    def test_circuit_closes_after_successful_recovery(self):
        """Test circuit breaker closes after successful recovery"""
        # Open the circuit
        mock_func = Mock(side_effect=Exception("Test error"))
        for _ in range(3):
            with self.assertRaises(Exception):
                self.circuit_breaker.call(mock_func)

        # Wait for recovery timeout
        time.sleep(1.1)

        # Successful calls to close circuit
        working_func = Mock(return_value="success")
        for _ in range(2):  # success_threshold = 2
            result = self.circuit_breaker.call(working_func)
            self.assertEqual(result, "success")

        # Circuit should now be closed
        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.CLOSED)

    def test_circuit_metrics(self):
        """Test circuit breaker metrics collection"""
        # Execute some successful calls
        success_func = Mock(return_value="success")
        for _ in range(3):
            self.circuit_breaker.call(success_func)

        # Execute some failed calls
        error_func = Mock(side_effect=Exception("Test error"))
        for _ in range(2):
            with self.assertRaises(Exception):
                self.circuit_breaker.call(error_func)

        metrics = self.circuit_breaker.metrics

        self.assertEqual(metrics.total_requests, 5)
        self.assertEqual(metrics.successful_requests, 3)
        self.assertEqual(metrics.failed_requests, 2)
        self.assertEqual(metrics.success_rate, 60.0)
        self.assertIsNotNone(metrics.last_success)
        self.assertIsNotNone(metrics.last_failure)

    def test_circuit_status(self):
        """Test circuit breaker status reporting"""
        status = self.circuit_breaker.get_status()

        self.assertEqual(status["name"], "test_service")
        self.assertEqual(status["state"], "closed")
        self.assertIn("metrics", status)
        self.assertIn("config", status)

        # Verify metrics structure
        metrics = status["metrics"]
        self.assertIn("total_requests", metrics)
        self.assertIn("success_rate", metrics)
        self.assertIn("availability", metrics)


class TestRetryHandler(unittest.TestCase):
    """Test retry handler functionality"""

    def setUp(self):
        """Set up test retry handler"""
        self.config = RetryConfig(
            max_retries=3,
            initial_delay=0.1,  # Short delay for testing
            max_delay=1.0,
            exponential_base=2.0,
            jitter=False,  # Disable jitter for predictable testing
        )
        self.retry_handler = RetryHandler(self.config)

    def test_successful_call_no_retry(self):
        """Test successful call requires no retries"""
        mock_func = Mock(return_value="success")

        result = self.retry_handler.execute_with_retry(mock_func, "arg1", kwarg="value")

        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("arg1", kwarg="value")

    def test_retry_on_failure(self):
        """Test retry logic on failures"""
        # Fail twice, then succeed
        mock_func = Mock(side_effect=[Exception("Error 1"), Exception("Error 2"), "success"])

        result = self.retry_handler.execute_with_retry(mock_func)

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_exhaustion(self):
        """Test retry exhaustion raises exception"""
        mock_func = Mock(side_effect=Exception("Persistent error"))

        with self.assertRaises(RetryExhaustedException):
            self.retry_handler.execute_with_retry(mock_func)

        # Should have tried max_retries + 1 times
        self.assertEqual(mock_func.call_count, 4)  # 1 initial + 3 retries

    def test_circuit_breaker_exception_no_retry(self):
        """Test circuit breaker exceptions are not retried"""
        mock_func = Mock(side_effect=CircuitBreakerException("Circuit open"))

        with self.assertRaises(CircuitBreakerException):
            self.retry_handler.execute_with_retry(mock_func)

        # Should only have tried once
        mock_func.assert_called_once()

    def test_exponential_backoff_delay(self):
        """Test exponential backoff delay calculation"""
        # Test delay calculation
        delay1 = self.retry_handler._calculate_delay(1)
        delay2 = self.retry_handler._calculate_delay(2)
        delay3 = self.retry_handler._calculate_delay(3)

        # Delays should increase exponentially
        self.assertAlmostEqual(delay1, 0.1, places=2)  # initial_delay
        self.assertAlmostEqual(delay2, 0.2, places=2)  # initial_delay * 2^1
        self.assertAlmostEqual(delay3, 0.4, places=2)  # initial_delay * 2^2

    def test_max_delay_cap(self):
        """Test maximum delay cap"""
        # Very high attempt should be capped at max_delay
        delay = self.retry_handler._calculate_delay(10)
        self.assertLessEqual(delay, self.config.max_delay)


class TestNetworkResilienceManager(unittest.TestCase):
    """Test network resilience manager"""

    def setUp(self):
        """Set up test manager"""
        self.manager = NetworkResilienceManager()

    def test_circuit_breaker_creation(self):
        """Test circuit breaker creation and retrieval"""
        cb1 = self.manager.get_circuit_breaker("service1")
        cb2 = self.manager.get_circuit_breaker("service1")  # Same service
        cb3 = self.manager.get_circuit_breaker("service2")  # Different service

        # Same service should return same instance
        self.assertIs(cb1, cb2)

        # Different service should return different instance
        self.assertIsNot(cb1, cb3)

        # Names should be correct
        self.assertEqual(cb1.name, "service1")
        self.assertEqual(cb3.name, "service2")

    def test_execute_with_resilience_success(self):
        """Test successful execution with resilience patterns"""
        mock_func = Mock(return_value="success")

        result = self.manager.execute_with_resilience("test_service", mock_func, None, None, "arg1", kwarg="value")

        self.assertEqual(result, "success")
        mock_func.assert_called_with("arg1", kwarg="value")

    def test_execute_with_resilience_failure(self):
        """Test failure handling with resilience patterns"""
        mock_func = Mock(side_effect=Exception("Persistent error"))

        with self.assertRaises(RetryExhaustedException):
            self.manager.execute_with_resilience("test_service", mock_func)

        # Should have attempted retries
        self.assertGreater(mock_func.call_count, 1)

    def test_status_reporting(self):
        """Test status reporting for all circuit breakers"""
        # Create some circuit breakers
        self.manager.get_circuit_breaker("service1")
        self.manager.get_circuit_breaker("service2")

        status = self.manager.get_all_status()

        self.assertIn("service1", status)
        self.assertIn("service2", status)
        self.assertEqual(len(status), 2)

    def test_circuit_breaker_reset(self):
        """Test circuit breaker reset functionality"""
        # Open a circuit breaker
        cb = self.manager.get_circuit_breaker("test_service")
        cb.state = CircuitBreakerState.OPEN
        cb.failure_count = 5

        # Reset it
        self.manager.reset_circuit_breaker("test_service")

        # Should be closed with reset counters
        self.assertEqual(cb.state, CircuitBreakerState.CLOSED)
        self.assertEqual(cb.failure_count, 0)


class TestResilientDecorator(unittest.TestCase):
    """Test network resilience decorator"""

    def test_decorator_success(self):
        """Test decorator with successful function"""

        @with_network_resilience("test_service")
        def test_func(arg1, kwarg=None):
            return f"success: {arg1}, {kwarg}"

        result = test_func("value1", kwarg="value2")
        self.assertEqual(result, "success: value1, value2")

    def test_decorator_with_custom_config(self):
        """Test decorator with custom configuration"""
        circuit_config = CircuitBreakerConfig(failure_threshold=2)
        retry_config = RetryConfig(max_retries=1)

        @with_network_resilience("test_service", circuit_config=circuit_config, retry_config=retry_config)
        def test_func():
            raise Exception("Test error")

        with self.assertRaises(RetryExhaustedException):
            test_func()


class TestResilientMempoolSpaceService(unittest.TestCase):
    """Test resilient Mempool.space service"""

    def setUp(self):
        """Set up test service"""
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

        # Mock the service config
        from services.base_financial_service import ServiceConfig

        self.service_config = ServiceConfig(
            name="test_mempool_space",
            base_url="https://mempool.space/api",
            timeout_seconds=10,
            max_retries=1,
        )

    @patch("services.resilient_mempool_space.ResilientMempoolSpaceService._make_request_with_retry")
    def test_resilient_fee_estimates(self, mock_request):
        """Test resilient fee estimates with mocked response"""
        from services.resilient_mempool_space import ResilientMempoolSpaceService

        # Mock successful response
        mock_request.return_value = {
            "fastestFee": 15,
            "halfHourFee": 12,
            "hourFee": 10,
            "economyFee": 8,
        }

        service = ResilientMempoolSpaceService(self.service_config)
        result = service.get_fee_estimates()

        self.assertIn("fastestFee", result)
        self.assertEqual(result["fastestFee"], 15)
        self.assertNotIn("fallback", result)

    @patch("services.resilient_mempool_space.ResilientMempoolSpaceService._make_request_with_retry")
    def test_fallback_response(self, mock_request):
        """Test fallback response when circuit breaker is open"""
        from services.resilient_mempool_space import ResilientMempoolSpaceService

        # Mock repeated failures to open circuit breaker
        mock_request.side_effect = Exception("API Error")

        service = ResilientMempoolSpaceService(self.service_config)

        # Make enough failed requests to open circuit breaker
        for _ in range(5):
            try:
                service.get_fee_estimates()
            except:
                pass

        # Next request should return fallback
        result = service.get_fee_estimates()

        self.assertIn("fallback", result)
        self.assertTrue(result["fallback"])
        self.assertIn("fastestFee", result)  # Should have fallback fee data

    def test_service_health_metrics(self):
        """Test service health metrics collection"""
        from services.resilient_mempool_space import ResilientMempoolSpaceService

        service = ResilientMempoolSpaceService(self.service_config)
        health = service.get_service_health()

        self.assertIn("service_name", health)
        self.assertIn("circuit_breaker_state", health)
        self.assertIn("success_rate", health)
        self.assertIn("availability", health)
        self.assertIn("health_status", health)

        self.assertEqual(health["service_name"], "mempool_space")


class TestConcurrentCircuitBreaker(unittest.TestCase):
    """Test circuit breaker thread safety"""

    def test_concurrent_access(self):
        """Test circuit breaker handles concurrent access correctly"""
        circuit_breaker = CircuitBreaker("concurrent_test")
        results = []
        exceptions = []

        def worker():
            try:
                mock_func = Mock(return_value="success")
                result = circuit_breaker.call(mock_func)
                results.append(result)
            except Exception as e:
                exceptions.append(e)

        # Create multiple threads
        threads = [threading.Thread(target=worker) for _ in range(10)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join()

        # All should succeed
        self.assertEqual(len(results), 10)
        self.assertEqual(len(exceptions), 0)
        self.assertEqual(circuit_breaker.metrics.successful_requests, 10)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
