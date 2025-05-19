"""Unit tests for get_streem_forecast.py."""

import os
from datetime import datetime
from datetime import timedelta
from enum import Enum
from unittest.mock import Mock

import pytest
import requests
import typer
from click.exceptions import Exit as ClickExit
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from app.nomination.get_streem_forecast import INSTALLATIONS_AUTOCOMPLETE
from app.nomination.get_streem_forecast import PARIS_TZ
from app.nomination.get_streem_forecast import Resolutions
from app.nomination.get_streem_forecast import authenticate
from app.nomination.get_streem_forecast import get_forecast
from app.nomination.get_streem_forecast import load_credentials
from app.nomination.get_streem_forecast import main


# Mock constants for testing
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_pass"
TEST_AUTH_TOKEN = "mock_token"
TEST_INSTALLATION = INSTALLATIONS_AUTOCOMPLETE[0]  # "VGP Rouen"
BASE_URL = "https://api.streem.eu"
TIMEOUT = 10


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
def mock_requests_get(mocker: MockerFixture) -> Mock:
    """Fixture to mock requests.get."""
    return mocker.patch("requests.get")


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for Typer CLI runner."""
    return CliRunner()


def test_resolutions_enum() -> None:
    """Test Resolutions enum values."""
    expected_values = ["5m", "10m", "15m", "30m", "1h", "1d", "1M"]
    assert [r.value for r in Resolutions] == expected_values
    assert Resolutions.h1.value == "1h"
    assert isinstance(Resolutions.m5, Enum)
    assert Resolutions.m5.value == "5m"


def test_load_credentials_success(mock_env: MockerFixture) -> None:
    """Test load_credentials with valid environment variables."""
    username, password = load_credentials()
    assert username == TEST_USERNAME
    assert password == TEST_PASSWORD


def test_load_credentials_missing_env(mocker: MockerFixture) -> None:
    """Test load_credentials with missing environment variables."""
    mocker.patch("app.nomination.get_streem_forecast.load_dotenv", return_value=None)
    mocker.patch.dict(os.environ, {}, clear=True)
    with pytest.raises(ClickExit):
        load_credentials()


def test_authenticate_success(mock_requests_get: Mock) -> None:
    """Test authenticate with successful response."""
    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {"auth_token": TEST_AUTH_TOKEN}
    mock_requests_get.return_value = mock_response

    token = authenticate(TEST_USERNAME, TEST_PASSWORD)

    assert token == TEST_AUTH_TOKEN
    mock_requests_get.assert_called_once_with(
        f"{BASE_URL}/authenticate",
        params={"email": TEST_USERNAME, "password": TEST_PASSWORD},
        headers={"accept": "application/json"},
        timeout=TIMEOUT,
    )


def test_authenticate_failure(mock_requests_get: Mock) -> None:
    """Test authenticate with failed response."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_requests_get.return_value = mock_response

    with pytest.raises(ClickExit):
        authenticate(TEST_USERNAME, TEST_PASSWORD)


def test_get_forecast_success(mock_requests_get: Mock) -> None:
    """Test get_forecast with successful response."""
    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {"data": [{"time": "2025-05-16T00:00:00Z", "value": 100}]}
    mock_requests_get.return_value = mock_response

    start_date = datetime.now(tz=PARIS_TZ)
    end_date = start_date + timedelta(hours=23, minutes=59)
    result = get_forecast(TEST_INSTALLATION, start_date, end_date, Resolutions.h1.value, TEST_AUTH_TOKEN)

    assert result == {"data": [{"time": "2025-05-16T00:00:00Z", "value": 100}]}
    mock_requests_get.assert_called_once_with(
        f"{BASE_URL}/v2/installations/{TEST_INSTALLATION}/forecast",
        params={
            "type": "Generation",
            "start_date": start_date.isoformat() + "Z",
            "end_date": end_date.isoformat() + "Z",
            "resolution": "1h",
        },
        headers={
            "accept": "application/json",
            "Authorization": TEST_AUTH_TOKEN,
        },
        timeout=TIMEOUT,
    )


def test_get_forecast_failure(mock_requests_get: Mock) -> None:
    """Test get_forecast with failed response."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_requests_get.return_value = mock_response

    start_date = datetime.now(tz=PARIS_TZ)
    end_date = start_date + timedelta(hours=23, minutes=59)

    with pytest.raises(ClickExit):
        get_forecast(TEST_INSTALLATION, start_date, end_date, Resolutions.h1.value, TEST_AUTH_TOKEN)


def test_main_success(runner: CliRunner, mock_requests_get: Mock, mock_env: MockerFixture) -> None:
    """Test main function with successful CLI execution."""
    # Mock authentication response
    auth_response = Mock()
    auth_response.status_code = requests.codes.ok
    auth_response.json.return_value = {"auth_token": TEST_AUTH_TOKEN}

    # Mock forecast response
    forecast_response = Mock()
    forecast_response.status_code = requests.codes.ok
    forecast_response.json.return_value = {"data": [{"time": "2025-05-16T00:00:00Z", "value": 100}]}

    # Set up mock to return both responses
    mock_requests_get.side_effect = [auth_response, forecast_response]

    tomorrow = (datetime.now(tz=PARIS_TZ) + timedelta(days=1)).strftime("%Y-%m-%d")
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(
        app,
        ["--date", tomorrow, "--name", TEST_INSTALLATION, "--resolution", "1h"],
    )

    assert result.exit_code == 0
    assert "Forecast Data" in result.stdout
    assert mock_requests_get.call_count == 2  # noqa: PLR2004


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
    mocker.patch("app.nomination.get_streem_forecast.load_dotenv", return_value=None)
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
