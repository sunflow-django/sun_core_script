# ruff: noqa: T201
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from loguru import logger
from rich import print  # noqa: A004
from rich.console import Console
from rich.table import Table

from app.services.nordpool.api import AuctionAPI
from app.services.nordpool.schema import CombinedOrdersResponse
from app.services.nordpool.schema import CurveOrder
from app.services.nordpool.schema import CurveOrderPatch
from app.services.nordpool.schema import CurveOrderResponse
from app.services.nordpool.schema import OrderFormat
from app.services.nordpool.schema import OrderStateType
from app.services.nordpool.utils import tomorrow_str


# Configure loggin
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="WARNING")  # Add handler for WARNING and above

# Default values
DEFAULT_PRODUCT_ID = "CWE_H_DA_1"
DEFAULT_AREA_CODE = "FR"
DEFAULT_PORTFOLIO = "FR-SUNFLOW"


# Color mappings for State and Type columns
STATE_COLORS = {
    "New": "green",
    "Accepted": "green1",
    "Cancelled": "orange3",
    "UserAccepted": "green3",
    "ResultsPublished": "blue",
    "None": "red",
}

TYPE_COLORS = {"Curve": "yellow", "Block": "cyan"}


def print_order_table(orders: list) -> None:
    """Print order list with colored State and Type columns"""
    table = Table(title="Orders")
    table.add_column("Order ID", style="cyan")
    table.add_column("Auction ID", style="magenta")
    table.add_column("State")
    table.add_column("Modified")
    table.add_column("Type")

    for order in orders:
        state = order["state"]
        order_type = order["type"]
        state_color = STATE_COLORS.get(state, "white")
        type_color = TYPE_COLORS.get(order_type, "white")

        table.add_row(
            order["order_id"],
            order["auction_id"],
            f"[{state_color}]{state}[/{state_color}]",
            order["modified"],
            f"[{type_color}]{order_type}[/{type_color}]",
        )

    Console().print(table)


app = typer.Typer(help="Manage energy trades on the Nordpool platform", pretty_exceptions_show_locals=False)


def complete_uuid(incomplete: str) -> str:
    """UUID autocompletion"""  # TODO add google doc string
    uuids = ["550e8400-e29b-41d4-a716-446655440000", "123e4567-e89b-12d3-a456-426614174000"]
    for uuid_str in uuids:
        if uuid_str.startswith(incomplete):
            yield uuid_str


@app.callback()
def main(
    context: typer.Context,
    username: Annotated[
        str | None,
        typer.Option("--username", "-u", envvar="NORDPOOL_USERNAME", help="Nordpool username"),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option(
            "--password",
            "-p",
            envvar="NORDPOOL_PASSWORD",
            prompt=True,
            hide_input=True,
            help="Nordpool password",
        ),
    ] = None,
    *,
    prod: Annotated[bool, typer.Option("--prod/--dev", help="Use production environment (default: dev)")] = False,
) -> None:
    """Initialize global options for Nordpool commands."""
    # Initialize API
    api = AuctionAPI(
        username=username,
        password=password,
        prod=prod,
    )

    # Initialize context
    context.obj = {
        "username": username,
        "password": password,
        "prod": prod,
        "api": api,
    }


@app.command("list")
@app.command("l")
def get_orders(  # noqa: PLR0913
    context: typer.Context,
    date: Annotated[
        datetime,
        typer.Option(
            "--date",
            "-d",
            formats=["%Y%m%d"],
            # TODO understand why an order place for D+1 appears in D+1 *and* D+2
            help="Auction date (i.e. delivery day) in YYYYMMDD format",
        ),
    ] = tomorrow_str(),
    state: Annotated[
        OrderStateType | None,
        typer.Option(
            "--state",
            "-s",
            help="Filter by state. Possible values: New, Accepted, Cancelled, UserAccepted, ResultsPublished, None",
        ),
    ] = None,
    order_format: Annotated[
        OrderFormat | None,
        typer.Option("--type", "-t", help="Filter by order type. Possible values: Curve, Block"),
    ] = None,
    portfolio: Annotated[
        str,
        typer.Option("--portfolio", "-p", help="Portfolio to use"),
    ] = DEFAULT_PORTFOLIO,
    area_code: Annotated[
        str,
        typer.Option("--area-code", "-a", help="Area code to use"),
    ] = DEFAULT_AREA_CODE,
    product_id: Annotated[
        str,
        typer.Option("--product-id", "-i", help="Product ID to use"),
    ] = DEFAULT_PRODUCT_ID,
) -> None:
    """
    List orders for the given date (YYYYMMDD, default: tomorrow, Paris time).
    """
    api: AuctionAPI = context.obj["api"]

    # Construct auction_id
    auction_id = f"{product_id}-{date.strftime('%Y%m%d')}"

    # Fetch orders from API
    response: CombinedOrdersResponse = api.get_orders(
        auction_id=auction_id,
        portfolios=[portfolio],
        area_codes=[area_code],
    )
    if response is None:
        print(f"No order found for auction_id: {auction_id}, portfolios: {portfolio}, area_codes={area_code}.")
        return

    # Format orders in a list
    orders_list = response.list_orders_details()

    # Apply filters if provided
    if state:
        orders_list = [order for order in orders_list if order["state"] == state]
    if order_format:
        orders_list = [order for order in orders_list if order["type"] == order_format]

    # Display results
    print_order_table(orders_list)


@app.command("detail")
@app.command("d")
def get_curve_order(
    context: typer.Context,
    uuid: Annotated[uuid.UUID, typer.Argument(autocompletion=complete_uuid, help="UUID of the order")],
    *,
    save: Annotated[bool, typer.Option("--save", "-s", help="Save to a file")] = False,
) -> None:
    """
    Detail the order with the given UUID.
    """
    api: AuctionAPI = context.obj["api"]

    # Fetch orders from API
    response: CurveOrderResponse = api.get_curve_order(order_id=uuid)
    if response is None:
        print(f"No order found for auction_id: {uuid}.")
        return
    print(response)


@app.command("update")
def patch_curve_order(
    context: typer.Context,
    uuid: Annotated[uuid.UUID, typer.Argument(autocompletion=complete_uuid, help="UUID of the order")],
    filename: Annotated[Path, typer.Argument(help="Filename to read the curve order from")],
    *,
    dry: Annotated[bool, typer.Option("--dry", "-d", help="Only validate the file format")] = False,
) -> None:
    """
    Update an existing order for the given date from the file content.
    """
    # Check if filename exists and is a file
    if not filename.exists() or not filename.is_file():
        print(f"[red]Error[/red]: '{filename}' does not exist or is not a file.")
        raise typer.Exit(code=1)

    # Read and validate file content
    try:
        with filename.open("r") as f:
            patch_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[red]Error[/red]: invalid JSON in '{filename}'.")
        print(e)
        raise typer.Exit(code=1) from e
    try:
        patch = CurveOrderPatch(**patch_data)
    except (TypeError, ValueError) as e:
        print(f"[red]Error[/red]: Not a valid CurveOrderPatch in '{filename}'.")
        raise typer.Exit(code=1) from e

    # Dry run
    if dry:
        print("File content [green]validated[/green] successfully (dry run).")
        raise typer.Exit

    # Fetch orders from API
    api: AuctionAPI = context.obj["api"]
    response: CurveOrderResponse = api.patch_curve_order(order_id=uuid, patch_data=patch)
    if response is None:
        msg = f"[red]Error[/red]: Order {uuid} could not be patched from {filename}."
        print(msg)
        raise typer.Exit(code=1)

    print(patch)


@app.command("post")
@app.command("p")
def post_curve_order(
    context: typer.Context,
    filename: Annotated[Path, typer.Argument(help="Filename to read the curve order from")],
    date: Annotated[
        datetime,
        typer.Option(
            "--date",
            "-d",
            formats=["%Y%m%d"],
            help="Auction date (i.e. delivery day) in YYYYMMDD format",
        ),
    ] = tomorrow_str(),
    *,
    dry: Annotated[bool, typer.Option("--dry", "-d", help="Only validate the file format")] = False,
) -> None:
    """
    Post a new curve order for the given date from the file content.
    """
    # Check if filename exists and is a file
    if not filename.exists() or not filename.is_file():
        print(f"[red]Error[/red]: '{filename}' does not exist or is not a file.")
        raise typer.Exit(code=1)

    # Read and validate file content
    try:
        with filename.open("r") as f:
            order_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[red]Error[/red]: invalid JSON in '{filename}'.")
        print(e)
        raise typer.Exit(code=1) from e
    try:
        order = CurveOrder(**order_data)
    except (TypeError, ValueError) as e:
        print(f"[red]Error[/red]: Not a valid CurveOrder in'{filename}'.")
        raise typer.Exit(code=1) from e

    # Dry run
    if dry:
        print("File content [green]validated[/green] successfully (dry run).")
        raise typer.Exit

    # Fetch orders from API
    api: AuctionAPI = context.obj["api"]
    response: CurveOrderResponse = api.post_curve_order(order)
    if response is None:
        msg = f"[red]Error[/red]: Order could not be posted from {filename} for date {date.strftime('%Y%m%d')}"
        print(msg)
        raise typer.Exit(code=1)

    print(order)


@app.command("zero")
@app.command("z")
def zero_order(
    context: typer.Context,
    uuid: Annotated[uuid.UUID, typer.Argument(autocompletion=complete_uuid, help="UUID of the order")],
) -> None:
    """
    Zero out the order with the given UUID.
    """
    # Fetch orders from API
    api: AuctionAPI = context.obj["api"]
    order: CurveOrderResponse = api.get_curve_order(order_id=uuid)
    if order is None:
        msg = f"[red]Error[/red]: Volumes could not be zero out in order {uuid}."
        raise typer.Exit(code=1)
    patch = order.to_curve_order_patch()
    zero_patch= patch.zero_volumes()
    order: CurveOrderResponse = api.patch_curve_order(order_id=uuid, patch_data=zero_patch)
    if order is None:
        msg = f"[red]Error[/red]: Volumes could not be zero out in oOrder {uuid}."
        print(msg)
        raise typer.Exit(code=1)

    print(order)


if __name__ == "__main__":
    load_dotenv(".env")
    app()
