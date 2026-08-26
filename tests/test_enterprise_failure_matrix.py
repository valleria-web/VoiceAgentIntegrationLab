from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)

VALID_TICKET_REQUEST = {
    "customer_id": "2001",
    "order_id": "1111",
    "issue": "Delivery status follow-up",
}


def test_secondary_customer_exists() -> None:
    response = client.get("/customers/2002")

    assert response.status_code == 200
    assert response.json() == {
        "customer_id": "2002",
        "name": "Bruno Lima",
        "email": "bruno.lima@example.com",
        "status": "active",
    }


def test_support_ticket_rejects_unknown_order_without_mutation() -> None:
    response = client.post(
        "/support-tickets",
        json={**VALID_TICKET_REQUEST, "order_id": "9999"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}
    assert client.get("/support-tickets/TCK-3001").status_code == 404


def test_support_ticket_rejects_customer_mismatch_without_mutation() -> None:
    response = client.post(
        "/support-tickets",
        json={**VALID_TICKET_REQUEST, "customer_id": "2002"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Customer does not match order"}
    assert client.get("/support-tickets/TCK-3001").status_code == 404


def test_failed_ticket_requests_do_not_consume_identifier() -> None:
    mismatch_response = client.post(
        "/support-tickets",
        json={**VALID_TICKET_REQUEST, "customer_id": "2002"},
    )
    unknown_order_response = client.post(
        "/support-tickets",
        json={**VALID_TICKET_REQUEST, "order_id": "9999"},
    )
    valid_response = client.post("/support-tickets", json=VALID_TICKET_REQUEST)

    assert mismatch_response.status_code == 409
    assert unknown_order_response.status_code == 404
    assert valid_response.status_code == 201
    assert valid_response.json()["ticket_id"] == "TCK-3001"


def test_enterprise_timeout_returns_504() -> None:
    response = client.get("/orders/TIMEOUT")

    assert response.status_code == 504
    assert response.json() == {"detail": "Enterprise API timeout"}


def test_existing_order_not_found_behavior_is_preserved() -> None:
    response = client.get("/orders/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_invalid_ticket_request_does_not_consume_identifier() -> None:
    invalid_response = client.post(
        "/support-tickets",
        json={"customer_id": "2001", "order_id": "1111"},
    )
    valid_response = client.post("/support-tickets", json=VALID_TICKET_REQUEST)

    assert invalid_response.status_code == 422
    assert valid_response.status_code == 201
    assert valid_response.json()["ticket_id"] == "TCK-3001"
