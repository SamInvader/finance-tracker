from datetime import datetime

from finance_tracker.database import DB_PATH, get_db_connection


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


def add_transaction(amount, txn_type, category, date_value, description):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (amount, type, category, date, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (float(amount), txn_type, category, date_value, description, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_transactions(filters=None):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM transactions"
    params = []
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
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY date DESC, created_at DESC"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_transaction_by_id(transaction_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_transaction(transaction_id, amount, txn_type, category, date_value, description):
    conn = get_db_connection()
    conn.execute(
        "UPDATE transactions SET amount = ?, type = ?, category = ?, date = ?, description = ? WHERE id = ?",
        (float(amount), txn_type, category, date_value, description, transaction_id),
    )
    conn.commit()
    conn.close()


def delete_transaction(transaction_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()


def get_budget_for_month(month):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM budgets WHERE month = ?", (month,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_budget(month, amount):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM budgets WHERE month = ?", (month,)).fetchone()
    if existing:
        conn.execute(
            "UPDATE budgets SET amount = ?, updated_at = ? WHERE month = ?",
            (float(amount), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), month),
        )
    else:
        conn.execute(
            "INSERT INTO budgets (month, amount, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (month, float(amount), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
        )
    conn.commit()
    conn.close()


def get_savings_goals():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM savings_goals ORDER BY target_date ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_savings_goal(name, target_amount, current_amount, target_date, description):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO savings_goals (name, target_amount, current_amount, target_date, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, float(target_amount), float(current_amount), target_date, description, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def update_savings_goal(goal_id, change_amount, direction):
    conn = get_db_connection()
    row = conn.execute("SELECT current_amount FROM savings_goals WHERE id = ?", (goal_id,)).fetchone()
    if not row:
        conn.close()
        return False

    current = float(row["current_amount"])
    next_amount = current + change_amount if direction == "add" else current - change_amount
    if next_amount < 0:
        conn.close()
        return False

    conn.execute("UPDATE savings_goals SET current_amount = ? WHERE id = ?", (next_amount, goal_id))
    conn.commit()
    conn.close()
    return True


def get_all_months():
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT strftime('%Y-%m', date) AS month FROM transactions ORDER BY month ASC").fetchall()
    conn.close()
    return [row["month"] for row in rows]


def get_monthly_summary(year_month):
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
        FROM transactions
        WHERE strftime('%Y-%m', date) = ?
        """,
        (year_month,),
    ).fetchone()
    conn.close()
    return dict(row) if row else {"income": 0.0, "expense": 0.0}


def get_monthly_expense_by_category(year_month):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM transactions WHERE type = 'expense' AND strftime('%Y-%m', date) = ? GROUP BY category ORDER BY total DESC",
        (year_month,),
    ).fetchall()
    conn.close()
    return {row["category"]: float(row["total"]) for row in rows}


def get_last_six_months_income_expense():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT strftime('%Y-%m', date) AS month,
               COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
               COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
        FROM transactions
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month ASC
        LIMIT 6
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
