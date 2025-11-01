#!/usr/bin/env python3
"""
US Trading Session Manager

Provides accurate trading session timing for US stock markets with:
- NYSE and NASDAQ regular hours (9:30 AM - 4:00 PM ET)
- Market holiday detection
- Cache TTL calculation based on trading session end
- Timezone handling for Eastern Time (ET)
"""

import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


class USMarketHolidays:
    """US Stock Market Holiday Detection"""

    @staticmethod
    def get_market_holidays(year: int) -> set:
        """
        Get market holidays for a given year

        Args:
            year: Year to get holidays for

        Returns:
            Set of holiday dates as datetime.date objects
        """
        holidays = set()

        # New Year's Day
        new_years = datetime(year, 1, 1).date()
        if new_years.weekday() == 6:  # Sunday
            new_years = datetime(year, 1, 2).date()
        elif new_years.weekday() == 5:  # Saturday
            new_years = datetime(year, 1, 3).date()
        holidays.add(new_years)

        # Martin Luther King Jr. Day (3rd Monday in January)
        mlk_day = USMarketHolidays._get_nth_weekday(year, 1, 0, 3)
        holidays.add(mlk_day)

        # Presidents Day (3rd Monday in February)
        presidents_day = USMarketHolidays._get_nth_weekday(year, 2, 0, 3)
        holidays.add(presidents_day)

        # Good Friday (Friday before Easter)
        easter = USMarketHolidays._calculate_easter(year)
        good_friday = easter - timedelta(days=2)
        holidays.add(good_friday.date())

        # Memorial Day (last Monday in May)
        memorial_day = USMarketHolidays._get_last_weekday(year, 5, 0)
        holidays.add(memorial_day)

        # Juneteenth (June 19)
        juneteenth = datetime(year, 6, 19).date()
        if juneteenth.weekday() == 6:  # Sunday
            juneteenth = datetime(year, 6, 20).date()
        elif juneteenth.weekday() == 5:  # Saturday
            juneteenth = datetime(year, 6, 18).date()
        holidays.add(juneteenth)

        # Independence Day (July 4)
        independence_day = datetime(year, 7, 4).date()
        if independence_day.weekday() == 6:  # Sunday
            independence_day = datetime(year, 7, 5).date()
        elif independence_day.weekday() == 5:  # Saturday
            independence_day = datetime(year, 7, 3).date()
        holidays.add(independence_day)

        # Labor Day (1st Monday in September)
        labor_day = USMarketHolidays._get_nth_weekday(year, 9, 0, 1)
        holidays.add(labor_day)

        # Thanksgiving Day (4th Thursday in November)
        thanksgiving = USMarketHolidays._get_nth_weekday(year, 11, 3, 4)
        holidays.add(thanksgiving)

        # Christmas Day (December 25)
        christmas = datetime(year, 12, 25).date()
        if christmas.weekday() == 6:  # Sunday
            christmas = datetime(year, 12, 26).date()
        elif christmas.weekday() == 5:  # Saturday
            christmas = datetime(year, 12, 24).date()
        holidays.add(christmas)

        return holidays

    @staticmethod
    def _get_nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime.date:
        """Get the nth occurrence of a weekday in a month"""
        first_day = datetime(year, month, 1)
        first_weekday = first_day.weekday()

        # Calculate days to first occurrence of target weekday
        days_to_weekday = (weekday - first_weekday) % 7

        # Calculate date of nth occurrence
        target_date = first_day + timedelta(days=days_to_weekday + (n - 1) * 7)
        return target_date.date()

    @staticmethod
    def _get_last_weekday(year: int, month: int, weekday: int) -> datetime.date:
        """Get the last occurrence of a weekday in a month"""
        # Start from the last day of the month and work backwards
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)

        # Find the last occurrence of the target weekday
        days_back = (last_day.weekday() - weekday) % 7
        target_date = last_day - timedelta(days=days_back)
        return target_date.date()

    @staticmethod
    def _calculate_easter(year: int) -> datetime:
        """Calculate Easter Sunday using the algorithm"""
        # Anonymous Gregorian algorithm
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        ell = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * ell) // 451
        month = (h + ell - 7 * m + 114) // 31
        day = ((h + ell - 7 * m + 114) % 31) + 1

        return datetime(year, month, day)


class TradingSessionManager:
    """
    US Trading Session Management

    Provides accurate timing for US stock market sessions with:
    - Regular market hours: 9:30 AM - 4:00 PM ET
    - Holiday and weekend detection
    - Cache TTL calculations based on session timing
    """

    def __init__(self):
        """Initialize Trading Session Manager"""
        self.logger = logging.getLogger(__name__)

        # US Eastern Time zone
        self.eastern_tz = ZoneInfo("America/New_York")

        # Regular trading hours (ET)
        self.market_open = time(9, 30)  # 9:30 AM ET
        self.market_close = time(16, 0)  # 4:00 PM ET

        # Cache buffer after market close
        self.cache_buffer_minutes = 5

        # Holiday cache
        self._holiday_cache: dict[int, set] = {}

    def is_trading_day(self, dt: datetime | None = None) -> bool:
        """
        Check if a given date is a trading day

        Args:
            dt: DateTime to check (defaults to current ET time)

        Returns:
            True if it's a trading day (weekday, not holiday)
        """
        if dt is None:
            dt = self.get_current_et_time()

        # Convert to ET if needed
        if dt.tzinfo is None:
            dt = self.eastern_tz.localize(dt)
        elif dt.tzinfo != self.eastern_tz:
            dt = dt.astimezone(self.eastern_tz)

        # Check if weekday (Monday=0, Sunday=6)
        if dt.weekday() >= 5:  # Saturday or Sunday
            return False

        # Check if market holiday
        return not self.is_market_holiday(dt.date())

    def is_market_holiday(self, date_obj) -> bool:
        """
        Check if a date is a market holiday

        Args:
            date_obj: Date to check (datetime.date object)

        Returns:
            True if it's a market holiday
        """
        year = date_obj.year

        # Cache holidays for the year
        if year not in self._holiday_cache:
            self._holiday_cache[year] = USMarketHolidays.get_market_holidays(year)

        return date_obj in self._holiday_cache[year]

    def is_market_open(self, dt: datetime | None = None) -> bool:
        """
        Check if the market is currently open

        Args:
            dt: DateTime to check (defaults to current ET time)

        Returns:
            True if market is open
        """
        if dt is None:
            dt = self.get_current_et_time()

        # Convert to ET if needed
        if dt.tzinfo is None:
            dt = self.eastern_tz.localize(dt)
        elif dt.tzinfo != self.eastern_tz:
            dt = dt.astimezone(self.eastern_tz)

        # Check if trading day
        if not self.is_trading_day(dt):
            return False

        # Check if within trading hours
        current_time = dt.time()
        return self.market_open <= current_time <= self.market_close

    def get_current_et_time(self) -> datetime:
        """Get current time in Eastern Time"""
        return datetime.now(self.eastern_tz)

    def get_next_market_close(self, dt: datetime | None = None) -> datetime:
        """
        Get the next market close time

        Args:
            dt: Reference datetime (defaults to current ET time)

        Returns:
            DateTime of next market close in ET
        """
        if dt is None:
            dt = self.get_current_et_time()

        # Convert to ET if needed
        if dt.tzinfo is None:
            dt = self.eastern_tz.localize(dt)
        elif dt.tzinfo != self.eastern_tz:
            dt = dt.astimezone(self.eastern_tz)

        # Start with today's close
        today_close = dt.replace(
            hour=self.market_close.hour,
            minute=self.market_close.minute,
            second=0,
            microsecond=0,
        )

        # If today is a trading day and we haven't passed close time
        if self.is_trading_day(dt) and dt.time() < self.market_close:
            return today_close

        # Otherwise, find next trading day
        next_day = dt + timedelta(days=1)
        while not self.is_trading_day(next_day):
            next_day += timedelta(days=1)

        return next_day.replace(
            hour=self.market_close.hour,
            minute=self.market_close.minute,
            second=0,
            microsecond=0,
        )

    def get_cache_ttl_seconds(self, dt: datetime | None = None) -> int:
        """
        Calculate cache TTL in seconds until next market close + buffer

        For market data, cache should expire at the end of the trading session
        plus a small buffer to account for delayed data.

        Args:
            dt: Reference datetime (defaults to current ET time)

        Returns:
            TTL in seconds until market close + buffer
        """
        if dt is None:
            dt = self.get_current_et_time()

        next_close = self.get_next_market_close(dt)

        # Add buffer time after market close
        cache_expiry = next_close + timedelta(minutes=self.cache_buffer_minutes)

        # Calculate seconds until expiry
        time_diff = cache_expiry - dt

        # Ensure minimum TTL of 1 minute
        ttl_seconds = max(60, int(time_diff.total_seconds()))

        self.logger.debug(
            f"Market close TTL calculated: {ttl_seconds}s (expires at {cache_expiry.strftime('%Y-%m-%d %H:%M:%S %Z')})"
        )

        return ttl_seconds

    def get_market_status(self, dt: datetime | None = None) -> dict[str, any]:
        """
        Get comprehensive market status information

        Args:
            dt: Reference datetime (defaults to current ET time)

        Returns:
            Dictionary with market status details
        """
        if dt is None:
            dt = self.get_current_et_time()

        # Convert to ET if needed
        if dt.tzinfo is None:
            dt = self.eastern_tz.localize(dt)
        elif dt.tzinfo != self.eastern_tz:
            dt = dt.astimezone(self.eastern_tz)

        is_trading_day = self.is_trading_day(dt)
        is_open = self.is_market_open(dt)
        next_close = self.get_next_market_close(dt)
        cache_ttl = self.get_cache_ttl_seconds(dt)

        return {
            "current_time_et": dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "is_trading_day": is_trading_day,
            "is_market_holiday": (self.is_market_holiday(dt.date()) if is_trading_day else None),
            "is_market_open": is_open,
            "market_open_time": f"{self.market_open.strftime('%H:%M')} ET",
            "market_close_time": f"{self.market_close.strftime('%H:%M')} ET",
            "next_market_close": next_close.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "cache_ttl_seconds": cache_ttl,
            "cache_expires_at": (dt + timedelta(seconds=cache_ttl)).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }


def create_trading_session_manager() -> TradingSessionManager:
    """Factory function to create a Trading Session Manager"""
    return TradingSessionManager()


# Example usage and testing
if __name__ == "__main__":
    import json

    print("🏛️  US Trading Session Manager Test")
    print("=" * 50)

    manager = create_trading_session_manager()
    status = manager.get_market_status()

    print("📊 Current Market Status:")
    print(json.dumps(status, indent=2))

    # Test different scenarios
    test_times = [
        # Regular trading day, before open
        datetime(2024, 3, 15, 8, 0),  # Friday 8:00 AM ET
        # Regular trading day, market open
        datetime(2024, 3, 15, 11, 30),  # Friday 11:30 AM ET
        # Regular trading day, after close
        datetime(2024, 3, 15, 17, 0),  # Friday 5:00 PM ET
        # Weekend
        datetime(2024, 3, 16, 11, 0),  # Saturday 11:00 AM ET
        # Holiday (approximate)
        datetime(2024, 12, 25, 11, 0),  # Christmas Day 11:00 AM ET
    ]

    print("\n🧪 Test Scenarios:")
    print("-" * 30)

    for i, test_time in enumerate(test_times, 1):
        test_status = manager.get_market_status(test_time)
        print("\n{i}. {test_time.strftime('%Y-%m-%d %H:%M')} ET:")
        print("   Trading Day: {test_status['is_trading_day']}")
        print("   Market Open: {test_status['is_market_open']}")
        print("   Cache TTL: {test_status['cache_ttl_seconds']}s")
        print("   Next Close: {test_status['next_market_close']}")
