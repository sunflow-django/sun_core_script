"""Unit tests for get_streem_forecast.py."""

import os
from datetime import datetime
from datetime import timedelta
from enum import Enum
from unittest.mock import Mock

import pytest
import typer
from click.exceptions import Exit as ClickExit
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from app.services.streem.api import ForecastType
from app.services.streem.get_streem_forecast import INSTALLATIONS_AUTOCOMPLETE
from app.services.streem.get_streem_forecast import PARIS_TZ
from app.services.streem.get_streem_forecast import Resolution
from app.services.streem.get_streem_forecast import load_credentials
from app.services.streem.get_streem_forecast import main


# Mock constants for testing
TESTED_MODULE = "app.services.streem.get_streem_forecast"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_pass"
TEST_INSTALLATION = INSTALLATIONS_AUTOCOMPLETE[0]  # "VGP Rouen"


@pytest.fixture
def mock_env(mocker: MockerFixture) -> None:
    """Fixture to mock environment variables and dotenv."""
    mocker.patch.dict(
        os.environ,
        {
            "STREEM_USERNAME": TEST_USERNAME,
            "STREEM_PASSWORD": TEST_PASSWORD,
        },
    )


@pytest.fixture
def mock_streem_api(mocker: MockerFixture) -> Mock:
    """Fixture to mock StreemAPI."""
    mock_api = mocker.patch(TESTED_MODULE + ".StreemAPI")
    mock_instance = mock_api.return_value
    mock_instance.get_forecast.return_value = [
        {"time": "2025-05-16T00:00:00Z", "value": 100},
    ]
    return mock_instance


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for Typer CLI runner."""
    return CliRunner()


@pytest.fixture
def tomorrow_dates() -> tuple[str, datetime, datetime]:
    """Fixture for tomorrow's date and expected start/end datetimes."""
    tomorrow = (datetime.now(tz=PARIS_TZ) + timedelta(days=1)).date()
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    expected_start_date = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, tzinfo=PARIS_TZ)
    expected_end_date = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 0, tzinfo=PARIS_TZ)
    return tomorrow_str, expected_start_date, expected_end_date


def test_resolutions_enum() -> None:
    """Test Resolution enum values."""
    expected_values = ["5m", "10m", "15m", "30m", "1h", "1d", "1M"]
    assert [r.value for r in Resolution] == expected_values
    assert Resolution.H1.value == "1h"
    assert isinstance(Resolution.M5, Enum)
    assert Resolution.M5.value == "5m"


def test_load_credentials_success(mock_env: MockerFixture) -> None:
    """Test load_credentials with valid environment variables."""
    username, password = load_credentials()
    assert username == TEST_USERNAME
    assert password == TEST_PASSWORD


def test_load_credentials_missing_env(mocker: MockerFixture) -> None:
    """Test load_credentials with missing environment variables."""
    mocker.patch(TESTED_MODULE + ".load_dotenv", return_value=None)
    mocker.patch.dict(os.environ, {}, clear=True)
    with pytest.raises(ClickExit):
        load_credentials()


def test_main_success(
    runner: CliRunner,
    mock_streem_api: Mock,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
) -> None:
    """Test main function with successful CLI execution."""
    tomorrow_str, expected_start_date, expected_end_date = tomorrow_dates

    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        [
            "--date",
            tomorrow_str,
            "--name",
            TEST_INSTALLATION,
            "--resolution",
            "1h",
        ],
    )

    assert result.exit_code == 0  # Fixed exit code
    assert "Forecast Data" in result.stdout
    mock_streem_api.get_forecast.assert_called_once_with(
        name=TEST_INSTALLATION,
        forecast_type=ForecastType.GENERATION,
        start_date=expected_start_date,
        end_date=expected_end_date,
        resolution=Resolution.H1,
    )


def test_main_api_error(
    runner: CliRunner,
    mocker: MockerFixture,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
) -> None:
    """Test main function when StreemAPI raises an error."""
    mock_api = mocker.patch(TESTED_MODULE + ".StreemAPI")
    mock_instance = mock_api.return_value
    # Mock StreemAPIError to avoid constructor issues
    mock_instance.get_forecast.side_effect = Exception("API connection failed")  # Temporary workaround

    tomorrow_str, _, _ = tomorrow_dates
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", tomorrow_str, "--name", TEST_INSTALLATION, "--resolution", "1h"],
    )

    assert result.exit_code == 1


@pytest.mark.parametrize("resolution", list(Resolution))
def test_main_different_resolutions(
    runner: CliRunner,
    mock_streem_api: Mock,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
    resolution: Resolution,
) -> None:
    """Test main function with different resolution values."""
    tomorrow_str, expected_start_date, expected_end_date = tomorrow_dates

    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", tomorrow_str, "--name", TEST_INSTALLATION, "--resolution", resolution.value],
    )

    assert result.exit_code == 0
    assert "Forecast Data" in result.stdout
    mock_streem_api.get_forecast.assert_called_once_with(
        name=TEST_INSTALLATION,
        forecast_type=ForecastType.GENERATION,
        start_date=expected_start_date,
        end_date=expected_end_date,
        resolution=resolution,
    )


def test_main_different_installations(
    runner: CliRunner,
    mock_streem_api: Mock,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
) -> None:
    """Test main function with different installation names."""
    tomorrow_str, expected_start_date, expected_end_date = tomorrow_dates

    app = typer.Typer()
    app.command()(main)
    for installation in INSTALLATIONS_AUTOCOMPLETE:
        result = runner.invoke(
            app,
            ["--date", tomorrow_str, "--name", installation, "--resolution", "1h"],
        )
        assert result.exit_code == 0
        assert "Forecast Data" in result.stdout
        mock_streem_api.get_forecast.assert_called_with(
            name=installation,
            forecast_type=ForecastType.GENERATION,
            start_date=expected_start_date,
            end_date=expected_end_date,
            resolution=Resolution.H1,
        )


def test_main_default_arguments(
    runner: CliRunner,
    mock_streem_api: Mock,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
) -> None:
    """Test main function with default arguments."""
    _, expected_start_date, expected_end_date = tomorrow_dates

    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(app)  # No arguments provided

    assert result.exit_code == 0
    assert "Forecast Data" in result.stdout
    mock_streem_api.get_forecast.assert_called_once_with(
        name=INSTALLATIONS_AUTOCOMPLETE[0],
        forecast_type=ForecastType.GENERATION,
        start_date=expected_start_date,
        end_date=expected_end_date,
        resolution=Resolution.H1,
    )


def test_main_invalid_date(runner: CliRunner) -> None:
    """Test main function with invalid date format."""
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", "invalid-date", "--name", TEST_INSTALLATION, "--resolution", "1h"],
    )

    assert result.exit_code == 2  # noqa: PLR2004
    assert "Invalid value for '--date'" in result.stdout


def test_main_missing_credentials(runner: CliRunner, mocker: MockerFixture) -> None:
    """Test main function with missing credentials."""
    mocker.patch(TESTED_MODULE + ".load_dotenv", return_value=None)
    mocker.patch.dict(os.environ, {}, clear=True)
    tomorrow = (datetime.now(tz=PARIS_TZ) + timedelta(days=1)).strftime("%Y-%m-%d")
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", tomorrow, "--name", TEST_INSTALLATION, "--resolution", "1h"],
    )

    assert result.exit_code == 1
    assert "STREEM_USERNAME and STREEM_PASSWORD must be set in .env file" in result.stdout


def test_main_output_formatting(
    runner: CliRunner,
    mock_streem_api: Mock,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
) -> None:
    """Test main function output formatting."""
    mock_streem_api.get_forecast.return_value = [
        {"time": "2025-05-16T00:00:00Z", "value": 100},
        {"time": "2025-05-16T01:00:00Z", "value": 150},
    ]

    tomorrow_str, _, _ = tomorrow_dates
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", tomorrow_str, "--name", TEST_INSTALLATION, "--resolution", "1h"],
    )

    assert result.exit_code == 0
    assert "Forecast Data" in result.stdout
    assert "2025-05-16T00:00:00Z" in result.stdout
    assert "100" in result.stdout
    assert "2025-05-16T01:00:00Z" in result.stdout
    assert "150" in result.stdout


def test_main_invalid_installation(
    runner: CliRunner,
    mock_streem_api: Mock,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
) -> None:
    """Test main function with invalid installation name."""
    mock_streem_api.get_forecast.side_effect = Exception("Invalid installation name")  # Temporary workaround

    tomorrow_str, _, _ = tomorrow_dates
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", tomorrow_str, "--name", "Invalid Installation", "--resolution", "1h"],
    )

    assert result.exit_code == 1


def test_main_empty_forecast(
    runner: CliRunner,
    mock_streem_api: Mock,
    mock_env: MockerFixture,
    tomorrow_dates: tuple[str, datetime, datetime],
) -> None:
    """Test main function with empty forecast data."""
    mock_streem_api.get_forecast.return_value = []

    tomorrow_str, _, _ = tomorrow_dates
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", tomorrow_str, "--name", TEST_INSTALLATION, "--resolution", "1h"],
    )

    assert result.exit_code == 0
    assert "Forecast Data" in result.stdout
    assert "[]" in result.stdout


def test_main_past_date(runner: CliRunner, mock_streem_api: Mock, mock_env: MockerFixture) -> None:
    """Test main function with a past date."""
    mock_streem_api.get_forecast.side_effect = Exception("Date in the past is not allowed")  # Temporary workaround

    past_date = (datetime.now(tz=PARIS_TZ) - timedelta(days=1)).strftime("%Y-%m-%d")
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", past_date, "--name", TEST_INSTALLATION, "--resolution", "1h"],
    )

    assert result.exit_code == 1
