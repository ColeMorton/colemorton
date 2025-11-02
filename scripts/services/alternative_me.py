"""
Alternative.me Service

Production-grade Alternative.me Crypto Fear & Greed Index integration with:
- Most popular crypto sentiment indicator with daily updates
- 0-100 scale sentiment scoring with historical data
- Multiple data sources integration for comprehensive sentiment analysis
- Completely free API with no authentication required
- Perfect for Bitcoin cycle analysis and market sentiment tracking
"""

import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))


class AlternativeMeService(BaseFinancialService):
    """
    Alternative.me service extending BaseFinancialService

    Provides access to Alternative.me's Crypto Fear & Greed Index including:
    - Current and historical sentiment data
    - Date-specific queries and range analysis
    - Statistical analysis and correlation studies
    - Market sentiment summaries and extreme value detection
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Alternative.me is completely free, no API key required
        if not self.config.base_url:
            self.config.base_url = "https://api.alternative.me"

    def _validate_response(
        self, data: dict[str, Any] | list[dict[str, Any]], endpoint: str
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Validate Alternative.me response data"""

        if not data:
            raise DataNotFoundError(f"No data returned from Alternative.me {endpoint}")

        # Alternative.me returns data in 'data' field
        if isinstance(data, dict):
            if "data" in data:
                return data["data"]
            # Some endpoints return direct data
            return data

        return data

    def _classify_sentiment(self, value: int) -> str:
        """Classify Fear & Greed value into sentiment category"""
        if value <= 20:
            return "Extreme Fear"
        if value <= 40:
            return "Fear"
        if value <= 60:
            return "Neutral"
        if value <= 80:
            return "Greed"
        return "Extreme Greed"

    def get_current_fear_greed(self) -> dict[str, Any]:
        """Get current Fear & Greed Index value"""
        endpoint = "/fng/"
        data = self._make_request_with_retry(endpoint)

        validated_data = self._validate_response(data, "current fear greed")

        # Enhance data with sentiment classification
        if isinstance(validated_data, list) and len(validated_data) > 0:
            current = validated_data[0]
            current["sentiment_classification"] = self._classify_sentiment(int(current["value"]))
            current["timestamp_formatted"] = datetime.fromtimestamp(int(current["timestamp"])).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            return current

        return validated_data

    def get_historical_fear_greed(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get historical Fear & Greed Index values"""
        if limit > 1000:
            limit = 1000
        elif limit < 1:
            limit = 1

        endpoint = f"/fng/?limit={limit}"
        data = self._make_request_with_retry(endpoint)

        validated_data = self._validate_response(data, "historical fear greed")

        # Enhance data with sentiment classification
        if isinstance(validated_data, list):
            for item in validated_data:
                item["sentiment_classification"] = self._classify_sentiment(int(item["value"]))
                item["timestamp_formatted"] = datetime.fromtimestamp(int(item["timestamp"])).strftime("%Y-%m-%d")

        return validated_data

    def get_fear_greed_by_date(self, date_str: str) -> dict[str, Any]:
        """Get Fear & Greed Index for a specific date"""
        # Parse date - handle both DD-MM-YYYY and YYYY-MM-DD formats
        try:
            if "-" in date_str:
                parts = date_str.split("-")
                if len(parts[0]) == 4:  # YYYY-MM-DD
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                else:  # DD-MM-YYYY
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            else:
                raise ValueError("Invalid date format")

            formatted_date = date_obj.strftime("%d-%m-%Y")
        except:
            raise ValueError("Invalid date format. Use DD-MM-YYYY or YYYY-MM-DD")

        endpoint = f"/fng/?limit=1&date={formatted_date}"
        data = self._make_request_with_retry(endpoint)

        validated_data = self._validate_response(data, f"fear greed for {date_str}")

        if isinstance(validated_data, list) and len(validated_data) > 0:
            item = validated_data[0]
            item["sentiment_classification"] = self._classify_sentiment(int(item["value"]))
            item["timestamp_formatted"] = datetime.fromtimestamp(int(item["timestamp"])).strftime("%Y-%m-%d")
            return item

        return {}

    def get_fear_greed_range(self, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """Get Fear & Greed Index for a date range"""
        try:
            # Parse dates
            if "-" in start_date and len(start_date.split("-")[0]) == 4:
                start_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_obj = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                start_obj = datetime.strptime(start_date, "%d-%m-%Y")
                end_obj = datetime.strptime(end_date, "%d-%m-%Y")

            # Calculate days difference
            days_diff = (end_obj - start_obj).days + 1
            if days_diff > 1000:
                days_diff = 1000

        except:
            raise ValueError("Invalid date format. Use DD-MM-YYYY or YYYY-MM-DD")

        # Get historical data and filter by date range
        historical_data = self.get_historical_fear_greed(days_diff)

        # Filter data for the specific range
        filtered_data = []
        for item in historical_data:
            item_date = datetime.fromtimestamp(int(item["timestamp"]))
            if start_obj <= item_date <= end_obj:
                filtered_data.append(item)

        return filtered_data

    def get_sentiment_analysis(self, days: int = 30) -> dict[str, Any]:
        """Get sentiment analysis with statistics over specified period"""
        historical_data = self.get_historical_fear_greed(days)

        if not historical_data:
            return {}

        values = [int(item["value"]) for item in historical_data]

        # Calculate statistics
        analysis = {
            "period_days": days,
            "data_points": len(values),
            "current_value": values[0] if values else 0,
            "average": round(statistics.mean(values), 2),
            "median": statistics.median(values),
            "min_value": min(values),
            "max_value": max(values),
            "standard_deviation": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
            "volatility": round(statistics.stdev(values) / statistics.mean(values) * 100, 2)
            if len(values) > 1 and statistics.mean(values) > 0
            else 0,
        }

        # Zone distribution
        zones = {
            "Extreme Fear (0-20)": len([v for v in values if v <= 20]),
            "Fear (21-40)": len([v for v in values if 21 <= v <= 40]),
            "Neutral (41-60)": len([v for v in values if 41 <= v <= 60]),
            "Greed (61-80)": len([v for v in values if 61 <= v <= 80]),
            "Extreme Greed (81-100)": len([v for v in values if v >= 81]),
        }

        analysis["zone_distribution"] = zones
        analysis["current_sentiment"] = self._classify_sentiment(values[0] if values else 50)

        return analysis

    def get_extreme_values(self, days: int = 365) -> dict[str, Any]:
        """Get extreme fear and greed values over specified period"""
        historical_data = self.get_historical_fear_greed(days)

        if not historical_data:
            return {}

        values = [(int(item["value"]), item) for item in historical_data]
        values.sort(key=lambda x: x[0])

        extreme_fear = values[0][1]  # Lowest value
        extreme_greed = values[-1][1]  # Highest value

        return {
            "period_days": days,
            "extreme_fear": {
                "value": extreme_fear["value"],
                "date": extreme_fear["timestamp_formatted"],
                "classification": extreme_fear["sentiment_classification"],
            },
            "extreme_greed": {
                "value": extreme_greed["value"],
                "date": extreme_greed["timestamp_formatted"],
                "classification": extreme_greed["sentiment_classification"],
            },
        }

    def get_bitcoin_correlation(self, days: int = 90) -> dict[str, Any]:
        """Analyze correlation between Fear & Greed and Bitcoin price movements"""
        # Note: This is a simplified correlation analysis
        # In production, you'd want to integrate with price data from another service

        historical_data = self.get_historical_fear_greed(days)

        if not historical_data:
            return {}

        # Calculate basic sentiment trends
        values = [int(item["value"]) for item in historical_data]

        # Calculate momentum (day-over-day changes)
        changes = []
        for i in range(1, len(values)):
            change = values[i - 1] - values[i]  # Note: data is reverse chronological
            changes.append(change)

        analysis = {
            "period_days": days,
            "sentiment_trend": "Improving" if sum(changes) > 0 else "Declining",
            "average_daily_change": round(statistics.mean(changes), 2) if changes else 0,
            "volatility": round(statistics.stdev(changes), 2) if len(changes) > 1 else 0,
            "note": "Full correlation analysis requires price data integration",
        }

        return analysis

    def get_zone_distribution(self, days: int = 365) -> dict[str, Any]:
        """Get distribution of time spent in different Fear & Greed zones"""
        historical_data = self.get_historical_fear_greed(days)

        if not historical_data:
            return {}

        values = [int(item["value"]) for item in historical_data]
        total_days = len(values)

        zones = {
            "Extreme Fear (0-20)": len([v for v in values if v <= 20]),
            "Fear (21-40)": len([v for v in values if 21 <= v <= 40]),
            "Neutral (41-60)": len([v for v in values if 41 <= v <= 60]),
            "Greed (61-80)": len([v for v in values if 61 <= v <= 80]),
            "Extreme Greed (81-100)": len([v for v in values if v >= 81]),
        }

        # Calculate percentages
        zone_percentages = {zone: round((count / total_days) * 100, 1) for zone, count in zones.items()}

        return {
            "period_days": days,
            "total_data_points": total_days,
            "zone_counts": zones,
            "zone_percentages": zone_percentages,
            "dominant_sentiment": max(zone_percentages, key=zone_percentages.get),
        }

    def get_market_summary(self) -> dict[str, Any]:
        """Get comprehensive market sentiment summary"""
        current = self.get_current_fear_greed()
        analysis_30d = self.get_sentiment_analysis(30)
        extremes_1y = self.get_extreme_values(365)

        return {
            "current_index": current,
            "monthly_analysis": analysis_30d,
            "yearly_extremes": extremes_1y,
            "summary_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def create_alternative_me_service(env: str = "dev") -> AlternativeMeService:
    """
    Factory function to create AlternativeMeService with environment-specific configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured AlternativeMeService instance
    """
    try:
        # Alternative.me is completely free, no configuration needed
        service_config = ServiceConfig(
            name="alternative_me",
            api_key=None,  # No API key required
            base_url="https://api.alternative.me",
            timeout_seconds=30,
            max_retries=3,
        )

        return AlternativeMeService(service_config)

    except Exception:
        # Fallback configuration
        service_config = ServiceConfig(
            name="alternative_me",
            api_key=None,
            base_url="https://api.alternative.me",
            timeout_seconds=30,
            max_retries=3,
        )

        return AlternativeMeService(service_config)
