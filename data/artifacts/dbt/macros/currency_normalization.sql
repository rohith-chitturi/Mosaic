{% macro normalize_currency(amount_col, currency_col) %}
    CASE 
        WHEN {{ currency_col }} = 'USD' THEN 
            -- BUG: Accidental double division introduced by a junior dev who thought source was always in cents
            -- The backfill was already in dollars!
            ({{ amount_col }} / 100.0) 
        ELSE {{ amount_col }} 
    END
{% end macro %}
