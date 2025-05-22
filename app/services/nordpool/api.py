import base64
import typing

import requests

from app.services.nordpool.schema import CurveOrder


# Definitions
# Product: A traded product. Ex.: "CWE_H_DA_1" for CWE Hour Day Ahead 19.05.2025. It is available in several area codes
# Area codes: A country. Ex.: "FR" for France
# Auction: A trading day for a product (no area code). Ex.: "CWE_H_DA_1-20250519", for CWE Hour Day Ahead 19.05.2025
# Contract:  A hour for an auction (no area code). Ex: "CWE_H_DA_1-20250520-01"

# Urls
BASE_URL_TEST = "https://auctions-api.test.nordpoolgroup.com"
TOKEN_URL_TEST = "https://sts.test.nordpoolgroup.com/connect/token"

BASE_URL_PROD = "https://auctions-api.nordpoolgroup.com"
TOKEN_URL_PROD = "https://sts..nordpoolgroup.com/connect/token"

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
    "inspection_result": "/api/v{version}/auctions/{externalAuctionId}/orders/{orderId}/results",
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
    def __init__(
        self,
        username: str,
        password: str,
        *,
        prod: bool = False,
    ) -> None:
        """Initialize the AuctionAPI client.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            prod (bool): Set to True for production environment
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
        """Authenticate and obtain an access token using OAuth2 password flow."""
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
        json: dict[str, typing.Any] | None = None,
    ) -> dict[str, typing.Any] | list[dict[str, typing.Any]]:
        """Helper method to make authenticated HTTP requests.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST").
            url (str): The URL to request.
            params (dict[str, str | list[str]], optional): Query parameters.
            json (dict[str, Any], optional): JSON data for the request body.

        Returns:
            dict[str, Any] | list[dict[str, Any]]: The JSON response.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.request(method, url, params=params, json=json, headers=headers, timeout=TIMEOUT)
        if not response.ok:
            try:
                print("Response JSON:", response.json())  # noqa: T201
            except ValueError:
                print("Response body:", response.text)  # noqa: T201
        response.raise_for_status()
        return response.json()

    def get_auctions(
        self,
        close_bidding_from: str | None = None,
        close_bidding_to: str | None = None,
    ) -> list[dict[str, typing.Any]]:
        """Get auctions that are closed for bidding during the given time period.

        Args:
            close_bidding_from (str | None): Filter auctions with close bidding from this date-time.
            close_bidding_to (str | None): Filter auctions with close bidding to this date-time.

        Returns:
            list[dict[str, Any]]: List of auction objects.

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

    def get_auction_detail(self, auction_id: str) -> list[dict[str, typing.Any]]:
        """Get details of a specific auction.

        Args:
            auction_id (str): The ID of the auction.

        Returns:
            list[dict[str, Any]]: List of auction multi-resolution response objects.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['auction'].format(version=self.version, auctionId=auction_id)}"
        return self._make_request(GET, url)

    def get_orders(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> dict[str, typing.Any]:
        """
        Get orders placed for a specific auction, limited to company, portfolios and areas user has access to.
        Selection can be filtered by specifying portfolios and areas in the search parameters. Returns all order types.

        Args:
            auction_id (str): The ID of the auction.
            portfolios (list[str] | None): List of portfolios to filter.
            area_codes (list[str] | None): List of area codes to filter.

        Returns:
            dict[str, Any]: Combined orders response.

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
    ) -> list[dict[str, typing.Any]]:
        """
        Get trades for a specific auction, limited to company, portfolios and areas user has access to.
        Selection can be filtered by specifying portfolios and areas in the search parameters. Returns all ord

        Args:
            auction_id (str): The ID of the auction.
            portfolios (list[str] | None): List of portfolios to filter.
            area_codes (list[str] | None): List of area codes to filter.

        Returns:
            list[dict[str, Any]]: List of trade objects.

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

    def post_block_order(self, block_list: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Post a new block list.

        Args:
            block_list (dict[str, Any]): The block list data.

        Returns:
            dict[str, Any]: Created block list response.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['block_orders'].format(version=self.version)}"
        return self._make_request(POST, url, json=block_list)

    def get_block_order(self, order_id: str) -> dict[str, typing.Any]:
        """Get a block list by order ID.

        Args:
            order_id (str): The ID of the order.

        Returns:
            dict[str, Any]: Block list response.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['block_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(GET, url)

    def patch_block_order(self, order_id: str, patch_data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Patch a block order.

        Args:
            order_id (str): The ID of the order.
            patch_data (dict[str, Any]): The patch data for the block order.

        Returns:
            dict[str, Any]: Updated block list response.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['block_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(PATCH, url, json=patch_data)

    def post_curve_order(self, curve_order: CurveOrder) -> dict[str, typing.Any]:
        """Post a new curve order.

        Args:
            curve_order (dict[str, Any]): The curve order data.

        Returns:
            dict[str, Any]: Created curve order response.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['curve_orders'].format(version=self.version)}"
        return self._make_request(POST, url, json=curve_order)

    def get_curve_order(self, order_id: str) -> dict[str, typing.Any]:
        """Get a curve order by order ID.

        Args:
            order_id (str): The ID of the order.

        Returns:
            dict[str, Any]: Curve order response.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['curve_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(GET, url)

    def patch_curve_order(self, order_id: str, patch_data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Patch a curve order.

        Args:
            order_id (str): The ID of the order.
            patch_data (dict[str, Any]): The patch data for the curve order.

        Returns:
            dict[str, Any]: Updated curve order response.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['curve_order'].format(version=self.version, orderId=order_id)}"
        return self._make_request(PATCH, url, json=patch_data)

    def get_prices(self, auction_id: str) -> dict[str, typing.Any]:
        """
        Get prices for a specific auction, user has access to.
        🚩 Prices are only available for seven days in the past.

        Args:
            auction_id (str): The ID of the auction.

        Returns:
            dict[str, Any]: Auction price object.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['prices'].format(version=self.version, auctionId=auction_id)}"
        return self._make_request(GET, url)

    def get_inspection_result_for_order(self, external_auction_id: str, order_id: str) -> dict[str, typing.Any]:
        """Get inspection result for an order.

        Args:
            external_auction_id (str): The external ID of the auction.
            order_id (str): The ID of the order.

        Returns:
            dict[str, Any]: Reasonability results info.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = self.base_url + ENDPOINTS["inspection_result"].format(
            version=self.version,
            externalAuctionId=external_auction_id,
            orderId=order_id,
        )
        return self._make_request(GET, url)

    def get_state(self) -> None:
        """Get the state of the API.

        Returns:
            None: No content is returned, only status is checked.

        Raises:
            requests.HTTPError: If the API request fails with a non-200 status code.
        """
        url = f"{self.base_url}{ENDPOINTS['state']}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()

    def get_portfolio_volumes(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> dict[str, typing.Any]:
        """Get portfolio volumes for a specific auction, limited by portfolios and areas the user has access to.
        Selection can be filtered by specifying portfolios and areas in the search parameters.

        Args:
            auction_id (str): The ID of the auction.
            portfolios (list[str] | None): List of portfolios to filter.
            area_codes (list[str] | None): List of area codes to filter.

        Returns:
            dict[str, Any]: Portfolio volume response.

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
