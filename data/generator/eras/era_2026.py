import os
import json
import random
import csv
from typing import List, Dict, Any
from data.generator.domains.universe import DataUniverse
from data.generator.core.mapping import IDMapper
from data.generator.exporters.csv_exporter import export_to_csv

class Era2026:
    def __init__(self, universe: DataUniverse, output_dir: str):
        self.universe = universe
        self.base_output_dir = output_dir
        self.output_dir = os.path.join(output_dir, "2026_nosql")
        self.rng = random.Random(2026)
        
    def generate(self):
        self._generate_nosql_orders()
        self._generate_crm_export()
        
        from data.generator.artifacts.graphql import generate_graphql_artifacts
        generate_graphql_artifacts(os.path.join(self.output_dir, "..", "..", "artifacts", "graphql"), self.output_dir, self.base_output_dir)
        print(f"Generated 2026 Era datasets in {self.output_dir}")

    def _generate_nosql_orders(self):
        os.makedirs(self.output_dir, exist_ok=True)
        nosql_path = os.path.join(self.output_dir, "orders_collection.jsonl")
        
        with open(nosql_path, "w", encoding='utf-8') as f:
            for i, order in enumerate(self.universe.orders):
                order_id = IDMapper.to_uuid(order.internal_id)
                customer_ref = IDMapper.to_uuid(order.customer_id)
                
                # Fetch order items from canonical universe
                items = []
                for item in self.universe.order_items:
                    if item.order_id == order.internal_id:
                        prod_int_id = int(item.product_id.split('_')[1]) + 5000
                        items.append({
                            "productRef": str(prod_int_id),
                            "quantity": item.quantity,
                            "unitPrice": round(item.unit_price_cents / 100.0, 2)
                        })
                
                # Calculate totalValue as sum of items.quantity * items.unitPrice
                total_value = sum(item["quantity"] * item["unitPrice"] for item in items)
                total_value = round(total_value, 2)
                
                # 5% Schema Drift Anomaly (NOSQL_ORDER_SCHEMA_DRIFT_001)
                doc = {
                    "orderId": order_id,
                    "customerRef": customer_ref,
                    "totalValue": total_value
                }
                
                if i % 20 == 0:
                    doc["lineItems"] = items
                else:
                    doc["items"] = items
                    
                f.write(json.dumps(doc) + "\n")

    def _generate_crm_export(self):
        crm_path = os.path.join(self.output_dir, "crm_export_2026.csv")
        crm_data = []
        
        # Read from canonical to generate names, but apply identity matching rules
        for i, customer in enumerate(self.universe.customers):
            # Identity Rules: 60% EXACT, 20% NORMALIZED, 10% FUZZY, 10% UNRESOLVED
            # 0-59 (mod 100): EXACT
            # 60-79: NORMALIZED
            # 80-89: FUZZY
            # 90-99: UNRESOLVED
            rem = i % 100
            
            email = customer.email.lower()
            first = customer.first_name
            last = customer.last_name
            phone = customer.phone
            
            if rem < 60: # EXACT
                pass
            elif rem < 80: # NORMALIZED
                email = email.upper() # Change casing
                phone = phone.replace("-", "").replace(".", "") + " ext 1"
            elif rem < 90: # FUZZY
                # Typo in email and name
                if len(email) > 5:
                    email = email[:3] + email[4:] # drop 4th char
                first = first[:len(first)-1] # drop last char
                last = last + "son"
            else: # UNRESOLVED
                # Missing email or completely ambiguous
                email = ""
                if i % 2 == 0:
                    first = "John"
                    last = "Doe"
                    
            crm_data.append({
                "crm_id": f"CRM-{1000+i}",
                "first_name": first,
                "last_name": last,
                "email_address": email,
                "phone": phone
            })
            
        export_to_csv(crm_data, crm_path)
