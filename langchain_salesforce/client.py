"""Construction of the underlying ``simple-salesforce`` client."""

import os
from typing import Any, Dict, Optional

from simple_salesforce import Salesforce

from langchain_salesforce.validation import validate_api_name

#: ``login`` for production orgs, ``test`` for sandboxes.
DEFAULT_DOMAIN = "login"

#: Salesforce REST API version used when the caller does not pick one.
DEFAULT_API_VERSION = "59.0"

#: Sent as the ``Sforce-Call-Options`` client identifier for API usage tracking.
DEFAULT_CLIENT_ID = "langchain-salesforce"

#: Credential name -> environment variable consulted when it is not passed in.
CREDENTIAL_ENV_VARS: Dict[str, str] = {
    "username": "SALESFORCE_USERNAME",
    "password": "SALESFORCE_PASSWORD",
    "security_token": "SALESFORCE_SECURITY_TOKEN",
    "domain": "SALESFORCE_DOMAIN",
}

#: Credentials that must be resolved before a client can be built.
REQUIRED_CREDENTIALS = ("username", "password", "security_token")


def create_salesforce_client(
    username: Optional[str] = None,
    password: Optional[str] = None,
    security_token: Optional[str] = None,
    domain: Optional[str] = None,
    version: str = DEFAULT_API_VERSION,
    client_id: str = DEFAULT_CLIENT_ID,
) -> Salesforce:
    """Build an authenticated Salesforce client.

    Any credential left as ``None`` falls back to its environment variable (see
    :data:`CREDENTIAL_ENV_VARS`).

    Raises:
        ValueError: If a required credential is neither passed nor set in the
            environment.
    """
    credentials = {
        "username": username,
        "password": password,
        "security_token": security_token,
        "domain": domain,
    }
    resolved = {
        name: value or os.environ.get(CREDENTIAL_ENV_VARS[name])
        for name, value in credentials.items()
    }

    missing = [name for name in REQUIRED_CREDENTIALS if not resolved[name]]
    if missing:
        raise ValueError(
            "Missing Salesforce credentials: "
            f"{', '.join(missing)}. Pass them to SalesforceTool(...) or set "
            f"{', '.join(CREDENTIAL_ENV_VARS[name] for name in missing)}."
        )

    return Salesforce(
        username=resolved["username"],
        password=resolved["password"],
        security_token=resolved["security_token"],
        domain=resolved["domain"] or DEFAULT_DOMAIN,
        version=version,
        client_id=client_id,
    )


def get_sobject(salesforce: Salesforce, object_name: str) -> Any:
    """Return the ``SFType`` accessor for ``object_name`` after validating it."""
    return getattr(salesforce, validate_api_name(object_name))
