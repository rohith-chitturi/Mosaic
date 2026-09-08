import os

def generate_2018_migration(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    sql = """
-- 2018 PostgreSQL Migration
-- Moving customers and orders to the new system, leaving products in legacy MySQL.

CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(customer_id),
    amount DECIMAL(12,2),
    order_date TIMESTAMP
);

-- Migration logic excerpt
-- INSERT INTO customers (customer_id, first_name, last_name, email, phone, created_at)
-- SELECT UUID_GENERATE_V5(namespace, cust_id::TEXT), split_part(name, ' ', 1), split_part(name, ' ', 2), email, phone_number, created_at FROM legacy_customers;
-- 
-- INSERT INTO orders (order_id, customer_id, amount, order_date)
-- SELECT UUID_GENERATE_V5(namespace, order_id::TEXT), UUID_GENERATE_V5(namespace, cust_id::TEXT), amount_cents / 100.0, order_date FROM legacy_orders;
"""
    with open(os.path.join(output_dir, "2018_postgres_migration.sql"), "w") as f:
        f.write(sql)

def generate_2024_sql_artifacts(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    sql = """
-- 2024 Curated Customer Join
-- Creates the gold curated customer table from Postgres and Data Lake.

CREATE TABLE curated_customers AS
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email AS email_address,
    c.phone,
    f.customer_transaction_total AS customer_revenue, -- Undocumented rename!
    TRUE AS is_active,
    CURRENT_TIMESTAMP AS curated_at
FROM postgres_customers c
LEFT JOIN lake_customer_features f ON c.customer_id = f.customer_id;
"""
    with open(os.path.join(output_dir, "2024_curated_customer.sql"), "w") as f:
        f.write(sql)
