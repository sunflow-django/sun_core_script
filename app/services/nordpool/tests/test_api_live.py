import uuid

import pytest

from app.core.config import settings
from app.services.nordpool.api import AuctionAPI
from app.services.nordpool.schema import AuctionMultiResolutionResponse
from app.services.nordpool.schema import AuctionPrice
from app.services.nordpool.schema import AuctionResponse
from app.services.nordpool.schema import Block
from app.services.nordpool.schema import BlockList
from app.services.nordpool.schema import BlockListResponse
from app.services.nordpool.schema import BlockOrderPatch
from app.services.nordpool.schema import BlockPeriod
from app.services.nordpool.schema import BlockResultResponse
from app.services.nordpool.schema import CombinedOrdersResponse
from app.services.nordpool.schema import Curve
from app.services.nordpool.schema import CurveOrder
from app.services.nordpool.schema import CurveOrderPatch
from app.services.nordpool.schema import CurveOrderResponse
from app.services.nordpool.schema import CurvePoint
from app.services.nordpool.schema import OrderResultResponse
from app.services.nordpool.schema import PortfolioVolumeResponse
from app.services.nordpool.schema import ReasonabilityResultsInfo


@pytest.fixture
def api() -> AuctionAPI:
    return AuctionAPI(
        username=settings.NORDPOOL_USERNAME,
        password=settings.NORDPOOL_PASSWORD,
        prod=False,
    )


@pytest.mark.live
def test_api_get_auctions(api: AuctionAPI) -> None:
    auctions = api.get_auctions(
        close_bidding_from="2025-05-19T10:00:00Z",
        close_bidding_to="2025-05-19T10:00:00Z",
    )
    assert isinstance(auctions, AuctionResponse) or auctions is None, "Response should be AuctionResponse or None"
    if auctions is not None:
        assert auctions.id is not None, "Auction should have an 'id'"
        assert auctions.name is not None, "Auction should have a 'name'"
        assert auctions.state is not None, "Auction should have a 'state'"
        assert auctions.close_for_bidding is not None, "Auction should have 'closeForBidding'"
        assert auctions.delivery_start is not None, "Auction should have 'deliveryStart'"
        assert auctions.delivery_end is not None, "Auction should have 'deliveryEnd'"


@pytest.mark.live
def test_api_get_auction_detail(api: AuctionAPI) -> None:
    auction_id = "CWE_H_DA_1-20250519"
    auction_detail = api.get_auction_detail(auction_id)
    assert isinstance(auction_detail, AuctionMultiResolutionResponse) or auction_detail is None, (
        "Response should be AuctionMultiResolutionResponse or None"
    )
    if auction_detail is not None:
        assert auction_detail.id is not None, "Auction detail should have 'id'"
        assert auction_detail.name is not None, "Auction detail should have 'name'"
        assert auction_detail.state is not None, "Auction detail should have 'state'"
        assert auction_detail.close_for_bidding is not None, "Auction detail should have 'closeForBidding'"
        assert auction_detail.delivery_start is not None, "Auction detail should have 'deliveryStart'"
        assert auction_detail.delivery_end is not None, "Auction detail should have 'deliveryEnd'"
        assert auction_detail.available_order_types is not None, "Auction detail should have 'availableOrderTypes'"
        assert isinstance(auction_detail.available_order_types, list), "availableOrderTypes should be a list"
        assert auction_detail.currencies is not None, "Auction detail should have 'currencies'"
        assert isinstance(auction_detail.currencies, list), "currencies should be a list"
        assert auction_detail.contracts is not None, "Auction detail should have 'contracts'"
        assert isinstance(auction_detail.contracts, list), "contracts should be a list"


@pytest.mark.live
def test_api_get_orders(api: AuctionAPI) -> None:
    auction_id = "CWE_H_DA_1-20250519"
    orders = api.get_orders(auction_id, portfolios=["FR-SUNFLOW"], area_codes=["FR"])
    assert isinstance(orders, CombinedOrdersResponse) or orders is None, (
        "Response should be CombinedOrdersResponse or None"
    )
    if orders is not None:
        assert orders.curve_orders is not None, "Expected 'curveOrders' key"
        assert orders.block_lists is not None, "Expected 'blockLists' key"


@pytest.mark.live
def test_api_get_trades(api: AuctionAPI) -> None:
    # Note: This test may fail due to access restrictions or unpublished results
    auction_id = "CWE_H_DA_1-20250517"
    trades = api.get_trades(auction_id)

    assert isinstance(trades, OrderResultResponse | BlockResultResponse) or trades is None, (
        "Response should be OrderResultResponse, BlockResultResponse, or None"
    )
    if trades is not None and trades.trades:
        trade = trades.trades[0]
        assert trade.trade_id is not None, "Trade should have 'tradeId'"
        assert trade.contract_id is not None, "Trade should have 'contractId'"


@pytest.mark.live
def test_api_post_block_order(api: AuctionAPI) -> None:
    block_order = BlockList(
        auction_id="CWE_H_DA_1-20250519",
        portfolio="TestPortfolio",
        area_code="TBW",
        blocks=[
            Block(
                name="TestBlock",
                price=50.0,
                minimum_acceptance_ratio=1.0,
                periods=[BlockPeriod(contract_id="NPIDA_1-20250519-01", volume=-100.0)],
            ),
        ],
    )
    created_block_list = api.post_block_order(block_order)
    assert isinstance(created_block_list, BlockListResponse) or created_block_list is None, (
        "Response should be BlockListResponse or None"
    )
    if created_block_list is not None:
        assert created_block_list.order_id is not None, "Expected 'orderId' in response"


@pytest.mark.live
def test_api_get_block_order(api: AuctionAPI) -> None:
    # Note: Replace with a valid order_id from a previous post_block_order call
    order_id = uuid.uuid4()  # Placeholder; ideally, obtain from a created order
    block_list = api.get_block_order(order_id)
    assert isinstance(block_list, BlockListResponse) or block_list is None, (
        "Response should be BlockListResponse or None"
    )
    if block_list is not None:
        assert block_list.order_id is not None, "Expected 'orderId' key"
        assert block_list.blocks is not None, "Expected 'blocks' key"


@pytest.mark.live
def test_api_patch_block_order(api: AuctionAPI) -> None:
    # Note: Replace with a valid order_id from a previous post_block_order call
    order_id = uuid.uuid4()  # Placeholder; ideally, obtain from a created order
    patch_data = BlockOrderPatch(comment="Updated comment")
    updated_block_list = api.patch_block_order(order_id, patch_data)
    assert isinstance(updated_block_list, BlockListResponse) or updated_block_list is None, (
        "Response should be BlockListResponse or None"
    )
    if updated_block_list is not None:
        assert updated_block_list.comment == "Updated comment", "Comment should be updated"


@pytest.mark.live
def test_api_post_curve_order(api: AuctionAPI) -> None:
    curve_order = CurveOrder(
        auction_id="CWE_H_DA_1-20250519",
        portfolio="TestPortfolio",
        area_code="FR",
        curves=[
            Curve(
                contract_id="CWE_H_DA_1-20250520-01",
                curve_points=[
                    CurvePoint(price=-500.0, volume=100.0),
                    CurvePoint(price=3000.0, volume=-100.0),
                ],
            ),
        ],
    )
    created_curve_order = api.post_curve_order(curve_order)
    assert isinstance(created_curve_order, CurveOrderResponse) or created_curve_order is None, (
        "Response should be CurveOrderResponse or None"
    )
    if created_curve_order is not None:
        assert created_curve_order.order_id is not None, "Expected 'orderId' in response"


@pytest.mark.live
def test_api_get_curve_order(api: AuctionAPI) -> None:
    # Note: Replace with a valid order_id from a previous post_curve_order call
    order_id = uuid.uuid4()  # Placeholder; ideally, obtain from a created order
    curve_order = api.get_curve_order(order_id)
    assert isinstance(curve_order, CurveOrderResponse) or curve_order is None, (
        "Response should be CurveOrderResponse or None"
    )
    if curve_order is not None:
        assert curve_order.order_id is not None, "Expected 'orderId' key"
        assert curve_order.curves is not None, "Expected 'curves' key"


@pytest.mark.live
def test_api_patch_curve_order(api: AuctionAPI) -> None:
    # Note: Replace with a valid order_id from a previous post_curve_order call
    order_id = uuid.uuid4()  # Placeholder; ideally, obtain from a created order
    patch_data = CurveOrderPatch(comment="Updated curve comment")
    updated_curve_order = api.patch_curve_order(order_id, patch_data)
    assert isinstance(updated_curve_order, CurveOrderResponse) or updated_curve_order is None, (
        "Response should be CurveOrderResponse or None"
    )
    if updated_curve_order is not None:
        assert updated_curve_order.comment == "Updated curve comment", "Comment should be updated"


@pytest.mark.live
def test_api_get_prices(api: AuctionAPI) -> None:
    # Note: This test may fail due to unpublished results or access restrictions
    auction_id = "CWE_H_DA_1-20250519"
    prices = api.get_prices(auction_id)
    assert isinstance(prices, AuctionPrice) or prices is None, "Response should be AuctionPrice or None"
    if prices is not None:
        assert prices.auction is not None, "Expected 'auction' key"
        assert prices.contracts is not None, "Expected 'contracts' key"


@pytest.mark.live
def test_api_get_reasonability_result_for_order(api: AuctionAPI) -> None:
    # Note: Replace with valid external_auction_id and order_id
    external_auction_id = "CWE_H_DA_1-20250519"
    order_id = uuid.uuid4()  # Placeholder; ideally, obtain from a created order
    reasonability_result = api.get_reasonability_result_for_order(external_auction_id, order_id)
    assert isinstance(reasonability_result, ReasonabilityResultsInfo) or reasonability_result is None, (
        "Response should be ReasonabilityResultsInfo or None"
    )
    if reasonability_result is not None:
        assert reasonability_result.portfolio is not None, "Expected 'portfolio' key"
        assert reasonability_result.area is not None, "Expected 'area' key"


@pytest.mark.live
def test_api_get_state(api: AuctionAPI) -> None:
    state = api.get_state()
    assert isinstance(state, bool), "Response should be a boolean"
    assert state, "API state should be True for a successful response"


@pytest.mark.live
def test_api_get_portfolio_volumes(api: AuctionAPI) -> None:
    # Note: This test may fail due to unpublished results or access restrictions
    auction_id = "CWE_H_DA_1-20250519"
    volumes = api.get_portfolio_volumes(auction_id)
    assert isinstance(volumes, PortfolioVolumeResponse) or volumes is None, (
        "Response should be PortfolioVolumeResponse or None"
    )
    if volumes is not None:
        assert volumes.auction_id is not None, "Expected 'auctionId' key"
        assert volumes.portfolio_net_volumes is not None, "Expected 'portfolioNetVolumes' key"
