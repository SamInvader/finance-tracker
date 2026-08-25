import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "instance" / "finance_tracker.db"
ACCOUNT_DB_DIR = BASE_DIR / "instance" / "accounts"


def ensure_account_storage():
    ACCOUNT_DB_DIR.mkdir(parents=True, exist_ok=True)


def get_account_db_path(account_id=None):
    ensure_account_storage()
    if not account_id:
        return DB_PATH
    safe_id = str(account_id).strip()
    if not safe_id:
        return DB_PATH
    return ACCOUNT_DB_DIR / f"{safe_id}.db"


def _create_default_schema(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS budget_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            is_purchased INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL NOT NULL DEFAULT 0,
            target_date TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()


def get_db_connection(account_id=None):
    db_path = get_account_db_path(account_id)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    table_names = {
        row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "transactions" not in table_names or "budgets" not in table_names or "savings_goals" not in table_names or "budget_items" not in table_names:
        _create_default_schema(conn)
        table_names = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    conn.commit()
    return conn


def _ensure_column(conn, table_name, column_name, column_def):
    cur = conn.cursor()
    columns = cur.execute(f"PRAGMA table_info({table_name})").fetchall()
    if not any(column[1] == column_name for column in columns):
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")


def init_db(account_id=None):
    conn = get_db_connection(account_id)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS budget_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            is_purchased INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT DEFAULT 'default',
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL NOT NULL DEFAULT 0,
            target_date TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    _ensure_column(conn, "transactions", "account_id", "TEXT DEFAULT 'default'")
    _ensure_column(conn, "budgets", "account_id", "TEXT DEFAULT 'default'")
    _ensure_column(conn, "savings_goals", "account_id", "TEXT DEFAULT 'default'")

    conn.commit()
    conn.close()


def reset_all_account_data():
    if DB_PATH.exists():
        DB_PATH.unlink()
    ensure_account_storage()
    for db_file in ACCOUNT_DB_DIR.glob("*.db"):
        db_file.unlink(missing_ok=True)
    init_db()


def format_date(value):
    if isinstance(value, str):
        return value
    return value.strftime("%Y-%m-%d")


@dataclass
class Transaction:
    id: Optional[int] = None
    amount: float = 0.0
    type: str = "expense"
    category: str = "Other"
    date: str = ""
    description: str = ""
    created_at: str = ""

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            amount=float(row["amount"]),
            type=row["type"],
            category=row["category"],
            date=row["date"],
            description=row["description"],
            created_at=row["created_at"],
        )


@dataclass
class Budget:
    id: Optional[int] = None
    month: str = ""
    amount: float = 0.0
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            month=row["month"],
            amount=float(row["amount"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class SavingsGoal:
    id: Optional[int] = None
    name: str = ""
    target_amount: float = 0.0
    current_amount: float = 0.0
    target_date: str = ""
    description: str = ""
    created_at: str = ""

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            target_amount=float(row["target_amount"]),
            current_amount=float(row["current_amount"]),
            target_date=row["target_date"],
            description=row["description"],
            created_at=row["created_at"],
        )
