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

_SUPPORT_TICKETS: dict[str, dict[str, str]] = {}
_NEXT_SUPPORT_TICKET_NUMBER = 3001

_CALLBACKS: dict[str, dict[str, str]] = {}
_NEXT_CALLBACK_NUMBER = 4001


def get_order(order_id: str) -> dict[str, str] | None:
    """Return a copy of an enterprise order when it exists."""
    order = _ORDERS.get(order_id)
    return dict(order) if order is not None else None


def get_customer(customer_id: str) -> dict[str, str] | None:
    """Return a copy of an enterprise customer when it exists."""
    customer = _CUSTOMERS.get(customer_id)
    return dict(customer) if customer is not None else None


def create_support_ticket(
    customer_id: str,
    order_id: str,
    issue: str,
) -> dict[str, str]:
    """Create and retain a deterministic support ticket."""
    global _NEXT_SUPPORT_TICKET_NUMBER

    ticket_id = f"TCK-{_NEXT_SUPPORT_TICKET_NUMBER}"
    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "order_id": order_id,
        "issue": issue,
        "status": "open",
    }
    _SUPPORT_TICKETS[ticket_id] = ticket
    _NEXT_SUPPORT_TICKET_NUMBER += 1
    return dict(ticket)


def get_support_ticket(ticket_id: str) -> dict[str, str] | None:
    """Return a copy of a retained support ticket when it exists."""
    ticket = _SUPPORT_TICKETS.get(ticket_id)
    return dict(ticket) if ticket is not None else None


def create_callback(
    customer_id: str,
    phone: str,
    scheduled_for: str,
    reason: str,
) -> dict[str, str]:
    """Schedule and retain a deterministic callback."""
    global _NEXT_CALLBACK_NUMBER

    callback_id = f"CBK-{_NEXT_CALLBACK_NUMBER}"
    callback = {
        "callback_id": callback_id,
        "customer_id": customer_id,
        "phone": phone,
        "scheduled_for": scheduled_for,
        "reason": reason,
        "status": "scheduled",
    }
    _CALLBACKS[callback_id] = callback
    _NEXT_CALLBACK_NUMBER += 1
    return dict(callback)


def get_callback(callback_id: str) -> dict[str, str] | None:
    """Return a copy of a scheduled callback when it exists."""
    callback = _CALLBACKS.get(callback_id)
    return dict(callback) if callback is not None else None
