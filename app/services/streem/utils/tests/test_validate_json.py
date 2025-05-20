from unittest.mock import Mock
from unittest.mock import patch

import pytest

from app.services.streem.utils.validate_json import validate_json


@pytest.mark.parametrize(
    ("schema_result", "dates_result", "expected_result"),
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
        (False, False, False),
    ],
    ids=[
        "both_valid",
        "schema_invalid",
        "dates_invalid",
        "both_invalid",
    ],
)
def test_validate_json(*, schema_result: bool, dates_result: bool, expected_result: bool) -> None:
    """Test validate_json with mocked _validate_schema and _validate_dates."""
    # Mock _validate_schema and _validate_dates
    with (
        patch("app.services.streem.utils.validate_json._validate_schema") as mock_schema,
        patch("app.services.streem.utils.validate_json._validate_dates") as mock_dates,
    ):
        mock_schema.return_value = schema_result
        mock_dates.return_value = dates_result

        # Call validate_json with dummy arguments (not used due to mocks)
        result = validate_json([], Mock())

    assert result == expected_result
