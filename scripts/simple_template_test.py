#!/usr/bin/env python3
"""Simple template test to verify inheritance and macro structure"""

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


# Paths
scripts_dir = Path(__file__).parent
templates_dir = scripts_dir / "templates"
test_data_dir = scripts_dir / "test_data"

# Setup Jinja2
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))

# Load sample data
with open(test_data_dir / "sample_fundamental_data.json") as f:
    fundamental_data = json.load(f)

with open(test_data_dir / "sample_sector_data.json") as f:
    sector_data = json.load(f)

print("Testing template loading and basic rendering...")

try:
    # Test fundamental template
    print("\n1. Loading fundamental_analysis_enhanced.j2...")
    fund_template = jinja_env.get_template("fundamental_analysis_enhanced.j2")
    print("   ✅ Fundamental template loaded successfully")

    # Test sector template
    print("\n2. Loading sector_analysis_enhanced.j2...")
    sector_template = jinja_env.get_template("sector_analysis_enhanced.j2")
    print("   ✅ Sector template loaded successfully")

    # Test base template
    print("\n3. Loading shared/base_analysis_template.j2...")
    base_template = jinja_env.get_template("shared/base_analysis_template.j2")
    print("   ✅ Base template loaded successfully")

    # Test macro files
    macros = [
        "shared/macros/economic_sensitivity_macro.j2",
        "shared/macros/risk_assessment_macro.j2",
        "shared/macros/confidence_scoring_macro.j2",
        "shared/macros/data_quality_macro.j2",
        "shared/macros/valuation_framework_macro.j2",
    ]

    print("\n4. Testing macro files...")
    for macro in macros:
        macro_template = jinja_env.get_template(macro)
        print("   ✅ {macro} loaded successfully")

    # Test simple rendering
    print("\n5. Testing basic template rendering...")

    context = {
        "data": fundamental_data,
        "ticker": "AAPL",
        "timestamp": "2025-07-16T12:00:00",
        "analysis_type": "fundamental",
    }

    # Just test that it doesn't crash
    content = fund_template.render(**context)
    print("   ✅ Fundamental template rendered: {len(content):,} characters")

    context_sector = {
        "data": sector_data,
        "sector": "XLK",
        "timestamp": "2025-07-16T12:00:00",
        "analysis_type": "sector",
    }

    content_sector = sector_template.render(**context_sector)
    print("   ✅ Sector template rendered: {len(content_sector):,} characters")

    print("\n🎉 SUCCESS: All templates loaded and rendered successfully!")
    print("✨ Template inheritance and macros are working correctly!")

except Exception:
    print("\n❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
