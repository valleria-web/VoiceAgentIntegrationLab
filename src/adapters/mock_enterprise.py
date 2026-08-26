"""Deterministic in-memory mock of the enterprise order system."""


_ORDERS: dict[str, dict[str, str]] = {
    "1111": {
        "order_id": "1111",
        "status": "in_transit",
        "estimated_delivery": "2026-08-28",
    }
}

_CUSTOMERS: dict[str, dict[str, str]] = {
    "2001": {
        "customer_id": "2001",
        "name": "Ana Costa",
        "email": "ana.costa@example.com",
        "status": "active",
    }
}


def get_order(order_id: str) -> dict[str, str] | None:
    """Return a copy of an enterprise order when it exists."""
    order = _ORDERS.get(order_id)
    return dict(order) if order is not None else None


def get_customer(customer_id: str) -> dict[str, str] | None:
    """Return a copy of an enterprise customer when it exists."""
    customer = _CUSTOMERS.get(customer_id)
    return dict(customer) if customer is not None else None
