"""Salesforce tool for interacting with Salesforce CRM."""

from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, PrivateAttr
from simple_salesforce import Salesforce

from langchain_salesforce.client import (
    DEFAULT_API_VERSION,
    DEFAULT_CLIENT_ID,
    create_salesforce_client,
)
from langchain_salesforce.operations import OperationResult, execute
from langchain_salesforce.schemas import SalesforceQueryInput


class SalesforceTool(BaseTool):
    """Tool for interacting with Salesforce CRM using simple-salesforce.

    Setup:
        Install the package and provide credentials, either as constructor
        arguments or through the environment:

        .. code-block:: bash

            pip install langchain-salesforce
            export SALESFORCE_USERNAME="your-username"
            export SALESFORCE_PASSWORD="your-password"
            export SALESFORCE_SECURITY_TOKEN="your-security-token"
            export SALESFORCE_DOMAIN="login"  # or "test" for a sandbox

    Examples:
        .. code-block:: python

            tool = SalesforceTool()

            tool.invoke({
                "operation": "query",
                "query": "SELECT Id, Name FROM Contact LIMIT 5",
            })
            tool.invoke({"operation": "describe", "object_name": "Account"})
            tool.invoke({
                "operation": "create",
                "object_name": "Contact",
                "record_data": {"LastName": "Smith"},
            })

    The full list of operations, and the parameters each one needs, lives in
    :data:`langchain_salesforce.operations.OPERATIONS`.
    """

    name: str = "salesforce"
    description: str = (
        "Tool for interacting with Salesforce CRM. Can run SOQL queries and SOSL "
        "searches, describe object schemas, list available objects, get field "
        "metadata, and create, read, update, upsert and delete records."
    )
    args_schema: Type[BaseModel] = SalesforceQueryInput
    _sf: Salesforce = PrivateAttr()

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_token: Optional[str] = None,
        domain: Optional[str] = None,
        salesforce_client: Optional[Salesforce] = None,
        *,
        version: str = DEFAULT_API_VERSION,
        client_id: str = DEFAULT_CLIENT_ID,
    ) -> None:
        """Initialize the Salesforce connection.

        Credentials that are not passed in are read from the environment; pass
        ``salesforce_client`` to reuse an already authenticated client.
        """
        super().__init__()
        self._sf = salesforce_client or create_salesforce_client(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain,
            version=version,
            client_id=client_id,
        )

    def _run(self, operation: str, **params: Any) -> OperationResult:
        """Execute a Salesforce operation.

        Raises:
            ValueError: If the operation is unknown or a required parameter is
                missing.
        """
        return execute(self._sf, operation, params)
