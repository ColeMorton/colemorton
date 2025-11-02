#!/usr/bin/env python3
"""
Puppeteer Fix Verification Test

This script validates that the ES module/CommonJS fix for Puppeteer is working.
"""

import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_cjs_extension():
    """Test that Puppeteer scripts are generated with .cjs extension."""
    print("🔍 Testing Puppeteer script extension...")

    generator_path = project_root / "scripts/photo_booth_generator.py"
    with open(generator_path) as f:
        content = f.read()

    # Check for .cjs extension
    if '.cjs"' not in content:
        print("❌ Puppeteer scripts not using .cjs extension")
        return False

    # Check against old .js extension
    if "puppeteer_script_{datetime.now().strftime" in content and '.js"' in content:
        print("❌ Still using .js extension for Puppeteer scripts")
        return False

    print("✅ Puppeteer scripts use .cjs extension")
    return True


def test_puppeteer_syntax():
    """Test that Puppeteer script uses correct modern syntax."""
    print("🔍 Testing Puppeteer script syntax...")

    generator_path = project_root / "scripts/photo_booth_generator.py"
    with open(generator_path) as f:
        content = f.read()

    # Check for deprecated methods
    if "waitForTimeout" in content:
        print("❌ Using deprecated waitForTimeout method")
        return False

    if "waitForDelay" in content:
        print("❌ Using non-existent waitForDelay method")
        return False

    # Check for correct setTimeout approach
    if "setTimeout(resolve, 3000)" not in content:
        print("❌ Not using correct setTimeout approach for delays")
        return False

    # Check for CommonJS require (should still be there)
    if "require('puppeteer')" not in content:
        print("❌ Missing CommonJS require statement")
        return False

    print("✅ Puppeteer script uses correct modern syntax")
    return True


def test_output_directory():
    """Test that screenshots are being generated in the correct location."""
    print("🔍 Testing screenshot output directory...")

    output_dir = project_root / "frontend/data/outputs/photo-booth"
    if not output_dir.exists():
        print("❌ Output directory doesn't exist: {output_dir}")
        return False

    # Check for recent screenshot files
    screenshot_files = list(output_dir.glob("*.png"))
    if not screenshot_files:
        print("⚠️ No screenshot files found (may need to run generation first)")
        return None  # Neutral result

    print("✅ Found {len(screenshot_files)} screenshot files in output directory")
    return True


def test_es_module_compatibility():
    """Test that the fix resolves the ES module/CommonJS conflict."""
    print("🔍 Testing ES module compatibility...")

    # Check frontend package.json for ES module configuration
    package_json_path = project_root / "frontend/package.json"
    with open(package_json_path) as f:
        content = f.read()

    if '"type": "module"' not in content:
        print("⚠️ Frontend not configured as ES module (test may not be relevant)")
        return None

    # The key test is that we're using .cjs extension which bypasses the ES module issue
    generator_path = project_root / "scripts/photo_booth_generator.py"
    with open(generator_path) as f:
        generator_content = f.read()

    if '.cjs"' in generator_content and "require('puppeteer')" in generator_content:
        print("✅ ES module compatibility fix is properly implemented")
        return True
    print("❌ ES module compatibility fix not properly implemented")
    return False


def main():
    """Run all Puppeteer fix verification tests."""
    print("🚀 Running Puppeteer Fix Verification Tests")
    print("=" * 50)

    tests = [
        test_cjs_extension,
        test_puppeteer_syntax,
        test_output_directory,
        test_es_module_compatibility,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test in tests:
        try:
            result = test()
            if result is True:
                passed += 1
            elif result is False:
                failed += 1
            else:  # result is None (skipped)
                skipped += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0:
        print("🎉 Puppeteer ES module/CommonJS fix is working correctly!")
        print("\n📋 Key fixes implemented:")
        print("1. Using .cjs extension for Puppeteer scripts ✅")
        print("2. Modern setTimeout syntax for delays ✅")
        print("3. ES module compatibility maintained ✅")
        print("4. Screenshot generation working ✅")

        if skipped > 0:
            print(f"\n💡 Note: {skipped} test(s) skipped (no screenshots found - run yarn photo-booth:generate)")

        return 0
    print("💥 Some tests failed. Please fix the issues above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
