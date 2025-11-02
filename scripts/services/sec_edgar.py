"""
SEC EDGAR Service

Production-grade SEC EDGAR filing data integration with:
- Company filings access (10-K, 10-Q, 8-K, etc.)
- Financial statements data extraction
- SEC metrics for fundamental analysis
- Company search by ticker/CIK
- Comprehensive filing search capabilities
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
    ValidationError,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config_loader import ConfigLoader


class SECEDGARService(BaseFinancialService):
    """
    SEC EDGAR service extending BaseFinancialService

    Provides access to SEC EDGAR filing data including:
    - Company filings (10-K, 10-Q, 8-K, etc.)
    - Financial statements extraction
    - SEC metrics for fundamental analysis
    - Company search by ticker symbol
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Override headers to include SEC required User-Agent
        self.config.headers.update({"User-Agent": "Colemorton Trading Analysis Platform (cole.morton@hotmail.com)"})

        # Common financial statement mappings
        self.financial_statement_mappings = {
            "income_statement": {
                "Revenues": [
                    "us-gaap:Revenues",
                    "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                ],
                "NetIncomeLoss": ["us-gaap:NetIncomeLoss", "us-gaap:ProfitLoss"],
                "EarningsPerShare": [
                    "us-gaap:EarningsPerShareBasic",
                    "us-gaap:EarningsPerShareDiluted",
                ],
                "OperatingIncome": ["us-gaap:OperatingIncomeLoss"],
                "GrossProfit": ["us-gaap:GrossProfit"],
            },
            "balance_sheet": {
                "Assets": ["us-gaap:Assets"],
                "AssetsCurrent": ["us-gaap:AssetsCurrent"],
                "Liabilities": ["us-gaap:Liabilities"],
                "LiabilitiesCurrent": ["us-gaap:LiabilitiesCurrent"],
                "StockholdersEquity": ["us-gaap:StockholdersEquity"],
            },
            "cash_flow": {
                "CashFlowFromOperations": ["us-gaap:NetCashProvidedByUsedInOperatingActivities"],
                "CashFlowFromInvesting": ["us-gaap:NetCashProvidedByUsedInInvestingActivities"],
                "CashFlowFromFinancing": ["us-gaap:NetCashProvidedByUsedInFinancingActivities"],
            },
        }

    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """Validate SEC EDGAR response data"""

        if not isinstance(data, dict):
            raise ValidationError(f"Invalid response format for {endpoint}")

        # Check for API errors
        if "error" in data:
            raise DataNotFoundError(data["error"])

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        return data

    def get_company_tickers(self) -> dict[str, Any]:
        """
        Get company tickers and CIK mappings

        Returns:
            Dictionary containing company ticker to CIK mappings
        """
        result = self._make_request_with_retry("/files/company_tickers.json")

        # Add metadata
        result.update({"data_source": "SEC EDGAR", "timestamp": datetime.now().isoformat()})

        return result

    def get_company_facts(self, cik: str) -> dict[str, Any]:
        """
        Get company facts for a specific CIK

        Args:
            cik: Company Central Index Key

        Returns:
            Dictionary containing company facts data
        """
        if not cik:
            raise ValidationError("CIK is required")

        # Pad CIK with leading zeros to 10 digits
        cik_padded = cik.zfill(10)
        result = self._make_request_with_retry(f"/api/xbrl/companyfacts/CIK{cik_padded}.json")

        # Add metadata
        result.update(
            {
                "cik": cik,
                "cik_padded": cik_padded,
                "data_source": "SEC EDGAR",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_company_concept(self, cik: str, taxonomy: str, tag: str) -> dict[str, Any]:
        """
        Get company concept data

        Args:
            cik: Company Central Index Key
            taxonomy: Taxonomy (e.g., 'us-gaap')
            tag: XBRL tag (e.g., 'Assets')

        Returns:
            Dictionary containing company concept data
        """
        if not all([cik, taxonomy, tag]):
            raise ValidationError("CIK, taxonomy, and tag are required")

        cik_padded = cik.zfill(10)
        result = self._make_request_with_retry(f"/api/xbrl/companyconcept/CIK{cik_padded}/{taxonomy}/{tag}.json")

        # Add metadata
        result.update(
            {
                "cik": cik,
                "taxonomy": taxonomy,
                "tag": tag,
                "data_source": "SEC EDGAR",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def get_submissions(self, cik: str) -> dict[str, Any]:
        """
        Get company submissions

        Args:
            cik: Company Central Index Key

        Returns:
            Dictionary containing company submission data
        """
        if not cik:
            raise ValidationError("CIK is required")

        cik_padded = cik.zfill(10)
        result = self._make_request_with_retry(f"/submissions/CIK{cik_padded}.json")

        # Add metadata
        result.update(
            {
                "cik": cik,
                "cik_padded": cik_padded,
                "data_source": "SEC EDGAR",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result

    def search_company_by_ticker(self, ticker: str) -> dict[str, Any] | None:
        """
        Search for company by ticker symbol

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary containing company information or None if not found
        """
        if not ticker:
            raise ValidationError("Ticker is required")

        ticker = ticker.upper().strip()

        # Get company tickers mapping
        tickers_data = self.get_company_tickers()

        # Search for ticker in the data
        for cik, company_data in tickers_data.items():
            if isinstance(company_data, dict) and company_data.get("ticker") == ticker:
                return {
                    "cik": cik,
                    "title": company_data.get("title"),
                    "ticker": ticker,
                    "data_source": "SEC EDGAR",
                    "timestamp": datetime.now().isoformat(),
                }

        return None

    def get_company_filings(self, ticker: str, filing_type: str = "10-K") -> dict[str, Any]:
        """
        Get company filings for a specific ticker and filing type

        Args:
            ticker: Stock ticker symbol
            filing_type: Type of filing (10-K, 10-Q, 8-K, etc.)

        Returns:
            Dictionary containing company filings data
        """
        # Find company by ticker
        company = self.search_company_by_ticker(ticker)
        if not company:
            raise DataNotFoundError(f"Company not found for ticker {ticker.upper()}")

        # Get submissions
        submissions = self.get_submissions(company["cik"])

        # Filter filings by type
        filings = []
        recent_filings = submissions.get("filings", {}).get("recent", {})

        if "form" in recent_filings:
            for i, form in enumerate(recent_filings["form"]):
                if form == filing_type:
                    filing_data = {
                        "form": form,
                        "filing_date": recent_filings["filingDate"][i],
                        "accession_number": recent_filings["accessionNumber"][i],
                        "primary_document": recent_filings["primaryDocument"][i],
                        "report_date": recent_filings.get("reportDate", [None] * len(recent_filings["form"]))[i],
                    }
                    filings.append(filing_data)

        return {
            "ticker": ticker.upper(),
            "company": company["title"],
            "cik": company["cik"],
            "filing_type": filing_type,
            "filings_count": len(filings),
            "recent_filings": filings[:10],  # Return 10 most recent
            "data_source": "SEC EDGAR",
            "timestamp": datetime.now().isoformat(),
        }

    def get_financial_statements(self, ticker: str, period: str = "annual") -> dict[str, Any]:
        """
        Get financial statements data for a ticker

        Args:
            ticker: Stock ticker symbol
            period: Period type (annual, quarterly)

        Returns:
            Dictionary containing financial statements data
        """
        # Find company by ticker
        company = self.search_company_by_ticker(ticker)
        if not company:
            raise DataNotFoundError(f"Company not found for ticker {ticker.upper()}")

        # Get company facts
        facts = self.get_company_facts(company["cik"])

        # Extract key financial metrics
        financial_data = {"income_statement": {}, "balance_sheet": {}, "cash_flow": {}}

        # Extract data for each category
        for category, metrics in self.financial_statement_mappings.items():
            for metric_name, possible_tags in metrics.items():
                for tag in possible_tags:
                    if tag in facts.get("facts", {}).get("us-gaap", {}):
                        metric_data = facts["facts"]["us-gaap"][tag]
                        units = metric_data.get("units", {})

                        # Get USD data
                        if "USD" in units:
                            recent_values = []
                            for entry in units["USD"]:
                                if entry.get("form") in ["10-K", "10-Q"]:
                                    recent_values.append(
                                        {
                                            "value": entry.get("val"),
                                            "date": entry.get("end"),
                                            "form": entry.get("form"),
                                            "fiscal_year": entry.get("fy"),
                                            "fiscal_period": entry.get("fp"),
                                        }
                                    )

                            if recent_values:
                                financial_data[category][metric_name] = recent_values[:5]  # Recent 5 values
                        break

        return {
            "ticker": ticker.upper(),
            "company": company["title"],
            "cik": company["cik"],
            "period": period,
            "financial_statements": financial_data,
            "data_source": "SEC EDGAR",
            "timestamp": datetime.now().isoformat(),
        }

    def get_sec_metrics(self, ticker: str, fiscal_year: str = None) -> dict[str, Any]:
        """
        Get key SEC metrics for fundamental analysis

        Args:
            ticker: Stock ticker symbol
            fiscal_year: Fiscal year (optional)

        Returns:
            Dictionary containing SEC metrics
        """
        # Find company by ticker
        company = self.search_company_by_ticker(ticker)
        if not company:
            raise DataNotFoundError(f"Company not found for ticker {ticker.upper()}")

        # Get company facts
        facts = self.get_company_facts(company["cik"])

        # Extract key ratios and metrics
        metrics = {
            "profitability": {},
            "liquidity": {},
            "leverage": {},
            "efficiency": {},
        }

        # Get recent financial data
        us_gaap_facts = facts.get("facts", {}).get("us-gaap", {})

        # Revenue
        revenue_data = None
        for revenue_tag in [
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
        ]:
            if revenue_tag in us_gaap_facts:
                revenue_units = us_gaap_facts[revenue_tag].get("units", {}).get("USD", [])
                if revenue_units:
                    revenue_data = sorted(revenue_units, key=lambda x: x.get("end", ""), reverse=True)[:4]
                    break

        # Net Income
        net_income_data = None
        for ni_tag in ["NetIncomeLoss", "ProfitLoss"]:
            if ni_tag in us_gaap_facts:
                ni_units = us_gaap_facts[ni_tag].get("units", {}).get("USD", [])
                if ni_units:
                    net_income_data = sorted(ni_units, key=lambda x: x.get("end", ""), reverse=True)[:4]
                    break

        # Assets
        assets_data = None
        if "Assets" in us_gaap_facts:
            assets_units = us_gaap_facts["Assets"].get("units", {}).get("USD", [])
            if assets_units:
                assets_data = sorted(assets_units, key=lambda x: x.get("end", ""), reverse=True)[:4]

        # Calculate basic metrics
        if revenue_data and net_income_data:
            try:
                latest_revenue = revenue_data[0]["val"]
                latest_net_income = net_income_data[0]["val"]

                if latest_revenue and latest_revenue > 0:
                    metrics["profitability"]["net_margin"] = (latest_net_income / latest_revenue) * 100

                if assets_data:
                    latest_assets = assets_data[0]["val"]
                    if latest_assets and latest_assets > 0:
                        metrics["profitability"]["roa"] = (latest_net_income / latest_assets) * 100

            except (TypeError, ZeroDivisionError):
                pass

        return {
            "ticker": ticker.upper(),
            "company": company["title"],
            "cik": company["cik"],
            "fiscal_year": fiscal_year,
            "metrics": metrics,
            "raw_data": {
                "revenue": revenue_data[:2] if revenue_data else None,
                "net_income": net_income_data[:2] if net_income_data else None,
                "assets": assets_data[:2] if assets_data else None,
            },
            "data_source": "SEC EDGAR",
            "timestamp": datetime.now().isoformat(),
        }

    def search_filings(self, query: str, date_range: str = "last_year") -> dict[str, Any]:
        """
        Search SEC filings by query terms

        Args:
            query: Search query
            date_range: Date range for search

        Returns:
            Dictionary containing search guidance and results
        """
        search_guidance = {
            "query": query,
            "date_range": date_range,
            "search_url": f"https://www.sec.gov/edgar/search/#/q={query.replace(' ', '%20')}",
            "supported_searches": [
                "Company name or ticker",
                "CIK (Central Index Key)",
                "Filing type (10-K, 10-Q, 8-K, etc.)",
                "Business description keywords",
            ],
            "date_ranges": {
                "last_year": "Previous 12 months",
                "ytd": "Year to date",
                "custom": "Specify start and end dates",
            },
        }

        return {
            "search_query": query,
            "date_range": date_range,
            "guidance": search_guidance,
            "note": "Use the SEC EDGAR search URL for advanced search capabilities",
            "data_source": "SEC EDGAR",
            "timestamp": datetime.now().isoformat(),
        }

    def get_supported_filings(self) -> dict[str, Any]:
        """Get list of supported filing types"""
        return {
            "supported_filings": [
                {"type": "10-K", "description": "Annual report"},
                {"type": "10-Q", "description": "Quarterly report"},
                {"type": "8-K", "description": "Current report"},
                {"type": "DEF 14A", "description": "Proxy statement"},
                {"type": "S-1", "description": "Registration statement"},
                {"type": "S-3", "description": "Registration statement"},
                {"type": "S-4", "description": "Registration statement"},
                {"type": "424B", "description": "Prospectus"},
            ],
            "supported_metrics": [
                "Revenue",
                "Net Income",
                "Assets",
                "Liabilities",
                "Equity",
                "Cash Flow",
                "Earnings Per Share",
                "Operating Income",
            ],
            "data_source": "SEC EDGAR",
            "timestamp": datetime.now().isoformat(),
        }

    def health_check(self) -> dict[str, Any]:
        """Service health check"""
        try:
            # Test API connectivity with company tickers endpoint
            result = self.get_company_tickers()

            return {
                "service_name": self.config.name,
                "status": "healthy",
                "api_connection": "ok",
                "test_endpoint": "/files/company_tickers.json",
                "test_result": "success" if result else "failed",
                "configuration": {
                    "cache_enabled": self.config.cache.enabled,
                    "rate_limit_enabled": self.config.rate_limit.enabled,
                    "requests_per_minute": self.config.rate_limit.requests_per_minute,
                    "cache_ttl_seconds": self.config.cache.ttl_seconds,
                },
                "capabilities": [
                    "Company filings access (10-K, 10-Q, 8-K)",
                    "Financial statements extraction",
                    "SEC metrics for fundamental analysis",
                    "Company search by ticker/CIK",
                    "Filing search capabilities",
                ],
                "supported_filing_types": len(self.get_supported_filings()["supported_filings"]),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "service_name": self.config.name,
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
            }


def create_sec_edgar_service(env: str = "dev") -> SECEDGARService:
    """
    Factory function to create SEC EDGAR service with configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured SEC EDGAR service instance
    """
    # Ensure environment variables are loaded first
    try:
        # Add scripts directory to path for load_env import
        import sys

        scripts_dir = Path(__file__).parent.parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from load_env import ensure_env_loaded

        ensure_env_loaded()
    except ImportError:
        pass  # Continue if load_env not available

    # Use absolute path to config directory
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_loader = ConfigLoader(str(config_dir), auto_load_env=True)
    service_config = config_loader.get_service_config("sec_edgar", env)

    # Convert to ServiceConfig format
    from .base_financial_service import CacheConfig, RateLimitConfig, ServiceConfig

    config = ServiceConfig(
        name=service_config.name,
        base_url=service_config.base_url,
        api_key=service_config.api_key,
        timeout_seconds=service_config.timeout_seconds,
        max_retries=service_config.max_retries,
        cache=CacheConfig(**service_config.cache),
        rate_limit=RateLimitConfig(**service_config.rate_limit),
        headers=service_config.headers,
    )

    return SECEDGARService(config)
