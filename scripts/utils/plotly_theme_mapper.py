#!/usr/bin/env python3
"""
Plotly theme mapper for Cole Morton design system integration.

This module maps Cole Morton theme configurations to Plotly templates
and layout specifications for consistent styling across chart engines.
"""

from typing import Any

import plotly.graph_objects as go
import plotly.io as pio


class PlotlyThemeMapper:
    """Maps Cole Morton themes to Plotly configurations."""

    def __init__(self, theme_manager):
        """
        Initialize Plotly theme mapper.

        Args:
            theme_manager: Cole Morton theme manager instance
        """
        self.theme_manager = theme_manager
        self._create_sensylate_templates()

    def _create_sensylate_templates(self):
        """Create comprehensive Plotly templates for light and dark modes."""
        # Create light mode template
        light_template = self._create_template("light")
        pio.templates["colemorton_light"] = light_template

        # Create dark mode template
        dark_template = self._create_template("dark")
        pio.templates["colemorton_dark"] = dark_template

        # Create high-DPI optimized templates
        light_hd_template = self._create_high_dpi_template("light")
        pio.templates["colemorton_light_hd"] = light_hd_template

        dark_hd_template = self._create_high_dpi_template("dark")
        pio.templates["colemorton_dark_hd"] = dark_hd_template

        # Create dashboard-specific template
        dashboard_template = self._create_dashboard_template("light")
        pio.templates["sensylate_dashboard"] = dashboard_template

        # Set default template
        pio.templates.default = "colemorton_light"

    def _create_template(self, mode: str) -> go.layout.Template:
        """
        Create a Plotly template for the specified mode.

        Args:
            mode: 'light' or 'dark'

        Returns:
            Plotly template object
        """
        theme = self.theme_manager.get_theme_colors(mode)
        colors = self.theme_manager.color_palette

        # Get font configuration
        fonts = self.theme_manager._get_font_list()
        primary_font = fonts[0] if fonts else "sans-serif"

        template = go.layout.Template()

        # Layout configuration
        template.layout = go.Layout(
            # Color scheme
            plot_bgcolor=theme.background,
            paper_bgcolor=theme.background,
            # Font configuration
            font=dict(family=", ".join(fonts), size=12, color=theme.body_text),
            # Title styling
            title=dict(
                font=dict(family=", ".join(fonts), size=18, color=theme.primary_text),
                pad=dict(t=45),  # Match matplotlib title padding
            ),
            # Axis styling
            xaxis=dict(
                showgrid=True,
                gridcolor=theme.borders,
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor=theme.borders,
                showline=True,
                linecolor=theme.borders,
                tickfont=dict(size=10, color=theme.body_text),
                title_font=dict(size=12, color=theme.body_text),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=theme.borders,
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor=theme.borders,
                showline=True,
                linecolor=theme.borders,
                tickfont=dict(size=10, color=theme.body_text),
                title_font=dict(size=12, color=theme.body_text),
            ),
            # Legend styling
            legend=dict(
                bgcolor=theme.card_backgrounds,
                bordercolor=theme.borders,
                borderwidth=1,
                font=dict(size=11, color=theme.body_text),
            ),
            # Margin configuration
            margin=dict(l=60, r=60, t=80, b=60),
            # Colorway (default color sequence)
            colorway=colors.get_extended_palette(),
        )

        # Bar chart styling
        template.data.bar = [go.Bar(marker=dict(line=dict(color=theme.borders, width=1)), opacity=0.8)]

        # Pie/Donut chart styling
        template.data.pie = [
            go.Pie(
                marker=dict(line=dict(color=theme.background, width=2)),
                textfont=dict(color="white", size=9),
            )
        ]

        # Scatter plot styling
        template.data.scatter = [go.Scatter(marker=dict(line=dict(color=theme.borders, width=0.8)))]

        return template

    def _create_high_dpi_template(self, mode: str) -> go.layout.Template:
        """
        Create high-DPI optimized template for print and export quality.

        Args:
            mode: 'light' or 'dark'

        Returns:
            High-DPI optimized Plotly template
        """
        # Start with base template
        template = self._create_template(mode)

        # Enhance for high-DPI
        template.layout.font.size = 14  # Larger base font
        template.layout.title.font.size = 22  # Larger title

        # Increase line widths and marker sizes for better visibility
        if hasattr(template.data, "scatter"):
            for scatter in template.data.scatter:
                if hasattr(scatter.marker, "line"):
                    scatter.marker.line.width = 1.5

        if hasattr(template.data, "bar"):
            for bar in template.data.bar:
                if hasattr(bar.marker, "line"):
                    bar.marker.line.width = 1.5

        # Enhanced grid and axis styling for high-DPI
        template.layout.xaxis.gridwidth = 1
        template.layout.yaxis.gridwidth = 1
        template.layout.xaxis.linewidth = 2
        template.layout.yaxis.linewidth = 2

        return template

    def _create_dashboard_template(self, mode: str) -> go.layout.Template:
        """
        Create dashboard-specific template optimized for multi-chart layouts.

        Args:
            mode: 'light' or 'dark'

        Returns:
            Dashboard-optimized Plotly template
        """
        template = self._create_template(mode)
        theme = self.theme_manager.get_theme_colors(mode)

        # Dashboard-specific layout optimizations
        template.layout.margin = dict(l=50, r=50, t=80, b=50)  # Tighter margins
        template.layout.font.size = 11  # Slightly smaller for space efficiency
        template.layout.title.font.size = 16  # Smaller title for dashboard context

        # Optimize for subplot layouts
        template.layout.xaxis.ticklabelstandoff = 15
        template.layout.yaxis.ticklabelstandoff = 15
        template.layout.xaxis.tickfont.size = 9
        template.layout.yaxis.tickfont.size = 9

        # Enhanced subplot borders and spacing
        template.layout.plot_bgcolor = theme.background
        template.layout.paper_bgcolor = theme.background

        return template

    def get_template_name(self, mode: str = "light", high_dpi: bool = False, dashboard: bool = False) -> str:
        """
        Get appropriate template name based on requirements.

        Args:
            mode: 'light' or 'dark'
            high_dpi: Whether to use high-DPI template
            dashboard: Whether to use dashboard-optimized template

        Returns:
            Template name string
        """
        if dashboard:
            return "sensylate_dashboard"
        if high_dpi:
            return f"sensylate_{mode}_hd"
        return f"sensylate_{mode}"

    def apply_template(
        self,
        fig: go.Figure,
        mode: str = "light",
        high_dpi: bool = False,
        dashboard: bool = False,
    ) -> go.Figure:
        """
        Apply appropriate Cole Morton template to figure.

        Args:
            fig: Plotly figure
            mode: 'light' or 'dark'
            high_dpi: Whether to use high-DPI template
            dashboard: Whether to use dashboard template

        Returns:
            Figure with applied template
        """
        template_name = self.get_template_name(mode, high_dpi, dashboard)
        fig.update_layout(template=template_name)
        return fig

    def get_layout_config(self, mode: str = "light", title: str = "") -> dict[str, Any]:
        """
        Get Plotly layout configuration for specified mode.

        Args:
            mode: 'light' or 'dark'
            title: Chart title

        Returns:
            Dictionary of layout parameters
        """
        theme = self.theme_manager.get_theme_colors(mode)

        return {
            "template": f"sensylate_{mode}",
            "title": {
                "text": title,
                "font": {
                    "size": 18,
                    "color": theme.primary_text,
                    "family": ", ".join(self.theme_manager._get_font_list()),
                },
                "pad": {"t": 45},
            },
            "showlegend": False,  # Default, override as needed
            "hovermode": "closest",
            "plot_bgcolor": theme.background,
            "paper_bgcolor": theme.background,
        }

    def get_quality_colors_mapping(self) -> dict[str, str]:
        """Get Plotly-compatible quality color mapping."""
        return self.theme_manager.get_quality_colors()

    def get_performance_colors_mapping(self) -> dict[str, str]:
        """Get Plotly-compatible performance color mapping."""
        return self.theme_manager.get_performance_colors()

    def get_monthly_colors_list(self) -> list[str]:
        """Get Plotly-compatible monthly color list."""
        return self.theme_manager.get_monthly_colors()

    def apply_theme_to_figure(self, fig: go.Figure, mode: str = "light", title: str = ""):
        """
        Apply Cole Morton theme to a Plotly figure.

        Args:
            fig: Plotly figure object
            mode: 'light' or 'dark'
            title: Chart title
        """
        layout_config = self.get_layout_config(mode, title)
        fig.update_layout(**layout_config)

    def create_export_config(self, width: int = 1600, height: int = 1200, scale: float = 2.0) -> dict[str, Any]:
        """
        Create export configuration for high-quality static images.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            scale: Scale factor for high DPI

        Returns:
            Export configuration dictionary
        """
        return {"width": width, "height": height, "scale": scale, "format": "png"}

    def get_advanced_styling_config(self, chart_type: str, mode: str = "light") -> dict[str, Any]:
        """
        Get advanced styling configuration for complex chart types.

        Args:
            chart_type: Type of chart ('waterfall', 'scatter', 'performance_bands')
            mode: 'light' or 'dark'

        Returns:
            Advanced styling configuration dictionary
        """
        theme = self.theme_manager.get_theme_colors(mode)
        performance_colors = self.get_performance_colors_mapping()

        if chart_type == "waterfall":
            return {
                "bars": {
                    "positive_color": performance_colors["positive"],
                    "negative_color": performance_colors["negative"],
                    "opacity": 0.8,
                    "border_color": theme.borders,
                    "border_width": 0.5,
                },
                "cumulative_line": {
                    "color": self.theme_manager.color_palette.tertiary_data,
                    "width": 3,
                    "opacity": 0.8,
                    "marker_size": 6,
                    "marker_color": self.theme_manager.color_palette.tertiary_data,
                    "marker_border_color": "white",
                    "marker_border_width": 1,
                },
                "annotations": {
                    "threshold": 2.0,
                    "font_size": 8,
                    "font_color": "white",
                    "font_weight": "bold",
                },
                "zones": {
                    "breakeven_line_color": theme.body_text,
                    "breakeven_line_style": "solid",
                    "breakeven_line_width": 1,
                    "breakeven_opacity": 0.5,
                    "breakeven_label_font_size": 8,
                    "breakeven_label_color": theme.body_text,
                    "breakeven_label_bg": theme.background,
                    "breakeven_label_border": theme.borders,
                },
            }

        if chart_type == "scatter":
            return {
                "markers": {
                    "base_size": 15,
                    "magnitude_scaling": 20,
                    "outlier_boost": 5,
                    "base_alpha": 0.8,
                    "medium_density_alpha": 0.6,
                    "border_color": theme.borders,
                    "border_width": 0.8,
                },
                "quality_alphas": {
                    "Excellent": 0.9,
                    "Good": 0.8,
                    "Poor": 0.6,
                    "Failed": 0.5,
                    "Poor Setup": 0.4,
                },
                "trend_line": {
                    "color": self.theme_manager.color_palette.tertiary_data,
                    "width": 2,
                    "style": "dash",
                    "opacity": 0.7,
                },
                "labels": {
                    "outlier_threshold": 5.0,
                    "extreme_duration_min": 3,
                    "extreme_duration_max": 45,
                    "large_bubble_threshold": 30,
                    "max_labels": 10,
                    "font_size": 9,
                    "font_color": theme.primary_text,
                    "bg_color": theme.card_backgrounds,
                    "border_color": theme.borders,
                    "border_width": 0.5,
                    "opacity": 0.8,
                    "offset_x": 2.0,
                    "offset_y": 0.5,
                },
                "zero_line": {
                    "color": theme.body_text,
                    "style": "solid",
                    "width": 1,
                    "opacity": 0.3,
                },
            }

        if chart_type == "clustering":
            return {
                "centroids": {
                    "base_size": 25,
                    "size_scaling": 2,
                    "opacity": 0.7,
                    "border_color": theme.borders,
                    "border_width": 2,
                    "text_color": "white",
                    "text_size": 8,
                },
                "noise_points": {
                    "size": 8,
                    "opacity": 0.6,
                    "border_color": theme.borders,
                    "border_width": 0.5,
                },
                "statistics": {
                    "font_size": 8,
                    "font_color": theme.primary_text,
                    "bg_color": theme.card_backgrounds,
                    "border_color": theme.borders,
                    "border_width": 1,
                    "opacity": 0.8,
                    "position": {"x": 0.02, "y": 0.98},
                },
            }

        if chart_type == "performance_bands":
            return {
                "bars": {
                    "opacity": 0.8,
                    "border_color": theme.borders,
                    "border_width": 1,
                    "text_position": "outside",
                    "text_font_size": 10,
                    "text_font_color": theme.primary_text,
                    "text_font_weight": "bold",
                },
                "colors": {
                    "winner_bands": performance_colors["positive"],
                    "loser_bands": performance_colors["negative"],
                    "neutral_bands": theme.borders,
                },
                "layout": {
                    "category_order": "total ascending",  # Best performers at top
                    "grid_color": theme.borders,
                    "grid_width": 0.5,
                },
            }

        return {}

    def get_scalability_styling(self, volume_category: str, mode: str = "light") -> dict[str, Any]:
        """
        Get styling configuration based on data volume for scalability optimization.

        Args:
            volume_category: 'small', 'medium', 'large'
            mode: 'light' or 'dark'

        Returns:
            Scalability-optimized styling configuration
        """
        theme = self.theme_manager.get_theme_colors(mode)

        base_config = {
            "small": {
                "opacity": 0.8,
                "detail_level": "high",
                "label_frequency": 1,
                "marker_size_multiplier": 1.0,
                "show_individual_labels": True,
                "show_annotations": True,
            },
            "medium": {
                "opacity": 0.6,
                "detail_level": "medium",
                "label_frequency": 2,
                "marker_size_multiplier": 0.8,
                "show_individual_labels": True,
                "show_annotations": False,
            },
            "large": {
                "opacity": 0.5,
                "detail_level": "low",
                "label_frequency": 5,
                "marker_size_multiplier": 0.6,
                "show_individual_labels": False,
                "show_annotations": False,
                "use_clustering": True,
                "use_performance_bands": True,
            },
        }

        return base_config.get(volume_category, base_config["medium"])

    def apply_advanced_styling(self, fig: go.Figure, chart_type: str, mode: str = "light", **kwargs):
        """
        Apply advanced styling to a Plotly figure based on chart type.

        Args:
            fig: Plotly figure object
            chart_type: Type of chart
            mode: 'light' or 'dark'
            **kwargs: Additional styling parameters
        """
        # Get base theme configuration
        self.apply_theme_to_figure(fig, mode, kwargs.get("title", ""))

        # Apply chart-specific advanced styling
        styling_config = self.get_advanced_styling_config(chart_type, mode)

        # Update figure based on styling configuration
        if chart_type == "scatter":
            # Apply scatter-specific styling optimizations
            fig.update_traces(marker=dict(opacity=styling_config.get("markers", {}).get("base_alpha", 0.8)))
        elif chart_type == "waterfall":
            # Apply waterfall-specific styling optimizations
            fig.update_traces(opacity=styling_config.get("bars", {}).get("opacity", 0.8))

        # Apply responsive layout adjustments
        fig.update_layout(autosize=True)

    def get_font_configuration(self, mode: str = "light") -> dict[str, Any]:
        """
        Get comprehensive font configuration for Plotly with Heebo integration.

        Args:
            mode: Theme mode ('light' or 'dark')

        Returns:
            Font configuration dictionary
        """
        # Get font list from theme manager
        fonts = self.theme_manager._get_font_list() if self.theme_manager else ["sans-serif"]

        # Heebo font stack with fallbacks
        heebo_stack = [
            "Heebo",
            "-apple-system",
            "BlinkMacSystemFont",
            "Segoe UI",
            "Helvetica Neue",
            "Arial",
            "DejaVu Sans",
            "Liberation Sans",
            "sans-serif",
        ]

        # Combine Heebo with existing fonts, removing duplicates
        combined_fonts = []
        for font in heebo_stack:
            if font not in combined_fonts:
                combined_fonts.append(font)

        # Add any additional fonts from theme manager
        for font in fonts:
            if font not in combined_fonts:
                combined_fonts.append(font)

        theme = self.theme_manager.get_theme_colors(mode) if self.theme_manager else None

        return {
            "family": ", ".join(combined_fonts),
            "sizes": {
                "title": 20,
                "subtitle": 16,
                "axis_title": 12,
                "axis_labels": 10,
                "legend": 11,
                "annotation": 9,
                "body": 12,
            },
            "colors": {
                "primary": theme.primary_text if theme else "#121212",
                "secondary": theme.body_text if theme else "#444444",
                "muted": theme.borders if theme else "#666666",
            },
            "weights": {"normal": "normal", "medium": "500", "bold": "bold"},
        }

    def apply_font_configuration(self, fig: go.Figure, mode: str = "light") -> go.Figure:
        """
        Apply comprehensive font configuration to Plotly figure.

        Args:
            fig: Plotly figure
            mode: Theme mode

        Returns:
            Figure with enhanced font configuration
        """
        font_config = self.get_font_configuration(mode)

        # Apply global font settings
        fig.update_layout(
            font={
                "family": font_config["family"],
                "size": font_config["sizes"]["body"],
                "color": font_config["colors"]["primary"],
            },
            title_font={
                "family": font_config["family"],
                "size": font_config["sizes"]["title"],
                "color": font_config["colors"]["primary"],
            },
        )

        # Apply to all axes
        axis_config = {
            "title": {
                "font": {
                    "family": font_config["family"],
                    "size": font_config["sizes"]["axis_title"],
                    "color": font_config["colors"]["secondary"],
                }
            },
            "tickfont": {
                "family": font_config["family"],
                "size": font_config["sizes"]["axis_labels"],
                "color": font_config["colors"]["secondary"],
            },
        }

        fig.update_xaxes(**axis_config)
        fig.update_yaxes(**axis_config)

        return fig

    def create_multi_format_exporter(self) -> "MultiFormatExporter":
        """
        Create multi-format exporter with comprehensive format support.

        Returns:
            MultiFormatExporter instance
        """
        return MultiFormatExporter(self)


class MultiFormatExporter:
    """Enhanced export system supporting multiple formats with optimized settings."""

    def __init__(self, theme_mapper: PlotlyThemeMapper):
        """
        Initialize multi-format exporter.

        Args:
            theme_mapper: PlotlyThemeMapper instance for styling
        """
        self.theme_mapper = theme_mapper

    def export_chart(
        self,
        fig: go.Figure,
        filepath: str,
        formats: list[str] = None,
        high_dpi: bool = True,
        mode: str = "light",
    ) -> dict[str, str]:
        """
        Export chart in multiple formats with optimized settings.

        Args:
            fig: Plotly figure to export
            filepath: Base filepath (without extension)
            formats: List of formats ('png', 'pdf', 'svg', 'html', 'webp')
            high_dpi: Whether to use high-DPI settings
            mode: Theme mode

        Returns:
            Dictionary mapping format to exported filepath
        """
        if formats is None:
            formats = ["png", "pdf", "svg"]

        # Apply font configuration
        fig = self.theme_mapper.apply_font_configuration(fig, mode)

        # Apply appropriate template
        fig = self.theme_mapper.apply_template(fig, mode, high_dpi=high_dpi)

        exported_files = {}

        for format_type in formats:
            output_path = f"{filepath}.{format_type}"

            try:
                if format_type.lower() == "png":
                    self._export_png(fig, output_path, high_dpi)
                elif format_type.lower() == "pdf":
                    self._export_pdf(fig, output_path, high_dpi)
                elif format_type.lower() == "svg":
                    self._export_svg(fig, output_path)
                elif format_type.lower() == "html":
                    self._export_html(fig, output_path)
                elif format_type.lower() == "webp":
                    self._export_webp(fig, output_path, high_dpi)
                else:
                    # Generic export
                    fig.write_image(output_path, format=format_type)

                exported_files[format_type] = output_path

            except Exception as e:
                print(f"Warning: Failed to export {format_type}: {e}")

        return exported_files

    def _export_png(self, fig: go.Figure, filepath: str, high_dpi: bool):
        """Export PNG with optimized settings."""
        config = {
            "width": 1600,
            "height": 1200,
            "scale": 3 if high_dpi else 2,
            "format": "png",
        }
        fig.write_image(filepath, **config)

    def _export_pdf(self, fig: go.Figure, filepath: str, high_dpi: bool):
        """Export PDF with vector quality."""
        config = {"width": 1600, "height": 1200, "format": "pdf"}
        # PDF doesn't need scale factor as it's vector
        fig.write_image(filepath, **config)

    def _export_svg(self, fig: go.Figure, filepath: str):
        """Export SVG with vector graphics."""
        config = {"width": 1600, "height": 1200, "format": "svg"}
        fig.write_image(filepath, **config)

    def _export_html(self, fig: go.Figure, filepath: str):
        """Export interactive HTML."""
        config = {
            "include_plotlyjs": "cdn",
            "div_id": "plotly-chart",
            "config": {
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
            },
        }
        fig.write_html(filepath, **config)

    def _export_webp(self, fig: go.Figure, filepath: str, high_dpi: bool):
        """Export WebP with optimized compression."""
        config = {
            "width": 1600,
            "height": 1200,
            "scale": 2 if high_dpi else 1,
            "format": "webp",
        }
        fig.write_image(filepath, **config)

    def create_export_batch(
        self,
        figures: dict[str, go.Figure],
        output_dir: str,
        formats: list[str] = None,
        high_dpi: bool = True,
        mode: str = "light",
    ) -> dict[str, dict[str, str]]:
        """
        Export multiple figures in batch with consistent settings.

        Args:
            figures: Dictionary mapping figure names to Plotly figures
            output_dir: Output directory path
            formats: List of export formats
            high_dpi: Whether to use high-DPI settings
            mode: Theme mode

        Returns:
            Dictionary mapping figure names to exported file paths
        """
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        batch_results = {}

        for fig_name, fig in figures.items():
            filepath = str(output_path / fig_name)
            exported_files = self.export_chart(fig, filepath, formats, high_dpi, mode)
            batch_results[fig_name] = exported_files

        return batch_results
