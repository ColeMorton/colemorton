#!/usr/bin/env python3
"""
Production Performance Optimizer for Plotly chart generation.

This module provides production-grade performance optimizations including
caching, memory management, batch processing, and scalability enhancements
for high-volume chart generation workloads.
"""

import hashlib
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from functools import wraps
from typing import Any

import plotly.graph_objects as go
import plotly.io as pio


@dataclass
class PerformanceMetrics:
    """Performance metrics for chart generation."""

    chart_type: str
    generation_time: float
    memory_usage: int
    cache_hit: bool
    data_size: int
    optimization_level: str


class PlotlyTemplateCache:
    """High-performance template caching system."""

    def __init__(self, max_size: int = 100):
        """
        Initialize template cache.

        Args:
            max_size: Maximum number of cached templates
        """
        self.max_size = max_size
        self.cache = {}
        self.access_count = {}
        self.lock = threading.RLock()

    def get_template(self, template_name: str, mode: str) -> go.layout.Template | None:
        """
        Get cached template or None if not found.

        Args:
            template_name: Name of the template
            mode: Theme mode ('light' or 'dark')

        Returns:
            Cached template or None
        """
        cache_key = f"{template_name}_{mode}"

        with self.lock:
            if cache_key in self.cache:
                self.access_count[cache_key] = self.access_count.get(cache_key, 0) + 1
                return self.cache[cache_key]

        return None

    def set_template(self, template_name: str, mode: str, template: go.layout.Template):
        """
        Cache a template.

        Args:
            template_name: Name of the template
            mode: Theme mode
            template: Template object to cache
        """
        cache_key = f"{template_name}_{mode}"

        with self.lock:
            # Evict least recently used if at capacity
            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                lru_key = min(self.access_count.keys(), key=self.access_count.get)
                del self.cache[lru_key]
                del self.access_count[lru_key]

            self.cache[cache_key] = template
            self.access_count[cache_key] = 1

    def clear(self):
        """Clear all cached templates."""
        with self.lock:
            self.cache.clear()
            self.access_count.clear()


class DataSampleManager:
    """Manages data sampling for large datasets."""

    @staticmethod
    def should_sample(data_size: int, chart_type: str) -> bool:
        """
        Determine if data should be sampled.

        Args:
            data_size: Size of the dataset
            chart_type: Type of chart being generated

        Returns:
            True if sampling is recommended
        """
        thresholds = {
            "scatter": 1000,
            "waterfall": 200,
            "monthly_bars": 50,
            "donut": 20,
        }

        threshold = thresholds.get(chart_type.lower(), 500)
        return data_size > threshold

    @staticmethod
    def sample_data(data: list[Any], target_size: int, strategy: str = "intelligent") -> list[Any]:
        """
        Sample data using specified strategy.

        Args:
            data: Original dataset
            target_size: Target sample size
            strategy: Sampling strategy ('random', 'systematic', 'intelligent')

        Returns:
            Sampled dataset
        """
        if len(data) <= target_size:
            return data

        if strategy == "random":
            import random

            return random.sample(data, target_size)

        if strategy == "systematic":
            step = len(data) // target_size
            return [data[i] for i in range(0, len(data), step)][:target_size]

        if strategy == "intelligent":
            # Keep outliers and representative samples
            sorted_data = sorted(data, key=lambda x: getattr(x, "return_pct", 0))

            # Take extremes (outliers)
            extremes_count = min(target_size // 4, 10)
            extremes = sorted_data[:extremes_count] + sorted_data[-extremes_count:]

            # Take systematic sample from middle
            remaining_size = target_size - len(extremes)
            middle_data = sorted_data[extremes_count:-extremes_count]

            if middle_data and remaining_size > 0:
                step = len(middle_data) // remaining_size
                middle_sample = [middle_data[i] for i in range(0, len(middle_data), max(1, step))][:remaining_size]
                return extremes + middle_sample

            return extremes

        return data[:target_size]


class ChartGenerationOptimizer:
    """Production-grade chart generation optimizer."""

    def __init__(self, theme_manager=None):
        """
        Initialize production optimizer.

        Args:
            theme_manager: Optional theme manager instance
        """
        self.theme_manager = theme_manager
        self.template_cache = PlotlyTemplateCache(max_size=50)
        self.data_sampler = DataSampleManager()
        self.metrics_history = []
        self.config_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Performance configuration
        self.config = {
            "enable_webgl": True,
            "cache_templates": True,
            "sample_large_datasets": True,
            "batch_processing": True,
            "memory_optimization": True,
            "parallel_processing": True,
        }

        # Configure Plotly for production
        self._configure_plotly_production()

    def _configure_plotly_production(self):
        """Configure Plotly for production performance."""
        # Configure renderers for production
        pio.renderers.default = "png"

        # Optimize Kaleido for production
        try:
            if hasattr(pio, "kaleido") and pio.kaleido.scope:
                # Production Kaleido settings
                pio.kaleido.scope.default_format = "png"
                pio.kaleido.scope.default_scale = 2  # Balanced quality/performance
                pio.kaleido.scope.chromium_args = [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-features=VizDisplayCompositor",
                ]
        except Exception:
            # Continue without Kaleido optimization
            pass

    def optimize_chart_generation(
        self, chart_generator_func: Callable, chart_type: str, data: list[Any], **kwargs
    ) -> tuple[Any, PerformanceMetrics]:
        """
        Optimize chart generation with caching and performance enhancements.

        Args:
            chart_generator_func: Chart generation function
            chart_type: Type of chart being generated
            data: Chart data
            **kwargs: Additional arguments for chart generation

        Returns:
            Tuple of (generated_chart, performance_metrics)
        """
        start_time = time.time()
        memory_start = self._get_memory_usage()

        # Generate cache key
        cache_key = self._generate_cache_key(chart_type, data, kwargs)

        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result and self.config["cache_templates"]:
            metrics = PerformanceMetrics(
                chart_type=chart_type,
                generation_time=time.time() - start_time,
                memory_usage=self._get_memory_usage() - memory_start,
                cache_hit=True,
                data_size=len(data),
                optimization_level="cached",
            )
            return cached_result, metrics

        # Optimize data if needed
        optimized_data = self._optimize_data(data, chart_type)
        optimization_level = "sampled" if len(optimized_data) < len(data) else "full"

        # Configure WebGL if appropriate
        if self._should_use_webgl(chart_type, len(optimized_data)):
            kwargs["use_webgl"] = True
            optimization_level += "_webgl"

        # Generate chart with optimizations
        try:
            result = chart_generator_func(data=optimized_data, **kwargs)

            # Cache result if appropriate
            if self._should_cache_result(chart_type, len(data)):
                self._cache_result(cache_key, result)

            # Record metrics
            metrics = PerformanceMetrics(
                chart_type=chart_type,
                generation_time=time.time() - start_time,
                memory_usage=self._get_memory_usage() - memory_start,
                cache_hit=False,
                data_size=len(data),
                optimization_level=optimization_level,
            )

            self.metrics_history.append(metrics)
            return result, metrics

        except Exception:
            # Fallback to non-optimized generation
            result = chart_generator_func(data=data, **kwargs)

            metrics = PerformanceMetrics(
                chart_type=chart_type,
                generation_time=time.time() - start_time,
                memory_usage=self._get_memory_usage() - memory_start,
                cache_hit=False,
                data_size=len(data),
                optimization_level="fallback",
            )

            return result, metrics

    def batch_optimize_charts(
        self, chart_requests: list[dict[str, Any]], max_workers: int | None = None
    ) -> list[tuple[Any, PerformanceMetrics]]:
        """
        Batch process multiple chart generation requests with optimization.

        Args:
            chart_requests: List of chart generation requests
            max_workers: Maximum number of worker threads

        Returns:
            List of (chart_result, metrics) tuples
        """
        if not self.config["batch_processing"]:
            # Sequential processing
            return [self.optimize_chart_generation(**request) for request in chart_requests]

        # Parallel batch processing
        max_workers = max_workers or min(len(chart_requests), 4)
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_request = {
                executor.submit(self.optimize_chart_generation, **request): request for request in chart_requests
            }

            # Collect results
            for future in as_completed(future_to_request):
                try:
                    result = future.result()
                    results.append(result)
                except Exception:
                    # Log error and continue
                    print("Chart generation failed: {e}")
                    results.append((None, None))

        return results

    def _optimize_data(self, data: list[Any], chart_type: str) -> list[Any]:
        """Optimize data for chart generation."""
        if not self.config["sample_large_datasets"]:
            return data

        if self.data_sampler.should_sample(len(data), chart_type):
            # Determine target size based on chart type
            target_sizes = {
                "scatter": 500,
                "waterfall": 100,
                "monthly_bars": 24,  # 2 years of monthly data
                "donut": 15,
            }

            target_size = target_sizes.get(chart_type.lower(), 200)
            return self.data_sampler.sample_data(data, target_size, "intelligent")

        return data

    def _should_use_webgl(self, chart_type: str, data_size: int) -> bool:
        """Determine if WebGL should be used for performance."""
        if not self.config["enable_webgl"]:
            return False

        # WebGL benefits for large scatter plots
        if "scatter" in chart_type.lower() and data_size > 100:
            return True

        return False

    def _generate_cache_key(self, chart_type: str, data: list[Any], kwargs: dict[str, Any]) -> str:
        """Generate cache key for chart configuration."""
        # Create deterministic hash from chart parameters
        cache_data = {
            "chart_type": chart_type,
            "data_hash": self._hash_data(data),
            "kwargs": {k: v for k, v in kwargs.items() if k != "figure"},  # Exclude figure objects
        }

        cache_string = str(sorted(cache_data.items()))
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _hash_data(self, data: list[Any]) -> str:
        """Generate hash for data list."""
        try:
            # Sample data for hashing to avoid performance issues
            sample_data = data[:10] if len(data) > 10 else data
            data_string = str([(getattr(item, "__dict__", str(item))) for item in sample_data])
            return hashlib.md5(data_string.encode()).hexdigest()
        except:
            return hashlib.md5(str(len(data)).encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Any | None:
        """Get cached result if available."""
        return self.config_cache.get(cache_key)

    def _cache_result(self, cache_key: str, result: Any):
        """Cache generation result."""
        # Limit cache size
        if len(self.config_cache) > 100:
            # Remove oldest entries
            oldest_keys = list(self.config_cache.keys())[:20]
            for key in oldest_keys:
                del self.config_cache[key]

        self.config_cache[cache_key] = result

    def _should_cache_result(self, chart_type: str, data_size: int) -> bool:
        """Determine if result should be cached."""
        # Cache smaller datasets and standard chart types
        if data_size < 100 and chart_type in ["monthly_bars", "donut"]:
            return True
        return False

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except ImportError:
            return 0

    def get_performance_report(self) -> dict[str, Any]:
        """
        Generate performance report from metrics history.

        Returns:
            Performance report dictionary
        """
        if not self.metrics_history:
            return {"message": "No performance data available"}

        # Calculate statistics
        total_charts = len(self.metrics_history)
        cache_hits = sum(1 for m in self.metrics_history if m.cache_hit)

        generation_times = [m.generation_time for m in self.metrics_history]
        memory_usage = [m.memory_usage for m in self.metrics_history]

        # Group by chart type
        by_chart_type = {}
        for metric in self.metrics_history:
            if metric.chart_type not in by_chart_type:
                by_chart_type[metric.chart_type] = []
            by_chart_type[metric.chart_type].append(metric)

        chart_type_stats = {}
        for chart_type, metrics in by_chart_type.items():
            times = [m.generation_time for m in metrics]
            chart_type_stats[chart_type] = {
                "count": len(metrics),
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "cache_hit_rate": sum(1 for m in metrics if m.cache_hit) / len(metrics),
            }

        return {
            "summary": {
                "total_charts_generated": total_charts,
                "cache_hit_rate": cache_hits / total_charts if total_charts > 0 else 0,
                "avg_generation_time": sum(generation_times) / len(generation_times),
                "total_memory_used": sum(memory_usage),
                "optimization_config": self.config,
            },
            "by_chart_type": chart_type_stats,
            "performance_trends": {
                "generation_times": generation_times[-20:],  # Last 20 charts
                "memory_usage": memory_usage[-20:],
            },
        }

    def optimize_export_settings(self, format: str = "png", quality_level: str = "balanced") -> dict[str, Any]:
        """
        Get optimized export settings for production.

        Args:
            format: Export format
            quality_level: Quality level ('fast', 'balanced', 'high')

        Returns:
            Optimized export configuration
        """
        base_config = {"format": format, "engine": "kaleido"}

        if quality_level == "fast":
            base_config.update({"width": 800, "height": 600, "scale": 1})
        elif quality_level == "balanced":
            base_config.update({"width": 1200, "height": 900, "scale": 2})
        elif quality_level == "high":
            base_config.update({"width": 1600, "height": 1200, "scale": 3})

        return base_config

    def cleanup_resources(self):
        """Clean up optimizer resources."""
        self.template_cache.clear()
        self.config_cache.clear()
        self.executor.shutdown(wait=True)


def performance_monitor(func):
    """Decorator to monitor chart generation performance."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()

            print("⚡ {func.__name__} completed in {end_time - start_time:.3f}s")
            return result
        except Exception:
            end_time = time.time()
            print("❌ {func.__name__} failed in {end_time - start_time:.3f}s: {e}")
            raise

    return wrapper


def create_production_optimizer(theme_manager=None) -> ChartGenerationOptimizer:
    """
    Factory function to create a ChartGenerationOptimizer instance.

    Args:
        theme_manager: Optional theme manager instance

    Returns:
        Configured ChartGenerationOptimizer instance
    """
    return ChartGenerationOptimizer(theme_manager)


if __name__ == "__main__":
    # Test production optimizer
    optimizer = create_production_optimizer()

    print("🚀 Production Optimizer Initialized")
    print("Configuration: {optimizer.config}")

    # Test template caching
    optimizer.template_cache.set_template("test", "light", "template_object")
    cached = optimizer.template_cache.get_template("test", "light")
    print("✅ Template caching working: {cached is not None}")

    # Test data sampling
    large_data = list(range(1000))
    sampled = optimizer.data_sampler.sample_data(large_data, 100, "intelligent")
    print("📊 Data sampling: {len(large_data)} -> {len(sampled)} items")

    # Generate performance report
    report = optimizer.get_performance_report()
    print("📈 Performance report: {report.get('message', 'Data available')}")

    print("✅ Production optimizer ready for deployment")
