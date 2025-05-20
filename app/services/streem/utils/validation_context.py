from dataclasses import dataclass
from datetime import datetime

from app.constants.time_zones import PARIS_TZ


@dataclass
class ValidationContext:
    """Validation context for json from Streem API"""

    delivery_date: str
    freq: str
    mini: float  # kWh
    maxi: float  # kWh

    def __post_init__(self) -> None:
        """Validate:
        - Delivery_date must be in 'YYYY-MM-DD'
        - freq is one of "1h", "15min"
        - 0 <= mini <=  maxi
        """
        try:
            datetime.strptime(self.delivery_date, "%Y-%m-%d").replace(tzinfo=PARIS_TZ)
        except ValueError as e:
            msg = f"delivery_date must be in 'YYYY-MM-DD' format, got '{self.delivery_date}'"
            raise ValueError(msg) from e

        if self.freq not in ["1h", "15min"]:
            msg = f"freq must be one of '1h' or '15min', got '{self.freq}'"
            raise ValueError(msg)

        if not (0 <= self.mini <= self.maxi):
            msg = f"mini /maxi must be: 0 <= mini <= maxi. Got mini={self.mini}, maxi={self.maxi}"
            raise ValueError(msg)

    @property
    def multiplier(self) -> int:
        """Returns the number of items in one hour"""
        return 1 if self.freq == "1h" else 4

    @property
    def min_length(self) -> int:
        """Returns the number of items in a day, during a spring forward DST day"""
        return 23 * self.multiplier

    @property
    def max_length(self) -> int:
        """Returns the number of items in a day, during a fall back DST day"""
        return 25 * self.multiplier
