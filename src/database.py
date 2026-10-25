
import os

import psycopg
from dotenv import load_dotenv

# Load database settings from the project's .env file
load_dotenv()


def get_connection():
    """Connect to the fraud detection PostgreSQL database."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "fraud_detection_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )


def test_connection():
    """Check which database and user Python connected to."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            database, user = cur.fetchone()

    print(f"Connected successfully to database: {database}")
    print(f"Connected as PostgreSQL user: {user}")


if __name__ == "__main__":
    test_connection()
