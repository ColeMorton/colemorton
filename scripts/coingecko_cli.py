#!/usr/bin/env python3
"""
CoinGecko CLI

Command-line interface for CoinGecko cryptocurrency data with:
- Real-time prices for 17,000+ cryptocurrencies
- Market data across 1,000+ exchanges and 200+ blockchain networks
- Historical data and trending cryptocurrencies
- Global market statistics and search capabilities
- Bitcoin sentiment analysis for broader market context
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.coingecko import create_coingecko_service
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError


class CoinGeckoCLI(BaseFinancialCLI):
    """CLI for CoinGecko service"""

    def __init__(self):
        super().__init__(
            service_name="coingecko",
            description="CoinGecko cryptocurrency data service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_coingecko_service(env)
        return self.service

    def _add_service_commands(self) -> None:
        """Add CoinGecko specific commands"""

        @self.app.command("price")
        def get_crypto_price(
            coin_ids: str = typer.Argument(..., help="Comma-separated coin IDs (e.g., bitcoin,ethereum)"),
            vs_currencies: str = typer.Option("usd", help="Comma-separated currencies"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current price of cryptocurrencies"""
            try:
                service = self._get_service(env)

                result = service.get_price(coin_ids, vs_currencies)
                self._output_result(result, output_format, f"Crypto Prices: {coin_ids}")

            except Exception as e:
                self._handle_error(e, f"Failed to get prices for {coin_ids}")

        @self.app.command("coin")
        def get_coin_details(
            coin_id: str = typer.Argument(..., help="Coin ID (e.g., bitcoin, ethereum)"),
            localization: bool = typer.Option(False, help="Include localized data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get detailed information about a specific cryptocurrency"""
            try:
                service = self._get_service(env)

                result = service.get_coin_data(coin_id, localization)
                self._output_result(result, output_format, f"Coin Details: {coin_id}")

            except Exception as e:
                self._handle_error(e, f"Failed to get coin details for {coin_id}")

        @self.app.command("markets")
        def get_market_data(
            vs_currency: str = typer.Option("usd", help="Currency for prices"),
            order: str = typer.Option("market_cap_desc", help="Sorting order"),
            per_page: int = typer.Option(100, help="Number of results per page (max 250)"),
            page: int = typer.Option(1, help="Page number"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get market data for top cryptocurrencies"""
            try:
                service = self._get_service(env)

                if per_page > 250:
                    per_page = 250

                result = service.get_market_data(vs_currency, order, per_page, page)
                self._output_result(result, output_format, f"Crypto Markets (page {page})")

            except Exception as e:
                self._handle_error(e, "Failed to get market data")

        @self.app.command("history")
        def get_historical_data(
            coin_id: str = typer.Argument(..., help="Coin ID"),
            vs_currency: str = typer.Option("usd", help="Currency for prices"),
            days: int = typer.Option(30, help="Number of days of historical data"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get historical market data for a cryptocurrency"""
            try:
                service = self._get_service(env)

                result = service.get_historical_data(coin_id, vs_currency, days)
                self._output_result(result, output_format, f"Historical Data: {coin_id} ({days} days)")

            except Exception as e:
                self._handle_error(e, f"Failed to get historical data for {coin_id}")

        @self.app.command("search")
        def search_cryptocurrencies(
            query: str = typer.Argument(..., help="Search query (coin name or symbol)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Search for cryptocurrencies by name or symbol"""
            try:
                service = self._get_service(env)

                result = service.search_coins(query)
                self._output_result(result, output_format, f"Search Results: {query}")

            except Exception as e:
                self._handle_error(e, f"Failed to search for '{query}'")

        @self.app.command("trending")
        def get_trending(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get trending cryptocurrencies"""
            try:
                service = self._get_service(env)

                result = service.get_trending()
                self._output_result(result, output_format, "Trending Cryptocurrencies")

            except Exception as e:
                self._handle_error(e, "Failed to get trending cryptocurrencies")

        @self.app.command("global")
        def get_global_data(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get global cryptocurrency market statistics"""
            try:
                service = self._get_service(env)

                result = service.get_global_data()
                self._output_result(result, output_format, "Global Crypto Market Data")

            except Exception as e:
                self._handle_error(e, "Failed to get global market data")

        @self.app.command("sentiment")
        def get_bitcoin_sentiment(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin sentiment analysis for broader market context"""
            try:
                service = self._get_service(env)

                result = service.get_bitcoin_sentiment()
                self._output_result(result, output_format, "Bitcoin Market Sentiment")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin sentiment")

        @self.app.command("top")
        def get_top_cryptocurrencies(
            limit: int = typer.Option(10, help="Number of top cryptocurrencies"),
            vs_currency: str = typer.Option("usd", help="Currency for prices"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get top cryptocurrencies by market cap"""
            try:
                service = self._get_service(env)

                result = service.get_market_data(vs_currency, "market_cap_desc", limit, 1)

                # Simplify for table output
                if output_format == OutputFormat.TABLE and isinstance(result, list):
                    simplified_result = []
                    for coin in result:
                        if isinstance(coin, dict):
                            simplified_result.append(
                                {
                                    "rank": coin.get("market_cap_rank", "N/A"),
                                    "name": coin.get("name", "N/A"),
                                    "symbol": coin.get("symbol", "").upper(),
                                    "price": f"${coin.get('current_price', 0):,.2f}",
                                    "change_24h": f"{coin.get('price_change_percentage_24h', 0):+.2f}%",
                                    "market_cap": f"${coin.get('market_cap', 0):,.0f}",
                                }
                            )
                    result = simplified_result

                self._output_result(result, output_format, f"Top {limit} Cryptocurrencies")

            except Exception as e:
                self._handle_error(e, f"Failed to get top {limit} cryptocurrencies")

        @self.app.command("compare")
        def compare_cryptocurrencies(
            coin_ids: str = typer.Argument(..., help="Comma-separated coin IDs to compare"),
            vs_currency: str = typer.Option("usd", help="Currency for comparison"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Compare multiple cryptocurrencies"""
            try:
                service = self._get_service(env)
                coin_list = [coin.strip() for coin in coin_ids.split(",")]

                results = []
                for coin_id in coin_list:
                    try:
                        coin_data = service.get_coin_data(coin_id)
                        if coin_data:
                            results.append(
                                {
                                    "coin": coin_data.get("name", coin_id),
                                    "symbol": coin_data.get("symbol", "").upper(),
                                    "price": f"${coin_data.get('current_price', 0):,.2f}",
                                    "change_24h": f"{coin_data.get('price_change_percentage_24h', 0):+.2f}%",
                                    "market_cap_rank": coin_data.get("market_cap_rank", "N/A"),
                                    "market_cap": f"${coin_data.get('market_cap', 0):,.0f}",
                                }
                            )
                    except Exception as e:
                        results.append(
                            {
                                "coin": coin_id,
                                "symbol": "ERROR",
                                "price": "ERROR",
                                "change_24h": "ERROR",
                                "market_cap_rank": "ERROR",
                                "market_cap": "ERROR",
                                "error": str(e),
                            }
                        )

                self._output_result(results, output_format, "Cryptocurrency Comparison")

            except Exception as e:
                self._handle_error(e, "Failed to compare cryptocurrencies")

        @self.app.command("batch")
        def batch_prices(
            coin_ids: str = typer.Argument(..., help="Comma-separated coin IDs"),
            vs_currency: str = typer.Option("usd", help="Currency for prices"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get prices for multiple cryptocurrencies in a batch"""
            try:
                service = self._get_service(env)

                result = service.get_price(coin_ids, vs_currency)

                # Convert to table format if requested
                if output_format == OutputFormat.TABLE and isinstance(result, dict):
                    table_result = []
                    for coin_id, data in result.items():
                        if isinstance(data, dict) and coin_id not in [
                            "coin_ids",
                            "vs_currencies",
                            "source",
                            "timestamp",
                        ]:
                            table_result.append(
                                {
                                    "coin_id": coin_id,
                                    "price": f"${data.get(vs_currency, 0):,.2f}",
                                    "market_cap": f"${data.get(f'{vs_currency}_market_cap', 0):,.0f}",
                                    "volume_24h": f"${data.get(f'{vs_currency}_24h_vol', 0):,.0f}",
                                    "change_24h": f"{data.get(f'{vs_currency}_24h_change', 0):+.2f}%",
                                }
                            )
                    result = table_result

                self._output_result(result, output_format, f"Batch Prices: {coin_ids}")

            except Exception as e:
                self._handle_error(e, "Failed to get batch prices")

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform CoinGecko service health check"""
        service = self._get_service(env)
        return service.health_check()

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        service = self._get_service(env)

        if action == "clear":
            service.clear_cache()
            return {"action": "clear", "status": "success", "message": "Cache cleared"}
        if action == "cleanup":
            service.cleanup_cache()
            return {
                "action": "cleanup",
                "status": "success",
                "message": "Expired cache entries removed",
            }
        if action == "stats":
            return {
                "action": "stats",
                "cache_info": service.get_service_info(),
                "cache_directory": str(service.cache.cache_dir),
            }
        raise ValidationError(f"Unknown cache action: {action}")


def main():
    """Main entry point for CoinGecko CLI"""
    cli = CoinGeckoCLI()
    cli.run()


if __name__ == "__main__":
    main()
