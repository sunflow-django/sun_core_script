# ruff: noqa: PLR2004, PLR0913,ANN001
from datetime import datetime

import pytest

from app.constants.time_zones import PARIS_TZ
from app.constants.time_zones import UTC_TZ
from app.services.streem.utils import VolumeDataValidationError
from app.services.streem.utils import get_day_hours_paris
from app.services.streem.utils import parse_iso8601
from app.services.streem.utils import transform_volume_data
from app.services.streem.utils import validate_volume_data


class TestTransformVolumeData:
    """Tests for the transform_volume_data function."""

    @pytest.mark.parametrize(
        (
            "volume_data",
            "product_id",
            "expected_auction_id",
            "area_code",
            "portfolio",
            "expected_curves",
            "expected_volumes",
        ),
        [
            # Standard valid input (multiple timestamps)
            (
                [
                    {"date": "2025-05-20T10:00:00+02:00", "data": 1463.9},
                    {"date": "2025-05-20T11:00:00+02:00", "data": 1500.0},
                ],
                "CWE_H_DA_1",
                "CWE_H_DA_1-20250520",
                "FR",
                "TestAuctions FR",
                [
                    "CWE_H_DA_1-20250521-11",
                    "CWE_H_DA_1-20250521-12",
                ],
                [-1.5, -1.5],
            ),
            # UTC timezone
            (
                [{"date": "2025-05-20T10:00:00+00:00", "data": 1463.9}],
                "CWE_H_DA_1",
                "CWE_H_DA_1-20250520",
                "FR",
                "TestAuctions FR",
                ["CWE_H_DA_1-20250521-11"],
                [-1.5],
            ),
            # Custom parameters
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 1463.9}],
                "CUSTOM_AUCTION",
                "CUSTOM_AUCTION-20250520",
                "DE",
                "Custom Portfolio",
                ["CUSTOM_AUCTION-20250521-11"],
                [-1.5],
            ),
            # Non-integer volume
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 1555.55}],
                "CWE_H_DA_1",
                "CWE_H_DA_1-20250520",
                "FR",
                "TestAuctions FR",
                ["CWE_H_DA_1-20250521-11"],
                [-1.6],
            ),
            # Small volume
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 100.0}],
                "CWE_H_DA_1",
                "CWE_H_DA_1-20250520",
                "FR",
                "TestAuctions FR",
                ["CWE_H_DA_1-20250521-11"],
                [-0.1],
            ),
            # Zero volume
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 0.0}],
                "CWE_H_DA_1",
                "CWE_H_DA_1-20250520",
                "FR",
                "TestAuctions FR",
                ["CWE_H_DA_1-20250521-11"],
                [0.0],
            ),
            # Midnight hour
            (
                [{"date": "2025-05-20T00:00:00+02:00", "data": 1000.0}],
                "CWE_H_DA_1",
                "CWE_H_DA_1-20250520",
                "FR",
                "TestAuctions FR",
                ["CWE_H_DA_1-20250521-01"],
                [-1.0],
            ),
            # End of day
            (
                [{"date": "2025-05-20T23:00:00+02:00", "data": 1000.0}],
                "CWE_H_DA_1",
                "CWE_H_DA_1-20250520",
                "FR",
                "TestAuctions FR",
                ["CWE_H_DA_1-20250521-24"],
                [-1.0],
            ),
        ],
        ids=[
            "standard_valid_input",
            "utc_timezone",
            "custom_parameters",
            "non_integer_volume",
            "small_volume",
            "zero_volume",
            "midnight_hour",
            "end_of_day",
        ],
    )
    def test_valid_input(
        self,
        volume_data,
        product_id,
        expected_auction_id,
        area_code,
        portfolio,
        expected_curves,
        expected_volumes,
    ) -> None:
        """Test transform_volume_data with various valid inputs."""
        result = transform_volume_data(
            volume_data=volume_data,
            product_id=product_id,
            area_code=area_code,
            portfolio=portfolio,
        )

        assert result["auctionId"] == expected_auction_id
        assert result["areaCode"] == area_code
        assert result["portfolio"] == portfolio
        assert result["comment"] is None
        assert len(result["curves"]) == len(volume_data)

        for i, curve in enumerate(result["curves"]):
            assert curve["contractId"] == expected_curves[i]
            assert len(curve["curvePoints"]) == 4
            assert curve["curvePoints"][2]["volume"] == expected_volumes[i]
            assert curve["curvePoints"][3]["volume"] == expected_volumes[i]
            assert curve["curvePoints"][0] == {"price": -500.00, "volume": 0.00}
            assert curve["curvePoints"][1] == {"price": -0.01, "volume": 0.00}

    def test_empty_input(self) -> None:
        """Test transform_volume_data with empty input data."""
        result = transform_volume_data(volume_data=[])
        assert result == {"error": "Input data is empty"}

    @pytest.mark.parametrize(
        ("volume_data", "expected_error_contains"),
        [
            (
                [{"date": "2025-05-20T99:00:00", "data": 1463.9}],
                "Invalid ISO 8601 format",
            ),
            (
                [{"timestamp": "2025-05-20T10:00:00+02:00", "data": 1463.9}],
                "'date'",
            ),
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": "invalid"}],
                "could not convert string to float",
            ),
        ],
        ids=["invalid_date_format", "missing_key", "invalid_data_type"],
    )
    def test_invalid_input(self, volume_data, expected_error_contains) -> None:
        """Test transform_volume_data with invalid inputs."""
        result = transform_volume_data(volume_data=volume_data)
        assert result["error"]
        assert expected_error_contains in result["error"]

    # TODO : remove or adpat test
    def test_dst_spring_forward(self) -> None:
        """Test transform_volume_data during DST spring forward (March 30, 2025)."""
        volume_data = [
            {"date": "2025-03-30T01:00:00+01:00", "data": 1000.0},  # CET
            {"date": "2025-03-30T03:00:00+02:00", "data": 1000.0},  # CEST
        ]
        result = transform_volume_data(volume_data=volume_data)
        assert result["curves"][0]["contractId"] == "CWE_H_DA_1-20250331-02"
        assert result["curves"][1]["contractId"] == "CWE_H_DA_1-20250331-04"
        assert result["curves"][0]["curvePoints"][2]["volume"] == -1.0
        assert result["curves"][1]["curvePoints"][2]["volume"] == -1.0

    # TODO : remove or adpat test
    def test_dst_fall_back(self) -> None:
        """Test transform_volume_data during DST fall back (October 26, 2025)."""
        volume_data = [
            {"date": "2025-10-26T02:00:00+02:00", "data": 1000.0},  # CEST
            {"date": "2025-10-26T02:00:00+01:00", "data": 1000.0},  # CET
        ]
        result = transform_volume_data(volume_data=volume_data)
        assert result["curves"][0]["contractId"] == "CWE_H_DA_1-20251027-03"
        assert result["curves"][1]["contractId"] == "CWE_H_DA_1-20251027-03"
        assert result["curves"][0]["curvePoints"][2]["volume"] == -1.0
        assert result["curves"][1]["curvePoints"][2]["volume"] == -1.0


class TestParseISO8601:
    """Tests for the parse_iso8601 function."""

    @pytest.mark.parametrize(
        ("timestamp", "expected_datetime", "expected_tzname"),
        [
            (
                "2025-05-20T10:00:00+02:00",
                datetime(2025, 5, 20, 10, 0, 0, tzinfo=PARIS_TZ),
                "UTC+02:00",
            ),
            (
                "2025-05-20T10:00:00Z",
                datetime(2025, 5, 20, 10, 0, 0, tzinfo=UTC_TZ),
                "UTC",
            ),
            (
                "2025-05-20T10:00+02:00",
                datetime(2025, 5, 20, 10, 0, 0, tzinfo=PARIS_TZ),
                "UTC+02:00",
            ),
            (
                "2025-05-20T10:00:00.123456+02:00",
                datetime(2025, 5, 20, 10, 0, 0, 123456, tzinfo=PARIS_TZ),
                "UTC+02:00",
            ),
        ],
        ids=["standard", "utc_z", "no_seconds", "fractional_seconds"],
    )
    def test_valid_iso8601(self, timestamp, expected_datetime, expected_tzname) -> None:
        """Test parsing valid ISO 8601 timestamps."""
        result = parse_iso8601(timestamp)
        assert result == expected_datetime
        assert result.tzname() == expected_tzname

    @pytest.mark.parametrize(
        ("timestamp", "expected_error_match"),
        [
            (
                "2025-13-20T10:00:00+02:00",
                "Invalid ISO 8601 format: 2025-13-20T10:00:00\\+02:00",
            ),
            (
                "2025-05-20T25:00:00+02:00",
                "Invalid ISO 8601 format: 2025-05-20T25:00:00\\+02:00",
            ),
            (
                "2025-05-20T10:00:00+99",
                "offset must be a timedelta strictly between",
            ),
            (
                "",
                "Invalid ISO 8601 format: ",
            ),
        ],
        ids=["invalid_date", "invalid_time", "invalid_timezone", "empty_string"],
    )
    def test_invalid_iso8601(self, timestamp, expected_error_match) -> None:
        """Test parsing invalid ISO 8601 timestamps."""
        with pytest.raises(ValueError, match=expected_error_match):
            parse_iso8601(timestamp)


class TestValidateVolumeData:
    """Tests for the validate_volume_data function."""

    @pytest.mark.parametrize(
        ("volume_data", "freq", "min_value", "max_value"),
        [
            # Standard hourly input
            (
                [
                    {"date": "2025-05-20T00:00:00+02:00", "data": 0.0},
                    {"date": "2025-05-20T01:00:00+02:00", "data": 100.0},
                    {"date": "2025-05-20T02:00:00+02:00", "data": 200.0},
                    {"date": "2025-05-20T03:00:00+02:00", "data": 300.0},
                    {"date": "2025-05-20T04:00:00+02:00", "data": 400.0},
                    {"date": "2025-05-20T05:00:00+02:00", "data": 500.0},
                    {"date": "2025-05-20T06:00:00+02:00", "data": 600.0},
                    {"date": "2025-05-20T07:00:00+02:00", "data": 700.0},
                    {"date": "2025-05-20T08:00:00+02:00", "data": 800.0},
                    {"date": "2025-05-20T09:00:00+02:00", "data": 900.0},
                    {"date": "2025-05-20T10:00:00+02:00", "data": 1000.0},
                    {"date": "2025-05-20T11:00:00+02:00", "data": 1100.0},
                    {"date": "2025-05-20T12:00:00+02:00", "data": 1200.0},
                    {"date": "2025-05-20T13:00:00+02:00", "data": 1300.0},
                    {"date": "2025-05-20T14:00:00+02:00", "data": 1400.0},
                    {"date": "2025-05-20T15:00:00+02:00", "data": 1500.0},
                    {"date": "2025-05-20T16:00:00+02:00", "data": 1600.0},
                    {"date": "2025-05-20T17:00:00+02:00", "data": 1700.0},
                    {"date": "2025-05-20T18:00:00+02:00", "data": 1800.0},
                    {"date": "2025-05-20T19:00:00+02:00", "data": 1900.0},
                    {"date": "2025-05-20T20:00:00+02:00", "data": 2000.0},
                    {"date": "2025-05-20T21:00:00+02:00", "data": 2100.0},
                    {"date": "2025-05-20T22:00:00+02:00", "data": 2200.0},
                    {"date": "2025-05-20T23:00:00+02:00", "data": 2300.0},
                ],
                "1h",
                0.0,
                3000.0,
            ),
            # 15-minute input (subset for brevity)
            (
                [
                    {"date": "2025-05-20T00:00:00+02:00", "data": 0.0},
                    {"date": "2025-05-20T00:15:00+02:00", "data": 1.0},
                    {"date": "2025-05-20T00:30:00+02:00", "data": 2.0},
                    {"date": "2025-05-20T00:45:00+02:00", "data": 3.0},
                    {"date": "2025-05-20T01:00:00+02:00", "data": 4.0},
                    {"date": "2025-05-20T01:15:00+02:00", "data": 5.0},
                    {"date": "2025-05-20T01:30:00+02:00", "data": 6.0},
                    {"date": "2025-05-20T01:45:00+02:00", "data": 7.0},
                    # ... (continues to 96 points)
                ]
                + [
                    {"date": f"2025-05-20T{(i // 4):02d}:{(i % 4) * 15:02d}:00+02:00", "data": float(i)}
                    for i in range(8, 96)
                ],
                "15min",
                0.0,
                3000.0,
            ),
            # Custom min/max values
            (
                [
                    {"date": "2025-05-20T00:00:00+02:00", "data": 100.0},
                    {"date": "2025-05-20T01:00:00+02:00", "data": 200.0},
                    {"date": "2025-05-20T02:00:00+02:00", "data": 300.0},
                    {"date": "2025-05-20T03:00:00+02:00", "data": 400.0},
                    {"date": "2025-05-20T04:00:00+02:00", "data": 500.0},
                    {"date": "2025-05-20T05:00:00+02:00", "data": 600.0},
                    {"date": "2025-05-20T06:00:00+02:00", "data": 700.0},
                    {"date": "2025-05-20T07:00:00+02:00", "data": 800.0},
                    {"date": "2025-05-20T08:00:00+02:00", "data": 900.0},
                    {"date": "2025-05-20T09:00:00+02:00", "data": 1000.0},
                    {"date": "2025-05-20T10:00:00+02:00", "data": 1100.0},
                    {"date": "2025-05-20T11:00:00+02:00", "data": 1200.0},
                    {"date": "2025-05-20T12:00:00+02:00", "data": 1300.0},
                    {"date": "2025-05-20T13:00:00+02:00", "data": 1400.0},
                    {"date": "2025-05-20T14:00:00+02:00", "data": 1500.0},
                    {"date": "2025-05-20T15:00:00+02:00", "data": 1600.0},
                    {"date": "2025-05-20T16:00:00+02:00", "data": 1700.0},
                    {"date": "2025-05-20T17:00:00+02:00", "data": 1800.0},
                    {"date": "2025-05-20T18:00:00+02:00", "data": 1900.0},
                    {"date": "2025-05-20T19:00:00+02:00", "data": 2000.0},
                    {"date": "2025-05-20T20:00:00+02:00", "data": 2100.0},
                    {"date": "2025-05-20T21:00:00+02:00", "data": 2200.0},
                    {"date": "2025-05-20T22:00:00+02:00", "data": 2300.0},
                    {"date": "2025-05-20T23:00:00+02:00", "data": 2400.0},
                ],
                "1h",
                100.0,
                2400.0,
            ),
            # UTC timezone
            (
                [
                    {"date": "2025-05-19T22:00:00+00:00", "data": 0.0},
                    {"date": "2025-05-19T23:00:00+00:00", "data": 100.0},
                    {"date": "2025-05-20T00:00:00+00:00", "data": 200.0},
                    {"date": "2025-05-20T01:00:00+00:00", "data": 300.0},
                    {"date": "2025-05-20T02:00:00+00:00", "data": 400.0},
                    {"date": "2025-05-20T03:00:00+00:00", "data": 500.0},
                    {"date": "2025-05-20T04:00:00+00:00", "data": 600.0},
                    {"date": "2025-05-20T05:00:00+00:00", "data": 700.0},
                    {"date": "2025-05-20T06:00:00+00:00", "data": 800.0},
                    {"date": "2025-05-20T07:00:00+00:00", "data": 900.0},
                    {"date": "2025-05-20T08:00:00+00:00", "data": 1000.0},
                    {"date": "2025-05-20T09:00:00+00:00", "data": 1100.0},
                    {"date": "2025-05-20T10:00:00+00:00", "data": 1200.0},
                    {"date": "2025-05-20T11:00:00+00:00", "data": 1300.0},
                    {"date": "2025-05-20T12:00:00+00:00", "data": 1400.0},
                    {"date": "2025-05-20T13:00:00+00:00", "data": 1500.0},
                    {"date": "2025-05-20T14:00:00+00:00", "data": 1600.0},
                    {"date": "2025-05-20T15:00:00+00:00", "data": 1700.0},
                    {"date": "2025-05-20T16:00:00+00:00", "data": 1800.0},
                    {"date": "2025-05-20T17:00:00+00:00", "data": 1900.0},
                    {"date": "2025-05-20T18:00:00+00:00", "data": 2000.0},
                    {"date": "2025-05-20T19:00:00+00:00", "data": 2100.0},
                    {"date": "2025-05-20T20:00:00+00:00", "data": 2200.0},
                    {"date": "2025-05-20T21:00:00+00:00", "data": 2300.0},
                ],
                "1h",
                0.0,
                3000.0,
            ),
        ],
        ids=["hourly", "15min", "custom_min_max", "utc_timezone"],
    )
    def test_valid_input(self, volume_data, freq, min_value, max_value) -> None:
        """Test validate_volume_data with valid inputs."""
        result = validate_volume_data(
            volume_data=volume_data,
            freq=freq,
            min_value=min_value,
            max_value=max_value,
        )
        assert result is True

    @pytest.mark.parametrize(
        ("volume_data", "freq", "min_value", "max_value", "expected_error_contains"),
        [
            # Invalid frequency
            (
                [{"date": "2025-05-20T00:00:00+02:00", "data": 0.0}],
                "invalid_freq",
                0.0,
                3000.0,
                "freq must be '1h' or '15min'",
            ),
            # Cannot convert to DataFrame
            (
                [{"date": "2025-05-20T00:00:00+02:00", "data": 0.0}, None],
                "1h",
                0.0,
                3000.0,
                "Cannot convert volume_data to DataFrame",
            ),
            # Incorrect length (hourly)
            (
                [
                    {"date": "2025-05-20T00:00:00+02:00", "data": 0.0},
                    {"date": "2025-05-20T01:00:00+02:00", "data": 100.0},
                ],
                "1h",
                0.0,
                3000.0,
                "DataFrame must contain 24 rows for 1h freq",
            ),
            # Incorrect length (15min)
            (
                [
                    {"date": "2025-05-20T00:00:00+02:00", "data": 0.0},
                    {"date": "2025-05-20T00:15:00+02:00", "data": 100.0},
                ],
                "15min",
                0.0,
                3000.0,
                "DataFrame must contain 96 rows for 15min freq",
            ),
            # Missing keys
            (
                [{"timestamp": "2025-05-20T00:00:00+02:00", "data": 0.0}]
                + [{"date": f"2025-05-20T{(i):02d}:00:00+02:00", "data": float(i)} for i in range(1, 24)],
                "1h",
                0.0,
                3000.0,
                "Each item must have exactly 'date' and 'data' keys",
            ),
            # Non-numeric data
            (
                [{"date": "2025-05-20T00:00:00+02:00", "data": "invalid"}]
                + [{"date": f"2025-05-20T{(i):02d}:00:00+02:00", "data": float(i)} for i in range(1, 24)],
                "1h",
                0.0,
                3000.0,
                "All 'data' values must be numeric",
            ),
            # Data out of range
            (
                [{"date": "2025-05-20T00:00:00+02:00", "data": -1.0}]
                + [{"date": f"2025-05-20T{(i):02d}:00:00+02:00", "data": float(i)} for i in range(1, 24)],
                "1h",
                0.0,
                3000.0,
                "All 'data' values must be between 0.0 and 3000.0",
            ),
            # Invalid timestamp format
            (
                [{"date": "2025-05-20T99:00:00+02:00", "data": 0.0}]
                + [{"date": f"2025-05-20T{(i):02d}:00:00+02:00", "data": float(i)} for i in range(1, 24)],
                "1h",
                0.0,
                3000.0,
                "All 'date' values must be valid ISO 8601 timestamps with timezone",
            ),
            # Non-start-of-day timestamp
            (
                [{"date": "2025-05-20T01:00:00+02:00", "data": 0.0}]
                + [{"date": f"2025-05-20T{(i):02d}:00:00+02:00", "data": float(i)} for i in range(1, 23)]
                + [{"date": "2025-05-21T00:00:00+02:00", "data": 24.0}],
                "1h",
                0.0,
                3000.0,
                "First timestamp must be start of day",
            ),
            # Incorrect frequency spacing
            (
                [
                    {"date": "2025-05-20T00:00:00+02:00", "data": 0.0},
                    {"date": "2025-05-20T02:00:00+02:00", "data": 100.0},
                ]
                + [{"date": f"2025-05-20T{(i):02d}:00:00+02:00", "data": float(i)} for i in range(2, 24)],
                "1h",
                0.0,
                3000.0,
                "Timestamps must be exactly 1h apart",
            ),
        ],
        ids=[
            "invalid_freq",
            "invalid_dataframe",
            "incorrect_length_hourly",
            "incorrect_length_15min",
            "missing_keys",
            "non_numeric_data",
            "data_out_of_range",
            "invalid_timestamp",
            "non_start_of_day",
            "incorrect_spacing",
        ],
    )
    def test_invalid_input(self, volume_data, freq, min_value, max_value, expected_error_contains) -> None:
        """Test validate_volume_data with invalid inputs."""
        with pytest.raises(VolumeDataValidationError, match=expected_error_contains):
            validate_volume_data(
                volume_data=volume_data,
                freq=freq,
                min_value=min_value,
                max_value=max_value,
            )

    def test_dst_spring_forward(self) -> None:
        """Test validate_volume_data during DST spring forward (March 30, 2025)."""
        # Spring forward: 02:00 CET -> 03:00 CEST, so 23 hours
        volume_data = [
            {"date": "2025-03-30T00:00:00+01:00", "data": 1000.0},
            {"date": "2025-03-30T01:00:00+01:00", "data": 1000.0},
            {"date": "2025-03-30T03:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T04:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T05:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T06:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T07:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T08:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T09:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T10:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T11:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T12:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T13:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T14:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T15:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T16:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T17:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T18:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T19:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T20:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T21:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T22:00:00+02:00", "data": 1000.0},
            {"date": "2025-03-30T23:00:00+02:00", "data": 1000.0},
        ]
        result = validate_volume_data(volume_data=volume_data, freq="1h")
        assert result is True

    def test_dst_fall_back(self) -> None:
        """Test validate_volume_data during DST fall back (October 26, 2025)."""
        # Fall back: 25 hours due to repeated 02:00 hour
        volume_data = [
            {"date": "2025-10-26T00:00:00+02:00", "data": 1000.0},
            {"date": "2025-10-26T01:00:00+02:00", "data": 1000.0},
            {"date": "2025-10-26T02:00:00+02:00", "data": 1000.0},  # CEST
            {"date": "2025-10-26T02:00:00+01:00", "data": 1000.0},  # CET
            {"date": "2025-10-26T03:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T04:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T05:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T06:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T07:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T08:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T09:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T10:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T11:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T12:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T13:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T14:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T15:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T16:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T17:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T18:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T19:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T20:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T21:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T22:00:00+01:00", "data": 1000.0},
            {"date": "2025-10-26T23:00:00+01:00", "data": 1000.0},
        ]
        validate_volume_data(volume_data=volume_data, freq="1h")
        # with pytest.raises(VolumeDataValidationError, match="DataFrame must contain 24 rows for 1h freq"):
        #     validate_volume_data(volume_data=volume_data, freq="1h")


class TestGetDayHoursParis:
    """Tests for the get_day_hours_paris function."""

    @pytest.mark.parametrize(
        ("date_str", "expected_hours"),
        [
            ("2025-05-20", 24),  # Normal day
            ("2025-01-01", 24),  # New Year's Day (normal)
            ("2025-03-30", 23),  # DST spring forward (CET to CEST)
            ("2025-10-26", 25),  # DST fall back (CEST to CET)
            ("2024-12-31", 24),  # Edge of year
        ],
        ids=[
            "normal_day",
            "new_years_day",
            "dst_spring_forward",
            "dst_fall_back",
            "year_edge",
        ],
    )
    def test_valid_input(self, date_str, expected_hours) -> None:
        """Test get_day_hours_paris with valid date strings."""
        result = get_day_hours_paris(date_str)
        assert result == expected_hours

    @pytest.mark.parametrize(
        ("date_str", "expected_error_match"),
        [
            (
                "2025-13-20",
                "Invalid date format: 2025-13-20\\. Use 'YYYY-MM-DD'\\.",
            ),
            (
                "2025-05-32",
                "Invalid date format: 2025-05-32\\. Use 'YYYY-MM-DD'\\.",
            ),
            (
                "",
                "Invalid date format: \\. Use 'YYYY-MM-DD'\\.",
            ),
            (
                "invalid",
                "Invalid date format: invalid\\. Use 'YYYY-MM-DD'\\.",
            ),
        ],
        ids=[
            "invalid_month",
            "invalid_day",
            "empty_string",
            "non_date_string",
        ],
    )
    def test_invalid_input_valle_error(self, date_str, expected_error_match) -> None:
        """Test get_day_hours_paris with invalid date strings."""
        with pytest.raises(ValueError, match=expected_error_match):
            get_day_hours_paris(date_str)

    @pytest.mark.parametrize(
        ("date_str", "expected_error_match"),
        [
            (
                "2025/05/20",
                "Invalid date format: 2025/05/20\\. Use 'YYYY-MM-DD'\\.",
            ),
            (
                "2025 05 20",
                "Invalid date format: \\. Use 'YYYY-MM-DD'\\.",
            ),
        ],
        ids=[
            "wrong_separator_slash",
            "wrong_separator_space",
        ],
    )
    def test_invalid_input_(self, date_str, expected_error_match) -> None:
        """Test get_day_hours_paris with invalid date strings."""
        with pytest.raises(AssertionError, match=expected_error_match):
            get_day_hours_paris(date_str)


if __name__ == "__main__":
    pytest.main([__file__])
