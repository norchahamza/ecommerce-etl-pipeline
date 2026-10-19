# E-Commerce ETL & Analytics Pipeline (SQL + Python + PostgreSQL)

End-to-end data pipeline: raw CSV files → cleaning in **pandas** → **staging** tables in PostgreSQL → **star schema** built with SQL → analytics views → **Streamlit** dashboard.

## Architecture

```
CSV (dirty) ──► Python: extract + clean ──► PostgreSQL staging ──► SQL upserts ──► star schema (dw)
                                                                                      │
                                                          analytics views (window functions, RFM)
                                                                                      │
                                                                             Streamlit dashboard
```

**Star schema:** `fact_sales` + `dim_customer`, `dim_product`, `dim_date`.

**Analytics views:** monthly revenue with MoM growth (`LAG`), top products (`RANK`), category share, revenue by country, customer RFM segmentation (`NTILE`).

**Data quality rules:** deduplication, e-mail/country/status normalisation, removal of orphan orders, invalid quantities and prices, discount clipping.

## Quick start

```bash
git clone https://github.com/<your-user>/ecommerce-etl-pipeline.git
cd ecommerce-etl-pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

docker compose up -d        # PostgreSQL 16
python -m src.generate_data # synthetic dirty dataset -> data/raw
python -m src.etl           # run the pipeline (idempotent)
streamlit run dashboard/app.py
pytest -q                   # unit tests on the cleaning logic
```

## Structure

```
sql/        01_schema.sql · 02_transform.sql · 03_analytics_views.sql
src/        generate_data.py · transform.py · etl.py · config.py
dashboard/  app.py
tests/      test_transform.py
```

## Possible extensions
Orchestration with Airflow/Prefect, incremental loads, dbt models, CI with GitHub Actions.
