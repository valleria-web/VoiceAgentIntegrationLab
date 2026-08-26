"""Application behavior for customer lookup."""

from src.adapters import mock_enterprise


def get_customer(customer_id: str) -> dict[str, str] | None:
    """Retrieve a customer through the enterprise adapter."""
    return mock_enterprise.get_customer(customer_id)
