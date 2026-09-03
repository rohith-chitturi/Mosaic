import random
from faker import Faker
from datetime import datetime, timedelta
from typing import List

from data.generator.core.canonical_model import (
    CanonicalCustomer, CanonicalProduct, CanonicalOrder,
    CanonicalOrderItem, CanonicalPayment, CanonicalShipment, CanonicalReturn
)

class DataUniverse:
    def __init__(self, seed: int, scale: str):
        self.seed = seed
        self.scale = scale
        self.fake = Faker()
        self.fake.seed_instance(seed)
        random.seed(seed)
        
        self.customers: List[CanonicalCustomer] = []
        self.products: List[CanonicalProduct] = []
        self.orders: List[CanonicalOrder] = []
        self.order_items: List[CanonicalOrderItem] = []
        self.payments: List[CanonicalPayment] = []
        self.shipments: List[CanonicalShipment] = []
        self.returns: List[CanonicalReturn] = []

    def generate(self):
        scale_map = {
            "small": {"customers": 100, "products": 50, "orders": 500},
            "medium": {"customers": 1000, "products": 500, "orders": 10000},
            "large": {"customers": 10000, "products": 2000, "orders": 100000}
        }
        config = scale_map.get(self.scale, scale_map["small"])
        
        self._generate_products(config["products"])
        self._generate_customers(config["customers"])
        self._generate_orders(config["orders"])
        print(f"Generated canonical universe: {len(self.customers)} customers, {len(self.orders)} orders.")
        
    def _generate_products(self, count: int):
        categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
        for i in range(count):
            self.products.append(CanonicalProduct(
                internal_id=f"PROD_{i:04d}",
                name=self.fake.catch_phrase(),
                category=random.choice(categories),
                price_cents=random.randint(500, 50000),
                created_at=self.fake.date_time_between(start_date="-10y", end_date="-5y")
            ))

    def _generate_customers(self, count: int):
        for i in range(count):
            self.customers.append(CanonicalCustomer(
                internal_id=f"CUST_{i:05d}",
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=self.fake.email(),
                phone=self.fake.phone_number(),
                created_at=self.fake.date_time_between(start_date="-10y", end_date="now")
            ))

    def _generate_orders(self, count: int):
        for i in range(count):
            customer = random.choice(self.customers)
            # order date must be after customer creation
            order_date = self.fake.date_time_between_dates(datetime_start=customer.created_at, datetime_end=datetime.now())
            
            order_id = f"ORD_{i:06d}"
            
            # create 1 to 5 items
            num_items = random.randint(1, 5)
            total_cents = 0
            for j in range(num_items):
                product = random.choice(self.products)
                qty = random.randint(1, 3)
                total_cents += product.price_cents * qty
                
                item_id = f"ITEM_{i:06d}_{j}"
                self.order_items.append(CanonicalOrderItem(
                    internal_id=item_id,
                    order_id=order_id,
                    product_id=product.internal_id,
                    quantity=qty,
                    unit_price_cents=product.price_cents
                ))
                
                # 5% chance of return
                if random.random() < 0.05:
                    self.returns.append(CanonicalReturn(
                        internal_id=f"RET_{item_id}",
                        order_item_id=item_id,
                        reason=random.choice(["Defective", "Not Needed", "Wrong Item"]),
                        refunded_amount_cents=product.price_cents * qty,
                        created_at=order_date + timedelta(days=random.randint(1, 30))
                    ))
            
            self.orders.append(CanonicalOrder(
                internal_id=order_id,
                customer_id=customer.internal_id,
                total_amount_cents=total_cents,
                created_at=order_date
            ))
            
            # create payment
            self.payments.append(CanonicalPayment(
                internal_id=f"PAY_{order_id}",
                order_id=order_id,
                amount_cents=total_cents,
                payment_method=random.choice(["CREDIT_CARD", "PAYPAL", "BANK_TRANSFER"]),
                status=random.choice(["COMPLETED", "COMPLETED", "COMPLETED", "FAILED"]),
                created_at=order_date + timedelta(minutes=random.randint(1, 60))
            ))
            
            # create shipment
            self.shipments.append(CanonicalShipment(
                internal_id=f"SHIP_{order_id}",
                order_id=order_id,
                status=random.choice(["DELIVERED", "IN_TRANSIT", "PENDING"]),
                shipped_at=order_date + timedelta(days=random.randint(1, 5))
            ))
