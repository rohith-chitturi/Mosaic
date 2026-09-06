import os
import json
from data.generator.domains.universe import DataUniverse
from data.generator.core.mapping import IDMapper

def generate_ground_truth(universe: DataUniverse, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    lineage_cases = []
    data_quality_cases = []
    
    # 2016 -> 2018
    for c in universe.customers[:3]: 
        lineage_cases.append({
            "case_id": f"GT-CUST-{c.internal_id}",
            "source_era": "2016",
            "target_era": "2018",
            "source_urn": f"dataset:mysql:customers:2016:v1:column:cust_id",
            "target_urn": f"dataset:postgres:customers:2018:v1:column:customer_id",
            "relationship": "TRANSFORMED_FROM", # Was MIGRATED_TO, aligned to domain model
            "evidence_profile": ["NAME_SIMILARITY", "VALUE_OVERLAP", "TEMPORAL_ALIGNMENT"],
            "transformation": "IDMapper.to_uuid()",
            "notes": "Standard customer migration"
        })
        
    for o in universe.orders[:3]:
        lineage_cases.append({
            "case_id": f"GT-ORD-{o.internal_id}",
            "source_era": "2016",
            "target_era": "2018",
            "source_urn": f"dataset:mysql:orders:2016:v1:column:amount_cents",
            "target_urn": f"dataset:postgres:orders:2018:v1:column:amount",
            "relationship": "TRANSFORMED_FROM",
            "evidence_profile": ["SCHEMA_SIMILARITY"],
            "transformation": "amount_cents / 100.0",
            "notes": "Decimal conversion"
        })
        
    # 2018 -> 2022
    for c in universe.customers[:3]:
        lineage_cases.append({
            "case_id": f"GT-LAKE-{c.internal_id}",
            "source_era": "2018",
            "target_era": "2022",
            "source_urn": f"dataset:postgres:orders:2018:v1:column:amount",
            "target_urn": f"dataset:lake:customer_features:2022:v1:column:customer_transaction_total",
            "relationship": "DERIVED_FROM",
            "evidence_profile": ["SPARK_ARTIFACT_REFERENCE"],
            "transformation": "SUM(amount) GROUP BY customer_id",
            "notes": "Derived aggregation field"
        })
        
    # 2024 Era Scenarios
    # 1. Undocumented Rename
    lineage_cases.append({
        "case_id": "GT-RENAME-REVENUE",
        "source_urn": "dataset:lake:customer_features:2022:v1:column:customer_transaction_total",
        "target_urn": "dataset:lake:curated_customers:2024:v1:column:customer_revenue",
        "relationship": "RENAMED_FROM",
        "notes": "Exact same underlying mathematical aggregation, undocumented rename."
    })
    
    # 2. Equivalent Duplicate
    lineage_cases.append({
        "case_id": "GT-DUPLICATE-CUSTOMERS",
        "source_urn": "dataset:lake:curated_customers:2024:v1",
        "target_urn": "dataset:lake:raw_customers_v2:2024:v1",
        "relationship": "EQUIVALENT_TO",
        "notes": "Different schema order and format, but identical business records."
    })
    
    # 3. Genuine Snapshot
    lineage_cases.append({
        "case_id": "GT-SNAPSHOT-ORDERS",
        "source_urn": "dataset:postgres:orders:2018:v1",
        "target_urn": "dataset:lake:2023_orders_snapshot:2024:v1",
        "relationship": "SNAPSHOT_OF",
        "notes": "Snapshot captured explicitly at 2023-12-31 cutoff."
    })
    
    # 4. Partial Overlap (Marketing Leads)
    lineage_cases.append({
        "case_id": "GT-OVERLAP-LEADS",
        "source_urn": "dataset:postgres:customers:2018:v1",
        "target_urn": "dataset:lake:marketing_leads:2024:v1",
        "relationship": "PARTIAL_OVERLAP",
        "notes": "Deterministic 70% exact match, 10% stale match, 20% distinct."
    })
    
    # 5. Data Quality Cases (Backfill Corruption & Orphaned)
    data_quality_cases.append({
        "scenario_id": "BACKFILL_TZ_SHIFT_001",
        "affected_dataset": "dataset:lake:historical_order_backfill:2024:v1",
        "description": "Deterministic timezone shift from UTC to UTC+05:00 for ~5% of records",
        "status": "CONTRADICTED_BY"
    })
    
    data_quality_cases.append({
        "scenario_id": "BACKFILL_TRUNCATION_001",
        "affected_dataset": "dataset:lake:historical_order_backfill:2024:v1",
        "description": "Amount cast to integer truncating decimals for ~4% of records",
        "status": "CONTRADICTED_BY"
    })
    
    data_quality_cases.append({
        "scenario_id": "ORPHANED_LEGACY_FEATURES_001",
        "affected_dataset": "dataset:lake:customer_features_legacy_2024:2024:v1",
        "description": "Valid historical data that is no longer consumed.",
        "status": "ORPHANED"
    })

    ground_truth = {
        "lineage_cases": lineage_cases,
        "data_quality_cases": data_quality_cases
    }
        
    with open(os.path.join(output_dir, "ground_truth.json"), "w", encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=2)
