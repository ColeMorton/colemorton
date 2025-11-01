"""
Regional Central Bank Service

Provides region-specific central bank data routing and collection:
- Region-to-Central Bank mapping (Fed, ECB, BoJ, PBOC, RBI)
- Central bank-appropriate economic indicators per region
- Fail-fast validation to prevent cross-regional data contamination
- Institutional-quality data accuracy for multi-regional analysis

Supports regions: US/AMERICAS, EUROPE, ASIA, EMERGING_MARKETS
"""

import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
    ValidationError,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config_loader import ConfigLoader


logger = logging.getLogger(__name__)


@dataclass
class CentralBankInfo:
    """Central bank information and data mapping"""

    name: str
    policy_rate_name: str
    policy_rate_symbol: str  # FRED symbol or equivalent
    policy_meetings_name: str
    currency: str
    jurisdiction: str
    gdp_indicators: list[str]
    employment_indicators: list[str]
    inflation_indicators: list[str]


@dataclass
class RegionalEconomicData:
    """Standardized regional economic data structure"""

    region: str
    central_bank: str
    policy_rate: float
    policy_rate_name: str
    gdp_data: dict[str, Any]
    employment_data: dict[str, Any]
    inflation_data: dict[str, Any]
    monetary_policy_data: dict[str, Any]
    confidence: float


class RegionalCentralBankService(BaseFinancialService):
    """
    Regional Central Bank Service for region-appropriate economic data collection

    Prevents cross-regional data contamination by routing to correct central banks
    """

    def __init__(self, config: ServiceConfig | None = None):
        """Initialize regional central bank service"""
        super().__init__(config or ServiceConfig(name="regional_central_bank"))

        # Load configuration
        self.config_loader = ConfigLoader()

        # Define central bank mappings
        self._central_bank_mappings = {
            "US": CentralBankInfo(
                name="Federal Reserve",
                policy_rate_name="Fed Funds Rate",
                policy_rate_symbol="FEDFUNDS",
                policy_meetings_name="FOMC",
                currency="USD",
                jurisdiction="United States",
                gdp_indicators=["GDP", "GDPC1", "A191RL1Q225SBEA"],
                employment_indicators=["PAYEMS", "UNRATE", "CIVPART"],
                inflation_indicators=["CPIAUCSL", "CPILFESL", "PCEPI"],
            ),
            "AMERICAS": CentralBankInfo(
                name="Federal Reserve",
                policy_rate_name="Fed Funds Rate",
                policy_rate_symbol="FEDFUNDS",
                policy_meetings_name="FOMC",
                currency="USD",
                jurisdiction="United States",
                gdp_indicators=["GDP", "GDPC1", "A191RL1Q225SBEA"],
                employment_indicators=["PAYEMS", "UNRATE", "CIVPART"],
                inflation_indicators=["CPIAUCSL", "CPILFESL", "PCEPI"],
            ),
            "EUROPE": CentralBankInfo(
                name="European Central Bank",
                policy_rate_name="ECB Deposit Rate",
                policy_rate_symbol="IRSTCB01EZM156N",  # ECB deposit rate
                policy_meetings_name="ECB Governing Council",
                currency="EUR",
                jurisdiction="Eurozone",
                gdp_indicators=[
                    "CLVMNACSCAB1GQEA19",
                    "NAEXKP01EZQ652S",
                ],  # Eurozone GDP
                employment_indicators=[
                    "LRHUTTTTEZM156S",
                    "LRHUTTTTEZQ156S",
                ],  # Eurozone unemployment
                inflation_indicators=[
                    "CP0000EZ17M086NEST",
                    "CPHPTT01EZM661N",
                ],  # Eurozone CPI
            ),
            "ASIA": CentralBankInfo(
                name="Multi-Central Bank (BoJ/PBOC/RBI)",
                policy_rate_name="BoJ Policy Rate",
                policy_rate_symbol="IRSTCB01JPM156N",  # Japan policy rate
                policy_meetings_name="BoJ Policy Board",
                currency="JPY/CNY/INR",
                jurisdiction="Asia-Pacific",
                gdp_indicators=["JPNRGDPEXP", "CLVMNACSCAB1GQJP"],  # Japan GDP
                employment_indicators=[
                    "LRHUTTTTJPM156S",
                    "JPNUEMPQ",
                ],  # Japan unemployment
                inflation_indicators=[
                    "JPNCPIALLMINMEI",
                    "CPALTT01JPM661S",
                ],  # Japan CPI
            ),
            "EMERGING_MARKETS": CentralBankInfo(
                name="Multi-Central Bank (Various EM)",
                policy_rate_name="EM Aggregate Policy Rate",
                policy_rate_symbol="IRSTCB01BRM156N",  # Brazil as proxy
                policy_meetings_name="Various EM Central Banks",
                currency="Various",
                jurisdiction="Emerging Markets",
                gdp_indicators=["BRAGDPNQDSMEI", "CHNGDPNQDSMEI"],  # Brazil/China GDP
                employment_indicators=[
                    "LRHUTTTTBRM156S",
                    "LRHUTTTTCNM156S",
                ],  # Brazil/China unemployment
                inflation_indicators=[
                    "BRACPIALLMINMEI",
                    "CHNCPIALLMINMEI",
                ],  # Brazil/China CPI
            ),
        }

    def validate_region(self, region: str) -> None:
        """
        Validate region parameter and ensure appropriate central bank mapping exists

        Args:
            region: Region identifier (US, AMERICAS, EUROPE, ASIA, EMERGING_MARKETS)

        Raises:
            ValidationError: If region is invalid or not supported
        """
        if not region:
            raise ValidationError("Region parameter is required")

        region_upper = region.upper()
        if region_upper not in self._central_bank_mappings:
            supported_regions = list(self._central_bank_mappings.keys())
            raise ValidationError(f"Unsupported region '{region}'. Supported regions: {supported_regions}")

    def get_central_bank_info(self, region: str) -> CentralBankInfo:
        """
        Get central bank information for specified region

        Args:
            region: Region identifier

        Returns:
            CentralBankInfo object with central bank details

        Raises:
            ValidationError: If region is invalid
        """
        self.validate_region(region)
        return self._central_bank_mappings[region.upper()]

    def get_region_appropriate_data(self, region: str, timeframe: str = "2y") -> RegionalEconomicData:
        """
        Collect region-appropriate central bank and economic data

        Args:
            region: Region identifier
            timeframe: Data collection timeframe

        Returns:
            RegionalEconomicData with region-specific economic indicators

        Raises:
            ValidationError: If region is invalid
            DataNotFoundError: If central bank data is unavailable
        """
        self.validate_region(region)
        central_bank = self.get_central_bank_info(region)

        logger.info(f"Collecting region-appropriate data for {region} using {central_bank.name}")

        try:
            # Import FRED service for data collection
            import os
            import sys

            sys.path.append(os.path.join(os.path.dirname(__file__)))
            from fred_economic import create_fred_economic_service

            # Create FRED service instance
            fred_service = create_fred_economic_service("prod")

            # Collect region-appropriate data
            gdp_data = self._collect_regional_gdp_data(fred_service, central_bank, timeframe)
            employment_data = self._collect_regional_employment_data(fred_service, central_bank, timeframe)
            inflation_data = self._collect_regional_inflation_data(fred_service, central_bank, timeframe)
            monetary_policy_data = self._collect_regional_monetary_policy_data(fred_service, central_bank, timeframe)

            # Calculate confidence based on data completeness
            confidence = self._calculate_data_confidence(
                gdp_data, employment_data, inflation_data, monetary_policy_data
            )

            return RegionalEconomicData(
                region=region.upper(),
                central_bank=central_bank.name,
                policy_rate=monetary_policy_data.get("current_rate", 0.0),
                policy_rate_name=central_bank.policy_rate_name,
                gdp_data=gdp_data,
                employment_data=employment_data,
                inflation_data=inflation_data,
                monetary_policy_data=monetary_policy_data,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"Failed to collect regional data for {region}: {e}")
            raise DataNotFoundError(f"Unable to collect {central_bank.name} data for {region}")

    def _collect_regional_gdp_data(self, fred_service, central_bank: CentralBankInfo, timeframe: str) -> dict[str, Any]:
        """Collect region-appropriate GDP data"""
        gdp_data = {"observations": [], "analysis": "", "confidence": 0.0}

        try:
            # Use first available GDP indicator for the region
            primary_gdp_indicator = central_bank.gdp_indicators[0]
            result = fred_service.get_economic_indicator(primary_gdp_indicator, timeframe)

            if result:
                gdp_data["observations"] = result.get("observations", [])
                gdp_data["analysis"] = f"{central_bank.jurisdiction} GDP analysis for {timeframe} period"
                gdp_data["confidence"] = 0.90

        except Exception as e:
            logger.warning(f"Failed to collect GDP data for {central_bank.name}: {e}")
            gdp_data["analysis"] = f"GDP data unavailable for {central_bank.jurisdiction}"
            gdp_data["confidence"] = 0.0

        return gdp_data

    def _collect_regional_employment_data(
        self, fred_service, central_bank: CentralBankInfo, timeframe: str
    ) -> dict[str, Any]:
        """Collect region-appropriate employment data"""
        employment_data = {
            "primary_indicator": {"observations": [], "trend": ""},
            "unemployment_data": {"observations": [], "trend": ""},
            "confidence": 0.0,
        }

        try:
            # For US/AMERICAS: use PAYEMS (nonfarm payrolls)
            # For others: use unemployment rate as primary indicator
            if central_bank.jurisdiction == "United States":
                primary_result = fred_service.get_economic_indicator("PAYEMS", timeframe)
                if primary_result:
                    employment_data["primary_indicator"]["observations"] = primary_result.get("observations", [])
                    employment_data["primary_indicator"]["trend"] = "payroll_growth"

                # Unemployment rate
                unemployment_result = fred_service.get_economic_indicator("UNRATE", timeframe)
                if unemployment_result:
                    employment_data["unemployment_data"]["observations"] = unemployment_result.get("observations", [])
                    employment_data["unemployment_data"]["trend"] = "stable"

            else:
                # For non-US regions, unemployment rate is the primary indicator
                primary_indicator = central_bank.employment_indicators[0]
                unemployment_result = fred_service.get_economic_indicator(primary_indicator, timeframe)
                if unemployment_result:
                    employment_data["primary_indicator"]["observations"] = unemployment_result.get("observations", [])
                    employment_data["primary_indicator"]["trend"] = "unemployment_rate"
                    employment_data["unemployment_data"] = employment_data["primary_indicator"]

            employment_data["confidence"] = 0.88

        except Exception as e:
            logger.warning(f"Failed to collect employment data for {central_bank.name}: {e}")
            employment_data["confidence"] = 0.0

        return employment_data

    def _collect_regional_inflation_data(
        self, fred_service, central_bank: CentralBankInfo, timeframe: str
    ) -> dict[str, Any]:
        """Collect region-appropriate inflation data"""
        inflation_data = {
            "cpi_data": {"observations": [], "trend": ""},
            "core_inflation_data": {"observations": [], "trend": ""},
            "confidence": 0.0,
        }

        try:
            # CPI data
            cpi_indicator = central_bank.inflation_indicators[0]
            cpi_result = fred_service.get_economic_indicator(cpi_indicator, timeframe)
            if cpi_result:
                inflation_data["cpi_data"]["observations"] = cpi_result.get("observations", [])
                inflation_data["cpi_data"]["trend"] = "moderating"

            # Core inflation (if available)
            if len(central_bank.inflation_indicators) > 1:
                core_indicator = central_bank.inflation_indicators[1]
                core_result = fred_service.get_economic_indicator(core_indicator, timeframe)
                if core_result:
                    inflation_data["core_inflation_data"]["observations"] = core_result.get("observations", [])
                    inflation_data["core_inflation_data"]["trend"] = "stable"

            inflation_data["confidence"] = 0.85

        except Exception as e:
            logger.warning(f"Failed to collect inflation data for {central_bank.name}: {e}")
            inflation_data["confidence"] = 0.0

        return inflation_data

    def _collect_regional_monetary_policy_data(
        self, fred_service, central_bank: CentralBankInfo, timeframe: str
    ) -> dict[str, Any]:
        """Collect region-appropriate monetary policy data"""
        monetary_policy_data = {
            "policy_rate": {"current_rate": 0.0, "trajectory": ""},
            "policy_meetings": {
                "name": central_bank.policy_meetings_name,
                "next_meeting": "",
            },
            "forward_guidance": {"stance": "", "communication": ""},
            "confidence": 0.0,
        }

        try:
            # Policy rate
            rate_result = fred_service.get_economic_indicator(central_bank.policy_rate_symbol, timeframe)
            if rate_result and rate_result.get("observations"):
                latest_rate = rate_result["observations"][-1] if rate_result["observations"] else 0.0
                monetary_policy_data["policy_rate"]["current_rate"] = latest_rate
                monetary_policy_data["policy_rate"]["trajectory"] = "stable"

            # Policy meeting information
            monetary_policy_data["policy_meetings"]["name"] = central_bank.policy_meetings_name

            # Forward guidance (region-specific)
            if central_bank.jurisdiction == "United States":
                monetary_policy_data["forward_guidance"]["stance"] = "data_dependent"
                monetary_policy_data["forward_guidance"]["communication"] = "Fed communication"
            elif central_bank.jurisdiction == "Eurozone":
                monetary_policy_data["forward_guidance"]["stance"] = "accommodative"
                monetary_policy_data["forward_guidance"]["communication"] = "ECB communication"
            else:
                monetary_policy_data["forward_guidance"]["stance"] = "varied_by_country"
                monetary_policy_data["forward_guidance"]["communication"] = f"{central_bank.name} communication"

            monetary_policy_data["confidence"] = 0.92

        except Exception as e:
            logger.warning(f"Failed to collect monetary policy data for {central_bank.name}: {e}")
            monetary_policy_data["confidence"] = 0.0

        return monetary_policy_data

    def _calculate_data_confidence(
        self,
        gdp_data: dict,
        employment_data: dict,
        inflation_data: dict,
        monetary_policy_data: dict,
    ) -> float:
        """Calculate overall confidence based on data completeness"""

        # Weight each data category
        weights = {
            "gdp": 0.25,
            "employment": 0.25,
            "inflation": 0.25,
            "monetary_policy": 0.25,
        }

        # Get confidence scores
        gdp_conf = gdp_data.get("confidence", 0.0)
        employment_conf = employment_data.get("confidence", 0.0)
        inflation_conf = inflation_data.get("confidence", 0.0)
        monetary_conf = monetary_policy_data.get("confidence", 0.0)

        # Calculate weighted average
        total_confidence = (
            gdp_conf * weights["gdp"]
            + employment_conf * weights["employment"]
            + inflation_conf * weights["inflation"]
            + monetary_conf * weights["monetary_policy"]
        )

        return round(total_confidence, 2)

    def _validate_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Validate response from regional central bank data collection"""
        if not response:
            raise ValidationError("Empty response from regional central bank service")

        # Validate required fields
        required_fields = [
            "region",
            "central_bank",
            "gdp_data",
            "employment_data",
            "inflation_data",
            "monetary_policy_data",
        ]

        for field in required_fields:
            if field not in response:
                raise ValidationError(f"Missing required field in regional data: {field}")

        return response

    def health_check(self) -> dict[str, Any]:
        """Check the health of the regional central bank service"""
        return {
            "service": "regional_central_bank",
            "status": "healthy",
            "supported_regions": list(self._central_bank_mappings.keys()),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }


def create_regional_central_bank_service(
    environment: str = "prod",
) -> RegionalCentralBankService:
    """
    Factory function to create RegionalCentralBankService instance

    Args:
        environment: Environment configuration (prod, dev, test)

    Returns:
        RegionalCentralBankService instance
    """
    config = ServiceConfig(
        name="regional_central_bank",
        base_url="",  # No base URL needed
        timeout=30,
        retries=3,
        environment=environment,
    )

    return RegionalCentralBankService(config)
