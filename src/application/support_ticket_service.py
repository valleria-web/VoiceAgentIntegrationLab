"""Application behavior for support ticket creation and retrieval."""

from src.adapters import mock_enterprise


class OrderNotFoundError(Exception):
    """Signal that ticket creation referenced an unknown order."""


class CustomerOrderMismatchError(Exception):
    """Signal that the supplied customer does not own the order."""


def create_support_ticket(
    customer_id: str,
    order_id: str,
    issue: str,
) -> dict[str, str]:
    """Validate enterprise relations and create a support ticket."""
    order = mock_enterprise.get_order(order_id)
    if order is None:
        raise OrderNotFoundError

    order_customer_id = mock_enterprise.get_order_customer_id(order_id)
    if order_customer_id != customer_id:
        raise CustomerOrderMismatchError

    return mock_enterprise.create_support_ticket(customer_id, order_id, issue)


def get_support_ticket(ticket_id: str) -> dict[str, str] | None:
    """Retrieve a support ticket through the enterprise adapter."""
    return mock_enterprise.get_support_ticket(ticket_id)
