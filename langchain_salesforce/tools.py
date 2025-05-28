"""Salesforce tools for interacting with Salesforce CRM."""

from typing import Any, Dict, List, Optional, Type, Union, cast

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
            "'create', 'update', or 'delete'"
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
    """

    name: str = "salesforce"
    description: str = (
        "Tool for interacting with Salesforce CRM. Can query records, describe "
        "object schemas, list available objects, and perform create/update/delete "
        "operations."
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

    def _execute_query_operation(self, query: str) -> Dict[str, Any]:
        """Execute a SOQL query operation."""
        return self._sf.query(query)

    def _execute_describe_operation(self, object_name: str) -> Dict[str, Any]:
        """Execute a describe operation for an object."""
        obj = getattr(self._sf, object_name)
        return obj.describe()

    def _execute_list_objects_operation(self) -> List[Dict[str, Any]]:
        """Execute a list objects operation."""
        result = self._sf.describe()
        if not isinstance(result, dict) or "sobjects" not in result:
            raise ValueError("Invalid response from Salesforce describe() call")
        return result["sobjects"]

    def _execute_create_operation(
        self, object_name: str, record_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a create operation."""
        obj = getattr(self._sf, object_name)
        return obj.create(record_data)

    def _execute_update_operation(
        self, object_name: str, record_id: str, record_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an update operation."""
        obj = getattr(self._sf, object_name)
        return obj.update(record_id, record_data)

    def _execute_delete_operation(
        self, object_name: str, record_id: str
    ) -> Dict[str, Any]:
        """Execute a delete operation."""
        obj = getattr(self._sf, object_name)
        return obj.delete(record_id)

    # pylint: disable=arguments-differ,too-many-arguments,too-many-positional-arguments
    # pylint: disable=too-many-return-statements
    def _run(
        self,
        operation: str,
        object_name: Optional[str] = None,
        query: Optional[str] = None,
        record_data: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, Dict[str, Any], List[Dict[str, Any]]]:
        """Execute Salesforce operation."""
        # Suppress unused-argument warning for run_manager
        _ = run_manager

        try:
            if operation == "query":
                if not query:
                    raise ValueError("Query string is required for 'query' operation")
                return self._execute_query_operation(query)

            if operation == "describe":
                if not object_name:
                    raise ValueError(
                        "Object name is required for 'describe' operation"
                    )
                return self._execute_describe_operation(object_name)

            if operation == "list_objects":
                return self._execute_list_objects_operation()

            if operation == "create":
                if not object_name or not record_data:
                    raise ValueError(
                        "Object name and record data required for 'create' operation"
                    )
                return self._execute_create_operation(object_name, record_data)

            if operation == "update":
                if not object_name or not record_id or not record_data:
                    raise ValueError(
                        "Object name, record ID, and data required for "
                        "'update' operation"
                    )
                return self._execute_update_operation(
                    object_name, record_id, record_data
                )

            if operation == "delete":
                if not object_name or not record_id:
                    raise ValueError(
                        "Object name and record ID required for 'delete' operation"
                    )
                return self._execute_delete_operation(object_name, record_id)

            raise ValueError(f"Unsupported operation: {operation}")

        except (ValueError, AttributeError, KeyError) as exc:
            return f"Error performing Salesforce operation: {str(exc)}"

    # pylint: disable=arguments-differ,too-many-arguments,too-many-positional-arguments
    async def _arun(
        self,
        operation: str,
        object_name: Optional[str] = None,
        query: Optional[str] = None,
        record_data: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, Dict[str, Any], List[Dict[str, Any]]]:
        """Async implementation of Salesforce operations."""
        # Simple-salesforce doesn't have native async support,
        # so we just call the sync version
        try:
            return self._run(
                operation, object_name, query, record_data, record_id, run_manager
            )
        except Exception as exc:
            return f"Error performing Salesforce operation: {str(exc)}"

    def invoke(  # pylint: disable=arguments-renamed
        self,
        tool_input: Union[str, Dict[str, Any], ToolCall],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        """Run the tool."""
        if tool_input is None:
            raise ValueError("Unsupported input type: <class 'NoneType'>")

        if isinstance(tool_input, str):
            raise ValueError("Input must be a dictionary")

        if (hasattr(tool_input, "args") and hasattr(tool_input, "id") and
                hasattr(tool_input, "name")):
            input_dict = cast(Dict[str, Any], tool_input.args)
        else:
            input_dict = cast(Dict[str, Any], tool_input)

        if not isinstance(input_dict, dict):
            raise ValueError(f"Unsupported input type: {type(tool_input)}")

        if "operation" not in input_dict:
            raise ValueError("Input must be a dictionary with an 'operation' key")

        return self._run(**input_dict)

    async def ainvoke(  # pylint: disable=arguments-renamed
        self,
        tool_input: Union[str, Dict[str, Any], ToolCall],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        """Run the tool asynchronously."""
        if tool_input is None:
            raise ValueError("Unsupported input type: <class 'NoneType'>")

        if isinstance(tool_input, str):
            raise ValueError("Input must be a dictionary")

        if (hasattr(tool_input, "args") and hasattr(tool_input, "id") and
                hasattr(tool_input, "name")):
            input_dict = cast(Dict[str, Any], tool_input.args)
        else:
            input_dict = cast(Dict[str, Any], tool_input)

        if not isinstance(input_dict, dict):
            raise ValueError(f"Unsupported input type: {type(tool_input)}")

        if "operation" not in input_dict:
            raise ValueError("Input must be a dictionary with an 'operation' key")

        return await self._arun(**input_dict)
