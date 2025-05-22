# ruff: noqa: PLR2004, PLR0913, ANN001
from datetime import datetime

import pytest

from app.constants.time_zones import PARIS_TZ
from app.constants.time_zones import UTC_TZ
from app.services.streem.utils.streem_to_nordpool import OrderHeader
from app.services.streem.utils.streem_to_nordpool import parse_iso8601
from app.services.streem.utils.streem_to_nordpool import streem_to_nordpool


class TestTransformVolumeData:
    """Tests for the streem_to_nordpool function."""

    @pytest.mark.parametrize(
        (
            "json_data",
            "order_header",
            "expected_auction_id",
            "expected_area_code",
            "expected_portfolio",
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
                OrderHeader(product_id="CWE_H_DA_1", area_code="FR", portfolio="FR-SUNFLOW"),
                "CWE_H_DA_1-20250520",
                "FR",
                "FR-SUNFLOW",
                [
                    "CWE_H_DA_1-20250521-11",
                    "CWE_H_DA_1-20250521-12",
                ],
                [-1.5, -1.5],
            ),
            # UTC timezone
            (
                [{"date": "2025-05-20T10:00:00+00:00", "data": 1463.9}],
                OrderHeader(product_id="CWE_H_DA_1", area_code="FR", portfolio="FR-SUNFLOW"),
                "CWE_H_DA_1-20250520",
                "FR",
                "FR-SUNFLOW",
                ["CWE_H_DA_1-20250521-11"],
                [-1.5],
            ),
            # Custom parameters
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 1463.9}],
                OrderHeader(product_id="CUSTOM_AUCTION", area_code="DE", portfolio="Custom Portfolio"),
                "CUSTOM_AUCTION-20250520",
                "DE",
                "Custom Portfolio",
                ["CUSTOM_AUCTION-20250521-11"],
                [-1.5],
            ),
            # Non-integer volume
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 1555.55}],
                OrderHeader(product_id="CWE_H_DA_1", area_code="FR", portfolio="FR-SUNFLOW"),
                "CWE_H_DA_1-20250520",
                "FR",
                "FR-SUNFLOW",
                ["CWE_H_DA_1-20250521-11"],
                [-1.6],
            ),
            # Small volume
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 100.0}],
                OrderHeader(product_id="CWE_H_DA_1", area_code="FR", portfolio="FR-SUNFLOW"),
                "CWE_H_DA_1-20250520",
                "FR",
                "FR-SUNFLOW",
                ["CWE_H_DA_1-20250521-11"],
                [-0.1],
            ),
            # Zero volume
            (
                [{"date": "2025-05-20T10:00:00+02:00", "data": 0.0}],
                OrderHeader(product_id="CWE_H_DA_1", area_code="FR", portfolio="FR-SUNFLOW"),
                "CWE_H_DA_1-20250520",
                "FR",
                "FR-SUNFLOW",
                ["CWE_H_DA_1-20250521-11"],
                [0.0],
            ),
            # Midnight hour
            (
                [{"date": "2025-05-20T00:00:00+02:00", "data": 1000.0}],
                OrderHeader(product_id="CWE_H_DA_1", area_code="FR", portfolio="FR-SUNFLOW"),
                "CWE_H_DA_1-20250520",
                "FR",
                "FR-SUNFLOW",
                ["CWE_H_DA_1-20250521-01"],
                [-1.0],
            ),
            # End of day
            (
                [{"date": "2025-05-20T23:00:00+02:00", "data": 1000.0}],
                OrderHeader(product_id="CWE_H_DA_1", area_code="FR", portfolio="FR-SUNFLOW"),
                "CWE_H_DA_1-20250520",
                "FR",
                "FR-SUNFLOW",
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
        json_data,
        order_header,
        expected_auction_id,
        expected_area_code,
        expected_portfolio,
        expected_curves,
        expected_volumes,
    ) -> None:
        """Test streem_to_nordpool with various valid inputs."""
        result = streem_to_nordpool(json_data=json_data, oh=order_header)

        assert result["auctionId"] == expected_auction_id
        assert result["areaCode"] == expected_area_code
        assert result["portfolio"] == expected_portfolio
        assert result["comment"] is None
        assert len(result["curves"]) == len(json_data)

        for i, curve in enumerate(result["curves"]):
            assert curve["contractId"] == expected_curves[i]
            assert len(curve["curvePoints"]) == 4
            assert curve["curvePoints"][2]["volume"] == expected_volumes[i]
            assert curve["curvePoints"][3]["volume"] == expected_volumes[i]
            assert curve["curvePoints"][0] == {"price": -500.00, "volume": 0.00}
            assert curve["curvePoints"][1] == {"price": -0.01, "volume": 0.00}

    def test_empty_input(self) -> None:
        """Test streem_to_nordpool with empty input data."""
        result = streem_to_nordpool(json_data=[], oh=None)
        assert result == {"error": "Input data is empty"}

    @pytest.mark.parametrize(
        ("json_data", "expected_error_contains"),
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
    def test_invalid_input(self, json_data, expected_error_contains) -> None:
        """Test streem_to_nordpool with invalid inputs."""
        result = streem_to_nordpool(json_data=json_data, oh=None)
        assert result["error"]
        assert expected_error_contains in result["error"]

    def test_dst_spring_forward(self) -> None:
        """Test streem_to_nordpool during DST spring forward (March 30, 2025)."""
        json_data = [
            {"date": "2025-03-30T01:00:00+01:00", "data": 1000.0},  # CET
            {"date": "2025-03-30T03:00:00+02:00", "data": 1000.0},  # CEST
        ]
        result = streem_to_nordpool(json_data=json_data, oh=OrderHeader())
        assert result["curves"][0]["contractId"] == "CWE_H_DA_1-20250331-02"
        assert result["curves"][1]["contractId"] == "CWE_H_DA_1-20250331-04"
        assert result["curves"][0]["curvePoints"][2]["volume"] == -1.0
        assert result["curves"][1]["curvePoints"][2]["volume"] == -1.0

    def test_dst_fall_back(self) -> None:
        """Test streem_to_nordpool during DST fall back (October 26, 2025).
        Note: Current implementation does not handle 3a/3b hours; both 02:00 entries map to the same contract hour."""
        json_data = [
            {"date": "2025-10-26T02:00:00+02:00", "data": 1000.0},  # CEST
            {"date": "2025-10-26T02:00:00+01:00", "data": 1000.0},  # CET
        ]
        result = streem_to_nordpool(json_data=json_data, oh=OrderHeader())
        # Current behavior: both map to hour 03 due to simple hour + 1 logic
        assert result["curves"][0]["contractId"] == "CWE_H_DA_1-20251027-03"
        assert result["curves"][1]["contractId"] == "CWE_H_DA_1-20251027-03"
        assert result["curves"][0]["curvePoints"][2]["volume"] == -1.0
        assert result["curves"][1]["curvePoints"][2]["volume"] == -1.0
        # TODO: Update implementation to distinguish 3a/3b hours during DST fall back


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


if __name__ == "__main__":
    pytest.main([__file__])
