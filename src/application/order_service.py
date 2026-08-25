"""Application behavior for order lookup."""

from src.adapters import mock_enterprise


def get_order(order_id: str) -> dict[str, str] | None:
    """Retrieve an order through the enterprise adapter."""
    return mock_enterprise.get_order(order_id)
