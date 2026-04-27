from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class CartItem(BaseModel):
    product_id: str = Field(..., example="prod_101")
    quantity: int = Field(..., gt=0, example=2)


class ShippingAddress(BaseModel):
    street: str = Field(..., example="123 Tech Boulevard")
    city: str = Field(..., example="San Francisco")
    zip_code: str = Field(..., example="94105")
    country_code: str = Field(..., min_length=2, max_length=2, example="US")


class CheckoutRequest(BaseModel):
    customer_email: EmailStr
    items: List[CartItem]
    shipping_address: ShippingAddress
    payment_token: str = Field(..., example="tok_visa_998")
    apply_discount_code: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float
    estimated_delivery: str
    timestamp: datetime