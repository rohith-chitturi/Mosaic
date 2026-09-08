-- Staging orders from 2024 Lake Backfill
SELECT
    order_id AS order_nk,
    customer_id AS customer_nk,
    amount,
    currency,
    event_timestamp AS order_date
FROM {{ source('lake', 'historical_order_backfill') }}
