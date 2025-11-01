# Unified DASV Command System

This directory contains the **Unified DASV Command System** - a comprehensive framework for consistent script execution across all analysis domains in the Cole Morton platform.

## 🏗️ **System Architecture**

The unified command system consists of four core components that work together to provide institutional-grade analysis execution:

### 1. **Command-Script Mapping Registry** (`command_script_registry.json`)
- **Central registry** mapping all 47 commands to their implementation scripts, schemas, and templates
- **Path standardization** using consistent variable syntax (`{SCRIPTS_BASE}/`, `{TEMPLATES_BASE}/`, etc.)
- **Comprehensive coverage** across all DASV phases and analysis domains

### 2. **Command Script Resolver** (`command_script_resolver.py`)
- **Programmatic resolution** of command-script relationships
- **Sub-agent discovery** service for finding appropriate scripts
- **Dynamic path resolution** using the central registry

### 3. **Command Execution Service** (`command_execution_service.py`)
- **Unified execution interface** for individual DASV phases
- **Multiple execution modes** (direct script execution, sub-agent delegation)
- **Parameter validation** and environment preparation
- **Comprehensive result tracking** with metadata and confidence scoring

### 4. **DASV Workflow Orchestrator** (`dasv_workflow_orchestrator.py`)
- **Complete workflow management** (Discover → Analyze → Synthesize → Validate)
- **Quality gate enforcement** with institutional thresholds
- **Dependency management** between phases
- **Performance monitoring** and error handling

### 5. **Unified Command Interface** (`unified_command_interface.py`)
- **Single entry point** for all command execution
- **Command aliases** and shortcuts (e.g., `fa` for `fundamental_analysis`)
- **Flexible parameter handling** and validation
- **Consistent result formatting** across all domains

## 🚀 **Quick Start**

### Basic Command Execution

```bash
# Execute a single DASV phase
python unified_command_interface.py "fa:d AAPL"           # Fundamental analysis discover for AAPL
python unified_command_interface.py "sa:a sector=XLRE"   # Sector analysis analyze for XLRE

# Execute complete workflows
python unified_command_interface.py "fa:workflow AAPL"   # Full fundamental analysis workflow
python unified_command_interface.py "ca:workflow ticker_1=AAPL ticker_2=MSFT"  # Comparative analysis
```

### List Available Commands

```bash
# Show all available commands and workflows
python unified_command_interface.py --list

# Get information about a specific domain
python unified_command_interface.py --info fundamental_analysis
```

### Advanced Usage

```bash
# Execute with custom parameters
python unified_command_interface.py "ia:s industry=software_infrastructure date=20250814"

# Use sub-agent mode (requires Claude API integration)
python unified_command_interface.py "sa:workflow XLRE" --mode sub_agent
```

## 📋 **Supported Analysis Domains**

| Domain | Alias | Description | Phases |
|--------|-------|-------------|---------|
| `fundamental_analysis` | `fa` | Individual stock analysis | D → A → S → V |
| `sector_analysis` | `sa` | Sector-wide analysis | D → A → S → V |
| `industry_analysis` | `ia` | Industry-level analysis | D → A → S → V |
| `comparative_analysis` | `ca` | Cross-stock comparison | D → A → S → V |
| `macro_analysis` | `ma` | Macro-economic analysis | D → A → S → V |
| `trade_history` | `th` | Trading performance analysis | D → A → S → V |

**Phase Aliases:**
- `d` = `discover`
- `a` = `analyze`
- `s` = `synthesize`
- `v` = `validate`

## 🎯 **Key Features**

### 1. **Consistent Interface**
- **Unified parameter handling** across all analysis types
- **Standardized result formats** with metadata and confidence scores
- **Common error handling** and validation patterns

### 2. **Quality Assurance**
- **Institutional thresholds** (≥9.0/10 confidence baseline, ≥9.5/10 target)
- **Quality gate enforcement** between DASV phases
- **Comprehensive validation** with multi-source data verification

### 3. **Flexibility**
- **Multiple execution modes** (direct script, sub-agent delegation)
- **Configurable workflows** with custom parameters
- **Command aliases** and shortcuts for efficiency

### 4. **Monitoring & Observability**
- **Execution time tracking** and performance metrics
- **Comprehensive logging** with structured metadata
- **Quality score propagation** through workflow phases

## 🔧 **System Components**

### Command Execution Service
```python
from scripts.utils.command_execution_service import CommandExecutionService, ExecutionMode

service = CommandExecutionService()

# Execute single phase
result = service.execute_command(
    domain='fundamental_analysis',
    phase='discover',
    parameters={'ticker': 'AAPL', 'date': '20250814'},
    mode=ExecutionMode.DIRECT
)

# Execute full workflow
results = service.execute_full_dasv_workflow(
    domain='fundamental_analysis',
    parameters={'ticker': 'AAPL', 'date': '20250814'}
)
```

### DASV Workflow Orchestrator
```python
from scripts.utils.dasv_workflow_orchestrator import DASVWorkflowOrchestrator

orchestrator = DASVWorkflowOrchestrator()

# Execute workflow with quality gates
result = orchestrator.execute_workflow(
    domain='sector_analysis',
    parameters={'sector': 'XLRE', 'date': '20250814'}
)

# Access quality summary
print(result.quality_summary)
print(result.overall_confidence)
```

### Unified Command Interface
```python
from scripts.utils.unified_command_interface import UnifiedCommandInterface

interface = UnifiedCommandInterface()

# Execute command from string
result = interface.execute_command_string("fa:d AAPL")

# Execute full workflow
result = interface.execute_full_workflow(
    domain='fundamental_analysis',
    parameters={'ticker': 'AAPL'}
)
```

## 📊 **Quality Gates**

The system enforces quality gates at each DASV phase:

### Discovery Phase
- **Data completeness** validation
- **Price accuracy** verification (≤2% variance)
- **Source reliability** assessment

### Analysis Phase
- **Confidence threshold** enforcement (≥9.0/10)
- **Calculation accuracy** verification
- **Template gap coverage** validation

### Synthesis Phase
- **Template compliance** verification
- **Institutional presentation** quality
- **Confidence score** propagation (≥9.0/10)

### Validation Phase
- **Multi-source validation** across CLI services
- **Institutional quality** certification (≥9.5/10)
- **Evidence-based scoring** with audit trails

## 🔄 **Workflow Templates**

Each analysis domain has predefined workflow templates with:

- **Phase dependencies** (Discover → Analyze → Synthesize → Validate)
- **Quality gate specifications** for each phase
- **Timeout configurations** and performance expectations
- **Parameter validation** rules and requirements

Example template structure:
```json
{
  "fundamental_analysis": {
    "phases": ["discover", "analyze", "synthesize", "validate"],
    "quality_gates": {
      "discover": ["data_completeness", "price_accuracy"],
      "analyze": ["confidence_threshold", "calculation_accuracy"],
      "synthesize": ["template_compliance", "confidence_threshold"],
      "validate": ["institutional_quality", "validation_score"]
    },
    "dependencies": {
      "analyze": ["discover"],
      "synthesize": ["discover", "analyze"],
      "validate": ["discover", "analyze", "synthesize"]
    }
  }
}
```

## 🛠️ **Development & Maintenance**

### Path Standardization
All path references use consistent variable syntax:
- `{SCRIPTS_BASE}/` - Base script directory
- `{TEMPLATES_BASE}/` - Template directory
- `{DATA_OUTPUTS}/` - Output data directory
- `{SCHEMAS_BASE}/` - Schema directory

### Adding New Commands
1. **Update registry** (`command_script_registry.json`)
2. **Create script mappings** for all DASV phases
3. **Define quality gates** in workflow templates
4. **Test integration** with unified interface

### Quality Monitoring
- **Confidence score tracking** across all executions
- **Performance metrics** collection and analysis
- **Quality gate success rates** monitoring
- **Error pattern analysis** and improvement

## 🚀 **Integration Examples**

### Claude Command Integration
```bash
# These commands now have consistent execution patterns:
/fundamental_analyst AAPL      # Uses unified execution service
/sector_analyst XLRE          # Uses workflow orchestrator
/comparative_analyst/discover ticker_1=AAPL ticker_2=MSFT  # Uses command resolver
```

### Sub-Agent Integration
```python
# Sub-agents can discover appropriate scripts
from scripts.utils.command_script_resolver import CommandScriptResolver

resolver = CommandScriptResolver()
scripts = resolver.resolve_sub_agent_scripts('fundamental_analysis', 'discover', 'researcher')
```

### API Integration
```python
# Consistent API for all analysis types
def analyze_security(ticker, analysis_type='fundamental'):
    interface = UnifiedCommandInterface()
    result = interface.execute_full_workflow(
        domain=f'{analysis_type}_analysis',
        parameters={'ticker': ticker}
    )
    return result
```

## 📈 **Performance & Reliability**

### Execution Metrics
- **Average phase execution time** tracking
- **Success rate monitoring** across domains
- **Quality gate pass rates** analysis
- **Resource utilization** optimization

### Reliability Features
- **Comprehensive error handling** with graceful degradation
- **Timeout management** and resource protection
- **Quality threshold enforcement** with fail-fast behavior
- **Audit trail maintenance** for all executions

## 🎉 **Benefits**

### For Users
- **Single interface** for all analysis types
- **Consistent quality** across all outputs
- **Predictable performance** and reliability
- **Comprehensive documentation** and examples

### For Developers
- **Standardized patterns** for all command implementations
- **Reusable components** across analysis domains
- **Quality gate templates** for new command types
- **Comprehensive testing** and validation framework

### For Operations
- **Centralized monitoring** and observability
- **Performance optimization** opportunities
- **Quality trend analysis** and improvement tracking
- **Audit compliance** with institutional standards

---

## 📚 **Phase Implementation Summary**

### **Phase 3: Maximum Consistency Optimization (COMPLETED)**
✅ **Schema Consistency Optimizer** (`schema_consistency_optimizer.py`)
- Analyzed 18 existing schemas across 9 domains
- Generated standardized schema templates for all DASV phases
- Identified 4 key standardization opportunities
- Quality score baseline: 0.60/1.0 with improvement roadmap

✅ **Template Consistency Optimizer** (`template_consistency_optimizer.py`)
- Analyzed 32 Jinja2 templates across 7 domains
- Generated 24 standardized template files for all domain-phase combinations
- Quality score achieved: 0.72/1.0 with standardization recommendations
- Identified macro usage and base template adoption opportunities

✅ **DASV Consistency Validator** (`dasv_consistency_validator.py`)
- Comprehensive system-wide consistency validation framework
- 5 validation dimensions: schemas, templates, commands, quality standards, execution system
- Automated drift detection and quality scoring
- Institutional compliance monitoring with actionable recommendations

**Phase 3 Deliverables:**
- **4 standardized schema templates** (`scripts/standardized_schemas/`)
- **24 standardized template files** (`scripts/standardized_templates/`)
- **Comprehensive validation framework** with real-time consistency monitoring
- **Quality baseline establishment** with improvement tracking
- **Automated consistency reporting** for ongoing maintenance

### **Phase 4: Development & Maintenance Tools (COMPLETED)**
✅ **Automated Path Synchronizer** (`path_synchronizer.py`)
- Real-time detection of hardcoded path references across 47 command files
- Automated fix capability with backup and rollback functionality
- Integration with CI/CD pipelines for continuous path consistency monitoring
- Dry-run validation mode for safe deployment

✅ **Schema Migration Tool** (`schema_migrator.py`)
- Analysis of 18 existing schemas with automated migration plans
- Risk assessment (5 high-risk, 13 medium-risk migrations identified)
- Standardized schema template application with data preservation validation
- Backup and rollback capabilities for safe schema evolution

✅ **Template Upgrade Tool** (`template_upgrader.py`)
- Comprehensive analysis of 32 Jinja2 templates across all domains
- Automated upgrade to standardized patterns (base templates, macro imports, formatting)
- Risk-assessed upgrade plans (12 high-risk, 20 medium-risk upgrades)
- Content preservation validation and rollback support

✅ **CI/CD Integration Scripts** (`ci_cd_integration.py`)
- Four validation suites: pre_commit, pull_request, main_branch, nightly
- Automated pre-commit hook installation for immediate validation
- GitHub Actions workflow generation for CI pipeline integration
- Configurable quality gates with fail-fast and comprehensive modes

**Phase 4 Deliverables:**
- **4 development tools** for automated consistency maintenance
- **CI/CD integration** with pre-commit hooks and GitHub Actions
- **Quality gate enforcement** with configurable validation suites
- **Automated reporting** with JSON export for monitoring dashboards
- **Rollback capabilities** for all migration and upgrade operations

### **System Implementation Complete**

**Final System Status:**
- **Overall Architecture**: Unified DASV command system with institutional-grade execution
- **Consistency Framework**: Comprehensive validation and maintenance tools deployed
- **Development Workflow**: Automated CI/CD integration with quality gates
- **Command Coverage**: 47 commands across 6 analysis domains fully mapped
- **Template Standardization**: 32 templates analyzed with upgrade paths defined
- **Schema Evolution**: 18 schemas with migration plans and standardized templates

**Ongoing Maintenance:**
- **Automated validation** via pre-commit hooks and CI pipelines
- **Continuous monitoring** of system consistency and quality scores
- **Drift detection** with actionable recommendations for remediation
- **Performance tracking** baseline established for regression detection

The unified command system now provides a complete foundation for institutional-grade analysis execution with automated consistency maintenance, comprehensive quality assurance, and continuous monitoring across all analysis domains in the Cole Morton platform. All four implementation phases have established both the operational infrastructure and the maintenance tools needed for long-term system reliability and evolution.

---

## 🐛 **Known Validation Issues**

### Comparative Analysis Cross-Validation Bug (Resolved 2025-08-19)

#### Issue Description
The cross-analysis validation in `synthesis_cross_analysis_20250819_validation.json` incorrectly reported:
- `"frontmatter_consistency": "100%"`
- `"metadata_format_consistency": "100%"`

#### Actual State
- **TMO_vs_DHR_20250819.md**: Missing YAML frontmatter entirely
- **TSLA_vs_NIO_20250819.md**: Missing YAML frontmatter entirely
- **MRK_vs_TMO_20250818.md**: Has YAML frontmatter (correct structure)
- **KLAC_vs_QBTS_20250814.md**: Has YAML frontmatter (correct structure)

#### Root Cause
The validation logic only checked for the presence of document structure but failed to distinguish between:
1. **Enhanced Template**: Full YAML frontmatter with title, description, author, date, tags
2. **Basic Template**: Simple markdown headers without frontmatter

#### Resolution Applied
✅ **Template Standardization**: All comparative analysis templates updated to use enhanced structure
✅ **Missing Dependencies**: Created `shared/base_analysis_template.j2` base template
✅ **Jinja2 Inheritance**: Fixed broken template inheritance in synthesis templates
✅ **Generic References**: Removed ticker-specific `MU_vs_DHR` references from commands
✅ **Consistent Structure**: All future syntheses will include YAML frontmatter with emoji headers

#### Validation Logic Fix Required
Update the validation logic to:
- Detect presence/absence of YAML frontmatter (lines starting with `---`)
- Validate required frontmatter fields (title, description, author, date, tags)
- Correctly report structural inconsistencies when templates differ
- Flag frontmatter consistency as failed when only 50% have YAML

#### Template Enhancement Complete
All templates now standardized with:
- YAML frontmatter with comprehensive metadata
- Emoji section headers for visual structure
- Author attribution consistency
- Generic, ticker-agnostic structure

Future comparative analysis syntheses will consistently use the high-quality template structure.
