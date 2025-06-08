# langchain-salesforce

[![PyPI version](https://badge.fury.io/py/langchain-salesforce.svg)](https://badge.fury.io/py/langchain-salesforce)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/langchain-salesforce.svg)](https://pypi.org/project/langchain-salesforce/)
[![CI](https://github.com/colesmcintosh/langchain-salesforce/actions/workflows/ci.yml/badge.svg)](https://github.com/colesmcintosh/langchain-salesforce/actions/workflows/ci.yml)
[![Code Quality](https://github.com/colesmcintosh/langchain-salesforce/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/colesmcintosh/langchain-salesforce/actions/workflows/pr-checks.yml)

The `langchain-salesforce` package provides a seamless integration between LangChain and Salesforce CRM, enabling developers to leverage LangChain's powerful framework to interact with Salesforce data.

## Overview

This package allows you to connect to your Salesforce instance and perform various operations, such as querying data with SOQL, inspecting object schemas, and managing records (Create, Read, Update, Delete - CRUD). It is designed to be a flexible tool within the LangChain ecosystem.

## Key Features

-   **Salesforce CRM Integration**: Connect LangChain applications directly to Salesforce.
-   **SOQL Execution**: Run Salesforce Object Query Language (SOQL) queries.
-   **Schema Inspection**: Describe Salesforce object structures.
-   **Object Listing**: List all available SObjects in your Salesforce org.
-   **CRUD Operations**: Create, update, and delete Salesforce records.
-   **Environment Variable Configuration**: Easy setup using standard environment variables.
-   **Comprehensive Error Handling**: Robust error management for Salesforce API interactions.

## Installation

To install the package, run the following command:

```bash
pip install -U langchain-salesforce
```

## Configuration

Before using the tool, configure your Salesforce credentials by setting the following environment variables:

-   `SALESFORCE_USERNAME`: Your Salesforce username.
-   `SALESFORCE_PASSWORD`: Your Salesforce password.
-   `SALESFORCE_SECURITY_TOKEN`: Your Salesforce security token.
-   `SALESFORCE_DOMAIN`: Your Salesforce domain (e.g., "login" for production, "test" for sandbox environments). Defaults to "login".

## Quick Start

Here's a quick example of how to initialize the `SalesforceTool` and query for contacts:

```python
from langchain_salesforce import SalesforceTool
import os

# Initialize the tool (credentials can also be sourced from environment variables)
tool = SalesforceTool(
    username=os.getenv("SALESFORCE_USERNAME", "your-username"),
    password=os.getenv("SALESFORCE_PASSWORD", "your-password"),
    security_token=os.getenv("SALESFORCE_SECURITY_TOKEN", "your-token"),
    domain=os.getenv("SALESFORCE_DOMAIN", "login")
)

# Example: Query for the first 5 contacts
query_result = tool.run({
    "operation": "query",
    "query": "SELECT Id, Name, Email FROM Contact LIMIT 5"
})

print(query_result)
```

## `SalesforceTool` Usage

The `SalesforceTool` is the primary interface for interacting with Salesforce. It accepts a dictionary input specifying the `operation` and its required parameters.

### Supported Operations

#### 1. Query Data (`query`)
Execute SOQL queries to retrieve data from Salesforce.

```python
result = tool.run({
    "operation": "query",
    "query": "SELECT Id, Name, Industry FROM Account WHERE Industry = 'Technology' LIMIT 10"
})
print(result)
```

#### 2. Describe Object Schema (`describe`)
Get the schema information for a specific Salesforce object.

```python
schema = tool.run({
    "operation": "describe",
    "object_name": "Account"
})
print(schema)
```

#### 3. List Available Objects (`list_objects`)
Retrieve a list of all available SObjects in your Salesforce organization.

```python
available_objects = tool.run({
    "operation": "list_objects"
})
print(available_objects)
```

#### 4. Create New Record (`create`)
Create a new record for a specified Salesforce object.

```python
new_contact_details = tool.run({
    "operation": "create",
    "object_name": "Contact",
    "record_data": {
        "LastName": "Doe",
        "FirstName": "John",
        "Email": "john.doe@example.com",
        "Phone": "123-456-7890"
    }
})
print(new_contact_details) # Returns ID of the new record and success status
```

#### 5. Update Existing Record (`update`)
Update fields on an existing Salesforce record.

```python
update_status = tool.run({
    "operation": "update",
    "object_name": "Contact",
    "record_id": "003XXXXXXXXXXXXXXX",  # Replace with an actual Contact ID
    "record_data": {
        "Email": "john.doe.updated@example.com",
        "Description": "Updated contact information."
    }
})
print(update_status) # Returns ID of the updated record and success status
```

#### 6. Delete Record (`delete`)
Delete a Salesforce record by its ID.

```python
delete_confirmation = tool.run({
    "operation": "delete",
    "object_name": "Contact",
    "record_id": "003YYYYYYYYYYYYYYY"  # Replace with an actual Contact ID
})
print(delete_confirmation) # Returns ID of the deleted record and success status
```

## Development

Interested in contributing? Follow these steps to set up your development environment:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git # Replace with your repository URL
    cd langchain-salesforce
    ```

2.  **Install dependencies:**
    This project uses Poetry for dependency management.
    ```bash
    poetry install
    ```

3.  **Run tests:**
    ```bash
    make test
    ```

4.  **Run linters and formatters:**
    ```bash
    make lint
    ```

## CI/CD

This project uses GitHub Actions for continuous integration and deployment. All pull requests must pass the following checks:

- **Code formatting** (ruff format)
- **Import sorting** (ruff) 
- **Linting** (ruff check)
- **Type checking** (mypy)
- **Spelling** (codespell)
- **Unit tests** (pytest on Python 3.9, 3.10, 3.11)

### For Contributors

Before submitting a pull request:

```bash
# Format and fix imports
make format

# Check for issues
make lint  

# Run tests
make test
```

### Branch Protection

The `main` branch is protected and requires:
- All status checks to pass
- At least one approval
- Up-to-date branches

See [CI/CD Setup Guide](.github/SETUP.md) for detailed configuration instructions.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have suggestions or improvements. 

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all CI checks pass
5. Submit a pull request

For detailed guidelines, see our [Contributing Guide](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.