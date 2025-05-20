import logging

from jsonschema import FormatChecker
from jsonschema import ValidationError
from jsonschema import validate


def _validate_schema(json_data: list, mini: float, maxi: float) -> bool:
    """
    Validate the structure of JSON-like data (list).

    Checks:
    - The list has between 23 and 25 items (inclusive).
    - Each item has exactly two keys: 'date' and 'data'.
    - 'date' is a valid ISO 8601 date-time.
    - 'data' is a float between mini and maxi (inclusive).

    Args:
        json_data: List of dictionaries with 'date' and 'data' keys.
        mini: Minimum allowed value for 'data'.
        maxi: Maximum allowed value for 'data'.

    Returns:
        bool: True if validation succeeds, False if it fails.
    """
    schema = {
        "type": "array",
        "minItems": 23,
        "maxItems": 25,
        "items": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date-time"},
                "data": {"type": "number", "minimum": mini, "maximum": maxi},
            },
            "required": ["date", "data"],
            "additionalProperties": False,
        },
    }

    try:
        validate(instance=json_data, schema=schema, format_checker=FormatChecker())
    except ValidationError as e:
        msg = f"Schema validation failed: {e.message}"
        logging.exception(msg)
        return False
    else:
        return True
