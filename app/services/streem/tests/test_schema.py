from datetime import datetime

import pytest
from pydantic import ValidationError

from app.constants.time_zones import PARIS_TZ
from app.services.streem.schema import Alert
from app.services.streem.schema import Alerts
from app.services.streem.schema import AuthToken
from app.services.streem.schema import EnergyType
from app.services.streem.schema import ForecastType
from app.services.streem.schema import Installation
from app.services.streem.schema import Installations
from app.services.streem.schema import LoadCurve
from app.services.streem.schema import LoadCurvePoint
from app.services.streem.schema import Resolution


# Constants
PARIS_LATITUDE = 48.8566
PARIS_LONGITUDE = 2.3522
DATA = 100.5
DATA2 = 200.7


def test_forecast_type() -> None:
    """Test EnergyType Enum"""
    assert ForecastType.GENERATION == "Generation"
    assert ForecastType.DISPATCH_PROGRAM == "Dispatch_Program"

    # Test invalid enum value
    with pytest.raises(ValueError, match="'invalid' is not a valid ForecastType"):
        ForecastType("invalid")


def test_resolution() -> None:
    """Test Resolution Enum"""
    assert Resolution.M5 == "5m"
    assert Resolution.M10 == "10m"
    assert Resolution.M15 == "15m"
    assert Resolution.M30 == "30m"
    assert Resolution.H1 == "1h"
    assert Resolution.D1 == "1d"
    assert Resolution.M1 == "1M"

    # Test invalid enum value
    with pytest.raises(ValueError, match="'invalid' is not a valid Resolution"):
        Resolution("invalid")


def test_energy_type_enum() -> None:
    """Test EnergyType Enum"""
    assert EnergyType.SOLAR == "solar"
    assert EnergyType.WIND == "wind"
    assert EnergyType.HYDRO == "hydro"
    assert EnergyType.OTHER == "other"

    # Test invalid enum value
    with pytest.raises(ValueError, match="'invalid' is not a valid EnergyType"):
        EnergyType("invalid")


def test_auth_token_valid() -> None:
    """Test AuthToken"""
    token = AuthToken(auth_token="abc123")
    assert token.auth_token == "abc123"


def test_auth_token_extra_field_fails() -> None:
    """Test AuthToken"""
    with pytest.raises(ValidationError):
        AuthToken(auth_token="abc123", extra_field="invalid")


def test_installation_valid() -> None:
    """Test Installation"""
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


def test_installation_default_values() -> None:
    """Test Installation"""
    installation = Installation(name="Test Plant")
    assert installation.client_id is None
    assert installation.energy == EnergyType.OTHER
    assert installation.external_ref is None
    assert installation.latitude is None
    assert installation.longitude is None
    assert installation.name == "Test Plant"


def test_installation_extra_field_fails() -> None:
    """Test Installation"""
    with pytest.raises(ValidationError):
        Installation(name="Test Plant", extra_field="invalid")


def test_installations_empty() -> None:
    """Test Installations"""
    installations = Installations()
    assert isinstance(installations.root, list)
    assert len(installations.root) == 0
    assert list(installations.client_ids()) == []
    assert list(installations.names()) == []


def test_installations_multiple() -> None:
    """Test Installations"""
    installations = Installations(
        root=[
            Installation(name="Plant1", client_id="client1"),
            Installation(name="Plant2", client_id="client2"),
            Installation(name="Plant3"),
        ],
    )

    assert len(installations.root) == 3  # noqa: PLR2004
    assert list(installations.client_ids()) == ["client1", "client2"]
    assert list(installations.names()) == ["Plant1", "Plant2", "Plant3"]


def test_alert_valid() -> None:
    """Test Alert"""
    created_at = datetime.now(tz=PARIS_TZ)
    alert = Alert(type="warning", installation_name="Paris Solar Plant", created_at=created_at, closed_at=None)
    assert alert.type == "warning"
    assert alert.installation_name == "Paris Solar Plant"
    assert alert.created_at == created_at
    assert alert.closed_at is None


def test_alert_default_created_at() -> None:
    """Test Alert"""
    alert = Alert(type="error", installation_name="Test Plant")
    assert alert.type == "error"
    assert alert.installation_name == "Test Plant"
    assert isinstance(alert.created_at, datetime)
    assert alert.created_at.tzinfo == PARIS_TZ
    assert alert.closed_at is None


def test_alert_extra_field_fails() -> None:
    """Test Alert"""
    with pytest.raises(ValidationError):
        Alert(type="error", installation_name="Test Plant", extra_field="invalid")


def test_alerts_empty() -> None:
    """Test Alerts"""
    alerts = Alerts()
    assert isinstance(alerts.root, list)
    assert len(alerts.root) == 0
    assert list(alerts.installation_names()) == []


def test_alerts_multiple() -> None:
    """Test Alerts"""
    alerts = Alerts(
        root=[Alert(type="warning", installation_name="Plant1"), Alert(type="error", installation_name="Plant2")],
    )

    assert len(alerts.root) == 2  # noqa: PLR2004
    assert list(alerts.installation_names()) == ["Plant1", "Plant2"]


def test_load_curve_point_valid() -> None:
    """Test LoadCurvePoint"""
    date = datetime.now(tz=PARIS_TZ)
    point = LoadCurvePoint(data=DATA, date=date)
    assert point.data == DATA
    assert point.date == date


def test_load_curve_point_default_date() -> None:
    """Test LoadCurvePoint"""
    point = LoadCurvePoint(data=DATA)
    assert point.data == DATA
    assert isinstance(point.date, datetime)
    assert point.date.tzinfo == PARIS_TZ


def test_load_curve_point_extra_field_fails() -> None:
    """Test LoadCurvePoint"""
    with pytest.raises(ValidationError):
        LoadCurvePoint(data=DATA, date=datetime.now(tz=PARIS_TZ), extra_field="invalid")


def test_load_curve_empty() -> None:
    """Test LoadCurve"""
    curve = LoadCurve(points=[])
    assert isinstance(curve.points, list)
    assert len(curve.points) == 0


def test_load_curve_multiple_points() -> None:
    """Test LoadCurve"""
    date1 = datetime.now(tz=PARIS_TZ)
    date2 = datetime.now(tz=PARIS_TZ)
    curve = LoadCurve(points=[LoadCurvePoint(data=DATA, date=date1), LoadCurvePoint(data=DATA2, date=date2)])

    assert len(curve.points) == 2  # noqa: PLR2004
    assert curve.points[0].data == DATA
    assert curve.points[0].date == date1
    assert curve.points[1].data == DATA2
    assert curve.points[1].date == date2


def test_load_curve_alias() -> None:
    """Test LoadCurve"""
    curve = LoadCurve(points=[{"data": DATA, "date": datetime.now(tz=PARIS_TZ)}])
    assert len(curve.points) == 1
    assert curve.points[0].data == DATA
