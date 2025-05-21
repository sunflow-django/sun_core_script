import json

import pytest
from jsonschema.exceptions import ValidationError

from app.services.streem.installation import Installation
from app.services.streem.installation import InstallationManager


# Constants for magic values
PARIS_LATITUDE = 48.86
PARIS_LONGITUDE = 2.35
EXPECTED_INSTALLATION_COUNT = 2


@pytest.fixture
def valid_installation_json() -> str:
    """Fixture providing a valid JSON string for a single installation."""
    return json.dumps(
        {
            "name": "Test Installation",
            "energy": "solar",
            "latitude": PARIS_LATITUDE,
            "longitude": PARIS_LONGITUDE,
        },
    )


@pytest.fixture
def invalid_installation_json_missing_name() -> str:
    """Fixture providing an invalid JSON string missing the 'name' field."""
    return json.dumps(
        {
            "energy": "solar",
        },
    )


@pytest.fixture
def invalid_installation_json_extra_field() -> str:
    """Fixture providing an invalid JSON string with an extra field."""
    return json.dumps(
        {
            "name": "Test Installation",
            "energy": "solar",
            "extra_field": "invalid",
        },
    )


@pytest.fixture
def invalid_installation_json_wrong_energy() -> str:
    """Fixture providing an invalid JSON string with an invalid 'energy' value."""
    return json.dumps(
        {
            "name": "Test Installation",
            "energy": "nuclear",
        },
    )


@pytest.fixture
def valid_installation_manager_json() -> str:
    """Fixture providing a valid JSON string for multiple installations."""
    return json.dumps(
        [
            {
                "name": "Installation 1",
                "energy": "wind",
                "client_id": "C001",
            },
            {
                "name": "Installation 2",
                "energy": "hydro",
                "external_ref": "REF002",
            },
        ],
    )


@pytest.fixture
def empty_installation_manager_json() -> str:
    """Fixture providing an empty JSON array for InstallationManager."""
    return json.dumps([])


@pytest.fixture
def invalid_installation_manager_json() -> str:
    """Fixture providing an invalid JSON string (not a list)."""
    return json.dumps(
        {
            "name": "Not a list",
        },
    )


# Tests for Installation class
def test_installation_from_json_valid(valid_installation_json: str) -> None:
    """Test that a valid JSON string correctly initializes an Installation."""
    installation = Installation.from_json(valid_installation_json)
    assert installation.name == "Test Installation"
    assert installation.energy == "solar"
    assert installation.latitude == PARIS_LATITUDE
    assert installation.longitude == PARIS_LONGITUDE
    assert installation.client_id is None
    assert installation.external_ref is None


def test_installation_from_json_default_energy() -> None:
    """Test that 'energy' defaults to 'other' when not provided."""
    json_data = json.dumps(
        {
            "name": "Test Installation",
        },
    )
    installation = Installation.from_json(json_data)
    assert installation.energy == "other"  # Default value


def test_installation_from_json_missing_name(invalid_installation_json_missing_name: str) -> None:
    """Test that missing 'name' raises a ValidationError."""
    with pytest.raises(ValidationError, match=r".*'name' is a required property.*"):
        Installation.from_json(invalid_installation_json_missing_name)


def test_installation_from_json_extra_field(invalid_installation_json_extra_field: str) -> None:
    """Test that extra fields raise a ValidationError."""
    with pytest.raises(ValidationError, match=r".*Additional properties are not allowed.*"):
        Installation.from_json(invalid_installation_json_extra_field)


def test_installation_from_json_wrong_energy(invalid_installation_json_wrong_energy: str) -> None:
    """Test that an invalid 'energy' value raises a ValidationError."""
    with pytest.raises(ValidationError, match=r".*'nuclear' is not one of \['solar', 'wind', 'hydro', 'other'\].*"):
        Installation.from_json(invalid_installation_json_wrong_energy)


# Tests for InstallationManager class
def test_installation_manager_from_json_valid(valid_installation_manager_json: str) -> None:
    """Test that a valid JSON array correctly populates InstallationManager."""
    manager = InstallationManager.from_json(valid_installation_manager_json)
    assert len(manager.installations) == EXPECTED_INSTALLATION_COUNT
    assert manager.installations[0].name == "Installation 1"
    assert manager.installations[0].energy == "wind"
    assert manager.installations[0].client_id == "C001"
    assert manager.installations[1].name == "Installation 2"
    assert manager.installations[1].energy == "hydro"
    assert manager.installations[1].external_ref == "REF002"


def test_installation_manager_from_json_empty(empty_installation_manager_json: str) -> None:
    """Test that an empty JSON array results in an empty InstallationManager."""
    manager = InstallationManager.from_json(empty_installation_manager_json)
    assert len(manager.installations) == 0


def test_installation_manager_from_json_invalid_not_list(invalid_installation_manager_json: str) -> None:
    """Test that a non-array JSON input raises a ValidationError."""
    with pytest.raises(ValidationError, match=r".*'type'.*"):
        InstallationManager.from_json(invalid_installation_manager_json)


def test_installation_manager_from_json_invalid_installation() -> None:
    """Test that an invalid installation in the array raises a ValidationError."""
    invalid_json = json.dumps([{"energy": "solar"}])  # Missing 'name'
    with pytest.raises(ValidationError, match=r".*'name' is a required property.*"):
        InstallationManager.from_json(invalid_json)


def test_installation_manager_iter_client_ids(valid_installation_manager_json: str) -> None:
    """Test that iter_client_ids yields the correct client IDs."""
    manager = InstallationManager.from_json(valid_installation_manager_json)
    client_ids = list(manager.iter_client_ids())
    assert client_ids == ["C001", None]


def test_installation_manager_iter_names(valid_installation_manager_json: str) -> None:
    """Test that iter_names yields the correct names."""
    manager = InstallationManager.from_json(valid_installation_manager_json)
    names = list(manager.iter_names())
    assert names == ["Installation 1", "Installation 2"]
