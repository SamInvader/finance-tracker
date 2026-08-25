from finance_tracker.database import get_db_connection
from finance_tracker.security import hash_password, verify_password


def test_password_hash_verifies_successfully():
    password = "MyStrongPass123!"
    stored = hash_password(password)
    assert verify_password(password, stored) is True


def test_password_hash_rejects_wrong_password():
    password = "MyStrongPass123!"
    stored = hash_password(password)
    assert verify_password("WrongPassword!", stored) is False


def test_fresh_account_db_is_initialized_with_schema():
    account_id = "regression-account-001"
    conn = get_db_connection(account_id)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'transactions'"
    ).fetchone()
    conn.close()
    assert tables is not None
