# Quick Start Guide

**Version**: 1.0 | **Last Updated**: 2025-01-15 | **Status**: Active
**Authority**: Documentation Owner | **Audience**: New Users & Developers

## Purpose & Scope

This guide provides a streamlined path to get Colemorton up and running quickly, focusing on the essential setup steps and first-run experience.

## Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** for frontend development
- **Python 3.9+** for data processing
- **Git** for version control
- **Yarn** package manager
- **Basic terminal/command line familiarity**

## 🚀 5-Minute Setup

### Step 1: Clone and Initial Setup

```bash
# Clone the repository
git clone https://github.com/colemorton/platform.git
cd colemorton

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup frontend
cd frontend/
yarn install
```

### Step 2: Environment Configuration

```bash
# From the root directory
cp .env.example .env
# Edit .env with your API keys (optional for basic functionality)
```

### Step 3: Verify Installation

```bash
# Test Python backend
make test

# Test frontend
cd frontend/
yarn test
```

### Step 4: First Run

```bash
# Start frontend development server
cd frontend/
yarn dev
# Access at http://localhost:4321

# In another terminal, run a sample analysis
python scripts/fundamental_analysis/fundamental_discovery.py AAPL
```

## ✅ Verification Checklist

After setup, verify these work:

- [ ] Frontend loads at `http://localhost:4321`
- [ ] Python scripts run without errors
- [ ] Data outputs appear in `data/outputs/`
- [ ] Test suites pass (`make test` and `yarn test`)

## 🎯 First Tasks

### Explore the Platform

1. **Browse existing content**: Check `frontend/src/content/blog/` for analysis examples
2. **Check data outputs**: Look in `data/outputs/` for existing analysis results
3. **Review configuration**: Examine `config/` directory for system settings

### Run Your First Analysis

```bash
# Generate a fundamental analysis
python scripts/fundamental_analysis/fundamental_analysis.py AAPL

# Create a dashboard
python scripts/dashboard_generator.py

# Check the results
ls data/outputs/fundamental_analysis/
```

### Create Your First Content

```bash
# The analysis scripts automatically generate content
# Check the results in data/outputs/
# Move relevant content to frontend/src/content/blog/ for publication
```

## 🔧 Common First-Run Issues

### Python Environment Issues

```bash
# Check Python version
python --version  # Should be 3.9+

# If dependencies fail to install
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

```bash
# Check Node.js version
node --version  # Should be 18+

# If yarn install fails
cd frontend/
rm -rf node_modules yarn.lock
yarn install
```

### Data Pipeline Issues

```bash
# Check data directory structure
ls data/
ls data/outputs/

# If outputs are missing
mkdir -p data/outputs/fundamental_analysis
mkdir -p data/outputs/sector_analysis
```

## 📁 Key Directory Structure

After successful setup, you should see:

```
colemorton/
├── frontend/                 # Astro frontend platform
│   ├── src/content/         # Content collections
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── scripts/                 # Python analysis tools
│   ├── fundamental_analysis/ # Core analysis pipeline
│   ├── utils/               # Utility modules
│   └── services/            # API integrations
├── data/                    # Data storage
│   ├── outputs/             # Analysis results
│   ├── cache/               # Caching system
│   └── images/              # Charts and visualizations
├── config/                  # System configuration
├── templates/               # Analysis templates
└── docs/                    # Documentation
```

## 🎓 Learning Path

### Beginner (First Hour)
1. **Complete setup** using this guide
2. **Read the [User Manual](01-user-manual.md)** for comprehensive overview
3. **Run sample analysis** with provided scripts
4. **Explore the frontend** at localhost:4321

### Intermediate (First Day)
1. **Review [System Architecture](System Architecture Overview.md)** for technical understanding
2. **Experiment with different analysis scripts** in `scripts/`
3. **Customize configuration** in `config/` directory
4. **Try content generation** pipeline

### Advanced (First Week)
1. **Dive into the codebase** in `scripts/` and `frontend/src/`
2. **Understand the DASV framework** (Discovery-Analyze-Synthesize-Validate)
3. **Explore data sources** and API integrations
4. **Customize templates** and analysis parameters

## 🔗 Next Steps

After completing this quick start:

1. **Read the complete [User Manual](01-user-manual.md)**
2. **Explore the [System Architecture](System Architecture Overview.md)**
3. **Review existing analysis** in `data/outputs/`
4. **Join the community** (if applicable)
5. **Start building** your own analysis workflows

## 📚 Documentation Links

- **[User Manual](01-user-manual.md)**: Complete usage guide
- **[System Architecture Overview](System Architecture Overview.md)**: Technical architecture
- **[Content Lifecycle Management](Content Lifecycle & Content Lifecycle Management System.md)**: Content pipeline details
- **[Technical Health Assessment](technical_health_assessment_20250715.md)**: Current system status

## 🆘 Getting Help

If you encounter issues:

1. **Check the [User Manual troubleshooting section](01-user-manual.md#-troubleshooting)**
2. **Review log files** in `data/outputs/logs/`
3. **Check system requirements** above
4. **Verify all dependencies** are installed correctly

## 🎉 Success!

You're now ready to use Colemorton! The platform provides:

- **Automated trading analysis** with institutional-quality reports
- **Multi-source data integration** from 18+ financial APIs
- **Professional content generation** for blogs and social media
- **Interactive visualizations** with modern web interface
- **Comprehensive quality assurance** with automated testing

Start with the fundamental analysis scripts and explore the generated content in the frontend platform.

---

**Setup Time**: ~5 minutes
**Learning Curve**: Beginner-friendly with comprehensive documentation
**Support**: Complete user manual and troubleshooting guides available

*Welcome to Colemorton - your comprehensive trading analysis platform!*
