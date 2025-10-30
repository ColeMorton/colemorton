"""
Test for the consolidated chart configuration system.
Verifies that the symbol-metadata merge into chart-data-dependencies.json works correctly.
"""

import json
import pytest
from pathlib import Path


class TestConfigConsolidation:
    """Test cases for the consolidated chart configuration."""

    @pytest.fixture
    def config_path(self):
        """Path to the consolidated configuration file."""
        project_root = Path(__file__).parent.parent
        return project_root / "frontend/src/config/chart-data-dependencies.json"

    @pytest.fixture
    def config_data(self, config_path):
        """Load the consolidated configuration data."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def test_config_file_exists(self, config_path):
        """Test that the consolidated config file exists."""
        assert config_path.exists(), "Consolidated config file should exist"

    def test_config_structure(self, config_data):
        """Test that the config has the expected structure."""
        # Original chart-data-dependencies structure
        assert "version" in config_data
        assert "dependencies" in config_data
        assert "settings" in config_data

        # New symbol metadata structure
        assert "symbolMetadata" in config_data
        assert "chartTypeMapping" in config_data
        assert "defaults" in config_data

    def test_symbol_metadata_content(self, config_data):
        """Test that symbol metadata contains expected symbols."""
        symbols = config_data["symbolMetadata"]

        # Should contain AAPL and MSTR
        assert "AAPL" in symbols
        assert "MSTR" in symbols

        # Check AAPL structure
        aapl = symbols["AAPL"]
        assert aapl["name"] == "Apple Inc."
        assert aapl["displayName"] == "Apple Price"
        assert aapl["chartType"] == "apple-price"
        assert aapl["dataYears"] == 15

        # Check MSTR structure
        mstr = symbols["MSTR"]
        assert mstr["name"] == "MicroStrategy Inc."
        assert mstr["displayName"] == "Strategy Price"
        assert mstr["chartType"] == "mstr-price"
        assert mstr["dataYears"] == 6

    def test_chart_type_mapping(self, config_data):
        """Test that chart type mapping is correct."""
        mapping = config_data["chartTypeMapping"]

        assert mapping["apple-price"] == "AAPL"
        assert mapping["mstr-price"] == "MSTR"

    def test_defaults_section(self, config_data):
        """Test that defaults section exists with expected values."""
        defaults = config_data["defaults"]

        assert defaults["yAxisLabel"] == "Price ($)"
        assert defaults["period"] == "1y"
        assert defaults["dataFormat"] == "csv"
        assert defaults["refreshInterval"] == 86400000
        assert defaults["warningThreshold"] == 24
        assert defaults["errorThreshold"] == 48

    def test_dependencies_preserved(self, config_data):
        """Test that original dependencies are preserved."""
        deps = config_data["dependencies"]

        # Should contain chart types that correspond to symbols
        assert "apple-price" in deps
        assert "mstr-price" in deps

        # Verify structure of apple-price dependency
        apple_dep = deps["apple-price"]
        assert apple_dep["chartType"] == "apple-price"
        assert apple_dep["chartStatus"] == "active"
        assert "primarySource" in apple_dep
        assert "freshness" in apple_dep
        assert "refreshPolicy" in apple_dep

    def test_symbol_to_dependency_consistency(self, config_data):
        """Test that symbol metadata is consistent with dependencies."""
        symbols = config_data["symbolMetadata"]
        deps = config_data["dependencies"]
        mapping = config_data["chartTypeMapping"]

        for symbol, symbol_data in symbols.items():
            chart_type = symbol_data["chartType"]

            # Chart type should be in mapping
            assert chart_type in mapping
            assert mapping[chart_type] == symbol

            # Chart type should have a dependency entry (only check for those that exist)
            # Some symbols like XPEV/NIO may be used only in multi-stock comparisons
            if chart_type in deps:
                assert deps[chart_type]["chartType"] == chart_type


def test_python_script_integration():
    """Test that the Python script can load the consolidated config."""
    import sys
    import os

    # Add scripts directory to path
    script_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(script_dir))

    try:
        from copy_stock_data import get_symbol_data_years

        # Test known symbols
        assert get_symbol_data_years("AAPL") == 15
        assert get_symbol_data_years("MSTR") == 6
        assert get_symbol_data_years("UNKNOWN") == 1  # Default fallback

    finally:
        # Clean up path
        sys.path.remove(str(script_dir))


if __name__ == "__main__":
    pytest.main([__file__])
