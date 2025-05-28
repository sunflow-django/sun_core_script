from datetime import datetime
from typing import Annotated
from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator

from app.services.streem.schema import ForecastType
from app.services.streem.schema import Resolution


class GetInstallationDetailInput(BaseModel, extra="forbid"):
    """Class to validate inputs of the get_installation_detail function."""

    model_config = ConfigDict(populate_by_name=True)

    name: Annotated[str, Field(description="Name or client ID of the installation.")]


class GetInstallationAlertsInput(BaseModel, extra="forbid"):
    """Class to validate inputs of the get_installation_alerts function."""

    model_config = ConfigDict(populate_by_name=True)

    name: Annotated[str, Field(description="Name of the installation")]
    start_date: Annotated[datetime | None, Field(description="Date after which alert occurred")] = None
    end_date: Annotated[datetime | None, Field(description="Date before which alert occurred")] = None
    all_alerts: Annotated[
        bool,
        Field(description="True: get all alerts. False: get open alerts only.", strict=True),
    ] = True


class GetInstallationForecastInput(BaseModel, extra="forbid"):
    """Class to validate inputs of the get_installation_forecast function."""

    model_config = ConfigDict(populate_by_name=True)

    name: Annotated[str, Field(description="Name or client ID of the installation.")]
    resolution: Annotated[Resolution, Field(description="The time resolution for the forecast data.")] = Resolution.H1
    forecast_type: Annotated[ForecastType, Field(description="Type of forecast")] = ForecastType.DISPATCH_PROGRAM
    start_date: Annotated[
        datetime | None,
        Field(description="The start date and time of the forecast (must be timezone-aware)."),
    ] = None
    end_date: Annotated[
        datetime | None,
        Field(description="The end date and time of the forecast (must be timezone-aware)."),
    ] = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        # Error messages
        missing_date_error = "Both start_date and end_date must be provided together or both must be None."
        invalid_date_range_error = "end_date must be after start_date."
        start_date_tz = "start_date must be timezone-aware"
        end_date_tz = "end_date must be timezone-aware"

        # Validate timezone-awareness
        if self.start_date is not None and self.start_date.tzinfo is None:
            raise ValueError(start_date_tz)
        if self.end_date is not None and self.end_date.tzinfo is None:
            raise ValueError(end_date_tz)

        # Check if one is provided and the other is not
        if (self.start_date is None) != (self.end_date is None):
            raise ValueError(missing_date_error)

        # Check if both are provided and end_date is not after start_date
        if self.start_date is not None and self.end_date is not None and self.end_date <= self.start_date:
            raise ValueError(invalid_date_range_error)

        return self


class GetAlertstInput(BaseModel, extra="forbid"):
    """Class to validate inputs of the get_alerts function."""

    model_config = ConfigDict(populate_by_name=True)

    start_date: Annotated[
        datetime | None,
        Field(description="The start date and time of the forecast (must be timezone-aware)."),
    ] = None
    end_date: Annotated[
        datetime | None,
        Field(description="The end date and time of the forecast (must be timezone-aware)."),
    ] = None
    all_alerts: Annotated[
        bool,
        Field(description="True: get all alerts. False: get open alerts only.", strict=True),
    ] = True
