import psycopg2, os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    dbname="postgres",
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    sslmode=os.getenv("PGSSLMODE","require"),
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("CREATE DATABASE avataresdb;")
print(" BD avataresdb creada")
conn.close()
