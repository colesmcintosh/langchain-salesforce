# langchain-salesforce

[![PyPI version](https://badge.fury.io/py/langchain-salesforce.svg)](https://badge.fury.io/py/langchain-salesforce)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/langchain-salesforce.svg)](https://pypi.org/project/langchain-salesforce/)
[![CI](https://github.com/colesmcintosh/langchain-salesforce/actions/workflows/ci.yml/badge.svg)](https://github.com/colesmcintosh/langchain-salesforce/actions/workflows/ci.yml)

LangChain integration for Salesforce CRM. Query data with SOQL, inspect schemas, and manage records (CRUD) directly from your LangChain applications.

## Installation

```bash
pip install -U langchain-salesforce
```

## Configuration

Set these environment variables:

| Variable | Description |
|----------|-------------|
| `SALESFORCE_USERNAME` | Your Salesforce username |
| `SALESFORCE_PASSWORD` | Your Salesforce password |
| `SALESFORCE_SECURITY_TOKEN` | Your Salesforce security token |
| `SALESFORCE_DOMAIN` | `login` (production) or `test` (sandbox). Default: `login` |

## Quick Start

```python
from langchain_salesforce import SalesforceTool

# Credentials are read from the environment, or pass them explicitly:
# SalesforceTool(username=..., password=..., security_token=..., domain=...)
tool = SalesforceTool()

result = tool.invoke({
    "operation": "query",
    "query": "SELECT Id, Name, Email FROM Contact LIMIT 5"
})
```

## Operations

| Operation | Description | Required Parameters |
|-----------|-------------|---------------------|
| `query` | Execute a SOQL query (first batch, up to 2000 records) | `query` |
| `query_all` | Execute a SOQL query and follow pagination for every record | `query` |
| `search` | Execute a SOSL search | `search` |
| `describe` | Get an object schema | `object_name` |
| `list_objects` | List all SObjects | — |
| `get_field_metadata` | Get field details | `object_name`, `field_name` |
| `get` | Retrieve a record by ID | `object_name`, `record_id` |
| `create` | Create a record | `object_name`, `record_data` |
| `update` | Update a record | `object_name`, `record_id`, `record_data` |
| `upsert` | Create or update a record | `object_name`, `record_id`, `record_data` |
| `delete` | Delete a record | `object_name`, `record_id` |

### Examples

```python
# Fetch every matching record, not just the first 2000
tool.invoke({"operation": "query_all", "query": "SELECT Id FROM Contact"})

# Search across objects with SOSL
tool.invoke({
    "operation": "search",
    "search": "FIND {Acme} IN ALL FIELDS RETURNING Account(Id, Name)",
})

# Describe an object and inspect one of its fields
tool.invoke({"operation": "describe", "object_name": "Account"})
tool.invoke({
    "operation": "get_field_metadata",
    "object_name": "Contact",
    "field_name": "Email",
})

# Read a single record
tool.invoke({"operation": "get", "object_name": "Contact", "record_id": "003XXXXXXXXXXXXXXX"})

# Create, update and delete
tool.invoke({
    "operation": "create",
    "object_name": "Contact",
    "record_data": {"LastName": "Doe", "Email": "doe@example.com"},
})
tool.invoke({
    "operation": "update",
    "object_name": "Contact",
    "record_id": "003XXXXXXXXXXXXXXX",
    "record_data": {"Email": "updated@example.com"},
})
tool.invoke({"operation": "delete", "object_name": "Contact", "record_id": "003XXXXXXXXXXXXXXX"})

# Upsert by external ID
tool.invoke({
    "operation": "upsert",
    "object_name": "Contact",
    "record_id": "External_Id__c/abc-123",
    "record_data": {"LastName": "Doe"},
})
```

Reads return the Salesforce payload unchanged. Writes always return a dict:
`create` returns Salesforce's `{"id": ..., "success": ..., "errors": [...]}`, while
`update`, `upsert` and `delete` return
`{"id": ..., "success": True, "status_code": 204}` (`201` when an upsert created
the record).

## Package Layout

| Module | Responsibility |
|--------|----------------|
| `tools.py` | The `SalesforceTool` LangChain tool |
| `operations.py` | Operation registry: each operation's handler and required parameters |
| `schemas.py` | `SalesforceQueryInput`, the tool's argument schema |
| `client.py` | Building the authenticated `simple-salesforce` client |
| `validation.py` | Object name, field name and record ID validators |

## Development

```bash
git clone https://github.com/colesmcintosh/langchain-salesforce.git
cd langchain-salesforce
uv sync --all-groups

make format  # Format code
make lint    # Run linters
make test    # Run tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE).
