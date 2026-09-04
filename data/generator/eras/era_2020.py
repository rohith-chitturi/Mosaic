from typing import List, Dict
import os
import copy
from data.generator.domains.universe import DataUniverse
from data.generator.exporters.json_exporter import export_to_json
from data.generator.core.mapping import IDMapper

class Era2020:
    def __init__(self, universe: DataUniverse, output_dir: str):
        self.universe = universe
        self.output_dir = os.path.join(output_dir, "2020_kafka")
        
    def generate(self):
        self._generate_customer_events_v1()
        self._generate_customer_events_v2()
        self._generate_order_events_v1()
        self._generate_order_events_v2()
        self._generate_payment_events_v1()
        print(f"Generated 2020 Era datasets in {self.output_dir}")
        
    def _generate_customer_events_v1(self):
        data = []
        for c in self.universe.customers:
            data.append({
                "schema_version": "v1",
                "customer_id": IDMapper.to_uuid(c.internal_id),
                "name": f"{c.first_name} {c.last_name}",
                "event_timestamp": c.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            })
        export_to_json(data, os.path.join(self.output_dir, "customer_events_v1.json"))

    def _generate_customer_events_v2(self):
        data = []
        for c in self.universe.customers:
            data.append({
                "schema_version": "v2",
                "customer_id": IDMapper.to_uuid(c.internal_id),
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "event_timestamp": c.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            })
        export_to_json(data, os.path.join(self.output_dir, "customer_events_v2.json"))
        
    def _generate_order_events_v1(self):
        data = []
        for o in self.universe.orders:
            data.append({
                "schema_version": "v1",
                "order_id": IDMapper.to_uuid(o.internal_id),
                "customer_id": IDMapper.to_uuid(o.customer_id),
                "amount": round(o.total_amount_cents / 100.0, 2),
                "event_timestamp": o.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            })
        export_to_json(data, os.path.join(self.output_dir, "order_events_v1.json"))
        
    def _generate_order_events_v2(self):
        data = []
        for o in self.universe.orders:
            data.append({
                "schema_version": "v2",
                "order_id": IDMapper.to_uuid(o.internal_id),
                "customer_id": IDMapper.to_uuid(o.customer_id),
                "amount": round(o.total_amount_cents / 100.0, 2),
                "currency": "USD",
                "event_timestamp": o.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            })
        export_to_json(data, os.path.join(self.output_dir, "order_events_v2.json"))

    def _generate_payment_events_v1(self):
        data = []
        for p in self.universe.payments:
            data.append({
                "schema_version": "v1",
                "payment_id": IDMapper.to_uuid(p.internal_id),
                "order_id": IDMapper.to_uuid(p.order_id),
                "amount": round(p.amount_cents / 100.0, 2),
                "method": p.payment_method,
                "event_timestamp": p.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            })
        export_to_json(data, os.path.join(self.output_dir, "payment_events_v1.json"))
