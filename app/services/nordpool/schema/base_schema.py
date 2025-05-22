# TODO convert field to annotated.
# TODO compare to autogenerate model
# TODO add  extra="forbid" in all modules and test for it
from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class ApprovalSource(str, Enum):
    """Enum for approval source types."""

    AUTOMATIC = "Automatic"
    OPERATOR = "Operator"
    MEMBER = "Member"


class AuctionStateType(str, Enum):
    """Enum for auction state types."""

    OPEN = "Open"
    CLOSED = "Closed"
    RESULTS_PUBLISHED = "ResultsPublished"
    CANCELLED = "Cancelled"


class OrderType(BaseModel, extra="forbid"):
    """Schema for order type."""

    id: int = Field(...)
    name: str | None = Field(default=None, min_length=0)


class Currency(BaseModel, extra="forbid"):
    """Schema for currency details."""

    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=0)
    min_price: float = Field(..., alias="minPrice")
    max_price: float = Field(..., alias="maxPrice")


class Contract(BaseModel, extra="forbid"):
    """Schema for contract details."""

    id: str | None = Field(default=None, min_length=0)
    delivery_start: datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime = Field(..., alias="deliveryEnd")


class AreaContractGroup(BaseModel, extra="forbid"):
    """Schema for area contract group."""

    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    contracts: list[Contract] | None = Field(default=None)


class PortfolioArea(BaseModel, extra="forbid"):
    """Schema for portfolio area details."""

    code: str | None = Field(default=None, min_length=0)
    name: str | None = Field(default=None, min_length=0)
    eic_code: str | None = Field(default=None, alias="eicCode", min_length=0)
    curve_min_volume_limit: float = Field(..., alias="curveMinVolumeLimit")
    curve_max_volume_limit: float = Field(..., alias="curveMaxVolumeLimit")
    auction_trading_resolution: int = Field(..., alias="auctionTradingResolution")


class AuctionPortfolio(BaseModel, extra="forbid"):
    """Schema for auction portfolio details."""

    name: str | None = Field(default=None, min_length=0)
    id: str | None = Field(default=None, min_length=0)
    currency: str | None = Field(default=None, min_length=0)
    company_id: str | None = Field(default=None, alias="companyId", min_length=0)
    company_name: str | None = Field(default=None, alias="companyName", min_length=0)
    permission: str | None = Field(default=None, min_length=0)
    areas: list[PortfolioArea] | None = Field(default=None)


class ContractNetVolume(BaseModel, extra="forbid"):
    """Schema for contract net volume."""

    net_volume: float | None = Field(default=None, alias="netVolume")
    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    delivery_start: datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime = Field(..., alias="deliveryEnd")


class AreaNetVolume(BaseModel, extra="forbid"):
    """Schema for area net volume."""

    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    net_volumes: list[ContractNetVolume] | None = Field(default=None, alias="netVolumes")


class PortfolioNetVolume(BaseModel, extra="forbid"):
    """Schema for portfolio net volume."""

    portfolio: str | None = Field(default=None, min_length=0)
    company_name: str | None = Field(default=None, alias="companyName", min_length=0)
    area_net_volumes: list[AreaNetVolume] | None = Field(default=None, alias="areaNetVolumes")


class CurrencyPrice(BaseModel, extra="forbid"):
    """Schema for currency price details."""

    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=0)
    market_price: float | None = Field(default=None, alias="marketPrice")
    status: str = Field(...)


class AreaPrice(BaseModel, extra="forbid"):
    """Schema for area price details."""

    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    prices: list[CurrencyPrice] | None = Field(default=None)


class ContractPrice(BaseModel, extra="forbid"):
    """Schema for contract price details."""

    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    delivery_start: datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime = Field(..., alias="deliveryEnd")
    areas: list[AreaPrice] | None = Field(default=None)


class BlockPeriod(BaseModel, extra="forbid"):
    """Schema for block period details."""

    contract_id: Annotated[str, Field(alias="contractId", min_length=1)]
    volume: float = Field(...)


class Block(BaseModel, extra="forbid"):
    """Schema for block details."""

    name: str = Field(..., min_length=1)
    price: float = Field(...)
    minimum_acceptance_ratio: float = Field(..., alias="minimumAcceptanceRatio")
    linked_to: str | None = Field(default=None, alias="linkedTo", min_length=0)
    exclusive_group: str | None = Field(default=None, alias="exclusiveGroup", min_length=0)
    periods: list[BlockPeriod] = Field(...)
    is_spread_block: bool = Field(..., alias="isSpreadBlock")


class BlockResponse(Block):
    """Schema for block response details, extending Block."""

    modifier: str | None = Field(default=None, min_length=0)
    state: str = Field(...)


class Order(BaseModel, extra="forbid"):
    """Represents order details for the NPS Auction API."""

    auction_id: str = Field(..., alias="auctionId", min_length=1)
    portfolio: str = Field(..., min_length=1)
    area_code: str = Field(..., alias="areaCode", min_length=1)
    comment: str | None = Field(default=None, max_length=255, min_length=0)


class OrderStateType(str, Enum):
    """Enum for order state types."""

    NEW = "New"
    ACCEPTED = "Accepted"
    CANCELLED = "Cancelled"
    USER_ACCEPTED = "UserAccepted"
    RESULTS_PUBLISHED = "ResultsPublished"
    NONE = "None"


class OrderResponse(BaseModel, extra="forbid"):
    """Schema for order response details."""

    order_id: UUID = Field(..., alias="orderId")
    auction_id: str | None = Field(default=None, alias="auctionId", min_length=0)
    company_name: str | None = Field(default=None, alias="companyName", min_length=0)
    portfolio: str | None = Field(default=None, min_length=0)
    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    modifier: str | None = Field(default=None, min_length=0)
    modified: datetime = Field(...)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=0)
    comment: str | None = Field(default=None, min_length=0)
    resolution_seconds: int = Field(..., alias="resolutionSeconds")


class TradeSide(str, Enum):
    """Enum for trade side types."""

    BUY = "Buy"
    SELL = "Sell"


class AuctionResultState(str, Enum):
    """Enum for auction result state types."""

    NOT_AVAILABLE = "NotAvailable"
    PRELIMINARY_RESULTS = "PreliminaryResults"
    FINAL = "Final"
    INITIAL_PRICE = "InitialPrice"


class Trade(BaseModel, extra="forbid"):
    """Schema for trade details."""

    trade_id: str | None = Field(default=None, alias="tradeId", min_length=0)
    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    delivery_start: datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime = Field(..., alias="deliveryEnd")
    volume: float = Field(...)
    price: float = Field(...)
    side: TradeSide = Field(...)
    status: AuctionResultState = Field(...)


class CurvePoint(BaseModel, extra="forbid"):
    """Schema for curve point details."""

    price: float = Field(...)
    volume: float = Field(...)


class CurveOrder(BaseModel, extra="forbid"):
    """Schema for curve details."""

    contract_id: str = Field(..., alias="contractId", min_length=1)
    curve_points: list[CurvePoint] = Field(..., alias="curvePoints")


class CurveOrder(Order, extra="forbid"):
    """Represents order details for the NPS Crurve Order Auction API."""

    curves: list[CurveOrder]


class ValidatedCurve(BaseModel, extra="forbid"):
    """Schema for validated curve details."""

    id: UUID = Field(...)
    time_step: int = Field(..., alias="timeStep")
    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    is_valid: bool = Field(..., alias="isValid")
    validation_message: str | None = Field(default=None, alias="validationMessage", min_length=0)


class OrderResultType(str, Enum):
    """Enum for order result types."""

    CURVE = "Curve"
    BLOCK = "Block"
    ROUNDING_RESIDUAL = "RoundingResidual"


class OrderApprovalState(str, Enum):
    """Enum for order approval state types."""

    UNDEFINED = "Undefined"
    APPROVED = "Approved"
    NOT_APPROVED = "NotApproved"
