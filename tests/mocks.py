"""Builders for the mocked Salesforce clients used across the unit tests."""

from typing import Any, Dict, List
from unittest.mock import MagicMock

from simple_salesforce import Salesforce
from simple_salesforce.api import SFType

RECORD_ID = "003000000000001"
RECORD_ID_18 = "003000000000001AAA"

QUERY = "SELECT Id, Name FROM Account LIMIT 1"
SOSL = "FIND {Test} IN ALL FIELDS RETURNING Account(Id, Name)"

QUERY_RESULT: Dict[str, Any] = {"records": [{"Id": "1", "Name": "Test"}]}
SEARCH_RESULT: Dict[str, Any] = {"searchRecords": [{"Id": "1", "Name": "Test"}]}
SOBJECTS: List[Dict[str, Any]] = [{"name": "Account"}]
CREATE_RESULT: Dict[str, Any] = {"id": "1", "success": True, "errors": []}
GET_RESULT: Dict[str, Any] = {"Id": RECORD_ID, "Email": "test@example.com"}

EMAIL_FIELD: Dict[str, Any] = {
    "name": "Email",
    "type": "email",
    "length": 80,
    "label": "Email",
    "updateable": True,
    "createable": True,
    "nillable": True,
    "unique": False,
}
NAME_FIELD: Dict[str, Any] = {
    "name": "Name",
    "type": "string",
    "length": 255,
    "label": "Account Name",
    "updateable": True,
    "createable": True,
    "nillable": False,
    "unique": False,
}


def make_sobject(*fields: Dict[str, Any]) -> MagicMock:
    """Build a mocked ``SFType`` accessor.

    ``update``, ``delete`` and ``upsert`` return bare HTTP status codes, matching
    what simple-salesforce hands back.
    """
    sobject = MagicMock(spec=SFType)
    sobject.describe.return_value = {"fields": list(fields)}
    sobject.get.return_value = GET_RESULT
    sobject.create.return_value = CREATE_RESULT
    sobject.update.return_value = 204
    sobject.delete.return_value = 204
    sobject.upsert.return_value = 201
    return sobject


def make_salesforce() -> MagicMock:
    """Build a mocked Salesforce client covering every supported operation."""
    salesforce = MagicMock(spec=Salesforce)
    salesforce.query.return_value = QUERY_RESULT
    salesforce.query_all.return_value = QUERY_RESULT
    salesforce.search.return_value = SEARCH_RESULT
    salesforce.describe.return_value = {"sobjects": SOBJECTS}
    salesforce.Account = make_sobject(EMAIL_FIELD, NAME_FIELD)
    salesforce.Contact = make_sobject(EMAIL_FIELD)
    return salesforce
