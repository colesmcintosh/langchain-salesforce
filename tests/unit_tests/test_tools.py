"""Unit tests for the Salesforce tool's operations."""

from typing import Any, Callable, Dict
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import ToolMessage
from pydantic import ValidationError

from langchain_salesforce import SalesforceTool, operation_names
from tests.mocks import (
    CREATE_RESULT,
    EMAIL_FIELD,
    GET_RESULT,
    NAME_FIELD,
    QUERY,
    QUERY_RESULT,
    RECORD_ID,
    RECORD_ID_18,
    SEARCH_RESULT,
    SOBJECTS,
    SOSL,
    make_salesforce,
)

RECORD_DATA = {"Email": "updated@example.com"}

Check = Callable[[MagicMock], None]

#: One case per supported operation: the call, its result and what it should
#: have asked the Salesforce client to do.
OPERATION_CASES = [
    pytest.param(
        {"operation": "query", "query": QUERY},
        QUERY_RESULT,
        lambda sf: sf.query.assert_called_once_with(QUERY),
        id="query",
    ),
    pytest.param(
        {"operation": "query_all", "query": QUERY},
        QUERY_RESULT,
        lambda sf: sf.query_all.assert_called_once_with(QUERY),
        id="query_all",
    ),
    pytest.param(
        {"operation": "search", "search": SOSL},
        SEARCH_RESULT,
        lambda sf: sf.search.assert_called_once_with(SOSL),
        id="search",
    ),
    pytest.param(
        {"operation": "describe", "object_name": "Account"},
        {"fields": [EMAIL_FIELD, NAME_FIELD]},
        lambda sf: sf.Account.describe.assert_called_once(),
        id="describe",
    ),
    pytest.param(
        {"operation": "list_objects"},
        SOBJECTS,
        lambda sf: sf.describe.assert_called_once(),
        id="list_objects",
    ),
    pytest.param(
        {
            "operation": "get_field_metadata",
            "object_name": "Contact",
            "field_name": "Email",
        },
        EMAIL_FIELD,
        lambda sf: sf.Contact.describe.assert_called_once(),
        id="get_field_metadata",
    ),
    pytest.param(
        {"operation": "get", "object_name": "Contact", "record_id": RECORD_ID},
        GET_RESULT,
        lambda sf: sf.Contact.get.assert_called_once_with(RECORD_ID),
        id="get",
    ),
    pytest.param(
        {
            "operation": "create",
            "object_name": "Contact",
            "record_data": RECORD_DATA,
        },
        CREATE_RESULT,
        lambda sf: sf.Contact.create.assert_called_once_with(RECORD_DATA),
        id="create",
    ),
    pytest.param(
        {
            "operation": "update",
            "object_name": "Contact",
            "record_id": RECORD_ID,
            "record_data": RECORD_DATA,
        },
        {"id": RECORD_ID, "success": True, "status_code": 204},
        lambda sf: sf.Contact.update.assert_called_once_with(RECORD_ID, RECORD_DATA),
        id="update",
    ),
    pytest.param(
        {
            "operation": "upsert",
            "object_name": "Contact",
            "record_id": "External_Id__c/abc-123",
            "record_data": RECORD_DATA,
        },
        {"id": "External_Id__c/abc-123", "success": True, "status_code": 201},
        lambda sf: sf.Contact.upsert.assert_called_once_with(
            "External_Id__c/abc-123", RECORD_DATA
        ),
        id="upsert",
    ),
    pytest.param(
        {"operation": "delete", "object_name": "Contact", "record_id": RECORD_ID_18},
        {"id": RECORD_ID_18, "success": True, "status_code": 204},
        lambda sf: sf.Contact.delete.assert_called_once_with(RECORD_ID_18),
        id="delete",
    ),
]


def test_every_operation_is_covered() -> None:
    """The case table above must exercise every supported operation."""
    covered = {case.values[0]["operation"] for case in OPERATION_CASES}  # type: ignore[index]
    assert covered == set(operation_names())


@pytest.mark.parametrize(("call", "expected", "check"), OPERATION_CASES)
def test_operation(
    sf_tool: SalesforceTool,
    mock_sf: MagicMock,
    call: Dict[str, Any],
    expected: Any,
    check: Check,
) -> None:
    """Each operation returns the Salesforce payload and calls the right client."""
    assert sf_tool.invoke(call) == expected
    check(mock_sf)


@pytest.mark.parametrize(("call", "expected", "check"), OPERATION_CASES)
async def test_operation_async(
    sf_tool: SalesforceTool,
    mock_sf: MagicMock,
    call: Dict[str, Any],
    expected: Any,
    check: Check,
) -> None:
    """Every operation behaves identically when awaited."""
    assert await sf_tool.ainvoke(call) == expected
    check(mock_sf)


@pytest.mark.parametrize(
    ("call", "missing"),
    [
        ({"operation": "query"}, "query"),
        ({"operation": "query_all"}, "query"),
        ({"operation": "search"}, "search"),
        ({"operation": "describe"}, "object_name"),
        ({"operation": "describe", "object_name": ""}, "object_name"),
        ({"operation": "get_field_metadata", "field_name": "Email"}, "object_name"),
        ({"operation": "get_field_metadata", "object_name": "Contact"}, "field_name"),
        ({"operation": "get", "object_name": "Contact"}, "record_id"),
        ({"operation": "create", "record_data": {}}, "object_name, record_data"),
        ({"operation": "create", "object_name": "Contact"}, "record_data"),
        (
            {"operation": "update", "object_name": "Contact", "record_id": RECORD_ID},
            "record_data",
        ),
        (
            {"operation": "update", "object_name": "Contact", "record_data": {}},
            "record_id, record_data",
        ),
        ({"operation": "upsert", "object_name": "Contact"}, "record_id, record_data"),
        ({"operation": "delete", "object_name": "Contact"}, "record_id"),
    ],
)
def test_missing_required_params(
    sf_tool: SalesforceTool, call: Dict[str, Any], missing: str
) -> None:
    """Missing parameters are reported by name before any call is made."""
    with pytest.raises(ValueError, match=f"Missing required parameter.*{missing}"):
        sf_tool.invoke(call)


def test_unsupported_operation(sf_tool: SalesforceTool) -> None:
    """An unknown operation lists the ones that are supported."""
    with pytest.raises(ValueError, match="Unsupported operation: nope"):
        sf_tool.invoke({"operation": "nope"})


@pytest.mark.parametrize(
    "object_name",
    ["__class__", "__dict__", "_session", "Account.Name", "foo bar", "a/b", "1Bad"],
)
def test_invalid_object_name_rejected(
    sf_tool: SalesforceTool, object_name: str
) -> None:
    """Object names that could reach client internals are rejected."""
    with pytest.raises(ValueError, match="Invalid Salesforce object name"):
        sf_tool.invoke({"operation": "describe", "object_name": object_name})


@pytest.mark.parametrize("record_id", ["1", "abc", "../etc/passwd", "' OR 1=1 --"])
def test_invalid_record_id_rejected(sf_tool: SalesforceTool, record_id: str) -> None:
    """Malformed record IDs never reach Salesforce."""
    with pytest.raises(ValueError, match="Invalid Salesforce record ID"):
        sf_tool.invoke(
            {"operation": "delete", "object_name": "Contact", "record_id": record_id}
        )


def test_field_metadata_not_found(sf_tool: SalesforceTool) -> None:
    """A field that the object does not define raises a clear error."""
    with pytest.raises(ValueError, match="Field 'Missing' not found"):
        sf_tool.invoke(
            {
                "operation": "get_field_metadata",
                "object_name": "Contact",
                "field_name": "Missing",
            }
        )


def test_list_objects_invalid_response() -> None:
    """A describe() response without 'sobjects' is reported rather than returned."""
    salesforce = make_salesforce()
    salesforce.describe.return_value = {"invalid": "response"}
    tool = SalesforceTool(salesforce_client=salesforce)

    with pytest.raises(ValueError, match="Invalid response from Salesforce describe"):
        tool.invoke({"operation": "list_objects"})


def test_invoke_with_tool_call_returns_tool_message(sf_tool: SalesforceTool) -> None:
    """A ToolCall gets the standard LangChain ToolMessage treatment."""
    result = sf_tool.invoke(
        {
            "type": "tool_call",
            "name": "salesforce",
            "id": "call-1",
            "args": {"operation": "query", "query": QUERY},
        }
    )

    assert isinstance(result, ToolMessage)
    assert result.tool_call_id == "call-1"
    assert "records" in str(result.content)


@pytest.mark.parametrize("bad_input", [None, [1, 2, 3], {}])
def test_invalid_input_rejected(sf_tool: SalesforceTool, bad_input: Any) -> None:
    """Input that does not match the schema fails validation."""
    with pytest.raises(ValidationError):
        sf_tool.invoke(bad_input)


def test_errors_propagate(sf_tool: SalesforceTool, mock_sf: MagicMock) -> None:
    """Salesforce failures are not swallowed."""
    mock_sf.query.side_effect = Exception("Query error")

    with pytest.raises(Exception, match="Query error"):
        sf_tool.invoke({"operation": "query", "query": QUERY})
