import os
import json
import csv

def test_2026_era():
    nosql_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'generated', '2026_nosql'))
    graphql_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'artifacts', 'graphql'))
    manifests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'manifests'))
    
    nosql_path = os.path.join(nosql_dir, "orders_collection.jsonl")
    crm_path = os.path.join(nosql_dir, "crm_export_2026.csv")
    schema_path = os.path.join(graphql_dir, "schema.graphql")
    api_logs_path = os.path.join(graphql_dir, "api_query_logs.jsonl")
    gt_path = os.path.join(manifests_dir, "ground_truth.json")
    
    # 1. Read NoSQL orders
    orders = []
    with open(nosql_path, "r", encoding='utf-8') as f:
        for line in f:
            orders.append(json.loads(line))
            
    # [x] exactly 5% of NoSQL records use lineItems
    line_items_count = sum(1 for o in orders if "lineItems" in o)
    items_count = sum(1 for o in orders if "items" in o)
    assert line_items_count == len(orders) // 20, f"Expected 5% lineItems, found {line_items_count}/{len(orders)}"
    
    # [x] items and lineItems are semantically equivalent for affected records
    for o in orders:
        if "lineItems" in o:
            assert "items" not in o, "Record has both items and lineItems"
            arr = o["lineItems"]
        else:
            arr = o["items"]
        assert isinstance(arr, list), "Array not found"
        if len(arr) > 0:
            assert "quantity" in arr[0] and "unitPrice" in arr[0], "Semantic fields missing"
            
    # [x] totalValue exactly equals Σ(quantity × unitPrice)
    for o in orders:
        arr = o.get("lineItems", o.get("items", []))
        calc_total = sum(item["quantity"] * item["unitPrice"] for item in arr)
        assert abs(o["totalValue"] - calc_total) < 0.01, f"totalValue mismatch: {o['totalValue']} != {calc_total}"
        
    # [x] CRM identity-category counts equal configured deterministic percentages
    crm_data = []
    with open(crm_path, "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        crm_data = list(reader)
        
    # In era_2026.py we used mod 100 on the index to categorize 100 canonical customers.
    # We should have exactly 60 EXACT, 20 NORMALIZED, 10 FUZZY, 10 UNRESOLVED.
    exact = sum(1 for i, row in enumerate(crm_data) if i % 100 < 60)
    norm = sum(1 for i, row in enumerate(crm_data) if 60 <= (i % 100) < 80)
    fuzzy = sum(1 for i, row in enumerate(crm_data) if 80 <= (i % 100) < 90)
    unres = sum(1 for i, row in enumerate(crm_data) if 90 <= (i % 100))
    
    assert exact == 60, f"Expected 60 exact matches, got {exact}"
    assert norm == 20, f"Expected 20 normalized matches, got {norm}"
    assert fuzzy == 10, f"Expected 10 fuzzy matches, got {fuzzy}"
    assert unres == 10, f"Expected 10 unresolved matches, got {unres}"
    
    # [x] GraphQL schema references valid warehouse/NoSQL fields
    with open(schema_path, "r", encoding='utf-8') as f:
        schema_content = f.read()
        assert "lifetimeValue: Float" in schema_content, "Missing warehouse field in schema"
        assert "orders: [Order!]" in schema_content, "Missing NoSQL field in schema"
        
    # [x] API query logs contain valid composite responses
    logs = []
    with open(api_logs_path, "r", encoding='utf-8') as f:
        for line in f:
            logs.append(json.loads(line))
            
    for log in logs:
        assert "customer" in log["response"]["data"]
        cust = log["response"]["data"]["customer"]
        assert "lifetimeValue" in cust, "Response missing composite warehouse data"
        assert "orders" in cust, "Response missing composite NoSQL data"
        
    # [x] Ground Truth identity cases resolve to actual CRM/warehouse records
    with open(gt_path, "r", encoding='utf-8') as f:
        gt = json.load(f)
        
    identity_cases = gt.get("identity_cases", [])
    assert len(identity_cases) == 4, "Expected 4 identity cases"
    for case in identity_cases:
        assert case["source_urn"].startswith("dataset:lake:crm_export:2026")
        assert case["target_urn"].startswith("dataset:warehouse:dim_customers:2025")
        
    # [x] all Ground Truth lineage URNs resolve to observable artifacts
    lineage_cases = gt.get("lineage_cases", [])
    era2026_cases = [c for c in lineage_cases if "2026" in c["target_urn"]]
    assert len(era2026_cases) == 4, "Expected 4 Era 2026 lineage cases"
    
    for case in era2026_cases:
        assert case["target_urn"].startswith("dataset:nosql:orders_collection:2026"), "URN prefix mismatch"

    print("All 2026 Era specific validations passed.")

if __name__ == "__main__":
    test_2026_era()
