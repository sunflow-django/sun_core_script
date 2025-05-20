import logging
from unittest.mock import Mock

import pendulum
import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.constants.time_zones import PARIS_TZ
from app.services.streem.utils.validate_json import _validate_dates
from app.services.streem.utils.validation_context import ValidationContext


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> Mock:
    """Mock logging.exception for capturing error messages."""
    mock = Mock()
    monkeypatch.setattr(logging, "exception", mock)
    return mock


@pytest.mark.parametrize(
    ("freq", "num_items"),
    [
        ("1h", 24),
        ("15min", 96),
    ],
    ids=["1h_valid", "15min_valid"],
)
def test_valid_dates(freq: str, num_items: int, mock_logger: Mock) -> None:
    """Test valid date sequences for 1h and 15min frequencies."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [
        {
            "date": start_date.add(minutes=15 * i if freq == "15min" else 60 * i).isoformat(),
            "data": 1.0,
        }
        for i in range(num_items)
    ]
    context = ValidationContext(
        delivery_date="2025-05-20",
        freq=freq,
        mini=0.0,
        maxi=10.0,
    )

    result = _validate_dates(json_data, context)

    assert result is True
    mock_logger.assert_not_called()


@pytest.mark.parametrize(
    ("freq", "num_items", "expected_count"),
    [
        ("1h", 23, 24),
        ("1h", 25, 24),
        ("15min", 95, 96),
        ("15min", 97, 96),
    ],
    ids=[
        "1h_too_few",
        "1h_too_many",
        "15min_too_few",
        "15min_too_many",
    ],
)
def test_invalid_item_count(freq: str, num_items: int, expected_count: int, mock_logger: Mock) -> None:
    """Test incorrect item counts for 1h and 15min frequencies."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [
        {
            "date": start_date.add(minutes=15 * i if freq == "15min" else 60 * i).isoformat(),
            "data": 1.0,
        }
        for i in range(num_items)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=0.0, maxi=10.0)

    result = _validate_dates(json_data, context)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0] == f"Invalid item count: {num_items}. Expected {expected_count} for {freq} on 2025-05-20"


@pytest.mark.parametrize(
    "freq",
    ["1h", "15min"],
    ids=["1h_wrong_date", "15min_wrong_date"],
)
def test_wrong_date_sequence(freq: str, mock_logger: Mock) -> None:
    """Test incorrect date sequences (e.g., wrong date in sequence)."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    num_items = 24 if freq == "1h" else 96
    json_data = [
        {
            "date": (
                # Introduce a wrong date at index 1
                start_date.add(days=1).isoformat()
                if i == 1
                else start_date.add(minutes=15 * i if freq == "15min" else 60 * i).isoformat()
            ),
            "data": 1.0,
        }
        for i in range(num_items)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=0.0, maxi=10.0)

    result = _validate_dates(json_data, context)

    assert result is False
    mock_logger.assert_not_called()  # No exception logged, just sequence mismatch


@pytest.mark.parametrize(
    ("freq", "invalid_date", "index"),
    [
        ("1h", "2025-05-20T", 0),
        ("1h", "invalid_date", 1),
        ("15min", "2025-05-20T25:00:00+02:00", 2),
        ("15min", "", 3),
    ],
    ids=["1h_not_iso", "1h_invalid", "15min_invalid_hour", "15min_empty"],
)
def test_invalid_date_format(freq: str, invalid_date: str, index: int, mock_logger: Mock) -> None:
    """Test invalid date formats in the sequence."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    num_items = 24 if freq == "1h" else 96
    json_data = [
        {
            "date": invalid_date
            if i == index
            else start_date.add(minutes=15 * i if freq == "15min" else 60 * i).isoformat(),
            "data": 1.0,
        }
        for i in range(num_items)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=0.0, maxi=10.0)

    result = _validate_dates(json_data, context)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0] == f"Invalid date at item {index}: {invalid_date}"


def test_missing_date_key(mock_logger: Mock) -> None:
    """Test missing 'date' key in one item."""
    start_date = pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ)
    json_data = [
        {"data": 1.0} if i == 0 else {"date": start_date.add(hours=i).isoformat(), "data": 1.0} for i in range(24)
    ]
    context = ValidationContext(delivery_date="2025-05-20", freq="1h", mini=0.0, maxi=10.0)

    result = _validate_dates(json_data, context)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert args[0] == "Invalid date at item 0: missing"


def test_dates_outside_day(mock_logger: Mock) -> None:
    """Test dates outside the expected day boundaries."""
    start_date = pendulum.datetime(2025, 5, 19, 0, 0, 0, tz=PARIS_TZ)  # Previous day
    json_data = [{"date": start_date.add(hours=i).isoformat(), "data": 1.0} for i in range(24)]
    context = ValidationContext(delivery_date="2025-05-20", freq="1h", mini=0.0, maxi=10.0)

    result = _validate_dates(json_data, context)

    assert result is False
    mock_logger.assert_not_called()  # Fails due to sequence mismatch, not parsing error
