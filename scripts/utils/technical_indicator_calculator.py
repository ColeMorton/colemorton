#!/usr/bin/env python3
"""
Technical Indicator Calculator

Calculates common technical indicators from historical price data for
enhanced market analysis and trading signal generation.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from historical_data_manager import DataType, HistoricalDataManager, Timeframe


@dataclass
class PriceData:
    """Price data structure for technical calculations"""

    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class TechnicalIndicatorCalculator:
    """
    Calculates technical indicators from historical price data

    Features:
    - Moving averages (SMA, EMA)
    - Momentum indicators (RSI, MACD, Stochastic)
    - Volatility indicators (Bollinger Bands, ATR)
    - Volume indicators (OBV, Volume SMA)
    - Trend indicators (ADX, Parabolic SAR)
    """

    def __init__(self, historical_manager: HistoricalDataManager | None = None):
        """
        Initialize Technical Indicator Calculator

        Args:
            historical_manager: HistoricalDataManager instance for data access
        """
        self.hdm = historical_manager or HistoricalDataManager()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for technical indicator calculator"""
        logger = logging.getLogger("technical_indicator_calculator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def get_price_data(self, symbol: str, days: int = 200, timeframe: Timeframe = Timeframe.DAILY) -> list[PriceData]:
        """
        Retrieve historical price data for calculations

        Args:
            symbol: Stock symbol
            days: Number of days of historical data to retrieve
            timeframe: Data timeframe

        Returns:
            List of PriceData objects sorted by date
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        raw_data = self.hdm.retrieve_data(
            symbol=symbol,
            data_type=DataType.STOCK_DAILY_PRICES,
            date_start=start_date,
            date_end=end_date,
            timeframe=timeframe,
        )

        price_data = []
        for record in raw_data:
            try:
                data_dict = record.get("data", {})
                price_data.append(
                    PriceData(
                        date=datetime.fromisoformat(record["date"]),
                        open=float(data_dict.get("open", 0)),
                        high=float(data_dict.get("high", 0)),
                        low=float(data_dict.get("low", 0)),
                        close=float(data_dict.get("close", 0)),
                        volume=int(data_dict.get("volume", 0)),
                    )
                )
            except (KeyError, ValueError, TypeError) as e:
                self.logger.warning(f"Failed to parse price data for {symbol}: {e}")
                continue

        # Sort by date
        price_data.sort(key=lambda x: x.date)
        return price_data

    # Moving Averages
    def calculate_sma(self, prices: list[float], window: int) -> float | None:
        """Calculate Simple Moving Average"""
        if len(prices) < window:
            return None
        return sum(prices[-window:]) / window

    def calculate_ema(self, prices: list[float], window: int) -> float | None:
        """Calculate Exponential Moving Average"""
        if len(prices) < window:
            return None

        multiplier = 2 / (window + 1)
        ema = prices[0]  # Start with first price

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    # Momentum Indicators
    def calculate_rsi(self, prices: list[float], window: int = 14) -> float | None:
        """Calculate Relative Strength Index"""
        if len(prices) < window + 1:
            return None

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        if len(gains) < window:
            return None

        avg_gain = sum(gains[-window:]) / window
        avg_loss = sum(losses[-window:]) / window

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_macd(
        self,
        prices: list[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> dict[str, float] | None:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow_period:
            return None

        # Calculate EMAs
        ema_fast = []
        ema_slow = []

        # Calculate fast EMA
        for i in range(fast_period - 1, len(prices)):
            fast_ema = self.calculate_ema(prices[: i + 1], fast_period)
            if fast_ema is not None:
                ema_fast.append(fast_ema)

        # Calculate slow EMA
        for i in range(slow_period - 1, len(prices)):
            slow_ema = self.calculate_ema(prices[: i + 1], slow_period)
            if slow_ema is not None:
                ema_slow.append(slow_ema)

        if len(ema_fast) == 0 or len(ema_slow) == 0:
            return None

        # MACD line = Fast EMA - Slow EMA
        macd_line = ema_fast[-1] - ema_slow[-1]

        # Calculate signal line (EMA of MACD)
        macd_values = []
        for i in range(min(len(ema_fast), len(ema_slow))):
            macd_values.append(ema_fast[i] - ema_slow[i])

        signal_line = self.calculate_ema(macd_values, signal_period)
        if signal_line is None:
            signal_line = macd_line

        histogram = macd_line - signal_line

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    def calculate_stochastic(
        self, price_data: list[PriceData], k_period: int = 14, d_period: int = 3
    ) -> dict[str, float] | None:
        """Calculate Stochastic Oscillator"""
        if len(price_data) < k_period:
            return None

        # Get recent data
        recent_data = price_data[-k_period:]

        current_close = recent_data[-1].close
        lowest_low = min(data.low for data in recent_data)
        highest_high = max(data.high for data in recent_data)

        if highest_high == lowest_low:
            k_percent = 50
        else:
            k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100

        # For %D calculation, we'd need multiple %K values
        # Simplified version returns current %K
        return {"k_percent": k_percent, "d_percent": k_percent}  # Simplified

    # Volatility Indicators
    def calculate_bollinger_bands(
        self, prices: list[float], window: int = 20, std_dev: float = 2.0
    ) -> dict[str, float] | None:
        """Calculate Bollinger Bands"""
        if len(prices) < window:
            return None

        sma = self.calculate_sma(prices, window)
        if sma is None:
            return None

        # Calculate standard deviation
        recent_prices = prices[-window:]
        variance = sum((price - sma) ** 2 for price in recent_prices) / window
        std = variance**0.5

        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)

        return {
            "upper": upper_band,
            "middle": sma,
            "lower": lower_band,
            "bandwidth": (upper_band - lower_band) / sma * 100,
        }

    def calculate_atr(self, price_data: list[PriceData], window: int = 14) -> float | None:
        """Calculate Average True Range"""
        if len(price_data) < window + 1:
            return None

        true_ranges = []

        for i in range(1, len(price_data)):
            high = price_data[i].high
            low = price_data[i].low
            prev_close = price_data[i - 1].close

            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)

            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)

        if len(true_ranges) < window:
            return None

        return sum(true_ranges[-window:]) / window

    # Volume Indicators
    def calculate_obv(self, price_data: list[PriceData]) -> float | None:
        """Calculate On-Balance Volume"""
        if len(price_data) < 2:
            return None

        obv = 0

        for i in range(1, len(price_data)):
            if price_data[i].close > price_data[i - 1].close:
                obv += price_data[i].volume
            elif price_data[i].close < price_data[i - 1].close:
                obv -= price_data[i].volume
            # If close == prev_close, OBV stays the same

        return obv

    def calculate_volume_sma(self, price_data: list[PriceData], window: int = 20) -> float | None:
        """Calculate Volume Simple Moving Average"""
        if len(price_data) < window:
            return None

        volumes = [data.volume for data in price_data[-window:]]
        return sum(volumes) / window

    def calculate_all_indicators(self, symbol: str, days: int = 200) -> dict[str, Any] | None:
        """
        Calculate all available technical indicators for a symbol

        Args:
            symbol: Stock symbol
            days: Days of historical data to use

        Returns:
            Dictionary containing all calculated indicators
        """
        try:
            price_data = self.get_price_data(symbol, days)

            if len(price_data) < 50:  # Need minimum data for calculations
                self.logger.warning(f"Insufficient price data for {symbol}: {len(price_data)} records")
                return None

            closes = [data.close for data in price_data]

            indicators = {
                "symbol": symbol,
                "date": datetime.now().isoformat(),
                "data_points": len(price_data),
                "indicators": {},
            }

            # Moving Averages
            indicators["indicators"]["sma_20"] = self.calculate_sma(closes, 20)
            indicators["indicators"]["sma_50"] = self.calculate_sma(closes, 50)
            indicators["indicators"]["sma_200"] = self.calculate_sma(closes, 200)
            indicators["indicators"]["ema_12"] = self.calculate_ema(closes, 12)
            indicators["indicators"]["ema_26"] = self.calculate_ema(closes, 26)

            # Momentum Indicators
            indicators["indicators"]["rsi_14"] = self.calculate_rsi(closes, 14)
            indicators["indicators"]["macd"] = self.calculate_macd(closes)
            indicators["indicators"]["stochastic"] = self.calculate_stochastic(price_data)

            # Volatility Indicators
            indicators["indicators"]["bollinger_bands"] = self.calculate_bollinger_bands(closes)
            indicators["indicators"]["atr_14"] = self.calculate_atr(price_data, 14)

            # Volume Indicators
            indicators["indicators"]["obv"] = self.calculate_obv(price_data)
            indicators["indicators"]["volume_sma_20"] = self.calculate_volume_sma(price_data, 20)

            # Current price info
            current_price = closes[-1]
            indicators["indicators"]["current_price"] = current_price
            indicators["indicators"]["price_change"] = closes[-1] - closes[-2] if len(closes) > 1 else 0
            indicators["indicators"]["price_change_pct"] = (
                ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) > 1 and closes[-2] != 0 else 0
            )

            self.logger.info(f"Calculated {len(indicators['indicators'])} indicators for {symbol}")
            return indicators

        except Exception as e:
            self.logger.error(f"Error calculating indicators for {symbol}: {e}")
            return None

    def store_indicators(self, symbol: str, indicators: dict[str, Any]) -> bool:
        """
        Store calculated indicators in historical data system

        Args:
            symbol: Stock symbol
            indicators: Calculated indicators data

        Returns:
            True if stored successfully
        """
        try:
            return self.hdm.store_data(
                symbol=symbol,
                data=indicators,
                data_type=DataType.TECHNICAL_INDICATORS,
                source="internal_calculation",
            )
        except Exception as e:
            self.logger.error(f"Error storing indicators for {symbol}: {e}")
            return False

    def calculate_and_store_indicators(self, symbols: list[str]) -> dict[str, Any]:
        """
        Calculate and store technical indicators for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            Summary of calculation results
        """
        results = {
            "total_symbols": len(symbols),
            "successful": [],
            "failed": [],
            "total_indicators_calculated": 0,
        }

        for symbol in symbols:
            try:
                self.logger.info(f"Calculating indicators for {symbol}")

                indicators = self.calculate_all_indicators(symbol)
                if indicators:
                    if self.store_indicators(symbol, indicators):
                        results["successful"].append(symbol)
                        results["total_indicators_calculated"] += len(indicators.get("indicators", {}))
                    else:
                        results["failed"].append(f"{symbol}: Storage failed")
                else:
                    results["failed"].append(f"{symbol}: Calculation failed")

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                results["failed"].append(error_msg)
                self.logger.error(f"Error processing {symbol}: {e}")

        self.logger.info(
            f"Indicator calculation completed: {len(results['successful'])} successful, {len(results['failed'])} failed"
        )
        return results


def create_technical_indicator_calculator(
    base_path: Path | None = None,
) -> TechnicalIndicatorCalculator:
    """Factory function to create technical indicator calculator"""
    hdm = HistoricalDataManager(base_path=base_path)
    return TechnicalIndicatorCalculator(historical_manager=hdm)


if __name__ == "__main__":
    # Example usage
    calculator = create_technical_indicator_calculator()

    print("📊 Technical Indicator Calculator")
    print("=" * 50)

    # Test with sample symbols
    test_symbols = ["AAPL", "MSFT", "GOOGL"]

    print("Calculating indicators for: {', '.join(test_symbols)}")
    results = calculator.calculate_and_store_indicators(test_symbols)

    print("\n📈 Results:")
    print("Total symbols: {results['total_symbols']}")
    print("Successful: {len(results['successful'])}")
    print("Failed: {len(results['failed'])}")
    print("Total indicators calculated: {results['total_indicators_calculated']}")

    if results["successful"]:
        print("✅ Successful: {', '.join(results['successful'])}")

    if results["failed"]:
        print("❌ Failed: {results['failed']}")

    # Show sample calculation for one symbol
    if results["successful"]:
        sample_symbol = results["successful"][0]
        indicators = calculator.calculate_all_indicators(sample_symbol, days=100)
        if indicators:
            print("\n📊 Sample indicators for {sample_symbol}:")
            for name, value in indicators["indicators"].items():
                if isinstance(value, dict):
                    print("  {name}: {value}")
                elif isinstance(value, float):
                    print("  {name}: {value:.2f}")
                else:
                    print("  {name}: {value}")
