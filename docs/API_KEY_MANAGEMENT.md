# API Key Management System

**Version**: 2.0 | **Last Updated**: 2024-08-14 | **Status**: Active
**Authority**: Platform Architecture | **Audience**: Developers

This document describes the secure API key management system implemented for the Colemorton Command System.

## Overview

The API key management system provides secure, centralized configuration of API keys for financial data services while maintaining security best practices suitable for a local-only development environment.

## Architecture

### Core Components

1. **Environment File (`.env`)** - Secure storage of API keys
2. **ConfigManager** - Centralized key retrieval with validation
3. **Financial Services Config** - Service configuration with environment variable references
4. **Secure Logging** - Automatic obfuscation of sensitive data in logs
5. **Setup Script** - Validation and setup assistance

### Security Features

- ✅ API keys stored in `.env` file (excluded from version control)
- ✅ Automatic key format validation
- ✅ Key obfuscation in logs and error messages
- ✅ Environment variable substitution in configuration files
- ✅ Fail-fast validation for missing or invalid keys
- ✅ Service-specific key format validation

## Supported Services

| Service | API Key | Required | Format |
|---------|---------|----------|--------|
| Alpha Vantage | `ALPHA_VANTAGE_API_KEY` | Yes | 16-20 alphanumeric |
| FRED Economic | `FRED_API_KEY` | Yes | 32 char hexadecimal |
| SEC EDGAR | `SEC_EDGAR_API_KEY` | Yes | 64+ char hexadecimal |
| Financial Modeling Prep | `FMP_API_KEY` | Yes | 20+ alphanumeric |
| CoinGecko | `COINGECKO_API_KEY` | No | Variable |
| IMF | `IMF_API_KEY` | No | Not required |
| EIA | `EIA_API_KEY` | No | Not required |

## Setup Instructions

### 1. Initial Setup

```bash
# Run the setup script to validate your environment
python scripts/setup_environment.py
```

### 2. Configure API Keys

Create or update your `.env` file with the following format:

```bash
# Financial Data API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
SEC_EDGAR_API_KEY=your_sec_edgar_key_here
FRED_API_KEY=your_fred_key_here
FMP_API_KEY=your_fmp_key_here

# Optional API Keys
COINGECKO_API_KEY=not_required
IMF_API_KEY=not_required
EIA_API_KEY=not_required
```

### 3. Obtain API Keys

#### Alpha Vantage (Stock Market Data)
- **URL**: https://www.alphavantage.co/support/#api-key
- **Description**: Free stock market data API
- **Format**: 16-20 alphanumeric characters

#### FRED Economic (Federal Reserve Data)
- **URL**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Description**: Federal Reserve economic data
- **Format**: 32 character hexadecimal string

#### SEC EDGAR (Regulatory Filings)
- **URL**: https://www.sec.gov/edgar/sec-api-documentation
- **Description**: SEC filings and regulatory data
- **Format**: 64+ character hexadecimal string

#### Financial Modeling Prep (Company Fundamentals)
- **URL**: https://financialmodelingprep.com/developer/docs
- **Description**: Financial data and company fundamentals
- **Format**: 20+ alphanumeric characters

### 4. Validate Configuration

```bash
# Re-run setup script to validate
python scripts/setup_environment.py
```

## Usage in Code

### Using ConfigManager

```python
from utils.config_manager import ConfigManager

# Initialize configuration manager
config = ConfigManager()

# Get API key with validation
try:
    api_key = config.get_api_key("ALPHA_VANTAGE_API_KEY", required=True)
    print(f"API key loaded: {api_key[:4]}...{api_key[-4:]}")
except ConfigurationError as e:
    print(f"API key error: {e}")

# Get detailed status information
status = config.get_api_key_status("ALPHA_VANTAGE_API_KEY")
print(f"Key status: {status}")
```

### Using Secure Logging

```python
from utils.secure_logging import create_secure_logger

# Create secure logger (automatically obfuscates API keys)
logger = create_secure_logger(__name__)

# These will be automatically obfuscated in logs
logger.info(f"Using API key: {api_key}")  # Shows as Q420...HHKM
logger.info(f"Config: {config_dict}")     # API keys automatically masked
```

### Loading Environment Variables

```python
from load_env import ensure_env_loaded

# Ensure .env file is loaded (call at start of scripts)
ensure_env_loaded()
```

## Configuration Files

### Financial Services Configuration

The `config/services/financial_services.yaml` file now uses environment variable references:

```yaml
services:
  alpha_vantage:
    name: "alpha_vantage"
    base_url: "https://www.alphavantage.co/query"
    api_key: "${ALPHA_VANTAGE_API_KEY}"
    rate_limit:
      requests_per_minute: 5
```

### Git Ignore

The `.gitignore` file excludes sensitive configuration:

```gitignore
# Environment variables and sensitive configuration
.env
.env.local
.env.*.local
*.env

# API keys and secrets
**/api_keys.json
**/secrets.json
**/config/secrets/
**/*local.json
```

## Security Best Practices

1. **Never commit API keys** - Use environment variables and .env files
2. **Validate key formats** - Detect invalid or placeholder keys
3. **Obfuscate in logs** - Prevent accidental exposure in log files
4. **Fail-fast validation** - Catch configuration issues early
5. **Centralized management** - Single source of truth for key retrieval

## Troubleshooting

### Common Issues

1. **"API key not found" errors**
   - Verify `.env` file exists in project root
   - Check that environment variables are loaded with `python scripts/load_env.py`
   - Ensure key names match exactly (case-sensitive)

2. **"Invalid API key format" errors**
   - Check API key format against service requirements
   - Remove quotes or extra spaces from keys
   - Verify key is not a placeholder value

3. **Configuration loading errors**
   - Run `python scripts/setup_environment.py` to diagnose issues
   - Check YAML syntax in configuration files
   - Verify file paths and permissions

### Diagnostic Commands

```bash
# Check environment setup
python scripts/setup_environment.py

# Load and display environment variables (obfuscated)
python scripts/load_env.py

# Test secure logging
python scripts/utils/secure_logging.py

# Validate specific service configuration
python -c "from utils.config_manager import ConfigManager; c=ConfigManager(); print(c.get_api_key_status('ALPHA_VANTAGE_API_KEY'))"
```

## Migration Guide

If you're migrating from hardcoded API keys:

1. **Create `.env` file** with your existing keys
2. **Run setup script** to validate configuration
3. **Update code** to use ConfigManager instead of hardcoded values
4. **Test thoroughly** to ensure all services work correctly
5. **Commit changes** (without .env file)

This system provides enterprise-grade security practices while maintaining the simplicity needed for local development environments.
