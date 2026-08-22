import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "instance" / "finance_tracker.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            month TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    conn.close()


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
