import os
import hashlib
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
from data.generator.domains.universe import DataUniverse
from data.generator.exporters.json_exporter import export_to_json
from data.generator.exporters.csv_exporter import export_to_csv
from data.generator.core.mapping import IDMapper
import random

def hash_to_bigint(value_str: str) -> int:
    """Deterministic hashing to 64-bit unsigned integer."""
    # MD5 hash of canonical UTF-8 string
    hash_obj = hashlib.md5(value_str.encode('utf-8'))
    # Take first 8 bytes (64 bits) and convert to unsigned int
    return int.from_bytes(hash_obj.digest()[:8], byteorder='big', signed=False)

class Era2025:
    def __init__(self, universe: DataUniverse, output_dir: str):
        self.universe = universe
        self.output_dir = os.path.join(output_dir, "2025_warehouse")
        self.rng = random.Random(2025) # specific seed for 2025 anomalies
        
    def generate(self):
        self._generate_dim_products()
        self._generate_dim_customers()
        self._generate_dim_date()
        self._generate_fact_orders()
        self._generate_mart_monthly_revenue()
        
        from data.generator.artifacts.dbt import generate_2025_dbt_artifacts
        generate_2025_dbt_artifacts(os.path.join(self.output_dir, "..", "..", "artifacts", "dbt"))
        print(f"Generated 2025 Era warehouse datasets in {self.output_dir}")

    def _generate_dim_products(self):
        # Rescue 2016 MySQL products
        dim_products = []
        for p in self.universe.products:
            # The 2016 mysql product_id was an integer (e.g. 5001 + index)
            # In mapping, we used `p.internal_id` directly for MySQL but let's simulate the NK correctly
            # In 2016 era, product ID was int(p.internal_id.split('_')[1]) + 5000
            product_nk = str(int(p.internal_id.split('_')[1]) + 5000)
            product_sk = hash_to_bigint(f"product|{product_nk}")
            
            dim_products.append({
                "product_sk": product_sk,
                "product_nk": product_nk,
                "product_name": p.name,
                "category": p.category,
                "warehouse_created_at": "2025-01-01T00:00:00"
            })
            
        export_to_csv(dim_products, os.path.join(self.output_dir, "core", "dim_products.csv"))

    def _generate_dim_customers(self):
        # Customer dimension with SCD Type 2
        dim_customers = []
        
        # Calculate base CLV (from 2024 revenue)
        customer_totals = {}
        for o in self.universe.orders:
            cid = IDMapper.to_uuid(o.customer_id)
            customer_totals[cid] = customer_totals.get(cid, 0) + o.total_amount_cents
            
        for i, c in enumerate(self.universe.customers):
            customer_nk = IDMapper.to_uuid(c.internal_id)
            total_cents = customer_totals.get(customer_nk, 0)
            revenue = round(total_cents / 100.0, 2)
            
            # Genuine metric transformation: CLV = revenue - 5% returns reserve
            clv = round(revenue * 0.95, 2)
            
            # Version 1 (Base)
            v1_sk = hash_to_bigint(f"customer|{customer_nk}|1")
            
            # Determine if this customer gets an SCD change (5% of customers)
            has_scd2_change = (i % 20 == 0)
            
            if has_scd2_change:
                # Version 1 valid up to mid-2024
                dim_customers.append({
                    "customer_sk": v1_sk,
                    "customer_nk": customer_nk,
                    "email": c.email.lower().strip(),
                    "customer_lifetime_value": clv,
                    "valid_from": "2018-01-01T00:00:00",
                    "valid_to": "2024-06-30T23:59:59",
                    "is_current": False
                })
                
                # Version 2 (Current) with a new email
                v2_sk = hash_to_bigint(f"customer|{customer_nk}|2")
                new_email = "updated_" + c.email.lower().strip()
                dim_customers.append({
                    "customer_sk": v2_sk,
                    "customer_nk": customer_nk,
                    "email": new_email,
                    "customer_lifetime_value": clv,
                    "valid_from": "2024-07-01T00:00:00",
                    "valid_to": None,
                    "is_current": True
                })
            else:
                # Only 1 version
                dim_customers.append({
                    "customer_sk": v1_sk,
                    "customer_nk": customer_nk,
                    "email": c.email.lower().strip(),
                    "customer_lifetime_value": clv,
                    "valid_from": "2018-01-01T00:00:00",
                    "valid_to": None,
                    "is_current": True
                })
                
        export_to_csv(dim_customers, os.path.join(self.output_dir, "core", "dim_customers.csv"))

    def _generate_dim_date(self):
        dim_date = []
        start_date = datetime(2016, 1, 1)
        for i in range(365 * 10): # 10 years of dates
            dt = start_date + timedelta(days=i)
            date_sk = hash_to_bigint(f"date|{dt.strftime('%Y-%m-%d')}")
            dim_date.append({
                "date_sk": date_sk,
                "full_date": dt.strftime('%Y-%m-%d'),
                "year": dt.year,
                "month": dt.month,
                "day": dt.day
            })
        export_to_csv(dim_date, os.path.join(self.output_dir, "core", "dim_date.csv"))

    def _generate_fact_orders(self):
        fact_orders = []
        
        # Sort for determinism
        sorted_orders = sorted(self.universe.orders, key=lambda x: x.internal_id)
        
        for i, o in enumerate(sorted_orders):
            order_nk = IDMapper.to_uuid(o.internal_id)
            order_sk = hash_to_bigint(f"order|{order_nk}")
            
            customer_nk = IDMapper.to_uuid(o.customer_id)
            
            # The order maps to the customer SK that was valid at the time of the order
            # But for simplicity, we map to the appropriate SK based on date
            # Or just use the base customer_nk to get the v1 or v2 SK.
            has_scd2_change = (int(o.customer_id.split('_')[1]) % 20 == 0)
            if has_scd2_change and o.created_at > datetime(2024, 6, 30):
                customer_sk = hash_to_bigint(f"customer|{customer_nk}|2")
            else:
                customer_sk = hash_to_bigint(f"customer|{customer_nk}|1")
                
            date_sk = hash_to_bigint(f"date|{o.created_at.strftime('%Y-%m-%d')}")
            
            # Find the product
            # In canonical model, orders have order_items. We'll pick the first item's product for this denormalized simple fact table
            # Or we can just join to product_sk.
            # In CanonicalInternalModel, Order doesn't have direct products, OrderItem does.
            # For simplicity of this warehouse fact, we will assign a dummy product if missing, but we shouldn't.
            # We'll just look up the first item if available, else a default 2016 product.
            # Actually, OrderItems are in self.universe.order_items.
            items = [item for item in self.universe.order_items if item.order_id == o.internal_id]
            if items:
                prod_internal = items[0].product_id
                product_nk = str(int(prod_internal.split('_')[1]) + 5000)
                product_sk = hash_to_bigint(f"product|{product_nk}")
            else:
                product_sk = hash_to_bigint(f"product|5001")
            
            # Base amount from backfill (which was already in dollars but maybe had truncation!)
            # The backfill had 1234.78 for normal, and 1234 for truncated. We'll just use the canonical total_cents to derive what 2024 lake had.
            # Normal amount in backfill:
            lake_amount = round(o.total_amount_cents / 100.0, 2)
            if i % 25 == 0:
                # Mimic the truncation from 2024 backfill
                lake_amount = float(int(o.total_amount_cents / 100))
                
            order_amount_usd = lake_amount
            
            # The dbt Currency Macro Bug (DBT_CURRENCY_MACRO_BUG_001)
            # 5% of records double divided by 100
            if i % 20 == 0:
                order_amount_usd = round(order_amount_usd / 100.0, 4)
                
            fact_record = {
                "order_sk": order_sk,
                "order_nk": order_nk,
                "customer_sk": customer_sk,
                "product_sk": product_sk,
                "order_date_sk": date_sk,
                "quantity": sum(item.quantity for item in items) if items else 1,
                "order_amount_usd": order_amount_usd,
                "currency": "USD"
            }
            
            fact_orders.append(fact_record)
            
            # Incremental Load Duplicate Issue (WAREHOUSE_DUPLICATE_FACT_001)
            if i % 50 == 0:
                fact_orders.append(fact_record.copy())
                
        export_to_csv(fact_orders, os.path.join(self.output_dir, "core", "fact_orders.csv"))

    def _generate_mart_monthly_revenue(self):
        # Aggregation of fact_orders
        # For simplicity in generator, we'll just read from the facts we just generated
        # Group by year-month and sum order_amount_usd
        # We need to map date_sk back to year-month.
        import collections
        monthly_rev = collections.defaultdict(float)
        
        # Reconstruct the date map for fast lookup
        date_map = {}
        start_date = datetime(2016, 1, 1)
        for i in range(365 * 10):
            dt = start_date + timedelta(days=i)
            sk = hash_to_bigint(f"date|{dt.strftime('%Y-%m-%d')}")
            date_map[sk] = dt.strftime('%Y-%m')
            
        fact_orders_path = os.path.join(self.output_dir, "core", "fact_orders.csv")
        with open(fact_orders_path, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                d_sk = int(row["order_date_sk"])
                amount = float(row["order_amount_usd"])
                ym = date_map.get(d_sk, "UNKNOWN")
                monthly_rev[ym] += amount
                
        mart = []
        for ym, rev in sorted(monthly_rev.items()):
            mart.append({
                "revenue_month": ym,
                "total_revenue_usd": round(rev, 2)
            })
            
        export_to_csv(mart, os.path.join(self.output_dir, "marts", "mart_monthly_revenue.csv"))
