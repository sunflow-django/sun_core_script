from datetime import UTC
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
INVALID_LATITUDE = 91.0  # Outside valid range [-90, 90]
INVALID_LONGITUDE = 181.0  # Outside valid range [-180, 180]
UTC_TZ = UTC


@pytest.fixture
def valid_installation() -> Installation:
    """Fixture for a valid Installation instance."""
    return Installation(
        client_id="client1",
        energy=EnergyType.SOLAR,
        external_ref="ref1",
        latitude=PARIS_LATITUDE,
        longitude=PARIS_LONGITUDE,
        name="Paris Solar Plant",
    )


@pytest.fixture
def valid_alert() -> Alert:
    """Fixture for a valid Alert instance."""
    return Alert(
        type="warning",
        installation_name="Paris Solar Plant",
        created_at=datetime.now(tz=PARIS_TZ),
        closed_at=None,
    )


@pytest.fixture
def valid_load_curve_point() -> LoadCurvePoint:
    """Fixture for a valid LoadCurvePoint instance."""
    return LoadCurvePoint(data=DATA, date=datetime.now(tz=PARIS_TZ))


class TestForecastType:
    """Tests for ForecastType Enum."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (ForecastType.GENERATION, "Generation"),
            (ForecastType.DISPATCH_PROGRAM, "Dispatch_Program"),
        ],
    )
    def test_valid_values(self, value: ForecastType, expected: str) -> None:
        assert value == expected

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="'invalid' is not a valid ForecastType"):
            ForecastType("invalid")


class TestResolution:
    """Tests for Resolution Enum."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (Resolution.M5, "5m"),
            (Resolution.M10, "10m"),
            (Resolution.M15, "15m"),
            (Resolution.M30, "30m"),
            (Resolution.H1, "1h"),
            (Resolution.D1, "1d"),
            (Resolution.M1, "1M"),
        ],
    )
    def test_valid_values(self, value: Resolution, expected: str) -> None:
        assert value == expected

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="'invalid' is not a valid Resolution"):
            Resolution("invalid")


class TestEnergyType:
    """Tests for EnergyType Enum."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (EnergyType.SOLAR, "solar"),
            (EnergyType.WIND, "wind"),
            (EnergyType.HYDRO, "hydro"),
            (EnergyType.OTHER, "other"),
        ],
    )
    def test_valid_values(self, value: EnergyType, expected: str) -> None:
        assert value == expected

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="'invalid' is not a valid EnergyType"):
            EnergyType("invalid")


class TestAuthToken:
    """Tests for AuthToken class."""

    def test_valid_auth_token(self) -> None:
        token = AuthToken(auth_token="abc123")
        assert token.auth_token == "abc123"

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            AuthToken(auth_token="abc123", extra_field="invalid")

    def test_json_serialization(self) -> None:
        token = AuthToken(auth_token="abc123")
        assert token.model_dump_json() == '{"auth_token":"abc123"}'
        assert AuthToken.model_validate_json('{"auth_token":"abc123"}') == token


class TestInstallation:
    """Tests for Installation class."""

    def test_valid_installation(self, valid_installation: Installation) -> None:
        assert valid_installation.client_id == "client1"
        assert valid_installation.energy == EnergyType.SOLAR
        assert valid_installation.external_ref == "ref1"
        assert valid_installation.latitude == PARIS_LATITUDE
        assert valid_installation.longitude == PARIS_LONGITUDE
        assert valid_installation.name == "Paris Solar Plant"

    def test_default_values(self) -> None:
        installation = Installation(name="Test Plant")
        assert installation.client_id is None
        assert installation.energy == EnergyType.OTHER
        assert installation.external_ref is None
        assert installation.latitude is None
        assert installation.longitude is None
        assert installation.name == "Test Plant"

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Installation(name="Test Plant", extra_field="invalid")

    @pytest.mark.parametrize(
        ("latitude", "longitude"),
        [
            (INVALID_LATITUDE, PARIS_LONGITUDE),
            (-INVALID_LATITUDE, PARIS_LONGITUDE),
            (PARIS_LATITUDE, INVALID_LONGITUDE),
            (PARIS_LATITUDE, -INVALID_LONGITUDE),
        ],
    )
    def test_invalid_coordinates(self, latitude: float, longitude: float) -> None:
        with pytest.raises(
            ValidationError,
            match="Value error, Latitude must be between -90 and 90|Longitude must be between -180 and 180",
        ):
            Installation(
                name="Test Plant",
                latitude=latitude,
                longitude=longitude,
            )

    def test_json_serialization(self, valid_installation: Installation) -> None:
        expected_json = (
            f'{{"client_id":"client1","energy":"solar","external_ref":"ref1",'
            f'"latitude":{PARIS_LATITUDE},"longitude":{PARIS_LONGITUDE},"name":"Paris Solar Plant"}}'
        )
        assert valid_installation.model_dump_json() == expected_json
        assert Installation.model_validate_json(expected_json) == valid_installation


class TestInstallationList:
    """Tests for InstallationList class."""

    @pytest.fixture
    def installation_list(self) -> InstallationList:
        return InstallationList(
            root=[
                Installation(name="Plant1", client_id="client1"),
                Installation(name="Plant2", client_id="client2"),
                Installation(name="Plant3"),
            ],
        )

    def test_empty_installations(self) -> None:
        installations = InstallationList()
        assert isinstance(installations.root, list)
        assert len(installations.root) == 0
        assert list(installations.client_ids()) == []
        assert list(installations.names()) == []

    def test_multiple_installations(self, installation_list: InstallationList) -> None:
        assert len(installation_list.root) == EXPECTED_INSTALLATIONS_COUNT
        assert list(installation_list.client_ids()) == ["client1", "client2"]
        assert list(installation_list.names()) == ["Plant1", "Plant2", "Plant3"]

    def test_json_serialization(self, installation_list: InstallationList) -> None:
        json_data = installation_list.model_dump_json()
        assert InstallationList.model_validate_json(json_data) == installation_list


class TestAlert:
    """Tests for Alert class."""

    def test_valid_alert(self, valid_alert: Alert) -> None:
        assert valid_alert.type == "warning"
        assert valid_alert.installation_name == "Paris Solar Plant"
        assert isinstance(valid_alert.created_at, datetime)
        assert valid_alert.created_at.tzinfo == PARIS_TZ
        assert valid_alert.closed_at is None

    def test_default_created_at(self) -> None:
        alert = Alert(type="error", installation_name="Test Plant")
        assert alert.type == "error"
        assert alert.installation_name == "Test Plant"
        assert isinstance(alert.created_at, datetime)
        assert alert.created_at.tzinfo == PARIS_TZ
        assert alert.closed_at is None

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Alert(type="error", installation_name="Test Plant", extra_field="invalid")

    def test_number_coercion_to_str(self) -> None:
        alert = Alert(type=123, installation_name="Test Plant")
        assert alert.type == "123"
        assert alert.installation_name == "Test Plant"

    def test_invalid_timezone(self) -> None:
        with pytest.raises(ValidationError, match="Value error, datetime must be timezone-aware"):
            Alert(
                type="warning",
                installation_name="Test Plant",
                created_at=datetime.now(tz=None),
            )

    def test_json_serialization(self, valid_alert: Alert) -> None:
        json_data = valid_alert.model_dump_json()
        assert Alert.model_validate_json(json_data) == valid_alert


class TestAlertList:
    """Tests for AlertList class."""

    @pytest.fixture
    def alert_list(self) -> AlertList:
        return AlertList(
            root=[Alert(type="warning", installation_name="Plant1"), Alert(type="error", installation_name="Plant2")],
        )

    def test_empty_alerts(self) -> None:
        alerts = AlertList()
        assert isinstance(alerts.root, list)
        assert len(alerts.root) == 0
        assert list(alerts.installation_names()) == []

    def test_multiple_alerts(self, alert_list: AlertList) -> None:
        assert len(alert_list.root) == EXPECTED_ALERTS_COUNT
        assert list(alert_list.installation_names()) == ["Plant1", "Plant2"]

    def test_json_serialization(self, alert_list: AlertList) -> None:
        json_data = alert_list.model_dump_json()
        assert AlertList.model_validate_json(json_data) == alert_list


class TestLoadCurvePoint:
    """Tests for LoadCurvePoint class."""

    def test_valid_load_curve_point(self, valid_load_curve_point: LoadCurvePoint) -> None:
        assert valid_load_curve_point.data == DATA
        assert isinstance(valid_load_curve_point.date, datetime)
        assert valid_load_curve_point.date.tzinfo == PARIS_TZ

    def test_default_date(self) -> None:
        point = LoadCurvePoint(data=DATA)
        assert point.data == DATA
        assert isinstance(point.date, datetime)
        assert point.date.tzinfo == PARIS_TZ

    def test_extra_field_fails(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            LoadCurvePoint(data=DATA, date=datetime.now(tz=PARIS_TZ), extra_field="invalid")

    def test_invalid_timezone(self) -> None:
        with pytest.raises(ValidationError, match="Value error, datetime must be timezone-aware"):
            LoadCurvePoint(data=DATA, date=datetime.now(tz=None))

    def test_json_serialization(self, valid_load_curve_point: LoadCurvePoint) -> None:
        json_data = valid_load_curve_point.model_dump_json()
        assert LoadCurvePoint.model_validate_json(json_data) == valid_load_curve_point


class TestLoadCurve:
    """Tests for LoadCurve class."""

    @pytest.fixture
    def load_curve(self) -> LoadCurve:
        date1 = datetime.now(tz=PARIS_TZ)
        date2 = datetime.now(tz=PARIS_TZ)
        return LoadCurve(root=[LoadCurvePoint(data=DATA, date=date1), LoadCurvePoint(data=DATA2, date=date2)])

    def test_empty_load_curve(self) -> None:
        curve = LoadCurve([])
        assert isinstance(curve.root, list)
        assert len(curve.root) == 0

    def test_multiple_points(self, load_curve: LoadCurve) -> None:
        assert len(load_curve.root) == EXPECTED_POINTS_COUNT
        assert load_curve.root[0].data == DATA
        assert load_curve.root[1].data == DATA2
        assert all(isinstance(point.date, datetime) for point in load_curve.root)
        assert all(point.date.tzinfo == PARIS_TZ for point in load_curve.root)

    def test_load_curve_alias(self) -> None:
        curve = LoadCurve(root=[{"data": DATA, "date": datetime.now(tz=PARIS_TZ)}])
        assert len(curve.root) == 1
        assert curve.root[0].data == DATA

    def test_json_serialization(self, load_curve: LoadCurve) -> None:
        json_data = load_curve.model_dump_json()
        assert LoadCurve.model_validate_json(json_data) == load_curve
