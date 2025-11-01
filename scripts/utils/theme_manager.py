#!/usr/bin/env python3
"""
Theme manager for Sensylate design system integration.

This module provides color palette and theme management for dashboard generation,
ensuring consistency with the Sensylate brand guidelines.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml


@dataclass
class ColorPalette:
    """Represents the Sensylate color palette."""

    # Primary chart colors
    primary_data: str = "#26c6da"  # Cyan
    secondary_data: str = "#7e57c2"  # Purple
    tertiary_data: str = "#3179f5"  # Blue

    def get_extended_palette(self) -> list:
        """Get the full extended color palette as a list."""
        return [
            self.primary_data,
            self.secondary_data,
            self.tertiary_data,
        ]


@dataclass
class ThemeColors:
    """Represents theme-specific colors (light/dark mode)."""

    background: str
    card_backgrounds: str
    primary_text: str
    body_text: str
    muted_text: str
    borders: str


@dataclass
class Typography:
    """Represents typography settings."""

    primary_family: str = "Heebo"
    regular_weight: int = 400
    semibold_weight: int = 600
    fallback: str = "sans-serif"


class ThemeManager:
    """Manages theme configuration and color palettes for dashboard generation."""

    def __init__(self, config_path: str | None = None):
        """
        Initialize theme manager.

        Args:
            config_path: Optional path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.config = self._load_config()

        # Initialize palettes
        self.color_palette = self._create_color_palette()
        self.light_theme = self._create_light_theme()
        self.dark_theme = self._create_dark_theme()
        self.typography = self._create_typography()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path:
            # Use default configuration
            return self._get_default_config()

        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return self._get_default_config()

            with open(config_file) as file:
                config_data: Any = yaml.safe_load(file)
                if config_data is not None and isinstance(config_data, dict):
                    return cast(dict[str, Any], config_data)
                return {}

        except Exception as e:
            self.logger.error(f"Failed to load config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default Sensylate theme configuration."""
        return {
            "design_system": {
                "colors": {
                    "primary_data": "#26c6da",
                    "secondary_data": "#7e57c2",
                    "tertiary_data": "#3179f5",
                },
                "light_mode": {
                    "background": "#fff",
                    "card_backgrounds": "#f6f6f6",
                    "primary_text": "#121212",
                    "body_text": "#444444",
                    "muted_text": "#717171",
                    "borders": "#eaeaea",
                },
                "dark_mode": {
                    "background": "#202124",
                    "card_backgrounds": "#222222",
                    "primary_text": "#fff",
                    "body_text": "#B4AFB6",
                    "muted_text": "#B4AFB6",
                    "borders": "#3E3E3E",
                },
                "fonts": {
                    "primary_family": "Heebo",
                    "source": "local",
                    "base_path": "fonts/heebo",
                    "files": {
                        400: "heebo-400.ttf",
                        600: "heebo-600.ttf",
                        700: "heebo-700.ttf",
                        800: "heebo-800.ttf",
                    },
                    "weights": {
                        "regular": 400,
                        "semibold": 600,
                        "bold": 700,
                        "extrabold": 800,
                    },
                    "fallback": "sans-serif",
                },
            }
        }

    def _create_color_palette(self) -> ColorPalette:
        """Create color palette from configuration."""
        colors_config = self.config.get("design_system", {}).get("colors", {})

        return ColorPalette(
            primary_data=colors_config.get("primary_data", "#26c6da"),
            secondary_data=colors_config.get("secondary_data", "#7e57c2"),
            tertiary_data=colors_config.get("tertiary_data", "#3179f5"),
        )

    def _create_light_theme(self) -> ThemeColors:
        """Create light mode theme colors."""
        light_config = self.config.get("design_system", {}).get("light_mode", {})

        return ThemeColors(
            background=light_config.get("background", "#fff"),
            card_backgrounds=light_config.get("card_backgrounds", "#f6f6f6"),
            primary_text=light_config.get("primary_text", "#121212"),
            body_text=light_config.get("body_text", "#444444"),
            muted_text=light_config.get("muted_text", "#717171"),
            borders=light_config.get("borders", "#eaeaea"),
        )

    def _create_dark_theme(self) -> ThemeColors:
        """Create dark mode theme colors."""
        dark_config = self.config.get("design_system", {}).get("dark_mode", {})

        return ThemeColors(
            background=dark_config.get("background", "#202124"),
            card_backgrounds=dark_config.get("card_backgrounds", "#222222"),
            primary_text=dark_config.get("primary_text", "#fff"),
            body_text=dark_config.get("body_text", "#B4AFB6"),
            muted_text=dark_config.get("muted_text", "#B4AFB6"),
            borders=dark_config.get("borders", "#3E3E3E"),
        )

    def _create_typography(self) -> Typography:
        """Create typography configuration."""
        fonts_config = self.config.get("design_system", {}).get("fonts", {})
        weights = fonts_config.get("weights", {})

        return Typography(
            primary_family=fonts_config.get("primary_family", "Heebo"),
            regular_weight=weights.get("regular", 400),
            semibold_weight=weights.get("semibold", 600),
            fallback=fonts_config.get("fallback", "sans-serif"),
        )

    def get_theme_colors(self, mode: str = "light") -> ThemeColors:
        """
        Get theme colors for specified mode.

        Args:
            mode: 'light' or 'dark'

        Returns:
            ThemeColors object for the specified mode
        """
        if mode.lower() == "dark":
            return self.dark_theme
        return self.light_theme

    def get_quality_colors(self) -> dict[str, str]:
        """
        Get color mapping for trade quality categories.

        Returns:
            Dictionary mapping quality categories to colors
        """
        return {
            "Excellent": self.color_palette.primary_data,  # Cyan
            "Good": self.color_palette.tertiary_data,  # Blue
            "Poor": self.color_palette.secondary_data,  # Purple
        }

    def get_performance_colors(self) -> dict[str, str]:
        """
        Get color mapping for performance indicators.

        Returns:
            Dictionary mapping performance types to colors
        """
        return {
            "positive": self.color_palette.primary_data,  # Cyan for gains
            "negative": self.color_palette.secondary_data,  # Purple for losses
            "neutral": self.color_palette.tertiary_data,  # Blue for neutral
        }

    def get_monthly_colors(self) -> list:
        """
        Get colors for monthly performance charts.

        Returns:
            List of colors for monthly data series
        """
        return [
            self.color_palette.secondary_data,  # Purple
            self.color_palette.primary_data,  # Cyan
            self.color_palette.tertiary_data,  # Blue
        ]

    def get_matplotlib_style(self, mode: str = "light") -> dict[str, Any]:
        """
        Get matplotlib style configuration for the specified mode.

        Args:
            mode: 'light' or 'dark'

        Returns:
            Dictionary of matplotlib style parameters
        """
        theme = self.get_theme_colors(mode)

        return {
            "figure.facecolor": theme.background,
            "axes.facecolor": theme.background,
            "axes.edgecolor": theme.borders,
            "axes.labelcolor": theme.body_text,
            "text.color": theme.body_text,
            "xtick.color": theme.body_text,
            "ytick.color": theme.body_text,
            "grid.color": theme.borders,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": True,
            "axes.spines.bottom": True,
            "axes.grid": True,
            "font.family": self._get_font_list(),
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 9,
            "figure.titlesize": 14,
        }

    def validate_colors(self) -> bool:
        """
        Validate that all required colors are properly defined.

        Returns:
            True if all colors are valid, False otherwise
        """
        try:
            # Check primary colors
            colors_to_check = [
                self.color_palette.primary_data,
                self.color_palette.secondary_data,
                self.color_palette.tertiary_data,
            ]

            # Check extended palette
            colors_to_check.extend(self.color_palette.get_extended_palette())

            # Check theme colors
            for theme in [self.light_theme, self.dark_theme]:
                colors_to_check.extend(
                    [
                        theme.background,
                        theme.primary_text,
                        theme.body_text,
                        theme.borders,
                    ]
                )

            # Validate hex color format
            for color in colors_to_check:
                if not color.startswith("#"):
                    self.logger.error(f"Invalid color format: {color}")
                    return False

                # Accept both #RGB and #RRGGBB formats
                hex_part = color[1:]
                if len(hex_part) not in [3, 6]:
                    self.logger.error(f"Invalid color format: {color}")
                    return False

                # Check if it's a valid hex color
                int(hex_part, 16)

            return True

        except Exception as e:
            self.logger.error(f"Color validation failed: {e}")
            return False

    def _get_font_list(self) -> list[str]:
        """
        Get prioritized font list with fallbacks.

        Returns:
            List of font families in priority order
        """
        fonts = [self.typography.primary_family]

        # Add common system fallbacks
        if self.typography.primary_family.lower() == "heebo":
            fonts.extend(
                [
                    "Helvetica Neue",
                    "Arial",
                    "DejaVu Sans",
                    "Liberation Sans",
                    "sans-serif",
                ]
            )
        else:
            fonts.append(self.typography.fallback)

        return fonts

    def configure_font_fallbacks(self) -> None:
        """Configure fonts using local font manager."""
        from .local_font_manager import initialize_fonts

        success = initialize_fonts()

        if success:
            self.logger.info(f"Successfully configured local '{self.typography.primary_family}' fonts")
        else:
            self.logger.warning("Local fonts not available, using system fallbacks")

    def get_title_style(self, mode: str = "light") -> dict[str, Any]:
        """
        Get standardized title styling for all charts.

        Args:
            mode: 'light' or 'dark'

        Returns:
            Dictionary of title styling parameters
        """
        theme = self.get_theme_colors(mode)

        return {
            "fontsize": 18,  # Increased to 18 for maximum prominence
            "fontweight": "bold",
            "color": theme.primary_text,
            "pad": 45,  # Significantly increased padding to eliminate overlap
            "fontfamily": self._get_font_list(),
        }

    def apply_title_style(self, ax: object, title: str, mode: str = "light") -> None:
        """
        Apply standardized title styling to an axes object.

        Args:
            ax: Matplotlib axes object
            title: Title text
            mode: 'light' or 'dark'
        """
        style = self.get_title_style(mode)
        if hasattr(ax, "set_title"):
            ax.set_title(title, **style)


def create_theme_manager(config_path: str | None = None) -> ThemeManager:
    """
    Factory function to create a ThemeManager instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured ThemeManager instance
    """
    return ThemeManager(config_path)


if __name__ == "__main__":
    # Test theme manager
    theme_manager = create_theme_manager()

    print("Color Palette:")
    print("  Primary: {theme_manager.color_palette.primary_data}")
    print("  Secondary: {theme_manager.color_palette.secondary_data}")
    print("  Tertiary: {theme_manager.color_palette.tertiary_data}")

    print("\nLight Theme:")
    light = theme_manager.light_theme
    print("  Background: {light.background}")
    print("  Text: {light.primary_text}")

    print("\nDark Theme:")
    dark = theme_manager.dark_theme
    print("  Background: {dark.background}")
    print("  Text: {dark.primary_text}")

    print("\nColor validation: {theme_manager.validate_colors()}")
