"""LangChain standard unit tests for SalesforceTool."""

from typing import Any, Dict, Type

import pytest

from langchain_salesforce import SalesforceTool
from tests.mocks import QUERY, make_salesforce

try:
    from langchain_tests.unit_tests import ToolsUnitTests
except ImportError:  # pragma: no cover - langchain-tests is a test-only extra
    pytest.skip("langchain-tests is not installed", allow_module_level=True)


@pytest.mark.unit
class TestSalesforceToolUnit(ToolsUnitTests):
    """Runs the LangChain standard tool test suite against SalesforceTool."""

    @property
    def tool_constructor(self) -> Type[SalesforceTool]:
        return SalesforceTool

    @property
    def tool_constructor_params(self) -> Dict[str, Any]:
        return {"salesforce_client": make_salesforce()}

    @property
    def tool_invoke_params_example(self) -> Dict[str, str]:
        return {"operation": "query", "query": QUERY}
