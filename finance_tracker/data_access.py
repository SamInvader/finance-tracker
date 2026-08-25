from datetime import datetime

from finance_tracker.database import get_db_connection


INCOME_CATEGORIES = ["Allowance", "Salary", "Freelance", "Gift", "Other"]
EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Education",
    "Bills",
    "Entertainment",
    "Shopping",
    "Health",
    "Other",
]


def get_active_account_id():
    from flask import request

    active_id = request.cookies.get("active_account_id")
    if active_id:
        return active_id
    return "default"


def add_transaction(amount, txn_type, category, date_value, description, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (account_id, amount, type, category, date, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (account_id, float(amount), txn_type, category, date_value, description, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_transactions(filters=None, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    cur = conn.cursor()
    query = "SELECT * FROM transactions WHERE account_id = ?"
    params = [account_id]
    clauses = []

    if filters:
        if filters.get("type") and filters["type"] != "all":
            clauses.append("type = ?")
            params.append(filters["type"])
        if filters.get("category") and filters["category"] != "all":
            clauses.append("category = ?")
            params.append(filters["category"])
        if filters.get("month"):
            clauses.append("strftime('%Y-%m', date) = ?")
            params.append(filters["month"])
        if filters.get("search"):
            clauses.append("description LIKE ?")
            params.append(f"%{filters['search']}%")
        if filters.get("start_date"):
            clauses.append("date >= ?")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            clauses.append("date <= ?")
            params.append(filters["end_date"])

    if clauses:
        query += " AND " + " AND ".join(clauses)

    query += " ORDER BY date DESC, created_at DESC"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_transaction_by_id(transaction_id, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    row = conn.execute("SELECT * FROM transactions WHERE id = ? AND account_id = ?", (transaction_id, account_id)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_transaction(transaction_id, amount, txn_type, category, date_value, description, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    conn.execute(
        "UPDATE transactions SET amount = ?, type = ?, category = ?, date = ?, description = ? WHERE id = ? AND account_id = ?",
        (float(amount), txn_type, category, date_value, description, transaction_id, account_id),
    )
    conn.commit()
    conn.close()


def delete_transaction(transaction_id, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    conn.execute("DELETE FROM transactions WHERE id = ? AND account_id = ?", (transaction_id, account_id))
    conn.commit()
    conn.close()


def get_budget_for_month(month, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    row = conn.execute("SELECT * FROM budgets WHERE month = ? AND account_id = ?", (month, account_id)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_budget(month, amount, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    existing = conn.execute("SELECT id FROM budgets WHERE month = ? AND account_id = ?", (month, account_id)).fetchone()
    if existing:
        conn.execute(
            "UPDATE budgets SET amount = ?, updated_at = ? WHERE month = ? AND account_id = ?",
            (float(amount), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), month, account_id),
        )
    else:
        conn.execute(
            "INSERT INTO budgets (account_id, month, amount, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (account_id, month, float(amount), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
        )
    conn.commit()
    conn.close()


def get_savings_goals(account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    rows = conn.execute("SELECT * FROM savings_goals WHERE account_id = ? ORDER BY target_date ASC", (account_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_savings_goal(name, target_amount, current_amount, target_date, description, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    conn.execute(
        "INSERT INTO savings_goals (account_id, name, target_amount, current_amount, target_date, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (account_id, name, float(target_amount), float(current_amount), target_date, description, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def update_savings_goal(goal_id, change_amount, direction, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    row = conn.execute("SELECT current_amount FROM savings_goals WHERE id = ? AND account_id = ?", (goal_id, account_id)).fetchone()
    if not row:
        conn.close()
        return False

    current = float(row["current_amount"])
    next_amount = current + change_amount if direction == "add" else current - change_amount
    if next_amount < 0:
        conn.close()
        return False

    conn.execute("UPDATE savings_goals SET current_amount = ? WHERE id = ? AND account_id = ?", (next_amount, goal_id, account_id))
    conn.commit()
    conn.close()
    return True


def get_all_months(account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    rows = conn.execute("SELECT DISTINCT strftime('%Y-%m', date) AS month FROM transactions WHERE account_id = ? ORDER BY month ASC", (account_id,)).fetchall()
    conn.close()
    return [row["month"] for row in rows]


def get_monthly_summary(year_month, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    row = conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
        FROM transactions
        WHERE account_id = ? AND strftime('%Y-%m', date) = ?
        """,
        (account_id, year_month),
    ).fetchone()
    conn.close()
    return dict(row) if row else {"income": 0.0, "expense": 0.0}


def get_monthly_expense_by_category(year_month, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM transactions WHERE account_id = ? AND type = 'expense' AND strftime('%Y-%m', date) = ? GROUP BY category ORDER BY total DESC",
        (account_id, year_month),
    ).fetchall()
    conn.close()
    return {row["category"]: float(row["total"]) for row in rows}


def get_last_six_months_income_expense(account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    rows = conn.execute(
        """
        SELECT strftime('%Y-%m', date) AS month,
               COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
               COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
        FROM transactions
        WHERE account_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month ASC
        LIMIT 6
        """,
        (account_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_smart_daily_budget(month, account_id=None):
    account_id = account_id or get_active_account_id()
    daily_budget = get_budget_for_month(month, account_id)
    budget_amount = float((daily_budget or {}).get('amount', 0.0) or 0.0)
    txns = get_transactions({"month": month}, account_id)
    monthly_expense = sum(float(t['amount']) for t in txns if t['type'] == 'expense')
    days_in_month = 30
    savings_total = sum(float(goal['target_amount']) for goal in get_savings_goals(account_id))
    savings_saved = sum(float(goal['current_amount']) for goal in get_savings_goals(account_id))
    remaining_goal = max(0.0, savings_total - savings_saved)
    suggested_save = remaining_goal / max(days_in_month, 1)

    if not budget_amount:
        spending_cap = max(0.0, monthly_expense / max(days_in_month, 1))
        return {
            "daily_budget": round(spending_cap, 2),
            "suggested_save_per_day": round(suggested_save, 2),
            "spending_limit": round(spending_cap, 2),
            "notes": ["No monthly target set yet, so the system used your recent spending pattern to estimate a safe daily cap."],
            "plan": [
                {"label": f"Day {index}", "value": round(min(spending_cap, (monthly_expense / max(days_in_month, 1)) + (index * 0.5)), 2)}
                for index in range(1, 8)
            ],
        }

    daily_limit = max(0.0, (budget_amount - monthly_expense) / days_in_month)
    return {
        "daily_budget": round(max(0.0, daily_limit), 2),
        "suggested_save_per_day": round(max(0.0, suggested_save), 2),
        "spending_limit": round(max(0.0, budget_amount / days_in_month), 2),
        "notes": [
            "Daily spending is estimated from your active monthly budget and recent expense patterns.",
            "Savings guidance is based on the remaining contribution needed to hit your goal before the target date." if remaining_goal else "Your savings goals look on track based on the current totals.",
        ],
        "plan": [
            {"label": f"Day {index}", "value": round(max(0.0, min(budget_amount / 30, (budget_amount - monthly_expense) / 30 + (index * 1.25))), 2)}
            for index in range(1, 8)
        ],
    }


def get_budget_items(account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    rows = conn.execute("SELECT * FROM budget_items WHERE account_id = ? ORDER BY created_at DESC", (account_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_budget_item(name, amount, month, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    conn.execute(
        "INSERT INTO budget_items (account_id, name, amount, month, is_purchased, created_at) VALUES (?, ?, ?, ?, 0, ?)",
        (account_id, name, float(amount), month, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def delete_budget_item(item_id, account_id=None):
    account_id = account_id or get_active_account_id()
    conn = get_db_connection(account_id)
    conn.execute("DELETE FROM budget_items WHERE id = ? AND account_id = ?", (item_id, account_id))
    conn.commit()
    conn.close()
