#!/usr/bin/env python3
"""
Photo Booth Controls Hidden Test

This script validates that photo-booth-controls are properly hidden from screenshots.
"""

import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_photobooth_base_controls_css():
    """Test that PhotoBoothBase.astro has CSS to hide photo-booth-controls."""
    print("🔍 Testing PhotoBoothBase controls hiding CSS...")

    layout_path = project_root / "frontend/src/layouts/PhotoBoothBase.astro"
    if not layout_path.exists():
        print("❌ PhotoBoothBase layout not found: {layout_path}")
        return False

    with open(layout_path) as f:
        content = f.read()

    # Check for photo-booth-controls hiding CSS
    required_css = [
        ".photo-booth-controls",
        "display: none !important",
        "visibility: hidden !important",
    ]

    for css_rule in required_css:
        if css_rule not in content:
            print("❌ Missing CSS rule for hiding controls: {css_rule}")
            return False

    print("✅ PhotoBoothBase has CSS to hide photo-booth-controls")
    return True


def test_photobooth_component_has_controls():
    """Test that PhotoBoothDisplay component has the photo-booth-controls class."""
    print("🔍 Testing PhotoBoothDisplay component structure...")

    component_path = project_root / "frontend/src/layouts/shortcodes/PhotoBoothDisplay.tsx"
    if not component_path.exists():
        print("❌ PhotoBoothDisplay component not found: {component_path}")
        return False

    with open(component_path) as f:
        content = f.read()

    # Check for photo-booth-controls class
    if 'className="photo-booth-controls' not in content:
        print("❌ PhotoBoothDisplay component missing photo-booth-controls class")
        return False

    # Check for control elements that should be hidden
    control_elements = [
        "Dashboard Selector",
        "Mode Selector",
        "Status Indicator",
        "Dashboard Info",
    ]

    missing_elements = []
    for element in control_elements:
        if element not in content:
            missing_elements.append(element)

    if missing_elements:
        print("❌ Missing control elements: {missing_elements}")
        return False

    print("✅ PhotoBoothDisplay component has proper control structure")
    return True


def test_controls_only_affect_screenshots():
    """Test that controls hiding only affects PhotoBoothBase, not regular pages."""
    print("🔍 Testing that controls hiding is isolated to PhotoBoothBase...")

    # Check that regular Base.astro doesn't hide photo-booth-controls
    base_layout_path = project_root / "frontend/src/layouts/Base.astro"
    if base_layout_path.exists():
        with open(base_layout_path) as f:
            base_content = f.read()

        if ".photo-booth-controls" in base_content and "display: none" in base_content:
            print("❌ Regular Base.astro also hides photo-booth-controls (should only be PhotoBoothBase)")
            return False

    print("✅ Controls hiding is properly isolated to PhotoBoothBase layout")
    return True


def test_screenshot_specific_hiding():
    """Test that the CSS approach will work for screenshot generation."""
    print("🔍 Testing CSS specificity and priority...")

    layout_path = project_root / "frontend/src/layouts/PhotoBoothBase.astro"
    with open(layout_path) as f:
        content = f.read()

    # Check that CSS uses !important for reliable hiding
    controls_css_section = content[
        content.find(".photo-booth-controls") : content.find("}", content.find(".photo-booth-controls")) + 1
    ]

    if "!important" not in controls_css_section:
        print("❌ CSS doesn't use !important - may not override component styles")
        return False

    # Check for both display and visibility properties for complete hiding
    if "display: none" not in controls_css_section:
        print("❌ Missing display: none property")
        return False

    if "visibility: hidden" not in controls_css_section:
        print("❌ Missing visibility: hidden property")
        return False

    print("✅ CSS has proper specificity and priority for screenshot hiding")
    return True


def test_dashboard_content_not_hidden():
    """Test that dashboard content is not affected by the controls hiding."""
    print("🔍 Testing that dashboard content remains visible...")

    layout_path = project_root / "frontend/src/layouts/PhotoBoothBase.astro"
    with open(layout_path) as f:
        content = f.read()

    # Make sure we're not accidentally hiding dashboard content
    problematic_selectors = [
        ".photo-booth-dashboard",
        ".dashboard-content",
        ".photo-booth-chart",
        "ChartDisplay",
    ]

    for selector in problematic_selectors:
        if f"{selector} {{" in content and "display: none" in content[content.find(f"{selector} {{") :]:
            print("❌ Dashboard content selector {selector} is being hidden")
            return False

    print("✅ Dashboard content selectors are not affected by controls hiding")
    return True


def main():
    """Run all photo booth controls hiding tests."""
    print("🚀 Running Photo Booth Controls Hidden Tests")
    print("=" * 50)

    tests = [
        test_photobooth_base_controls_css,
        test_photobooth_component_has_controls,
        test_controls_only_affect_screenshots,
        test_screenshot_specific_hiding,
        test_dashboard_content_not_hidden,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception:
            print("❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()

    print("=" * 50)
    print("📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 Photo booth controls are properly hidden from screenshots!")
        print("\n📋 Validation confirmed:")
        print("1. PhotoBoothBase.astro has CSS to hide .photo-booth-controls ✅")
        print("2. PhotoBoothDisplay.tsx has proper control structure ✅")
        print("3. Controls hiding isolated to screenshot layout ✅")
        print("4. CSS has proper specificity and priority ✅")
        print("5. Dashboard content remains visible ✅")

        print("\n✨ Screenshot-only hidden elements:")
        print("- Dashboard selector dropdown ✅")
        print("- Light/Dark mode buttons ✅")
        print("- Ready status indicator ✅")
        print("- Dashboard info panel ✅")

        print("\n📸 Screenshots will now show only:")
        print("- Dashboard charts and visualizations")
        print("- No control panels or UI elements")

        return 0
    print("💥 Some tests failed. Please fix the issues above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
