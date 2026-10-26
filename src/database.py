
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    # First, check local environment variables.
    database_url = os.getenv("DATABASE_URL")

    # In Streamlit Cloud, read the connection from app Secrets.
    if not database_url:
        try:
            import streamlit as st
            database_url = st.secrets.get("DATABASE_URL")
        except Exception:
            database_url = None

    # Use Neon when DATABASE_URL is configured.
    if database_url:
        return psycopg.connect(
            database_url,
            connect_timeout=10,
        )

    # Otherwise, use your existing local PostgreSQL database.
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "fraud_detection_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )


def test_connection():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            database, user = cur.fetchone()

    print(f"Connected successfully to database: {database}")
    print(f"Connected as PostgreSQL user: {user}")


if __name__ == "__main__":
    test_connection()
