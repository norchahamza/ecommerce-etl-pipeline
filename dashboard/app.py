import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
DB_URL = os.getenv("DATABASE_URL",
                   "postgresql+psycopg2://etl_user:etl_pass@localhost:5432/ecommerce")

st.set_page_config(page_title="E-Commerce Analytics", layout="wide")
st.title("E-Commerce Analytics Dashboard")


@st.cache_data(ttl=60)
def q(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, create_engine(DB_URL))


monthly = q("SELECT * FROM dw.v_monthly_revenue")
rfm = q("SELECT * FROM dw.v_customer_rfm")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"{monthly['revenue'].sum():,.0f} €")
c2.metric("Orders", f"{monthly['orders'].sum():,}")
c3.metric("Avg order value", f"{monthly['revenue'].sum() / monthly['orders'].sum():,.2f} €")
c4.metric("Active customers", f"{len(rfm):,}")

st.subheader("Monthly revenue")
st.plotly_chart(px.line(monthly, x="month", y="revenue", markers=True), use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Revenue by category")
    st.plotly_chart(px.pie(q("SELECT * FROM dw.v_category_revenue"),
                           names="category", values="revenue"), use_container_width=True)
with right:
    st.subheader("Revenue by country")
    st.plotly_chart(px.bar(q("SELECT * FROM dw.v_country_revenue ORDER BY revenue DESC"),
                           x="country", y="revenue"), use_container_width=True)

st.subheader("Top 10 products")
st.dataframe(q("SELECT * FROM dw.v_top_products ORDER BY revenue_rank LIMIT 10"),
             use_container_width=True)

st.subheader("Customer segments (RFM)")
seg = rfm.groupby("segment", as_index=False).agg(customers=("customer_key", "count"),
                                                 revenue=("monetary", "sum"))
st.plotly_chart(px.bar(seg, x="segment", y="customers", color="segment"),
                use_container_width=True)
