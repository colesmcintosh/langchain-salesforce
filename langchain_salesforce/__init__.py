"""LangChain integration for Salesforce CRM."""

from importlib import metadata

from langchain_salesforce.client import create_salesforce_client
from langchain_salesforce.operations import OPERATIONS, operation_names
from langchain_salesforce.schemas import SalesforceQueryInput
from langchain_salesforce.tools import SalesforceTool

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = "0.0.1"
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "OPERATIONS",
    "SalesforceQueryInput",
    "SalesforceTool",
    "__version__",
    "create_salesforce_client",
    "operation_names",
]
