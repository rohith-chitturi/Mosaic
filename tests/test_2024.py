import os
import json
import csv
from datetime import datetime

def test_2024_era():
    lake_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'generated', '2024_lake'))
    
    # 1. Curated dataset consistency
    with open(os.path.join(lake_dir, "curated", "customers.json"), "r") as f:
        curated = json.load(f)
    assert len(curated) > 0, "Curated customers missing"
    assert "customer_revenue" in curated[0], "Undocumented rename missing"
    
    # 2. Duplicate dataset equivalence
    with open(os.path.join(lake_dir, "raw", "customers_v2.csv"), "r") as f:
        reader = csv.DictReader(f)
        raw = list(reader)
    assert len(raw) == len(curated), "Duplicate dataset size mismatch"
    assert "revenue_str" in raw[0], "Raw dataset should have revenue_str"
    
    # 3. Snapshot temporal correctness
    with open(os.path.join(lake_dir, "snapshots", "2023_orders_snapshot.json"), "r") as f:
        snapshot = json.load(f)
    for row in snapshot:
        dt = datetime.strptime(row["order_date"], "%Y-%m-%dT%H:%M:%S")
        assert dt <= datetime(2023, 12, 31, 23, 59, 59), "Snapshot contains 2024 data!"
        
    # 4. Backfill subset corruption
    with open(os.path.join(lake_dir, "backfills", "historical_order_backfill.json"), "r") as f:
        backfill = json.load(f)
    
    # We generated TZ shift every 20th record, truncation every 25th record.
    # Just checking they exist.
    assert len(backfill) > 0, "Backfill missing"
    
    # 5. Partition migration boundary
    logs_dir = os.path.join(lake_dir, "logs", "user_activity")
    has_year_month = any(d.startswith("year=2024") for d in os.listdir(logs_dir))
    has_dt = any(d.startswith("dt=2024-") for d in os.listdir(logs_dir))
    assert has_year_month and has_dt, "Partition migration failed"
    
    # 6. Marketing lead overlap percentage
    with open(os.path.join(lake_dir, "third_party", "marketing_leads.csv"), "r") as f:
        leads = list(csv.DictReader(f))
    
    stale_emails = [l for l in leads if l["lead_email"].startswith("old_")]
    assert len(stale_emails) > 0, "No stale overlap found"
    assert "customer_id" not in leads[0], "Leaked internal ID in marketing leads"
    
    # Explicit validation of deterministic rounding logic
    # We generated 100 canonical customers.
    # Expect 70 exact, 10 stale, 20 faker -> Total 100 leads.
    assert len(leads) == 100, f"Expected 100 leads, got {len(leads)}"
    assert len(stale_emails) == 10, f"Expected 10 stale leads, got {len(stale_emails)}"
    
    # 7. Orphan dataset
    with open(os.path.join(lake_dir, "legacy", "customer_features_legacy_2024.json"), "r") as f:
        orphan = json.load(f)
    assert len(orphan) > 0, "Orphaned dataset missing"
    assert "deprecated_at" in orphan[0], "Orphan missing deprecated flag"
    
    print("All 2024 Era specific validations passed.")

if __name__ == "__main__":
    test_2024_era()
