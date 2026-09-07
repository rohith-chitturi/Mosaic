-- Dimension Customers (SCD Type 2 snapshot logic simulated)
SELECT
    customer_sk,
    customer_nk,
    LOWER(TRIM(email)) AS email,
    -- Genuine Metric Transformation: CLV
    -- revenue from 2024 lake minus 5% historical returns reserve
    (customer_revenue - (customer_revenue * 0.05)) AS customer_lifetime_value,
    valid_from,
    valid_to,
    is_current
FROM {{ ref('stg_customers_scd2') }}
