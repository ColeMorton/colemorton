#!/usr/bin/env python3
"""
Yahoo Finance CLI

Command-line interface for Yahoo Finance data with:
- Stock quotes and fundamentals
- Historical price data
- Financial statements
- Market data summaries
- YAML configuration support
- Multiple output formats
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.yahoo_finance import create_yahoo_finance_service
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError


class YahooFinanceCLI(BaseFinancialCLI):
    """CLI for Yahoo Finance service"""

    def __init__(self):
        super().__init__(service_name="yahoo_finance", description="Yahoo Finance data service CLI")
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_yahoo_finance_service(env)
        return self.service

    def _add_service_commands(self) -> None:
        """Add Yahoo Finance specific commands"""

        @self.app.command("quote")
        def get_quote(
            ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., AAPL)"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
            no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching"),
        ):
            """Get stock quote and fundamental data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_stock_info(ticker)
                self._output_result(result, output_format, f"Stock Quote: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get quote for {ticker}")

        @self.app.command("history")
        def get_history(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            period: str = typer.Option(
                "comprehensive",
                help="Time period (comprehensive=daily only, 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
            ),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
            summary: bool = typer.Option(False, "--summary", help="Return summary instead of full data"),
        ):
            """Get historical price data - defaults to comprehensive collection (max daily only)"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                if summary:
                    result = service.get_market_data_summary(ticker, period if period != "comprehensive" else "max")
                    title = f"Market Summary: {ticker} ({period})"
                elif period == "comprehensive":
                    # Trigger comprehensive collection: daily (max) only - weekly disabled by default
                    print("🔄 Initiating comprehensive data collection for {ticker}")
                    print("   - Daily data: Maximum available history")
                    print("   - Weekly data: Disabled by default (use explicit weekly command if needed)")

                    # Fetch daily data (max) - this will trigger comprehensive collection
                    daily_result = service.get_historical_data(ticker, "max")

                    # Return daily-only results
                    result = {
                        "ticker": ticker,
                        "collection_type": "comprehensive",
                        "daily_data": daily_result,
                        "summary": {
                            "daily_records": len(daily_result.get("data", [])),
                            "weekly_records": 0,
                            "total_records": len(daily_result.get("data", [])),
                        },
                    }
                    title = f"Comprehensive Historical Data: {ticker} (max daily only)"
                else:
                    result = service.get_historical_data(ticker, period)
                    title = f"Historical Data: {ticker} ({period})"

                self._output_result(result, output_format, title)

            except Exception as e:
                self._handle_error(e, f"Failed to get historical data for {ticker}")

        @self.app.command("financials")
        def get_financials(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get financial statements"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_financial_statements(ticker)
                self._output_result(result, output_format, f"Financial Statements: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get financials for {ticker}")

        @self.app.command("analyze")
        def analyze_stock(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            period: str = typer.Option("1y", help="Analysis period"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Comprehensive stock analysis"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                # Get comprehensive data
                quote_data = service.get_stock_info(ticker)
                summary_data = service.get_market_data_summary(ticker, period)

                # Combine for comprehensive analysis
                analysis = {
                    "ticker": ticker,
                    "analysis_timestamp": quote_data.get("timestamp"),
                    "current_data": {
                        "company_name": quote_data.get("name"),
                        "current_price": quote_data.get("current_price"),
                        "market_cap": quote_data.get("market_cap"),
                        "pe_ratio": quote_data.get("pe_ratio"),
                        "sector": quote_data.get("sector"),
                        "industry": quote_data.get("industry"),
                    },
                    "performance_analysis": summary_data.get("performance_summary", {}),
                    "volume_analysis": summary_data.get("volume_summary", {}),
                    "data_quality": {
                        "quote_data_available": "current_price" in quote_data,
                        "historical_data_points": summary_data.get("data_points", 0),
                        "analysis_period": period,
                    },
                }

                self._output_result(analysis, output_format, f"Stock Analysis: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to analyze {ticker}")

        @self.app.command("collection-status")
        def collection_status(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Check historical data collection status for a ticker"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                # Get service info with historical data stats
                service_info = service.get_service_info()

                # Check if files exist for this ticker
                from pathlib import Path

                base_path = Path("data/raw/stocks") / ticker.upper()

                status = {
                    "ticker": ticker,
                    "collection_enabled": service_info.get("historical_storage", {}).get("enabled", False),
                    "files_exist": base_path.exists(),
                    "data_types": [],
                    "file_counts": {},
                    "date_ranges": {},
                }

                if base_path.exists():
                    for data_type_dir in base_path.iterdir():
                        if data_type_dir.is_dir():
                            data_type = data_type_dir.name
                            status["data_types"].append(data_type)

                            # Count files
                            files = list(data_type_dir.rglob("*.json"))
                            status["file_counts"][data_type] = len(files)

                            # Get date range
                            if files:
                                dates = []
                                for file_path in files:
                                    try:
                                        # Extract date from filename: TICKER_YYYY-MM-DD_datatype.json
                                        parts = file_path.stem.split("_")
                                        if len(parts) >= 2:
                                            date_part = parts[1]
                                            if "-" in date_part:
                                                dates.append(date_part)
                                    except (ValueError, IndexError):
                                        continue

                                if dates:
                                    dates.sort()
                                    status["date_ranges"][data_type] = {
                                        "earliest": dates[0],
                                        "latest": dates[-1],
                                        "total_dates": len(dates),
                                    }

                self._output_result(status, output_format, f"Collection Status: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get collection status for {ticker}")

        @self.app.command("batch")
        def batch_quotes(
            tickers: str = typer.Argument(..., help="Comma-separated ticker symbols"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
            fields: str = typer.Option(
                "symbol,current_price,market_cap,pe_ratio",
                help="Comma-separated fields to include",
            ),
        ):
            """Get quotes for multiple stocks"""
            try:
                ticker_list = [t.strip().upper() for t in tickers.split(",")]
                field_list = [f.strip() for f in fields.split(",")]
                service = self._get_service(env)

                results = []
                for ticker in ticker_list:
                    try:
                        ticker = self.validate_ticker(ticker)
                        quote_data = service.get_stock_info(ticker)

                        # Extract requested fields
                        row = {}
                        for field in field_list:
                            row[field] = quote_data.get(field, "N/A")
                        results.append(row)

                    except Exception as e:
                        # Add error row
                        row = dict.fromkeys(field_list, "ERROR")
                        row["symbol"] = ticker
                        row["error"] = str(e)
                        results.append(row)

                self._output_result(results, output_format, "Batch Stock Quotes")

            except Exception as e:
                self._handle_error(e, "Batch quote operation failed")

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Yahoo Finance service health check"""
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
    """Main entry point for Yahoo Finance CLI"""
    cli = YahooFinanceCLI()
    cli.run()


if __name__ == "__main__":
    main()
