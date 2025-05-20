from datetime import datetime
from enum import Enum
from http import HTTPStatus

import requests


# Source: https://app.streem.eu/doc
# Constants
BASE_URL = "https://api.streem.eu"
TIMEOUT = 3  # seconds
GET = "GET"
POST = "POST"
PATCH = "PATCH"


# Helper class
class ForecastType(str, Enum):
    """Enum for forecast types."""

    GENERATION = "Generation"
    DISPATCH_PROGRAM = "Dispatch_Program"


class Resolution(str, Enum):
    """Enum for time resolutions."""

    M5 = "5m"
    M10 = "10m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    D1 = "1d"
    M1 = "1M"


# Main class
class StreemAPIError(Exception):
    """Custom exception for Streem API errors."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"Streem API Error {status_code}: {message}")


class StreemAPI:
    """Client for interacting with the Streem Energy API.

    Attributes:
        base_url (str): The base URL for the API.
        username (str): The username for authentication.
        password (str): The password for authentication.
        token (str | None): The authentication token.
        timeout (int): Timeout for API requests in seconds.
    """

    def __init__(self, username: str, password: str) -> None:
        """Initialize the StreemAPI client.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.base_url = BASE_URL
        self.username = username
        self.password = password
        self.token = None
        self.timeout = TIMEOUT
        self.authenticate()

    def authenticate(self) -> None:
        """Authenticate with the Streem API and obtain an access token.

        Raises:
            StreemAPIError: If authentication fails.
        """
        url = f"{self.base_url}/authenticate"
        params = {"email": self.username, "password": self.password}
        headers = {"accept": "application/json"}
        response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        if response.status_code != HTTPStatus.OK:
            raise StreemAPIError(response.status_code, response.text)
        self.token = response.json()["auth_token"]

    def _make_request(self, method: str, endpoint: str, params: dict | None = None) -> dict:
        """Helper method to make authenticated HTTP requests.

        Args:
            method (str): The HTTP method (e.g., "GET").
            endpoint (str): The API endpoint.
            params (dict | None): Query parameters.

        Returns:
            dict: The JSON response.

        Raises:
            Exception: If not authenticated.
            StreemAPIError: If the API request fails.
        """
        if self.token is None:
            msg = "Not authenticated. Call authenticate() first."
            raise StreemAPIError(HTTPStatus.FORBIDDEN, msg)
        url = f"{self.base_url}{endpoint}"
        headers = {
            "accept": "application/json",
            "Authorization": self.token,
        }
        response = requests.request(method, url, params=params, headers=headers, timeout=self.timeout)
        if response.status_code != HTTPStatus.OK:
            raise StreemAPIError(response.status_code, response.text)
        return response.json()

    def get_installations(self) -> list[dict]:
        """Get a list of all installations.

        Returns:
            list[dict]: The list of installation data.

        Raises:
            StreemAPIError: If the API request fails.
        """
        endpoint = "/v2/installations"
        return self._make_request(GET, endpoint)

    def get_installation_detail(self, name: str) -> list[dict]:
        """Get details for one installation.

        Returns:
            dict: The dict of installation details.
            {
            "client_id": "string",
            "energy": "other",
            "external_ref": "string",
            "latitude": 0,
            "longitude": 0,
            "name": "string"
            }

        Raises:
            StreemAPIError: If the API request fails.
        """
        endpoint = f"/v2/installations/{name}"
        return self._make_request(GET, endpoint)

    def get_installation_alerts(
        self,
        name: str,
        start_date: datetime,
        end_date: datetime,
        *,
        all_alerts: bool = True,
    ) -> list[dict]:
        """Get alerts for one installation.

        Returns:
            dict: The dict of installation details.
            {
            "client_id": "string",
            "energy": "other",
            "external_ref": "string",
            "latitude": 0,
            "longitude": 0,
            "name": "string"
            }

        Raises:
            StreemAPIError: If the API request fails.
        """
        endpoint = f"/v2/installations/{name}/alerts"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "all": all_alerts,
        }
        return self._make_request(GET, endpoint, params=params)

    def get_forecast(
        self,
        name: str,
        forecast_type: ForecastType,
        start_date: datetime,
        end_date: datetime,
        resolution: Resolution,
    ) -> list[dict]:
        """Fetch forecast data for a given installation.

        Args:
            name (str): The name or client ID of the installation.
            forecast_type (ForecastType): The type of forecast.
            start_date (datetime): The start date and time (must be timezone-aware).
            end_date (datetime): The end date and time (must be timezone-aware).
            resolution (Resolution): The time resolution for the forecast data.

        Returns:
            list[dict]: The forecast data.

        Raises:
            StreemAPIError: If the API request fails.
        """
        endpoint = f"/v2/installations/{name}/forecast"
        params = {
            "type": forecast_type.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "resolution": resolution.value,
        }
        return self._make_request(GET, endpoint, params=params)

    def get_alerts(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        *,
        all_alerts: bool = False,
    ) -> list[dict]:
        """Fetch alerts from the Streem API.

        Args:
            start_date (datetime | None): The start date and time (must be timezone-aware).
            end_date (datetime | None): The end date and time (must be timezone-aware).
            all_alerts (bool): If True, fetch all alerts; otherwise, fetch only open alerts.

        Returns:
            list[dict]: The list of alert data.

        Raises:
            StreemAPIError: If the API request fails.
            ValueError: If datetime parameters are not timezone-aware.
        """
        endpoint = "/v2/alerts"
        params = {"all": str(all_alerts).lower()}
        if start_date:
            if start_date.tzinfo is None:
                msg = "start_date must be timezone-aware"
                raise ValueError(msg)
            params["start_date"] = start_date.isoformat()
        if end_date:
            if end_date.tzinfo is None:
                msg = "end_date must be timezone-aware"
                raise ValueError(msg)
            params["end_date"] = end_date.isoformat()
        return self._make_request(GET, endpoint, params=params)
