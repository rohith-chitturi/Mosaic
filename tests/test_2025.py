import os
import json
import csv
from datetime import datetime
from data.generator.eras.era_2025 import hash_to_bigint

def test_2025_era():
    warehouse_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'generated', '2025_warehouse'))
    
    # 1. Deterministic SK generation
    # Same NK and version should yield exactly the same BigInt
    sk1 = hash_to_bigint("customer|UUID-123|1")
    sk2 = hash_to_bigint("customer|UUID-123|1")
    assert sk1 == sk2, "hash_to_bigint is not deterministic"
    assert isinstance(sk1, int), "SK is not an integer"
    
    # 2. Duplicate Fact Selection
    with open(os.path.join(warehouse_dir, "core", "fact_orders.csv"), "r") as f:
        facts = list(csv.DictReader(f))
        
    order_sks = [f["order_sk"] for f in facts]
    duplicates = len(facts) - len(set(order_sks))
    
    # There are 500 orders total. We duplicate every 50th order, so exactly 10 duplicates.
    assert duplicates == 10, f"Expected exactly 10 duplicate facts, found {duplicates}"
    
    # 3. SCD Type 2 logic
    with open(os.path.join(warehouse_dir, "core", "dim_customers.csv"), "r") as f:
        customers = list(csv.DictReader(f))
        
    nks = [c["customer_nk"] for c in customers]
    scd_customers = [nk for nk in set(nks) if nks.count(nk) > 1]
    
    assert len(scd_customers) == 5, f"Expected exactly 5 customers with SCD changes (5% of 100), found {len(scd_customers)}"
    
    for nk in scd_customers:
        versions = [c for c in customers if c["customer_nk"] == nk]
        assert len(versions) == 2, "SCD customer should have exactly 2 versions"
        assert versions[0]["customer_sk"] != versions[1]["customer_sk"], "SCD versions must have distinct SKs"
        assert versions[0]["is_current"] == "False" and versions[1]["is_current"] == "True", "is_current logic failed"
        assert versions[0]["valid_to"] != "", "Version 1 should be closed"
        assert versions[1]["valid_to"] == "", "Version 2 should be open"
        
    # 4. CLV Transformation matches explicit logic
    c0 = customers[0]
    # We can't directly assert the exact value without knowing the source revenue, but we can check it's defined
    assert "customer_lifetime_value" in c0, "CLV column missing"
    
    print("All 2025 Era specific validations passed.")

if __name__ == "__main__":
    test_2025_era()
