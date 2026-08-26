"""HTTP interface for deterministic enterprise endpoints."""

from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, StringConstraints

from src.application import customer_service, order_service, support_ticket_service


app = FastAPI(title="Voice Agent Integration Lab", version="0.1.0")

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SupportTicketRequest(BaseModel):
    """Validated request body for support ticket creation."""

    customer_id: NonEmptyString
    order_id: NonEmptyString
    issue: NonEmptyString


@app.get("/orders/{order_id}")
def read_order(order_id: str) -> dict[str, str]:
    """Expose order lookup through HTTP."""
    order = order_service.get_order(order_id)
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
    return support_ticket_service.create_support_ticket(
        customer_id=request.customer_id,
        order_id=request.order_id,
        issue=request.issue,
    )


@app.get("/support-tickets/{ticket_id}")
def read_support_ticket(ticket_id: str) -> dict[str, str]:
    """Expose support ticket lookup through HTTP."""
    ticket = support_ticket_service.get_support_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    return ticket
