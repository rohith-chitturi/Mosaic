import os
import json

def generate_graphql_artifacts(output_dir: str, nosql_dir: str, base_output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Write schema.graphql
    schema_path = os.path.join(output_dir, "schema.graphql")
    with open(schema_path, "w", encoding='utf-8') as f:
        f.write("""type Customer {
    customerId: ID!
    name: String
    lifetimeValue: Float
    orders: [Order!]
}

type Order {
    orderId: ID!
    totalValue: Float
    items: [OrderItem!]
}

type OrderItem {
    productRef: String!
    quantity: Int!
    unitPrice: Float!
}

type Query {
    customer(id: ID!): Customer
}
""")

    # 2. Generate api_query_logs.jsonl
    # We will pick a few customers, read their CLV from warehouse and their orders from NoSQL, and composite them.
    logs_path = os.path.join(output_dir, "api_query_logs.jsonl")
    
    warehouse_customers_path = os.path.join(base_output_dir, "2025_warehouse", "core", "dim_customers.csv")
    nosql_orders_path = os.path.join(nosql_dir, "orders_collection.jsonl")
    
    clv_map = {}
    if os.path.exists(warehouse_customers_path):
        import csv
        with open(warehouse_customers_path, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["is_current"] == "True":
                    clv_map[row["customer_nk"]] = float(row["customer_lifetime_value"])
                    
    orders_map = {}
    if os.path.exists(nosql_orders_path):
        with open(nosql_orders_path, "r", encoding='utf-8') as f:
            for line in f:
                doc = json.loads(line)
                cref = doc.get("customerRef")
                if cref not in orders_map:
                    orders_map[cref] = []
                orders_map[cref].append({
                    "orderId": doc.get("orderId"),
                    "totalValue": doc.get("totalValue"),
                    "items": doc.get("items") or doc.get("lineItems")
                })
                
    with open(logs_path, "w", encoding='utf-8') as f:
        # Generate 5 sample logs
        c_nks = list(clv_map.keys())[:5]
        for c_nk in c_nks:
            response = {
                "data": {
                    "customer": {
                        "customerId": c_nk,
                        "lifetimeValue": clv_map[c_nk],
                        "orders": orders_map.get(c_nk, [])
                    }
                }
            }
            log_entry = {
                "query": f"query {{ customer(id: \"{c_nk}\") {{ customerId lifetimeValue orders {{ orderId totalValue items {{ productRef quantity unitPrice }} }} }} }}",
                "response": response
            }
            f.write(json.dumps(log_entry) + "\n")
