import logging
from unittest.mock import Mock

import pendulum
import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.constants.time_zones import PARIS_TZ
from app.services.streem.utils.validate_json import _validate_schema
from app.services.streem.utils.validation_context import ValidationContext


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> Mock:
    """Mocking logging."""
    mock = Mock()
    monkeypatch.setattr(logging, "exception", mock)
    return mock


@pytest.mark.parametrize(
    ("freq", "num_items", "expected_result"),
    [
        ("1h", 22, False),
        ("1h", 23, True),
        ("1h", 24, True),
        ("1h", 25, True),
        ("1h", 26, False),
        ("15min", 91, False),
        ("15min", 92, True),
        ("15min", 96, True),
        ("15min", 100, True),
        ("15min", 101, False),
    ],
    ids=[
        "1h_below_min_22",
        "1h_min_23",
        "1h_normal_24",
        "1h_max_25",
        "1h_above_max_26",
        "15min_below_min_91",
        "15min_min_92",
        "15min_normal_96",
        "15min_max_100",
        "15min_above_max_101",
    ],
)
def test_item_count(
    freq: str,
    num_items: int,
    *,
    expected_result: bool,
    mock_logger: Mock,
) -> None:
    """Test item count constraints (minItems and maxItems based on freq)."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [
        {"date": start_date.add(minutes=15 * i if freq == "15min" else i).isoformat(), "data": float(i)}
        for i in range(num_items)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=0.0, maxi=100.0)

    result = _validate_schema(json_data, context)

    assert result == expected_result
    if not expected_result:
        mock_logger.assert_called_once()
        args, _ = mock_logger.call_args
        assert args[0].startswith("Schema validation failed:")


@pytest.mark.parametrize(
    ("freq", "mini", "maxi", "data_value"),
    [
        ("1h", 1.0, 22.0, 0.0),
        ("1h", 1.0, 22.0, 23.0),
        ("15min", 1.0, 22.0, 0.0),
        ("15min", 1.0, 22.0, 23.0),
    ],
    ids=[
        "1h_data_below_mini",
        "1h_data_above_maxi",
        "15min_data_below_mini",
        "15min_data_above_maxi",
    ],
)
def test_data_out_of_range(
    freq: str,
    mini: float,
    maxi: float,
    data_value: float,
    mock_logger: Mock,
) -> None:
    """Test data values outside mini/maxi range."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    num_items = 24 if freq == "1h" else 96
    json_data = [
        {
            "date": start_date.add(minutes=15 * i if freq == "15min" else i).isoformat(),
            "data": data_value,
        }
        for i in range(num_items)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=mini, maxi=maxi)

    result = _validate_schema(json_data, context)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0].startswith("Schema validation failed:")


def test_invalid_structure(mock_logger: Mock) -> None:
    """Test invalid structure (extra keys, missing keys, non-dict)."""
    context = ValidationContext(delivery_date="2025-05-20", freq="1h", mini=0.0, maxi=23.0)
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
        result = _validate_schema(json_data, context)

        assert result is False
        mock_logger.assert_called()
        args, _ = mock_logger.call_args
        assert args[0].startswith("Schema validation failed:")
        mock_logger.reset_mock()


@pytest.mark.parametrize(
    ("freq", "invalid_date", "expected_error_contains"),
    [
        ("1h", "2025-05-20", "is not a 'date-time'"),
        ("1h", "2025-05-20T25:00:00+02:00", "is not a 'date-time'"),
        ("1h", "invalid_date", "is not a 'date-time'"),
        ("1h", "", "is not a 'date-time'"),
        ("15min", "2025-05-20", "is not a 'date-time'"),
        ("15min", "2025-05-20T25:00:00+02:00", "is not a 'date-time'"),
        ("15min", "invalid_date", "is not a 'date-time'"),
        ("15min", "", "is not a 'date-time'"),
    ],
    ids=[
        "1h_not_iso",
        "1h_invalid_hour",
        "1h_non_date",
        "1h_empty",
        "15min_not_iso",
        "15min_invalid_hour",
        "15min_non_date",
        "15min_empty",
    ],
)
def test_invalid_date(
    freq: str,
    invalid_date: str,
    expected_error_contains: str,
    mock_logger: Mock,
) -> None:
    """Test invalid date formats."""
    num_items = 24 if freq == "1h" else 96
    json_data = [{"date": invalid_date, "data": float(i)} for i in range(num_items)]
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=0.0, maxi=23.0)

    result = _validate_schema(json_data, context)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0].startswith("Schema validation failed:")
    assert expected_error_contains in args[0]


@pytest.mark.parametrize(
    "freq",
    ["1h", "15min"],
    ids=["1h_boundary", "15min_boundary"],
)
def test_data_boundary_values(freq: str) -> None:
    """Test data at boundary values (mini and maxi)."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    num_items = 23 if freq == "1h" else 92
    json_data = [
        {
            "date": start_date.add(minutes=15 * i if freq == "15min" else i).isoformat(),
            "data": 0.0 if i % 2 == 0 else 23.0,
        }
        for i in range(num_items)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=0.0, maxi=23.0)

    result = _validate_schema(json_data, context)

    assert result is True


def test_non_numeric_data(mock_logger: Mock) -> None:
    """Test non-numeric data values."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [
        {
            "date": start_date.add(hours=i).isoformat(),
            "data": "not a number",
        }
        for i in range(23)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq="1h", mini=0.0, maxi=23.0)

    result = _validate_schema(json_data, context)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0].startswith("Schema validation failed:")
