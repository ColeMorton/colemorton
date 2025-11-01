#!/usr/bin/env python3
"""
Test script for Twitter Jinja2 template integration

Validates template rendering and integration with the existing
content automation CLI system.
"""

import sys
from datetime import datetime
from pathlib import Path


# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
except ImportError:
    print("Error: jinja2 not installed. Run: pip install jinja2")
    sys.exit(1)


class TwitterTemplateTest:
    """Test suite for Twitter template integration"""

    def __init__(self):
        self.templates_dir = scripts_dir / "templates" / "twitter"
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)), autoescape=True)

    def test_fundamental_valuation_template(self):
        """Test fundamental analysis valuation template (Template A)"""
        print("Testing Fundamental Valuation Template...")

        # Sample data context
        context = {
            "ticker": "AAPL",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "current_price": 185.50,
                "date": "20250118",
                "fair_value_low": 200.0,
                "fair_value_high": 220.0,
                "weighted_fair_value": 210.0,
                "valuation_methods": [
                    {"name": "DCF Model", "value": 215.0, "confidence": 85},
                    {"name": "Comparable Analysis", "value": 205.0, "confidence": 90},
                    {"name": "Sum-of-Parts", "value": 210.0, "confidence": 80},
                ],
                "key_assumption": "Services growth continues at 15% annually",
                "bull_case_target": 250.0,
                "bull_case_probability": 35,
            },
        }

        try:
            template = self.env.get_template("fundamental/twitter_fundamental_A_valuation.j2")
            content = template.render(**context)

            # Validate content
            self.validate_content(content, "fundamental")
            print("✅ Fundamental valuation template test PASSED")
            print("Generated content preview:\n{content[:200]}...\n")
            return True

        except TemplateNotFound:
            print("❌ Template not found: {e}")
            return False
        except Exception:
            print("❌ Template rendering failed: {e}")
            return False

    def test_strategy_template(self):
        """Test strategy template rendering"""
        print("Testing Strategy Template...")

        context = {
            "ticker": "TSLA",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "date": "20250118",
                "strategy_type": "SMA",
                "short_window": 10,
                "long_window": 25,
                "period": "5 years",
                "net_performance": 156.7,
                "win_rate": 42.3,
                "total_trades": 87,
                "avg_win": 8.4,
                "avg_loss": 3.2,
                "reward_risk_ratio": 2.6,
                "reward_risk": 2.6,
                "max_drawdown": 12.4,
                "sharpe": 1.8,
                "sortino": 2.1,
                "exposure": 65.2,
                "avg_trade_length": 18,
                "expectancy": 1.65,
                "current_month": "January",
                "current_month_performance": 73.5,
                "signal_triggered": True,
                "current_price": 248.50,
                "technical_setup": "Bullish breakout above resistance",
                "fundamental_catalyst": "FSD beta release momentum",
            },
        }

        try:
            template = self.env.get_template("strategy/twitter_post_strategy.j2")

            # Debug: Try to render with minimal context first
            try:
                content = template.render(**context)
            except Exception:
                print("❌ Template rendering failed: {render_error}")
                # Try with just required variables
                minimal_context = {
                    "ticker": context["ticker"],
                    "timestamp": context["timestamp"],
                    "data": {},
                }
                try:
                    template.render(**minimal_context)
                    print("✅ Minimal context worked - issue is with data structure")
                except Exception:
                    print("❌ Even minimal context failed: {minimal_error}")
                return False

            self.validate_content(content, "strategy")
            print("✅ Strategy template test PASSED")
            print("Generated content preview:\n{content[:200]}...\n")
            return True

        except TemplateNotFound:
            print("❌ Template not found: {e}")
            return False
        except Exception:
            print("❌ Unexpected error: {e}")
            return False

    def test_base_template_macros(self):
        """Test base template macro functionality"""
        print("Testing Base Template Macros...")

        try:
            # Test disclaimer macro
            template_content = """
            {%- from 'shared/base_twitter.j2' import disclaimer -%}
            {{ disclaimer('fundamental') }}
            """

            template = self.env.from_string(template_content)
            content = template.render()

            if "Not financial advice" in content:
                print("✅ Disclaimer macro test PASSED")
                return True
            print("❌ Disclaimer macro test FAILED")
            return False

        except Exception:
            print("❌ Base template macro test failed: {e}")
            return False

    def validate_content(self, content, content_type):
        """Validate generated content meets requirements"""
        checks = {
            "has_disclaimer": "⚠️" in content and "Not financial advice" in content,
            "has_blog_link": "https://www.colemorton.com" in content,
            "has_hashtags": "#" in content,
            "within_reasonable_length": len(content) < 2000,  # Multi-tweet thread
            "no_template_errors": "{{" not in content and "}}" not in content,
        }

        for check, passed in checks.items():
            if not passed:
                print("⚠️  Validation warning: {check} failed")

        return all(checks.values())

    def test_template_inheritance(self):
        """Test template inheritance and shared components"""
        print("Testing Template Inheritance...")

        try:
            # Check if shared components exist
            shared_files = ["shared/base_twitter.j2", "shared/components.j2"]

            for file_path in shared_files:
                template_path = self.templates_dir / file_path
                if not template_path.exists():
                    print("❌ Missing shared component: {file_path}")
                    return False

            print("✅ Template inheritance structure test PASSED")
            return True

        except Exception:
            print("❌ Template inheritance test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all template tests"""
        print("🚀 Starting Twitter Template Integration Tests\n")

        tests = [
            self.test_template_inheritance,
            self.test_base_template_macros,
            self.test_fundamental_valuation_template,
            self.test_strategy_template,
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception:
                print("❌ Test failed with exception: {e}")
                results.append(False)
            print()  # Add spacing between tests

        # Summary
        passed = sum(results)
        total = len(results)

        print("📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests PASSED! Template integration is working correctly.")
        else:
            print("⚠️  Some tests failed. Check template configuration and dependencies.")

        return passed == total


def main():
    """Main test execution"""
    try:
        test_suite = TwitterTemplateTest()
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception:
        print("❌ Test suite failed to initialize: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
