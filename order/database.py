import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure your docker-compose or .env has this URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/micro_db")

def get_db_conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)