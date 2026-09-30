from datetime import datetime
from database import initialize_database
from expenses import add_expense, list_expenses, update_expense, delete_expense, filtered_expenses
from budget import set_budget, monthly_summary, category_summary, budget_status


def money(value):
    return f"${value:,.2f}"


def read_amount(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                raise ValueError
            return round(value, 2)
        except ValueError:
            print("Please enter a positive number.")


def read_date(prompt="Date (YYYY-MM-DD, Enter for today): "):
    while True:
        value = input(prompt).strip()
        if not value:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Use YYYY-MM-DD format.")


def show_rows(rows):
    if not rows:
        print("\nNo expenses found.")
        return
    print("\nID  Date        Category        Amount       Description")
    print("-" * 72)
    for row in rows:
        print(f"{row['id']:<3} {row['expense_date']:<11} {row['category']:<15} "
              f"{money(row['amount']):<12} {row['description']}")


def add_flow():
    print("\n--- Add Expense ---")
    amount = read_amount("Amount: $")
    category = input("Category (Food/Gas/Shopping/Tuition/Entertainment/Other): ").strip() or "Other"
    description = input("Description: ").strip()
    expense_date = read_date()
    expense_id = add_expense(amount, category, description, expense_date)
    print(f"Expense #{expense_id} added.")


def filter_flow():
    print("\n--- Search / Filter ---")
    category = input("Category (Enter to skip): ").strip() or None
    month = input("Month YYYY-MM (Enter to skip): ").strip() or None
    show_rows(filtered_expenses(category, month))


def update_flow():
    show_rows(list_expenses())
    try:
        expense_id = int(input("\nExpense ID to edit: "))
    except ValueError:
        print("Invalid ID.")
        return
    amount = read_amount("New amount: $")
    category = input("New category: ").strip() or "Other"
    description = input("New description: ").strip()
    expense_date = read_date("New date (YYYY-MM-DD, Enter for today): ")
    if update_expense(expense_id, amount, category, description, expense_date):
        print("Expense updated.")
    else:
        print("Expense ID not found.")


def delete_flow():
    show_rows(list_expenses())
    try:
        expense_id = int(input("\nExpense ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return
    confirm = input("Type YES to confirm: ").strip().upper()
    if confirm == "YES":
        print("Expense deleted." if delete_expense(expense_id) else "Expense ID not found.")
    else:
        print("Delete cancelled.")


def summary_flow():
    month = input("Month (YYYY-MM): ").strip()
    summary = monthly_summary(month)
    print(f"\n--- Summary for {month} ---")
    print(f"Transactions: {summary['count']}")
    print(f"Total spent: {money(summary['total'])}")
    print("\nBy category:")
    categories = category_summary(month)
    if not categories:
        print("No spending recorded.")
    for row in categories:
        print(f"  {row['category']:<18} {money(row['total'])}")


def budget_flow():
    month = input("Month (YYYY-MM): ").strip()
    amount = read_amount("Monthly budget: $")
    set_budget(month, amount)
    print("Budget saved.")


def status_flow():
    month = input("Month (YYYY-MM): ").strip()
    status = budget_status(month)
    if status["budget"] is None:
        print("No budget set for that month.")
        return
    print(f"\nBudget:    {money(status['budget'])}")
    print(f"Spent:     {money(status['spent'])}")
    print(f"Remaining: {money(status['remaining'])}")
    print(f"Used:      {status['percent_used']:.1f}%")
    if status["remaining"] < 0:
        print("WARNING: You are over budget.")
    elif status["percent_used"] >= 80:
        print("WARNING: You have used at least 80% of your budget.")


def main():
    initialize_database()
    actions = {
        "1": add_flow, "2": lambda: show_rows(list_expenses()),
        "3": filter_flow, "4": update_flow, "5": delete_flow,
        "6": summary_flow, "7": budget_flow, "8": status_flow,
    }

    while True:
        print("""
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
""")
        choice = input("Choose an option: ").strip()
        if choice == "9":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except ValueError as exc:
                print(f"Error: {exc}")
        else:
            print("Choose a number from 1 to 9.")


if __name__ == "__main__":
    main()
