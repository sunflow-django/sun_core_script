from collections.abc import Iterator
from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import RootModel
from pydantic import field_validator

from app.constants.time_zones import PARIS_TZ


# Constants
MIN_LAT = -90
MAX_LAT = 90
MIN_LON = -180
MAX_LON = 180

# Messages
MSG_TZ = "datetime must be timezone-aware"
MSG_LAT = "Latitude must be between -90 and 90"
MSG_LON = "Longitude must be between -180 and 180"

class ForecastType(str, Enum):
    """
    Enum for forecast types.
    - Generation: Generation timeseries (active power)
    - Dispatch_Program: Day-ahead Production Schedule
    """

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


class EnergyType(str, Enum):
    """Enum for installation energy types."""

    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    OTHER = "other"


class AuthToken(BaseModel, extra="forbid"):
    model_config = ConfigDict(populate_by_name=True)

    auth_token: Annotated[str, Field(description="API token")]





class Installation(BaseModel, extra="forbid"):
    """Schema for one installation."""

    model_config = ConfigDict(populate_by_name=True)

    client_id: Annotated[str | None, Field(description="Client reference")] = None
    energy: Annotated[EnergyType, Field(description="Type of the installation")] = EnergyType.OTHER
    external_ref: Annotated[str | None, Field(description="Client reference")] = None
    latitude: Annotated[float | None, Field(description="Latitude (in degrees)")] = None
    longitude: Annotated[float | None, Field(description="Longitude (in degrees)")] = None
    name: Annotated[str, Field(description="Name of the installation")]

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float | None) -> float | None:
        if v is not None and not MIN_LAT <= v <= MAX_LAT:
            raise ValueError(MSG_LAT)
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float | None) -> float | None:
        if v is not None and not MIN_LON <= v <= MAX_LON:
            raise ValueError(MSG_LON)
        return v


class InstallationList(RootModel):
    """Schema for a list of installations."""

    root: list[Installation] = Field(default_factory=list)

    def client_ids(self) -> Iterator[str]:
        """Yield the client ID of each installation."""
        for client in self.root:
            if client.client_id is not None:
                yield client.client_id

    def names(self) -> Iterator[str]:
        """Yield the name of each installation."""
        for client in self.root:
            yield client.name


class Alert(BaseModel, extra="forbid"):
    """Schema for a single alert data."""

    model_config = ConfigDict(coerce_numbers_to_str=True)

    type: Annotated[str, Field(description="Alarm type")]
    installation_name: Annotated[str, Field(description="Name of the installation")]
    created_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(tz=PARIS_TZ), description="Date of creation"),
    ]
    closed_at: Annotated[datetime | None, Field(description="Potential close date")] = None

    @field_validator("created_at", "closed_at")
    @classmethod
    def validate_timezone(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError(MSG_TZ)
        return v


class AlertList(RootModel):
    """Schema for a list of alerts."""

    root: list[Alert] = Field(default_factory=list)

    def installation_names(self) -> Iterator[str]:
        """Yield the name of each installation."""
        for alert in self.root:
            yield alert.installation_name


class LoadCurvePoint(BaseModel, extra="forbid"):
    """Schema for a single load curve point."""

    data: Annotated[float | None, Field(description="Time series value")] = None
    date: Annotated[datetime, Field(default_factory=lambda: datetime.now(tz=PARIS_TZ), description="Date time")]

    @field_validator("date")
    @classmethod
    def validate_timezone(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError(MSG_TZ)
        return v


class LoadCurve(RootModel):
    """Schema for load curve data."""

    root: list[LoadCurvePoint]
