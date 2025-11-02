# 📖 Colemorton User Manual

**Version**: 2.1 | **Last Updated**: 2024-09-07 | **Status**: Active
**Authority**: Documentation Owner | **Audience**: All Users

> **Complete guide to using Colemorton's multi-modal platform for trading analysis, content creation, and AI command collaboration.**

## 🎯 Quick Navigation

- [🚀 Getting Started](#-getting-started)
- [🐍 Python Data Pipeline](#-python-data-pipeline)
- [📊 Trading Analysis](#-trading-analysis)
- [₿ Bitcoin Cycle Intelligence](#-bitcoin-cycle-intelligence)
- [🌐 Frontend Features](#-frontend-features)
- [🔧 Development Tools](#-development-tools)
- [⚙️ Configuration](#-configuration)
- [🔧 Troubleshooting](#-troubleshooting)

---

## 🚀 Getting Started

### System Requirements

- **Node.js**: 18+ for frontend development
- **Python**: 3.9+ for data processing
- **Git**: For version control and collaboration
- **Yarn**: Package manager for frontend dependencies

### Initial Setup

1. **Clone and Install**:
   ```bash
   git clone [repository-url]
   cd colemorton

   # Frontend setup
   cd frontend/
   yarn install

   # Python setup (from root)
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Environment Configuration**:
   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit with your settings
   # Configure API keys and database connections
   ```

3. **Verify Installation**:
   ```bash
   # Test frontend
   cd frontend/
   yarn test

   # Test Python pipeline
   make test

   # Test data pipeline
   make test-pipeline
   ```

### First Run

1. **Start Development Environment**:
   ```bash
   cd frontend/
   yarn dev
   ```

2. **Run Your First Analysis**:
   ```bash
   make dev-pipeline
   ```

3. **Try AI Commands**:
   ```bash
   make test
   ```

---

## 🐍 Python Data Pipeline

> **⭐ FEATURE**: Comprehensive trading analysis pipeline with fundamental analysis, sector analysis, and content generation.

### What is the Data Pipeline?

The Python backend provides a complete trading analysis framework:
- **Multi-Source Data**: Integrates with 18+ financial APIs (Yahoo Finance, Alpha Vantage, SEC Edgar, FRED, etc.)
- **DASV Framework**: Discovery → Analysis → Synthesis → Validation workflow
- **Automated Analysis**: Generates comprehensive fundamental analysis reports
- **Content Generation**: Creates blog posts, social media content, and sector analysis
- **Visualization**: Multi-format dashboard generation with Plotly and Matplotlib

### Quick Start (2 Minutes)

1. **Check Data Pipeline Structure**:
   ```bash
   ls data/outputs/
   # Should show: fundamental_analysis/ sector_analysis/ twitter_post_strategy/
   ```

2. **Run Fundamental Analysis**:
   ```bash
   python scripts/fundamental_analysis/fundamental_analysis.py AAPL
   ```

3. **Generate Dashboard**:
   ```bash
   python scripts/dashboard_generator.py
   ```

### Available Analysis Tools

#### 📊 Fundamental Analysis
| Script | Purpose | Usage |
|--------|---------|-------|
| `fundamental_discovery.py` | Data collection from multiple sources | `python scripts/fundamental_analysis/fundamental_discovery.py AAPL` |
| `fundamental_analysis.py` | Complete analysis pipeline | `python scripts/fundamental_analysis/fundamental_analysis.py AAPL` |
| `analysis_validation.py` | Analysis quality validation | `python scripts/fundamental_analysis/analysis_validation.py` |
| `investment_synthesis.py` | Investment recommendation synthesis | `python scripts/fundamental_analysis/investment_synthesis.py` |

#### 📈 Trading Analysis
| Script | Purpose | Usage |
|--------|---------|-------|
| `comprehensive_trade_analysis.py` | Complete trade analysis | `python scripts/comprehensive_trade_analysis.py` |
| `trade_history_cli.py` | Trading history analysis | `python scripts/trade_history_cli.py` |
| `yahoo_finance_cli.py` | Yahoo Finance data integration | `python scripts/yahoo_finance_cli.py AAPL` |

#### 🎨 Content & Visualization
| Script | Purpose | Usage |
|--------|---------|-------|
| `dashboard_generator.py` | Multi-format dashboard generation | `python scripts/dashboard_generator.py` |
| `generate_trade_history_images.py` | Trading chart generation | `python scripts/generate_trade_history_images.py` |

📚 **Full Guide**: See individual script documentation and `templates/` directory for analysis templates.

---

## 🔧 DASV Framework & Sub-Agent Architecture

> **⭐ NEW FEATURE**: Institutional-grade analysis framework with universal sub-agent delegation pattern.

### Framework Overview

The **DASV (Discovery → Analyze → Synthesize → Validate)** Framework provides systematic progression from raw data to validated analysis outputs with institutional-grade quality standards (≥9.0/10.0 confidence).

**Core Documentation**:
- **Framework Specification**: `.claude/DASV_Framework_Specification.md` - Complete framework architecture and implementation guidelines
- **Implementation Summary**: `.claude/DASV_Implementation_Summary.md` - Current status and optimization results

### Sub-Agent Trilogy

**Researcher Sub-Agent** (`.claude/agents/researcher.md`):
- **Purpose**: Data collection and discovery phase execution
- **Capabilities**: Multi-source validation, CLI service orchestration, institutional quality enforcement
- **Usage**: Automatically handles all `*_discover` command implementations

**Analyst Sub-Agent** (`.claude/agents/analyst.md`):
- **Purpose**: Statistical analysis and insights generation
- **Capabilities**: Financial health assessment, risk quantification, validation enhancement
- **Usage**: Automatically handles all `*_analyze` command implementations

**Synthesist Sub-Agent** (`.claude/agents/synthesist.md`):
- **Purpose**: Publication-ready document generation
- **Capabilities**: Template integration, professional presentation, evidence integration
- **Usage**: Automatically handles all `*_synthesize` command implementations

### Analysis Domains

The framework supports 6 analysis domains with **56% complexity reduction** achieved through sub-agent delegation:

| Domain | Purpose | Template Location | Status |
|--------|---------|-------------------|--------|
| **Fundamental Analysis** | Company financial health | `./templates/analysis/fundamental_analysis_template.md` | ✅ Optimized |
| **Sector Analysis** | 11-sector ETF framework | `./templates/analysis/sector_analysis_template.md` | ✅ Optimized |
| **Industry Analysis** | Competitive landscape | `./templates/analysis/industry_analysis_template.md` | ✅ Optimized |
| **Macro Analysis** | Business cycle assessment | `./templates/analysis/macro_analysis_template.md` | ✅ Optimized |
| **Comparative Analysis** | Winner/loser determination | `./templates/analysis/comparative_analysis_template.md` | ✅ Optimized |
| **Trade History** | Performance tracking | `./templates/analysis/trade_history_template.md` | ✅ Optimized |

### Quality Standards

**Universal Quality Tiers**:
- **Institutional Excellence** (≥9.5): Premium grade, publication-ready
- **Institutional Standard** (≥9.0): Professional analysis baseline
- **Professional Standard** (≥8.0): Internal analysis minimum

**Enhancement Protocol**: When validation files exist, sub-agents automatically target 9.5+ confidence scores through systematic optimization.

### File Organization

```
data/outputs/{analysis_type}/
├── {IDENTIFIER}_{YYYYMMDD}.md                          # Synthesis output
├── discovery/{IDENTIFIER}_{YYYYMMDD}_discovery.json    # Discovery data
├── analysis/{IDENTIFIER}_{YYYYMMDD}_analysis.json      # Analysis insights
└── validation/{IDENTIFIER}_{YYYYMMDD}_validation.json  # Validation assessment
```

**Usage Examples**:
```bash
# Run discovery phase (handled by researcher sub-agent)
/fundamental_analyst_discover ticker=AAPL confidence_threshold=0.9

# Run analysis phase (handled by analyst sub-agent)
/fundamental_analyst_analyze analysis_file=data/outputs/fundamental_analysis/discovery/AAPL_20250811_discovery.json

# Run synthesis phase (handled by synthesist sub-agent)
/fundamental_analyst_synthesize analysis_file=data/outputs/fundamental_analysis/analysis/AAPL_20250811_analysis.json
```

---

## 📊 Trading Analysis

### Data Processing Pipeline

Colemorton provides a complete trading analysis framework:

#### 1. Data Extraction
```bash
# Extract market data for specific symbols
make extract-data ENV=prod

# Quick development extraction
make quick-extract
```

**What it does**: Downloads market data, applies technical indicators, validates data quality.

#### 2. Feature Engineering
```bash
# Process extracted data
make process-data

# Quick processing for development
make quick-process
```

**What it does**: Generates technical indicators, calculates features, prepares data for analysis.

#### 3. Strategy Development
```bash
# Train trading models
make train-model

# Full pipeline (extract → process → train)
make full-pipeline
```

**What it does**: Develops trading strategies, backtests performance, generates model files.

#### 4. Report Generation
```bash
# Create analysis reports
make generate-report

# Environment-specific
make prod-pipeline
```

**What it does**: Creates comprehensive analysis reports with interactive Plotly visualizations, multi-format dashboard exports, and performance summaries.

### Configuration Files

All trading analysis is configuration-driven:

#### Data Sources (`config/pipelines/data_extraction.yaml`)
```yaml
symbols: ["AAPL", "GOOGL", "TSLA"]
timeframe: "1d"
indicators: ["SMA", "EMA", "RSI", "MACD"]
```

#### Strategy Parameters (`config/pipelines/model_training.yaml`)
```yaml
strategy_type: "momentum"
lookback_period: 20
risk_tolerance: 0.02
```

#### Environment Settings (`config/environments/`)
- `dev.yaml` - Development settings
- `staging.yaml` - Testing environment
- `prod.yaml` - Production parameters

### Output Structure

All analysis outputs are organized in `data/outputs/`:
```
data/outputs/
├── fundamental_analysis/  # Fundamental analysis results
├── sector_analysis/      # Sector-specific analysis
├── reports/             # Analysis reports (HTML, PDF, Markdown)
├── visualizations/      # Interactive Plotly charts (PNG, PDF, SVG, HTML)
├── dashboards/          # Performance dashboards with multi-format export
├── frontend_configs/    # JSON configurations for React integration
├── exports/            # Data exports (CSV, JSON, Parquet)
└── logs/              # Execution logs
```

### AI-Enhanced Analysis

Use AI commands to enhance your trading analysis:

```bash
# Analyze strategy performance
> "/architect - analyze the momentum strategy backtest results"

# Create social content about performance
> "/twitter-post-strategy - post about our AAPL analysis results"

# Prioritize strategy improvements
> "/product-owner - prioritize trading strategy enhancements"
```

---

## ₿ Bitcoin Cycle Intelligence

> **⭐ FEATURE**: Advanced Bitcoin cycle analysis with on-chain data integration and institutional-grade cycle intelligence.

### What is Bitcoin Cycle Intelligence?

The Bitcoin Cycle Intelligence system provides comprehensive Bitcoin analysis through the DASV framework:
- **On-Chain Analytics**: Integrates with 80+ Bitcoin data sources including Mempool.space, CoinMetrics, Glassnode
- **Cycle Indicators**: MVRV Z-Score, PI Cycle Top, NUPL zones, Reserve Risk assessment
- **Network Health**: Hash rate analysis, mining economics, network security metrics
- **Economic Context**: Federal Reserve policy impact, global liquidity positioning
- **Multi-Source Validation**: Cross-validation across free tier Bitcoin data sources

### Quick Start (5 Minutes)

#### 1. Discovery Phase - Gather Bitcoin Data
```bash
# Discovery phase - gather comprehensive Bitcoin on-chain data
> "Think like a Bitcoin technical specialist and run the discover phase for Bitcoin cycle analysis"

# Or with specific parameters
> "Run cli_enhanced_bitcoin_cycle_intelligence_discover with analysis date 2025-09-04"
```

**What it does**: Collects Bitcoin on-chain data, market prices, cycle indicators, network health metrics, and institutional flows.

#### 2. Analysis Phase - Cycle Intelligence
```bash
# Analysis phase - comprehensive cycle indicators analysis
> "Analyze the Bitcoin discovery data using the cycle intelligence framework"

# Or with confidence threshold
> "Run cli_enhanced_bitcoin_cycle_intelligence_analyze with confidence threshold 0.9"
```

**What it does**: Calculates MVRV Z-Score, PI Cycle signals, LTH behavior, Rainbow Price Model positioning, NUPL zones, and Reserve Risk opportunities.

#### 3. Synthesis Phase - Intelligence Report
```bash
# Synthesis phase - generate Bitcoin Cycle Intelligence Report
> "Generate a comprehensive Bitcoin Cycle Intelligence Report from the analysis data"

# Or with specific depth
> "Run cli_enhanced_bitcoin_cycle_intelligence_synthesize with institutional depth"
```

**What it does**: Creates institutional-grade Bitcoin intelligence reports with cycle thesis, strategic recommendations, and risk assessment.

#### 4. Validation Phase - Quality Assurance
```bash
# Validation phase - ensure institutional quality
> "Validate the Bitcoin intelligence report with >9.5/10 confidence requirement"
```

**What it does**: Multi-source validation, confidence scoring verification, and quality assurance for institutional standards.

### Expected Output Structure

All Bitcoin analysis outputs are organized in `data/outputs/bitcoin_cycle_intelligence/`:

```
data/outputs/bitcoin_cycle_intelligence/
├── discovery/
│   └── bitcoin_cycle_20250904_discovery.json     # On-chain data collection
├── analysis/
│   └── bitcoin_cycle_20250904_analysis.json      # Cycle indicators analysis
├── bitcoin_cycle_20250904.md                     # Intelligence report
└── validation_report_20250904.json               # Quality assurance
```

### Key Bitcoin Cycle Indicators

#### MVRV Z-Score Analysis
- **Purpose**: Identify market cycle extremes (euphoria vs capitulation zones)
- **Ranges**: -2 to +7 with zone classifications
- **Usage**: Accumulation opportunities at low scores, distribution signals at high scores

#### PI Cycle Top Indicator
- **Purpose**: Identify potential cycle tops with historical accuracy
- **Mechanism**: 111-day MA vs 350-day MA × 2 crossover
- **Track Record**: High accuracy in identifying Bitcoin cycle peaks

#### NUPL (Net Unrealized Profit/Loss) Zones
- **Purpose**: Assess market sentiment through holder profit/loss analysis
- **Zones**: Capitulation → Hope → Optimism → Belief → Euphoria → Greed
- **Application**: Strategic positioning based on market psychology

#### Reserve Risk Assessment
- **Purpose**: Evaluate long-term holder conviction and accumulation opportunities
- **Calculation**: Price/HODL Bank ratio analysis
- **Insight**: Lower values indicate stronger accumulation opportunities

### CLI Services Integration

Bitcoin Cycle Intelligence integrates with multiple data sources:

#### Free Tier Services (Recommended)
```yaml
Primary Data Sources:
  - CoinGecko API: Comprehensive Bitcoin market data (50 calls/month free)
  - Mempool.space API: Bitcoin blockchain and mempool analysis (free)
  - CoinMetrics API: Institutional-grade network metrics (free tier)
  - Alternative.me API: Fear & Greed sentiment index (free)
  - Blockchain.com API: Bitcoin network statistics (free)
```

#### Enhanced Services (Paid Tiers)
```yaml
Advanced Analytics:
  - Glassnode: Advanced on-chain analytics ($29/month)
  - Whale Alert: Large transaction monitoring (paid)
  - Hashrate Index: Mining industry analytics (mixed pricing)
```

### Configuration and Customization

#### Analysis Parameters
```bash
# Discovery phase options
--analysis-date: Target date for analysis (YYYY-MM-DD)
--services: Comma-separated list of CLI services to use
--data-quality-threshold: Minimum data quality score (0.8-1.0)

# Analysis phase options
--confidence-threshold: Minimum confidence for conclusions (0.8-1.0)
--cycle-indicators: Enable comprehensive cycle analysis (true/false)
--valuation-framework: Enable Bitcoin valuation models (true/false)
--risk-quantification: Enable Bitcoin-specific risk matrices (true/false)

# Synthesis phase options
--synthesis-depth: Analysis complexity (institutional/comprehensive/executive)
--economic-context: Integrate macro intelligence (true/false)
--cycle-scenario-count: Number of scenarios to analyze (3/5/7)
```

### AI-Enhanced Bitcoin Analysis

Use AI commands to enhance your Bitcoin analysis:

```bash
# Analyze current Bitcoin cycle position
> "/architect - analyze Bitcoin's current cycle phase using MVRV and PI Cycle indicators"

# Create social content about Bitcoin analysis
> "/twitter-post - share our Bitcoin cycle analysis insights"

# Compare with historical cycles
> "/researcher - compare current Bitcoin cycle with 2017 and 2021 patterns"

# Risk assessment focus
> "/analyst - assess Bitcoin network security risks and hash rate concentration"
```

### Quality Standards

Bitcoin Cycle Intelligence maintains institutional-grade quality:

**Data Validation:**
- ✅ Multi-source price validation (≤2% tolerance)
- ✅ Cross-validation across 5+ Bitcoin services
- ✅ Real-time service health monitoring
- ✅ Data quality scoring ≥0.9 for institutional grade

**Analysis Standards:**
- ✅ Confidence threshold ≥0.8 for all components
- ✅ Evidence-backed cycle assessments
- ✅ Historical accuracy validation
- ✅ Risk-adjusted recommendations

**Report Quality:**
- ✅ Institutional-grade presentation format
- ✅ Multi-model valuation triangulation
- ✅ Comprehensive risk quantification
- ✅ Strategic positioning framework

---

## 🌐 Frontend Features

### Blog and Content Management

The Astro-powered frontend provides:

#### Multi-Author Blog System
- **Content Types**: Blog posts, pages, author profiles
- **Authoring**: Markdown/MDX with custom shortcodes
- **Organization**: Categories, tags, series support
- **SEO**: Automatic meta tags, sitemaps, RSS feeds

#### Theme System
- **Dark/Light Mode**: Automatic or manual toggle
- **Responsive Design**: Mobile-first with TailwindCSS
- **Customization**: Theme settings in `src/config/theme.json`

#### Interactive Features
- **Search**: Full-text search across all content
- **Comments**: Disqus integration
- **Analytics**: Google Tag Manager support
- **Social Sharing**: Automatic social media cards

### Development Workflow

#### Content Creation
```bash
cd frontend/

# Start development server
yarn dev

# Create new blog post
# Add file to src/content/blog/my-new-post.md

# Generate optimized builds
yarn build
```

#### Configuration Management
```bash
# Generate JSON configs from YAML
yarn generate-json

# Update all configurations
yarn format

# Type checking
yarn check
```

#### Testing and Quality
```bash
# Run tests
yarn test
yarn test:watch
yarn test:coverage

# Code quality
yarn lint
yarn format
yarn pre-commit
```

### Content Integration with Trading Analysis

The frontend automatically integrates with your trading analysis:

1. **Analysis Reports**: Automatically displayed in blog format
2. **Interactive Visualizations**: Plotly charts with hover, zoom, and pan capabilities
3. **Dashboard Integration**: Performance dashboards exported in multiple formats
4. **Frontend Components**: JSON schema configurations for React chart components
5. **Performance Updates**: AI-generated content from trading results
6. **Social Media**: Auto-generated posts about trading performance

### Configuration Files

#### Site Settings (`src/config/config.json`)
```json
{
  "title": "Colemorton Trading Analysis",
  "description": "Multi-modal trading strategy platform",
  "author": "Your Name",
  "social": {
    "twitter": "@yourhandle"
  }
}
```

#### Navigation (`src/config/menu.json`)
```json
{
  "main": [
    {"name": "Blog", "url": "/blog"},
    {"name": "Analysis", "url": "/analysis"},
    {"name": "About", "url": "/about"}
  ]
}
```

---

## 🔧 Development Tools

### Python Development

#### Quality Assurance
- **Code Formatting**: `make format` (black, isort)
- **Linting**: `make lint` (flake8, mypy, bandit)
- **Testing**: `make test` (pytest with coverage)
- **Pre-commit Hooks**: Automated quality checks on commit

#### Available Make Commands
```bash
# Development workflow
make format              # Format Python code with black/isort
make lint               # Run linting with flake8
make test               # Run Python tests with pytest
make generate-dashboard # Generate trading dashboards

# Pipeline commands
make dev-pipeline       # Development data pipeline
make validate-caching   # Validate data caching system
```

### Frontend Development

#### Available Commands
```bash
# Development workflow
yarn dev               # Start development server
yarn build            # Production build
yarn test             # Run test suite
yarn lint             # ESLint with auto-fix
yarn check            # TypeScript checking

# Content management
yarn generate-json    # Generate JSON configs from YAML
yarn format          # Format code with Prettier
```

### Data Analysis Workflow

#### Complete Analysis Pipeline
```bash
# Step 1: Data Discovery
python scripts/fundamental_analysis/fundamental_discovery.py AAPL

# Step 2: Analysis
python scripts/fundamental_analysis/fundamental_analysis.py AAPL

# Step 3: Validation
python scripts/fundamental_analysis/analysis_validation.py AAPL_20250715.md

# Step 4: Dashboard Generation
python scripts/dashboard_generator.py
```

#### Content Creation
```bash
# Generate trading analysis content
python scripts/comprehensive_trade_analysis.py

# Create social media content
# Results automatically saved to data/outputs/twitter_post_strategy/
```

---

## ⚙️ Configuration

### Environment Configuration

#### Development Environment
```bash
# .env.development
NODE_ENV=development
API_BASE_URL=http://localhost:3000
LOG_LEVEL=debug
```

#### Production Environment
```bash
# .env.production
NODE_ENV=production
API_BASE_URL=https://api.colemorton.com
LOG_LEVEL=info
```

### Trading Analysis Configuration

#### Data Sources (`config/pipelines/data_extraction.yaml`)
```yaml
metadata:
  name: "Market Data Pipeline"
  version: "1.0.0"

input:
  api:
    endpoint: "https://api.tradingview.com/data"
    symbols: ["AAPL", "GOOGL", "TSLA"]
    timeframe: "1d"

output:
  file_path: "data/raw/market_data_{timestamp}.parquet"
  format: "parquet"

processing:
  indicators: ["SMA", "EMA", "RSI", "MACD"]
  validation: true
```

#### Strategy Parameters (`config/pipelines/model_training.yaml`)
```yaml
strategy:
  type: "momentum"
  parameters:
    lookback_period: 20
    signal_threshold: 0.02
    risk_management:
      max_position_size: 0.1
      stop_loss: 0.05
      take_profit: 0.15

backtesting:
  start_date: "2023-01-01"
  end_date: "2024-01-01"
  initial_capital: 100000
```

### Frontend Configuration

#### Site Configuration (`frontend/src/config/config.json`)
```json
{
  "site": {
    "title": "Colemorton",
    "description": "Multi-modal trading analysis platform",
    "author": "Cole Morton",
    "url": "https://colemorton.com"
  },
  "features": {
    "darkMode": true,
    "search": true,
    "comments": false,
    "analytics": true
  },
  "social": {
    "twitter": "@colemorton",
    "github": "colemorton/platform"
  }
}
```

#### Theme Settings (`frontend/src/config/theme.json`)
```json
{
  "colors": {
    "primary": "#3b82f6",
    "secondary": "#64748b",
    "accent": "#f59e0b"
  },
  "typography": {
    "headingFont": "Heebo",
    "bodyFont": "Heebo"
  },
  "layout": {
    "maxWidth": "1280px",
    "sidebar": true
  }
}
```

### AI Command Configuration

#### Data Output Structure (`data/outputs/`)
```yaml
analysis_outputs:
  fundamental_analysis:
    location: "data/outputs/fundamental_analysis/"
    format: "json, markdown"
    status: "active"
  sector_analysis:
    location: "data/outputs/sector_analysis/"
    format: "json, markdown"
    status: "active"

command_integration:
  data_sources: ["data/outputs/fundamental_analysis/", "data/outputs/sector_analysis/"]
  output_format: "markdown, json"
```

#### Template System (`templates/` and `scripts/templates/`)

**Hybrid Template System**: Colemorton uses a sophisticated hybrid template system that combines authoritative markdown specifications with functional Jinja2 implementations:

```yaml
template_architecture:
  authoritative_specifications:
    location: "templates/analysis/"
    files:
      - "fundamental_analysis_template.md"  # 476 lines of institutional requirements
      - "sector_analysis_template.md"       # 709 lines with sector customization
    purpose: "Complete methodology, validation rules, and compliance standards"

  functional_implementations:
    location: "scripts/templates/"
    files:
      - "fundamental_analysis_enhanced.j2"   # Jinja2 template with inheritance
      - "sector_analysis_enhanced.j2"        # Sector-specific Jinja2 template
    features:
      - "Template inheritance and shared components"
      - "40-50% reduction in template duplication"
      - "Dynamic content generation with confidence scoring"

  shared_components:
    location: "scripts/templates/shared/"
    files:
      - "base_analysis_template.j2"          # Common structure and blocks
      - "macros/*.j2"                        # Reusable components
    benefits:
      - "Economic sensitivity matrices"
      - "Risk assessment frameworks"
      - "Confidence scoring systems"
      - "Data quality validation"
```

**Usage Patterns**:

1. **Command Files** reference markdown specifications:
   ```bash
   # Commands use authoritative specifications for compliance
   fundamental_analyst_synthesize.md -> templates/analysis/fundamental_analysis_template.md
   sector_analyst_synthesize.md -> templates/analysis/sector_analysis_template.md
   ```

2. **CLI Tools** use Jinja2 implementations:
   ```bash
   # Content Automation CLI renders using enhanced templates
   python scripts/content_automation_cli.py analysis --type fundamental
   python scripts/content_automation_cli.py analysis --type sector
   ```

3. **Validation** against authoritative standards:
   ```bash
   # Validation commands check against markdown specifications
   fundamental_analyst_validate.md -> validates template compliance
   sector_analyst_validate.md -> validates sector customization rules
   ```

**Template Features**:

- **Institutional Quality**: 0.9+ confidence baseline, multi-source validation
- **Economic Integration**: FRED indicators, GDP/employment correlations
- **Risk Quantification**: Probability/impact matrices with monitoring KPIs
- **Cross-Sector Analysis**: Complete 11-sector relative positioning
- **CLI Integration**: 7-source data validation (Yahoo Finance, Alpha Vantage, FMP, FRED, SEC EDGAR, CoinGecko, IMF)
- **Compliance Framework**: Template validation checklist and quality gates

**Development Workflow**:

1. **Specifications** (markdown files): Define methodology and requirements
2. **Implementation** (Jinja2 files): Functional templates with inheritance
3. **Commands** reference specifications for institutional compliance
4. **CLI** uses implementations for efficient document generation
5. **Validation** ensures output meets specification standards

---

## 🔧 Troubleshooting

### Common Issues

#### Frontend Issues

**Issue**: Development server won't start
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
cd frontend/
rm -rf node_modules yarn.lock
yarn install

# Check for port conflicts (Astro dev server)
lsof -i :4321
```

**Issue**: Build failures
```bash
cd frontend/

# Check TypeScript errors
yarn check

# Run linting
yarn lint

# Build with verbose output
yarn build --verbose
```

#### Trading Analysis Issues

**Issue**: Data extraction fails
```bash
# Check API credentials
cat .env | grep API

# Validate configuration
make validate-configs

# Check network connectivity
ping api.tradingview.com
```

**Issue**: Pipeline execution errors
```bash
# Check Python environment
python --version  # Should be 3.9+
pip list | grep pandas

# Run individual steps
make extract-data
make process-data
make train-model
```

#### Python Data Pipeline Issues

**Issue**: Analysis scripts not working
```bash
# Check Python environment
python --version  # Should be 3.9+
pip list | grep pandas

# Verify data pipeline structure
ls data/outputs/
ls data/outputs/*/

# Test individual components
python scripts/fundamental_analysis/fundamental_discovery.py AAPL
```

**Issue**: Missing analysis outputs
```bash
# Check data outputs directory
ls data/outputs/fundamental_analysis/
ls data/outputs/sector_analysis/

# Verify recent analysis runs
find data/outputs -name "*.json" -mtime -1

# Run analysis pipeline
make dev-pipeline
```

### Performance Optimization

#### Frontend Performance
```bash
# Optimize images
yarn build --analyze

# Check bundle size
yarn build && ls -la dist/

# Lighthouse audit
yarn preview  # Then run Lighthouse on localhost:4321
```

#### Trading Analysis Performance
```bash
# Parallel execution
make -j4 full-pipeline

# Profile execution
time make extract-data

# Optimize data processing
# Edit config/pipelines/feature_engineering.yaml to reduce indicators
```

#### Data Pipeline Performance
```bash
# Check data pipeline outputs
ls -la data/outputs/*/

# Monitor analysis output freshness
find data/outputs -name "*.json" -mtime -1

# Profile script execution
time python scripts/fundamental_analysis/fundamental_analysis.py AAPL
```

### Getting Help

#### Log Files
- **Frontend**: Browser developer tools console
- **Trading Analysis**: `data/outputs/logs/`
- **Python Scripts**: Check terminal output and error messages

#### Debug Information
```bash
# System information
python --version
node --version
yarn --version

# Analysis data status
ls -la data/outputs/*/
cat data/outputs/fundamental_analysis/*/analysis.json
```

#### Contact Support
- **GitHub Issues**: [Repository issues page]
- **Documentation**: This manual and inline code documentation
- **Community**: [Discord/Slack if available]

---

## 📚 Additional Resources

- **[Python Scripts Documentation](../scripts/)**: Complete guide to Python analysis tools
- **[Technical Documentation](01-project-overview.md)**: Detailed technical implementation
- **[API Reference](../docs/API.md)**: Trading analysis API documentation
- **[Contributing Guide](../CONTRIBUTING.md)**: How to contribute to the project

---

**🎉 You're ready to use Colemorton!** This platform combines powerful trading analysis with intelligent AI collaboration to deliver superior insights and content. Start with the Quick Start guide above, then explore the advanced features as you become comfortable with the system.
