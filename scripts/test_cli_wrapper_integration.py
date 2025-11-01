#!/usr/bin/env python3
"""
Test CLI Wrapper Integration

Test the integrated CLI wrapper with new architectural components.
"""

import sys
from pathlib import Path


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cli_wrapper import CLIServiceManager, CLIServiceWrapper
from result_types import ProcessingResult
from script_config import ScriptConfig


def test_cli_wrapper_integration():
    """Test the CLI wrapper integration with new architectural components"""

    print("Testing CLI Wrapper Integration...")

    # Create mock directories
    base_path = Path("/tmp/test_sensylate_cli")
    base_path.mkdir(exist_ok=True)

    data_outputs_path = base_path / "data" / "outputs"
    data_outputs_path.mkdir(parents=True, exist_ok=True)

    templates_path = base_path / "templates"
    templates_path.mkdir(exist_ok=True)

    # Create scripts directory (required by CLI wrapper)
    scripts_path = base_path / "scripts"
    scripts_path.mkdir(exist_ok=True)

    # Create config
    config = ScriptConfig(
        base_path=base_path,
        data_outputs_path=data_outputs_path,
        templates_path=templates_path,
        twitter_outputs_path=data_outputs_path / "twitter",
        twitter_templates_path=templates_path / "twitter",
    )

    print("Config created: {config.base_path}")
    print()

    # Test CLIServiceWrapper
    print("=== Testing CLIServiceWrapper ===")

    # Test with a non-existent service (should handle gracefully)
    wrapper = CLIServiceWrapper("test_service", config)

    print("Service name: {wrapper.service_name}")
    print("Global available: {wrapper.global_available}")
    print("Local available: {wrapper.local_available}")
    print("Is available: {wrapper.is_available()}")
    print("Timeout: {wrapper.timeout}")
    print("Config integration: {wrapper.config is not None}")
    print()

    # Test service info
    service_info = wrapper.get_service_info()
    print("Service info: {service_info}")
    print()

    # Test CLIServiceManager
    print("=== Testing CLIServiceManager ===")

    manager = CLIServiceManager(config)

    print("Total services: {len(manager.services)}")
    print("Available services: {manager.get_available_services()}")
    print("Config integration: {manager.config is not None}")
    print("Registry integration: {manager.script_registry is not None}")
    print()

    # Test service status
    status = manager.get_service_status()
    print("Service status: {status}")
    print()

    # Test health check
    health = manager.health_check_all()
    print("Health check summary: {health['summary']}")
    print()

    # Test error handling
    print("=== Testing Error Handling ===")

    try:
        # This should fail with proper error handling
        manager.get_service("non_existent_service")
    except Exception:
        print("Expected error caught: {type(e).__name__}: {e}")

    try:
        # This should fail with proper error handling
        wrapper.execute_command("")
    except Exception:
        print("Expected error caught: {type(e).__name__}: {e}")

    print()

    # Test result type
    print("=== Testing Result Types ===")

    # Create a mock ProcessingResult
    result = ProcessingResult(
        success=True,
        operation="test_cli_operation",
        content="Test output",
        processing_time=0.1,
    )

    result.add_metadata("service_name", "test_service")
    result.add_metadata("execution_mode", "test")

    print("Result success: {result.success}")
    print("Result operation: {result.operation}")
    print("Result metadata: {result.metadata}")
    print()

    print("CLI Wrapper Integration test completed successfully!")


if __name__ == "__main__":
    test_cli_wrapper_integration()
