"""Integration tests for the Salesforce tool.

The standard LangChain suite runs against a mocked client, while the live tests
only run when real Salesforce credentials are present in the environment.
"""

import os
from typing import Any, Dict, List, Type

import pytest
from langchain_tests.integration_tests import ToolsIntegrationTests

from langchain_salesforce import SalesforceTool
from langchain_salesforce.client import CREDENTIAL_ENV_VARS, REQUIRED_CREDENTIALS
from tests.mocks import QUERY, make_salesforce

LIVE_ENV_VARS = [CREDENTIAL_ENV_VARS[name] for name in REQUIRED_CREDENTIALS]


@pytest.mark.integration
class TestSalesforceToolIntegration(ToolsIntegrationTests):
    """Standard integration tests for SalesforceTool."""

    @property
    def tool_constructor(self) -> Type[SalesforceTool]:
        return SalesforceTool

    @property
    def tool_constructor_params(self) -> Dict[str, Any]:
        return {"salesforce_client": make_salesforce()}

    @property
    def tool_invoke_params_example(self) -> Dict[str, str]:
        return {"operation": "query", "query": QUERY}


@pytest.mark.integration
@pytest.mark.skipif(
    not all(os.environ.get(name) for name in LIVE_ENV_VARS),
    reason=f"Live Salesforce credentials ({', '.join(LIVE_ENV_VARS)}) are not set",
)
class TestSalesforceToolLive:
    """Read-only tests against a real Salesforce org."""

    @pytest.fixture(scope="class")
    def tool(self) -> SalesforceTool:
        return SalesforceTool()

    def test_list_objects(self, tool: SalesforceTool) -> None:
        objects: List[Dict[str, Any]] = tool.invoke({"operation": "list_objects"})
        assert objects and "name" in objects[0]

    def test_query_current_user(self, tool: SalesforceTool) -> None:
        username = os.environ[CREDENTIAL_ENV_VARS["username"]]
        result = tool.invoke(
            {
                "operation": "query",
                "query": (
                    "SELECT Id, Username FROM User "
                    f"WHERE Username = '{username}' LIMIT 1"
                ),
            }
        )
        assert result["records"]

    def test_describe_user(self, tool: SalesforceTool) -> None:
        assert "fields" in tool.invoke({"operation": "describe", "object_name": "User"})

    def test_field_metadata(self, tool: SalesforceTool) -> None:
        field = tool.invoke(
            {
                "operation": "get_field_metadata",
                "object_name": "User",
                "field_name": "Username",
            }
        )
        assert field["name"] == "Username"


@pytest.mark.integration
class TestSalesforceToolWriteOperations:
    """Write operations, exercised against a mocked client."""

    def test_create_update_delete_round_trip(self, sf_tool: SalesforceTool) -> None:
        created = sf_tool.invoke(
            {
                "operation": "create",
                "object_name": "Account",
                "record_data": {"Name": "Test Account"},
            }
        )
        assert created["success"]

        record_id = "001xx000003DGb2AAG"
        updated = sf_tool.invoke(
            {
                "operation": "update",
                "object_name": "Account",
                "record_id": record_id,
                "record_data": {"Name": "Updated Test Account"},
            }
        )
        assert updated == {"id": record_id, "success": True, "status_code": 204}

        deleted = sf_tool.invoke(
            {
                "operation": "delete",
                "object_name": "Account",
                "record_id": record_id,
            }
        )
        assert deleted == {"id": record_id, "success": True, "status_code": 204}
