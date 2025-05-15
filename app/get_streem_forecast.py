"""Command-line tool to fetch forecast data from Streem Energy API."""

import os
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import Annotated

import requests
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.pretty import pprint

from app.constants.time_zones import PARIS_TZ


console = Console()

# Available installations (can be expanded)
INSTALLATIONS_AUTOCOMPLETE = ["VGP Rouen"]

# Constants
STREEM_USERNAME = "STREEM_USERNAME"
STREEM_PASSWORD = "STREEM_PASSWORD"
BASE_URL = "https://api.streem.eu"
API_VERSION = "/v2"
AUTHENTICATE_EP = "/authenticate"
INSTALLATIONS_EP = "/installations"
FORECAST_EP = "/forecast"
TIMEOUT = 10  # seconds


# Valid resolutions from API documentation
class Resolutions(str, Enum):
    m5 = "5m"
    m10 = "10m"
    m15 = "15m"
    m30 = "30m"
    h1 = "1h"
    d1 = "1d"
    M1 = "1M"


def load_credentials() -> tuple[str, str]:
    """Load Streem API credentials from .env file.

    Returns:
        Tuple containing username and password.
    """
    load_dotenv()

    username = os.getenv(STREEM_USERNAME)
    password = os.getenv(STREEM_PASSWORD)

    if not username or not password:
        console.print(f"[bold red]Error:[/bold red] {STREEM_USERNAME} and {STREEM_PASSWORD} must be set in .env file.")
        raise typer.Exit(code=1)

    return username, password


def authenticate(username: str, password: str) -> str:
    """Authenticate with Streem API and return auth token.

    Args:
        username: Streem API username.
        password: Streem API password.

    Returns:
        Authentication token.

    Raises:
        typer.Exit: If authentication fails.
    """
    url = BASE_URL + AUTHENTICATE_EP
    params = {"email": username, "password": password}
    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)

    if response.status_code != requests.codes.ok:
        console.print(f"[bold red]Authentication failed:[/bold red] Status {response.status_code} - {response.text}")
        raise typer.Exit(code=1)

    return response.json()["auth_token"]


def get_forecast(
    installation_name: str,
    start_date: datetime,
    end_date: datetime,
    resolution: str,
    auth_token: str,
) -> dict:
    """Fetch forecast data from Streem API.

    Args:
        installation_name: Name of the installation.
        start_date: Start date and time for forecast.
        end_date: End date and time for forecast.
        resolution: Time resolution for forecast data.
        auth_token: Authentication token for API.

    Returns:
        Forecast data as a dictionary.

    Raises:
        typer.Exit: If API call fails.
    """
    url = f"{BASE_URL}{API_VERSION}{INSTALLATIONS_EP}/{installation_name}{FORECAST_EP}"
    params = {
        "type": "Generation",
        "start_date": start_date.isoformat() + "Z",
        "end_date": end_date.isoformat() + "Z",
        "resolution": resolution,
    }
    headers = {
        "accept": "application/json",
        "Authorization": auth_token,
    }

    response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)

    if response.status_code != requests.codes.ok:
        console.print(f"[bold red]Forecast fetch failed:[/bold red] Status {response.status_code} - {response.text}")
        raise typer.Exit(code=1)

    return response.json()


def main(
    date: Annotated[
        datetime,
        typer.Option(
            "--date",
            "-d",
            help="Date to retrieve forecast for (defaults to tomorrow)",
            formats=["%Y-%m-%d"],
        ),
    ] = (datetime.now(tz=PARIS_TZ).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime(
        "%Y-%m-%d",
    ),
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Installation name",
            autocompletion=lambda: INSTALLATIONS_AUTOCOMPLETE,
        ),
    ] = INSTALLATIONS_AUTOCOMPLETE[0],
    resolution: Annotated[
        Resolutions,
        typer.Option(
            "--resolution",
            "-r",
            help="Time resolution for forecast",
            autocompletion=lambda: [r.value for r in Resolutions],
        ),
    ] = Resolutions.h1,
) -> None:
    """Fetch and display forecast data from Streem Energy API."""
    # Set start and end times for the specified date, timezone-aware
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=PARIS_TZ)
    end_date = date.replace(hour=23, minute=59, second=0, microsecond=0, tzinfo=PARIS_TZ)

    # Load credentials and authenticate
    username, password = load_credentials()
    auth_token = authenticate(username, password)

    # Fetch forecast data
    forecast_data = get_forecast(name, start_date, end_date, resolution, auth_token)

    # Pretty print the response
    console.print("\n[bold green]Forecast Data:[/bold green]")
    pprint(forecast_data, console=console)


if __name__ == "__main__":
    typer.run(main)
