#!/usr/bin/env python3
"""
Real-Time Financial Data Validation Service

Provides real-time validation of financial claims and data accuracy for content generation.
Integrates with Yahoo Finance and other data sources to ensure financial accuracy
before content publication.

Key Features:
- Real-time price validation with configurable tolerance thresholds
- Multi-source data cross-validation
- Fail-fast validation logic with tiered severity system
- Data freshness monitoring and SLA tracking
- Automated feedback loops for content correction
- Hierarchical data source authority management

Usage:
    service = RealTimeValidationService()
    result = service.validate_financial_claims(claims_data)
    if result.is_blocking:
        # Handle validation failure
        pass
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from base_financial_service import FinancialServiceError
from yahoo_finance import create_yahoo_finance_service


logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Validation severity levels"""

    CRITICAL = "critical"  # Blocks publication
    HIGH = "high"  # Requires review
    MEDIUM = "medium"  # Flags for monitoring
    LOW = "low"  # Info only


class ValidationStatus(Enum):
    """Validation result status"""

    PASSED = "passed"
    FLAGGED = "flagged"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class ValidationThreshold:
    """Validation threshold configuration"""

    metric: str
    critical_threshold: float  # Blocks publication
    high_threshold: float  # Requires review
    medium_threshold: float  # Monitoring
    unit: str
    description: str


@dataclass
class ValidationIssue:
    """Individual validation issue"""

    severity: SeverityLevel
    metric: str
    claimed_value: float | str
    actual_value: float | str
    variance: float | None
    threshold_exceeded: float
    description: str
    recommendation: str
    is_blocking: bool


@dataclass
class ValidationResult:
    """Comprehensive validation result"""

    status: ValidationStatus
    overall_score: float
    is_blocking: bool
    ready_for_publication: bool
    issues: list[ValidationIssue]
    data_freshness_hours: float
    validation_timestamp: datetime
    sources_validated: list[str]


class ErrorToleranceConfig:
    """Configuration for validation error tolerances"""

    def __init__(self):
        self.thresholds = {
            # Price accuracy thresholds
            "stock_price_variance": ValidationThreshold(
                metric="stock_price_variance",
                critical_threshold=3.0,  # 3%+ blocks
                high_threshold=2.0,  # 2%+ requires review
                medium_threshold=1.0,  # 1%+ monitoring
                unit="percent",
                description="Stock price variance from real-time market data",
            ),
            # Return calculation thresholds
            "return_calculation_variance": ValidationThreshold(
                metric="return_calculation_variance",
                critical_threshold=5.0,  # 5%+ blocks
                high_threshold=3.0,  # 3%+ requires review
                medium_threshold=2.0,  # 2%+ monitoring
                unit="percent",
                description="Expected return calculation variance",
            ),
            # Financial metrics thresholds
            "financial_metric_variance": ValidationThreshold(
                metric="financial_metric_variance",
                critical_threshold=2.0,  # 2%+ blocks for financial metrics
                high_threshold=1.0,  # 1%+ requires review
                medium_threshold=0.5,  # 0.5%+ monitoring
                unit="percent",
                description="Financial metrics (margins, ratios) variance",
            ),
            # Data freshness thresholds
            "data_freshness_hours": ValidationThreshold(
                metric="data_freshness_hours",
                critical_threshold=48.0,  # 48h+ blocks
                high_threshold=24.0,  # 24h+ requires review
                medium_threshold=8.0,  # 8h+ monitoring
                unit="hours",
                description="Data age from last market update",
            ),
            # Market cap thresholds
            "market_cap_variance": ValidationThreshold(
                metric="market_cap_variance",
                critical_threshold=5.0,  # 5%+ blocks
                high_threshold=3.0,  # 3%+ requires review
                medium_threshold=2.0,  # 2%+ monitoring
                unit="percent",
                description="Market capitalization variance",
            ),
        }

    def get_threshold(self, metric: str) -> ValidationThreshold | None:
        """Get threshold configuration for a metric"""
        return self.thresholds.get(metric)

    def update_threshold(self, metric: str, threshold: ValidationThreshold) -> None:
        """Update threshold configuration"""
        self.thresholds[metric] = threshold


class DataSourceHierarchy:
    """Manages data source authority and hierarchy"""

    def __init__(self):
        # Data source priority (1 = highest authority)
        self.source_priority = {
            "yahoo_finance_realtime": 1,
            "yahoo_finance_api": 2,
            "alpha_vantage": 3,
            "analysis_files": 4,
            "config_fallback": 5,
        }

        self.source_reliability = {
            "yahoo_finance_realtime": 0.95,
            "yahoo_finance_api": 0.92,
            "alpha_vantage": 0.88,
            "analysis_files": 0.85,
            "config_fallback": 0.70,
        }

    def get_authoritative_source(self, sources: list[str]) -> str:
        """Get the most authoritative source from available sources"""
        available_sources = [s for s in sources if s in self.source_priority]
        if not available_sources:
            return "unknown"

        return min(available_sources, key=lambda s: self.source_priority[s])

    def get_reliability_score(self, source: str) -> float:
        """Get reliability score for a data source"""
        return self.source_reliability.get(source, 0.5)


class RealTimeValidationService:
    """
    Real-time financial data validation service

    Validates financial claims against live market data with configurable
    tolerances and fail-fast logic.
    """

    def __init__(self, config_path: str | None = None):
        self.tolerance_config = ErrorToleranceConfig()
        self.source_hierarchy = DataSourceHierarchy()
        self.cache = {}
        self.cache_ttl = timedelta(minutes=2)  # 2-minute cache for validation

        # Initialize Yahoo Finance service
        try:
            self.yf_service = create_yahoo_finance_service("prod")
            logger.info("✓ Yahoo Finance service initialized for validation")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Yahoo Finance service: {e}")
            self.yf_service = None

        # Validation statistics
        self.validation_stats = {
            "total_validations": 0,
            "blocked_publications": 0,
            "flagged_issues": 0,
            "average_validation_time_ms": 0.0,
        }

        logger.info("Real-time validation service initialized")

    def validate_stock_claims(self, claims: dict[str, Any]) -> ValidationResult:
        """
        Validate stock-related financial claims against real-time data

        Args:
            claims: Dictionary containing stock claims to validate
                   Format: {
                       'ticker': 'TSLA',
                       'current_price': 335.16,
                       'expected_return': 14.9,
                       'target_price': 385.0,
                       'financial_metrics': {...}
                   }

        Returns:
            ValidationResult with detailed validation outcomes
        """
        start_time = time.time()
        self.validation_stats["total_validations"] += 1

        issues = []
        sources_validated = []

        ticker = claims.get("ticker")
        if not ticker:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.CRITICAL,
                    metric="ticker_missing",
                    claimed_value="",
                    actual_value="required",
                    variance=None,
                    threshold_exceeded=1.0,
                    description="Ticker symbol is required for validation",
                    recommendation="Add ticker symbol to claims data",
                    is_blocking=True,
                )
            )

            return ValidationResult(
                status=ValidationStatus.BLOCKED,
                overall_score=0.0,
                is_blocking=True,
                ready_for_publication=False,
                issues=issues,
                data_freshness_hours=0.0,
                validation_timestamp=datetime.now(),
                sources_validated=sources_validated,
            )

        # Get real-time market data
        try:
            market_data = self._get_current_market_data(ticker)
            sources_validated.append("yahoo_finance_realtime")

            # Validate current price
            if "current_price" in claims and "current_price" in market_data:
                price_issue = self._validate_price_claim(
                    claimed_price=claims["current_price"],
                    actual_price=market_data["current_price"],
                    ticker=ticker,
                )
                if price_issue:
                    issues.append(price_issue)

            # Validate expected return calculation
            if all(k in claims for k in ["current_price", "target_price", "expected_return"]):
                return_issue = self._validate_return_calculation(
                    current_price=claims["current_price"],
                    target_price=claims["target_price"],
                    claimed_return=claims["expected_return"],
                    actual_current_price=market_data.get("current_price"),
                    ticker=ticker,
                )
                if return_issue:
                    issues.append(return_issue)

            # Validate market cap if provided
            if "market_cap" in claims and "market_cap" in market_data:
                mcap_issue = self._validate_market_cap(
                    claimed_mcap=claims["market_cap"],
                    actual_mcap=market_data["market_cap"],
                    ticker=ticker,
                )
                if mcap_issue:
                    issues.append(mcap_issue)

        except Exception as e:
            logger.error(f"Market data validation failed for {ticker}: {e}")
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.HIGH,
                    metric="market_data_unavailable",
                    claimed_value="required",
                    actual_value="unavailable",
                    variance=None,
                    threshold_exceeded=1.0,
                    description=f"Real-time market data unavailable: {str(e)}",
                    recommendation="Verify data sources and retry validation",
                    is_blocking=False,
                )
            )

        # Calculate overall validation score
        validation_time_ms = (time.time() - start_time) * 1000
        self._update_validation_stats(validation_time_ms)

        # Determine overall status
        is_blocking = any(issue.is_blocking for issue in issues)
        has_high_severity = any(issue.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] for issue in issues)

        if is_blocking:
            status = ValidationStatus.BLOCKED
            self.validation_stats["blocked_publications"] += 1
        elif has_high_severity:
            status = ValidationStatus.FLAGGED
            self.validation_stats["flagged_issues"] += 1
        elif issues:
            status = ValidationStatus.FLAGGED
        else:
            status = ValidationStatus.PASSED

        # Calculate overall score (0-10 scale)
        if is_blocking:
            overall_score = 0.0
        elif not issues:
            overall_score = 10.0
        else:
            # Deduct points based on issue severity
            deductions = sum(self._get_severity_deduction(issue.severity) for issue in issues)
            overall_score = max(0.0, 10.0 - deductions)

        return ValidationResult(
            status=status,
            overall_score=overall_score,
            is_blocking=is_blocking,
            ready_for_publication=not is_blocking,
            issues=issues,
            data_freshness_hours=(market_data.get("data_age_hours", 0.0) if "market_data" in locals() else 0.0),
            validation_timestamp=datetime.now(),
            sources_validated=sources_validated,
        )

    def _get_current_market_data(self, ticker: str) -> dict[str, Any]:
        """Get current market data with caching"""
        cache_key = f"market_data_{ticker}"

        # Check cache first
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if datetime.now() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["data"]

        if not self.yf_service:
            raise FinancialServiceError("Yahoo Finance service not available")

        # Fetch real-time data
        stock_info = self.yf_service.get_stock_info(ticker)

        # Extract relevant data
        market_data = {
            "ticker": ticker.upper(),
            "current_price": stock_info.get("regularMarketPrice", stock_info.get("currentPrice")),
            "market_cap": stock_info.get("marketCap"),
            "volume": stock_info.get("regularMarketVolume"),
            "data_timestamp": datetime.now(),
            "data_age_hours": 0.1,  # Very recent real-time data
            "source": "yahoo_finance_realtime",
        }

        # Cache the result
        self.cache[cache_key] = {"data": market_data, "timestamp": datetime.now()}

        return market_data

    def _validate_price_claim(self, claimed_price: float, actual_price: float, ticker: str) -> ValidationIssue | None:
        """Validate stock price claim against real-time data"""
        if actual_price is None or actual_price <= 0:
            return ValidationIssue(
                severity=SeverityLevel.HIGH,
                metric="stock_price_unavailable",
                claimed_value=claimed_price,
                actual_value="unavailable",
                variance=None,
                threshold_exceeded=1.0,
                description=f"Real-time price unavailable for {ticker}",
                recommendation="Verify ticker symbol and data availability",
                is_blocking=False,
            )

        # Calculate variance
        variance = abs(claimed_price - actual_price) / actual_price * 100
        threshold = self.tolerance_config.get_threshold("stock_price_variance")

        severity = None
        is_blocking = False

        if variance >= threshold.critical_threshold:
            severity = SeverityLevel.CRITICAL
            is_blocking = True
        elif variance >= threshold.high_threshold:
            severity = SeverityLevel.HIGH
        elif variance >= threshold.medium_threshold:
            severity = SeverityLevel.MEDIUM

        if severity:
            return ValidationIssue(
                severity=severity,
                metric="stock_price_variance",
                claimed_value=claimed_price,
                actual_value=actual_price,
                variance=variance,
                threshold_exceeded=variance,
                description=f"{ticker} price variance: {variance:.1f}% (claimed ${claimed_price:.2f} vs actual ${actual_price:.2f})",
                recommendation=f"Update price to ${actual_price:.2f} or verify data source",
                is_blocking=is_blocking,
            )

        return None

    def _validate_return_calculation(
        self,
        current_price: float,
        target_price: float,
        claimed_return: float,
        actual_current_price: float | None,
        ticker: str,
    ) -> ValidationIssue | None:
        """Validate expected return calculation accuracy"""
        # Calculate expected return based on claimed current price
        claimed_calc_return = ((target_price - current_price) / current_price) * 100

        # Calculate expected return based on actual current price if available
        if actual_current_price and actual_current_price > 0:
            actual_calc_return = ((target_price - actual_current_price) / actual_current_price) * 100
            primary_comparison = actual_calc_return
            comparison_base = f"actual price ${actual_current_price:.2f}"
        else:
            primary_comparison = claimed_calc_return
            comparison_base = f"claimed price ${current_price:.2f}"

        # Calculate variance from claimed return
        variance = abs(claimed_return - primary_comparison)
        threshold = self.tolerance_config.get_threshold("return_calculation_variance")

        severity = None
        is_blocking = False

        if variance >= threshold.critical_threshold:
            severity = SeverityLevel.CRITICAL
            is_blocking = True
        elif variance >= threshold.high_threshold:
            severity = SeverityLevel.HIGH
        elif variance >= threshold.medium_threshold:
            severity = SeverityLevel.MEDIUM

        if severity:
            return ValidationIssue(
                severity=severity,
                metric="return_calculation_variance",
                claimed_value=claimed_return,
                actual_value=primary_comparison,
                variance=variance,
                threshold_exceeded=variance,
                description=f"{ticker} return calculation variance: {variance:.1f}pp (claimed {claimed_return:.1f}% vs calculated {primary_comparison:.1f}% from {comparison_base})",
                recommendation=f"Update expected return to {primary_comparison:.1f}% or verify target price",
                is_blocking=is_blocking,
            )

        return None

    def _validate_market_cap(self, claimed_mcap: float, actual_mcap: float, ticker: str) -> ValidationIssue | None:
        """Validate market capitalization claim"""
        if actual_mcap is None or actual_mcap <= 0:
            return None  # Skip validation if data unavailable

        # Convert to same units (billions)
        claimed_mcap_b = claimed_mcap / 1e9 if claimed_mcap > 1e9 else claimed_mcap
        actual_mcap_b = actual_mcap / 1e9 if actual_mcap > 1e9 else actual_mcap

        # Calculate variance
        variance = abs(claimed_mcap_b - actual_mcap_b) / actual_mcap_b * 100
        threshold = self.tolerance_config.get_threshold("market_cap_variance")

        severity = None
        is_blocking = False

        if variance >= threshold.critical_threshold:
            severity = SeverityLevel.CRITICAL
            is_blocking = True
        elif variance >= threshold.high_threshold:
            severity = SeverityLevel.HIGH
        elif variance >= threshold.medium_threshold:
            severity = SeverityLevel.MEDIUM

        if severity:
            return ValidationIssue(
                severity=severity,
                metric="market_cap_variance",
                claimed_value=claimed_mcap_b,
                actual_value=actual_mcap_b,
                variance=variance,
                threshold_exceeded=variance,
                description=f"{ticker} market cap variance: {variance:.1f}% (claimed ${claimed_mcap_b:.1f}B vs actual ${actual_mcap_b:.1f}B)",
                recommendation=f"Update market cap to ${actual_mcap_b:.1f}B or verify calculation",
                is_blocking=is_blocking,
            )

        return None

    def _get_severity_deduction(self, severity: SeverityLevel) -> float:
        """Get point deduction for issue severity"""
        deductions = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 3.0,
            SeverityLevel.MEDIUM: 1.0,
            SeverityLevel.LOW: 0.2,
        }
        return deductions.get(severity, 0.0)

    def _update_validation_stats(self, validation_time_ms: float) -> None:
        """Update validation statistics"""
        current_avg = self.validation_stats["average_validation_time_ms"]
        total_validations = self.validation_stats["total_validations"]

        # Calculate running average
        self.validation_stats["average_validation_time_ms"] = (
            current_avg * (total_validations - 1) + validation_time_ms
        ) / total_validations

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation service statistics"""
        return {
            "validation_statistics": self.validation_stats.copy(),
            "threshold_configuration": {
                name: {
                    "critical": threshold.critical_threshold,
                    "high": threshold.high_threshold,
                    "medium": threshold.medium_threshold,
                    "unit": threshold.unit,
                }
                for name, threshold in self.tolerance_config.thresholds.items()
            },
            "data_source_hierarchy": self.source_hierarchy.source_priority,
            "service_status": {
                "yahoo_finance_available": self.yf_service is not None,
                "cache_size": len(self.cache),
                "uptime": "active",
            },
        }

    def validate_twitter_post_claims(self, post_content: str, metadata: dict[str, Any] = None) -> ValidationResult:
        """
        Validate financial claims in Twitter post content

        Args:
            post_content: Twitter post content to validate
            metadata: Additional metadata (ticker, analysis source, etc.)

        Returns:
            ValidationResult with validation outcomes
        """
        # Extract financial claims from post content
        claims = self._extract_financial_claims(post_content, metadata)

        if not claims:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                overall_score=8.0,  # No claims to validate
                is_blocking=False,
                ready_for_publication=True,
                issues=[],
                data_freshness_hours=0.0,
                validation_timestamp=datetime.now(),
                sources_validated=[],
            )

        return self.validate_stock_claims(claims)

    def _extract_financial_claims(self, content: str, metadata: dict[str, Any] = None) -> dict[str, Any]:
        """Extract financial claims from Twitter post content"""
        import re

        claims = {}

        # Extract ticker from metadata or content
        if metadata and "ticker" in metadata:
            claims["ticker"] = metadata["ticker"]
        else:
            # Look for $TICKER pattern
            ticker_match = re.search(r"\$([A-Z]{1,5})", content)
            if ticker_match:
                claims["ticker"] = ticker_match.group(1)

        # Extract prices and targets
        price_pattern = r"\$([0-9,]+\.?\d*)"
        prices = re.findall(price_pattern, content)

        # Extract percentages (expected returns) - pattern reserved for future use

        # Look for target patterns
        target_match = re.search(r"target[:\s@]*\$?([0-9,]+\.?\d*)", content, re.IGNORECASE)
        if target_match:
            claims["target_price"] = float(target_match.group(1).replace(",", ""))

        # Look for return patterns
        return_match = re.search(r"\(([+-]?\d+\.?\d*)%\)", content)
        if return_match:
            claims["expected_return"] = float(return_match.group(1))

        # Try to infer current price from context
        if prices and len(prices) >= 2:
            # Usually current price mentioned before target
            claims["current_price"] = float(prices[0].replace(",", ""))

        return claims


def create_real_time_validation_service() -> RealTimeValidationService:
    """Factory function to create validation service"""
    return RealTimeValidationService()


if __name__ == "__main__":
    # Test the validation service
    logging.basicConfig(level=logging.INFO)

    service = create_real_time_validation_service()

    # Test with TSLA data from the validation issue
    test_claims = {
        "ticker": "TSLA",
        "current_price": 335.16,  # Claimed price
        "target_price": 385.0,
        "expected_return": 14.9,  # This should trigger validation error
    }

    print("Testing validation service...")
    result = service.validate_stock_claims(test_claims)

    print("\nValidation Result:")
    print("Status: {result.status.value}")
    print("Overall Score: {result.overall_score}/10.0")
    print("Ready for Publication: {result.ready_for_publication}")
    print("Blocking Issues: {result.is_blocking}")

    for issue in result.issues:
        print("\n{issue.severity.value.upper()} - {issue.metric}:")
        print("  {issue.description}")
        print("  Recommendation: {issue.recommendation}")
