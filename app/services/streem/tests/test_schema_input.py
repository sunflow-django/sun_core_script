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


@pytest.fixture
def valid_datetime() -> datetime:
    return datetime(2025, 5, 28, 12, 0, tzinfo=ZoneInfo("UTC"))


class TestGetInstallationDetailInput:
    def test_get_installation_detail_input_valid(self) -> None:
        data = {"name": "installation_123"}
        model = GetInstallationDetailInput(**data)
        assert model.name == "installation_123"

    def test_get_installation_detail_input_missing_name(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            GetInstallationDetailInput()
        assert "name" in str(exc_info.value)

    def test_get_installation_detail_input_extra_field(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            GetInstallationDetailInput(name="installation_123", extra="forbidden")
        assert "extra inputs are not permitted" in str(exc_info.value).lower()


class TestGetInstallationAlertsInput:
    def test_get_installation_alerts_input_valid_full(self, valid_datetime: datetime) -> None:
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

    def test_get_installation_alerts_input_valid_minimal(self) -> None:
        data = {"name": "installation_123"}
        model = GetInstallationAlertsInput(**data)
        assert model.name == "installation_123"
        assert model.start_date is None
        assert model.end_date is None
        assert model.all_alerts is True


class TestGetForecastInput:
    def test_get_forecast_input_valid_full(self, valid_datetime: datetime) -> None:
        data = {
            "name": "installation_123",
            "forecast_type": ForecastType.DISPATCH_PROGRAM,
            "start_date": valid_datetime,
            "end_date": valid_datetime,
            "resolution": Resolution.H1,
        }
        model = GetInstallationForecastInput(**data)
        assert model.name == "installation_123"
        assert model.forecast_type == ForecastType.DISPATCH_PROGRAM
        assert model.start_date == valid_datetime
        assert model.end_date == valid_datetime
        assert model.resolution == Resolution.H1

    def test_get_forecast_input_valid_minimal(self) -> None:
        data = {"name": "installation_123"}
        model = GetInstallationForecastInput(**data)
        assert model.name == "installation_123"
        assert model.forecast_type == ForecastType.DISPATCH_PROGRAM
        assert model.start_date is None
        assert model.end_date is None
        assert model.resolution == Resolution.H1

    def test_get_forecast_input_missing_name(self) -> None:
        data = {"resolution": Resolution.H1}
        with pytest.raises(ValidationError) as exc_info:
            GetInstallationForecastInput(**data)
        assert "name" in str(exc_info.value)


class TestGetAlertstInput:
    def test_get_alerts_input_valid_full(self, valid_datetime: datetime) -> None:
        data = {
            "start_date": valid_datetime,
            "end_date": valid_datetime,
            "all_alerts": False,
        }
        model = GetAlertstInput(**data)
        assert model.start_date == data["start_date"]
        assert model.end_date == data["end_date"]
        assert model.all_alerts is False

    def test_get_alerts_input_valid_minimal(self) -> None:
        model = GetAlertstInput()
        assert model.start_date is None
        assert model.end_date is None
        assert model.all_alerts is True

    def test_get_alerts_input_extra_field(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            GetAlertstInput(extra="forbidden")
        assert "extra inputs are not permitted" in str(exc_info.value).lower()
