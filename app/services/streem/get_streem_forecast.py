"""Command-line tool to fetch forecast data from Streem Energy API."""

import os
from datetime import datetime
from datetime import timedelta
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.pretty import pprint

from app.constants.time_zones import PARIS_TZ
from app.services.streem.api import ForecastType
from app.services.streem.api import Resolution
from app.services.streem.api import StreemAPI
from app.services.streem.api import StreemAPIError


console = Console()

# Available installations (can be expanded)
INSTALLATIONS_AUTOCOMPLETE = ["VGP Rouen"]

# Constants
STREEM_USERNAME = "STREEM_USERNAME"
STREEM_PASSWORD = "STREEM_PASSWORD"


def load_credentials() -> tuple[str, str]:
    """Load Streem API credentials from .env file.

    Returns:
        tuple[str, str]: Tuple containing username and password.
    """
    load_dotenv()
    username = os.getenv(STREEM_USERNAME)
    password = os.getenv(STREEM_PASSWORD)
    if not username or not password:
        console.print(f"[bold red]Error:[/bold red] {STREEM_USERNAME} and {STREEM_PASSWORD} must be set in .env file.")
        raise typer.Exit(code=1)
    return username, password


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
        Resolution,
        typer.Option(
            "--resolution",
            "-r",
            help="Time resolution for forecast",
            autocompletion=lambda: [r.value for r in Resolution],
        ),
    ] = Resolution.H1,
) -> None:
    """Fetch and display forecast data from Streem Energy API."""
    # Set start and end times for the specified date, timezone-aware
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=PARIS_TZ)
    end_date = date.replace(hour=23, minute=59, second=0, microsecond=0, tzinfo=PARIS_TZ)

    # Load credentials
    username, password = load_credentials()

    # Create API client
    api = StreemAPI(username, password)

    try:
        forecast_data = api.get_forecast(
            name=name,
            forecast_type=ForecastType.GENERATION,
            start_date=start_date,
            end_date=end_date,
            resolution=resolution,
        )
        # Pretty print the response
        console.print("\n[bold green]Forecast Data:[/bold green]")
        pprint(forecast_data, console=console)
    except StreemAPIError as e:
        console.print(f"[bold red]Error connecting to Streem API:[/bold red] {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    typer.run(main)
