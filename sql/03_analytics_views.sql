-- Analytics layer. Revenue = completed orders only.
CREATE OR REPLACE VIEW dw.v_monthly_revenue AS
WITH m AS (
    SELECT d.year, d.month, MIN(d.full_date) AS month_start,
           SUM(f.total_amount) AS revenue, COUNT(DISTINCT f.order_id) AS orders
    FROM dw.fact_sales f JOIN dw.dim_date d ON d.date_key = f.date_key
    WHERE f.status = 'completed' GROUP BY d.year, d.month)
SELECT date_trunc('month', month_start)::date AS month,
       ROUND(revenue, 2)::float8 AS revenue, orders,
       ROUND(revenue / orders, 2)::float8 AS avg_order_value,
       ROUND(100.0 * (revenue - LAG(revenue) OVER w) / NULLIF(LAG(revenue) OVER w, 0), 1)::float8 AS mom_growth_pct
FROM m WINDOW w AS (ORDER BY year, month)
ORDER BY month;

CREATE OR REPLACE VIEW dw.v_top_products AS
SELECT p.product_name, p.category, SUM(f.quantity)::int AS units,
       ROUND(SUM(f.total_amount), 2)::float8 AS revenue,
       RANK() OVER (ORDER BY SUM(f.total_amount) DESC) AS revenue_rank
FROM dw.fact_sales f JOIN dw.dim_product p ON p.product_key = f.product_key
WHERE f.status = 'completed'
GROUP BY p.product_key, p.product_name, p.category;

CREATE OR REPLACE VIEW dw.v_category_revenue AS
SELECT p.category, ROUND(SUM(f.total_amount), 2)::float8 AS revenue,
       ROUND(100.0 * SUM(f.total_amount) / SUM(SUM(f.total_amount)) OVER (), 1)::float8 AS share_pct
FROM dw.fact_sales f JOIN dw.dim_product p ON p.product_key = f.product_key
WHERE f.status = 'completed' GROUP BY p.category;

CREATE OR REPLACE VIEW dw.v_country_revenue AS
SELECT c.country, ROUND(SUM(f.total_amount), 2)::float8 AS revenue,
       COUNT(DISTINCT f.customer_key) AS customers
FROM dw.fact_sales f JOIN dw.dim_customer c ON c.customer_key = f.customer_key
WHERE f.status = 'completed' GROUP BY c.country;

CREATE OR REPLACE VIEW dw.v_customer_rfm AS
WITH base AS (
    SELECT c.customer_key, c.full_name, c.country, MAX(d.full_date) AS last_order,
           COUNT(DISTINCT f.order_id) AS frequency, SUM(f.total_amount) AS monetary
    FROM dw.fact_sales f
    JOIN dw.dim_customer c ON c.customer_key = f.customer_key
    JOIN dw.dim_date d ON d.date_key = f.date_key
    WHERE f.status = 'completed'
    GROUP BY c.customer_key, c.full_name, c.country),
scored AS (
    SELECT b.*, (SELECT MAX(last_order) FROM base) - b.last_order AS recency_days,
           NTILE(4) OVER (ORDER BY (SELECT MAX(last_order) FROM base) - b.last_order DESC) AS r_score,
           NTILE(4) OVER (ORDER BY b.frequency) AS f_score,
           NTILE(4) OVER (ORDER BY b.monetary) AS m_score
    FROM base b)
SELECT customer_key, full_name, country, last_order, recency_days, frequency,
       ROUND(monetary, 2)::float8 AS monetary, r_score, f_score, m_score,
       CASE WHEN r_score >= 3 AND f_score >= 3 THEN 'Champions'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At risk'
            WHEN r_score >= 3 THEN 'Recent'
            ELSE 'Low value' END AS segment
FROM scored;
