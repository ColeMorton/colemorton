#!/usr/bin/env python3
"""
Binance API CLI

Command-line interface for Binance API public market data with:
- Free public market data for Bitcoin and other cryptocurrencies
- Real-time ticker information and 24-hour statistics
- Order book depth and recent trades data
- Historical klines/candlestick data for technical analysis
- Exchange information and trading rules
- Completely free public endpoints with no authentication required
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.binance_api import create_binance_api_service
from utils.cli_base import BaseFinancialCLI, OutputFormat


class BinanceAPICLI(BaseFinancialCLI):
    """CLI for Binance API public market data service"""

    def __init__(self):
        super().__init__(
            service_name="binance_api",
            description="Binance API public market data service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_binance_api_service(env)
        return self.service

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Binance API service health check"""
        try:
            service = self._get_service(env)
            service.get_server_time()
            return {"status": "healthy", "service": "binance_api", "env": env}
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "binance_api",
                "env": env,
                "error": str(e),
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        return {
            "action": action,
            "service": "binance_api",
            "env": env,
            "status": "no_cache_implemented",
        }

    def _add_service_commands(self) -> None:
        """Add Binance API specific commands"""

        @self.app.command("exchange-info")
        def get_exchange_info(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get exchange trading rules and symbol information"""
            try:
                service = self._get_service(env)

                result = service.get_exchange_info()
                self._output_result(result, output_format, "Exchange Information")

            except Exception as e:
                self._handle_error(e, "Failed to get exchange information")

        @self.app.command("server-time")
        def get_server_time(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get server time"""
            try:
                service = self._get_service(env)

                result = service.get_server_time()
                self._output_result(result, output_format, "Server Time")

            except Exception as e:
                self._handle_error(e, "Failed to get server time")

        @self.app.command("24hr-ticker")
        def get_24hr_ticker_stats(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get 24hr ticker price change statistics"""
            try:
                service = self._get_service(env)

                result = service.get_24hr_ticker_stats(symbol)
                self._output_result(result, output_format, f"24hr Ticker: {symbol}")

            except Exception as e:
                self._handle_error(e, f"Failed to get 24hr ticker for {symbol}")

        @self.app.command("all-24hr-tickers")
        def get_all_24hr_ticker_stats(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get 24hr ticker price change statistics for all symbols"""
            try:
                service = self._get_service(env)

                result = service.get_all_24hr_ticker_stats()
                self._output_result(result, output_format, "All 24hr Tickers")

            except Exception as e:
                self._handle_error(e, "Failed to get all 24hr tickers")

        @self.app.command("price")
        def get_symbol_price_ticker(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get latest price for a symbol"""
            try:
                service = self._get_service(env)

                result = service.get_symbol_price_ticker(symbol)
                self._output_result(result, output_format, f"Price: {symbol}")

            except Exception as e:
                self._handle_error(e, f"Failed to get price for {symbol}")

        @self.app.command("all-prices")
        def get_all_symbol_price_tickers(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get latest prices for all symbols"""
            try:
                service = self._get_service(env)

                result = service.get_all_symbol_price_tickers()
                self._output_result(result, output_format, "All Symbol Prices")

            except Exception as e:
                self._handle_error(e, "Failed to get all symbol prices")

        @self.app.command("book-ticker")
        def get_order_book_ticker(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get best price/qty on the order book"""
            try:
                service = self._get_service(env)

                result = service.get_order_book_ticker(symbol)
                self._output_result(result, output_format, f"Order Book Ticker: {symbol}")

            except Exception as e:
                self._handle_error(e, f"Failed to get order book ticker for {symbol}")

        @self.app.command("all-book-tickers")
        def get_all_order_book_tickers(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get best price/qty on the order book for all symbols"""
            try:
                service = self._get_service(env)

                result = service.get_all_order_book_tickers()
                self._output_result(result, output_format, "All Order Book Tickers")

            except Exception as e:
                self._handle_error(e, "Failed to get all order book tickers")

        @self.app.command("orderbook")
        def get_order_book(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            limit: int = typer.Option(100, help="Number of entries (5,10,20,50,100,500,1000,5000)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get order book depth"""
            try:
                service = self._get_service(env)

                valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
                if limit not in valid_limits:
                    limit = 100

                result = service.get_order_book(symbol, limit)
                self._output_result(result, output_format, f"Order Book: {symbol}")

            except Exception as e:
                self._handle_error(e, f"Failed to get order book for {symbol}")

        @self.app.command("recent-trades")
        def get_recent_trades(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            limit: int = typer.Option(500, help="Number of trades (max 1000)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get recent trades list"""
            try:
                service = self._get_service(env)

                if limit > 1000:
                    limit = 1000
                elif limit < 1:
                    limit = 1

                result = service.get_recent_trades(symbol, limit)
                self._output_result(result, output_format, f"Recent Trades: {symbol}")

            except Exception as e:
                self._handle_error(e, f"Failed to get recent trades for {symbol}")

        @self.app.command("historical-trades")
        def get_historical_trades(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            limit: int = typer.Option(500, help="Number of trades (max 1000)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get older market trades"""
            try:
                service = self._get_service(env)

                if limit > 1000:
                    limit = 1000
                elif limit < 1:
                    limit = 1

                result = service.get_historical_trades(symbol, limit)
                self._output_result(result, output_format, f"Historical Trades: {symbol}")

            except Exception as e:
                self._handle_error(e, f"Failed to get historical trades for {symbol}")

        @self.app.command("klines")
        def get_klines(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            interval: str = typer.Option(
                "1h",
                help="Time interval (1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M)",
            ),
            start_time: str = typer.Option("", help="Start time (milliseconds timestamp)"),
            end_time: str = typer.Option("", help="End time (milliseconds timestamp)"),
            limit: int = typer.Option(500, help="Number of klines (max 1000)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get kline/candlestick data"""
            try:
                service = self._get_service(env)

                if limit > 1000:
                    limit = 1000
                elif limit < 1:
                    limit = 1

                result = service.get_klines(
                    symbol=symbol,
                    interval=interval,
                    start_time=start_time if start_time else None,
                    end_time=end_time if end_time else None,
                    limit=limit,
                )
                self._output_result(result, output_format, f"Klines: {symbol} ({interval})")

            except Exception as e:
                self._handle_error(e, f"Failed to get klines for {symbol}")

        @self.app.command("avg-price")
        def get_average_price(
            symbol: str = typer.Option("BTCUSDT", help="Trading symbol (e.g., BTCUSDT)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current average price for a symbol"""
            try:
                service = self._get_service(env)

                result = service.get_average_price(symbol)
                self._output_result(result, output_format, f"Average Price: {symbol}")

            except Exception as e:
                self._handle_error(e, f"Failed to get average price for {symbol}")

        @self.app.command("bitcoin-data")
        def get_bitcoin_data(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive Bitcoin market data"""
            try:
                service = self._get_service(env)

                result = service.get_bitcoin_data()
                self._output_result(result, output_format, "Bitcoin Market Data")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin market data")

        @self.app.command("bitcoin-orderbook-analysis")
        def get_bitcoin_orderbook_analysis(
            limit: int = typer.Option(100, help="Order book depth limit"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin order book with analysis"""
            try:
                service = self._get_service(env)

                valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
                if limit not in valid_limits:
                    limit = 100

                result = service.get_bitcoin_orderbook_analysis(limit)
                self._output_result(result, output_format, "Bitcoin Order Book Analysis")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin order book analysis")

        @self.app.command("market-summary")
        def get_market_summary(
            symbols: str = typer.Option("", help="Comma-separated symbols (default: BTC,ETH,BNB,ADA,SOL)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get market summary for specified symbols or Bitcoin-focused symbols"""
            try:
                service = self._get_service(env)

                symbol_list = None
                if symbols:
                    symbol_list = [s.strip().upper() for s in symbols.split(",")]
                    # Ensure USDT pairs
                    symbol_list = [s if s.endswith("USDT") else f"{s}USDT" for s in symbol_list]

                result = service.get_market_summary(symbol_list)
                self._output_result(result, output_format, "Market Summary")

            except Exception as e:
                self._handle_error(e, "Failed to get market summary")

        @self.app.command("bitcoin-history")
        def get_bitcoin_price_history(
            days: int = typer.Option(7, help="Number of days of history (max 30)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin price history for analysis"""
            try:
                service = self._get_service(env)

                if days > 30:
                    days = 30
                elif days < 1:
                    days = 1

                result = service.get_bitcoin_price_history(days)
                self._output_result(result, output_format, f"Bitcoin Price History ({days} days)")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin price history")


def main():
    """Main entry point for the Binance API CLI"""
    cli = BinanceAPICLI()
    cli.run()


if __name__ == "__main__":
    main()
