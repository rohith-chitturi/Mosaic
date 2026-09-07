import os

def generate_2025_dbt_artifacts(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # Write dbt_project.yml
    with open(os.path.join(output_dir, "dbt_project.yml"), "w") as f:
        f.write("""name: 'meridian_warehouse'
version: '1.0.0'
config-version: 2
profile: 'meridian'
model-paths: ["models"]
macro-paths: ["macros"]
""")

    # Write staging models
    os.makedirs(os.path.join(output_dir, "models", "staging"), exist_ok=True)
    with open(os.path.join(output_dir, "models", "staging", "stg_orders.sql"), "w") as f:
        f.write("""-- Staging orders from 2024 Lake Backfill
SELECT
    order_id AS order_nk,
    customer_id AS customer_nk,
    amount,
    currency,
    event_timestamp AS order_date
FROM {{ source('lake', 'historical_order_backfill') }}
""")

    # Write core models
    os.makedirs(os.path.join(output_dir, "models", "core"), exist_ok=True)
    with open(os.path.join(output_dir, "models", "core", "dim_customers.sql"), "w") as f:
        f.write("""-- Dimension Customers (SCD Type 2 snapshot logic simulated)
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
""")

    with open(os.path.join(output_dir, "models", "core", "fact_orders.sql"), "w") as f:
        f.write("""-- Fact Orders
SELECT
    {{ generate_sk('order', 'order_nk') }} AS order_sk,
    order_nk,
    customer_sk,
    product_sk,
    date_sk AS order_date_sk,
    quantity,
    -- Here is the macro invocation
    {{ normalize_currency('amount', 'currency') }} AS order_amount_usd,
    'USD' AS currency
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_customers') }} c ON o.customer_nk = c.customer_nk
LEFT JOIN {{ ref('dim_products') }} p ON o.product_nk = p.product_nk
LEFT JOIN {{ ref('dim_date') }} d ON o.order_date = d.full_date
""")

    # Write macro with the bug
    os.makedirs(os.path.join(output_dir, "macros"), exist_ok=True)
    with open(os.path.join(output_dir, "macros", "currency_normalization.sql"), "w") as f:
        f.write("""{% macro normalize_currency(amount_col, currency_col) %}
    CASE 
        WHEN {{ currency_col }} = 'USD' THEN 
            -- BUG: Accidental double division introduced by a junior dev who thought source was always in cents
            -- The backfill was already in dollars!
            ({{ amount_col }} / 100.0) 
        ELSE {{ amount_col }} 
    END
{% end macro %}
""")
