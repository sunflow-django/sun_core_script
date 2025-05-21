from app.services.nordpool.schema.base_schema import Curve
from app.services.nordpool.schema.base_schema import OrderResponse
from app.services.nordpool.schema.base_schema import OrderStateType


class CurveOrderResponse(OrderResponse):
    """Schema for curve order response data, inheriting from OrderResponse.

    Attributes:
        state: The state of the order.
        curves: List of curves associated with the order.

    Returns:
        CurveOrderResponse: The validated curve order response instance.
    """

    state: OrderStateType
    curves: list[Curve] | None = None
