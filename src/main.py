"""HTTP interface for deterministic enterprise endpoints."""

from fastapi import FastAPI, HTTPException

from src.application import customer_service, order_service


app = FastAPI(title="Voice Agent Integration Lab", version="0.1.0")


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
