from datetime import datetime
from database import get_connection


def validate_month(month):
    datetime.strptime(month, "%Y-%m")


def set_budget(month, amount):
    validate_month(month)
    if amount <= 0:
        raise ValueError("Budget must be positive.")
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO budgets(month, amount) VALUES (?, ?)
               ON CONFLICT(month) DO UPDATE SET amount=excluded.amount""",
            (month, amount),
        )


def monthly_summary(month):
    validate_month(month)
    with get_connection() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total
               FROM expenses WHERE substr(expense_date, 1, 7)=?""",
            (month,),
        ).fetchone()
        return {"count": row["count"], "total": row["total"]}


def category_summary(month):
    validate_month(month)
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
    validate_month(month)
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
