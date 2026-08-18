"""Unit tests for building the Salesforce client."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from langchain_salesforce import SalesforceTool, create_salesforce_client
from langchain_salesforce.client import (
    DEFAULT_API_VERSION,
    DEFAULT_CLIENT_ID,
    DEFAULT_DOMAIN,
    get_sobject,
)

CREDENTIALS = {
    "SALESFORCE_USERNAME": "user@example.com",
    "SALESFORCE_PASSWORD": "password",
    "SALESFORCE_SECURITY_TOKEN": "token",
}


@pytest.fixture
def salesforce_ctor() -> Any:
    """Patch the simple-salesforce constructor and hand back the mock."""
    with patch("langchain_salesforce.client.Salesforce") as ctor:
        yield ctor


def kwargs_of(ctor: MagicMock) -> Dict[str, Any]:
    ctor.assert_called_once()
    return dict(ctor.call_args.kwargs)


def test_explicit_credentials_win(
    salesforce_ctor: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Arguments take precedence over the environment."""
    for key, value in CREDENTIALS.items():
        monkeypatch.setenv(key, value)

    create_salesforce_client(
        username="explicit@example.com",
        password="explicit",
        security_token="explicit-token",
        domain="test",
    )

    assert kwargs_of(salesforce_ctor) == {
        "username": "explicit@example.com",
        "password": "explicit",
        "security_token": "explicit-token",
        "domain": "test",
        "version": DEFAULT_API_VERSION,
        "client_id": DEFAULT_CLIENT_ID,
    }


def test_credentials_fall_back_to_environment(
    salesforce_ctor: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing arguments are read from the environment, and domain defaults."""
    for key, value in CREDENTIALS.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("SALESFORCE_DOMAIN", raising=False)

    create_salesforce_client()

    assert kwargs_of(salesforce_ctor) == {
        "username": "user@example.com",
        "password": "password",
        "security_token": "token",
        "domain": DEFAULT_DOMAIN,
        "version": DEFAULT_API_VERSION,
        "client_id": DEFAULT_CLIENT_ID,
    }


def test_version_and_client_id_are_configurable(salesforce_ctor: MagicMock) -> None:
    """The API version and client ID can be overridden."""
    create_salesforce_client(
        username="u", password="p", security_token="t", version="61.0", client_id="app"
    )

    assert kwargs_of(salesforce_ctor)["version"] == "61.0"
    assert kwargs_of(salesforce_ctor)["client_id"] == "app"


@pytest.mark.parametrize("missing", list(CREDENTIALS))
def test_missing_credentials_are_named(
    missing: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The error says which credentials to supply."""
    for key, value in CREDENTIALS.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv(missing)

    with pytest.raises(ValueError, match=f"Missing Salesforce credentials.*{missing}"):
        create_salesforce_client()


def test_tool_builds_client_from_environment(
    salesforce_ctor: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SalesforceTool() with no arguments authenticates from the environment."""
    for key, value in CREDENTIALS.items():
        monkeypatch.setenv(key, value)

    tool = SalesforceTool()

    assert tool._sf is salesforce_ctor.return_value
    assert kwargs_of(salesforce_ctor)["username"] == "user@example.com"


def test_tool_reuses_supplied_client(salesforce_ctor: MagicMock) -> None:
    """An existing client is used as-is, without authenticating again."""
    client = MagicMock()

    assert SalesforceTool(salesforce_client=client)._sf is client
    salesforce_ctor.assert_not_called()


def test_connection_errors_propagate(salesforce_ctor: MagicMock) -> None:
    """Authentication failures surface to the caller."""
    salesforce_ctor.side_effect = Exception("Connection error")

    with pytest.raises(Exception, match="Connection error"):
        SalesforceTool(username="u", password="p", security_token="t")


def test_get_sobject_validates_name() -> None:
    """The SObject accessor rejects names that are not API names."""
    client = MagicMock()
    assert get_sobject(client, "Account") is client.Account

    with pytest.raises(ValueError, match="Invalid Salesforce object name"):
        get_sobject(client, "__class__")
