"""ETL entry point: CSV -> clean (pandas) -> staging (Postgres) -> star schema (SQL)."""
import logging

import pandas as pd
from sqlalchemy import create_engine, text

from src import transform as t
from src.config import DB_URL, RAW_DIR, SQL_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("etl")


def extract() -> dict:
    raw = {n: pd.read_csv(RAW_DIR / f"{n}.csv")
           for n in ["customers", "products", "orders", "order_items"]}
    for n, df in raw.items():
        log.info("extract %-12s %6d rows", n, len(df))
    return raw


def transform(raw: dict) -> dict:
    customers = t.clean_customers(raw["customers"])
    products = t.clean_products(raw["products"])
    orders = t.clean_orders(raw["orders"], set(customers["customer_id"]))
    items = t.clean_order_items(raw["order_items"], set(orders["order_id"]),
                                set(products["product_id"]))
    clean = {"stg_customers": customers, "stg_products": products,
             "stg_orders": orders, "stg_order_items": items}
    for n, df in clean.items():
        log.info("transform %-16s %6d rows", n, len(df))
    return clean


def run_sql_file(engine, name: str):
    log.info("running %s", name)
    with engine.begin() as conn:
        conn.exec_driver_sql((SQL_DIR / name).read_text())


def load(clean: dict, engine):
    run_sql_file(engine, "01_schema.sql")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE staging.stg_order_items, staging.stg_orders, "
                          "staging.stg_products, staging.stg_customers"))
        # parents first, then children
        for name in ["stg_customers", "stg_products", "stg_orders", "stg_order_items"]:
            clean[name].to_sql(name, conn, schema="staging", if_exists="append",
                               index=False, method="multi", chunksize=1000)
    run_sql_file(engine, "02_transform.sql")
    run_sql_file(engine, "03_analytics_views.sql")


def main():
    engine = create_engine(DB_URL)
    load(transform(extract()), engine)
    with engine.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM dw.fact_sales")).scalar()
    log.info("done: dw.fact_sales has %d rows", n)


if __name__ == "__main__":
    main()
