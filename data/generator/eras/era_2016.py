from typing import List, Dict
import os
from data.generator.domains.universe import DataUniverse
from data.generator.exporters.csv_exporter import export_to_csv
from data.generator.core.mapping import IDMapper

class Era2016:
    def __init__(self, universe: DataUniverse, output_dir: str):
        self.universe = universe
        self.output_dir = os.path.join(output_dir, "2016_mysql")
        
    def generate(self):
        self._generate_customers()
        self._generate_orders()
        self._generate_products()
        print(f"Generated 2016 Era datasets in {self.output_dir}")
        
    def _generate_customers(self):
        data = []
        for c in self.universe.customers:
            # 2016 Era Schema: cust_id, name, email, phone_number, created_at
            cust_id = IDMapper.to_legacy_int(c.internal_id)
            data.append({
                "cust_id": cust_id,
                "name": f"{c.first_name} {c.last_name}",
                "email": c.email,
                "phone_number": c.phone,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        export_to_csv(data, os.path.join(self.output_dir, "customers.csv"))
        
    def _generate_orders(self):
        data = []
        for o in self.universe.orders:
            # orders logic
            order_id = IDMapper.to_legacy_int(o.internal_id)
            cust_id = IDMapper.to_legacy_int(o.customer_id)
            data.append({
                "order_id": order_id,
                "cust_id": cust_id,
                "amount_cents": o.total_amount_cents,
                "order_date": o.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        export_to_csv(data, os.path.join(self.output_dir, "orders.csv"))
        
    def _generate_products(self):
        data = []
        for p in self.universe.products:
            prod_id = IDMapper.to_legacy_int(p.internal_id)
            data.append({
                "prod_id": prod_id,
                "title": p.name,
                "category": p.category,
                "price_cents": p.price_cents
            })
        export_to_csv(data, os.path.join(self.output_dir, "products.csv"))
