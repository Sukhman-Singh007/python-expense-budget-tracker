# Python Expense & Budget Tracker

A command-line personal finance application built with Python and SQLite. It stores expenses persistently, summarizes monthly spending, groups spending by category, and compares expenses against monthly budgets.

## Features

- Add, view, edit, and delete expenses
- Store amount, category, date, and description
- Persistent SQLite database
- Filter expenses by category and month
- Monthly spending totals
- Category-based spending breakdowns
- Set or update monthly budgets
- Calculate remaining budget and percentage used
- Warning when spending reaches 80% of a budget or exceeds it
- Parameterized SQL queries
- Input validation and error handling
- Automated unit tests

## Technologies

- Python 3
- SQLite / SQL
- Git & GitHub

## Run Locally

```bash
git clone https://github.com/YOUR-USERNAME/python-expense-budget-tracker.git
cd python-expense-budget-tracker
python3 main.py
```

No third-party packages are required.

## Run Tests

```bash
python3 -m unittest -v
```

## Database Design

### expenses
- `id` — unique transaction ID
- `amount` — expense amount
- `category` — spending category
- `description` — optional transaction description
- `expense_date` — transaction date

### budgets
- `month` — budget month in YYYY-MM format
- `amount` — monthly budget

## Example

```text
===============================
   EXPENSE & BUDGET TRACKER
===============================
1. Add expense
2. View all expenses
3. Search / filter expenses
4. Edit expense
5. Delete expense
6. Monthly spending summary
7. Set monthly budget
8. Check budget status
9. Exit
```

## Resume Description

**Python Expense & Budget Tracker | Python, SQL, Git**

- Developed a command-line financial tool for recording expenses and generating monthly spending summaries and category-based breakdowns.
- Implemented SQLite-backed persistence, budget tracking, search/filtering, input validation, and parameterized SQL queries for reliable transaction management.
