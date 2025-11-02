#!/usr/bin/env python3
"""
Test Utilities for Bitcoin CLI Services

Provides mock implementations, fixtures, and test doubles for isolated testing
of Bitcoin CLI services without external API dependencies.
"""

import json
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, Mock

import requests


class MockResponse:
    """Mock HTTP response object"""

    def __init__(self, json_data: dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code} Error")


class BitcoinTestFixtures:
    """Test fixtures with realistic Bitcoin data"""

    @staticmethod
    def mempool_space_fee_estimates():
        """Mock fee estimates from Mempool.space"""
        return {
            "fastestFee": 15,
            "halfHourFee": 12,
            "hourFee": 10,
            "economyFee": 8,
            "minimumFee": 6,
        }

    @staticmethod
    def mempool_space_mempool_info():
        """Mock mempool info from Mempool.space"""
        return {
            "count": 45821,
            "vsize": 128472983,
            "total_fee": 185294738,
            "fee_histogram": [
                [6, 12485],
                [8, 8294],
                [10, 15847],
                [12, 6582],
                [15, 2613],
            ],
        }

    @staticmethod
    def mempool_space_network_stats():
        """Mock network stats from Mempool.space"""
        return {
            "mempool": BitcoinTestFixtures.mempool_space_mempool_info(),
            "fees": BitcoinTestFixtures.mempool_space_fee_estimates(),
            "difficulty": 88104191118077.4,
            "hashrate_1w": 6.28e20,
            "price": 65429.50,
        }

    @staticmethod
    def blockchain_com_latest_block():
        """Mock latest block from Blockchain.com"""
        return {
            "hash": "000000000000000000024b1e2c1c5d8f4b2a3c1d5e6f7a8b9c0d1e2f3a4b5c6d",
            "ver": 536870912,
            "prev_block": "0000000000000000000123a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4",
            "mrkl_root": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
            "time": int(datetime.now().timestamp()),
            "bits": 386089497,
            "fee": 0,
            "nonce": 3654651744,
            "n_tx": 2847,
            "size": 1247583,
            "block_index": 850000,
            "main_chain": True,
            "height": 850000,
            "weight": 3993156,
        }

    @staticmethod
    def blockchain_com_network_stats():
        """Mock network stats from Blockchain.com"""
        return {
            "market_price_usd": 65432.15,
            "hash_rate": 628000000000000000000,
            "total_fees_btc": 0.15847291,
            "n_btc_mined": 6.25,
            "n_tx": 285947,
            "n_blocks_mined": 144,
            "minutes_between_blocks": 10.2,
            "totalbc": 1968437500000000,
            "n_blocks_total": 850000,
            "estimated_transaction_volume_usd": 12845792834.67,
            "blocks_size": 179287463,
            "miners_revenue_usd": 42847291.67,
            "nextretarget": 851008,
            "difficulty": 88104191118077,
            "estimated_btc_sent": 285947.15847291,
            "miners_revenue_btc": 655.15847291,
            "total_btc_sent": 285947158472.91,
            "trade_volume_btc": 15847.29,
            "trade_volume_usd": 1037582943.67,
        }

    @staticmethod
    def coinmetrics_network_data():
        """Mock network data from CoinMetrics"""
        base_date = datetime.now() - timedelta(days=7)
        return [
            {
                "asset": "btc",
                "time": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "AdrActCnt": 850000 + i * 1000,
                "BlkCnt": 144,
                "TxCnt": 285000 + i * 500,
                "TxTfrValUSD": 12000000000 + i * 100000000,
            }
            for i in range(8)
        ]

    @staticmethod
    def coinmetrics_market_data():
        """Mock market data from CoinMetrics"""
        base_date = datetime.now() - timedelta(days=7)
        return [
            {
                "asset": "btc",
                "time": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "PriceUSD": 65000 + i * 100,
                "CapMrktCurUSD": 1280000000000 + i * 1000000000,
                "VolTrusted24hUSD": 15000000000 + i * 50000000,
            }
            for i in range(8)
        ]

    @staticmethod
    def coinmetrics_mining_data():
        """Mock mining data from CoinMetrics"""
        base_date = datetime.now() - timedelta(days=7)
        return [
            {
                "asset": "btc",
                "time": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "HashRate": 6.28e20 + i * 1e18,
                "DiffMean": 88104191118077 + i * 1000000000,
                "BlkCnt": 144,
                "RevUSD": 42000000 + i * 100000,
                "FeeMeanUSD": 15.5 + i * 0.5,
            }
            for i in range(8)
        ]

    @staticmethod
    def alternative_me_fear_greed():
        """Mock Fear & Greed index from Alternative.me"""
        return {
            "data": [
                {
                    "value": "45",
                    "value_classification": "Fear",
                    "timestamp": str(int(datetime.now().timestamp())),
                    "time_until_update": "18472",
                }
            ]
        }

    @staticmethod
    def alternative_me_historical_fear_greed():
        """Mock historical Fear & Greed data"""
        base_timestamp = int(datetime.now().timestamp())
        return {
            "data": [
                {
                    "value": str(45 + i),
                    "value_classification": "Neutral" if 40 < (45 + i) < 60 else "Fear",
                    "timestamp": str(base_timestamp - i * 86400),  # Daily intervals
                    "time_until_update": "0",
                }
                for i in range(30)
            ]
        }

    @staticmethod
    def binance_exchange_info():
        """Mock exchange info from Binance"""
        return {
            "timezone": "UTC",
            "serverTime": int(datetime.now().timestamp() * 1000),
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "baseAsset": "BTC",
                    "quoteAsset": "USDT",
                    "baseAssetPrecision": 8,
                    "quotePrecision": 8,
                    "quoteAssetPrecision": 8,
                    "orderTypes": [
                        "LIMIT",
                        "LIMIT_MAKER",
                        "MARKET",
                        "STOP_LOSS_LIMIT",
                        "TAKE_PROFIT_LIMIT",
                    ],
                    "icebergAllowed": True,
                    "ocoAllowed": True,
                    "isSpotTradingAllowed": True,
                    "isMarginTradingAllowed": True,
                    "permissions": ["SPOT", "MARGIN"],
                }
            ],
        }

    @staticmethod
    def binance_24hr_ticker():
        """Mock 24hr ticker from Binance"""
        return {
            "symbol": "BTCUSDT",
            "priceChange": "1250.75000000",
            "priceChangePercent": "1.95",
            "weightedAvgPrice": "65125.42315789",
            "prevClosePrice": "64175.25000000",
            "lastPrice": "65426.00000000",
            "lastQty": "0.00158700",
            "bidPrice": "65425.99000000",
            "askPrice": "65426.00000000",
            "openPrice": "64175.25000000",
            "highPrice": "66250.00000000",
            "lowPrice": "63825.15000000",
            "volume": "28547.15847291",
            "quoteVolume": "1858472914.67284300",
            "openTime": int((datetime.now() - timedelta(hours=24)).timestamp() * 1000),
            "closeTime": int(datetime.now().timestamp() * 1000),
            "firstId": 3254761928,
            "lastId": 3254847295,
            "count": 85368,
        }


class MockServiceFactory:
    """Factory for creating mock services"""

    @staticmethod
    def create_mock_mempool_service():
        """Create mock Mempool.space service"""
        mock_service = MagicMock()
        mock_service.get_fee_estimates.return_value = BitcoinTestFixtures.mempool_space_fee_estimates()
        mock_service.get_mempool_info.return_value = BitcoinTestFixtures.mempool_space_mempool_info()
        mock_service.get_network_stats.return_value = BitcoinTestFixtures.mempool_space_network_stats()
        mock_service.get_bitcoin_price.return_value = {"price": 65429.50}
        mock_service.get_difficulty_info.return_value = {"difficulty": 88104191118077.4}
        mock_service.get_hashrate_info.return_value = {"hashrate": 6.28e20}
        return mock_service

    @staticmethod
    def create_mock_blockchain_service():
        """Create mock Blockchain.com service"""
        mock_service = MagicMock()
        mock_service.get_latest_block.return_value = BitcoinTestFixtures.blockchain_com_latest_block()
        mock_service.get_network_stats.return_value = BitcoinTestFixtures.blockchain_com_network_stats()
        mock_service.get_blockchain_summary.return_value = {
            "network_stats": BitcoinTestFixtures.blockchain_com_network_stats(),
            "difficulty": 88104191118077,
            "hashrate": 628000000000000000000,
            "market_price": 65432.15,
        }
        mock_service.get_market_price_usd.return_value = {"price": 65432.15}
        mock_service.get_mempool_info.return_value = {"count": 45821, "size": 128472983}
        mock_service.get_difficulty.return_value = {"difficulty": 88104191118077}
        mock_service.get_hashrate.return_value = {"hashrate": 628000000000000000000}
        mock_service.get_total_bitcoins.return_value = {"total": 19684375}
        return mock_service

    @staticmethod
    def create_mock_coinmetrics_service():
        """Create mock CoinMetrics service"""
        mock_service = MagicMock()
        mock_service.get_network_data.return_value = BitcoinTestFixtures.coinmetrics_network_data()
        mock_service.get_market_data.return_value = BitcoinTestFixtures.coinmetrics_market_data()
        mock_service.get_mining_data.return_value = BitcoinTestFixtures.coinmetrics_mining_data()
        mock_service.get_supported_assets.return_value = [{"asset": "btc", "name": "Bitcoin"}]
        return mock_service

    @staticmethod
    def create_mock_alternative_me_service():
        """Create mock Alternative.me service"""
        mock_service = MagicMock()
        mock_service.get_current_fear_greed.return_value = BitcoinTestFixtures.alternative_me_fear_greed()["data"][0]
        mock_service.get_historical_fear_greed.return_value = (
            BitcoinTestFixtures.alternative_me_historical_fear_greed()["data"]
        )
        mock_service.get_sentiment_analysis.return_value = {
            "period_days": 30,
            "average": 45.5,
            "current_sentiment": "Neutral",
        }
        return mock_service

    @staticmethod
    def create_mock_binance_service():
        """Create mock Binance API service"""
        mock_service = MagicMock()
        mock_service.get_exchange_info.return_value = BitcoinTestFixtures.binance_exchange_info()
        mock_service.get_24hr_ticker_stats.return_value = BitcoinTestFixtures.binance_24hr_ticker()
        mock_service.get_server_time.return_value = {"serverTime": int(datetime.now().timestamp() * 1000)}
        mock_service.get_symbol_price_ticker.return_value = {
            "symbol": "BTCUSDT",
            "price": "65426.00",
        }
        mock_service.get_bitcoin_data.return_value = {
            "ticker": BitcoinTestFixtures.binance_24hr_ticker(),
            "price": 65426.00,
        }
        return mock_service

    @staticmethod
    def create_mock_services_dict():
        """Create dictionary of all mock services for dependency injection"""
        return {
            "mempool_space": MockServiceFactory.create_mock_mempool_service(),
            "blockchain_com": MockServiceFactory.create_mock_blockchain_service(),
            "coinmetrics": MockServiceFactory.create_mock_coinmetrics_service(),
            "alternative_me": MockServiceFactory.create_mock_alternative_me_service(),
            "binance_api": MockServiceFactory.create_mock_binance_service(),
        }


class MockHTTPAdapter:
    """Mock HTTP adapter for requests"""

    def __init__(self):
        self.responses = {
            # Mempool.space endpoints
            "https://mempool.space/api/v1/fees/recommended": BitcoinTestFixtures.mempool_space_fee_estimates(),
            "https://mempool.space/api/mempool": BitcoinTestFixtures.mempool_space_mempool_info(),
            # Blockchain.com endpoints
            "https://blockchain.info/latestblock": BitcoinTestFixtures.blockchain_com_latest_block(),
            "https://blockchain.info/stats?format=json": BitcoinTestFixtures.blockchain_com_network_stats(),
            # CoinMetrics endpoints
            "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics": {
                "data": BitcoinTestFixtures.coinmetrics_network_data()
            },
            # Alternative.me endpoints
            "https://api.alternative.me/fng/?limit=1": BitcoinTestFixtures.alternative_me_fear_greed(),
            "https://api.alternative.me/fng/?limit=30": BitcoinTestFixtures.alternative_me_historical_fear_greed(),
            # Binance endpoints
            "https://api.binance.com/api/v3/exchangeInfo": BitcoinTestFixtures.binance_exchange_info(),
            "https://api.binance.com/api/v3/ticker/24hr": BitcoinTestFixtures.binance_24hr_ticker(),
            "https://api.binance.com/api/v3/time": {"serverTime": int(datetime.now().timestamp() * 1000)},
        }

    def get_mock_response(self, url: str) -> MockResponse:
        """Get mock response for URL"""
        for pattern, response_data in self.responses.items():
            if pattern in url:
                return MockResponse(response_data)

        # Default response for unmatched URLs
        return MockResponse({"error": "Mock endpoint not found"}, 404)


def patch_requests_get(mock_adapter: MockHTTPAdapter):
    """Decorator to patch requests.get with mock responses"""

    def mock_get(url, **kwargs):
        return mock_adapter.get_mock_response(url)

    return mock_get


def patch_requests_post(mock_adapter: MockHTTPAdapter):
    """Decorator to patch requests.post with mock responses"""

    def mock_post(url, **kwargs):
        return mock_adapter.get_mock_response(url)

    return mock_post


# Test configuration helpers
def get_test_service_config():
    """Get standard test service configuration"""
    from services.base_financial_service import ServiceConfig

    return ServiceConfig(
        name="test_service",
        base_url="https://test.api.com",
        api_key=None,
        timeout_seconds=10,
        max_retries=1,
    )


def create_test_services_with_mocks():
    """Create all test services with mock dependencies"""
    from services.bitcoin_network_stats import create_bitcoin_network_stats_service

    mock_services = MockServiceFactory.create_mock_services_dict()

    # Create bitcoin_network_stats with mock dependencies
    bitcoin_network_stats = create_bitcoin_network_stats_service("test", mock_services)

    # Add the aggregation service to the mock services dict
    mock_services["bitcoin_network_stats"] = bitcoin_network_stats

    return mock_services


class CLIMockingUtilities:
    """CLI-level mocking utilities for subprocess and command testing"""

    @staticmethod
    def mock_successful_cli_command(cli_output: dict[str, Any]) -> Mock:
        """Create mock for successful CLI command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(cli_output)
        mock_result.stderr = ""
        return mock_result

    @staticmethod
    def mock_failed_cli_command(error_message: str, return_code: int = 1) -> Mock:
        """Create mock for failed CLI command execution"""
        mock_result = Mock()
        mock_result.returncode = return_code
        mock_result.stdout = ""
        mock_result.stderr = error_message
        return mock_result

    @staticmethod
    def mock_cli_health_check_success(service_name: str) -> Mock:
        """Create mock for successful CLI health check"""
        health_data = {
            "service": service_name,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "env": "test",
        }
        return CLIMockingUtilities.mock_successful_cli_command(health_data)

    @staticmethod
    def mock_cli_config_output(service_name: str) -> Mock:
        """Create mock for CLI config command output"""
        config_data = {
            "service": service_name,
            "base_url": f"https://api.{service_name}.com",
            "timeout_seconds": 30,
            "max_retries": 3,
        }
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = f"""service: {service_name}
base_url: https://api.{service_name}.com
timeout_seconds: 30
max_retries: 3
"""
        mock_result.stderr = ""
        return mock_result


class BitcoinCLITestScenarios:
    """Pre-configured test scenarios for Bitcoin CLI testing"""

    @staticmethod
    def mempool_space_fee_estimates_success():
        """Successful mempool.space fees command scenario"""
        return CLIMockingUtilities.mock_successful_cli_command(BitcoinTestFixtures.mempool_space_fee_estimates())

    @staticmethod
    def blockchain_com_latest_block_success():
        """Successful blockchain.com latest block command scenario"""
        return CLIMockingUtilities.mock_successful_cli_command(BitcoinTestFixtures.blockchain_com_latest_block())

    @staticmethod
    def alternative_me_fear_greed_success():
        """Successful alternative.me fear & greed command scenario"""
        fear_greed_data = BitcoinTestFixtures.alternative_me_fear_greed()["data"][0]
        return CLIMockingUtilities.mock_successful_cli_command(fear_greed_data)

    @staticmethod
    def binance_price_ticker_success():
        """Successful binance price ticker command scenario"""
        price_data = {"symbol": "BTCUSDT", "price": "65426.00"}
        return CLIMockingUtilities.mock_successful_cli_command(price_data)

    @staticmethod
    def bitcoin_network_stats_overview_success():
        """Successful bitcoin network stats overview command scenario"""
        overview_data = {
            "timestamp": datetime.now().isoformat(),
            "sources": ["mempool_space", "blockchain_com", "binance_api"],
            "summary": {
                "total_data_sources": 3,
                "successful_sources": 3,
                "total_errors": 0,
                "data_quality": "excellent",
            },
            "network_health": {
                "mempool_congestion": "low",
                "fee_pressure": "moderate",
                "hash_rate_trend": "stable",
            },
        }
        return CLIMockingUtilities.mock_successful_cli_command(overview_data)

    @staticmethod
    def api_rate_limit_error():
        """API rate limit error scenario"""
        return CLIMockingUtilities.mock_failed_cli_command("Rate limit exceeded. Please try again later.", 429)

    @staticmethod
    def network_connection_error():
        """Network connection error scenario"""
        return CLIMockingUtilities.mock_failed_cli_command("Connection error: Unable to reach API endpoint", 503)

    @staticmethod
    def invalid_command_error():
        """Invalid command error scenario"""
        return CLIMockingUtilities.mock_failed_cli_command("No such command 'invalid_command'", 2)
