import logging
from unittest.mock import Mock

import pendulum
import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.constants.time_zones import PARIS_TZ
from app.services.streem.utils.validate_json import _validate_schema


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> Mock:
    """Mocking logging."""
    mock = Mock()
    monkeypatch.setattr(logging, "exception", mock)
    return mock


@pytest.mark.parametrize(
    ("num_items", "expected_result"),
    [
        (23, True),
        (24, True),
        (25, True),
        (22, False),
        (26, False),
    ],
    ids=["min_23", "normal_24", "max_25", "below_min_22", "above_max_26"],
)
def test_item_count(
    num_items: int,
    *,
    expected_result: bool,
    mock_logger: Mock,
) -> None:
    """Test item count constraints (minItems: 23, maxItems: 25)."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [{"date": start_date.add(hours=i).isoformat(), "data": float(i)} for i in range(num_items)]

    result = _validate_schema(json_data, 0, 30)

    assert result == expected_result
    if not expected_result:
        mock_logger.assert_called_once()
        args, _ = mock_logger.call_args
        assert args[0].startswith("Schema validation failed:")


@pytest.mark.parametrize(
    ("mini", "maxi", "data_value"),
    [
        (1.0, 22.0, 0.0),
        (1.0, 22.0, 23.0),
    ],
    ids=["data_below_mini", "data_above_maxi"],
)
def test_data_out_of_range(
    mini: float,
    maxi: float,
    data_value: float,
    mock_logger: Mock,
) -> None:
    """Test data values outside mini/maxi range."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [{"date": start_date.add(hours=i).isoformat(), "data": data_value} for i in range(24)]

    result = _validate_schema(json_data, mini, maxi)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0].startswith("Schema validation failed:")


def test_invalid_structure(mock_logger: Mock) -> None:
    """Test invalid structure (extra keys, missing keys, non-dict)."""
    invalid_structures = [
        # Extra key
        [{"date": "2025-05-20T00:00:00+02:00", "data": 0.0, "extra": 1}] * 23,
        # Missing data key
        [{"date": "2025-05-20T00:00:00+02:00"}] * 23,
        # Missing date key
        [{"data": 0.0}] * 23,
        # Non-dictionary item
        [{"date": "2025-05-20T00:00:00+02:00", "data": 0.0}] * 22 + ["not a dict"],
    ]
    for json_data in invalid_structures:
        result = _validate_schema(json_data, mini=0.0, maxi=23.0)

        assert result is False
        mock_logger.assert_called()
        args, _ = mock_logger.call_args
        assert args[0].startswith("Schema validation failed:")
        mock_logger.reset_mock()


@pytest.mark.parametrize(
    ("invalid_date", "expected_error_contains"),
    [
        ("2025-05-20", "is not a 'date-time'"),  # Not ISO 8601 date-time
        ("2025-05-20T25:00:00+02:00", "is not a 'date-time'"),  # Invalid hour
        ("invalid_date", "is not a 'date-time'"),  # Non-date string
        ("", "is not a 'date-time'"),  # Empty string
    ],
    ids=["not_iso", "invalid_hour", "non_date", "empty"],
)
def test_invalid_date(
    invalid_date: str,
    expected_error_contains: str,
    mock_logger: Mock,
) -> None:
    """Test invalid date formats."""
    json_data = [{"date": invalid_date, "data": float(i)} for i in range(24)]

    result = _validate_schema(json_data, mini=0.0, maxi=23.0)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0].startswith("Schema validation failed:")
    assert expected_error_contains in args[0]


def test_data_boundary_values() -> None:
    """Test data at boundary values (mini and maxi)."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [{"date": start_date.add(hours=i).isoformat(), "data": 0.0 if i % 2 == 0 else 23.0} for i in range(23)]
    result = _validate_schema(json_data, mini=0.0, maxi=23.0)
    assert result is True


def test_non_numeric_data(mock_logger: Mock) -> None:
    """Test non-numeric data values."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [{"date": start_date.add(hours=i).isoformat(), "data": "not a number"} for i in range(23)]

    result = _validate_schema(json_data, mini=0.0, maxi=23.0)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0].startswith("Schema validation failed:")
