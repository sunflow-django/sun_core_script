import pytest

from app.core.config import settings
from app.services.nordpool.api import CLIENT_AUTHORISATION_STRING
from app.services.nordpool.api import AuctionAPI


@pytest.fixture
def api() -> AuctionAPI:
    return AuctionAPI(
        username=settings.NORDPOOL_USERNAME,
        password=settings.NORDPOOL_PASSWORD,
        prod=False,
    )


# TODO: OK
@pytest.mark.live
def test_api_get_auctions(api: AuctionAPI) -> None:
    auctions = api.get_auctions(close_bidding_from="2025-05-19T10:00:00Z", close_bidding_to="2025-05-19T10:00:00Z")
    assert isinstance(auctions, list), "Response should be a list"
    assert len(auctions) > 0, "Expected at least one auction in the date range"
    for auction in auctions:
        assert "id" in auction, "Auction should have an 'id'"
        assert "name" in auction, "Auction should have a 'name'"
        assert "state" in auction, "Auction should have a 'state'"
        assert "closeForBidding" in auction, "Auction should have 'closeForBidding'"
        assert "deliveryStart" in auction, "Auction should have 'deliveryStart'"
        assert "deliveryEnd" in auction, "Auction should have 'deliveryEnd'"


# TODO: OK
@pytest.mark.live
def test_api_get_auction_detail(api: AuctionAPI) -> None:
    auction_id = "CWE_H_DA_1-20250519"
    auction_detail = api.get_auction_detail(auction_id)
    assert isinstance(auction_detail, dict), "Response should be a dict"
    if auction_detail:
        assert "id" in auction_detail, "Auction detail should have 'id'"
        assert "name" in auction_detail, "Auction detail should have 'name'"
        assert "state" in auction_detail, "Auction detail should have 'state'"
        assert "closeForBidding" in auction_detail, "Auction detail should have 'closeForBidding'"
        assert "deliveryStart" in auction_detail, "Auction detail should have 'deliveryStart'"
        assert "deliveryEnd" in auction_detail, "Auction detail should have 'deliveryEnd'"

        assert "availableOrderTypes" in auction_detail, "Auction detail should have 'availableOrderTypes'"
        assert isinstance(auction_detail["availableOrderTypes"], list), "availableOrderTypes should be a list"

        assert "currencies" in auction_detail, "Auction detail should have 'availableOrderTypes'"
        assert isinstance(auction_detail["currencies"], list), "currencies should be a list"

        assert "contracts" in auction_detail, "Auction detail should have 'availableOrderTypes'"
        assert isinstance(auction_detail["contracts"], list), "contracts should be a list"


# TODO: OK
@pytest.mark.live
def test_api_get_orders(api: AuctionAPI) -> None:
    auction_id = "CWE_H_DA_1-20250519"

    orders = api.get_orders(auction_id, portfolios=["FR-SUNFLOW"], area_codes=["FR"])
    assert isinstance(orders, dict), "Response should be a dictionary"
    assert "curveOrders" in orders, "Expected 'curveOrders' key"
    assert "blockLists" in orders, "Expected 'blockLists' key"


# TODO: not working. Acces was granted on May 19
@pytest.mark.live
def test_api_get_trades(api: AuctionAPI) -> None:
    """
    {
    "type": "https://tools.ietf.org/html/rfc9110#section-15.5.4",
    "title": "Forbidden",
    "status": 403,
    "detail": "Access to auction 'CWE_H_DA_1-20250517' denied",
    "traceId": "00-fcb1a4d10795739d5267ab3c759fe328-0e439c899d043607-00"
    }
    {
    "type": "https://tools.ietf.org/html/rfc9110#section-15.5.5",
    "title": "Not Found",
    "status": 404,
    "detail": "Auction 'CWE_H_DA_1-20250519' results are not yet published",
    "traceId": "00-be7bc94c8790e036e9e74948cbcaa552-81bcbfd345ced9ca-00"
    }
    """
    auction_id = "CWE_H_DA_1-20250517"
    trades = api.get_trades(auction_id)
    assert isinstance(trades, dict), "Response should be a dict"
    if trades:
        trade = trades[0]
        assert "tradeId" in trade, "Trade should have 'tradeId'"
        assert "contractId" in trade, "Trade should have 'contractId'"



@pytest.mark.live
def test_api_post_block_order(api: AuctionAPI) -> None:
    block_order = {
        "blocks": [
            {
                "name": "TestBlock",
                "price": 50.0,
                "minimumAcceptanceRatio": 1.0,
                "periods": [{"contractId": "NPIDA_1-20250519-01", "volume": -100.0}],
            },
        ],
        "auctionId": "CWE_H_DA_1-20250519",
        "portfolio": "TestPortfolio",
        "areaCode": "TBW",
    }
    created_block_list = api.post_block_order(block_order)
    assert isinstance(created_block_list, dict), "Response should be a dictionary"
    assert "orderId" in created_block_list, "Expected 'orderId' in response"

@pytest.mark.live
def test_api_get_block_order(api: AuctionAPI) -> None:
    order_id = "some_order_id"
    block_list = api.get_block_order(order_id)
    assert isinstance(block_list, dict), "Response should be a dictionary"
    assert "orderId" in block_list, "Expected 'orderId' key"
    assert "blocks" in block_list, "Expected 'blocks' key"


@pytest.mark.live
def test_api_patch_block_order(api: AuctionAPI) -> None:
    order_id = "some_order_id"
    patch_data = {"comment": "Updated comment"}
    updated_block_list = api.patch_block_order(order_id, patch_data)
    assert isinstance(updated_block_list, dict), "Response should be a dictionary"
    assert updated_block_list["comment"] == "Updated comment", "Comment should be updated"


@pytest.mark.live
def test_api_post_curve_order(api: AuctionAPI) -> None:
    curve_order = {
        "curves": [
            {
                "contractId": "CWE_H_DA_1-20250520-01",
                "curvePoints": [
                    {"price": -500.0, "volume": 100.0},
                    {"price": 3000.0, "volume": -100.0},
                ],
            },
        ],
        "auctionId": "CWE_H_DA_1-20250519",
        "portfolio": "TestPortfolio",
        "areaCode": "FR",
    }
    created_curve_order = api.post_curve_order(curve_order)
    assert isinstance(created_curve_order, dict), "Response should be a dictionary"
    assert "orderId" in created_curve_order, "Expected 'orderId' in response"



@pytest.mark.live
def test_api_get_curve_order(api: AuctionAPI) -> None:
    order_id = "some_curve_order_id"
    curve_order = api.get_curve_order(order_id)
    assert isinstance(curve_order, dict), "Response should be a dictionary"
    assert "orderId" in curve_order, "Expected 'orderId' key"
    assert "curves" in curve_order, "Expected 'curves' key"


@pytest.mark.live
def test_api_patch_curve_order(api: AuctionAPI) -> None:
    order_id = "some_curve_order_id"
    patch_data = {"comment": "Updated curve comment"}
    updated_curve_order = api.patch_curve_order(order_id, patch_data)
    assert isinstance(updated_curve_order, dict), "Response should be a dictionary"
    assert updated_curve_order["comment"] == "Updated curve comment", "Comment should be updated"


# TODO: not working. Acces was granted on May 19
@pytest.mark.live
def test_api_get_prices(api: AuctionAPI) -> None:
    auction_id = "CWE_H_DA_1-20250519"
    prices = api.get_prices(auction_id)
    assert isinstance(prices, dict), "Response should be a dictionary"
    assert "auction" in prices, "Expected 'auction' key"
    assert "contracts" in prices, "Expected 'contracts' key"


@pytest.mark.live
def test_api_get_inspection_result_for_order(api: AuctionAPI) -> None:
    external_auction_id = "some_external_auction_id"
    order_id = "some_order_id"
    inspection_result = api.get_inspection_result_for_order(external_auction_id, order_id)
    assert isinstance(inspection_result, dict), "Response should be a dictionary"
    assert "portfolio" in inspection_result, "Expected 'portfolio' key"
    assert "area" in inspection_result, "Expected 'area' key"


@pytest.mark.live
def test_api_get_state(api: AuctionAPI) -> None:
    api.get_state()  # If no exception is raised, the test passes


# TODO: not working. Acces was granted on May 19
@pytest.mark.live
def test_api_get_portfolio_volumes(api: AuctionAPI) -> None:
    auction_id = "CWE_H_DA_1-20250519"
    volumes = api.get_portfolio_volumes(auction_id)
    assert isinstance(volumes, dict), "Response should be a dictionary"
    assert "auctionId" in volumes, "Expected 'auctionId' key"
    assert "portfolioNetVolumes" in volumes, "Expected 'portfolioNetVolumes' key"


def test_client_authorisation_string() -> None:
    assert CLIENT_AUTHORISATION_STRING == "Y2xpZW50X2F1Y3Rpb25fYXBpOmNsaWVudF9hdWN0aW9uX2FwaQ=="
