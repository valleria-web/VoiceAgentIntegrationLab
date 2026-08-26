from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)

CANONICAL_REQUEST = {
    "customer_id": "2001",
    "order_id": "1111",
    "issue": "Delivery status follow-up",
}

CANONICAL_TICKET = {
    "ticket_id": "TCK-3001",
    **CANONICAL_REQUEST,
    "status": "open",
}


def test_create_canonical_support_ticket() -> None:
    response = client.post("/support-tickets", json=CANONICAL_REQUEST)

    assert response.status_code == 201
    assert response.json() == CANONICAL_TICKET


def test_created_support_ticket_is_observable() -> None:
    creation_response = client.post("/support-tickets", json=CANONICAL_REQUEST)
    created_ticket = creation_response.json()

    retrieval_response = client.get(
        f"/support-tickets/{created_ticket['ticket_id']}"
    )

    assert creation_response.status_code == 201
    assert retrieval_response.status_code == 200
    assert retrieval_response.json() == created_ticket


def test_get_unknown_support_ticket_returns_404() -> None:
    response = client.get("/support-tickets/TCK-9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Support ticket not found"}


def test_invalid_support_ticket_requests_are_rejected() -> None:
    invalid_requests = [
        {"customer_id": "2001", "order_id": "1111"},
        {**CANONICAL_REQUEST, "customer_id": ""},
        {**CANONICAL_REQUEST, "order_id": ""},
        {**CANONICAL_REQUEST, "issue": ""},
        {**CANONICAL_REQUEST, "issue": "   "},
        {**CANONICAL_REQUEST, "customer_id": 2001},
        {**CANONICAL_REQUEST, "order_id": 1111},
    ]

    responses = [
        client.post("/support-tickets", json=request) for request in invalid_requests
    ]

    assert all(response.status_code == 422 for response in responses)
    assert all(response.status_code != 201 for response in responses)
