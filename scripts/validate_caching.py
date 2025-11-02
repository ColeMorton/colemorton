#!/usr/bin/env python3
"""
Cache Validation Script
Validates that all financial services are properly implementing caching
"""

import json
import sys
import time
from pathlib import Path
from typing import Any


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.cache_manager import create_cache_manager


class CacheValidator:
    """Validates caching implementation across all services"""

    def __init__(self):
        self.services_to_test = [
            "yahoo_finance",
            "alpha_vantage",
            "fmp",
            "fred_economic",
            "coingecko",
            "sec_edgar",
            "imf_data",
        ]
        self.validation_results = {}

    def test_service_caching(self, service_name: str) -> dict[str, Any]:
        """Test caching for a specific service"""
        print("Testing caching for {service_name}...")

        result = {
            "service_name": service_name,
            "cache_manager_works": False,
            "cache_set_works": False,
            "cache_get_works": False,
            "cache_expiry_works": False,
            "ttl_configured": False,
            "ttl_seconds": None,
            "errors": [],
        }

        try:
            # Test cache manager creation
            cache_manager = create_cache_manager(service_name)
            result["cache_manager_works"] = True
            result["ttl_seconds"] = cache_manager.ttl
            result["ttl_configured"] = cache_manager.ttl > 0

            # Test cache set
            test_key = f"test_validation_{int(time.time())}"
            test_data = {
                "test": True,
                "timestamp": time.time(),
                "service": service_name,
            }
            cache_manager.set(test_key, test_data)
            result["cache_set_works"] = True

            # Test cache get
            retrieved_data = cache_manager.get(test_key)
            if retrieved_data and retrieved_data.get("test") is True:
                result["cache_get_works"] = True
            else:
                result["errors"].append("Cache get returned incorrect data")

            # Test cache statistics
            stats = cache_manager.get_stats()
            if stats and "hit_ratio" in stats:
                result["stats_available"] = True
                result["current_stats"] = stats

            print("  ✅ {service_name}: Cache working, TTL={cache_manager.ttl}s")

        except Exception as e:
            result["errors"].append(f"Cache validation error: {str(e)}")
            print("  ❌ {service_name}: {str(e)}")

        return result

    def test_cli_service_integration(self) -> dict[str, Any]:
        """Test that CLI services are using caching"""
        print("\nTesting CLI service integration...")

        cli_scripts = list(Path("./scripts").glob("*_cli.py"))
        integration_results = {
            "cli_scripts_found": len(cli_scripts),
            "scripts_with_caching": 0,
            "scripts": [],
        }

        for cli_script in cli_scripts:
            script_name = cli_script.stem
            result = {
                "script_name": script_name,
                "uses_service_layer": False,
                "has_cache_config": False,
            }

            try:
                with open(cli_script) as f:
                    content = f.read()

                # Check if it uses service layer (good sign for caching)
                if "create_" in content and "_service(" in content:
                    result["uses_service_layer"] = True
                    integration_results["scripts_with_caching"] += 1

                # Check if it has cache-related configuration
                if "cache" in content.lower() or "ttl" in content.lower():
                    result["has_cache_config"] = True

            except Exception as e:
                result["error"] = str(e)

            integration_results["scripts"].append(result)

        print(
            f"  📊 Found {integration_results['scripts_with_caching']}/{integration_results['cli_scripts_found']} CLI scripts using service layer"
        )
        return integration_results

    def check_cache_directories(self) -> dict[str, Any]:
        """Check cache directory structure and sizes"""
        print("\nChecking cache directories...")

        cache_root = Path("./data/cache")
        directory_info = {
            "cache_root_exists": cache_root.exists(),
            "service_directories": [],
            "total_cache_size_mb": 0,
            "total_files": 0,
        }

        if cache_root.exists():
            for service_dir in cache_root.iterdir():
                if service_dir.is_dir():
                    cache_files = list(service_dir.glob("*.json"))
                    total_size = sum(f.stat().st_size for f in cache_files)

                    service_info = {
                        "service_name": service_dir.name,
                        "cache_files": len(cache_files),
                        "size_mb": total_size / (1024 * 1024),
                        "oldest_file": None,
                        "newest_file": None,
                    }

                    if cache_files:
                        file_times = [(f, f.stat().st_mtime) for f in cache_files]
                        file_times.sort(key=lambda x: x[1])
                        service_info["oldest_file"] = time.ctime(file_times[0][1])
                        service_info["newest_file"] = time.ctime(file_times[-1][1])

                    directory_info["service_directories"].append(service_info)
                    directory_info["total_cache_size_mb"] += service_info["size_mb"]
                    directory_info["total_files"] += service_info["cache_files"]

        print("  📁 Cache root exists: {directory_info['cache_root_exists']}")
        print("  📁 Total cache size: {directory_info['total_cache_size_mb']:.2f} MB")
        print("  📁 Total cache files: {directory_info['total_files']}")

        return directory_info

    def validate_ttl_consistency(self) -> dict[str, Any]:
        """Validate TTL consistency across services"""
        print("\nValidating TTL consistency...")

        ttl_analysis = {
            "services_analyzed": 0,
            "consistent_ttls": 0,
            "standard_ttl": 900,  # 15 minutes
            "services": [],
            "recommendations": [],
        }

        for service_name in self.services_to_test:
            try:
                cache_manager = create_cache_manager(service_name)
                ttl_info = {
                    "service_name": service_name,
                    "ttl_seconds": cache_manager.ttl,
                    "ttl_minutes": cache_manager.ttl / 60,
                    "is_standard": cache_manager.ttl == ttl_analysis["standard_ttl"],
                    "category": self._categorize_ttl(cache_manager.ttl),
                }

                if ttl_info["is_standard"]:
                    ttl_analysis["consistent_ttls"] += 1

                ttl_analysis["services"].append(ttl_info)
                ttl_analysis["services_analyzed"] += 1

            except Exception as e:
                ttl_analysis["services"].append({"service_name": service_name, "error": str(e)})

        # Generate recommendations
        non_standard = [s for s in ttl_analysis["services"] if not s.get("is_standard", False)]
        if non_standard:
            ttl_analysis["recommendations"].append(
                f"Consider standardizing TTL for {len(non_standard)} services to 15 minutes"
            )

        print(
            f"  ⏱️  {ttl_analysis['consistent_ttls']}/{ttl_analysis['services_analyzed']} services using standard 15-minute TTL"
        )

        return ttl_analysis

    def _categorize_ttl(self, ttl_seconds: int) -> str:
        """Categorize TTL values"""
        if ttl_seconds <= 300:
            return "short (≤5 min)"
        if ttl_seconds <= 900:
            return "standard (≤15 min)"
        if ttl_seconds <= 3600:
            return "medium (≤1 hour)"
        return "long (>1 hour)"

    def run_full_validation(self) -> dict[str, Any]:
        """Run comprehensive cache validation"""
        print("🔍 Starting Comprehensive Cache Validation\n")
        print("=" * 60)

        # Test individual services
        print("\n1. Testing Individual Service Caching")
        print("-" * 40)
        for service_name in self.services_to_test:
            self.validation_results[service_name] = self.test_service_caching(service_name)

        # Test CLI integration
        print("\n2. Testing CLI Service Integration")
        print("-" * 40)
        cli_results = self.test_cli_service_integration()

        # Check cache directories
        print("\n3. Cache Directory Analysis")
        print("-" * 40)
        directory_results = self.check_cache_directories()

        # Validate TTL consistency
        print("\n4. TTL Consistency Analysis")
        print("-" * 40)
        ttl_results = self.validate_ttl_consistency()

        # Generate summary
        summary = self._generate_summary()

        full_results = {
            "timestamp": time.time(),
            "individual_services": self.validation_results,
            "cli_integration": cli_results,
            "cache_directories": directory_results,
            "ttl_analysis": ttl_results,
            "summary": summary,
        }

        self._print_summary(summary)

        return full_results

    def _generate_summary(self) -> dict[str, Any]:
        """Generate validation summary"""
        working_services = sum(1 for r in self.validation_results.values() if r.get("cache_get_works", False))

        return {
            "total_services_tested": len(self.services_to_test),
            "services_with_working_cache": working_services,
            "cache_success_rate": working_services / len(self.services_to_test),
            "critical_issues": self._identify_critical_issues(),
            "recommendations": self._generate_recommendations(),
        }

    def _identify_critical_issues(self) -> list[str]:
        """Identify critical caching issues"""
        issues = []

        for service_name, result in self.validation_results.items():
            if not result.get("cache_manager_works", False):
                issues.append(f"{service_name}: Cache manager creation failed")
            elif not result.get("cache_get_works", False):
                issues.append(f"{service_name}: Cache retrieval not working")
            elif not result.get("ttl_configured", False):
                issues.append(f"{service_name}: TTL not properly configured")

        return issues

    def _generate_recommendations(self) -> list[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Check for inconsistent TTLs
        ttls = [r.get("ttl_seconds", 0) for r in self.validation_results.values()]
        unique_ttls = set(ttls)
        if len(unique_ttls) > 3:
            recommendations.append("Standardize TTL values across services (consider using 900s for most services)")

        # Check for missing cache
        non_working = [name for name, r in self.validation_results.items() if not r.get("cache_get_works", False)]
        if non_working:
            recommendations.append(f"Fix caching for services: {', '.join(non_working)}")

        return recommendations

    def _print_summary(self, summary: dict[str, Any]) -> None:
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("🏆 CACHE VALIDATION SUMMARY")
        print("=" * 60)

        print("📊 Services tested: {summary['total_services_tested']}")
        print("✅ Working cache: {summary['services_with_working_cache']}")
        print("📈 Success rate: {summary['cache_success_rate']:.1%}")

        if summary["critical_issues"]:
            print("\n❌ Critical issues ({len(summary['critical_issues'])}):")
            for issue in summary["critical_issues"]:
                print("   • {issue}")

        if summary["recommendations"]:
            print("\n💡 Recommendations ({len(summary['recommendations'])}):")
            for rec in summary["recommendations"]:
                print("   • {rec}")

        if summary["cache_success_rate"] >= 0.9:
            print("\n🎉 Excellent! Cache implementation is working well across services.")
        elif summary["cache_success_rate"] >= 0.7:
            print("\n👍 Good cache implementation with room for improvement.")
        else:
            print("\n⚠️  Cache implementation needs attention - several services have issues.")


if __name__ == "__main__":
    validator = CacheValidator()
    results = validator.run_full_validation()

    # Save results
    results_file = Path("./data/cache_validation_results.json")
    results_file.parent.mkdir(exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n💾 Full results saved to: {results_file}")
