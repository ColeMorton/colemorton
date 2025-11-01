#!/usr/bin/env python3
"""
Logo Generation Helper Script

This script generates high-quality brand logo images using the photo booth system
with multiple formats, resolutions, and themes.

Usage:
    python3 scripts/generate_logos.py [options]

Options:
    --all           Generate all logo variants (default)
    --formats       Specify formats: png, svg, both (default: both)
    --sizes         Specify DPI: 150, 300, 600, all (default: all)
    --themes        Specify themes: light, dark, both (default: both)
    --base-url      Base URL for development server (default: http://localhost:4321)
    --output-dir    Output directory for generated logos (default: data/outputs/logos)

Examples:
    # Generate all variants (recommended)
    python3 scripts/generate_logos.py

    # Generate only PNG files at 300 DPI
    python3 scripts/generate_logos.py --formats png --sizes 300

    # Generate dark theme only
    python3 scripts/generate_logos.py --themes dark
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_setup import setup_logging


class LogoGenerator:
    """Helper class for generating brand logos in multiple formats."""

    def __init__(
        self,
        base_url: str = "http://localhost:4321",
        output_dir: str = "data/outputs/logos",
    ):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Standard logo generation configurations for both brands
        base_configurations = [
            # Web optimized versions
            {
                "mode": "light",
                "format": "png",
                "dpi": 150,
                "scale": 2,
                "aspect": "16:9",
                "use_case": "web_light",
            },
            {
                "mode": "dark",
                "format": "png",
                "dpi": 150,
                "scale": 2,
                "aspect": "16:9",
                "use_case": "web_dark",
            },
            # Print quality versions
            {
                "mode": "light",
                "format": "png",
                "dpi": 300,
                "scale": 3,
                "aspect": "16:9",
                "use_case": "print_light",
            },
            {
                "mode": "dark",
                "format": "png",
                "dpi": 300,
                "scale": 3,
                "aspect": "16:9",
                "use_case": "print_dark",
            },
            # Ultra high quality versions
            {
                "mode": "light",
                "format": "png",
                "dpi": 600,
                "scale": 4,
                "aspect": "16:9",
                "use_case": "ultra_light",
            },
            {
                "mode": "dark",
                "format": "png",
                "dpi": 600,
                "scale": 4,
                "aspect": "16:9",
                "use_case": "ultra_dark",
            },
            # SVG versions (scalable)
            {
                "mode": "light",
                "format": "svg",
                "dpi": 300,
                "scale": 3,
                "aspect": "16:9",
                "use_case": "vector_light",
            },
            {
                "mode": "dark",
                "format": "svg",
                "dpi": 300,
                "scale": 3,
                "aspect": "16:9",
                "use_case": "vector_dark",
            },
            # Portrait versions for social media
            {
                "mode": "light",
                "format": "png",
                "dpi": 300,
                "scale": 3,
                "aspect": "3:4",
                "use_case": "portrait_light",
            },
            {
                "mode": "dark",
                "format": "png",
                "dpi": 300,
                "scale": 3,
                "aspect": "3:4",
                "use_case": "portrait_dark",
            },
        ]

        # Generate configurations for both brands
        self.configurations = []
        for brand in ["personal", "attribution"]:
            for config in base_configurations:
                brand_config = config.copy()
                brand_config["brand"] = brand
                brand_config["use_case"] = f"{brand}_{config['use_case']}"
                self.configurations.append(brand_config)

    def filter_configurations(
        self,
        formats: str | list[str] = "both",
        sizes: str | list[str] = "all",
        themes: str | list[str] = "both",
        brands: str | list[str] = "both",
    ) -> list[dict]:
        """Filter configurations based on user preferences."""
        configs = self.configurations.copy()

        # Filter by format
        if formats != "all":
            if isinstance(formats, str):
                if formats == "both":
                    format_list = ["png", "svg"]
                else:
                    format_list = [formats]
            else:
                format_list = formats
            configs = [c for c in configs if c["format"] in format_list]

        # Filter by DPI/size
        if sizes != "all":
            if isinstance(sizes, str):
                if sizes == "all":
                    dpi_list = [150, 300, 600]
                else:
                    dpi_list = [int(sizes)]
            else:
                dpi_list = [int(s) for s in sizes]
            configs = [c for c in configs if c["dpi"] in dpi_list]

        # Filter by theme
        if themes != "both":
            if isinstance(themes, str):
                if themes == "both":
                    theme_list = ["light", "dark"]
                else:
                    theme_list = [themes]
            else:
                theme_list = themes
            configs = [c for c in configs if c["mode"] in theme_list]

        # Filter by brand
        if brands != "both":
            if isinstance(brands, str):
                if brands == "both":
                    brand_list = ["personal", "attribution"]
                else:
                    brand_list = [brands]
            else:
                brand_list = brands
            configs = [c for c in configs if c["brand"] in brand_list]

        return configs

    def generate_logo(self, config: dict) -> bool:
        """Generate a single logo with the given configuration."""
        cmd = [
            "python3",
            str(project_root / "scripts" / "photo_booth_generator.py"),
            "--dashboard",
            "logo_generation",
            "--mode",
            config["mode"],
            "--aspect-ratio",
            config["aspect"],
            "--format",
            config["format"],
            "--dpi",
            str(config["dpi"]),
            "--scale-factor",
            str(config["scale"]),
            "--brand",
            config["brand"],
            "--base-url",
            self.base_url,
        ]

        self.logger.info(
            f"🎨 Generating {config['use_case']} logo ({config['brand']}, {config['format']}, {config['dpi']} DPI)"
        )

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"✅ Generated {config['use_case']} logo successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to generate {config['use_case']} logo: {e.stderr}")
            return False

    def generate_all_logos(self, formats="both", sizes="all", themes="both", brands="both") -> dict:
        """Generate all requested logo variants."""
        configs = self.filter_configurations(formats, sizes, themes, brands)
        results = {"success": [], "failed": []}

        self.logger.info(f"🚀 Starting logo generation: {len(configs)} variants")

        for config in configs:
            if self.generate_logo(config):
                results["success"].append(config["use_case"])
            else:
                results["failed"].append(config["use_case"])

        # Summary
        self.logger.info(
            f"📊 Generation complete: {len(results['success'])} successful, {len(results['failed'])} failed"
        )

        if results["success"]:
            self.logger.info("✅ Successfully generated:")
            for use_case in results["success"]:
                self.logger.info(f"   • {use_case}")

        if results["failed"]:
            self.logger.error("❌ Failed to generate:")
            for use_case in results["failed"]:
                self.logger.error(f"   • {use_case}")

        return results

    def organize_outputs(self):
        """Organize generated logo files into a clean directory structure."""
        source_dir = project_root / "data" / "outputs" / "photo-booth"
        target_dir = self.output_dir

        if not source_dir.exists():
            self.logger.warning("No photo booth outputs found to organize")
            return

        # Find logo-related files
        logo_files = list(source_dir.glob("logo_generation_*"))

        if not logo_files:
            self.logger.warning("No logo generation files found")
            return

        self.logger.info(f"📁 Organizing {len(logo_files)} logo files")

        # Create organized structure
        for logo_file in logo_files:
            # Parse filename to determine organization
            filename = logo_file.name
            parts = filename.split("_")

            if len(parts) >= 7:  # Updated to handle brand parameter
                mode = parts[2]  # light/dark
                aspect = parts[3]  # 16:9, 3:4
                format_ext = parts[4]  # png, svg
                dpi = parts[5]  # 150dpi, 300dpi, 600dpi
                brand = parts[6] if len(parts) > 6 else "personal"  # personal/attribution

                # Create organized path with brand prefix
                if brand == "attribution":
                    brand_prefix = "colemorton_com"
                else:
                    brand_prefix = "cole_morton"

                organized_name = f"{brand_prefix}_logo_{mode}_{dpi}_{aspect.replace(':', 'x')}.{logo_file.suffix[1:]}"
                organized_path = target_dir / organized_name

                # Copy file
                shutil.copy2(logo_file, organized_path)
                self.logger.info(f"📄 Organized: {organized_name}")

        self.logger.info(f"✅ Logo files organized in {target_dir}")


def main():
    """Main function for command line interface."""
    parser = argparse.ArgumentParser(
        description="Generate brand logo images in multiple formats and resolutions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--formats",
        choices=["png", "svg", "both"],
        default="both",
        help="Image formats to generate (default: both)",
    )
    parser.add_argument(
        "--sizes",
        choices=["150", "300", "600", "all"],
        default="all",
        help="DPI resolutions to generate (default: all)",
    )
    parser.add_argument(
        "--themes",
        choices=["light", "dark", "both"],
        default="both",
        help="Theme variants to generate (default: both)",
    )
    parser.add_argument(
        "--brands",
        choices=["personal", "attribution", "both"],
        default="both",
        help="Brand variants to generate (default: both)",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:4321",
        help="Base URL for development server (default: http://localhost:4321)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/outputs/logos",
        help="Output directory for organized logos (default: data/outputs/logos)",
    )
    parser.add_argument(
        "--organize",
        action="store_true",
        help="Organize existing logo files without generating new ones",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    setup_logging(level="DEBUG" if args.verbose else "INFO")

    # Create generator
    generator = LogoGenerator(base_url=args.base_url, output_dir=args.output_dir)

    if args.organize:
        # Only organize existing files
        generator.organize_outputs()
    else:
        # Generate logos and then organize
        results = generator.generate_all_logos(
            formats=args.formats,
            sizes=args.sizes,
            themes=args.themes,
            brands=args.brands,
        )

        # Organize the outputs
        generator.organize_outputs()

        # Exit with appropriate code
        if results["failed"]:
            sys.exit(1)
        else:
            print("\n🎉 All logos generated successfully!")
            print(f"📂 Find your logos in: {generator.output_dir}")


if __name__ == "__main__":
    main()
