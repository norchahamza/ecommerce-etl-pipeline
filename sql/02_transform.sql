-- Staging -> star schema. Safe to re-run (upserts).
INSERT INTO dw.dim_customer (customer_id, full_name, email, country, signup_date)
SELECT customer_id, full_name, email, country, signup_date FROM staging.stg_customers
ON CONFLICT (customer_id) DO UPDATE SET
    full_name = EXCLUDED.full_name, email = EXCLUDED.email,
    country = EXCLUDED.country, signup_date = EXCLUDED.signup_date;

INSERT INTO dw.dim_product (product_id, product_name, category, unit_price)
SELECT product_id, product_name, category, unit_price FROM staging.stg_products
ON CONFLICT (product_id) DO UPDATE SET
    product_name = EXCLUDED.product_name, category = EXCLUDED.category,
    unit_price = EXCLUDED.unit_price;

INSERT INTO dw.dim_date (date_key, full_date, year, quarter, month, month_name, day_of_week, is_weekend)
SELECT to_char(d, 'YYYYMMDD')::int, d::date,
       EXTRACT(YEAR FROM d)::int, EXTRACT(QUARTER FROM d)::int, EXTRACT(MONTH FROM d)::int,
       trim(to_char(d, 'Month')), EXTRACT(ISODOW FROM d)::int, EXTRACT(ISODOW FROM d) IN (6, 7)
FROM generate_series('2023-01-01'::date, '2026-12-31'::date, interval '1 day') AS d
ON CONFLICT (date_key) DO NOTHING;

INSERT INTO dw.fact_sales (order_item_id, order_id, customer_key, product_key, date_key,
                           quantity, unit_price, discount, total_amount, status)
SELECT i.order_item_id, i.order_id, c.customer_key, p.product_key,
       to_char(o.order_date, 'YYYYMMDD')::int,
       i.quantity, i.unit_price, i.discount,
       ROUND(i.quantity * i.unit_price * (1 - i.discount), 2), o.status
FROM staging.stg_order_items i
JOIN staging.stg_orders o   ON o.order_id = i.order_id
JOIN dw.dim_customer c      ON c.customer_id = o.customer_id
JOIN dw.dim_product p       ON p.product_id = i.product_id
ON CONFLICT (order_item_id) DO UPDATE SET
    quantity = EXCLUDED.quantity, unit_price = EXCLUDED.unit_price,
    discount = EXCLUDED.discount, total_amount = EXCLUDED.total_amount,
    status = EXCLUDED.status;
