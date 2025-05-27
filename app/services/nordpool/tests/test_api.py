from collections.abc import Generator
from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

import pytest
import requests
import requests_mock

from app.constants.time_zones import PARIS_TZ
from app.services.nordpool.api import AuctionAPI
from app.services.nordpool.constants import BASE_URL_TEST
from app.services.nordpool.constants import ENDPOINTS
from app.services.nordpool.constants import TOKEN_URL_TEST
from app.services.nordpool.schema import AuctionMultiResolutionResponse
from app.services.nordpool.schema import AuctionPrice
from app.services.nordpool.schema import AuctionResponse
from app.services.nordpool.schema import BlockList
from app.services.nordpool.schema import BlockListResponse
from app.services.nordpool.schema import BlockOrderPatch
from app.services.nordpool.schema import BlockResultResponse
from app.services.nordpool.schema import CombinedOrdersResponse
from app.services.nordpool.schema import ContractPrice
from app.services.nordpool.schema import CurveOrder
from app.services.nordpool.schema import CurveOrderPatch
from app.services.nordpool.schema import CurveOrderResponse
from app.services.nordpool.schema import OrderResultResponse
from app.services.nordpool.schema import PortfolioVolumeResponse
from app.services.nordpool.schema import ProblemDetails
from app.services.nordpool.schema import ReasonabilityResultsInfo


# Fake data for testing, aligned with schema.py
fake_auction_price = AuctionPrice(
    auction="fake_auction_id",
    auction_delivery_start=datetime.now(tz=PARIS_TZ).isoformat(),
    auction_delivery_end=datetime.now(tz=PARIS_TZ).isoformat(),
    contracts=[ContractPrice(contract_id="fake_contract_id")],
)

fake_portfolio_volumes = PortfolioVolumeResponse(
    auction_id="fake_auction_id",
    portfolio_net_volumes=[],
)

fake_auction_detail = AuctionMultiResolutionResponse(
    id="fake_auction_id",
    name="Fake Auction Detail",
    state="Open",
)

fake_block_list = BlockList(
    auction_id="fake_auction_id",
    portfolio="fake_portfolio",
    area_code="FR",
    blocks=[],
)

fake_block_order_patch = BlockOrderPatch(
    blocks=[],
    comment="Updated block order",
)

fake_curve_order = CurveOrder(
    auction_id="fake_auction_id",
    portfolio="fake_portfolio",
    area_code="FR",
    curves=[],
)

fake_curve_order_patch = CurveOrderPatch(
    curves=[],
    comment="Updated curve order",
)

fake_order_result = OrderResultResponse(
    order_id=str(uuid4()),
    auction_id="fake_auction_id",
    trades=[],
)

fake_block_result = BlockResultResponse(
    order_id=str(uuid4()),
    auction_id="fake_auction_id",
    trades=[],
    name="Fake Block Result",
)

fake_reasonability_result = ReasonabilityResultsInfo(
    auction_id="fake_auction_id",
    order_id=str(uuid4()),
    curves=[],
)

fake_state = {"status": "Operational"}

fake_orders = CombinedOrdersResponse(
    curve_orders=[CurveOrderResponse(order_id=str(uuid4()), auction_id="fake_auction_id", curves=[])],
    block_lists=[BlockListResponse(order_id=str(uuid4()), auction_id="fake_auction_id", blocks=[])],
)


@pytest.fixture
def mock_api() -> Generator[requests_mock.Mocker, None, None]:
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL_TEST, json={"access_token": "fake_token"})
        yield mocker


class TestAuthentication:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        assert api.token == "fake_token"

    def test_failure(self, mock_api: requests_mock.Mocker) -> None:
        mock_api.post(TOKEN_URL_TEST, status_code=401, json={"error": "invalid_grant"})
        with pytest.raises(requests.exceptions.HTTPError):
            AuctionAPI(username="test_user", password="wrong_pass", prod=False)

    def test_network_error(self, mock_api: requests_mock.Mocker) -> None:
        mock_api.post(TOKEN_URL_TEST, exc=requests.exceptions.ConnectionError)
        with pytest.raises(requests.exceptions.ConnectionError):
            AuctionAPI(username="test_user", password="test_pass", prod=False)


class TestGetAuctions:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        auction_url = f"{BASE_URL_TEST}{ENDPOINTS['auctions'].format(version='1')}"
        mock_api.get(auction_url, json=fake_auction_detail.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auctions()
        assert isinstance(result, AuctionResponse)
        assert result.id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        mock_api.get(
            f"{BASE_URL_TEST}/api/v1/auctions",
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auctions(close_bidding_from="invalid_date")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        auction_url = f"{BASE_URL_TEST}{ENDPOINTS['auctions'].format(version='1')}"
        mock_api.get(auction_url, status_code=400, json=ProblemDetails(detail="Bad Request").model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auctions()
        assert result is None

    def test_invalid_response(self, mock_api: requests_mock.Mocker) -> None:
        auction_url = f"{BASE_URL_TEST}{ENDPOINTS['auctions'].format(version='1')}"
        mock_api.get(auction_url, json={"invalid": "data"})
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auctions()
        assert result is None

    def test_network_error(self, mock_api: requests_mock.Mocker) -> None:
        auction_url = f"{BASE_URL_TEST}{ENDPOINTS['auctions'].format(version='1')}"
        mock_api.get(auction_url, exc=requests.exceptions.ConnectionError)
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auctions()
        assert result is None


class TestGetOrders:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        orders_url = f"{BASE_URL_TEST}{ENDPOINTS['orders'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(orders_url, json=fake_orders.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_orders(auction_id="fake_auction_id")
        assert isinstance(result, CombinedOrdersResponse)
        assert len(result.curve_orders or []) == 1
        assert len(result.block_lists or []) == 1

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        invalid_url = f"{BASE_URL_TEST}{ENDPOINTS['orders'].format(version='1', auctionId='')}"
        mock_api.get(
            invalid_url,
            status_code=400,
            json=ProblemDetails(detail="Invalid auction ID").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_orders(auction_id="")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        orders_url = f"{BASE_URL_TEST}{ENDPOINTS['orders'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(orders_url, status_code=401, json=ProblemDetails(detail="Unauthorized").model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_orders(auction_id="fake_auction_id")
        assert result is None

    def test_invalid_response(self, mock_api: requests_mock.Mocker) -> None:
        orders_url = f"{BASE_URL_TEST}{ENDPOINTS['orders'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(orders_url, json={"invalid": "data"})
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_orders(auction_id="fake_auction_id")
        assert result is None


class TestGetTrades:
    def test_success_order_result(self, mock_api: requests_mock.Mocker) -> None:
        trades_url = f"{BASE_URL_TEST}{ENDPOINTS['trades'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(trades_url, json=fake_order_result.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_trades(auction_id="fake_auction_id")
        assert isinstance(result, OrderResultResponse)
        assert result.auction_id == "fake_auction_id"

    def test_success_block_result(self, mock_api: requests_mock.Mocker) -> None:
        trades_url = f"{BASE_URL_TEST}{ENDPOINTS['trades'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(trades_url, json=fake_block_result.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_trades(auction_id="fake_auction_id")
        assert isinstance(result, BlockResultResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        invalid_url = f"{BASE_URL_TEST}{ENDPOINTS['trades'].format(version='1', auctionId='')}"
        mock_api.get(
            invalid_url,
            status_code=400,
            json=ProblemDetails(detail="Invalid auction ID").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_trades(auction_id="")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        trades_url = f"{BASE_URL_TEST}{ENDPOINTS['trades'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(trades_url, status_code=400, json=ProblemDetails(detail="Bad Request").model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_trades(auction_id="fake_auction_id")
        assert result is None

    def test_invalid_response(self, mock_api: requests_mock.Mocker) -> None:
        trades_url = f"{BASE_URL_TEST}{ENDPOINTS['trades'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(trades_url, json={"invalid": "data"})
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_trades(auction_id="fake_auction_id")
        assert result is None


class TestGetPrices:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        prices_url = f"{BASE_URL_TEST}{ENDPOINTS['prices'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(prices_url, json=fake_auction_price.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_prices(auction_id="fake_auction_id")
        assert isinstance(result, AuctionPrice)
        assert result.auction == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        invalid_url = f"{BASE_URL_TEST}{ENDPOINTS['prices'].format(version='1', auctionId='')}"
        mock_api.get(
            invalid_url,
            status_code=400,
            json=ProblemDetails(detail="Invalid auction ID").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_prices(auction_id="")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        prices_url = f"{BASE_URL_TEST}{ENDPOINTS['prices'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(prices_url, status_code=400, json=ProblemDetails(detail="Bad Request").model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_prices(auction_id="fake_auction_id")
        assert result is None

    def test_invalid_response(self, mock_api: requests_mock.Mocker) -> None:
        prices_url = f"{BASE_URL_TEST}{ENDPOINTS['prices'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(prices_url, json={"invalid": "data"})
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_prices(auction_id="fake_auction_id")
        assert result is None


class TestGetPortfolioVolumes:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        volumes_url = (
            f"{BASE_URL_TEST}{ENDPOINTS['portfolio_volumes'].format(version='1', auctionId='fake_auction_id')}"
        )
        mock_api.get(volumes_url, json=fake_portfolio_volumes.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_portfolio_volumes(auction_id="fake_auction_id")
        assert isinstance(result, PortfolioVolumeResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        invalid_url = f"{BASE_URL_TEST}{ENDPOINTS['portfolio_volumes'].format(version='1', auctionId='')}"
        mock_api.get(
            invalid_url,
            status_code=400,
            json=ProblemDetails(detail="Invalid auction ID").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_portfolio_volumes(auction_id="")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        volumes_url = (
            f"{BASE_URL_TEST}{ENDPOINTS['portfolio_volumes'].format(version='1', auctionId='fake_auction_id')}"
        )
        mock_api.get(volumes_url, status_code=400, json=ProblemDetails(detail="Bad Request").model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_portfolio_volumes(auction_id="fake_auction_id")
        assert result is None


class TestGetAuctionDetail:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        auction_url = f"{BASE_URL_TEST}{ENDPOINTS['auction'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(auction_url, json=fake_auction_detail.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auction_detail(auction_id="fake_auction_id")
        assert isinstance(result, AuctionMultiResolutionResponse)
        assert result.id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        invalid_url = f"{BASE_URL_TEST}{ENDPOINTS['auction'].format(version='1', auctionId='')}"
        mock_api.get(
            invalid_url,
            status_code=400,
            json=ProblemDetails(detail="Invalid auction ID").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auction_detail(auction_id="")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        auction_url = f"{BASE_URL_TEST}{ENDPOINTS['auction'].format(version='1', auctionId='fake_auction_id')}"
        mock_api.get(auction_url, status_code=400, json=ProblemDetails(detail="Bad Request").model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_auction_detail(auction_id="fake_auction_id")
        assert result is None


class TestGetBlockOrder:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        block_order_url = f"{BASE_URL_TEST}{ENDPOINTS['block_order'].format(version='1', orderId=order_id)}"
        mock_api.get(block_order_url, json=fake_block_list.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_block_order(order_id=order_id)
        assert isinstance(result, BlockListResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        mock_api.get(
            f"{BASE_URL_TEST}{ENDPOINTS['block_order'].format(version='1', orderId='invalid_uuid')}",
            status_code=400,
            json=ProblemDetails(detail="Invalid order ID").model_dump(mode="json"),
        )
        result = api.get_block_order(order_id="invalid_uuid")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        block_order_url = f"{BASE_URL_TEST}{ENDPOINTS['block_order'].format(version='1', orderId=order_id)}"
        mock_api.get(
            block_order_url,
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_block_order(order_id=order_id)
        assert result is None


class TestPatchBlockOrder:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        block_order_url = f"{BASE_URL_TEST}{ENDPOINTS['block_order'].format(version='1', orderId=order_id)}"
        mock_api.patch(block_order_url, json=fake_block_list.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.patch_block_order(order_id=order_id, patch_data=fake_block_order_patch)
        assert isinstance(result, BlockListResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        mock_api.patch(
            f"{BASE_URL_TEST}{ENDPOINTS['block_order'].format(version='1', orderId='invalid_uuid')}",
            status_code=400,
            json=ProblemDetails(detail="Invalid order ID").model_dump(mode="json"),
        )
        result = api.patch_block_order(order_id="invalid_uuid", patch_data=fake_block_order_patch)
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        block_order_url = f"{BASE_URL_TEST}{ENDPOINTS['block_order'].format(version='1', orderId=order_id)}"
        mock_api.patch(
            block_order_url,
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.patch_block_order(order_id=order_id, patch_data=fake_block_order_patch)
        assert result is None


class TestPostBlockOrder:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        block_orders_url = f"{BASE_URL_TEST}{ENDPOINTS['block_orders'].format(version='1')}"
        mock_api.post(block_orders_url, json=fake_block_list.model_dump(mode="json"), status_code=HTTPStatus.CREATED)
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.post_block_order(block_list=fake_block_list)
        assert isinstance(result, BlockListResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        invalid_block_list = BlockList(auction_id="invalid_id", portfolio="invalid_portfolio", area_code="FR")
        block_orders_url = f"{BASE_URL_TEST}{ENDPOINTS['block_orders'].format(version='1')}"
        mock_api.post(
            block_orders_url,
            status_code=400,
            json=ProblemDetails(detail="Invalid input").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.post_block_order(block_list=invalid_block_list)
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        block_orders_url = f"{BASE_URL_TEST}{ENDPOINTS['block_orders'].format(version='1')}"
        mock_api.post(
            block_orders_url,
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.post_block_order(block_list=fake_block_list)
        assert result is None


class TestGetCurveOrder:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        curve_order_url = f"{BASE_URL_TEST}{ENDPOINTS['curve_order'].format(version='1', orderId=order_id)}"
        mock_api.get(curve_order_url, json=fake_orders.curve_orders[0].model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_curve_order(order_id=order_id)
        assert isinstance(result, CurveOrderResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        mock_api.get(
            f"{BASE_URL_TEST}{ENDPOINTS['curve_order'].format(version='1', orderId='invalid_uuid')}",
            status_code=400,
            json=ProblemDetails(detail="Invalid order ID").model_dump(mode="json"),
        )
        result = api.get_curve_order(order_id="invalid_uuid")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        curve_order_url = f"{BASE_URL_TEST}{ENDPOINTS['curve_order'].format(version='1', orderId=order_id)}"
        mock_api.get(
            curve_order_url,
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_curve_order(order_id=order_id)
        assert result is None


class TestPatchCurveOrder:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        curve_order_url = f"{BASE_URL_TEST}{ENDPOINTS['curve_order'].format(version='1', orderId=order_id)}"
        mock_api.patch(curve_order_url, json=fake_orders.curve_orders[0].model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.patch_curve_order(order_id=order_id, patch_data=fake_curve_order_patch)
        assert isinstance(result, CurveOrderResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        mock_api.patch(
            f"{BASE_URL_TEST}{ENDPOINTS['curve_order'].format(version='1', orderId='invalid_uuid')}",
            status_code=400,
            json=ProblemDetails(detail="Invalid order ID").model_dump(mode="json"),
        )
        result = api.patch_curve_order(order_id="invalid_uuid", patch_data=fake_curve_order_patch)
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        curve_order_url = f"{BASE_URL_TEST}{ENDPOINTS['curve_order'].format(version='1', orderId=order_id)}"
        mock_api.patch(
            curve_order_url,
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.patch_curve_order(order_id=order_id, patch_data=fake_curve_order_patch)
        assert result is None


class TestPostCurveOrder:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        curve_orders_url = f"{BASE_URL_TEST}{ENDPOINTS['curve_orders'].format(version='1')}"
        mock_api.post(
            curve_orders_url,
            json=fake_orders.curve_orders[0].model_dump(mode="json"),
            status_code=HTTPStatus.CREATED,
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.post_curve_order(curve_order=fake_curve_order)
        assert isinstance(result, CurveOrderResponse)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        invalid_curve_order = CurveOrder(
            auction_id="invalid_id",
            portfolio="invalid_portfolio",
            area_code="FR",
            curves=[],
        )
        curve_orders_url = f"{BASE_URL_TEST}{ENDPOINTS['curve_orders'].format(version='1')}"
        mock_api.post(
            curve_orders_url,
            status_code=400,
            json=ProblemDetails(detail="Invalid input").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.post_curve_order(curve_order=invalid_curve_order)
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        curve_orders_url = f"{BASE_URL_TEST}{ENDPOINTS['curve_orders'].format(version='1')}"
        mock_api.post(
            curve_orders_url,
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.post_curve_order(curve_order=fake_curve_order)
        assert result is None


class TestGetReasonabilityResult:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        reasonability_url = (
            f"{BASE_URL_TEST}"
            f"{
                ENDPOINTS['reasonability_result'].format(
                    version='1', externalAuctionId='fake_auction_id', orderId=order_id
                )
            }"
        )
        mock_api.get(reasonability_url, json=fake_reasonability_result.model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_reasonability_result_for_order(external_auction_id="fake_auction_id", order_id=order_id)
        assert isinstance(result, ReasonabilityResultsInfo)
        assert result.auction_id == "fake_auction_id"

    def test_invalid_input(self, mock_api: requests_mock.Mocker) -> None:
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        mock_api.get(
            (
                f"{BASE_URL_TEST}{
                    ENDPOINTS['reasonability_result'].format(version='1', externalAuctionId='', orderId='invalid_uuid')
                }"
            ),
            status_code=400,
            json=ProblemDetails(detail="Invalid input").model_dump(mode="json"),
        )
        result = api.get_reasonability_result_for_order(external_auction_id="", order_id="invalid_uuid")
        assert result is None

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        order_id = str(uuid4())
        reasonability_url = f"{BASE_URL_TEST}{
            ENDPOINTS['reasonability_result'].format(version='1', externalAuctionId='fake_auction_id', orderId=order_id)
        }"
        mock_api.get(
            reasonability_url,
            status_code=400,
            json=ProblemDetails(detail="Bad Request").model_dump(mode="json"),
        )
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_reasonability_result_for_order(external_auction_id="fake_auction_id", order_id=order_id)
        assert result is None


class TestGetState:
    def test_success(self, mock_api: requests_mock.Mocker) -> None:
        state_url = f"{BASE_URL_TEST}{ENDPOINTS['state']}"
        mock_api.get(state_url, json=fake_state)
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_state()
        assert result is True

    def test_http_error(self, mock_api: requests_mock.Mocker) -> None:
        state_url = f"{BASE_URL_TEST}{ENDPOINTS['state']}"
        mock_api.get(state_url, status_code=400, json=ProblemDetails(detail="Bad Request").model_dump(mode="json"))
        api = AuctionAPI(username="test_user", password="test_pass", prod=False)
        result = api.get_state()
        assert result is False
