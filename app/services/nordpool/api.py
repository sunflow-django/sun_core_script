import base64
from typing import Any

import requests

from app.services.nordpool.schema import AuctionMultiResolutionResponse
from app.services.nordpool.schema import AuctionPrice
from app.services.nordpool.schema import AuctionResponse
from app.services.nordpool.schema import BlockList
from app.services.nordpool.schema import BlockListResponse
from app.services.nordpool.schema import BlockOrderPatch
from app.services.nordpool.schema import BlockResultResponse
from app.services.nordpool.schema import CombinedOrdersResponse
from app.services.nordpool.schema import CurveOrder
from app.services.nordpool.schema import CurveOrderPatch
from app.services.nordpool.schema import CurveOrderResponse
from app.services.nordpool.schema import OrderResultResponse
from app.services.nordpool.schema import PortfolioVolumeResponse
from app.services.nordpool.schema import ProblemDetails
from app.services.nordpool.schema import ReasonabilityResultsInfo


# Definitions
# - Product: A traded product. Ex.: "CWE_H_DA_1" for CWE Hour Day Ahead on 19.05.2025. Available in several area codes
# - Area codes: A country. Ex.: "FR" for France
# - Auction: A trading day for a product (no area code). Ex.: "CWE_H_DA_1-20250519", for CWE Hour Day Ahead 19.05.2025
# - Contract:  A trading hour for an auction (no area code). Ex: "CWE_H_DA_1-20250520-01"

# Urls
BASE_URL_TEST = "https://auctions-api.test.nordpoolgroup.com"
TOKEN_URL_TEST = "https://sts.test.nordpoolgroup.com/connect/token"

BASE_URL_PROD = "https://auctions-api.nordpoolgroup.com"
TOKEN_URL_PROD = "https://sts.nordpoolgroup.com/connect/token"

ENDPOINTS = {
    "auctions": "/api/v{version}/auctions",
    "orders": "/api/v{version}/auctions/{auctionId}/orders",
    "trades": "/api/v{version}/auctions/{auctionId}/trades",
    "prices": "/api/v{version}/auctions/{auctionId}/prices",
    "portfolio_volumes": "/api/v{version}/auctions/{auctionId}/portfoliovolumes",
    "auction": "/api/v{version}/auctions/{auctionId}",
    "block_order": "/api/v{version}/blockorders/{orderId}",
    "block_orders": "/api/v{version}/blockorders",
    "curve_order": "/api/v{version}/curveorders/{orderId}",
    "curve_orders": "/api/v{version}/curveorders",
    "reasonability_result": "/api/v{version}/auctions/{externalAuctionId}/orders/{orderId}/results",
    "state": "/api/state",
}

# Constants
TIMEOUT = 3  # seconds
GET = "GET"
POST = "POST"
PATCH = "PATCH"

# For client ID / client secret / client authorization string
# Refer to https://developers.nordpoolgroup.com/reference/clients-and-scopes and
# https://developers.nordpoolgroup.com/reference/auth-introduction#section-request-header
AUCTION_API = "auction_api"
CLIENT_AUCTION_API = "client_auction_api"
CLIENT_AUTHORISATION_STRING = base64.b64encode(f"{CLIENT_AUCTION_API}:{CLIENT_AUCTION_API}".encode()).decode()


class AuctionAPI:
    """Handle raw connections to Nordpool Auction API.

    This class provides methods to interact with the Nordpool Auction API, including authentication,
    retrieving auctions, orders, trades, prices, portfolio volumes, and managing block and curve orders.
    """

    def __init__(
        self,
        username: str,
        password: str,
        *,
        prod: bool = False,
    ) -> None:
        """Initialize the AuctionAPI client with authentication credentials.

        Args:
            username: The username for API authentication.
            password: The password for API authentication.
            prod: If True, use the production environment; otherwise, use the test environment. Defaults to False.

        """
        self.username: str = username
        self.password: str = password
        self.prod: bool = prod

        # Refer to https://developers.nordpoolgroup.com/reference/auth-introduction
        self.base_url: str = BASE_URL_PROD if prod else BASE_URL_TEST
        self.token_url: str = TOKEN_URL_PROD if prod else TOKEN_URL_TEST
        self.version: str = "1"  # The API version

        self.token: str | None = None
        self.authenticate()

    def authenticate(self) -> None:
        """Authenticate with the Nordpool API using OAuth2 password flow to obtain an access token.

        Raises:
            requests.HTTPError: If the authentication request fails with a non-200 status code.
        """
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "scope": AUCTION_API,
            "client_id": CLIENT_AUCTION_API,
            "client_secret": CLIENT_AUCTION_API,
        }

        headers = {
            "Authorization": f"Basic {CLIENT_AUTHORISATION_STRING}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(url=self.token_url, data=data, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def _make_request(
        self,
        method: str,
        url: str,
        params: dict[str, str | list[str]] | None = None,
        json: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any] | ProblemDetails]:
        """Make an authenticated HTTP request to the Nordpool API.

        Args:
            method: The HTTP method (e.g., "GET", "POST", "PATCH").
            url: The API endpoint URL.
            params: Query parameters for the request. Defaults to None.
            json: JSON data for the request body. Defaults to None.

        Returns:
            A tuple containing the HTTP status code and either the JSON response as a dictionary
            or a ProblemDetails object if the response is not JSON-parsable or an error occurs.

        Raises:
            requests.RequestException: If a network error occurs during the request.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.request(method, url, params=params, json=json, headers=headers, timeout=TIMEOUT)
            try:  # Normal response
                return response.status_code, response.json()
            except ValueError:  # Not a json response
                pb = ProblemDetails(
                    title="ValueError",
                    status=response.status_code,
                    detail=response.text,
                )
                return response.status_code, pb
        except requests.RequestException:  # Unidentified error
            pb = ProblemDetails(
                title="Unidentified error",
                status=0,
                detail="Request failed. Network error ?",
            )
            return 0, pb

    # Auctions
    def get_auctions(
        self,
        close_bidding_from: str | None = None,
        close_bidding_to: str | None = None,
    ) -> tuple[int, AuctionResponse | ProblemDetails]:
        """Retrieve auctions that are closed for bidding within the specified time period.

        Args:
            close_bidding_from: Filter auctions with close bidding starting from this date (ISO 8601 format)
            close_bidding_to: Filter auctions with close bidding ending at this date (ISO 8601 format)

        Returns:
            A tuple containing the HTTP status code and either an AuctionResponse object or a ProblemDetails object if
            an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['auctions'].format(version=self.version)}"
        params = {}
        if close_bidding_from:
            params["closeBiddingFrom"] = close_bidding_from
        if close_bidding_to:
            params["closeBiddingTo"] = close_bidding_to
        return self._make_request(GET, url, params=params)

    def get_orders(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> tuple[int, CombinedOrdersResponse | ProblemDetails]:
        """Retrieve orders for a specific auction, filtered by portfolios and area codes.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").
            portfolios: List of portfolio IDs to filter the orders. Defaults to None.
            area_codes: List of area codes (e.g., "FR") to filter the orders. Defaults to None.

        Returns:
            A tuple containing the HTTP status code and either a CombinedOrdersResponse object or a ProblemDetails
            object if an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['orders'].format(version=self.version, auctionId=auction_id)}"
        params = {}
        if portfolios:
            params["portfolios"] = portfolios
        if area_codes:
            params["areaCodes"] = area_codes
        return self._make_request(GET, url, params=params)

    def get_trades(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> tuple[int, OrderResultResponse | BlockResultResponse | ProblemDetails]:
        """Retrieve trades for a specific auction, filtered by portfolios and area codes.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").
            portfolios: List of portfolio IDs to filter the trades. Defaults to None.
            area_codes: List of area codes (e.g., "FR") to filter the trades. Defaults to None.

        Returns:
            A tuple containing the HTTP status code and either an OrderResultResponse, BlockResultResponse, or
            ProblemDetails object if an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['trades'].format(version=self.version, auctionId=auction_id)}"
        params = {}
        if portfolios:
            params["portfolios"] = portfolios
        if area_codes:
            params["areaCodes"] = area_codes
        return self._make_request(GET, url, params=params)

    def get_prices(self, auction_id: str) -> tuple[int, AuctionPrice | ProblemDetails]:
        """Retrieve prices for a specific auction.

        Note:
            Prices are only available for auctions up to seven days in the past.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").

        Returns:
            A tuple containing the HTTP status code and either an AuctionPrice object or a ProblemDetails object if an
            error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['prices'].format(version=self.version, auctionId=auction_id)}"
        return self._make_request(GET, url)

    def get_portfolio_volumes(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> tuple[int, PortfolioVolumeResponse | ProblemDetails]:
        """Retrieve portfolio volumes for a specific auction, filtered by portfolios and area codes.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").
            portfolios: List of portfolio IDs to filter the volumes. Defaults to None.
            area_codes: List of area codes (e.g., "FR") to filter the volumes. Defaults to None.

        Returns:
            A tuple containing the HTTP status code and either a PortfolioVolumeResponse object or a ProblemDetails
            object if an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['portfolio_volumes'].format(version=self.version, auctionId=auction_id)}"
        params = {}
        if portfolios:
            params["portfolios"] = portfolios
        if area_codes:
            params["areaCodes"] = area_codes
        return self._make_request(GET, url, params=params)

    def get_auction_detail(self, auction_id: str) -> tuple[int, AuctionMultiResolutionResponse | ProblemDetails]:
        """Retrieve detailed information for a specific auction.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").

        Returns:
            A tuple containing the HTTP status code and either an AuctionMultiResolutionResponse object or a
            ProblemDetails object if an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['auction'].format(version=self.version, auctionId=auction_id)}"
        return self._make_request(GET, url)

    # Block Order
    def get_block_order(self, order_id: str) -> tuple[int, BlockListResponse | ProblemDetails]:
        """Retrieve a block order by its order ID.

        Args:
            order_id: The ID of the block order.

        Returns:
            A tuple containing the HTTP status code and either a BlockListResponse object or a ProblemDetails object if
            an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['block_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(GET, url)

    def patch_block_order(
        self,
        order_id: str,
        patch_data: BlockOrderPatch,
    ) -> tuple[int, BlockListResponse | ProblemDetails]:
        """Update an existing block order with the provided patch data.

        Args:
            order_id: The ID of the block order to update.
            patch_data: The patch data to apply to the block order.

        Returns:
            A tuple containing the HTTP status code and either a BlockListResponse object or a ProblemDetails object if
            an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['block_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(PATCH, url, json=patch_data)

    def post_block_order(self, block_list: BlockList) -> tuple[int, BlockListResponse | ProblemDetails]:
        """Create a new block order.

        Args:
            block_list: The block order data to create.

        Returns:
            A tuple containing the HTTP status code and either a BlockListResponse object or a ProblemDetails object if
            an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['block_orders'].format(version=self.version)}"
        return self._make_request(POST, url, json=block_list)

    # Curve Order
    def get_curve_order(self, order_id: str) -> tuple[int, CurveOrderResponse | ProblemDetails]:
        """Retrieve a curve order by its order ID.

        Args:
            order_id: The ID of the curve order.

        Returns:
            A tuple containing the HTTP status code and either a CurveOrderResponse object or a ProblemDetails object if
            an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['curve_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(GET, url)

    def patch_curve_order(
        self,
        order_id: str,
        patch_data: CurveOrderPatch,
    ) -> tuple[int, CurveOrderResponse | ProblemDetails]:
        """Update an existing curve order with the provided patch data.

        Args:
            order_id: The ID of the curve order to update.
            patch_data: The patch data to apply to the curve order.

        Returns:
            A tuple containing the HTTP status code and either a CurveOrderResponse object or a ProblemDetails object if
            an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['curve_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(PATCH, url, json=patch_data)

    def post_curve_order(self, curve_order: CurveOrder) -> tuple[int, CurveOrderResponse | ProblemDetails]:
        """Create a new curve order.

        Args:
            curve_order: The curve order data to create.

        Returns:
            A tuple containing the HTTP status code and either a CurveOrderResponse object or a ProblemDetails object if
            an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['curve_orders'].format(version=self.version)}"
        return self._make_request(POST, url, json=curve_order)

    # Reasonability
    def get_reasonability_result_for_order(
        self,
        external_auction_id: str,
        order_id: str,
    ) -> tuple[int, ReasonabilityResultsInfo | ProblemDetails]:
        """Retrieve reasonability results for a specific order in an auction.

        Args:
            external_auction_id: The external ID of the auction (e.g., "CWE_H_DA_1-20250519").
            order_id: The ID of the order.

        Returns:
            A tuple containing the HTTP status code and either a ReasonabilityResultsInfo object or a ProblemDetails
            object if an error occurs.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = self.base_url + ENDPOINTS["reasonability_result"].format(
            version=self.version,
            externalAuctionId=external_auction_id,
            orderId=order_id,
        )
        return self._make_request(GET, url)

    # State
    def get_state(self) -> tuple[int, dict | ProblemDetails]:
        """Check the operational state of the Nordpool API.

        Returns:
            None: No content is returned; only the status is checked.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['state']}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
