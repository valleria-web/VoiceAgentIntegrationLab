"""HTTP interface for deterministic enterprise endpoints."""

from datetime import datetime
import re
from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, StringConstraints, field_validator

from src.application import (
    callback_service,
    customer_service,
    order_service,
    support_ticket_service,
)


app = FastAPI(title="Voice Agent Integration Lab", version="0.1.0")

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SupportTicketRequest(BaseModel):
    """Validated request body for support ticket creation."""

    customer_id: NonEmptyString
    order_id: NonEmptyString
    issue: NonEmptyString


class CallbackRequest(BaseModel):
    """Validated request body for callback scheduling."""

    customer_id: NonEmptyString
    phone: NonEmptyString
    scheduled_for: NonEmptyString
    reason: NonEmptyString

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Require a simple E.164-style international phone number."""
        if re.fullmatch(r"\+[1-9]\d{1,14}", phone) is None:
            raise ValueError(
                "Invalid phone number format. Expected value beginning with +"
            )
        return phone

    @field_validator("scheduled_for")
    @classmethod
    def validate_scheduled_for(cls, scheduled_for: str) -> str:
        """Require a valid ISO-8601 datetime with timezone information."""
        try:
            parsed_datetime = datetime.fromisoformat(scheduled_for)
        except ValueError as exc:
            raise ValueError("scheduled_for must be a valid ISO-8601 datetime") from exc

        if parsed_datetime.tzinfo is None or parsed_datetime.utcoffset() is None:
            raise ValueError("scheduled_for must include a timezone offset")

        return scheduled_for


@app.get("/orders/{order_id}")
def read_order(order_id: str) -> dict[str, str]:
    """Expose order lookup through HTTP."""
    try:
        order = order_service.get_order(order_id)
    except order_service.EnterpriseTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Enterprise API timeout",
        ) from exc

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@app.get("/customers/{customer_id}")
def read_customer(customer_id: str) -> dict[str, str]:
    """Expose customer lookup through HTTP."""
    customer = customer_service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@app.post("/support-tickets", status_code=status.HTTP_201_CREATED)
def create_support_ticket(request: SupportTicketRequest) -> dict[str, str]:
    """Create a support ticket through the application service."""
    try:
        return support_ticket_service.create_support_ticket(
            customer_id=request.customer_id,
            order_id=request.order_id,
            issue=request.issue,
        )
    except support_ticket_service.OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Order not found") from exc
    except support_ticket_service.CustomerOrderMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer does not match order",
        ) from exc


@app.get("/support-tickets/{ticket_id}")
def read_support_ticket(ticket_id: str) -> dict[str, str]:
    """Expose support ticket lookup through HTTP."""
    ticket = support_ticket_service.get_support_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    return ticket


@app.post("/callbacks", status_code=status.HTTP_201_CREATED)
def create_callback(request: CallbackRequest) -> dict[str, str]:
    """Schedule a callback through the application service."""
    return callback_service.create_callback(
        customer_id=request.customer_id,
        phone=request.phone,
        scheduled_for=request.scheduled_for,
        reason=request.reason,
    )


@app.get("/callbacks/{callback_id}")
def read_callback(callback_id: str) -> dict[str, str]:
    """Expose callback lookup through HTTP."""
    callback = callback_service.get_callback(callback_id)
    if callback is None:
        raise HTTPException(status_code=404, detail="Callback not found")

    return callback
