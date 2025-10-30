# Command Name Template

**Version**: 2.0 | **Last Updated**: 2024-08-14 | **Status**: Active
**Authority**: Platform Architecture | **Audience**: Command Developers

**Command Classification**: [📊|🎯|🔧|🌐] **[Core Product Command|Assistant|Tool|Integration]**
**Knowledge Domain**: `domain-name-expertise`
**Ecosystem Version**: `X.Y.Z` *(Last Updated: YYYY-MM-DD)*
**Outputs To**: `{DATA_OUTPUTS}/output_directory/`

## Script Integration Mapping

**Primary Script**: `{SCRIPTS_BASE}/path/to/primary_script.py`
**Script Class**: `{ScriptClassName}`
**Registry Name**: `{registry_name}`
**Content Types**: `["content_type_1", "content_type_2"]`
**Requires Validation**: `true|false`

**Registry Decorator**:
```python
@twitter_script(
    name="{registry_name}",
    content_types=["{content_type}"],
    requires_validation={true|false}
)
class {ScriptClassName}(BaseScript):
    """Script description"""
```

**Additional Scripts** (if multi-phase workflow):
```yaml
discovery_script:
  path: "{SCRIPTS_BASE}/path/to/discovery.py"
  class: "DiscoveryScript"
  phase: "Phase 1 - Data Collection"

analysis_script:
  path: "{SCRIPTS_BASE}/path/to/analysis.py"
  class: "AnalysisScript"
  phase: "Phase 2 - Analysis"

synthesis_script:
  path: "{SCRIPTS_BASE}/path/to/synthesis.py"
  class: "SynthesisScript"
  phase: "Phase 3 - Document Generation"

validation_script:
  path: "{SCRIPTS_BASE}/path/to/validation.py"
  class: "ValidationScript"
  phase: "Phase 4 - Quality Assurance"
```

## Template Integration Architecture

**Template Directory**: `{TEMPLATES_BASE}/template_category/`

**Template Mappings**:
| Template ID | File Path | Selection Criteria | Purpose |
|------------|-----------|-------------------|---------|
| template_a | `category/template_variant_a.j2` | condition_1 AND condition_2 | Primary use case |
| template_b | `category/template_variant_b.j2` | condition_3 OR condition_4 | Alternative approach |
| template_default | `category/default_template.j2` | fallback_condition | Fallback option |

**Shared Components**:
```yaml
base_template:
  path: "{TEMPLATES_BASE}/shared/base_template.j2"
  purpose: "Base template with common macros"

components:
  path: "{TEMPLATES_BASE}/shared/components.j2"
  purpose: "Reusable component macros"

validation_template:
  path: "{TEMPLATES_BASE}/validation/quality_checklist.j2"
  purpose: "Content quality validation"
```

**Template Selection Algorithm**:
```python
def select_optimal_template(data_context):
    """Intelligent template selection based on data characteristics"""

    # Template A: Primary Condition
    if (data_context.get('metric_1', 0) > threshold_1 and
        data_context.get('confidence', 0) > threshold_2):
        return 'category/template_variant_a.j2'

    # Template B: Alternative Condition
    if (condition_check(data_context) and
        data_context.get('type') == 'specific_type'):
        return 'category/template_variant_b.j2'

    # Default fallback
    return 'category/default_template.j2'
```

## CLI Service Integration

**Service Commands**:
```yaml
primary_service:
  command: "python {SCRIPTS_BASE}/service_cli.py"
  usage: "{command} action {parameter} --env prod --output-format json"
  purpose: "Primary data source description"
  health_check: "{command} health --env prod"

secondary_service:
  command: "python {SCRIPTS_BASE}/backup_service_cli.py"
  usage: "{command} action {parameter} --env prod --output-format json"
  purpose: "Backup/validation data source"
  health_check: "{command} health --env prod"

supporting_service:
  command: "python {SCRIPTS_BASE}/context_service_cli.py"
  usage: "{command} context --env prod --output-format json"
  purpose: "Supporting context/intelligence"
  health_check: "{command} health --env prod"
```

**Service Integration Protocol**:
```bash
# Pre-execution health check
python {SCRIPTS_BASE}/service_cli.py health --env prod

# Data collection
python {SCRIPTS_BASE}/service_cli.py collect {ticker} --env prod --output-format json

# Validation
python {SCRIPTS_BASE}/service_cli.py validate {ticker} --env prod --output-format json
```

## Data Flow & File References

**Input Sources**:
```yaml
primary_data:
  path: "{DATA_OUTPUTS}/source_directory/{IDENTIFIER}_{YYYYMMDD}.md"
  format: "markdown|json|csv"
  required: true
  description: "Primary data source description"

supplementary_data:
  path: "{DATA_IMAGES}/image_directory/{IDENTIFIER}_{YYYYMMDD}.png"
  format: "png|jpg|pdf"
  required: false
  description: "Visual/supplementary data source"

validation_data:
  path: "{DATA_OUTPUTS}/validation_directory/{IDENTIFIER}_{YYYYMMDD}_validation.json"
  format: "json"
  required: false
  description: "Validation/enhancement input"
```

**Output Structure**:
```yaml
primary_output:
  path: "{DATA_OUTPUTS}/output_directory/{IDENTIFIER}_{YYYYMMDD}.md"
  format: "markdown"
  description: "Main output file"

metadata_output:
  path: "{DATA_OUTPUTS}/output_directory/{IDENTIFIER}_{YYYYMMDD}_metadata.json"
  format: "json"
  description: "Execution metadata and quality scores"

validation_output:
  path: "{DATA_OUTPUTS}/output_directory/validation/{IDENTIFIER}_{YYYYMMDD}_validation.json"
  format: "json"
  description: "Quality validation results"
```

**Data Authority Protocol**:
```yaml
authority_hierarchy:
  primary: "service_name_1"  # Highest authority for conflicts
  secondary: "service_name_2"  # Fallback source
  validation: "service_name_3"  # Cross-validation source

conflict_resolution:
  threshold: "2%"  # Maximum variance before flag
  action: "use_primary"  # Resolution strategy
  logging: "comprehensive"  # Document all conflicts
```

## Execution Examples

### Direct Python Execution
```python
from script_registry import get_global_registry
from script_config import ScriptConfig

# Initialize
config = ScriptConfig.from_environment()
registry = get_global_registry(config)

# Execute single script
result = registry.execute_script(
    "{registry_name}",
    parameter_1="value_1",
    parameter_2="value_2",
    template_variant="template_a"  # Optional override
)

# Execute workflow (multi-phase)
workflow_result = execute_workflow(
    phases=["discover", "analyze", "synthesize", "validate"],
    parameter_1="value_1",
    parameter_2="value_2"
)
```

### Command Line Execution
```bash
# Via content automation CLI
python {SCRIPTS_BASE}/content_automation_cli.py \
    --script {registry_name} \
    --parameter-1 value_1 \
    --parameter-2 value_2 \
    --template-variant template_a

# Via direct script execution
python {SCRIPTS_BASE}/path/to/primary_script.py \
    --parameter-1 value_1 \
    --parameter-2 value_2 \
    --config-file config.yaml

# Via registry CLI
python {SCRIPTS_BASE}/script_registry_cli.py \
    --execute {registry_name} \
    --params '{"parameter_1": "value_1", "parameter_2": "value_2"}'
```

### Claude Command Execution
```
/{command_name} parameter_1 parameter_2
/{command_name} action=specific_action parameter_1=value_1
/{command_name} /path/to/validation/file_validation.json
```

## Parameters

### Core Parameters
- `parameter_1`: Description of parameter 1 - `option1` | `option2` | `option3` (required|optional, default: value)
- `parameter_2`: Description of parameter 2 - `valueA` | `valueB` (optional, default: valueA)
- `date`: Date in YYYYMMDD format (optional, defaults to current date)
- `confidence_threshold`: Minimum confidence requirement - `9.0` | `9.5` | `9.8` (optional, default: 9.0)

### Advanced Parameters
- `validation_enhancement`: Enable validation-driven optimization - `true` | `false` (optional, default: true)
- `template_variant`: Specific template override - `template_a` | `template_b` | `auto` (optional, default: auto)
- `cli_validation`: Enable real-time CLI service validation - `true` | `false` (optional, default: true)
- `depth`: Processing depth - `summary` | `standard` | `comprehensive` | `institutional` (optional, default: comprehensive)

### Workflow Parameters (Multi-Phase Commands)
- `phase_start`: Starting phase - `discover` | `analyze` | `synthesize` | `validate` (optional)
- `phase_end`: Ending phase - `discover` | `analyze` | `synthesize` | `validate` (optional)
- `continue_on_error`: Continue workflow despite errors - `true` | `false` (optional, default: false)
- `output_format`: Output format preference - `json` | `markdown` | `both` (optional, default: both)

## Quality Standards Framework

### Confidence Scoring
**Institutional-Quality Thresholds**:
- **Baseline Quality**: 9.0/10 minimum for institutional usage
- **Enhanced Quality**: 9.5/10 target for validation-optimized content
- **Premium Quality**: 9.8/10 for compliance-critical requirements
- **Perfect Quality**: 10.0/10 for exact regulatory compliance

### Validation Protocols
**Multi-Source Validation Standards**:
- **Data Accuracy**: ≤2% variance from authoritative sources
- **Content Integrity**: ≤1% variance for critical claims
- **Real-Time Currency**: Current market data integration
- **Service Health**: 80%+ operational across all CLI services

### Quality Gate Enforcement
**Critical Validation Points**:
1. **Input Phase**: Data source validation and completeness check
2. **Processing Phase**: Template selection and content generation
3. **Validation Phase**: Quality scoring and compliance verification
4. **Output Phase**: Final review and institutional certification

## Validation & Testing Framework

**Validation Script Integration**:
```yaml
validation_script:
  path: "{SCRIPTS_BASE}/validation/command_validation.py"
  class: "CommandValidationScript"
  methodology: "comprehensive_validation_framework"

test_files:
  unit_tests: "{SCRIPTS_BASE}/tests/test_{command_name}.py"
  integration_tests: "{SCRIPTS_BASE}/tests/integration/test_{command_name}_integration.py"
  validation_tests: "{SCRIPTS_BASE}/tests/validation/test_{command_name}_validation.py"
```

**Quality Assurance Workflow**:
```bash
# Run validation
python {SCRIPTS_BASE}/validation/command_validation.py \
    --command {command_name} \
    --output-file validation_result.json \
    --confidence-threshold 9.0

# Run tests
python -m pytest {SCRIPTS_BASE}/tests/test_{command_name}.py -v
python -m pytest {SCRIPTS_BASE}/tests/integration/ -k {command_name}
```

## Cross-Command Integration

### Upstream Dependencies
**Commands that provide input to this command**:
- `upstream_command_1`: Provides data type A via {DATA_OUTPUTS}/source_a/
- `upstream_command_2`: Provides data type B via {DATA_OUTPUTS}/source_b/

### Downstream Dependencies
**Commands that consume this command's outputs**:
- `downstream_command_1`: Consumes output for purpose A
- `downstream_command_2`: Transforms output for platform B

### Coordination Workflows
**Multi-Command Orchestration**:
```bash
# Sequential execution
/{upstream_command} parameter_1 parameter_2
/{current_command} derived_parameter_1 derived_parameter_2
/{downstream_command} output_reference

# Parallel validation
/{current_command} input_a && /{validation_command} output_a
```

## Output Management

### File Organization
**Output Structure**:
```
{DATA_OUTPUTS}/output_directory/
├── {IDENTIFIER}_{YYYYMMDD}.md (primary output)
├── {IDENTIFIER}_{YYYYMMDD}_metadata.json (execution metadata)
├── backup/{IDENTIFIER}_{YYYYMMDD}_backup.md (backup copy)
└── validation/{IDENTIFIER}_{YYYYMMDD}_validation.json (quality validation)
```

### Quality Metadata
**Comprehensive Tracking**:
```json
{
  "metadata": {
    "command_name": "{command_name}",
    "execution_timestamp": "ISO_8601_format",
    "framework_version": "X.Y.Z",
    "confidence_score": "9.X/10.0",
    "validation_status": "PASSED|FLAGGED|FAILED"
  },
  "execution_context": {
    "script_class": "{ScriptClassName}",
    "template_used": "template_variant_x.j2",
    "cli_services_health": {"service_1": "healthy", "service_2": "healthy"},
    "data_sources": ["source_1", "source_2", "source_3"]
  },
  "quality_assessment": {
    "data_accuracy": "9.X/10.0",
    "content_quality": "9.X/10.0",
    "compliance_status": "COMPLIANT|FLAGGED|NON_COMPLIANT",
    "institutional_ready": "true|false"
  }
}
```

## Usage Examples

### Basic Usage
```
/{command_name} TICKER_20250718
/{command_name} action=discover ticker=AAPL date=20250718
```

### Advanced Usage
```
/{command_name} action=full_workflow ticker=MSFT confidence_threshold=9.5 template_variant=template_a
```

### Validation Enhancement
```
/{command_name} {DATA_OUTPUTS}/output_directory/validation/TICKER_20250718_validation.json
```

---

**Integration with Framework**: This command integrates with the broader Sensylate ecosystem through standardized script registry, template system, CLI service integration, and validation framework protocols.

**Author**: Cole Morton
**Framework**: [Specific Framework if applicable]
**Confidence**: [Command confidence based on implementation completeness]
**Data Quality**: [Data quality assessment based on source validation]
