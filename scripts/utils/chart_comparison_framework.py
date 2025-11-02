#!/usr/bin/env python3
"""
Visual comparison framework for matplotlib vs Plotly chart outputs.

This module provides tools to generate side-by-side comparisons and
quality metrics for chart migration validation.
"""

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from PIL import Image

from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    QualityDistribution,
)


class ChartComparisonFramework:
    """Framework for comparing matplotlib and Plotly chart outputs."""

    def __init__(self, output_dir: str = "data/outputs/chart_comparisons"):
        """
        Initialize comparison framework.

        Args:
            output_dir: Directory for saving comparison outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def compare_charts(
        self,
        matplotlib_generator,
        plotly_generator,
        chart_type: str,
        test_data: Any,
        mode: str = "light",
    ) -> dict[str, Any]:
        """
        Compare matplotlib and Plotly implementations of a chart.

        Args:
            matplotlib_generator: Matplotlib chart generator instance
            plotly_generator: Plotly chart generator instance
            chart_type: Type of chart to compare
            test_data: Test data for the chart
            mode: 'light' or 'dark' mode

        Returns:
            Dictionary containing comparison results
        """
        # Generate matplotlib chart
        fig_mpl, ax_mpl = plt.subplots(figsize=(8, 6))
        theme = matplotlib_generator.theme_manager.get_theme_colors(mode)
        fig_mpl.patch.set_facecolor(theme.background)
        ax_mpl.set_facecolor(theme.background)

        # Call the appropriate matplotlib method
        if chart_type == "monthly_bars":
            matplotlib_generator.create_enhanced_monthly_bars(ax_mpl, test_data, mode)
        elif chart_type == "donut_chart":
            matplotlib_generator.create_enhanced_donut_chart(ax_mpl, test_data, mode)
        elif chart_type == "waterfall":
            matplotlib_generator.create_waterfall_chart(ax_mpl, test_data, mode)
        elif chart_type == "scatter":
            matplotlib_generator.create_enhanced_scatter(ax_mpl, test_data, mode)

        # Save matplotlib output
        mpl_path = self.output_dir / f"{chart_type}_matplotlib_{mode}.png"
        fig_mpl.savefig(mpl_path, dpi=150, bbox_inches="tight", facecolor=theme.background)
        plt.close(fig_mpl)

        # Generate Plotly chart
        fig_plotly = go.Figure()

        # Call the appropriate Plotly method
        if chart_type == "monthly_bars":
            result = plotly_generator.create_enhanced_monthly_bars(fig_plotly, test_data, mode)
            if result is not None and isinstance(result, go.Figure):
                fig_plotly = result
        elif chart_type == "donut_chart":
            result = plotly_generator.create_enhanced_donut_chart(fig_plotly, test_data, mode)
            if result is not None and isinstance(result, go.Figure):
                fig_plotly = result
        elif chart_type == "waterfall":
            result = plotly_generator.create_waterfall_chart(fig_plotly, test_data, mode)
            if result is not None and isinstance(result, go.Figure):
                fig_plotly = result
        elif chart_type == "scatter":
            result = plotly_generator.create_enhanced_scatter(fig_plotly, test_data, mode)
            if result is not None and isinstance(result, go.Figure):
                fig_plotly = result

        # Save Plotly output
        plotly_path = self.output_dir / f"{chart_type}_plotly_{mode}.png"
        fig_plotly.write_image(plotly_path, width=800, height=600, scale=2)

        # Create side-by-side comparison
        comparison_path = self._create_side_by_side_comparison(mpl_path, plotly_path, chart_type, mode)

        # Calculate visual similarity metrics
        similarity_metrics = self._calculate_similarity_metrics(mpl_path, plotly_path)

        # Export JSON schema
        json_schema = plotly_generator.export_chart_config(f"enhanced_{chart_type}", {"mode": mode})
        schema_path = self.output_dir / f"{chart_type}_schema_{mode}.json"
        with open(schema_path, "w") as f:
            json.dump(json_schema, f, indent=2)

        return {
            "matplotlib_path": str(mpl_path),
            "plotly_path": str(plotly_path),
            "comparison_path": str(comparison_path),
            "schema_path": str(schema_path),
            "similarity_metrics": similarity_metrics,
            "chart_type": chart_type,
            "mode": mode,
        }

    def _create_side_by_side_comparison(self, mpl_path: Path, plotly_path: Path, chart_type: str, mode: str) -> Path:
        """Create side-by-side comparison image."""
        # Load images
        img_mpl = Image.open(mpl_path)
        img_plotly = Image.open(plotly_path)

        # Resize to same height
        height = max(img_mpl.height, img_plotly.height)
        img_mpl = img_mpl.resize(
            (int(img_mpl.width * height / img_mpl.height), height),
            Image.Resampling.LANCZOS,
        )
        img_plotly = img_plotly.resize(
            (int(img_plotly.width * height / img_plotly.height), height),
            Image.Resampling.LANCZOS,
        )

        # Create comparison image
        total_width = img_mpl.width + img_plotly.width + 20  # 20px gap
        comparison = Image.new("RGB", (total_width, height + 80), "white")

        # Paste images
        comparison.paste(img_mpl, (0, 80))
        comparison.paste(img_plotly, (img_mpl.width + 20, 80))

        # Add labels
        from PIL import ImageDraw, ImageFont

        draw = ImageDraw.Draw(comparison)

        # Try to use a better font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial.ttf", 24)
            title_font = ImageFont.truetype("Arial.ttf", 32)
        except:
            font = ImageFont.load_default()
            title_font = font

        # Add title
        title = f"{chart_type.replace('_', ' ').title()} Comparison ({mode.title()} Mode)"
        draw.text((total_width // 2, 20), title, fill="black", font=title_font, anchor="mt")

        # Add labels
        draw.text((img_mpl.width // 2, 60), "Matplotlib", fill="black", font=font, anchor="mb")
        draw.text(
            (img_mpl.width + 20 + img_plotly.width // 2, 60),
            "Plotly",
            fill="black",
            font=font,
            anchor="mb",
        )

        # Save comparison
        comparison_path = self.output_dir / f"{chart_type}_comparison_{mode}.png"
        comparison.save(comparison_path)

        return comparison_path

    def _calculate_similarity_metrics(self, img1_path: Path, img2_path: Path) -> dict[str, float]:
        """Calculate visual similarity metrics between two images."""
        # Load images as numpy arrays
        img1 = np.array(Image.open(img1_path).convert("RGB"))
        img2 = np.array(Image.open(img2_path).convert("RGB"))

        # Resize to same dimensions for comparison
        height = min(img1.shape[0], img2.shape[0])
        width = min(img1.shape[1], img2.shape[1])
        img1 = img1[:height, :width]
        img2 = img2[:height, :width]

        # Calculate metrics
        mse = np.mean((img1 - img2) ** 2)
        similarity_percent = max(0, 100 - (mse / 255**2 * 100))

        return {
            "mse": float(mse),
            "similarity_percent": float(similarity_percent),
            "size_match": img1.shape == img2.shape,
        }

    def generate_test_report(self, comparison_results: list[dict[str, Any]]) -> str:
        """
        Generate a test report from comparison results.

        Args:
            comparison_results: List of comparison result dictionaries

        Returns:
            Path to generated report
        """
        report_path = self.output_dir / "comparison_report.md"

        with open(report_path, "w") as f:
            f.write("# Chart Migration Comparison Report\n\n")
            f.write("## Summary\n\n")

            # Calculate overall metrics
            avg_similarity = np.mean([r["similarity_metrics"]["similarity_percent"] for r in comparison_results])
            f.write(f"- **Average Visual Similarity**: {avg_similarity:.1f}%\n")
            f.write(f"- **Charts Compared**: {len(comparison_results)}\n")
            from datetime import datetime

            f.write(f"- **Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Detailed Comparisons\n\n")

            for result in comparison_results:
                f.write(f"### {result['chart_type'].replace('_', ' ').title()} ({result['mode'].title()} Mode)\n\n")
                f.write(f"![Comparison]({Path(result['comparison_path']).name})\n\n")

                metrics = result["similarity_metrics"]
                f.write(f"- **Visual Similarity**: {metrics['similarity_percent']:.1f}%\n")
                f.write(f"- **MSE**: {metrics['mse']:.2f}\n")
                f.write(f"- **Size Match**: {'✓' if metrics['size_match'] else '✗'}\n")
                f.write(
                    f"- **JSON Schema**: [{Path(result['schema_path']).name}]({Path(result['schema_path']).name})\n\n"
                )

                f.write("---\n\n")

        return str(report_path)


def create_test_data() -> dict[str, Any]:
    """Create sample test data for chart comparison."""
    # Monthly performance data
    monthly_data = [
        MonthlyPerformance(
            month="January",
            year=2024,
            trades_closed=12,
            win_rate=65.5,
            average_return=2.3,
            market_context="Bullish",
        ),
        MonthlyPerformance(
            month="February",
            year=2024,
            trades_closed=8,
            win_rate=58.2,
            average_return=-0.8,
            market_context="Bearish",
        ),
        MonthlyPerformance(
            month="March",
            year=2024,
            trades_closed=15,
            win_rate=72.1,
            average_return=3.5,
            market_context="Volatile",
        ),
        MonthlyPerformance(
            month="April",
            year=2024,
            trades_closed=10,
            win_rate=61.8,
            average_return=1.2,
            market_context="Sideways",
        ),
        MonthlyPerformance(
            month="May",
            year=2024,
            trades_closed=13,
            win_rate=69.3,
            average_return=2.7,
            market_context="Bullish",
        ),
        MonthlyPerformance(
            month="June",
            year=2024,
            trades_closed=9,
            win_rate=55.7,
            average_return=-1.1,
            market_context="Bearish",
        ),
    ]

    # Quality distribution data
    quality_data = [
        QualityDistribution(
            category="Excellent",
            count=15,
            percentage=25.5,
            win_rate=85.2,
            average_return=4.2,
        ),
        QualityDistribution(
            category="Good",
            count=21,
            percentage=35.8,
            win_rate=68.5,
            average_return=2.1,
        ),
        QualityDistribution(
            category="Poor",
            count=12,
            percentage=20.3,
            win_rate=45.7,
            average_return=-0.8,
        ),
        QualityDistribution(
            category="Failed",
            count=11,
            percentage=18.4,
            win_rate=22.1,
            average_return=-3.5,
        ),
    ]

    return {"monthly_data": monthly_data, "quality_data": quality_data}
