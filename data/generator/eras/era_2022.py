import os
from data.generator.domains.universe import DataUniverse
from data.generator.exporters.json_exporter import export_to_json
from data.generator.core.mapping import IDMapper
from data.generator.artifacts.spark import generate_2022_spark_artifacts

class Era2022:
    def __init__(self, universe: DataUniverse, output_dir: str):
        self.universe = universe
        self.output_dir = os.path.join(output_dir, "2022_lake")
        
    def generate(self):
        self._generate_customer_features()
        generate_2022_spark_artifacts(os.path.join(self.output_dir, "..", "..", "artifacts", "spark"))
        print(f"Generated 2022 Era datasets in {self.output_dir}")
        
    def _generate_customer_features(self):
        # Calculate customer transaction totals
        customer_totals = {}
        for o in self.universe.orders:
            cid = IDMapper.to_uuid(o.customer_id)
            customer_totals[cid] = customer_totals.get(cid, 0) + o.total_amount_cents
            
        data = []
        for c in self.universe.customers:
            cid = IDMapper.to_uuid(c.internal_id)
            total_cents = customer_totals.get(cid, 0)
            data.append({
                "customer_id": cid,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "customer_transaction_total": round(total_cents / 100.0, 2),
                "is_active": True
            })
            
        # Simulate partitioned parquet output
        out_file = os.path.join(self.output_dir, "customer_features", "year=2022", "month=01", "part-0000.parquet.json")
        export_to_json(data, out_file)
