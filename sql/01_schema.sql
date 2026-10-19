-- Staging (landing zone) + Data Warehouse (star schema). Idempotent.
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS staging.stg_customers (
    customer_id INT PRIMARY KEY, full_name TEXT, email TEXT, country TEXT, signup_date DATE);
CREATE TABLE IF NOT EXISTS staging.stg_products (
    product_id INT PRIMARY KEY, product_name TEXT, category TEXT, unit_price NUMERIC(10,2));
CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id INT PRIMARY KEY, customer_id INT, order_date DATE, status TEXT);
CREATE TABLE IF NOT EXISTS staging.stg_order_items (
    order_item_id INT PRIMARY KEY, order_id INT, product_id INT,
    quantity INT, unit_price NUMERIC(10,2), discount NUMERIC(4,2));

CREATE TABLE IF NOT EXISTS dw.dim_customer (
    customer_key SERIAL PRIMARY KEY, customer_id INT NOT NULL UNIQUE,
    full_name TEXT, email TEXT, country TEXT, signup_date DATE);
CREATE TABLE IF NOT EXISTS dw.dim_product (
    product_key SERIAL PRIMARY KEY, product_id INT NOT NULL UNIQUE,
    product_name TEXT, category TEXT, unit_price NUMERIC(10,2));
CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key INT PRIMARY KEY, full_date DATE NOT NULL, year INT, quarter INT,
    month INT, month_name TEXT, day_of_week INT, is_weekend BOOLEAN);
CREATE TABLE IF NOT EXISTS dw.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    order_item_id INT NOT NULL UNIQUE,
    order_id INT NOT NULL,
    customer_key INT NOT NULL REFERENCES dw.dim_customer(customer_key),
    product_key INT NOT NULL REFERENCES dw.dim_product(product_key),
    date_key INT NOT NULL REFERENCES dw.dim_date(date_key),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(4,2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(12,2) NOT NULL,
    status TEXT NOT NULL);

CREATE INDEX IF NOT EXISTS ix_fact_customer ON dw.fact_sales (customer_key);
CREATE INDEX IF NOT EXISTS ix_fact_product  ON dw.fact_sales (product_key);
CREATE INDEX IF NOT EXISTS ix_fact_date     ON dw.fact_sales (date_key);
