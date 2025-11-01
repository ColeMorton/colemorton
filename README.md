[![Netlify Status](https://api.netlify.com/api/v1/badges/f076302a-1a27-49d4-a2b9-0bfa3a5c84af/deploy-status)](https://app.netlify.com/projects/colemorton/deploys)

# Cole Morton - Personal Website & Trading Analysis Platform

**Modern Astro-based personal website with integrated Python data processing for financial analysis, dashboard generation, and AI-powered content creation.**

**Version**: 2.0.0 | **Last Updated**: 2025-08-12 | **Health Score**: 8.5/10 | **GenContentOps Maturity**: 9.2/10 | **Status**: Active

---

## 🎯 Platform Overview

This is Cole Morton's personal website and blog platform, built with modern web technologies and enhanced with **enterprise-grade GenContentOps (Generative Content Operations)** capabilities. The platform combines a sleek Astro frontend with sophisticated AI orchestration systems that enable automated financial analysis, content generation, and interactive dashboards at institutional quality standards.

### Core Capabilities

- **🏠 Personal Website**: Modern blog platform with dynamic content management
- **🚀 GenContentOps Platform**: 21-command AI orchestration system with enterprise-grade content generation
- **📊 DASV Framework**: Discovery-Analyze-Synthesize-Validate workflow with institutional quality standards
- **🤖 Multi-Tier AI Integration**: Infrastructure, Product, Microservices, and Sub-agent command layers
- **📈 Advanced Dashboard Generation**: Dual-engine visualization with Plotly/Matplotlib and automated export
- **🔄 Contract-Driven Data Pipeline**: Automatic service orchestration with 18+ financial API integrations
- **⚡ Modern Frontend**: Astro 5.12+ with React 19, TailwindCSS 4, and TypeScript

---

## 🏗️ Architecture & Tech Stack

### Frontend Excellence
**Modern Static Site Generation with Dynamic Capabilities**

```
frontend/                           # Astro Frontend Platform
├── src/
│   ├── content/                   # Content collections (blog, pages, dashboards)
│   ├── layouts/                   # Astro layout components
│   └── components/                # React + TypeScript components
├── public/                        # Static assets and images
└── scripts/                       # Build and deployment automation
```

**Technology Stack:**
- **Astro 5.12.8** - Latest static site generation with islands architecture
- **React 19.1.0** - Modern React with concurrent features
- **TailwindCSS 4.1.4** - Latest utility-first CSS framework
- **TypeScript 5.8.3** - Full type safety across the platform
- **Plotly.js 3.0.1** - Interactive data visualization

### Backend Data Processing
**Python-Powered Analytics Engine**

```
scripts/                           # Python Data Processing Engine
├── fundamental_analysis/          # Financial analysis workflows
├── utils/                        # Shared utilities and chart generators
├── services/                     # API integrations (Yahoo Finance, Alpha Vantage, etc.)
├── templates/                    # Jinja2 templates for content generation
└── tests/                        # Testing framework and validation
```

**Python Stack:**
- **Python 3.9+** with modern dependency management
- **Pandas 2.0+** - Advanced data manipulation and analysis
- **Plotly 6.1+** - Interactive visualization generation
- **SQLAlchemy 2.0+** - Database connectivity and ORM
- **Requests** - API integration for financial data sources

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** for frontend development
- **Python 3.9+** for data processing
- **Yarn** package manager
- **Git** for version control

### Setup Instructions

1. **Clone and Install Dependencies**
   ```bash
   git clone https://github.com/ColeMorton/colemorton.git
   cd colemorton

   # Frontend setup
   cd frontend/
   yarn install

   # Python setup (from root)
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Environment Configuration**
   ```bash
   # Copy environment template (if available)
   cp .env.example .env

   # Configure API keys for financial data sources
   # Edit .env with your API keys for Yahoo Finance, Alpha Vantage, etc.
   ```

3. **Development Servers**
   ```bash
   # Frontend development server
   cd frontend/
   yarn dev                    # Starts Astro dev server at localhost:4321

   # Python data processing (from root)
   make install               # Install Python dependencies
   make test                  # Run test suite
   ```

---

## 📊 Key Features

### 1. **Personal Website & Blog**
- Modern Astro-based static site with dynamic content
- Responsive design with TailwindCSS 4
- Blog posts, calculators, and interactive dashboards
- SEO-optimized with automatic sitemap generation

### 2. **Trading Analysis System**
- **Fundamental Analysis**: Comprehensive financial metrics and ratios
- **Data Visualization**: Interactive charts with Plotly.js
- **Multi-Source Data**: Integration with financial APIs (Yahoo Finance, Alpha Vantage, FMP)
- **Report Generation**: Automated markdown reports with embedded visualizations

### 3. **Dashboard Generation**
- **Photo Booth System**: Automated screenshot generation of dashboard content
- **Multiple Formats**: PNG, PDF, SVG export capabilities
- **Theme Support**: Light and dark mode dashboard generation
- **Responsive Layouts**: Optimized for different screen sizes and aspect ratios

### 4. **AI Command Integration**
- **Claude Commands**: Integrated AI assistance for content creation and analysis
- **Content Generation**: Automated blog post and social media content creation
- **Analysis Automation**: AI-powered financial analysis and reporting
- **Documentation Management**: Automated documentation generation and maintenance

---

## 🚀 GenContentOps Architecture

### Enterprise-Grade Content Orchestration System

This platform implements a sophisticated **GenContentOps (Generative Content Operations)** framework that represents enterprise-level AI orchestration capabilities. The system demonstrates production-scale content generation with institutional quality standards.

#### DASV Framework Implementation

**Discovery-Analyze-Synthesize-Validate Workflow:**

```
📊 Discovery Phase
├── Multi-API data collection (18+ financial services)
├── Schema validation and quality assessment
└── Confidence scoring and metadata generation

🔍 Analysis Phase
├── Cross-validation with multiple data sources
├── Risk quantification and valuation modeling
└── Economic context integration

📝 Synthesis Phase
├── Intelligent template selection
├── Multi-format content generation (blog, social, visual)
└── Compliance validation and disclaimers

✅ Validation Phase
├── Institutional quality standards (9.0+ confidence)
├── Multi-tier quality gates and error checking
└── Audit trail and metadata documentation
```

#### Production Scale Evidence

**Content Generation at Scale:**
- **100+ Fundamental Analysis** reports with complete DASV processing
- **Multi-Format Outputs**: Markdown, JSON, validation results, visualizations
- **Institutional Quality**: 9.0+ confidence thresholds with compliance standards
- **Active Production**: Continuous content generation through August 2025

#### Quality Assurance Framework

```python
# Institutional-grade validation standards
quality_thresholds = {
    "institutional_minimum": 9.0,
    "publication_minimum": 8.5,
    "accuracy_minimum": 9.5,
    "compliance_minimum": 9.5
}
```

**Quality Gates:**
- **Content Structure**: Format compliance and required elements
- **Accuracy Standards**: Cross-API validation within 2% variance
- **Compliance Framework**: Investment disclaimers and risk warnings
- **Engagement Optimization**: Social media performance validation

---

## 🤖 AI Command System

The platform integrates with Claude AI through a sophisticated AI agent (Claude Command) orchestration system located in `.claude/commands/`:

### Available Commands

| Command | Purpose | Status |
|---------|---------|---------|
| `fundamental_analyst.md` | Comprehensive financial analysis automation | ✅ Active |
| `content_publisher.md` | Blog post and content creation | ✅ Active |
| `documentation_owner.md` | Documentation management and organization | ✅ Active |
| `twitter.md` | Social media content generation | ✅ Active |
| `sector_analyst.md` | Market sector analysis | ✅ Active |
| `industry_analyst.md` | Industry-specific analysis | ✅ Active |

### Command Usage
```bash
# Example: Generate fundamental analysis
/fundamental_analyst AAPL

# Example: Create blog content
/content_publisher --topic "Market Analysis" --format blog

# Example: Generate social media content
/twitter --analysis-file "data/outputs/fundamental_analysis/AAPL_20250812.md"
```

---

## 💻 Development Workflow

### Frontend Development
```bash
cd frontend/
yarn dev                    # Development server
yarn build                  # Production build
yarn test                   # Run test suite
yarn lint                   # ESLint with auto-fix
yarn check                  # TypeScript checking
```

### Python Data Processing
```bash
# Analysis pipelines
make full-pipeline          # Complete data processing pipeline
make generate-dashboard     # Generate dashboard visualizations
make test                   # Run Python test suite

# Development shortcuts
make quick-dashboard        # Quick dashboard generation for development
make clean                  # Clean generated files
make format                 # Code formatting with black + isort
make lint                   # Code linting with flake8
```

### Quality Assurance
- **Pre-commit Hooks**: Automated code quality checks (black, isort, flake8, ESLint)
- **Type Safety**: Full TypeScript coverage on frontend, Python type hints
- **Testing**: Comprehensive test suites for both frontend and backend
- **Security**: Automated dependency vulnerability scanning

---

## 📚 Documentation

Comprehensive documentation is available with our newly organized structure:

### Quick Navigation
- **[📖 Complete User Manual](docs/01-user-manual.md)** - Comprehensive usage guide
- **[🎯 Quick Start Guide](docs/01-quick-start-guide.md)** - 5-minute setup
- **[🏗️ System Architecture](docs/02-data-architecture.md)** - Technical architecture overview
- **[🤖 AI Content Synthesis](docs/03-ai-content-synthesis-guide.md)** - AI integration guide
- **[⚙️ Development Standards](docs/03-development-standards.md)** - Code quality and best practices
- **[🎛️ Command System Guide](docs/05-command-system-guide.md)** - AI command development

### Documentation Hub
- **[📑 Master Index](docs/00-index.md)** - Complete documentation navigation with user journey guides
- **25 organized documents** covering all aspects of the platform
- **User journey guides** for beginners, developers, and content creators
- **Cross-referenced** with consistent naming and structure

---

## 📈 Data Processing Pipeline

### Supported Data Sources
- **Yahoo Finance** - Market data, financials, and pricing
- **Alpha Vantage** - Technical indicators and market data
- **Financial Modeling Prep (FMP)** - Fundamental analysis data
- **FRED Economic Data** - Macroeconomic indicators
- **SEC EDGAR** - Corporate filings and reports

### Analysis Capabilities
- **Fundamental Analysis**: Financial ratios, valuation models, growth metrics
- **Technical Analysis**: Chart patterns, indicators, price action
- **Sector Analysis**: Industry comparisons and sector rotation analysis
- **Portfolio Analysis**: Performance tracking and risk assessment
- **Macro Analysis**: Economic indicators and market correlations

### Visualization Features
- **Interactive Charts**: Plotly-powered interactive visualizations
- **Dashboard Export**: Multi-format export (PNG, PDF, SVG)
- **Theme Support**: Professional light and dark themes
- **Responsive Design**: Optimized for desktop, tablet, and mobile viewing

---

## 🏃‍♂️ Project Scripts & Automation

### Frontend Scripts
```bash
# Content generation
yarn generate-json         # Generate JSON data from markdown
yarn generate-pages        # Generate dynamic pages

# Photo booth system
yarn photo-booth:generate   # Generate dashboard screenshots
yarn photo-booth:export    # Export dashboards with custom settings

# Development utilities
yarn flags:sync            # Sync feature flags
yarn data:pipeline         # Run data processing pipeline
yarn sanitize-build        # Clean and optimize build output
```

### Python Scripts
```bash
# Core analysis scripts
python scripts/comprehensive_trade_analysis.py
python scripts/dashboard_generator.py
python scripts/fundamental_analysis/fundamental_analysis.py

# Utility scripts
python scripts/cache_optimization.py
python scripts/test_dependencies.py
python scripts/validate_templates.py
```

---

## 🔧 Configuration & Environment

### Environment Variables
```bash
# API Configuration
YAHOO_FINANCE_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/db

# Application Settings
NODE_ENV=development
LOG_LEVEL=INFO
```

### Configuration Files
- **`config/`** - Environment-specific configurations
- **`frontend/src/content.config.ts`** - Content collection schemas
- **`scripts/script_config.py`** - Python script configuration management

---

## 🚀 Deployment

### Frontend Deployment (Netlify)
The frontend is automatically deployed to Netlify with the following pipeline:
```bash
yarn build                 # Production build with optimizations
yarn sanitize-build        # Security hardening and cleanup
netlify deploy --prod      # Atomic deployment with rollback capability
```

### Python Services
Backend processing can be containerized for scalable deployment:
```bash
docker build -t colemorton-analytics:latest .
docker run --env-file .env.prod colemorton-analytics:latest
```

---

## 🧪 Testing & Quality Assurance

### Testing Framework
- **Frontend**: Vitest + Testing Library for React components
- **Backend**: pytest for Python testing with comprehensive fixtures
- **E2E Testing**: Photo booth system testing with Puppeteer
- **Integration**: Full pipeline testing with real data sources

### Quality Gates
- **TypeScript**: Full type coverage with strict configuration
- **ESLint**: React and Astro-specific linting rules
- **Python**: black (code formatting), isort (import sorting), flake8 (linting), mypy (type checking)
- **Security**: bandit (Python security), npm audit (dependency vulnerabilities)

### Continuous Integration
```bash
# Pre-commit hooks
pre-commit run --all-files  # Run all quality checks locally

# Full test suite
make test-all               # Run all Python tests
yarn test                   # Run all frontend tests
```

---

## 🤝 Contributing

### Development Setup
1. Fork the repository and clone your fork
2. Follow the setup instructions above
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes and ensure tests pass
5. Commit with descriptive messages
6. Push to your fork and create a pull request

### Code Quality Standards
- Follow existing code style (enforced by pre-commit hooks)
- Add tests for new functionality
- Update documentation as needed
- Ensure all quality gates pass before submitting PR

---

## 📊 Project Status & Health

### Current Metrics
- **Overall Health**: 8.5/10 - Strong technical foundation with room for enhancement
- **Test Coverage**: Comprehensive test suites with ongoing expansion
- **Documentation**: Complete with 25 organized documents and user guides
- **Code Quality**: Excellent with comprehensive linting and formatting automation
- **Security**: Strong practices with automated vulnerability scanning

### Active Development Areas
- **Testing**: Expanding test coverage across all components
- **Performance**: Dashboard generation optimization
- **Security**: API key management and secret hardening
- **Features**: Enhanced AI integration and analysis capabilities

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Cole Morton**
- Website: [colemorton.com](https://colemorton.com)
- Platform: Modern personal website with sophisticated data analysis capabilities

---

**Cole Morton Platform** - *Where modern web development meets sophisticated financial analysis and AI-powered content creation.*
