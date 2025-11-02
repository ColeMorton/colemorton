#!/usr/bin/env python3
"""
SEC EDGAR CLI

Command-line interface for SEC EDGAR filing data with:
- Company filings access (10-K, 10-Q, 8-K, etc.)
- Financial statements data extraction
- SEC metrics for fundamental analysis
- Company search by ticker/CIK
- Comprehensive filing search capabilities
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.sec_edgar import create_sec_edgar_service
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError


class SECEDGARCLl(BaseFinancialCLI):
    """CLI for SEC EDGAR service"""

    def __init__(self):
        super().__init__(service_name="sec_edgar", description="SEC EDGAR filing data service CLI")
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_sec_edgar_service(env)
        return self.service

    def _add_service_commands(self) -> None:
        """Add SEC EDGAR specific commands"""

        @self.app.command("search")
        def search_company(
            ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., AAPL)"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Search for company by ticker symbol"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.search_company_by_ticker(ticker)
                if result:
                    self._output_result(result, output_format, f"Company Search: {ticker}")
                else:
                    self._output_result(
                        {
                            "error": f"Company not found for ticker {ticker}",
                            "ticker": ticker,
                        },
                        output_format,
                        f"Company Search: {ticker}",
                    )

            except Exception as e:
                self._handle_error(e, f"Failed to search for company {ticker}")

        @self.app.command("filings")
        def get_company_filings(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            filing_type: str = typer.Option("10-K", help="Filing type (10-K, 10-Q, 8-K, etc.)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company filings for a specific ticker and filing type"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_company_filings(ticker, filing_type)
                self._output_result(result, output_format, f"Company Filings: {ticker} ({filing_type})")

            except Exception as e:
                self._handle_error(e, f"Failed to get filings for {ticker}")

        @self.app.command("financials")
        def get_financial_statements(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            period: str = typer.Option("annual", help="Period type (annual, quarterly)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get financial statements data for a ticker"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_financial_statements(ticker, period)
                self._output_result(result, output_format, f"Financial Statements: {ticker} ({period})")

            except Exception as e:
                self._handle_error(e, f"Failed to get financial statements for {ticker}")

        @self.app.command("metrics")
        def get_sec_metrics(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            fiscal_year: str = typer.Option(None, help="Fiscal year (optional)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get key SEC metrics for fundamental analysis"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_sec_metrics(ticker, fiscal_year)
                self._output_result(result, output_format, f"SEC Metrics: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get SEC metrics for {ticker}")

        @self.app.command("facts")
        def get_company_facts(
            cik: str = typer.Argument(..., help="Company CIK (Central Index Key)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company facts for a specific CIK"""
            try:
                service = self._get_service(env)

                result = service.get_company_facts(cik)
                self._output_result(result, output_format, f"Company Facts: CIK {cik}")

            except Exception as e:
                self._handle_error(e, f"Failed to get company facts for CIK {cik}")

        @self.app.command("concept")
        def get_company_concept(
            cik: str = typer.Argument(..., help="Company CIK"),
            taxonomy: str = typer.Argument(..., help="Taxonomy (e.g., us-gaap)"),
            tag: str = typer.Argument(..., help="XBRL tag (e.g., Assets)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company concept data"""
            try:
                service = self._get_service(env)

                result = service.get_company_concept(cik, taxonomy, tag)
                self._output_result(
                    result,
                    output_format,
                    f"Company Concept: CIK {cik} {taxonomy}:{tag}",
                )

            except Exception as e:
                self._handle_error(e, f"Failed to get company concept for CIK {cik}")

        @self.app.command("submissions")
        def get_submissions(
            cik: str = typer.Argument(..., help="Company CIK"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company submissions"""
            try:
                service = self._get_service(env)

                result = service.get_submissions(cik)
                self._output_result(result, output_format, f"Company Submissions: CIK {cik}")

            except Exception as e:
                self._handle_error(e, f"Failed to get submissions for CIK {cik}")

        @self.app.command("tickers")
        def get_company_tickers(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company tickers and CIK mappings"""
            try:
                service = self._get_service(env)

                result = service.get_company_tickers()
                self._output_result(result, output_format, "Company Tickers")

            except Exception as e:
                self._handle_error(e, "Failed to get company tickers")

        @self.app.command("filing-search")
        def search_filings(
            query: str = typer.Argument(..., help="Search query"),
            date_range: str = typer.Option("last_year", help="Date range (last_year, ytd, custom)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Search SEC filings by query terms"""
            try:
                service = self._get_service(env)

                result = service.search_filings(query, date_range)
                self._output_result(result, output_format, f"Filing Search: {query}")

            except Exception as e:
                self._handle_error(e, f"Failed to search filings for '{query}'")

        @self.app.command("supported")
        def get_supported_filings(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get list of supported filing types and metrics"""
            try:
                service = self._get_service(env)

                result = service.get_supported_filings()
                self._output_result(result, output_format, "Supported Filings & Metrics")

            except Exception as e:
                self._handle_error(e, "Failed to get supported filings")

        @self.app.command("analyze")
        def comprehensive_analysis(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            include_filings: bool = typer.Option(True, help="Include recent filings"),
            filing_types: str = typer.Option("10-K,10-Q", help="Comma-separated filing types"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Comprehensive SEC EDGAR analysis"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                # Gather comprehensive data
                analysis = {
                    "ticker": ticker,
                    "analysis_timestamp": (
                        service.search_company_by_ticker(ticker).get("timestamp")
                        if service.search_company_by_ticker(ticker)
                        else None
                    ),
                    "company_info": service.search_company_by_ticker(ticker),
                    "financial_statements": service.get_financial_statements(ticker),
                    "sec_metrics": service.get_sec_metrics(ticker),
                }

                # Add filings if requested
                if include_filings:
                    analysis["filings"] = {}
                    for filing_type in filing_types.split(","):
                        filing_type = filing_type.strip()
                        try:
                            analysis["filings"][filing_type] = service.get_company_filings(ticker, filing_type)
                        except Exception as e:
                            analysis["filings"][filing_type] = {"error": str(e)}

                self._output_result(analysis, output_format, f"Comprehensive SEC Analysis: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to perform comprehensive analysis for {ticker}")

        @self.app.command("batch")
        def batch_metrics(
            tickers: str = typer.Argument(..., help="Comma-separated ticker symbols"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get SEC metrics for multiple tickers"""
            try:
                service = self._get_service(env)
                ticker_list = [t.strip().upper() for t in tickers.split(",")]

                results = []
                for ticker in ticker_list:
                    try:
                        metrics = service.get_sec_metrics(ticker)
                        profitability = metrics.get("metrics", {}).get("profitability", {})

                        row = {
                            "ticker": ticker,
                            "company": metrics.get("company", "Unknown"),
                            "net_margin": profitability.get("net_margin", "N/A"),
                            "roa": profitability.get("roa", "N/A"),
                            "status": "success",
                        }
                        results.append(row)

                    except Exception as e:
                        row = {
                            "ticker": ticker,
                            "company": "ERROR",
                            "net_margin": "ERROR",
                            "roa": "ERROR",
                            "status": "error",
                            "error": str(e),
                        }
                        results.append(row)

                self._output_result(
                    results,
                    output_format,
                    f"Batch SEC Metrics ({len(ticker_list)} tickers)",
                )

            except Exception as e:
                self._handle_error(e, "Batch metrics operation failed")

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform SEC EDGAR service health check"""
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
    """Main entry point for SEC EDGAR CLI"""
    cli = SECEDGARCLl()
    cli.run()


if __name__ == "__main__":
    main()
