"""Generate a realistic (and deliberately dirty) e-commerce dataset as CSV files."""
import numpy as np
import pandas as pd

from src.config import RAW_DIR

COUNTRIES = ["France", "Italy", "Germany", "Spain", "United Kingdom", "USA"]
CATEGORIES = {"Electronics": (30, 900), "Home": (10, 300), "Books": (5, 40),
              "Clothing": (15, 150), "Sports": (10, 250)}


def generate(n_customers=500, n_products=60, n_orders=3000, seed=42):
    rng = np.random.default_rng(seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    customers = pd.DataFrame({
        "customer_id": range(1, n_customers + 1),
        "full_name": [f"Customer {i}" for i in range(1, n_customers + 1)],
        "email": [f"customer{i}@example.com" for i in range(1, n_customers + 1)],
        "country": rng.choice(COUNTRIES, n_customers),
        "signup_date": pd.Timestamp("2023-01-01")
        + pd.to_timedelta(rng.integers(0, 700, n_customers), unit="D"),
    })
    # --- dirty data on purpose ---
    customers.loc[:19, "email"] = customers.loc[:19, "email"].str.upper() + " "
    customers.loc[20:29, "email"] = None
    customers.loc[30:44, "country"] = customers.loc[30:44, "country"].str.lower()
    customers = pd.concat([customers, customers.iloc[:10]], ignore_index=True)  # duplicates

    cats = rng.choice(list(CATEGORIES), n_products)
    products = pd.DataFrame({
        "product_id": range(1, n_products + 1),
        "product_name": [f"{c} Item {i}" for i, c in enumerate(cats, 1)],
        "category": cats,
        "unit_price": [round(rng.uniform(*CATEGORIES[c]), 2) for c in cats],
    })

    order_ids = np.arange(1, n_orders + 1)
    cust_ids = rng.integers(1, n_customers + 1, n_orders)
    cust_ids[:15] = 9999  # orphan customers
    orders = pd.DataFrame({
        "order_id": order_ids,
        "customer_id": cust_ids,
        "order_date": pd.Timestamp("2024-01-01")
        + pd.to_timedelta(rng.integers(0, 730, n_orders), unit="D"),
        "status": rng.choice(["completed", "cancelled", "returned", "pending"],
                             n_orders, p=[0.85, 0.07, 0.05, 0.03]),
    })
    orders.loc[:49, "status"] = orders.loc[:49, "status"].str.upper()  # inconsistent case

    rows, item_id = [], 1
    price = products.set_index("product_id")["unit_price"]
    for oid in order_ids:
        for pid in rng.choice(products["product_id"], rng.integers(1, 5), replace=False):
            rows.append((item_id, oid, pid, int(rng.integers(1, 6)), price[pid],
                         float(rng.choice([0, 0, 0, 0.05, 0.1, 0.2]))))
            item_id += 1
    items = pd.DataFrame(rows, columns=["order_item_id", "order_id", "product_id",
                                        "quantity", "unit_price", "discount"])
    items.loc[:24, "quantity"] = -1  # invalid quantities

    for name, df in [("customers", customers), ("products", products),
                     ("orders", orders), ("order_items", items)]:
        df.to_csv(RAW_DIR / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows")


if __name__ == "__main__":
    generate()
