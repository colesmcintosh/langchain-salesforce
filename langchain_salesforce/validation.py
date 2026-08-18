"""Validation helpers for Salesforce identifiers.

Object and field API names are restricted to letters, digits and underscores and
must begin with a letter, while record IDs are always 15 (case-sensitive) or 18
(case-insensitive) alphanumeric characters. Checking these before a name reaches
``getattr()`` on the Salesforce client keeps callers from reaching arbitrary
client attributes such as ``session`` or ``__class__``.
"""

import re
from typing import Pattern

#: API names: start with a letter, then letters, digits or underscores. This also
#: covers namespaced and custom names such as ``ns__My_Object__c``.
API_NAME_RE: Pattern[str] = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

#: Record IDs: 15 case-sensitive characters, optionally with the 3 character
#: case-insensitive checksum suffix.
RECORD_ID_RE: Pattern[str] = re.compile(r"^[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?$")


def validate_api_name(name: str, kind: str = "object name") -> str:
    """Return ``name`` if it is a well formed Salesforce API name.

    Args:
        name: The object or field API name to check.
        kind: Wording used in the error message, e.g. ``"field name"``.

    Raises:
        ValueError: If ``name`` is not a valid API name.
    """
    if not isinstance(name, str) or not API_NAME_RE.match(name):
        raise ValueError(
            f"Invalid Salesforce {kind}: {name!r}. Names must start with a letter "
            "and contain only alphanumeric characters and underscores."
        )
    return name


def validate_record_id(record_id: str) -> str:
    """Return ``record_id`` if it matches the Salesforce ID format.

    Raises:
        ValueError: If ``record_id`` is not 15 or 18 alphanumeric characters.
    """
    if not isinstance(record_id, str) or not RECORD_ID_RE.match(record_id):
        raise ValueError(
            f"Invalid Salesforce record ID: {record_id!r}. Record IDs must be 15 "
            "or 18 alphanumeric characters."
        )
    return record_id


def validate_record_reference(reference: str) -> str:
    """Return ``reference`` if it identifies a record for an upsert.

    Upserts address a record either by its Salesforce ID or by an external ID,
    written as ``ExternalIdField__c/value``.

    Raises:
        ValueError: If ``reference`` is neither form.
    """
    if isinstance(reference, str) and "/" in reference:
        field_name, _, external_id = reference.partition("/")
        validate_api_name(field_name, "external ID field name")
        if not external_id or "/" in external_id:
            raise ValueError(
                f"Invalid Salesforce external ID reference: {reference!r}. Use "
                "'ExternalIdField__c/value'."
            )
        return reference
    return validate_record_id(reference)
