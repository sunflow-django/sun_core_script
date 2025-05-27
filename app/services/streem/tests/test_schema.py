from datetime import datetime

import pytest
from pydantic import ValidationError

from app.constants.time_zones import PARIS_TZ
from app.services.streem.schema import Alert
from app.services.streem.schema import AlertList
from app.services.streem.schema import AuthToken
from app.services.streem.schema import EnergyType
from app.services.streem.schema import ForecastType
from app.services.streem.schema import Installation
from app.services.streem.schema import InstallationList
from app.services.streem.schema import LoadCurve
from app.services.streem.schema import LoadCurvePoint
from app.services.streem.schema import Resolution


# Constants
PARIS_LATITUDE = 48.8566
PARIS_LONGITUDE = 2.3522
DATA = 100.5
DATA2 = 200.7
EXPECTED_INSTALLATIONS_COUNT = 3
EXPECTED_ALERTS_COUNT = 2
EXPECTED_POINTS_COUNT = 2


class TestForecastType:
    """Tests for ForecastType Enum"""

    def test_valid_values(self) -> None:
        assert ForecastType.GENERATION == "Generation"
        assert ForecastType.DISPATCH_PROGRAM == "Dispatch_Program"

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="'invalid' is not a valid ForecastType"):
            ForecastType("invalid")


class TestResolution:
    """Tests for Resolution Enum"""

    def test_valid_values(self) -> None:
        assert Resolution.M5 == "5m"
        assert Resolution.M10 == "10m"
        assert Resolution.M15 == "15m"
        assert Resolution.M30 == "30m"
        assert Resolution.H1 == "1h"
        assert Resolution.D1 == "1d"
        assert Resolution.M1 == "1M"

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="'invalid' is not a valid Resolution"):
            Resolution("invalid")


class TestEnergyType:
    """Tests for EnergyType Enum"""

    def test_valid_values(self) -> None:
        assert EnergyType.SOLAR == "solar"
        assert EnergyType.WIND == "wind"
        assert EnergyType.HYDRO == "hydro"
        assert EnergyType.OTHER == "other"

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="'invalid' is not a valid EnergyType"):
            EnergyType("invalid")


class TestAuthToken:
    """Tests for AuthToken class"""

    def test_valid_auth_token(self) -> None:
        token = AuthToken(auth_token="abc123")
        assert token.auth_token == "abc123"

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError):
            AuthToken(auth_token="abc123", extra_field="invalid")


class TestInstallation:
    """Tests for Installation class"""

    def test_valid_installation(self) -> None:
        installation = Installation(
            client_id="client1",
            energy=EnergyType.SOLAR,
            external_ref="ref1",
            latitude=PARIS_LATITUDE,
            longitude=PARIS_LONGITUDE,
            name="Paris Solar Plant",
        )
        assert installation.client_id == "client1"
        assert installation.energy == EnergyType.SOLAR
        assert installation.external_ref == "ref1"
        assert installation.latitude == PARIS_LATITUDE
        assert installation.longitude == PARIS_LONGITUDE
        assert installation.name == "Paris Solar Plant"

    def test_default_values(self) -> None:
        installation = Installation(name="Test Plant")
        assert installation.client_id is None
        assert installation.energy == EnergyType.OTHER
        assert installation.external_ref is None
        assert installation.latitude is None
        assert installation.longitude is None
        assert installation.name == "Test Plant"

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError):
            Installation(name="Test Plant", extra_field="invalid")


class TestInstallations:
    """Tests for Installations class"""

    def test_empty_installations(self) -> None:
        installations = InstallationList()
        assert isinstance(installations.root, list)
        assert len(installations.root) == 0
        assert list(installations.client_ids()) == []
        assert list(installations.names()) == []

    def test_multiple_installations(self) -> None:
        installations = InstallationList(
            root=[
                Installation(name="Plant1", client_id="client1"),
                Installation(name="Plant2", client_id="client2"),
                Installation(name="Plant3"),
            ],
        )
        assert len(installations.root) == EXPECTED_INSTALLATIONS_COUNT
        assert list(installations.client_ids()) == ["client1", "client2"]
        assert list(installations.names()) == ["Plant1", "Plant2", "Plant3"]


class TestAlert:
    """Tests for Alert class"""

    def test_valid_alert(self) -> None:
        created_at = datetime.now(tz=PARIS_TZ)
        alert = Alert(type="warning", installation_name="Paris Solar Plant", created_at=created_at, closed_at=None)
        assert alert.type == "warning"
        assert alert.installation_name == "Paris Solar Plant"
        assert alert.created_at == created_at
        assert alert.closed_at is None

    def test_default_created_at(self) -> None:
        alert = Alert(type="error", installation_name="Test Plant")
        assert alert.type == "error"
        assert alert.installation_name == "Test Plant"
        assert isinstance(alert.created_at, datetime)
        assert alert.created_at.tzinfo == PARIS_TZ
        assert alert.closed_at is None

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError):
            Alert(type="error", installation_name="Test Plant", extra_field="invalid")


class TestAlerts:
    """Tests for Alerts class"""

    def test_empty_alerts(self) -> None:
        alerts = AlertList()
        assert isinstance(alerts.root, list)
        assert len(alerts.root) == 0
        assert list(alerts.installation_names()) == []

    def test_multiple_alerts(self) -> None:
        alerts = AlertList(
            root=[Alert(type="warning", installation_name="Plant1"), Alert(type="error", installation_name="Plant2")],
        )
        assert len(alerts.root) == EXPECTED_ALERTS_COUNT
        assert list(alerts.installation_names()) == ["Plant1", "Plant2"]


class TestLoadCurvePoint:
    """Tests for LoadCurvePoint class"""

    def test_valid_load_curve_point(self) -> None:
        date = datetime.now(tz=PARIS_TZ)
        point = LoadCurvePoint(data=DATA, date=date)
        assert point.data == DATA
        assert point.date == date

    def test_default_date(self) -> None:
        point = LoadCurvePoint(data=DATA)
        assert point.data == DATA
        assert isinstance(point.date, datetime)
        assert point.date.tzinfo == PARIS_TZ

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError):
            LoadCurvePoint(data=DATA, date=datetime.now(tz=PARIS_TZ), extra_field="invalid")


class TestLoadCurve:
    """Tests for LoadCurve class"""

    def test_empty_load_curve(self) -> None:
        curve = LoadCurve(points=[])
        assert isinstance(curve.points, list)
        assert len(curve.points) == 0

    def test_multiple_points(self) -> None:
        date1 = datetime.now(tz=PARIS_TZ)
        date2 = datetime.now(tz=PARIS_TZ)
        curve = LoadCurve(points=[LoadCurvePoint(data=DATA, date=date1), LoadCurvePoint(data=DATA2, date=date2)])
        assert len(curve.points) == EXPECTED_POINTS_COUNT
        assert curve.points[0].data == DATA
        assert curve.points[0].date == date1
        assert curve.points[1].data == DATA2
        assert curve.points[1].date == date2

    def test_load_curve_alias(self) -> None:
        curve = LoadCurve(points=[{"data": DATA, "date": datetime.now(tz=PARIS_TZ)}])
        assert len(curve.points) == 1
        assert curve.points[0].data == DATA
