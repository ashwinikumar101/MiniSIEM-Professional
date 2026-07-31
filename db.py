import sqlite3
import psycopg2

from config import Config

def get_connection():
    """
    Returns a database connection.
    Uses PostgreSQL if DATABASE_URL exists.
    Otherwise uses SQLite.
    """

    if Config.DATABASE_URL:
        print("🐘 Connected to PostgreSQL")
        return psycopg2.connect(Config.DATABASE_URL)

    print("📁 Connected to SQLite")
    return sqlite3.connect("database/siem.db")