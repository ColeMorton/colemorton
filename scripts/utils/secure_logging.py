#!/usr/bin/env python3
"""
Secure Logging Utilities

Provides utilities for logging with automatic API key obfuscation and security-aware formatting.
Prevents accidental exposure of sensitive information in log files.
"""

import logging
import re
from typing import Any


class SecureFormatter(logging.Formatter):
    """
    Custom logging formatter that automatically obfuscates API keys and other sensitive data
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Patterns for sensitive data that should be obfuscated
        self.sensitive_patterns = [
            # API key patterns
            (
                re.compile(r'(api_?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9]{8,})', re.IGNORECASE),
                r"\1****\2****",
            ),
            (
                re.compile(
                    r'([A-Z_]+_API_KEY["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9]{8,})',
                    re.IGNORECASE,
                ),
                r"\1****",
            ),
            # Specific API key formats
            (
                re.compile(
                    r'(["\']?)([a-f0-9]{64}|[a-f0-9]{32}|[A-Z0-9]{16,20})(["\']?)',
                    re.IGNORECASE,
                ),
                self._obfuscate_key,
            ),
            # Bearer tokens
            (re.compile(r"(bearer\s+)([a-zA-Z0-9._-]{20,})", re.IGNORECASE), r"\1****"),
            # Basic auth
            (
                re.compile(r"(authorization:\s*basic\s+)([a-zA-Z0-9+/=]{20,})", re.IGNORECASE),
                r"\1****",
            ),
            # URLs with embedded credentials
            (re.compile(r"(https?://[^:]+:)[^@]+(@)", re.IGNORECASE), r"\1****\2"),
            # Generic secrets (key-value pairs)
            (
                re.compile(
                    r'(secret|password|pwd|token)["\']?\s*[:=]\s*["\']?([^"\s]{8,})',
                    re.IGNORECASE,
                ),
                r"\1=****",
            ),
        ]

    def _obfuscate_key(self, match) -> str:
        """Obfuscate an API key while preserving some context"""
        prefix = match.group(1) or ""
        key = match.group(2)
        suffix = match.group(3) or ""

        if len(key) > 8:
            obfuscated = f"{key[:4]}...{key[-4:]}"
        else:
            obfuscated = f"{key[:2]}****{key[-2:]}"

        return f"{prefix}{obfuscated}{suffix}"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with security obfuscation"""
        # Get the original formatted message
        formatted = super().format(record)

        # Apply obfuscation patterns
        for pattern, replacement in self.sensitive_patterns:
            if callable(replacement):
                formatted = pattern.sub(replacement, formatted)
            else:
                formatted = pattern.sub(replacement, formatted)

        return formatted


class SecureLogger:
    """
    Wrapper for logging that ensures sensitive data is automatically obfuscated
    """

    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Add secure formatter if not already present
        if not any(isinstance(handler.formatter, SecureFormatter) for handler in self.logger.handlers):
            self._setup_secure_handlers()

    def _setup_secure_handlers(self):
        """Set up secure logging handlers with obfuscation"""
        # Create secure formatter
        secure_formatter = SecureFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Update existing handlers
        for handler in self.logger.handlers:
            handler.setFormatter(secure_formatter)

        # If no handlers exist, create a secure console handler
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(secure_formatter)
            self.logger.addHandler(console_handler)

    def log_api_status(self, service_name: str, status: dict[str, Any]):
        """Safely log API service status with automatic obfuscation"""
        safe_status = status.copy()

        # Always obfuscate any actual key values
        if "api_key" in safe_status:
            key = safe_status["api_key"]
            if key and len(str(key)) > 8:
                safe_status["api_key"] = f"{str(key)[:4]}...{str(key)[-4:]}"

        # Log the safe status
        self.logger.info(f"API Service Status - {service_name}: {safe_status}")

    def log_config_validation(self, config_name: str, is_valid: bool, details: dict | None = None):
        """Log configuration validation results safely"""
        status = "VALID" if is_valid else "INVALID"
        message = f"Configuration validation - {config_name}: {status}"

        if details:
            # Filter out any sensitive details
            safe_details = {
                k: v
                for k, v in details.items()
                if not any(sensitive in k.lower() for sensitive in ["key", "secret", "password", "token"])
            }
            if safe_details:
                message += f" - Details: {safe_details}"

        self.logger.info(message)

    def debug(self, message: Any, *args, **kwargs):
        """Debug logging with obfuscation"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: Any, *args, **kwargs):
        """Info logging with obfuscation"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: Any, *args, **kwargs):
        """Warning logging with obfuscation"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: Any, *args, **kwargs):
        """Error logging with obfuscation"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: Any, *args, **kwargs):
        """Critical logging with obfuscation"""
        self.logger.critical(message, *args, **kwargs)


def create_secure_logger(name: str, level: int = logging.INFO) -> SecureLogger:
    """Factory function to create a secure logger instance"""
    return SecureLogger(name, level)


def obfuscate_api_keys_in_text(text: str) -> str:
    """
    Utility function to obfuscate API keys in arbitrary text

    Args:
        text: Text that may contain API keys

    Returns:
        Text with API keys obfuscated
    """
    formatter = SecureFormatter()

    # Apply the same patterns used by the formatter
    for pattern, replacement in formatter.sensitive_patterns:
        if callable(replacement):
            # For callable replacements, we need to simulate the match
            def safe_replacement(match):
                return replacement(match)

            text = pattern.sub(safe_replacement, text)
        else:
            text = pattern.sub(replacement, text)

    return text


def setup_secure_logging_for_module(module_name: str, level: int = logging.INFO) -> SecureLogger:
    """
    Set up secure logging for a module with proper obfuscation

    Args:
        module_name: Name of the module
        level: Logging level

    Returns:
        SecureLogger instance
    """
    # Disable any existing loggers to prevent duplicate output
    existing_logger = logging.getLogger(module_name)
    existing_logger.handlers.clear()

    # Create and return secure logger
    return create_secure_logger(module_name, level)


# Example usage and testing
if __name__ == "__main__":
    # Test the secure logging
    test_logger = create_secure_logger("test_secure_logging")

    # These should be obfuscated in the output
    test_logger.info("API_KEY=Q4206ZINHPUCHHKM should be obfuscated")
    test_logger.info("Bearer token abc123def456ghi789 should be hidden")
    test_logger.info('{"api_key": "adf9715a6970ae8a72cb83119284516557c2ea0820c92e33b13689ef0cfa1926"}')
    test_logger.info("FRED_API_KEY: 8e5ae1273bd7a0307a0323ff1ed6ce73")

    # Test API status logging
    test_status = {
        "service": "alpha_vantage",
        "api_key": "Q4206ZINHPUCHHKM",
        "status": "active",
        "rate_limit": 5,
    }
    test_logger.log_api_status("Alpha Vantage", test_status)
