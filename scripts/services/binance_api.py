"""
Binance API Service

Production-grade Binance API integration with:
- Free public market data for Bitcoin and other cryptocurrencies
- Real-time ticker information and 24-hour statistics
- Order book depth and recent trades data
- Historical klines/candlestick data for technical analysis
- Exchange information and trading rules
- Completely free public endpoints with no authentication required
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


class BinanceAPIService(BaseFinancialService):
    """
    Binance API service extending BaseFinancialService

    Provides access to Binance's free public API including:
    - Real-time ticker information and 24-hour price statistics
    - Order book depth and recent trades data
    - Historical klines/candlestick data for comprehensive analysis
    - Exchange information and symbol details
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Binance public API is completely free, no API key required
        if not self.config.base_url:
            self.config.base_url = "https://api.binance.com"

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate Binance API response data"""

        if not data:
            raise DataNotFoundError(f"No data returned from Binance API {endpoint}")

        # Check for Binance API error responses
        if isinstance(data, dict) and "code" in data and "msg" in data:
            raise DataNotFoundError(f"Binance API error: {data['msg']} (Code: {data['code']})")

        return data

    def get_exchange_info(self) -> dict[str, Any]:
        """Get exchange trading rules and symbol information"""
        endpoint = "/api/v3/exchangeInfo"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "exchange info")

    def get_server_time(self) -> dict[str, Any]:
        """Get server time"""
        endpoint = "/api/v3/time"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "server time")

    def get_24hr_ticker_stats(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        """Get 24hr ticker price change statistics"""
        endpoint = "/api/v3/ticker/24hr"
        params = {"symbol": symbol.upper()}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"24hr ticker stats for {symbol}")

    def get_all_24hr_ticker_stats(self) -> list[dict[str, Any]]:
        """Get 24hr ticker price change statistics for all symbols"""
        endpoint = "/api/v3/ticker/24hr"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "all 24hr ticker stats")

    def get_symbol_price_ticker(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        """Get latest price for a symbol"""
        endpoint = "/api/v3/ticker/price"
        params = {"symbol": symbol.upper()}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"price ticker for {symbol}")

    def get_all_symbol_price_tickers(self) -> list[dict[str, Any]]:
        """Get latest prices for all symbols"""
        endpoint = "/api/v3/ticker/price"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "all symbol prices")

    def get_order_book_ticker(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        """Get best price/qty on the order book"""
        endpoint = "/api/v3/ticker/bookTicker"
        params = {"symbol": symbol.upper()}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"order book ticker for {symbol}")

    def get_all_order_book_tickers(self) -> list[dict[str, Any]]:
        """Get best price/qty on the order book for all symbols"""
        endpoint = "/api/v3/ticker/bookTicker"
        data = self._make_request_with_retry(endpoint)
        return self._validate_response(data, "all order book tickers")

    def get_order_book(self, symbol: str = "BTCUSDT", limit: int = 100) -> dict[str, Any]:
        """Get order book depth"""
        valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
        if limit not in valid_limits:
            limit = 100

        endpoint = "/api/v3/depth"
        params = {"symbol": symbol.upper(), "limit": limit}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"order book for {symbol}")

    def get_recent_trades(self, symbol: str = "BTCUSDT", limit: int = 500) -> list[dict[str, Any]]:
        """Get recent trades list"""
        if limit > 1000:
            limit = 1000
        elif limit < 1:
            limit = 1

        endpoint = "/api/v3/trades"
        params = {"symbol": symbol.upper(), "limit": limit}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"recent trades for {symbol}")

    def get_historical_trades(self, symbol: str = "BTCUSDT", limit: int = 500) -> list[dict[str, Any]]:
        """Get older market trades"""
        if limit > 1000:
            limit = 1000
        elif limit < 1:
            limit = 1

        endpoint = "/api/v3/historicalTrades"
        params = {"symbol": symbol.upper(), "limit": limit}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"historical trades for {symbol}")

    def get_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int = 500,
    ) -> list[list[str | float]]:
        """Get kline/candlestick data"""

        # Validate interval
        valid_intervals = [
            "1s",
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ]
        if interval not in valid_intervals:
            interval = "1h"

        if limit > 1000:
            limit = 1000
        elif limit < 1:
            limit = 1

        endpoint = "/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"klines for {symbol}")

    def get_average_price(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        """Get current average price for a symbol"""
        endpoint = "/api/v3/avgPrice"
        params = {"symbol": symbol.upper()}
        data = self._make_request_with_retry(endpoint, params=params)
        return self._validate_response(data, f"average price for {symbol}")

    def get_bitcoin_data(self) -> dict[str, Any]:
        """Get comprehensive Bitcoin market data"""
        bitcoin_data = {}

        # Get Bitcoin price and stats
        try:
            bitcoin_data["price_ticker"] = self.get_symbol_price_ticker("BTCUSDT")
        except:
            bitcoin_data["price_ticker"] = {}

        try:
            bitcoin_data["24hr_stats"] = self.get_24hr_ticker_stats("BTCUSDT")
        except:
            bitcoin_data["24hr_stats"] = {}

        try:
            bitcoin_data["order_book_ticker"] = self.get_order_book_ticker("BTCUSDT")
        except:
            bitcoin_data["order_book_ticker"] = {}

        try:
            bitcoin_data["average_price"] = self.get_average_price("BTCUSDT")
        except:
            bitcoin_data["average_price"] = {}

        bitcoin_data["timestamp"] = datetime.now().isoformat()
        bitcoin_data["symbol"] = "BTCUSDT"

        return bitcoin_data

    def get_bitcoin_orderbook_analysis(self, limit: int = 100) -> dict[str, Any]:
        """Get Bitcoin order book with analysis"""
        order_book = self.get_order_book("BTCUSDT", limit)

        if not order_book or "bids" not in order_book or "asks" not in order_book:
            return {}

        # Calculate order book metrics
        bids = [[float(price), float(qty)] for price, qty in order_book["bids"][:10]]
        asks = [[float(price), float(qty)] for price, qty in order_book["asks"][:10]]

        if bids and asks:
            best_bid = bids[0][0]
            best_ask = asks[0][0]
            spread = best_ask - best_bid
            spread_percent = (spread / best_bid) * 100

            # Calculate total volume at top levels
            bid_volume = sum([qty for price, qty in bids])
            ask_volume = sum([qty for price, qty in asks])

            analysis = {
                "order_book": order_book,
                "analysis": {
                    "best_bid": best_bid,
                    "best_ask": best_ask,
                    "spread": spread,
                    "spread_percent": round(spread_percent, 4),
                    "bid_volume_top_10": round(bid_volume, 4),
                    "ask_volume_top_10": round(ask_volume, 4),
                    "buy_sell_ratio": round(bid_volume / ask_volume, 4) if ask_volume > 0 else 0,
                },
                "timestamp": datetime.now().isoformat(),
            }

            return analysis

        return {
            "order_book": order_book,
            "analysis": {},
            "timestamp": datetime.now().isoformat(),
        }

    def get_market_summary(self, symbols: list[str] = None) -> dict[str, Any]:
        """Get market summary for specified symbols or Bitcoin-focused symbols"""
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]

        summary = {
            "symbols": [],
            "market_overview": {},
            "timestamp": datetime.now().isoformat(),
        }

        for symbol in symbols:
            try:
                ticker_data = self.get_24hr_ticker_stats(symbol)
                price_data = self.get_symbol_price_ticker(symbol)

                symbol_summary = {
                    "symbol": symbol,
                    "current_price": float(price_data.get("price", 0)),
                    "price_change_24h": float(ticker_data.get("priceChange", 0)),
                    "price_change_percent_24h": float(ticker_data.get("priceChangePercent", 0)),
                    "volume_24h": float(ticker_data.get("volume", 0)),
                    "high_24h": float(ticker_data.get("highPrice", 0)),
                    "low_24h": float(ticker_data.get("lowPrice", 0)),
                }

                summary["symbols"].append(symbol_summary)

            except Exception:
                # Skip failed symbols
                continue

        # Calculate market overview
        if summary["symbols"]:
            total_volume = sum([s["volume_24h"] for s in summary["symbols"]])
            avg_change = sum([s["price_change_percent_24h"] for s in summary["symbols"]]) / len(summary["symbols"])

            summary["market_overview"] = {
                "total_symbols": len(summary["symbols"]),
                "total_volume_24h": round(total_volume, 2),
                "average_change_percent_24h": round(avg_change, 2),
                "symbols_up": len([s for s in summary["symbols"] if s["price_change_percent_24h"] > 0]),
                "symbols_down": len([s for s in summary["symbols"] if s["price_change_percent_24h"] < 0]),
            }

        return summary

    def get_bitcoin_price_history(self, days: int = 7) -> dict[str, Any]:
        """Get Bitcoin price history for analysis"""
        if days > 30:
            days = 30
        elif days < 1:
            days = 1

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # Convert to milliseconds
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)

        # Determine interval based on days
        if days <= 1:
            interval = "15m"
        elif days <= 7:
            interval = "1h"
        else:
            interval = "4h"

        try:
            klines = self.get_klines(
                symbol="BTCUSDT",
                interval=interval,
                start_time=str(start_ms),
                end_time=str(end_ms),
                limit=1000,
            )

            # Process klines data
            price_history = []
            for kline in klines:
                price_data = {
                    "open_time": int(kline[0]),
                    "open_price": float(kline[1]),
                    "high_price": float(kline[2]),
                    "low_price": float(kline[3]),
                    "close_price": float(kline[4]),
                    "volume": float(kline[5]),
                    "close_time": int(kline[6]),
                    "datetime": datetime.fromtimestamp(int(kline[0]) / 1000).isoformat(),
                }
                price_history.append(price_data)

            # Calculate summary statistics
            if price_history:
                closes = [p["close_price"] for p in price_history]
                highs = [p["high_price"] for p in price_history]
                lows = [p["low_price"] for p in price_history]
                volumes = [p["volume"] for p in price_history]

                summary_stats = {
                    "period_days": days,
                    "interval": interval,
                    "data_points": len(price_history),
                    "start_price": closes[0] if closes else 0,
                    "end_price": closes[-1] if closes else 0,
                    "price_change": closes[-1] - closes[0] if len(closes) >= 2 else 0,
                    "price_change_percent": ((closes[-1] - closes[0]) / closes[0] * 100)
                    if len(closes) >= 2 and closes[0] > 0
                    else 0,
                    "highest_price": max(highs) if highs else 0,
                    "lowest_price": min(lows) if lows else 0,
                    "average_volume": sum(volumes) / len(volumes) if volumes else 0,
                    "total_volume": sum(volumes) if volumes else 0,
                }

                return {
                    "price_history": price_history,
                    "summary_stats": summary_stats,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception:
            pass

        return {
            "price_history": [],
            "summary_stats": {},
            "timestamp": datetime.now().isoformat(),
        }


def create_binance_api_service(env: str = "dev") -> BinanceAPIService:
    """
    Factory function to create BinanceAPIService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured BinanceAPIService instance
    """
    try:
        # Binance public API is completely free, no configuration needed
        service_config = ServiceConfig(
            name="binance_api",
            api_key=None,  # No API key required for public endpoints
            base_url="https://api.binance.com",
            timeout_seconds=30,
            max_retries=3,
        )

        return BinanceAPIService(service_config)

    except Exception:
        # Fallback configuration
        service_config = ServiceConfig(
            name="binance_api",
            api_key=None,
            base_url="https://api.binance.com",
            timeout_seconds=30,
            max_retries=3,
        )

        return BinanceAPIService(service_config)
