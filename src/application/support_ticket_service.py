"""Application behavior for support ticket creation and retrieval."""

from src.adapters import mock_enterprise


def create_support_ticket(
    customer_id: str,
    order_id: str,
    issue: str,
) -> dict[str, str]:
    """Create a support ticket through the enterprise adapter."""
    return mock_enterprise.create_support_ticket(customer_id, order_id, issue)


def get_support_ticket(ticket_id: str) -> dict[str, str] | None:
    """Retrieve a support ticket through the enterprise adapter."""
    return mock_enterprise.get_support_ticket(ticket_id)
