from finance_tracker.security import hash_password, verify_password


def test_password_hash_verifies_successfully():
    password = "MyStrongPass123!"
    stored = hash_password(password)
    assert verify_password(password, stored) is True


def test_password_hash_rejects_wrong_password():
    password = "MyStrongPass123!"
    stored = hash_password(password)
    assert verify_password("WrongPassword!", stored) is False
