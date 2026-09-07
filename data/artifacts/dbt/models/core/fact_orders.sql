-- Fact Orders
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
