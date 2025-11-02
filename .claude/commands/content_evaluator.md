# Content Evaluator

**Command Classification**: 🔧 **Tool**
**Knowledge Domain**: `content-quality-assessment`
**Ecosystem Version**: `2.1.0` *(Last Updated: 2025-07-18)*
**Outputs To**: `{DATA_OUTPUTS}/content_evaluation/`

## Script Integration Mapping

**Primary Script**: `{SCRIPTS_BASE}/base_scripts/content_evaluation_script.py`
**Script Class**: `ContentEvaluationScript`
**Registry Name**: `content_evaluation`
**Content Types**: `["content_evaluation"]`
**Requires Validation**: `false`

**Registry Decorator**:
```python
@twitter_script(
    name="content_evaluation",
    content_types=["content_evaluation"],
    requires_validation=False
)
class ContentEvaluationScript(BaseScript):
    """Expert analytical content validation system with systematic research methodology"""
```

**Additional Scripts** (multi-phase workflow):
```yaml
validation_script:
  path: "{SCRIPTS_BASE}/content_validation/financial_data_validator.py"
  class: "FinancialDataValidator"
  phase: "Phase 1 - Financial Data Validation"

market_data_script:
  path: "{SCRIPTS_BASE}/market_data/market_data_integrator.py"
  class: "MarketDataIntegrator"
  phase: "Phase 2 - Real-Time Market Data Integration"

compliance_script:
  path: "{SCRIPTS_BASE}/compliance/regulatory_compliance_checker.py"
  class: "RegulatoryComplianceChecker"
  phase: "Phase 3 - Regulatory Compliance Assessment"

evidence_script:
  path: "{SCRIPTS_BASE}/research/evidence_sourcing_engine.py"
  class: "EvidenceSourcingEngine"
  phase: "Phase 4 - Evidence Quality Assessment"
```

## Template Integration Architecture

**Template Directory**: `{TEMPLATES_BASE}/content_evaluation/`

**Template Mappings**:
| Template ID | File Path | Selection Criteria | Purpose |
|------------|-----------|-------------------|---------|
| financial_analysis_evaluation | `evaluation/financial_analysis_validation.j2` | Content type financial analysis | Investment research validation |
| market_research_evaluation | `evaluation/market_research_validation.j2` | Content type market research | Market analysis quality assessment |
| strategic_assessment_evaluation | `evaluation/strategic_assessment_validation.j2` | Content type strategic analysis | Business intelligence validation |
| comparative_analysis_evaluation | `evaluation/comparative_analysis_validation.j2` | Content type comparative analysis | Cross-stock comparative investment analysis validation |
| compliance_evaluation | `evaluation/compliance_validation.j2` | Regulatory content focus | Compliance and risk assessment |
| general_content_evaluation | `evaluation/general_content_validation.j2` | Default fallback template | General content quality assessment |

**Shared Components**:
```yaml
evaluation_base_template:
  path: "{TEMPLATES_BASE}/content_evaluation/shared/evaluation_base.j2"
  purpose: "Base template with common evaluation framework and scoring"

evidence_matrix_template:
  path: "{TEMPLATES_BASE}/content_evaluation/shared/evidence_matrix.j2"
  purpose: "Evidence-based validation matrix and source tracking"

risk_assessment_template:
  path: "{TEMPLATES_BASE}/content_evaluation/shared/risk_assessment.j2"
  purpose: "Risk calibration and impact assessment components"

comparative_matrix_template:
  path: "{TEMPLATES_BASE}/content_evaluation/shared/comparative_matrix.j2"
  purpose: "Cross-stock comparative analysis validation and consistency checking"
```

**Template Selection Algorithm**:
```python
def select_evaluation_template(content_analysis):
    """Select optimal template for content evaluation"""

    # Financial analysis evaluation for investment content
    if (content_analysis.get('content_type') == 'financial_analysis' or
        len(content_analysis.get('stock_symbols', [])) > 0):
        return 'evaluation/financial_analysis_validation.j2'

    # Market research evaluation for market analysis
    elif content_analysis.get('content_type') == 'market_research':
        return 'evaluation/market_research_validation.j2'

    # Strategic assessment for business intelligence
    elif content_analysis.get('content_type') == 'strategic_analysis':
        return 'evaluation/strategic_assessment_validation.j2'

    # Comparative analysis evaluation for cross-stock analysis
    elif (content_analysis.get('content_type') == 'comparative_analysis' or
          '_vs_' in content_analysis.get('filename', '').lower() or
          len(content_analysis.get('stock_symbols', [])) >= 2):
        return 'evaluation/comparative_analysis_validation.j2'

    # Compliance evaluation for regulatory content
    elif (content_analysis.get('regulatory_focus', False) or
          content_analysis.get('compliance_required', False)):
        return 'evaluation/compliance_validation.j2'

    # Default general content evaluation
    return 'evaluation/general_content_validation.j2'
```

## CLI Service Integration

**Service Commands**:
```yaml
yahoo_finance_cli:
  command: "python {SCRIPTS_BASE}/yahoo_finance_cli.py"
  usage: "{command} quote {ticker} --env prod --output-format json"
  purpose: "Real-time market data validation for financial content"
  health_check: "{command} health --env prod"
  priority: "primary"

sec_edgar_cli:
  command: "python {SCRIPTS_BASE}/sec_edgar_cli.py"
  usage: "{command} filings {ticker} --env prod --output-format json"
  purpose: "Primary source verification from SEC filings"
  health_check: "{command} health --env prod"
  priority: "primary"

fred_economic_cli:
  command: "python {SCRIPTS_BASE}/fred_economic_cli.py"
  usage: "{command} indicators --env prod --output-format json"
  purpose: "Economic data validation and context verification"
  health_check: "{command} health --env prod"
  priority: "secondary"

fmp_cli:
  command: "python {SCRIPTS_BASE}/fmp_cli.py"
  usage: "{command} profile {ticker} --env prod --output-format json"
  purpose: "Financial data cross-validation and verification"
  health_check: "{command} health --env prod"
  priority: "secondary"

alpha_vantage_cli:
  command: "python {SCRIPTS_BASE}/alpha_vantage_cli.py"
  usage: "{command} fundamentals {ticker} --env prod --output-format json"
  purpose: "Alternative financial data source for validation"
  health_check: "{command} health --env prod"
  priority: "tertiary"
```

**Content Evaluation Integration Protocol**:
```bash
# Real-time financial data validation
python {SCRIPTS_BASE}/yahoo_finance_cli.py quote {ticker} --env prod --output-format json

# Primary source verification
python {SCRIPTS_BASE}/sec_edgar_cli.py filings {ticker} --env prod --output-format json

# Economic context validation
python {SCRIPTS_BASE}/fred_economic_cli.py indicators --env prod --output-format json

# Cross-validation with alternative sources
python {SCRIPTS_BASE}/fmp_cli.py profile {ticker} --env prod --output-format json
```

**Data Authority Protocol**:
```yaml
authority_hierarchy:
  primary_sources: "HIGHEST_AUTHORITY"  # SEC filings, official reports
  real_time_market: "PRICING_AUTHORITY"  # Yahoo Finance for current market data
  regulatory_data: "COMPLIANCE_AUTHORITY"  # SEC EDGAR for regulatory information
  cross_validation: "VERIFICATION_AUTHORITY"  # FMP/Alpha Vantage for data verification

conflict_resolution:
  financial_precedence: "primary_sources"  # SEC filings take priority
  pricing_authority: "yahoo_finance"  # Primary source for market data
  variance_threshold: "5%"  # Acceptable variance for real-time data
  action: "evidence_based_resolution"  # Resolution strategy
```

## Data Flow & File References

**Input Sources**:
```yaml
evaluation_target:
  path: "{USER_PROVIDED_FILE_PATH}"
  format: "markdown"
  required: true
  description: "Target file for comprehensive content evaluation"

financial_data_sources:
  path: "CLI_SERVICES_REAL_TIME"
  format: "json"
  required: false
  description: "Real-time financial data for content validation"

regulatory_filings:
  path: "CLI_SERVICES_REAL_TIME"
  format: "json"
  required: false
  description: "SEC filings and regulatory data for primary source verification"

economic_indicators:
  path: "CLI_SERVICES_REAL_TIME"
  format: "json"
  required: false
  description: "Economic data for macroeconomic content validation"

evaluation_templates:
  path: "{TEMPLATES_BASE}/content_evaluation/"
  format: "jinja2"
  required: true
  description: "Evaluation templates for different content types"
```

**Output Structure**:
```yaml
evaluation_report:
  path: "{TARGET_FILE_DIRECTORY}/{TARGET_FILENAME}_evaluation.md"
  format: "markdown"
  description: "Comprehensive content evaluation report with evidence-based scoring"

evaluation_metadata:
  path: "{DATA_OUTPUTS}/content_evaluation/{TARGET_FILENAME}_{YYYYMMDD}_metadata.json"
  format: "json"
  description: "Evaluation metadata including validation sources and confidence scores"

evidence_matrix:
  path: "{DATA_OUTPUTS}/content_evaluation/evidence/{TARGET_FILENAME}_{YYYYMMDD}_evidence.json"
  format: "json"
  description: "Evidence tracking matrix with source verification and confidence levels"

validation_summary:
  path: "{DATA_OUTPUTS}/content_evaluation/summary/{TARGET_FILENAME}_{YYYYMMDD}_summary.json"
  format: "json"
  description: "Validation summary with key findings and recommendations"
```

**Evaluation Dependencies**:
```yaml
content_evaluation_flow:
  context_establishment:
    - "content type identification and classification"
    - "stock symbols extraction for financial validation"
    - "data freshness requirements assessment"
    - "methodology and confidence level analysis"

  validation_execution:
    - "multi-source financial data verification"
    - "primary source cross-referencing"
    - "regulatory compliance assessment"
    - "evidence quality categorization"

  assessment_generation:
    - "evidence-based scoring calculation"
    - "risk impact assessment"
    - "decision confidence determination"
    - "actionable recommendations development"
```

## Parameters

### Core Parameters
- `filename`: Target file for evaluation (required, must exist in project)
- `evaluation_depth`: Analysis depth - `standard` | `comprehensive` | `institutional` (optional, default: comprehensive)
- `validation_focus`: Specific validation areas - `financial_data` | `market_analysis` | `regulatory_compliance` | `methodology` (optional)
- `real_time_validation`: Enable real-time market data validation - `true` | `false` (optional, default: true)

### Advanced Parameters
- `confidence_threshold`: Minimum confidence requirement - `9.0` | `9.5` | `9.8` (optional, default: 9.0)
- `template_variant`: Specific template override - `financial_analysis` | `market_research` | `strategic_assessment` | `comparative_analysis` | `auto` (optional, default: auto)
- `comparative_validation`: Enable specialized comparative analysis validation - `true` | `false` (optional, default: auto-detect)
- `cross_stock_threshold`: Cross-stock data consistency threshold - `1%` | `3%` | `5%` (optional, default: 3%)
- `cli_validation`: Enable real-time CLI service validation - `true` | `false` (optional, default: true)
- `output_format`: Output format preference - `markdown` | `json` | `both` (optional, default: markdown)

### Workflow Parameters (Multi-Phase Commands)
- `phase_start`: Starting phase - `validation` | `market_data` | `compliance` | `evidence` (optional)
- `phase_end`: Ending phase - `validation` | `market_data` | `compliance` | `evidence` (optional)
- `continue_on_error`: Continue workflow despite errors - `true` | `false` (optional, default: false)
- `content_type`: Content type for evaluation - `financial_analysis` | `trade_history` | `sector_analysis` | `comparative_analysis` (optional)

## Systematic Evaluation Methodology

**Phase 0: Pre-Evaluation Context Establishment**
- Document analysis date and data freshness requirements
- Identify content type (financial analysis, market research, strategic assessment, comparative analysis)
- Extract stock symbols/tickers for real-time data validation via Yahoo Finance CLI
- **For Comparative Analysis**: Identify both companies and validate cross-stock comparison framework
- Assess claimed confidence levels and methodology transparency
- Note any explicit limitations or assumptions stated

**Phase 1: Structured Content Analysis**
1. **Claim Categorization**: Sort all assertions into:
   - Quantitative claims (financial metrics, market data, growth rates)
   - Qualitative assessments (competitive positioning, risk factors)
   - Predictive statements (forecasts, scenario analysis)
   - Methodological assumptions (valuation models, data sources)

2. **Evidence Mapping**: For each claim, identify:
   - Primary source requirements (SEC filings, official reports)
   - **For Comparative Analysis**: Cross-stock data consistency requirements
   - Verification methodology needed
   - Potential conflict indicators
   - Time-sensitivity factors

**Phase 2: Multi-Source Validation Protocol**
3. **Primary Source Verification**:
   - Cross-reference ALL quantitative data with official sources (10-K, 10-Q, earnings calls)
   - **For Comparative Analysis**: Validate data consistency across both companies
   - Validate regulatory information via authoritative bodies (SEC, FDA, etc.)
   - **Use Yahoo Finance MCP server** for real-time financial data validation:
     - MCP tool `get_stock_fundamentals(ticker)` - Current stock metrics and valuations
     - MCP tool `get_financial_statements(ticker)` - Financial statements and data integrity
     - MCP tool `get_market_data_summary(ticker, period)` - Historical performance analysis
     - **For Comparative Analysis**: Execute for both tickers and cross-validate comparative claims
   - Verify timeline accuracy against actual events

4. **Consistency Analysis**:
   - Compare claims against peer analysis and consensus estimates
   - **For Comparative Analysis**: Verify cross-stock comparison methodology and winner determination logic
   - Check internal logical consistency within the document
   - **For Comparative Analysis**: Validate risk matrix probabilities and portfolio allocation rationale
   - Identify conflicts between stated confidence and supporting evidence
   - Assess methodology appropriateness for stated conclusions

**Phase 3: Risk-Calibrated Assessment**
5. **Failure Mode Detection**:
   - Data staleness beyond acceptable thresholds
   - Circular reasoning or confirmation bias patterns
   - Overconfidence in uncertain domains
   - Missing critical risk factors or alternative scenarios

6. **Impact Prioritization**:
   - Classify errors by potential decision impact (Critical/High/Medium/Low)
   - Weight accuracy issues by materiality to core thesis
   - Identify "thesis-breaking" vs "refinement-needed" discrepancies

**Phase 4: Standardized Scoring & Reporting**
7. **Evidence-Based Rating System**:
   - Score each category using defined benchmarks
   - Document confidence intervals for all assessments
   - Provide explicit reasoning for all major rating decisions
   - Include "unknown/unverifiable" designations where appropriate

8. **Actionable Report Generation**: Produce structured evaluation with:
   - Executive summary with overall reliability score
   - Category-specific accuracy breakdown with evidence links
   - Critical gaps requiring immediate attention
   - Decision-impact assessment (safe to use/use with caution/do not use)
   - Recommended follow-up research priorities

## Standardized Evaluation Framework

**Quality Assurance Checkpoints** (apply at each phase):
- Can I trace this claim to a primary, authoritative source?
- Does the evidence quality match the confidence level claimed?
- Would I stake my professional reputation on this assessment?
- Have I considered alternative explanations for apparent discrepancies?
- Is my evaluation methodology transparent and reproducible?

**Evidence-Based Rating Benchmarks**:

**Financial Data Accuracy (Weight: 30%)**
- A (9-10): All metrics verified via official filings, <5% variance from source, cross-stock data consistent
- B (7-8): Minor discrepancies <10%, or timing lags clearly noted, comparative ratios accurate
- C (5-6): Significant errors 10-25%, or methodology concerns present, some cross-stock inconsistencies
- D (3-4): Major errors >25%, or unverifiable source claims, significant comparative data issues
- F (1-2): Fundamental calculation errors or fabricated data, cross-stock analysis fundamentally flawed

**Comparative Analysis Quality (Weight: 25%)** *[For Comparative Analysis Only]*
- A (9-10): Sound comparative methodology, winner determination well-supported, risk matrices accurate
- B (7-8): Generally sound comparison with minor gaps in cross-stock analysis or portfolio logic
- C (5-6): Some comparative methodology concerns or questionable winner determination rationale
- D (3-4): Significant comparative framework issues or unsupported cross-stock conclusions
- F (1-2): Comparative methodology fundamentally flawed or winner determination lacks basis

**Market Analysis Quality (Weight: 25%)** *[For Non-Comparative Analysis]*
- A (9-10): Assumptions backed by current research, peer consensus alignment
- B (7-8): Reasonable assumptions with minor gaps in supporting evidence
- C (5-6): Questionable assumptions or significant peer disagreement
- D (3-4): Unsupported assumptions or contradicted by evidence
- F (1-2): Assumptions contradicted by readily available data

**Risk Assessment (Weight: 20%)**
- A (9-10): Risk matrices accurate, stress testing sound, comparative risk analysis well-calibrated
- B (7-8): Generally sound risk assessment with minor probability or impact uncertainties
- C (5-6): Some risk probability miscalibration or missing cross-stock risk considerations
- D (3-4): Significant risk assessment gaps or understated comparative risks
- F (1-2): Risk analysis fundamentally flawed or critical risks ignored

**Regulatory/Compliance Assessment (Weight: 15%)**
- A (9-10): Current regulatory status verified, compliance requirements understood
- B (7-8): Generally current with minor regulatory timeline uncertainties
- C (5-6): Some outdated regulatory information or compliance gaps
- D (3-4): Major regulatory gaps or compliance misunderstandings
- F (1-2): Fundamental regulatory misunderstanding or ignored compliance issues

**Methodology Transparency (Weight: 10%)**
- A (9-10): Methodology explicit, confidence levels appropriate, comparative framework clear
- B (7-8): Generally transparent with minor gaps in methodology or comparative logic disclosure
- C (5-6): Some methodology concerns or overconfident comparative assertions
- D (3-4): Significant methodology gaps or inappropriate confidence in comparative claims
- F (1-2): Methodology opaque or comparative confidence claims unsupported by analysis

## Structured Output Requirements

**Report Template** (mandatory sections):

```markdown
# [Content Type] Evaluation Report: [Title]

## Executive Assessment
**Overall Reliability Score**: [X.X/10] | **Decision Confidence**: [High/Medium/Low/Do Not Use]
**Evaluation Date**: [Date] | **Evaluator Confidence**: [X.X/10]

[2-3 sentence summary of content reliability and primary concerns]

## Evidence-Based Scoring Breakdown
| Category | Score | Grade | Weight | Evidence Quality | Key Issues |
|----------|-------|--------|--------|------------------|------------|
| Financial Data | X.X/10 | [A-F] | 30% | [Primary/Secondary/Unverified] | [Brief summary] |
| Comparative Analysis* | X.X/10 | [A-F] | 25% | [Primary/Secondary/Unverified] | [Brief summary] |
| Risk Assessment | X.X/10 | [A-F] | 20% | [Primary/Secondary/Unverified] | [Brief summary] |
| Regulatory/Compliance | X.X/10 | [A-F] | 15% | [Primary/Secondary/Unverified] | [Brief summary] |
| Methodology | X.X/10 | [A-F] | 10% | [Primary/Secondary/Unverified] | [Brief summary] |

*For comparative analysis content only. Non-comparative content uses Market Analysis (25%) instead.

## Critical Findings Matrix
### ✅ Verified Claims (High Confidence)
[List with source citations]

### ⚠️ Questionable Claims (Medium Confidence)
[List with explanation of concerns]

### ❌ Inaccurate Claims (Low Confidence)
[List with correcting evidence]

### ❓ Unverifiable Claims
[List with research limitations noted]

## Decision Impact Assessment
**Thesis-Breaking Issues**: [None/List critical flaws]
**Material Concerns**: [List significant but non-fatal issues]
**Refinement Needed**: [List minor corrections required]

## Usage Recommendations
- **Safe for Decision-Making**: [Yes/No + reasoning]
- **Required Corrections**: [Prioritized list]
- **Follow-up Research**: [Specific recommendations]
- **Monitoring Requirements**: [Key data points to track]

## Methodology Notes
**Sources Consulted**: [Count and types]
**Yahoo Finance Bridge Validation**: [Stock symbols verified with real-time data]
**Research Limitations**: [What couldn't be verified]
**Confidence Intervals**: [Where uncertainty exists]
**Evaluation Methodology**: [Key validation approaches used]
```

**File Output Location**: Same directory as source file with `_evaluation.md` suffix
**Quality Check**: Every evaluation must include source links for major validation points

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
2. **Processing Phase**: Template selection and content evaluation
3. **Validation Phase**: Quality scoring and compliance verification
4. **Output Phase**: Final review and institutional certification

## Real-Time Financial Data Validation Protocol

**CLI Service Integration for Content Validation**:

When evaluating financial content, ALWAYS use the CLI service ecosystem for current market data validation. This ensures accuracy against live market conditions rather than potentially stale information.

**Required CLI Commands for Financial Content**:

1. **Stock Information Validation**:
   ```bash
   python {SCRIPTS_BASE}/yahoo_finance_cli.py quote {SYMBOL} --env prod --output-format json
   ```
   **Validates**: Current price, market cap, P/E ratio, 52-week range, volume, sector/industry, analyst recommendations

2. **Financial Statements Verification**:
   ```bash
   python {SCRIPTS_BASE}/sec_edgar_cli.py filings {SYMBOL} --env prod --output-format json
   ```
   **Validates**: Income statement metrics, balance sheet data, cash flow statements

3. **Historical Performance Check**:
   ```bash
   python {SCRIPTS_BASE}/fmp_cli.py historical {SYMBOL} --period {PERIOD} --env prod --output-format json
   ```
   **Validates**: Historical price movements, growth calculations, trend analysis
   **Periods**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

**CLI Service Integration Workflow**:

**Step 1: Symbol Extraction**
- Scan content for stock symbols/tickers (e.g., HIMS, AAPL, TSLA)
- **For Comparative Analysis**: Identify both companies being compared (e.g., AAPL vs MSFT)
- Note claimed stock prices, valuations, and financial metrics
- **For Comparative Analysis**: Extract comparative ratios, risk matrices, and portfolio allocations
- Identify date ranges for historical data validation

**Step 2: Real-Time Validation**
- Execute CLI service commands for each identified symbol
- **For Comparative Analysis**: Execute for both companies and validate cross-stock comparisons
- Compare CLI service results with content claims
- **For Comparative Analysis**: Verify comparative ratios and relative positioning accuracy
- Calculate variance percentages for quantitative metrics
- **For Comparative Analysis**: Cross-validate winner determination logic with actual data
- Flag discrepancies exceeding accuracy thresholds

**Step 3: Data Quality Assessment**
- **Primary Data** (0-5% variance): Grade A reliability
- **Minor Discrepancy** (5-10% variance): Grade B with timing notation
- **Significant Error** (10-25% variance): Grade C with methodology concerns
- **Major Inaccuracy** (>25% variance): Grade D/F requiring correction
- **For Comparative Analysis**: Additional cross-stock consistency threshold (≤3% variance between comparative claims)

**CLI Service Data Reliability Standards**:
- Yahoo Finance provides real-time market data with <15 minute delay
- SEC EDGAR provides official regulatory filings and compliance data
- FMP provides comprehensive financial statements and historical data
- Alpha Vantage provides alternative data sources for cross-validation

**Error Handling & Limitations**:
- If primary CLI service fails, use backup services for validation
- Note any symbols not available in service databases
- Handle market closure times and weekend data limitations
- Cross-reference unusual readings with multiple CLI services

## Execution Examples

### Direct Python Execution
```python
from script_registry import get_global_registry
from script_config import ScriptConfig

# Initialize
config = ScriptConfig.from_environment()
registry = get_global_registry(config)

# Execute content evaluation
result = registry.execute_script(
    "content_evaluation",
    filename="/{DATA_OUTPUTS}/fundamental_analysis/COMPANY_DATE.md",
    evaluation_depth="comprehensive",
    real_time_validation=True
)

# Execute with specific validation focus
result = registry.execute_script(
    "content_evaluation",
    filename="/{DATA_OUTPUTS}/market_research/SECTOR_ANALYSIS_20250718.md",
    validation_focus=["financial_data", "regulatory_compliance"],
    evaluation_depth="institutional"
)

# Execute compliance-focused evaluation
result = registry.execute_script(
    "content_evaluation",
    filename="/{DATA_OUTPUTS}/strategic_analysis/BUSINESS_PLAN_20250718.md",
    validation_focus=["regulatory_compliance", "methodology"],
    evaluation_depth="standard"
)
```

### Command Line Execution
```bash
# Via content automation CLI
python {SCRIPTS_BASE}/content_automation_cli.py \
    --script content_evaluation \
    --filename "/{DATA_OUTPUTS}/fundamental_analysis/COMPANY_DATE.md" \
    --evaluation-depth comprehensive \
    --real-time-validation true

# Via direct script execution
python {SCRIPTS_BASE}/base_scripts/content_evaluation_script.py \
    --filename "/{DATA_OUTPUTS}/market_research/SECTOR_ANALYSIS_20250718.md" \
    --validation-focus financial_data,regulatory_compliance \
    --evaluation-depth institutional

# Compliance-focused evaluation
python {SCRIPTS_BASE}/base_scripts/content_evaluation_script.py \
    --filename "/{DATA_OUTPUTS}/strategic_analysis/BUSINESS_PLAN_20250718.md" \
    --validation-focus regulatory_compliance,methodology

# Batch evaluation with real-time validation
python {SCRIPTS_BASE}/content_evaluation/batch_evaluator.py \
    --directory "/{DATA_OUTPUTS}/fundamental_analysis/" \
    --pattern "*_20250718.md" \
    --real-time-validation true
```

### Claude Command Execution
```
# Standard content evaluation
/content_evaluator filename="/{DATA_OUTPUTS}/fundamental_analysis/COMPANY_DATE.md"

# Comprehensive evaluation with real-time validation
/content_evaluator filename="/{DATA_OUTPUTS}/market_research/SECTOR_ANALYSIS_20250718.md" evaluation_depth=comprehensive real_time_validation=true

# Compliance-focused evaluation
/content_evaluator filename="/{DATA_OUTPUTS}/strategic_analysis/BUSINESS_PLAN_20250718.md" validation_focus=regulatory_compliance,methodology

# Financial analysis evaluation
/content_evaluator filename="/{DATA_OUTPUTS}/fundamental_analysis/AAPL_20250718.md" validation_focus=financial_data,market_analysis

# Institutional-grade evaluation
/content_evaluator filename="/{DATA_OUTPUTS}/investment_research/PORTFOLIO_ANALYSIS_20250718.md" evaluation_depth=institutional
```

### Content Evaluation Workflow Examples
```
# Financial content evaluation workflow
/content_evaluator filename="/{DATA_OUTPUTS}/fundamental_analysis/TSLA_20250718.md" evaluation_depth=comprehensive

# Market research validation workflow
/content_evaluator filename="/{DATA_OUTPUTS}/sector_analysis/technology_20250718.md" validation_focus=market_analysis,methodology

# Strategic analysis compliance check
/content_evaluator filename="/{DATA_OUTPUTS}/business_intelligence/M_AND_A_ANALYSIS_20250718.md" validation_focus=regulatory_compliance

# Multi-source validation for critical content
/content_evaluator filename="/{DATA_OUTPUTS}/investment_recommendations/HIGH_CONVICTION_PICKS_20250718.md" evaluation_depth=institutional real_time_validation=true

# Comparative analysis evaluation examples
/content_evaluator filename="/{DATA_OUTPUTS}/comparative_analysis/AAPL_vs_GOOGL_20250718.md" comparative_validation=true
/content_evaluator filename="/{DATA_OUTPUTS}/comparative_analysis/cross-sector-comparison-20250718.md" evaluation_depth=comprehensive
```

Analyzes the specified file and generates comprehensive accuracy evaluation report with evidence-based scoring and actionable recommendations.

## Self-Monitoring & Quality Assurance

**Pre-Evaluation Diagnostic Questions**:
- What is the claimed confidence level and is methodology adequate to support it?
- What are the highest-risk claims that could materially impact decisions?
- Which assertions require real-time data vs. historical verification?
- What stock symbols/tickers need validation via Yahoo Finance Bridge?
- Are there domain-specific validation requirements I need to consider?

**Post-Evaluation Validation Checklist**:
- [ ] Have I verified all quantitative claims against primary sources?
- [ ] Have I used Yahoo Finance Bridge to validate all stock-specific metrics?
- [ ] Can I defend every grade assignment with specific evidence?
- [ ] Would an expert in this domain reach similar conclusions?
- [ ] Are my recommendations proportionate to the evidence quality?
- [ ] Have I clearly separated what I know vs. what I cannot verify?

**Failure Mode Prevention**:
- **Confirmation Bias**: Actively seek evidence that contradicts original analysis
- **Authority Bias**: Verify prestigious sources just as rigorously as others
- **Anchoring**: Assess each claim independently before forming overall judgment
- **Overconfidence**: Include explicit uncertainty acknowledgments where appropriate

## Continuous Improvement Protocol

**After Each Evaluation**:
- Document any research limitations encountered
- Note sources that proved most/least reliable
- Identify patterns in content accuracy issues
- Record methodology refinements for future use

**Success Metrics**:
- Decision-makers report high confidence in evaluation reliability
- Subsequent events validate risk assessments and accuracy judgments
- Evaluation methodology proves replicable across different content types
- Time-to-evaluation decreases while maintaining quality standards

## Cross-Command Integration

### Upstream Dependencies
**Commands that provide input to this command**:
- `fundamental_analyst`: Provides fundamental analysis reports via {DATA_OUTPUTS}/fundamental_analysis/
- `trade_history`: Provides trade history reports via {DATA_OUTPUTS}/trade_history/
- `sector_analyst`: Provides sector analysis reports via {DATA_OUTPUTS}/sector_analysis/
- `comparative_analyst`: Provides comparative analysis reports via {DATA_OUTPUTS}/comparative_analysis/ (DASV framework)

### Downstream Dependencies
**Commands that consume this command's outputs**:
- `content_publisher`: Consumes evaluation reports for publication quality assurance
- `documentation_owner`: Transforms evaluation results for documentation updates

### Coordination Workflows
**Multi-Command Orchestration**:
```bash
# Sequential evaluation workflow
/fundamental_analyst TICKER
/content_evaluator filename="{DATA_OUTPUTS}/fundamental_analysis/TICKER_YYYYMMDD.md"
/content_publisher ticker=TICKER

# Comparative analysis evaluation workflow
/comparative_analyst/discover ticker_1=AAPL ticker_2=MSFT
/comparative_analyst/synthesize analysis_file="{DATA_OUTPUTS}/comparative_analysis/analysis/AAPL_vs_MSFT_{date}_analysis.json"
/content_evaluator filename="{DATA_OUTPUTS}/comparative_analysis/AAPL_vs_MSFT_YYYYMMDD.md" comparative_validation=true
/content_publisher content_type=comparative_analysis

# Validation workflow
/trade_history action=analyze
/content_evaluator filename="{DATA_OUTPUTS}/trade_history/trading-performance-historical-YYYYMMDD.md"
```

## Post-Execution Protocol

### Required Actions
1. **Generate Output Metadata**: Include evaluation metadata for quality tracking
2. **Store Evaluation Results**: Save to `./{DATA_OUTPUTS}/content_evaluation/` directories
3. **Evidence Documentation**: Maintain evidence matrix with source verification
4. **Quality Validation**: Ensure evaluation meets institutional standards

### Output Metadata Template
```yaml
metadata:
  generated_by: "content-evaluator"
  timestamp: "{ISO-8601-timestamp}"
  target_file: "{source-file}"
  content_type: "content_evaluation"

evaluation_metrics:
  overall_reliability_score: "{score}/10"
  evaluation_confidence: "{confidence}/10"
  evidence_quality: "{primary/secondary/unverified}"
  validation_completeness: true

quality_assurance:
  cli_services_validated: true
  primary_sources_verified: true
  institutional_standards: true
```

## Implementation Notes

**Optimal Usage Scenarios**:
- Investment research requiring regulatory compliance
- Strategic planning with material financial implications
- Due diligence on third-party analysis and recommendations
- Content quality assurance for publication or distribution

**Scaling Considerations**:
- Template structure enables consistent evaluation across analysts
- Benchmarks allow comparison of content quality over time
- Methodology transparency enables audit and refinement
- Evidence requirements scale with decision materiality

---

## Usage Examples

### Basic Usage
```
/content_evaluator filename="{DATA_OUTPUTS}/fundamental_analysis/AAPL_20250718.md"
/content_evaluator filename="{DATA_OUTPUTS}/trade_history/trading-performance-historical-20250718.md"
/content_evaluator filename="{DATA_OUTPUTS}/comparative_analysis/AAPL_vs_MSFT_20250718.md"
```

### Advanced Usage
```
/content_evaluator filename="{DATA_OUTPUTS}/sector_analysis/technology-sector-analysis-20250718.md" evaluation_depth=institutional confidence_threshold=9.5
/content_evaluator filename="{DATA_OUTPUTS}/comparative_analysis/AAPL_vs_MSFT_20250718.md" comparative_validation=true cross_stock_threshold=1%
```

### Validation Enhancement
```
/content_evaluator filename="{DATA_OUTPUTS}/fundamental_analysis/TSLA_20250718.md" validation_focus=financial_data,market_analysis real_time_validation=true
/content_evaluator filename="{DATA_OUTPUTS}/comparative_analysis/MU_vs_DHR_20250730.md" evaluation_depth=institutional template_variant=comparative_analysis
```

---

**Integration with Framework**: This command integrates with the broader Colemorton ecosystem through standardized script registry, template system, CLI service integration, and validation framework protocols.

**Author**: Cole Morton
**Framework**: Content Quality Assessment Framework
**Confidence**: High - Standardized evaluation methodology
**Data Quality**: High - Multi-source validation protocols
