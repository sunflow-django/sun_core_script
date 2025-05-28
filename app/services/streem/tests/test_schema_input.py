from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from app.services.streem.schema import ForecastType
from app.services.streem.schema import Resolution
from app.services.streem.schema_input import GetAlertstInput
from app.services.streem.schema_input import GetInstallationAlertsInput
from app.services.streem.schema_input import GetInstallationDetailInput
from app.services.streem.schema_input import GetInstallationForecastInput


# Fixtures
@pytest.fixture
def valid_datetime() -> datetime:
    """Return a timezone-aware datetime for May 28, 2025, 12:00 UTC."""
    return datetime(2025, 5, 28, 12, 0, tzinfo=ZoneInfo("UTC"))


@pytest.fixture
def later_datetime() -> datetime:
    """Return a timezone-aware datetime for May 29, 2025, 12:00 UTC."""
    return datetime(2025, 5, 29, 12, 0, tzinfo=ZoneInfo("UTC"))


@pytest.fixture
def non_timezone_datetime() -> datetime:
    """Return a non-timezone-aware datetime."""
    return datetime(2025, 5, 28, 12, 0)  # noqa: DTZ001


@pytest.fixture
def non_timezone_later_datetime() -> datetime:
    """Return a non-timezone-aware datetime for May 29, 2025, 12:00."""
    return datetime(2025, 5, 29, 12, 0)  # noqa: DTZ001


class TestGetInstallationDetailInput:
    """Tests for GetInstallationDetailInput model validation."""

    def test_valid_input(self) -> None:
        """Test valid input with name provided."""
        data = {"name": "installation_123"}
        model = GetInstallationDetailInput(**data)
        assert model.name == "installation_123"

    def test_missing_name(self) -> None:
        """Test validation error when name is missing."""
        with pytest.raises(ValidationError, match=r"name\s+Field required"):
            GetInstallationDetailInput()

    def test_invalid_name_type(self) -> None:
        """Test validation error when name is not a string."""
        with pytest.raises(ValidationError, match=r"name\s+Input should be a valid string"):
            GetInstallationDetailInput(name=123)

    def test_extra_field(self) -> None:
        """Test validation error for extra fields."""
        with pytest.raises(ValidationError, match=r"extra\s+Extra inputs are not permitted"):
            GetInstallationDetailInput(name="installation_123", extra="forbidden")


class TestGetInstallationAlertsInput:
    """Tests for GetInstallationAlertsInput model validation."""

    def test_valid_full_input(self, valid_datetime: datetime) -> None:
        """Test valid input with all fields provided."""
        data = {
            "name": "installation_123",
            "start_date": valid_datetime,
            "end_date": valid_datetime,
            "all_alerts": False,
        }
        model = GetInstallationAlertsInput(**data)
        assert model.name == "installation_123"
        assert model.start_date == data["start_date"]
        assert model.end_date == data["end_date"]
        assert model.all_alerts is False

    def test_valid_minimal_input(self) -> None:
        """Test valid input with only required field (name)."""
        data = {"name": "installation_123"}
        model = GetInstallationAlertsInput(**data)
        assert model.name == "installation_123"
        assert model.start_date is None
        assert model.end_date is None
        assert model.all_alerts is True

    def test_missing_name(self) -> None:
        """Test validation error when name is missing."""
        with pytest.raises(ValidationError, match=r"name\s+Field required"):
            GetInstallationAlertsInput()

    def test_invalid_name_type(self) -> None:
        """Test validation error when name is not a string."""
        with pytest.raises(ValidationError, match=r"name\s+Input should be a valid string"):
            GetInstallationAlertsInput(name=123)

    def test_invalid_all_alerts_type(self) -> None:
        """Test validation error when all_alerts is not a boolean."""
        with pytest.raises(ValidationError, match=r"all_alerts\s+Input should be a valid boolean"):
            GetInstallationAlertsInput(name="installation_123", all_alerts="true")


class TestGetInstallationForecastInput:
    """Tests for GetInstallationForecastInput model validation, including custom date validator."""

    def test_valid_full_input(self, valid_datetime: datetime, later_datetime: datetime) -> None:
        """Test valid input with all fields provided."""
        data = {
            "name": "installation_123",
            "forecast_type": ForecastType.DISPATCH_PROGRAM,
            "start_date": valid_datetime,
            "end_date": later_datetime,
            "resolution": Resolution.H1,
        }
        model = GetInstallationForecastInput(**data)
        assert model.name == "installation_123"
        assert model.forecast_type == ForecastType.DISPATCH_PROGRAM
        assert model.start_date == valid_datetime
        assert model.end_date == later_datetime
        assert model.resolution == Resolution.H1

    def test_valid_minimal_input(self) -> None:
        """Test valid input with only required field (name)."""
        data = {"name": "installation_123"}
        model = GetInstallationForecastInput(**data)
        assert model.name == "installation_123"
        assert model.forecast_type == ForecastType.DISPATCH_PROGRAM
        assert model.start_date is None
        assert model.end_date is None
        assert model.resolution == Resolution.H1

    def test_missing_name(self) -> None:
        """Test validation error when name is missing."""
        with pytest.raises(ValidationError, match=r"name\s+Field required"):
            GetInstallationForecastInput(resolution=Resolution.H1)

    def test_invalid_name_type(self) -> None:
        """Test validation error when name is not a string."""
        with pytest.raises(ValidationError, match=r"name\s+Input should be a valid string"):
            GetInstallationForecastInput(name=123)

    @pytest.mark.parametrize(
        "forecast_type",
        list(ForecastType),
    )
    def test_valid_forecast_type(
        self,
        forecast_type: ForecastType,
        valid_datetime: datetime,
        later_datetime: datetime,
    ) -> None:
        """Test valid forecast_type enum values."""
        data = {
            "name": "installation_123",
            "forecast_type": forecast_type,
            "start_date": valid_datetime,
            "end_date": later_datetime,
            "resolution": Resolution.H1,
        }
        model = GetInstallationForecastInput(**data)
        assert model.forecast_type == forecast_type

    def test_invalid_forecast_type(self) -> None:
        """Test validation error for invalid forecast_type."""
        with pytest.raises(
            ValidationError,
            match=r"forecast_type\s+Input should be 'Generation' or 'Dispatch_Program'",
        ):
            GetInstallationForecastInput(name="installation_123", forecast_type="invalid")

    @pytest.mark.parametrize("resolution", list(Resolution))
    def test_valid_resolution(self, resolution: Resolution, valid_datetime: datetime, later_datetime: datetime) -> None:
        """Test valid resolution enum values."""
        data = {
            "name": "installation_123",
            "resolution": resolution,
            "start_date": valid_datetime,
            "end_date": later_datetime,
        }
        model = GetInstallationForecastInput(**data)
        assert model.resolution == resolution

    def test_invalid_resolution(self) -> None:
        """Test validation error for invalid resolution."""
        with pytest.raises(
            ValidationError,
            match=r"resolution\s+Input should be '5m', '10m', '15m', '30m', '1h', '1d' or '1M'",
        ):
            GetInstallationForecastInput(name="installation_123", resolution="invalid")

    def test_missing_one_date(self, valid_datetime: datetime) -> None:
        """Test validation error when only one of start_date or end_date is provided."""
        data = {"name": "installation_123", "start_date": valid_datetime}
        with pytest.raises(ValidationError, match="Both start_date and end_date must be provided together"):
            GetInstallationForecastInput(**data)

        data = {"name": "installation_123", "end_date": valid_datetime}
        with pytest.raises(ValidationError, match="Both start_date and end_date must be provided together"):
            GetInstallationForecastInput(**data)

    def test_invalid_date_range(self, valid_datetime: datetime) -> None:
        """Test validation error when end_date is not after start_date."""
        data = {
            "name": "installation_123",
            "start_date": valid_datetime,
            "end_date": valid_datetime,  # Same as start_date
        }
        with pytest.raises(ValidationError, match="end_date must be after start_date"):
            GetInstallationForecastInput(**data)

        earlier_datetime = valid_datetime.replace(day=27)  # One day earlier
        data = {
            "name": "installation_123",
            "start_date": valid_datetime,
            "end_date": earlier_datetime,  # end_date before start_date
        }
        with pytest.raises(ValidationError, match="end_date must be after start_date"):
            GetInstallationForecastInput(**data)

    def test_non_timezone_aware_dates(
        self,
        non_timezone_datetime: datetime,
        non_timezone_later_datetime: datetime,
    ) -> None:
        """Test validation error for non-timezone-aware start_date or end_date."""
        data = {
            "name": "installation_123",
            "start_date": non_timezone_datetime,
            "end_date": non_timezone_later_datetime,
        }
        with pytest.raises(ValidationError, match="start_date must be timezone-aware"):
            GetInstallationForecastInput(**data)

    def test_extra_field(self) -> None:
        """Test validation error for extra fields."""
        with pytest.raises(ValidationError, match=r"extra\s+Extra inputs are not permitted"):
            GetInstallationForecastInput(name="installation_123", extra="forbidden")


class TestGetAlertstInput:
    """Tests for GetAlertstInput model validation."""

    def test_valid_full_input(self, valid_datetime: datetime, later_datetime: datetime) -> None:
        """Test valid input with all fields provided."""
        data = {
            "start_date": valid_datetime,
            "end_date": later_datetime,
            "all_alerts": False,
        }
        model = GetAlertstInput(**data)
        assert model.start_date == data["start_date"]
        assert model.end_date == data["end_date"]
        assert model.all_alerts is False

    def test_valid_minimal_input(self) -> None:
        """Test valid input with all fields defaulted."""
        model = GetAlertstInput()
        assert model.start_date is None
        assert model.end_date is None
        assert model.all_alerts is True

    def test_invalid_all_alerts_type(self) -> None:
        """Test validation error when all_alerts is not a boolean."""
        with pytest.raises(ValidationError, match=r"all_alerts\s+Input should be a valid boolean"):
            GetAlertstInput(all_alerts="true")

    def test_extra_field(self) -> None:
        """Test validation error for extra fields."""
        with pytest.raises(ValidationError, match=r"extra\s+Extra inputs are not permitted"):
            GetAlertstInput(extra="forbidden")
