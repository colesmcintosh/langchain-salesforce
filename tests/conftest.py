"""Shared fixtures for the test suite."""

from unittest.mock import MagicMock

import pytest

from langchain_salesforce import SalesforceTool
from tests.mocks import make_salesforce


@pytest.fixture
def mock_sf() -> MagicMock:
    """A mocked Salesforce client."""
    return make_salesforce()


@pytest.fixture
def sf_tool(mock_sf: MagicMock) -> SalesforceTool:
    """A tool wired to :func:`mock_sf`."""
    return SalesforceTool(salesforce_client=mock_sf)
