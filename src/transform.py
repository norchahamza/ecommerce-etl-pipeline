"""Pure-pandas cleaning functions (easy to unit test, no DB needed)."""
import pandas as pd

VALID_STATUS = {"completed", "cancelled", "returned", "pending"}


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["full_name"] = df["full_name"].str.strip()
    df["email"] = df["email"].str.strip().str.lower()
    df["country"] = df["country"].str.strip().str.title().replace({"Usa": "USA"})
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    return df.dropna(subset=["customer_id"]).drop_duplicates("customer_id", keep="first")


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["product_name"] = df["product_name"].str.strip()
    df["category"] = df["category"].str.strip().str.title()
    df = df[df["unit_price"] > 0]
    return df.drop_duplicates("product_id", keep="first")


def clean_orders(df: pd.DataFrame, valid_customer_ids) -> pd.DataFrame:
    df = df.copy()
    df["status"] = df["status"].str.strip().str.lower()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])
    df = df[df["status"].isin(VALID_STATUS) & df["customer_id"].isin(valid_customer_ids)]
    return df.drop_duplicates("order_id", keep="first")


def clean_order_items(df: pd.DataFrame, valid_order_ids, valid_product_ids) -> pd.DataFrame:
    df = df.copy()
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
    df["discount"] = df["discount"].fillna(0).clip(0, 1)
    df = df[df["order_id"].isin(valid_order_ids) & df["product_id"].isin(valid_product_ids)]
    return df.drop_duplicates("order_item_id", keep="first")
