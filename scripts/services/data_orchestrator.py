"""
Data Orchestrator

Coordinates multiple financial data services to provide:
- Cross-source data validation and consistency checking
- Multi-source price validation with confidence scoring
- Unified data aggregation and enrichment
- Institutional-grade data quality assessment
- Error handling and fallback strategies
"""

import logging
from datetime import datetime
from typing import Any


class DataOrchestrator:
    """
    Orchestrates multiple financial data services for enhanced reliability

    Provides:
    - Cross-source validation
    - Data quality assessment
    - Fallback strategies
    - Confidence scoring
    """

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.logger = logging.getLogger("data_orchestrator")

    def register_service(self, name: str, service: Any) -> None:
        """Register a financial service"""
        self.services[name] = service
        self.logger.info(f"Registered service: {name}")

    def unregister_service(self, name: str) -> None:
        """Unregister a financial service"""
        if name in self.services:
            del self.services[name]
            self.logger.info(f"Unregistered service: {name}")

    def list_services(self) -> list[str]:
        """List all registered services"""
        return list(self.services.keys())

    def validate_cross_source_prices(self, ticker: str, source_methods: dict[str, str]) -> dict[str, Any]:
        """
        Validate prices across multiple sources

        Args:
            ticker: Stock ticker symbol
            source_methods: Dict mapping service names to method names

        Returns:
            Dict containing validation results and confidence score
        """
        price_sources = {}
        errors = {}

        for service_name, method_name in source_methods.items():
            if service_name not in self.services:
                errors[service_name] = f"Service {service_name} not registered"
                continue

            try:
                service = self.services[service_name]
                method = getattr(service, method_name, None)

                if not method:
                    errors[service_name] = f"Method {method_name} not found"
                    continue

                result = method(ticker)

                # Extract price from different response formats
                price = self._extract_price_from_response(result, service_name)
                if price:
                    price_sources[service_name] = price

            except Exception as e:
                errors[service_name] = str(e)
                self.logger.warning(f"Failed to get price from {service_name}: {e}")

        return self._calculate_price_validation(price_sources, errors)

    def _extract_price_from_response(self, response: dict[str, Any], service_name: str) -> float | None:
        """Extract price from service response"""

        # Common price field names across services
        price_fields = [
            "current_price",
            "price",
            "currentPrice",
            "regularMarketPrice",
            "last_price",
            "close",
            "Close",
            "last",
            "lastPrice",
        ]

        # Handle nested response formats
        if isinstance(response, dict):
            # Try direct price fields
            for field in price_fields:
                if field in response and response[field] is not None:
                    try:
                        return float(response[field])
                    except (ValueError, TypeError):
                        continue

            # Try nested data structures
            for nested_key in ["data", "quote", "Global Quote", "result"]:
                if nested_key in response:
                    nested_data = response[nested_key]
                    if isinstance(nested_data, dict):
                        for field in price_fields:
                            if field in nested_data and nested_data[field] is not None:
                                try:
                                    return float(nested_data[field])
                                except (ValueError, TypeError):
                                    continue
                    elif isinstance(nested_data, list) and len(nested_data) > 0:
                        for field in price_fields:
                            if field in nested_data[0] and nested_data[0][field] is not None:
                                try:
                                    return float(nested_data[0][field])
                                except (ValueError, TypeError):
                                    continue

        return None

    def _calculate_price_validation(self, price_sources: dict[str, float], errors: dict[str, str]) -> dict[str, Any]:
        """Calculate price validation metrics"""

        if not price_sources:
            return {
                "validation_status": "failed",
                "confidence_score": 0.0,
                "price_sources": {},
                "errors": errors,
                "validated_price": None,
                "price_consistency": False,
                "deviation_percentage": None,
            }

        prices = list(price_sources.values())

        if len(prices) == 1:
            return {
                "validation_status": "single_source",
                "confidence_score": 0.75,
                "price_sources": price_sources,
                "errors": errors,
                "validated_price": prices[0],
                "price_consistency": True,
                "deviation_percentage": 0.0,
            }

        # Calculate statistics
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        deviation_percentage = (price_range / avg_price * 100) if avg_price > 0 else 100

        # Determine consistency and confidence
        is_consistent = deviation_percentage < 1.0  # Less than 1% deviation

        if is_consistent:
            confidence_score = min(0.95, 0.85 + (0.1 * len(prices) / 5))  # Higher confidence with more sources
            validation_status = "consistent"
        elif deviation_percentage < 5.0:
            confidence_score = 0.7
            validation_status = "acceptable"
        else:
            confidence_score = 0.4
            validation_status = "inconsistent"

        return {
            "validation_status": validation_status,
            "confidence_score": confidence_score,
            "price_sources": price_sources,
            "errors": errors,
            "validated_price": avg_price,
            "price_consistency": is_consistent,
            "deviation_percentage": deviation_percentage,
            "price_statistics": {
                "average": avg_price,
                "minimum": min_price,
                "maximum": max_price,
                "range": price_range,
                "source_count": len(prices),
            },
        }

    def get_comprehensive_analysis(self, ticker: str, services_config: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """
        Get comprehensive analysis from multiple services

        Args:
            ticker: Stock ticker symbol
            services_config: Configuration for each service

        Returns:
            Comprehensive analysis with data quality metrics
        """
        results = {}
        errors = {}
        successful_sources = 0

        for service_name, config in services_config.items():
            if service_name not in self.services:
                errors[service_name] = f"Service {service_name} not registered"
                continue

            try:
                service = self.services[service_name]
                method_name = config.get("method", "get_stock_info")
                method = getattr(service, method_name, None)

                if not method:
                    errors[service_name] = f"Method {method_name} not found"
                    continue

                # Call service method with configured parameters
                params = config.get("params", {})
                result = method(ticker, **params)

                results[service_name] = {
                    "data": result,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "method": method_name,
                }
                successful_sources += 1

            except Exception as e:
                error_msg = str(e)
                errors[service_name] = error_msg
                results[service_name] = {
                    "data": None,
                    "status": "error",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat(),
                }
                self.logger.error(f"Service {service_name} failed for {ticker}: {e}")

        # Calculate overall data quality
        total_sources = len(services_config)
        data_quality = successful_sources / total_sources if total_sources > 0 else 0.0

        # Determine overall status
        if data_quality >= 0.8:
            overall_status = "excellent"
        elif data_quality >= 0.6:
            overall_status = "good"
        elif data_quality >= 0.4:
            overall_status = "fair"
        else:
            overall_status = "poor"

        return {
            "ticker": ticker.upper(),
            "analysis_timestamp": datetime.now().isoformat(),
            "data_quality": {
                "overall_score": data_quality,
                "overall_status": overall_status,
                "successful_sources": successful_sources,
                "total_sources": total_sources,
                "success_rate": data_quality * 100,
            },
            "service_results": results,
            "errors": errors,
            "metadata": {
                "services_used": list(services_config.keys()),
                "orchestrator_version": "1.0.0",
            },
        }

    def health_check_all_services(self) -> dict[str, Any]:
        """Perform health check on all registered services"""
        health_results = {}

        for service_name, service in self.services.items():
            try:
                if hasattr(service, "health_check"):
                    result = service.health_check()
                    health_results[service_name] = {
                        "status": "healthy",
                        "details": result,
                    }
                else:
                    health_results[service_name] = {
                        "status": "unknown",
                        "details": {"error": "No health_check method available"},
                    }
            except Exception as e:
                health_results[service_name] = {
                    "status": "unhealthy",
                    "details": {"error": str(e)},
                }

        # Calculate overall health
        healthy_count = sum(1 for result in health_results.values() if result["status"] == "healthy")
        total_count = len(health_results)
        overall_health = "healthy" if healthy_count == total_count else "degraded"

        return {
            "overall_health": overall_health,
            "healthy_services": healthy_count,
            "total_services": total_count,
            "services": health_results,
            "timestamp": datetime.now().isoformat(),
        }

    def cleanup_all_caches(self) -> dict[str, Any]:
        """Clean up caches for all registered services"""
        cleanup_results = {}

        for service_name, service in self.services.items():
            try:
                if hasattr(service, "cleanup_cache"):
                    service.cleanup_cache()
                    cleanup_results[service_name] = "success"
                else:
                    cleanup_results[service_name] = "no_cache_cleanup_method"
            except Exception as e:
                cleanup_results[service_name] = f"error: {str(e)}"

        return {
            "cleanup_results": cleanup_results,
            "timestamp": datetime.now().isoformat(),
        }
