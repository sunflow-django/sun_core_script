from datetime import datetime

import pytest
from pydantic import ValidationError

from app.constants.time_zones import PARIS_TZ
from app.services.streem.schema import Alert
from app.services.streem.schema import Alerts
from app.services.streem.schema import EnergyType
from app.services.streem.schema import Installation
from app.services.streem.schema import Installations
from app.services.streem.schema import LoadCurve
from app.services.streem.schema import LoadCurvePoint


# Constants to avoid magic value used in comparison
PARIS_LATITUDE = 48.8566
PARIS_LONGITUDE = 2.3522
DATA_1 = 105.5
DATA_2 = 200.7
DATA_3 = 150.0


def test_installation_validation() -> None:
    """Test Installation model validation."""
    data = {
        "client_id": "client123",
        "energy": "solar",
        "external_ref": "ref456",
        "latitude": PARIS_LATITUDE,
        "longitude": PARIS_LONGITUDE,
        "name": "Paris Solar Plant",
    }
    installation = Installation(**data)
    assert installation.client_id == "client123"
    assert installation.energy == EnergyType.SOLAR
    assert installation.external_ref == "ref456"
    assert installation.latitude == PARIS_LATITUDE
    assert installation.longitude == PARIS_LONGITUDE
    assert installation.name == "Paris Solar Plant"


@pytest.mark.parametrize(
    ("data", "expected_name", "expected_energy"),
    [
        (
            {
                "name": "Minimal Plant",
                "energy": "wind",
            },
            "Minimal Plant",
            EnergyType.WIND,
        ),
        (
            {
                "name": "Default Plant",
                "client_id": None,
                "energy": "other",
                "external_ref": None,
                "latitude": None,
                "longitude": None,
            },
            "Default Plant",
            EnergyType.OTHER,
        ),
    ],
)
def test_installation_parametrized(
    data: dict,
    expected_name: str,
    expected_energy: EnergyType,
) -> None:
    """Test Installation model with various input configurations."""
    installation = Installation(**data)
    assert installation.name == expected_name
    assert installation.energy == expected_energy
    assert installation.client_id == data.get("client_id")
    assert installation.external_ref == data.get("external_ref")
    assert installation.latitude == data.get("latitude")
    assert installation.longitude == data.get("longitude")


def test_installation_invalid_energy() -> None:
    """Test Installation with invalid energy type."""
    data = {
        "name": "Invalid Plant",
        "energy": "invalid",
    }
    with pytest.raises(ValidationError):
        Installation(**data)


def test_installation_missing_name() -> None:
    """Test Installation with missing required name field."""
    data = {
        "energy": "solar",
    }
    with pytest.raises(ValidationError):
        Installation(**data)


def test_installations_validation() -> None:
    """Test Installations model validation."""
    data = {
        "installations": [
            {
                "client_id": "client123",
                "energy": "solar",
                "name": "Paris Solar Plant",
            },
            {
                "client_id": None,
                "energy": "wind",
                "name": "Brittany Wind Farm",
            },
        ],
    }
    installations = Installations(**data)
    assert len(installations.installations) == 2  # noqa: PLR2004
    assert installations.installations[0].client_id == "client123"
    assert installations.installations[0].name == "Paris Solar Plant"
    assert installations.installations[1].client_id is None
    assert installations.installations[1].name == "Brittany Wind Farm"


def test_installations_empty() -> None:
    """Test Installations with empty list."""
    installations = Installations(installations=[])
    assert installations.installations == []


def test_installations_client_ids() -> None:
    """Test Installations client_ids iterator."""
    installations = Installations(
        installations=[
            Installation(name="Plant1", client_id="client1"),
            Installation(name="Plant2", client_id=None),
            Installation(name="Plant3", client_id="client3"),
        ],
    )
    client_ids = list(installations.client_ids())
    assert client_ids == ["client1", "client3"]


def test_installations_names() -> None:
    """Test Installations names iterator."""
    installations = Installations(
        installations=[
            Installation(name="Plant1", client_id="client1"),
            Installation(name="Plant2", client_id=None),
            Installation(name="Plant3", client_id="client3"),
        ],
    )
    names = list(installations.names())
    assert names == ["Plant1", "Plant2", "Plant3"]


@pytest.mark.parametrize(
    ("installations_data", "expected_client_ids", "expected_names"),
    [
        (
            [],
            [],
            [],
        ),
        (
            [
                {"name": "Plant1", "client_id": "client1"},
                {"name": "Plant2", "client_id": None},
            ],
            ["client1"],
            ["Plant1", "Plant2"],
        ),
        (
            [
                {"name": "Plant3", "client_id": "client3"},
                {"name": "Plant4", "client_id": "client4"},
            ],
            ["client3", "client4"],
            ["Plant3", "Plant4"],
        ),
    ],
)
def test_installations_parametrized(
    installations_data: list[dict],
    expected_client_ids: list[str],
    expected_names: list[str],
) -> None:
    """Test Installations model with various input configurations."""
    installations = Installations(
        installations=[Installation(**data) for data in installations_data],
    )
    assert list(installations.client_ids()) == expected_client_ids
    assert list(installations.names()) == expected_names


def test_alert_validation() -> None:
    """Test Alert model validation."""
    data = {
        "closed_at": "2025-05-21T18:00:00+02:00",
        "created_at": "2025-05-20T12:00:00+02:00",
        "installation_name": "Paris Solar Plant",
        "type": "Overheating",
    }
    alert = Alert(**data)
    assert alert.closed_at == datetime(2025, 5, 21, 18, 0, tzinfo=PARIS_TZ)
    assert alert.created_at == datetime(2025, 5, 20, 12, 0, tzinfo=PARIS_TZ)
    assert alert.installation_name == "Paris Solar Plant"
    assert alert.type == "Overheating"


@pytest.mark.parametrize(
    ("data", "expected_installation_name", "expected_type"),
    [
        (
            {
                "created_at": "2025-05-20T12:00:00+02:00",
                "installation_name": "Minimal Plant",
                "type": "Voltage Spike",
            },
            "Minimal Plant",
            "Voltage Spike",
        ),
        (
            {
                "created_at": "2025-05-20T12:00:00+02:00",
                "installation_name": "Null Plant",
                "type": "Maintenance",
                "closed_at": None,
            },
            "Null Plant",
            "Maintenance",
        ),
    ],
)
def test_alert_parametrized(
    data: dict,
    expected_installation_name: str,
    expected_type: str,
) -> None:
    """Test Alert model with various input configurations."""
    alert = Alert(**data)
    assert alert.installation_name == expected_installation_name
    assert alert.type == expected_type
    assert alert.created_at == datetime(2025, 5, 20, 12, 0, tzinfo=PARIS_TZ)
    assert alert.closed_at == data.get("closed_at")


def test_alert_missing_required() -> None:
    """Test Alert with missing required fields."""
    data = {
        "installation_name": "Missing Plant",
    }
    with pytest.raises(ValidationError):
        Alert(**data)


def test_alerts_validation() -> None:
    """Test Alerts model validation."""
    data = {
        "alerts": [
            {
                "installation_name": "Paris Solar Plant",
                "type": "Overheating",
                "created_at": "2025-05-20T12:00:00+02:00",
            },
            {
                "installation_name": "Brittany Wind Farm",
                "type": "Maintenance",
                "created_at": "2025-05-20T13:00:00+02:00",
            },
        ],
    }
    alerts = Alerts(**data)
    assert len(alerts.alerts) == 2  # noqa: PLR2004
    assert alerts.alerts[0].installation_name == "Paris Solar Plant"
    assert alerts.alerts[0].type == "Overheating"
    assert alerts.alerts[1].installation_name == "Brittany Wind Farm"
    assert alerts.alerts[1].type == "Maintenance"


def test_alerts_empty() -> None:
    """Test Alerts with empty list."""
    alerts = Alerts(alerts=[])
    assert alerts.alerts == []


def test_alerts_installation_names() -> None:
    """Test Alerts installation_names iterator."""
    alerts = Alerts(
        alerts=[
            Alert(
                installation_name="Plant1",
                type="Overheating",
                created_at=datetime(2025, 5, 20, 12, 0, tzinfo=PARIS_TZ),
            ),
            Alert(
                installation_name="Plant2",
                type="Maintenance",
                created_at=datetime(2025, 5, 20, 13, 0, tzinfo=PARIS_TZ),
            ),
        ],
    )
    names = list(alerts.installation_names())
    assert names == ["Plant1", "Plant2"]


@pytest.mark.parametrize(
    ("alerts_data", "expected_names"),
    [
        (
            [],
            [],
        ),
        (
            [
                {
                    "installation_name": "Plant1",
                    "type": "Overheating",
                    "created_at": "2025-05-20T12:00:00+02:00",
                },
            ],
            ["Plant1"],
        ),
        (
            [
                {
                    "installation_name": "Plant1",
                    "type": "Overheating",
                    "created_at": "2025-05-20T12:00:00+02:00",
                },
                {
                    "installation_name": "Plant2",
                    "type": "Maintenance",
                    "created_at": "2025-05-20T13:00:00+02:00",
                },
            ],
            ["Plant1", "Plant2"],
        ),
    ],
)
def test_alerts_parametrized(
    alerts_data: list[dict],
    expected_names: list[str],
) -> None:
    """Test Alerts model with various input configurations."""
    alerts = Alerts(alerts=[Alert(**data) for data in alerts_data])
    assert list(alerts.installation_names()) == expected_names


def test_load_curve_point_validation() -> None:
    """Test LoadCurvePoint model validation."""
    data = {
        "data": DATA_1,
        "date": "2025-05-21T18:00:00+02:00",
    }
    point = LoadCurvePoint(**data)
    assert point.data == DATA_1
    assert point.date == datetime(2025, 5, 21, 18, 0, tzinfo=PARIS_TZ)


def test_load_curve_validation() -> None:
    """Test LoadCurve model validation."""
    data = {
        "points": [
            {"data": DATA_1, "date": "2025-05-21T18:00:00+02:00"},
            {"data": DATA_2, "date": "2025-05-21T19:00:00+02:00"},
        ],
    }
    curve = LoadCurve(**data)
    assert len(curve.points) == 2  # noqa: PLR2004
    assert curve.points[0].data == DATA_1
    assert curve.points[0].date == datetime(2025, 5, 21, 18, 0, tzinfo=PARIS_TZ)
    assert curve.points[1].data == DATA_2
    assert curve.points[1].date == datetime(2025, 5, 21, 19, 0, tzinfo=PARIS_TZ)


def test_load_curve_empty() -> None:
    """Test LoadCurve with empty points."""
    curve = LoadCurve(points=[])
    assert curve.points == []


@pytest.mark.parametrize(
    ("data", "expected_points_length"),
    [
        (
            {"points": []},
            0,
        ),
        (
            {},
            0,
        ),
        (
            {
                "points": [
                    {"data": DATA_3, "date": "2025-05-21T18:00:00+02:00"},
                ],
            },
            1,
        ),
    ],
)
def test_load_curve_parametrized(data: dict, expected_points_length: int) -> None:
    """Test LoadCurve model with various input configurations."""
    curve = LoadCurve(**data)
    assert len(curve.points) == expected_points_length
    if expected_points_length > 0:
        assert curve.points[0].data == DATA_3
        assert curve.points[0].date == datetime(2025, 5, 21, 18, 0, tzinfo=PARIS_TZ)


@pytest.mark.parametrize(
    ("data", "expected_data", "expected_date"),
    [
        (
            {
                "data": DATA_3,
                "date": "2025-05-21T18:00:00+02:00",
            },
            DATA_3,
            datetime(2025, 5, 21, 18, 0, tzinfo=PARIS_TZ),
        ),
        (
            {
                "data": 0.0,
                "date": "2025-05-21T19:00:00+02:00",
            },
            0.0,
            datetime(2025, 5, 21, 19, 0, tzinfo=PARIS_TZ),
        ),
    ],
)
def test_load_curve_point_parametrized(
    data: dict,
    expected_data: float,
    expected_date: datetime,
) -> None:
    """Test LoadCurvePoint model with various input configurations."""
    point = LoadCurvePoint(**data)
    assert point.data == expected_data
    assert point.date == expected_date
