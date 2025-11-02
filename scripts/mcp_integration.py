#!/usr/bin/env python3
"""
MCP Integration Utility - Unified Data Access Layer

Provides standardized access to MCP servers for existing Python scripts,
enabling unified data access patterns and reducing API dependencies.
"""

import hashlib
import json
import logging
import pickle
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPIntegrationError(Exception):
    """Base exception for MCP integration errors"""


class ServerNotFoundError(MCPIntegrationError):
    """Raised when MCP server is not available"""


class DataAccessError(MCPIntegrationError):
    """Raised when data access fails"""


class CacheManager:
    """Advanced multi-level cache manager for MCP data access"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session_cache = {}  # Level 1: In-memory session cache
        self.file_cache_dir = self.cache_dir / "file_cache"  # Level 2: File cache
        self.file_cache_dir.mkdir(exist_ok=True)

        # Cache TTL settings (in seconds)
        self.session_ttl = 300  # 5 minutes
        self.file_ttl = 900  # 15 minutes
        self.market_hours_ttl = 1800  # 30 minutes during market hours

        # Performance tracking
        self.cache_stats = {
            "session_hits": 0,
            "file_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
        }

    def _is_market_hours(self) -> bool:
        """Check if current time is during market hours (9:30 AM - 4:00 PM ET)"""
        now = datetime.now()
        # Simplified market hours check - in production would account for holidays/weekends
        return 9 <= now.hour <= 16 and now.weekday() < 5

    def _get_cache_key(self, server_name: str, tool_name: str, **kwargs) -> str:
        """Generate a unique cache key for the request"""
        key_data = f"{server_name}_{tool_name}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()

    def _get_file_cache_path(self, cache_key: str) -> Path:
        """Get file cache path for the given key"""
        return self.file_cache_dir / f"{cache_key}.pkl"

    def _is_cache_valid(self, cache_time: datetime, is_market_data: bool = False) -> bool:
        """Check if cache entry is still valid based on TTL"""
        now = datetime.now()
        age = (now - cache_time).total_seconds()

        if is_market_data and self._is_market_hours():
            return age < self.market_hours_ttl
        return age < self.file_ttl

    def get(self, server_name: str, tool_name: str, **kwargs) -> dict[str, Any] | None:
        """Get data from cache with intelligent fallback"""
        self.cache_stats["total_requests"] += 1
        cache_key = self._get_cache_key(server_name, tool_name, **kwargs)
        is_market_data = "stock" in tool_name.lower() or "market" in tool_name.lower()

        # Level 1: Check session cache
        if cache_key in self.session_cache:
            cached_result, cache_time = self.session_cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.session_ttl:
                self.cache_stats["session_hits"] += 1
                logger.debug(f"Session cache hit for {server_name}.{tool_name}")
                return cached_result
            # Expired session cache entry
            del self.session_cache[cache_key]

        # Level 2: Check file cache
        file_cache_path = self._get_file_cache_path(cache_key)
        if file_cache_path.exists():
            try:
                with open(file_cache_path, "rb") as f:
                    cached_data = pickle.load(f)
                    cached_result, cache_time = (
                        cached_data["result"],
                        cached_data["timestamp"],
                    )

                if self._is_cache_valid(cache_time, is_market_data):
                    # Promote to session cache
                    self.session_cache[cache_key] = (cached_result, cache_time)
                    self.cache_stats["file_hits"] += 1
                    logger.debug(f"File cache hit for {server_name}.{tool_name}")
                    return cached_result
                # Expired file cache entry
                file_cache_path.unlink()

            except Exception as e:
                logger.warning(f"Failed to load file cache: {e}")
                if file_cache_path.exists():
                    file_cache_path.unlink()

        # Cache miss
        self.cache_stats["cache_misses"] += 1
        return None

    def set(self, server_name: str, tool_name: str, result: dict[str, Any], **kwargs):
        """Store data in all cache levels"""
        cache_key = self._get_cache_key(server_name, tool_name, **kwargs)
        timestamp = datetime.now()

        # Store in session cache
        self.session_cache[cache_key] = (result, timestamp)

        # Store in file cache
        try:
            file_cache_path = self._get_file_cache_path(cache_key)
            cache_data = {
                "result": result,
                "timestamp": timestamp,
                "server_name": server_name,
                "tool_name": tool_name,
                "kwargs": kwargs,
            }

            with open(file_cache_path, "wb") as f:
                pickle.dump(cache_data, f)

            logger.debug(f"Stored in cache: {server_name}.{tool_name}")

        except Exception as e:
            logger.warning(f"Failed to store file cache: {e}")

    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching a pattern"""
        # Invalidate session cache
        keys_to_remove = [k for k in self.session_cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self.session_cache[key]

        # Invalidate file cache
        for cache_file in self.file_cache_dir.glob(f"*{pattern}*.pkl"):
            cache_file.unlink()

        logger.info(f"Invalidated cache entries matching pattern: {pattern}")

    def cleanup_expired(self):
        """Clean up expired cache entries"""
        now = datetime.now()

        # Clean session cache
        expired_keys = []
        for key, (result, cache_time) in self.session_cache.items():
            if (now - cache_time).total_seconds() > self.session_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.session_cache[key]

        # Clean file cache
        for cache_file in self.file_cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, "rb") as f:
                    cached_data = pickle.load(f)
                    cache_time = cached_data["timestamp"]

                if (now - cache_time).total_seconds() > self.file_ttl:
                    cache_file.unlink()

            except Exception as e:
                logger.warning(f"Error processing cache file {cache_file}: {e}")
                cache_file.unlink()

        logger.info("Cache cleanup completed")

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.cache_stats["total_requests"]
        total_hits = self.cache_stats["session_hits"] + self.cache_stats["file_hits"]

        return {
            "cache_stats": self.cache_stats,
            "hit_ratio": ((total_hits / total_requests * 100) if total_requests > 0 else 0),
            "session_cache_size": len(self.session_cache),
            "file_cache_size": len(list(self.file_cache_dir.glob("*.pkl"))),
            "cache_directory": str(self.cache_dir),
        }


class MCPDataAccess:
    """Unified data access layer for MCP servers with advanced caching"""

    def __init__(self, config_path: str = "mcp-servers.json", enable_caching: bool = True):
        self.config_path = Path(config_path)
        self.servers = self._load_server_config()
        self.enable_caching = enable_caching

        # Initialize advanced cache manager
        if self.enable_caching:
            self.cache_manager = CacheManager()
        else:
            self.cache_manager = None

        # Performance metrics
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "response_times": [],
        }

    def _load_server_config(self) -> dict:
        """Load MCP server configuration"""
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            return config.get("mcpServers", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load MCP server config: {e}")
            return {}

    def _call_mcp_tool(self, server_name: str, tool_name: str, **kwargs) -> dict:
        """Call an MCP tool with advanced caching and performance tracking"""

        if server_name not in self.servers:
            raise ServerNotFoundError(f"MCP server '{server_name}' not configured")

        # Update performance metrics
        self.performance_metrics["total_requests"] += 1
        start_time = time.time()

        # Check advanced cache
        if self.enable_caching and self.cache_manager:
            cached_result = self.cache_manager.get(server_name, tool_name, **kwargs)
            if cached_result is not None:
                # Cache hit - record performance but don't count as API call
                response_time = time.time() - start_time
                self.performance_metrics["response_times"].append(response_time)
                self._update_average_response_time()
                logger.info(f"Cache hit for {server_name}.{tool_name}")
                return cached_result

        try:
            # Prepare the MCP call
            server_config = self.servers[server_name]
            command = [server_config["command"]] + server_config.get("args", [])

            # Create input for the MCP server
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": kwargs},
            }

            # Execute the MCP server call
            result = subprocess.run(
                command,
                input=json.dumps(mcp_request),
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                raise DataAccessError(f"MCP tool call failed: {result.stderr}")

            # Parse the result
            try:
                response = json.loads(result.stdout)
                if "error" in response:
                    raise DataAccessError(f"MCP tool error: {response['error']}")

                tool_result = response.get("result", {})

                # Parse the tool result if it's a JSON string
                if isinstance(tool_result.get("content"), list) and tool_result["content"]:
                    content = tool_result["content"][0].get("text", "{}")
                    try:
                        parsed_result = json.loads(content)
                    except json.JSONDecodeError:
                        parsed_result = {"raw_content": content}
                else:
                    parsed_result = tool_result

                # Store in advanced cache
                if self.enable_caching and self.cache_manager:
                    self.cache_manager.set(server_name, tool_name, parsed_result, **kwargs)

                # Record successful request performance
                response_time = time.time() - start_time
                self.performance_metrics["successful_requests"] += 1
                self.performance_metrics["response_times"].append(response_time)
                self._update_average_response_time()

                logger.info(f"MCP tool call successful: {server_name}.{tool_name} ({response_time:.3f}s)")
                return parsed_result

            except json.JSONDecodeError as e:
                raise DataAccessError(f"Failed to parse MCP response: {e}")

        except subprocess.TimeoutExpired:
            # Record failed request
            self.performance_metrics["failed_requests"] += 1
            response_time = time.time() - start_time
            self.performance_metrics["response_times"].append(response_time)
            self._update_average_response_time()
            raise DataAccessError(f"MCP tool call timed out: {server_name}.{tool_name}")
        except Exception as e:
            # Record failed request
            self.performance_metrics["failed_requests"] += 1
            response_time = time.time() - start_time
            self.performance_metrics["response_times"].append(response_time)
            self._update_average_response_time()
            raise DataAccessError(f"MCP tool call failed: {str(e)}")

    def _update_average_response_time(self):
        """Update the average response time metric"""
        if self.performance_metrics["response_times"]:
            # Keep only the last 100 response times for rolling average
            if len(self.performance_metrics["response_times"]) > 100:
                self.performance_metrics["response_times"] = self.performance_metrics["response_times"][-100:]

            self.performance_metrics["average_response_time"] = sum(self.performance_metrics["response_times"]) / len(
                self.performance_metrics["response_times"]
            )

    # Yahoo Finance Integration
    def get_stock_fundamentals(self, ticker: str) -> dict:
        """Get stock fundamentals via Yahoo Finance MCP server"""
        return self._call_mcp_tool("external-api", "get_company_fundamentals", ticker=ticker)

    def get_market_data(self, ticker: str, period: str = "1y") -> dict:
        """Get historical market data via Yahoo Finance MCP server"""
        return self._call_mcp_tool("external-api", "get_historical_data", ticker=ticker, period=period)

    def get_financial_statements(self, ticker: str) -> dict:
        """Get financial statements via Yahoo Finance MCP server"""
        return self._call_mcp_tool("external-api", "get_company_fundamentals", ticker=ticker)

    # SEC EDGAR Integration
    def get_company_filings(self, ticker: str, filing_type: str = "10-K") -> dict:
        """Get SEC filings via EDGAR MCP server"""
        return self._call_mcp_tool("external-api", "get_sec_filings", ticker=ticker, filing_type=filing_type)

    def get_edgar_financial_statements(self, ticker: str, period: str = "annual") -> dict:
        """Get SEC financial statements via EDGAR MCP server"""
        return self._call_mcp_tool("external-api", "get_sec_filings", ticker=ticker, filing_type="10-K")

    def get_sec_metrics(self, ticker: str, fiscal_year: str = None) -> dict:
        """Get SEC metrics via EDGAR MCP server"""
        kwargs = {"ticker": ticker}
        if fiscal_year:
            kwargs["fiscal_year"] = fiscal_year
        return self._call_mcp_tool("external-api", "get_sec_filings", **kwargs)

    # FRED Economic Data Integration
    def get_economic_indicator(self, series_id: str, date_range: str = "1y") -> dict:
        """Get economic indicator via FRED MCP server"""
        return self._call_mcp_tool(
            "external-api",
            "get_economic_data",
            indicator=series_id,
            start_date=date_range,
        )

    def get_sector_indicators(self, sector: str, indicators: str = "") -> dict:
        """Get sector-specific economic indicators via FRED MCP server"""
        return self._call_mcp_tool("external-api", "get_sector_performance")

    def get_inflation_data(self, period: str = "1y") -> dict:
        """Get inflation data via FRED MCP server"""
        return self._call_mcp_tool("external-api", "get_economic_data", indicator="CPIAUCSL")

    def get_interest_rates(self, rate_type: str = "all", period: str = "1y") -> dict:
        """Get interest rate data via FRED MCP server"""
        return self._call_mcp_tool("external-api", "get_economic_data", indicator="FEDFUNDS")

    # Cole Morton Trading Integration (deprecated - using external-api)
    def get_fundamental_analysis(self, ticker: str) -> dict:
        """Get comprehensive fundamental analysis via External API server"""
        return self._call_mcp_tool("external-api", "get_comprehensive_stock_analysis", ticker=ticker)

    def list_available_analyses(self, analysis_type: str = "fundamental_analysis") -> dict:
        """List available analyses via Cole Morton Trading MCP server"""
        raise NotImplementedError(
            "colemorton-trading server has been deprecated. Use external-api for fundamental analysis."
        )

    def get_trading_performance(self) -> dict:
        """Get trading performance data via Cole Morton Trading MCP server"""
        raise NotImplementedError("colemorton-trading server has been deprecated.")

    def generate_blog_content_from_analysis(self, ticker: str, content_type: str = "fundamental_analysis") -> dict:
        """Generate blog content from analysis via Cole Morton Trading MCP server"""
        return self._call_mcp_tool(
            "content-publishing",
            "generate_fundamental_analysis_blog",
            analysis_data={"ticker": ticker},
        )

    # Content Automation Integration
    def generate_blog_post(self, template_name: str, data: dict) -> dict:
        """Generate blog post via Content Automation MCP server"""
        return self._call_mcp_tool(
            "content-automation",
            "generate_blog_post",
            template_name=template_name,
            data=json.dumps(data),
        )

    def create_social_content(self, ticker: str, analysis_type: str, key_points: str) -> dict:
        """Create social media content via Content Automation MCP server"""
        return self._call_mcp_tool(
            "content-automation",
            "create_social_content",
            ticker=ticker,
            analysis_type=analysis_type,
            key_points=key_points,
        )

    def optimize_seo_content(self, content: str, keywords: str) -> dict:
        """Optimize content for SEO via Content Automation MCP server"""
        return self._call_mcp_tool(
            "content-automation",
            "optimize_seo_content",
            content=content,
            keywords=keywords,
        )

    # Utility Methods
    def get_comprehensive_analysis(self, ticker: str) -> dict:
        """Get comprehensive analysis combining multiple data sources"""

        logger.info(f"Starting comprehensive analysis for {ticker}")

        analysis = {
            "ticker": ticker.upper(),
            "analysis_date": datetime.now().isoformat(),
            "data_sources": [],
            "yahoo_finance": {},
            "sec_edgar": {},
            "economic_context": {},
            "existing_analysis": {},
        }

        # Yahoo Finance Data
        try:
            analysis["yahoo_finance"]["fundamentals"] = self.get_stock_fundamentals(ticker)
            analysis["yahoo_finance"]["market_data"] = self.get_market_data(ticker, "1y")
            analysis["yahoo_finance"]["financial_statements"] = self.get_financial_statements(ticker)
            analysis["data_sources"].append("yahoo_finance")
            logger.info(f"Yahoo Finance data retrieved for {ticker}")
        except Exception as e:
            logger.warning(f"Failed to get Yahoo Finance data: {e}")
            analysis["yahoo_finance"]["error"] = str(e)

        # SEC EDGAR Data
        try:
            analysis["sec_edgar"]["filings"] = self.get_company_filings(ticker, "10-K")
            analysis["sec_edgar"]["financial_statements"] = self.get_edgar_financial_statements(ticker)
            analysis["sec_edgar"]["metrics"] = self.get_sec_metrics(ticker)
            analysis["data_sources"].append("sec_edgar")
            logger.info(f"SEC EDGAR data retrieved for {ticker}")
        except Exception as e:
            logger.warning(f"Failed to get SEC EDGAR data: {e}")
            analysis["sec_edgar"]["error"] = str(e)

        # Economic Context
        try:
            analysis["economic_context"]["inflation"] = self.get_inflation_data("1y")
            analysis["economic_context"]["interest_rates"] = self.get_interest_rates("all", "1y")
            analysis["data_sources"].append("economic_context")
            logger.info("Economic context data retrieved")
        except Exception as e:
            logger.warning(f"Failed to get economic data: {e}")
            analysis["economic_context"]["error"] = str(e)

        # Existing Analysis
        try:
            analysis["existing_analysis"]["fundamental"] = self.get_fundamental_analysis(ticker)
            analysis["data_sources"].append("existing_analysis")
            logger.info(f"Existing analysis retrieved for {ticker}")
        except Exception as e:
            logger.warning(f"Failed to get existing analysis: {e}")
            analysis["existing_analysis"]["error"] = str(e)

        analysis["data_sources_count"] = len(analysis["data_sources"])
        analysis["analysis_complete"] = len(analysis["data_sources"]) > 0

        logger.info(f"Comprehensive analysis complete for {ticker}: {len(analysis['data_sources'])} sources")
        return analysis

    def save_analysis_to_file(self, analysis: dict, output_dir: str = "data/outputs/mcp_integration") -> str:
        """Save analysis results to file"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        ticker = analysis.get("ticker", "UNKNOWN")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_mcp_analysis_{timestamp}.json"

        file_path = output_path / filename

        with open(file_path, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"Analysis saved to {file_path}")
        return str(file_path)

    def clear_cache(self):
        """Clear all cache levels"""
        if self.cache_manager:
            self.cache_manager.session_cache.clear()
            # Also clean file cache
            for cache_file in self.cache_manager.file_cache_dir.glob("*.pkl"):
                cache_file.unlink()
            logger.info("All cache levels cleared")
        else:
            logger.info("Caching is disabled")

    def get_cache_stats(self) -> dict:
        """Get comprehensive cache statistics"""
        if self.cache_manager:
            return self.cache_manager.get_stats()
        return {"caching_disabled": True}

    def get_performance_metrics(self) -> dict:
        """Get comprehensive performance metrics"""
        metrics = self.performance_metrics.copy()

        # Calculate success rate
        total = metrics["total_requests"]
        if total > 0:
            metrics["success_rate"] = (metrics["successful_requests"] / total) * 100
            metrics["failure_rate"] = (metrics["failed_requests"] / total) * 100
        else:
            metrics["success_rate"] = 0
            metrics["failure_rate"] = 0

        # Add cache metrics if available
        if self.cache_manager:
            cache_stats = self.cache_manager.get_stats()
            metrics["cache_performance"] = cache_stats

        return metrics

    def invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries, optionally by pattern"""
        if self.cache_manager:
            if pattern:
                self.cache_manager.invalidate_pattern(pattern)
                logger.info(f"Invalidated cache entries matching: {pattern}")
            else:
                self.clear_cache()
        else:
            logger.info("Caching is disabled")

    def cleanup_cache(self):
        """Clean up expired cache entries"""
        if self.cache_manager:
            self.cache_manager.cleanup_expired()
        else:
            logger.info("Caching is disabled")

    def optimize_performance(self) -> dict:
        """Analyze and optimize performance"""
        recommendations = []

        metrics = self.get_performance_metrics()

        # Analyze performance metrics
        if metrics["total_requests"] > 10:
            if metrics["failure_rate"] > 10:
                recommendations.append("High failure rate detected - check MCP server stability")

            if metrics["average_response_time"] > 5.0:
                recommendations.append("Slow response times - consider server optimization")

            # Cache performance analysis
            if self.cache_manager:
                cache_stats = metrics.get("cache_performance", {})
                hit_ratio = cache_stats.get("hit_ratio", 0)

                if hit_ratio < 30:
                    recommendations.append("Low cache hit ratio - consider increasing cache TTL")
                elif hit_ratio > 80:
                    recommendations.append("Excellent cache performance")

        return {
            "performance_analysis": metrics,
            "recommendations": recommendations,
            "optimization_applied": len(recommendations) == 0,
        }


# Convenience function for scripts
def get_mcp_data_access() -> MCPDataAccess:
    """Get MCP data access instance"""
    return MCPDataAccess()


# Example usage functions for existing scripts
def example_yahoo_finance_integration():
    """Example of how to integrate with Yahoo Finance via MCP"""

    mcp = get_mcp_data_access()

    # Instead of direct yfinance calls:
    # ticker_obj = yf.Ticker("AAPL")
    # info = ticker_obj.info

    # Use MCP integration:
    fundamentals = mcp.get_stock_fundamentals("AAPL")
    market_data = mcp.get_market_data("AAPL", "1y")

    return {"fundamentals": fundamentals, "market_data": market_data}


def example_comprehensive_analysis():
    """Example of comprehensive analysis using multiple MCP servers"""

    mcp = get_mcp_data_access()

    # Get comprehensive analysis for a ticker
    ticker = "AAPL"
    analysis = mcp.get_comprehensive_analysis(ticker)

    # Save to file
    file_path = mcp.save_analysis_to_file(analysis)

    print("Comprehensive analysis saved to: {file_path}")
    return analysis


if __name__ == "__main__":
    # Example usage
    print("MCP Integration Utility - Example Usage")

    try:
        mcp = get_mcp_data_access()

        # Test Yahoo Finance integration
        print("\n1. Testing Yahoo Finance integration...")
        yahoo_data = mcp.get_stock_fundamentals("AAPL")
        print("Yahoo Finance data retrieved: {bool(yahoo_data)}")

        # Test SEC EDGAR integration
        print("\n2. Testing SEC EDGAR integration...")
        edgar_data = mcp.get_company_filings("AAPL", "10-K")
        print("SEC EDGAR data retrieved: {bool(edgar_data)}")

        # Test FRED integration
        print("\n3. Testing FRED integration...")
        inflation_data = mcp.get_inflation_data("1y")
        print("FRED data retrieved: {bool(inflation_data)}")

        # Test comprehensive analysis
        print("\n4. Testing comprehensive analysis...")
        comprehensive = mcp.get_comprehensive_analysis("AAPL")
        print("Data sources: {comprehensive.get('data_sources', [])}")

        # Cache stats and performance metrics
        print("\n5. Cache statistics: {mcp.get_cache_stats()}")
        print("\n6. Performance metrics: {mcp.get_performance_metrics()}")

        # Performance optimization
        print("\n7. Performance optimization: {mcp.optimize_performance()}")

        # Cache cleanup
        print("\n8. Running cache cleanup...")
        mcp.cleanup_cache()

    except Exception as e:
        print("Error: {e}")
        logger.error(f"MCP integration test failed: {e}")
