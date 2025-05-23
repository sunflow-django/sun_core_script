import sys
from datetime import datetime
from datetime import timedelta

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from app.constants.time_zones import PARIS_TZ
from app.core.config import settings
from app.services.nordpool.api_manager import AuctionApiManager
from app.services.nordpool.schema import OrderStateType


# Configure loggin
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="WARNING")  # Add handler for WARNING and above

# Default values
DEFAULT_PRODUCT_ID = "CWE_H_DA_1"
DEFAULT_AREA_CODE = "FR"
DEFAULT_PORTFOLIO = "FR-SUNFLOW"


def get_default_date() -> str:
    """Return tomorrow's date in YYYYMMDD format"""
    tomorrow = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
    return tomorrow.strftime("%Y%m%d")


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


def print_table(orders: list) -> None:
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


app = typer.Typer()


@app.command()
def list_orders(  # noqa: PLR0913
    state: OrderStateType | None = typer.Option(
        None,
        "--state",
        "-s",
        help="Filter by order state. Possible values: New, Accepted, Cancelled, UserAccepted, ResultsPublished, None",
    ),
    order_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by order type. Possible values: Curve, Block",
        autocompletion=lambda: ["Curve", "Block"],
    ),
    portfolio: str = typer.Option(DEFAULT_PORTFOLIO, "--portfolio", "-p", help="Portfolio to use"),
    area_code: str = typer.Option(DEFAULT_AREA_CODE, "--area-code", "-a", help="Area code to use"),
    product_id: str = typer.Option(DEFAULT_PRODUCT_ID, "--product-id", help="Product ID to use"),
    date: str = typer.Option(
        get_default_date,
        "--date",
        "-d",
        help="Auction date (i.e. delivery day) in YYYYMMDD format",  # TODO understand why an order place for D+1 appears in D+1 *and* D+2  # noqa: E501
    ),
) -> None:
    """Fetch and display Nordpool orders with optional filters"""
    # Initialize API manager
    norpool_manager = AuctionApiManager(
        username=settings.NORDPOOL_USERNAME,
        password=settings.NORDPOOL_PASSWORD,
        prod=False,
    )

    # Construct auction_id
    auction_id = f"{product_id}-{date}"

    # Fetch orders from API
    orders_obj = norpool_manager.get_order(
        auction_id=auction_id,
        portfolios=[portfolio],
        area_codes=[area_code],
    )

    # Format orders in a list
    orders_list = AuctionApiManager.list_existing_orders(orders_obj)

    # Apply filters if provided
    if state:
        orders_list = [order for order in orders_list if order["state"] == state]
    if order_type:
        orders_list = [order for order in orders_list if order["type"] == order_type]

    # Display results
    print_table(orders_list)


if __name__ == "__main__":
    app()
