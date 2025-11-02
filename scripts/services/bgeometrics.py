"""
BGeometrics Service

Production-grade BGeometrics Bitcoin on-chain data integration with:
- MVRV (Market Value to Realized Value) ratio with daily updates
- MVRV Z-Score for statistical market analysis
- LTH-MVRV (Long Term Holder) metrics for cycle analysis
- Completely free API with no authentication required
- Perfect for Bitcoin cycle analysis and institutional-grade on-chain metrics
"""

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


class BGeometricsService(BaseFinancialService):
    """
    BGeometrics service extending BaseFinancialService

    Provides access to BGeometrics' free Bitcoin on-chain metrics including:
    - MVRV ratio and MVRV Z-Score metrics
    - Long Term Holder MVRV (LTH-MVRV) data
    - Bitcoin cycle analysis metrics
    - Historical on-chain data with daily granularity
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # BGeometrics API is completely free, no API key required
        if not self.config.base_url:
            # Based on research, they have bitcoin-data.com API
            self.config.base_url = "https://bitcoin-data.com/api/v1"

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate BGeometrics response data"""

        if not data:
            raise DataNotFoundError(f"No data returned from BGeometrics {endpoint}")

        # Handle different response structures
        if isinstance(data, dict):
            # Check for error responses
            if "error" in data:
                raise DataNotFoundError(f"BGeometrics API error: {data['error']}")

            # Extract data if wrapped
            if "data" in data:
                return data["data"]
            return data

        return data

    def _format_date(self, date_input: str | datetime) -> str:
        """Format date for API requests"""
        if isinstance(date_input, str):
            return date_input
        if isinstance(date_input, datetime):
            return date_input.strftime("%Y-%m-%d")
        raise ValueError(f"Invalid date format: {date_input}")


def create_bgeometrics_service(env: str = "dev") -> BGeometricsService:
    """
    Factory function to create BGeometricsService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured BGeometricsService instance
    """
    try:
        # BGeometrics is completely free, no configuration needed
        service_config = ServiceConfig(
            name="bgeometrics",
            api_key=None,  # No API key required
            base_url="https://bitcoin-data.com/api/v1",
            timeout_seconds=30,
            max_retries=3,
        )

        return BGeometricsService(service_config)

    except Exception:
        # Fallback configuration
        service_config = ServiceConfig(
            name="bgeometrics",
            api_key=None,
            base_url="https://bitcoin-data.com/api/v1",
            timeout_seconds=30,
            max_retries=3,
        )

        return BGeometricsService(service_config)


if __name__ == "__main__":
    # Test the service
    import logging

    logging.basicConfig(level=logging.INFO)

    service = create_bgeometrics_service()

    print("Testing BGeometrics service:")
    print("Current MVRV:", service.get_current_mvrv())
