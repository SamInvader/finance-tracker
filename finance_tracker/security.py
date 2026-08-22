import hashlib
import hmac
import os


def hash_password(password, salt=None):
    if not isinstance(password, str):
        password = str(password)
    if salt is None:
        salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200000,
    )
    return f"{salt}${digest.hex()}"


def verify_password(password, stored_hash):
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, digest = stored_hash.split("$", 1)
    candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, stored_hash) and hmac.compare_digest(digest, candidate.split("$", 1)[1])
