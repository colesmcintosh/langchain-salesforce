"""Input schema for :class:`~langchain_salesforce.tools.SalesforceTool`."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from langchain_salesforce.operations import describe_operations, operation_names


class SalesforceQueryInput(BaseModel):
    """Arguments accepted by the Salesforce tool.

    Which fields are required depends on ``operation``; see
    :data:`~langchain_salesforce.operations.OPERATIONS`.
    """

    operation: str = Field(
        ...,
        description=f"The operation to perform: {describe_operations()}",
        json_schema_extra={"enum": list(operation_names())},
    )
    object_name: Optional[str] = Field(
        None,
        description="The Salesforce object name (e.g., 'Contact', 'Account', 'Lead')",
    )
    query: Optional[str] = Field(
        None,
        description="The SOQL query string for the 'query' and 'query_all' operations",
    )
    search: Optional[str] = Field(
        None,
        description=(
            "The SOSL search string for the 'search' operation, e.g. "
            "'FIND {Acme} IN ALL FIELDS RETURNING Account(Id, Name)'"
        ),
    )
    record_data: Optional[Dict[str, Any]] = Field(
        None, description="Data for create/update/upsert operations as key-value pairs"
    )
    record_id: Optional[str] = Field(
        None,
        description=(
            "Salesforce record ID for get/update/delete operations. For 'upsert' "
            "an external ID may be used instead, written as "
            "'ExternalIdField__c/value'."
        ),
    )
    field_name: Optional[str] = Field(
        None, description="The field name for the 'get_field_metadata' operation"
    )
