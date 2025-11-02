#!/usr/bin/env python3
"""
Financial Modeling Prep CLI

Command-line interface for Financial Modeling Prep data with:
- 70,000+ stocks with 30 years historical data
- Real-time stock prices and financial statements
- Insider trading data and earnings transcripts
- Company profiles and financial ratios
- Economic calendar and market news
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.fmp import create_fmp_service
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError


class FMPCLI(BaseFinancialCLI):
    """CLI for Financial Modeling Prep service"""

    def __init__(self):
        super().__init__(
            service_name="fmp",
            description="Financial Modeling Prep advanced stock data service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_fmp_service(env)
        return self.service

    def _add_service_commands(self) -> None:
        """Add FMP specific commands"""

        @self.app.command("quote")
        def get_stock_quote(
            ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., AAPL)"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get real-time stock quote with comprehensive market data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_stock_quote(ticker)
                self._output_result(result, output_format, f"Stock Quote: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get quote for {ticker}")

        @self.app.command("profile")
        def get_company_profile(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive company profile and business information"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_company_profile(ticker)
                self._output_result(result, output_format, f"Company Profile: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get profile for {ticker}")

        @self.app.command("financials")
        def get_financial_statements(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            statement_type: str = typer.Option(
                "income-statement",
                help="Statement type (income-statement, balance-sheet-statement, cash-flow-statement)",
            ),
            period: str = typer.Option("annual", help="Period type (annual, quarter)"),
            limit: int = typer.Option(10, help="Number of periods to retrieve"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get detailed financial statements with historical data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_financial_statements(ticker, statement_type, period, limit)
                self._output_result(
                    result,
                    output_format,
                    f"Financial Statements: {ticker} ({statement_type})",
                )

            except Exception as e:
                self._handle_error(e, f"Failed to get financial statements for {ticker}")

        @self.app.command("metrics")
        def get_key_metrics(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            period: str = typer.Option("annual", help="Period type (annual, quarter)"),
            limit: int = typer.Option(10, help="Number of periods to retrieve"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get key financial metrics and performance indicators"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_key_metrics(ticker, period, limit)
                self._output_result(result, output_format, f"Key Metrics: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get key metrics for {ticker}")

        @self.app.command("ratios")
        def get_financial_ratios(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            period: str = typer.Option("annual", help="Period type (annual, quarter)"),
            limit: int = typer.Option(10, help="Number of periods to retrieve"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get financial ratios"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_financial_ratios(ticker, period, limit)
                self._output_result(result, output_format, f"Financial Ratios: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get financial ratios for {ticker}")

        @self.app.command("history")
        def get_historical_prices(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            from_date: str = typer.Option(None, help="Start date (YYYY-MM-DD)"),
            to_date: str = typer.Option(None, help="End date (YYYY-MM-DD)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get historical stock price data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_historical_prices(ticker, from_date, to_date)
                self._output_result(result, output_format, f"Historical Prices: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get historical prices for {ticker}")

        @self.app.command("insider")
        def get_insider_trading(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            limit: int = typer.Option(100, help="Maximum number of insider trades"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get insider trading data for a company"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_insider_trading(ticker, limit)
                self._output_result(result, output_format, f"Insider Trading: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get insider trading for {ticker}")

        @self.app.command("screen")
        def screen_stocks(
            market_cap_min: int = typer.Option(None, help="Minimum market cap"),
            market_cap_max: int = typer.Option(None, help="Maximum market cap"),
            beta_min: float = typer.Option(None, help="Minimum beta"),
            beta_max: float = typer.Option(None, help="Maximum beta"),
            volume_min: int = typer.Option(None, help="Minimum volume"),
            volume_max: int = typer.Option(None, help="Maximum volume"),
            dividend_min: float = typer.Option(None, help="Minimum dividend yield"),
            dividend_max: float = typer.Option(None, help="Maximum dividend yield"),
            limit: int = typer.Option(100, help="Maximum results"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Screen stocks based on financial criteria"""
            try:
                service = self._get_service(env)

                result = service.get_stock_screener(
                    market_cap_more_than=market_cap_min,
                    market_cap_lower_than=market_cap_max,
                    beta_more_than=beta_min,
                    beta_lower_than=beta_max,
                    volume_more_than=volume_min,
                    volume_lower_than=volume_max,
                    dividend_more_than=dividend_min,
                    dividend_lower_than=dividend_max,
                    limit=limit,
                )

                self._output_result(result, output_format, f"Stock Screener Results (limit: {limit})")

            except Exception as e:
                self._handle_error(e, "Failed to screen stocks")

        @self.app.command("movers")
        def get_market_movers(
            mover_type: str = typer.Option("gainers", help="Type of movers (gainers, losers, actives)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get market movers (gainers, losers, most active)"""
            try:
                service = self._get_service(env)

                if mover_type == "gainers":
                    result = service.get_market_gainers()
                elif mover_type == "losers":
                    result = service.get_market_losers()
                elif mover_type == "actives":
                    result = service.get_market_most_active()
                else:
                    raise ValidationError("mover_type must be 'gainers', 'losers', or 'actives'")

                self._output_result(result, output_format, f"Market Movers: {mover_type}")

            except Exception as e:
                self._handle_error(e, f"Failed to get market {mover_type}")

        @self.app.command("earnings")
        def get_earnings_calendar(
            from_date: str = typer.Option(None, help="Start date (YYYY-MM-DD)"),
            to_date: str = typer.Option(None, help="End date (YYYY-MM-DD)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get earnings calendar for upcoming earnings releases"""
            try:
                service = self._get_service(env)

                result = service.get_earnings_calendar(from_date, to_date)
                self._output_result(result, output_format, "Earnings Calendar")

            except Exception as e:
                self._handle_error(e, "Failed to get earnings calendar")

        @self.app.command("economic")
        def get_economic_calendar(
            from_date: str = typer.Option(None, help="Start date (YYYY-MM-DD)"),
            to_date: str = typer.Option(None, help="End date (YYYY-MM-DD)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get economic calendar"""
            try:
                service = self._get_service(env)

                result = service.get_economic_calendar(from_date, to_date)
                self._output_result(result, output_format, "Economic Calendar")

            except Exception as e:
                self._handle_error(e, "Failed to get economic calendar")

        @self.app.command("analyze")
        def comprehensive_analysis(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            include_financials: bool = typer.Option(True, help="Include financial statements"),
            include_insider: bool = typer.Option(True, help="Include insider trading"),
            periods: int = typer.Option(3, help="Number of periods for financials"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Comprehensive FMP analysis including profile, financials, and metrics"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                # Gather comprehensive data
                analysis = {
                    "ticker": ticker,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "profile": service.get_company_profile(ticker),
                    "quote": service.get_stock_quote(ticker),
                    "key_metrics": service.get_key_metrics(ticker, limit=periods),
                    "financial_ratios": service.get_financial_ratios(ticker, limit=periods),
                }

                # Add financial statements if requested
                if include_financials:
                    analysis["financials"] = {
                        "income_statement": service.get_financial_statements(ticker, "income-statement", limit=periods),
                        "balance_sheet": service.get_financial_statements(
                            ticker, "balance-sheet-statement", limit=periods
                        ),
                        "cash_flow": service.get_financial_statements(ticker, "cash-flow-statement", limit=periods),
                    }

                # Add insider trading if requested
                if include_insider:
                    try:
                        analysis["insider_trading"] = service.get_insider_trading(ticker, limit=20)
                    except Exception as e:
                        analysis["insider_trading"] = {"error": str(e)}

                self._output_result(analysis, output_format, f"Comprehensive Analysis: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to perform comprehensive analysis for {ticker}")

        @self.app.command("batch")
        def batch_quotes(
            tickers: str = typer.Argument(..., help="Comma-separated ticker symbols"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get quotes for multiple tickers"""
            try:
                service = self._get_service(env)
                ticker_list = [t.strip().upper() for t in tickers.split(",")]

                results = []
                for ticker in ticker_list:
                    try:
                        quote_data = service.get_stock_quote(ticker)
                        if quote_data and isinstance(quote_data, list) and len(quote_data) > 0:
                            quote = quote_data[0]
                            row = {
                                "ticker": ticker,
                                "price": quote.get("price", "N/A"),
                                "change": quote.get("change", "N/A"),
                                "changePercent": quote.get("changesPercentage", "N/A"),
                                "volume": quote.get("volume", "N/A"),
                                "marketCap": quote.get("marketCap", "N/A"),
                            }
                            results.append(row)

                    except Exception as e:
                        row = {
                            "ticker": ticker,
                            "price": "ERROR",
                            "change": "ERROR",
                            "changePercent": "ERROR",
                            "volume": "ERROR",
                            "marketCap": "ERROR",
                            "error": str(e),
                        }
                        results.append(row)

                self._output_result(results, output_format, f"Batch Quotes ({len(ticker_list)} tickers)")

            except Exception as e:
                self._handle_error(e, "Batch quotes operation failed")

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform FMP service health check"""
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
    """Main entry point for FMP CLI"""
    cli = FMPCLI()
    cli.run()


if __name__ == "__main__":
    main()
