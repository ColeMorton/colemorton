#!/usr/bin/env python3
"""
Industry Analysis Script Registry Module
Registers all industry analysis DASV scripts with the global registry
"""

import sys
from pathlib import Path


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from industry_analysis.industry_analysis import IndustryAnalysisScript

# Import industry analysis scripts
from industry_analysis.industry_discovery import IndustryDiscoveryScript
from industry_analysis.industry_synthesis import IndustrySynthesisScript
from industry_analysis.industry_validation import IndustryValidationScript
from script_config import load_default_config

# Import registry components
from script_registry import get_global_registry, register_script


def register_industry_analysis_scripts():
    """Register all industry analysis scripts with the global registry"""

    print("🏭 Registering Industry Analysis DASV Scripts...")

    # Get or create global registry
    config = load_default_config()
    registry = get_global_registry(config)

    # Register industry analysis scripts
    scripts_to_register = [
        ("industry_discovery", IndustryDiscoveryScript),
        ("industry_analysis", IndustryAnalysisScript),
        ("industry_synthesis", IndustrySynthesisScript),
        ("industry_validation", IndustryValidationScript),
    ]

    registered_count = 0
    for script_name, script_class in scripts_to_register:
        try:
            register_script(script_class, script_name)
            print("  ✅ Registered: {script_name}")
            registered_count += 1
        except Exception:
            print("  ❌ Failed to register {script_name}: {e}")

    print(
        f"📊 Industry Analysis Registration Complete: {registered_count}/{len(scripts_to_register)} scripts registered"
    )

    # Verify registration
    print("\n🔍 Verifying Registration:")
    available_scripts = registry.list_available_scripts()

    for script_name, _ in scripts_to_register:
        if script_name in available_scripts:
            print("  ✅ {script_name} - Available")
        else:
            print("  ❌ {script_name} - Missing")

    return registry


def list_industry_scripts():
    """List all registered industry analysis scripts"""

    registry = get_global_registry()
    industry_scripts = [s for s in registry.list_available_scripts() if "industry" in s]

    print("\n📋 Industry Analysis Scripts ({len(industry_scripts)}):")
    for script_name in sorted(industry_scripts):
        metadata = registry.get_script_metadata(script_name)
        if metadata:
            print("  • {script_name}: {metadata.description}")
            print("    Content Types: {metadata.supported_content_types}")
            print("    Requires Validation: {metadata.requires_validation}")
        else:
            print("  • {script_name}: No metadata available")


def test_industry_script_execution():
    """Test execution of industry analysis scripts"""

    print("\n🧪 Testing Industry Script Execution:")

    registry = get_global_registry()

    # Test parameters
    test_params = {
        "industry": "software_infrastructure",
        "date": "20250728",
        "depth": "summary",
    }

    # Test discovery script
    try:
        result = registry.execute_script("industry_discovery", **test_params)
        if result.success:
            print("  ✅ industry_discovery - Test passed")
        else:
            print("  ❌ industry_discovery - Test failed: {result.error}")
    except Exception:
        print("  ❌ industry_discovery - Exception: {e}")

    # Test analysis script (requires discovery output)
    test_params_analysis = test_params.copy()
    test_params_analysis["discovery_file"] = (
        "./data/outputs/industry_analysis/discovery/software_infrastructure_20250728_discovery.json"
    )

    try:
        result = registry.execute_script("industry_analysis", **test_params_analysis)
        if result.success:
            print("  ✅ industry_analysis - Test passed")
        else:
            print("  ❌ industry_analysis - Test failed: {result.error}")
    except Exception:
        print("  ❌ industry_analysis - Exception: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Industry Analysis Script Registry")
    parser.add_argument("--register", action="store_true", help="Register scripts")
    parser.add_argument("--list", action="store_true", help="List registered scripts")
    parser.add_argument("--test", action="store_true", help="Test script execution")
    parser.add_argument("--all", action="store_true", help="Run all operations")

    args = parser.parse_args()

    if args.all or args.register:
        register_industry_analysis_scripts()

    if args.all or args.list:
        list_industry_scripts()

    if args.all or args.test:
        test_industry_script_execution()

    if not any([args.register, args.list, args.test, args.all]):
        print("No operation specified. Use --help for options.")
        register_industry_analysis_scripts()  # Default operation
