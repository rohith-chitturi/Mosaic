import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.generator.domains.universe import DataUniverse
import hashlib

def test_referential_integrity():
    print("Running referential integrity tests...")
    u = DataUniverse(seed=42, scale="small")
    u.generate_canonical_only()
    
    # Extract IDs for fast lookup
    cust_ids = {c.internal_id for c in u.customers}
    order_ids = {o.internal_id for o in u.orders}
    prod_ids = {p.internal_id for p in u.products}
    item_ids = {i.internal_id for i in u.order_items}
    
    for o in u.orders:
        assert o.customer_id in cust_ids, f"Order {o.internal_id} references invalid customer {o.customer_id}"
        
    for i in u.order_items:
        assert i.order_id in order_ids, f"OrderItem {i.internal_id} references invalid order {i.order_id}"
        assert i.product_id in prod_ids, f"OrderItem {i.internal_id} references invalid product {i.product_id}"
        
    for p in u.payments:
        assert p.order_id in order_ids, f"Payment {p.internal_id} references invalid order {p.order_id}"
        
    for s in u.shipments:
        assert s.order_id in order_ids, f"Shipment {s.internal_id} references invalid order {s.order_id}"
        
    for r in u.returns:
        assert r.order_item_id in item_ids, f"Return {r.internal_id} references invalid item {r.order_item_id}"

    print("Referential integrity tests passed.")

def hash_universe(u: DataUniverse) -> str:
    # A simple way to hash the canonical model
    h = hashlib.sha256()
    for c in u.customers:
        h.update(c.internal_id.encode())
        h.update(c.email.encode())
    for o in u.orders:
        h.update(o.internal_id.encode())
        h.update(str(o.total_amount_cents).encode())
    return h.hexdigest()

def test_determinism():
    print("Running determinism tests...")
    u1 = DataUniverse(seed=42, scale="small")
    u1.generate_canonical_only()
    h1 = hash_universe(u1)
    
    u2 = DataUniverse(seed=42, scale="small")
    u2.generate_canonical_only()
    h2 = hash_universe(u2)
    
    u3 = DataUniverse(seed=43, scale="small")
    u3.generate_canonical_only()
    h3 = hash_universe(u3)
    
    assert h1 == h2, "Determinism failed! Same seed produced different hashes."
    assert h1 != h3, "Determinism failed! Different seeds produced identical hashes."
    print("Determinism tests passed.")

if __name__ == "__main__":
    test_referential_integrity()
    test_determinism()
    print("All canonical tests passed!")
