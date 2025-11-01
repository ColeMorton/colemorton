# Dashboard Generation Guide

**Version**: 2.0 | **Last Updated**: 2024-08-14 | **Status**: Active
**Authority**: Product Team | **Audience**: Developers

## Overview

The Dashboard Generation system provides automated creation of high-quality performance overview visualizations for historical trading reports. The system generates professional dual-mode (light/dark) dashboard images that integrate seamlessly with Colemorton's design system.

## Features

- **Plotly-Powered**: Next-generation chart generation with interactive capabilities
- **Dual-Mode Support**: Automatic generation of both light and dark theme dashboards
- **Multi-Format Export**: PNG, PDF, SVG, and HTML export options
- **JSON Schema Integration**: Frontend-ready chart configurations for React components
- **Scalability**: Intelligent handling of datasets from 15 to 200+ trades with performance optimization
- **Brand Compliance**: Full integration with Colemorton design system and 5 Plotly templates
- **Production Optimized**: Template caching, data sampling, and batch processing
- **High Quality Output**: 300+ DPI exports with professional print quality

## Quick Start

### Basic Usage

```bash
# Generate both light and dark mode dashboards
python scripts/dashboard_generator.py \\
    --input data/outputs/trade_history/HISTORICAL_PERFORMANCE_REPORT_20250626.md \\
    --mode both

# Generate only light mode
python scripts/dashboard_generator.py \\
    --input data/outputs/trade_history/HISTORICAL_PERFORMANCE_REPORT_20250626.md \\
    --mode light

# Validate configuration without generating
python scripts/dashboard_generator.py \\
    --input data/outputs/trade_history/HISTORICAL_PERFORMANCE_REPORT_20250626.md \\
    --validate-only
```

### Makefile Integration

```bash
# Quick dashboard generation (development)
make quick-dashboard

# Validate dashboard configuration
make quick-dashboard-validate

# Generate dashboard as part of full pipeline
make full-pipeline-with-dashboard

# Clean dashboard outputs
make clean-dashboards
```

## Plotly Chart Engine

The dashboard system now uses **Plotly** as the default chart generation engine, offering enhanced capabilities over the previous matplotlib system:

### Chart Engine Options

```bash
# Use Plotly (default, recommended)
python scripts/dashboard_generator.py --chart-engine plotly

# Fallback to matplotlib if needed
python scripts/dashboard_generator.py --chart-engine matplotlib
```

### Multi-Format Export

```bash
# Export in multiple formats
python scripts/dashboard_generator.py \\
    --export-formats png,pdf,svg \\
    --high-dpi \\
    --scale 3

# Export for frontend integration
python scripts/dashboard_generator.py \\
    --export-frontend-config \\
    --export-json-schema
```

### Template Selection

```bash
# Use specific Plotly template
python scripts/dashboard_generator.py \\
    --template colemorton_light_hd \\  # High-DPI optimized
    --template colemorton_dashboard   # Dashboard optimized

# Enable production optimizations
python scripts/dashboard_generator.py \\
    --enable-caching \\
    --enable-sampling \\
    --batch-processing
```

## Command Line Interface

### dashboard_generator.py

```bash
python scripts/dashboard_generator.py [OPTIONS]

Required Arguments:
  --input FILE          Input historical performance markdown file

Optional Arguments:
  --config FILE         Path to YAML configuration file
                        (default: configs/dashboard_generation.yaml)
  --mode {light,dark,both}
                        Dashboard mode to generate (default: both)
  --output-dir DIR      Output directory override (default from config)
  --env {dev,staging,prod}
                        Environment configuration (default: dev)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level (default: INFO)
  --validate-only       Only validate configuration and input
  --quiet               Suppress non-essential output (useful for Make)
```

### generate_report_with_dashboard.py

```bash
python scripts/generate_report_with_dashboard.py [OPTIONS]

Required Arguments:
  --input FILE          Input data file for report generation

Optional Arguments:
  --report-config FILE  Report generation configuration
                        (default: configs/report_generation.yaml)
  --dashboard-config FILE
                        Dashboard generation configuration
                        (default: configs/dashboard_generation.yaml)
  --output-dir DIR      Output directory override
  --env {dev,staging,prod}
                        Environment configuration (default: dev)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level (default: INFO)
  --quiet               Suppress non-essential output
```

## Configuration

### Dashboard Configuration File

The dashboard system uses `configs/dashboard_generation.yaml` for configuration:

```yaml
# Design System Configuration
design_system:
  colors:
    primary_data: "#26c6da"      # Colemorton primary chart color
    secondary_data: "#7e57c2"    # Colemorton secondary chart color
    tertiary_data: "#3179f5"     # Colemorton tertiary chart color

# Output Configuration
output:
  directory: "data/outputs/dashboards"
  filename_template: "historical-performance-dashboard-{mode}-{date}.png"
  dpi: 300
  format: "png"

# Scalability Configuration
scalability:
  trade_volume_thresholds:
    small: 50      # ≤50 trades: individual trade waterfall
    medium: 100    # 51-100 trades: grouped performance bands
    large: 200     # 101-200 trades: statistical distribution

  monthly_timeline_thresholds:
    compact: 3     # 1-3 months: full month names
    medium: 8      # 4-8 months: month abbreviations
    condensed: 12  # 9-12 months: compact view

# Theme Configuration
theme:
  light:
    background: "#ffffff"
    primary_text: "#333333"
    body_text: "#666666"
  dark:
    background: "#1a1a1a"
    primary_text: "#ffffff"
    body_text: "#cccccc"
```

### Environment-Specific Configuration

The system supports environment-specific overrides:

- `dev`: Development settings with debug output
- `staging`: Staging environment with production-like settings
- `prod`: Production settings with optimized performance

## Makefile Targets

### Core Targets

```bash
# Generate dashboard from latest historical data
make generate-dashboard

# Generate both light and dark mode dashboards
make generate-dashboard-light
make generate-dashboard-dark

# Integrated report and dashboard generation
make generate-report-integrated
make full-pipeline-with-dashboard
```

### Development Targets

```bash
# Quick dashboard generation with latest data
make quick-dashboard

# Validate configuration only
make quick-dashboard-validate

# Environment-specific pipelines
make dev-pipeline-dashboard
make staging-pipeline-dashboard
make prod-pipeline-dashboard
```

### Utility Targets

```bash
# Clean dashboard outputs
make clean-dashboards

# Setup directories
make setup-dirs

# Validate all configurations
make validate-configs
```

## Scalability Features

The dashboard system automatically adapts visualization techniques based on dataset characteristics:

### Trade Volume Adaptation

- **Small Datasets (≤50 trades)**: Individual trade waterfall charts
- **Medium Datasets (51-100 trades)**: Performance bands with grouped analysis
- **Large Datasets (101-200+ trades)**: Statistical distribution visualization

### Timeline Compression

- **Compact (1-3 months)**: Full month names ("January 2024")
- **Medium (4-8 months)**: Month abbreviations ("Jan '24")
- **Condensed (9-12 months)**: Single letter format ("J24")

### Density Management

- **Low Density (≤50 trades)**: Standard scatter plots with full opacity
- **Medium Density (51-150 trades)**: Reduced opacity for clarity
- **High Density (151-200+ trades)**: DBSCAN clustering with centroids

## Output Structure

Generated dashboards follow a consistent structure:

```
data/outputs/dashboards/
├── historical-performance-dashboard-light-20250626.png
├── historical-performance-dashboard-dark-20250626.png
└── logs/
    └── dashboard_generation_20250626.log
```

### Dashboard Components

Each dashboard includes:

1. **Key Metrics Row**: Win rate, total return, profit factor, total trades
2. **Monthly Performance**: Bar chart with win rates and returns
3. **Trade Quality Analysis**: Donut chart with quality distribution
4. **Performance Waterfall**: Individual trade performance visualization
5. **Duration vs Return**: Scatter plot with trend analysis

## Integration Examples

### Standalone Dashboard Generation

```bash
#!/bin/bash
# Generate dashboard for specific report
python scripts/dashboard_generator.py \\
    --input "data/outputs/trade_history/HISTORICAL_PERFORMANCE_REPORT_20250626.md" \\
    --mode both \\
    --env prod \\
    --output-dir "custom/output/path"
```

### Batch Processing

```bash
#!/bin/bash
# Generate dashboards for all historical reports
for report in data/outputs/trade_history/HISTORICAL_*.md; do
    echo "Processing $report..."
    python scripts/dashboard_generator.py \\
        --input "$report" \\
        --mode both \\
        --quiet
done
```

### Pipeline Integration

```yaml
# GitHub Actions example
- name: Generate Performance Dashboards
  run: |
    make setup-dirs
    make generate-report-integrated ENV=prod
    ls -la data/outputs/dashboards/
```

## Troubleshooting

### Common Issues

1. **Font Not Found Warnings**
   ```
   findfont: Font family 'Heebo' not found.
   ```
   **Solution**: This is expected behavior. The system uses intelligent font fallbacks.

2. **Configuration Validation Errors**
   ```bash
   # Validate configuration
   make validate-configs

   # Test specific configuration
   python scripts/dashboard_generator.py --validate-only --input test_file.md
   ```

3. **Input File Not Found**
   ```bash
   # Check available files
   ls -la data/outputs/trade_history/

   # Use most recent file
   make quick-dashboard
   ```

4. **Permission Errors**
   ```bash
   # Ensure output directory exists and is writable
   make setup-dirs
   chmod 755 data/outputs/dashboards/
   ```

### Debug Mode

```bash
# Run with debug output
python scripts/dashboard_generator.py \\
    --input your_file.md \\
    --log-level DEBUG

# Check logs
tail -f data/outputs/logs/dashboard_generation_*.log
```

## Performance Considerations

### Memory Usage

- Small datasets (≤50 trades): ~50MB peak memory
- Medium datasets (51-100 trades): ~100MB peak memory
- Large datasets (101-200+ trades): ~200MB peak memory

### Generation Time

- Small datasets: ~5-10 seconds
- Medium datasets: ~10-20 seconds
- Large datasets: ~20-30 seconds

### Optimization Tips

1. Use `--quiet` flag for batch processing
2. Use `--validate-only` for configuration testing
3. Consider using `--mode light` or `--mode dark` for single-mode generation
4. Clean output directories regularly with `make clean-dashboards`

## Advanced Usage

### Custom Configuration

```yaml
# Create custom configuration file
cp configs/dashboard_generation.yaml configs/custom_dashboard.yaml

# Edit configuration
vim configs/custom_dashboard.yaml

# Use custom configuration
python scripts/dashboard_generator.py \\
    --config configs/custom_dashboard.yaml \\
    --input your_file.md
```

### Output Format Customization

```yaml
# In configuration file
output:
  dpi: 600          # Higher resolution
  format: "svg"     # Vector format
  filename_template: "custom-dashboard-{mode}-{timestamp}.{format}"
```

### Frontend Integration

The Plotly-powered system now supports frontend integration through JSON schemas and chart configurations:

```bash
# Export chart configurations for React components
python scripts/dashboard_generator.py \\
    --export-frontend-config \\
    --output-config-dir data/outputs/frontend_configs

# Export JSON schemas for TypeScript definitions
python scripts/dashboard_generator.py \\
    --export-json-schema \\
    --schema-output-dir data/outputs/schemas
```

#### Frontend Configuration Files

Generated configuration files can be used directly in React components:

```javascript
// Example usage in React
import monthlyBarsConfig from './configs/monthly_bars_config.json';

function DashboardChart() {
  return (
    <PlotlyChart
      chartType={monthlyBarsConfig.chart_type}
      data={monthlyBarsConfig.data}
      theme={monthlyBarsConfig.theme}
      layout={monthlyBarsConfig.layout}
    />
  );
}
```

### Environment Variables

```bash
# Set environment variables
export DASHBOARD_CONFIG="configs/production_dashboard.yaml"
export DASHBOARD_OUTPUT_DIR="/custom/output/path"
export DASHBOARD_LOG_LEVEL="INFO"

# Use in scripts
python scripts/dashboard_generator.py \\
    --config "${DASHBOARD_CONFIG}" \\
    --output-dir "${DASHBOARD_OUTPUT_DIR}" \\
    --log-level "${DASHBOARD_LOG_LEVEL}" \\
    --input your_file.md
```

## API Reference

### Python API

```python
from scripts.dashboard_generator import DashboardGenerator, main
from scripts.utils.config_loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
config = config_loader.load_with_environment("configs/dashboard_generation.yaml", "prod")

# Generate dashboard
generator = DashboardGenerator(config)
output_file = generator.generate_dashboard(input_file, mode="light")

# Or use the main function
generated_files = main(config, input_file, mode="both", output_dir="/custom/path")
```

### Configuration API

```python
from scripts.utils.theme_manager import create_theme_manager
from scripts.utils.scalability_manager import create_scalability_manager

# Create managers
theme_manager = create_theme_manager()
scalability_manager = create_scalability_manager(config)

# Check scalability category
trade_category = scalability_manager.detect_trade_volume_category(trades)
recommendations = scalability_manager.get_chart_recommendation(trades, monthly_data)
```

## Support

For issues and questions:

1. Check this documentation
2. Review configuration files in `configs/`
3. Check log files in `data/outputs/logs/`
4. Run validation with `--validate-only`
5. Use debug mode with `--log-level DEBUG`
