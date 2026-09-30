from datetime import datetime
from database import get_connection


def validate_date(value):
    datetime.strptime(value, "%Y-%m-%d")


def add_expense(amount, category, description, expense_date):
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    validate_date(expense_date)
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO expenses(amount, category, description, expense_date)
               VALUES (?, ?, ?, ?)""",
            (amount, category.strip() or "Other", description.strip(), expense_date),
        )
        return cursor.lastrowid


def list_expenses():
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
        ).fetchall()


def filtered_expenses(category=None, month=None):
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if category:
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)
    if month:
        datetime.strptime(month, "%Y-%m")
        query += " AND substr(expense_date, 1, 7) = ?"
        params.append(month)
    query += " ORDER BY expense_date DESC, id DESC"
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def update_expense(expense_id, amount, category, description, expense_date):
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    validate_date(expense_date)
    with get_connection() as conn:
        cursor = conn.execute(
            """UPDATE expenses
               SET amount=?, category=?, description=?, expense_date=?
               WHERE id=?""",
            (amount, category.strip() or "Other", description.strip(), expense_date, expense_id),
        )
        return cursor.rowcount > 0


def delete_expense(expense_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        return cursor.rowcount > 0
