from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.services.nordpool.schema.base_schema import AuctionPortfolio
from app.services.nordpool.schema.base_schema import AuctionStateType
from app.services.nordpool.schema.base_schema import Contract
from app.services.nordpool.schema.base_schema import Currency
from app.services.nordpool.schema.base_schema import OrderType


class AuctionResponse(BaseModel):
    """Schema for auction response data.

    Attributes:
        id: The unique identifier for the auction.
        name: The name of the auction.
        state: The current state of the auction.
        close_for_bidding: The datetime when bidding closes.
        delivery_start: The datetime when delivery starts.
        delivery_end: The datetime when delivery ends.
        available_order_types: List of available order types.
        currencies: List of supported currencies.
        contracts: List of contracts associated with the auction.
        portfolios: List of portfolios associated with the auction.

    Returns:
        AuctionResponse: The validated auction response instance.
    """

    id: str | None = None
    name: str | None = None
    state: AuctionStateType
    close_for_bidding: datetime = Field(alias="closeForBidding")
    delivery_start: datetime = Field(alias="deliveryStart")
    delivery_end: datetime = Field(alias="deliveryEnd")
    available_order_types: list[OrderType] | None = Field(
        default=None,
        alias="availableOrderTypes",
    )
    currencies: list[Currency] | None = None
    contracts: list[Contract] | None = None
    portfolios: list[AuctionPortfolio] | None = None
