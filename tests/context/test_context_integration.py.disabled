"""
Integration tests for context provider framework.

These tests verify that the context providers work together correctly
and that the overall context injection system functions as designed.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from context import LocalCommandContext, create_local_context
from context.providers import MCPContextProvider, DataContextProvider, ValidationContextProvider
from context.factories import ContextFactory


class TestContextIntegration:
    """Integration tests for the context framework"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "test_config.yaml"
        self.mcp_config_path = self.temp_dir / "mcp-servers.json"

        # Create test MCP config
        mcp_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["test_server.py"],
                    "description": "Test MCP server"
                }
            }
        }

        with open(self.mcp_config_path, 'w') as f:
            import json
            json.dump(mcp_config, f)

        # Create test context config
        test_config = {
            "execution": {
                "environment": "test",
                "timeout": 60
            },
            "data": {
                "base_output_path": str(self.temp_dir / "outputs"),
                "cache_enabled": True,
                "backup_enabled": False
            },
            "mcp": {
                "config_path": str(self.mcp_config_path),
                "health_check_enabled": False,
                "retry_attempts": 1,
                "timeout": 30
            },
            "validation": {
                "confidence_threshold": 0.7,
                "quality_gates": "standard",
                "format_validation": True
            }
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_context_factory_creates_valid_context(self):
        """Test that ContextFactory creates a valid LocalCommandContext"""
        factory = ContextFactory(self.config_path)
        context = factory.create_context("test_command")

        assert isinstance(context, LocalCommandContext)
        assert context.execution.command_name == "test_command"
        assert context.execution.environment == "test"
        assert context.data.base_output_path == Path(self.temp_dir / "outputs")
        assert "test-server" in context.mcp.available_servers
        assert context.validation.confidence_threshold == 0.7

    def test_providers_initialization(self):
        """Test that all providers can be initialized with context"""
        context = create_local_context("test_command", mcp_config_path=self.mcp_config_path)

        # Test MCP provider
        mcp_provider = MCPContextProvider(context.mcp)
        assert mcp_provider.context == context.mcp
        assert mcp_provider.server_config is not None

        # Test Data provider
        data_provider = DataContextProvider(context.data)
        assert data_provider.context == context.data
        assert data_provider.context.base_output_path.exists()

        # Test Validation provider
        validation_provider = ValidationContextProvider(context.validation)
        assert validation_provider.context == context.validation
        assert validation_provider.validation_rules is not None

    def test_data_provider_operations(self):
        """Test data provider file operations"""
        context = create_local_context("test_command", mcp_config_path=self.mcp_config_path)
        data_provider = DataContextProvider(context.data)

        # Test output path creation
        output_path = data_provider.get_output_path("test_category", "test_sub")
        assert output_path.exists()
        assert output_path.name == "test_sub"
        assert output_path.parent.name == "test_category"

        # Test file operations
        test_data = {"test": "data", "number": 123}
        filename = "test_output.json"

        saved_path = data_provider.save_json_output(test_data, output_path, filename)
        assert saved_path.exists()

        loaded_data = data_provider.load_json_input(saved_path)
        assert loaded_data == test_data

    def test_validation_provider_ticker_validation(self):
        """Test validation provider ticker validation"""
        context = create_local_context("test_command", mcp_config_path=self.mcp_config_path)
        validation_provider = ValidationContextProvider(context.validation)

        # Valid ticker
        result = validation_provider.validate_ticker_symbol("AAPL")
        assert result.is_valid
        assert result.confidence_score == 1.0

        # Invalid ticker
        result = validation_provider.validate_ticker_symbol("")
        assert not result.is_valid
        assert len(result.issues) > 0

    def test_mcp_provider_server_discovery(self):
        """Test MCP provider server discovery"""
        context = create_local_context("test_command", mcp_config_path=self.mcp_config_path)
        mcp_provider = MCPContextProvider(context.mcp)

        # Test server availability
        assert mcp_provider.is_server_configured("test-server")
        assert not mcp_provider.is_server_configured("nonexistent-server")

        # Test server list
        servers = mcp_provider.get_available_servers()
        assert "test-server" in servers

    def test_context_serialization(self):
        """Test context serialization to dictionary"""
        context = create_local_context("test_command", mcp_config_path=self.mcp_config_path)

        context_dict = context.to_dict()

        assert "execution" in context_dict
        assert "data" in context_dict
        assert "mcp" in context_dict
        assert "validation" in context_dict
        assert context_dict["execution"]["command_name"] == "test_command"

    def test_child_context_creation(self):
        """Test creating child contexts"""
        parent_context = create_local_context("parent_command", mcp_config_path=self.mcp_config_path)

        child_context = parent_context.create_child_context("child_command")

        assert child_context.execution.command_name == "child_command"
        assert child_context.data.base_output_path == parent_context.data.base_output_path
        assert child_context.mcp.available_servers == parent_context.mcp.available_servers
        assert child_context.validation.confidence_threshold == parent_context.validation.confidence_threshold

    def test_config_validation(self):
        """Test configuration validation"""
        factory = ContextFactory(self.config_path)

        issues = factory.validate_config()
        assert isinstance(issues, list)
        # Should have no issues with valid config
        assert len(issues) == 0

    def test_command_overrides(self):
        """Test command-specific configuration overrides"""
        # Add command override to config
        config_with_override = {
            "execution": {"timeout": 300},
            "data": {"base_output_path": str(self.temp_dir / "outputs")},
            "mcp": {"config_path": str(self.mcp_config_path)},
            "validation": {"confidence_threshold": 0.8},
            "command_overrides": {
                "special_command": {
                    "validation": {
                        "confidence_threshold": 0.95,
                        "quality_gates": "institutional"
                    },
                    "execution": {
                        "timeout": 600
                    }
                }
            }
        }

        override_config_path = self.temp_dir / "override_config.yaml"
        with open(override_config_path, 'w') as f:
            yaml.dump(config_with_override, f)

        factory = ContextFactory(override_config_path)

        # Regular command uses base config
        regular_context = factory.create_context("regular_command")
        assert regular_context.validation.confidence_threshold == 0.8
        assert regular_context.execution.timeout == 300

        # Special command uses overrides
        special_context = factory.create_context("special_command")
        assert special_context.validation.confidence_threshold == 0.95
        assert special_context.execution.timeout == 600


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
