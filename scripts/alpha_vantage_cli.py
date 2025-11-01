#!/usr/bin/env python3
"""
Alpha Vantage CLI

Command-line interface for Alpha Vantage data with:
- Real-time stock quotes with comprehensive market data
- 60+ technical indicators
- AI-powered news sentiment analysis
- Global market coverage (stocks, forex, cryptocurrencies)
- Economic indicators and market news
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.alpha_vantage import create_alpha_vantage_service  # noqa: E402
from utils.cli_base import BaseFinancialCLI, OutputFormat, ValidationError  # noqa: E402


class AlphaVantageCLI(BaseFinancialCLI):
    """CLI for Alpha Vantage service"""

    def __init__(self):
        super().__init__(
            service_name="alpha_vantage",
            description="Alpha Vantage enhanced stock data service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_alpha_vantage_service(env)
        return self.service

    def _add_service_commands(self) -> None:
        """Add Alpha Vantage specific commands"""

        @self.app.command("quote")
        def get_quote(
            ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., AAPL)"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get real-time stock quote with comprehensive market data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_stock_quote(ticker)
                self._output_result(result, output_format, f"Alpha Vantage Quote: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get quote for {ticker}")

        @self.app.command("daily")
        def get_daily_data(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            outputsize: str = typer.Option("compact", help="Output size (compact/full)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get daily stock price data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_daily_data(ticker, outputsize)
                self._output_result(result, output_format, f"Daily Data: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get daily data for {ticker}")

        @self.app.command("intraday")
        def get_intraday_data(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            interval: str = typer.Option("5min", help="Time interval (1min, 5min, 15min, 30min, 60min)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get intraday stock data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_intraday_data(ticker, interval)
                self._output_result(result, output_format, f"Intraday Data: {ticker} ({interval})")

            except Exception as e:
                self._handle_error(e, f"Failed to get intraday data for {ticker}")

        @self.app.command("technical")
        def get_technical_indicator(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            function: str = typer.Argument(..., help="Technical indicator (SMA, RSI, MACD, BBANDS, etc.)"),
            interval: str = typer.Option("daily", help="Time interval"),
            time_period: int = typer.Option(20, help="Number of periods for calculation"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get technical indicator data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_technical_indicator(ticker, function, interval, time_period)
                self._output_result(result, output_format, f"Technical Indicator: {ticker} {function}")

            except Exception as e:
                self._handle_error(e, f"Failed to get technical indicator {function} for {ticker}")

        @self.app.command("overview")
        def get_company_overview(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company overview and fundamental data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_company_overview(ticker)
                self._output_result(result, output_format, f"Company Overview: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get company overview for {ticker}")

        @self.app.command("financials")
        def get_financial_statements(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            statement_type: str = typer.Option("income", help="Statement type (income, balance, cash_flow)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company financial statements"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_financial_statements(ticker, statement_type)
                self._output_result(
                    result,
                    output_format,
                    f"Financial Statements: {ticker} ({statement_type})",
                )

            except Exception as e:
                self._handle_error(e, f"Failed to get {statement_type} statements for {ticker}")

        @self.app.command("earnings")
        def get_earnings(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get company earnings data"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                result = service.get_earnings(ticker)
                self._output_result(result, output_format, f"Earnings Data: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to get earnings for {ticker}")

        @self.app.command("news")
        def get_news_sentiment(
            tickers: str = typer.Option(None, help="Comma-separated ticker symbols"),
            topics: str = typer.Option(None, help="Comma-separated topics"),
            limit: int = typer.Option(50, help="Maximum number of articles"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get AI-powered news sentiment analysis"""
            try:
                service = self._get_service(env)

                result = service.get_news_sentiment(tickers, topics, limit)
                self._output_result(result, output_format, "News Sentiment Analysis")

            except Exception as e:
                self._handle_error(e, "Failed to get news sentiment")

        @self.app.command("economic")
        def get_economic_indicator(
            function: str = typer.Argument(..., help="Economic indicator (GDP, INFLATION, UNEMPLOYMENT)"),
            interval: str = typer.Option("monthly", help="Data interval (monthly, quarterly, annual)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get economic indicator data"""
            try:
                service = self._get_service(env)

                result = service.get_economic_indicator(function, interval)
                self._output_result(result, output_format, f"Economic Indicator: {function}")

            except Exception as e:
                self._handle_error(e, f"Failed to get economic indicator {function}")

        @self.app.command("forex")
        def get_forex_rate(
            from_currency: str = typer.Argument(..., help="Source currency (e.g., USD)"),
            to_currency: str = typer.Argument(..., help="Target currency (e.g., EUR)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get foreign exchange rate"""
            try:
                service = self._get_service(env)

                result = service.get_forex_rate(from_currency, to_currency)
                self._output_result(result, output_format, f"Forex Rate: {from_currency}/{to_currency}")

            except Exception as e:
                self._handle_error(e, f"Failed to get forex rate {from_currency}/{to_currency}")

        @self.app.command("crypto")
        def get_crypto_daily(
            symbol: str = typer.Argument(..., help="Cryptocurrency symbol (e.g., BTC, ETH)"),
            market: str = typer.Option("USD", help="Market currency"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get daily cryptocurrency data"""
            try:
                service = self._get_service(env)

                result = service.get_crypto_daily(symbol, market)
                self._output_result(result, output_format, f"Crypto Daily: {symbol}/{market}")

            except Exception as e:
                self._handle_error(e, f"Failed to get crypto data for {symbol}")

        @self.app.command("analyze")
        def comprehensive_analysis(
            ticker: str = typer.Argument(..., help="Stock ticker symbol"),
            include_sentiment: bool = typer.Option(True, help="Include sentiment analysis"),
            technical_indicators: str = typer.Option("SMA,RSI", help="Comma-separated technical indicators"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Comprehensive Alpha Vantage analysis"""
            try:
                ticker = self.validate_ticker(ticker)
                service = self._get_service(env)

                # Gather comprehensive data
                analysis = {
                    "ticker": ticker,
                    "analysis_timestamp": service.get_stock_quote(ticker).get("timestamp"),
                    "quote_data": service.get_stock_quote(ticker),
                    "company_overview": service.get_company_overview(ticker),
                }

                # Add sentiment analysis if requested
                if include_sentiment:
                    try:
                        analysis["sentiment_analysis"] = service.get_news_sentiment(ticker)
                    except Exception as e:
                        analysis["sentiment_analysis"] = {"error": str(e)}

                # Add technical indicators
                if technical_indicators:
                    analysis["technical_indicators"] = {}
                    for indicator in technical_indicators.split(","):
                        indicator = indicator.strip().upper()
                        try:
                            analysis["technical_indicators"][indicator] = service.get_technical_indicator(
                                ticker, indicator
                            )
                        except Exception as e:
                            analysis["technical_indicators"][indicator] = {"error": str(e)}

                self._output_result(analysis, output_format, f"Comprehensive Analysis: {ticker}")

            except Exception as e:
                self._handle_error(e, f"Failed to perform comprehensive analysis for {ticker}")

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Alpha Vantage service health check"""
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
    """Main entry point for Alpha Vantage CLI"""
    cli = AlphaVantageCLI()
    cli.run()


if __name__ == "__main__":
    main()
