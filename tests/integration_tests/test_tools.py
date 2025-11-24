"""Integration tests for the Salesforce tool."""

import os
from typing import Any, Dict, Type
from unittest.mock import MagicMock

import pytest
from langchain_core.tools import BaseTool
from langchain_tests.integration_tests import ToolsIntegrationTests
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import (
    SalesforceAuthenticationFailed,
    SalesforceExpiredSession,
)

from langchain_salesforce.tools import SalesforceTool

# Required environment variables for Salesforce connection
REQUIRED_ENV_VARS = [
    "SALESFORCE_USERNAME",
    "SALESFORCE_PASSWORD",
    "SALESFORCE_SECURITY_TOKEN",
    "SALESFORCE_DOMAIN",
]


def create_salesforce_client() -> Salesforce:
    """Create a new authenticated Salesforce client."""
    try:
        return Salesforce(
            username=os.environ["SALESFORCE_USERNAME"],
            password=os.environ["SALESFORCE_PASSWORD"],
            security_token=os.environ["SALESFORCE_SECURITY_TOKEN"],
            domain=os.environ["SALESFORCE_DOMAIN"],
            client_id="LangChainSalesforceIntegration",
            version="57.0",  # Using latest stable API version
        )
    except (SalesforceAuthenticationFailed, SalesforceExpiredSession) as e:
        pytest.fail(f"Failed to authenticate with Salesforce: {str(e)}")
        raise AssertionError from e


@pytest.mark.integration
class TestSalesforceToolIntegration(ToolsIntegrationTests):
    """Standard integration tests for SalesforceTool."""

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
        result = tool.invoke(self.tool_invoke_params_example)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"

    @pytest.mark.xfail(reason="SalesforceTool requires custom response handling")
    async def test_async_invoke_matches_output_schema(self, tool: BaseTool) -> None:
        """Test that async tool invocation returns valid output."""
        result = await tool.ainvoke(self.tool_invoke_params_example)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"

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


@pytest.mark.integration
class TestSalesforceToolLiveIntegration:
    """Live integration tests for SalesforceTool.

    These tests require actual Salesforce credentials.
    """

    @pytest.fixture(autouse=True)
    def setup_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up environment variables for tests."""
        env_vars = {
            "SALESFORCE_USERNAME": "test@example.com",  # Test placeholder
            "SALESFORCE_PASSWORD": "test_password",  # Test placeholder
            "SALESFORCE_SECURITY_TOKEN": "test_token",  # Test placeholder
            "SALESFORCE_DOMAIN": "test",  # Test placeholder
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

    @pytest.fixture
    def salesforce_client(self) -> Salesforce:
        """Create a new Salesforce client for each test."""
        return create_salesforce_client()

    @pytest.mark.skip(reason="Salesforce password has expired and needs to be reset")
    def test_live_salesforce_connection(self, salesforce_client: Salesforce) -> None:
        """Test actual connection to Salesforce using environment variables."""
        try:
            # First try a simple query that doesn't require much access
            query = "SELECT Id, Username FROM User WHERE Username = :username"
            result = salesforce_client.query(query, include_deleted=False)
            assert isinstance(result, dict)
            assert "records" in result
            assert len(result["records"]) > 0
        except SalesforceExpiredSession:
            # If session expired, create a new client and retry
            salesforce_client = create_salesforce_client()
            result = salesforce_client.query(query, include_deleted=False)
            assert isinstance(result, dict)
            assert "records" in result
            assert len(result["records"]) > 0

    @pytest.mark.skip(reason="Salesforce password has expired and needs to be reset")
    def test_live_salesforce_tool_read_operations(
        self,
        salesforce_client: Salesforce,
    ) -> None:
        """Test SalesforceTool with actual Salesforce connection.

        Tests read-only operations.
        """
        try:
            tool = SalesforceTool(
                username=os.environ["SALESFORCE_USERNAME"],
                password=os.environ["SALESFORCE_PASSWORD"],
                security_token=os.environ["SALESFORCE_SECURITY_TOKEN"],
                domain=os.environ["SALESFORCE_DOMAIN"],
                salesforce_client=salesforce_client,
            )

            # Test listing available objects (this requires less access)
            list_result = tool.invoke({"operation": "list_objects"})
            assert isinstance(list_result, list)
            assert len(list_result) > 0
            assert isinstance(list_result[0], dict)
            assert "name" in list_result[0]

            # Test querying the current user (more likely to succeed)
            query_result = tool.invoke(
                {
                    "operation": "query",
                    "query": "SELECT Id, Username FROM User WHERE Username = :username",
                    "parameters": {"username": os.environ["SALESFORCE_USERNAME"]},
                }
            )
            assert isinstance(query_result, dict)
            assert "records" in query_result
            assert len(query_result["records"]) > 0

            # Test describing User object (more likely to have access)
            describe_result = tool.invoke(
                {"operation": "describe", "object_name": "User"}
            )
            assert isinstance(describe_result, dict)
            assert "fields" in describe_result

        except SalesforceExpiredSession:
            # If session expired, create a new client and tool, then retry
            salesforce_client = create_salesforce_client()
            tool = SalesforceTool(
                username=os.environ["SALESFORCE_USERNAME"],
                password=os.environ["SALESFORCE_PASSWORD"],
                security_token=os.environ["SALESFORCE_SECURITY_TOKEN"],
                domain=os.environ["SALESFORCE_DOMAIN"],
                salesforce_client=salesforce_client,
            )

            # Retry with simpler operations
            list_result = tool.invoke({"operation": "list_objects"})
            assert isinstance(list_result, list)
            assert len(list_result) > 0

            query_result = tool.invoke(
                {
                    "operation": "query",
                    "query": "SELECT Id, Username FROM User WHERE Username = :username",
                    "parameters": {"username": os.environ["SALESFORCE_USERNAME"]},
                }
            )
            assert isinstance(query_result, dict)
            assert "records" in query_result

            describe_result = tool.invoke(
                {"operation": "describe", "object_name": "User"}
            )
            assert isinstance(describe_result, dict)
            assert "fields" in describe_result


@pytest.mark.integration
class TestSalesforceToolMockedOperations:
    """Tests for SalesforceTool write operations using mocked client."""

    def test_write_operations_with_mock(self) -> None:
        """Test write operations using mocked Salesforce client.

        Tests create/update/delete operations.
        """
        mock_sf = MagicMock(spec=Salesforce)

        # Setup mock responses
        mock_sf.Account = MagicMock()
        mock_sf.Account.create.return_value = {
            "id": "001xx000003DGb2AAG",
            "success": True,
        }
        mock_sf.Account.update.return_value = {"success": True}
        mock_sf.Account.delete.return_value = {"success": True}
        mock_sf.Account.describe.return_value = {
            "fields": [
                {
                    "name": "Name",
                    "type": "string",
                    "length": 255,
                    "label": "Account Name",
                    "updateable": True,
                    "createable": True,
                    "nillable": False,
                    "unique": False,
                }
            ]
        }

        tool = SalesforceTool(
            username="test@example.com",
            password="test_password",
            security_token="test_token",
            domain="test",
            salesforce_client=mock_sf,
        )

        # Test create operation
        create_result = tool.invoke(
            {
                "operation": "create",
                "object_name": "Account",
                "record_data": {"Name": "Test Account"},
            }
        )
        assert isinstance(create_result, dict)
        assert "id" in create_result
        assert "success" in create_result
        mock_sf.Account.create.assert_called_once_with({"Name": "Test Account"})

        # Test update operation
        update_result = tool.invoke(
            {
                "operation": "update",
                "object_name": "Account",
                "record_id": "001xx000003DGb2AAG",
                "record_data": {"Name": "Updated Test Account"},
            }
        )
        assert isinstance(update_result, dict)
        assert "success" in update_result
        mock_sf.Account.update.assert_called_once_with(
            "001xx000003DGb2AAG", {"Name": "Updated Test Account"}
        )

        # Test delete operation
        delete_result = tool.invoke(
            {
                "operation": "delete",
                "object_name": "Account",
                "record_id": "001xx000003DGb2AAG",
            }
        )
        assert isinstance(delete_result, dict)
        assert "success" in delete_result
        mock_sf.Account.delete.assert_called_once_with("001xx000003DGb2AAG")

        # Test get_field_metadata operation
        get_field_metadata_result = tool.invoke(
            {
                "operation": "get_field_metadata",
                "object_name": "Account",
                "field_name": "Name",
            }
        )
        assert isinstance(get_field_metadata_result, dict)
        assert "name" in get_field_metadata_result
        assert get_field_metadata_result["name"] == "Name"
        mock_sf.Account.describe.assert_called_once()
