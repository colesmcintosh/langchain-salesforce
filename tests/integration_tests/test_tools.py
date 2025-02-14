"""Integration tests for the Salesforce tool."""

from typing import Any, Dict, Type
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ToolCall
from langchain_tests.integration_tests import ToolsIntegrationTests
from simple_salesforce import Salesforce

from langchain_salesforce.tools import SalesforceTool


@pytest.mark.integration
class TestSalesforceToolIntegration(ToolsIntegrationTests):
    @property
    def tool_constructor(self) -> Type[SalesforceTool]:
        return SalesforceTool

    @property
    def tool_constructor_params(self) -> Dict[str, Any]:
        mock_sf = MagicMock(spec=Salesforce)
        mock_sf.query = MagicMock(
            return_value={"records": [{"Id": "1", "Name": "Test"}]}
        )
        return {
            "username": "test@example.com",
            "password": "test_password",
            "security_token": "test_token",
            "domain": "test",
            "salesforce_client": mock_sf,
        }

    @property
    def tool_invoke_params_example(self) -> Dict[str, str]:
        return {"operation": "query", "query": "SELECT Id, Name FROM Account LIMIT 1"}

    @pytest.fixture(autouse=True)
    def setup_salesforce_mock(self, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        """Set up Salesforce mock for all tests."""
        mock_sf = MagicMock(spec=Salesforce)
        mock_sf.query = MagicMock(
            return_value={"records": [{"Id": "1", "Name": "Test"}]}
        )

        # Mock the authentication process
        def mock_init(self: Any, *args: Any, **kwargs: Any) -> None:
            self.session_id = "test_session_id"
            self.sf_instance = "test.salesforce.com"

        monkeypatch.setattr("simple_salesforce.Salesforce.__init__", mock_init)
        monkeypatch.setattr("simple_salesforce.Salesforce", mock_sf)
        return mock_sf

    @pytest.mark.xfail(reason="SalesforceTool requires custom response handling")
    def test_invoke_matches_output_schema(self, tool: BaseTool) -> None:
        """Test that tool invocation returns valid output."""
        tool_call = ToolCall(
            name=tool.name,
            args=self.tool_invoke_params_example,
            id="123",
            type="tool_call",
        )
        result = tool.invoke(tool_call)
        assert isinstance(result, ToolMessage)
        assert isinstance(result.content, str)
        # Verify the content is a string representation of the expected response
        assert '"records"' in result.content
        assert '"Id": "1"' in result.content
        assert '"Name": "Test"' in result.content

    @pytest.mark.xfail(reason="SalesforceTool requires custom response handling")
    async def test_async_invoke_matches_output_schema(self, tool: BaseTool) -> None:
        """Test that async tool invocation returns valid output."""
        tool_call = ToolCall(
            name=tool.name,
            args=self.tool_invoke_params_example,
            id="123",
            type="tool_call",
        )
        result = await tool.ainvoke(tool_call)
        assert isinstance(result, ToolMessage)
        assert isinstance(result.content, str)
        # Verify the content is a string representation of the expected response
        assert '"records"' in result.content
        assert '"Id": "1"' in result.content
        assert '"Name": "Test"' in result.content

    @pytest.mark.xfail(reason="SalesforceTool requires custom response handling")
    def test_invoke_no_tool_call(self, tool: BaseTool) -> None:
        """Test that tool can be invoked without a ToolCall."""
        result = tool.invoke(self.tool_invoke_params_example)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"

    @pytest.mark.xfail(reason="SalesforceTool requires custom response handling")
    async def test_async_invoke_no_tool_call(self, tool: BaseTool) -> None:
        """Test that tool can be invoked asynchronously without a ToolCall."""
        result = await tool.ainvoke(self.tool_invoke_params_example)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"
