from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_get_canonical_order() -> None:
    response = client.get("/orders/1111")

    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1111",
        "status": "in_transit",
        "estimated_delivery": "2026-08-28",
    }


def test_get_unknown_order_returns_404() -> None:
    response = client.get("/orders/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_get_canonical_order_is_deterministic() -> None:
    responses = [client.get("/orders/1111") for _ in range(5)]
    payloads = [response.json() for response in responses]

    assert all(response.status_code == 200 for response in responses)
    assert all(payload == payloads[0] for payload in payloads)
