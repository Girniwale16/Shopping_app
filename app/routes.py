import os
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header, status
import psycopg2

from app.database import get_db
from app.models import CheckoutRequest, OrderResponse

router = APIRouter()

API_KEY = os.getenv("API_KEY", "sk_test_12345")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return x_api_key


@router.post(
    "/api/v1/orders/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Checkout"],
)
async def process_checkout(
    request: CheckoutRequest,
    api_key: str = Depends(verify_api_key),
    db=Depends(get_db),
):
    total_amount = 0.0
    cursor = db.cursor()

    try:
        for item in request.items:
            cursor.execute(
                "SELECT * FROM products WHERE product_id = %s",
                (item.product_id,)
            )
            product = cursor.fetchone()

            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found.")

            if product["stock"] < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product['name']}. Only {product['stock']} left."
                )

            total_amount += product["price"] * item.quantity

        if request.apply_discount_code == "SAVE20":
            total_amount *= 0.80

        total_amount *= 1.08

        if request.payment_token == "tok_fail":
            raise HTTPException(status_code=402, detail="Payment declined by bank.")

        for item in request.items:
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                (item.quantity, item.product_id)
            )

        order_id = f"ord_{uuid.uuid4().hex[:8]}"
        now = datetime.now()

        cursor.execute(
            """
            INSERT INTO orders
            (order_id, customer_email, status, total_amount, estimated_delivery, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                order_id,
                request.customer_email,
                "PAYMENT_CONFIRMED",
                round(total_amount, 2),
                "3-5 Business Days",
                now.isoformat()
            )
        )

        db.commit()

        return OrderResponse(
            order_id=order_id,
            status="PAYMENT_CONFIRMED",
            total_amount=round(total_amount, 2),
            estimated_delivery="3-5 Business Days",
            timestamp=now
        )

    except psycopg2.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cursor.close()


@router.get(
    "/api/v1/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Orders"],
)
async def get_order(
    order_id: str,
    api_key: str = Depends(verify_api_key),
    db=Depends(get_db),
):
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM orders WHERE order_id = %s",
        (order_id,)
    )
    order = cursor.fetchone()
    cursor.close()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        order_id=order["order_id"],
        status=order["status"],
        total_amount=order["total_amount"],
        estimated_delivery=order["estimated_delivery"],
        timestamp=datetime.fromisoformat(order["timestamp"])
    )


@router.get(
    "/api/v1/inventory/{product_id}",
    tags=["Inventory"],
)
async def check_inventory(
    product_id: str,
    db=Depends(get_db),
):
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE product_id = %s",
        (product_id,)
    )
    product = cursor.fetchone()
    cursor.close()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "product_id": product_id,
        "name": product["name"],
        "in_stock": product["stock"] > 0,
        "quantity_available": product["stock"]
    }