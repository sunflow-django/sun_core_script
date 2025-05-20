import logging
from unittest.mock import Mock

import pendulum
import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.constants.time_zones import PARIS_TZ
from app.services.streem.utils.validate_json_pd import validate_json_pd
from app.services.streem.utils.validation_context import ValidationContext


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> Mock:
    """Mock logging.exception for capturing error messages."""
    mock = Mock()
    monkeypatch.setattr(logging, "exception", mock)
    return mock


@pytest.mark.parametrize(
    ("volume_data", "freq", "num_items", "min_value", "max_value", "delivery_date", "tz_offset"),
    [
        # Standard hourly
        (
            [
                {
                    "date": pendulum.parse("2025-05-20T00:00:00+02:00", tz=PARIS_TZ).add(hours=i).isoformat(),
                    "data": i,
                }
                for i in range(24)
            ],
            "1h",
            24,
            0.0,
            100.0,
            "2025-05-20",
            "+02:00",
        ),
        # Standard 15min
        (
            [
                {
                    "date": pendulum.parse("2025-05-20T00:00:00+02:00", tz=PARIS_TZ).add(minutes=15 * i).isoformat(),
                    "data": i,
                }
                for i in range(96)
            ],
            "15min",
            96,
            0.0,
            100.0,
            "2025-05-20",
            "+02:00",
        ),
        # Custom min/max
        (
            [
                {
                    "date": pendulum.parse("2025-05-20T00:00:00+02:00", tz=PARIS_TZ).add(hours=i).isoformat(),
                    "data": 100 + i,
                }
                for i in range(24)
            ],
            "1h",
            24,
            100.0,
            200.0,
            "2025-05-20",
            "+02:00",
        ),
        # UTC timezone
        (
            [
                {
                    "date": pendulum.parse("2025-05-19T22:00:00+00:00", tz="UTC").add(hours=i).isoformat(),
                    "data": i,
                }
                for i in range(24)
            ],
            "1h",
            24,
            0.0,
            3000.0,
            "2025-05-20",
            "+00:00",
        ),
        # DST spring forward 1h
        (
            [
                {"date": "2025-03-30T00:00:00+01:00", "data": 0.0},
                {"date": "2025-03-30T01:00:00+01:00", "data": 1.0},
                {"date": "2025-03-30T03:00:00+02:00", "data": 3.0},
            ]
            + [{"date": f"2025-03-30T{i:02d}:00:00+02:00", "data": i} for i in range(4, 24)],
            "1h",
            23,
            0.0,
            3000.0,
            "2025-03-30",
            "+01:00/+02:00",
        ),
        # DST fall back 1h
        (
            [
                {"date": "2025-10-26T00:00:00+02:00", "data": 0.0},
                {"date": "2025-10-26T01:00:00+02:00", "data": 1.0},
                {"date": "2025-10-26T02:00:00+02:00", "data": 2.0},  # CEST
                {"date": "2025-10-26T02:00:00+01:00", "data": 3.0},  # CET
            ]
            + [{"date": f"2025-10-26T{i:02d}:00:00+01:00", "data": i} for i in range(3, 24)],
            "1h",
            25,
            0.0,
            3000.0,
            "2025-10-26",
            "+02:00/+01:00",
        ),
        # DST spring forward 15min
        (
            [
                {"date": f"2025-03-30T00:{i * 15:02d}:00+01:00", "data": 1000.0}
                for i in range(4)  # 00:00 to 00:45
            ]
            + [
                {"date": f"2025-03-30T01:{i * 15:02d}:00+01:00", "data": 1000.0}
                for i in range(4)  # 01:00 to 01:45
            ]
            + [
                {"date": f"2025-03-30T03:{i * 15:02d}:00+02:00", "data": 1000.0}
                for i in range(4)  # 03:00 to 03:45
            ]
            + [
                {"date": f"2025-03-30T{i // 4:02d}:{(i % 4) * 15:02d}:00+02:00", "data": 1000.0}
                for i in range(16, 96)  # 04:00 to 23:45
            ],
            "15min",
            92,
            0.0,
            3000.0,
            "2025-03-30",
            "+01:00/+02:00",
        ),
        # DST fall back 15min
        (
            [
                {"date": f"2025-10-26T00:{i * 15:02d}:00+02:00", "data": 1000.0}
                for i in range(4)  # 00:00 to 00:45
            ]
            + [
                {"date": f"2025-10-26T01:{i * 15:02d}:00+02:00", "data": 1000.0}
                for i in range(4)  # 01:00 to 01:45
            ]
            + [
                {"date": f"2025-10-26T02:{i * 15:02d}:00+02:00", "data": 1000.0}
                for i in range(4)  # 02:00 to 02:45 CEST
            ]
            + [
                {"date": f"2025-10-26T02:{i * 15:02d}:00+01:00", "data": 1000.0}
                for i in range(4)  # 02:00 to 02:45 CET
            ]
            + [
                {"date": f"2025-10-26T{i // 4:02d}:{(i % 4) * 15:02d}:00+01:00", "data": 1000.0}
                for i in range(12, 96)  # 03:00 to 23:45
            ],
            "15min",
            100,
            0.0,
            3000.0,
            "2025-10-26",
            "+02:00/+01:00",
        ),
    ],
    ids=[
        "hourly",
        "15min",
        "custom_min_max",
        "utc_timezone",
        "dst_spring_forward_1h",
        "dst_fall_back_1h",
        "dst_spring_forward_15min",
        "dst_fall_back_15min",
    ],
)
def test_valid_input(  # noqa: PLR0913
    volume_data: list,
    freq: str,
    num_items: int,
    min_value: float,
    max_value: float,
    delivery_date: str,
    tz_offset: str,
    mock_logger: Mock,
) -> None:
    """Test validate_json_pd with valid inputs."""
    context = ValidationContext(
        delivery_date=delivery_date,
        freq=freq,
        mini=min_value,
        maxi=max_value,
    )
    result = validate_json_pd(volume_data=volume_data, context=context)
    assert result is True
    mock_logger.assert_not_called()


@pytest.mark.parametrize(
    ("volume_data", "freq", "min_value", "max_value", "delivery_date", "expected_error_contains"),
    [
        # Cannot convert to DataFrame
        (
            [{"date": "2025-05-20T00:00:00+02:00", "data": 0.0}, None],
            "1h",
            0.0,
            3000.0,
            "2025-05-20",
            "Cannot convert volume_data to DataFrame",
        ),
        # Incorrect columns
        (
            [{"timestamp": "2025-05-20T00:00:00+02:00", "data": 0.0}] * 24,
            "1h",
            0.0,
            3000.0,
            "2025-05-20",
            "Each item must have exactly 'date' and 'data' keys",
        ),
        # Non-numeric data
        (
            [{"date": "2025-05-20T00:00:00+02:00", "data": "invalid"}] * 24,
            "1h",
            0.0,
            3000.0,
            "2025-05-20",
            "All 'data' values must be numeric",
        ),
        # Data out of range
        (
            [{"date": "2025-05-20T00:00:00+02:00", "data": -1.0}] * 24,
            "1h",
            0.0,
            3000.0,
            "2025-05-20",
            "All 'data' values must be between 0.0 and 3000.0",
        ),
        # Invalid timestamp format
        (
            [{"date": "2025-05-20T99:00:00+02:00", "data": 0.0}] * 24,
            "1h",
            0.0,
            3000.0,
            "2025-05-20",
            "All 'date' values must be valid ISO 8601 timestamps with timezone",
        ),
        # Incorrect length (hourly)
        (
            [{"date": f"2025-05-20T{i:02d}:00:00+02:00", "data": 0.0} for i in range(23)],
            "1h",
            0.0,
            3000.0,
            "2025-05-20",
            "Invalid item count: 23. Expected 24",
        ),
        # Incorrect length (15min)
        (
            [{"date": f"2025-05-20T{i // 4:02d}:{(i % 4) * 15:02d}:00+02:00", "data": 0.0} for i in range(95)],
            "15min",
            0.0,
            3000.0,
            "2025-05-20",
            "Invalid item count: 95. Expected 96",
        ),
        # Incorrect frequency spacing
        (
            [
                {"date": "2025-05-20T00:00:00+02:00", "data": 0.0},
                {"date": "2025-05-20T02:00:00+02:00", "data": 0.0},
            ]
            + [{"date": f"2025-05-20T{i:02d}:00:00+02:00", "data": 0.0} for i in range(2, 24)],
            "1h",
            0.0,
            3000.0,
            "2025-05-20",
            "Timestamps must be exactly 1h apart",
        ),
    ],
    ids=[
        "invalid_dataframe",
        "incorrect_columns",
        "non_numeric_data",
        "data_out_of_range",
        "invalid_timestamp",
        "incorrect_length_hourly",
        "incorrect_length_15min",
        "incorrect_spacing",
    ],
)
def test_invalid_input(  # noqa: PLR0913
    volume_data: list,
    freq: str,
    min_value: float,
    max_value: float,
    delivery_date: str,
    expected_error_contains: str,
    mock_logger: Mock,
) -> None:
    """Test validate_json_pd with invalid inputs."""
    context = ValidationContext(
        delivery_date=delivery_date,
        freq=freq,
        mini=min_value,
        maxi=max_value,
    )

    result = validate_json_pd(volume_data=volume_data, context=context)

    assert result is False
    mock_logger.assert_called_once()
    args, _ = mock_logger.call_args
    assert expected_error_contains in args[0]
