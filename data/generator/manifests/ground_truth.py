import os
import json
from data.generator.domains.universe import DataUniverse
from data.generator.core.mapping import IDMapper

def generate_ground_truth(universe: DataUniverse, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    cases = []
    
    for c in universe.customers[:5]: 
        cases.append({
            "case_id": f"GT-CUST-{c.internal_id}",
            "case_type": "POSITIVE",
            "difficulty": "EASY",
            "source_era": "2016",
            "target_era": "2018",
            "source_urn": f"dataset:mysql:customers:2016:v1:column:cust_id",
            "target_urn": f"dataset:postgres:customers:2018:v1:column:customer_id",
            "relationship": "MIGRATED_TO",
            "expected": True,
            "evidence_profile": ["NAME_SIMILARITY", "VALUE_OVERLAP", "TEMPORAL_ALIGNMENT"],
            "transformation": "IDMapper.to_uuid()",
            "notes": "Standard customer migration"
        })
        
    for o in universe.orders[:5]:
        cases.append({
            "case_id": f"GT-ORD-{o.internal_id}",
            "case_type": "POSITIVE",
            "difficulty": "MEDIUM",
            "source_era": "2016",
            "target_era": "2018",
            "source_urn": f"dataset:mysql:orders:2016:v1:column:amount_cents",
            "target_urn": f"dataset:postgres:orders:2018:v1:column:amount",
            "relationship": "TRANSFORMED_FROM",
            "expected": True,
            "evidence_profile": ["SCHEMA_SIMILARITY"],
            "transformation": "amount_cents / 100.0",
            "notes": "Decimal conversion"
        })
        
    for c in universe.customers[:5]:
        cases.append({
            "case_id": f"GT-LAKE-{c.internal_id}",
            "case_type": "POSITIVE",
            "difficulty": "HARD",
            "source_era": "2018",
            "target_era": "2022",
            "source_urn": f"dataset:postgres:orders:2018:v1:column:amount",
            "target_urn": f"dataset:lake:customer_features:2022:v1:column:customer_transaction_total",
            "relationship": "DERIVED_FROM",
            "expected": True,
            "evidence_profile": ["SPARK_ARTIFACT_REFERENCE"],
            "transformation": "SUM(amount) GROUP BY customer_id",
            "notes": "Derived aggregation field"
        })
        
    with open(os.path.join(output_dir, "ground_truth.json"), "w", encoding='utf-8') as f:
        json.dump(cases, f, indent=2)
