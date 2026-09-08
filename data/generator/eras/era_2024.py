import os
import random
from datetime import datetime, timedelta
from typing import List, Dict
from data.generator.domains.universe import DataUniverse
from data.generator.exporters.json_exporter import export_to_json
from data.generator.exporters.csv_exporter import export_to_csv
from data.generator.core.mapping import IDMapper
from data.generator.artifacts.spark import generate_2024_spark_artifacts
from data.generator.artifacts.sql import generate_2024_sql_artifacts

class Era2024:
    def __init__(self, universe: DataUniverse, output_dir: str):
        self.universe = universe
        self.output_dir = os.path.join(output_dir, "2024_lake")
        # Ensure deterministic randomness for 2024 specific data
        self.rng = random.Random(42)
        
    def generate(self):
        self._generate_curated_customers()
        self._generate_orders_snapshot()
        self._generate_historical_backfill()
        self._generate_user_activity_logs()
        self._generate_marketing_leads()
        self._generate_orphaned_dataset()
        
        generate_2024_sql_artifacts(os.path.join(self.output_dir, "..", "..", "artifacts", "sql"))
        generate_2024_spark_artifacts(os.path.join(self.output_dir, "..", "..", "artifacts", "spark"))
        print(f"Generated 2024 Era datasets in {self.output_dir}")

    def _generate_curated_customers(self):
        # 1. Curated Customers (Join 2018 Postgres Identity + 2022 Lake Aggregations)
        # Undocumented rename: customer_transaction_total -> customer_revenue
        customer_totals = {}
        for o in self.universe.orders:
            cid = IDMapper.to_uuid(o.customer_id)
            customer_totals[cid] = customer_totals.get(cid, 0) + o.total_amount_cents

        curated = []
        raw_duplicate = []
        for c in self.universe.customers:
            cid = IDMapper.to_uuid(c.internal_id)
            total_cents = customer_totals.get(cid, 0)
            revenue = round(total_cents / 100.0, 2)
            
            curated_record = {
                "customer_id": cid,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email_address": c.email, # slight rename from email
                "phone": c.phone,
                "customer_revenue": revenue, # renamed from customer_transaction_total
                "is_active": True,
                "curated_at": "2024-05-01T12:00:00"
            }
            curated.append(curated_record)
            
            # 2. Realistic Duplicate (different order, stringified numbers, alternate nulls)
            raw_record = {
                "id": cid,
                "revenue_str": f"{revenue:.2f}",
                "contact_email": c.email,
                "fname": c.first_name,
                "lname": c.last_name,
                "phone_num": c.phone if c.phone else "N/A"
            }
            raw_duplicate.append(raw_record)
            
        export_to_json(curated, os.path.join(self.output_dir, "curated", "customers.json"))
        export_to_csv(raw_duplicate, os.path.join(self.output_dir, "raw", "customers_v2.csv"))

    def _generate_orders_snapshot(self):
        # 3. Genuine Temporal Snapshot (2023-12-31 cutoff)
        cutoff = datetime(2023, 12, 31, 23, 59, 59)
        snapshot = []
        for o in self.universe.orders:
            if o.created_at <= cutoff:
                snapshot.append({
                    "order_id": IDMapper.to_uuid(o.internal_id),
                    "customer_id": IDMapper.to_uuid(o.customer_id),
                    "amount": round(o.total_amount_cents / 100.0, 2),
                    "order_date": o.created_at.strftime("%Y-%m-%dT%H:%M:%S")
                })
        export_to_json(snapshot, os.path.join(self.output_dir, "snapshots", "2023_orders_snapshot.json"))

    def _generate_historical_backfill(self):
        # 4. Historical Backfill with controlled anomalies
        # Based on 2020 Kafka order_events_v2
        backfill = []
        
        # Sort to ensure deterministic subsetting
        sorted_orders = sorted(self.universe.orders, key=lambda x: x.internal_id)
        
        for i, o in enumerate(sorted_orders):
            record = {
                "schema_version": "v2",
                "order_id": IDMapper.to_uuid(o.internal_id),
                "customer_id": IDMapper.to_uuid(o.customer_id),
                "amount": round(o.total_amount_cents / 100.0, 2),
                "currency": "USD",
                "event_timestamp": o.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            # Deterministic anomalies based on index modulo
            if i % 20 == 0:
                # BACKFILL_TZ_SHIFT_001 (+5 hours)
                shifted = o.created_at + timedelta(hours=5)
                record["event_timestamp"] = shifted.strftime("%Y-%m-%dT%H:%M:%S")
                record["anomaly"] = "TZ_SHIFT" # just for generator truth, won't output in real prod but we need ground truth mapping
                # wait, DO NOT leak anomaly into data!
                del record["anomaly"]
                
                shifted = o.created_at + timedelta(hours=5)
                record["event_timestamp"] = shifted.strftime("%Y-%m-%dT%H:%M:%S")
            elif i % 25 == 0:
                # BACKFILL_TRUNCATION_001 (truncate decimal to int)
                record["amount"] = float(int(o.total_amount_cents / 100))
                
            backfill.append(record)
            
        export_to_json(backfill, os.path.join(self.output_dir, "backfills", "historical_order_backfill.json"))

    def _generate_user_activity_logs(self):
        # 5. Partition Evolution
        # Mock some logs
        pre_migration = []
        post_migration = []
        
        # April 1, 2024 is the boundary
        boundary = datetime(2024, 4, 1)
        
        for i in range(100):
            event_date = datetime(2024, 1, 1) + timedelta(days=self.rng.randint(0, 180))
            record = {
                "log_id": f"LOG-{i:05d}",
                "customer_id": IDMapper.to_uuid(f"CUST_{self.rng.randint(0,99):05d}"),
                "action": self.rng.choice(["login", "view", "click"]),
                "timestamp": event_date.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            if event_date < boundary:
                month_str = f"{event_date.month:02d}"
                export_to_json([record], os.path.join(self.output_dir, "logs", "user_activity", f"year=2024", f"month={month_str}", f"log_{i}.json"))
            else:
                dt_str = event_date.strftime("%Y-%m-%d")
                export_to_json([record], os.path.join(self.output_dir, "logs", "user_activity", f"dt={dt_str}", f"log_{i}.json"))

    def _generate_marketing_leads(self):
        # 6. Partial Overlap (70% exact, 10% stale, 20% faker)
        leads = []
        total = len(self.universe.customers)
        # Rounding rule: Use integer floor (int()) for deterministic counts
        exact_count = int(total * 0.70)
        stale_count = int(total * 0.10)
        # New count uses subtraction to guarantee exact total preservation regardless of rounding
        new_count = total - exact_count - stale_count
        
        # 70% Exact matches
        for c in self.universe.customers[:exact_count]:
            leads.append({
                "campaign_id": "CAMP_2024_01",
                "lead_email": c.email,
                "lead_phone": c.phone,
                "full_name": f"{c.first_name} {c.last_name}"
            })
            
        # 10% Stale/Ambiguous
        for c in self.universe.customers[exact_count:exact_count+stale_count]:
            leads.append({
                "campaign_id": "CAMP_2024_01",
                "lead_email": f"old_{c.email}", # explicitly stale
                "lead_phone": "", # missing phone
                "full_name": f"{c.first_name} {c.last_name}"
            })
            
        # 20% New Leads
        from faker import Faker
        faker = Faker()
        faker.seed_instance(42)
        for i in range(new_count):
            leads.append({
                "campaign_id": "CAMP_2024_01",
                "lead_email": faker.email(),
                "lead_phone": faker.phone_number(),
                "full_name": faker.name()
            })
            
        export_to_csv(leads, os.path.join(self.output_dir, "third_party", "marketing_leads.csv"))

    def _generate_orphaned_dataset(self):
        # 7. Orphaned/Deprecated Dataset
        # Same as 2022 features but stale schema
        data = []
        for c in self.universe.customers[:10]:
            cid = IDMapper.to_uuid(c.internal_id)
            data.append({
                "customer_uuid": cid,
                "metric_total": 500.00,
                "deprecated_at": "2023-01-01T00:00:00"
            })
        export_to_json(data, os.path.join(self.output_dir, "legacy", "customer_features_legacy_2024.json"))
