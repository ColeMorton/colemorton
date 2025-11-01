#!/usr/bin/env python3
"""
Photo Booth Dashboard Screenshot Generator

This script generates high-resolution dashboard screenshots using Puppeteer
via Node.js subprocess calls for web-based dashboard rendering.
"""

import argparse
import json
import logging
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_setup import setup_logging


class PhotoBoothGenerator:
    """Main photo booth screenshot generation class."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize photo booth generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.get("base_url", "http://localhost:4321")
        output_dir_path = config.get("output", {}).get("directory", "data/outputs/photo-booth")
        if not Path(output_dir_path).is_absolute():
            self.output_dir = project_root / output_dir_path
        else:
            self.output_dir = Path(output_dir_path)
        self.screenshot_settings = config.get("screenshot_settings", {})

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_server_status(self) -> bool:
        """
        Check if the development server is running and accessible.

        Returns:
            bool: True if server is accessible, False otherwise
        """
        try:
            self.logger.info(f"Checking server status at {self.base_url}")

            # Try to access the photo booth page
            test_url = f"{self.base_url}/photo-booth"
            request = urllib.request.Request(test_url)

            with urllib.request.urlopen(request, timeout=5) as response:
                if response.status == 200:
                    self.logger.info("✅ Development server is running and accessible")
                    return True
                self.logger.error(f"❌ Server responded with status {response.status}")
                return False

        except urllib.error.URLError as e:
            if "Connection refused" in str(e):
                self.logger.error(f"❌ Connection refused to {self.base_url}")
                self.logger.error("🔧 SOLUTION: Start the development server first:")
                self.logger.error("   cd frontend && yarn dev")
                self.logger.error("   Wait for 'Local http://localhost:4321/' message")
                self.logger.error("   Then run this export script in a new terminal")
            else:
                self.logger.error(f"❌ Cannot connect to server: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error checking server: {e}")
            return False

    def generate_screenshot(
        self,
        dashboard_id: str,
        mode: str = "light",
        aspect_ratio: str = "16:9",
        export_format: str = "png",
        dpi: int = 300,
        scale_factor: int = 3,
        custom_config: dict[str, Any] | None = None,
        ticker: str | None = None,
        brand: str | None = None,
    ) -> Path | list[Path]:
        """
        Generate a single dashboard screenshot.

        Args:
            dashboard_id: ID of the dashboard to screenshot
            mode: Theme mode ('light' or 'dark')
            aspect_ratio: Aspect ratio ('16:9', '4:3', '3:4')
            export_format: Export format ('png', 'svg', 'both')
            dpi: DPI setting for PNG output (150, 300, 600)
            scale_factor: Scale factor for high-DPI (2, 3, 4)
            custom_config: Optional custom screenshot configuration

        Returns:
            Path to the generated screenshot (or list of paths for 'both' format)
        """
        self.logger.info(f"Generating {export_format} export: {dashboard_id} ({mode} mode, {aspect_ratio}, {dpi} DPI)")

        # Check if development server is running before attempting screenshot
        if not self.check_server_status():
            raise RuntimeError("Development server is not accessible. Please start the server first.")

        # Build URL with parameters
        url = f"{self.base_url}/photo-booth?dashboard={dashboard_id}&mode={mode}&aspect_ratio={aspect_ratio}"

        # Add ticker parameter for fundamental analysis dashboard
        if ticker and dashboard_id == "fundamental_analysis":
            url += f"&ticker={ticker}"

        # Get aspect ratio dimensions from config (use fundamental-specific dimensions if applicable)
        aspect_dimensions = self._get_aspect_ratio_dimensions(aspect_ratio, dashboard_id)

        # Generate output filename(s)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Support both new and legacy filename templates
        filename_template = self.config.get("output", {}).get(
            "filename_template",
            "{dashboard_id}_{mode}_{aspect_ratio}_{format}_{dpi}dpi_{timestamp}.{extension}",
        )

        output_paths = []
        formats_to_generate = ["png", "svg"] if export_format == "both" else [export_format]

        for fmt in formats_to_generate:
            extension = "svg" if fmt == "svg" else "png"
            filename = filename_template.format(
                dashboard_id=dashboard_id,
                mode=mode,
                aspect_ratio=aspect_ratio.replace(":", "x"),
                format=fmt,
                dpi=dpi,
                brand=brand or "personal",
                timestamp=timestamp,
                extension=extension,
            )
            output_paths.append(self.output_dir / filename)

        # Merge screenshot settings with aspect ratio dimensions
        settings = {**self.screenshot_settings}
        settings["viewport"] = aspect_dimensions
        settings["device_scale_factor"] = scale_factor
        if custom_config:
            settings.update(custom_config)

        generated_files = []

        try:
            for i, fmt in enumerate(formats_to_generate):
                output_path = output_paths[i]

                if fmt == "svg":
                    # Generate SVG using dedicated SVG exporter
                    result = self._generate_svg(url, str(output_path), aspect_dimensions)
                    if result:
                        generated_files.append(output_path)
                        self.logger.info(f"SVG saved to: {output_path}")

                elif fmt == "png":
                    # Generate PNG using Puppeteer + Sharp processing
                    temp_png_path = str(output_path).replace(".png", "_temp.png")

                    # Create Node.js script for Puppeteer
                    puppeteer_script = self._create_puppeteer_script(url, temp_png_path, settings)

                    # Execute Puppeteer script to get raw PNG
                    self._execute_puppeteer_script(puppeteer_script)

                    if Path(temp_png_path).exists():
                        # Process with Sharp.js for high-DPI and optimization
                        sharp_result = self._process_with_sharp(temp_png_path, str(output_path), dpi, scale_factor)

                        if sharp_result:
                            generated_files.append(output_path)
                            self.logger.info(f"High-DPI PNG saved to: {output_path}")

                            # Clean up temp file
                            Path(temp_png_path).unlink()
                        else:
                            raise RuntimeError(f"Sharp processing failed for {output_path}")
                    else:
                        raise RuntimeError(f"Puppeteer PNG generation failed: {temp_png_path} not created")

            if not generated_files:
                raise RuntimeError("No files were generated successfully")

            return generated_files[0] if len(generated_files) == 1 else generated_files

        except Exception as e:
            self.logger.error(f"Failed to generate export: {e}")
            raise

    def generate_all_dashboards(
        self,
        dashboards: list[str] | None = None,
        modes: list[str] | None = None,
        aspect_ratio: str = "16:9",
        export_format: str = "png",
        dpi: int = 300,
        scale_factor: int = 3,
        ticker: str | None = None,
    ) -> list[Path]:
        """
        Generate screenshots for multiple dashboards.

        Args:
            dashboards: List of dashboard IDs to generate (default: all active)
            modes: List of modes to generate (default: from config)
            aspect_ratio: Aspect ratio for export (default: 16:9)
            export_format: Export format (default: png)
            dpi: DPI setting for PNG output (default: 300)
            scale_factor: Scale factor for high-DPI (default: 3)

        Returns:
            List of generated screenshot paths
        """
        # Check if development server is running before attempting multiple screenshots
        if not self.check_server_status():
            raise RuntimeError("Development server is not accessible. Please start the server first.")

        # Load photo booth config
        photo_booth_config_path = project_root / "frontend/src/config/photo-booth.json"
        with open(photo_booth_config_path) as f:
            photo_booth_config = json.load(f)

        # Determine dashboards to generate
        if dashboards is None:
            active_dashboards = [d["id"] for d in photo_booth_config["active_dashboards"] if d["enabled"]]
        else:
            active_dashboards = dashboards

        # Determine modes to generate
        if modes is None:
            modes = photo_booth_config.get("output", {}).get("modes", ["light", "dark"])

        generated_files = []

        for dashboard_id in active_dashboards:
            for mode in modes:
                try:
                    result = self.generate_screenshot(
                        dashboard_id,
                        mode,
                        aspect_ratio=aspect_ratio,
                        export_format=export_format,
                        dpi=dpi,
                        scale_factor=scale_factor,
                        ticker=ticker,
                    )
                    # Handle both single file and multiple file results
                    if isinstance(result, list):
                        generated_files.extend(result)
                    else:
                        generated_files.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to generate {export_format} export for {dashboard_id} ({mode}): {e}")
                    continue

        self.logger.info(f"Generated {len(generated_files)} screenshots")
        return generated_files

    def _create_puppeteer_script(self, url: str, output_path: str, settings: dict[str, Any]) -> str:
        """Create Node.js Puppeteer script for screenshot generation."""
        viewport = settings.get("viewport", {"width": 1920, "height": 1080})
        device_scale_factor = settings.get("device_scale_factor", 2)
        timeout = settings.get("timeout", 30000)
        wait_for_selector = settings.get("wait_for_selector", ".photo-booth-ready")

        script = f"""
const puppeteer = require('puppeteer');

(async () => {{
  const browser = await puppeteer.launch({{
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  }});

  try {{
    const page = await browser.newPage();

    // Set viewport and device scale factor
    await page.setViewport({{
      width: {viewport["width"]},
      height: {viewport["height"]},
      deviceScaleFactor: {device_scale_factor}
    }});

    // Navigate to the page
    console.log('Navigating to:', '{url}');
    await page.goto('{url}', {{ waitUntil: 'networkidle0', timeout: {timeout} }});

    // Wait for dashboard to be ready
    console.log('Waiting for dashboard to be ready...');
    await page.waitForSelector('{wait_for_selector}', {{ timeout: {timeout} }});

    /* Wait for all charts to be fully loaded and rendered */
    console.log('Waiting for charts to load and render...');
    try {{
      /* Wait for all PlotlyChart containers to be present */
      await page.waitForFunction(() => {{
        const chartContainers = document.querySelectorAll('[data-testid="plotly-chart-container"]');
        if (chartContainers.length === 0) {{
          console.log('No chart containers found, continuing...');
          return true; /* No charts present, continue */
        }}

        let allChartsReady = true;
        let readyCount = 0;

        chartContainers.forEach((container, index) => {{
          const isLoaded = container.getAttribute('data-chart-loaded') === 'true';
          const isRendered = container.getAttribute('data-chart-rendered') === 'true';
          const isReady = isLoaded && isRendered;

          console.log(`Chart ${{index}}: loaded=${{isLoaded}}, rendered=${{isRendered}}, ready=${{isReady}}`);

          if (isReady) {{
            readyCount++;
          }} else {{
            allChartsReady = false;
          }}
        }});

        console.log(`Charts ready: ${{readyCount}}/${{chartContainers.length}}`);
        return allChartsReady;
      }}, {{ timeout: 15000 }});

      console.log('All charts are loaded and rendered!');

      /* Additional short wait to ensure visual stability */
      await new Promise(resolve => setTimeout(resolve, 1000));

    }} catch (error) {{
      console.warn('Chart loading timeout, continuing with screenshot:', error.message);
      /* Fallback: short wait if chart detection fails */
      await new Promise(resolve => setTimeout(resolve, 2000));
    }}

    // Hide UI elements for clean screenshot
    console.log('Hiding UI elements for clean screenshot...');
    await page.evaluate(() => {{
      // Hide photo booth controls
      const controls = document.querySelectorAll('.photo-booth-controls');
      controls.forEach(element => {{
        element.style.display = 'none';
        element.style.visibility = 'hidden';
      }});

      // Hide Astro dev toolbar
      const devToolbarSelectors = [
        'astro-dev-toolbar',
        '#dev-toolbar-root',
        '[data-astro-dev-toolbar]',
        '.astro-dev-toolbar',
        '#astro-dev-toolbar'
      ];

      let hiddenDevElements = 0;
      devToolbarSelectors.forEach(selector => {{
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {{
          element.style.display = 'none';
          element.style.visibility = 'hidden';
          hiddenDevElements++;
        }});
      }});

      console.log(`Hidden ${{controls.length}} control elements and ${{hiddenDevElements}} dev toolbar elements`);
    }});

    // Take screenshot
    console.log('Taking screenshot...');
    await page.screenshot({{
      path: '{output_path}',
      fullPage: {str(settings.get("full_page", True)).lower()},
      type: '{settings.get("format", "png")}',
      quality: {settings.get("quality", 95) if settings.get("format") == "jpeg" else "undefined"}
    }});

    console.log('Screenshot saved to:', '{output_path}');

  }} catch (error) {{
    console.error('Screenshot generation failed:', error);
    process.exit(1);
  }} finally {{
    await browser.close();
  }}
}})();
"""
        return script

    def _execute_puppeteer_script(self, script: str) -> None:
        """Execute the Puppeteer script using Node.js."""
        # Write script to temporary file in frontend directory for proper module resolution
        frontend_dir = project_root / "frontend"
        script_path = frontend_dir / f"puppeteer_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cjs"

        try:
            with open(script_path, "w") as f:
                f.write(script)

            # Execute with Node.js from frontend directory
            result = subprocess.run(
                ["node", str(script_path)],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"Puppeteer script failed: {result.stderr}")

            self.logger.debug(f"Puppeteer output: {result.stdout}")

        finally:
            # Clean up temporary script
            if script_path.exists():
                script_path.unlink()

    def _get_aspect_ratio_dimensions(self, aspect_ratio: str, dashboard_id: str = None) -> dict[str, int]:
        """Get viewport dimensions for the specified aspect ratio."""
        # Load export options from config
        export_options = self.config.get("export_options", {})
        aspect_ratios = export_options.get("aspect_ratios", {}).get("available", [])

        # Find matching aspect ratio
        for ar in aspect_ratios:
            if ar["id"] == aspect_ratio:
                # Use fundamental-specific dimensions for fundamental analysis dashboard
                if dashboard_id == "fundamental_analysis" and "fundamental_dimensions" in ar:
                    self.logger.info(
                        f"Using fundamental-specific dimensions for {dashboard_id}: {ar['fundamental_dimensions']}"
                    )
                    return ar["fundamental_dimensions"]
                return ar["dimensions"]

        # Default fallback to 16:9
        self.logger.warning(f"Aspect ratio {aspect_ratio} not found, using default 16:9")
        return {"width": 1920, "height": 1080}

    def _generate_svg(self, url: str, output_path: str, dimensions: dict[str, int]) -> bool:
        """Generate SVG using the SVG exporter utility."""
        try:
            # Execute SVG exporter
            frontend_dir = project_root / "frontend"
            svg_exporter_path = project_root / "scripts/utils/svg_exporter.js"

            result = subprocess.run(
                [
                    "node",
                    str(svg_exporter_path),
                    "export",
                    url,
                    output_path,
                    str(dimensions["width"]),
                    str(dimensions["height"]),
                ],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                self.logger.debug(f"SVG exporter output: {result.stdout}")
                return True
            self.logger.error(f"SVG exporter failed: {result.stderr}")
            return False

        except Exception as e:
            self.logger.error(f"SVG generation failed: {e}")
            return False

    def _process_with_sharp(self, input_path: str, output_path: str, dpi: int, scale_factor: int) -> bool:
        """Process PNG with Sharp.js for high-DPI and optimization."""
        try:
            # Execute Sharp processor
            frontend_dir = project_root / "frontend"
            sharp_processor_path = project_root / "scripts/utils/sharp_processor.js"

            result = subprocess.run(
                [
                    "node",
                    str(sharp_processor_path),
                    "process",
                    input_path,
                    output_path,
                    str(dpi),
                    "1",  # Scale factor is already applied in Puppeteer
                ],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                self.logger.debug(f"Sharp processor output: {result.stdout}")
                return True
            self.logger.error(f"Sharp processor failed: {result.stderr}")
            return False

        except Exception as e:
            self.logger.error(f"Sharp processing failed: {e}")
            return False

    def cleanup_old_screenshots(self) -> None:
        """Clean up old screenshots based on configuration."""
        cleanup_config = self.config.get("output", {}).get("auto_cleanup", {})

        if not cleanup_config.get("enabled", False):
            return

        keep_latest = cleanup_config.get("keep_latest", 5)
        older_than_days = cleanup_config.get("older_than_days", 30)

        # Implementation for cleanup logic
        # This is a placeholder - would implement file age checking and deletion
        self.logger.info(f"Cleanup: keeping latest {keep_latest}, removing files older than {older_than_days} days")


def load_config() -> dict[str, Any]:
    """Load configuration from photo-booth config file."""
    config_path = project_root / "frontend/src/config/photo-booth.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Photo booth config not found: {config_path}")

    with open(config_path) as f:
        return json.load(f)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard", help="Dashboard ID to generate (default: all active dashboards)")
    parser.add_argument(
        "--mode",
        choices=["light", "dark", "both"],
        default="both",
        help="Theme mode to generate",
    )
    parser.add_argument(
        "--aspect-ratio",
        choices=["16:9", "4:3", "3:4"],
        default="16:9",
        help="Aspect ratio for export",
    )
    parser.add_argument(
        "--format",
        choices=["png", "svg", "both"],
        default="png",
        help="Export format",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        choices=[150, 300, 600],
        default=300,
        help="DPI setting for PNG output",
    )
    parser.add_argument(
        "--scale-factor",
        type=int,
        choices=[2, 3, 4],
        default=3,
        help="Scale factor for high-DPI output",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:4321",
        help="Base URL for the Astro development server",
    )
    parser.add_argument("--output-dir", help="Output directory override (default from config)")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up old screenshots after generation",
    )
    parser.add_argument(
        "--ticker",
        help="Ticker symbol for fundamental analysis dashboard (e.g., GOOGL, NVDA, ASML)",
    )
    parser.add_argument(
        "--brand",
        choices=["personal", "attribution"],
        help="Brand variant for logo generation dashboard (personal: Cole Morton, attribution: colemorton.com)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    try:
        # Setup logging
        setup_logging(level=args.log_level)

        # Load configuration
        config = load_config()

        # Override base URL if provided
        config["base_url"] = args.base_url

        # Override output directory if provided
        if args.output_dir:
            config["output"]["directory"] = args.output_dir

        # Create generator
        generator = PhotoBoothGenerator(config)

        # Determine modes to generate
        modes = ["light", "dark"] if args.mode == "both" else [args.mode]

        # Generate screenshots
        if args.dashboard:
            generated_files = []
            for mode in modes:
                result = generator.generate_screenshot(
                    args.dashboard,
                    mode,
                    aspect_ratio=args.aspect_ratio,
                    export_format=args.format,
                    dpi=args.dpi,
                    scale_factor=args.scale_factor,
                    ticker=args.ticker,
                    brand=args.brand,
                )
                # Handle both single file and multiple file results
                if isinstance(result, list):
                    generated_files.extend(result)
                else:
                    generated_files.append(result)
        else:
            generated_files = generator.generate_all_dashboards(
                modes=modes,
                aspect_ratio=args.aspect_ratio,
                export_format=args.format,
                dpi=args.dpi,
                scale_factor=args.scale_factor,
                ticker=args.ticker,
            )

        # Cleanup if requested
        if args.cleanup:
            generator.cleanup_old_screenshots()

        # Print results
        print("✅ Generated {len(generated_files)} screenshot(s):")
        for path in generated_files:
            print("  - {path}")

    except Exception as e:
        logging.error(f"Photo booth generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
