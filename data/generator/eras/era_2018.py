import os
from data.generator.domains.universe import DataUniverse
from data.generator.exporters.json_exporter import export_to_json
from data.generator.core.mapping import IDMapper
from data.generator.artifacts.sql import generate_2018_migration

class Era2018:
    def __init__(self, universe: DataUniverse, output_dir: str):
        self.universe = universe
        self.output_dir = os.path.join(output_dir, "2018_postgres")
        
    def generate(self):
        self._generate_customers()
        self._generate_orders()
        generate_2018_migration(os.path.join(self.output_dir, "..", "..", "artifacts", "sql"))
        print(f"Generated 2018 Era datasets in {self.output_dir}")
        
    def _generate_customers(self):
        data = []
        for c in self.universe.customers:
            # 2018 Era Schema: customer_id (UUID), first_name, last_name, email, phone
            data.append({
                "customer_id": IDMapper.to_uuid(c.internal_id),
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "phone": c.phone,
                "created_at": c.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            })
        export_to_json(data, os.path.join(self.output_dir, "customers.json"))
        
    def _generate_orders(self):
        data = []
        for o in self.universe.orders:
            data.append({
                "order_id": IDMapper.to_uuid(o.internal_id),
                "customer_id": IDMapper.to_uuid(o.customer_id),
                "amount": round(o.total_amount_cents / 100.0, 2),
                "order_date": o.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            })
        export_to_json(data, os.path.join(self.output_dir, "orders.json"))
