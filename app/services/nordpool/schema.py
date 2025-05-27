from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ApprovalSource(str, Enum):
    AUTOMATIC = "Automatic"
    OPERATOR = "Operator"
    MEMBER = "Member"


class AuctionResultState(str, Enum):
    NOT_AVAILABLE = "NotAvailable"
    PRELIMINARY_RESULTS = "PreliminaryResults"
    FINAL = "Final"
    INITIAL_PRICE = "InitialPrice"


class AuctionStateType(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    RESULTS_PUBLISHED = "ResultsPublished"
    CANCELLED = "Cancelled"


class BlockPeriod(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    contract_id: Annotated[str, Field(alias="contractId", min_length=1)]
    volume: float


class Contract(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None


class ContractNetVolume(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    net_volume: Annotated[float | None, Field(alias="netVolume")] = None
    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None


class Currency(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    min_price: Annotated[float | None, Field(alias="minPrice")] = None
    max_price: Annotated[float | None, Field(alias="maxPrice")] = None


class CurrencyPrice(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    market_price: Annotated[float | None, Field(alias="marketPrice")] = None
    status: AuctionResultState | None = None


class CurvePoint(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    price: float
    volume: float


class Order(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    auction_id: Annotated[str, Field(alias="auctionId", min_length=1)]
    portfolio: Annotated[str, Field(min_length=1)]
    area_code: Annotated[str, Field(alias="areaCode", min_length=1)]
    comment: Annotated[str | None, Field(max_length=255, min_length=0)] = None


class OrderApprovalState(str, Enum):
    UNDEFINED = "Undefined"
    APPROVED = "Approved"
    NOT_APPROVED = "NotApproved"


class OrderResponse(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    order_id: Annotated[UUID | None, Field(alias="orderId")] = None
    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    portfolio: str | None = None
    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    modifier: str | None = None
    modified: datetime | None = None
    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    comment: str | None = None
    resolution_seconds: Annotated[int | None, Field(alias="resolutionSeconds")] = None


class OrderResultType(str, Enum):
    CURVE = "Curve"
    BLOCK = "Block"
    ROUNDING_RESIDUAL = "RoundingResidual"


class OrderFormat(str, Enum):
    CURVE = "Curve"
    BLOCK = "Block"


class OrderStateType(str, Enum):
    NEW = "New"
    ACCEPTED = "Accepted"
    CANCELLED = "Cancelled"
    USER_ACCEPTED = "UserAccepted"
    RESULTS_PUBLISHED = "ResultsPublished"
    NONE = "None"


class OrderType(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    name: str | None = None


class PortfolioArea(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    code: str | None = None
    name: str | None = None
    eic_code: Annotated[str | None, Field(alias="eicCode")] = None
    curve_min_volume_limit: Annotated[float | None, Field(alias="curveMinVolumeLimit")] = None
    curve_max_volume_limit: Annotated[float | None, Field(alias="curveMaxVolumeLimit")] = None
    auction_trading_resolution: Annotated[int | None, Field(alias="auctionTradingResolution")] = None


class ProblemDetails(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


class TradeSide(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


class ValidatedCurve(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID | None = None
    time_step: Annotated[int | None, Field(alias="timeStep")] = None
    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    is_valid: Annotated[bool | None, Field(alias="isValid")] = None
    validation_message: Annotated[str | None, Field(alias="validationMessage")] = None


class AreaContractGroup(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    contracts: list[Contract] | None = None


class AreaNetVolume(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    net_volumes: Annotated[list[ContractNetVolume] | None, Field(alias="netVolumes")] = None


class AreaPrice(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    prices: list[CurrencyPrice] | None = None


class AuctionPortfolio(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    id: str | None = None
    currency: str | None = None
    company_id: Annotated[str | None, Field(alias="companyId")] = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    permission: str | None = None
    areas: list[PortfolioArea] | None = None


class AuctionResponse(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    name: str | None = None
    state: AuctionStateType | None = None
    close_for_bidding: Annotated[datetime | None, Field(alias="closeForBidding")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    available_order_types: Annotated[list[OrderType] | None, Field(alias="availableOrderTypes")] = None
    currencies: list[Currency] | None = None
    contracts: list[Contract] | None = None
    portfolios: list[AuctionPortfolio] | None = None


class Block(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    name: Annotated[str, Field(min_length=1)]
    price: float
    minimum_acceptance_ratio: Annotated[float, Field(alias="minimumAcceptanceRatio")]
    linked_to: Annotated[str | None, Field(alias="linkedTo")] = None
    exclusive_group: Annotated[str | None, Field(alias="exclusiveGroup")] = None
    periods: list[BlockPeriod]
    is_spread_block: Annotated[bool | None, Field(alias="isSpreadBlock")] = None


class BlockResponse(Block, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    modifier: str | None = None
    state: OrderStateType | None = None


class ContractPrice(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    areas: list[AreaPrice] | None = None


class Curve(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    contract_id: Annotated[str, Field(alias="contractId", min_length=1)]
    curve_points: Annotated[list[CurvePoint], Field(alias="curvePoints")]


class CurveOrder(Order, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    curves: list[Curve]

    def to_patch(self) -> "CurveOrderPatch":
        """
        Convert self to a CurveOrderPatch.

        Args:
            curve_order: CurveOrder object to convert

        Returns:
            CurveOrderPatch with the same curves and comment as the input CurveOrder
        """
        return CurveOrderPatch(curves=self.curves, comment=self.comment)


class CurveOrderPatch(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    curves: list[Curve] | None = None
    comment: Annotated[str | None, Field(max_length=255, min_length=0)] = None

    def sort(self) -> None:
        """Sort the curves list in-place by increasing contract_id."""
        if self.curves is not None:
            self.curves.sort(key=lambda curve: curve.contract_id)

    def sorted(self) -> "CurveOrderPatch":
        """Return a new instance with curves sorted by increasing contract_id."""

        new_instance = deepcopy(self)
        if new_instance.curves is not None:
            new_instance.curves = sorted(new_instance.curves, key=lambda curve: curve.contract_id)
        return new_instance

    def zero_volumes(self) -> "CurveOrderPatch":
        """Return a new instance with all volumes set to 0.0."""
        new_instance = deepcopy(self)
        if new_instance.curves is not None:
            for curve in new_instance.curves:
                for point in curve.curve_points:
                    point.volume = 0.0
        return new_instance


class CurveOrderResponse(OrderResponse, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    state: OrderStateType | None = None
    curves: list[Curve] | None = None

    def sort(self) -> None:
        """Sort the curves list in-place by increasing contract_id."""
        if self.curves is not None:
            self.curves.sort(key=lambda curve: curve.contract_id)

    def sorted(self) -> "CurveOrderResponse":
        """Return a new instance with curves sorted by increasing contract_id."""

        new_instance = deepcopy(self)
        if new_instance.curves is not None:
            new_instance.curves = sorted(new_instance.curves, key=lambda curve: curve.contract_id)
        return new_instance

    def to_curve_order_patch(self) -> CurveOrderPatch:
        """Extract a CurveOrderPatch from this CurveOrderResponse."""
        return CurveOrderPatch(curves=deepcopy(self.curves) if self.curves is not None else None, comment=self.comment)


class PortfolioNetVolume(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    portfolio: str | None = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    area_net_volumes: Annotated[list[AreaNetVolume] | None, Field(alias="areaNetVolumes")] = None


class PortfolioVolumeResponse(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    portfolio_net_volumes: Annotated[list[PortfolioNetVolume] | None, Field(alias="portfolioNetVolumes")] = None


class ReasonabilityResultsInfo(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    portfolio: str | None = None
    area: str | None = None
    order_approval_state: Annotated[OrderApprovalState | None, Field(alias="orderApprovalState")] = None
    curves: list[ValidatedCurve] | None = None
    reference_day: Annotated[str | None, Field(alias="referenceDay")] = None
    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    order_id: Annotated[UUID | None, Field(alias="orderId")] = None
    approval_modifier: Annotated[str | None, Field(alias="approvalModifier")] = None
    approval_source: Annotated[ApprovalSource | None, Field(alias="approvalSource")] = None

    def extract_invalid_curves(self) -> list[ValidatedCurve]:
        """
        Return a list of curves where is_valid is False or None.
        """
        # Handle case where curves is None or empty
        if not self.curves:
            return []

        # Filter curves where is_valid is not True (i.e., False or None)
        return [curve for curve in self.curves if curve.is_valid is not True]


class Trade(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    trade_id: Annotated[str | None, Field(alias="tradeId")] = None
    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    volume: float | None = None
    price: float | None = None
    side: TradeSide | None = None
    status: AuctionResultState | None = None


class AuctionMultiResolutionResponse(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    name: str | None = None
    state: AuctionStateType | None = None
    close_for_bidding: Annotated[datetime | None, Field(alias="closeForBidding")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    available_order_types: Annotated[list[OrderType] | None, Field(alias="availableOrderTypes")] = None
    currencies: list[Currency] | None = None
    contracts: list[AreaContractGroup] | None = None
    portfolios: list[AuctionPortfolio] | None = None


class AuctionPrice(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    auction: str | None = None
    auction_delivery_start: Annotated[datetime | None, Field(alias="auctionDeliveryStart")] = None
    auction_delivery_end: Annotated[datetime | None, Field(alias="auctionDeliveryEnd")] = None
    contracts: list[ContractPrice] | None = None


class BlockList(Order, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    blocks: list[Block | BlockResponse] | None = None


class BlockListResponse(OrderResponse, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    blocks: list[BlockResponse] | None = None


class BlockOrderPatch(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    blocks: list[Block | BlockResponse] | None = None
    comment: Annotated[str | None, Field(max_length=255, min_length=0)] = None


class CombinedOrdersResponse(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    curve_orders: Annotated[list[CurveOrderResponse] | None, Field(alias="curveOrders")] = None
    block_lists: Annotated[list[BlockListResponse] | None, Field(alias="blockLists")] = None

    def list_orders_details(self) -> list[dict[str, str]]:
        """
        Extract order details: order_id, auction_id, state, modified, type.
        """
        curve_orders = [
            {
                "order_id": str(order.order_id) if order.order_id else "N/A",
                "auction_id": order.auction_id if order.auction_id else "N/A",
                "state": order.state.value if order.state else "None",
                "modified": order.modified.isoformat() if order.modified else "N/A",
                "type": "Curve",
            }
            for order in self.curve_orders or []
        ]

        block_orders = [
            {
                "order_id": str(block_list.order_id) if block_list.order_id else "N/A",
                "auction_id": block_list.auction_id if block_list.auction_id else "N/A",
                "state": block.state.value if block.state else "None",
                "modified": block_list.modified.isoformat() if block_list.modified else "N/A",
                "type": "Block",
            }
            for block_list in self.block_lists or []
            for block in block_list.blocks or []
        ]

        return curve_orders + block_orders

    def select_curve_order_by_auction_id(self, auction_id: str) -> UUID | None:
        """
        Select a curve order  by auction_id.

        Args:
            auction_id: String representing the contract ID to search for

        Returns:
            UUID of the matching order_id or None if not found

        Raises:
            ValueError: If more than one CurveOrderResponse matches the auction_id
        """
        if self.curve_orders is None:
            return None

        matching_orders = [co for co in self.curve_orders if co.auction_id == auction_id]

        if len(matching_orders) > 1:
            msg = f"Multiple CurveOrderResponse found for auction_id: {auction_id}"
            raise ValueError(msg)

        return matching_orders[0].order_id if matching_orders else None

    def count_by_state_and_type(self) -> dict[str, dict[str, int]]:
        """
        Count orders by state and type and state from a CombinedOrdersResponse.
        Returns a dictionary with order types as keys and state counts as nested dictionaries.
        """
        result = {"CurveOrder": defaultdict(int), "BlockOrder": defaultdict(int)}

        # Count Curve Orders
        if self.curve_orders:
            for order in self.curve_orders:
                state = order.state.value if order.state else "None"
                result["CurveOrder"][state] += 1

        # Count Block Orders
        if self.block_lists:
            for block_list in self.block_lists:
                if block_list.blocks:
                    for block in block_list.blocks:
                        state = block.state.value if block.state else "None"
                        result["BlockOrder"][state] += 1

        # Convert defaultdict to regular dict for clean output
        return {"CurveOrder": dict(result["CurveOrder"]), "BlockOrder": dict(result["BlockOrder"])}


class OrderResultResponse(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    order_id: Annotated[str | None, Field(alias="orderId")] = None
    order_type: Annotated[OrderResultType | None, Field(alias="orderType")] = None
    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    user_id: Annotated[str | None, Field(alias="userId")] = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    portfolio: str | None = None
    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    trades: list[Trade] | None = None


class BlockResultResponse(OrderResultResponse, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    exclusive_group: Annotated[str | None, Field(alias="exclusiveGroup")] = None
    linked_to: Annotated[str | None, Field(alias="linkedTo")] = None
    is_spread_block: Annotated[bool | None, Field(alias="isSpreadBlock")] = None
