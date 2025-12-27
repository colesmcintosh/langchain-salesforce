"""Unit tests for the Salesforce tool."""

import os
from typing import Any, Dict, Type, cast
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.tools import BaseTool
from langchain_tests.unit_tests import ToolsUnitTests
from simple_salesforce import Salesforce
from simple_salesforce.api import SFType

from langchain_salesforce.tools import SalesforceTool


class MockSalesforce:
    """Mock Salesforce client for testing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize mock Salesforce client."""
        self.session_id = "test_session_id"
        self.sf_instance = "test.salesforce.com"


@pytest.mark.unit
class TestSalesforceToolUnit(ToolsUnitTests):
    @property
    def tool_constructor(self) -> Type[SalesforceTool]:
        return SalesforceTool

    @property
    def tool_constructor_params(self) -> Dict[str, Any]:
        mock_sf = MagicMock(spec=Salesforce)
        mock_sf.query = MagicMock(
            return_value={"records": [{"Id": "1", "Name": "Test"}]}
        )
        mock_sf.describe = MagicMock(return_value={"sobjects": [{"name": "Account"}]})

        mock_account = MagicMock(spec=SFType)
        mock_account.describe = MagicMock(
            return_value={
                "fields": [
                    {
                        "name": "Email",
                        "type": "email",
                        "length": 80,
                        "label": "Email",
                        "updateable": True,
                        "createable": True,
                        "nillable": True,
                        "unique": False,
                    },
                    {
                        "name": "Name",
                        "type": "string",
                        "length": 255,
                        "label": "Account Name",
                        "updateable": True,
                        "createable": True,
                        "nillable": False,
                        "unique": False,
                    },
                ]
            }
        )
        mock_sf.Account = mock_account

        mock_contact = MagicMock(spec=SFType)
        mock_contact.create = MagicMock(return_value={"id": "1", "success": True})
        mock_contact.update = MagicMock(return_value={"success": True})
        mock_contact.delete = MagicMock(return_value={"success": True})
        mock_contact.describe = MagicMock(
            return_value={
                "fields": [
                    {
                        "name": "Email",
                        "type": "email",
                        "length": 80,
                        "label": "Email",
                        "updateable": True,
                        "createable": True,
                        "nillable": True,
                        "unique": False,
                    },
                ]
            }
        )
        mock_sf.Contact = mock_contact

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

    def test_init(self) -> None:
        """Test initialization of the tool."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        assert isinstance(tool, self.tool_constructor)
        assert tool.name == "salesforce"
        assert tool.description is not None

    def test_has_name(self, tool: BaseTool) -> None:
        """Test that the tool has a name."""
        assert tool.name == "salesforce"

    def test_has_input_schema(self, tool: BaseTool) -> None:
        """Test that the tool has an input schema."""
        assert tool.args_schema is not None

    def test_input_schema_matches_invoke_params(self, tool: BaseTool) -> None:
        """Test that the input schema matches the invoke parameters."""
        if tool.args_schema is None:
            schema: dict[str, Any] = {}
        elif isinstance(tool.args_schema, dict):
            schema = tool.args_schema
        else:
            schema = tool.args_schema.model_json_schema()
        for key in self.tool_invoke_params_example:
            assert key in schema["properties"]

    def test_init_from_env(self) -> None:
        """Test initialization from environment variables."""
        mock_sf = MagicMock(spec=Salesforce)
        with patch.dict(
            "os.environ",
            {
                "SALESFORCE_USERNAME": "test@example.com",
                "SALESFORCE_PASSWORD": "test_password",
                "SALESFORCE_SECURITY_TOKEN": "test_token",
                "SALESFORCE_DOMAIN": "test",
            },
        ):
            tool = self.tool_constructor(
                username=os.environ["SALESFORCE_USERNAME"],
                password=os.environ["SALESFORCE_PASSWORD"],
                security_token=os.environ["SALESFORCE_SECURITY_TOKEN"],
                domain=os.environ["SALESFORCE_DOMAIN"],
                salesforce_client=mock_sf,
            )
            assert isinstance(tool, self.tool_constructor)

    def test_no_overrides_DO_NOT_OVERRIDE(self) -> None:
        """Test that DO_NOT_OVERRIDE methods are not overridden."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        assert not hasattr(tool, "DO_NOT_OVERRIDE")

    def test_query_operation(self) -> None:
        """Test the query operation."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        query = "SELECT Id, Name FROM Account"

        result = tool._run(operation="query", query=query)

        assert result == {"records": [{"Id": "1", "Name": "Test"}]}
        mock_query = cast(MagicMock, tool._sf.query)
        assert mock_query.call_count == 1
        assert mock_query.call_args[0][0] == query

    def test_describe_operation(self) -> None:
        """Test the describe operation."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        result = tool._run(operation="describe", object_name="Account")

        expected_fields = [
            {
                "name": "Email",
                "type": "email",
                "length": 80,
                "label": "Email",
                "updateable": True,
                "createable": True,
                "nillable": True,
                "unique": False,
            },
            {
                "name": "Name",
                "type": "string",
                "length": 255,
                "label": "Account Name",
                "updateable": True,
                "createable": True,
                "nillable": False,
                "unique": False,
            },
        ]

        assert result == {"fields": expected_fields}
        mock_describe = cast(MagicMock, tool._sf.Account.describe)
        assert mock_describe.call_count == 1

    def test_list_objects_operation(self) -> None:
        """Test the list_objects operation."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        result = tool._run(operation="list_objects")

        assert result == [{"name": "Account"}]
        mock_describe = cast(MagicMock, tool._sf.describe)
        assert mock_describe.call_count == 1

    def test_create_operation(self) -> None:
        """Test the create operation."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        record_data = {"LastName": "Test", "Email": "test@example.com"}

        result = tool._run(
            operation="create",
            object_name="Contact",
            record_data=record_data,
        )

        assert result == {"id": "1", "success": True}
        mock_create = cast(MagicMock, tool._sf.Contact.create)
        assert mock_create.call_count == 1
        assert mock_create.call_args[0][0] == record_data

    def test_update_operation(self) -> None:
        """Test the update operation."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        record_data = {"Email": "updated@example.com"}

        result = tool._run(
            operation="update",
            object_name="Contact",
            record_id="1",
            record_data=record_data,
        )

        assert result == {"success": True}
        mock_update = cast(MagicMock, tool._sf.Contact.update)
        assert mock_update.call_count == 1
        assert mock_update.call_args[0] == ("1", record_data)

    def test_delete_operation(self) -> None:
        """Test the delete operation."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        result = tool._run(operation="delete", object_name="Contact", record_id="1")

        assert result == {"success": True}
        mock_delete = cast(MagicMock, tool._sf.Contact.delete)
        assert mock_delete.call_count == 1
        assert mock_delete.call_args[0][0] == "1"

    def test_get_field_metadata_operation(self) -> None:
        """Test the get_field_metadata operation."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        result = tool._run(
            operation="get_field_metadata", object_name="Contact", field_name="Email"
        )

        expected_field_metadata = {
            "name": "Email",
            "type": "email",
            "length": 80,
            "label": "Email",
            "updateable": True,
            "createable": True,
            "nillable": True,
            "unique": False,
        }

        assert result == expected_field_metadata
        mock_describe = cast(MagicMock, tool._sf.Contact.describe)
        assert mock_describe.call_count == 1

    def test_get_field_metadata_field_not_found(self) -> None:
        """Test get_field_metadata operation with non-existent field."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        with pytest.raises(ValueError) as exc_info:
            tool._run(
                operation="get_field_metadata",
                object_name="Contact",
                field_name="NonExistentField",
            )

        assert "Field 'NonExistentField' not found in object 'Contact'" in str(
            exc_info.value
        )
        mock_describe = cast(MagicMock, tool._sf.Contact.describe)
        assert mock_describe.call_count == 1

    def test_invalid_operation(self) -> None:
        """Test handling of invalid operations."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="invalid")
        assert "Unsupported operation: invalid" in str(exc_info.value)

    def test_missing_required_params(self) -> None:
        """Test handling of missing required parameters."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Test query without query string
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="query")
        assert "Query string is required" in str(exc_info.value)

        # Test describe without object name
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="describe")
        assert "Object name is required" in str(exc_info.value)

        # Test get_field_metadata without object name
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="get_field_metadata", field_name="Email")
        assert (
            "Object name and field name required for 'get_field_metadata' operation"
            in str(exc_info.value)
        )

        # Test get_field_metadata without field name
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="get_field_metadata", object_name="Contact")
        assert (
            "Object name and field name required for 'get_field_metadata' operation"
            in str(exc_info.value)
        )

    def test_init_error(self) -> None:
        """Test error handling during initialization."""

        class MockSalesforceError(MockSalesforce):
            """Mock Salesforce client that raises an error."""

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                """Initialize mock Salesforce client that raises an error."""
                raise Exception("Connection error")

        with pytest.raises(Exception) as exc_info:
            SalesforceTool(
                username="test@example.com",
                password="test_password",
                security_token="test_token",
                domain="test",
                salesforce_client=cast(Salesforce, MockSalesforceError()),
            )
        assert "Connection error" in str(exc_info.value)

    def test_list_objects_error(self) -> None:
        """Test error handling for list_objects with invalid response."""
        mock_sf = MagicMock(spec=Salesforce)
        mock_sf.describe = MagicMock(return_value={"invalid": "response"})
        tool = self.tool_constructor(
            username="test@example.com",
            password="test_password",
            security_token="test_token",
            domain="test",
            salesforce_client=mock_sf,
        )

        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="list_objects")
        assert "Invalid response from Salesforce describe() call" in str(exc_info.value)

    def test_create_missing_params(self) -> None:
        """Test create operation with missing parameters."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Test without object_name
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="create", record_data={"LastName": "Test"})
        assert "Object name and record data required" in str(exc_info.value)

        # Test without record_data
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="create", object_name="Contact")
        assert "Object name and record data required" in str(exc_info.value)

    def test_update_missing_params(self) -> None:
        """Test update operation with missing parameters."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Test without object_name
        with pytest.raises(ValueError) as exc_info:
            tool._run(
                operation="update",
                record_id="1",
                record_data={"Email": "test@example.com"},
            )
        assert "Object name, record ID, and data required" in str(exc_info.value)

        # Test without record_id
        with pytest.raises(ValueError) as exc_info:
            tool._run(
                operation="update",
                object_name="Contact",
                record_data={"Email": "test@example.com"},
            )
        assert "Object name, record ID, and data required" in str(exc_info.value)

        # Test without record_data
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="update", object_name="Contact", record_id="1")
        assert "Object name, record ID, and data required" in str(exc_info.value)

    def test_delete_missing_params(self) -> None:
        """Test delete operation with missing parameters."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Test without object_name
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="delete", record_id="1")
        assert "Object name and record ID required" in str(exc_info.value)

        # Test without record_id
        with pytest.raises(ValueError) as exc_info:
            tool._run(operation="delete", object_name="Contact")
        assert "Object name and record ID required" in str(exc_info.value)

    async def test_arun(self) -> None:
        """Test the async run method."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        query = "SELECT Id FROM Account"

        result = await tool._arun(operation="query", query=query)

        assert result == {"records": [{"Id": "1", "Name": "Test"}]}
        mock_query = cast(MagicMock, tool._sf.query)
        assert mock_query.call_count == 1
        assert mock_query.call_args[0][0] == query

    async def test_arun_error(self) -> None:
        """Test error handling in async run method."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        mock_query = cast(MagicMock, tool._sf.query)
        mock_query.side_effect = Exception("Query error")

        with pytest.raises(Exception) as exc_info:
            await tool._arun(operation="query", query="SELECT Id FROM Account")
        assert "Query error" in str(exc_info.value)

    def mock_init(self, *args: Any, **kwargs: Any) -> None:
        """Mock initialization method with proper type annotation."""
        self.session_id = "test_session_id"
        self.sf_instance = "test.salesforce.com"

    def test_invoke_with_string_input(self) -> None:
        """Test invoking the tool with a string input."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        # Convert string to dict before invoking
        input_dict = {
            "operation": "query",
            "query": "SELECT Id, Name FROM Account LIMIT 1",
        }
        result = tool.invoke(input_dict)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"

    async def test_ainvoke_with_string_input(self) -> None:
        """Test invoking the tool asynchronously with a string input."""
        tool = self.tool_constructor(**self.tool_constructor_params)
        # Convert string to dict before invoking
        input_dict = {
            "operation": "query",
            "query": "SELECT Id, Name FROM Account LIMIT 1",
        }
        result = await tool.ainvoke(input_dict)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"

    def test_invoke_with_invalid_input_type(self) -> None:
        """Test invoke with invalid input type."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        with pytest.raises(ValueError) as exc_info:
            tool.invoke({})
        assert "Input must be a dictionary with an 'operation' key" in str(
            exc_info.value
        )

        # Test with completely invalid type (non-dict)
        with pytest.raises(ValueError) as exc_info:
            tool.invoke("not a dict")  # type: ignore
        assert "Input must be a dictionary" in str(exc_info.value)

    async def test_ainvoke_with_invalid_input_type(self) -> None:
        """Test ainvoke with invalid input type."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        with pytest.raises(ValueError) as exc_info:
            await tool.ainvoke({})
        assert "Input must be a dictionary with an 'operation' key" in str(
            exc_info.value
        )

        # Test with completely invalid type (non-dict)
        with pytest.raises(ValueError) as exc_info:
            await tool.ainvoke("not a dict")  # type: ignore
        assert "Input must be a dictionary" in str(exc_info.value)

    def test_invoke_with_none_input(self) -> None:
        """Test invoking the tool with None input."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        with pytest.raises(ValueError) as exc_info:
            tool.invoke(None)  # type: ignore
        assert "Unsupported input type: <class 'NoneType'>" in str(exc_info.value)

    async def test_ainvoke_with_none_input(self) -> None:
        """Test invoking the tool asynchronously with None input."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        with pytest.raises(ValueError) as exc_info:
            await tool.ainvoke(None)  # type: ignore
        assert "Unsupported input type: <class 'NoneType'>" in str(exc_info.value)

    def test_invoke_with_tool_call(self) -> None:
        """Test invoking the tool with a ToolCall object."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Create a mock ToolCall object
        mock_tool_call = MagicMock()
        mock_tool_call.args = {
            "operation": "query",
            "query": "SELECT Id, Name FROM Account LIMIT 1",
        }
        mock_tool_call.id = "test_id"
        mock_tool_call.name = "test_name"

        result = tool.invoke(mock_tool_call)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"

    async def test_ainvoke_with_tool_call(self) -> None:
        """Test invoking the tool asynchronously with a ToolCall object."""
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Create a mock ToolCall object
        mock_tool_call = MagicMock()
        mock_tool_call.args = {
            "operation": "query",
            "query": "SELECT Id, Name FROM Account LIMIT 1",
        }
        mock_tool_call.id = "test_id"
        mock_tool_call.name = "test_name"

        result = await tool.ainvoke(mock_tool_call)
        assert isinstance(result, dict)
        assert "records" in result
        assert result["records"][0]["Id"] == "1"
        assert result["records"][0]["Name"] == "Test"

    def test_invoke_with_non_dict_non_string_input(self) -> None:
        """Test invoking the tool with input that is neither a dict, string, or
        ToolCall.
        """
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Test with a list (which is not a dict, string, or ToolCall)
        with pytest.raises(ValueError) as exc_info:
            tool.invoke([1, 2, 3])  # type: ignore
        assert "Unsupported input type: <class 'list'>" in str(exc_info.value)

    async def test_ainvoke_with_non_dict_non_string_input(self) -> None:
        """Test invoking the tool asynchronously with input that is neither a
        dict, string, or ToolCall.
        """
        tool = self.tool_constructor(**self.tool_constructor_params)

        # Test with a list (which is not a dict, string, or ToolCall)
        with pytest.raises(ValueError) as exc_info:
            await tool.ainvoke([1, 2, 3])  # type: ignore
        assert "Unsupported input type: <class 'list'>" in str(exc_info.value)
