"""Application behavior for callback scheduling and retrieval."""

from src.adapters import mock_enterprise


def create_callback(
    customer_id: str,
    phone: str,
    scheduled_for: str,
    reason: str,
) -> dict[str, str]:
    """Schedule a callback through the enterprise adapter."""
    return mock_enterprise.create_callback(
        customer_id,
        phone,
        scheduled_for,
        reason,
    )


def get_callback(callback_id: str) -> dict[str, str] | None:
    """Retrieve a callback through the enterprise adapter."""
    return mock_enterprise.get_callback(callback_id)
