import pandas as pd

from src import transform as t


def test_clean_customers_normalises_and_dedups():
    df = pd.DataFrame({
        "customer_id": [1, 1, 2], "full_name": [" A ", " A ", "B"],
        "email": [" A@X.COM ", " A@X.COM ", None],
        "country": ["usa", "usa", "france"], "signup_date": ["2024-01-01"] * 3})
    out = t.clean_customers(df)
    assert len(out) == 2
    assert out.iloc[0]["email"] == "a@x.com"
    assert out.iloc[0]["country"] == "USA"


def test_clean_orders_drops_orphans_and_lowercases_status():
    df = pd.DataFrame({"order_id": [1, 2], "customer_id": [1, 999],
                       "order_date": ["2024-05-01"] * 2, "status": ["COMPLETED", "completed"]})
    out = t.clean_orders(df, {1})
    assert list(out["order_id"]) == [1]
    assert out.iloc[0]["status"] == "completed"


def test_clean_items_drops_invalid_quantity_and_clips_discount():
    df = pd.DataFrame({"order_item_id": [1, 2], "order_id": [1, 1], "product_id": [1, 1],
                       "quantity": [-1, 2], "unit_price": [10.0, 10.0], "discount": [0.0, 1.5]})
    out = t.clean_order_items(df, {1}, {1})
    assert len(out) == 1 and out.iloc[0]["discount"] == 1.0
