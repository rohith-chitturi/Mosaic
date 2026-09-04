from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class CanonicalCustomer:
    internal_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: datetime

@dataclass
class CanonicalProduct:
    internal_id: str
    name: str
    category: str
    price_cents: int
    created_at: datetime

@dataclass
class CanonicalOrder:
    internal_id: str
    customer_id: str
    total_amount_cents: int
    created_at: datetime

@dataclass
class CanonicalOrderItem:
    internal_id: str
    order_id: str
    product_id: str
    quantity: int
    unit_price_cents: int

@dataclass
class CanonicalPayment:
    internal_id: str
    order_id: str
    amount_cents: int
    payment_method: str
    status: str
    created_at: datetime

@dataclass
class CanonicalShipment:
    internal_id: str
    order_id: str
    status: str
    shipped_at: Optional[datetime]

@dataclass
class CanonicalReturn:
    internal_id: str
    order_item_id: str
    reason: str
    refunded_amount_cents: int
    created_at: datetime
