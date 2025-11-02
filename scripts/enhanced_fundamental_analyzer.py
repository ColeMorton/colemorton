#!/usr/bin/env python3
"""
Enhanced Fundamental Analyzer - MCP-Powered Analysis

Demonstrates integration of multiple MCP servers for comprehensive
fundamental analysis with economic context and automated content generation.
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

# Import the MCP integration utility
from mcp_integration import MCPDataAccess


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EnhancedFundamentalAnalyzer:
    """Enhanced fundamental analyzer using MCP servers"""

    def __init__(self, output_dir: str = "data/outputs/enhanced_analysis"):
        self.mcp = MCPDataAccess()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_ticker(self, ticker: str, include_economic_context: bool = True) -> dict:
        """Perform comprehensive fundamental analysis for a ticker"""

        logger.info(f"Starting enhanced analysis for {ticker}")

        analysis = {
            "ticker": ticker.upper(),
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_type": "enhanced_fundamental",
            "data_sources": [],
            "financial_data": {},
            "economic_context": {},
            "sec_filings": {},
            "valuation_metrics": {},
            "risk_assessment": {},
            "investment_thesis": {},
            "content_generation": {},
        }

        # 1. Yahoo Finance Financial Data
        try:
            logger.info(f"Retrieving Yahoo Finance data for {ticker}")

            # Get comprehensive financial data
            fundamentals = self.mcp.get_stock_fundamentals(ticker)
            market_data = self.mcp.get_market_data(ticker, "2y")
            financial_statements = self.mcp.get_financial_statements(ticker)

            analysis["financial_data"] = {
                "fundamentals": fundamentals,
                "market_data": market_data,
                "financial_statements": financial_statements,
                "data_quality": ("high" if all([fundamentals, market_data, financial_statements]) else "partial"),
            }
            analysis["data_sources"].append("yahoo_finance")

            # Extract key metrics for valuation
            if fundamentals and not fundamentals.get("error"):
                analysis["valuation_metrics"] = self._extract_valuation_metrics(fundamentals)

        except Exception as e:
            logger.error(f"Failed to get Yahoo Finance data: {e}")
            analysis["financial_data"]["error"] = str(e)

        # 2. SEC EDGAR Regulatory Data
        try:
            logger.info(f"Retrieving SEC EDGAR data for {ticker}")

            # Get SEC filings and metrics
            filings = self.mcp.get_company_filings(ticker, "10-K")
            sec_financial = self.mcp.get_edgar_financial_statements(ticker)
            sec_metrics = self.mcp.get_sec_metrics(ticker)

            analysis["sec_filings"] = {
                "recent_filings": filings,
                "financial_statements": sec_financial,
                "metrics": sec_metrics,
                "compliance_status": ("current" if filings and not filings.get("error") else "unknown"),
            }
            analysis["data_sources"].append("sec_edgar")

        except Exception as e:
            logger.error(f"Failed to get SEC EDGAR data: {e}")
            analysis["sec_filings"]["error"] = str(e)

        # 3. Economic Context (if requested)
        if include_economic_context:
            try:
                logger.info("Retrieving economic context data")

                # Get relevant economic indicators
                inflation = self.mcp.get_inflation_data("1y")
                interest_rates = self.mcp.get_interest_rates("all", "1y")

                # Get sector-specific indicators
                sector = self._determine_sector(analysis.get("financial_data", {}).get("fundamentals", {}))
                sector_indicators = self.mcp.get_sector_indicators(sector) if sector else {}

                analysis["economic_context"] = {
                    "inflation_data": inflation,
                    "interest_rates": interest_rates,
                    "sector_indicators": sector_indicators,
                    "sector": sector,
                    "economic_summary": self._summarize_economic_context(inflation, interest_rates),
                }
                analysis["data_sources"].append("fred_economic")

            except Exception as e:
                logger.error(f"Failed to get economic context: {e}")
                analysis["economic_context"]["error"] = str(e)

        # 4. Risk Assessment
        analysis["risk_assessment"] = self._perform_risk_assessment(analysis)

        # 5. Investment Thesis Generation
        analysis["investment_thesis"] = self._generate_investment_thesis(analysis)

        # 6. Content Generation
        try:
            content_data = self._prepare_content_data(analysis)
            blog_content = self.mcp.generate_blog_post("fundamental_analysis", content_data)
            social_content = self.mcp.create_social_content(
                ticker,
                "fundamental_analysis",
                analysis["investment_thesis"].get("key_points", ""),
            )

            analysis["content_generation"] = {
                "blog_post": blog_content,
                "social_content": social_content,
                "content_ready": not bool(blog_content.get("error") or social_content.get("error")),
            }
            analysis["data_sources"].append("content_automation")

        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            analysis["content_generation"]["error"] = str(e)

        # Final summary
        analysis["analysis_summary"] = {
            "data_sources_count": len(analysis["data_sources"]),
            "data_sources": analysis["data_sources"],
            "analysis_complete": len(analysis["data_sources"]) >= 2,
            "economic_context_included": include_economic_context,
            "content_generated": "content_automation" in analysis["data_sources"],
        }

        logger.info(f"Enhanced analysis complete for {ticker}: {len(analysis['data_sources'])} data sources")
        return analysis

    def _extract_valuation_metrics(self, fundamentals: dict) -> dict:
        """Extract key valuation metrics from fundamentals data"""

        metrics = {
            "pe_ratio": None,
            "price_to_book": None,
            "price_to_sales": None,
            "dividend_yield": None,
            "market_cap": None,
            "enterprise_value": None,
            "debt_to_equity": None,
            "return_on_equity": None,
        }

        try:
            # Extract from different possible data structures
            if isinstance(fundamentals, dict):
                data = fundamentals.get("data", fundamentals)

                # Map common Yahoo Finance fields
                field_mapping = {
                    "pe_ratio": ["trailingPE", "forwardPE", "pe_ratio"],
                    "price_to_book": ["priceToBook", "price_to_book"],
                    "price_to_sales": [
                        "priceToSalesTrailing12Months",
                        "price_to_sales",
                    ],
                    "dividend_yield": ["dividendYield", "dividend_yield"],
                    "market_cap": ["marketCap", "market_cap"],
                    "enterprise_value": ["enterpriseValue", "enterprise_value"],
                    "debt_to_equity": ["debtToEquity", "debt_to_equity"],
                    "return_on_equity": ["returnOnEquity", "return_on_equity"],
                }

                for metric, possible_fields in field_mapping.items():
                    for field in possible_fields:
                        if field in data and data[field] is not None:
                            metrics[metric] = data[field]
                            break

        except Exception as e:
            logger.warning(f"Failed to extract valuation metrics: {e}")

        return metrics

    def _determine_sector(self, fundamentals: dict) -> str:
        """Determine company sector from fundamentals data"""

        try:
            if isinstance(fundamentals, dict):
                data = fundamentals.get("data", fundamentals)

                # Look for sector information
                sector_fields = ["sector", "sectorKey", "industry"]
                for field in sector_fields:
                    if field in data and data[field]:
                        sector = str(data[field]).lower()

                        # Map to FRED-compatible sectors
                        sector_mapping = {
                            "technology": "technology",
                            "healthcare": "healthcare",
                            "financial": "financial",
                            "energy": "energy",
                            "retail": "retail",
                            "consumer": "retail",
                            "real estate": "housing",
                            "utilities": "energy",
                            "industrials": "technology",
                        }

                        for key, mapped_sector in sector_mapping.items():
                            if key in sector:
                                return mapped_sector

        except Exception as e:
            logger.warning(f"Failed to determine sector: {e}")

        return "technology"  # Default sector

    def _summarize_economic_context(self, inflation: dict, interest_rates: dict) -> dict:
        """Summarize economic context for analysis"""

        summary = {
            "inflation_trend": "unknown",
            "interest_rate_environment": "unknown",
            "economic_outlook": "neutral",
            "investment_implications": [],
        }

        try:
            # Analyze inflation
            if inflation and not inflation.get("error"):
                inflation_measures = inflation.get("inflation_measures", {})
                if "CPI" in inflation_measures:
                    cpi_data = inflation_measures["CPI"]
                    latest_value = cpi_data.get("latest_value", 0)

                    if latest_value < 2:
                        summary["inflation_trend"] = "low"
                        summary["investment_implications"].append("Low inflation supports growth stocks")
                    elif latest_value > 4:
                        summary["inflation_trend"] = "high"
                        summary["investment_implications"].append("High inflation pressures margins")
                    else:
                        summary["inflation_trend"] = "moderate"

            # Analyze interest rates
            if interest_rates and not interest_rates.get("error"):
                rates_data = interest_rates.get("interest_rates", {})
                if "Federal_Funds_Rate" in rates_data:
                    fed_rate = rates_data["Federal_Funds_Rate"].get("latest_value", 0)

                    if fed_rate < 2:
                        summary["interest_rate_environment"] = "low"
                        summary["investment_implications"].append("Low rates support equity valuations")
                    elif fed_rate > 5:
                        summary["interest_rate_environment"] = "high"
                        summary["investment_implications"].append("High rates pressure valuations")
                    else:
                        summary["interest_rate_environment"] = "moderate"

        except Exception as e:
            logger.warning(f"Failed to summarize economic context: {e}")

        return summary

    def _perform_risk_assessment(self, analysis: dict) -> dict:
        """Perform comprehensive risk assessment"""

        risks = {
            "financial_risks": [],
            "regulatory_risks": [],
            "economic_risks": [],
            "overall_risk_level": "medium",
        }

        try:
            # Financial risks
            valuation = analysis.get("valuation_metrics", {})
            if valuation.get("pe_ratio") and valuation["pe_ratio"] > 30:
                risks["financial_risks"].append("High P/E ratio indicates valuation risk")

            if valuation.get("debt_to_equity") and valuation["debt_to_equity"] > 1:
                risks["financial_risks"].append("High debt levels increase financial risk")

            # Regulatory risks
            sec_filings = analysis.get("sec_filings", {})
            if sec_filings.get("compliance_status") != "current":
                risks["regulatory_risks"].append("Potential SEC filing compliance issues")

            # Economic risks
            economic = analysis.get("economic_context", {})
            if economic.get("economic_summary", {}).get("inflation_trend") == "high":
                risks["economic_risks"].append("High inflation environment")

            if economic.get("economic_summary", {}).get("interest_rate_environment") == "high":
                risks["economic_risks"].append("Rising interest rate environment")

            # Overall risk level
            total_risks = len(risks["financial_risks"]) + len(risks["regulatory_risks"]) + len(risks["economic_risks"])
            if total_risks >= 4:
                risks["overall_risk_level"] = "high"
            elif total_risks >= 2:
                risks["overall_risk_level"] = "medium"
            else:
                risks["overall_risk_level"] = "low"

        except Exception as e:
            logger.warning(f"Risk assessment failed: {e}")

        return risks

    def _generate_investment_thesis(self, analysis: dict) -> dict:
        """Generate investment thesis based on analysis"""

        thesis = {
            "recommendation": "hold",
            "confidence_level": "medium",
            "key_points": "",
            "strengths": [],
            "weaknesses": [],
            "price_target": None,
            "time_horizon": "12_months",
        }

        try:
            # Analyze strengths
            valuation = analysis.get("valuation_metrics", {})

            if valuation.get("return_on_equity") and valuation["return_on_equity"] > 0.15:
                thesis["strengths"].append("Strong return on equity")

            if valuation.get("pe_ratio") and valuation["pe_ratio"] < 20:
                thesis["strengths"].append("Reasonable valuation")

            if valuation.get("debt_to_equity") and valuation["debt_to_equity"] < 0.5:
                thesis["strengths"].append("Conservative debt levels")

            # Analyze weaknesses
            risk_assessment = analysis.get("risk_assessment", {})

            if risk_assessment.get("overall_risk_level") == "high":
                thesis["weaknesses"].append("High overall risk profile")

            if len(risk_assessment.get("financial_risks", [])) > 2:
                thesis["weaknesses"].append("Multiple financial risk factors")

            # Generate recommendation
            strength_score = len(thesis["strengths"])
            weakness_score = len(thesis["weaknesses"])

            if strength_score > weakness_score + 1:
                thesis["recommendation"] = "buy"
                thesis["confidence_level"] = "high"
            elif weakness_score > strength_score + 1:
                thesis["recommendation"] = "sell"
                thesis["confidence_level"] = "medium"
            else:
                thesis["recommendation"] = "hold"
                thesis["confidence_level"] = "medium"

            # Create key points summary
            thesis["key_points"] = "\n".join(
                [
                    f"Recommendation: {thesis['recommendation'].upper()}",
                    f"Risk Level: {risk_assessment.get('overall_risk_level', 'medium')}",
                    f"Strengths: {len(thesis['strengths'])}",
                    f"Concerns: {len(thesis['weaknesses'])}",
                ]
            )

        except Exception as e:
            logger.warning(f"Investment thesis generation failed: {e}")

        return thesis

    def _prepare_content_data(self, analysis: dict) -> dict:
        """Prepare data for content generation"""

        ticker = analysis.get("ticker", "")

        content_data = {
            "ticker": ticker,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "data_source": "Enhanced MCP Analysis",
            "executive_summary": f"Comprehensive analysis of {ticker} using multiple data sources",
            "financial_metrics": self._format_financial_metrics(analysis),
            "valuation_analysis": self._format_valuation_analysis(analysis),
            "strengths_opportunities": "\n".join(analysis.get("investment_thesis", {}).get("strengths", [])),
            "risks_concerns": "\n".join(analysis.get("risk_assessment", {}).get("financial_risks", [])),
            "investment_recommendation": analysis.get("investment_thesis", {}).get("recommendation", "hold").upper(),
        }

        return content_data

    def _format_financial_metrics(self, analysis: dict) -> str:
        """Format financial metrics for content"""

        metrics = analysis.get("valuation_metrics", {})
        formatted = []

        if metrics.get("pe_ratio"):
            formatted.append(f"P/E Ratio: {metrics['pe_ratio']:.2f}")
        if metrics.get("market_cap"):
            formatted.append(f"Market Cap: ${metrics['market_cap']:,.0f}")
        if metrics.get("return_on_equity"):
            formatted.append(f"ROE: {metrics['return_on_equity']:.1%}")

        return "\n".join(formatted) if formatted else "Financial metrics not available"

    def _format_valuation_analysis(self, analysis: dict) -> str:
        """Format valuation analysis for content"""

        thesis = analysis.get("investment_thesis", {})

        return f"""
Recommendation: {thesis.get("recommendation", "hold").upper()}
Confidence: {thesis.get("confidence_level", "medium")}
Risk Level: {analysis.get("risk_assessment", {}).get("overall_risk_level", "medium")}
Time Horizon: {thesis.get("time_horizon", "12_months").replace("_", " ")}
"""

    def save_analysis(self, analysis: dict, ticker: str) -> str:
        """Save analysis to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker.upper()}_enhanced_analysis_{timestamp}.json"
        file_path = self.output_dir / filename

        with open(file_path, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"Enhanced analysis saved to {file_path}")
        return str(file_path)

    def generate_summary_report(self, analysis: dict) -> str:
        """Generate human-readable summary report"""

        ticker = analysis.get("ticker", "UNKNOWN")

        report = f"""
# Enhanced Fundamental Analysis Report: {ticker}

**Analysis Date:** {analysis.get("analysis_timestamp", "Unknown")}
**Data Sources:** {", ".join(analysis.get("data_sources", []))}

## Executive Summary
- **Recommendation:** {analysis.get("investment_thesis", {}).get("recommendation", "hold").upper()}
- **Risk Level:** {analysis.get("risk_assessment", {}).get("overall_risk_level", "medium").upper()}
- **Confidence:** {analysis.get("investment_thesis", {}).get("confidence_level", "medium").upper()}

## Financial Metrics
{self._format_financial_metrics(analysis)}

## Investment Thesis
**Strengths:**
{chr(10).join("- " + s for s in analysis.get("investment_thesis", {}).get("strengths", []))}

**Concerns:**
{chr(10).join("- " + w for w in analysis.get("risk_assessment", {}).get("financial_risks", []))}

## Economic Context
{analysis.get("economic_context", {}).get("economic_summary", {}).get("economic_outlook", "Neutral economic environment")}

## Data Quality
- **Sources Used:** {len(analysis.get("data_sources", []))}
- **Analysis Complete:** {"Yes" if analysis.get("analysis_summary", {}).get("analysis_complete") else "Partial"}
- **Content Generated:** {"Yes" if analysis.get("content_generation", {}).get("content_ready") else "No"}

---
*Generated by Enhanced Fundamental Analyzer using MCP integration*
"""

        return report


def main():
    """Main function for command-line usage"""

    parser = argparse.ArgumentParser(description="Enhanced Fundamental Analysis using MCP")
    parser.add_argument("ticker", help="Stock ticker symbol to analyze")
    parser.add_argument("--no-economic", action="store_true", help="Skip economic context analysis")
    parser.add_argument(
        "--output-dir",
        default="data/outputs/enhanced_analysis",
        help="Output directory",
    )
    parser.add_argument("--save-report", action="store_true", help="Save human-readable report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Create analyzer
        analyzer = EnhancedFundamentalAnalyzer(args.output_dir)

        # Perform analysis
        print("Starting enhanced fundamental analysis for {args.ticker}...")
        analysis = analyzer.analyze_ticker(args.ticker, include_economic_context=not args.no_economic)

        # Save analysis
        json_file = analyzer.save_analysis(analysis, args.ticker)
        print("Analysis saved to: {json_file}")

        # Generate and save report if requested
        if args.save_report:
            report = analyzer.generate_summary_report(analysis)
            report_file = (
                Path(args.output_dir)
                / f"{args.ticker.upper()}_summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )

            with open(report_file, "w") as f:
                f.write(report)

            print("Summary report saved to: {report_file}")

        # Print summary
        summary = analysis.get("analysis_summary", {})
        print("\nAnalysis Summary:")
        print("- Data Sources: {summary.get('data_sources_count', 0)}")
        print("- Analysis Complete: {summary.get('analysis_complete', False)}")
        print("- Content Generated: {summary.get('content_generated', False)}")

        # Print recommendation
        thesis = analysis.get("investment_thesis", {})
        print("\nInvestment Recommendation:")
        print("- Action: {thesis.get('recommendation', 'hold').upper()}")
        print("- Confidence: {thesis.get('confidence_level', 'medium').upper()}")
        print(f"- Risk Level: {analysis.get('risk_assessment', {}).get('overall_risk_level', 'medium').upper()}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print("Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
