"""Unit tests for the Salesforce identifier validators."""

from typing import Any

import pytest

from langchain_salesforce.validation import (
    validate_api_name,
    validate_record_id,
    validate_record_reference,
)


@pytest.mark.parametrize(
    "name", ["Account", "Contact", "My_Custom_Object__c", "ns__Object__c", "A1"]
)
def test_valid_api_names(name: str) -> None:
    assert validate_api_name(name) == name


@pytest.mark.parametrize(
    "name",
    ["", "1Account", "_session", "__class__", "Account.Name", "a b", "a/b", None],
)
def test_invalid_api_names(name: Any) -> None:
    with pytest.raises(ValueError, match="Invalid Salesforce object name"):
        validate_api_name(name)


def test_api_name_error_mentions_kind() -> None:
    with pytest.raises(ValueError, match="Invalid Salesforce field name"):
        validate_api_name("bad name", "field name")


@pytest.mark.parametrize("record_id", ["003000000000001", "003000000000001AAA"])
def test_valid_record_ids(record_id: str) -> None:
    assert validate_record_id(record_id) == record_id


@pytest.mark.parametrize(
    "record_id",
    [
        "",
        "1",
        "abc",
        "003000000000001A",
        "003000000000001AAAA",
        "003-00000000001",
        None,
    ],
)
def test_invalid_record_ids(record_id: Any) -> None:
    with pytest.raises(ValueError, match="Invalid Salesforce record ID"):
        validate_record_id(record_id)


@pytest.mark.parametrize(
    "reference", ["003000000000001", "External_Id__c/abc-123", "Ext__c/1"]
)
def test_valid_record_references(reference: str) -> None:
    assert validate_record_reference(reference) == reference


@pytest.mark.parametrize(
    ("reference", "message"),
    [
        ("bad name/1", "Invalid Salesforce external ID field name"),
        ("External_Id__c/", "Invalid Salesforce external ID reference"),
        ("External_Id__c/a/b", "Invalid Salesforce external ID reference"),
        ("nope", "Invalid Salesforce record ID"),
    ],
)
def test_invalid_record_references(reference: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        validate_record_reference(reference)
