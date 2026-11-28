import math
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database
import expenses
import budget
import main


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

    def test_unpadded_month_is_normalized(self):
        expenses.add_expense(80, "Food", "Groceries", "2026-09-10")
        budget.set_budget("2026-9", 200)
        self.assertEqual(len(expenses.filtered_expenses(None, "2026-9")), 1)
        self.assertEqual(budget.monthly_summary("2026-9")["count"], 1)
        status = budget.budget_status("2026-09")
        self.assertEqual(status["budget"], 200)
        self.assertEqual(status["spent"], 80)

    def test_unpadded_date_is_stored_zero_padded(self):
        expense_id = expenses.add_expense(15, "Food", "Snack", "2026-9-5")
        rows = expenses.list_expenses()
        self.assertEqual(rows[0]["id"], expense_id)
        self.assertEqual(rows[0]["expense_date"], "2026-09-05")
        self.assertEqual(len(expenses.filtered_expenses(None, "2026-09")), 1)

    def test_rejects_non_finite_amounts(self):
        for bad_amount in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                expenses.add_expense(bad_amount, "Food", "Bad", "2026-09-30")
            expense_id = expenses.add_expense(20, "Food", "OK", "2026-09-30")
            with self.assertRaises(ValueError):
                expenses.update_expense(
                    expense_id, bad_amount, "Food", "Bad", "2026-09-30"
                )
            with self.assertRaises(ValueError):
                budget.set_budget("2026-09", bad_amount)
        self.assertEqual(len(expenses.list_expenses()), 3)

    def test_category_summary_groups_case_insensitively(self):
        # "Food", "food" and "FOOD" are one category when filtering, so the
        # monthly summary must not split them into three separate rows.
        expenses.add_expense(10, "Food", "Lunch", "2026-09-10")
        expenses.add_expense(20, "food", "Dinner", "2026-09-11")
        expenses.add_expense(5, "FOOD", "Snack", "2026-09-12")
        expenses.add_expense(7, "Gas", "Fuel", "2026-09-13")
        rows = budget.category_summary("2026-09")
        self.assertEqual(len(rows), 2)
        food = [r for r in rows if r["category"].lower() == "food"]
        self.assertEqual(len(food), 1)
        self.assertEqual(food[0]["total"], 35)

    def test_read_amount_reprompts_on_non_finite(self):
        with patch("builtins.input", side_effect=["nan", "inf", "-5", "12.5"]):
            self.assertEqual(main.read_amount("Amount: $"), 12.5)

    def test_read_date_returns_default_on_empty_input(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(
                main.read_date("Date: ", default="2026-09-01"), "2026-09-01"
            )
        with patch("builtins.input", return_value="2026-09-02"):
            self.assertEqual(
                main.read_date("Date: ", default="2026-09-01"), "2026-09-02"
            )

    def test_update_flow_keeps_original_date_on_empty_input(self):
        # Pressing Enter for the date while editing must keep the
        # expense's date — not silently rewrite it to today.
        expense_id = expenses.add_expense(20, "Food", "Lunch", "2026-09-01")
        with patch(
            "builtins.input",
            side_effect=[str(expense_id), "25", "Food", "Updated", ""],
        ):
            main.update_flow()
        rows = expenses.list_expenses()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], 25)
        self.assertEqual(rows[0]["expense_date"], "2026-09-01")

    def test_update_flow_keeps_category_and_description_on_empty_input(self):
        # Pressing Enter for category/description while editing must
        # keep the old values — it used to rewrite the category to
        # "Other" and wipe the description to "".
        expense_id = expenses.add_expense(20, "Food", "Lunch", "2026-09-01")
        with patch(
            "builtins.input",
            side_effect=[str(expense_id), "25", "", "", ""],
        ):
            main.update_flow()
        rows = expenses.list_expenses()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], 25)
        self.assertEqual(rows[0]["category"], "Food")
        self.assertEqual(rows[0]["description"], "Lunch")
        self.assertEqual(rows[0]["expense_date"], "2026-09-01")

    def test_read_amount_returns_default_on_empty_input(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(main.read_amount("Amount: $", default=20.0), 20.0)
        with patch("builtins.input", return_value="12.5"):
            self.assertEqual(main.read_amount("Amount: $", default=20.0), 12.5)

    def test_update_flow_keeps_amount_on_empty_input(self):
        # Pressing Enter for the amount while editing must keep the
        # expense's amount — it used to loop forever asking for a
        # positive number, with no way to keep the current value.
        expense_id = expenses.add_expense(20, "Food", "Lunch", "2026-09-01")
        with patch(
            "builtins.input",
            side_effect=[str(expense_id), "", "", "", ""],
        ):
            main.update_flow()
        rows = expenses.list_expenses()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], 20)
        self.assertEqual(rows[0]["category"], "Food")
        self.assertEqual(rows[0]["description"], "Lunch")
        self.assertEqual(rows[0]["expense_date"], "2026-09-01")

    def test_update_flow_reports_unknown_id_before_prompting(self):
        # An unknown ID is reported up front instead of asking for
        # all the new values first.
        with patch("builtins.input", side_effect=["999"]):
            main.update_flow()
        self.assertEqual(len(expenses.list_expenses()), 0)

    def test_read_month_reprompts_on_invalid_input(self):
        # A bad month used to raise a raw ValueError ("time data 'abc'
        # does not match format '%Y-%m'") that the main loop printed
        # as a cryptic "Error:" line. Like read_date, it now
        # re-prompts until the month parses.
        with patch(
            "builtins.input", side_effect=["abc", "2026-13", "2026-9"]
        ):
            self.assertEqual(main.read_month("Month: "), "2026-09")

    def test_read_month_empty_input_means_current_month(self):
        # Enter for the month means the current month, like Enter for
        # the date means today.
        from datetime import datetime

        with patch("builtins.input", return_value=""):
            self.assertEqual(
                main.read_month("Month: "),
                datetime.now().strftime("%Y-%m"),
            )

    def test_summary_flow_reprompts_on_bad_month(self):
        # The monthly summary used to die on a bad month with the raw
        # strptime error; it now asks again and shows the summary.
        with patch("builtins.input", side_effect=["abc", "2026-09"]):
            main.summary_flow()

    def test_read_amount_rounds_half_cents_up(self):
        # Amounts are money, not binary floats: round(2.675, 2) is
        # 2.67 because 2.675 is stored as 2.67499..., so the tracker
        # silently recorded a cent less than the user typed.
        for typed, expected in (("2.675", 2.68), ("1.005", 1.01),
                                ("10.005", 10.01), ("12.345", 12.35)):
            with patch("builtins.input", return_value=typed):
                self.assertEqual(main.read_amount("Amount: $"), expected)


if __name__ == "__main__":
    unittest.main()
