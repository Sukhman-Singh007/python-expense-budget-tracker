import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "expenses.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            expense_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY,
            amount REAL NOT NULL CHECK(amount > 0)
        );

        CREATE INDEX IF NOT EXISTS idx_expenses_date
        ON expenses(expense_date);

        CREATE INDEX IF NOT EXISTS idx_expenses_category
        ON expenses(category);
        """)
