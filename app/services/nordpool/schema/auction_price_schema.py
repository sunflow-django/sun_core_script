from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.services.nordpool.schema.base_schema import ContractPrice


class AuctionPrice(BaseModel):
    """Schema for auction price response data.

    Attributes:
        auction: The auction identifier.
        auction_delivery_start: The datetime when auction delivery starts.
        auction_delivery_end: The datetime when auction delivery ends.
        contracts: List of contract prices.

    Returns:
        AuctionPrice: The validated auction price instance.
    """

    auction: str | None = None
    auction_delivery_start: datetime = Field(alias="auctionDeliveryStart")
    auction_delivery_end: datetime = Field(alias="auctionDeliveryEnd")
    contracts: list[ContractPrice] | None = None
