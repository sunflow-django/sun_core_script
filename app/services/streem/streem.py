import os
import sys
from datetime import datetime
from typing import Annotated

import typer
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.table import Table

from app.services.streem.api import StreemAPI
from app.services.streem.schema import AlertList
from app.services.streem.schema import ForecastType
from app.services.streem.schema import Installation
from app.services.streem.schema import InstallationList
from app.services.streem.schema import LoadCurve
from app.services.streem.schema import Resolution


# Configure logging
logger.remove()
logger.add(sys.stderr, level="DEBUG")

console = Console()

app = typer.Typer(help="Connect to Streem Energy API", pretty_exceptions_show_locals=True)


def print_installation_list(installations: InstallationList) -> None:
    """Print a nicely formatted table for a list of installations."""
    console = Console()
    table = Table(title="Installations", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Client ID", style="magenta")
    table.add_column("Energy Type", style="green")
    table.add_column("Latitude", style="yellow")
    table.add_column("Longitude", style="yellow")

    for installation in installations.root:
        table.add_row(
            installation.name,
            installation.client_id or "N/A",
            installation.energy.value,
            str(installation.latitude) if installation.latitude is not None else "N/A",
            str(installation.longitude) if installation.longitude is not None else "N/A",
        )

    console.print(table)


def print_installation_detail(installation: Installation) -> None:
    """Print a nicely formatted table for a single installation's details."""
    console = Console()
    table = Table(title=f"Details for {installation.name}", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="green")

    table.add_row("Name", installation.name)
    table.add_row("Client ID", installation.client_id or "N/A")
    table.add_row("Energy Type", installation.energy.value)
    table.add_row("External Ref", installation.external_ref or "N/A")
    table.add_row("Latitude", str(installation.latitude) if installation.latitude is not None else "N/A")
    table.add_row("Longitude", str(installation.longitude) if installation.longitude is not None else "N/A")

    console.print(table)


def print_alert_list(alerts: AlertList, title: str = "Alerts") -> None:
    """Print a nicely formatted table for a list of alerts."""
    console = Console()
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Installation", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Created At", style="green")
    table.add_column("Closed At", style="yellow")

    for alert in alerts.root:
        closed_at = alert.closed_at.isoformat() if alert.closed_at else "Open"
        table.add_row(
            alert.installation_name,
            alert.type,
            alert.created_at.isoformat(),
            closed_at,
        )

    console.print(table)


def load_credentials() -> tuple[str, str]:
    """Load Streem API credentials from .env file."""
    load_dotenv()
    username = os.getenv("STREEM_USERNAME")
    password = os.getenv("STREEM_PASSWORD")
    if not username or not password:
        console.print("[bold red]Error:[/bold red] STREEM_USERNAME and STREEM_PASSWORD must be set in .env file.")
        raise typer.Exit(code=1)
    return username, password


@app.callback()
def main(
    context: typer.Context,
    username: Annotated[
        str | None,
        typer.Option("--username", "-u", envvar="STREEM_USERNAME", help="Streem username"),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option("--password", "-p", envvar="STREEM_PASSWORD", help="Streem password"),
    ] = None,
) -> None:
    """Initialize the Streem API client with credentials."""
    if not username or not password:
        username, password = load_credentials()
    try:
        api = StreemAPI(username, password)
        context.obj = {"api": api}
    except Exception as e:
        console.print(f"[bold red]Authentication failed:[/bold red] {e}")
        raise typer.Exit(code=1) from e


@app.command("list")
@app.command("l")
def get_installations(context: typer.Context) -> None:
    """List all installations."""
    api: StreemAPI = context.obj["api"]
    installations: InstallationList = api.get_installations()
    if installations is None:
        console.print("[bold red]Error:[/bold red] Failed to retrieve installations.")
        return

    print_installation_list(installations)


@app.command("detail")
@app.command("d")
def get_installation_detail(
    context: typer.Context,
    name: Annotated[str, typer.Argument(help="Installation name")],
) -> None:
    """Get details for a specific installation."""
    api: StreemAPI = context.obj["api"]
    installation: Installation = api.get_installation_detail(name)
    if installation is None:
        console.print(f"[bold red]Error:[/bold red] Failed to retrieve details for installation '{name}'.")
        return

    console.print("[bold green]Installation Details:[/bold green]")
    print_installation_detail(installation)


@app.command("alerts")
@app.command("a")
def get_installation_alerts(
    context: typer.Context,
    name: Annotated[str, typer.Argument(help="Installation name")],
    start_date: Annotated[
        datetime | None,
        typer.Option(
            "--start-date",
            "-s",
            formats=["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"],
            help="Start date (ISO format with TZ)",
        ),
    ] = None,
    end_date: Annotated[
        datetime | None,
        typer.Option(
            "--end-date",
            "-e",
            formats=["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"],
            help="End date (ISO format with TZ)",
        ),
    ] = None,
    *,
    all_alerts: Annotated[bool, typer.Option("--all", help="Get all alerts (default: True)")] = True,
) -> None:
    """Get alerts for a specific installation."""
    api: StreemAPI = context.obj["api"]
    alerts: AlertList = api.get_installation_alerts(name, start_date, end_date, all_alerts=all_alerts)
    if alerts is None:
        console.print(f"[bold red]Error:[/bold red] Failed to retrieve alerts for installation '{name}'.")
        return

    print_alert_list(alerts)
$$$ il faut start et end si no pas bon

@app.command("forecast")
@app.command("f")
def get_installation_forecast(  # noqa: PLR0913
    context: typer.Context,
    name: Annotated[str, typer.Argument(help="Installation name")],
    resolution: Annotated[Resolution, typer.Option("--resolution", "-r", help="Time resolution")] = Resolution.H1,
    forecast_type: Annotated[
        ForecastType,
        typer.Option("--type", "-t", help="Forecast type"),
    ] = ForecastType.DISPATCH_PROGRAM,
    start_date: Annotated[
        datetime | None,
        typer.Option("--start-date", "-s", formats=["%Y-%m-%dT%H:%M:%S%z"], help="Start date (ISO format with TZ)"),
    ] = None,
    end_date: Annotated[
        datetime | None,
        typer.Option("--end-date", "-e", formats=["%Y-%m-%dT%H:%M:%S%z"], help="End date (ISO format with TZ)"),
    ] = None,
) -> None:
    """Get forecast data for a specific installation."""
    api: StreemAPI = context.obj["api"]
    forecast: LoadCurve = api.get_installation_forecast(name, resolution, forecast_type, start_date, end_date)
    if forecast is None:
        console.print(f"[bold red]Error:[/bold red] Failed to retrieve forecast for installation '{name}'.")
        return

    table = Table(title=f"Forecast for {name}")
    table.add_column("Date", style="cyan")
    table.add_column("Value", style="magenta")

    for point in forecast.root:
        table.add_row(
            point.date.isoformat(),
            str(point.data) if point.data is not None else "N/A",
        )
    console.print(table)


@app.command("all_alerts")
def get_all_alerts(
    context: typer.Context,
    start_date: Annotated[
        datetime | None,
        typer.Option("--start-date", "-s", formats=["%Y-%m-%dT%H:%M:%S%z"], help="Start date (ISO format with TZ)"),
    ] = None,
    end_date: Annotated[
        datetime | None,
        typer.Option("--end-date", "-e", formats=["%Y-%m-%dT%H:%M:%S%z"], help="End date (ISO format with TZ)"),
    ] = None,
    *,
    all_alerts: Annotated[bool, typer.Option("--all", help="Get all alerts (default: True)")] = True,
) -> None:
    """Get all alerts with optional filters."""
    api: StreemAPI = context.obj["api"]
    alerts: AlertList = api.get_alerts(start_date, end_date, all_alerts=all_alerts)
    if alerts is None:
        console.print("[bold red]Error:[/bold red] Failed to retrieve alerts.")
        return

    table = Table(title="All Alerts")
    table.add_column("Installation", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Created At", style="green")
    table.add_column("Closed At", style="yellow")

    for alert in alerts.root:
        closed_at = alert.closed_at.isoformat() if alert.closed_at else "Open"
        table.add_row(
            alert.installation_name,
            alert.type,
            alert.created_at.isoformat(),
            closed_at,
        )
    console.print(table)


if __name__ == "__main__":
    app()
