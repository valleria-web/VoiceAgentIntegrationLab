from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)

CANONICAL_CUSTOMER = {
    "customer_id": "2001",
    "name": "Ana Costa",
    "email": "ana.costa@example.com",
    "status": "active",
}


def test_get_canonical_customer() -> None:
    response = client.get("/customers/2001")

    assert response.status_code == 200
    assert response.json() == CANONICAL_CUSTOMER


def test_get_unknown_customer_returns_404() -> None:
    response = client.get("/customers/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}


def test_get_canonical_customer_is_deterministic() -> None:
    responses = [client.get("/customers/2001") for _ in range(5)]
    payloads = [response.json() for response in responses]

    assert all(response.status_code == 200 for response in responses)
    assert all(payload == CANONICAL_CUSTOMER for payload in payloads)
    assert all(payload == payloads[0] for payload in payloads)
