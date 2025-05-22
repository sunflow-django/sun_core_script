from collections.abc import Iterator
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import RootModel

from app.constants.time_zones import PARIS_TZ


class EnergyType(str, Enum):
    """Enum for installation energy types."""

    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    OTHER = "other"


class Installation(BaseModel, extra="forbid"):
    """Schema for installation data.

    Attributes:
        client_id: Client reference, optional.
        energy: Type of the installation (solar, wind, hydro, other).
        external_ref: Client reference, optional.
        latitude: Latitude in degrees, optional.
        longitude: Longitude in degrees, optional.
        name: Name of the installation.

    Returns:
        Installation: The validated installation instance.
    """

    client_id: str | None = None
    energy: EnergyType = Field(default=EnergyType.OTHER)
    external_ref: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str


class Installations(RootModel):
    """Schema for a list of installations.

    Attributes:
        root: List of installation objects.

    Returns:
        Installations: The validated installations instance.
    """

    root: list[Installation] = Field(default_factory=list)

    def client_ids(self) -> Iterator[str]:
        """Yield client IDs from the installations.

        Yields:
            str: A client ID, excluding None values.
        """
        for client in self.root:
            if client.client_id is not None:
                yield client.client_id

    def names(self) -> Iterator[str]:
        """Yield names from the installations.

        Yields:
            str: An installation name.
        """
        for client in self.root:
            yield client.name


class Alert(BaseModel, extra="forbid"):
    """Schema for alert data.

    Attributes:
        type: Alarm type.
        installation_name: Name of the installation.
        created_at: Date of creation.
        closed_at: Potential close date, optional.

    Returns:
        Alert: The validated alert instance.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)

    type: str
    installation_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=PARIS_TZ))
    closed_at: datetime | None = None


class Alerts(RootModel):
    """Schema for a list of alerts.

    Attributes:
        root: List of alert objects.

    Returns:
        Alerts: The validated alerts instance.
    """

    root: list[Alert] = Field(default_factory=list)

    def installation_names(self) -> Iterator[str]:
        """Yield installation names from the alerts.

        Yields:
            str: An installation name.
        """
        for alert in self.root:
            yield alert.installation_name


class LoadCurvePoint(BaseModel, extra="forbid"):
    """Schema for a single load curve point.

    Attributes:
        data: Time series value.
        date: Date and time of the data point.

    Returns:
        LoadCurvePoint: The validated load curve point instance.
    """

    data: float
    date: datetime = Field(default_factory=lambda: datetime.now(tz=PARIS_TZ))


class LoadCurve(BaseModel, extra="forbid"):
    """Schema for load curve data.

    Attributes:
        points: List of load curve points.

    Returns:
        LoadCurve: The validated load curve instance.
    """

    points: list[LoadCurvePoint] = Field(default_factory=list, alias="points")
