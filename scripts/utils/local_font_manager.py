#!/usr/bin/env python3
"""
Local font manager for Sensylate unified font system.

This module provides local font loading and management for Python/matplotlib
integration, using the same font files as the frontend for consistency.
"""

import logging
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt


class LocalFontManager:
    """Manages local font loading for Python/matplotlib integration."""

    def __init__(self, project_root: str | None = None):
        """
        Initialize local font manager.

        Args:
            project_root: Optional path to project root directory.
                         If None, will auto-detect based on current file location.
        """
        self.logger = logging.getLogger(__name__)
        self.project_root = self._get_project_root(project_root)
        self.fonts_dir = self.project_root / "fonts" / "heebo"
        self._font_paths: dict[str, Path] = {}
        self._fonts_loaded = False

    def _get_project_root(self, project_root: str | None) -> Path:
        """
        Get project root directory.

        Args:
            project_root: Optional explicit project root path

        Returns:
            Path object pointing to project root
        """
        if project_root:
            return Path(project_root).resolve()

        # Auto-detect project root from current file location
        current_file = Path(__file__).resolve()

        # Navigate up from scripts/utils/ to project root
        for parent in current_file.parents:
            if (parent / "fonts").exists() and (parent / "frontend").exists():
                return parent

        # Fallback: assume we're in scripts/utils/
        return current_file.parent.parent.parent

    def validate_font_directory(self) -> bool:
        """
        Validate that font directory and files exist.

        Returns:
            True if all required font files exist, False otherwise
        """
        if not self.fonts_dir.exists():
            self.logger.error(f"Font directory not found: {self.fonts_dir}")
            return False

        required_fonts = [
            "heebo-400.ttf",  # Regular
            "heebo-600.ttf",  # Semi-bold
            "heebo-700.ttf",  # Bold
            "heebo-800.ttf",  # Extra-bold
        ]

        missing_fonts = []
        for font_file in required_fonts:
            font_path = self.fonts_dir / font_file
            if not font_path.exists():
                missing_fonts.append(font_file)
            else:
                # Store font paths for later use
                weight = font_file.split("-")[1].split(".")[0]
                self._font_paths[weight] = font_path

        if missing_fonts:
            self.logger.error(f"Missing font files: {missing_fonts}")
            return False

        self.logger.info(f"All required Heebo font files found in {self.fonts_dir}")
        return True

    def load_fonts(self) -> bool:
        """
        Load local Heebo fonts into matplotlib font manager.

        Returns:
            True if fonts loaded successfully, False otherwise
        """
        if self._fonts_loaded:
            self.logger.debug("Fonts already loaded")
            return True

        if not self.validate_font_directory():
            return False

        try:
            loaded_count = 0

            for weight, font_path in self._font_paths.items():
                try:
                    # Add font to matplotlib font manager
                    fm.fontManager.addfont(str(font_path))
                    self.logger.debug(f"Loaded Heebo weight {weight} from {font_path}")
                    loaded_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to load font {font_path}: {e}")
                    continue

            if loaded_count > 0:
                # Refresh font manager to recognize new fonts safely
                # Note: Avoid direct __init__ access to maintain type safety
                plt.rcParams["font.family"] = ["Heebo", "sans-serif"]

                # Configure matplotlib to use Heebo as primary font
                self._configure_matplotlib_fonts()

                self._fonts_loaded = True
                self.logger.info(f"Successfully loaded {loaded_count} Heebo font weights")
                return True
            self.logger.error("No Heebo fonts could be loaded")
            return False

        except Exception as e:
            self.logger.error(f"Font loading failed: {e}")
            return False

    def _configure_matplotlib_fonts(self) -> None:
        """Configure matplotlib to use local Heebo fonts."""
        # Set font family list with Heebo as primary
        font_list = self.get_font_list()
        plt.rcParams["font.family"] = font_list

        self.logger.debug(f"Configured matplotlib font family: {font_list}")

    def get_font_list(self) -> list[str]:
        """
        Get prioritized font list with Heebo and system fallbacks.

        Returns:
            List of font families in priority order
        """
        return [
            "Heebo",
            "Helvetica Neue",
            "Arial",
            "DejaVu Sans",
            "Liberation Sans",
            "sans-serif",
        ]

    def is_heebo_available(self) -> bool:
        """
        Check if Heebo font is available in matplotlib.

        Returns:
            True if Heebo is available, False otherwise
        """
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        return "Heebo" in available_fonts

    def get_font_info(self) -> dict:
        """
        Get information about loaded fonts.

        Returns:
            Dictionary with font loading status and paths
        """
        return {
            "fonts_loaded": self._fonts_loaded,
            "heebo_available": self.is_heebo_available(),
            "fonts_directory": str(self.fonts_dir),
            "loaded_font_paths": {weight: str(path) for weight, path in self._font_paths.items()},
            "matplotlib_font_list": self.get_font_list(),
        }

    def initialize_for_plotting(self) -> bool:
        """
        Initialize fonts for plotting operations.

        This is the main method to call before creating plots.

        Returns:
            True if fonts are ready for plotting, False otherwise
        """
        success = self.load_fonts()

        if success:
            self.logger.info("Heebo fonts ready for plotting")
        else:
            self.logger.warning("Using system fonts as fallback")
            # Configure fallback fonts
            plt.rcParams["font.family"] = self.get_font_list()[1:]  # Skip Heebo

        return success


def create_font_manager(project_root: str | None = None) -> LocalFontManager:
    """
    Factory function to create a LocalFontManager instance.

    Args:
        project_root: Optional path to project root directory

    Returns:
        Configured LocalFontManager instance
    """
    return LocalFontManager(project_root)


def initialize_fonts(project_root: str | None = None) -> bool:
    """
    Convenience function to initialize fonts for plotting.

    Args:
        project_root: Optional path to project root directory

    Returns:
        True if fonts are ready, False if using fallback
    """
    font_manager = create_font_manager(project_root)
    return font_manager.initialize_for_plotting()


if __name__ == "__main__":
    # Test local font manager
    logging.basicConfig(level=logging.INFO)

    font_manager = create_font_manager()

    print("Font Manager Status:")
    print("Project root: {font_manager.project_root}")
    print("Fonts directory: {font_manager.fonts_dir}")
    print("Directory exists: {font_manager.fonts_dir.exists()}")
    print("Font validation: {font_manager.validate_font_directory()}")

    success = font_manager.initialize_for_plotting()
    print("Initialization success: {success}")

    info = font_manager.get_font_info()
    print("\nFont Info:")
    for key, value in info.items():
        print("  {key}: {value}")
