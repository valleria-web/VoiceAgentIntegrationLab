"""HTTP interface for the minimal Sprint 2 enterprise endpoint."""

from fastapi import FastAPI, HTTPException

from src.application import order_service


app = FastAPI(title="Voice Agent Integration Lab", version="0.1.0")


@app.get("/orders/{order_id}")
def read_order(order_id: str) -> dict[str, str]:
    """Expose order lookup through HTTP."""
    order = order_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
