#!/usr/bin/env python3
"""
Bitcoin Data Generators for Enhanced Schema Validation

Property-based testing data generators that create realistic Bitcoin data
for comprehensive schema validation and edge case testing.
"""

import random
from datetime import datetime, timedelta
from typing import Any


try:
    from hypothesis import strategies as st
    from hypothesis.strategies import (
        composite,
        datetimes,
        floats,
        integers,
        sampled_from,
        text,
    )

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Fallback implementations without hypothesis


class BitcoinDataGenerator:
    """Base class for Bitcoin-related data generators"""

    def __init__(self, seed: int | None = None):
        self.random = random.Random(seed)
        self.current_block_height = 850000  # Approximate current block height
        self.current_difficulty = 88104191118077.4
        self.current_hash_rate = 6.28e20

    def generate_bitcoin_address(self, address_type: str = "p2pkh") -> str:
        """Generate a realistic Bitcoin address"""
        if address_type == "p2pkh":
            # Legacy address starting with '1'
            return "1" + self._generate_base58_string(33)
        if address_type == "p2sh":
            # Script hash address starting with '3'
            return "3" + self._generate_base58_string(33)
        if address_type == "bech32":
            # Bech32 address starting with 'bc1'
            return "bc1q" + self._generate_hex_string(58)
        return self.generate_bitcoin_address("p2pkh")

    def generate_transaction_id(self) -> str:
        """Generate a realistic transaction ID (64-character hex)"""
        return self._generate_hex_string(64)

    def generate_block_hash(self) -> str:
        """Generate a realistic block hash (64-character hex with leading zeros)"""
        leading_zeros = self.random.randint(10, 19)  # Bitcoin blocks have many leading zeros
        hash_part = self._generate_hex_string(64 - leading_zeros)
        return "0" * leading_zeros + hash_part

    def generate_realistic_fee(self, fee_type: str = "normal") -> int:
        """Generate realistic Bitcoin transaction fees (sat/vB)"""
        fee_ranges = {
            "low": (1, 5),
            "economy": (6, 10),
            "normal": (11, 20),
            "high": (21, 50),
            "urgent": (51, 200),
        }
        min_fee, max_fee = fee_ranges.get(fee_type, fee_ranges["normal"])
        return self.random.randint(min_fee, max_fee)

    def generate_realistic_bitcoin_price(self) -> float:
        """Generate realistic Bitcoin price (USD)"""
        # Price range based on historical Bitcoin prices
        base_price = 50000
        variation = self.random.uniform(-0.3, 0.3)  # ±30% variation
        return round(base_price * (1 + variation), 2)

    def generate_block_height(self, deviation: int = 1000) -> int:
        """Generate realistic block height"""
        return self.current_block_height + self.random.randint(-deviation, deviation)

    def generate_timestamp(self, hours_ago: int = 24) -> int:
        """Generate realistic timestamp within specified hours"""
        now = datetime.now()
        past_time = now - timedelta(hours=self.random.randint(0, hours_ago))
        return int(past_time.timestamp())

    def _generate_hex_string(self, length: int) -> str:
        """Generate hex string of specified length"""
        return "".join(self.random.choices("0123456789abcdef", k=length))

    def _generate_base58_string(self, length: int) -> str:
        """Generate Base58 string (Bitcoin address format)"""
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return "".join(self.random.choices(base58_chars, k=length))


class MempoolSpaceDataGenerator(BitcoinDataGenerator):
    """Generator for Mempool.space API responses"""

    def generate_fee_estimates(self) -> dict[str, Any]:
        """Generate realistic fee estimates"""
        fastest = self.generate_realistic_fee("urgent")
        half_hour = self.generate_realistic_fee("high")
        hour = self.generate_realistic_fee("normal")
        economy = self.generate_realistic_fee("economy")
        minimum = self.generate_realistic_fee("low")

        return {
            "fastestFee": fastest,
            "halfHourFee": half_hour,
            "hourFee": hour,
            "economyFee": economy,
            "minimumFee": minimum,
        }

    def generate_mempool_info(self) -> dict[str, Any]:
        """Generate realistic mempool information"""
        return {
            "count": self.random.randint(20000, 80000),
            "vsize": self.random.randint(50000000, 200000000),
            "total_fee": self.random.randint(100000000, 500000000),
            "fee_histogram": [
                [self.generate_realistic_fee("low"), self.random.randint(5000, 20000)],
                [
                    self.generate_realistic_fee("economy"),
                    self.random.randint(3000, 15000),
                ],
                [
                    self.generate_realistic_fee("normal"),
                    self.random.randint(8000, 25000),
                ],
                [self.generate_realistic_fee("high"), self.random.randint(2000, 8000)],
                [self.generate_realistic_fee("urgent"), self.random.randint(500, 3000)],
            ],
        }

    def generate_recent_blocks(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate list of recent blocks"""
        blocks = []
        current_height = self.generate_block_height()

        for i in range(count):
            block = {
                "id": self.generate_block_hash(),
                "height": current_height - i,
                "version": 536870912,
                "timestamp": self.generate_timestamp(hours_ago=i * 1),
                "tx_count": self.random.randint(500, 3000),
                "size": self.random.randint(800000, 1400000),
                "weight": self.random.randint(3000000, 4000000),
                "merkle_root": self._generate_hex_string(64),
                "previousblockhash": self.generate_block_hash() if i < count - 1 else None,
                "mediantime": self.generate_timestamp(hours_ago=i * 1 + 1),
                "nonce": self.random.randint(1000000000, 4000000000),
                "bits": 386089497,
                "difficulty": self.current_difficulty,
                "chainwork": self._generate_hex_string(64),
                "nTx": self.random.randint(500, 3000),
            }
            blocks.append(block)

        return blocks

    def generate_transaction(self) -> dict[str, Any]:
        """Generate realistic Bitcoin transaction"""
        return {
            "txid": self.generate_transaction_id(),
            "version": 2,
            "locktime": 0,
            "size": self.random.randint(200, 1000),
            "weight": self.random.randint(800, 4000),
            "fee": self.random.randint(1000, 50000),  # satoshis
            "status": {
                "confirmed": self.random.choice([True, False]),
                "block_height": self.generate_block_height() if self.random.choice([True, False]) else None,
                "block_hash": self.generate_block_hash() if self.random.choice([True, False]) else None,
                "block_time": self.generate_timestamp() if self.random.choice([True, False]) else None,
            },
            "vin": [
                {
                    "txid": self.generate_transaction_id(),
                    "vout": self.random.randint(0, 5),
                    "prevout": {
                        "scriptpubkey": self._generate_hex_string(50),
                        "scriptpubkey_asm": "OP_DUP OP_HASH160 ... OP_EQUALVERIFY OP_CHECKSIG",
                        "scriptpubkey_type": "p2pkh",
                        "scriptpubkey_address": self.generate_bitcoin_address("p2pkh"),
                        "value": self.random.randint(100000, 10000000),  # satoshis
                    },
                }
            ],
            "vout": [
                {
                    "scriptpubkey": self._generate_hex_string(50),
                    "scriptpubkey_asm": "OP_DUP OP_HASH160 ... OP_EQUALVERIFY OP_CHECKSIG",
                    "scriptpubkey_type": "p2pkh",
                    "scriptpubkey_address": self.generate_bitcoin_address("p2pkh"),
                    "value": self.random.randint(50000, 5000000),  # satoshis
                }
            ],
        }


class BlockchainComDataGenerator(BitcoinDataGenerator):
    """Generator for Blockchain.com API responses"""

    def generate_latest_block(self) -> dict[str, Any]:
        """Generate realistic latest block data"""
        return {
            "hash": self.generate_block_hash(),
            "ver": 536870912,
            "prev_block": self.generate_block_hash(),
            "mrkl_root": self._generate_hex_string(64),
            "time": self.generate_timestamp(),
            "bits": 386089497,
            "fee": 0,
            "nonce": self.random.randint(1000000000, 4000000000),
            "n_tx": self.random.randint(1000, 4000),
            "size": self.random.randint(1000000, 1400000),
            "block_index": self.random.randint(800000, 900000),
            "main_chain": True,
            "height": self.generate_block_height(),
            "weight": self.random.randint(3500000, 4000000),
        }

    def generate_network_stats(self) -> dict[str, Any]:
        """Generate realistic network statistics"""
        return {
            "market_price_usd": self.generate_realistic_bitcoin_price(),
            "hash_rate": self.current_hash_rate * self.random.uniform(0.8, 1.2),
            "total_fees_btc": round(self.random.uniform(0.1, 0.3), 8),
            "n_btc_mined": 6.25,  # Current block reward
            "n_tx": self.random.randint(300000, 500000),
            "n_blocks_mined": 144,  # Approximately 144 blocks per day
            "minutes_between_blocks": round(self.random.uniform(8, 12), 2),
            "totalbc": 19500000 * 100000000,  # Total bitcoins in satoshis
            "n_blocks_total": self.generate_block_height(),
            "estimated_transaction_volume_usd": self.random.randint(1000000000, 5000000000),
            "blocks_size": self.random.randint(1000000000, 2000000000),
            "miners_revenue_usd": self.random.randint(10000000, 30000000),
            "nextretarget": self.generate_block_height() + self.random.randint(1000, 2000),
            "difficulty": self.current_difficulty,
            "estimated_btc_sent": self.random.randint(500000, 2000000),
            "miners_revenue_btc": self.random.randint(800, 1200),
            "total_btc_sent": self.random.randint(19000000, 19500000),
            "trade_volume_btc": self.random.uniform(50000, 150000),
            "trade_volume_usd": self.random.randint(1000000000, 3000000000),
        }


class AlternativeMeDataGenerator(BitcoinDataGenerator):
    """Generator for Alternative.me Fear & Greed API responses"""

    def generate_fear_greed_data(self, historical: bool = False) -> dict[str, Any]:
        """Generate Fear & Greed index data"""
        if historical:
            data_points = []
            for i in range(30):  # 30 days of data
                timestamp = int((datetime.now() - timedelta(days=i)).timestamp())
                value = self.random.randint(0, 100)
                classification = self._classify_fear_greed(value)

                data_points.append(
                    {
                        "value": str(value),
                        "value_classification": classification,
                        "timestamp": str(timestamp),
                        "time_until_update": str(self.random.randint(3600, 86400)),
                    }
                )

            return {
                "name": "Fear and Greed Index",
                "data": data_points,
                "metadata": {"error": None},
            }
        value = self.random.randint(0, 100)
        return {
            "name": "Fear and Greed Index",
            "data": [
                {
                    "value": str(value),
                    "value_classification": self._classify_fear_greed(value),
                    "timestamp": str(int(datetime.now().timestamp())),
                    "time_until_update": str(self.random.randint(3600, 86400)),
                }
            ],
            "metadata": {"error": None},
        }

    def _classify_fear_greed(self, value: int) -> str:
        """Classify fear & greed value"""
        if value <= 25:
            return "Extreme Fear"
        if value <= 45:
            return "Fear"
        if value <= 55:
            return "Neutral"
        if value <= 75:
            return "Greed"
        return "Extreme Greed"


class BinanceAPIDataGenerator(BitcoinDataGenerator):
    """Generator for Binance API responses"""

    def generate_24hr_ticker(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        """Generate 24hr ticker statistics"""
        base_price = self.generate_realistic_bitcoin_price()
        price_change = base_price * self.random.uniform(-0.05, 0.05)  # ±5% daily change

        return {
            "symbol": symbol,
            "priceChange": f"{price_change:.2f}",
            "priceChangePercent": f"{(price_change / base_price) * 100:.2f}",
            "weightedAvgPrice": f"{base_price + self.random.uniform(-1000, 1000):.2f}",
            "prevClosePrice": f"{base_price - price_change:.2f}",
            "lastPrice": f"{base_price:.2f}",
            "lastQty": f"{self.random.uniform(0.001, 1.0):.8f}",
            "bidPrice": f"{base_price - self.random.uniform(1, 10):.2f}",
            "askPrice": f"{base_price + self.random.uniform(1, 10):.2f}",
            "openPrice": f"{base_price - price_change:.2f}",
            "highPrice": f"{base_price + self.random.uniform(500, 2000):.2f}",
            "lowPrice": f"{base_price - self.random.uniform(500, 2000):.2f}",
            "volume": f"{self.random.uniform(10000, 50000):.8f}",
            "quoteVolume": f"{self.random.uniform(500000000, 2000000000):.2f}",
            "openTime": int((datetime.now() - timedelta(hours=24)).timestamp() * 1000),
            "closeTime": int(datetime.now().timestamp() * 1000),
            "firstId": self.random.randint(1000000000, 2000000000),
            "lastId": self.random.randint(2000000000, 3000000000),
            "count": self.random.randint(500000, 2000000),
        }

    def generate_server_time(self) -> dict[str, Any]:
        """Generate server time response"""
        return {"serverTime": int(datetime.now().timestamp() * 1000)}

    def generate_price_ticker(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        """Generate simple price ticker"""
        return {
            "symbol": symbol,
            "price": f"{self.generate_realistic_bitcoin_price():.2f}",
        }


class CoinMetricsDataGenerator(BitcoinDataGenerator):
    """Generator for CoinMetrics API responses"""

    def generate_asset_metrics(self, asset: str = "btc", metrics: list[str] = None) -> dict[str, Any]:
        """Generate asset metrics data"""
        if metrics is None:
            metrics = ["PriceUSD", "CapMrktCurUSD", "TxCnt", "AdrActCnt"]

        data_points = []
        for i in range(30):  # 30 days of data
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            data_point = {"asset": asset, "time": date}

            for metric in metrics:
                if metric == "PriceUSD":
                    data_point[metric] = str(self.generate_realistic_bitcoin_price())
                elif metric == "CapMrktCurUSD":
                    market_cap = self.generate_realistic_bitcoin_price() * 19500000  # Approximate BTC supply
                    data_point[metric] = str(int(market_cap))
                elif metric == "TxCnt":
                    data_point[metric] = str(self.random.randint(250000, 400000))
                elif metric == "AdrActCnt":
                    data_point[metric] = str(self.random.randint(800000, 1200000))
                else:
                    data_point[metric] = str(self.random.uniform(1, 1000000))

            data_points.append(data_point)

        return {"data": data_points}

    def generate_supported_assets(self) -> list[dict[str, Any]]:
        """Generate supported assets list"""
        return [
            {"asset": "btc", "full_name": "Bitcoin"},
            {"asset": "eth", "full_name": "Ethereum"},
            {"asset": "ltc", "full_name": "Litecoin"},
            {"asset": "xrp", "full_name": "XRP"},
            {"asset": "bch", "full_name": "Bitcoin Cash"},
        ]


class BitcoinSchemaTestDataGenerator:
    """High-level generator for Bitcoin schema validation testing"""

    def __init__(self, seed: int | None = None):
        self.mempool_generator = MempoolSpaceDataGenerator(seed)
        self.blockchain_generator = BlockchainComDataGenerator(seed)
        self.alternative_generator = AlternativeMeDataGenerator(seed)
        self.binance_generator = BinanceAPIDataGenerator(seed)
        self.coinmetrics_generator = CoinMetricsDataGenerator(seed)

    def generate_discovery_schema_data(self, service_names: list[str]) -> dict[str, Any]:
        """Generate data for discovery schema validation"""
        analysis_date = datetime.now().strftime("%Y-%m-%d")

        data = {
            "analysis_date": analysis_date,
            "data_sources": {},
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_sources": len(service_names),
                "data_quality": "synthetic",
            },
        }

        for service_name in service_names:
            if service_name == "mempool_space_cli":
                data["data_sources"][service_name] = {
                    "fee_estimates": self.mempool_generator.generate_fee_estimates(),
                    "mempool_info": self.mempool_generator.generate_mempool_info(),
                    "recent_blocks": self.mempool_generator.generate_recent_blocks(5),
                }
            elif service_name == "blockchain_com_cli":
                data["data_sources"][service_name] = {
                    "latest_block": self.blockchain_generator.generate_latest_block(),
                    "network_stats": self.blockchain_generator.generate_network_stats(),
                }
            elif service_name == "alternative_me_cli":
                data["data_sources"][service_name] = {
                    "fear_greed": self.alternative_generator.generate_fear_greed_data(),
                    "historical": self.alternative_generator.generate_fear_greed_data(historical=True),
                }
            elif service_name == "binance_api_cli":
                data["data_sources"][service_name] = {
                    "btc_ticker": self.binance_generator.generate_24hr_ticker(),
                    "server_time": self.binance_generator.generate_server_time(),
                }
            elif service_name == "coinmetrics_cli":
                data["data_sources"][service_name] = {
                    "btc_metrics": self.coinmetrics_generator.generate_asset_metrics(),
                    "supported_assets": self.coinmetrics_generator.generate_supported_assets(),
                }

        return data

    def generate_edge_case_data(self) -> dict[str, Any]:
        """Generate edge case data for robust testing"""
        return {
            "empty_responses": {},
            "null_values": {"price": None, "timestamp": None, "block_hash": None},
            "extreme_values": {
                "very_high_fee": 10000,  # 10,000 sat/vB
                "very_low_fee": 0.1,
                "extreme_fear": 0,
                "extreme_greed": 100,
                "high_block_height": 2000000,
                "negative_price": -100.50,
            },
            "malformed_data": {
                "invalid_hash": "not_a_valid_hash",
                "invalid_address": "invalid_bitcoin_address",
                "invalid_timestamp": "not_a_timestamp",
                "invalid_json": "{incomplete json",
                "wrong_data_types": {
                    "price_as_string": "fifty_thousand",
                    "height_as_float": 850000.5,
                    "boolean_as_string": "true",
                },
            },
        }


# Convenience functions for quick data generation
def generate_bitcoin_discovery_data(services: list[str] = None, seed: int = None) -> dict[str, Any]:
    """Quick function to generate Bitcoin discovery schema data"""
    if services is None:
        services = [
            "mempool_space_cli",
            "blockchain_com_cli",
            "alternative_me_cli",
            "binance_api_cli",
            "coinmetrics_cli",
        ]

    generator = BitcoinSchemaTestDataGenerator(seed)
    return generator.generate_discovery_schema_data(services)


def generate_bitcoin_edge_cases(seed: int = None) -> dict[str, Any]:
    """Quick function to generate edge case data"""
    generator = BitcoinSchemaTestDataGenerator(seed)
    return generator.generate_edge_case_data()


# Export all generators
__all__ = [
    "BitcoinDataGenerator",
    "MempoolSpaceDataGenerator",
    "BlockchainComDataGenerator",
    "AlternativeMeDataGenerator",
    "BinanceAPIDataGenerator",
    "CoinMetricsDataGenerator",
    "BitcoinSchemaTestDataGenerator",
    "generate_bitcoin_discovery_data",
    "generate_bitcoin_edge_cases",
]
