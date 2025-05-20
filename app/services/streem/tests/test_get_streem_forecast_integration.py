import os
from datetime import datetime
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from typer import Exit as TyperExit

from app.constants.time_zones import PARIS_TZ
from app.services.streem.api import ForecastType
from app.services.streem.api import Resolution
from app.services.streem.get_streem_forecast import load_credentials
from app.services.streem.get_streem_forecast import main


# Mock forecast data for 2025-05-21, hourly resolution
MOCK_FORECAST_DATA = [
    {"date": "2025-05-21T00:00:00+02:00", "data": 0.0},
    {"date": "2025-05-21T01:00:00+02:00", "data": 0.0},
    {"date": "2025-05-21T02:00:00+02:00", "data": 0.0},
    {"date": "2025-05-21T03:00:00+02:00", "data": 0.0},
    {"date": "2025-05-21T04:00:00+02:00", "data": 0.0},
    {"date": "2025-05-21T05:00:00+02:00", "data": 0.0},
    {"date": "2025-05-21T06:00:00+02:00", "data": 14.6},
    {"date": "2025-05-21T07:00:00+02:00", "data": 139.0},
    {"date": "2025-05-21T08:00:00+02:00", "data": 485.1},
    {"date": "2025-05-21T09:00:00+02:00", "data": 956.0},
    {"date": "2025-05-21T10:00:00+02:00", "data": 963.3},
    {"date": "2025-05-21T11:00:00+02:00", "data": 1184.3},
    {"date": "2025-05-21T12:00:00+02:00", "data": 1153.2},
    {"date": "2025-05-21T13:00:00+02:00", "data": 908.2},
    {"date": "2025-05-21T14:00:00+02:00", "data": 442.6},
    {"date": "2025-05-21T15:00:00+02:00", "data": 314.4},
    {"date": "2025-05-21T16:00:00+02:00", "data": 370.0},
    {"date": "2025-05-21T17:00:00+02:00", "data": 750.4},
    {"date": "2025-05-21T18:00:00+02:00", "data": 887.8},
    {"date": "2025-05-21T19:00:00+02:00", "data": 486.8},
    {"date": "2025-05-21T20:00:00+02:00", "data": 180.1},
    {"date": "2025-05-21T21:00:00+02:00", "data": 23.2},
    {"date": "2025-05-21T22:00:00+02:00", "data": 0.2},
    {"date": "2025-05-21T23:00:00+02:00", "data": 0.0},
]


@pytest.fixture
def mock_env(mocker: MockerFixture) -> None:
    """Mock environment variables for Streem API credentials."""
    mocker.patch("dotenv.load_dotenv", return_value=None)
    mocker.patch.dict(
        os.environ,
        {
            "STREEM_USERNAME": "test_user",
            "STREEM_PASSWORD": "test_pass",
        },
    )


@pytest.fixture
def mock_streem_api(mocker: MockerFixture) -> Mock:
    """Mock StreemAPI class with predefined forecast data."""
    mock_api = mocker.patch("app.services.streem.get_streem_forecast.StreemAPI")
    mock_instance = mock_api.return_value
    mock_instance.get_forecast.return_value = MOCK_FORECAST_DATA
    return mock_instance


def test_main(
    mock_env: None,
    mock_streem_api: Mock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify main function fetches and displays forecast data."""
    # Arrange
    test_date = datetime(2025, 5, 21, tzinfo=PARIS_TZ)
    name = "VGP Rouen"
    resolution = Resolution.H1

    # Act
    main(date=test_date, name=name, resolution=resolution)

    # Assert API call
    mock_streem_api.get_forecast.assert_called_once_with(
        name=name,
        forecast_type=ForecastType.GENERATION,
        start_date=test_date.replace(hour=0, minute=0, second=0, microsecond=0),
        end_date=test_date.replace(hour=23, minute=59, second=0, microsecond=0),
        resolution=resolution,
    )

    # Assert output
    captured = capsys.readouterr()
    output = captured.out
    assert "Forecast Data:" in output

    # Check if key data points are in the output
    assert "'date': '2025-05-21T00:00:00+02:00', 'data': 0" in output
    assert "'date': '2025-05-21T11:00:00+02:00', 'data': 1184.3" in output
    assert "'date': '2025-05-21T23:00:00+02:00', 'data': 0" in output


def test_load_credentials_missing_env(mocker: MockerFixture) -> None:
    """Verify load_credentials raises Exit when credentials are missing."""
    mocker.patch("dotenv.load_dotenv", return_value=None)
    mocker.patch("os.getenv", side_effect=lambda key: None)

    with pytest.raises(TyperExit):
        load_credentials()
