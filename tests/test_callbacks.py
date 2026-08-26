from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)

CANONICAL_REQUEST = {
    "customer_id": "2001",
    "phone": "+5511999990001",
    "scheduled_for": "2026-08-29T15:00:00-03:00",
    "reason": "Order delivery follow-up",
}

CANONICAL_CALLBACK = {
    "callback_id": "CBK-4001",
    **CANONICAL_REQUEST,
    "status": "scheduled",
}


def test_schedule_canonical_callback() -> None:
    response = client.post("/callbacks", json=CANONICAL_REQUEST)

    assert response.status_code == 201
    assert response.json() == CANONICAL_CALLBACK


def test_scheduled_callback_is_observable() -> None:
    creation_response = client.post("/callbacks", json=CANONICAL_REQUEST)
    created_callback = creation_response.json()

    retrieval_response = client.get(
        f"/callbacks/{created_callback['callback_id']}"
    )

    assert creation_response.status_code == 201
    assert created_callback["callback_id"] == "CBK-4001"
    assert retrieval_response.status_code == 200
    assert retrieval_response.json() == created_callback


def test_get_unknown_callback_returns_404() -> None:
    response = client.get("/callbacks/CBK-9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Callback not found"}


def test_invalid_phone_is_rejected_without_mutation() -> None:
    response = client.post(
        "/callbacks",
        json={**CANONICAL_REQUEST, "phone": "11999990001"},
    )

    assert response.status_code == 422
    assert response.status_code != 201
    assert client.get("/callbacks/CBK-4001").status_code == 404


def test_timezone_less_datetime_is_rejected_without_mutation() -> None:
    response = client.post(
        "/callbacks",
        json={
            **CANONICAL_REQUEST,
            "scheduled_for": "2026-08-29T15:00:00",
        },
    )

    assert response.status_code == 422
    assert response.status_code != 201
    assert client.get("/callbacks/CBK-4001").status_code == 404


def test_missing_required_field_is_rejected_without_mutation() -> None:
    request_without_reason = {
        key: value for key, value in CANONICAL_REQUEST.items() if key != "reason"
    }

    response = client.post("/callbacks", json=request_without_reason)

    assert response.status_code == 422
    assert response.status_code != 201
    assert client.get("/callbacks/CBK-4001").status_code == 404
