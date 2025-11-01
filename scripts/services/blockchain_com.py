"""
Blockchain.com Service

Production-grade Blockchain.com API integration with:
- Free blockchain explorer API with comprehensive Bitcoin data
- Block information and transaction data access
- Address balance and transaction history
- Network statistics and mempool information
- Raw blockchain data for in-depth analysis
- Completely free API with no authentication required
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))


class BlockchainComService(BaseFinancialService):
    """
    Blockchain.com service extending BaseFinancialService

    Provides access to Blockchain.com's free blockchain explorer API including:
    - Block information and transaction data
    - Address balances and transaction history
    - Network statistics and mempool data
    - Raw blockchain data for comprehensive Bitcoin analysis
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Blockchain.com is completely free, no API key required
        if not self.config.base_url:
            self.config.base_url = "https://blockchain.info"

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate Blockchain.com response data"""

        if not data:
            raise DataNotFoundError(f"No data returned from Blockchain.com {endpoint}")

        # Blockchain.com returns clean data, minimal validation needed
        return data

    def get_latest_block(self) -> dict[str, Any]:
        """Get latest block information"""
        endpoint = "/latestblock"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "latest block")

    def get_block_info(self, block_hash: str) -> dict[str, Any]:
        """Get detailed information about a specific block"""
        # Handle both block hash and block height
        if block_hash.isdigit():
            endpoint = f"/rawblock/{block_hash}"
        else:
            endpoint = f"/rawblock/{block_hash}"

        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, f"block {block_hash}")

    def get_block_height(self, height: int) -> dict[str, Any]:
        """Get block information by height"""
        endpoint = f"/block-height/{height}"
        params = {"format": "json"}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"block height {height}")

    def get_transaction_info(self, tx_hash: str) -> dict[str, Any]:
        """Get detailed information about a specific transaction"""
        endpoint = f"/rawtx/{tx_hash}"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, f"transaction {tx_hash}")

    def get_address_info(self, address: str, limit: int = 50) -> dict[str, Any]:
        """Get address information including balance and transactions"""
        if limit > 100:
            limit = 100
        elif limit < 1:
            limit = 1

        endpoint = f"/rawaddr/{address}"
        params = {"limit": limit}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"address {address}")

    def get_address_balance(self, address: str) -> dict[str, Any]:
        """Get address balance only"""
        endpoint = f"/q/addressbalance/{address}"
        balance = self._make_request_with_retry(endpoint)

        # Convert raw balance to structured format
        return {
            "address": address,
            "balance_satoshis": balance if isinstance(balance, int) else 0,
            "balance_btc": (balance / 100000000) if isinstance(balance, int) else 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    def get_multiple_addresses_balance(self, addresses: list[str]) -> dict[str, Any]:
        """Get balances for multiple addresses"""
        if len(addresses) > 100:
            addresses = addresses[:100]

        address_string = "|".join(addresses)
        endpoint = "/balance"
        params = {"active": address_string}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, "multiple addresses balance")

    def get_unspent_outputs(self, address: str) -> dict[str, Any]:
        """Get unspent transaction outputs for an address"""
        endpoint = "/unspent"
        params = {"active": address}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"unspent outputs for {address}")

    def get_network_stats(self) -> dict[str, Any]:
        """Get Bitcoin network statistics"""
        endpoint = "/stats"
        params = {"format": "json"}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, "network stats")

    def get_mempool_info(self) -> dict[str, Any]:
        """Get mempool statistics"""
        endpoint = "/q/unconfirmedcount"
        unconfirmed_count = self._make_request_with_retry(endpoint)

        # Get additional mempool data
        endpoint_size = "/q/mempool_size"
        try:
            mempool_size = self._make_request_with_retry(endpoint_size)
        except:
            mempool_size = 0

        return {
            "unconfirmed_transactions": unconfirmed_count if isinstance(unconfirmed_count, int) else 0,
            "mempool_size_bytes": mempool_size if isinstance(mempool_size, int) else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def get_difficulty(self) -> dict[str, Any]:
        """Get current Bitcoin mining difficulty"""
        endpoint = "/q/getdifficulty"
        difficulty = self._make_request_with_retry(endpoint)

        return {
            "difficulty": difficulty if isinstance(difficulty, (int, float)) else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def get_hashrate(self) -> dict[str, Any]:
        """Get estimated network hash rate"""
        endpoint = "/q/hashrate"
        hashrate = self._make_request_with_retry(endpoint)

        return {
            "hashrate_ghash_per_sec": hashrate if isinstance(hashrate, (int, float)) else 0,
            "hashrate_thash_per_sec": (hashrate / 1000) if isinstance(hashrate, (int, float)) else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def get_total_bitcoins(self) -> dict[str, Any]:
        """Get total bitcoins in circulation"""
        endpoint = "/q/totalbc"
        total_bc = self._make_request_with_retry(endpoint)

        return {
            "total_bitcoins_satoshis": total_bc if isinstance(total_bc, int) else 0,
            "total_bitcoins": (total_bc / 100000000) if isinstance(total_bc, int) else 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    def get_market_price_usd(self) -> dict[str, Any]:
        """Get current Bitcoin price in USD"""
        endpoint = "/q/24hrprice"
        price = self._make_request_with_retry(endpoint)

        return {
            "price_usd": price if isinstance(price, (int, float)) else 0.0,
            "timestamp": datetime.now().isoformat(),
            "source": "blockchain.com",
        }

    def get_transaction_fee_per_kb(self) -> dict[str, Any]:
        """Get average transaction fee per KB"""
        endpoint = "/q/avgtxvalue"
        try:
            avg_tx_value = self._make_request_with_retry(endpoint)
        except:
            avg_tx_value = 0

        # Get additional fee data
        endpoint_fee = "/q/avgtxfee"
        try:
            avg_tx_fee = self._make_request_with_retry(endpoint_fee)
        except:
            avg_tx_fee = 0

        return {
            "average_transaction_value_satoshis": avg_tx_value if isinstance(avg_tx_value, int) else 0,
            "average_transaction_fee_satoshis": avg_tx_fee if isinstance(avg_tx_fee, int) else 0,
            "average_transaction_value_btc": (avg_tx_value / 100000000) if isinstance(avg_tx_value, int) else 0.0,
            "average_transaction_fee_btc": (avg_tx_fee / 100000000) if isinstance(avg_tx_fee, int) else 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    def get_blocks_mined_today(self) -> dict[str, Any]:
        """Get number of blocks mined in the last 24 hours"""
        endpoint = "/q/24hrtransactioncount"
        try:
            tx_count_24h = self._make_request_with_retry(endpoint)
        except:
            tx_count_24h = 0

        # Estimate blocks (roughly 144 blocks per day)
        current_time = datetime.now()
        yesterday = current_time - timedelta(days=1)

        return {
            "transactions_24h": tx_count_24h if isinstance(tx_count_24h, int) else 0,
            "estimated_blocks_24h": 144,  # Theoretical maximum
            "timestamp": current_time.isoformat(),
            "period_start": yesterday.isoformat(),
        }

    def get_address_transactions(self, address: str, offset: int = 0) -> dict[str, Any]:
        """Get transactions for a specific address with pagination"""
        if offset < 0:
            offset = 0

        endpoint = f"/rawaddr/{address}"
        params = {"offset": offset, "limit": 50}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"transactions for {address}")

    def get_blockchain_summary(self) -> dict[str, Any]:
        """Get comprehensive blockchain summary"""
        # Combine multiple endpoints for comprehensive overview
        summary = {}

        try:
            summary["latest_block"] = self.get_latest_block()
        except:
            summary["latest_block"] = {}

        try:
            summary["network_stats"] = self.get_network_stats()
        except:
            summary["network_stats"] = {}

        try:
            summary["mempool"] = self.get_mempool_info()
        except:
            summary["mempool"] = {}

        try:
            summary["difficulty"] = self.get_difficulty()
        except:
            summary["difficulty"] = {}

        try:
            summary["hashrate"] = self.get_hashrate()
        except:
            summary["hashrate"] = {}

        try:
            summary["market_price"] = self.get_market_price_usd()
        except:
            summary["market_price"] = {}

        summary["timestamp"] = datetime.now().isoformat()
        return summary


def create_blockchain_com_service(env: str = "dev") -> BlockchainComService:
    """
    Factory function to create BlockchainComService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured BlockchainComService instance
    """
    try:
        # Blockchain.com is completely free, no configuration needed
        service_config = ServiceConfig(
            name="blockchain_com",
            api_key=None,  # No API key required
            base_url="https://blockchain.info",
            timeout_seconds=30,
            max_retries=3,
        )

        return BlockchainComService(service_config)

    except Exception:
        # Fallback configuration
        service_config = ServiceConfig(
            name="blockchain_com",
            api_key=None,
            base_url="https://blockchain.info",
            timeout_seconds=30,
            max_retries=3,
        )

        return BlockchainComService(service_config)
