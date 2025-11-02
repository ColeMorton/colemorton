"""
Mempool.space Service

Production-grade Mempool.space Bitcoin blockchain data integration with:
- Real-time Bitcoin mempool monitoring and fee estimation
- Block data and transaction analysis
- Mining statistics and hash rate information
- Network health metrics and confirmation tracking
- Lightning Network statistics and node information
- Completely free API with no authentication required
"""

import sys
from pathlib import Path
from typing import Any

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config_loader import ConfigLoader


class MempoolSpaceService(BaseFinancialService):
    """
    Mempool.space service extending BaseFinancialService

    Provides access to Mempool.space's comprehensive Bitcoin blockchain data including:
    - Real-time mempool monitoring and fee estimation
    - Block data and transaction analysis
    - Mining statistics and hash rate information
    - Network health metrics and Lightning Network data
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Mempool.space is completely free, no API key required
        # Base URL is https://mempool.space/api/
        if not self.config.base_url:
            self.config.base_url = "https://mempool.space/api"

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate Mempool.space response data"""

        if not data:
            raise DataNotFoundError(f"No data returned from Mempool.space {endpoint}")

        # Mempool.space returns clean data, minimal validation needed
        return data

    def get_fee_estimates(self) -> dict[str, Any]:
        """Get recommended Bitcoin transaction fees"""
        endpoint = "/v1/fees/recommended"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "fee estimates")

    def get_mempool_info(self) -> dict[str, Any]:
        """Get current mempool statistics"""
        endpoint = "/mempool"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "mempool info")

    def get_recent_blocks(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent Bitcoin blocks"""
        if limit > 25:
            limit = 25

        endpoint = "/v1/blocks"
        data = self._make_request_with_retry(endpoint)

        if isinstance(data, list):
            return data[:limit]
        return self._validate_response(data, "recent blocks")

    def get_block_info(self, block_hash: str) -> dict[str, Any]:
        """Get detailed information about a specific block"""
        # Handle both block hash and block height
        if block_hash.isdigit():
            endpoint = f"/v1/block-height/{block_hash}"
            # First get the hash for the height
            block_hash = self._make_request_with_retry(endpoint)
            if isinstance(block_hash, str):
                endpoint = f"/v1/block/{block_hash}"
            else:
                raise DataNotFoundError(f"Block height {block_hash} not found")
        else:
            endpoint = f"/v1/block/{block_hash}"

        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, f"block {block_hash}")

    def get_transaction_info(self, txid: str) -> dict[str, Any]:
        """Get detailed information about a Bitcoin transaction"""
        endpoint = f"/tx/{txid}"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, f"transaction {txid}")

    def get_difficulty_info(self) -> dict[str, Any]:
        """Get Bitcoin mining difficulty information"""
        endpoint = "/v1/difficulty-adjustment"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "difficulty info")

    def get_hashrate_info(self, timeframe: str = "1w") -> list[dict[str, Any]]:
        """Get Bitcoin network hash rate statistics"""
        # Validate timeframe
        valid_timeframes = ["1d", "1w", "1m", "3m", "6m", "1y", "2y", "3y"]
        if timeframe not in valid_timeframes:
            timeframe = "1w"

        endpoint = f"/v1/mining/hashrate/{timeframe}"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, f"hashrate {timeframe}")

    def get_bitcoin_price(self) -> dict[str, Any]:
        """Get current Bitcoin price from Mempool.space"""
        endpoint = "/v1/prices"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "Bitcoin price")

    def get_address_info(self, address: str) -> dict[str, Any]:
        """Get information about a Bitcoin address"""
        endpoint = f"/address/{address}"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, f"address {address}")

    def get_lightning_stats(self) -> dict[str, Any]:
        """Get Lightning Network statistics"""
        endpoint = "/v1/lightning/statistics/latest"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "Lightning Network stats")

    def get_network_stats(self) -> dict[str, Any]:
        """Get comprehensive Bitcoin network statistics"""
        # Combine multiple endpoints for comprehensive network health
        stats = {
            "mempool": self.get_mempool_info(),
            "fees": self.get_fee_estimates(),
            "difficulty": self.get_difficulty_info(),
            "hashrate_1w": self.get_hashrate_info("1w"),
            "price": self.get_bitcoin_price(),
            "lightning": self.get_lightning_stats(),
        }
        return stats


def create_mempool_space_service(env: str = "dev") -> MempoolSpaceService:
    """
    Factory function to create MempoolSpaceService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured MempoolSpaceService instance
    """
    try:
        # Load configuration
        config_loader = ConfigLoader()

        # Create service config - Mempool.space is free, no API key needed
        service_config = ServiceConfig(
            name="mempool_space",
            api_key=None,  # No API key required
            base_url="https://mempool.space/api",
            timeout_seconds=30,
            max_retries=3,
        )

        return MempoolSpaceService(service_config)

    except Exception:
        # Fallback configuration
        service_config = ServiceConfig(
            name="mempool_space",
            api_key=None,
            base_url="https://mempool.space/api",
            timeout_seconds=30,
            max_retries=3,
        )

        return MempoolSpaceService(service_config)
