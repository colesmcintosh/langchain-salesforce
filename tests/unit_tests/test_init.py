"""Unit tests for package initialization."""

import sys
from importlib import metadata
from unittest.mock import patch


def test_version_fallback() -> None:
    """Test version fallback when package metadata is not available."""
    with patch("importlib.metadata.version", side_effect=metadata.PackageNotFoundError):
        # Save original modules
        original_modules = dict(sys.modules)

        try:
            # Remove langchain_salesforce from sys.modules if it exists
            if "langchain_salesforce" in sys.modules:
                del sys.modules["langchain_salesforce"]

            # Import and test
            import langchain_salesforce

            assert langchain_salesforce.__version__ == "0.0.1"
        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)
