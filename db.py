# db.py
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        sslmode=os.getenv("PGSSLMODE","require"),
        port=int(os.getenv("PGPORT","5432"))
    )
