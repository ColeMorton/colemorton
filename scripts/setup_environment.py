#!/usr/bin/env python3
"""
Environment Setup and Validation Script

Helps users set up and validate their API key configuration for the Sensylate system.
Provides detailed status reporting and setup guidance.
"""

import sys
from pathlib import Path


# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
from load_env import ensure_env_loaded


ensure_env_loaded()

# Add utils to path for importing config manager
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from config_manager import ConfigManager, ConfigurationError


def print_header(title: str) -> None:
    """Print a formatted header"""
    print("\n{'=' * 60}")
    print(" {title}")
    print("{'=' * 60}")


def print_status(status: str, message: str) -> None:
    """Print a status message with colored indicator"""
    indicators = {"SUCCESS": "✅", "WARNING": "⚠️ ", "ERROR": "❌", "INFO": "ℹ️ "}
    print("{indicators.get(status, '•')} {message}")


def check_environment_file() -> dict[str, str]:
    """Check for .env file and load environment variables"""
    env_path = Path(".env")
    env_vars = {}

    if env_path.exists():
        print_status("SUCCESS", f"Found .env file: {env_path.absolute()}")

        # Load environment variables from .env file
        with open(env_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")

        print_status("INFO", f"Loaded {len(env_vars)} variables from .env file")
    else:
        print_status("WARNING", "No .env file found")
        print("  Please create a .env file with your API keys")
        print("  You can copy from .env.example if available")

    return env_vars


def validate_api_keys(config_manager: ConfigManager) -> dict[str, dict]:
    """Validate all API keys and return status report"""
    api_keys_to_check = [
        "ALPHA_VANTAGE_API_KEY",
        "SEC_EDGAR_API_KEY",
        "FRED_API_KEY",
        "FMP_API_KEY",
        "COINGECKO_API_KEY",
        "IMF_API_KEY",
        "EIA_API_KEY",
    ]

    results = {}
    for key_name in api_keys_to_check:
        results[key_name] = config_manager.get_api_key_status(key_name)

    return results


def print_api_key_report(results: dict[str, dict]) -> None:
    """Print detailed API key status report"""
    print_header("API Key Status Report")

    required_keys = []
    optional_keys = []
    error_keys = []

    for key_name, status in results.items():
        if status.get("required", False):
            required_keys.append((key_name, status))
        else:
            optional_keys.append((key_name, status))

    # Report required keys
    print("\n📋 REQUIRED API KEYS:")
    for key_name, status in required_keys:
        if status["found"] and status["valid_format"]:
            print_status(
                "SUCCESS",
                f"{key_name}: {status['obfuscated_value']} ({status['source']})",
            )
        elif status["found"] and not status["valid_format"]:
            print_status("WARNING", f"{key_name}: Invalid format ({status['length']} chars)")
            error_keys.append(key_name)
        else:
            print_status("ERROR", f"{key_name}: NOT FOUND")
            error_keys.append(key_name)

    # Report optional keys
    print("\n📋 OPTIONAL API KEYS:")
    for key_name, status in optional_keys:
        if status["found"] and status.get("obfuscated_value") == "not_required":
            print_status("INFO", f"{key_name}: Not required")
        elif status["found"] and status["valid_format"]:
            print_status(
                "SUCCESS",
                f"{key_name}: {status['obfuscated_value']} ({status['source']})",
            )
        elif status["found"] and not status["valid_format"]:
            print_status("WARNING", f"{key_name}: Invalid format")
        else:
            print_status("INFO", f"{key_name}: Not configured (optional)")

    return error_keys


def provide_setup_guidance(error_keys: list[str]) -> None:
    """Provide guidance for fixing configuration issues"""
    if not error_keys:
        print_status("SUCCESS", "All required API keys are properly configured!")
        return

    print_header("Setup Guidance")

    key_instructions = {
        "ALPHA_VANTAGE_API_KEY": {
            "url": "https://www.alphavantage.co/support/#api-key",
            "description": "Free stock market data API",
            "format": "16-20 alphanumeric characters",
        },
        "SEC_EDGAR_API_KEY": {
            "url": "https://www.sec.gov/edgar/sec-api-documentation",
            "description": "SEC filings and regulatory data",
            "format": "64+ character hexadecimal string",
        },
        "FRED_API_KEY": {
            "url": "https://fred.stlouisfed.org/docs/api/api_key.html",
            "description": "Federal Reserve economic data",
            "format": "32 character hexadecimal string",
        },
        "FMP_API_KEY": {
            "url": "https://financialmodelingprep.com/developer/docs",
            "description": "Financial data and company fundamentals",
            "format": "20+ alphanumeric characters",
        },
    }

    for key_name in error_keys:
        if key_name in key_instructions:
            info = key_instructions[key_name]
            print("\n🔑 {key_name}:")
            print("   Description: {info['description']}")
            print("   Get API key: {info['url']}")
            print("   Expected format: {info['format']}")
            print("   Add to .env: {key_name}=your_api_key_here")

    print("\n📝 Next steps:")
    print("1. Obtain the missing API keys from the URLs above")
    print("2. Add them to your .env file")
    print("3. Run this script again to validate")


def check_financial_services_config() -> bool:
    """Check if financial services configuration exists and is valid"""
    config_path = Path("config/services/financial_services.yaml")

    if config_path.exists():
        print_status("SUCCESS", f"Found financial services config: {config_path}")
        try:
            # Test loading the configuration
            config_manager = ConfigManager()
            print_status("SUCCESS", "Financial services configuration loaded successfully")
            return True
        except Exception as e:
            print_status("ERROR", f"Invalid financial services configuration: {e}")
            return False
    else:
        print_status("ERROR", f"Financial services config not found: {config_path}")
        return False


def main():
    """Main setup and validation routine"""
    print_header("Sensylate Environment Setup & Validation")

    # Check current directory
    if not Path("scripts").exists() or not Path("config").exists():
        print_status("ERROR", "Please run this script from the project root directory")
        sys.exit(1)

    # Check .env file
    env_vars = check_environment_file()

    # Check financial services configuration
    config_valid = check_financial_services_config()
    if not config_valid:
        sys.exit(1)

    try:
        # Initialize configuration manager
        config_manager = ConfigManager()

        # Validate API keys
        results = validate_api_keys(config_manager)
        error_keys = print_api_key_report(results)

        # Provide guidance if needed
        provide_setup_guidance(error_keys)

        # Final status
        if not error_keys:
            print_header("✅ SETUP COMPLETE")
            print("Your environment is properly configured!")
            print("You can now run financial analysis scripts.")
        else:
            print_header("⚠️  SETUP INCOMPLETE")
            print(f"Please configure {len(error_keys)} missing API key(s) and run again.")
            sys.exit(1)

    except ConfigurationError as e:
        print_status("ERROR", f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print_status("ERROR", f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
