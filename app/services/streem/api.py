from datetime import datetime
from http import HTTPStatus

import requests
from loguru import logger
from pydantic import ValidationError

from app.services.streem.schema import AlertList
from app.services.streem.schema import ForecastType
from app.services.streem.schema import Installation
from app.services.streem.schema import InstallationList
from app.services.streem.schema import LoadCurve
from app.services.streem.schema import Resolution
from app.services.streem.schema_input import GetAlertstInput
from app.services.streem.schema_input import GetInstallationAlertsInput
from app.services.streem.schema_input import GetInstallationDetailInput
from app.services.streem.schema_input import GetInstallationForecastInput


# Source: https://app.streem.eu/doc
# Constants
BASE_URL = "https://api.streem.eu"
TIMEOUT = 3  # seconds


class StreemAPI:
    """Client for interacting with the Streem Energy API."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the StreemAPI client with authentication credentials..

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.username = username
        self.password = password

        self.token: str | None = None
        self.authenticate()

    def authenticate(self) -> None:
        """Authenticate with the Streem API using OAuth2 password flow to obtain an access token."""
        url = f"{BASE_URL}/authenticate"
        params = {"email": self.username, "password": self.password}  # TODO is this really clear text url ?
        headers = {"accept": "application/json"}

        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)

        response.raise_for_status()
        response_data = response.json()
        if "auth_token" in response_data:
            self.token = response_data["auth_token"]
        else:
            msg = "auth_token not found in response"
            raise KeyError(msg)

    def _make_request(
        self,
        method: str,
        url: str,
        params: dict[str, str | list[str]] | None = None,
    ) -> dict | None:
        """Helper method to make authenticated HTTP requests.

        Args:
            method: The HTTP method (e.g., "GET", "POST", "PATCH").
            url: The API endpoint URL.
            params: Query parameters for the request. Defaults to None.

        Returns:
            The JSON response, or None if an error occurs.

        """
        headers = {
            "accept": "application/json",
            "Authorization": self.token,
        }
        response = requests.request(method, url, params=params, headers=headers, timeout=TIMEOUT)
        if response.status_code != HTTPStatus.OK:
            msg = f"Request failed. Code: {response.status_code}. Text: {response.text}"
            logger.error(msg)
            return None
        return response.json()

    def get_installations(self) -> InstallationList | None:
        """Get a list of all installations.

        Returns:
            An InstallationList containing the list of installations, or None if an error occurs.
        """
        # Request preparation
        url = f"{BASE_URL}/v2/installations"

        # Request
        response = self._make_request("GET", url)

        # Output validation
        try:
            installations = InstallationList.model_validate(response)
        except ValidationError:
            logger.exception(f"Not an InstallationList: {response}")
            return None
        return installations

    def get_installation_detail(self, name: str) -> Installation | None:
        """Get details for one installation.

        Returns:
            An Installation containing the detail of an installation, or None if an error occurs.
        """
        # Input validation
        try:
            GetInstallationDetailInput(name=name)
        except ValidationError:
            logger.exception(f"Input not a valid GetInstallationDetailInput: {name}")
            return None

        # Request preparation
        url = f"{BASE_URL}/v2/installations/{name}"

        # Request
        response = self._make_request("GET", url)

        # Output validation
        try:
            installation = Installation.model_validate(response)
        except ValidationError:
            logger.exception(f"Not an Installation: {response}")
            return None
        return installation

    def get_installation_alerts(
        self,
        name: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        *,
        all_alerts: bool = True,
    ) -> AlertList | None:
        """
        Get a list of open alerts belonging to the selected installation.
        All open alerts will be returned if no start or end date(time) are provided.

        Returns:
            An Installation containing the detail of an installation, or None if an error occurs.
        """
        # Input validation
        try:
            GetInstallationAlertsInput(name=name, start_date=start_date, end_date=end_date, all_alerts=all_alerts)
        except ValidationError:
            msg = f"Inputs not a valid GetInstallationAlertsInput: {(name, start_date, end_date, all_alerts)}"
            logger.exception(msg)
            return None

        # Request preparation
        url = f"{BASE_URL}/v2/installations/{name}/alerts"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "all": all_alerts,
        }
        # Request
        response = self._make_request("GET", url, params=params)

        # Output validation
        try:
            alerts = AlertList.model_validate(response)
        except ValidationError:
            logger.exception(f"Not an Installation: {response}")
            return None
        return alerts

    def get_installation_forecast(
        self,
        name: str,
        resolution: Resolution = Resolution.H1,
        forecast_type: ForecastType = ForecastType.DISPATCH_PROGRAM,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> LoadCurve | None:
        """Fetch forecast data (load curve) between date start_date and end_date for the given installation

        Type: the load curve type. It can be:
        - Generation: Generation timeseries (active power)
        - Dispatch_Program: Day-ahead Production Schedule

        If no date range is provided, then the time series is returned for the last month.

        Returns:
            The forecast data, or None if an error occurs.
        """
        # Input validation
        try:
            GetInstallationForecastInput(
                forecast_type=forecast_type,
                start_date=start_date,
                end_date=end_date,
                resolution=resolution,
                name=name,
            )
        except ValidationError:
            inputs = (forecast_type, start_date, end_date, resolution, name)
            msg = f"Inputs not a valid GetInstallationForecastInput: {inputs}"
            logger.exception(msg)
            return None

        # Request preparation
        url = f"{BASE_URL}/v2/installations/{name}/forecast"
        params = {
            "type": forecast_type.value,
            "resolution": resolution.value,
        }
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        # Request
        response = self._make_request("GET", url, params=params)

        # Output validation
        try:
            load_curve = LoadCurve.model_validate(response)
        except ValidationError:
            logger.exception(f"Not a LoadCurve: {response}")
            return None
        return load_curve

    def get_alerts(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        *,
        all_alerts: bool = True,
    ) -> AlertList:
        """
        Get a list of open alerts.
        All open alerts will be returned if no start or end date(time) are provided.

        Returns:
            The list of alert data, or None if an error occurs.
        """
        # Input validation
        try:
            GetAlertstInput(
                start_date=start_date,
                end_date=end_date,
                all_alerts=all_alerts,
            )
        except ValidationError:
            logger.exception(f"Inputs not a valid GetAlertstInput: {(start_date, end_date, all_alerts)}")
            return None

        # Request preparation
        url = f"{BASE_URL}/v2/alerts"
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

        # Request
        response = self._make_request("GET", url, params=params)

        # Output validation
        try:
            load_curve = AlertList.model_validate(response)
        except ValidationError:
            logger.exception(f"Not an AlertList: {response}")
            return None
        return load_curve
