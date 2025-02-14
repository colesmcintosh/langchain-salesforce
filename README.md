# langchain-salesforce

This package contains the LangChain integration with Salesforce, providing tools to interact with Salesforce CRM data using LangChain's framework.

## Features

- Salesforce CRM integration with LangChain
- SOQL query execution
- Object schema inspection
- CRUD operations on Salesforce objects
- Comprehensive error handling

## Installation

```bash
pip install -U langchain-salesforce
```

## Configuration

Configure your Salesforce credentials by setting the following environment variables:

* `SALESFORCE_USERNAME` - Your Salesforce username
* `SALESFORCE_PASSWORD` - Your Salesforce password
* `SALESFORCE_SECURITY_TOKEN` - Your Salesforce security token
* `SALESFORCE_DOMAIN` - Your Salesforce domain (defaults to "login", use "test" for sandbox)

## Usage

The `SalesforceTool` class provides a comprehensive interface to interact with Salesforce CRM:

```python
from langchain_salesforce import SalesforceTool

# Initialize the tool
tool = SalesforceTool(
    username="your-username",
    password="your-password",
    security_token="your-security-token",
    domain="login"  # or "test" for sandbox
)

# Query contacts
result = tool.run({
    "operation": "query",
    "query": "SELECT Id, Name, Email FROM Contact LIMIT 5"
})

# Get object schema
schema = tool.run({
    "operation": "describe",
    "object_name": "Account"
})

# Create new contact
new_contact = tool.run({
    "operation": "create",
    "object_name": "Contact",
    "record_data": {"LastName": "Smith", "Email": "smith@example.com"}
})

# Update a contact
updated_contact = tool.run({
    "operation": "update",
    "object_name": "Contact",
    "record_id": "003XXXXXXXXXXXXXXX",
    "record_data": {"Email": "new.email@example.com"}
})

# Delete a contact
delete_result = tool.run({
    "operation": "delete",
    "object_name": "Contact",
    "record_id": "003XXXXXXXXXXXXXXX"
})

# List available objects
objects = tool.run({
    "operation": "list_objects"
})
```

## Supported Operations

- `query`: Execute SOQL queries
- `describe`: Get object schema information
- `list_objects`: List available Salesforce objects
- `create`: Create new records
- `update`: Update existing records
- `delete`: Delete records

## Development

To contribute to this project:

1. Clone the repository
2. Install dependencies with Poetry:
```bash
poetry install
```

3. Run tests:
```bash
make test
```

4. Run linting:
```bash
make lint
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.