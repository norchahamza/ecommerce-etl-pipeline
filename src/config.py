import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SQL_DIR = ROOT / "sql"
DB_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://etl_user:etl_pass@localhost:5432/ecommerce"
)
