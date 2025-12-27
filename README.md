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

tool = SalesforceTool()

# Query contacts
result = tool.run({
    "operation": "query",
    "query": "SELECT Id, Name, Email FROM Contact LIMIT 5"
})
```

## Operations

| Operation | Description | Required Parameters |
|-----------|-------------|---------------------|
| `query` | Execute SOQL queries | `query` |
| `describe` | Get object schema | `object_name` |
| `list_objects` | List all SObjects | — |
| `create` | Create a record | `object_name`, `record_data` |
| `update` | Update a record | `object_name`, `record_id`, `record_data` |
| `delete` | Delete a record | `object_name`, `record_id` |
| `get_field_metadata` | Get field details | `object_name`, `field_name` |

### Examples

```python
# Describe an object
tool.run({"operation": "describe", "object_name": "Account"})

# Create a record
tool.run({
    "operation": "create",
    "object_name": "Contact",
    "record_data": {"LastName": "Doe", "Email": "doe@example.com"}
})

# Update a record
tool.run({
    "operation": "update",
    "object_name": "Contact",
    "record_id": "003XXXXXXXXXXXXXXX",
    "record_data": {"Email": "updated@example.com"}
})

# Delete a record
tool.run({"operation": "delete", "object_name": "Contact", "record_id": "003XXXXXXXXXXXXXXX"})

# Get field metadata
tool.run({"operation": "get_field_metadata", "object_name": "Contact", "field_name": "Email"})
```

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
