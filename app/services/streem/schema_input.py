from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

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
    start_date: Annotated[datetime | None, Field(description="Date after which alert occured")] = None
    end_date: Annotated[datetime | None, Field(description="Date before which alert occured")] = None
    all_alerts: Annotated[
        bool,
        Field(description="True: get all alerts. False:  get open alerts only."),
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
        bool ,
        Field(description="True: get all alerts. False:  get open alerts only."),
    ] = True
