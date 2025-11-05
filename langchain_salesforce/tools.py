"""Salesforce tools for interacting with Salesforce CRM."""

from typing import Any, Callable, Dict, List, Optional, Type, Union, cast

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ToolCall
from pydantic import BaseModel, Field, PrivateAttr
from simple_salesforce import Salesforce


class SalesforceQueryInput(BaseModel):
    """Input schema for Salesforce query operations."""

    operation: str = Field(
        ...,
        description=(
            "The operation to perform: 'query' (SOQL query), 'describe' "
            "(get object schema), 'list_objects' (get available objects), "
            "'create', 'update', 'delete', or 'get_field_metadata'"
        ),
    )
    object_name: Optional[str] = Field(
        None,
        description="The Salesforce object name (e.g., 'Contact', 'Account', 'Lead')",
    )
    query: Optional[str] = Field(
        None, description="The SOQL query string for 'query' operation"
    )
    record_data: Optional[Dict[str, Any]] = Field(
        None, description="Data for create/update operations as key-value pairs"
    )
    record_id: Optional[str] = Field(
        None, description="Salesforce record ID for update/delete operations"
    )
    field_name: Optional[str] = Field(
        None, description="The field name for 'get_field_metadata' operation"
    )


class SalesforceTool(BaseTool):
    """Tool for interacting with Salesforce CRM using simple-salesforce.

    Setup:
        Install required packages and set environment variables:

        .. code-block:: bash

            pip install simple-salesforce
            export SALESFORCE_USERNAME="your-username"
            export SALESFORCE_PASSWORD="your-password"
            export SALESFORCE_SECURITY_TOKEN="your-security-token"
            export SALESFORCE_DOMAIN="login" # or "test" for sandbox

    Examples:
        Query contacts:
            {
                "operation": "query",
                "query": "SELECT Id, Name, Email FROM Contact LIMIT 5"
            }

        Get Account object schema:
            {
                "operation": "describe",
                "object_name": "Account"
            }

        List available objects:
            {
                "operation": "list_objects"
            }

        Create new contact:
            {
                "operation": "create",
                "object_name": "Contact",
                "record_data": {"LastName": "Smith", "Email": "smith@example.com"}
            }

        Get field metadata:
            {
                "operation": "get_field_metadata",
                "object_name": "Contact",
                "field_name": "Email"
            }
    """

    name: str = "salesforce"
    description: str = (
        "Tool for interacting with Salesforce CRM. Can query records, describe "
        "object schemas, list available objects, get field metadata, and perform "
        "create/update/delete operations."
    )
    args_schema: Type[BaseModel] = SalesforceQueryInput
    _sf: Salesforce = PrivateAttr()

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        username: str,
        password: str,
        security_token: str,
        domain: str = "login",
        salesforce_client: Optional[Salesforce] = None,
    ) -> None:
        """Initialize Salesforce connection."""
        super().__init__()
        self._sf = salesforce_client or Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain,
        )

    def _execute_query(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a SOQL query operation."""
        return self._sf.query(query)

    def _execute_describe(self, object_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a describe operation for an object."""
        return getattr(self._sf, object_name).describe()

    def _execute_list_objects(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Execute a list objects operation."""
        result = self._sf.describe()
        if not isinstance(result, dict) or "sobjects" not in result:
            raise ValueError("Invalid response from Salesforce describe() call")
        return result["sobjects"]

    def _execute_create(
        self, object_name: str, record_data: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a create operation."""
        return getattr(self._sf, object_name).create(record_data)

    def _execute_update(
        self,
        object_name: str,
        record_id: str,
        record_data: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute an update operation."""
        return getattr(self._sf, object_name).update(record_id, record_data)

    def _execute_delete(
        self, object_name: str, record_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a delete operation."""
        return getattr(self._sf, object_name).delete(record_id)

    def _execute_get_field_metadata(
        self, object_name: str, field_name: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a get field metadata operation."""
        # Get the full object description
        object_description = getattr(self._sf, object_name).describe()

        # Find the specific field in the fields list
        fields = object_description.get("fields", [])
        field_metadata = next(
            (field for field in fields if field.get("name") == field_name), None
        )

        if field_metadata is None:
            raise ValueError(
                f"Field '{field_name}' not found in object '{object_name}'"
            )
        return field_metadata

    def _validate_operation_params(self, operation: str, **params: Any) -> None:
        """Validate required parameters for each operation."""
        validations = {
            "query": lambda: params.get("query") is not None,
            "describe": lambda: params.get("object_name") is not None,
            "list_objects": lambda: True,
            "create": lambda: params.get("object_name") and params.get("record_data"),
            "update": lambda: (
                params.get("object_name")
                and params.get("record_id")
                and params.get("record_data")
            ),
            "delete": lambda: params.get("object_name") and params.get("record_id"),
            "get_field_metadata": lambda: (
                params.get("object_name") and params.get("field_name")
            ),
        }

        error_messages = {
            "query": "Query string is required for 'query' operation",
            "describe": "Object name is required for 'describe' operation",
            "create": "Object name and record data required for 'create' operation",
            "update": (
                "Object name, record ID, and data required for 'update' operation"
            ),
            "delete": "Object name and record ID required for 'delete' operation",
            "get_field_metadata": (
                "Object name and field name required for 'get_field_metadata' operation"
            ),
        }

        if operation not in validations:
            raise ValueError(f"Unsupported operation: {operation}")

        if not validations[operation]():
            raise ValueError(error_messages[operation])

    def _parse_salesforce_input(
        self, input: Union[str, Dict[Any, Any], ToolCall]
    ) -> Dict[str, Any]:
        """Parse and validate input from various formats."""
        if input is None:
            raise ValueError("Unsupported input type: <class 'NoneType'>")

        if isinstance(input, str):
            raise ValueError("Input must be a dictionary")

        # Handle ToolCall type by checking for required attributes
        if hasattr(input, "args") and hasattr(input, "id") and hasattr(input, "name"):
            input_dict = cast(Dict[str, Any], input.args)  # type: ignore[union-attr]
        else:
            input_dict = cast(Dict[str, Any], input)

        if not isinstance(input_dict, dict):
            raise ValueError(f"Unsupported input type: {type(input)}")

        if "operation" not in input_dict:
            raise ValueError("Input must be a dictionary with an 'operation' key")

        return input_dict

    # pylint: disable=arguments-differ,too-many-arguments,too-many-positional-arguments
    def _run(
        self,
        operation: str,
        object_name: Optional[str] = None,
        query: Optional[str] = None,
        record_data: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None,
        field_name: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Execute Salesforce operation."""
        # Suppress unused-argument warning for run_manager
        _ = run_manager

        # Operation dispatch dictionary
        operations: Dict[
            str, Callable[..., Union[Dict[str, Any], List[Dict[str, Any]]]]
        ] = {
            "query": self._execute_query,
            "describe": self._execute_describe,
            "list_objects": self._execute_list_objects,
            "create": self._execute_create,
            "update": self._execute_update,
            "delete": self._execute_delete,
            "get_field_metadata": self._execute_get_field_metadata,
        }

        params = {
            "object_name": object_name,
            "query": query,
            "record_data": record_data,
            "record_id": record_id,
            "field_name": field_name,
        }

        self._validate_operation_params(operation, **params)
        operation_func = operations[operation]
        return operation_func(**params)

    # pylint: disable=arguments-differ,too-many-arguments,too-many-positional-arguments
    async def _arun(
        self,
        operation: str,
        object_name: Optional[str] = None,
        query: Optional[str] = None,
        record_data: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None,
        field_name: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Async implementation of Salesforce operations."""
        # Simple-salesforce doesn't have native async support,
        # so we just call the sync version
        return self._run(
            operation,
            object_name,
            query,
            record_data,
            record_id,
            field_name,
            run_manager,
        )

    def invoke(
        self,
        input: Union[str, Dict[Any, Any], ToolCall],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        """Run the tool."""
        input_dict = self._parse_salesforce_input(input)
        return self._run(**input_dict)

    async def ainvoke(
        self,
        input: Union[str, Dict[Any, Any], ToolCall],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        """Run the tool asynchronously."""
        input_dict = self._parse_salesforce_input(input)
        return await self._arun(**input_dict)
