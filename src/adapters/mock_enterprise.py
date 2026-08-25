"""Deterministic in-memory mock of the enterprise order system."""


_ORDERS: dict[str, dict[str, str]] = {
    "1111": {
        "order_id": "1111",
        "status": "in_transit",
        "estimated_delivery": "2026-08-28",
    }
}


def get_order(order_id: str) -> dict[str, str] | None:
    """Return a copy of an enterprise order when it exists."""
    order = _ORDERS.get(order_id)
    return dict(order) if order is not None else None
