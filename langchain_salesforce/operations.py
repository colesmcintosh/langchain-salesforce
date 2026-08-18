"""The Salesforce operations exposed by :class:`~.tools.SalesforceTool`.

Every operation is declared exactly once, by decorating its implementation with
:func:`operation`, which records the parameters it requires and the summary shown
to the model. Dispatch, parameter validation and the input schema description are
all derived from that single declaration.
"""

from typing import Any, Callable, Dict, List, NamedTuple, Tuple, Union

from simple_salesforce import Salesforce

from langchain_salesforce.client import get_sobject
from langchain_salesforce.validation import (
    validate_api_name,
    validate_record_id,
    validate_record_reference,
)

#: Operation parameters, keyed by the field names of ``SalesforceQueryInput``.
Params = Dict[str, Any]

#: What an operation hands back: a Salesforce payload or a list of them.
OperationResult = Union[Dict[str, Any], List[Dict[str, Any]]]

Handler = Callable[[Salesforce, Params], Any]


class Operation(NamedTuple):
    """A single Salesforce operation.

    Attributes:
        name: The value callers pass as ``operation``.
        summary: Short description surfaced to the model in the input schema.
        required: Parameters that must be supplied for this operation.
        handler: Callable performing the operation.
    """

    name: str
    summary: str
    required: Tuple[str, ...]
    handler: Handler


#: Every supported operation, keyed by name, in declaration order.
OPERATIONS: Dict[str, Operation] = {}


def operation(name: str, *required: str, summary: str) -> Callable[[Handler], Handler]:
    """Register the decorated function as the handler for ``name``."""

    def register(handler: Handler) -> Handler:
        OPERATIONS[name] = Operation(name, summary, required, handler)
        return handler

    return register


def _write_result(result: Any, record_id: Any = None) -> Dict[str, Any]:
    """Normalize the result of a write into a dict.

    ``SFType.create`` returns the decoded JSON payload, while ``update``,
    ``upsert`` and ``delete`` return only the bare HTTP status code (``201``
    created, ``204`` no content). Both are surfaced as a dict so callers always
    get the same shape.
    """
    if isinstance(result, dict):
        return result
    status_code = int(result)
    return {
        "id": record_id,
        "success": 200 <= status_code < 300,
        "status_code": status_code,
    }


@operation(
    "query",
    "query",
    summary="run a SOQL query, returning the first batch of up to 2000 records",
)
def _query(salesforce: Salesforce, params: Params) -> Any:
    return salesforce.query(params["query"])


@operation(
    "query_all",
    "query",
    summary="run a SOQL query, following pagination until every record is fetched",
)
def _query_all(salesforce: Salesforce, params: Params) -> Any:
    return salesforce.query_all(params["query"])


@operation(
    "search", "search", summary="run a SOSL search such as FIND {Acme} IN ALL FIELDS"
)
def _search(salesforce: Salesforce, params: Params) -> Any:
    return salesforce.search(params["search"])


@operation("describe", "object_name", summary="get an object's schema")
def _describe(salesforce: Salesforce, params: Params) -> Dict[str, Any]:
    return get_sobject(salesforce, params["object_name"]).describe()


@operation("list_objects", summary="list the available objects")
def _list_objects(salesforce: Salesforce, params: Params) -> Any:
    result = salesforce.describe()
    if not isinstance(result, dict) or "sobjects" not in result:
        raise ValueError("Invalid response from Salesforce describe() call")
    return result["sobjects"]


@operation(
    "get_field_metadata",
    "object_name",
    "field_name",
    summary="get the metadata of a single field",
)
def _field_metadata(salesforce: Salesforce, params: Params) -> Any:
    field_name = validate_api_name(params["field_name"], "field name")
    for field in _describe(salesforce, params).get("fields", []):
        if field.get("name") == field_name:
            return field
    raise ValueError(
        f"Field '{field_name}' not found in object '{params['object_name']}'"
    )


@operation("get", "object_name", "record_id", summary="retrieve one record by ID")
def _get(salesforce: Salesforce, params: Params) -> Any:
    record_id = validate_record_id(params["record_id"])
    return get_sobject(salesforce, params["object_name"]).get(record_id)


@operation("create", "object_name", "record_data", summary="create a record")
def _create(salesforce: Salesforce, params: Params) -> Any:
    sobject = get_sobject(salesforce, params["object_name"])
    return _write_result(sobject.create(params["record_data"]))


@operation(
    "update", "object_name", "record_id", "record_data", summary="update a record"
)
def _update(salesforce: Salesforce, params: Params) -> Any:
    record_id = validate_record_id(params["record_id"])
    sobject = get_sobject(salesforce, params["object_name"])
    return _write_result(sobject.update(record_id, params["record_data"]), record_id)


@operation(
    "upsert",
    "object_name",
    "record_id",
    "record_data",
    summary="create or update a record, addressed by ID or external ID",
)
def _upsert(salesforce: Salesforce, params: Params) -> Any:
    reference = validate_record_reference(params["record_id"])
    sobject = get_sobject(salesforce, params["object_name"])
    return _write_result(sobject.upsert(reference, params["record_data"]), reference)


@operation("delete", "object_name", "record_id", summary="delete a record")
def _delete(salesforce: Salesforce, params: Params) -> Any:
    record_id = validate_record_id(params["record_id"])
    sobject = get_sobject(salesforce, params["object_name"])
    return _write_result(sobject.delete(record_id), record_id)


def operation_names() -> Tuple[str, ...]:
    """The supported operation names, in declaration order."""
    return tuple(OPERATIONS)


def describe_operations() -> str:
    """Render the operation catalogue for the input schema description."""
    return "; ".join(f"'{op.name}' ({op.summary})" for op in OPERATIONS.values())


def execute(salesforce: Salesforce, name: str, params: Params) -> OperationResult:
    """Validate ``params`` and run the operation called ``name``.

    Raises:
        ValueError: If the operation is unknown or a required parameter is
            missing.
    """
    spec = OPERATIONS.get(name)
    if spec is None:
        raise ValueError(
            f"Unsupported operation: {name}. "
            f"Supported operations: {', '.join(operation_names())}."
        )

    missing = [param for param in spec.required if not params.get(param)]
    if missing:
        raise ValueError(
            f"Missing required parameter(s) for '{name}' operation: "
            f"{', '.join(missing)}."
        )
    return spec.handler(salesforce, params)
