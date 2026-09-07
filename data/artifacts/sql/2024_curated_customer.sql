
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
