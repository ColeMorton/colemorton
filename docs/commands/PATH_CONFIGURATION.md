# Path Configuration Reference

**Version**: 2.0 | **Last Updated**: 2024-08-14 | **Status**: Active
**Authority**: Platform Architecture | **Audience**: Command Developers

This document defines the standardized path variables used across all Claude commands in the Colemorton project.

## Base Path Variables

All commands use configurable base paths to ensure consistency and maintainability:

### Primary Base Paths

```yaml
SCRIPTS_BASE:
  default: "./scripts"
  description: "Root directory for all Python scripts"
  environment_variable: "COLEMORTON_SCRIPTS_BASE"
  examples:
    - "{SCRIPTS_BASE}/yahoo_finance_cli.py"
    - "{SCRIPTS_BASE}/base_scripts/fundamental_analysis_script.py"
    - "{SCRIPTS_BASE}/fundamental_analysis/fundamental_discovery.py"

DATA_OUTPUTS:
  default: "./data/outputs"
  description: "Root directory for all generated outputs"
  environment_variable: "COLEMORTON_DATA_OUTPUTS"
  examples:
    - "{DATA_OUTPUTS}/fundamental_analysis/AAPL_20250718.md"
    - "{DATA_OUTPUTS}/twitter/fundamental_analysis/TSLA_20250718.md"
    - "{DATA_OUTPUTS}/sector_analysis/technology_20250718.md"

TEMPLATES_BASE:
  default: "./scripts/templates"
  description: "Root directory for all Jinja2 templates"
  environment_variable: "COLEMORTON_TEMPLATES_BASE"
  examples:
    - "{TEMPLATES_BASE}/twitter/fundamental/twitter_fundamental_A_valuation.j2"
    - "{TEMPLATES_BASE}/shared/base_twitter.j2"
    - "{TEMPLATES_BASE}/validation/content_quality_checklist.j2"

DATA_IMAGES:
  default: "./data/images"
  description: "Root directory for all image data"
  environment_variable: "COLEMORTON_DATA_IMAGES"
  examples:
    - "{DATA_IMAGES}/trendspider_tabular/AAPL_20250718.png"
    - "{DATA_IMAGES}/tradingview/TSLA_20250718.png"
    - "{DATA_IMAGES}/charts/sector_performance_20250718.png"
```

### Configuration Paths

```yaml
CONFIG_BASE:
  default: "./config"
  description: "Configuration files and settings"
  environment_variable: "COLEMORTON_CONFIG_BASE"
  examples:
    - "{CONFIG_BASE}/financial_services.yaml"
    - "{CONFIG_BASE}/script_registry.json"
    - "{CONFIG_BASE}/validation_thresholds.yaml"

LOGS_BASE:
  default: "./logs"
  description: "Application logs and execution traces"
  environment_variable: "COLEMORTON_LOGS_BASE"
  examples:
    - "{LOGS_BASE}/twitter_system.log"
    - "{LOGS_BASE}/cli_services.log"
    - "{LOGS_BASE}/validation_results.log"
```

## Path Resolution Logic

### Environment Variable Priority

Path resolution follows this priority order:

1. **Environment Variable** (if set)
2. **Configuration File** (if specified in ScriptConfig)
3. **Default Relative Path** (fallback)

### Example Resolution

```python
# In ScriptConfig.from_environment()
import os
from pathlib import Path

def resolve_base_path(env_var: str, default: str) -> Path:
    """Resolve base path with environment variable override"""

    # 1. Check environment variable
    env_value = os.environ.get(env_var)
    if env_value:
        return Path(env_value)

    # 2. Use default relative path
    return Path(default)

# Usage
SCRIPTS_BASE = resolve_base_path("COLEMORTON_SCRIPTS_BASE", "./scripts")
DATA_OUTPUTS = resolve_base_path("COLEMORTON_DATA_OUTPUTS", "./data/outputs")
TEMPLATES_BASE = resolve_base_path("COLEMORTON_TEMPLATES_BASE", "./scripts/templates")
DATA_IMAGES = resolve_base_path("COLEMORTON_DATA_IMAGES", "./data/images")
```

## Directory Structure Examples

### Complete Project Structure

```
colemorton/
├── scripts/                           # {SCRIPTS_BASE}
│   ├── base_scripts/
│   │   ├── fundamental_analysis_script.py
│   │   ├── sector_analysis_script.py
│   │   └── trade_history_script.py
│   ├── fundamental_analysis/
│   │   ├── fundamental_discovery.py
│   │   ├── fundamental_analysis.py
│   │   ├── investment_synthesis.py
│   │   └── analysis_validation.py
│   ├── templates/                     # {TEMPLATES_BASE}
│   │   ├── twitter/
│   │   │   ├── fundamental/
│   │   │   ├── strategy/
│   │   │   ├── shared/
│   │   │   └── validation/
│   │   └── analysis/
│   ├── yahoo_finance_cli.py
│   ├── alpha_vantage_cli.py
│   └── content_automation_cli.py
├── data/
│   ├── outputs/                       # {DATA_OUTPUTS}
│   │   ├── fundamental_analysis/
│   │   │   ├── discovery/
│   │   │   ├── analysis/
│   │   │   └── validation/
│   │   ├── twitter/
│   │   │   ├── fundamental_analysis/
│   │   │   ├── post_strategy/
│   │   │   └── trade_history/
│   │   └── sector_analysis/
│   └── images/                        # {DATA_IMAGES}
│       ├── trendspider_tabular/
│       ├── trendspider_full/
│       └── tradingview/
├── config/                            # {CONFIG_BASE}
│   ├── financial_services.yaml
│   ├── script_registry.json
│   └── validation_thresholds.yaml
└── logs/                              # {LOGS_BASE}
    ├── twitter_system.log
    ├── cli_services.log
    └── validation_results.log
```

## Command Documentation Standards

### Path Reference Format

When documenting paths in commands, always use the standardized format:

```markdown
**Script Path**: `{SCRIPTS_BASE}/path/to/script.py`
**Template Path**: `{TEMPLATES_BASE}/category/template.j2`
**Output Path**: `{DATA_OUTPUTS}/category/{IDENTIFIER}_{DATE}.ext`
**Input Path**: `{DATA_IMAGES}/source/{IDENTIFIER}_{DATE}.ext`
```

### File Naming Conventions

```yaml
analysis_files:
  pattern: "{TICKER}_{YYYYMMDD}.ext"
  examples:
    - "AAPL_20250718.md"
    - "TSLA_20250718.json"
    - "MSFT_20250718_metadata.json"

validation_files:
  pattern: "{IDENTIFIER}_{YYYYMMDD}_validation.json"
  examples:
    - "AAPL_20250718_validation.json"
    - "sector_technology_20250718_validation.json"

discovery_files:
  pattern: "{TICKER}_{YYYYMMDD}_discovery.json"
  examples:
    - "AAPL_20250718_discovery.json"
    - "GOOGL_20250718_discovery.json"
```

## Integration with ScriptConfig

### Configuration Integration

```python
from pathlib import Path
from script_config import ScriptConfig

# ScriptConfig automatically resolves paths
config = ScriptConfig.from_environment()

# Access resolved paths
scripts_base = config.base_path / "scripts"  # Equivalent to {SCRIPTS_BASE}
templates_base = config.templates_path      # Equivalent to {TEMPLATES_BASE}
data_outputs = config.data_outputs_path     # Equivalent to {DATA_OUTPUTS}
twitter_outputs = config.twitter_outputs_path  # Twitter-specific outputs

# Use in command execution
fundamental_script = scripts_base / "fundamental_analysis" / "fundamental_discovery.py"
twitter_template = templates_base / "twitter" / "fundamental" / "twitter_fundamental_A_valuation.j2"
output_file = data_outputs / "fundamental_analysis" / f"{ticker}_{date}.md"
```

## Best Practices

### Command Documentation

1. **Always use base path variables** instead of hardcoded paths
2. **Provide full path examples** for clarity
3. **Document environment variable overrides** where applicable
4. **Include directory structure context** when relevant

### Script Implementation

1. **Import ScriptConfig** for path resolution
2. **Use Path objects** for cross-platform compatibility
3. **Validate path existence** before operations
4. **Create directories** as needed with `mkdir(parents=True, exist_ok=True)`

### Template References

1. **Use relative paths from TEMPLATES_BASE**
2. **Group templates by content type**
3. **Document template inheritance hierarchy**
4. **Specify shared component dependencies**

## Environment Configuration Examples

### Development Environment

```bash
export COLEMORTON_SCRIPTS_BASE="/Users/dev/colemorton/scripts"
export COLEMORTON_DATA_OUTPUTS="/Users/dev/colemorton/data/outputs"
export COLEMORTON_TEMPLATES_BASE="/Users/dev/colemorton/scripts/templates"
export COLEMORTON_DATA_IMAGES="/Users/dev/colemorton/data/images"
```

### Production Environment

```bash
export COLEMORTON_SCRIPTS_BASE="/opt/colemorton/scripts"
export COLEMORTON_DATA_OUTPUTS="/var/colemorton/outputs"
export COLEMORTON_TEMPLATES_BASE="/opt/colemorton/templates"
export COLEMORTON_DATA_IMAGES="/var/colemorton/images"
export COLEMORTON_LOGS_BASE="/var/log/colemorton"
```

### Docker Environment

```dockerfile
ENV COLEMORTON_SCRIPTS_BASE=/app/scripts
ENV COLEMORTON_DATA_OUTPUTS=/app/data/outputs
ENV COLEMORTON_TEMPLATES_BASE=/app/templates
ENV COLEMORTON_DATA_IMAGES=/app/data/images
ENV COLEMORTON_LOGS_BASE=/app/logs
```

---

**Last Updated**: 2025-07-18
**Applies To**: All Claude commands using standardized path references
**Version**: 1.0.0
