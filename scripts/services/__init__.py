"""
Financial Services Package

Provides standardized financial data access services with:
- Consistent error handling and validation
- Production-grade caching and rate limiting
- Cross-source data validation
- Unified configuration management
"""

from .alpha_vantage import AlphaVantageService, create_alpha_vantage_service
from .base_financial_service import BaseFinancialService
from .coingecko import CoinGeckoService, create_coingecko_service
from .data_orchestrator import DataOrchestrator
from .fmp import FMPService, create_fmp_service
from .fred_economic import FREDEconomicService, create_fred_economic_service
from .imf import IMFService, create_imf_service
from .sec_edgar import SECEDGARService, create_sec_edgar_service
from .yahoo_finance import YahooFinanceAPIService, create_yahoo_finance_service


__all__ = [
    "BaseFinancialService",
    "DataOrchestrator",
    "YahooFinanceAPIService",
    "create_yahoo_finance_service",
    "AlphaVantageService",
    "create_alpha_vantage_service",
    "FREDEconomicService",
    "create_fred_economic_service",
    "SECEDGARService",
    "create_sec_edgar_service",
    "FMPService",
    "create_fmp_service",
    "CoinGeckoService",
    "create_coingecko_service",
    "IMFService",
    "create_imf_service",
]

# Service registry for dynamic discovery
SERVICE_REGISTRY = {}


def register_service(name: str, service_class):
    """Register a financial service"""
    SERVICE_REGISTRY[name] = service_class


def get_service(name: str):
    """Get a registered financial service"""
    return SERVICE_REGISTRY.get(name)


def list_services():
    """List all registered services"""
    return list(SERVICE_REGISTRY.keys())


# Auto-register available services
register_service("yahoo_finance", create_yahoo_finance_service)
register_service("alpha_vantage", create_alpha_vantage_service)
register_service("fred", create_fred_economic_service)
register_service("sec_edgar", create_sec_edgar_service)
register_service("fmp", create_fmp_service)
register_service("coingecko", create_coingecko_service)
register_service("imf", create_imf_service)
