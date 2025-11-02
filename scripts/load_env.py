#!/usr/bin/env python3
"""
Environment Variable Loader

Loads environment variables from .env file into the current process.
This ensures that all scripts can access the API keys properly.
"""

import os
from pathlib import Path


def load_env_file(env_path: str = ".env") -> dict:
    """
    Load environment variables from a .env file

    Args:
        env_path: Path to the .env file

    Returns:
        Dictionary of loaded variables
    """
    env_vars = {}
    env_file = Path(env_path)

    if not env_file.exists():
        print("Warning: .env file not found at {env_file.absolute()}")
        return env_vars

    with open(env_file) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Parse key=value pairs
            if "=" not in line:
                print("Warning: Invalid line {line_num} in .env file: {line}")
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # Set in environment
            os.environ[key] = value
            env_vars[key] = value

    return env_vars


def ensure_env_loaded():
    """Ensure .env file is loaded, call this at the start of scripts"""
    if not os.getenv("ALPHA_VANTAGE_API_KEY"):
        # Try to load from .env file
        loaded = load_env_file()
        if loaded:
            print("Loaded {len(loaded)} environment variables from .env file")


if __name__ == "__main__":
    # Load environment variables when run directly
    loaded_vars = load_env_file()
    print("Loaded {len(loaded_vars)} environment variables:")

    # Print non-sensitive variables
    for key, value in loaded_vars.items():
        if "API_KEY" in key:
            print("  {key}=****")
        else:
            print("  {key}={value}")
