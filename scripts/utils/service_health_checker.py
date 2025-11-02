#!/usr/bin/env python3
"""
Service Health Check and Fallback Mechanisms

Provides health monitoring for financial data services with graceful fallback options.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ServiceHealthChecker:
    """Health checker for financial data services with fallback mechanisms"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.services = {}
        self.fallback_data = {}

    def check_yahoo_finance_service(self) -> dict[str, Any]:
        """Check Yahoo Finance CLI service health"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "services"))
            from yahoo_finance import create_yahoo_finance_service

            service = create_yahoo_finance_service("prod")
            health = service.health_check()

            return {
                "service": "yahoo_finance",
                "status": health.get("status", "unknown"),
                "operational": health.get("status") == "healthy",
                "timestamp": datetime.now().isoformat(),
                "details": health,
            }
        except Exception as e:
            return {
                "service": "yahoo_finance",
                "status": "unhealthy",
                "operational": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def check_all_services(self) -> dict[str, Any]:
        """Check health of all available services"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_health": True,
            "operational_count": 0,
            "total_count": 0,
        }

        # Check Yahoo Finance
        yf_health = self.check_yahoo_finance_service()
        results["services"]["yahoo_finance"] = yf_health
        results["total_count"] += 1

        if yf_health["operational"]:
            results["operational_count"] += 1
        else:
            results["overall_health"] = False

        # Add placeholder for other services
        services_to_implement = ["sec_edgar", "fred_economic", "alpha_vantage"]
        for service in services_to_implement:
            results["services"][service] = {
                "service": service,
                "status": "not_implemented",
                "operational": False,
                "timestamp": datetime.now().isoformat(),
            }
            results["total_count"] += 1
            results["overall_health"] = False

        results["health_percentage"] = (results["operational_count"] / results["total_count"]) * 100

        return results

    def get_fallback_data(self, data_type: str, symbol: str = None) -> dict[str, Any] | None:
        """Get fallback data when services are unavailable"""
        fallback_templates = {
            "stock_quote": {
                "symbol": symbol or "UNKNOWN",
                "name": f"{symbol or 'UNKNOWN'} Inc.",
                "current_price": None,
                "market_cap": None,
                "pe_ratio": None,
                "sector": "Unknown",
                "industry": "Unknown",
                "timestamp": datetime.now().isoformat(),
                "data_quality": "fallback_template",
                "warning": "Real-time data unavailable - using fallback template",
            }
        }

        return fallback_templates.get(data_type)

    def validate_with_fallback(self, data_type: str, symbol: str = None) -> dict[str, Any]:
        """Attempt validation with fallback on failure"""
        health_check = self.check_all_services()

        if health_check["services"]["yahoo_finance"]["operational"]:
            try:
                # Attempt to get real data
                sys.path.insert(0, str(Path(__file__).parent.parent / "services"))
                from yahoo_finance import create_yahoo_finance_service

                service = create_yahoo_finance_service("prod")

                if data_type == "stock_quote" and symbol:
                    result = service.get_stock_info(symbol)
                    result["data_quality"] = "real_time"
                    result["service_status"] = "operational"
                    return result

            except Exception as e:
                self.logger.warning(f"Real-time data failed for {symbol}: {e}")

        # Fall back to template data
        fallback = self.get_fallback_data(data_type, symbol)
        if fallback:
            fallback["fallback_reason"] = "Service unavailable or failed"
            return fallback

        return {
            "error": f"No data available for {data_type}",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """CLI interface for service health checking"""
    import argparse

    parser = argparse.ArgumentParser(description="Service Health Checker")
    parser.add_argument("command", choices=["health", "validate"], help="Command to execute")
    parser.add_argument("--symbol", help="Stock symbol for validation")
    parser.add_argument("--data-type", default="stock_quote", help="Data type for validation")
    parser.add_argument("--output-format", default="json", choices=["json"], help="Output format")

    args = parser.parse_args()

    checker = ServiceHealthChecker()

    try:
        if args.command == "health":
            result = checker.check_all_services()
        elif args.command == "validate":
            result = checker.validate_with_fallback(args.data_type, args.symbol)

        if args.output_format == "json":
            print(json.dumps(result, indent=2, default=str))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
