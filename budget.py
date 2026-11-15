import math
from datetime import datetime
from database import get_connection


def normalize_month(month):
    """Parse a YYYY-M[M] month and return it zero-padded (YYYY-MM).

    strptime accepts "2026-9", but expense dates are stored zero-padded
    ("2026-09-05"), so an unpadded month matched nothing and a budget set
    as "2026-9" was invisible to "2026-09" lookups.
    """
    return datetime.strptime(month, "%Y-%m").strftime("%Y-%m")


def validate_month(month):
    normalize_month(month)


def set_budget(month, amount):
    month = normalize_month(month)
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Budget must be a positive number.")
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO budgets(month, amount) VALUES (?, ?)
               ON CONFLICT(month) DO UPDATE SET amount=excluded.amount""",
            (month, amount),
        )


def monthly_summary(month):
    month = normalize_month(month)
    with get_connection() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total
               FROM expenses WHERE substr(expense_date, 1, 7)=?""",
            (month,),
        ).fetchone()
        return {"count": row["count"], "total": row["total"]}


def category_summary(month):
    month = normalize_month(month)
    with get_connection() as conn:
        return conn.execute(
            """SELECT category, ROUND(SUM(amount), 2) AS total
               FROM expenses
               WHERE substr(expense_date, 1, 7)=?
               GROUP BY category
               ORDER BY total DESC""",
            (month,),
        ).fetchall()


def budget_status(month):
    month = normalize_month(month)
    with get_connection() as conn:
        budget_row = conn.execute(
            "SELECT amount FROM budgets WHERE month=?", (month,)
        ).fetchone()
        spent_row = conn.execute(
            """SELECT COALESCE(SUM(amount), 0) AS spent
               FROM expenses WHERE substr(expense_date, 1, 7)=?""",
            (month,),
        ).fetchone()

    budget = budget_row["amount"] if budget_row else None
    spent = spent_row["spent"]
    if budget is None:
        return {"budget": None, "spent": spent, "remaining": None, "percent_used": None}
    return {
        "budget": budget,
        "spent": spent,
        "remaining": budget - spent,
        "percent_used": (spent / budget) * 100,
    }
