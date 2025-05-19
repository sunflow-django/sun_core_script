# ruff: noqa: PLR2004
from datetime import datetime

import pytest

from app.constants.time_zones import PARIS_TZ
from app.constants.time_zones import UTC_TZ
from app.nomination.curve_transform import parse_iso8601
from app.nomination.curve_transform import transform_curve


class TestTransformCurve:
    """Tests for the transform_curve function."""

    def test_valid_input(self) -> None:
        """Test transform_curve with valid input data."""
        volume_data = [
            {"date": "2025-05-20T10:00:00+02:00", "data": 1463.9},
            {"date": "2025-05-20T11:00:00+02:00", "data": 1500.0},
        ]
        result = transform_curve(
            volume_data=volume_data,
            auction_id="CWE_QH_DA_1",
            area_code="FR",
            portfolio="TestAuctions FR",
        )

        assert result["auctionId"] == "CWE_QH_DA_1"
        assert result["areaCode"] == "FR"
        assert result["portfolio"] == "TestAuctions FR"
        assert result["comment"] is None
        assert len(result["curves"]) == 2

        # Check first curve
        assert result["curves"][0]["contractId"] == "CWE_QH_DA_1-20250520-10"
        assert len(result["curves"][0]["curvePoints"]) == 4
        assert result["curves"][0]["curvePoints"][2]["volume"] == -1463.9

        # Check second curve
        assert result["curves"][1]["contractId"] == "CWE_QH_DA_1-20250520-11"
        assert result["curves"][1]["curvePoints"][2]["volume"] == -1500.0

    def test_empty_input(self) -> None:
        """Test transform_curve with empty input data."""
        result = transform_curve(volume_data=[])
        assert result == {"error": "Input data is empty"}

    def test_invalid_date_format(self) -> None:
        """Test transform_curve with invalid date format (ex.: 99h)."""
        volume_data = [{"date": "2025-05-20T99:00:00", "data": 1463.9}]
        result = transform_curve(volume_data=volume_data)
        assert "Invalid date or volume format" in result["error"]

    def test_missing_key(self) -> None:
        """Test transform_curve with missing key in input data."""
        volume_data = [{"timestamp": "2025-05-20T10:00:00+02:00", "data": 1463.9}]
        result = transform_curve(volume_data=volume_data)
        assert "Invalid date or volume format" in result["error"]

    def test_invalid_data_type(self) -> None:
        """Test transform_curve with non-numeric data value."""
        volume_data = [{"date": "2025-05-20T10:00:00+02:00", "data": "invalid"}]
        result = transform_curve(volume_data=volume_data)
        assert "Invalid date or volume format" in result["error"]

    def test_different_timezone(self) -> None:
        """Test transform_curve with different timezone."""
        volume_data = [
            {"date": "2025-05-20T10:00:00+00:00", "data": 1463.9},  # UTC timezone
        ]
        result = transform_curve(volume_data=volume_data)
        assert result["curves"][0]["contractId"] == "CWE_QH_DA_1-20250520-10"
        assert result["curves"][0]["curvePoints"][2]["volume"] == -1463.9

    def test_custom_parameters(self) -> None:
        """Test transform_curve with custom auction_id, area_code, and portfolio."""
        volume_data = [{"date": "2025-05-20T10:00:00+02:00", "data": 1463.9}]
        result = transform_curve(
            volume_data=volume_data,
            auction_id="CUSTOM_AUCTION",
            area_code="DE",
            portfolio="Custom Portfolio",
        )
        assert result["auctionId"] == "CUSTOM_AUCTION"
        assert result["areaCode"] == "DE"
        assert result["portfolio"] == "Custom Portfolio"
        assert result["curves"][0]["contractId"].startswith("CUSTOM_AUCTION-")

    def test_curve_points_structure(self) -> None:
        """Test the structure and values of curvePoints."""
        volume_data = [{"date": "2025-05-20T10:00:00+02:00", "data": 1000.0}]
        result = transform_curve(volume_data=volume_data)

        curve_points = result["curves"][0]["curvePoints"]
        assert len(curve_points) == 4
        assert curve_points[0] == {"price": -500.00, "volume": 0.00}
        assert curve_points[1] == {"price": -0.01, "volume": 0.00}
        assert curve_points[2] == {"price": 0.00, "volume": -1000.0}
        assert curve_points[3] == {"price": 4000.00, "volume": -1000.0}


class TestParseISO8601:
    """Tests for the parse_iso8601 function."""

    def test_valid_iso8601(self) -> None:
        """Test parsing a valid ISO 8601 timestamp with timezone offset."""
        result = parse_iso8601("2025-05-20T10:00:00+02:00")
        expected = datetime(2025, 5, 20, 10, 0, 0, tzinfo=PARIS_TZ)
        assert result == expected
        assert result.tzname() == "UTC+02:00"

    def test_valid_iso8601_with_z(self) -> None:
        """Test parsing a valid ISO 8601 timestamp with 'Z' (UTC)."""
        result = parse_iso8601("2025-05-20T10:00:00Z")
        expected = datetime(2025, 5, 20, 10, 0, 0, tzinfo=UTC_TZ)
        assert result == expected
        assert result.tzname() == "UTC"

    def test_valid_iso8601_no_seconds(self) -> None:
        """Test parsing a valid ISO 8601 timestamp without seconds."""
        result = parse_iso8601("2025-05-20T10:00+02:00")
        expected = datetime(2025, 5, 20, 10, 0, 0, tzinfo=PARIS_TZ)
        assert result == expected
        assert result.tzname() == "UTC+02:00"

    def test_invalid_date(self) -> None:
        """Test parsing an invalid date (e.g., invalid month)."""
        with pytest.raises(ValueError, match="Invalid ISO 8601 format: 2025-13-20T10:00:00\\+02:00"):
            parse_iso8601("2025-13-20T10:00:00+02:00")

    def test_invalid_time(self) -> None:
        """Test parsing an invalid time (e.g., hour > 23)."""
        with pytest.raises(ValueError, match="Invalid ISO 8601 format: 2025-05-20T25:00:00\\+02:00"):
            parse_iso8601("2025-05-20T25:00:00+02:00")

    def test_invalid_timezone(self) -> None:
        """Test parsing an invalid timezone format (e.g., > 99)."""
        with pytest.raises(ValueError, match="offset must be a timedelta strictly between"):
            parse_iso8601("2025-05-20T10:00:00+99")

    def test_empty_string(self) -> None:
        """Test parsing an empty string."""
        with pytest.raises(ValueError, match="Invalid ISO 8601 format: "):
            parse_iso8601("")

    def test_fractional_seconds(self) -> None:
        """Test parsing a timestamp with fractional seconds."""
        result = parse_iso8601("2025-05-20T10:00:00.123456+02:00")
        expected = datetime(2025, 5, 20, 10, 0, 0, 123456, tzinfo=PARIS_TZ)
        assert result == expected
        assert result.tzname() == "UTC+02:00"
