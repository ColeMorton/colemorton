"""
Bitcoin Network Statistics Service

Production-grade Bitcoin network statistics aggregation with:
- Comprehensive network health metrics from multiple free sources
- Real-time mempool and mining data aggregation
- Historical network statistics and trend analysis
- Multi-source data validation and reliability
- Completely free service using public APIs (Mempool.space, Blockchain.com, CoinMetrics)
"""

import statistics
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


class BitcoinNetworkStatsService(BaseFinancialService):
    """
    Bitcoin Network Statistics service extending BaseFinancialService

    Aggregates Bitcoin network data from multiple free sources to provide:
    - Comprehensive network health metrics and mining statistics
    - Real-time mempool monitoring and fee analysis
    - Historical network data and trend analysis
    - Multi-source validation for data reliability
    """

    def __init__(self, config: ServiceConfig, services: dict[str, Any] | None = None):
        super().__init__(config)

        # Initialize component services - use dependency injection for testability
        self.services = services or {}
        self.mempool_service = None
        self.blockchain_service = None
        self.coinmetrics_service = None

    def _get_mempool_service(self):
        """Get or create Mempool.space service instance"""
        if self.mempool_service is None:
            if "mempool_space" in self.services:
                self.mempool_service = self.services["mempool_space"]
            else:
                # Lazy import to avoid circular dependencies
                from .mempool_space import create_mempool_space_service

                self.mempool_service = create_mempool_space_service()
        return self.mempool_service

    def _get_blockchain_service(self):
        """Get or create Blockchain.com service instance"""
        if self.blockchain_service is None:
            if "blockchain_com" in self.services:
                self.blockchain_service = self.services["blockchain_com"]
            else:
                # Lazy import to avoid circular dependencies
                from .blockchain_com import create_blockchain_com_service

                self.blockchain_service = create_blockchain_com_service()
        return self.blockchain_service

    def _get_coinmetrics_service(self):
        """Get or create CoinMetrics service instance"""
        if self.coinmetrics_service is None:
            if "coinmetrics" in self.services:
                self.coinmetrics_service = self.services["coinmetrics"]
            else:
                # Lazy import to avoid circular dependencies
                from .coinmetrics import create_coinmetrics_service

                self.coinmetrics_service = create_coinmetrics_service()
        return self.coinmetrics_service

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate response data"""

        if not data:
            raise DataNotFoundError(f"No data returned from Bitcoin Network Stats {endpoint}")

        return data

    def get_network_overview(self) -> dict[str, Any]:
        """Get comprehensive Bitcoin network overview"""
        overview = {
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "network_health": {},
            "mempool_status": {},
            "mining_stats": {},
            "price_info": {},
            "errors": [],
        }

        # Get data from Mempool.space
        try:
            mempool_service = self._get_mempool_service()

            # Network stats
            network_stats = mempool_service.get_network_stats()
            overview["sources"].append("mempool.space")

            if "mempool" in network_stats:
                overview["mempool_status"]["mempool_space"] = network_stats["mempool"]

            if "fees" in network_stats:
                overview["mempool_status"]["fees"] = network_stats["fees"]

            if "difficulty" in network_stats:
                overview["mining_stats"]["difficulty"] = network_stats["difficulty"]

            if "hashrate_1w" in network_stats:
                overview["mining_stats"]["hashrate_weekly"] = network_stats["hashrate_1w"]

            if "price" in network_stats:
                overview["price_info"]["mempool_space"] = network_stats["price"]

        except Exception as e:
            overview["errors"].append(f"Mempool.space error: {str(e)}")

        # Get data from Blockchain.com
        try:
            blockchain_service = self._get_blockchain_service()

            # Network summary
            blockchain_summary = blockchain_service.get_blockchain_summary()
            overview["sources"].append("blockchain.com")

            if "network_stats" in blockchain_summary:
                overview["network_health"]["blockchain_com"] = blockchain_summary["network_stats"]

            if "difficulty" in blockchain_summary:
                overview["mining_stats"]["difficulty_blockchain"] = blockchain_summary["difficulty"]

            if "hashrate" in blockchain_summary:
                overview["mining_stats"]["hashrate_blockchain"] = blockchain_summary["hashrate"]

            if "market_price" in blockchain_summary:
                overview["price_info"]["blockchain_com"] = blockchain_summary["market_price"]

        except Exception as e:
            overview["errors"].append(f"Blockchain.com error: {str(e)}")

        # Get data from CoinMetrics (basic network data)
        try:
            coinmetrics_service = self._get_coinmetrics_service()

            # Recent network data
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            network_data = coinmetrics_service.get_network_data(
                asset="btc",
                metrics="AdrActCnt,BlkCnt,TxCnt",
                start_date=start_date,
                end_date=end_date,
            )

            if network_data and len(network_data) > 0:
                latest = network_data[-1]
                overview["network_health"]["coinmetrics"] = {
                    "active_addresses": latest.get("AdrActCnt"),
                    "block_count": latest.get("BlkCnt"),
                    "transaction_count": latest.get("TxCnt"),
                    "date": latest.get("time"),
                }
                overview["sources"].append("coinmetrics")

        except Exception as e:
            overview["errors"].append(f"CoinMetrics error: {str(e)}")

        return overview

    def get_mempool_analysis(self) -> dict[str, Any]:
        """Get detailed mempool analysis"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "mempool_metrics": {},
            "fee_analysis": {},
            "confirmation_times": {},
            "sources": [],
            "errors": [],
        }

        # Mempool.space mempool data
        try:
            mempool_service = self._get_mempool_service()

            mempool_info = mempool_service.get_mempool_info()
            fee_estimates = mempool_service.get_fee_estimates()

            analysis["mempool_metrics"]["mempool_space"] = mempool_info
            analysis["fee_analysis"]["recommended_fees"] = fee_estimates
            analysis["sources"].append("mempool.space")

        except Exception as e:
            analysis["errors"].append(f"Mempool.space error: {str(e)}")

        # Blockchain.com mempool data
        try:
            blockchain_service = self._get_blockchain_service()

            mempool_info = blockchain_service.get_mempool_info()
            analysis["mempool_metrics"]["blockchain_com"] = mempool_info
            analysis["sources"].append("blockchain.com")

        except Exception as e:
            analysis["errors"].append(f"Blockchain.com error: {str(e)}")

        return analysis

    def get_mining_statistics(self) -> dict[str, Any]:
        """Get comprehensive mining and difficulty statistics"""
        mining_stats = {
            "timestamp": datetime.now().isoformat(),
            "current_difficulty": {},
            "hashrate_metrics": {},
            "block_statistics": {},
            "sources": [],
            "errors": [],
        }

        # Mempool.space mining data
        try:
            mempool_service = self._get_mempool_service()

            difficulty_info = mempool_service.get_difficulty_info()
            hashrate_1w = mempool_service.get_hashrate_info("1w")
            hashrate_1m = mempool_service.get_hashrate_info("1m")

            mining_stats["current_difficulty"]["mempool_space"] = difficulty_info
            mining_stats["hashrate_metrics"]["weekly"] = hashrate_1w
            mining_stats["hashrate_metrics"]["monthly"] = hashrate_1m
            mining_stats["sources"].append("mempool.space")

        except Exception as e:
            mining_stats["errors"].append(f"Mempool.space error: {str(e)}")

        # Blockchain.com mining data
        try:
            blockchain_service = self._get_blockchain_service()

            difficulty = blockchain_service.get_difficulty()
            hashrate = blockchain_service.get_hashrate()

            mining_stats["current_difficulty"]["blockchain_com"] = difficulty
            mining_stats["hashrate_metrics"]["blockchain_com"] = hashrate
            mining_stats["sources"].append("blockchain.com")

        except Exception as e:
            mining_stats["errors"].append(f"Blockchain.com error: {str(e)}")

        # CoinMetrics mining data
        try:
            coinmetrics_service = self._get_coinmetrics_service()

            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            mining_data = coinmetrics_service.get_mining_data(asset="btc", start_date=start_date, end_date=end_date)

            if mining_data and len(mining_data) > 0:
                latest = mining_data[-1]
                mining_stats["block_statistics"]["coinmetrics"] = {
                    "hash_rate": latest.get("HashRate"),
                    "difficulty": latest.get("DiffMean"),
                    "block_count": latest.get("BlkCnt"),
                    "revenue_usd": latest.get("RevUSD"),
                    "date": latest.get("time"),
                }
                mining_stats["sources"].append("coinmetrics")

        except Exception as e:
            mining_stats["errors"].append(f"CoinMetrics error: {str(e)}")

        return mining_stats

    def get_network_health_metrics(self) -> dict[str, Any]:
        """Get network health and activity metrics"""
        health_metrics = {
            "timestamp": datetime.now().isoformat(),
            "activity_metrics": {},
            "network_capacity": {},
            "transaction_metrics": {},
            "sources": [],
            "errors": [],
        }

        # CoinMetrics network health data
        try:
            coinmetrics_service = self._get_coinmetrics_service()

            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # Network activity metrics
            network_data = coinmetrics_service.get_network_data(
                asset="btc",
                metrics="AdrActCnt,TxCnt,TxTfrValUSD,BlkCnt",
                start_date=start_date,
                end_date=end_date,
            )

            if network_data and len(network_data) > 0:
                # Calculate trends over the period
                recent_data = network_data[-7:]  # Last 7 days
                older_data = network_data[-14:-7]  # Previous 7 days

                if recent_data and older_data:
                    # Calculate averages
                    recent_tx_count = statistics.mean([float(d.get("TxCnt", 0)) for d in recent_data if d.get("TxCnt")])
                    older_tx_count = statistics.mean([float(d.get("TxCnt", 0)) for d in older_data if d.get("TxCnt")])

                    recent_active_addr = statistics.mean(
                        [float(d.get("AdrActCnt", 0)) for d in recent_data if d.get("AdrActCnt")]
                    )
                    older_active_addr = statistics.mean(
                        [float(d.get("AdrActCnt", 0)) for d in older_data if d.get("AdrActCnt")]
                    )

                    recent_transfer_value = statistics.mean(
                        [float(d.get("TxTfrValUSD", 0)) for d in recent_data if d.get("TxTfrValUSD")]
                    )
                    older_transfer_value = statistics.mean(
                        [float(d.get("TxTfrValUSD", 0)) for d in older_data if d.get("TxTfrValUSD")]
                    )

                    health_metrics["activity_metrics"]["coinmetrics"] = {
                        "transaction_count_7d_avg": round(recent_tx_count, 2),
                        "transaction_count_trend": "up" if recent_tx_count > older_tx_count else "down",
                        "transaction_count_change_percent": round(
                            ((recent_tx_count - older_tx_count) / older_tx_count * 100),
                            2,
                        )
                        if older_tx_count > 0
                        else 0,
                        "active_addresses_7d_avg": round(recent_active_addr, 2),
                        "active_addresses_trend": "up" if recent_active_addr > older_active_addr else "down",
                        "active_addresses_change_percent": round(
                            ((recent_active_addr - older_active_addr) / older_active_addr * 100),
                            2,
                        )
                        if older_active_addr > 0
                        else 0,
                        "transfer_value_usd_7d_avg": round(recent_transfer_value, 2),
                        "transfer_value_trend": "up" if recent_transfer_value > older_transfer_value else "down",
                        "transfer_value_change_percent": round(
                            ((recent_transfer_value - older_transfer_value) / older_transfer_value * 100),
                            2,
                        )
                        if older_transfer_value > 0
                        else 0,
                    }

                health_metrics["sources"].append("coinmetrics")

        except Exception as e:
            health_metrics["errors"].append(f"CoinMetrics error: {str(e)}")

        # Blockchain.com network data
        try:
            blockchain_service = self._get_blockchain_service()

            network_stats = blockchain_service.get_network_stats()
            total_bitcoins = blockchain_service.get_total_bitcoins()

            health_metrics["network_capacity"]["blockchain_com"] = {
                "network_stats": network_stats,
                "total_bitcoins": total_bitcoins,
            }
            health_metrics["sources"].append("blockchain.com")

        except Exception as e:
            health_metrics["errors"].append(f"Blockchain.com error: {str(e)}")

        return health_metrics

    def get_price_and_market_data(self) -> dict[str, Any]:
        """Get Bitcoin price and market data from multiple sources"""
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "price_sources": {},
            "market_metrics": {},
            "sources": [],
            "errors": [],
        }

        # Mempool.space price
        try:
            mempool_service = self._get_mempool_service()
            price_info = mempool_service.get_bitcoin_price()
            market_data["price_sources"]["mempool_space"] = price_info
            market_data["sources"].append("mempool.space")
        except Exception as e:
            market_data["errors"].append(f"Mempool.space price error: {str(e)}")

        # Blockchain.com price
        try:
            blockchain_service = self._get_blockchain_service()
            price_info = blockchain_service.get_market_price_usd()
            market_data["price_sources"]["blockchain_com"] = price_info
            market_data["sources"].append("blockchain.com")
        except Exception as e:
            market_data["errors"].append(f"Blockchain.com price error: {str(e)}")

        # CoinMetrics market data
        try:
            coinmetrics_service = self._get_coinmetrics_service()

            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            market_data_cm = coinmetrics_service.get_market_data(asset="btc", start_date=start_date, end_date=end_date)

            if market_data_cm and len(market_data_cm) > 0:
                latest = market_data_cm[-1]
                market_data["price_sources"]["coinmetrics"] = {
                    "price_usd": latest.get("PriceUSD"),
                    "market_cap_usd": latest.get("CapMrktCurUSD"),
                    "volume_trusted_24h_usd": latest.get("VolTrusted24hUSD"),
                    "date": latest.get("time"),
                }
                market_data["sources"].append("coinmetrics")

        except Exception as e:
            market_data["errors"].append(f"CoinMetrics market error: {str(e)}")

        return market_data

    def get_comprehensive_report(self) -> dict[str, Any]:
        """Get comprehensive Bitcoin network statistics report"""
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "report_type": "comprehensive_bitcoin_network_statistics",
            "data_sources": [],
            "network_overview": {},
            "mempool_analysis": {},
            "mining_statistics": {},
            "network_health": {},
            "market_data": {},
            "summary": {},
            "errors": [],
        }

        # Gather all data sections
        try:
            report["network_overview"] = self.get_network_overview()
            report["data_sources"].extend(report["network_overview"].get("sources", []))
        except Exception as e:
            report["errors"].append(f"Network overview error: {str(e)}")

        try:
            report["mempool_analysis"] = self.get_mempool_analysis()
        except Exception as e:
            report["errors"].append(f"Mempool analysis error: {str(e)}")

        try:
            report["mining_statistics"] = self.get_mining_statistics()
        except Exception as e:
            report["errors"].append(f"Mining statistics error: {str(e)}")

        try:
            report["network_health"] = self.get_network_health_metrics()
        except Exception as e:
            report["errors"].append(f"Network health error: {str(e)}")

        try:
            report["market_data"] = self.get_price_and_market_data()
        except Exception as e:
            report["errors"].append(f"Market data error: {str(e)}")

        # Generate summary
        report["summary"] = {
            "total_data_sources": len(set(report["data_sources"])),
            "unique_sources": list(set(report["data_sources"])),
            "report_sections": len(
                [
                    k
                    for k in report
                    if k
                    not in [
                        "report_timestamp",
                        "report_type",
                        "data_sources",
                        "summary",
                        "errors",
                    ]
                ]
            ),
            "total_errors": len(report["errors"]),
            "data_quality": "good" if len(report["errors"]) < 3 else "degraded",
        }

        return report


def create_bitcoin_network_stats_service(
    env: str = "dev", services: dict[str, Any] | None = None
) -> BitcoinNetworkStatsService:
    """
    Factory function to create BitcoinNetworkStatsService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)
        services: Optional dictionary of pre-configured services for dependency injection (used in tests)

    Returns:
        Configured BitcoinNetworkStatsService instance
    """
    try:
        # Bitcoin Network Stats aggregates free APIs, no configuration needed
        service_config = ServiceConfig(
            name="bitcoin_network_stats",
            api_key=None,  # Not needed for aggregation service
            base_url="https://aggregation.service",  # Placeholder for aggregation service
            timeout_seconds=60,  # Longer timeout for multiple API calls
            max_retries=3,
        )

        return BitcoinNetworkStatsService(service_config, services)

    except Exception:
        # Fallback configuration
        service_config = ServiceConfig(
            name="bitcoin_network_stats",
            api_key=None,
            base_url="https://aggregation.service",  # Placeholder for aggregation service
            timeout_seconds=60,
            max_retries=3,
        )

        return BitcoinNetworkStatsService(service_config, services)
