from collections.abc import Iterator

import pytest

from src.adapters import mock_enterprise


@pytest.fixture(autouse=True)
def reset_mock_enterprise_runtime_state() -> Iterator[None]:
    """Keep mutable mock resources and identifiers isolated per test."""
    mock_enterprise.reset_runtime_state()
    yield
    mock_enterprise.reset_runtime_state()
