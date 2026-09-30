import os
import tempfile
import unittest
from pathlib import Path

import database
import expenses
import budget


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(delete=False)
        self.temp.close()
        database.DB_PATH = Path(self.temp.name)
        database.initialize_database()

    def tearDown(self):
        os.unlink(self.temp.name)

    def test_add_and_list(self):
        expense_id = expenses.add_expense(12.50, "Food", "Lunch", "2026-09-30")
        rows = expenses.list_expenses()
        self.assertEqual(rows[0]["id"], expense_id)
        self.assertEqual(rows[0]["category"], "Food")

    def test_filter(self):
        expenses.add_expense(45, "Gas", "Fuel", "2026-09-20")
        expenses.add_expense(10, "Food", "Snack", "2026-08-20")
        rows = expenses.filtered_expenses("Gas", "2026-09")
        self.assertEqual(len(rows), 1)

    def test_budget_status(self):
        expenses.add_expense(80, "Food", "Groceries", "2026-09-10")
        budget.set_budget("2026-09", 200)
        status = budget.budget_status("2026-09")
        self.assertEqual(status["spent"], 80)
        self.assertEqual(status["remaining"], 120)

    def test_update_and_delete(self):
        expense_id = expenses.add_expense(20, "Other", "Test", "2026-09-01")
        self.assertTrue(expenses.update_expense(
            expense_id, 30, "Shopping", "Updated", "2026-09-02"
        ))
        self.assertTrue(expenses.delete_expense(expense_id))
        self.assertEqual(len(expenses.list_expenses()), 0)


if __name__ == "__main__":
    unittest.main()
